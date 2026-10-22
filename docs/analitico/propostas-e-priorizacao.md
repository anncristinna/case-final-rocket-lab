# Propostas de solução, priorização e ganho esperado

Entregável analítico (Comitê Executivo): *propostas priorizadas, com critério explícito, evidência nos dados e ganho
esperado; pelo menos duas com ganho quantificado e premissas de cálculo explícitas*. Todos os números têm origem em
[`../../resultados/`](../../resultados/).

## O diagnóstico em três linhas

1. **A demanda mais que dobrou (+120% em 18 meses) sem capacidade correspondente**: o cadastro não mostra aumento da equipe (5 saídas e 5 entradas, 25 atendentes cadastrados), e a **espera** do Nível 2 foi de 5 para 22 min. O CSAT passou de 86% para 57% e o abandono, de 1,4% para 3,8%.
2. **O custo está no atendimento humano** (93,65% do custo em 43% dos chamados) **e em poucos motivos** (5 motivos = 43% dos chamados e 60% do custo), que têm baixa resolução (31% a 38%) e alta reincidência (53% a 58%).
3. **O autosserviço funciona onde o problema é simples** (cadastral, fatura, limite) **e falha onde é crítico** (renegociação, compra não autorizada, cancelamento); parte dos casos simples ainda chega ao humano (12.411 chamados).

## Critério de priorização

Cada proposta recebe nota de 1 a 5 em quatro critérios, com pesos:

| Critério | Peso | O que mede |
|---|---|---|
| **Impacto financeiro** | 35% | Economia anual estimada (ou custo adicional). Resposta direta à preocupação do Gerente Financeiro |
| **Impacto no cliente** | 25% | Efeito esperado em CSAT, espera e abandono (Customer Success e Marketing) |
| **Facilidade de execução** | 25% | 5 = ação de processo/configuração em semanas; 1 = projeto com investimento e prazo longos |
| **Solidez da evidência** | 15% | 5 = efeito medido diretamente nos dados; 1 = depende de hipótese sem dado |

Nota final = soma ponderada. Os pesos e as notas são **estimativa do Claude Code** a partir dos números, **a validar pelo grupo** antes da
apresentação. A **sequência de execução** não é só a ordem de nota: habilitadores baratos entram primeiro.

| # | Proposta | Fin. (35%) | Cliente (25%) | Facilidade (25%) | Evidência (15%) | **Nota** |
|---|---|---|---|---|---|---|
| P1 | Resolver na primeira interação os 5 motivos críticos (reduzir reincidência) | 5 | 4 | 3 | 4 | **4,10** |
| P2 | Deflexão dos motivos simples para o autosserviço | 2 | 3 | 4 | 4 | **3,05** |
| P3 | Dimensionar capacidade e escala (espera ≤ 5 min), começando pelo Nível 2 | 2 | 5 | 2 | 3 | **2,90** |
| P4 | Governança de dados: pesquisa, atendente, abandono | 1 | 2 | 4 | 5 | **2,60** |

## De quem é cada número

| Item | Origem | Status |
|---|---|---|
| 20% de deflexão (A) e 30% de redução de reincidência (B) | **Grupo** (`PCT_DEFLEXAO` e `PCT_REDUCAO_REINCIDENCIA` no `Silver_To_Gold`) | Hipóteses de negócio; validar em piloto |
| Custo de referência de R$ 1,4 mi | Entrevista com o Gerente Financeiro (case, p. 5) | Dado do case |
| Pesos e notas de priorização | Claude Code | A validar pelo grupo |
| Jornada de ~160 h/mês e ocupação do Nível 1 e 2 | Claude Code | Premissa, a validar |
| Contagem de atendentes vigentes (13 e 7) | Claude Code, a partir do cadastro | Frágil (12% dos chamados fora do vínculo) |
| Teto de CSAT (~82,2%) | Claude Code | Estimativa, a validar |
| Líquido P1 + P2 (R$ 258 a 279 mil/ano) | Claude Code | A confirmar com query |
| Metas dos KPIs | Claude Code | A validar pelo grupo e pelo Comitê |

## P1 — Resolver na primeira interação os cinco motivos críticos (**ganho quantificado**)

