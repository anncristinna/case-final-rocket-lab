# Operação por canal

> Conteúdo destinado ao Notion compartilhado do grupo. Números de `analise_geral_corrigida.py`, rodado
> localmente sobre os CSVs completos — reconfirmar no Databricks antes de publicar.

| Canal | Chamados | Resolução | TME | TMA | Abandono | Custo médio | CSAT |
|---|---|---|---|---|---|---|---|
| Atendimento inicial | 39.697 | 52,5% | 399,5 s | 968,5 s | 4,4% | R$ 13,60 | 60,7% |
| URA | 39.533 | 45,4% | — (0 s) | 210,6 s | 0,0% | R$ 1,84 | 84,0% |
| Chatbot | 35.517 | 49,0% | — (0 s) | 113,6 s | 0,0% | R$ 0,57 | 86,4% |
| Atendimento especializado | 17.091 | 63,7% | 815,6 s | 2.326,0 s | 9,7% | R$ 48,68 | 34,1% |

*TME aparece como 0s na URA e no Chatbot porque são canais de autosserviço — não há fila, o atendimento
começa no mesmo instante da abertura.*

## Leitura

- O atendimento especializado tem a **melhor resolução (63,7%)** e o **maior custo médio (R$ 48,68)**,
  mas a **pior satisfação (CSAT 34,1%)** e o **maior abandono (9,7%)** — é onde os casos mais complexos
  (e mais caros) terminam, e isso cobra satisfação.
- URA e Chatbot (autosserviço) custam quase nada por chamado (R$ 1,84 e R$ 0,57) e têm CSAT alto (84% e
  86%), mas resolução mais baixa (45,4% e 49,0%) — fazem bem o que resolvem, mas resolvem menos casos.
- Abandono só existe nos canais humanos (4,4% no inicial, 9,7% no especializado) — faz sentido, já que
  autosserviço não tem fila de espera por um atendente.
