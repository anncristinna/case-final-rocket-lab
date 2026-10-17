# Databricks notebook source
# MAGIC %md
# MAGIC # Base — carga, limpeza e panorama geral
# MAGIC **Notebook base, único, mudado só por PR combinado e revisado pelo grupo** (evita conflito de
# MAGIC merge de várias pessoas editando o mesmo arquivo). Cada pessoa explora o seu tema no Databricks do
# MAGIC jeito que preferir — copiando este notebook, fazendo `%run` nele, ou outro notebook à parte — e leva
# MAGIC o resultado final pro `.md` correspondente em `analises/` (ver `analises/README.md`), nunca pro
# MAGIC Notion direto do notebook. Aqui ficam definidos `chamados`, `custos`, `pesquisa`, `horarios`,
# MAGIC `atendentes`, `motivos`, `canais_dim`, `clientes` e `base` (a tabela consolidada, uma linha por
# MAGIC chamado) — reaproveite a limpeza daqui pra não divergir dos outros `.md`.
# MAGIC
# MAGIC Parte do notebook exploratório inicial do Juan (`Análise de Chamados Insights Primários.ipynb`,
# MAGIC mantido só localmente, fora do git — tem um e-mail pessoal embutido no `base_path`) e corrige os
# MAGIC problemas encontrados nele — tabela completa em `docs/achados_analise_geral.md`. Resumo:
# MAGIC
# MAGIC | # | Problema no original | Correção aqui |
# MAGIC |---|---|---|
# MAGIC | 1 | `inferSchema=True` — risco de perder zeros à esquerda do CPF (`id_cliente`) | leitura 100% `string`, cast explícito do que precisa |
# MAGIC | 2 | Limpeza de `custo` remove **todo ponto** → `23.24` virava `2324`, `74.71reais` virava `7471` → custo total R$ 42,2 mi | regra que só remove ponto de milhar quando há vírgula → custo total correto ~R$ 1,45 mi |
# MAGIC | 3 | `tempo_espera`/`tempo_atendimento` usados direto de `chamados`, rotulados como "min" | são **segundos**, e truncados para durações ≥ 1.000 s — tempos vêm de `chamados_hora` |
# MAGIC | 4 | Notas de pesquisa -1/0/6 entram na média (só filtra nulo) | nota só é válida de 1 a 5, resto vira `null` + flag |
# MAGIC | 5 | 2.636 `id_chamado` duplicados e 781 `id_custo` duplicados não removidos | `dropDuplicates` antes de qualquer agregação — **repita isso em toda análise de tema**, senão os números não batem entre os `.md` |
# MAGIC | 6 | Não usa `chamados_hora`: sem abandono, sem correção do ano de abertura | abandono = sem hora de início; ano da abertura corrigido quando dá pra confirmar pela finalização |
# MAGIC
# MAGIC Nenhuma linha de `clientes` (CPF/nome/e-mail) é impressa em nenhuma análise.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Carga dos dados
# MAGIC Widget `base_path` sem valor padrão (pra não embutir caminho/e-mail de ninguém).
# MAGIC
# MAGIC ⚠️ **Tem que ser um Volume** (`/Volumes/<catalogo>/<schema>/<volume>`) — o Spark serverless do Free
# MAGIC Edition **não lê CSV de pasta do Workspace** (`/Workspace/...`) com `spark.read`, só de Volume.
# MAGIC Suba os 8 CSVs num Volume do Unity Catalog antes de rodar (ex.: *Catalog → criar Volume → Upload*;
# MAGIC combinar com o grupo quem sobe os arquivos e qual o caminho exato, e anotar aqui).

# COMMAND ----------

dbutils.widgets.text("base_path", "")
BASE_PATH = dbutils.widgets.get("base_path")
if not BASE_PATH:
    raise ValueError("Preencha o widget 'base_path' com um caminho de Volume: '/Volumes/<catalogo>/<schema>/<volume>'.")
