# Custos e pesquisa de satisfação — Milton

> Preenchido a partir de `analises/milton_custos_pesquisa.py`, rodado localmente (PySpark) sobre os CSVs
> completos de `data/raw/`. Destinado ao Notion compartilhado do grupo — reconfirmar rodando no Databricks
> antes de publicar. Nenhuma linha de `clientes` (CPF/nome/e-mail) aparece aqui.
>
> Cada seção tem um bloco **"Como foi calculado"** com a definição do termo, as colunas de origem e o
> raciocínio aplicado — pra quem for ler no Notion sem abrir o notebook entender de onde vem o número.

## Problemas já conhecidos (confirmados ao rodar)

- `custo` em 8+ formatos de texto (`9,99`, `99.99`, `R$ 9,99`, `9.99reais`, negativos...) — já tratado
  no notebook base.
- 781 linhas duplicadas (idênticas) por `id_custo` → **130.288 custos únicos**.
- 544 custos ≤ 0 (271 negativos + 273 zero) — ver decisão pendente abaixo.
- 1.550 chamados sem nenhum lançamento de custo.
- 6.899 notas inválidas no arquivo (antes de deduplicar); 6.836 após dedup (ver nota na seção de pesquisa).
- 802 chamados com mais de uma pesquisa registrada — dedup prioriza a nota válida quando existe.

> **Como foi calculado:** tudo isso vem de `custos.custo` (texto bruto) e `pesquisa_satisfacao.nota_atendimento`
> (texto bruto), lidos sem `inferSchema` (tudo string) no notebook base. "Duplicada" = mesma linha
> repetida com o mesmo `id_custo`/não se aplica a `id_pesquisa`, mas a mesma combinação de `id_chamado` +
> nota repetida é o caso de pesquisa duplicada.

## Custo total e a decisão pendente sobre custo ≤ 0

| Cenário | Custo total |
|---|---|
| Incluindo custo ≤ 0 (mantido com flag) | **R$ 1.447.671,52** |
| Excluindo custo ≤ 0 (tratado como estorno/erro) | R$ 1.450.617,85 |

Diferença: R$ 2.946,33 (~0,2% do total) — **decisão do grupo**, não decidimos por conta própria.

> **Como foi calculado:** `custo_total` = soma de `custos.custo` (já convertido de texto pra número:
> mantém só dígitos/`,`/`.`/`-`, trata vírgula como decimal brasileiro) após remover as 781 linhas
> duplicadas por `id_custo`. `dq_custo_invalido` marca valores que não converteram pra número mesmo
> depois da limpeza (ficam fora da soma nos dois cenários). `dq_custo_nao_positivo` marca `custo <= 0`
> (negativo ou zero) — **"incluindo"** soma todo `custo` válido; **"excluindo"** filtra `custo > 0` antes
> de somar. "Chamados sem custo" = `chamados.id_chamado` que não aparece em nenhuma linha válida de
> `custos` (join `LEFT ANTI` entre as duas tabelas).

## Custo mensal x volume de chamados

Custo médio por chamado **estável (~R$ 11)** do início ao fim; o gasto total mais que dobrou porque o
**volume** mais que dobrou (4.368 → 9.599 chamados/mês). `qtd_lancamentos` = chamados com custo lançado
naquele mês; `qtd_chamados` = volume total do mês (alguns chamados não têm custo lançado).

| Mês | Custo total | Chamados | Custo médio/chamado |
|---|---|---|---|
| 2025-01 | R$ 46.118,21 | 4.368 | R$ 10,56 |
| 2025-02 | R$ 51.123,41 | 4.688 | R$ 10,91 |
| 2025-03 | R$ 51.977,90 | 4.925 | R$ 10,55 |
| 2025-04 | R$ 57.860,17 | 5.221 | R$ 11,08 |
| 2025-05 | R$ 59.989,49 | 5.508 | R$ 10,89 |
| 2025-06 | R$ 63.554,22 | 5.824 | R$ 10,91 |
| 2025-07 | R$ 66.540,42 | 6.069 | R$ 10,96 |
| 2025-08 | R$ 67.825,17 | 6.322 | R$ 10,73 |
| 2025-09 | R$ 71.387,68 | 6.558 | R$ 10,89 |
| 2025-10 | R$ 75.434,99 | 6.941 | R$ 10,87 |
| 2025-11 | R$ 80.164,68 | 7.215 | R$ 11,11 |
| 2025-12 | R$ 83.896,55 | 7.552 | R$ 11,11 |
| 2026-01 | R$ 84.905,77 | 7.753 | R$ 10,95 |
| 2026-02 | R$ 89.374,76 | 8.090 | R$ 11,05 |
| 2026-03 | R$ 91.767,33 | 8.365 | R$ 10,97 |
| 2026-04 | R$ 95.917,98 | 8.598 | R$ 11,16 |
| 2026-05 | R$ 100.599,06 | 8.981 | R$ 11,20 |
| 2026-06 | R$ 103.575,88 | 9.261 | R$ 11,18 |
| 2026-07 | R$ 105.657,85 | 9.599 | R$ 11,01 |

