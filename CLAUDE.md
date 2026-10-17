# CLAUDE.md — Case V-Credit (Rocket Lab 2026)

## Contexto
Grupo resolvendo o case da V-Credit (Visagio): Yuri, Cris, Juan, Richard, Milton, Gabriel, Anna.
Objetivo: a partir da análise dos dados de atendimento, chegar a recomendações práticas, priorizadas
e justificadas com dados (pelo menos 2 com ganho quantificado e premissas explícitas) para o Comitê Executivo.
Comunicação em **português do Brasil**.

**Abordagem atual (recomeço, mais simples e direta):** em vez de um notebook por pessoa, o grupo parte
do notebook exploratório inicial do Juan e constrói **um único notebook corrigido**, que vai para o
workspace Databricks do grupo (por enquanto, **sem Git folder** — upload manual via Workspace, ver seção
"Databricks" abaixo). Os resultados da análise vão para o **Notion compartilhado** do grupo, não para
documentos neste repositório.

## Prazos
- Quinta 22/10 às 18h: entregáveis técnicos.
- Sexta 23/10: apresentação (20 min + 15 min de perguntas).

## Estrutura
- `README.md`: nome do projeto, grupo, link para `docs/convencoes-git.md`.
- `docs/convencoes-git.md`: branches, commits (Conventional Commits) e Pull Requests.
- `docs/achados_analise_geral.md`: o que foi corrigido no notebook em relação ao original do Juan,
  indicadores gerais tratados e pendências — atualizar no mesmo commit se mudar alguma regra de limpeza.
- `analises/analise_geral_corrigida.py`: o notebook (carga, limpeza, insights).
- `analises/*.md` (exceto o README): conteúdo pronto para colar no Notion compartilhado do grupo —
  atualizar junto se os números do notebook mudarem.
- `data/raw/`: CSVs locais (fora do git). Notebooks de referência soltos em `data/` (ex.: o original do
  Juan) também ficam fora do git — ver `.gitignore`.

## Regras de dados
- **Nunca** commitar CSV ou arquivo com token/segredo. Nunca ler/exibir `.env` e afins.
- Dados têm CPF, nome e e-mail em `clientes`: nunca imprimir essas colunas em outputs, docs ou commits.
  O notebook original do Juan também tem um e-mail pessoal embutido no `base_path` — não reaproveitar
  esse caminho, nem comitar o `.ipynb` original como está.
- Encoding: `clientes.csv` e `Chamados_Hora.CSV` são `cp1252`/`ISO-8859-1`; os demais `utf-8`.
- **Tempos**: a fonte da verdade são os timestamps de `chamados_hora` (abertura/início/finalização).
  O campo `tempo_atendimento` de `chamados` está **truncado** para durações ≥ 1.000 s (subestima o TMA
  humano em várias vezes) — nunca usar esse campo original em KPI, só os tempos calculados pelos timestamps.
- **Custo**: o campo `custo` tem formatos mistos (`9,99`, `R$ 9,99`, `9.99reais`, negativos...). Regra de
  limpeza: manter só dígitos/`,`/`.`/`-`; se tiver vírgula, é separador decimal brasileiro (remover pontos
  de milhar antes de trocar a vírgula por ponto); se não tiver vírgula, o ponto já é decimal e fica como
  está. **Nunca remover todo ponto indiscriminadamente** — foi o erro do notebook original do Juan, que
  inflou o custo total em quase 30× (R$ 42 mi em vez de ~R$ 1,45 mi).
- `nota_atendimento` só é válida de 1 a 5; `-1`, `0`, `6` e vazio são inválidos (virar `null` + flag, não
  descartar a linha em silêncio).
- Anomalias em geral viram flag/coluna `dq_*`, nunca descarte silencioso.
- Ambiente Databricks **Free Edition**: só serverless, SQL warehouse 2X-Small, cota diária de uso. Evitar
  `collect()`/`toPandas()` em tabelas grandes (~130 mil linhas nas maiores); agregar no Spark antes de
  qualquer `display()`.
- Para testar localmente, use PySpark (Spark 4.x) com os CSVs de `data/raw/`.

## Databricks (workspace, sem Git folder por enquanto)
- Fluxo simplificado: editar o notebook localmente (`.py`, formato fonte `# Databricks notebook source`)
  → *Workspace → Import* manual no workspace do grupo → rodar e testar lá.
- Sugestão de pasta no workspace: algo como `/Workspace/Users/<seu-email>/vcredit/` (ou uma pasta
  compartilhada, se o workspace permitir), com o notebook corrigido dentro. Mantenha o nome do arquivo
  igual ao do repositório para não perder o rastro de qual versão está onde.
- Quando terminar de testar uma mudança no Databricks, traga a versão final de volta para o repositório
  (exportar/copiar o código) para o grupo não perder o trabalho.
- Isso é um começo deliberadamente mais simples que a arquitetura medalhão original; se o grupo retomar
  bronze/silver/gold depois, reavaliar se vale a pena configurar o Git folder nessa hora.

## Fluxo de trabalho esperado do Claude
1. Antes de alterar o notebook corrigido, reler as regras de dados acima (tempos, custo, notas, PII) e
   `docs/achados_analise_geral.md`.
2. Valide sintaxe (`python -m py_compile analises/*.py`) antes de comitar.
3. Mudou um número do notebook? Atualize o `.md` correspondente em `analises/` e, se for uma regra de
   limpeza, `docs/achados_analise_geral.md` também — no mesmo commit.
4. Commits pequenos, em português no imperativo, seguindo `docs/convencoes-git.md`.
5. Números que vão para o Notion devem sair de uma consulta reproduzível no notebook — citar a tabela de origem.

## Definições de KPI (confirmar com o grupo; mudar aqui se mudar)
- **Taxa de resolução** = chamados `resolvido = true` / chamados totais.
- **TME** (tempo médio de espera) = abertura → início do atendimento; **TMA** = início → finalização
  (ambos pelos timestamps de `chamados_hora`).
- **CSAT** = % de notas 4 e 5 entre as respondidas.
- **Abandono** = chamado sem hora de início de atendimento (espera registrada, sem atendimento).
- **Custo por chamado** = soma de `custos.custo` por `id_chamado`.
