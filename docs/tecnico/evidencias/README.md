# Evidências do pipeline

Provas de que o pipeline roda como Job e é idempotente. A leitura e a conclusão estão em
[`../notebooks-e-jobs.md`](../notebooks-e-jobs.md); aqui ficam só os arquivos de origem.

| Arquivo | O que é |
|---|---|
| `job-visagio.yaml` | Configuração real do Job `visagio - job` no Databricks Workflows (sem e-mail do criador) |
| `job-execucoes.png` | Print da lista de execuções do Job (7 execuções; 3 com gatilho "By scheduler"), cortado para não mostrar o e-mail do criador |
| `manifesto_rodada1_exp_20261022_012729.{csv,json}` | Manifesto original da exportação da rodada 1 (22/10 01:27 UTC, versão Delta da gold = 2), igual ao `_manifesto` do `pacote_powerbi.zip` |
| `manifesto_rodada2_exp_20261022_044507.{csv,json}` | Manifesto original da exportação da rodada 2 (22/10 04:45 UTC, versão Delta da gold = 7) |
| `comparacao_manifestos.csv` | Comparação original, feita pelo grupo, de linhas e `checksum_linhas` das 22 tabelas exportadas entre as duas rodadas (22 de 22 iguais) |
| `painel/painel-atendimento-v-credit.pdf` | PDF das 7 páginas do painel Power BI (22/10/2026), exportado do Desktop; sem metadados de autor. Mostra nomes de atendentes (mantidos por decisão do grupo; base fictícia) |
| `Validacao_Idempotencia.ipynb` | Foto de todas as tabelas `*_raw`, `*_silver` e `*_gold` (linhas e checksum `xxhash64`) e comparação linha a linha entre versões Delta. Versão limpa: sem `userName` nem `userId` |

## Cuidados

- Os manifestos só têm nome de tabela, contagens, checksums e horários; **não há dado pessoal**. Por isso o `.gitignore`
  abre uma exceção para os `.csv` desta pasta (`!docs/tecnico/evidencias/**/*.csv`).
- Antes de versionar qualquer print ou saída nova, confira se não mostra e-mail de usuário, CPF, nome ou e-mail de cliente.
- Todos os arquivos de manifesto e de comparação são os **originais** enviados pelo grupo, sem edição (os `.csv` mantêm o fim de linha CRLF de origem).
