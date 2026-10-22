# Painel de indicadores consolidado (Power BI)

Entregável técnico: *painel de indicadores consolidado, com as principais métricas que ilustram o resultado dos
tratamentos*. O Databricks Free Edition não integra com o Power BI; o caminho previsto pelo enunciado é exportar a
camada gold em CSV e importar no Power BI Desktop. É o que faz o `Gold_To_CSV.ipynb`.

> ⚠️ O pacote que está no repositório de trabalho (`data/powerbi/pacote_powerbi.zip`, fora do git) traz **só os CSVs**.
> O arquivo `.pbix` do painel **não está** na pasta; ele também fica fora do git (embute dados). Guardar
> o `.pbix` no drive do grupo e anexar prints/PDF das páginas à entrega.

## Conteúdo do pacote (`exp_20261022_012729`, exportado em 22/10/2026 01:27 UTC)

| Pasta | Arquivos | Linhas |
|---|---|---|
| `modelo/` | `fato_atendimento` (47 colunas) | 131.838 |
| | `dim_calendario` (sem o membro `-1`), `dim_hora`, `dim_faixa_espera`, `dim_canal`, `dim_motivo`, `dim_atendente`, `dim_cliente` | 730 / 25 / 6 / 5 / 15 / 28 / 47.706 |
| `analiticas/` | As 14 tabelas analíticas da gold | ver [`../../resultados/`](../../resultados/) |
| raiz | `_manifesto.csv`, `_manifesto.json` | id do pacote, versão Delta de origem, checksum por tabela |

Formato: UTF-8, vírgula, cabeçalho, aspas duplas, ponto decimal, datas `yyyy-MM-dd`, timestamps `yyyy-MM-dd HH:mm:ss`,
booleanos `true`/`false`, nulo = campo vazio.

### O que o modelo de consumo muda em relação à gold

| Tabela | Ajuste | Motivo |
|---|---|---|
| `fato_atendimento` | Junta `qualidade_chamado_gold` por `id_chamado` (1 para 1, validado); acrescenta `cliente_mapeado` e `recontato_elegivel` | Um único relacionamento no Power BI, sem ambiguidade |
| `dim_calendario` | Remove a linha `id_data = -1` | Habilita inteligência temporal; chamados sem data continuam na fato |
| `dim_cliente` | Acrescenta o membro `SEM_CADASTRO` (hash fixo) | Os 1.330 chamados (1,0%) com `id_cliente` sem cadastro não somem do relatório |

## Relacionamentos (todos 1 → N, dimensão → fato)

| Dimensão | Chave | Coluna na fato |
|---|---|---|
| `dim_calendario` | `id_data` | `id_data` |
| `dim_hora` | `id_hora` | `id_hora` |
| `dim_faixa_espera` | `id_faixa_espera` | `id_faixa_espera` |
| `dim_canal` | `id_canal` | `id_canal` |
| `dim_motivo` | `id_motivo` | `id_motivo` |
| `dim_atendente` | `id_atendente` | `id_atendente` |
| `dim_cliente` | `id_cliente_hash` | `id_cliente_hash` |

Chaves negativas (`-1`, `-2`, `-3`) são membros desconhecidos, por desenho; elas mantêm 100% dos chamados na fato.

## Medidas (definições do projeto)

| Indicador | Definição | Coluna / observação |
|---|---|---|
| Chamados | Contagem de `id_chamado` | |
| Taxa de resolução | Chamados `resolvido = true` ÷ chamados com `resolvido` informado | 50,88% (os não informados ficam fora da conta) |
| TME | Média de `tempo_espera_seg` ÷ 60 | Só chamados atendidos, com sequência de horários válida |
| TMA | Média de `tempo_atendimento_seg` ÷ 60 | Idem; **nunca** o campo `tempo_atendimento` de `chamados` |
| Abandono | Média de `abandonado` | Sem horário de início de atendimento |
| CSAT | Notas ≥ 4 ÷ chamados com nota válida (1 a 5) | Média de `satisfeito`; versão `satisfeito_ajustado` usa `nota_ajustada` |
| Custo | Soma de `custo` | Só lançamentos > 0 |
| Custo por chamado | `custo` ÷ chamados com custo válido | R$ 11,18 |
| Reincidência (7d) | Média de `reincidente_7d` (usar `recontato_elegivel = true` como base) | Mesmo cliente e motivo em até 7 dias |

## Páginas sugeridas (mesma história da apresentação)

1. **Visão geral**: cartões (chamados, resolução, TME, TMA, CSAT, abandono, custo) e evolução mensal. Fonte: `visao_geral`, `kpi_mensal`.
2. **Funil e canais**: volume, custo e CSAT por etapa; TME por etapa ao longo do tempo. Fonte: `funil_atendimento`, `etapa_mensal`.
3. **Motivos**: Pareto, reincidência e custo por motivo. Fonte: `motivos_pareto`, `motivo_etapa`.
4. **Satisfação**: CSAT por faixa de espera, etapa, reincidência. Fonte: `satisfacao_drivers`.
5. **Operação**: demanda por dia e hora, atendentes. Fonte: `demanda_dia_hora`, `atendentes_desempenho`.
6. **Qualidade dos dados**: inconsistências e impacto nos KPIs. Fonte: `qualidade_dados`, `impacto_indicadores`.
7. **Simulação de ganhos**: cenários A e B com premissas editáveis. Fonte: `simulacao_ganhos`.

Cada página corresponde a um arquivo de [`../../resultados/`](../../resultados/), que traz os números de conferência.
