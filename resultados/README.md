# resultados/

Resultados da análise sobre a **camada gold** (janeiro/2025 a julho/2026, 19 meses, 131.838 chamados únicos).
Cada arquivo traz os números de uma frente, a tabela gold de origem e a leitura. Nada aqui é digitado à mão a
partir de outra fonte: os números saem das tabelas `dados_vcredit.default.*_gold` (e, equivalentemente, dos CSVs
de `analiticas/` do pacote do Power BI, `exp_20261022_012729`).

| Arquivo | Conteúdo | Tabelas gold de origem |
|---|---|---|
| [`01-visao-geral.md`](01-visao-geral.md) | KPIs gerais, evolução mensal, comparativo ano contra ano, e o que cada fala das entrevistas diz em face dos dados | `visao_geral`, `kpi_mensal`, `comparativo_yoy` |
| [`02-funil-e-canais.md`](02-funil-e-canais.md) | Funil de atendimento por etapa e canal, custo por etapa, evolução mensal por etapa | `funil_atendimento`, `etapa_mensal` |
| [`03-motivos.md`](03-motivos.md) | Pareto de motivos, escape do autosserviço, reincidência e custo | `motivos_pareto`, `motivo_etapa` |
| [`04-atendentes.md`](04-atendentes.md) | Desempenho por nível, capacidade instalada e limites da leitura | `atendentes_desempenho`, `dim_atendente` |
| [`05-satisfacao.md`](05-satisfacao.md) | O que move o CSAT: espera, etapa, reincidência, resolução; demanda por dia e hora | `satisfacao_drivers`, `demanda_dia_hora` |
| [`06-perfil-clientes.md`](06-perfil-clientes.md) | Faixa etária e região: há diferença de comportamento? | `perfil_cliente` |
| [`07-custos-e-simulacao.md`](07-custos-e-simulacao.md) | Custo total e por etapa, simulação dos cenários A e B, sensibilidade | `visao_geral`, `funil_atendimento`, `simulacao_ganhos` |

A confiabilidade dos dados (inconsistências, tratamento e impacto) está em
[`../docs/analitico/confiabilidade-dos-dados.md`](../docs/analitico/confiabilidade-dos-dados.md), e as recomendações em
[`../docs/analitico/propostas-e-priorizacao.md`](../docs/analitico/propostas-e-priorizacao.md).

## Definições (iguais às do Power BI)

- **Taxa de resolução**: chamados com `resolvido = true` ÷ chamados com `resolvido` informado (2.014 chamados ficam fora por não terem informação).
- **TME**: abertura → início do atendimento. **TMA**: início → finalização. Ambos pelos timestamps de `chamados_hora`, em minutos, só entre chamados atendidos com sequência de horários válida.
- **CSAT**: % de notas 4 e 5 entre as respondidas (nota válida de 1 a 5). **CSAT ajustado** usa `nota_ajustada` (6→5; 0 e -1→1).
- **Abandono**: chamado sem hora de início de atendimento.
- **Custo**: soma dos lançamentos de `custos` maiores que zero; **custo por chamado** = custo ÷ chamados com custo válido.
- **Etapas do funil**: Autosserviço (URA e Chatbot), Nível 1 (Atendimento Inicial), Nível 2 (Atendimento Especializado).
- **Reincidência (7d)**: o mesmo cliente abriu outro chamado com o mesmo motivo até 7 dias depois do anterior.

## Cuidados

- Os números cobrem os 131.838 chamados únicos (2.636 duplicatas idênticas removidas na silver).
- Não há nenhum dado pessoal de cliente. Atendentes aparecem por `id_atendente` e nível (no painel os nomes são mantidos por decisão do
  grupo, base fictícia; ver [`../docs/tecnico/arquitetura-medalhao.md`](../docs/tecnico/arquitetura-medalhao.md)).
- Para reproduzir: rodar o job da pasta [`../medalhao/`](../medalhao/) e consultar a tabela gold indicada.

Versão consolidada em PDF: [`../docs/pdf/02-Documentacao-da-Solucao-VCredit.pdf`](../docs/pdf/02-Documentacao-da-Solucao-VCredit.pdf).
