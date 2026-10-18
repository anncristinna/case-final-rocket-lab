# Bronze — Landing to Bronze

Início da camada bronze de verdade (não é mais rascunho — ver `medalhao_rascunho/` para o desenho
original, mantido só como referência histórica). Passo a passo completo de como montar isso no
workspace do grupo (pastas, Volume, permissões, troubleshooting) em `docs/databricks-estrutura.md`.

> No workspace do grupo, este notebook vive em `Shared/case-final-rocket-lab/medalhao/Landing_To_Bronze`
> (a estrutura real diverge um pouco do que o guia planejava — `medalhao/` em vez de `00_base/`; ver
> nota no topo de `docs/databricks-estrutura.md`).

## `Landing_To_Bronze.ipynb`

Notebook **único** — ingere as 8 tabelas num loop (mesma lógica pra todas: ler fiel à origem, escrever
com `overwrite`). Não tem lógica diferente por tabela, então, diferente de `analises/`, não faz sentido
uma cópia por pessoa aqui. **Mudar só por PR revisado**, igual ao notebook base em `analises/`.

Os CSVs ficam num **Volume do Unity Catalog** (`dados_vcredit`). A leitura usa **pandas** em vez de
`spark.read`: pandas acessa qualquer caminho montado localmente (Volume ou pasta do Workspace) sem
diferença de código, então o notebook não precisou mudar quando os CSVs saíram da pasta do Workspace e
foram pro Volume — só o caminho que você preenche no widget muda.

Validado localmente (fora do Databricks, simulando a pasta com os CSVs de `data/raw/`): as 8 contagens
batem exatamente com o esperado, e a string literal `"NULL"` em `nota_atendimento` fica preservada
separada das células realmente vazias — ver `docs/achados_analise_geral.md`. A linha
`CREATE SCHEMA IF NOT EXISTS` (nova, pra evitar falha se o schema `vcredit_bronze` ainda não existir)
não dá pra testar localmente no Windows (precisa de `winutils.exe`) — é uma chamada padrão do Spark,
risco baixo, mas confirme que rodou sem erro na primeira execução no Databricks.

Pra rodar: no Databricks, preencha o widget `base_path` com o caminho do Volume — copie pelo **Catalog**
pra não errar o nome do schema (`/Volumes/workspace/<schema>/dados_vcredit`) — e rode todas as células.

## Regras da bronze (resumo — completo em `CLAUDE.md`)

- Tudo como `string`, **sem interpretar nada** (nem célula vazia vira nulo) — fiel à origem no sentido
  mais literal; correção de conteúdo é papel da silver, fase futura.
- `_ingestion_ts` e `_source_file` em toda tabela, pra rastrear quando e de onde veio.
- `overwrite` — idempotente, rodar de novo dá o mesmo resultado.
- Nenhum `display()`/`show()` de linha inteira em tabelas com dado pessoal (`clientes`).
