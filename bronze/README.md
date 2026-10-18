# Bronze — Landing to Bronze

Início da camada bronze de verdade (não é mais rascunho — ver `medalhao_rascunho/` para o desenho
original, mantido só como referência histórica).

## `Landing_To_Bronze.ipynb`

Notebook **único** — ingere as 8 tabelas num loop (mesma lógica pra todas: ler fiel à origem, escrever
com `overwrite`). Não tem lógica diferente por tabela, então, diferente de `analises/`, não faz sentido
uma cópia por pessoa aqui. **Mudar só por PR revisado**, igual ao notebook base em `analises/`.

Pra rodar: no Databricks, preencha o widget `base_path` com um Volume do Unity Catalog (não funciona
com pasta do Workspace — ver `CLAUDE.md`) e rode todas as células.

## Regras da bronze (resumo — completo em `CLAUDE.md`)

- Tudo como `string`, sem correção de conteúdo (isso é silver, fase futura).
- `_ingestion_ts` e `_source_file` em toda tabela, pra rastrear quando e de onde veio.
- `overwrite` — idempotente, rodar de novo dá o mesmo resultado.
- Nenhum `display()`/`show()` de linha inteira em tabelas com dado pessoal (`clientes`).