if not BASE_PATH.startswith("/Volumes"):
    raise ValueError(
        f"'{BASE_PATH}' não é um Volume. O Spark serverless não lê CSV de pasta do Workspace — "
        "suba os CSVs num Volume do Unity Catalog e use '/Volumes/<catalogo>/<schema>/<volume>'."
    )

# COMMAND ----------

from pyspark.sql import functions as F, Window

# Arquivo -> (nome, encoding). clientes.csv e Chamados_Hora.CSV em ISO-8859-1; os demais UTF-8.
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
    caminho = f"{BASE_PATH}/{arquivo}"
    leitor = spark.read.option("header", True).option("inferSchema", False).option("encoding", encoding)
    if arquivo != "Chamados_Hora.CSV":  # Chamados_Hora.CSV não tem aspas
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
# MAGIC ## 2. Funções reutilizáveis

# COMMAND ----------

_ACC_FROM = "áàâãäéèêëíìîïóòôõöúùûüçñ"
_ACC_TO = "aaaaaeeeeiiiiooooouuuucn"


def norm_key(c):
    x = F.translate(F.lower(F.trim(c)), _ACC_FROM, _ACC_TO)
    x = F.regexp_replace(x, r"[_\-]+", " ")
    x = F.regexp_replace(x, r"\s+", " ")
    return F.trim(x)


def blank_to_null(c):
    return F.when(F.trim(c) == "", F.lit(None)).otherwise(F.trim(c))


def add_try(df, out, col, kind, fmt=None):
    tmp = f"__{out}_tmp"
    d = df.withColumn(tmp, col)
    if kind == "date":
        e = f"cast(try_to_timestamp(`{tmp}`, '{fmt}') as date)"
    elif kind == "ts":
        e = f"try_to_timestamp(`{tmp}`, '{fmt}')"
    else:
        e = f"try_cast(`{tmp}` as {kind})"
    return d.withColumn(out, F.expr(e)).drop(tmp)


CANAL_ALIAS = {
    "u.r.a": "ura",
    "chat bot": "chatbot",
    "atend. inicial": "atendimento inicial",
    "atend. especializado": "atendimento especializado",
}
_mapa_canal = F.create_map(*[F.lit(x) for kv in CANAL_ALIAS.items() for x in kv])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Limpeza

# COMMAND ----------

# MAGIC %md
# MAGIC ### Chamados
# MAGIC Dedup por `id_chamado` (2.636 duplicatas idênticas esperadas); `canal`/`motivo` normalizados;
# MAGIC `resolvido` em booleano; `id_atendente` com placeholder (`0`, `99`, `999`) flagado.

# COMMAND ----------

_canal_key_bruta = norm_key(F.col("canal"))
_res_key = norm_key(F.col("resolvido"))
_resolvido_bool = (
    F.when(_res_key.isin("sim", "s", "1", "true", "yes", "resolvido"), F.lit(True))
     .when(_res_key.isin("nao", "n", "0", "false", "nao resolvido"), F.lit(False))
)

_total_chamados_bruto = df_chamados.count()
chamados = (
    df_chamados.dropDuplicates(["id_chamado"])
    .select(
        F.trim("id_chamado").alias("id_chamado"),
        F.trim("id_cliente").alias("id_cliente"),
        F.coalesce(_mapa_canal[_canal_key_bruta], _canal_key_bruta).alias("canal_key"),
        norm_key(F.col("motivo")).alias("motivo_key"),
        F.trim("id_atendente").alias("id_atendente"),
        _resolvido_bool.alias("resolvido"),
    )
    .withColumn("dq_resolvido_invalido", F.col("resolvido").isNull())
    .withColumn("dq_atendente_invalido", F.col("id_atendente").isin("0", "99", "999") | F.col("id_atendente").isNull())
    .cache()
)
print(f"chamados: {_total_chamados_bruto:,} linhas no arquivo, {chamados.count():,} únicas por id_chamado "
      f"({_total_chamados_bruto - chamados.count():,} duplicatas removidas)")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Custos
