# Panorama geral da operação

> Conteúdo destinado ao Notion compartilhado do grupo. Números de `analise_geral_corrigida.py`, rodado
> localmente sobre os CSVs completos — reconfirmar no Databricks antes de publicar. Detalhes técnicos e
> comparação com o notebook original em `docs/achados_analise_geral.md`.

## Números principais

| Indicador | Valor |
|---|---|
| Chamados (únicos) | 131.838 |
| Clientes | 47.705 |
| Atendentes ativos | 20 |
| Custo total do período | R$ 1.447.671,52 |
| Taxa de resolução | 50,9% |
| Tempo médio de espera (TME) | 216,0 s (~3,6 min) |
| Tempo médio de atendimento (TMA) | 661,9 s (~11,0 min) |
| Abandono (sem início de atendimento) | 2,6% |
| CSAT (% notas 4 e 5) | 71,6% |
| Nota média | 3,98 / 5 (73.383 respostas) |

## Distribuição das notas de satisfação (válidas, 1 a 5)

| Nota | Respostas |
|---|---|
| 1 | 2.742 |
| 2 | 4.772 |
| 3 | 13.347 |
| 4 | 23.090 |
| 5 | 29.432 |

## Leitura

- Metade dos chamados é resolvida (50,9%) — há espaço claro de melhora.
- O tempo de atendimento médio real (11 min) é bem maior do que o que o notebook inicial mostrava, porque
  aquele usava um campo truncado do sistema de origem.
- 2,6% dos chamados terminam em abandono (cliente desiste antes do atendimento começar) — ver recorte por
  canal em `por_canal.md`, concentrado nos canais humanos.
