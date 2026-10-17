# Databricks notebook source
# MAGIC %md
# MAGIC # Carga compartilhada dos CSVs
# MAGIC `%run ./_carga_dados` a partir do notebook de cada responsável. Carrega os 8 CSVs **sem inferSchema**
# MAGIC (tudo como `string`; cada análise faz o cast explícito do que precisar) e expõe:
# MAGIC `df_chamados`, `df_chamados_hora`, `df_clientes`, `df_custos`, `df_pesquisa`, `df_canais`,
# MAGIC `df_motivos`, `df_atendentes`.
# MAGIC
# MAGIC Também expõe funções reutilizáveis (aproveitadas de `medalhao_rascunho/03_silver.py`):
# MAGIC `norm_key`, `blank_to_null`, `add_try` e o mapa `CANAL_ALIAS`.
# MAGIC
# MAGIC Contagens esperadas (medidas numa execução local; reconfirmar aqui): chamados 134.474 ·
# MAGIC chamados_hora 131.838 · clientes 47.705 · custos 131.069 · pesquisa_satisfacao 81.021 ·
# MAGIC base_atendentes 25 · base_motivos 14 · canais 4.

# COMMAND ----------

dbutils.widgets.text("base_path", "")
BASE_PATH = dbutils.widgets.get("base_path")

if not BASE_PATH:
    raise ValueError(
        "Preencha o widget 'base_path'. Exemplos: "
        "'/Workspace/Users/<seu-email>/projeto final/dados' (Workspace) ou "
        "'/Volumes/<catalogo>/<schema>/<volume>' (Volume do Unity Catalog)."
    )

# Volumes já são um caminho de arquivo nativo; outros caminhos (Workspace) precisam do prefixo file://
_prefixo = "" if BASE_PATH.startswith("/Volumes") else "file://"

# COMMAND ----------

from pyspark.sql import functions as F

# Arquivo -> (nome da tabela, encoding). Nomes de arquivo exatamente como entregues.
# clientes.csv e Chamados_Hora.CSV estão em ISO-8859-1 (NÃO ler como UTF-8); os demais, UTF-8.
_FONTES = {
    "chamados.csv":            ("chamados",            "UTF-8"),
    "Chamados_Hora.CSV":       ("chamados_hora",       "ISO-8859-1"),
    "clientes.csv":            ("clientes",            "ISO-8859-1"),
    "custos.csv":              ("custos",              "UTF-8"),
    "pesquisa_satisfacao.csv": ("pesquisa_satisfacao", "UTF-8"),
    "base_atendentes.csv":     ("base_atendentes",     "UTF-8"),
    "base_motivos.csv":        ("base_motivos",        "UTF-8"),
    "canais.csv":              ("canais",              "UTF-8"),
}

_tabelas = {}
_contagens = []

for arquivo, (nome, encoding) in _FONTES.items():
    caminho = f"{_prefixo}{BASE_PATH}/{arquivo}"

    leitor = (
        spark.read
        .option("header", True)
        .option("inferSchema", False)  # tudo string; cast explícito em cada análise
        .option("encoding", encoding)
    )
    # Chamados_Hora.CSV não tem aspas; os demais seguem o padrão CSV com aspas duplas
    if arquivo != "Chamados_Hora.CSV":
        leitor = leitor.option("quote", '"').option("escape", '"')

    df = leitor.csv(caminho)

    for antigo in df.columns:
        novo = antigo.replace("﻿", "").strip().lower()
        if novo != antigo:
            df = df.withColumnRenamed(antigo, novo)

    _tabelas[nome] = df
    _contagens.append((nome, df.count()))

df_chamados = _tabelas["chamados"]
df_chamados_hora = _tabelas["chamados_hora"]
df_clientes = _tabelas["clientes"]
df_custos = _tabelas["custos"]
df_pesquisa = _tabelas["pesquisa_satisfacao"]
df_atendentes = _tabelas["base_atendentes"]
df_motivos = _tabelas["base_motivos"]
df_canais = _tabelas["canais"]

for nome, linhas in _contagens:
    print(f"{nome}: {linhas:,} linhas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Funções reutilizáveis

# COMMAND ----------

_ACC_FROM = "áàâãäéèêëíìîïóòôõöúùûüçñ"
_ACC_TO = "aaaaaeeeeiiiiooooouuuucn"


def norm_key(c):
    """Chave de comparação: minúsculo, sem acento, '_'/'-' viram espaço, espaços colapsados."""
    x = F.translate(F.lower(F.trim(c)), _ACC_FROM, _ACC_TO)
    x = F.regexp_replace(x, r"[_\-]+", " ")
    x = F.regexp_replace(x, r"\s+", " ")
    return F.trim(x)


def blank_to_null(c):
    return F.when(F.trim(c) == "", F.lit(None)).otherwise(F.trim(c))


def add_try(df, out, col, kind, fmt=None):
    """Adiciona coluna `out` = conversão segura (null se inválida). kind: int|double|date|ts."""
    tmp = f"__{out}_tmp"
    d = df.withColumn(tmp, col)
    if kind == "date":
        e = f"cast(try_to_timestamp(`{tmp}`, '{fmt}') as date)"
    elif kind == "ts":
        e = f"try_to_timestamp(`{tmp}`, '{fmt}')"
    else:
        e = f"try_cast(`{tmp}` as {kind})"
    return d.withColumn(out, F.expr(e)).drop(tmp)


# Variações de grafia de canal observadas em chamados.canal (ex.: "U.R.A", "Chat Bot", "Atend. Inicial")
CANAL_ALIAS = {
    "u.r.a": "ura",
    "chat bot": "chatbot",
    "atend. inicial": "atendimento inicial",
    "atend. especializado": "atendimento especializado",
}
