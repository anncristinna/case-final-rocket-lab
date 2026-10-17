# Tempos e abandono — Juan

> Template a preencher. Conteúdo final destinado ao Notion compartilhado do grupo. KPIs compartilhados em
> `CLAUDE.md`: TME e TMA sempre pelos timestamps de `chamados_hora`, **nunca** pelo campo truncado
> `tempo_atendimento` de `chamados`.

## Problemas já conhecidos (confirmar ao rodar)

- Timestamp no formato `dd/MM/yyyy às HH:mm:ss` — o conector "às" precisa ser removido por regex (a base
  já faz isso, ver `analise_geral_corrigida.py`).
- ~198 chamados com o ano da abertura errado (+1 ou +2 anos) — já corrigido na base, comparando com a
  finalização.
- 3.414 chamados (2,6%) sem hora de início de atendimento = abandono.

## A preencher

### TME e TMA por mês

| Mês | TME (s) | TMA (s) |
|---|---|---|

### TME e TMA por canal

| Canal | TME (s) | TMA (s) |
|---|---|---|

### TME e TMA por hora do dia

| Hora | TME (s) | TMA (s) | Chamados |
|---|---|---|---|

### Abandono por canal e por mês

| Recorte | % abandono |
|---|---|

### Picos de demanda

_Dia da semana, hora do dia — onde concentra volume._

## Leitura

_O que isso mostra, em linguagem de apresentação._
