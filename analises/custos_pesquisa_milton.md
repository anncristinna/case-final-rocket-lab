# Custos e pesquisa de satisfação — Milton

Leitura dos resultados de `custos_pesquisa_milton.py`, rodado localmente (PySpark 4.2) sobre os 8 CSVs
completos em `data/raw/`. Todos os números batem com os de referência já registrados em
`achados_qualidade_dados.md` e `achados_hipoteses.md` — **reconfirmar no Databricks** antes de usar em slides.
Nenhum dado pessoal (CPF/nome/e-mail) aparece neste documento.

## 1. Custos

### 1.1 Limpeza
Custos têm 8 formatos de texto (`9,99` · `99,99` · `R$ 9,99` · `9.99reais` · negativos etc.). A regra —
manter só dígitos/`,`/`.`/`-`, tratar vírgula como decimal brasileiro removendo pontos de milhar antes —
resolve todos sem distorcer o valor. O notebook inicial, ao remover todo ponto, inflou o custo total para
R$ 42,2 mi; o valor correto é **R$ 1,45 mi**.

Depois de remover 781 linhas duplicadas por `id_custo`: **130.288 custos únicos**.

### 1.2 Total e a decisão pendente sobre custo ≤ 0
544 lançamentos são ≤ 0 (271 negativos + 273 zero). As duas versões do total:

| Cenário | Custo total |
|---|---|
| Incluindo custo ≤ 0 (mantido com flag) | **R$ 1.447.671,52** |
| Excluindo custo ≤ 0 (tratado como estorno/erro) | R$ 1.450.617,85 |

Diferença: R$ 2.946,33 (~0,2% do total) — **decisão do grupo**, não decidimos por conta própria.

Quantis de custo por lançamento (10/25/50/75/90/99%): R$ 0,48 · 0,84 · 2,13 · 13,27 · 31,59 · 169,42.
**1.550 chamados** não têm nenhum lançamento de custo.

### 1.3 Custo mensal x volume de chamados
Separando o efeito "mais chamados" do efeito "cada chamado ficou mais caro":

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

O custo médio por chamado é **estável** (~R$ 11) do início ao fim; o gasto total mais que dobrou porque o
**volume** mais que dobrou (4.368 → 9.599 chamados/mês).

### 1.4 Custo por canal, motivo, categoria e nível

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
| (sem atendente válido) | R$ 11,23 | 764 |

Diferença nível 2 − nível 1: **R$ 14,31/chamado** (nível 2 custa ~3,2× o nível 1).

| Categoria do motivo | Custo médio | Chamados |
|---|---|---|
| Atendimento | R$ 14,68 | 14.333 |
| (sem categoria — a confirmar) | R$ 12,61 | 13.282 |
| Cartão | R$ 10,87 | 34.929 |
| Financeiro | R$ 10,57 | 59.646 |
| Benefícios | R$ 9,66 | 4.979 |
| Cadastral | R$ 6,11 | 4.669 |

Motivo mais caro em média: "Renegociação de dívida" (R$ 16,64); mais barato: "Alteração de dados
cadastrais" (R$ 6,11). Lista completa no notebook.

### 1.5 Pareto: onde o gasto se concentra

| Canal | % acumulado do custo | % dos chamados |
|---|---|---|
| Atendimento especializado | 56,8% | 13,0% |
| + Atendimento inicial | 93,7% | 43,1% |
| + URA | 98,6% | 73,1% |
| + Chatbot | 100% | 100% |

Por motivo, os 4 primeiros ("Problema com aplicativo", "Compra não autorizada", "Renegociação de dívida",
"Contestação de fatura") já respondem por **53,6%** do custo total — lista completa de 14 motivos no notebook.

### 1.6 Maiores outliers
Os 20 maiores lançamentos individuais variam de R$ 149,56 a R$ 169,42 — nenhum parece erro de digitação
isolado (não há valores absurdamente fora da curva); ver lista completa no notebook se precisar auditar
`id_custo`/`id_chamado` específicos.

**O que isso mostra:** o custo total tratado (~R$ 1,45 mi) é ~30× menor que o número do notebook inicial —
era erro de limpeza, não o cenário real. O gasto cresce por **volume**, não por custo unitário; é bastante
concentrado em poucos canais/motivos (Pareto); e o nível 2 custa, em média, ~3,2× o nível 1 — base da
recomendação quantificada na seção 4.

## 2. Pesquisa de satisfação

