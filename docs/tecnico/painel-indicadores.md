# Painel de indicadores consolidado (Power BI)

Entregável técnico: *painel de indicadores consolidado, com as principais métricas que ilustram o resultado dos tratamentos*. O Databricks Free
Edition não integra com o Power BI; o caminho previsto pelo enunciado é exportar a camada gold em CSV e importar no Power BI Desktop. O
`Gold_To_CSV.ipynb` faz a exportação e o painel lê as **14 tabelas analíticas** dessa exportação.

## O que é e onde está

| Item | Onde |
|---|---|
| **Projeto PBIP** (texto, versionável) | [`../../powerbi/painel-v-credit/`](../../powerbi/painel-v-credit/): `Painel_Atendimento_VCredit.pbip` abre o projeto |
| Relatório (páginas e visuais, em JSON) | `Painel_Atendimento_VCredit.Report/definition/` (7 páginas) |
| Modelo semântico (tabelas, medidas, relacionamentos, parâmetro, em TMDL) | `Painel_Atendimento_VCredit.SemanticModel/definition/` |
| **Arquivo `.pbix`** | Disponível no drive do grupo. **Não** é versionado, porque embute dados |
| **PDF do painel** (7 páginas, versão de 22/10/2026) | [`evidencias/painel/painel-atendimento-v-credit.pdf`](evidencias/painel/painel-atendimento-v-credit.pdf) |
| Dados (CSV, cache `.abf`, `localSettings.json`) | **Não vão para o git**: o `.gitignore` bloqueia CSV, `.pbix`, `.zip`, o cache (`cache.abf`) e as configurações locais (`localSettings.json`) do Power BI |

O PBIP guarda só definição, sem dados. Quem abre o projeto precisa apontar o parâmetro `PastaCSV` para uma exportação e **atualizar** para carregar os dados.

## Fonte de dados: as 14 tabelas analíticas

