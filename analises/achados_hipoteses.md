# Afirmações dos stakeholders e como testá-las

> Números medidos numa execução local sobre os CSVs completos; reconfirmar no Databricks antes de usar em slides.

O enunciado traz falas do Comitê. Os dados já permitem uma primeira leitura de várias delas.
**Resultados preliminares** (pipeline rodado localmente sobre os dados completos; correlação, não causalidade;
reconfirmar no Databricks antes de levar aos slides).

| Stakeholder | Afirmação | Leitura preliminar |
|---|---|---|
| Gerente Financeiro | Gasto passou de R$ 1,4 mi em 19 meses e cresce todo mês | **Confirmado**: R$ 1,448 mi em jan/25–jul/26. Custo mensal R$ 46 mil → R$ 106 mil. O **custo por chamado ficou estável** (R$ 10,67 → R$ 11,11); o que cresceu foi o **volume** (4.368 → 9.596 chamados/mês, +120%). |
| Coord. Customer Success | Tempo de espera/atendimento subiu e resolução caiu, principalmente no nível 2 | **Em grande parte confirmado**: TME médio 86 s → 339 s; resolução geral 54,4% → 47,7%; nível 2: 57,8% → 49,6%. O TMA humano mudou pouco (1.303 s → 1.368 s). |
| Coord. Customer Success | Muitos clientes desistem antes de serem atendidos | **Confirmado e agravado**: abandono 1,4% → 3,8% ao mês; 3.414 chamados no total, só nos canais humanos. Quem desiste quase não responde pesquisa (20,6% vs. 56,6% dos demais) e, quando responde, dá nota pior que qualquer motivo registrado (média 1,14 de 5) — poucas respostas, mas sinal forte de que abandono é também um problema de satisfação, não só de custo invisível. |
| Dir. Tecnologia | O chatbot funciona bem; o problema é o perfil do usuário | **A testar**: resolução do chatbot 49,0% vs URA 45,4% vs humano 52–64%. Falta cruzar com idade/faixa etária (cruzamento a confirmar no notebook de clientes). |
| Dir. Tecnologia | Há inconsistências entre registros, custos e notas | **Confirmado e quantificado**: ver `achados_qualidade_dados.md` (24 problemas; TMA humano subestimado 4,7×). |
| Dir. Marketing | Satisfação era 85% em jan/25; a piora é externa e "não deve ser muito diferente do ano passado" | **Início confirmado, resto refutado**: CSAT (notas 4–5) 86,2% em jan/25 → **56,7% em jul/26**, queda contínua de ~30 p.p. Taxa de resposta à pesquisa: 55,7% dos chamados. **A causa não parece externa/geral**: a queda por canal entre jan/25 e jul/26 é bem desigual — atendimento especializado 63,7%→11,5% (−52 p.p.) e atendimento inicial 83,4%→38,4% (−45 p.p.), contra chatbot 92,3%→78,9% (−13 p.p.) e URA 91,8%→72,6% (−19 p.p.). Uma causa externa afetaria todos os canais de forma parecida; a concentração nos canais **humanos** aponta para um problema operacional interno. |
| Atendentes | Alta demanda vem da lentidão do app/site | **A testar**: participação do motivo "Problema com aplicativo" e das consultas simples no volume. |
| Atendentes | URA tem caminhos confusos | **A testar**: resolução da URA é a menor (45,4%). Falta ver a taxa de escalonamento. |

### Fotografia por canal (período todo, preliminar)

| Canal | Chamados | Custo médio/chamado | Resolução | Abandono |
|---|---|---|---|---|
| URA | 39.533 | R$ 1,84 | 45,4% | — |
| Chatbot | 35.517 | R$ 0,57 | 49,0% | — |
| Atendimento inicial | 39.697 | R$ 13,60 | 52,5% | 4,4% |
| Atendimento especializado | 17.091 | R$ 48,68 | 63,7% | 9,7% |

Custo médio por chamado: nível 1 R$ 6,65; nível 2 R$ 20,96. Cada chamado que chega ao atendimento
especializado custa ~85× um de chatbot.

**Concentração do gasto (Pareto, preliminar):** o atendimento especializado concentra **56,8%** de todo o
custo com só **13%** dos chamados; junto com o atendimento inicial, os dois canais humanos somam **93,7%**
do gasto. Por motivo, os 4 primeiros ("Problema com aplicativo", "Compra não autorizada", "Renegociação de
dívida", "Contestação de fatura") já respondem por **53,6%** do custo total.

## Ideias de frentes de solução (priorizar depois com critério explícito)

Todas dependem de confirmação nos dados; as de ganho quantificável são as candidatas às duas propostas obrigatórias.

1. **Desviar motivos simples para prevenção/autosserviço** (consulta de fatura/limite, bloqueio/desbloqueio):
   ganho = chamados evitáveis × diferença de custo entre canal humano e autosserviço (cruzamento canal × motivo, a confirmar no notebook).
2. **Reduzir escalonamento para o nível 2** (script/treinamento no nível 1 nos motivos que mais escalam):
   ganho = chamados evitáveis × (R$ 20,96 − R$ 6,65) = **R$ 14,31/chamado** (nível 2 custa ~3,2× o nível 1).
   **Já quantificado em 3 cenários** (ver `custos_pesquisa_milton.py` seção f; base de 40.859 chamados no
   nível 2 no período): conservador (5% evitável) ≈ R$ 29,2 mil · base (15%) ≈ R$ 87,7 mil · otimista (25%)
   ≈ R$ 146,2 mil. Premissa explícita e não medida nos dados: a fração evitável (`p%`); `nivel_atendente`
   é uma *proxy* de escalonamento (não há no dataset um registro explícito de "escalou de 1 para 2").
3. **Reduzir abandono na fila** dos canais humanos: ganho = chamados recuperados × custo evitado de recontato + efeito no CSAT.
4. **Capacitação focada** nos atendentes/motivos com pior resolução (métrica por atendente, a confirmar no notebook).
5. **Governança de dados**: padronizar cadastro de canal/motivo/atendente, formatos de custo e tempo, controle de acesso
   (preocupação de segurança do Diretor de Tecnologia).

Critérios de priorização candidatos: impacto financeiro, impacto na satisfação, esforço/prazo, risco, dependência de TI.
