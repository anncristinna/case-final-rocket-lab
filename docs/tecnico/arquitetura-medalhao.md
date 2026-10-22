# Arquitetura medalhão

Entregável técnico (Diretor de Tecnologia): camadas de ingestão, tratamento e consolidação, com
rastreabilidade, qualidade e integridade. Código em [`../../medalhao/`](../../medalhao/).

```
CSVs (Workspace)  →  Bronze (*_raw)  →  Silver (*_silver)  →  Gold (*_gold)  →  CSV / Power BI
 8 arquivos           8 tabelas          9 tabelas + base       7 dim + fato +       Volume
                      tudo string        tipadas, flags dq_*    qualidade + 14 OLAP  exportacao_powerbi
```

Ambiente: Databricks Free Edition (serverless), catálogo `dados_vcredit`, schema `default`.

## Bronze — `Landing_To_Bronze.ipynb`

- **Fiel à origem**: as 8 tabelas entram como `string` (`inferSchema=false`), sem renomear nem corrigir nada.
- **Encoding por arquivo**: `clientes` e `Chamados_Hora` são `ISO-8859-1`; as demais `UTF-8`. Sem isso os acentos
  quebram.
- **Rastreabilidade**: toda tabela ganha `_source_file`, `_source_file_mod_ts` e `_ingestion_ts`.
- **Idempotência**: `overwrite` por tabela. Contagens: `chamados` 134.474, `chamados_hora` 131.838, `clientes` 47.705,
  `custos` 131.069, `pesquisa_satisfacao` 81.021, `base_atendentes` 25, `base_motivos` 14, `canais` 4.

## Silver — `Bronze_To_Silver.ipynb`

Notebook único, uma seção por tabela, mais a seção 8 (consolidado). Toda anomalia vira flag `dq_*`; nenhuma
linha é descartada em silêncio (a única remoção são duplicatas idênticas).

| Tabela | Tratamento principal |
|---|---|
| `chamados_silver` | 2.636 `id_chamado` duplicados removidos (134.474 → 131.838); `canal_chave`/`motivo_chave` normalizados (minúsculo, sem acento); `resolvido` booleano; `id_atendente` placeholder (0, 99, 999) ou vazio marcado em `dq_atendente_invalido` |
| `clientes_silver` | `id_cliente` (CPF) só como chave de junção e nunca exibido; idade fora de 18-110 vira inválida; `regiao` padronizada |
| `atendentes_silver` | nível extraído como 1 ou 2; datas de admissão/desligamento viram `date` |
| `motivos_silver` | `criticidade` em minúsculo; `categoria` vazia vira "Outro" |
| `canais_silver`, `canais_depara_silver` | nome oficial via `ALIASES`; de-para variação → `id_canal` (0 variações sem correspondência) |
| `custos_silver` | `custo` em formatos mistos limpo sem inflar o valor (ver abaixo); `decimal(12,2)`; 781 `id_custo` duplicados removidos |
| `pesquisa_satisfacao_silver` | nota válida só de 1 a 5 (`dq_nota_invalida`); `nota_ajustada` (6→5; 0 e -1→1) como premissa explícita |
| `chamados_hora_silver` | **fonte da verdade dos tempos**; ano de abertura corrigido em 198 chamados; virada de dia corrigida em 1 |
| `base_silver` | junção final, uma linha por `id_chamado`; `dq_cliente_sem_correspondencia` (~1,0% dos chamados) |

Regras que mudam número (detalhes e impacto em [`../analitico/confiabilidade-dos-dados.md`](../analitico/confiabilidade-dos-dados.md)):

- **Tempos** vêm só dos timestamps de `chamados_hora`. O `tempo_atendimento` de `chamados` é truncado para durações ≥ 1.000 s e nunca é usado.
- **Custo**: com vírgula, ela é o decimal brasileiro (pontos de milhar saem antes); sem vírgula, o ponto já é decimal. Remover todo ponto, como no notebook exploratório inicial, inflava o total para ~R$ 42 mi (o correto é ~R$ 1,45 mi). Na `base_silver` e na gold só entram lançamentos > 0.

## Gold — `Silver_To_Gold.ipynb`

Esquema em estrela (diagrama em [`../../medalhao/modelagem/modelagem-gold.png`](../../medalhao/modelagem/modelagem-gold.png); guia célula a célula em PDF na mesma pasta):