### 2.1 Limpeza
Nota válida: inteiro de 1 a 5. Das 81.021 linhas do arquivo, **6.899 têm nota inválida** (-1, 0, 6 ou vazio).

Ao deduplicar por `id_chamado` (802 chamados com mais de uma pesquisa), priorizamos a linha com **nota
válida** quando existe uma: descobrimos que só 751 desses 802 têm de fato a mesma nota válida repetida; os
outros ~51 têm as duas linhas inválidas, e um pequeno resto mistura uma válida com uma inválida. Por isso,
depois do dedup, restam **80.219 pesquisas únicas** e **6.836 notas inválidas** — número um pouco menor que
o 6.899 "brutos", porque o dedup recupera a nota válida de alguns chamados duplicados.

### 2.2 Distribuição das notas válidas

| Nota | Respostas |
|---|---|
| 1 | 2.742 |
| 2 | 4.772 |
| 3 | 13.347 |
| 4 | 23.090 |
| 5 | 29.432 |

### 2.3 Taxa de resposta — geral, por mês e por canal
Taxa de resposta geral: **55,7%** dos chamados únicos.

| Mês | Taxa de resposta | Mês | Taxa de resposta |
|---|---|---|---|
| 2025-01 | 65,0% | 2025-10 | 57,5% |
| 2025-02 | 65,7% | 2025-11 | 55,8% |
| 2025-03 | 63,0% | 2025-12 | 54,6% |
| 2025-04 | 61,1% | 2026-01 | 54,2% |
| 2025-05 | 62,3% | 2026-02 | 53,6% |
| 2025-06 | 60,9% | 2026-03 | 51,6% |
| 2025-07 | 60,7% | 2026-04 | 50,7% |
| 2025-08 | 57,5% | 2026-05 | 49,7% |
| 2025-09 | 57,7% | 2026-06 | 49,9% |
| | | 2026-07 | 48,4% |

| Canal | Taxa de resposta |
|---|---|
| URA | 57,2% |
| Chatbot | 56,0% |
| Atendimento inicial | 55,1% |
| Atendimento especializado | 52,9% |

**Risco de viés:** a taxa de resposta cai de 65% para 48% ao longo do período — quem responde hoje pode não
ser mais representativo de quem respondia no início. A diferença entre canais é pequena (52,9% a 57,2%), então
comparar CSAT entre canais é razoavelmente justo; comparar CSAT entre o início e o fim do período já não é
tão simples, porque a própria base de quem responde mudou.

### 2.4 CSAT mensal (% de notas 4 e 5 entre as válidas)

| Mês | CSAT | Mês | CSAT |
|---|---|---|---|
| 2025-01 | **86,2%** | 2025-10 | 73,9% |
| 2025-02 | 86,2% | 2025-11 | 71,9% |
| 2025-03 | 84,1% | 2025-12 | 70,4% |
| 2025-04 | 82,3% | 2026-01 | 67,2% |
| 2025-05 | 82,4% | 2026-02 | 67,0% |
| 2025-06 | 79,5% | 2026-03 | 63,6% |
| 2025-07 | 78,7% | 2026-04 | 63,7% |
| 2025-08 | 77,0% | 2026-05 | 60,0% |
| 2025-09 | 74,1% | 2026-06 | 59,0% |
| | | 2026-07 | **56,7%** |

### 2.5 CSAT por canal, nível, motivo, categoria e resolução

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

Por categoria do motivo: Cadastral (84,7%) e Benefícios (74,2%) no topo; Atendimento (61,3%) no fim —
lista completa de motivos e categorias no notebook.

### 2.6 Nota x tempo de espera, x TMA e x abandono

| Faixa de espera (TME) | CSAT | Respostas |
|---|---|---|
| 0-1 min | 85,1% | 43.176 |
| 1-5 min | 75,1% | 11.180 |
| 5-15 min | 49,2% | 14.132 |
| 15+ min | **8,6%** | 4.077 |

| Faixa de atendimento (TMA) | CSAT | Respostas |
|---|---|---|
| 0-2 min | 85,4% | 17.471 |
| 2-5 min | 83,7% | 22.030 |
| 5-15 min | 68,5% | 15.616 |
| 15+ min | 48,2% | 17.562 |

| Abandonado | Chamados | Respostas | Taxa de resposta | Nota média |
|---|---|---|---|---|
| Não | 128.424 | 72.679 | 56,6% | 4,00 |
| Sim | 3.414 | 704 | 20,6% | **1,14** |

