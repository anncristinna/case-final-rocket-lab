# Análises

| Arquivo | Conteúdo | Status |
|---|---|---|
| `analise_geral_corrigida.py` | notebook base (carga, limpeza, panorama geral) — **único, mudado só por PR combinado**; ver aviso no topo do arquivo | pronto |
| `panorama_geral.md` | números gerais da operação | preenchido |
| `por_canal.md` | volume, resolução, tempos, abandono, custo e CSAT por canal (Richard) | preenchido |
| `top_motivos.md` | os 10 motivos com mais chamados (Cris) | preenchido |
| `top_atendentes.md` | os 10 atendentes com mais chamados (Cris) | preenchido |
| `por_regiao.md` | volume, resolução e custo por região do cliente (Yuri) | preenchido |
| `custos_pesquisa.md` | custo mensal, por canal/motivo/nível, CSAT, taxa de resposta (Milton) | **template a preencher** |
| `tempos_abandono.md` | TME/TMA por mês/canal/hora, abandono, picos de demanda (Juan) | **template a preencher** |

Cada pessoa explora o seu tema no Databricks do jeito que preferir (copiando o notebook base, `%run`
nele, ou um notebook à parte — sem arquivo `.py` fixo pra cada um, pra não gerar conflito de merge editando
o mesmo código) e leva o resultado final para o `.md` correspondente. Reaproveite a limpeza do notebook
base (dedup por `id_chamado`/`id_custo`, regra de custo, nota válida 1-5, tempos pelos timestamps) — se
cada um tratar os dados de um jeito diferente, os números não batem entre os `.md`.

Todo `.md` é conteúdo pronto para colar no **Notion compartilhado do grupo** — números batidos localmente
contra os CSVs completos, reconfirmar rodando no Databricks antes de publicar. Detalhes técnicos da
correção (o que mudou em relação ao notebook inicial do Juan) ficam em
[`../docs/achados_analise_geral.md`](../docs/achados_analise_geral.md). KPIs compartilhados em `CLAUDE.md`.
