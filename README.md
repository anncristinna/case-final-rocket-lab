# Case Final Rocket Lab — V-Credit

Transformação digital do atendimento da **V-Credit** (case Visagio / Rocket Lab 2026).
Objetivo: a partir da análise dos dados de atendimento, chegar a recomendações práticas,
priorizadas e justificadas com dados para o Comitê Executivo.

> ⚠️ O enunciado e as bases do case são confidenciais (propriedade intelectual da Visagio).
> **Nenhum CSV deve ser commitado.** O `.gitignore` já bloqueia, mas confira antes de cada push.

Fase atual: **análise exploratória**, com cada pessoa aprofundando a tabela da sua responsabilidade
a partir do notebook inicial do Juan. A arquitetura medalhão (bronze/silver/gold) fica para uma
fase posterior — o rascunho já escrito está em [`medalhao_rascunho/`](medalhao_rascunho/), sem rodar por enquanto.

## Entregas e prazos

| O quê | Prazo |
|---|---|
| Entregáveis técnicos (medalhão, notebooks documentados, painel, jobs idempotentes) | **Quinta 22/10, 18h** |
| Apresentação final (20 min + 15 min de perguntas do Comitê) | **Sexta 23/10** |

## Cronograma do grupo

| Dia | Foco | Horário da reunião |
|---|---|---|
| Sáb 17/10 | Discussão do projeto, divisão de tarefas, criação do git, divisão do dataset para análise inicial | — |
| Dom 18/10 | Modelagem do problema, bronze e silver, definir o que entra na gold, consultas analíticas, como apresentar | 18h |
| Seg 19/10 | Gold, parte visual dos dados, decidir a solução e tudo que será entregue | 20h |
| Ter 20/10 | Elaborar a solução, justificar decisões com base nos dados, começar os entregáveis | 20h |
| Qua 21/10 | Slides e apresentação | 20h |
| Qui 22/10 | Treinar a apresentação | 20h |

> ⚠️ **Conflito de prazos a resolver:** o enunciado fixa os **entregáveis técnicos para quinta 22/10 às 18h**
> (notebooks, painel, jobs), mas o cronograma acima reserva a quinta à noite para ensaio.
> Na prática, o pipeline, o painel e os jobs precisam estar prontos e revisados até **quarta**.

## Estrutura

```
.
├── README.md                      # este arquivo
├── CLAUDE.md                      # contexto e regras para o Claude Code
├── docs/
│   ├── databricks-git-folder.md   # como sincronizar o repo com o workspace Databricks
│   └── convencoes-git.md          # branches, commits (Conventional Commits) e Pull Requests
├── analises/                      # análise exploratória — foco atual do grupo
│   ├── README.md
│   ├── analise_chamados_insights_primarios.ipynb   # notebook original (Juan), intocado
│   ├── _carga_dados.py            # carga compartilhada dos 8 CSVs
│   ├── clientes_yuri.py
│   ├── atendentes_motivos_cris.py
│   ├── chamados_hora_juan.py
│   ├── canais_richard.py
│   ├── custos_pesquisa_milton.py
│   ├── achados_qualidade_dados.md # inconsistências encontradas e tratamento sugerido
│   └── achados_hipoteses.md       # afirmações dos stakeholders a validar com dados
├── medalhao_rascunho/             # rascunho do pipeline bronze/silver/gold — fase futura, não rodar
└── data/raw/                      # CSVs originais (fora do git)
```

## Divisão da análise (todos ficam com `chamados`)

| Responsável | Bases |
|---|---|
| Yuri | clientes |
| Cris | base_atendentes, base_motivos |
| Juan | chamados_hora |
| Richard | canais |
| Milton | custos, pesquisa_satisfacao |
| Gabriel | entrou no grupo em 17/10; tabela ainda não atribuída |

## Requisitos do enunciado (checklist)

**Técnico (Diretor de Tecnologia)**
- [ ] Arquitetura medalhão (ingestão, tratamento, consolidação) com rastreabilidade
- [ ] Notebooks documentados no Databricks Free Edition
- [ ] Painel de indicadores consolidado
- [ ] Jobs automáticos encadeando os notebooks; pipeline **idempotente**

**Negócio (Comitê: Gerente Financeiro, Coordenadora de CS, Diretor de Tecnologia, Diretora de Marketing)**
- [ ] Leitura sobre a **confiabilidade dos dados**: inconsistências, tratamento e impacto nos indicadores
- [ ] Apresentação executiva com as principais conclusões
- [ ] Propostas de solução priorizadas (critério de priorização explícito), cada uma com ganho esperado;
      **ao menos duas com ganho quantificado** e premissas de cálculo
- [ ] Discussão de oportunidades e aprendizados

**Regras do enunciado**
- Tratamento e análise no Databricks Free Edition; sem integração nativa com Power BI
  (se usar, exportar tabelas em CSV).
- Bases de sistemas distintos: formatos de data, codificações e nomenclaturas diferentes.
- Divergência entre campos calculados e registros de horário: o grupo decide e documenta a fonte da verdade.

## Como começar

1. Clone o repositório e crie sua branch: `git switch -c feat/<seu-nome>-<assunto>`.
2. Copie os 8 CSVs para `data/raw/` (fora do git) — veja os nomes esperados em [`analises/_carga_dados.py`](analises/_carga_dados.py).
3. No Databricks, configure o widget `base_path` do notebook `_carga_dados` apontando para o seu Volume/Workspace.
4. Rode `%run ./_carga_dados` a partir do seu notebook (`clientes_yuri.py`, etc.) e continue a análise.
5. Para sincronizar com o workspace Databricks, veja [`docs/databricks-git-folder.md`](docs/databricks-git-folder.md).

## Fluxo de trabalho com Git

- **Nunca** trabalhe direto na `main` — abra Pull Request e peça revisão de outra pessoa do grupo.
  Exceção já usada: o primeiro push (reorganização inicial) foi direto na `main` porque o repositório
  estava vazio; isso não se repete.
- Antes de pushar: sem CSV, sem dado pessoal (CPF/nome/e-mail) em output de célula.
- Branches por pessoa/tarefa (`feat/`, `update/`, `fix/`, `docs/`, `chore/`) e commits em
  [Conventional Commits](https://www.conventionalcommits.org/pt-br/) — convenção completa, com exemplos,
  em [`docs/convencoes-git.md`](docs/convencoes-git.md).

## Convenções de dados

- Colunas em `snake_case` minúsculo.
- `clientes.csv` e `Chamados_Hora.CSV` são `cp1252`/`ISO-8859-1`; os demais `utf-8`.
- Problemas de qualidade viram **flags**, não linhas descartadas em silêncio.
- Dados pessoais (CPF/nome/e-mail) nunca aparecem em output de célula, doc ou commit.

## Time

Yuri · Cris · Juan · Richard · Milton · Gabriel
