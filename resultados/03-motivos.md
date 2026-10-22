# 03 — Motivos de contato

Fonte: `motivos_pareto_gold` e `motivo_etapa_gold` (14 motivos). `categoria` e `criticidade` vêm de `dim_motivo_gold`
(`categoria` vazia na origem virou "Outro": Cancelamento de conta, Contratação de cartão adicional e Transferência de agência).

## Pareto

| Motivo | Categoria | Crit. | Chamados | % | % acum. | Chegou ao humano | Nível 2 | Resolução | Reincidência 7d | TMA (min) | Custo/chamado (R$) | % do custo | CSAT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Consulta de fatura | Financeiro | baixa | 16.684 | 12,65% | 12,65% | 29,8% | 5,6% | 67,1% | 29,6% | 7,8 | 6,97 | 7,88% | 81,2% |
| Problema com aplicativo | Atendimento | média | 14.333 | 10,87% | 23,53% | 53,8% | 19,4% | 37,8% | 53,1% | 13,8 | 14,76 | 14,36% | 61,3% |
| Consulta de limite | Financeiro | baixa | 13.906 | 10,55% | 34,07% | 31,2% | 6,0% | 65,6% | 30,8% | 8,0 | 7,24 | 6,84% | 81,3% |
| Bloqueio de cartão | Cartão | alta | 13.128 | 9,96% | 44,03% | 32,8% | 6,6% | 63,5% | 32,3% | 8,3 | 7,69 | 6,86% | 80,7% |
| Compra não autorizada | Cartão | alta | 12.991 | 9,85% | 53,89% | 58,1% | 21,6% | 32,4% | 57,2% | 15,0 | 16,13 | 14,21% | 60,5% |
| Renegociação de dívida | Financeiro | alta | 12.377 | 9,39% | 63,27% | 59,3% | 23,1% | 30,8% | 58,4% | 15,3 | 16,73 | 14,02% | 57,4% |
| Contestação de fatura | Financeiro | alta | 11.139 | 8,45% | 71,72% | 54,7% | 18,6% | 36,9% | 53,9% | 13,7 | 14,54 | 10,99% | 63,5% |
| Desbloqueio de cartão | Cartão | alta | 8.810 | 6,68% | 78,41% | 33,0% | 8,1% | 62,9% | 32,6% | 8,6 | 8,17 | 4,88% | 79,0% |
| Cancelamento de conta | Outro | alta | 5.914 | 4,49% | 82,89% | 57,5% | 21,5% | 33,3% | 56,5% | 14,6 | 15,88 | 6,38% | 59,9% |
| Consulta de contrato | Financeiro | média | 5.540 | 4,20% | 87,09% | 36,3% | 8,2% | 59,5% | 36,0% | 9,2 | 8,75 | 3,28% | 77,6% |
| Dúvidas gerais sobre programa de pontos | Benefícios | baixa | 4.979 | 3,78% | 90,87% | 40,5% | 10,1% | 54,3% | 39,6% | 10,0 | 9,73 | 3,29% | 74,3% |
| Contratação de cartão adicional | Outro | média | 4.894 | 3,71% | 94,58% | 42,3% | 10,5% | 52,3% | 41,6% | 10,6 | 10,33 | 3,43% | 74,7% |
| Alteração de dados cadastrais | Cadastral | baixa | 4.669 | 3,54% | 98,12% | 23,2% | 5,3% | 74,0% | 22,8% | 7,1 | 6,17 | 1,95% | 84,7% |
| Transferência de agência | Outro | média | 2.474 | 1,88% | 100% | 40,3% | 9,9% | 54,8% | 39,6% | 10,0 | 9,70 | 1,63% | 74,7% |

## Dois grupos bem distintos

| Grupo | Motivos | % dos chamados | % do custo | Resolução | Reincidência 7d | CSAT |
|---|---|---|---|---|---|---|
| **A. Críticos e caros** | Problema com aplicativo, Compra não autorizada, Renegociação de dívida, Contestação de fatura, Cancelamento de conta | **43,0%** (56.754) | **60,0%** | 31% a 38% | 53% a 58% | 57% a 64% |
| **B. Simples (baixa criticidade)** | Consulta de fatura, Consulta de limite, Dúvidas sobre programa de pontos, Alteração de dados cadastrais | 30,5% | 20,0% | 54% a 74% | 23% a 40% | 74% a 85% |

(Grupo B soma 12,65 + 10,55 + 3,78 + 3,54 = 30,52% dos chamados e 7,88 + 6,84 + 3,29 + 1,95 = 19,96% do custo.)

- Os cinco motivos do grupo A têm **o mesmo padrão**: mais de 53% chegam ao humano, ~20% chegam ao Nível 2, resolvem só ~1/3 e **mais da metade volta em até 7 dias** (53% a 58%). O custo por chamado é o dobro do grupo B.
- Dos 14 motivos, só um passa de 70% de resolução (cadastral, 74,0%); fatura, limite, bloqueio e desbloqueio ficam entre 63% e 67%. **O autosserviço resolve bem o simples** (ex.: cadastral resolve 76,6% e fatura, 65,4% já no autosserviço) **e mal o crítico** (renegociação 11,2%, compra não autorizada 12,7%, cancelamento 15,3%, contestação 20,3%).

## Para onde vai cada motivo (`motivo_etapa_gold`)

| Motivo | Autosserviço | Nível 1 | Nível 2 | Resolução no autosserviço |
|---|---|---|---|---|
| Consulta de fatura | 70,2% | 24,3% | 5,6% | 65,4% |
| Consulta de limite | 68,9% | 25,2% | 6,0% | 63,5% |
| Bloqueio de cartão | 67,3% | 26,1% | 6,6% | 61,1% |
| Desbloqueio de cartão | 67,0% | 24,9% | 8,1% | 62,8% |
| Alteração de dados cadastrais | 76,8% | 18,0% | 5,3% | 76,6% |
| Consulta de contrato | 63,7% | 28,2% | 8,2% | 55,7% |
| Dúvidas sobre programa de pontos | 59,5% | 30,4% | 10,1% | 48,9% |
| Transferência de agência | 59,7% | 30,4% | 9,9% | 48,7% |
| Contratação de cartão adicional | 57,7% | 31,8% | 10,5% | 44,9% |
| Problema com aplicativo | 46,2% | 34,4% | 19,4% | 25,6% |
| Contestação de fatura | 45,3% | 36,1% | 18,6% | 20,3% |
| Cancelamento de conta | 42,5% | 36,0% | 21,5% | 15,3% |
| Compra não autorizada | 41,9% | 36,6% | 21,6% | 12,7% |
| Renegociação de dívida | 40,8% | 36,1% | 23,1% | 11,2% |

(% = parcela dos chamados do motivo em cada etapa.)

**Leitura**: os motivos de baixa criticidade (fatura, limite, cadastral, pontos) já são em boa parte autosserviço,
mas ainda **12.411 chamados** deles chegaram a atendimento humano. É a base do cenário A de
[`07-custos-e-simulacao.md`](07-custos-e-simulacao.md).
