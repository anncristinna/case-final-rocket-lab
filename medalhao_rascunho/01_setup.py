# Databricks notebook source
# MAGIC %md
# MAGIC # 01 · Setup (rodar uma vez)
# MAGIC Cria os schemas do medalhão e os Volumes. Depois, suba os 8 CSVs para o Volume `raw`
# MAGIC (*Catalog → workspace → vcredit_bronze → Volumes → raw → Upload*).
# MAGIC É idempotente: `IF NOT EXISTS`.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

for schema in (SCHEMA_BRONZE, SCHEMA_SILVER, SCHEMA_GOLD):
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{schema}")

spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA_BRONZE}.raw")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA_GOLD}.exports")

display(spark.sql(f"SHOW SCHEMAS IN {CATALOG}"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conferência dos arquivos no Volume `raw`

# COMMAND ----------

import os

presentes = set(os.listdir(VOLUME_RAW)) if os.path.exists(VOLUME_RAW) else set()
for arquivo in SOURCES:
    print(("OK       " if arquivo in presentes else "FALTANDO ") + arquivo)

faltando = [a for a in SOURCES if a not in presentes]
if faltando:
    print(f"\nSuba os {len(faltando)} arquivo(s) faltante(s) para {VOLUME_RAW} antes de rodar a bronze.")
