# CLAUDE.md — Case V-Credit (Rocket Lab 2026)

## Contexto
Grupo resolvendo o case da V-Credit (Visagio): Yuri, Cris, Juan, Richard, Milton, Gabriel, Anna.
Objetivo: a partir da análise dos dados de atendimento, chegar a recomendações práticas, priorizadas
e justificadas com dados (pelo menos 2 com ganho quantificado e premissas explícitas) para o Comitê Executivo.
Comunicação em **português do Brasil**.

**Abordagem atual (recomeço, mais simples e direta):** o grupo parte do notebook exploratório inicial do
Juan e corrige num **notebook base único** (`analises/analise_geral_corrigida.py`), que fica só no
workspace Databricks do grupo (por enquanto, **sem Git folder** — upload manual via Workspace, ver seção
"Databricks" abaixo). Esse notebook base muda só por PR combinado e revisado — **não criar um `.py` por
pessoa**, cada um explora o seu tema no Databricks do jeito que preferir e leva o resultado pro `.md`
correspondente em `analises/` (ver `analises/README.md` para a lista e quem é responsável por qual).
Os resultados da análise vão para o **Notion compartilhado** do grupo a partir desses `.md`.

Em paralelo, a camada **bronze** começou de verdade: `bronze/Landing_To_Bronze.ipynb` ingere as 8
tabelas (um `print` de contagem por tabela, nada além disso — simples de propósito, feito em cima do
que o próprio grupo já estava rodando no Databricks). Lê direto da pasta do Workspace
(`Shared/case-final-rocket-lab/dados`) com `spark.read` usando o esquema `file:` no caminho
(`file:/Workspace/Shared/case-final-rocket-lab/dados/<arquivo>.csv`) — testado pelo grupo, funciona pra
leitura distribuída (reverte o que a gente achava antes sobre Workspace não funcionar; ver nota em
`bronze/README.md`). Destino `dados_vcredit.default.<tabela>_raw` (sempre minúsculo), mesmo regime do
notebook base em `analises/`: muda só por PR revisado, sem cópia por pessoa. Ver `bronze/README.md`.

A camada **silver** é modular: um notebook por responsável em `silver/` (mesma divisão de tabelas de
`analises/README.md`), cada um lendo a sua tabela `*_raw` da bronze e escrevendo uma tabela
`dados_vcredit.default.<tabela>_silver`. A limpeza do `chamados` em si (sem dono único) e a junção das
5 tabelas silver numa `base_silver` ficam no `Silver_Consolidado.ipynb`, que roda depois dos outros 5.
Milton já preencheu o seu (`Silver_Custos_Pesquisa.ipynb`) — os outros 4 ainda são template vazio
(`# TODO`), cada responsável preenche com a própria lógica. Ver `silver/README.md`.

## Prazos
- Quinta 22/10 às 18h: entregáveis técnicos.
- Sexta 23/10: apresentação (20 min + 15 min de perguntas).

## Estrutura
- `README.md`: nome do projeto, grupo, link para `docs/convencoes-git.md`.
- `docs/convencoes-git.md`: branches, commits (Conventional Commits) e Pull Requests.
- `docs/achados_analise_geral.md`: o que foi corrigido no notebook em relação ao original do Juan,
  indicadores gerais tratados e pendências — atualizar no mesmo commit se mudar alguma regra de limpeza.
- `docs/databricks-estrutura.md`: passo a passo de pastas/Volume/permissões no workspace do grupo,
  valores de referência e troubleshooting comum.
- `analises/analise_geral_corrigida.py`: notebook base — carga, limpeza, panorama geral. Único arquivo
  de código; não criar uma cópia por pessoa.
- `analises/README.md`: lista de arquivos, responsáveis e status (preenchido/template).
- `analises/*.md` (exceto o README): conteúdo pronto para colar no Notion compartilhado do grupo — alguns
  já preenchidos, outros ainda são template a preencher (ver `analises/README.md`). Atualizar junto se os
  números do notebook base mudarem.
- `bronze/Landing_To_Bronze.ipynb`: notebook único de ingestão bronze (`.ipynb`, não `.py`), uma
  função (`ingere`) chamada por tabela, lê via `spark.read` (pasta do Workspace, esquema `file:`) e
  grava com `overwrite` em `dados_vcredit.default.<tabela>_raw`, sempre minúsculo — ver `bronze/README.md`.
- `silver/`: um notebook `.ipynb` por responsável (mesma divisão de `analises/README.md`), lê a
  tabela `*_raw` da bronze e grava `dados_vcredit.default.<tabela>_silver`; `Silver_Consolidado.ipynb`
  junta tudo numa `base_silver` e roda por último — ver `silver/README.md`.
