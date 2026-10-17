# Custos e pesquisa de satisfação — Milton

> Template a preencher. Conteúdo final destinado ao Notion compartilhado do grupo. KPIs e regras de
> limpeza compartilhadas em `CLAUDE.md` — reaproveite a lógica de `analises/analise_geral_corrigida.py`
> (dedup por `id_custo`, limpeza de `custo`, nota válida 1 a 5) pra não divergir dos outros `.md`.

## Problemas já conhecidos (confirmar ao rodar)

- `custo` em pelo menos 8 formatos de texto (`9,99`, `99.99`, `R$ 9,99`, `9.99reais`, negativos...).
- 781 linhas duplicadas (idênticas) por `id_custo`.
- ~544 custos ≤ 0 (negativos ou zero) — decidir com o grupo se entram na soma.
- ~1.550 chamados sem nenhum lançamento de custo.
- `nota_atendimento` só é válida de 1 a 5; ~6.899 notas inválidas no arquivo (antes de deduplicar).
- ~802 chamados com mais de uma pesquisa registrada.

## A preencher

### Custo total e custo mensal

_Custo total; custo médio por chamado mês a mês, ao lado do volume, pra separar "o gasto cresce porque o
volume cresce" de "o custo unitário sobe"._

| Mês | Custo total | Chamados | Custo médio/chamado |
|---|---|---|---|
| | | | |

### Custo por canal, motivo e nível do atendente

| Canal | Custo médio | Chamados |
|---|---|---|

| Motivo | Custo médio | Chamados |
|---|---|---|

| Nível do atendente | Custo médio | Chamados |
|---|---|---|

### CSAT por mês, canal, nível, motivo e resolução

_CSAT = % de notas 4 e 5 entre as válidas._

| Recorte | CSAT | Respostas |
|---|---|---|

### Taxa de resposta à pesquisa

_Geral, por mês e por canal — e o risco de viés de quem responde._

### Nota x tempo de espera, x TMA e x abandono

| Faixa | Nota média | CSAT | Respostas |
|---|---|---|---|

## Leitura

_O que isso mostra, em linguagem de apresentação._
