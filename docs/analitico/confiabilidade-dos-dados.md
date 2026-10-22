# Confiabilidade dos dados

Entregável analítico (Comitê Executivo): *leitura sobre a confiabilidade dos dados, apontando as principais
inconsistências encontradas, como foram tratadas e o impacto delas sobre os indicadores que a V-Credit acompanha hoje*.

Fontes: `qualidade_dados_gold`, `impacto_indicadores_gold`, `qualidade_chamado_gold` e os logs de contagem de
`medalhao/Bronze_To_Silver.ipynb`. Percentuais sobre os 131.838 chamados únicos, salvo indicação.

## Em uma frase

Os dados são **utilizáveis para decidir**, desde que passem pelo tratamento da silver: sem ele, o custo apareceria 29× maior, a espera, negativa, o
volume, 2% inflado e o CSAT, contaminado por notas impossíveis. **Três pontos seguem frágeis na origem** e merecem correção no sistema, não só no pipeline: a
**identificação do atendente**, a **cobertura da pesquisa de satisfação** e o **registro de abandono**.

## Confiança por indicador (após o tratamento)

| Indicador | Confiança | Por quê |
|---|---|---|
| Volume de chamados | Alta | Duplicatas idênticas removidas; 0 chamado sem registro na base de horários |
| Custo total e por chamado | Alta | Regra de limpeza validada contra o total esperado; 1,2% dos chamados sem custo (não somados) |
| TME e TMA | Alta | Todos os chamados atendidos têm sequência de horários válida após correção; só 199 chamados corrigidos (0,15%) |
| Taxa de resolução | Média-alta | 1,5% sem informação; depende de o abandono entrar ou não no denominador (50,9% contra 52,2%) |
| Abandono | Média | Definido por ausência de horário de início; não distingue desistência de falha de registro |
| Reincidência | Média | Exige `id_cliente`. Neste conjunto todos os chamados trazem id de cliente (`chamado_sem_id_cliente` = 0), então os 131.838 são elegíveis (`recontato_elegivel`) e os 1.330 com id sem cadastro **entram** na reincidência (só ficam fora de `perfil_cliente`). Limite: compara só com o chamado anterior imediato do mesmo cliente e motivo |
| **CSAT** | **Média-baixa** | 39,2% dos chamados sem pesquisa, cobertura caindo de 65% para 48%, 5,2% com nota fora da escala |
| **Análise por atendente** | **Baixa** | 56,6% dos chamados de autosserviço trazem atendente; 12,0% fora do vínculo do atendente |

(Classificação proposta pelo Claude Code, a validar pelo grupo.)

## Inconsistências, tratamento e impacto

