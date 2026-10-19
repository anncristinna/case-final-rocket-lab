# Bronze — Landing to Bronze

Início da camada bronze de verdade (não é mais rascunho — ver `medalhao_rascunho/` para o desenho
original, mantido só como referência histórica). Passo a passo completo de como montar isso no
workspace do grupo (pastas, Volume, permissões, troubleshooting) em `docs/databricks-estrutura.md`.

> No workspace do grupo, este notebook vive em `Shared/case-final-rocket-lab/medalhao/Landing_To_Bronze`
> (a estrutura real diverge um pouco do que o guia planejava — `medalhao/` em vez de `00_base/`).

## `Landing_To_Bronze.ipynb`

Notebook **único e simples** — uma função (`ingere`) chamada uma vez por tabela, baseado direto no que
o grupo já estava rodando no Databricks. **Mudar só por PR revisado**, igual ao notebook base em
`analises/`.

Lê direto da **pasta do Workspace** (`Shared/case-final-rocket-lab/dados`) com o esquema `file:` no
caminho (`file:/Workspace/Shared/case-final-rocket-lab/dados/<arquivo>.csv`) — sem isso, `spark.read`
distribuído dá erro de permissão nessa pasta. `base_path` é fixo (sem widget).

O que foi adicionado em cima do que o grupo já tinha:
- **Encoding por arquivo** (`clientes` e `Chamados_Hora` são `ISO-8859-1`; os demais `UTF-8`) — sem
  isso os acentos de `regiao`, `nome_canal` etc. saem quebrados nesses dois arquivos.
- **Nome da tabela de destino sempre em minúsculo** (`chamados_hora_raw`, não `Chamados_Hora_raw`) —
  consistente com as outras 7, mesmo o arquivo se chamando `Chamados_Hora.csv` (maiúscula).
- Uma linha de contagem (`print`) depois de cada `saveAsTable`, pra conferir sem precisar rodar outra
  célula.

O que foi **removido** de versões anteriores deste notebook, a pedido do grupo (simplicidade):
widget de `base_path`, suporte a Volume do Unity Catalog (o grupo está usando a pasta do Workspace
mesmo), `CREATE SCHEMA IF NOT EXISTS` (o schema `dados_vcredit.default` já existe), e a renomeação de
colunas (BOM/minúsculo) — na verdade isso nem era "fiel à origem" de verdade; bronze deveria preservar
o header como veio, correção fica pra silver.

Validado localmente (fora do Databricks, simulando a pasta com os CSVs de `data/raw/` e o mesmo esquema
`file:`): as 8 contagens batem exatamente com o esperado, os acentos de `regiao` saem corretos, e
`_source_file` resolve certo — inclusive sem o tratamento especial de aspas que o notebook tinha antes
para `Chamados_Hora` (o padrão do Spark já dá conta, não precisava da exceção).

## Regras da bronze (resumo — completo em `CLAUDE.md`)

- Tudo como `string` (`inferSchema=false`), sem renomear nem corrigir nada aqui — isso é papel da
  silver, fase futura.
- `_source_file`, `_source_file_mod_ts` e `_ingestion_ts` em toda tabela, pra rastrear quando e de onde
  veio.
- `overwrite` — idempotente, rodar de novo dá o mesmo resultado.
- Nenhum `display()`/`show()` de linha inteira em tabelas com dado pessoal (`clientes`).
