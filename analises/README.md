# Análises exploratórias

Fase atual do grupo: cada responsável aprofunda a tabela da sua área, a partir do notebook inicial
do Juan e da carga compartilhada em `_carga_dados.py`. Os números citados nos esqueletos vêm de uma
execução local anterior (CSVs completos) — cada notebook deve reconfirmá-los ao rodar.

## Arquivos

| Arquivo | Responsável | Tabela(s) |
|---|---|---|
| `analise_chamados_insights_primarios.ipynb` | Juan | primeira leitura de `chamados` (original, intocado) |
| `_carga_dados.py` | compartilhado | leitura dos 8 CSVs, funções reutilizáveis (`norm_key`, `blank_to_null`, `add_try`, `CANAL_ALIAS`) |
| `clientes_yuri.py` | Yuri | `clientes` |
| `atendentes_motivos_cris.py` | Cris | `base_atendentes`, `base_motivos` |
| `chamados_hora_juan.py` | Juan | `chamados_hora` |
| `canais_richard.py` | Richard | `canais` |
| `custos_pesquisa_milton.py` | Milton | `custos`, `pesquisa_satisfacao` |
| `achados_qualidade_dados.md` | — | inconsistências encontradas e tratamento sugerido (movido de `docs/qualidade_dados.md`) |
| `achados_hipoteses.md` | — | afirmações dos stakeholders a validar com dados (movido de `docs/hipoteses.md`) |

Todos os notebooks de responsável individual começam com `%run ./_carga_dados` para reaproveitar a carga.

## `analise_chamados_insights_primarios.ipynb` (Juan)
Primeira análise direto dos CSVs, feita no Databricks. **Versão original, mantida como registro.**
Não usar os números do resumo final nos slides sem revisar. Problemas conhecidos (detalhes em `achados_qualidade_dados.md`):

| Ponto | No notebook | Correto |
|---|---|---|
| Custo total | R$ 42,2 mi | **R$ 1,45 mi**. A limpeza remove todo ponto, então `23.24` vira `2324` e `74.71reais` vira `7471` |
| Custo médio no especializado | R$ 1.411 | ~R$ 49 (mesmo erro) |
| Unidade dos tempos | "min" | segundos |
| TMA (216,7) | do campo `tempo_atendimento` | o campo trunca valores ≥ 1.000 s; pelos timestamps o TMA é ~662 s (humano ~1.361 s) |
| Volume | 134.474 | 131.838 (2.636 duplicatas idênticas) |
| Satisfação média | inclui notas -1, 0 e 6 | filtrar notas fora de 1–5 |

Pontos corretos: variações de `resolvido` e de `canal`, formatos de `custo`, 20 atendentes ativos e taxa de resolução geral (50,9%).
O caminho recomendado é recalcular os insights a partir dos notebooks de `analises/` (que usam `_carga_dados.py`)
em vez de limpar tudo de novo neste notebook.

Atenção: o caminho `base_path` do notebook contém o e-mail pessoal do autor. **Não alterar o `.ipynb` original** —
apenas evitar reutilizar esse caminho; os demais notebooks usam o widget `base_path` de `_carga_dados.py`, sem valor
padrão embutido.
