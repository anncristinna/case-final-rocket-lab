# Bronze — Landing to Bronze

Início da camada bronze de verdade (não é mais rascunho — ver `medalhao_rascunho/` para o desenho
original, mantido só como referência histórica).

## `Landing_To_Bronze.ipynb`

Notebook **único** — ingere as 8 tabelas num loop com **Auto Loader** (`cloudFiles`), não
`spark.read.csv` em lote. Mesma lógica pra todas as tabelas, então, diferente de `analises/`, não faz
sentido uma cópia por pessoa aqui. **Mudar só por PR revisado**, igual ao notebook base em `analises/`.

⚠️ **Não testado localmente** — `cloudFiles` é específico do Databricks (não existe no PySpark
open-source). A primeira execução de verdade é no Databricks: confira as contagens da seção 4 do
notebook contra `docs/achados_analise_geral.md` antes de confiar no resultado.

Pra rodar: no Databricks, preencha o widget `base_path` com um Volume do Unity Catalog (não funciona
com pasta do Workspace — ver `CLAUDE.md`) e rode todas as células.

## Regras da bronze (resumo — completo em `CLAUDE.md`)

- Tudo como `string`, sem correção de conteúdo (isso é silver, fase futura).
- `_ingestion_ts` e `_source_file` em toda tabela, pra rastrear quando e de onde veio.
- **Idempotente via checkpoint do Auto Loader** (não `overwrite`): cada arquivo é processado uma única
  vez; rodar de novo sem mudar nada não duplica linha. Pra forçar reprocessar uma tabela do zero, veja
  a seção 5 do notebook (apagar checkpoint + schema + tabela).
- Nenhum `display()`/`show()` de linha inteira em tabelas com dado pessoal (`clientes`).
