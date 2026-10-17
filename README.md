# Case Final Rocket Lab — V-Credit

Transformação digital do atendimento da **V-Credit** (case Visagio / Rocket Lab 2026). Objetivo: a partir
da análise dos dados de atendimento, chegar a recomendações práticas, priorizadas e justificadas com
dados (pelo menos 2 com ganho quantificado e premissas explícitas) para o Comitê Executivo.

> ⚠️ O enunciado e as bases do case são confidenciais (propriedade intelectual da Visagio).
> **Nenhum CSV deve ser commitado.** O `.gitignore` já bloqueia, mas confira antes de cada push.

## Abordagem atual

Recomeço deliberadamente mais simples: em vez de um notebook por pessoa com arquitetura medalhão, o
grupo parte do notebook exploratório inicial do Juan e constrói **um único notebook corrigido**
(`analises/analise_geral_corrigida.py`), testado localmente e depois subido manualmente ao workspace
Databricks do grupo (sem Git folder por enquanto). **Os resultados vão para o Notion compartilhado** —
os arquivos `.md` em `analises/` já estão prontos para essa transcrição.

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
│   └── achados_analise_geral.md   # o que foi corrigido no notebook e por quê, indicadores gerais
├── analises/
│   ├── README.md
│   ├── analise_geral_corrigida.py # notebook — carga, limpeza e insights
│   ├── panorama_geral.md          # \
│   ├── por_canal.md               #  > conteúdo pronto para o Notion
│   ├── top_motivos.md             #  >
│   ├── por_regiao.md              #  >
│   └── top_atendentes.md          # /
└── data/raw/                      # CSVs originais (fora do git)
```

## Grupo

Yuri, Cris, Juan, Richard, Milton, Gabriel, Anna.

## Como começar

1. Clone o repositório e crie sua branch: `git switch -c feat/<seu-nome>-<assunto>` (convenção completa em
   [`docs/convencoes-git.md`](docs/convencoes-git.md)).
2. Copie os 8 CSVs para `data/raw/` (fora do git).
3. Para testar localmente: PySpark 4.x (um venv isolado funciona bem) sobre os CSVs de `data/raw/`.
4. Para rodar no Databricks: *Workspace → Import* do `analise_geral_corrigida.py`, preencha o widget
   `base_path` e rode. Sem Git folder por enquanto — depois de testar, traga a versão final de volta
   para o repositório.

## Regras rápidas

- **Nunca** trabalhe direto na `main` sem necessidade — branch + PR, revisão de pelo menos 1 pessoa
  (ver `docs/convencoes-git.md`). Exceção já usada: a configuração inicial do repositório.
- Sem CSV, sem dado pessoal (CPF/nome/e-mail de **clientes**) em output de célula, doc ou commit.
- Tempos de atendimento sempre pelos timestamps de `chamados_hora` — nunca pelo campo
  `tempo_atendimento` de `chamados` (truncado). Regras completas de dados em `CLAUDE.md`.
