# Databricks notebook source
# MAGIC %md
# MAGIC # Custos e pesquisa de satisfação — Milton
# MAGIC Tabelas: `custos`, `pesquisa_satisfacao` (cruzando com `chamados`, `chamados_hora`, `canais`,
# MAGIC `base_motivos` e `base_atendentes`).
# MAGIC
# MAGIC Valores de referência citados nas células markdown vêm de uma execução local anterior sobre os
# MAGIC CSVs completos — **este notebook deve reconferir e sinalizar qualquer diferença** ao rodar aqui.

# COMMAND ----------

# MAGIC %run ./_carga_dados

# COMMAND ----------

from pyspark.sql import functions as F, Window

# COMMAND ----------

# MAGIC %md
# MAGIC ## a) Custos — limpeza
# MAGIC Formatos observados: `0,39` · `3.45` · `R$ 1,46` · `3.45reais` · `R$ -2,10`.
# MAGIC
# MAGIC Regra: remover tudo que **não** for dígito, vírgula, ponto ou `-` (isso já cobre `R$`, espaços e o
# MAGIC sufixo `reais`). Se o que restar tiver vírgula, tratamos como separador decimal brasileiro: removemos
# MAGIC os pontos (seriam separador de milhar) e trocamos a vírgula por ponto. Se não tiver vírgula, o ponto
# MAGIC que já está lá **é** o separador decimal e fica como está.
# MAGIC
# MAGIC ⚠️ **Não remover todos os pontos indiscriminadamente.** Esse foi o erro do notebook inicial do Juan:
# MAGIC ao tirar todo ponto, `23.24` virava `2324` e `74.71reais` virava `7471`, inflando o custo total para
# MAGIC R$ 42,2 mi. O valor correto, com a regra acima, é **~R$ 1,45 mi**.

# COMMAND ----------

bruto = F.regexp_replace(F.trim(F.col("custo")), r"[^0-9,.\-]", "")
numero = F.when(
    bruto.contains(","),
    F.regexp_replace(F.regexp_replace(bruto, r"\.", ""), ",", "."),
).otherwise(bruto)

custos_tipado = (
    df_custos
    .withColumn("_bruto", F.trim(F.col("custo")))
    .withColumn("_numero", numero)
)
custos_tipado = add_try(custos_tipado, "custo_valor", F.col("_numero"), "double")
custos_tipado = add_try(custos_tipado, "id_custo_i", F.trim(F.col("id_custo")), "int")
custos_tipado = add_try(custos_tipado, "id_chamado_i", F.trim(F.col("id_chamado")), "int")

custos_limpo = (
    custos_tipado
    .select(
        F.col("id_custo_i").alias("id_custo"),
        F.col("id_chamado_i").alias("id_chamado"),
        F.col("custo_valor").alias("custo"),
    )
    .withColumn("dq_custo_invalido", F.col("custo").isNull())
    .withColumn("dq_custo_nao_positivo", F.col("custo") <= 0)
    .dropDuplicates(["id_custo"])
)

