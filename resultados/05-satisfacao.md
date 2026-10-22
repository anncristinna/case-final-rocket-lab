# 05 — Satisfação (CSAT) e demanda

Fonte: `satisfacao_drivers_gold` (CSAT por dimensão, 73.383 respostas válidas de 1 a 5), `demanda_dia_hora_gold`
(168 linhas = 7 dias × 24 horas) e `kpi_mensal_gold`.

## O que move o CSAT

| Dimensão | Valor | Respostas | CSAT | Nota média |
|---|---|---|---|---|
| **Espera** | até 5 min | 54.444 | **83,02%** | 4,30 |
| | 5 a 15 min | 14.154 | **49,24%** | 3,43 |
| | 15 a 30 min | 3.372 | **10,29%** | 2,17 |
| | 30 a 60 min | 679 | 0,44% | 1,41 |
| | mais de 60 min | 30 | 0,00% | 1,37 |
| **Reincidência** | Primeiro contato | 42.913 | **84,74%** | 4,35 |
| | Reincidente (7d) | 30.470 | **53,02%** | 3,46 |
| **Resolução** | Resolvido | 37.366 | 84,19% | 4,36 |
| | Não resolvido | 34.883 | 57,99% | 3,57 |
| **Etapa** | Autosserviço | 42.481 | 85,14% | 4,36 |
| | Nível 1 | 21.865 | 60,70% | 3,70 |
| | Nível 2 | 9.037 | 34,12% | 2,86 |
| **Canal** | Chatbot / URA | 19.884 / 22.597 | 86,44% / 83,99% | 4,40 / 4,32 |
| | Atendimento Inicial / Especializado | 21.865 / 9.037 | 60,70% / 34,12% | 3,70 / 2,86 |
| **Categoria do motivo** | Cadastral | 2.637 | 84,68% | 4,39 |
| | Benefícios | 2.749 | 74,25% | 4,05 |
| | Cartão / Financeiro | 19.515 / 33.260 | 72,84% / 72,73% | 4,01 / 4,01 |
| | Outro | 7.444 | 68,16% | 3,86 |
| | Atendimento (app, site, URA) | 7.778 | 61,31% | 3,68 |
| **Faixa horária** | Madrugada / Manhã / Tarde / Noite | 2.183 / 23.082 / 32.243 / 15.875 | 72,5% / 71,8% / 71,5% / 71,4% | ~4,0 |

Leitura:

1. **A espera é o fator mais forte**: o CSAT cai de 83% (até 5 min) para 49% (5 a 15 min) e para 10% (15 a 30 min). Acima de 30 minutos praticamente não há cliente satisfeito.
2. **Reincidência**: o cliente que volta em até 7 dias tem 31,7 p.p. a menos de CSAT que o do primeiro contato (53,0% contra 84,7%).
3. **Resolução** pesa muito (84,2% contra 58,0%).
4. **A hora do dia não importa** (71% a 73% em todas as faixas): o problema é a espera, não o horário em si.
5. Mesmo com espera até 5 min, o CSAT é de 83%, e **o CSAT do autosserviço (85%) é maior que o do humano**: o cliente aceita bem o autosserviço quando ele resolve.

Cuidados na interpretação:

- Espera, etapa e reincidência estão correlacionadas (o Nível 2 tem a pior espera e a pior resolução). Os números acima **não separam o efeito** de cada fator; a causalidade pressuposta (esperar menos eleva o CSAT) é plausível, não demonstrada.
- **Cobertura da pesquisa**: 39,2% dos chamados não têm pesquisa e a cobertura caiu de 65,0% (jan/25) para 48,4% (jul/26). Se quem tem pior experiência (ex.: quem abandona) responde menos, o CSAT real da operação é provavelmente **mais baixo** do que o medido. O CSAT por si só é um indicador otimista aqui.

## Demanda por dia e hora

| Corte | Participação nos chamados |
|---|---|
| Segunda-feira | 19,7% (25.962) |
| Terça a sexta | 15,6% a 16,7% por dia (20.503 a 22.008) |
| Sábado / Domingo | 9,2% (12.185) / 6,5% (8.627) |
| Madrugada (0h-5h) / Manhã (6h-11h) / Tarde (12h-17h) / Noite (18h-23h) | 2,9% / 31,4% / 44,0% / 21,6% |
| Horas de maior volume | 10h (8,2%), 15h (8,1%) e 14h (8,0%) |

**Dois terços dos chamados (66,8%) ocorrem entre 9h e 17h59**, e segunda-feira concentra 1 em cada 5. Um
dimensionamento de escala por faixa horária e dia da semana tem aqui um alvo claro (os dados de escala atual não foram fornecidos).
Em horários de pouco volume (madrugada) a espera pode ser alta mesmo com poucos chamados: o p90 de espera
está em `demanda_dia_hora_gold` para conferir cada célula dia × hora.
