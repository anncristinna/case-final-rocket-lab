# Databricks notebook source
# MAGIC %md
# MAGIC # 04 · Gold — fato e KPIs para análise e painel
# MAGIC - `fato_chamado`: 1 linha por chamado, com motivo, canal, atendente, tempos, custo e nota.
# MAGIC - Tabelas `kpi_*`: agregações prontas para o painel / Power BI.
# MAGIC - CPF substituído por `cliente_hash`; nome e e-mail nem chegam aqui.
# MAGIC - **Idempotente**: `overwrite`.
# MAGIC
# MAGIC **Decisões provisórias** (ver `docs/arquitetura.md`, tabela de decisões em aberto):
# MAGIC - Tempos: timestamps de `chamados_hora` têm prioridade; se ausentes, usa o campo original de `chamados`.
# MAGIC   `tempo_divergente` marca quando os dois diferem em mais de 60 s.
# MAGIC - `abandonado` = chamado sem hora de início de atendimento. Nesses casos a espera original está preenchida
# MAGIC   e o tempo de atendimento vazio, o que indica desistência do cliente na fila.
# MAGIC - CSAT = % de notas 4–5 entre os chamados que responderam a pesquisa.
# MAGIC
# MAGIC > Código inicial, ainda não executado no workspace.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

from pyspark.sql import functions as F

S = f"{CATALOG}.{SCHEMA_SILVER}"
G = f"{CATALOG}.{SCHEMA_GOLD}"


def save(df, nome):
    destino = f"{G}.{nome}"
    df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(destino)
    print(f"{destino}: {spark.table(destino).count():,} linhas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Fato

# COMMAND ----------

ch = spark.table(f"{S}.chamados")
h = spark.table(f"{S}.chamados_hora").drop("id_cliente_hora").withColumn("_tem_hora", F.lit(True))
mot = spark.table(f"{S}.base_motivos").select(
    "motivo_key",
    F.col("nome_motivo").alias("motivo"),
    "categoria",
    "criticidade",
)
can = spark.table(f"{S}.canais").select("canal_key", F.col("nome_canal").alias("canal"), "tipo_canal")
atd = spark.table(f"{S}.base_atendentes").select(
    "id_atendente",
    F.col("nivel_atendimento").alias("nivel_atendente"),
    F.col("data_admissao").alias("atendente_admissao"),
)
cli = spark.table(f"{S}.clientes").select(
    "id_cliente", F.col("regiao"), F.col("idade"), F.col("data_cadastro").alias("cliente_desde")
)
custo = (
    spark.table(f"{S}.custos")
    .where(~F.col("dq_custo_invalido"))
    .groupBy("id_chamado")
    .agg(
        F.sum("custo").alias("custo_total"),
        F.count("*").alias("qtd_lancamentos_custo"),
        F.max("dq_custo_nao_positivo").alias("dq_custo_nao_positivo"),
    )
)
nota = (
    spark.table(f"{S}.pesquisa_satisfacao")
    .where(~F.col("dq_nota_invalida"))
    .groupBy("id_chamado")
    .agg(F.avg("nota_atendimento").alias("nota"))
)

fato = (
    ch.join(h, "id_chamado", "left")
      .join(mot, "motivo_key", "left")
      .join(can, "canal_key", "left")
      .join(atd, "id_atendente", "left")
      .join(cli, "id_cliente", "left")
      .join(custo, "id_chamado", "left")
      .join(nota, "id_chamado", "left")
)

fato = (
    fato
    .withColumn("cliente_hash", F.sha2(F.concat(F.lit(HASH_SALT), F.col("id_cliente")), 256))
    .drop("id_cliente")
    .withColumn("tem_registro_hora", F.coalesce(F.col("_tem_hora"), F.lit(False)))
    .drop("_tem_hora")
    .withColumn("tempo_espera_final_s", F.coalesce(F.col("tempo_espera_calc_s"), F.col("tempo_espera_s")))
    .withColumn("tempo_atendimento_final_s", F.coalesce(F.col("tempo_atendimento_calc_s"), F.col("tempo_atendimento_s")))
    .withColumn(
        "tempo_divergente",
        (F.abs(F.col("tempo_espera_calc_s") - F.col("tempo_espera_s")) > 60)
        | (F.abs(F.col("tempo_atendimento_calc_s") - F.col("tempo_atendimento_s")) > 60),
    )
    # Sem hora de início, mas com espera registrada e sem tempo de atendimento: cliente desistiu.
    .withColumn("abandonado", F.col("inicio_ts").isNull())
    .withColumn("mes", F.trunc(F.to_date("abertura_ts"), "month"))
    .withColumn("faixa_etaria", F.when(F.col("idade") < 30, "18-29").when(F.col("idade") < 45, "30-44")
                                  .when(F.col("idade") < 60, "45-59").when(F.col("idade") >= 60, "60+"))
)

save(fato, "fato_chamado")

# COMMAND ----------

# MAGIC %md
# MAGIC ## KPIs
# MAGIC Todas as tabelas `kpi_*` usam as mesmas definições (ver `CLAUDE.md`).

# COMMAND ----------

def kpis(df, *dims):
    return df.groupBy(*dims).agg(
        F.count("*").alias("chamados"),
        F.avg(F.col("resolvido").cast("int")).alias("taxa_resolucao"),
        F.avg("tempo_espera_final_s").alias("tme_s"),
        F.avg("tempo_atendimento_final_s").alias("tma_s"),
        F.sum("custo_total").alias("custo_total"),
        F.avg("custo_total").alias("custo_medio_chamado"),
        F.count("nota").alias("respostas_pesquisa"),
        F.avg(F.when(F.col("nota").isNotNull(), (F.col("nota") >= 4).cast("int"))).alias("csat"),
        F.avg(F.col("abandonado").cast("int")).alias("pct_abandono"),
    )


f = spark.table(f"{G}.fato_chamado")

save(kpis(f, "mes"), "kpi_mensal")
save(kpis(f, "mes", "canal", "tipo_canal"), "kpi_canal_mes")
save(kpis(f, "motivo", "categoria", "criticidade"), "kpi_motivo")
save(kpis(f, "canal", "motivo"), "kpi_canal_motivo")
save(kpis(f, "nivel_atendente", "mes"), "kpi_nivel_mes")
save(kpis(f, "id_atendente", "nivel_atendente"), "kpi_atendente")
save(kpis(f, "faixa_etaria", "canal"), "kpi_faixa_etaria_canal")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conferência rápida

# COMMAND ----------

display(spark.table(f"{G}.kpi_mensal").orderBy("mes"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exportação para Power BI (opcional)
# MAGIC O Free Edition não integra com Power BI. Gera CSVs no Volume `exports`; baixe pela UI
# MAGIC (*Catalog → Volumes → exports*). **Não commitar** os arquivos.

# COMMAND ----------

EXPORTAR = False  # mude para True quando for exportar

if EXPORTAR:
    for t in ["kpi_mensal", "kpi_canal_mes", "kpi_motivo", "kpi_canal_motivo",
              "kpi_nivel_mes", "kpi_atendente", "kpi_faixa_etaria_canal"]:
        (spark.table(f"{G}.{t}").coalesce(1)
              .write.mode("overwrite").option("header", True).csv(f"{VOLUME_EXPORTS}/{t}"))
        print("exportado:", t)
