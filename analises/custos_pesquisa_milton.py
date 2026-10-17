# Databricks notebook source
# MAGIC %md
# MAGIC # Custos e pesquisa de satisfação — Milton
# MAGIC Tabelas: `custos`, `pesquisa_satisfacao` (cruzando com `chamados`, `chamados_hora`, `canais`,
# MAGIC `base_motivos` e `base_atendentes`). Este notebook só **lê** tabelas (nenhum `.write`), então
# MAGIC rodar de novo sobre os mesmos CSVs produz os mesmos números — idempotente por não ter efeito colateral.
# MAGIC
# MAGIC Valores de referência citados nas células markdown vêm de uma execução local anterior sobre os
# MAGIC CSVs completos — **este notebook deve reconferir e sinalizar qualquer diferença** ao rodar aqui.
# MAGIC Seções: (a-b) custos, (c-d) pesquisa, (e) cruzamento custo x satisfação, (f) recomendação
# MAGIC quantificada, (g) resumo. Nenhuma célula imprime `id_cliente`, nome ou e-mail.

# COMMAND ----------

# MAGIC %run ./_carga_dados

# COMMAND ----------

from pyspark.sql import functions as F, Window

# COMMAND ----------

# MAGIC %md
# MAGIC ## a) Custos — limpeza
# MAGIC Formatos observados: `0,39` · `3.45` · `R$ 1,46` · `3.45reais` · `R$ -2,10`.
# MAGIC
# MAGIC Regra: remover tudo que **não** for dígito, vírgula, ponto ou `-` (isso já cobre `R$`, espaços e o
# MAGIC sufixo `reais`). Se o que restar tiver vírgula, tratamos como separador decimal brasileiro: removemos
# MAGIC os pontos (seriam separador de milhar) e trocamos a vírgula por ponto. Se não tiver vírgula, o ponto
# MAGIC que já está lá **é** o separador decimal e fica como está.
# MAGIC
# MAGIC ⚠️ **Não remover todos os pontos indiscriminadamente.** Esse foi o erro do notebook inicial do Juan:
# MAGIC ao tirar todo ponto, `23.24` virava `2324` e `74.71reais` virava `7471`, inflando o custo total para
# MAGIC R$ 42,2 mi. O valor correto, com a regra acima, é **~R$ 1,45 mi**.

# COMMAND ----------

_bruto = F.regexp_replace(F.trim(F.col("custo")), r"[^0-9,.\-]", "")
_numero = F.when(
    _bruto.contains(","),
    F.regexp_replace(F.regexp_replace(_bruto, r"\.", ""), ",", "."),
).otherwise(_bruto)

custos_tipado = df_custos.withColumn("_numero", _numero)
custos_tipado = add_try(custos_tipado, "custo_valor", F.col("_numero"), "double")
custos_tipado = add_try(custos_tipado, "id_custo_i", F.trim(F.col("id_custo")), "int")
custos_tipado = add_try(custos_tipado, "id_chamado_i", F.trim(F.col("id_chamado")), "int")

custos_limpo = (
    custos_tipado
    .select(
        F.col("id_custo_i").alias("id_custo"),
        F.col("id_chamado_i").alias("id_chamado"),
        F.col("custo_valor").alias("custo"),
    )
    .withColumn("dq_custo_invalido", F.col("custo").isNull())
    .withColumn("dq_custo_nao_positivo", F.col("custo") <= 0)
    .dropDuplicates(["id_custo"])
    .cache()
)

