# Databricks notebook source
# MAGIC %md
# MAGIC # 03 · Silver — limpeza, padronização e tipagem
# MAGIC Regras (detalhes e impacto em `docs/qualidade_dados.md`):
# MAGIC - Texto livre (`motivo`, `canal`) → chave normalizada (`*_key`): minúsculo, sem acento, `_`→espaço.
# MAGIC - Níveis de atendente (`1`, `Nível 1`, `N2`…) → inteiro 1 ou 2.
# MAGIC - Datas em dois formatos, horários com "às", valores `R$ 1,46` → tipos corretos.
# MAGIC - Conversões usam `try_*`: valor inválido vira `null` + flag `dq_*` (nada some em silêncio).
# MAGIC - Dados pessoais: `nome` e `email` **não** passam para a silver.
# MAGIC - **Idempotente**: `overwrite` por tabela.
# MAGIC
# MAGIC > Código inicial, ainda não executado no workspace. Rode, confira as contagens de controle no fim e ajuste.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

from pyspark.sql import functions as F

B = f"{CATALOG}.{SCHEMA_BRONZE}"
S = f"{CATALOG}.{SCHEMA_SILVER}"

ACC_FROM = "áàâãäéèêëíìîïóòôõöúùûüçñ"
ACC_TO   = "aaaaaeeeeiiiiooooouuuucn"


def norm_key(c):
    """Chave de comparação: minúsculo, sem acento, '_' e '-' viram espaço, espaços colapsados."""
    x = F.translate(F.lower(F.trim(c)), ACC_FROM, ACC_TO)
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