**Problema**: Problema com aplicativo, Compra não autorizada, Renegociação de dívida, Contestação de fatura e Cancelamento de conta são 43,0% dos chamados e 60,0% do custo, com resolução de 31% a 38% e
reincidência em 7 dias de 53% a 58%. O cliente que volta tem CSAT de 53% (contra 85% no primeiro contato).

**Ações**:
- Roteiro de diagnóstico e solução por motivo, com alçada para o Nível 1 resolver sem escalar (hoje ~20% desses chamados chegam ao Nível 2).
- Replicar as práticas dos atendentes de melhor resolução do Nível 2 (ex.: o atendente 14 resolve 8,7 p.p. acima da média do nível); mentoria e observação de atendimentos.
- Pós-atendimento ativo (confirmar a resolução) para não resolvidos.
- Revisar o fluxo dos casos que o autosserviço quase nunca resolve (11% a 26% de resolução) para encaminhar direto ao nível certo.

**Ganho esperado** (cenário B de [`../../resultados/07-custos-e-simulacao.md`](../../resultados/07-custos-e-simulacao.md)):

| | |
|---|---|
| Base | 55.999 chamados reincidentes no período (14 motivos) |
| **Premissa** | **30% dos recontatos deixam de ocorrer** |
| Ganho unitário | Custo médio do chamado reincidente do motivo (R$ 20,31 a R$ 27,41) |
| Chamados evitados | 16.800 no período |
| **Economia** | **R$ 408,6 mil no período (19 meses), R$ 21,5 mil/mês, R$ 258,1 mil/ano** |
| Sensibilidade | 10% → R$ 86,0 mil/ano; 20% → R$ 172,0 mil/ano |

**Efeitos não monetizados**: menos demanda no Nível 2 (libera capacidade), menos espera e mais CSAT.
**Risco**: a premissa de 30% é hipótese; testar em piloto com 1 ou 2 motivos (ex.: Compra não autorizada e Renegociação, maiores economias) por 60 dias.

## P2 — Deflexão dos motivos simples para o autosserviço (**ganho quantificado**)

**Problema**: consulta de fatura, consulta de limite, dúvidas sobre programa de pontos e alteração de dados cadastrais já
resolvem 49% a 77% no autosserviço, mas ainda geram **12.411 chamados no atendimento humano** (custo de ~R$ 19 a R$ 21 acima do autosserviço por chamado).

**Ações**: tornar essas quatro jornadas completas e visíveis no app, no site e na URA (o motivo "Problema com aplicativo" é o 2º em volume, e as queixas de app lento e URA confusa já foram relatadas pelos atendentes); remover da
árvore da URA o desvio para humano quando o autosserviço resolve.

**Ganho esperado** (cenário A):

| | |
|---|---|
| Base | 12.411 chamados de baixa criticidade que chegaram ao humano |
| **Premissa** | **20% passam a se resolver no autosserviço** |
| Ganho unitário | Custo médio humano do motivo menos o custo médio do autosserviço do motivo (R$ 19,22 a R$ 21,18) |
| Chamados evitados | 2.482 no período |
| **Economia** | **R$ 48,9 mil no período, R$ 2,6 mil/mês, R$ 30,9 mil/ano** |
| Sensibilidade | 10% → R$ 15,4 mil/ano; 30% → R$ 46,3 mil/ano |

**Leitura honesta**: o ganho financeiro direto é **pequeno**, porque os motivos simples já são baratos. O valor de P2 é
**tirar volume do Nível 1** e melhorar a experiência (CSAT de 74% a 85% nesses motivos), não cortar custo.
**Custo de implantação não está incluído** e pode consumir boa parte da economia.

**P1 + P2: não somar.** 98,1% da base de P2 (12.172 de 12.411 chamados) já é reincidente e, portanto, já está na base de P1: os dois atacam o mesmo problema (recontato por falha de resolução). Líquido da sobreposição: **R$ 258 a 279 mil/ano**, estimativa do Claude Code **a confirmar** com a query de [`07-custos-e-simulacao.md`](../../resultados/07-custos-e-simulacao.md). Os R$ 288,9 mil (soma simples) são só um teto.

