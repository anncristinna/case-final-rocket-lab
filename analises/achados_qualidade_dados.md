# Qualidade dos dados

> Números medidos numa execução local sobre os CSVs completos; reconfirmar no Databricks antes de usar em slides.

Números **medidos** rodando um pipeline bronze → tratamento → consolidação localmente (Spark 4.2) sobre os CSVs completos.
As contagens brutas (coluna "arquivo") batem exatamente com os arquivos originais.
Este documento alimenta a entrega "leitura sobre a confiabilidade dos dados".

## Volumes

| Base | Linhas (arquivo) | Linhas (após tratamento sugerido) | Encoding |
|---|---|---|---|
| chamados | 134.474 | 131.838 | utf-8 |
| chamados_hora | 131.838 | 131.838 | cp1252 |
| clientes | 47.705 | 47.705 | cp1252 |
| custos | 131.069 | 130.288 | utf-8 |
| pesquisa_satisfacao | 81.021 | 81.021 | utf-8 |
| base_atendentes / base_motivos / canais | 25 / 14 / 4 | idem | utf-8 |

A diferença entre `chamados` e `chamados_hora` (2.636) são **duplicatas idênticas** em `chamados`:
após remover, os dois batem em 131.838 e todo chamado tem horário. Nota: o leitor de CSV do Spark testado
não aceitou `windows-1252`, então o código usa `iso-8859-1`, idêntico ao cp1252 para letras acentuadas do português.

## Problemas encontrados e tratamento

| # | Base | Problema | Quanto | Tratamento sugerido |
|---|---|---|---|---|
| 1 | chamados | Linhas duplicadas (idênticas) por `id_chamado` | 2.636 (2,0%) | `dropDuplicates` por id |
| 2 | chamados | `canal` com 8 grafias para 4 canais (`U.R.A`, `Chat Bot`, `Atend. Inicial`, `Atend. Especializado`, caixa e `_`) | 20.210 linhas (15%) usavam grafia fora do cadastro | `canal_key` normalizada + mapa de aliases |
| 3 | chamados | `motivo` com variação de caixa | todos casam após normalizar | `motivo_key` |
| 4 | chamados | `resolvido` em formatos mistos (`Sim`, `Não`, `S`, `N`, `1`, `0`, `Nao resolvido`, vazio) | vazio/inválido em 2.014 (1,5%) | booleano; inválido → `null` + `dq_resolvido_invalido` |
| 5 | chamados | `id_atendente` placeholder (0, 99, 999) fora do cadastro | 764 chamados (0,6%) | `dq_atendente_invalido`; nível fica `null` na consolidação |
| 6 | chamados | `tempo_atendimento` **truncado**: valores ≥ 1.000 s aparecem como 1–9 (só a casa do milhar) | 27.987 chamados; 39% do atendimento inicial e **86% do especializado**; chatbot/URA 0% | usar tempo calculado dos timestamps; guardar o original e `tempo_divergente` |
| 7 | chamados | `tempo_espera` com o mesmo truncamento | 6.107 chamados | idem |
| 8 | chamados | Colunas `hora_*` vazias | 100% | horários vêm de `chamados_hora` |
| 9 | chamados_hora | Timestamp `dd/MM/yyyy às HH:mm:ss` com encoding quebrado | todos | regex remove o "às" |
| 10 | chamados_hora | **Ano da abertura errado** (+1 ou +2 anos, caindo em 2026/2027, depois da finalização) | 198 chamados | corrigido subtraindo os anos; `dq_abertura_corrigida` |
| 11 | chamados_hora | Ordem inválida remanescente (fim < início) | 1 | tempos calculados ficam `null`; `dq_ordem_invalida` |
| 12 | chamados_hora | Sem hora de início, mas com espera registrada e sem tempo de atendimento: **cliente desistiu** | 3.414 (2,6%) | `dq_sem_inicio` → `abandonado` na gold |
| 13 | clientes | `data_cadastro` em dois formatos (`dd/MM/yyyy`, `yyyy-MM-dd`) | todas parseiam | `coalesce` dos dois formatos |
| 14 | clientes | Idade impossível (faixa observada 0–199) | 839 clientes (1,8%) | `dq_idade_invalida` (valor mantido, fora de 18–110 sinalizado) |
| 15 | clientes | **Dado pessoal** (CPF como `id_cliente`, nome, e-mail) | — | a confirmar no notebook: remover nome/e-mail e usar `cliente_hash` no lugar do CPF em qualquer saída consolidada |
| 16 | clientes/chamados | Chamado de cliente sem cadastro | 1.330 chamados (1,0%) | left join; região/idade `null` |
| 17 | custos | Formatos mistos: `9,9` · `9.9` · `R$ 9,9` · `9.9reais` · negativos | `9.9reais` em 10.580; negativos ~273 | remove tudo exceto dígitos/`,`/`.`/`-` e converte |
| 18 | custos | Linhas duplicadas (idênticas) | 781 | `dropDuplicates` por `id_custo` |
| 19 | custos | Custo ≤ 0 | 544 | mantido + `dq_custo_nao_positivo` (decidir se exclui) |
| 20 | custos | Chamados sem custo | 1.550 (1,2%) | `custo_total` `null` na consolidação |
| 21 | pesquisa | Notas inválidas: `-1` (421), `0` (393), `6` (407), vazias (5.678) | ~8,5% das linhas | nota fora de 1–5 → `null` + `dq_nota_invalida` |
| 22 | pesquisa | Chamado com mais de uma pesquisa (mesma nota) | 802 | média por chamado na consolidação |
| 23 | atendentes | `nivel_atendimento` em `1`, `Nível 1`, `N2`, `2`, `Nível 2` | 25 linhas | extrai o dígito |
| 24 | motivos | `categoria` vazia (3 de 14) e `criticidade` com caixa mista | — | imputação por critério do enunciado (**premissa a validar**) + `categoria_imputada` |