| # | Inconsistência | Tamanho | Tratamento | Impacto no indicador |
|---|---|---|---|---|
| 1 | `id_chamado` duplicado em `chamados` (cópias idênticas) | 2.636 (134.474 → 131.838) | Remoção das cópias exatas na silver | Volume e todos os totais inflados em ~2% se não removido |
| 2 | `id_custo` duplicado em `custos` (idênticos) | 781 | Remoção por `id_custo` | Custo duplicado |
| 3 | `custo` em formatos mistos (`9,99`, `R$ 9,99`, `9.99reais`, negativos) | Toda a coluna | Só dígitos, vírgula e ponto; vírgula = decimal brasileiro; sem vírgula, o ponto já é decimal | **Remover todo ponto (erro do notebook exploratório inicial) levava o total a R$ 42,2 mi; o correto é R$ 1,45 mi (29× menor)** |
| 4 | Custo ≤ 0 (negativo ou zero) | 544 em `qualidade_dados` (`custo_invalido_ou_nao_positivo`, 0,41% dos **chamados**). Divisão 271 negativos / 273 zeros e unidade (chamados ou lançamentos): **a confirmar** | Ficam na silver (`custo_com_problema`), fora da soma da gold | Total R$ 1.450.617,85 (só valores > 0) |
| 5 | Chamados sem nenhum custo | 1.550 (1,18%) | Custo nulo (não zero) | Custo médio por chamado: R$ 11,18 (só com custo) contra R$ 11,00 (diluído em todos) |
| 6 | `tempo_atendimento` de `chamados` truncado para durações ≥ 1.000 s | Campo todo | **Nunca usado**; tempos vêm dos timestamps de `chamados_hora` | Subestimaria o TMA humano em várias vezes (valores preliminares, a confirmar, em [`../tecnico/arquitetura-medalhao.md`](../tecnico/arquitetura-medalhao.md)) |
| 7 | Ano de abertura errado (abertura posterior à finalização) | 198 (0,15%) | Corrigido pelo ano da finalização, só quando a cadeia de horários fica válida | **TME bruto médio de −1.211,9 min (negativo) contra 3,6 min tratado** |
| 8 | Virada de dia não registrada (atendimento cruza a meia-noite) | 1 | Soma 1 dia à finalização (regra restrita, auditável) | Desprezível |
| 9 | Chamado sem horário de início | 3.414 (2,59%) | Marcado como **abandonado** (informativo); fora de TME/TMA | Abandono antes invisível (o notebook exploratório não usava `chamados_hora`) |
| 10 | Nota de satisfação fora de 1 a 5 (`-1`, `0`, `6`, vazio) | 6.836 (5,19%) | `nota` nula + `dq_nota_invalida`; **`nota_ajustada`** recupera 6→5 e 0/−1→1 como cenário (1.209 notas) | CSAT 71,57% (válidas) contra 70,96% (ajustada): −0,61 p.p. |
| 11 | Chamados sem pesquisa de satisfação | 51.619 (39,15%) | Nulo; fora da média | CSAT só representa quem respondeu; cobertura caiu de 65,0% (jan/25) para 48,4% (jul/26) |
| 12 | `resolvido` em branco | 2.014 (1,53%) | Nulo; fora do denominador | Resolução 50,88% (sobre informados) contra 52,24% (só atendidos) |
| 13 | `id_atendente` inválido (0, 99, 999, texto) | 764 (0,58%) | Membro `-2` "inválido na origem" | Sem atendente para esses chamados |
| 14 | Chamado humano sem atendente válido | 338 (0,26%) | Membros `-1`/`-2` | Idem |
| 15 | Chamado aberto antes da admissão ou depois do desligamento do atendente | 15.874 (12,04%) | Flag `atendente_fora_vigencia`; mantido | **Atribuição chamado → atendente não confiável** para ~1 em 8 chamados |
| 16 | Chamado de autosserviço (URA/chatbot) com atendente informado | 74.624 (56,60%) | Flag `autosservico_com_atendente`; mantido | Desempenho por atendente mistura autosserviço e humano |
| 17 | `id_cliente` do chamado sem cadastro em `clientes` | 1.330 (~1,0%) | `dq_cliente_sem_correspondencia`; membro `SEM_CADASTRO` no modelo do Power BI | Ficam fora de análises por perfil de cliente |
| 18 | Grafias de canal e de nível do atendente, caixa em criticidade, categoria de motivo vazia | Várias | Normalização e de-para (0 canais sem correspondência, 0 motivos sem correspondência); categoria vazia → "Outro" | Evita canais duplicados e motivos sem categoria |

Verificações que **passaram sem inconsistência**: 0 chamados sem canal ou motivo mapeado, 0 chamados sem registro na
base de horários, 0 chamados com mais de um custo, 0 erros de leitura de data, 0 atendente fora do cadastro e 0
atendente de nível divergente do canal (todos em `qualidade_dados_gold`).

## O impacto em uma tabela (`impacto_indicadores_gold`)

