# Databricks notebook source
# MAGIC %md
# MAGIC # 00 · Configuração compartilhada
# MAGIC Constantes usadas pelos demais notebooks via `%run ./00_config`.
# MAGIC Altere aqui (e só aqui) catálogo, schemas e caminhos.

# COMMAND ----------

CATALOG = "workspace"            # catálogo padrão do Databricks Free Edition
SCHEMA_BRONZE = "vcredit_bronze"
SCHEMA_SILVER = "vcredit_silver"
SCHEMA_GOLD = "vcredit_gold"

# Volumes (Unity Catalog) para arquivos
VOLUME_RAW = f"/Volumes/{CATALOG}/{SCHEMA_BRONZE}/raw"          # CSVs originais
VOLUME_EXPORTS = f"/Volumes/{CATALOG}/{SCHEMA_GOLD}/exports"    # CSVs da gold (Power BI)

# Arquivo -> (tabela bronze, encoding). Nomes de arquivo exatamente como entregues.
# Os arquivos de clientes e Chamados_Hora estão em cp1252. O leitor de CSV do Spark não aceita
# "windows-1252", então usamos "iso-8859-1": para letras acentuadas do português é idêntico.
SOURCES = {
    "chamados.csv":            ("chamados",            "utf-8"),
    "Chamados_Hora.CSV":       ("chamados_hora",       "iso-8859-1"),
    "clientes.csv":            ("clientes",            "iso-8859-1"),
    "custos.csv":              ("custos",              "utf-8"),
    "pesquisa_satisfacao.csv": ("pesquisa_satisfacao", "utf-8"),
    "base_atendentes.csv":     ("base_atendentes",     "utf-8"),
    "base_motivos.csv":        ("base_motivos",        "utf-8"),
    "canais.csv":              ("canais",              "utf-8"),
}

# Sal usado para anonimizar o id do cliente (CPF) na gold. Não é um segredo forte:
# serve apenas para que o hash não seja revertido por tabela-arco-íris simples.
HASH_SALT = "vcredit-rocketlab-2026"

print("Config carregada:", CATALOG, SCHEMA_BRONZE, SCHEMA_SILVER, SCHEMA_GOLD)