> **Como foi calculado:** `mes` = mês da **finalização** do chamado (`chamados_hora.hora_finalizacao_atendimento`,
> truncado pro primeiro dia do mês) — não o mês da abertura, porque ~198 chamados têm o ano da abertura
> errado. `qtd_chamados` conta **todos** os chamados daquele mês (`COUNT(*)` sobre a base consolidada,
> sem filtrar custo); `qtd_lancamentos` conta só os que têm `custo` válido. `custo_medio_por_chamado` =
> `custo_total / qtd_chamados` — divide pelo **volume total**, não só por quem tem lançamento (senão o
> número fica artificialmente mais alto, diluindo errado o efeito dos chamados sem custo). `custo_acumulado`
> = soma corrida mês a mês (window function ordenada por `mes`).

## Custo por canal, motivo, categoria e nível do atendente

| Canal | Custo médio | Chamados |
|---|---|---|
| Atendimento especializado | R$ 48,68 | 17.091 |
| Atendimento inicial | R$ 13,60 | 39.697 |
| URA | R$ 1,84 | 39.533 |
| Chatbot | R$ 0,57 | 35.517 |

| Nível do atendente | Custo médio | Chamados |
|---|---|---|
| 1 | R$ 6,65 | 90.215 |
| 2 | R$ 20,96 | 40.859 |

Diferença nível 2 − nível 1: **R$ 14,31/chamado** (nível 2 custa ~3,2× o nível 1) — base da recomendação
quantificada abaixo.

| Categoria do motivo | Custo médio | Chamados |
|---|---|---|
| Atendimento | R$ 14,68 | 14.333 |
| (sem categoria — a confirmar) | R$ 12,61 | 13.282 |
| Cartão | R$ 10,87 | 34.929 |
| Financeiro | R$ 10,57 | 59.646 |
| Benefícios | R$ 9,66 | 4.979 |
| Cadastral | R$ 6,11 | 4.669 |

Motivo mais caro em média: "Renegociação de dívida" (R$ 16,64); mais barato: "Alteração de dados
cadastrais" (R$ 6,11).

> **Como foi calculado:** `canal_key` = `chamados.canal` normalizado (minúsculo, sem acento, `_`/`-` →
> espaço) e mapeado pelos aliases conhecidos (`U.R.A`→`ura`, `Chat Bot`→`chatbot`, `Atend. Inicial`→
> `atendimento inicial`, `Atend. Especializado`→`atendimento especializado`) — sem isso, a mesma grafia em
> caixa/formato diferente contaria como canal separado. `motivo_key` é a mesma normalização aplicada a
> `chamados.motivo`. `categoria` vem de `base_motivos.categoria` (ligado por `motivo_key`); quando vazia,
> aparece como "(sem categoria — a confirmar)" em vez de descartar a linha. `nivel_atendente` = o dígito
> extraído de `base_atendentes.nivel_atendimento` (regex, cobre `1`, `Nível 1`, `N2` etc.), ligado por
> `chamados.id_atendente`. `custo_medio` = média de `custo` (soma de `custos` por chamado, já ligada à
> base) dentro de cada grupo; `chamados` conta todos os chamados do grupo, inclusive quem não tem custo
> (`AVG` do Spark ignora nulos automaticamente, `COUNT(*)` não). A diferença nível 2 − nível 1 é a base
> da recomendação: tratamos `nivel_atendente` como uma **aproximação** de "este chamado foi escalado" —
> não existe no dataset um campo que diga isso diretamente.

## Pareto: onde o gasto se concentra

| Canal | % acumulado do custo | % dos chamados |
|---|---|---|
| Atendimento especializado | 56,8% | 13,0% |
| + Atendimento inicial | 93,7% | 43,1% |
| + URA | 98,6% | 73,1% |
| + Chatbot | 100% | 100% |

Os 4 primeiros motivos ("Problema com aplicativo", "Compra não autorizada", "Renegociação de dívida",
"Contestação de fatura") já respondem por **53,6%** do custo total.