def save(df, nome):
    destino = f"{S}.{nome}"
    df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(destino)
    print(f"{destino}: {spark.table(destino).count():,} linhas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Atendentes

# COMMAND ----------

a = spark.table(f"{B}.base_atendentes")
a = add_try(a, "id", F.trim("id_atendente"), "int")
a = add_try(a, "nivel", F.regexp_extract("nivel_atendimento", r"(\d)", 1), "int")
a = add_try(a, "dt_adm", blank_to_null(F.col("data_admissao")), "date", "dd/MM/yyyy")
a = add_try(a, "dt_desl", blank_to_null(F.col("data_desligamento")), "date", "dd/MM/yyyy")

silver_atendentes = (
    a.select(
        F.col("id").alias("id_atendente"),
        F.trim("nome_atendente").alias("nome_atendente"),
        F.col("nivel").alias("nivel_atendimento"),
        F.col("dt_adm").alias("data_admissao"),
        F.col("dt_desl").alias("data_desligamento"),
        F.lower(F.trim("status_atendente")).alias("status_atendente"),
    )
    .withColumn(
        "dq_status_inconsistente",
        (F.col("status_atendente") == "ativo") & F.col("data_desligamento").isNotNull()
        | (F.col("status_atendente") == "inativo") & F.col("data_desligamento").isNull(),
    )
    .dropDuplicates(["id_atendente"])
)
save(silver_atendentes, "base_atendentes")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Motivos
# MAGIC `categoria` vazia em 3 de 14 motivos: **imputada** a partir do critério de categorização do enunciado
# MAGIC (premissa do grupo, a validar) e sinalizada em `categoria_imputada`.

# COMMAND ----------

CATEGORIA_IMPUTADA = {
    "transferencia de agencia": "Cadastral",
    "cancelamento de conta": "Financeiro",
    "contratacao de cartao adicional": "Cartao",
}
mapa_cat = F.create_map(*[F.lit(x) for kv in CATEGORIA_IMPUTADA.items() for x in kv])

m = spark.table(f"{B}.base_motivos")
m = add_try(m, "id", F.trim("id_motivo"), "int")
m = (
    m.withColumn("motivo_key", norm_key(F.col("nome_motivo")))
     .withColumn("categoria_orig", blank_to_null(F.col("categoria")))
)

silver_motivos = (
    m.select(
        F.col("id").alias("id_motivo"),
        F.trim("nome_motivo").alias("nome_motivo"),
        "motivo_key",
        F.coalesce(F.initcap("categoria_orig"), mapa_cat[F.col("motivo_key")]).alias("categoria"),
        F.col("categoria_orig").isNull().alias("categoria_imputada"),
        F.initcap(F.lower(F.trim("criticidade"))).alias("criticidade"),
    )
    .dropDuplicates(["id_motivo"])
)
save(silver_motivos, "base_motivos")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Canais

# COMMAND ----------

c = spark.table(f"{B}.canais")
c = add_try(c, "id", F.trim("id_canal"), "int")

silver_canais = (
    c.select(
        F.col("id").alias("id_canal"),
        F.trim("nome_canal").alias("nome_canal"),
        norm_key(F.col("nome_canal")).alias("canal_key"),
        F.initcap(F.lower(F.trim("tipo_canal"))).alias("tipo_canal"),
        F.lower(F.trim("status_canal")).alias("status_canal"),
    )
    .dropDuplicates(["id_canal"])
)
save(silver_canais, "canais")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Clientes (sem nome/e-mail)
# MAGIC `id_cliente` é CPF: mantido como **string** (zeros à esquerda). Datas em `dd/MM/yyyy` e `yyyy-MM-dd`.

# COMMAND ----------

cl = spark.table(f"{B}.clientes")
cl = add_try(cl, "idade_i", F.trim("idade"), "int")
cl = add_try(cl, "venc_i", F.trim("dia_vencimento_fatura"), "int")
cl = cl.withColumn(
    "dt_cad",
    F.coalesce(
        F.expr("cast(try_to_timestamp(trim(data_cadastro), 'dd/MM/yyyy') as date)"),
        F.expr("cast(try_to_timestamp(trim(data_cadastro), 'yyyy-MM-dd') as date)"),
    ),
)

silver_clientes = (
    cl.select(
        F.trim("id_cliente").alias("id_cliente"),
        F.initcap(F.trim("regiao")).alias("regiao"),
        F.col("idade_i").alias("idade"),
        F.col("dt_cad").alias("data_cadastro"),
        F.col("venc_i").alias("dia_vencimento_fatura"),
    )
    .withColumn("dq_idade_invalida", F.col("idade").isNull() | (F.col("idade") < 18) | (F.col("idade") > 110))
    .withColumn("dq_data_cadastro_invalida", F.col("data_cadastro").isNull())
    .dropDuplicates(["id_cliente"])
)
save(silver_clientes, "clientes")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Chamados
# MAGIC As colunas `hora_*` de `chamados` vêm vazias; os horários vêm de `chamados_hora`.
# MAGIC `tempo_espera`/`tempo_atendimento` (segundos) são mantidos como `*_s` e comparados com os timestamps na gold.

# COMMAND ----------

def seg(nome):
    return F.regexp_replace(F.trim(F.col(nome)), ",", ".")


ch = spark.table(f"{B}.chamados")
ch = add_try(ch, "id", F.trim("id_chamado"), "int")
ch = add_try(ch, "atend", F.trim("id_atendente"), "int")
ch = add_try(ch, "t_esp", seg("tempo_espera"), "double")
ch = add_try(ch, "t_atd", seg("tempo_atendimento"), "double")

res_key = norm_key(F.col("resolvido"))
resolvido = (
    F.when(res_key.isin("sim", "s", "1", "true", "yes", "resolvido"), F.lit(True))
     .when(res_key.isin("nao", "n", "0", "false", "nao resolvido"), F.lit(False))
)

# Variações de grafia de canal observadas nos dados (ex.: "U.R.A", "Chat Bot", "Atend. Inicial")
CANAL_ALIAS = {
    "u.r.a": "ura",
    "chat bot": "chatbot",
    "atend. inicial": "atendimento inicial",
    "atend. especializado": "atendimento especializado",
}
mapa_canal = F.create_map(*[F.lit(x) for kv in CANAL_ALIAS.items() for x in kv])
canal_key = F.coalesce(mapa_canal[norm_key(F.col("canal"))], norm_key(F.col("canal")))

silver_chamados_pre = (
    ch.select(
        F.col("id").alias("id_chamado"),
        F.trim("id_cliente").alias("id_cliente"),
        F.trim("motivo").alias("motivo_original"),
        norm_key(F.col("motivo")).alias("motivo_key"),
        F.trim("canal").alias("canal_original"),
        canal_key.alias("canal_key"),
        resolvido.alias("resolvido"),
        F.col("t_esp").alias("tempo_espera_s"),
        F.col("t_atd").alias("tempo_atendimento_s"),
        F.col("atend").alias("id_atendente"),
    )
    .withColumn("dq_resolvido_invalido", F.col("resolvido").isNull())
    .withColumn("dq_tempo_negativo", (F.col("tempo_espera_s") < 0) | (F.col("tempo_atendimento_s") < 0))
    # ids 0, 99 e 999 aparecem em chamados mas não existem no cadastro de atendentes (placeholders)
    .withColumn("dq_atendente_invalido", F.col("id_atendente").isin(0, 99, 999) | F.col("id_atendente").isNull())
)

total = silver_chamados_pre.count()
silver_chamados = silver_chamados_pre.dropDuplicates(["id_chamado"])
print(f"chamados: {total:,} linhas, {total - silver_chamados.count():,} duplicadas removidas por id_chamado")
save(silver_chamados, "chamados")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Chamados — horários
# MAGIC Formato `dd/MM/yyyy às HH:mm:ss`. O conector "às" é removido por regex (tolera caractere corrompido).
# MAGIC Chamado sem hora de início (`dq_sem_inicio`) = cliente esperou e desistiu: o campo original `tempo_espera`
# MAGIC vem preenchido e `tempo_atendimento` vazio (candidato a **abandono**).

# COMMAND ----------

def ts(nome):
    limpo = F.regexp_replace(F.trim(F.col(nome)), r"\s\S{1,3}\s", " ")
    return limpo


h = spark.table(f"{B}.chamados_hora")
h = add_try(h, "id", F.trim("id_chamado"), "int")
h = add_try(h, "abertura_ts", ts("hora_abertura_chamado"), "ts", "dd/MM/yyyy HH:mm:ss")
h = add_try(h, "inicio_ts", ts("hora_inicio_atendimento"), "ts", "dd/MM/yyyy HH:mm:ss")
h = add_try(h, "fim_ts", ts("hora_finalizacao_atendimento"), "ts", "dd/MM/yyyy HH:mm:ss")

# Em ~200 chamados o ANO da abertura está errado (+1 ou +2 anos, caindo em 2026/2027),
# enquanto início e fim estão certos. Corrigimos subtraindo os anos e sinalizamos.
h = h.withColumn(
    "_anos_erro",
    F.round((F.unix_timestamp("abertura_ts") - F.unix_timestamp("fim_ts")) / (365 * 86400)).cast("int"),
)
h = h.withColumn(
    "dq_abertura_corrigida",
    F.col("_anos_erro").isin(1, 2) & (F.col("abertura_ts") > F.col("fim_ts")),
)
h = h.withColumn(
    "abertura_ts",
    F.when(F.col("dq_abertura_corrigida"), F.expr("abertura_ts - make_interval(_anos_erro)"))
     .otherwise(F.col("abertura_ts")),
)

silver_hora_pre = (
    h.select(
        F.col("id").alias("id_chamado"),
        F.trim("id_cliente").alias("id_cliente_hora"),
        "abertura_ts", "inicio_ts", "fim_ts", "dq_abertura_corrigida",
    )
    .withColumn("dq_sem_abertura", F.col("abertura_ts").isNull())
    .withColumn("dq_sem_inicio", F.col("inicio_ts").isNull())
    .withColumn("dq_sem_fim", F.col("fim_ts").isNull())
    .withColumn(
        "dq_ordem_invalida",
        F.coalesce((F.col("inicio_ts") < F.col("abertura_ts")) | (F.col("fim_ts") < F.col("inicio_ts")), F.lit(False)),
    )
    # Tempos calculados dos timestamps = fonte da verdade (o campo original trunca valores >= 1000 s).
    .withColumn(
        "tempo_espera_calc_s",
        F.when(~F.col("dq_ordem_invalida"), F.unix_timestamp("inicio_ts") - F.unix_timestamp("abertura_ts")),
    )
    .withColumn(
        "tempo_atendimento_calc_s",
        F.when(~F.col("dq_ordem_invalida"), F.unix_timestamp("fim_ts") - F.unix_timestamp("inicio_ts")),
    )
)

total = silver_hora_pre.count()
silver_hora = silver_hora_pre.dropDuplicates(["id_chamado"])
print(f"chamados_hora: {total:,} linhas, {total - silver_hora.count():,} duplicadas removidas por id_chamado")
save(silver_hora, "chamados_hora")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Custos
# MAGIC `0,39`, `3.45`, `R$ 1,46`, `3.45reais`, `R$ -2,10` → double. Se houver milhar (`1.234,56`), remove o ponto antes de trocar a vírgula.
# MAGIC Custos ≤ 0 (~0,4%) ficam na tabela com `dq_custo_nao_positivo`.

# COMMAND ----------

cu = spark.table(f"{B}.custos")
cu = add_try(cu, "id", F.trim("id_custo"), "int")
cu = add_try(cu, "idc", F.trim("id_chamado"), "int")

# remove "R$", espaços e o sufixo "reais" (ex.: "3.45reais"); mantém dígitos, vírgula, ponto e sinal
bruto = F.regexp_replace(F.trim("custo"), r"[^0-9,.\-]", "")
numero = F.when(
    bruto.contains(","),
    F.regexp_replace(F.regexp_replace(bruto, r"\.", ""), ",", "."),
).otherwise(bruto)
cu = add_try(cu, "valor", numero, "double")

silver_custos = (
    cu.select(
        F.col("id").alias("id_custo"),
        F.col("idc").alias("id_chamado"),
        F.col("valor").alias("custo"),
    )
    .withColumn("dq_custo_invalido", F.col("custo").isNull())
    .withColumn("dq_custo_nao_positivo", F.col("custo") <= 0)
    .dropDuplicates(["id_custo"])
)
save(silver_custos, "custos")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pesquisa de satisfação
# MAGIC Nota válida: inteiro de 1 a 5; fora disso vira `null` + `dq_nota_invalida`.

# COMMAND ----------

p = spark.table(f"{B}.pesquisa_satisfacao")
p = add_try(p, "id", F.trim("id_pesquisa"), "int")
p = add_try(p, "idc", F.trim("id_chamado"), "int")
p = add_try(p, "nota_i", F.trim("nota_atendimento"), "int")

silver_pesquisa = (
    p.select(
        F.col("id").alias("id_pesquisa"),
        F.col("idc").alias("id_chamado"),
        F.when(F.col("nota_i").between(1, 5), F.col("nota_i")).alias("nota_atendimento"),
    )
    .withColumn("dq_nota_invalida", F.col("nota_atendimento").isNull())
    .dropDuplicates(["id_pesquisa"])
)
save(silver_pesquisa, "pesquisa_satisfacao")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Controles de integridade entre bases
# MAGIC Alimenta `docs/qualidade_dados.md` (quanto cada problema pesa nos indicadores).

# COMMAND ----------

controles = []


def anti(nome, esq, dir_, chave_esq, chave_dir=None):
    chave_dir = chave_dir or chave_esq
    l = spark.table(f"{S}.{esq}")
    r = spark.table(f"{S}.{dir_}")
    n = l.join(r, l[chave_esq] == r[chave_dir], "left_anti").count()
    controles.append((nome, f"{esq} sem correspondente em {dir_}", n))


anti("chamados→hora", "chamados", "chamados_hora", "id_chamado")
anti("hora→chamados", "chamados_hora", "chamados", "id_chamado")
anti("chamados→custos", "chamados", "custos", "id_chamado")
anti("custos→chamados", "custos", "chamados", "id_chamado")
anti("pesquisa→chamados", "pesquisa_satisfacao", "chamados", "id_chamado")
anti("chamados→clientes", "chamados", "clientes", "id_cliente")
anti("chamados→atendentes", "chamados", "base_atendentes", "id_atendente")
anti("chamados→motivos", "chamados", "base_motivos", "motivo_key")
anti("chamados→canais", "chamados", "canais", "canal_key")

df_controles = spark.createDataFrame(controles, ["controle", "descricao", "linhas"])
save(df_controles, "dq_integridade")
display(df_controles)