Abandono reduz muito a chance de resposta (20,6% vs. 56,6%), mas quando o cliente que desistiu responde, a
nota é péssima — sinal forte de insatisfação, mesmo com poucas respostas.

### 2.7 Testando a fala do Marketing: "CSAT era 85% em jan/25; a piora é externa"

| Canal | CSAT jan/2025 | CSAT jul/2026 | Queda |
|---|---|---|---|
| Atendimento especializado | 63,7% | 11,5% | **−52,1 p.p.** |
| Atendimento inicial | 83,4% | 38,4% | **−45,0 p.p.** |
| URA | 91,8% | 72,6% | −19,2 p.p. |
| Chatbot | 92,3% | 78,9% | −13,3 p.p. |

A queda **não é uniforme**: é 3-4× maior nos canais humanos que no autosserviço. Uma causa externa e geral
afetaria todos os canais de forma parecida — a concentração em atendimento humano aponta para um problema
operacional interno (capacidade, treinamento, fila), não uma causa externa.

**O que isso mostra:** a taxa de resposta cai com o tempo (risco de viés); abandono é tanto um problema de
custo quanto de satisfação; espera e atendimento longos pioram a nota de forma clara; e a fala do Marketing
de que a piora é externa **não se sustenta** — a queda está concentrada nos canais humanos.

## 3. Cruzamento custo x satisfação

| Nota | Custo médio |
|---|---|
| 1 | R$ 37,08 |
| 2 | R$ 28,27 |
| 3 | R$ 15,56 |
| 4 | R$ 9,24 |
| 5 | R$ 5,47 |

| Canal | Custo médio | Nota média |
|---|---|---|
| Atendimento especializado | R$ 48,68 | 2,86 |
| Atendimento inicial | R$ 13,60 | 3,70 |
| URA | R$ 1,84 | 4,32 |
| Chatbot | R$ 0,57 | 4,40 |

O atendimento especializado é o canal mais caro **e** o de menor nota — custo alto não compra satisfação
alta aqui. Investir em evitar a chegada até ele (prevenção/nível 1) tende a ganhar nos dois eixos.

## 4. Recomendação quantificada: reduzir o escalonamento para o nível 2

**Ideia:** treinar/equipar o nível 1 para resolver uma fração dos motivos que hoje terminam no nível 2,
evitando a diferença de custo entre os níveis.

**Premissas:**
1. Medido nos dados: custo médio nível 1 = R$ 6,65; nível 2 = R$ 20,96; diferença R$ 14,31.
2. Limitação dos dados: `nivel_atendente` é o nível de quem atendeu, não um registro explícito de
   "escalou de 1 para 2" — é uma *proxy* do custo de um chamado escalado.
3. Premissa do grupo (não vem dos dados): uma fração `p%` dos chamados hoje resolvidos no nível 2 poderia
   ser resolvida no nível 1 com script/treinamento adicional.
4. Ganho é bruto — não inclui o custo do próprio treinamento/script.

**Conta:** chamados atendidos no nível 2 no período = 40.859. Ganho = chamados nível 2 × `p%` × R$ 14,31.

| Cenário | `p%` evitável | Chamados evitáveis | Ganho estimado |
|---|---|---|---|
| Conservador | 5% | 2.043 | **R$ 29.231,23** |
| Base | 15% | 6.129 | **R$ 87.693,68** |
| Otimista | 25% | 10.215 | **R$ 146.156,13** |

**O que isso mostra:** mesmo no cenário conservador, a economia é relevante frente ao custo total tratado
(~R$ 1,45 mi no período); o número exato depende da premissa `p%` (não medida) e do custo do próprio
treinamento — por isso a apresentação deve deixar claro que é uma estimativa de ganho bruto, sensível à
premissa, não uma previsão.

## 5. Pontos a validar com o grupo

- **Custo ≤ 0** (544 lançamentos, R$ 2.946,33 de diferença): incluir ou excluir da soma — decisão do grupo.
- **Dedup da pesquisa**: agora prioriza a nota válida quando o chamado tem mais de uma pesquisa; confirmar
  que o grupo concorda com o critério.
- **Custo de escalonamento**: usa o nível do atendente como proxy; a fração `p%` evitável é uma hipótese a
  validar com quem conhece a operação, não um número medido.
- **Mês de referência**: CSAT e custo mensal usam o mês de finalização (não de abertura); chamados
  abandonados (sem finalização) não entram nessas visões mensais específicas.
- Confirmar todos os números rodando este mesmo notebook no Databricks antes de usar em slides.
