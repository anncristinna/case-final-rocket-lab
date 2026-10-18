# Bronze — Landing to Bronze

Início da camada bronze de verdade (não é mais rascunho — ver `medalhao_rascunho/` para o desenho
original, mantido só como referência histórica).

## Como usar o template

1. Copie `Landing_To_Bronze_template.ipynb` para `Landing_To_Bronze_<tabela>_<seunome>.ipynb`
   (ex.: `Landing_To_Bronze_custos_milton.ipynb`). **Não edite o template original** — ele é a base pra
   todo mundo, mudanças nele só por PR combinado (mesma regra do notebook base em `analises/`).
2. Preencha os `TODO` da célula de configuração: `ARQUIVO`, `ENCODING`, `TABELA`.
3. Rode no Databricks com um Volume do Unity Catalog como `base_path` (não funciona com pasta do
   Workspace — ver `CLAUDE.md`).
4. Confira a checklist no final do notebook antes de commitar.

## Responsável por tabela

Ver `analises/README.md` — mesma divisão: Yuri (`clientes`), Cris (`base_atendentes`, `base_motivos`),
Juan (`chamados_hora`), Richard (`canais`), Milton (`custos`, `pesquisa_satisfacao`). `chamados` pode
ficar com quem sobrar ou ser combinado entre o grupo.

## Regras da bronze (resumo — completo em `CLAUDE.md`)

- Tudo como `string`, sem correção de conteúdo (isso é silver, fase futura).
- `_ingestion_ts` e `_source_file` em toda tabela, pra rastrear quando e de onde veio.
- `overwrite` — idempotente, rodar de novo dá o mesmo resultado.
- Nenhum `display()`/`show()` de linha inteira em tabelas com dado pessoal (`clientes`).
