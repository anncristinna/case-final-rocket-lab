# 01 — Visão geral

Fonte: `visao_geral_gold`, `kpi_mensal_gold`, `comparativo_yoy_gold`. Período: 01/01/2025 a 31/07/2026 (19 meses).

## Indicadores do período

| Indicador | Valor |
|---|---|
| Chamados únicos | 131.838 |
| Abandonados | 3.414 (2,59%) |
| Taxa de resolução | 50,88% |
| TME (espera) | 3,60 min |
| TMA (atendimento) | 11,03 min |
| CSAT (notas 4 e 5) | 71,57% (nota média 3,98) |
| Custo total | R$ 1.450.617,85 |
| Custo médio por chamado | R$ 11,18 |
| Custo mensal médio | R$ 76.348,31 |

## Evolução: a piora é contínua, não pontual

| Mês | Chamados | Abandono | Resolução | TME (min) | TMA (min) | CSAT | Custo total (R$) | Custo/chamado (R$) |
|---|---|---|---|---|---|---|---|---|
| 2025-01 | 4.368 | 1,35% | 54,40% | 1,39 | 10,38 | 86,16% | 46.260 | 10,73 |
| 2025-07 | 6.069 | 2,22% | 51,92% | 2,51 | 11,00 | 78,65% | 66.599 | 11,15 |
| 2026-01 | 7.754 | 2,85% | 50,27% | 3,91 | 11,01 | 67,23% | 85.106 | 11,16 |
| 2026-07 | 9.596 | 3,82% | 47,75% | 5,70 | 11,18 | 56,68% | 105.731 | 11,18 |
| **Variação jan/25 → jul/26** | **+119,7%** | **×2,8** | **−6,65 p.p.** | **×4,1** | **+7,7%** | **−29,5 p.p.** | **+128,6%** | **+4,2%** |

Leitura:

- O volume mensal mais que dobrou (crescimento composto de ~4,5% ao mês). Janeiro a julho de 2026 contra o mesmo período de 2025: 60.646 contra 36.603 chamados (+65,7%).
- **O custo cresce com o volume, não com o custo unitário**: o custo por chamado ficou praticamente fixo (R$ 10,73 a R$ 11,18).
- **A degradação aparece na espera, não no tempo de atendimento**: TMA +7,7%, TME ×4,1. CSAT, abandono e resolução pioram mês a mês sem nenhuma inversão nos 19 meses.

## Comparativo ano contra ano (janeiro a julho)

| Mês | Chamados 2025 | 2026 | CSAT 2025 | 2026 | Abandono 2025 | 2026 | TME 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| Jan | 4.368 | 7.754 | 86,16% | 67,23% | 1,35% | 2,85% | 1,39 | 3,91 |
| Mar | 4.925 | 8.367 | 84,13% | 63,56% | 1,48% | 3,19% | 1,78 | 4,56 |
| Mai | 5.508 | 8.980 | 82,38% | 59,96% | 1,76% | 3,55% | 2,07 | 4,99 |
| Jul | 6.069 | 9.596 | 78,65% | 56,68% | 2,22% | 3,82% | 2,51 | 5,70 |

(`comparativo_yoy_gold` tem os 12 meses; agosto a dezembro de 2026 estão sem dados.)

## Falas das entrevistas contra os dados

| Quem | Afirmação | O que os dados mostram |
|---|---|---|
| Gerente Financeiro | O gasto passou de R$ 1,4 mi em 19 meses e cresce todo mês | **Confirmado**: R$ 1.450.617,85 (R$ 50.617,85, ou 3,6%, acima de R$ 1,4 mi). O custo mensal passou de R$ 46 mil para R$ 106 mil, **puxado por volume** (custo por chamado estável em ~R$ 11). A relação com a receita não pode ser testada: não há base de receita |
| Coord. de Customer Success | TMA subiu, resolução caiu (principalmente no nível 2) e muitos desistem antes de serem atendidos | **Em parte**: resolução −6,65 p.p. e abandono ×2,8, confirmados; o TMA geral subiu só 7,7% (o que explode é a **espera**). No Nível 2: resolução 63,8% → 57,7%, abandono 4,3% → 15,2%, TME 5,0 → 21,8 min (jan/25 → jul/26) |
| Diretor de Tecnologia | O chatbot resolve a maior parte; o problema é o perfil do usuário (analfabetos digitais) | **Não confirmado**: o chatbot resolve 48,97% (a URA, 45,38%); o autosserviço falha justamente nos casos mais caros: compra não autorizada (resolve 12,7% no autosserviço) e renegociação de dívida (11,2%). Idade pesa pouco (ver [`06-perfil-clientes.md`](06-perfil-clientes.md)). **Confirmado**: há inconsistências entre registros, custos e notas (ver confiabilidade dos dados) |
| Diretora de Marketing | O CSAT era 85% no começo de 2025; a piora é recente e externa à operação | **O ponto de partida é correto** (86,2% em jan/25), **mas a piora não é recente**: cai todos os meses, até 56,7% em jul/26 (−29,5 p.p.). Está ligada à espera: com espera até 5 min o CSAT é 83,0%, com 15 a 30 min, 10,3% (ver [`05-satisfacao.md`](05-satisfacao.md)) |
| Atendentes | Alta demanda por app/site lentos e URA confusa | **Compatível**: "Problema com aplicativo" é o 2º motivo (14.333 chamados, 10,9%); só 25,6% desses chamados se resolvem no autosserviço e 53,8% chegam a humano |

Obs.: nenhum dado de navegação da URA, do site ou do app foi fornecido. Essa causa só pode ser confirmada com
telemetria desses canais.
