# Convenções de Git — branches, commits e Pull Requests

Regras de colaboração do grupo. O fluxo com o Databricks (sem Git folder por enquanto) está em `CLAUDE.md`.

## Regra geral

- **Nunca** trabalhe direto na `main` — abra Pull Request e peça revisão de outra pessoa do grupo.
- Exceção já usada: como o repositório estava vazio, o primeiro push (reorganização inicial) foi direto
  na `main`. Isso não se repete: toda mudança a partir de agora passa por branch + PR.
- Antes de pushar: sem CSV, sem `.zip`/`.pbix` com dados (o pacote do Power BI fica em `data/powerbi/`, fora do git), sem dado pessoal (CPF/nome/e-mail) em output de célula.

## Branches

Uma branch por pessoa/tarefa, criada a partir da `main` atualizada: `git switch -c <tipo>/<nome>-<assunto>`.
Mesmo prefixo dos commits (veja abaixo), por exemplo:

- `feat/milton-custo-por-nivel` — nova análise ou notebook.
- `update/juan-chamados-hora-picos` — evolução de algo que já existe.
- `fix/yuri-parsing-data-cadastro` — correção de bug ou limpeza.
- `docs/cris-checklist-enunciado` — só documentação.
- `chore/richard-organiza-pastas` — organização, configs, sem mudar análise.

## Commits

Commits pequenos, seguindo [Conventional Commits](https://www.conventionalcommits.org/pt-br/): `<tipo>: <descrição no imperativo>`.
Tipos usados no projeto: `feat` (nova análise/funcionalidade), `update` (evolução de algo existente),
`fix` (correção de bug/limpeza), `docs` (documentação), `chore` (organização, configs, sem mudar análise).
Exemplos: `feat: adiciona analise de custo por canal`, `update: refina faixas de tempo de espera`,
`fix: corrige parsing de data cp1252 em clientes`, `docs: atualiza checklist do enunciado`.

## Pull Requests

- Título no mesmo padrão do commit (`tipo: descrição`); descrição curta do que mudou e por quê.
- Peça revisão de **pelo menos 1 outra pessoa** do grupo antes do merge — especialmente se tocar em
  regra de limpeza (atualize `docs/analitico/confiabilidade-dos-dados.md` e, se mudar número, o arquivo de `resultados/` correspondente no mesmo PR) ou em definição de KPI (`CLAUDE.md`).
- Antes de abrir o PR, confira: `git status --ignored` sem CSV/segredo e nenhuma saída de célula com dado pessoal.
- PR pequeno e focado numa tabela/tarefa — mais fácil de revisar que um PR com o trabalho de várias pessoas juntas.
- Prefira *squash merge* para manter o histórico da `main` limpo (um commit por PR).
