# Case Final Rocket Lab — V-Credit

Transformação digital do atendimento da **V-Credit** (case Visagio / Rocket Lab 2026). Objetivo: a partir
da análise dos dados de atendimento, chegar a recomendações práticas, priorizadas e justificadas com
dados (pelo menos 2 com ganho quantificado e premissas explícitas) para o Comitê Executivo.

> ⚠️ O enunciado e as bases do case são confidenciais (propriedade intelectual da Visagio).
> **Nenhum CSV deve ser commitado.** O `.gitignore` já bloqueia, mas confira antes de cada push.

## Abordagem atual

Recomeço deliberadamente mais simples: em vez de arquitetura medalhão, o grupo parte do notebook
exploratório inicial do Juan e corrige num **notebook base único** (`analises/analise_geral_corrigida.py`,
mudado só por PR combinado — não há um `.py` por pessoa, pra não gerar conflito de merge). Cada um
explora o seu tema no Databricks do jeito que preferir e leva o resultado pro `.md` correspondente em
`analises/` (alguns já preenchidos, outros ainda são template). **Os resultados vão para o Notion
compartilhado** a partir desses `.md`.

Em paralelo, começou a camada bronze de verdade: `bronze/Landing_To_Bronze.ipynb` ingere as 8 tabelas
num notebook único (mudado só por PR revisado — ver `bronze/README.md`).

## Entregas e prazos

| O quê | Prazo |
|---|---|
| Entregáveis técnicos | **Quinta 22/10, 18h** |
| Apresentação final (20 min + 15 min de perguntas do Comitê) | **Sexta 23/10** |

## Estrutura

```
.
├── README.md                      # este arquivo
├── CLAUDE.md                      # contexto e regras para o Claude Code
├── docs/
│   ├── convencoes-git.md          # branches, commits (Conventional Commits) e Pull Requests
│   ├── achados_analise_geral.md   # o que foi corrigido no notebook e por quê, indicadores gerais
│   └── databricks-estrutura.md    # pastas, Volume, permissões e troubleshooting no workspace
├── analises/
│   ├── README.md                  # lista de arquivos, responsáveis e status
│   ├── analise_geral_corrigida.py # notebook base — carga, limpeza, panorama geral
│   ├── milton_custos_pesquisa.py  # notebook de Milton (%run na base)
│   ├── perfil_custos_pesquisa.md  # perfil coluna a coluna de custos/pesquisa_satisfacao
│   ├── panorama_geral.md          # \
│   ├── por_canal.md               #  \
│   ├── top_motivos.md             #   \
│   ├── por_regiao.md              #    > preenchidos — prontos para o Notion
│   ├── top_atendentes.md          #   /
│   ├── custos_pesquisa.md         #  /
│   └── tempos_abandono.md         # template a preencher (Juan)
├── bronze/                        # início da camada bronze de verdade
│   ├── README.md                  # como usar o notebook, responsável pelo grupo
│   └── Landing_To_Bronze.ipynb    # ingere as 8 tabelas — notebook único, mudado só por PR revisado
├── silver/                        # templates de notebooks da camada silver, um por responsável
│   ├── README.md                  # divisão por responsável e ordem de execução
│   ├── Silver_Clientes.ipynb              # Yuri
│   ├── Silver_Atendentes_Motivos.ipynb    # Cris
│   ├── Silver_Chamados_Hora.ipynb         # Juan
│   ├── Silver_Canais.ipynb                # Richard
│   ├── Silver_Custos_Pesquisa.ipynb       # Milton — já preenchido
│   └── Silver_Consolidado.ipynb           # junta as 5 silver + chamados numa base_silver
└── data/raw/                      # CSVs originais (fora do git)
```

## Grupo

Yuri, Cris, Juan, Richard, Milton, Gabriel, Anna.

## Divisão da análise inicial

Todos ficam com `chamados` (já coberto por `analises/panorama_geral.md`); por tabela:

| Responsável | Tabela(s) | Arquivo em `analises/` |
|---|---|---|
| Yuri | `clientes` | `por_regiao.md` |
| Cris | `base_atendentes`, `base_motivos` | `top_atendentes.md`, `top_motivos.md` |
| Juan | `chamados_hora` | `tempos_abandono.md` |
| Richard | `canais` | `por_canal.md` |
| Milton | `custos`, `pesquisa_satisfacao` | `custos_pesquisa.md` |

## Como começar

1. Clone o repositório e crie sua branch: `git switch -c feat/<seu-nome>-<assunto>` (convenção completa em
   [`docs/convencoes-git.md`](docs/convencoes-git.md)).
2. Copie os 8 CSVs para `data/raw/` (fora do git).
3. Para testar localmente: PySpark 4.x (um venv isolado funciona bem) sobre os CSVs de `data/raw/`.
4. Para rodar no Databricks: a pasta do grupo é `Shared/case-final-rocket-lab/` (`analises/`, `medalhao/`,
   `resultados/`). Os 8 CSVs ficam num **Volume do Unity Catalog** (`dados_vcredit`) — passo a passo
   completo (pastas, Volume, permissões) em `docs/databricks-estrutura.md`. Preencha o widget
   `base_path` com o caminho do Volume (copie pelo Catalog) e rode. Sem Git folder por enquanto —
   depois de testar, traga a versão final de volta para o repositório.

## Regras rápidas

- **Nunca** trabalhe direto na `main` sem necessidade — branch + PR, revisão de pelo menos 1 pessoa
  (ver `docs/convencoes-git.md`). Exceção já usada: a configuração inicial do repositório.
- Sem CSV, sem dado pessoal (CPF/nome/e-mail de **clientes**) em output de célula, doc ou commit.
- Tempos de atendimento sempre pelos timestamps de `chamados_hora` — nunca pelo campo
  `tempo_atendimento` de `chamados` (truncado).
- `chamados` e `custos` têm duplicatas — sempre `dropDuplicates` por `id_chamado`/`id_custo` antes de
  agregar, senão os números não batem entre os `.md` de cada tema. Regras completas em `CLAUDE.md`.
