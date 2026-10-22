# Oportunidades e aprendizados

Entregável analítico (Comitê Executivo): *discussão de oportunidades e aprendizados, priorizando clareza, aplicabilidade e
impacto*. As propostas priorizadas e quantificadas estão em [`propostas-e-priorizacao.md`](propostas-e-priorizacao.md);
aqui ficam as oportunidades adicionais, o que aprendemos e o que ainda não sabemos.

## Aprendizados (o que os dados ensinaram)

1. **A piora é estrutural, não conjuntural.** CSAT, abandono, resolução e espera pioram **todos os meses** desde jan/25, sem nenhuma inversão. Isso contradiz a hipótese de causa externa e recente.
2. **O problema é a espera, não a duração do atendimento.** TMA +8%, TME ×4,1. A operação trabalha no mesmo ritmo, mas **tem a mesma equipe para o dobro da demanda**.
3. **Custo cresce com volume, não com preço unitário.** Custo por chamado fixo em ~R$ 11; custo mensal +129%. Cortar custo sem reduzir volume humano não é viável.
4. **O custo está concentrado:** 2 níveis humanos = 93,7% do custo; 5 motivos = 60%.
5. **O autosserviço é bom no simples, ruim no crítico**, e o chatbot, ao contrário do que se acreditava, resolve menos da metade (49%).
6. **Idade e região explicam pouco** do comportamento (efeito de ~5 p.p. na resolução do autosserviço entre os mais jovens e os mais velhos; região, nenhum). A explicação está no **processo**, não no perfil do cliente.
7. **Os indicadores que a empresa acompanha são frágeis em três pontos** (CSAT, atendente, abandono) e, sem o tratamento, enganariam: custo 29× maior, TME negativo.

## Oportunidades além das propostas

| Oportunidade | Evidência | Por que ainda não é uma proposta |
|---|---|---|
| **Etapa de Prevenção**: o funil desejado do case é dominado por prevenção (site e app), mas não há nenhum dado dela | Só 4 canais de atendimento existem na base | Sem dado de uso do site/app, não dá para dimensionar; incluir **telemetria de jornada** como primeiro passo |
| **Alertas proativos** para motivos previsíveis (fatura, vencimento, bloqueio) | Consulta de fatura é o 1º motivo (12,7%); cadastro/vencimento são previsíveis | Depende de integração com sistemas de cobrança/cartão que não conhecemos |
| **Roteamento inteligente de motivos críticos** direto ao Nível 2 | Compra não autorizada, renegociação e cancelamento têm resolução de 11% a 15% no autosserviço e 58% a 59% chegam ao humano | Reduz passagens, mas pede análise de custo e de capacidade do Nível 2 |
| **Retorno de chamada** em vez de espera na linha | Abandono de 9,7% (Nível 2); CSAT cai a 10% com espera de 15 a 30 min | Depende da plataforma de telefonia |
| **Mentoria entre pares no Nível 2** | Dispersão de 47,7% a 62,3% em resolução e de 14 a 24 min em TMA entre atendentes sem inconsistência de vínculo | Amostra pequena (6 atendentes); validar com observação direta |
| **Mudança de mix de canais para quem tem baixa resolução** (ex.: mais velhos no autosserviço) | Resolução no autosserviço: 43,9% (65+) contra 49,1% (25-34) | Efeito modesto; não justifica desenho separado por idade agora |

## Limitações do estudo (o que não sabemos)

- **Sem dados de receita**: a fala do Gerente Financeiro ("o crescimento não acompanha a receita") não pôde ser testada.
- **Sem escala, jornada nem absenteísmo**: a análise de capacidade usa o cadastro de atendentes (admissão/desligamento) e premissa de jornada de ~160 h/mês.
- **Sem telemetria de URA, site e app**: as queixas de navegação difícil e lentidão são consistentes com os motivos (aplicativo = 2º motivo), mas não medidas.
- **Correlação, não causalidade**: espera, etapa, reincidência e resolução andam juntas; o efeito de cada uma no CSAT não foi isolado.
- **Premissas de 20% e 30%** (cenários A e B) são hipóteses de negócio, não dados.
- **Custos de implantação** das propostas não estão nas economias.
- **Pesquisa respondida por 61% dos chamados** (48% no último mês): o CSAT pode estar superestimado.
- **Atendentes**: a atribuição chamado → atendente é frágil em 12% dos chamados e nos de autosserviço.

## Aprendizados do processo (como trabalhamos)

| Aprendizado | Efeito |
|---|---|
| **Corrigimos o notebook exploratório inicial** em vez de confiar nele: a limpeza de custo inflou o total em 29× | Os números que apresentamos são reproduzíveis e passam por regras escritas e testadas |
| **Tratamento visível**: toda anomalia é uma flag (`dq_*`) e o impacto de cada decisão é medido (`impacto_indicadores`) | O Comitê vê quanto cada escolha muda o KPI |
| **Medalhão com notebooks únicos e PR revisado** (sem cópia por pessoa) | Menos conflito de merge, números que batem entre as análises |
| **Privacidade por desenho**: CPF só como chave interna e nunca exibido; hash na gold | Uma saída de célula com CPF foi detectada e corrigida durante a revisão |
| **Documentar decisões** (hash sem HMAC; nome do atendente; `status_atendente`) | Divergências entre diagrama, guia e código foram achadas em revisão e resolvidas |

## Próximos passos

1. Fechar o painel com as sete páginas e anexar prints à entrega.
2. Decidir com o grupo se o nome do atendente aparece no material do Comitê.
3. Desenhar o piloto de P1 (motivos, duração, métrica de sucesso, grupo de controle).
4. Levantar os dados que faltam: escala e jornada, telemetria de app e URA, receita.
