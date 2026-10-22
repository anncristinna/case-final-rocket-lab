# Case Final Rocket Lab — V-Credit

Transformação digital do atendimento da **V-Credit** (case Visagio / Rocket Lab 2026). A partir da análise dos dados
de atendimento (jan/2025 a jul/2026, 131.838 chamados únicos), o grupo entrega uma arquitetura medalhão no Databricks
e recomendações priorizadas e justificadas com dados para o Comitê Executivo.

> ⚠️ O enunciado e as bases do case são confidenciais (propriedade intelectual da Visagio).
> **Nenhum CSV, `.zip` ou `.pbix` com dados vai para o git.** O `.gitignore` bloqueia, mas confira antes de cada push.

## Entregas e prazos

| Entregável | Para quem | Prazo | Onde está |
|---|---|---|---|
| **Técnico**: arquitetura medalhão, notebooks documentados, painel de indicadores, jobs idempotentes | Diretor de Tecnologia | **Quinta 22/10, 18h** | [`medalhao/`](medalhao/) + [`docs/tecnico/`](docs/tecnico/) |
| **Analítico e de negócio**: confiabilidade dos dados, apresentação executiva, propostas priorizadas, oportunidades e aprendizados | Comitê Executivo | **Sexta 23/10** (20 min + 15 min de perguntas) | [`resultados/`](resultados/) + [`docs/analitico/`](docs/analitico/) |

O mapa completo "item do enunciado → arquivo" está em [`docs/README.md`](docs/README.md).

## O resultado em poucas linhas

- O volume de chamados mais que dobrou (+120%) em 18 meses; o CSAT caiu de 86% para 57% e a espera do Nível 2 foi de 5 para 22 min.
- Custo total de **R$ 1,45 mi**, puxado por volume (custo por chamado estável em ~R$ 11); 43% dos chamados no humano = 94% do custo.
- Recomendações: resolver na primeira interação os 5 motivos críticos (**R$ 258 mil/ano**, premissa de 30%), deflexão dos motivos simples
  (**R$ 31 mil/ano**, premissa de 20%), capacidade e escala do Nível 2, e governança de dados. Detalhes em
  [`docs/analitico/propostas-e-priorizacao.md`](docs/analitico/propostas-e-priorizacao.md).

## Estrutura

```
.
├── README.md
├── CLAUDE.md                        contexto e regras para o Claude Code
├── medalhao/                        código da arquitetura medalhão (= pasta medalhao/ do Databricks)
│   ├── README.md                    ordem de execução, tabelas lidas e gravadas
│   ├── Landing_To_Bronze.ipynb      8 CSVs → *_raw
│   ├── Bronze_To_Silver.ipynb       limpeza e junção → *_silver + base_silver
│   ├── Silver_To_Gold.ipynb         modelo em estrela + 14 tabelas analíticas → *_gold
│   ├── Gold_To_CSV.ipynb            exporta a gold para o Power BI (Volume)
│   └── modelagem/                   diagramas da silver e da gold; guia da gold (PDF)
├── resultados/                      números da análise, um arquivo por frente (01 a 07)
├── docs/
│   ├── README.md                    mapa: item do enunciado → arquivo
│   ├── tecnico/                     arquitetura, notebooks e jobs, painel, histórico de revisões
│   ├── analitico/                   confiabilidade, propostas, oportunidades, roteiro da apresentação
│   ├── convencoes-git.md            branches, commits (Conventional Commits) e Pull Requests
│   └── databricks-estrutura.md      pastas, permissões e troubleshooting no workspace
└── data/                            fora do git (só o README): raw/ (8 CSVs) e powerbi/ (pacote do painel)
```

## Grupo

Yuri, Cris, Juan, Richard, Milton, Gabriel, Anna.

## Como começar

1. Clone o repositório e crie sua branch: `git switch -c feat/<seu-nome>-<assunto>` (convenção em
   [`docs/convencoes-git.md`](docs/convencoes-git.md)).
2. Para ler o que foi feito: [`docs/README.md`](docs/README.md), depois [`resultados/README.md`](resultados/README.md).
3. Para rodar: importe os 4 notebooks de `medalhao/` em `Shared/case-final-rocket-lab/medalhao/` no Databricks e execute na ordem
   (passo a passo em [`docs/databricks-estrutura.md`](docs/databricks-estrutura.md)). Os CSVs originais ficam em `data/raw/` (local, fora do git).
4. Para o painel: descompacte `data/powerbi/pacote_powerbi.zip` e siga
   [`docs/tecnico/painel-indicadores.md`](docs/tecnico/painel-indicadores.md).

## Regras rápidas

- Branch + PR, revisão de pelo menos 1 pessoa (ver `docs/convencoes-git.md`). Os notebooks de `medalhao/` mudam só por PR revisado, sem cópia por pessoa.
- Sem CSV e sem dado pessoal (CPF/nome/e-mail de **clientes**) em output de célula, doc ou commit. A gold só tem `id_cliente_hash`.
- Tempos de atendimento sempre pelos timestamps de `chamados_hora`, nunca pelo `tempo_atendimento` de `chamados` (truncado).
- Sempre remover duplicatas de `chamados` e `custos` antes de agregar. Regras completas em `CLAUDE.md`.
