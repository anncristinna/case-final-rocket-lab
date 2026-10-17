# Databricks notebook source
# MAGIC %md
# MAGIC # 02 · Bronze — ingestão fiel à origem
# MAGIC - Lê cada CSV do Volume `raw` com o **encoding correto** (`clientes` e `Chamados_Hora` são cp1252).
# MAGIC - **Tudo como string**: nenhuma correção de conteúdo aqui (isso é papel da silver).
# MAGIC - Colunas em minúsculo; acrescenta `_ingestion_ts` e `_source_file` para rastreabilidade.
# MAGIC - **Idempotente**: `overwrite` da tabela inteira; rodar de novo gera o mesmo resultado.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

from pyspark.sql import functions as F

resumo = []

for arquivo, (tabela, encoding) in SOURCES.items():
    caminho = f"{VOLUME_RAW}/{arquivo}"

    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", False)          # tudo string
        .option("encoding", encoding)
        .option("quote", '"')
        .option("escape", '"')
        .csv(caminho)
    )

    # padroniza nomes de coluna (remove BOM/espaços, minúsculo)
    for antigo in df.columns:
        novo = antigo.replace("﻿", "").strip().lower()
        if novo != antigo:
            df = df.withColumnRenamed(antigo, novo)

    df = (
        df.withColumn("_ingestion_ts", F.current_timestamp())
          .withColumn("_source_file", F.lit(arquivo))
    )

    destino = f"{CATALOG}.{SCHEMA_BRONZE}.{tabela}"
    (df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(destino))

    linhas = spark.table(destino).count()
    resumo.append((tabela, arquivo, encoding, linhas))
    print(f"{destino}: {linhas:,} linhas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Controle
# MAGIC Contagens esperadas (arquivos originais): chamados 134.474 · chamados_hora 131.838 · clientes 47.705 ·
# MAGIC custos 131.069 · pesquisa_satisfacao 81.021 · base_atendentes 25 · base_motivos 14 · canais 4.

# COMMAND ----------

display(spark.createDataFrame(resumo, ["tabela", "arquivo", "encoding", "linhas"]))
