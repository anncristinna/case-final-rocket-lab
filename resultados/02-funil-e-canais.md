# 02 — Funil de atendimento e canais

Fonte: `funil_atendimento_gold`, `etapa_mensal_gold`, `dim_canal_gold`. A etapa **Prevenção** (site e app) do funil do
case não aparece nos dados: a base de canais só traz os quatro canais de atendimento.

## Funil no período

| Etapa | Canal | Chamados | % chamados | Abandono | Resolução | TME (min) | TMA (min) | Custo total (R$) | % custo | Custo/chamado (R$) | CSAT |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Autosserviço | Chatbot | 35.517 | 26,94% | 0% | 48,97% | — | 1,89 | 20.153,68 | 1,39% | 0,58 | 86,44% |
| Autosserviço | URA | 39.533 | 29,99% | 0% | 45,38% | — | 3,51 | 71.949,96 | 4,96% | 1,85 | 83,99% |
| Nível 1 | Atendimento Inicial | 39.697 | 30,11% | 4,42% | 52,52% | 6,66 | 16,14 | 534.984,52 | 36,88% | 13,69 | 60,70% |
| Nível 2 | Atendimento Especializado | 17.091 | 12,96% | 9,70% | 63,73% | 13,59 | 38,77 | 823.529,69 | 56,77% | 48,98 | 34,12% |

Leitura:

- **Autosserviço absorve 56,9% dos chamados e custa 6,35% do total**; **Nível 1 e Nível 2 são 43,1% dos chamados e 93,7% do custo**. Um chamado no Nível 2 custa R$ 48,98: 84 vezes um no chatbot (R$ 0,58), 26 vezes um na URA (R$ 1,85) e 3,6 vezes um no Nível 1 (R$ 13,69).
- O funil real é parecido com o "atual" da figura 1 do enunciado (e longe do desejado, figura 2, com autosserviço dominante e humano mínimo): menos de **57%** dos chamados ficam no autosserviço.
- O autosserviço **não resolve a maioria**: 45% a 49% de resolução. Parte do que não se resolve ali chega ao humano (ver [`03-motivos.md`](03-motivos.md)).
- Satisfação despenca a cada etapa: 86% / 84% (chatbot / URA) → 61% (Nível 1) → 34% (Nível 2). Espera e abandono crescem na mesma direção.

## Evolução mensal por etapa

Fonte: `etapa_mensal_gold` (57 linhas = 19 meses × 3 etapas).

| Etapa | Mês | Chamados | Abandono | Resolução | TME (min) | TMA (min) | Custo/chamado (R$) | CSAT |
|---|---|---|---|---|---|---|---|---|
| Autosserviço | 2025-01 | 2.600 | 0% | 52,59% | 0,00 | 2,94 | 1,41 | 91,92% |
| | 2026-07 | 5.300 | 0% | 43,71% | 0,00 | 2,57 | 1,11 | 76,37% |
| Nível 1 | 2025-01 | 1.236 | 2,91% | 54,16% | 2,87 | 15,07 | 13,37 | 83,35% |
| | 2026-07 | 2.988 | 5,62% | 50,54% | 10,07 | 16,66 | 13,74 | 38,41% |
| Nível 2 | 2025-01 | 532 | 4,32% | 63,76% | 5,02 | 37,36 | 50,00 | 63,66% |
| | 2026-07 | 1.308 | 15,21% | 57,65% | 21,81 | 38,41 | 46,08 | 11,52% |

Leitura:

- O volume do **Nível 1 cresceu ×2,4 e o do Nível 2, ×2,5**; a participação de cada etapa no total ficou estável (~57% / 30% / 13%). Ou seja, não é o mix que piora: é a **escala**, sem capacidade correspondente (ver [`04-atendentes.md`](04-atendentes.md)).
- A **espera** é o que explode: TME do Nível 1 ×3,5 (2,9 → 10,1 min) e do Nível 2 ×4,3 (5,0 → 21,8 min). O TMA quase não muda.
- Em julho/26 o CSAT do Nível 2 chegou a **11,5%**, e quase 1 em cada 6 chamados do Nível 2 (15,2%) é abandonado antes do atendimento.
- O autosserviço também perde resolução (52,6% → 43,7%) e satisfação (91,9% → 76,4%) ao longo do tempo, algo que só se explica por mudança no tipo de demanda ou na qualidade do canal; os dados não permitem separar as duas hipóteses.
