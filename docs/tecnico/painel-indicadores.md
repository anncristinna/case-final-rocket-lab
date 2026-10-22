# Painel de indicadores consolidado (Power BI)

Entregável técnico: *painel de indicadores consolidado, com as principais métricas que ilustram o resultado dos
tratamentos*. O Databricks Free Edition não integra com o Power BI; o caminho previsto pelo enunciado é exportar a
camada gold em CSV e importar no Power BI Desktop. É o que faz o `Gold_To_CSV.ipynb`.

> ⚠️ O pacote do Power BI (`data/powerbi/pacote_powerbi.zip`, fora do git) traz **só os CSVs**. O arquivo `.pbix` embute dados e também fica fora do git.
> **Onde o `.pbix` será entregue:** drive compartilhado do grupo (link: _a preencher_). No repositório entram só o **PDF exportado** das páginas e os
> **prints**, em `docs/tecnico/evidencias/painel/` (a criar quando o painel ficar pronto). Antes de versionar, confira que as páginas não mostram
> nomes de atendentes nem qualquer dado de cliente.

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

## Painel mínimo da entrega (2 páginas)

Importe os CSVs com a localidade **Inglês (Estados Unidos)**: o pacote usa ponto decimal e datas `yyyy-MM-dd`. Se a localidade ficar em pt-BR, `1450617.85`
vira `145061785`. Os nomes de tabela abaixo são os dos arquivos; adapte as medidas se renomear (por exemplo, `fAtendimento`).

### Página 1: Visão geral

- **Tabelas:** `fato_atendimento`, `dim_calendario`, `dim_canal` (relacionamentos 1 → N de `dim_calendario[id_data]` e `dim_canal[id_canal]` para a fato).
- **Visuais:** cartões (Chamados, Taxa de resolução, TME, TMA, CSAT, Abandono, Custo e Custo por chamado); linha mensal por `dim_calendario[ano_mes]`
  (chamados em colunas, CSAT e TME em linhas); barras por `dim_canal[etapa_funil]` com % dos chamados, % do custo e CSAT.
- **Conferência:** os cartões têm que bater com `analiticas/visao_geral.csv`.

| Cartão | Valor esperado |
|---|---|
| Chamados | 131.838 |
| Taxa de resolução | 50,88% |
| TME | 3,60 min |
| TMA | 11,03 min |
| CSAT | 71,57% |
| Abandono | 2,59% |
| Custo | R$ 1.450.617,85 |
| Custo por chamado | R$ 11,18 |

### Página 2: Qualidade e tratamentos

- **Tabelas:** `analiticas/impacto_indicadores.csv` e `analiticas/qualidade_dados.csv`, sem relacionamento com o modelo.
- **Visuais:**
  - **Impacto dos tratamentos** (tabela, não gráfico, porque cada linha tem unidade diferente): `indicador`, `metodo_a`, `valor_a`, `metodo_b`, `valor_b`, `diferenca`. Destaque para o TME (−1.211,93 min bruto contra 3,60 min tratado) e para o CSAT (71,57% contra 70,96% com nota ajustada).
  - **Inconsistências** (barras por `grupo` e `indicador`, valor `pct_chamados`, com `qtd` na dica): as linhas marcadas `(informativo)` não são erro; **os indicadores se sobrepõem, não some**.
- **Mensagem da página:** o tratamento muda muito o custo e o TME, e pouco o TMA, o CSAT e a resolução.

### Medidas DAX (proposta, ainda não testada no Power BI)

Use `COUNTROWS(FILTER(...))` com `ISBLANK` nos denominadores. Em DAX, `BLANK() = FALSE()` é verdadeiro, e um filtro `<> BLANK()` descartaria os `false`.
Valide cada medida contra a tabela de valores esperados acima.

```dax
Chamados = COUNTROWS(fato_atendimento)

Taxa de resolução =
DIVIDE(
    COUNTROWS(FILTER(fato_atendimento, fato_atendimento[resolvido] = TRUE())),
    COUNTROWS(FILTER(fato_atendimento, NOT ISBLANK(fato_atendimento[resolvido])))
)

TME (min) = DIVIDE(AVERAGE(fato_atendimento[tempo_espera_seg]), 60)

TMA (min) = DIVIDE(AVERAGE(fato_atendimento[tempo_atendimento_seg]), 60)

Abandono =
DIVIDE(
    COUNTROWS(FILTER(fato_atendimento, fato_atendimento[abandonado] = TRUE())),
    [Chamados]
)

CSAT =
DIVIDE(
    COUNTROWS(FILTER(fato_atendimento, fato_atendimento[satisfeito] = TRUE())),
    COUNTROWS(FILTER(fato_atendimento, NOT ISBLANK(fato_atendimento[satisfeito])))
)

Custo = SUM(fato_atendimento[custo])

Custo por chamado =
DIVIDE(
    [Custo],
    COUNTROWS(FILTER(fato_atendimento, NOT ISBLANK(fato_atendimento[custo])))
)
```

`recontato_elegivel` hoje vale `true` para os 131.838 chamados (todos têm id de cliente, motivo mapeado e abertura conhecida), então filtrar por ele não exclui ninguém nesta base.

## Páginas adicionais (opcionais, mesma história da apresentação)

3. **Motivos**: Pareto, reincidência e custo por motivo. Fonte: `motivos_pareto`, `motivo_etapa`.
4. **Satisfação**: CSAT por faixa de espera, etapa e reincidência. Fonte: `satisfacao_drivers`.
5. **Operação**: demanda por dia e hora e atendentes. Fonte: `demanda_dia_hora`, `atendentes_desempenho`.
6. **Funil por etapa ao longo do tempo**: `etapa_mensal`.
7. **Simulação de ganhos**: cenários A e B com as premissas visíveis (e a ressalva de que **não se somam**). Fonte: `simulacao_ganhos`.

Cada página corresponde a um arquivo de [`../../resultados/`](../../resultados/), que traz os números de conferência.