> **Como foi calculado:** agrupa por `canal_key` (ou `motivo_key`), soma `custo` por grupo, ordena do
> maior pro menor custo e acumula essa soma (window function) dividindo pelo custo total geral — é o
> clássico "80/20": mostra quantos grupos (ordenados do mais caro pro mais barato) já explicam a maior
> parte do gasto.

## Pesquisa de satisfação — qualidade e taxa de resposta

Taxa de resposta geral: **55,7%** dos chamados únicos. Cai de 65% (jan/25) para 48% (jul/26) — risco de
viés: quem responde hoje pode não representar mais quem respondia no início.

| Canal | Taxa de resposta |
|---|---|
| URA | 57,2% |
| Chatbot | 56,0% |
| Atendimento inicial | 55,1% |
| Atendimento especializado | 52,9% |

> **Como foi calculado:** `nota_atendimento` só é válida de 1 a 5; `-1`, `0`, `6` e vazio viram `null` +
> flag `dq_nota_invalida` (6.899 linhas do arquivo, antes de deduplicar). Quando um `id_chamado` tem mais
> de uma pesquisa (802 casos), o dedup usa `ROW_NUMBER()` particionado por `id_chamado`, ordenado pra
> colocar nota válida primeiro — fica 1 linha por chamado, priorizando a nota válida quando existe (6.836
> notas inválidas sobram após o dedup, um pouco menos que as 6.899 brutas, porque às vezes a segunda
> linha duplicada tinha a nota válida). **Taxa de resposta** = chamados com `nota` não nula na base
> consolidada (ou seja, com pesquisa válida) ÷ total de chamados únicos — **não é** "quantas pesquisas
> existem", é "quantos chamados têm uma nota válida".

## CSAT por mês, canal, nível, motivo, categoria e resolução

CSAT mensal: **86,2% em jan/2025 caindo para 56,7% em jul/2026.**

| Canal | CSAT | Nota média |
|---|---|---|
| Chatbot | 86,4% | 4,40 |
| URA | 84,0% | 4,32 |
| Atendimento inicial | 60,7% | 3,70 |
| Atendimento especializado | 34,1% | 2,86 |

| Nível do atendente | CSAT | Nota média |
|---|---|---|
| 1 | 74,5% | 4,07 |
| 2 | 65,0% | 3,76 |

| Resolvido | CSAT | Nota média |
|---|---|---|
| Sim | 84,2% | 4,36 |
| Não | 58,0% | 3,57 |

Por categoria do motivo: Cadastral (84,7%) e Benefícios (74,2%) no topo; Atendimento (61,3%) no fim.

> **Como foi calculado:** **CSAT** = % de respostas com `nota >= 4` (ou seja, nota 4 ou 5) entre as
> respostas **válidas** (`nota` não nula) — nunca entre o total de chamados, só entre quem respondeu com
> nota válida. **Nota média** = média simples de `nota` no mesmo recorte. `resolvido` vem de
> `chamados.resolvido`, um campo de texto livre (`Sim`, `Não`, `S`, `N`, `1`, `0`, `Nao resolvido`,
> vazio) normalizado pro booleano `true`/`false`/`null` antes de agrupar. Cada tabela acima é o mesmo
> cálculo de CSAT/nota média, só trocando a coluna de agrupamento (`canal_key`, `nivel_atendente`,
> `motivo_key`, `categoria`, `resolvido`).

### Testando a fala do Marketing: "CSAT era 85% em jan/25; a piora é externa"

| Canal | CSAT jan/2025 | CSAT jul/2026 | Queda |
|---|---|---|---|
| Atendimento especializado | 63,7% | 11,5% | **−52,1 p.p.** |
| Atendimento inicial | 83,4% | 38,4% | **−45,0 p.p.** |
| URA | 91,8% | 72,6% | −19,2 p.p. |
| Chatbot | 92,3% | 78,9% | −13,3 p.p. |

A queda é 3-4× maior nos canais humanos — **não parece uma causa externa e geral**, e sim um problema
operacional concentrado no atendimento humano.

> **Como foi calculado:** calcula o CSAT (mesma definição acima) por `mes` e `canal_key`, pega o primeiro
> e o último mês com dado (jan/2025 e jul/2026) e usa `PIVOT` pra colocar os dois meses lado a lado por
> canal. A lógica do teste: se a queda fosse por um motivo externo e geral (ex.: um problema do mercado,
> sazonalidade), esperaríamos uma queda parecida em todos os canais; o fato de cair muito mais nos canais
> com atendente humano do que no autosserviço (URA/Chatbot) aponta pra uma causa interna e operacional.

## Nota x tempo de espera, x TMA e x abandono

