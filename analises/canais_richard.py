# Databricks notebook source
# MAGIC %md
# MAGIC # Canais — Richard
# MAGIC Tabela: `canais` (e `chamados.canal` para o cruzamento). 4 canais cadastrados: URA e Chatbot
# MAGIC (Autosserviço), Atendimento Inicial e Atendimento Especializado (Humano).
# MAGIC
# MAGIC Números abaixo vêm de uma execução local anterior sobre os CSVs completos — reconfirmar ao rodar aqui.

# COMMAND ----------

# MAGIC %run ./_carga_dados

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verificação básica

# COMMAND ----------

from pyspark.sql import functions as F

print("linhas canais:", df_canais.count())
df_canais.printSchema()
df_canais.select("nome_canal", "tipo_canal").show(truncate=False)

print("grafias distintas em chamados.canal:")
df_chamados.select(F.trim("canal").alias("canal")).distinct().show(20, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Problemas já conhecidos nesta tabela (confirmar aqui)
# MAGIC - `chamados.canal` tem 8 grafias para os 4 canais cadastrados, incluindo `U.R.A`, `Chat Bot`,
# MAGIC   `Atend. Inicial`, `Atend. Especializado` — cerca de 15% das linhas fora do padrão (medido localmente).
# MAGIC   Usar `norm_key` + `CANAL_ALIAS` (de `_carga_dados.py`) para casar com o cadastro.
# MAGIC - `chamados` tem 2.636 `id_chamado` duplicados (idênticos) — medido localmente.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Perguntas sugeridas (TODO)
# MAGIC - Volume, resolução, custo médio e abandono por canal.
# MAGIC - Funil do enunciado: Prevenção > Autosserviço > Nível 1 > Nível 2.
# MAGIC - Quanto do volume atual poderia migrar para o autosserviço (URA/Chatbot).