| Indicador | Método A | Método B | Diferença |
|---|---|---|---|
| CSAT | 71,57% (nota válida de 1 a 5, n = 73.383) | 70,96% (nota ajustada, n = 74.592) | −0,61 p.p. |
| Custo médio por chamado | R$ 11,18 (só com custo válido) | R$ 11,00 (diluído em todos) | −R$ 0,18 |
| TME | −1.211,93 min (bruto, inclui negativas) | 3,60 min (tratado) | +1.215,5 min |
| TMA | 11,02 min (bruto) | 11,03 min (tratado) | +0,01 min |
| Taxa de resolução | 50,88% (todos os informados) | 52,24% (exclui abandonados) | +1,36 p.p. |

Leitura: o tratamento **muda muito** o custo (R$ 42 mi → R$ 1,45 mi) e o TME (negativo → 3,6 min) e muda
**pouco** o TMA, o CSAT e a resolução, ou seja, as conclusões sobre eles são robustas à escolha do método.

## Segurança e privacidade da informação (preocupação do Diretor de Tecnologia)

- O `id_cliente` é o CPF e vem com nome e e-mail em `clientes`. No pipeline: nome e e-mail **nunca entram** em nenhuma seleção; o CPF só existe como chave de junção na silver e **nunca é exibido**; a gold só tem `id_cliente_hash` (SHA-256).
- Um achado de processo: uma versão anterior do notebook de verificação da bronze exibia amostras de `chamados` e `Chamados_Hora` que continham o `id_cliente` (CPF). Foi corrigido e as saídas, apagadas.
- O hash é SHA-256 **puro** (sem segredo) por decisão do grupo, pois o id do case é fictício. **Em dados reais seria necessário HMAC com segredo** ou pseudonimização por tabela de-para controlada.
- Cópia dos CSVs em pasta de Workspace compartilhada (`dados`) amplia a superfície de acesso: o destino recomendado é um **Volume do Unity Catalog** com `READ VOLUME` só para quem precisa.

## Recomendações de governança

1. **Atendente**: validar vínculo (admissão e desligamento) no momento do registro, impedir `id_atendente` em chamados de URA/chatbot e tipar o campo (hoje aceita 0, 99, 999 e texto).
2. **Pesquisa de satisfação**: validar a escala na captura (1 a 5), reduzir atrito para responder e medir cobertura mensal como KPI; sem isso, o CSAT não é confiável.
3. **Abandono**: registrar explicitamente o motivo do encerramento (cliente desistiu, queda, erro) em vez de inferir pela ausência do horário de início.
4. **Custo**: um único formato numérico na origem (decimal com ponto) e lançamento negativo/zero justificado.
5. **Chave única**: impedir `id_chamado` e `id_custo` duplicados na extração.
6. **Cadastro de clientes**: 1% dos chamados aponta para cliente inexistente; reconciliar as duas bases.
7. **Visão única**: manter o pipeline medalhão como fonte única de indicadores (hoje os números vivem em bases dispersas, como relatou o Diretor de Tecnologia).

## A confirmar no Databricks

Estes números ainda não foram conferidos por consulta no workspace. Até rodar as queries, valem como **a confirmar**:

| Item | Onde aparece | Query de conferência |
|---|---|---|
| 544 com custo ≤ 0, divisão 271 negativos / 273 zeros e unidade (chamados ou lançamentos) | Tabela de inconsistências, linha 4 | `SELECT COUNT_IF(custo < 0) AS negativos, COUNT_IF(custo = 0) AS zeros, COUNT(DISTINCT id_chamado) AS chamados FROM dados_vcredit.default.custos_silver WHERE custo <= 0` |
| Números da fonte da verdade dos tempos (média do campo truncado contra a dos timestamps) | [`arquitetura-medalhao.md`](../tecnico/arquitetura-medalhao.md), seção "Fonte da verdade dos tempos" | Query na mesma seção |
| Sobreposição entre os cenários A e B (12.172 de 12.411) | [`07-custos-e-simulacao.md`](../../resultados/07-custos-e-simulacao.md) | Query na mesma seção |
