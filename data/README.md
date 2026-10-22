# data/

Tudo que é **dado** fica aqui e **fora do git** (o `.gitignore` bloqueia tudo menos este README e o
`raw/.gitkeep`). As bases do case são confidenciais (propriedade intelectual da Visagio).

| Pasta | O que tem | Origem |
|---|---|---|
| `raw/` | Os 8 CSVs originais do case (`chamados`, `Chamados_Hora`, `clientes`, `custos`, `pesquisa_satisfacao`, `base_atendentes`, `base_motivos`, `canais`) | Material do case |
| `powerbi/` | `pacote_powerbi.zip`: saída do `medalhao/Gold_To_CSV.ipynb` (8 tabelas do modelo + 14 analíticas + manifesto), para importar no Power BI | Camada gold, exportada em 22/10/2026 |

## Por que o pacote do Power BI não vai para o git

`modelo/fato_atendimento.csv` tem uma linha por chamado (131.838 linhas, ~51 MB) com `id_cliente_hash`.
O hash é SHA-256 puro (decisão do grupo, ver `docs/tecnico/arquitetura-medalhao.md`), mas continua sendo
dado derivado das bases confidenciais. Compartilhe o zip pelo canal privado do grupo, não pelo repositório.
Os números agregados que importam para a apresentação estão em [`../resultados/`](../resultados/).

## Como usar o pacote

1. Descompacte `powerbi/pacote_powerbi.zip` numa pasta qualquer (ela traz `modelo/`, `analiticas/` e o
   manifesto `_manifesto.csv`/`_manifesto.json`).
2. O painel do repositório ([`../powerbi/`](../powerbi/)) lê só a pasta `analiticas/`: abra o `.pbip` no Power BI Desktop e aponte o parâmetro `PastaCSV` para ela
   (passo a passo em [`../docs/tecnico/painel-indicadores.md`](../docs/tecnico/painel-indicadores.md)). As 8 tabelas de `modelo/` (estrela, uma linha por chamado) ficam para análises mais detalhadas.
3. Descompacte sempre em pasta nova e vazia, fora do repositório.