print("custos únicos (após remover duplicatas por id_custo):", f"{custos_limpo.count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC Quadro dos padrões de formato encontrados (dígitos trocados por `9`, para não vazar valores reais):

# COMMAND ----------

_padrao = F.regexp_replace(F.trim(F.col("custo")), r"\d", "9")
display(
    df_custos
    .withColumn("padrao", _padrao)
    .groupBy("padrao")
    .count()
    .orderBy(F.desc("count"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC **O que isso mostra:** o formato de `custo` varia bastante (8+ padrões, incluindo `R$`, `reais` e
# MAGIC negativos), mas a regra de limpeza dá conta de todos sem distorcer o valor — diferente do notebook
# MAGIC inicial, que inflou o custo total em quase 30×.

# COMMAND ----------

# MAGIC %md
# MAGIC ## b) Custos — análises

# COMMAND ----------

# MAGIC %md
# MAGIC ### Total, distribuição e a decisão pendente sobre custo ≤ 0
# MAGIC `custos ≤ 0` (negativos ou zero) ficam na base com a flag `dq_custo_nao_positivo`. Mostramos as
# MAGIC **duas versões** do total — **a escolha de incluir ou excluir é do grupo**, não decidimos aqui.

# COMMAND ----------

validos = custos_limpo.where(~F.col("dq_custo_invalido"))

total_incluindo = validos.agg(F.sum("custo")).first()[0]
total_excluindo = validos.where(F.col("custo") > 0).agg(F.sum("custo")).first()[0]
qtd_nao_positivos = custos_limpo.where(F.col("dq_custo_nao_positivo")).count()
qtd_negativos = custos_limpo.where(F.col("custo") < 0).count()
qtd_zero = custos_limpo.where(F.col("custo") == 0).count()
soma_nao_positivos = validos.where(F.col("dq_custo_nao_positivo")).agg(F.sum("custo")).first()[0] or 0.0

display(
    spark.createDataFrame(
        [
            ("Incluindo custo <= 0 (mantido com flag)", float(total_incluindo)),
            ("Excluindo custo <= 0 (tratado como estorno/erro)", float(total_excluindo)),
        ],
        ["cenario", "custo_total"],
    )
)
print(
    f"custo <= 0: {qtd_nao_positivos:,} lançamentos ({qtd_negativos:,} negativos + {qtd_zero:,} zero), "
    f"somando R$ {soma_nao_positivos:,.2f} ({soma_nao_positivos / total_incluindo:.2%} do total 'incluindo')"
)

quantis = validos.approxQuantile("custo", [0.1, 0.25, 0.5, 0.75, 0.9, 0.99], 0.01)
print("quantis de custo por lançamento (10/25/50/75/90/99%):", quantis)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Chamados sem custo

# COMMAND ----------

chamados_unicos = df_chamados.select(F.trim("id_chamado").alias("id_chamado")).dropDuplicates(["id_chamado"])
chamados_sem_custo = chamados_unicos.join(validos, "id_chamado", "left_anti")
print("chamados sem custo:", f"{chamados_sem_custo.count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Dimensões compartilhadas: chamados, canal, motivo, nível e timestamps
# MAGIC `chamados` tem 2.636 `id_chamado` duplicados (idênticos): deduplicamos **uma única vez** aqui e
# MAGIC reaproveitamos em todas as análises (custo e pesquisa), para não contar o mesmo chamado duas vezes
# MAGIC nem reprocessar a mesma limpeza. `canal` é texto livre: normalizamos com `norm_key` + `CANAL_ALIAS`
# MAGIC (de `_carga_dados.py`). Os timestamps de `chamados_hora` também são lidos uma única vez aqui: deles
# MAGIC saem o mês (pela **finalização**, que não tem o erro de ano da abertura), o TME, o TMA e o abandono —
# MAGIC nunca usamos `chamados.tempo_atendimento` (truncado para durações ≥ 1.000 s).

# COMMAND ----------

mapa_canal = F.create_map(*[F.lit(x) for kv in CANAL_ALIAS.items() for x in kv])
_res_key = norm_key(F.col("resolvido"))
_resolvido_bool = (
    F.when(_res_key.isin("sim", "s", "1", "true", "yes", "resolvido"), F.lit(True))
     .when(_res_key.isin("nao", "n", "0", "false", "nao resolvido"), F.lit(False))
)
_canal_key_bruta = norm_key(F.col("canal"))

chamados_dedup = (
    df_chamados.dropDuplicates(["id_chamado"])
    .select(
        F.trim("id_chamado").alias("id_chamado"),
        F.trim("canal").alias("canal_original"),
        F.coalesce(mapa_canal[_canal_key_bruta], _canal_key_bruta).alias("canal_key"),
        norm_key(F.col("motivo")).alias("motivo_key"),
        F.trim("id_atendente").alias("id_atendente"),
        _resolvido_bool.alias("resolvido"),
    )
    .cache()
)

atendentes_nivel = (
    add_try(df_atendentes, "nivel", F.regexp_extract(F.col("nivel_atendimento"), r"(\d)", 1), "int")
    .select(F.trim("id_atendente").alias("id_atendente"), F.col("nivel").alias("nivel_atendente"))
    .cache()
)

motivos_dim = (
    df_motivos
    .withColumn("motivo_key", norm_key(F.col("nome_motivo")))
    .withColumn("_categoria", blank_to_null(F.col("categoria")))
    .select("motivo_key", F.coalesce(F.col("_categoria"), F.lit("(sem categoria — a confirmar)")).alias("categoria"))
    .dropDuplicates(["motivo_key"])
    .cache()
)


def _limpa_conector(col):
    # remove o conector "às" (tolera encoding corrompido) entre data e hora
    return F.regexp_replace(F.trim(col), r"\s\S{1,3}\s", " ")


_hora = df_chamados_hora.withColumn("id_chamado", F.trim(F.col("id_chamado")))
_hora = add_try(_hora, "abertura_ts", _limpa_conector(F.col("hora_abertura_chamado")), "ts", "dd/MM/yyyy HH:mm:ss")
_hora = add_try(_hora, "inicio_ts", _limpa_conector(F.col("hora_inicio_atendimento")), "ts", "dd/MM/yyyy HH:mm:ss")
_hora = add_try(_hora, "fim_ts", _limpa_conector(F.col("hora_finalizacao_atendimento")), "ts", "dd/MM/yyyy HH:mm:ss")

hora_tipada = (
    _hora
    # ⚠️ não corrigimos aqui o erro de ano na abertura (~198 chamados, ver chamados_hora_juan.py):
    # só excluímos da espera os casos com ordem impossível, que é o sintoma desse erro.
    .withColumn("dq_ordem_invalida_abertura", F.coalesce(F.col("inicio_ts") < F.col("abertura_ts"), F.lit(False)))
    .withColumn("dq_ordem_invalida_atendimento", F.coalesce(F.col("fim_ts") < F.col("inicio_ts"), F.lit(False)))
    .withColumn("abandonado", F.col("inicio_ts").isNull())
    .withColumn(
        "tempo_espera_s",
        F.when(
            ~F.col("dq_ordem_invalida_abertura") & F.col("inicio_ts").isNotNull(),
            F.unix_timestamp("inicio_ts") - F.unix_timestamp("abertura_ts"),
        ),
    )
    .withColumn(
        # TMA não depende da abertura, então não é afetado pelo erro de ano
        "tempo_atendimento_s",
        F.when(
            ~F.col("dq_ordem_invalida_atendimento") & F.col("fim_ts").isNotNull() & F.col("inicio_ts").isNotNull(),
            F.unix_timestamp("fim_ts") - F.unix_timestamp("inicio_ts"),
        ),
    )
    .withColumn("mes", F.trunc(F.to_date("fim_ts"), "month"))
    .select(
        "id_chamado", "mes", "abandonado", "tempo_espera_s", "tempo_atendimento_s",
        "dq_ordem_invalida_abertura", "dq_ordem_invalida_atendimento",
    )
    .dropDuplicates(["id_chamado"])
    .cache()
)
hora_mes = hora_tipada.select("id_chamado", "mes")

custo_por_chamado = validos.groupBy("id_chamado").agg(F.sum("custo").alias("custo_total"))

base_custo_dim = (
    chamados_dedup
    .join(custo_por_chamado, "id_chamado", "left")
    .join(atendentes_nivel, "id_atendente", "left")
    .join(motivos_dim, "motivo_key", "left")
    .cache()
)

print("chamados únicos:", f"{chamados_dedup.count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Custo mensal x volume de chamados
# MAGIC Lado a lado, para separar **"o gasto cresce porque o volume cresce"** de **"o custo unitário sobe"**.

# COMMAND ----------

volume_mes = chamados_dedup.join(hora_mes, "id_chamado", "left").groupBy("mes").agg(F.count("*").alias("qtd_chamados"))
custo_mes = (
    validos.join(hora_mes, "id_chamado", "inner")
    .groupBy("mes")
    .agg(F.sum("custo").alias("custo_total"), F.count("*").alias("qtd_lancamentos"))
)

_janela_mes = Window.orderBy("mes").rowsBetween(Window.unboundedPreceding, 0)
evolucao_mensal = (
    custo_mes.join(volume_mes, "mes", "left")
    .withColumn("custo_medio_por_chamado", F.col("custo_total") / F.col("qtd_chamados"))
    .withColumn("custo_acumulado", F.sum("custo_total").over(_janela_mes))
    .where(F.col("mes").isNotNull())
    .orderBy("mes")
)
display(evolucao_mensal)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Custo médio por canal, motivo, categoria do motivo e nível do atendente

# COMMAND ----------

print("Custo médio por canal:")
display(base_custo_dim.groupBy("canal_key").agg(F.avg("custo_total").alias("custo_medio"), F.count("*").alias("chamados")).orderBy(F.desc("custo_medio")))

print("Custo médio por motivo:")
display(base_custo_dim.groupBy("motivo_key").agg(F.avg("custo_total").alias("custo_medio"), F.count("*").alias("chamados")).orderBy(F.desc("custo_medio")))

print("Custo médio por categoria do motivo:")
display(base_custo_dim.groupBy("categoria").agg(F.avg("custo_total").alias("custo_medio"), F.count("*").alias("chamados")).orderBy(F.desc("custo_medio")))

print("Custo médio por nível do atendente:")
display(base_custo_dim.groupBy("nivel_atendente").agg(F.avg("custo_total").alias("custo_medio"), F.count("*").alias("chamados")).orderBy("nivel_atendente"))

custo_nivel1 = base_custo_dim.where(F.col("nivel_atendente") == 1).agg(F.avg("custo_total")).first()[0]
custo_nivel2 = base_custo_dim.where(F.col("nivel_atendente") == 2).agg(F.avg("custo_total")).first()[0]
diff_escalonamento = custo_nivel2 - custo_nivel1
print(
    f"\ncusto médio nível 1: R$ {custo_nivel1:,.2f} | nível 2: R$ {custo_nivel2:,.2f} | "
    f"diferença (proxy do custo de um chamado escalar para o nível 2): R$ {diff_escalonamento:,.2f} "
    f"({custo_nivel2 / custo_nivel1:,.1f}x)"
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Pareto: motivos e canais que concentram o gasto

# COMMAND ----------

def _pareto(df, chave):
    base = (
        df.groupBy(chave)
        .agg(F.sum("custo_total").alias("custo"), F.count("*").alias("chamados"))
        .where(F.col("custo").isNotNull())
    )
    total = base.agg(F.sum("custo")).first()[0]
    janela = Window.orderBy(F.desc("custo")).rowsBetween(Window.unboundedPreceding, 0)
    return (
        base.orderBy(F.desc("custo"))
        .withColumn("custo_acumulado", F.sum("custo").over(janela))
        .withColumn("pct_acumulado", F.col("custo_acumulado") / F.lit(total))
    )


print("Pareto por motivo (gasto acumulado):")
display(_pareto(base_custo_dim, "motivo_key"))

print("Pareto por canal (gasto acumulado):")
display(_pareto(base_custo_dim, "canal_key"))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Maiores outliers de custo

# COMMAND ----------

display(validos.orderBy(F.desc("custo")).limit(20))

# COMMAND ----------

# MAGIC %md
# MAGIC **O que isso mostra:** o custo total tratado (~R$ 1,45 mi) é ~30× menor que o número do notebook
# MAGIC inicial — era erro de limpeza, não o cenário real. O gasto cresce porque o **volume** de chamados
# MAGIC cresce (o custo médio por chamado é estável mês a mês); o gasto também é bastante concentrado em
# MAGIC poucos motivos/canais (ver Pareto) e o nível 2 custa, em média, várias vezes mais que o nível 1 — a
# MAGIC diferença de custo entre eles é a base da recomendação quantificada na seção (f). A decisão sobre
# MAGIC incluir ou excluir custo ≤ 0 (544 lançamentos) ainda está com o grupo; o total de referência usado
# MAGIC no restante deste notebook é o **"incluindo"**.

# COMMAND ----------

# MAGIC %md
# MAGIC ## c) Pesquisa de satisfação — limpeza
# MAGIC Nota válida: inteiro de **1 a 5**. `-1`, `0`, `6` e vazio viram `null` + `dq_nota_invalida`.
# MAGIC
# MAGIC Ao deduplicar por `id_chamado` (chamados com mais de uma pesquisa), priorizamos a linha com **nota
# MAGIC válida** quando existir — descobrimos que nem todo grupo duplicado tem a "mesma nota" repetida: 751
# MAGIC dos 802 chamados duplicados têm a mesma nota válida nas duas linhas, mas os outros ~51 têm todas as
# MAGIC linhas inválidas (ambas em branco/fora da faixa) e alguns poucos têm uma linha válida e outra
# MAGIC inválida. Por isso o número de notas inválidas **antes** de deduplicar (linha a linha do arquivo)
# MAGIC é diferente do número **depois** de deduplicar (uma linha por chamado) — mostramos os dois abaixo.

# COMMAND ----------

pesquisa_tipada = add_try(df_pesquisa, "id_pesquisa_i", F.trim(F.col("id_pesquisa")), "int")
pesquisa_tipada = add_try(pesquisa_tipada, "id_chamado_i", F.trim(F.col("id_chamado")), "int")
pesquisa_tipada = add_try(pesquisa_tipada, "nota_i", F.trim(F.col("nota_atendimento")), "int")

pesquisa_bruta = (
    pesquisa_tipada
    .select(
        F.col("id_pesquisa_i").alias("id_pesquisa"),
        F.col("id_chamado_i").alias("id_chamado"),
        F.when(F.col("nota_i").between(1, 5), F.col("nota_i")).alias("nota"),
    )
    .withColumn("dq_nota_invalida", F.col("nota").isNull())
)

total_pesquisa_bruta = pesquisa_bruta.count()
invalidas_bruto = pesquisa_bruta.where(F.col("dq_nota_invalida")).count()
print(f"pesquisas (linhas do arquivo): {total_pesquisa_bruta:,}")
print(f"notas inválidas (linhas do arquivo, antes de deduplicar): {invalidas_bruto:,}")

_janela_pesquisa = Window.partitionBy("id_chamado").orderBy(F.col("nota").isNull().asc(), F.col("id_pesquisa").asc())
pesquisa_limpa = (
    pesquisa_bruta
    .withColumn("_rank", F.row_number().over(_janela_pesquisa))
    .where(F.col("_rank") == 1)
    .drop("_rank")
    .cache()
)
print(f"pesquisas únicas por chamado (após dedup, nota válida priorizada): {pesquisa_limpa.count():,}")
print(f"notas inválidas após dedup: {pesquisa_limpa.where(F.col('dq_nota_invalida')).count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## d) Pesquisa de satisfação — análises

# COMMAND ----------

# MAGIC %md
# MAGIC ### Distribuição das notas válidas

# COMMAND ----------

display(pesquisa_limpa.where(~F.col("dq_nota_invalida")).groupBy("nota").count().orderBy("nota"))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Taxa de resposta por mês e por canal
# MAGIC Taxa de resposta geral = chamados com nota válida / chamados únicos. **Risco de viés:** só ~56%
# MAGIC respondem a pesquisa — se quem responde não for uma amostra representativa (ex.: clientes muito
# MAGIC insatisfeitos respondem mais, ou um canal específico tem resposta muito menor que os outros), o CSAT
# MAGIC medido pode não refletir a satisfação de quem **não** respondeu. Olhar a taxa por canal ajuda a avaliar
# MAGIC se a comparação de CSAT entre canais é justa.

# COMMAND ----------

respostas_validas = pesquisa_limpa.where(~F.col("dq_nota_invalida")).select("id_chamado").withColumn("respondeu", F.lit(1))
chamados_canal_mes = chamados_dedup.select("id_chamado", "canal_key").join(hora_mes, "id_chamado", "left")

taxa_resposta_geral = respostas_validas.count() / chamados_unicos.count()
print(f"taxa de resposta geral: {taxa_resposta_geral:.1%}")

print("Taxa de resposta por mês:")
display(
    chamados_canal_mes.join(respostas_validas, "id_chamado", "left")
    .groupBy("mes")
    .agg(F.count("*").alias("chamados"), F.sum(F.coalesce(F.col("respondeu"), F.lit(0))).alias("respostas"))
    .withColumn("taxa_resposta", F.col("respostas") / F.col("chamados"))
    .where(F.col("mes").isNotNull())
    .orderBy("mes")
)

print("Taxa de resposta por canal:")
display(
    chamados_canal_mes.join(respostas_validas, "id_chamado", "left")
    .groupBy("canal_key")
    .agg(F.count("*").alias("chamados"), F.sum(F.coalesce(F.col("respondeu"), F.lit(0))).alias("respostas"))
    .withColumn("taxa_resposta", F.col("respostas") / F.col("chamados"))
    .orderBy(F.desc("taxa_resposta"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### CSAT mensal
# MAGIC CSAT = % de notas 4 e 5 entre as **válidas**. Mês pelo mesmo critério do custo (finalização em `chamados_hora`).

# COMMAND ----------

display(
    pesquisa_limpa.where(~F.col("dq_nota_invalida"))
    .join(hora_mes, "id_chamado", "left")
    .where(F.col("mes").isNotNull())
    .groupBy("mes")
    .agg(F.count("*").alias("respostas"), F.avg((F.col("nota") >= 4).cast("int")).alias("csat"))
    .orderBy("mes")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### CSAT por canal, nível do atendente, motivo, categoria e resolução
# MAGIC `resolvido` em `chamados` vem em formatos mistos (`Sim`, `Não`, `S`, `N`, `1`, `0`, `Nao resolvido`,
# MAGIC vazio); normalizamos com `norm_key` antes de mapear para booleano.

# COMMAND ----------

base_nota_dim = (
    pesquisa_limpa.where(~F.col("dq_nota_invalida"))
    .join(chamados_dedup, "id_chamado", "left")
    .join(atendentes_nivel, "id_atendente", "left")
    .join(motivos_dim, "motivo_key", "left")
    .cache()
)


def _csat(df, chave):
    return (
        df.groupBy(chave)
        .agg(
            F.count("*").alias("respostas"),
            F.avg("nota").alias("nota_media"),
            F.avg((F.col("nota") >= 4).cast("int")).alias("csat"),
        )
        .orderBy(F.desc("csat"))
    )


for _chave, _titulo in [
    ("canal_key", "canal"),
    ("nivel_atendente", "nível do atendente"),
    ("motivo_key", "motivo"),
    ("categoria", "categoria do motivo"),
    ("resolvido", "resolução"),
]:
    print(f"CSAT por {_titulo}:")
    display(_csat(base_nota_dim, _chave))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Nota x tempo de espera, x TMA e x abandono
# MAGIC Tempos calculados a partir dos timestamps de `chamados_hora` (nunca de `chamados.tempo_atendimento`,
# MAGIC truncado para durações ≥ 1.000 s). Abandono = sem hora de início de atendimento (ver `CLAUDE.md`).

# COMMAND ----------

hora_tempos = hora_tipada.select("id_chamado", "tempo_espera_s", "tempo_atendimento_s", "abandonado")

_faixa_tme = (
    F.when(F.col("tempo_espera_s") <= 60, "0-1 min")
     .when(F.col("tempo_espera_s") <= 300, "1-5 min")
     .when(F.col("tempo_espera_s") <= 900, "5-15 min")
     .otherwise("15+ min")
)
_faixa_tma = (
    F.when(F.col("tempo_atendimento_s") <= 120, "0-2 min")
     .when(F.col("tempo_atendimento_s") <= 300, "2-5 min")
     .when(F.col("tempo_atendimento_s") <= 900, "5-15 min")
     .otherwise("15+ min")
)

print("Nota x faixa de TME (tempo de espera):")
display(
    pesquisa_limpa.where(~F.col("dq_nota_invalida"))
    .join(hora_tempos, "id_chamado", "inner")
    .where(F.col("tempo_espera_s").isNotNull())
    .withColumn("faixa_tme", _faixa_tme)
    .groupBy("faixa_tme")
    .agg(F.avg("nota").alias("nota_media"), F.avg((F.col("nota") >= 4).cast("int")).alias("csat"), F.count("*").alias("respostas"))
)

print("Nota x faixa de TMA (tempo de atendimento):")
display(
    pesquisa_limpa.where(~F.col("dq_nota_invalida"))
    .join(hora_tempos, "id_chamado", "inner")
    .where(F.col("tempo_atendimento_s").isNotNull())
    .withColumn("faixa_tma", _faixa_tma)
    .groupBy("faixa_tma")
    .agg(F.avg("nota").alias("nota_media"), F.avg((F.col("nota") >= 4).cast("int")).alias("csat"), F.count("*").alias("respostas"))
)

print("Resposta e nota por situação de abandono:")
display(
    chamados_dedup.select("id_chamado")
    .join(hora_tempos.select("id_chamado", "abandonado"), "id_chamado", "left")
    .join(pesquisa_limpa.where(~F.col("dq_nota_invalida")).select("id_chamado", "nota"), "id_chamado", "left")
    .withColumn("abandonado", F.coalesce(F.col("abandonado"), F.lit(False)))
    .groupBy("abandonado")
    .agg(F.count("*").alias("chamados"), F.count("nota").alias("respostas"), F.avg("nota").alias("nota_media"))
    .withColumn("taxa_resposta", F.col("respostas") / F.col("chamados"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Testando a fala do Marketing: "CSAT era 85% em jan/25; a piora é externa"
# MAGIC Comparamos o primeiro e o último mês com dado de CSAT por canal: se a queda for parecida em todos
# MAGIC os canais, é consistente com uma causa externa/geral; se estiver concentrada em um canal, é mais
# MAGIC provável que seja um problema específico daquele canal (operacional, não externo).

# COMMAND ----------

csat_canal_mes = (
    pesquisa_limpa.where(~F.col("dq_nota_invalida"))
    .join(chamados_dedup.select("id_chamado", "canal_key"), "id_chamado", "left")
    .join(hora_mes, "id_chamado", "left")
    .where(F.col("mes").isNotNull())
    .groupBy("mes", "canal_key")
    .agg(F.avg((F.col("nota") >= 4).cast("int")).alias("csat"), F.count("*").alias("respostas"))
)

_primeiro_mes = csat_canal_mes.agg(F.min("mes")).first()[0]
_ultimo_mes = csat_canal_mes.agg(F.max("mes")).first()[0]
print(f"comparando {_primeiro_mes} (citado pelo Marketing) com {_ultimo_mes} (mês mais recente com dado):")

display(
    csat_canal_mes.where(F.col("mes").isin(_primeiro_mes, _ultimo_mes))
    .groupBy("canal_key")
    .pivot("mes", [_primeiro_mes, _ultimo_mes])
    .agg(F.first("csat"))
    .orderBy("canal_key")
)

# COMMAND ----------

# MAGIC %md
# MAGIC **O que isso mostra:**
# MAGIC - A taxa de resposta geral (~56%) cai ao longo do tempo (65% em jan/25 para 48% em jul/26) — há risco
# MAGIC   real de viés: quem responde hoje pode não representar mais quem respondia no início do período.
# MAGIC - Chamados **abandonados respondem muito menos** (20,6% vs. 56,6% dos não abandonados) e, quando
# MAGIC   respondem, dão nota péssima (**média 1,14**, contra ~4,0 nos demais) — poucos dados, mas um sinal
# MAGIC   forte de que abandono é uma fonte concentrada de insatisfação, não só de custo invisível.
# MAGIC - Espera e atendimento mais longos pioram a nota de forma clara (CSAT cai de ~85% para ~9% entre
# MAGIC   quem espera até 1 min e quem espera 15+ min).
# MAGIC - **A fala do Marketing não se sustenta por completo:** a queda do CSAT entre jan/25 e jul/26 **não é
# MAGIC   uniforme entre canais** — atendimento especializado cai ~52 p.p. (63,7%→11,5%) e atendimento
# MAGIC   inicial ~45 p.p. (83,4%→38,4%), enquanto chatbot cai ~13 p.p. e URA ~19 p.p. Uma causa externa e
# MAGIC   geral afetaria todos os canais de forma parecida; a concentração nos canais **humanos** aponta para
# MAGIC   um problema operacional interno (capacidade, treinamento, fila), não só externo.

# COMMAND ----------

# MAGIC %md
# MAGIC ## e) Cruzamento custo x satisfação
# MAGIC Custo médio por nota e por canal, para identificar onde o custo alto **não** traz nota alta.

# COMMAND ----------

custo_nota = base_custo_dim.join(
    pesquisa_limpa.where(~F.col("dq_nota_invalida")).select("id_chamado", "nota"), "id_chamado", "inner"
)

print("Custo médio por nota:")
display(custo_nota.groupBy("nota").agg(F.avg("custo_total").alias("custo_medio"), F.count("*").alias("chamados")).orderBy("nota"))

print("Custo médio e nota média por canal, lado a lado:")
custo_canal = base_custo_dim.groupBy("canal_key").agg(F.avg("custo_total").alias("custo_medio"))
nota_canal = base_nota_dim.groupBy("canal_key").agg(F.avg("nota").alias("nota_media"))
display(custo_canal.join(nota_canal, "canal_key", "outer").orderBy(F.desc("custo_medio")))

# COMMAND ----------

# MAGIC %md
# MAGIC **O que isso mostra:** o atendimento especializado é o canal mais caro **e** o de menor nota média —
# MAGIC custo alto não compra satisfação alta aqui. Isso é esperado (motivos mais complexos vão para esse
# MAGIC canal), mas reforça que investir em **evitar** a chegada até ele (prevenção/nível 1) tende a ganhar
# MAGIC nos dois eixos, custo e satisfação — base da recomendação a seguir.

# COMMAND ----------

# MAGIC %md
# MAGIC ## f) Recomendação quantificada: reduzir o escalonamento para o nível 2
# MAGIC **Ideia:** treinar/equipar o nível 1 (script, alçada maior) para resolver uma fração dos motivos que
# MAGIC hoje terminam no nível 2, evitando a diferença de custo entre os níveis.
# MAGIC
# MAGIC ### Premissas (explícitas — células de dados acima vs. hipóteses do grupo)
# MAGIC 1. **Medido nos dados:** custo médio por chamado no nível 1 e no nível 2 (célula "Custo médio por
# MAGIC    canal, motivo, categoria do motivo e nível do atendente", acima).
# MAGIC 2. **Limitação dos dados (não é premissa, é fato):** `nivel_atendente` é o nível de quem **atendeu**
# MAGIC    o chamado — não existe nos dados um registro explícito de "este chamado escalou do nível 1 para o
# MAGIC    nível 2". Tratamos o custo médio do nível 2 como **proxy** do custo de um chamado escalado.
# MAGIC 3. **Premissa do grupo (não vem dos dados, precisa ser validada):** uma fração `p%` dos chamados hoje
# MAGIC    resolvidos no nível 2 poderia ser resolvida no nível 1 com script/treinamento adicional — ideia
# MAGIC    testada em 3 cenários de `p` abaixo, não um número definitivo.
# MAGIC 4. **Premissa:** o ganho é bruto (custo evitado de atendimento); não subtraímos o custo do próprio
# MAGIC    treinamento/script, que o grupo precisa estimar separadamente.
# MAGIC 5. **Premissa:** a diferença de custo médio nível 2 − nível 1 não muda com o volume deslocado (sem
# MAGIC    efeito de escala considerado).

# COMMAND ----------

# MAGIC %md
# MAGIC ### Conta passo a passo

# COMMAND ----------

chamados_nivel2 = base_custo_dim.where(F.col("nivel_atendente") == 2).count()
print(f"chamados atendidos no nível 2 no período: {chamados_nivel2:,}")
print(f"diferença de custo médio nível 2 - nível 1: R$ {diff_escalonamento:,.2f} por chamado\n")

_cenarios = [("conservador", 0.05), ("base", 0.15), ("otimista", 0.25)]
_linhas_cenario = []
for nome, pct in _cenarios:
    chamados_evitaveis = chamados_nivel2 * pct
    ganho = chamados_evitaveis * diff_escalonamento
    _linhas_cenario.append((nome, pct, chamados_evitaveis, float(ganho)))
    print(
        f"{nome:>12}: {pct:.0%} de {chamados_nivel2:,} chamados nível 2 = {chamados_evitaveis:,.0f} chamados "
        f"evitáveis x R$ {diff_escalonamento:,.2f} = R$ {ganho:,.2f} de economia no período medido"
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ### Sensibilidade (3 cenários)

# COMMAND ----------

display(
    spark.createDataFrame(_linhas_cenario, ["cenario", "pct_evitavel", "chamados_evitaveis", "ganho_estimado"])
    .orderBy("pct_evitavel")
)

# COMMAND ----------

# MAGIC %md
# MAGIC **O que isso mostra:** mesmo no cenário conservador (5% dos chamados de nível 2 evitados), a economia
# MAGIC estimada é relevante frente ao custo total tratado (~R$ 1,45 mi no período); no cenário base (15%) o
# MAGIC ganho se aproxima de uma fração de dois dígitos do gasto total com nível 2. O número exato depende da
# MAGIC premissa `p%` (não medida nos dados) e do custo do treinamento/script necessário — por isso a
# MAGIC apresentação deve deixar claro que é uma estimativa de **ganho bruto**, sensível à premissa, não uma
# MAGIC previsão.

# COMMAND ----------

# MAGIC %md
# MAGIC ## g) Resumo
# MAGIC
# MAGIC | Métrica | Valor de referência (execução local — reconferir aqui) |
# MAGIC |---|---|
# MAGIC | Custos únicos (após dedup por `id_custo`) | 130.288 |
# MAGIC | Custo total (incluindo custo ≤ 0) | R$ 1.447.671,52 |
# MAGIC | Custos ≤ 0 | 544 (271 negativos + 273 zero) |
# MAGIC | Chamados sem custo | 1.550 |
# MAGIC | Custo médio por chamado | ~R$ 11, estável de jan/25 (~4,4 mil chamados/mês) a jul/26 (~9,6 mil chamados/mês) |
# MAGIC | Custo médio por canal | URA ~R$ 1,84 · Chatbot ~R$ 0,57 · Atendimento Inicial ~R$ 13,60 · Especializado ~R$ 48,68 |
# MAGIC | Custo médio por nível | Nível 1 ~R$ 6,65 · Nível 2 ~R$ 20,96 (diferença ~R$ 14,31, ~3,15×) |
# MAGIC | Notas inválidas (linhas do arquivo, antes de deduplicar) | ~6.899 |
# MAGIC | Taxa de resposta à pesquisa | ~55,7% |
# MAGIC | CSAT mensal | ~86% em jan/2025 caindo para ~57% em jul/2026 |
# MAGIC
# MAGIC ### Pontos a validar com o grupo
# MAGIC - **Custo ≤ 0** (544 lançamentos): estorno real ou erro de lançamento? Mostramos as duas versões do
# MAGIC   total (incluindo/excluindo) na seção (b); a escolha final é do grupo.
# MAGIC - **Dedup da pesquisa**: agora prioriza a linha com nota válida quando o chamado tem mais de uma
# MAGIC   pesquisa (antes, a escolha entre as linhas duplicadas era arbitrária). Isso muda ligeiramente a
# MAGIC   contagem de notas válidas — confirmar que o grupo concorda com esse critério.
# MAGIC - **Custo de escalonamento** (seção f): usa o nível do atendente como *proxy* de "chamado escalado";
# MAGIC   não há no dataset um registro explícito de escalonamento. A fração `p%` de chamados evitáveis é uma
# MAGIC   premissa a validar com quem conhece a operação, não um número medido.
# MAGIC - **Mês de referência**: CSAT e custo mensal usam o mês de **finalização** (não de abertura) — por
# MAGIC   isso chamados abandonados (sem finalização) não entram nessas visões mensais específicas.
# MAGIC - **"Nota x tempo de espera/TMA"** não corrige o erro de ano na abertura (responsabilidade de
# MAGIC   `chamados_hora_juan.py`); os ~198 casos afetados são excluídos por ordem inválida, não corrigidos.
