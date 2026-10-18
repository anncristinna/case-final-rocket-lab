# Achados — análise geral corrigida

Resultado de rodar `analises/analise_geral_corrigida.py` localmente (PySpark 4.2, Spark local) sobre os
8 CSVs completos em `data/raw/`. **Reconfirmar rodando no Databricks do grupo antes de usar no Notion
ou em slides.** Nenhuma linha de `clientes` (CPF/nome/e-mail) aparece neste documento.

## Por que refazer a análise do Juan

O notebook exploratório inicial (`data/Análise de Chamados Insights Primários.ipynb`, mantido só
localmente — tem um e-mail pessoal embutido no `base_path`, por isso não entra no git) tinha a estrutura
certa, mas 6 problemas que distorceram os números:

| # | Problema no original | Quanto pesa | Correção |
|---|---|---|---|
| 1 | `inferSchema=True` na leitura — risco de perder o zero à esquerda do CPF (`id_cliente`) | risco silencioso, não quantificado | leitura 100% `string`; cast explícito só do que precisa virar número/data |
| 2 | Limpeza de `custo` remove **todo ponto** (`regexp_replace(col, "\\.", "")`) → `23.24` virava `2324`, `74.71reais` virava `7471` | custo total saía em **R$ 42,2 milhões** | só remove ponto de milhar quando o valor tem vírgula (daí sim é separador brasileiro); custo total correto: **R$ 1.447.671,52** |
| 3 | `tempo_espera`/`tempo_atendimento` usados direto de `chamados`, rotulados como "min" no resumo final | são **segundos**, e truncados para durações ≥ 1.000 s (perde a casa de milhar) | tempos vêm sempre de `chamados_hora` (timestamps reais); nunca do campo truncado |
| 4 | Notas de pesquisa -1, 0 e 6 entram na média (filtro só pega nulo) | contamina a nota/CSAT | nota só é válida de 1 a 5; resto vira `null` + flag `dq_nota_invalida` |
| 5 | 2.636 `id_chamado` duplicados (idênticos) não removidos antes de agregar | infla todo volume/contagem em ~2% | `dropDuplicates(["id_chamado"])` antes de qualquer agregação |
| 6 | `chamados_hora` não é usado em nenhum insight — sem abandono, sem correção do ano de abertura | abandono (3.414 chamados, 2,6%) ficava invisível | abandono = sem hora de início de atendimento; ~198 chamados com ano de abertura errado (+1/+2 anos) corrigidos comparando com a finalização |

Pontos do original que já estavam certos e foram mantidos: a estrutura dos insights (panorama, por canal,
por motivo, por região, por atendente), a identificação de que `resolvido` e `canal` tinham grafias
inconsistentes, e de que havia duplicatas em `chamados`.

## Volumes

| Base | Linhas (arquivo) | Linhas (após tratamento) |
|---|---|---|
| chamados | 134.474 | 131.838 (2.636 duplicatas removidas) |
| chamados_hora | 131.838 | 131.838 |
| clientes | 47.705 | 47.705 |
| custos | 131.069 | 130.288 (781 duplicatas removidas) |
| pesquisa_satisfacao | 81.021 | 80.219 únicas por chamado (6.899 notas inválidas no arquivo: 421 com `-1`, 393 com `0`, 407 com `6`, 2.842 realmente vazias e **2.836 com a string literal `"NULL"` como texto**, não um campo vazio — `try_cast` trata as duas formas de ausência do mesmo jeito; ver `analises/perfil_custos_pesquisa.md`) |
| base_atendentes / base_motivos / canais | 25 / 14 / 4 | idem |

198 chamados tiveram o ano da abertura corrigido (+1/+2 anos); 3.414 chamados (2,6%) ficaram sem hora de
início — contados como abandono.

## Indicadores gerais (tratados)

| Indicador | Valor |
|---|---|
| Chamados únicos | 131.838 |
| Clientes | 47.705 |
| Atendentes ativos | 20 |
| Custo total | R$ 1.447.671,52 |
| Taxa de resolução | 50,9% |
| TME (tempo médio de espera) | 216,0 s (3,6 min) |
| TMA (tempo médio de atendimento) | 661,9 s (11,0 min) |
| Abandono | 2,6% |
| CSAT (notas 4 e 5) | 71,6% |
| Nota média | 3,98/5 (73.383 respostas) |

## Impacto da correção (ingênuo vs. tratado)

| Indicador | Ingênuo (notebook original) | Tratado | Por quê |
|---|---|---|---|
| Custo total | R$ 42,2 milhões | **R$ 1.447.671,52** | limpeza removia todo ponto decimal |
| Volume de chamados | 134.474 | 131.838 | duplicatas idênticas |
| Satisfação média | 3,94/5 (inclui -1, 0, 6) | 3,98/5 (só notas 1-5) | pouca diferença no valor, mas o critério agora é correto |
| Abandono | não calculado | 2,6% (3.414 chamados) | não usava `chamados_hora` |
| TMA | rotulado "min", vindo do campo truncado | 661,9 s (11,0 min), pelos timestamps | campo original trunca durações ≥ 1.000 s |

## Pendências / decisões do grupo

- Confirmar todos os números rodando este notebook no Databricks antes de levar ao Notion ou a slides.
- `categoria` vazia em 3 motivos (ex.: "Cancelamento de conta") aparece como "(sem categoria — a
  confirmar)" — decidir se vale imputar uma categoria com o grupo.
- Custos ≤ 0 (negativos ou zero) continuam entrando na soma do custo total, só com flag
  `dq_custo_nao_positivo` — não foi reavaliado se devem ser excluídos.
- Atendentes de nível 1 concentram os maiores volumes individuais (os 10 com mais chamados são todos
  nível 1) — não investigamos se isso é um problema de distribuição de carga ou só reflexo de serem mais
  atendentes nesse nível.
