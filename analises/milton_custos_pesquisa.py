# Databricks notebook source
# MAGIC %md
# MAGIC # Custos e pesquisa de satisfação — Milton
# MAGIC Tabelas: `custos`, `pesquisa_satisfacao`. Faz `%run` no notebook base (carga, limpeza, `base`
# MAGIC consolidada) e reaproveita a limpeza de lá — não refaz dedup/normalização aqui.
# MAGIC
# MAGIC Valores de referência vêm de uma execução local anterior sobre os CSVs completos — **reconfira e
# MAGIC sinalize qualquer diferença** ao rodar aqui. Nenhuma célula imprime `id_cliente`, nome ou e-mail.

# COMMAND ----------

# MAGIC %run ./analise_geral_corrigida

# COMMAND ----------

from pyspark.sql import Window

# COMMAND ----------

# MAGIC %md
# MAGIC ## a) Custos — qualidade e a decisão pendente sobre custo ≤ 0
# MAGIC `custos` (já limpo e deduplicado pelo notebook base) tem a flag `dq_custo_nao_positivo`. Mostramos
# MAGIC as **duas versões** do total — incluir ou excluir é decisão do grupo, não decidimos aqui.

# COMMAND ----------

print("custos únicos:", f"{custos.count():,}")

_validos = custos.where(~F.col("dq_custo_invalido"))
total_incluindo = _validos.agg(F.sum("custo")).first()[0]
total_excluindo = _validos.where(F.col("custo") > 0).agg(F.sum("custo")).first()[0]
qtd_nao_positivos = custos.where(F.col("dq_custo_nao_positivo")).count()
qtd_negativos = custos.where(F.col("custo") < 0).count()
qtd_zero = custos.where(F.col("custo") == 0).count()

display(
    spark.createDataFrame(
        [
            ("Incluindo custo <= 0 (mantido com flag)", float(total_incluindo)),
            ("Excluindo custo <= 0 (tratado como estorno/erro)", float(total_excluindo)),
        ],
        ["cenario", "custo_total"],
    )
)
print(f"custo <= 0: {qtd_nao_positivos:,} lançamentos ({qtd_negativos:,} negativos + {qtd_zero:,} zero)")

