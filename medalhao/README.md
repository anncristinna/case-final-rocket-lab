# medalhao/

Código da arquitetura medalhão (Landing → Bronze → Silver → Gold → CSV para o Power BI). É a mesma pasta
`medalhao/` do workspace Databricks do grupo (`Shared/case-final-rocket-lab/medalhao/`); os nomes dos
arquivos são idênticos aos de lá. Documentação por camada: [`../docs/tecnico/`](../docs/tecnico/).

## Ordem de execução

| # | Notebook | Lê | Grava (`dados_vcredit.default.`) |
|---|---|---|---|
| 1 | `Landing_To_Bronze.ipynb` | 8 CSVs em `Shared/case-final-rocket-lab/dados` (`file:` + caminho do Workspace) | 8 tabelas `<tabela>_raw`, tudo `string` + colunas de rastreio |
| 2 | `Bronze_To_Silver.ipynb` | `*_raw` | 9 tabelas `*_silver` + `base_silver` (junção final) |
| 3 | `Silver_To_Gold.ipynb` | `*_silver` | 7 dimensões, `fato_atendimento_gold`, `qualidade_chamado_gold` e 14 tabelas analíticas (`*_gold`) |
| 4 | `Gold_To_CSV.ipynb` | `*_gold` | Volume `dados_vcredit.default.exportacao_powerbi`: `modelo/`, `analiticas/` e manifesto |

Cada notebook depende do anterior ter rodado. Todos são **idempotentes** (`overwrite` / `CREATE OR REPLACE`):
rodar de novo sobre a mesma entrada dá o mesmo resultado.

## Modelagem

- [`modelagem/modelagem-silver.png`](modelagem/modelagem-silver.png): diagrama ER da silver.
- [`modelagem/modelagem-gold.png`](modelagem/modelagem-gold.png): esquema estrela da gold.
- [`modelagem/guia_camada_gold_vcredit_texto.pdf`](modelagem/guia_camada_gold_vcredit_texto.pdf): guia célula a célula do
  `Silver_To_Gold.ipynb` (colunas, grão de cada tabela, cuidados de interpretação).

## Regras

- Muda só por PR revisado; sem cópia por pessoa. Testou no Databricks? Traga a versão final de volta para cá.
- Os `.ipynb` **sem saídas de tabela** (`Landing_To_Bronze` e `Bronze_To_Silver` foram limpos de propósito: as
  saídas traziam amostras de `clientes`). `Silver_To_Gold` e `Gold_To_CSV` mantêm só `print`s de contagem e
  verificações agregadas.
- Nunca exibir `id_cliente` (CPF), nome ou e-mail de `clientes` em saída de célula. `nome_atendente` não é
  dado restrito. A gold só tem `id_cliente_hash`.
- Validar sintaxe/JSON antes de comitar:
  `python -c "import json; json.load(open('medalhao/<arquivo>.ipynb', encoding='utf-8'))"`.
