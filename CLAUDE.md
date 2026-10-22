# CLAUDE.md — Case V-Credit (Rocket Lab 2026)

## Contexto
Grupo resolvendo o case da V-Credit (Visagio): Yuri, Cris, Juan, Richard, Milton, Gabriel, Anna.
Objetivo: a partir da análise dos dados de atendimento, chegar a recomendações práticas, priorizadas
e justificadas com dados (pelo menos 2 com ganho quantificado e premissas explícitas) para o Comitê Executivo.
Comunicação em **português do Brasil**.

**Estado atual:** a arquitetura medalhão está pronta e já rodou no Databricks (Free Edition, catálogo
`dados_vcredit`, schema `default`): `Landing_To_Bronze` → `Bronze_To_Silver` → `Silver_To_Gold` → `Gold_To_CSV`,
todos em `medalhao/`. A análise é feita **sobre a camada gold** (14 tabelas analíticas `*_gold`) e vive em
`resultados/`; a documentação é organizada pelos dois entregáveis do enunciado em `docs/`. Os notebooks de
`medalhao/` mudam só por PR revisado; não criar cópia por pessoa. Não há Git folder: o fluxo é editar
localmente → *Workspace → Import* → testar → trazer a versão final de volta (ver `docs/databricks-estrutura.md`).

## Prazos
- Quinta 22/10 às 18h: entregáveis técnicos (para o Diretor de Tecnologia).
- Sexta 23/10: apresentação ao Comitê (20 min + 15 min de perguntas).

## Estrutura
- `README.md`: visão geral, entregas, estrutura e como começar.
- `medalhao/`: 4 notebooks `.ipynb` (um por camada, mesmos nomes do Databricks), `README.md` (ordem e
  tabelas) e `modelagem/` (diagramas `modelagem-silver.png`/`modelagem-gold.png` e o guia da gold em PDF).
- `resultados/`: `README.md` + 7 arquivos numerados (`01-visao-geral` … `07-custos-e-simulacao`), cada um
  citando a tabela gold de origem. **Se mudar um número, atualize o arquivo correspondente.**
- `docs/README.md`: mapa "item do enunciado → arquivo".
  - `docs/tecnico/`: `arquitetura-medalhao.md`, `notebooks-e-jobs.md` (jobs e idempotência),
    `painel-indicadores.md` (Power BI) e `historico-revisoes-silver-gold.md` (registro).
  - `docs/analitico/`: `confiabilidade-dos-dados.md`, `propostas-e-priorizacao.md`,
    `oportunidades-e-aprendizados.md` e `roteiro-apresentacao.md`.
  - `docs/convencoes-git.md` e `docs/databricks-estrutura.md`: processo do grupo.
- `data/`: tudo que é dado, **fora do git** (só `data/README.md` é versionado): `raw/` (8 CSVs originais) e
  `powerbi/` (`pacote_powerbi.zip`, saída do `Gold_To_CSV`).

## Regras de dados
- **Nunca** commitar CSV, `.zip`/`.pbix` com dados ou arquivo com token/segredo (o pacote do Power BI fica em
  `data/powerbi/`, ignorado). Nunca ler/exibir `.env` e afins.
- Dados têm CPF (o próprio `id_cliente`), nome e e-mail em `clientes`: nunca imprimir essas colunas em outputs,
  docs ou commits. `id_cliente` só serve de chave de junção na silver; a gold só tem `id_cliente_hash` (SHA-256
  puro, decisão do grupo: o id do case é fictício). `nome_atendente` **não** é dado restrito (decisão sobre
  mostrar o nome no material do Comitê ainda em aberto; parâmetro `anonimizar_atendente` do `Gold_To_CSV`).
  O notebook exploratório original do Juan tem um e-mail pessoal embutido no `base_path`: nunca comitar.
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
  inflou o custo total em quase 30× (R$ 42 mi em vez de ~R$ 1,45 mi). Na `base_silver` e na gold, só
  lançamentos > 0 entram na soma (total: R$ 1.450.617,85).
- `nota_atendimento` só é válida de 1 a 5; `-1`, `0`, `6` e vazio são inválidos (virar `null` + flag, não
  descartar a linha em silêncio).
- **Duplicatas**: `chamados` tem 2.636 `id_chamado` duplicados (idênticos) e `custos` tem 781 `id_custo`
  duplicados. **Sempre** `dropDuplicates` por esse id antes de qualquer agregação, em toda análise —
  se cada análise tratar isso de um jeito diferente, os números não batem entre os arquivos de `resultados/`.
