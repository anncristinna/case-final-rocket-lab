# Databricks notebook source
# MAGIC %md
# MAGIC # Chamados (horários) — Juan
# MAGIC Tabela: `chamados_hora` (timestamps de abertura/início/fim — a fonte da verdade dos tempos,
# MAGIC ver `CLAUDE.md`). `chamados.tempo_atendimento` está truncado para durações ≥ 1.000 s: calcular
# MAGIC os tempos pelos timestamps, nunca usar o campo original em KPI.
# MAGIC
# MAGIC Números abaixo vêm de uma execução local anterior sobre os CSVs completos — reconfirmar ao rodar aqui.

# COMMAND ----------

# MAGIC %run ./_carga_dados

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verificação básica

# COMMAND ----------

from pyspark.sql import functions as F

print("linhas:", df_chamados_hora.count())
df_chamados_hora.printSchema()

(
    df_chamados_hora
    .select([F.count(F.when(F.col(c).isNull() | (F.trim(F.col(c)) == ""), c)).alias(c) for c in df_chamados_hora.columns])
    .show(truncate=False)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Problemas já conhecidos nesta tabela (confirmar aqui)
# MAGIC - Timestamps no formato `dd/MM/yyyy às HH:mm:ss` — o conector "às" precisa ser removido por regex
# MAGIC   (tolerar caractere corrompido pelo encoding) antes do parse.
# MAGIC - ~198 chamados (medido localmente) têm o **ano da abertura errado** (+1 ou +2 anos), com início/fim corretos.
# MAGIC - ~3.414 chamados (medido localmente) não têm hora de início de atendimento: espera registrada e sem
# MAGIC   atendimento = **abandono** (cliente desistiu na fila).
# MAGIC - Os tempos devem ser calculados pelos próprios timestamps, porque `chamados.tempo_atendimento` está
# MAGIC   truncado para valores ≥ 1.000 s (subestima o TMA humano, ver `achados_qualidade_dados.md`).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Perguntas sugeridas (TODO)
# MAGIC - TME e TMA por mês, canal e hora do dia.
# MAGIC - Abandono por canal e por mês.
# MAGIC - Picos de demanda (dia da semana, hora).