## P3 — Capacidade e escala: espera até 5 minutos (**ganho qualitativo com teto estimado**)

**Problema**: o cadastro não mostra aumento da equipe (entradas e saídas se compensam; 25 atendentes cadastrados), mas o volume humano
cresceu ×2,4 e ×2,5. A contagem de vigentes por mês (13 no Nível 1 e 7 no Nível 2) é **inferida** das datas de admissão e desligamento, que conflitam com 12% dos chamados; trate-a como estimativa frágil. O TME do Nível 2 foi de 5,0 para 21,8 min, o abandono do Nível 2, de 4,3% para 15,2%, e seu CSAT, de 64% para 12%. Dois terços do volume estão entre 9h e 17h59 e segunda-feira concentra 20%.

**Evidência de valor**: com espera até 5 min o CSAT é 83%; de 5 a 15 min, 49%; de 15 a 30 min, 10%.

**Estimativa (teto)** — premissas: (i) o CSAT de quem espera mais de 5 min passa a ser o de quem espera até 5 min (83,0%); (ii) nada mais muda.
Com isso, o CSAT geral iria de **71,6% para ~82,2%** (+10,7 p.p.); se apenas a faixa de 5 a 15 min migrasse, para ~78,1%. Como espera e etapa são correlatas, isso é um **teto
teórico**, não uma previsão. Os 3.414 chamados abandonados (2,6%) deixariam de ser perdidos.

**Ações**: escala por dia e hora com reforço em segunda-feira e no intervalo 9h-17h; priorizar o Nível 2 (maior espera, maior custo por chamado, menor CSAT); revisar roteamento Nível 1 → Nível 2; mecanismo de retorno de chamada para
não deixar o cliente esperando na linha; meta operacional de TME ≤ 5 min.
**Custo**: depende de contratação ou realocação (não estimado: não há dados de salário/escala). P1 e P2 reduzem o volume humano e **diminuem a necessidade de contratar**; por isso vêm antes.

## P4 — Governança de dados: pesquisa, atendente e abandono (habilitador)

**Problema**: o CSAT (indicador que mais pesa para Marketing e Customer Success) tem 39% dos chamados sem pesquisa e cobertura caindo (65% → 48%); a análise por atendente é inválida em 12% dos chamados (fora do vínculo) e em 56,6% dos de autosserviço (atendente informado); o abandono é inferido.
Detalhes e 7 ações em [`confiabilidade-dos-dados.md`](confiabilidade-dos-dados.md).

**Ganho**: qualitativo. Sem ele, **não dá para medir o resultado de P1 a P3**, e o CSAT atual pode **estar superestimado** (quem tem pior experiência tende a responder menos).
Esforço baixo (validações na captura e no cadastro): vale começar já.

## Sequência sugerida

| Horizonte | O quê |
|---|---|
| **Agora (até 30 dias)** | P4 (validação de escala da pesquisa, vínculo de atendente, motivo de encerramento); definir a linha de base dos KPIs no painel; reforço de escala em segunda-feira e 9h-17h (quick win de P3) |
| **30 a 90 dias** | Piloto de P1 em 2 motivos; início de P2 nas jornadas de fatura, limite, cadastro e pontos |
| **90 dias em diante** | Expandir P1 aos 5 motivos; dimensionar capacidade do Nível 2 com os dados de escala (P3); revisitar premissas de 20% e 30% com os resultados dos pilotos |

## Indicadores de acompanhamento (painel)

| KPI | Hoje (jul/26) | Meta sugerida (a validar) |
|---|---|---|
| TME Nível 2 | 21,8 min | ≤ 5 min |
| CSAT geral | 56,7% | Voltar a ≥ 75% |
| Reincidência 7d nos 5 motivos críticos | 53% a 58% | −30% (premissa de P1) |
| Chamados de baixa criticidade no humano | 12.411 no período | −20% (premissa de P2) |
| Cobertura da pesquisa | 48,4% | ≥ 65% (nível de jan/25) |
| Abandono | 3,8% | ≤ 1,4% (nível de jan/25) |

As metas são **sugestões do Claude Code**, ancoradas nos níveis de jan/25 e nas premissas das simulações; **a validar pelo grupo** e alinhar com o Comitê.
