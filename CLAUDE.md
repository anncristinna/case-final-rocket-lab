# CLAUDE.md — Case V-Credit (Rocket Lab 2026)

## Contexto
Grupo de 6 estudantes (Yuri, Cris, Juan, Richard, Milton, Gabriel) resolvendo o case da V-Credit (Visagio).
Objetivo final: pipeline medalhão no Databricks Free Edition + análise do atendimento + recomendações
priorizadas e justificadas com dados (pelo menos 2 com ganho quantificado e premissas explícitas).
**Fase atual (simplificada):** análise exploratória em `analises/`, cada pessoa na sua tabela — a medalhão
fica para depois (`medalhao_rascunho/`, não rodar agora).
Comunicação em **português do Brasil**.

## Prazos
- Quinta 22/10 às 18h: entregáveis técnicos (medalhão, notebooks documentados, painel, jobs idempotentes).
- Sexta 23/10: apresentação (20 min + 15 min de perguntas).

## Estrutura
- `analises/`: fase atual do grupo — análise exploratória por tabela, formato fonte Databricks
  (`# Databricks notebook source`, `# COMMAND ----------`). `_carga_dados.py` é a carga compartilhada;
  cada responsável tem seu notebook (`clientes_yuri.py`, `atendentes_motivos_cris.py`, `chamados_hora_juan.py`,
  `canais_richard.py`, `custos_pesquisa_milton.py`) e os achados ficam em `achados_qualidade_dados.md` e
  `achados_hipoteses.md`.
- `medalhao_rascunho/`: rascunho do pipeline bronze/silver/gold, material para uma fase futura — não é a
  etapa atual, não rodar sem reconfirmar antes.
- `docs/databricks-git-folder.md`: como sincronizar o repositório com o workspace Databricks (Git folder).
- `data/raw/`: CSVs locais (fora do git).

## Regras
- **Nunca** commitar CSV ou arquivo que contenha token/segredo. Nunca ler/exibir arquivos de segredo (`.env` e afins).
- Dados têm CPF, nome e e-mail: não imprimir linhas de `clientes` em outputs, docs ou commits. Gold usa `cliente_hash`.
- Bronze fiel à origem; correções só na silver; anomalias viram flag/coluna `dq_*`, não descarte silencioso.
- Toda transformação deve ser idempotente (`overwrite`/`MERGE`), sem `append` cego.
- Ambiente Databricks **Free Edition**: só serverless, SQL warehouse 2X-Small, sem Scala/R, cota diária de uso.
  Prefira consultas leves e evite `collect()`/`toPandas()` em tabelas grandes (~130 mil linhas nas maiores).
- Encoding: `clientes.csv` e `Chamados_Hora.CSV` são `cp1252`; os demais `utf-8`.
- **Tempos**: a fonte da verdade são os timestamps de `chamados_hora`. O campo `tempo_atendimento` de `chamados`
  está truncado para durações ≥ 1.000 s (subestima o TMA humano ~4,7×); nunca use o campo original em KPIs.
- Decisões de dados ficam registradas em `analises/achados_qualidade_dados.md`.
- Para testar localmente use PySpark (Spark 4.x) com os CSVs de `data/raw/`; o resultado deve bater com os docs.

## Fluxo de trabalho esperado do Claude
1. Antes de alterar um notebook de `analises/`, leia `analises/achados_qualidade_dados.md` e `analises/achados_hipoteses.md`.
2. Alterou regra de limpeza? Atualize `analises/achados_qualidade_dados.md` no mesmo commit.
3. Valide sintaxe (`python -m py_compile analises/*.py medalhao_rascunho/*.py`) antes de commitar.
4. Commits pequenos, mensagem em português no imperativo, em branch própria (nunca direto na `main`).
5. Números que vão para slides devem sair de consulta reproduzível e citar a tabela de origem.

## Definições de KPI (confirmar com o grupo; mudar aqui se mudar)
- **Taxa de resolução** = chamados `resolvido = true` / chamados totais.
- **TME** (tempo médio de espera) = abertura → início do atendimento; **TMA** = início → finalização.
- **CSAT** = % de notas 4 e 5 entre as respondidas (a Marketing citou 85% no início de 2025).
- **Abandono** = chamado sem hora de início de atendimento (espera registrada, sem atendimento).
- **Custo por chamado** = soma de `custos.custo` por `id_chamado`.
