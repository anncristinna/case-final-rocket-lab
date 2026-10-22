# 04 — Atendentes e capacidade

Fonte: `atendentes_desempenho_gold` (25 atendentes) e `dim_atendente_gold`. Atendentes aparecem por `id_atendente` e
nível neste arquivo; no painel os nomes são mantidos, por decisão do grupo (base fictícia; ver
[`../docs/tecnico/arquitetura-medalhao.md`](../docs/tecnico/arquitetura-medalhao.md)).

> ⚠️ **Leia estes números como indicativos.** A atribuição chamado → atendente tem problemas de origem (detalhes em
> [`../docs/analitico/confiabilidade-dos-dados.md`](../docs/analitico/confiabilidade-dos-dados.md)): **56,6% dos chamados de autosserviço
> trazem um `id_atendente`** (URA/chatbot não deveriam ter) e **12,0% dos chamados (15.874) estão fora do período de vínculo
> do atendente** (aberto antes da admissão ou depois do desligamento). Por isso as médias por atendente misturam
> chamados de autosserviço (TMA de 2 a 4 min) com os humanos.

## Cadastro

| Nível | Cadastrados | Ativos (sem data de desligamento) | Chamados atribuídos | TMA (min) | Resolução | CSAT | Custo/chamado (R$) |
|---|---|---|---|---|---|---|---|
| Nível 1 | 17 | 13 | 90.215 | 8,47 | 49,5% | 74,5% | 6,69 |
| Nível 2 | 8 | 7 | 40.859 | 16,85 | 54,0% | 65,0% | 21,08 |

(Médias ponderadas pelo número de chamados. Total atribuído: 131.074; os 764 restantes têm `id_atendente` inválido na origem.)

## Capacidade instalada contra demanda (estimativa)

O cadastro permite **inferir** quantos atendentes estavam vigentes em cada mês (admitidos e ainda não desligados). **Atenção:** essas datas conflitam com 12% dos chamados (15.874 fora do vínculo; os atendentes 21 a 25, por exemplo, têm chamados desde jan/25, antes da admissão). A contagem de 13 e 7 e as horas por atendente abaixo são, portanto, **estimativas frágeis do Claude Code**. O que resiste é a conclusão de que o quadro **não cresceu**: entradas e saídas se compensam e o total cadastrado é 25 de qualquer forma.

| | Jan/2025 | Jul/2026 | Variação |
|---|---|---|---|
| Atendentes de Nível 1 vigentes | 13 | 13 | 0 |
| Atendentes de Nível 2 vigentes | 7 | 7 | 0 |
| Chamados no Nível 1 | 1.236 | 2.988 | ×2,4 |
| Chamados no Nível 2 | 532 | 1.308 | ×2,5 |
| Chamados por atendente de N1 | 95 | 230 | ×2,4 |
| Chamados por atendente de N2 | 76 | 187 | ×2,5 |
| Horas de atendimento por atendente de N2 no mês (chamados × TMA ÷ atendentes) | 47 h | 120 h | ×2,5 |
| Horas de atendimento por atendente de N1 no mês | 24 h | 64 h | ×2,7 |

Admissões e desligamentos se compensaram (5 saídas e 5 entradas no período; entre as saídas, 4 de N1 e 1 de N2): **o cadastro não mostra
aumento da equipe enquanto a demanda humana mais que dobrou**. Contra uma jornada de referência de ~160 h/mês (premissa do Claude Code, não vem dos dados; a validar), o
Nível 2 passa de ~29% para ~75% do tempo só em atendimento, sem contar espera entre chamados, pausas e pico de demanda
(horários de pico em [`05-satisfacao.md`](05-satisfacao.md)). Isso é coerente com o TME do Nível 2 ter ido de 5,0 para 21,8 min.

Limites desta estimativa: os dados não trazem escala, jornada, absenteísmo nem fila por horário. Para o Nível 1 (~40% de ocupação estimada) a
capacidade média **não explica sozinha** a espera de 10 min; picos, escala por faixa horária e distribuição de chamados provavelmente pesam.
A recomendação inclui obter esses dados antes de dimensionar contratação.

## Atendentes sem inconsistência de vigência (15 dos 25)

Dispersão que não depende do problema de atribuição acima (atendentes 4 e 6 a 19, ativos e sem nenhum chamado fora de vigência):

| Nível | `id_atendente` | Chamados | TMA (min) | Resolução | CSAT | Custo/chamado (R$) | Rank de resolução no nível |
|---|---|---|---|---|---|---|---|
| 1 | 4 | 5.993 | 9,47 | 52,10% | 78,82% | 7,58 | 2 |
| 1 | 6 | 6.013 | 10,80 | 49,21% | 73,62% | 8,30 | 8 |
| 1 | 7 | 5.954 | 7,93 | 52,09% | 76,87% | 6,78 | 3 |
| 1 | 8 | 5.988 | 7,00 | 51,55% | 75,54% | 6,42 | 5 |
| 1 | 9 | 5.902 | 8,16 | 53,07% | 75,92% | 6,95 | 1 |
| 1 | 10 | 5.832 | 8,41 | 51,72% | 70,45% | 7,01 | 4 |
| 1 | 11 | 5.980 | 8,75 | 50,74% | 72,97% | 7,19 | 6 |
| 1 | 12 | 6.060 | 10,55 | 46,51% | 73,76% | 8,05 | 15 |
| 1 | 13 | 6.046 | 9,26 | 47,50% | 74,38% | 7,41 | 13 |
| 2 | 14 | 5.459 | 15,01 | 62,32% | 66,18% | 20,31 | 1 |
| 2 | 15 | 5.387 | 21,05 | 50,89% | 56,32% | 25,45 | 6 |
| 2 | 16 | 5.489 | 14,10 | 53,64% | 67,61% | 19,49 | 4 |
| 2 | 17 | 5.431 | 15,51 | 58,76% | 69,64% | 20,56 | 2 |
| 2 | 18 | 5.412 | 14,69 | 56,29% | 69,43% | 19,73 | 3 |
| 2 | 19 | 5.338 | 23,99 | 47,66% | 57,03% | 27,47 | 7 |

Leitura:

- **No Nível 2 há dispersão grande**: resolução de 47,7% (atendente 19) a 62,3% (atendente 14), TMA de 14 a 24 min e CSAT de 56% a 70%. Os dois atendentes mais lentos (15 e 19) também estão entre os piores em resolução e têm os dois menores CSAT: **mais tempo não significa melhor resolução**.
- O atendente 14 resolve 8,7 p.p. acima da média do nível e é um ponto de partida para capturar práticas (scripts, roteiro de diagnóstico) e usar em mentoria. Isso é uma hipótese a validar com observação de atendimentos, não uma conclusão causal.
- Seguir o ranking de poucos atendentes pede cautela: com 25 pessoas e diferenças de 1 a 3 p.p. em resolução no Nível 1, muitas posições são empate prático.
