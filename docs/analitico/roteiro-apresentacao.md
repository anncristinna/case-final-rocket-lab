# Roteiro da apresentação executiva (sexta, 23/10 — 20 min + 15 min de perguntas)

Entregável analítico: *apresentação executiva com as principais conclusões obtidas a partir da análise dos dados tratados*.
Público: Gerente Financeiro, Coordenadora de Customer Success, Diretor de Tecnologia e Diretora de Marketing.
Cada bloco responde a uma dor que o próprio Comitê trouxe nas entrevistas. **O deck é montado a partir deste roteiro**; os números estão em
[`../../resultados/`](../../resultados/) e o painel, em [`../tecnico/painel-indicadores.md`](../tecnico/painel-indicadores.md).

## Linha do tempo (20 min)

| Min | Bloco | Mensagem | Fonte |
|---|---|---|---|
| 0-2 | **Abertura** | A V-Credit dobrou o volume de atendimentos em 18 meses e a operação não acompanhou: o que os dados mostram e o que fazer | `resultados/01` |
| 2-5 | **Confiança nos números** | Os dados exigem tratamento: sem ele, custo 29× maior e espera negativa. Três pontos frágeis (CSAT, atendente, abandono) | `confiabilidade-dos-dados.md` |
| 5-8 | **O que aconteceu** | CSAT 86% → 57%, abandono ×2,8, TME ×4,1, custo +129% e custo/chamado estável. Piora todo mês, não recente | `resultados/01` |
| 8-11 | **Onde dói** | Funil: 43% dos chamados no humano = 93,65% do custo; 5 motivos = 60% do custo; Nível 2: TME 22 min, CSAT 12% | `resultados/02`, `03` |
| 11-13 | **Por quê** | Equipe sem crescimento no cadastro (entradas e saídas se compensam) para demanda humana ×2,5; espera derruba o CSAT (83% → 49% → 10%); reincidência 53% a 58% nos motivos críticos | `resultados/04`, `05` |
| 13-14 | **O que não é a causa** | Região: nenhum efeito; idade: efeito pequeno | `resultados/06` |
| 14-18 | **Recomendações** | P1 (R$ 258 mil/ano), P2 (R$ 31 mil/ano; **não somar**, P2 está quase todo dentro de P1), P3 (espera ≤ 5 min; CSAT teto ~82%), P4 (governança) e o critério de priorização | `propostas-e-priorizacao.md` |
| 18-20 | **Próximos passos** | Sequência (agora / 30-90 dias / 90+), piloto de P1 e o que precisamos do Comitê | `oportunidades-e-aprendizados.md` |

## Resposta direta a cada executivo

| Quem | Dor | Resposta em uma frase |
|---|---|---|
| Gerente Financeiro | "Gasto de R$ 1,4 mi; precisamos cortar" | Confirmado (R$ 1,45 mi). O custo cresce com volume, não com preço; economia identificada: **R$ 258 a 279 mil/ano** (P1 + P2, líquido da sobreposição; estimativa derivada, com a sobreposição conferida em 22/10), com premissas explícitas |
| Coord. de Customer Success | "Resolução caiu, muitos desistem, falta priorização" | Resolução −6,7 p.p., abandono ×2,8 (Nível 2: 15%). **Priorizar o Nível 2 e os 5 motivos críticos** |
| Diretor de Tecnologia | "Chatbot resolve; dados inconsistentes; segurança" | O chatbot resolve 49%. Inconsistências quantificadas e tratadas; CPF nunca exposto e hash na gold; pipeline medalhão idempotente |
| Diretora de Marketing | "CSAT de 85% e piora recente, talvez externa" | 86% em jan/25, **56,7% em jul/26, queda contínua** e ligada à espera (não ao horário nem à região) |

## Perguntas prováveis (15 min)

| Pergunta | Onde está a resposta |
|---|---|
| De onde vêm os 20% e 30%? | São **hipóteses**, com sensibilidade em 10%/20%/30% (`07-custos-e-simulacao`); por isso propomos piloto |
| A economia inclui o custo de implantar? | Não; é um limite explícito (`07`). Para P2 o ganho direto é pequeno; o valor é CSAT e capacidade |
| Por que não só contratar? | O cadastro não mostra aumento da equipe, mas P1 e P2 reduzem a necessidade; contratação (P3) vem com dados de escala |
| Dá para confiar no CSAT? | Só com ressalva: 39% sem pesquisa e cobertura caindo; provável superestimativa (`confiabilidade`) |
| E o desempenho individual dos atendentes? | Indicativo apenas: 12% dos chamados estão fora do vínculo e o campo atendente vem preenchido em 99,4% dos chamados de autosserviço (`resultados/04`); pergunta em aberto à V-Credit |
| O que o `ID_Atendente` representa em chamados de URA e chatbot? | Ainda não sabemos: o campo vem preenchido em 99,4% desses chamados, onde não deveria haver atendente humano. É pergunta em aberto à V-Credit (`confiabilidade`, perguntas em aberto) |
| O pipeline reproduz o mesmo resultado? | Sim, idempotente; checksum por tabela no manifesto (`tecnico/notebooks-e-jobs.md`) |
| E a Prevenção (site e app)? | Não há dados dela; ficou como oportunidade com telemetria (`oportunidades`) |
| O que é o `SEM_CADASTRO`? | 1.330 chamados (1%) com cliente inexistente na base; ficam visíveis no painel em vez de sumir |

## Antes de apresentar (checklist)

- [x] Prova de idempotência feita e registrada em [`../tecnico/notebooks-e-jobs.md`](../tecnico/notebooks-e-jobs.md) (evidências em `../tecnico/evidencias/`).
- [ ] Não baixar o `pacote_powerbi.zip` entre 12:00 e 12:10 (nem entre 00:00 e 00:10), quando o Job regrava o pacote.
- [x] Nomes dos atendentes mantidos (base fictícia): `anonimizar_atendente` fica `false`, sem regerar o pacote.
- [ ] Anexar prints das 7 páginas do painel e do Job no Databricks.
- [ ] Conferir cada número do deck contra o arquivo de `resultados/` correspondente.
- [ ] Ensaiar em 18 min (deixar 2 min de folga).