print("custos únicos (após remover duplicatas por id_custo):", custos_limpo.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Quadro dos padrões de formato encontrados (dígitos trocados por `9`, para não vazar valores reais):

# COMMAND ----------

padrao = F.regexp_replace(F.trim(F.col("custo")), r"\d", "9")
display(
    df_custos
    .withColumn("padrao", padrao)
    .groupBy("padrao")
    .count()
    .orderBy(F.desc("count"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## b) Custos — análises

# COMMAND ----------

# MAGIC %md
# MAGIC ### Total e distribuição

# COMMAND ----------

validos = custos_limpo.where(~F.col("dq_custo_invalido"))

total_custo = validos.agg(F.sum("custo")).first()[0]
print(f"custo total: R$ {total_custo:,.2f}")

quantis = validos.approxQuantile("custo", [0.1, 0.25, 0.5, 0.75, 0.9, 0.99], 0.01)
print("quantis (10/25/50/75/90/99%):", quantis)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Custos negativos, zero e chamados sem custo

# COMMAND ----------

print("custos <= 0:", custos_limpo.where(F.col("dq_custo_nao_positivo")).count())
print("custos negativos:", custos_limpo.where(F.col("custo") < 0).count())
print("custos iguais a zero:", custos_limpo.where(F.col("custo") == 0).count())

chamados_unicos = df_chamados.select(F.trim("id_chamado").alias("id_chamado")).dropDuplicates(["id_chamado"])
chamados_sem_custo = chamados_unicos.join(
    custos_limpo.where(~F.col("dq_custo_invalido")), "id_chamado", "left_anti"
)
print("chamados sem custo:", chamados_sem_custo.count())

# COMMAND ----------

# MAGIC %md
# MAGIC ### Custo por mês
# MAGIC Usamos o mês da **finalização** do atendimento (`chamados_hora.hora_finalizacao_atendimento`), não a
# MAGIC abertura: a abertura tem ~198 chamados com o ano errado (ver `chamados_hora_juan.py`), a finalização não.

# COMMAND ----------

def _limpa_conector(col):
    # remove o conector "às" (tolera encoding corrompido) entre data e hora
    return F.regexp_replace(F.trim(col), r"\s\S{1,3}\s", " ")


hora_tipada = add_try(
    df_chamados_hora.withColumn("id_chamado", F.trim(F.col("id_chamado"))),
    "fim_ts",
    _limpa_conector(F.col("hora_finalizacao_atendimento")),
    "ts",
    "dd/MM/yyyy HH:mm:ss",
)
hora_mes = hora_tipada.select(
    F.trim("id_chamado").alias("id_chamado"), F.trunc(F.to_date("fim_ts"), "month").alias("mes")
).dropDuplicates(["id_chamado"])

custo_mes = (
    custos_limpo.where(~F.col("dq_custo_invalido"))
    .join(hora_mes, "id_chamado", "inner")
    .groupBy("mes")
    .agg(F.sum("custo").alias("custo_total"), F.count("*").alias("qtd_lancamentos"))
    .orderBy("mes")
)
display(custo_mes)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Custo médio por canal, motivo e nível do atendente
# MAGIC `chamados` tem 2.636 `id_chamado` duplicados (idênticos): deduplicamos **antes** de qualquer join para
# MAGIC não contar o mesmo custo mais de uma vez. `canal` é texto livre: normalizamos com `norm_key` +
# MAGIC `CANAL_ALIAS` (de `_carga_dados.py`) antes de agrupar.

# COMMAND ----------

chamados_dedup = df_chamados.dropDuplicates(["id_chamado"]).select(
    F.trim("id_chamado").alias("id_chamado"),
    F.trim("canal").alias("canal_original"),
    F.trim("motivo").alias("motivo_original"),
    norm_key(F.col("canal")).alias("_canal_key_bruta"),
    norm_key(F.col("motivo")).alias("motivo_key"),
    F.trim("id_atendente").alias("id_atendente"),
)
mapa_canal = F.create_map(*[F.lit(x) for kv in CANAL_ALIAS.items() for x in kv])
chamados_dedup = chamados_dedup.withColumn(
    "canal_key", F.coalesce(mapa_canal[F.col("_canal_key_bruta")], F.col("_canal_key_bruta"))
).drop("_canal_key_bruta")

atendentes_nivel = add_try(
    df_atendentes, "nivel", F.regexp_extract(F.col("nivel_atendimento"), r"(\d)", 1), "int"
).select(F.trim("id_atendente").alias("id_atendente"), F.col("nivel").alias("nivel_atendente"))

custo_por_chamado = (
    custos_limpo.where(~F.col("dq_custo_invalido"))
    .groupBy("id_chamado")
    .agg(F.sum("custo").alias("custo_total"))
)

base_custo_dim = chamados_dedup.join(custo_por_chamado, "id_chamado", "left").join(
    atendentes_nivel, "id_atendente", "left"
)

print("Custo médio por canal:")
display(base_custo_dim.groupBy("canal_key").agg(F.avg("custo_total").alias("custo_medio"), F.count("*").alias("chamados")))

print("Custo médio por motivo:")
display(base_custo_dim.groupBy("motivo_key").agg(F.avg("custo_total").alias("custo_medio"), F.count("*").alias("chamados")))

print("Custo médio por nível do atendente:")
display(base_custo_dim.groupBy("nivel_atendente").agg(F.avg("custo_total").alias("custo_medio"), F.count("*").alias("chamados")))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Custo acumulado x volume de chamados
# MAGIC Separamos o efeito **volume** (mais chamados) do efeito **custo unitário** (cada chamado ficou mais caro?).

# COMMAND ----------

volume_mes = chamados_dedup.join(hora_mes, "id_chamado", "left").groupBy("mes").agg(F.count("*").alias("qtd_chamados"))

janela_mes = Window.orderBy("mes").rowsBetween(Window.unboundedPreceding, 0)
evolucao = (
    custo_mes.join(volume_mes, "mes", "left")
    .withColumn("custo_medio_por_chamado", F.col("custo_total") / F.col("qtd_chamados"))
    .withColumn("custo_acumulado", F.sum("custo_total").over(janela_mes))
    .orderBy("mes")
)
display(evolucao)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Maiores outliers de custo

# COMMAND ----------

display(custos_limpo.where(~F.col("dq_custo_invalido")).orderBy(F.desc("custo")).limit(20))

# COMMAND ----------

# MAGIC %md
# MAGIC ## c) Pesquisa de satisfação — limpeza
# MAGIC Nota válida: inteiro de **1 a 5**. `-1`, `0`, `6` e vazio viram `null` + `dq_nota_invalida`.
# MAGIC Deduplicamos por `id_chamado` (chamados com pesquisa repetida têm a mesma nota).

# COMMAND ----------

pesquisa_tipada = add_try(df_pesquisa, "id_pesquisa_i", F.trim(F.col("id_pesquisa")), "int")
pesquisa_tipada = add_try(pesquisa_tipada, "id_chamado_i", F.trim(F.col("id_chamado")), "int")
pesquisa_tipada = add_try(pesquisa_tipada, "nota_i", F.trim(F.col("nota_atendimento")), "int")

pesquisa_limpa = (
    pesquisa_tipada
    .select(
        F.col("id_pesquisa_i").alias("id_pesquisa"),
        F.col("id_chamado_i").alias("id_chamado"),
        F.when(F.col("nota_i").between(1, 5), F.col("nota_i")).alias("nota"),
    )
    .withColumn("dq_nota_invalida", F.col("nota").isNull())
    .dropDuplicates(["id_chamado"])
)
print("pesquisas únicas por chamado:", pesquisa_limpa.count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## d) Pesquisa de satisfação — análises

# COMMAND ----------

# MAGIC %md
# MAGIC ### Distribuição das notas e taxa de resposta

# COMMAND ----------

display(pesquisa_limpa.where(~F.col("dq_nota_invalida")).groupBy("nota").count().orderBy("nota"))

respostas_validas = pesquisa_limpa.where(~F.col("dq_nota_invalida")).count()
taxa_resposta = respostas_validas / chamados_unicos.count()
print(f"taxa de resposta: {taxa_resposta:.1%}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### CSAT mensal
# MAGIC CSAT = % de notas 4 e 5 entre as **válidas**. Mês pelo mesmo critério do custo (finalização em `chamados_hora`).

# COMMAND ----------

csat_mes = (
    pesquisa_limpa.where(~F.col("dq_nota_invalida"))
    .join(hora_mes, "id_chamado", "left")
    .groupBy("mes")
    .agg(
        F.count("*").alias("respostas"),
        F.avg((F.col("nota") >= 4).cast("int")).alias("csat"),
    )
    .orderBy("mes")
)
display(csat_mes)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Nota média por canal, motivo, nível do atendente e resolução
# MAGIC `resolvido` em `chamados` vem em formatos mistos (`Sim`, `Não`, `S`, `N`, `1`, `0`, `Nao resolvido`,
# MAGIC vazio); normalizamos com `norm_key` antes de mapear para booleano.

# COMMAND ----------

res_key = norm_key(F.col("resolvido"))
resolvido_bool = (
    F.when(res_key.isin("sim", "s", "1", "true", "yes", "resolvido"), F.lit(True))
     .when(res_key.isin("nao", "n", "0", "false", "nao resolvido"), F.lit(False))
)
chamados_resolvido = df_chamados.dropDuplicates(["id_chamado"]).select(
    F.trim("id_chamado").alias("id_chamado"), resolvido_bool.alias("resolvido")
)

base_nota_dim = (
    pesquisa_limpa.where(~F.col("dq_nota_invalida"))
    .join(chamados_dedup, "id_chamado", "left")
    .join(atendentes_nivel, "id_atendente", "left")
    .join(chamados_resolvido, "id_chamado", "left")
)

print("Nota média por canal:")
display(base_nota_dim.groupBy("canal_key").agg(F.avg("nota").alias("nota_media"), F.count("*").alias("respostas")))

print("Nota média por motivo:")
display(base_nota_dim.groupBy("motivo_key").agg(F.avg("nota").alias("nota_media"), F.count("*").alias("respostas")))

print("Nota média por nível do atendente:")
display(base_nota_dim.groupBy("nivel_atendente").agg(F.avg("nota").alias("nota_media"), F.count("*").alias("respostas")))

print("Nota média por resolução:")
display(base_nota_dim.groupBy("resolvido").agg(F.avg("nota").alias("nota_media"), F.count("*").alias("respostas")))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Nota x tempo de espera (faixas)
# MAGIC Tempo de espera = `hora_inicio_atendimento` − `hora_abertura_chamado` (ambos em `chamados_hora`).
# MAGIC ⚠️ Não aplicamos aqui a correção do ano da abertura (responsabilidade de `chamados_hora_juan.py`):
# MAGIC excluímos da análise os casos com ordem inválida (início antes da abertura), que é o sintoma desse erro.

# COMMAND ----------

hora_espera = add_try(
    hora_tipada, "abertura_ts", _limpa_conector(F.col("hora_abertura_chamado")), "ts", "dd/MM/yyyy HH:mm:ss"
)
hora_espera = add_try(
    hora_espera, "inicio_ts", _limpa_conector(F.col("hora_inicio_atendimento")), "ts", "dd/MM/yyyy HH:mm:ss"
)
hora_espera = (
    hora_espera
    .withColumn(
        "tempo_espera_s",
        F.when(
            F.col("inicio_ts").isNotNull() & (F.col("inicio_ts") >= F.col("abertura_ts")),
            F.unix_timestamp("inicio_ts") - F.unix_timestamp("abertura_ts"),
        ),
    )
    .select("id_chamado", "tempo_espera_s")
    .dropDuplicates(["id_chamado"])
)

faixa_espera = (
    F.when(F.col("tempo_espera_s") <= 60, "0-1 min")
     .when(F.col("tempo_espera_s") <= 300, "1-5 min")
     .when(F.col("tempo_espera_s") <= 900, "5-15 min")
     .otherwise("15+ min")
)

nota_x_espera = (
    pesquisa_limpa.where(~F.col("dq_nota_invalida"))
    .join(hora_espera, "id_chamado", "inner")
    .where(F.col("tempo_espera_s").isNotNull())
    .withColumn("faixa_espera", faixa_espera)
    .groupBy("faixa_espera")
    .agg(F.avg("nota").alias("nota_media"), F.count("*").alias("respostas"))
)
display(nota_x_espera)

# COMMAND ----------

# MAGIC %md
# MAGIC ## e) Cruzamento custo x satisfação
# MAGIC Custo médio por nota e por canal, para identificar onde o custo alto **não** traz nota alta.

# COMMAND ----------

custo_nota = base_custo_dim.join(
    pesquisa_limpa.where(~F.col("dq_nota_invalida")).select("id_chamado", "nota"), "id_chamado", "inner"
)

print("Custo médio por nota:")
display(custo_nota.groupBy("nota").agg(F.avg("custo_total").alias("custo_medio"), F.count("*").alias("chamados")))

print("Custo médio e nota média por canal, lado a lado:")
custo_canal = base_custo_dim.groupBy("canal_key").agg(F.avg("custo_total").alias("custo_medio"))
nota_canal = base_nota_dim.groupBy("canal_key").agg(F.avg("nota").alias("nota_media"))
display(custo_canal.join(nota_canal, "canal_key", "outer").orderBy(F.desc("custo_medio")))

# COMMAND ----------

# MAGIC %md
# MAGIC ## f) Resumo
# MAGIC
# MAGIC | Métrica | Valor de referência (execução local — reconferir aqui) |
# MAGIC |---|---|
# MAGIC | Custos únicos (após dedup por `id_custo`) | 130.288 |
# MAGIC | Custo total | R$ 1.447.671,52 |
# MAGIC | Custos ≤ 0 | ~544 |
# MAGIC | Custo médio por chamado | ~R$ 11, estável de jan/25 (~4,4 mil chamados/mês) a jul/26 (~9,6 mil chamados/mês) |
# MAGIC | CSAT | ~86% em jan/2025 caindo para ~57% em jul/2026 |
# MAGIC | Custo médio por canal | URA ~R$ 1,84 · Chatbot ~R$ 0,57 · Atendimento Inicial ~R$ 13,60 · Especializado ~R$ 48,68 |
# MAGIC | Taxa de resposta à pesquisa | ~55,7% |
# MAGIC
# MAGIC ### Pontos a validar com o grupo
# MAGIC - Custo ≤ 0: estorno real ou erro de lançamento? Hoje entra na soma, só com flag.
# MAGIC - "Nota x tempo de espera" não corrige o erro de ano na abertura (isso é do notebook de `chamados_hora_juan.py`);
# MAGIC   os casos afetados (~198) são excluídos por ordem inválida, não corrigidos.
# MAGIC - CSAT e custo mensal usam o mês de **finalização**, não de abertura — confirmar que o grupo concorda
# MAGIC   com essa referência temporal para o painel.
# MAGIC - Custo médio por canal/motivo/nível usa a dedupe de `chamados` por `id_chamado` (2.636 duplicatas
# MAGIC   removidas) e soma de custos por chamado — confirmar que não há chamado com múltiplos lançamentos de
# MAGIC   custo relevantes sendo diluídos nessa soma.
