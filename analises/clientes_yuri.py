# Databricks notebook source
# MAGIC %md
# MAGIC # Clientes — Yuri
# MAGIC Tabela: `clientes`. Leitura em **ISO-8859-1** (vem de `_carga_dados.py`, não ler como UTF-8).
# MAGIC `id_cliente` é o CPF (11 dígitos): manter como **string**, nunca converter para número.
# MAGIC
# MAGIC **NUNCA exibir `nome`, `email` ou `id_cliente` em saída de célula, doc ou commit.**
# MAGIC
# MAGIC Números abaixo vêm de uma execução local anterior sobre os CSVs completos — reconfirmar ao rodar aqui.

# COMMAND ----------

# MAGIC %run ./_carga_dados

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verificação básica

# COMMAND ----------

print("linhas:", df_clientes.count())
df_clientes.printSchema()

# COMMAND ----------

from pyspark.sql import functions as F

(
    df_clientes
    .select([F.count(F.when(F.col(c).isNull() | (F.trim(F.col(c)) == ""), c)).alias(c) for c in df_clientes.columns])
    .show(truncate=False)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Problemas já conhecidos nesta tabela (confirmar aqui)
# MAGIC - `data_cadastro` vem em dois formatos: `dd/MM/yyyy` e `yyyy-MM-dd`.
# MAGIC - `idade` tem valores impossíveis (faixa observada 0 a 199; ~839 clientes fora de 18–110 na execução local).
# MAGIC - ~1.330 chamados referenciam um `id_cliente` sem cadastro em `clientes` (medido localmente).
# MAGIC - `id_cliente` é CPF com 11 dígitos — manter como string (zeros à esquerda importam).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Perguntas sugeridas (TODO)
# MAGIC - Distribuição de clientes por região.
# MAGIC - Distribuição por faixa etária (e quantos ficam fora da faixa plausível 18–110).
# MAGIC - Tempo de casa (`data_cadastro`) e relação com volume/resolução de chamados.
# MAGIC - Idade × canal usado × resolução — hipótese do Diretor de Tecnologia de que o problema é o
# MAGIC   perfil digital do usuário, não o canal em si.
