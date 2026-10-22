# 06 — Perfil dos clientes (faixa etária e região)

Fonte: `perfil_cliente_gold` (36 linhas: dimensão × valor × etapa do funil), a partir de `dim_cliente_gold`
(`faixa_etaria`, `regiao`). Chamados sem cadastro na base de clientes (1.330, ~1,0%) ficam fora desta análise
(junção interna). Nenhum dado pessoal: só faixas e regiões.

## Faixa etária: efeito pequeno

| Faixa | Chamados | % no autosserviço | % Nível 2 | Resolução no autosserviço | CSAT no autosserviço | CSAT no Nível 1 | CSAT no Nível 2 |
|---|---|---|---|---|---|---|---|
| 18-24 | 85 | 63,5% | 8,2% | 57,4% | 96,6% | 57,1% | 50,0% |
| 25-34 | 6.845 | 58,2% | 12,1% | 49,1% | 85,8% | 63,2% | 33,3% |
| 35-44 | 28.226 | 58,1% | 12,7% | 49,8% | 85,9% | 60,5% | 32,5% |
| 45-54 | 37.441 | 57,2% | 12,7% | 47,4% | 85,3% | 60,5% | 35,0% |
| 55-64 | 27.978 | 56,5% | 13,2% | 46,3% | 85,2% | 61,4% | 34,2% |
| 65+ | 27.628 | 55,4% | 13,6% | 43,9% | 84,1% | 60,0% | 34,4% |
| Sem idade (inválida ou ausente) | 2.305 | 57,4% | 12,8% | 48,0% | 84,7% | 60,9% | 36,7% |

Leitura:

- Os mais velhos usam menos o autosserviço (55,4% contra 58,2% de 25-34) e resolvem menos nele (43,9% contra 49,1%), e a diferença é gradual. Isso **dá algum apoio** à fala do Diretor de Tecnologia sobre baixa familiaridade digital, mas o efeito é **modesto** (~5 p.p. na resolução do autosserviço), e a satisfação é praticamente igual em todas as faixas.
- A faixa 18-24 tem só 85 chamados (a base de clientes é concentrada em idades mais altas); não dá para tirar conclusão estatística dela.
- O perfil de idade **não explica** o gargalo do funil: ele existe para todas as idades.

## Região: sem diferença

| Região | Chamados | % no autosserviço | % Nível 1 | % Nível 2 | Resolução no autosserviço | Abandono N2 | CSAT N1 | CSAT N2 |
|---|---|---|---|---|---|---|---|---|
| Sudeste | 55.930 | 56,9% | 30,0% | 13,1% | 47,3% | 9,5% | 60,6% | 33,4% |
| Nordeste | 34.619 | 56,9% | 30,3% | 12,9% | 46,8% | 10,2% | 61,6% | 33,5% |
| Sul | 19.681 | 56,9% | 30,2% | 13,0% | 46,9% | 9,1% | 61,2% | 34,7% |
| Centro-Oeste | 11.172 | 57,1% | 30,1% | 12,8% | 47,3% | 10,1% | 59,6% | 35,8% |
| Norte | 9.106 | 57,1% | 30,1% | 12,8% | 47,3% | 10,1% | 59,1% | 37,7% |

Região **não é fator**: a distribuição por etapa varia menos de 0,5 p.p. e os demais indicadores pouco (CSAT do Nível 1 de 59% a 62%; do Nível 2, de 33% a 38%, a maior diferença, com amostras regionais menores). Recomendações que dependam de região (ex.: reforço regional) **não têm base nos dados**.