## Impacto nos indicadores (ingênuo vs. tratado)

| Indicador | Ingênuo | Tratado | Por quê |
|---|---|---|---|
| Volume de chamados | 134.474 | 131.838 | duplicatas |
| **TMA geral** | 217 s | **662 s** | `tempo_atendimento` truncado |
| **TMA canais humanos** | 290 s | **1.361 s** (4,7×) | idem |
| Custo total (jan/25–jul/26) | R$ 1.332.073 (descartando `…reais`) | **R$ 1.447.672** | −R$ 115,6 mil (−8%) sumiam por formato |
| Meses no período | 19 + meses fantasmas em 2027 | 19 (jan/25–jul/26) | ano da abertura errado |
| Abandono | invisível (parece "sem dado") | 3.414 chamados | linha sem início de atendimento |

Chamados do chatbot e da URA não sofrem o truncamento do tempo; o erro se concentra justamente nos canais humanos,
os mais caros. Qualquer análise de produtividade que use o campo original **subestima o TMA humano em ~4,7×**.

## Decisões tomadas (com evidência)

1. **Fonte da verdade dos tempos = timestamps** (`chamados_hora`). Evidência: o campo original é truncado
   em valores ≥ 1.000 s e coincide com os timestamps nos demais casos. O original é mantido para auditoria.
2. **Sem hora de início = abandono.** Evidência: nesses chamados `tempo_espera` está preenchido (mediana ~5 min)
   e `tempo_atendimento` vazio.
3. **Duplicatas removidas** (idênticas, sem perda de informação).

## Pendente

- Custo ≤ 0 (544): estorno ou erro? Decidir se entra na soma.
- Atendimentos antes da admissão / depois do desligamento do atendente (não testado).
- Premissa de `categoria` imputada nos 3 motivos sem categoria.
- Confirmar que os números batem rodando no Databricks.
