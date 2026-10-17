# Operação por região

> Conteúdo destinado ao Notion compartilhado do grupo. Números de `analise_geral_corrigida.py`, rodado
> localmente sobre os CSVs completos — reconfirmar no Databricks antes de publicar. Vem do cruzamento
> `chamados` × `clientes` (só o atributo `regiao`, nunca CPF/nome/e-mail).

## Volume e atendimento

| Região | Chamados | Idade média | Resolução | TME |
|---|---|---|---|---|
| Sudeste | 55.930 | 53,9 anos | 50,8% | 216,9 s |
| Nordeste | 34.619 | 54,2 anos | 50,8% | 215,3 s |
| Sul | 19.681 | 54,0 anos | 51,0% | 217,1 s |
| Centro-oeste | 11.172 | 54,3 anos | 51,2% | 214,1 s |
| Norte | 9.106 | 53,5 anos | 51,3% | 215,8 s |

## Custo

| Região | Custo total | Custo médio/chamado | Chamados |
|---|---|---|---|
| Sudeste | R$ 617.477,69 | R$ 11,17 | 55.293 |
| Nordeste | R$ 378.499,64 | R$ 11,06 | 34.213 |
| Sul | R$ 218.009,79 | R$ 11,22 | 19.431 |
| Centro-oeste | R$ 120.613,96 | R$ 10,93 | 11.032 |
| Norte | R$ 99.217,65 | R$ 11,01 | 9.009 |

## Leitura

- Resolução, idade média e TME são **muito parecidos entre regiões** (diferença menor que 1 p.p. na
  resolução, poucos segundos no TME) — a região não parece ser um fator relevante no atendimento.
- O custo total segue proporcionalmente o volume de chamados (Sudeste concentra ~42% do volume e ~43%
  do custo); o custo médio por chamado também é uniforme (~R$ 11 em todas as regiões).
- Conclusão preliminar: os problemas de atendimento (resolução, espera) parecem estruturais/por
  canal e motivo, não geográficos — ver `por_canal.md` e `top_motivos.md` para onde focar.
