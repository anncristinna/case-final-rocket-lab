# Documentação por entregável

A documentação segue os dois entregáveis do enunciado (*Dinâmica de Solução de Case*, p. 8-10): o
**técnico**, direcionado ao Diretor de Tecnologia, e o **analítico e de negócio**, direcionado ao Comitê
Executivo. Cada item do enunciado aponta para o arquivo que o responde.

## 1. Entregáveis técnicos — quinta, 22/10, 18h

| Entrega esperada (enunciado) | Onde está |
|---|---|
| Arquitetura medalhão: camadas de ingestão, tratamento e consolidação, com rastreabilidade, qualidade e integridade | [`tecnico/arquitetura-medalhao.md`](tecnico/arquitetura-medalhao.md) e o código em [`../medalhao/`](../medalhao/) |
| Notebooks documentados, em Databricks Free Edition | [`../medalhao/`](../medalhao/) (4 notebooks) + [`tecnico/notebooks-e-jobs.md`](tecnico/notebooks-e-jobs.md) |
| Painel de indicadores consolidado | [`tecnico/painel-indicadores.md`](tecnico/painel-indicadores.md) (7 páginas, parâmetro `PastaCSV`, conferência dos cartões) + projeto PBIP em [`../powerbi/`](../powerbi/) + pacote CSV em `data/powerbi/` (fora do git) |
| Jobs automáticos entre os notebooks; pipeline idempotente | [`tecnico/notebooks-e-jobs.md`](tecnico/notebooks-e-jobs.md) e as provas em [`tecnico/evidencias/`](tecnico/evidencias/) (YAML do Job, manifestos, validação) |

Apoio: [`databricks-estrutura.md`](databricks-estrutura.md) (pastas, Volume, permissões, troubleshooting) e
[`tecnico/historico-revisoes-silver-gold.md`](tecnico/historico-revisoes-silver-gold.md) (decisões e revisões da silver/gold).

## 2. Entregáveis analíticos e de negócio — sexta, 23/10 (20 min + 15 min de perguntas)

| Entrega esperada (enunciado) | Onde está |
|---|---|
| Leitura sobre a confiabilidade dos dados: inconsistências, tratamento e impacto nos indicadores | [`analitico/confiabilidade-dos-dados.md`](analitico/confiabilidade-dos-dados.md) |
| Apresentação executiva com as principais conclusões | [`analitico/roteiro-apresentacao.md`](analitico/roteiro-apresentacao.md) (roteiro de 20 min) sobre os números de [`../resultados/`](../resultados/) |
| Propostas de solução priorizadas, com critério explícito e ganho esperado (pelo menos 2 quantificados, com premissas) | [`analitico/propostas-e-priorizacao.md`](analitico/propostas-e-priorizacao.md) |
| Discussão de oportunidades e aprendizados | [`analitico/oportunidades-e-aprendizados.md`](analitico/oportunidades-e-aprendizados.md) |

Os números que sustentam tudo isso (visão geral, funil, motivos, atendentes, satisfação, perfil de cliente,
custos e simulação) estão em [`../resultados/`](../resultados/), cada um citando a tabela gold de origem.

## 3. Processo do grupo

- [`convencoes-git.md`](convencoes-git.md): branches, commits e Pull Requests.
- [`databricks-estrutura.md`](databricks-estrutura.md): como o workspace está organizado.
