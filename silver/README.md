# Silver — um notebook por responsável + um de junção

Camada silver modular: cada responsável limpa a(s) sua(s) tabela(s) lendo da bronze
(`dados_vcredit.default.<tabela>_raw`) e escreve o resultado numa tabela silver própria
(`dados_vcredit.default.<tabela>_silver`) — sem tocar no código de ninguém, sem conflito de merge.
No final, **um notebook de junção** (`Silver_Consolidado.ipynb`) lê as 5 tabelas silver + a `chamados`
(que ninguém é "dono" sozinho) e junta tudo numa `base_silver`, uma linha por chamado.

Cada notebook vem como **template**: já tem o cabeçalho, a explicação da tabela e os pontos que
precisam ser respeitados na limpeza, mas a célula de código em si fica vazia (só um `TODO`) — cada
responsável preenche a lógica do jeito que preferir, com base na própria análise.

## Notebooks

| Arquivo | Responsável | Tabela(s) bronze → silver |
|---|---|---|
| `Silver_Clientes.ipynb` | Yuri | `clientes_raw` → `clientes_silver` |
| `Silver_Atendentes_Motivos.ipynb` | Cris | `base_atendentes_raw`/`base_motivos_raw` → `base_atendentes_silver`/`base_motivos_silver` |
| `Silver_Chamados_Hora.ipynb` | Juan | `chamados_hora_raw` → `chamados_hora_silver` |
| `Silver_Canais.ipynb` | Richard | `canais_raw` → `canais_silver` |
| `Silver_Custos_Pesquisa.ipynb` | Milton | `custos_raw`/`pesquisa_satisfacao_raw` → `custos_silver`/`pesquisa_satisfacao_silver` |
| `Silver_Consolidado.ipynb` | — (roda por último) | `chamados_raw` + as 5 tabelas silver acima → `base_silver` |

Cada um dos 5 primeiros é **independente** — não precisa esperar os outros, só a bronze já existir.
O `Silver_Consolidado.ipynb` precisa rodar **depois** dos 5, porque só lê o que eles já escreveram —
não repete limpeza de ninguém.

## O que já vem pronto em cada notebook

- Cabeçalho identificando a tabela e o responsável.
- Explicação da tabela e os pontos de atenção na limpeza (ex.: `idade` inválida em `clientes`,
  truncamento em `chamados.tempo_atendimento`, regra de formato de `custo`, nota válida de 1 a 5).
- Constantes de origem/destino (nome da tabela bronze e da tabela silver) — assim todo mundo escreve
  no mesmo padrão de nome, sem precisar combinar isso de novo.
- Checklist no final.

O que falta preencher é só a lógica de limpeza em si — a célula de código fica com um `TODO`.

## Antes de usar no Databricks

1. Rodar a bronze primeiro — os 8 `*_raw` precisam existir.
2. Cada responsável preenche e roda o seu notebook (pode ser em qualquer ordem entre si).
3. Preencher e rodar `Silver_Consolidado.ipynb` por último, depois que as 5 tabelas silver já
   existirem.