# MAGIC Regra: manter só dígitos/`,`/`.`/`-`; só remove ponto de milhar quando há vírgula no resultado
# MAGIC (senão o ponto já é decimal). **Não remover todo ponto indiscriminadamente** — esse foi o erro do
# MAGIC notebook original (inflou o total para R$ 42,2 mi).

# COMMAND ----------

_bruto_custo = F.regexp_replace(F.trim(F.col("custo")), r"[^0-9,.\-]", "")
_numero_custo = F.when(
    _bruto_custo.contains(","),
    F.regexp_replace(F.regexp_replace(_bruto_custo, r"\.", ""), ",", "."),
).otherwise(_bruto_custo)

custos_tipado = add_try(df_custos.withColumn("_numero", _numero_custo), "custo", F.col("_numero"), "double")
custos = (
    custos_tipado
    .select(F.trim("id_custo").alias("id_custo"), F.trim("id_chamado").alias("id_chamado"), "custo")
    .withColumn("dq_custo_invalido", F.col("custo").isNull())
    .withColumn("dq_custo_nao_positivo", F.col("custo") <= 0)
    .dropDuplicates(["id_custo"])
    .cache()
)
print(f"custos únicos: {custos.count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Pesquisa de satisfação
# MAGIC Nota só é válida de 1 a 5 (`-1`, `0`, `6` e vazio viram `null` + flag — o original só filtrava nulo,
# MAGIC então a satisfação média saía contaminada por esses valores fora da faixa). Ao deduplicar por
# MAGIC `id_chamado`, prioriza a linha com nota válida quando existe mais de uma pesquisa pro mesmo chamado.

# COMMAND ----------

pesquisa_tipada = add_try(df_pesquisa, "nota_i", F.trim(F.col("nota_atendimento")), "int")
pesquisa_bruta = (
    pesquisa_tipada
    .select(
        F.trim("id_pesquisa").alias("id_pesquisa"),
        F.trim("id_chamado").alias("id_chamado"),
        F.when(F.col("nota_i").between(1, 5), F.col("nota_i")).alias("nota"),
    )
    .withColumn("dq_nota_invalida", F.col("nota").isNull())
)
_janela_pesquisa = Window.partitionBy("id_chamado").orderBy(F.col("nota").isNull().asc(), F.col("id_pesquisa").asc())
pesquisa = (
    pesquisa_bruta.withColumn("_rank", F.row_number().over(_janela_pesquisa))
    .where(F.col("_rank") == 1).drop("_rank")
    .cache()
)
print(f"pesquisas (arquivo): {pesquisa_bruta.count():,} | únicas por chamado: {pesquisa.count():,} "
      f"| notas inválidas (arquivo): {pesquisa_bruta.where('dq_nota_invalida').count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Chamados — horários (fonte da verdade dos tempos)
# MAGIC `chamados.tempo_espera`/`tempo_atendimento` são **segundos** (não "min") e truncados para durações
# MAGIC ≥ 1.000 s — por isso os tempos aqui vêm sempre de `chamados_hora`. ~198 chamados têm o **ano da
# MAGIC abertura errado** (+1/+2 anos); corrigimos comparando com a finalização. Abandono = sem hora de
# MAGIC início de atendimento (espera registrada, sem atendimento).

# COMMAND ----------

def _limpa_conector(col):
    return F.regexp_replace(F.trim(col), r"\s\S{1,3}\s", " ")


_hora = df_chamados_hora.withColumn("id_chamado", F.trim(F.col("id_chamado")))
_hora = add_try(_hora, "abertura_ts", _limpa_conector(F.col("hora_abertura_chamado")), "ts", "dd/MM/yyyy HH:mm:ss")
_hora = add_try(_hora, "inicio_ts", _limpa_conector(F.col("hora_inicio_atendimento")), "ts", "dd/MM/yyyy HH:mm:ss")
_hora = add_try(_hora, "fim_ts", _limpa_conector(F.col("hora_finalizacao_atendimento")), "ts", "dd/MM/yyyy HH:mm:ss")

_hora = _hora.withColumn(
    "_anos_erro",
    F.round((F.unix_timestamp("abertura_ts") - F.unix_timestamp("fim_ts")) / (365 * 86400)).cast("int"),
)
_hora = _hora.withColumn(
    "dq_abertura_corrigida",
    F.col("_anos_erro").isin(1, 2) & (F.col("abertura_ts") > F.col("fim_ts")),
)
_hora = _hora.withColumn(
    "abertura_ts",
    F.when(F.col("dq_abertura_corrigida"), F.expr("abertura_ts - make_interval(_anos_erro)")).otherwise(F.col("abertura_ts")),
)

horarios = (
    _hora
    .withColumn("dq_ordem_invalida", F.coalesce((F.col("inicio_ts") < F.col("abertura_ts")) | (F.col("fim_ts") < F.col("inicio_ts")), F.lit(False)))
    .withColumn("abandonado", F.col("inicio_ts").isNull())
    .withColumn("tempo_espera_s", F.when(~F.col("dq_ordem_invalida") & F.col("inicio_ts").isNotNull(), F.unix_timestamp("inicio_ts") - F.unix_timestamp("abertura_ts")))
    .withColumn("tempo_atendimento_s", F.when(~F.col("dq_ordem_invalida") & F.col("fim_ts").isNotNull() & F.col("inicio_ts").isNotNull(), F.unix_timestamp("fim_ts") - F.unix_timestamp("inicio_ts")))
    .withColumn("mes", F.trunc(F.to_date("fim_ts"), "month"))
    .withColumn("hora_abertura", F.hour("abertura_ts"))
    .select("id_chamado", "mes", "hora_abertura", "abandonado", "tempo_espera_s", "tempo_atendimento_s", "dq_abertura_corrigida")
    .dropDuplicates(["id_chamado"])
    .cache()
)
print(f"chamados com ano de abertura corrigido: {horarios.where('dq_abertura_corrigida').count():,}")
print(f"abandonados (sem hora de início): {horarios.where('abandonado').count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Clientes, atendentes, motivos, canais
# MAGIC Sem nome/e-mail/CPF em nenhuma saída — só `id_cliente` para join (nunca exibido) e atributos
# MAGIC agregados (`regiao`, `idade`).

# COMMAND ----------

clientes = add_try(df_clientes, "idade", F.trim("idade"), "int").select(
    F.trim("id_cliente").alias("id_cliente"),
    F.initcap(F.trim("regiao")).alias("regiao"),
    "idade",
).withColumn("dq_idade_invalida", F.col("idade").isNull() | (F.col("idade") < 18) | (F.col("idade") > 110)).cache()

atendentes = add_try(df_atendentes, "nivel_atendente", F.regexp_extract(F.col("nivel_atendimento"), r"(\d)", 1), "int").select(
    F.trim("id_atendente").alias("id_atendente"),
    F.trim("nome_atendente").alias("nome_atendente"),
    "nivel_atendente",
    F.lower(F.trim("status_atendente")).alias("status_atendente"),
).cache()

motivos = df_motivos.withColumn("motivo_key", norm_key(F.col("nome_motivo"))).select(
    "motivo_key",
    F.trim("nome_motivo").alias("motivo"),
    F.coalesce(blank_to_null(F.col("categoria")), F.lit("(sem categoria — a confirmar)")).alias("categoria"),
).dropDuplicates(["motivo_key"]).cache()

canais_dim = df_canais.withColumn("canal_key", norm_key(F.col("nome_canal"))).select(
    "canal_key", F.trim("nome_canal").alias("canal"), F.initcap(F.lower(F.trim("tipo_canal"))).alias("tipo_canal")
).dropDuplicates(["canal_key"]).cache()

print("ok")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Base consolidada (uma linha por chamado)
# MAGIC Reaproveitada por todas as análises de tema via `%run ./analise_geral_corrigida`.

# COMMAND ----------

custo_por_chamado = custos.where(~F.col("dq_custo_invalido")).groupBy("id_chamado").agg(F.sum("custo").alias("custo"))

base = (
    chamados
    .join(horarios, "id_chamado", "left")
    .join(custo_por_chamado, "id_chamado", "left")
    .join(pesquisa.where(~F.col("dq_nota_invalida")).select("id_chamado", "nota"), "id_chamado", "left")
    .join(atendentes, "id_atendente", "left")
    .join(motivos, "motivo_key", "left")
    .join(canais_dim, "canal_key", "left")
    .join(clientes, "id_cliente", "left")
    .drop("id_cliente")
    .cache()
)
print(f"chamados na base consolidada: {base.count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Panorama geral

# COMMAND ----------

total_chamados = base.count()
total_clientes = clientes.count()
total_atendentes_ativos = atendentes.where(F.col("status_atendente") == "ativo").count()
custo_total = custo_por_chamado.agg(F.sum("custo")).first()[0]

base_resolvido = base.where(~F.col("dq_resolvido_invalido"))
taxa_resolucao = base_resolvido.agg(F.avg(F.col("resolvido").cast("int"))).first()[0]

tme = base.where(F.col("tempo_espera_s").isNotNull()).agg(F.avg("tempo_espera_s")).first()[0]
tma = base.where(F.col("tempo_atendimento_s").isNotNull()).agg(F.avg("tempo_atendimento_s")).first()[0]
pct_abandono = base.agg(F.avg(F.col("abandonado").cast("int"))).first()[0]

base_csat = base.where(F.col("nota").isNotNull())
csat = base_csat.agg(F.avg((F.col("nota") >= 4).cast("int"))).first()[0]
nota_media = base_csat.agg(F.avg("nota")).first()[0]

print(f"Total de chamados (únicos):     {total_chamados:>10,}")
print(f"Total de clientes:               {total_clientes:>10,}")
print(f"Atendentes ativos:                {total_atendentes_ativos:>10}")
print(f"Custo total (R$):                {custo_total:>14,.2f}")
print(f"Taxa de resolução:               {taxa_resolucao:>13.1%}")
print(f"TME (tempo médio de espera):     {tme:>10,.1f} s  ({tme/60:,.1f} min)")
print(f"TMA (tempo médio de atendimento):{tma:>10,.1f} s  ({tma/60:,.1f} min)")
print(f"Abandono:                        {pct_abandono:>13.1%}")
print(f"CSAT (notas 4 e 5):               {csat:>13.1%}")
print(f"Nota média:                       {nota_media:>10,.2f}/5  ({base_csat.count():,} respostas)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Resumo — original (Juan) vs. corrigido
# MAGIC
# MAGIC | Métrica | No notebook original | Corrigido aqui |
# MAGIC |---|---|---|
# MAGIC | Custo total | R$ 42,2 mi | ~R$ 1,45 mi |
# MAGIC | Unidade dos tempos | rotulado "min" | segundos (vêm de `chamados_hora`, não do campo truncado) |
# MAGIC | Volume de chamados | 134.474 (com duplicatas) | 131.838 (deduplicado) |
# MAGIC | Satisfação média | inclui notas -1, 0 e 6 | só notas válidas (1-5) |
# MAGIC | Abandono | não calculado | calculado pelos timestamps |
# MAGIC | `id_cliente` (CPF) | risco de perder zero à esquerda (`inferSchema=True`) | lido como string, sempre |
# MAGIC
# MAGIC **Próximo passo:** cada pessoa explora o seu tema no Databricks (reaproveitando `base` e as outras
# MAGIC tabelas definidas aqui, ou do jeito que preferir) e leva o resultado pro `.md` correspondente em
# MAGIC `analises/` — ver `analises/README.md` para a lista de arquivos e responsáveis.
