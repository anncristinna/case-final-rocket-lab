# Databricks notebook source
# MAGIC %md
# MAGIC # Atendentes e motivos — Cris
# MAGIC Tabelas: `base_atendentes`, `base_motivos` (e `chamados` para cruzar `id_atendente`/motivo).
# MAGIC
# MAGIC Números abaixo vêm de uma execução local anterior sobre os CSVs completos — reconfirmar ao rodar aqui.

# COMMAND ----------

# MAGIC %run ./_carga_dados

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verificação básica

# COMMAND ----------

from pyspark.sql import functions as F

for nome, df in [("base_atendentes", df_atendentes), ("base_motivos", df_motivos)]:
    print(nome, "linhas:", df.count())
    df.printSchema()
    (
        df.select([F.count(F.when(F.col(c).isNull() | (F.trim(F.col(c)) == ""), c)).alias(c) for c in df.columns])
          .show(truncate=False)
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Problemas já conhecidos nesta tabela (confirmar aqui)
# MAGIC - `nivel_atendimento` com 5 grafias diferentes para 2 níveis: `1`, `Nível 1`, `2`, `N2`, `Nível 2`.
# MAGIC - Só 20 dos 25 atendentes estão `ativo` (medido localmente).
# MAGIC - `chamados.id_atendente` tem placeholders `0`, `99` e `999` que não existem no cadastro
# MAGIC   (~764 chamados na execução local) — não são atendentes reais.
# MAGIC - `base_motivos.categoria` vem vazia nos ids 14 (Transferência de agência), 16 (Cancelamento de conta)
# MAGIC   e 12 (Contratação de cartão adicional).
# MAGIC - `criticidade` em `base_motivos` com caixa mista (ex.: `Alta`, `alta`, `ALTA`).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Perguntas sugeridas (TODO)
# MAGIC - Taxa de resolução e TMA por atendente e por nível de atendimento.
# MAGIC - Atendentes recém-admitidos vs. antigos: diferença de resolução/TMA.
# MAGIC - Quais motivos mais escalam para o nível 2.
# MAGIC - Atendimentos registrados fora do período admissão/desligamento do atendente (sinal de erro de cadastro).