- `data/raw/`: CSVs locais (fora do git). Notebooks de referência soltos em `data/` (ex.: o original do
  Juan) também ficam fora do git — ver `.gitignore`.

## Regras de dados
- **Nunca** commitar CSV ou arquivo com token/segredo. Nunca ler/exibir `.env` e afins.
- Dados têm CPF, nome e e-mail em `clientes`: nunca imprimir essas colunas em outputs, docs ou commits.
  O notebook original do Juan também tem um e-mail pessoal embutido no `base_path` — não reaproveitar
  esse caminho, nem comitar o `.ipynb` original como está.
- Encoding: `clientes.csv` e `Chamados_Hora.csv` são `cp1252`/`ISO-8859-1`; os demais `utf-8`. (O
  arquivo era `Chamados_Hora.CSV`, maiúsculo; o grupo padronizou pra `.csv` minúsculo — tabela de
  destino na bronze também fica minúscula, `chamados_hora_raw`.)
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
- **Duplicatas**: `chamados` tem 2.636 `id_chamado` duplicados (idênticos) e `custos` tem 781 `id_custo`
  duplicados. **Sempre** `dropDuplicates` por esse id antes de qualquer agregação, em toda análise —
  se cada tema tratar isso de um jeito diferente, os números não batem entre os `.md`.
- Anomalias em geral viram flag/coluna `dq_*`, nunca descarte silencioso.
- Ambiente Databricks **Free Edition**: só serverless, SQL warehouse 2X-Small, cota diária de uso. Evitar
  `collect()`/`toPandas()` em tabelas grandes (~130 mil linhas nas maiores); agregar no Spark antes de
  qualquer `display()`.
- Para testar localmente, use PySpark (Spark 4.x) com os CSVs de `data/raw/` — inclusive
  `bronze/Landing_To_Bronze.ipynb` (`_metadata.file_path`/`_metadata.file_modification_time` são
  recurso padrão do Spark, não específico do Databricks); só a escrita em tabela gerenciada
  (`saveAsTable`) não dá pra testar no Windows local sem `winutils.exe` — testar com
  `createOrReplaceTempView` no lugar.

## Databricks (workspace, sem Git folder por enquanto)
- Fluxo simplificado: editar o notebook localmente (`.py`/`.ipynb`) → *Workspace → Import* manual no
  workspace do grupo → rodar e testar lá. Passo a passo completo em `docs/databricks-estrutura.md`.
- Pasta real do grupo: `Shared/case-final-rocket-lab/`, com `analises/` (notebooks de análise, inclusive
  o base), `medalhao/` (`Landing_To_Bronze`) e `resultados/`. Os CSVs estão em
  `Shared/case-final-rocket-lab/dados` (pasta do Workspace) — ver nota abaixo sobre como ler isso com
  `spark.read`. Existe também um catálogo `dados_vcredit` no Unity Catalog, usado hoje como destino das
  tabelas bronze (`dados_vcredit.default.<tabela>_raw`), não necessariamente pros CSVs de origem.
  Mantenha o nome do arquivo igual ao do repositório para não perder o rastro de qual versão está onde.
- `spark.read` numa pasta do Workspace só funciona em leitura distribuída usando o **esquema `file:`
  explícito** no caminho (`file:/Workspace/...`) — sem isso, dá erro de permissão (é o que intrigava a
  gente antes: não é que Workspace nunca funcione, é que faltava esse prefixo). `bronze/Landing_To_Bronze.ipynb`
  monta isso direto (`BASE_PATH` fixo, sem widget — se o grupo migrar os CSVs pra um Volume no futuro,
  troca a constante e tira o prefixo `file:`).
- Quando terminar de testar uma mudança no Databricks, traga a versão final de volta para o repositório
  (exportar/copiar o código) para o grupo não perder o trabalho.
- A camada bronze já começou (`bronze/`, ver acima) — ainda sem Git folder por enquanto; reavaliar se
  vale configurar quando silver/gold entrarem, se o volume de notebooks crescer muito pra importar à mão.

## Fluxo de trabalho esperado do Claude
1. Antes de alterar o notebook corrigido, reler as regras de dados acima (tempos, custo, notas, PII) e
   `docs/achados_analise_geral.md`.
2. Valide sintaxe (`python -m py_compile analises/*.py`) antes de comitar. Para `.ipynb` em `bronze/`,
   confira que o JSON é válido (`python -c "import json; json.load(open(arquivo, encoding='utf-8'))"`).
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