chamados_sem_custo = chamados.join(_validos, "id_chamado", "left_anti")
print("chamados sem custo:", f"{chamados_sem_custo.count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## b) Custo mensal x volume de chamados

# COMMAND ----------

_janela_mes = Window.orderBy("mes").rowsBetween(Window.unboundedPreceding, 0)
# qtd_chamados = volume TOTAL do mês (inclui quem não tem custo lançado); qtd_lancamentos = só quem tem
# custo. custo_medio_por_chamado divide pelo volume total, não só por quem tem lançamento.
_volume_mes = base.where(F.col("mes").isNotNull()).groupBy("mes").agg(F.count("*").alias("qtd_chamados"))
_custo_mes = (
    base.where(F.col("custo").isNotNull() & F.col("mes").isNotNull())
    .groupBy("mes")
    .agg(F.sum("custo").alias("custo_total"), F.count("*").alias("qtd_lancamentos"))
)
evolucao_mensal = (
    _custo_mes.join(_volume_mes, "mes", "left")
    .withColumn("custo_medio_por_chamado", F.col("custo_total") / F.col("qtd_chamados"))
    .withColumn("custo_acumulado", F.sum("custo_total").over(_janela_mes))
    .orderBy("mes")
)
display(evolucao_mensal)

# COMMAND ----------

# MAGIC %md
# MAGIC ## c) Custo por canal, motivo, categoria e nível do atendente

# COMMAND ----------

print("Custo médio por canal:")
display(base.groupBy("canal_key").agg(F.avg("custo").alias("custo_medio"), F.count("*").alias("chamados")).orderBy(F.desc("custo_medio")))

print("Custo médio por motivo:")
display(base.groupBy("motivo_key").agg(F.avg("custo").alias("custo_medio"), F.count("*").alias("chamados")).orderBy(F.desc("custo_medio")))

print("Custo médio por categoria do motivo:")
display(base.groupBy("categoria").agg(F.avg("custo").alias("custo_medio"), F.count("*").alias("chamados")).orderBy(F.desc("custo_medio")))

print("Custo médio por nível do atendente:")
display(base.groupBy("nivel_atendente").agg(F.avg("custo").alias("custo_medio"), F.count("*").alias("chamados")).orderBy("nivel_atendente"))

custo_nivel1 = base.where(F.col("nivel_atendente") == 1).agg(F.avg("custo")).first()[0]
custo_nivel2 = base.where(F.col("nivel_atendente") == 2).agg(F.avg("custo")).first()[0]
diff_escalonamento = custo_nivel2 - custo_nivel1
print(f"\ndiferença nível 2 - nível 1 (proxy de custo de escalonamento): R$ {diff_escalonamento:,.2f} ({custo_nivel2/custo_nivel1:,.1f}x)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## d) Pareto: motivos e canais que concentram o gasto

# COMMAND ----------

def _pareto(chave):
    tmp = base.groupBy(chave).agg(F.sum("custo").alias("custo"), F.count("*").alias("chamados")).where(F.col("custo").isNotNull())
    total = tmp.agg(F.sum("custo")).first()[0]
    janela = Window.orderBy(F.desc("custo")).rowsBetween(Window.unboundedPreceding, 0)
    return (
        tmp.orderBy(F.desc("custo"))
        .withColumn("custo_acumulado", F.sum("custo").over(janela))
        .withColumn("pct_acumulado", F.col("custo_acumulado") / F.lit(total))
    )


print("Pareto por motivo:")
display(_pareto("motivo_key"))
print("Pareto por canal:")
display(_pareto("canal_key"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## e) Pesquisa de satisfação — qualidade
# MAGIC `pesquisa` (do notebook base) já deduplica priorizando a nota válida quando o chamado tem mais de
# MAGIC uma pesquisa. `pesquisa_bruta` (também do notebook base) ainda tem todas as linhas do arquivo.

# COMMAND ----------

print(f"pesquisas (arquivo): {pesquisa_bruta.count():,}")
print(f"notas inválidas (arquivo, antes de deduplicar): {pesquisa_bruta.where('dq_nota_invalida').count():,}")
print(f"pesquisas únicas por chamado: {pesquisa.count():,}")
print(f"notas inválidas após dedup: {pesquisa.where('dq_nota_invalida').count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## f) Taxa de resposta — geral, por mês e por canal

# COMMAND ----------

taxa_resposta_geral = base.where(F.col("nota").isNotNull()).count() / chamados.count()
print(f"taxa de resposta geral: {taxa_resposta_geral:.1%}")

print("Taxa de resposta por mês:")
display(
    base.where(F.col("mes").isNotNull())
    .groupBy("mes")
    .agg(F.count("*").alias("chamados"), F.count("nota").alias("respostas"))
    .withColumn("taxa_resposta", F.col("respostas") / F.col("chamados"))
    .orderBy("mes")
)

print("Taxa de resposta por canal:")
display(
    base.groupBy("canal_key")
    .agg(F.count("*").alias("chamados"), F.count("nota").alias("respostas"))
    .withColumn("taxa_resposta", F.col("respostas") / F.col("chamados"))
    .orderBy(F.desc("taxa_resposta"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## g) CSAT por mês, canal, nível, motivo, categoria e resolução

# COMMAND ----------

print("CSAT mensal:")
display(
    base.where(F.col("nota").isNotNull() & F.col("mes").isNotNull())
    .groupBy("mes")
    .agg(F.count("*").alias("respostas"), F.avg((F.col("nota") >= 4).cast("int")).alias("csat"))
    .orderBy("mes")
)


def _csat(chave):
    return (
        base.where(F.col("nota").isNotNull())
        .groupBy(chave)
        .agg(F.count("*").alias("respostas"), F.avg("nota").alias("nota_media"), F.avg((F.col("nota") >= 4).cast("int")).alias("csat"))
        .orderBy(F.desc("csat"))
    )


for _chave, _titulo in [("canal_key", "canal"), ("nivel_atendente", "nível"), ("motivo_key", "motivo"), ("categoria", "categoria"), ("resolvido", "resolução")]:
    print(f"CSAT por {_titulo}:")
    display(_csat(_chave))

# COMMAND ----------

# MAGIC %md
# MAGIC ## h) Nota x tempo de espera, x TMA e x abandono

# COMMAND ----------

_faixa_tme = (
    F.when(F.col("tempo_espera_s") <= 60, "0-1 min")
     .when(F.col("tempo_espera_s") <= 300, "1-5 min")
     .when(F.col("tempo_espera_s") <= 900, "5-15 min")
     .otherwise("15+ min")
)
_faixa_tma = (
    F.when(F.col("tempo_atendimento_s") <= 120, "0-2 min")
     .when(F.col("tempo_atendimento_s") <= 300, "2-5 min")
     .when(F.col("tempo_atendimento_s") <= 900, "5-15 min")
     .otherwise("15+ min")
)

print("Nota x faixa de TME:")
display(
    base.where(F.col("nota").isNotNull() & F.col("tempo_espera_s").isNotNull())
    .withColumn("faixa_tme", _faixa_tme)
    .groupBy("faixa_tme")
    .agg(F.avg("nota").alias("nota_media"), F.avg((F.col("nota") >= 4).cast("int")).alias("csat"), F.count("*").alias("respostas"))
)

print("Nota x faixa de TMA:")
display(
    base.where(F.col("nota").isNotNull() & F.col("tempo_atendimento_s").isNotNull())
    .withColumn("faixa_tma", _faixa_tma)
    .groupBy("faixa_tma")
    .agg(F.avg("nota").alias("nota_media"), F.avg((F.col("nota") >= 4).cast("int")).alias("csat"), F.count("*").alias("respostas"))
)

print("Resposta e nota por situação de abandono:")
display(
    base.groupBy("abandonado")
    .agg(F.count("*").alias("chamados"), F.count("nota").alias("respostas"), F.avg("nota").alias("nota_media"))
    .withColumn("taxa_resposta", F.col("respostas") / F.col("chamados"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## i) Testando a fala do Marketing: "CSAT era 85% em jan/25; a piora é externa"

# COMMAND ----------

csat_canal_mes = (
    base.where(F.col("nota").isNotNull() & F.col("mes").isNotNull())
    .groupBy("mes", "canal_key")
    .agg(F.avg((F.col("nota") >= 4).cast("int")).alias("csat"))
)
_primeiro_mes = csat_canal_mes.agg(F.min("mes")).first()[0]
_ultimo_mes = csat_canal_mes.agg(F.max("mes")).first()[0]
print(f"comparando {_primeiro_mes} com {_ultimo_mes}:")
display(
    csat_canal_mes.where(F.col("mes").isin(_primeiro_mes, _ultimo_mes))
    .groupBy("canal_key")
    .pivot("mes", [_primeiro_mes, _ultimo_mes])
    .agg(F.first("csat"))
    .orderBy("canal_key")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## j) Cruzamento custo x satisfação

# COMMAND ----------

print("Custo médio por nota:")
display(base.where(F.col("nota").isNotNull()).groupBy("nota").agg(F.avg("custo").alias("custo_medio"), F.count("*").alias("chamados")).orderBy("nota"))

print("Custo médio e nota média por canal, lado a lado:")
display(
    base.groupBy("canal_key")
    .agg(F.avg("custo").alias("custo_medio"), F.avg("nota").alias("nota_media"))
    .orderBy(F.desc("custo_medio"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## k) Recomendação quantificada: reduzir o escalonamento para o nível 2
# MAGIC Premissas: `nivel_atendente` é proxy de "chamado escalado" (não há registro explícito de
# MAGIC escalonamento no dataset); `p%` de chamados evitáveis é hipótese do grupo, não medida nos dados;
# MAGIC ganho é bruto (não inclui custo do treinamento/script).

# COMMAND ----------

chamados_nivel2 = base.where(F.col("nivel_atendente") == 2).count()
print(f"chamados no nível 2: {chamados_nivel2:,} | diferença de custo nível 2 - nível 1: R$ {diff_escalonamento:,.2f}\n")

for nome, pct in [("conservador", 0.05), ("base", 0.15), ("otimista", 0.25)]:
    evitaveis = chamados_nivel2 * pct
    ganho = evitaveis * diff_escalonamento
    print(f"{nome:>12}: {pct:.0%} de {chamados_nivel2:,} = {evitaveis:,.0f} chamados evitáveis x R$ {diff_escalonamento:,.2f} = R$ {ganho:,.2f}")
