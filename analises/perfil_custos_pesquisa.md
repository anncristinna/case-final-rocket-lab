# Análise - custos

# id_custo

Inteiro, sequencial de 5.001 a 135.288, sem lacunas nesse intervalo (130.288 valores distintos, exatamente
o tamanho do intervalo). 781 ids aparecem em 2 linhas — são sempre a mesma linha repetida (`id_chamado` e
`custo` idênticos), não dois lançamentos diferentes com o mesmo id.

# id_chamado

Inteiro, chave de ligação com `chamados`. Nenhum valor nulo ou vazio. Praticamente 1 linha de custo por
chamado: 129.507 chamados com exatamente 1 lançamento e 781 com exatamente 2 (que são a duplicata
idêntica do `id_custo` acima) — nenhum chamado tem 2 custos realmente diferentes, só a mesma linha
duplicada.

# custo

Texto, nenhum valor vazio, mas em pelo menos 8 formatos: decimal com vírgula (`9,99`, a maioria — 51.053
linhas), com ponto (`9.99`), com `R$` na frente, com o sufixo `reais`, e negativos em qualquer uma dessas
combinações (98 a 10.580 linhas por combinação, ver `achados_analise_geral.md` pro detalhe completo).
Só remover todo ponto indiscriminadamente quebra o valor (ex.: `74.71reais` perderia o decimal e viraria
`7471`) — o parser precisa tratar vírgula como separador decimal brasileiro e o ponto como separador de
milhar só quando a vírgula também aparece no mesmo valor.

# Análise - pesquisa_satisfacao

# id_pesquisa

Inteiro, sequencial de 1 a 81.021, único — nenhuma duplicata (81.021 valores distintos para 81.021 linhas).

# id_chamado

Inteiro, chave de ligação com `chamados`. Nenhum valor nulo ou vazio. 79.417 chamados com exatamente 1
pesquisa e 802 com exatamente 2 (nunca mais que 2) — quando há 2, é quase sempre a mesma nota repetida
(751 dos 802 casos; os outros ~51 têm as duas linhas inválidas, e um pequeno resto mistura uma válida com
uma inválida).

# nota_atendimento

Deveria ser inteiro de 1 a 5. Duas formas distintas de "ausente": 2.842 linhas vêm realmente vazias (campo
nulo) e outras 2.836 trazem a string literal `"NULL"` como texto (não um campo vazio no CSV) — as duas
precisam ser tratadas como ausentes do mesmo jeito (um `try_cast` pra inteiro já resolve as duas, porque
`"NULL"` não converte pra número). Fora isso, 421 linhas têm `-1`, 393 têm `0` e 407 têm `6` — valores
fora da faixa válida. Somando tudo: **6.899 linhas inválidas** (2.842 + 2.836 + 421 + 393 + 407). Entre as
válidas: nota 5 (29.719), 4 (23.327), 3 (13.498), 2 (4.814) e 1 (2.764).