- Anomalias em geral viram flag/coluna `dq_*`, nunca descarte silencioso.
- Ambiente Databricks **Free Edition**: só serverless, SQL warehouse 2X-Small, cota diária de uso. Evitar
  `collect()`/`toPandas()` em tabelas grandes (~130 mil linhas nas maiores); agregar no Spark antes de
  qualquer `display()`.
- Para testar localmente, use PySpark (Spark 4.x) com os CSVs de `data/raw/` — inclusive
  `medalhao/Landing_To_Bronze.ipynb` (`_metadata.file_path`/`_metadata.file_modification_time` são
  recurso padrão do Spark, não específico do Databricks); só a escrita em tabela gerenciada
  (`saveAsTable`) não dá pra testar no Windows local sem `winutils.exe` — testar com
  `createOrReplaceTempView` no lugar.

## Databricks (workspace, sem Git folder por enquanto)
- Fluxo: editar o notebook localmente (`.ipynb`) → *Workspace → Import* manual → rodar e testar lá → trazer
  a versão final de volta para o repositório. Passo a passo em `docs/databricks-estrutura.md`.
- Pasta do grupo: `Shared/case-final-rocket-lab/` com `dados/` (os 8 CSVs), `medalhao/` e `resultados/`.
  Tabelas no Unity Catalog: `dados_vcredit.default.<tabela>_raw|_silver|_gold`; a exportação do Power BI vai
  para o Volume `dados_vcredit.default.exportacao_powerbi`. Mantenha o nome do arquivo igual ao do repositório.
- `spark.read` numa pasta do Workspace só funciona em leitura distribuída com o **esquema `file:`
  explícito** (`file:/Workspace/...`); sem isso dá erro de permissão. `Landing_To_Bronze` usa `BASE_PATH` fixo.
- Todos os notebooks são idempotentes (`overwrite`/`CREATE OR REPLACE`); ordem: Landing_To_Bronze →
  Bronze_To_Silver → Silver_To_Gold → Gold_To_CSV. A configuração real do Job no Databricks não está versionada
  (ver pendência em `docs/tecnico/notebooks-e-jobs.md`).
- `Landing_To_Bronze` e `Bronze_To_Silver` ficam **sem saídas de tabela** no repositório (as saídas de
  amostra traziam dados de `clientes`); `Silver_To_Gold` e `Gold_To_CSV` só têm `print`s de contagem.

## Fluxo de trabalho esperado do Claude
1. Antes de alterar um notebook, reler as regras de dados acima (tempos, custo, notas, PII, duplicatas),
   `docs/tecnico/arquitetura-medalhao.md` e `docs/analitico/confiabilidade-dos-dados.md`.
2. Para `.ipynb` em `medalhao/`, confira que o JSON é válido
   (`python -c "import json; json.load(open(arquivo, encoding='utf-8'))"`) e que nenhuma saída traz CPF, nome ou e-mail de cliente.
3. Mudou um número ou uma regra de limpeza? Atualize no mesmo commit o arquivo de `resultados/` correspondente
   e, se for regra de limpeza, `docs/analitico/confiabilidade-dos-dados.md` e `docs/tecnico/arquitetura-medalhao.md`.
4. Commits pequenos, em português no imperativo, seguindo `docs/convencoes-git.md`.
5. Todo número em `resultados/` e `docs/analitico/` deve citar a tabela gold de origem e ser reproduzível a
   partir dela; premissas (ex.: 20% e 30% da simulação) devem aparecer explícitas.

## Definições de KPI (iguais às do painel e de `resultados/README.md`; confirmar com o grupo, mudar aqui se mudar)
- **Taxa de resolução** = chamados `resolvido = true` / chamados com `resolvido` informado (50,88%).
- **TME** (tempo médio de espera) = abertura → início do atendimento; **TMA** = início → finalização
  (ambos pelos timestamps de `chamados_hora`, só chamados atendidos com sequência de horários válida).
- **CSAT** = % de notas 4 e 5 entre as respondidas (nota válida de 1 a 5). `nota_ajustada` (6→5; 0 e -1→1) é um cenário à parte.
- **Abandono** = chamado sem hora de início de atendimento (espera registrada, sem atendimento).
- **Custo por chamado** = soma de `custos.custo` (lançamentos > 0) por `id_chamado`, média sobre chamados com custo válido.
- **Etapas do funil**: Autosserviço (URA e Chatbot), Nível 1 (Atendimento Inicial), Nível 2 (Atendimento Especializado).
- **Reincidência (7d)** = mesmo cliente e mesmo motivo em até 7 dias do chamado anterior.
