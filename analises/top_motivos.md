# Top 10 motivos de chamado

> Conteúdo destinado ao Notion compartilhado do grupo. Números de `analise_geral_corrigida.py`, rodado
> localmente sobre os CSVs completos — reconfirmar no Databricks antes de publicar.

| Motivo | Categoria | Chamados | Resolução | TME |
|---|---|---|---|---|
| Consulta de fatura | Financeiro | 16.684 | 67,1% | 134,9 s |
| Problema com aplicativo | Atendimento | 14.333 | 37,8% | 298,6 s |
| Consulta de limite | Financeiro | 13.906 | 65,6% | 143,8 s |
| Bloqueio de cartão | Cartão | 13.128 | 63,5% | 150,4 s |
| Compra não autorizada | Cartão | 12.991 | 32,4% | 309,5 s |
| Renegociação de dívida | Financeiro | 12.377 | 30,8% | 317,1 s |
| Contestação de fatura | Financeiro | 11.139 | 36,8% | 276,2 s |
| Desbloqueio de cartão | Cartão | 8.810 | 62,9% | 156,2 s |
| Cancelamento de conta | (sem categoria — a confirmar) | 5.914 | 33,3% | 305,8 s |
| Consulta de contrato | Financeiro | 5.540 | 59,5% | 168,9 s |

## Leitura

- Os motivos mais simples (consultas de fatura/limite, bloqueio/desbloqueio de cartão) têm resolução
  acima de 60% e espera mais curta — bons candidatos a prevenção/autosserviço.
- Os motivos mais complexos (Compra não autorizada, Renegociação de dívida, Contestação de fatura,
  Cancelamento de conta) têm a **pior resolução (31% a 37%)** e a **maior espera** — concentram o
  problema de qualidade do atendimento.
- "Cancelamento de conta" é um dos 3 motivos sem categoria cadastrada (ver `docs/achados_analise_geral.md`,
  pendência a validar com o grupo).
