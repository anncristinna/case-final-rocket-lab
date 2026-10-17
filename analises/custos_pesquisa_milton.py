# Databricks notebook source
# MAGIC %md
# MAGIC # Custos e pesquisa de satisfação — Milton
# MAGIC Tabelas: `custos`, `pesquisa_satisfacao` (e `chamados`/`chamados_hora` para os cruzamentos).
# MAGIC
# MAGIC Números abaixo vêm de uma execução local anterior sobre os CSVs completos — reconfirmar ao rodar aqui.

# COMMAND ----------

# MAGIC %run ./_carga_dados

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verificação básica

# COMMAND ----------

from pyspark.sql import functions as F

for nome, df in [("custos", df_custos), ("pesquisa_satisfacao", df_pesquisa)]:
    print(nome, "linhas:", df.count())
    df.printSchema()
    (
        df.select([F.count(F.when(F.col(c).isNull() | (F.trim(F.col(c)) == ""), c)).alias(c) for c in df.columns])
          .show(truncate=False)
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Problemas já conhecidos nesta tabela (confirmar aqui)
# MAGIC - `custo` vem em pelo menos 8 formatos de texto (`9,99`, `99.99`, `R$ 9,99`, `9.99reais`, negativos...);
# MAGIC   cuidado ao limpar: remover todo ponto indiscriminadamente infla o total (erro do notebook inicial do Juan).
# MAGIC - `custos` tem 781 linhas duplicadas (idênticas) por `id_custo` (medido localmente).
# MAGIC - ~544 custos são ≤ 0 (negativos ou zero) — decidir com o grupo se entram na soma.
# MAGIC - ~1.550 chamados não têm nenhum lançamento de custo (medido localmente).
# MAGIC - `nota_atendimento` só é válida de 1 a 5; `-1`, `0`, `6` e vazio aparecem nos dados (~6.899 linhas,
# MAGIC   medido localmente).
# MAGIC - ~802 chamados têm mais de uma pesquisa registrada.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Perguntas sugeridas (TODO)
# MAGIC - Custo total e custo mensal, separando efeito de volume do efeito de custo unitário.
# MAGIC - Custo médio por canal, motivo e nível do atendente; quais motivos/canais concentram o gasto.
# MAGIC - Quanto custa, em média, um chamado atendido no nível 2 vs. nível 1.
# MAGIC - CSAT (% notas 4 e 5) por mês, canal, nível, motivo e resolução; taxa de resposta e risco de viés
# MAGIC   (quem responde pode não representar todo mundo).
# MAGIC - Relação da nota com tempo de espera, tempo de atendimento e abandono (tempos calculados pelos
# MAGIC   timestamps de `chamados_hora`, nunca pelo campo `tempo_atendimento` de `chamados`).
# MAGIC - Testar a fala do Marketing: CSAT era ~85% em jan/25 e a piora seria externa — a queda é igual em
# MAGIC   todos os canais ou concentrada em algum?
# MAGIC - Uma recomendação com ganho quantificado e premissas explícitas (ex.: custo evitável ao reduzir
# MAGIC   escalonamento para o nível 2).
