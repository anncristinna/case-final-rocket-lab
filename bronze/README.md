# Bronze — Landing to Bronze

Início da camada bronze de verdade (não é mais rascunho — ver `medalhao_rascunho/` para o desenho
original, mantido só como referência histórica).

## `Landing_To_Bronze.ipynb`

Notebook **único** — ingere as 8 tabelas num loop (mesma lógica pra todas: ler fiel à origem, escrever
com `overwrite`). Não tem lógica diferente por tabela, então, diferente de `analises/`, não faz sentido
uma cópia por pessoa aqui. **Mudar só por PR revisado**, igual ao notebook base em `analises/`.

Os CSVs ficam numa pasta do Workspace (`Shared/case-final-rocket-lab/dados`), não um Volume do Unity
Catalog — por isso a leitura usa **pandas** em vez de `spark.read`: o Spark serverless do Free Edition
não lê CSV de pasta do Workspace de forma distribuída, mas o driver acessa esse caminho como arquivo
local normal, então pandas funciona sem problema (e os arquivos são pequenos o bastante pra isso não
pesar). Se um dia os CSVs forem pra um Volume, o notebook continua funcionando sem mudar nada.

Validado localmente (fora do Databricks, simulando a pasta com os CSVs de `data/raw/`): as 8 contagens
batem exatamente com o esperado, e a string literal `"NULL"` em `nota_atendimento` fica preservada
separada das células realmente vazias — ver `docs/achados_analise_geral.md`.

Pra rodar: no Databricks, preencha o widget `base_path` com `/Workspace/Shared/case-final-rocket-lab/dados`
(ajuste se o caminho real for outro) e rode todas as células.

## Regras da bronze (resumo — completo em `CLAUDE.md`)

- Tudo como `string`, **sem interpretar nada** (nem célula vazia vira nulo) — fiel à origem no sentido
  mais literal; correção de conteúdo é papel da silver, fase futura.
- `_ingestion_ts` e `_source_file` em toda tabela, pra rastrear quando e de onde veio.
- `overwrite` — idempotente, rodar de novo dá o mesmo resultado.
- Nenhum `display()`/`show()` de linha inteira em tabelas com dado pessoal (`clientes`).