| Faixa de espera (TME) | CSAT | Nota média |
|---|---|---|
| 0-1 min | 85,1% | 4,36 |
| 1-5 min | 75,1% | 4,10 |
| 5-15 min | 49,2% | 3,43 |
| 15+ min | **8,6%** | 2,03 |

| Abandonado | Chamados | Taxa de resposta | Nota média |
|---|---|---|---|
| Não | 128.424 | 56,6% | 4,00 |
| Sim | 3.414 | 20,6% | **1,14** |

Abandono reduz muito a chance de resposta, mas quando o cliente que desistiu responde, a nota é péssima.

> **Como foi calculado:** **TME** (tempo médio de espera) = `hora_inicio_atendimento − hora_abertura_chamado`
> em segundos, **sempre** pelos timestamps de `chamados_hora` (nunca pelo campo `tempo_espera` de
> `chamados`, que vem truncado para durações ≥ 1.000 s). As faixas (0-1 min, 1-5 min, 5-15 min, 15+ min)
> são cortes que escolhemos pra visualizar a relação, não uma definição oficial do case. **Abandonado** =
> `hora_inicio_atendimento` vazia — o cliente abriu o chamado, ficou na espera, mas nunca chegou a ser
> atendido. "Taxa de resposta" aqui é a mesma definição da seção de pesquisa, só recortada por
> abandonado sim/não.

## Cruzamento custo x satisfação

| Canal | Custo médio | Nota média |
|---|---|---|
| Atendimento especializado | R$ 48,68 | 2,86 |
| Atendimento inicial | R$ 13,60 | 3,70 |
| URA | R$ 1,84 | 4,32 |
| Chatbot | R$ 0,57 | 4,40 |

O canal mais caro é o de menor nota — custo alto não compra satisfação alta aqui.

> **Como foi calculado:** mesma base (`custo` e `nota`, já definidos acima), só colocando as duas médias
> lado a lado por canal, pra ver visualmente se gastar mais correlaciona com nota melhor (aqui, o
> contrário: é uma correlação negativa).

## Recomendação quantificada: reduzir o escalonamento para o nível 2

**Premissas:** `nivel_atendente` é proxy de "chamado escalado" (não há registro explícito disso no
dataset); a fração `p%` de chamados evitáveis é hipótese do grupo, não medida; ganho é bruto (não inclui
custo de treinamento/script).

40.859 chamados no nível 2 no período × R$ 14,31/chamado de diferença:

| Cenário | % evitável | Chamados evitáveis | Ganho estimado |
|---|---|---|---|
| Conservador | 5% | 2.043 | **R$ 29.231,23** |
| Base | 15% | 6.129 | **R$ 87.693,68** |
| Otimista | 25% | 10.215 | **R$ 146.156,13** |

> **Como foi calculado:** `chamados_nivel2` = contagem de chamados cujo `nivel_atendente` é `2`. A conta
> é: `ganho = chamados_nivel2 × p% × diferença_de_custo` (R$ 14,31, calculada na seção de custo por
> nível). `p%` é um número que **escolhemos** pra testar 3 cenários (5%, 15%, 25%) — não vem de nenhuma
> coluna do dataset, é a fração de chamados do nível 2 que o grupo acredita que poderia ter sido resolvida
> no nível 1 com script/treinamento. Por isso o resultado é uma **estimativa de sensibilidade**, não uma
> previsão: o número certo depende de validar essa premissa com quem conhece a operação.

## Leitura

O custo total tratado (~R$ 1,45 mi) é ~30× menor que o número do notebook inicial — era erro de limpeza,
não a realidade. O gasto cresce por **volume**, não por custo unitário, e é bastante concentrado em poucos
canais/motivos. O atendimento especializado é o canal mais caro **e** o de menor satisfação; abandono é
tanto um problema de custo invisível quanto de satisfação (nota 1,14 entre quem desistiu e respondeu); e
a queda do CSAT geral não parece ter causa externa — está concentrada nos canais humanos. A recomendação
de reduzir escalonamento para o nível 2 já tem ganho estimado em 3 cenários, mas depende de uma premissa
(`p%`) que o grupo precisa validar.

## Pontos a validar com o grupo

- Custo ≤ 0 (544 lançamentos): incluir ou excluir da soma — as duas versões já calculadas acima.
- Critério de dedup da pesquisa (prioriza nota válida quando há duplicata).
- `nivel_atendente` como proxy de escalonamento e a premissa `p%` da recomendação.
- Mês de referência: custo/CSAT mensal usam o mês de finalização — chamados abandonados (sem
  finalização) não entram nessas visões mensais específicas.