- **Fato** `fato_atendimento_gold`: 1 linha por chamado (22 colunas), 131.838 linhas.
- **Auditoria** `qualidade_chamado_gold`: 1 para 1 com a fato (24 colunas), onde ficam as flags de qualidade.
- **7 dimensões**: `dim_calendario` (731), `dim_hora` (25), `dim_faixa_espera` (6), `dim_canal` (5), `dim_motivo` (15), `dim_atendente` (28), `dim_cliente` (47.705).
- **14 tabelas analíticas** prontas para BI: `visao_geral`, `kpi_mensal`, `comparativo_yoy`, `funil_atendimento`, `etapa_mensal`, `motivos_pareto`, `motivo_etapa`, `demanda_dia_hora`, `atendentes_desempenho`, `satisfacao_drivers`, `perfil_cliente`, `qualidade_dados`, `impacto_indicadores`, `simulacao_ganhos`.

Garantias de integridade:

- **Nenhum chamado se perde**: todos os joins da fato são `LEFT`; o que não casa vira membro desconhecido (chave `-1`, e `-1/-2/-3` em atendente), nunca linha descartada. O notebook confere `n_fato == n_chamados` e **interrompe** se houver chave órfã ou duplicada.
- **Funil**: `dim_canal.etapa_funil` mapeia URA/Chatbot → Autosserviço, Atendimento Inicial → Nível 1, Atendimento Especializado → Nível 2. A etapa Prevenção (site/app) não existe nos dados.

## Gold → CSV — `Gold_To_CSV.ipynb`

Exporta o modelo de consumo (1 fato + 7 dimensões) e as 14 analíticas para o Volume `exportacao_powerbi`,
porque o Free Edition não tem integração nativa com o Power BI (enunciado, p. 9-10). Detalhes em
[`painel-indicadores.md`](painel-indicadores.md).

## Rastreabilidade, qualidade e integridade — resumo

| Requisito | Como é atendido |
|---|---|
| Rastreabilidade | `_source_file`/`_ingestion_ts` na bronze; `_manifesto.csv/json` na exportação (id do pacote, versão Delta de cada tabela de origem, linhas, colunas, checksum) |
| Qualidade | Flags `dq_*` na silver; `qualidade_chamado_gold` e `qualidade_dados_gold` na gold; `impacto_indicadores_gold` mede quanto cada tratamento move cada KPI |
| Integridade | Dedup por chave na silver; checagem de órfãos, chaves únicas e contagem da fato na gold |
| Idempotência | `overwrite` / `CREATE OR REPLACE` em toda tabela; CSVs regravados por inteiro, em ordem fixa, com checksum independente da ordem |
| Segurança / privacidade | `id_cliente` (CPF) só como chave interna na silver e **nunca exibido**; na gold e na exportação existe apenas `id_cliente_hash`; nome, e-mail e CPF não existem na gold |

## Colunas de linhagem

Quatro colunas existem só para rastrear a execução e **mudam a cada rodada por definição**; todas ficam fora do checksum de idempotência
(ver [`notebooks-e-jobs.md`](notebooks-e-jobs.md)):

| Coluna | Onde | O que guarda |
|---|---|---|
| `_source_file`, `_source_file_mod_ts` | Todas as tabelas `*_raw` | Arquivo de origem e a data de modificação dele (não mudam se o CSV não mudar) |
| `_ingestion_ts` | Todas as tabelas `*_raw` | Hora da ingestão |
| `_treatment_ts` | `canais_silver` | `current_timestamp()` do tratamento; **não** é levada para a gold |
| `versao_bronze` | `chamados_hora_silver` | Versão Delta de `chamados_hora_raw` usada no tratamento (sobe a cada ingestão) |

## Tabelas no catálogo fora do pipeline

O Job escreve **41** tabelas (8 `*_raw`, 10 `*_silver` com a `base_silver` e 23 `*_gold`). O schema `dados_vcredit.default` tem **47** tabelas
`*_raw/_silver/_gold`: as 6 a mais são `canal_escalonamento_gold`, `canal_faixa_espera_gold`, `canal_faixa_horaria_gold`,
`canal_kpi_mensal_gold`, `canal_perfil_gold` e `canal_qualidade_gold`. **Nenhum dos 4 notebooks de `medalhao/` as cria** e o `Gold_To_CSV` não as exporta.
Origem a confirmar com o grupo: ou o notebook que as gera entra em `medalhao/` (e na contagem desta documentação), ou as tabelas são removidas.

## Fonte da verdade dos tempos

O enunciado (consideração 6) pede que o grupo decida e documente qual fonte vale quando um campo calculado diverge do registro de horário.

**Decisão:** todos os tempos (TME, TMA e tempo total) vêm **somente dos timestamps de `chamados_hora`** (abertura, início e finalização),
tratados na silver (`chamados_hora_silver`). O campo `tempo_atendimento` de `chamados` **nunca é usado em indicador**.