O parâmetro **`PastaCSV`** (texto) deve apontar para a pasta `analiticas` de uma exportação do Job (por exemplo
`exportacao_powerbi/exp_<timestamp>/analiticas`, ou a pasta `analiticas` do `pacote_powerbi.zip` descompactado; `<timestamp>` é o `pacote_id` do
`_manifesto`). Cada tabela lê `<PastaCSV>\<nome>.csv` (UTF-8, vírgula; o `Text.TrimEnd` aceita a pasta com ou sem `\` no fim). No repositório o
valor é um caminho genérico (`C:\caminho\para\exportacao\analiticas`) e **precisa ser trocado** em cada máquina.

| CSV | Granularidade | Filtra por período |
|---|---|---|
| `visao_geral.csv` | 1 linha, período completo | Não |
| `kpi_mensal.csv` | 1 linha por mês | Sim |
| `comparativo_yoy.csv` | 1 linha por mês do ano, 2025 e 2026 lado a lado | Não |
| `funil_atendimento.csv` | 1 linha por canal, período completo | Não |
| `etapa_mensal.csv` | mês × etapa do funil | Sim |
| `motivos_pareto.csv` | 1 linha por motivo | Não |
| `motivo_etapa.csv` | motivo × etapa do funil | Não |
| `demanda_dia_hora.csv` | dia da semana × hora de abertura | Não |
| `atendentes_desempenho.csv` | 1 linha por atendente | Não |
| `satisfacao_drivers.csv` | fator × valor, só chamados com nota | Não |
| `perfil_cliente.csv` | faixa etária ou região × etapa | Não |
| `qualidade_dados.csv` | 1 linha por indicador de qualidade | Não |
| `impacto_indicadores.csv` | indicador × método de cálculo | Não |
| `simulacao_ganhos.csv` | cenário × motivo (o painel recalcula os totais) | Não |

Além delas, o modelo tem tabelas calculadas dentro do próprio painel: `DimMes` e `DimEtapa` (eixos compartilhados), `Medidas`, `Alertas`,
`Metrica Heatmap`, `Premissa A` e `Premissa B` (seletores das premissas dos cenários), `Oportunidades`, `Def_Indicadores` e `Def_Tabelas`.

## As 7 páginas

| # | Página | Público | O que responde |
|---|---|---|---|
| 1 | **Visão executiva** | Comitê Executivo | Oito cartões (chamados, custo total, custo médio, resolução, TME, TMA, CSAT e a taxa de chamados sem início de atendimento), evolução mensal, custo no funil e "pontos de atenção". O que mudou ao longo dos meses, onde o custo se concentra e o que pede atenção imediata |
| 2 | **Financeiro** | Gerente Financeiro | O custo total cresce mais rápido que o volume? Qual etapa e quais motivos concentram o custo? Quanto custa cada resolução? Traz a diferença contra os R$ 1,4 mi da entrevista e a economia anual dos cenários A e B. Avisa que **não há receita** nas tabelas |
| 3 | **Customer Success** | Coordenadora de Customer Success | O TMA subiu e a resolução caiu, em qual etapa? Quando a demanda aperta e a espera sobe (mapa de calor)? Quais atendentes e motivos pedem apoio? Inclui o desempenho por atendente contra a média do nível (só com amostra suficiente) |
| 4 | **Tecnologia e dados** | Diretor de Tecnologia | O chatbot e a URA resolvem a maior parte? Que perfis mais chegam ao humano? Quais inconsistências existem (o gráfico mostra só os defeitos acima de 5% dos chamados; indicadores informativos ficam de fora) e quanto o tratamento muda os indicadores (`qualidade_dados` e `impacto_indicadores`)? Registra a decisão de privacidade (hash SHA-256 sem segredo) |
| 5 | **Marketing e CSAT** | Diretora de Marketing | O CSAT de 2026 difere do de 2025? Quanto dos chamados responde à pesquisa? Que fatores (espera, reincidência, resolução, etapa, canal, motivo, faixa horária) se associam a notas baixas? Lê como associação, não causalidade |
| 6 | **Oportunidades** | Comitê Executivo | Quais iniciativas trazem mais ganho, com quais premissas e o que ainda falta medir. Seletores das premissas de deflexão (A) e de redução de reincidência (B); sem seleção valem 20% e 30% |
| 7 | **Definições** | Todos | Como cada indicador é calculado, de qual tabela vem e a granularidade de cada tabela |

Cada página tem um quadro "Sobre esta página" (objetivo, público, perguntas e ações possíveis), e as páginas 1, 2, 3 e 5 têm filtro de período.

## Como abrir

1. Baixe uma exportação do Job (`pacote_powerbi.zip` do Volume `exportacao_powerbi`) e descompacte **fora do repositório**.
2. No Power BI Desktop, **abra o arquivo** `powerbi/painel-v-credit/Painel_Atendimento_VCredit.pbip`. Se o Desktop não abrir o formato, habilite o recurso de projeto (`.pbip`) em *Opções → Recursos em versão prévia*.
3. **Transformar dados → Gerenciar parâmetros → `PastaCSV`**: informe a pasta `analiticas` descompactada.
4. **Atualizar**. Confira os cartões abaixo.
5. Para entregar, salve também como `.pbix` no drive do grupo e exporte PDF e prints das páginas.

Não baixe o zip entre 12:00 e 12:10 (nem entre 00:00 e 00:10): o Job regrava o pacote nesses horários.

## Conferência dos cartões (período completo)

No período completo, os cartões leem `visao_geral` (valores exatos). Com filtro de período, o painel usa a média dos meses ponderada pelos chamados (CSAT, pelas
respostas), que é uma aproximação. O formato do cartão pode exibir o valor arredondado.

| Cartão | Valor esperado |
|---|---|
| Chamados | 131.838 |
| Custo total | R$ 1.450.617,85 |
| Custo médio por chamado | R$ 11,18 |
| Taxa de resolução | 50,88% |
| TME | 3,60 min |
| TMA | 11,03 min |
| CSAT | 71,57% |
| SEM INÍCIO DE ATENDIMENTO (PROXY), cartão das páginas 1 e 3 | 2,59% |
| Economia anual, cenário A (páginas 2 e 6) | R$ 30,9 mil (o cartão mostra R$ 30.863) |
| Economia anual, cenário B (páginas 2 e 6) | R$ 258,1 mil (o cartão mostra R$ 258.065) |

Os oito primeiros são os valores de `visao_geral.csv` (pacote `exp_20261022_012729`) e os dois cenários vêm de `simulacao_ganhos.csv`; com a mesma base eles devem se repetir em qualquer exportação nova. **Os cenários A e B se sobrepõem (98% da base de A já está em B): não somar.**
Se o custo aparecer 100 vezes maior (por exemplo `145061785`), a localidade de leitura do CSV está errada: use inglês (Estados Unidos) para números e datas.

## Limitações

- **Só as 14 tabelas agregadas, sem estrela.** O painel não usa as tabelas do modelo (`modelo/fato_atendimento.csv` e dimensões) e, por isso, não detalha por chamado. Os únicos relacionamentos são entre as tabelas mensais e de etapa e as dimensões `DimMes` e `DimEtapa`; as demais tabelas se ligam por medidas.
- **Cenários A e B não somam.** 98,1% da base do cenário A (12.172 de 12.411 chamados) já está na base do B (conferido no Databricks em 22/10/2026). Cada cartão mostra um cenário; somar os dois conta a mesma economia duas vezes. As premissas de 20% e 30% são hipóteses do grupo.
- **Abandono é um proxy.** O indicador conta chamados **sem hora de início de atendimento**; não confirma que o cliente desistiu. Por isso os cartões, eixos, títulos e alertas se chamam "sem início de atendimento (proxy)"; no mapa de calor a métrica é "Sem início (proxy)". Só os **nomes internos** das medidas e das colunas ainda usam "abandono" (`Abandono`, `Abandono CS`, `pct_abandono` etc.), e a definição na página 7 explica a equivalência.
- **Sem receita.** Não dá para dizer se o custo acompanha a receita, a preocupação do Gerente Financeiro.
- **Valores de período parcial são aproximados** (média de médias ponderada).
- **Nomes de atendentes mantidos; base fictícia.** A página "Customer Success" mostra `rotulo_atendente` (`anonimizar_atendente = false`, o padrão do `Gold_To_CSV`). Decisão do grupo, registrada aqui para não parecer esquecimento.
- **Campo atendente em chamados de autosserviço.** Vem preenchido em 99,4% dos chamados de URA e chatbot, onde não deveria haver atendente humano. Até confirmarmos o significado do campo (pergunta à V-Credit, em [`../analitico/confiabilidade-dos-dados.md`](../analitico/confiabilidade-dos-dados.md)), os números por atendente são indicativos e a tabela da página "Customer Success" é uma associação, não um ranking de desempenho.
- **Prevenção (site e app)** não existe nos dados; o painel não a mostra.