**Por quê:** o campo está truncado para durações a partir de 1.000 s, então subestima o TMA humano.

**Valores preliminares, a confirmar.** Foram calculados fora do Databricks, a partir do `chamados.csv` local e do `fato_atendimento.csv` do pacote. Até a
query abaixo ser rodada, não devem ser citados como números finais:

| Medida (preliminar) | Campo `chamados.tempo_atendimento` | Timestamps (`fato_atendimento_gold`) |
|---|---|---|
| Chamados com os dois valores | 127.375 | 127.375 |
| Média | 216,6 s (3,6 min) | 662,3 s (11,0 min) |
| Chamados com duração ≥ 1.000 s | — | 27.987 (22,0%) |
| Média nesses chamados | 1,6 s | 2.030 s |
| Valor máximo | 999 s | 9.000 s |
| Campo maior que os timestamps | 0 chamados | — |

Query de conferência no Databricks (substituir a tabela acima pelos valores dela):

```sql
WITH r AS (
  SELECT DISTINCT id_chamado, try_cast(tempo_atendimento AS DOUBLE) AS campo_s
  FROM dados_vcredit.default.chamados_raw
), j AS (
  SELECT r.campo_s, f.tempo_atendimento_seg AS ts_s
  FROM r JOIN dados_vcredit.default.fato_atendimento_gold f USING (id_chamado)
  WHERE r.campo_s IS NOT NULL AND f.tempo_atendimento_seg IS NOT NULL
)
SELECT COUNT(*) AS n,
       ROUND(AVG(campo_s), 1) AS media_campo_s,
       ROUND(AVG(ts_s), 1) AS media_timestamp_s,
       COUNT_IF(ts_s >= 1000) AS duracao_ge_1000s,
       ROUND(AVG(CASE WHEN ts_s >= 1000 THEN campo_s END), 1) AS media_campo_ge_1000s,
       ROUND(AVG(CASE WHEN ts_s >= 1000 THEN ts_s END), 1) AS media_timestamp_ge_1000s,
       MAX(campo_s) AS max_campo_s,
       MAX(ts_s) AS max_timestamp_s,
       COUNT_IF(campo_s > ts_s) AS campo_maior_que_timestamp
FROM j
```

## Escalabilidade

Hoje todas as tabelas são regravadas por inteiro (`overwrite` / `CREATE OR REPLACE`) a cada 12 h, o que é adequado ao volume atual (~130 mil chamados, execução de 7 a 8 min no serverless).
Para volumes maiores, o caminho é:

- **Carga incremental** na bronze e na silver (por exemplo, `MERGE` por `id_chamado`/`id_custo` e ingestão por arquivo novo), no lugar do `overwrite` completo.
- **Particionamento por data** na fato e nas tabelas de grande volume, e `OPTIMIZE` periódico das tabelas Delta.
- **Parâmetros de Job** (por exemplo, `anonimizar_atendente`) em vez de editar notebook.
- O desenho em camadas e a idempotência por chave seguem valendo: só muda como cada camada atualiza as tabelas.

## Decisões do grupo

| Decisão | Escolha | Motivo |
|---|---|---|
| Hash do `id_cliente` | `sha2` (SHA-256) puro, sem segredo/HMAC | O `id_cliente` do case é dado fictício, não CPF real; o risco de reversão por força bruta que justificaria o HMAC não se aplica. Em dado real, usar HMAC com segredo |
| `nome_atendente` | Não é dado restrito (a regra vale para CPF/nome/e-mail de **cliente**) | A exportação tem o parâmetro `anonimizar_atendente` (padrão `false`) para trocar o nome por "Atendente <id>" |
| `status_atendente` | Mantido com esse nome em `chamados_silver`; só vira `status_id_atendente` na `base_silver` | Evita colisão com `atendentes_silver.status_atendente` (significado diferente: ativo/inativo no cadastro) |
| Clientes sem cadastro (1.330 chamados, 1,0%) | Membro `SEM_CADASTRO` criado na exportação para o Power BI (`dim_cliente` do modelo de consumo) | Esses chamados não somem dos relatórios |
| Tipos em `dim_cliente_gold` | `data_cadastro` vira `date`, `dia_vencimento_fatura` vira `int` | A silver entrega string |
| Fonte da verdade dos tempos | Só os timestamps de `chamados_hora`; `chamados.tempo_atendimento` nunca entra em indicador | Campo truncado (seção "Fonte da verdade dos tempos") |

Pendente: decidir se o material do Comitê mostra o nome real do atendente ou um rótulo anônimo
(`anonimizar_atendente`). Ver também [`../analitico/confiabilidade-dos-dados.md`](../analitico/confiabilidade-dos-dados.md).
