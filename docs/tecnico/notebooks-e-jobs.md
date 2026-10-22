# Notebooks documentados, jobs e idempotência

Entregáveis técnicos: *notebooks documentados em Databricks (Free Edition)* e *jobs automáticos configurados entre os
notebooks, com pipeline idempotente*. Código em [`../../medalhao/`](../../medalhao/); arquivos de prova em
[`evidencias/`](evidencias/).

## Notebooks

Todos têm a mesma estrutura: cabeçalho com o grupo, célula "Sobre este notebook" (o que faz, regras, o que
grava), configuração no topo, uma seção por tabela, conferência com contagens e um **checklist antes de aplicar
uma mudança** no final.

| Notebook | Células | Documentação inline | Verificações que interrompem a execução |
|---|---|---|---|
| `Landing_To_Bronze.ipynb` | 8 | Encoding por arquivo, colunas de rastreio, caminho `file:` | — (imprime a contagem de cada tabela) |
| `Bronze_To_Silver.ipynb` | 33 | Uma seção por tabela com as regras de limpeza; checklist | Entrada vazia ou `id_chamado` ausente/duplicado (`chamados`, `chamados_hora`) |
| `Silver_To_Gold.ipynb` | 64 | Dicionário de colunas em [`guia_camada_gold_vcredit_texto.pdf`](../../medalhao/modelagem/guia_camada_gold_vcredit_texto.pdf); diagrama da estrela | Chave órfã ou duplicada; fato com número de linhas ≠ chamados da silver |
| `Gold_To_CSV.ipynb` | 10 | Formato dos CSVs, ajustes do modelo de consumo, manifesto | Tabela gold ausente; chave repetida; perda de chamado na junção; órfão fora do calendário; CSV com contagem diferente da tabela |

Nenhuma saída de célula exibe CPF, nome ou e-mail de cliente: são `print`s de contagem e checagens agregadas.

## Ordem e dependências

```
Landing_To_Bronze  →  Bronze_To_Silver  →  Silver_To_Gold  →  Gold_To_CSV
   (8 *_raw)            (9 *_silver +         (9 dim/fato +       (pacote_powerbi.zip
                         base_silver)          14 analíticas)      no Volume)
```

## Job de atualização (Databricks Workflows)

Job `visagio - job` (ID 218967712537699). Quatro tarefas de notebook em cadeia, cada uma com `run_if: ALL_SUCCESS`
(uma falha interrompe as seguintes). Configuração completa em [`evidencias/job-visagio.yaml`](evidencias/job-visagio.yaml).

| Item | Configuração real |
|---|---|
| Notebooks | `/Workspace/Shared/case-final-rocket-lab/medalhao/<Nome>` |
| Compute | Serverless, ambiente versão 6 (`Default`), `performance_target: PERFORMANCE_OPTIMIZED` |
| Agendamento | `20 0 0/12 * * ?` (Quartz: segundo, minuto, hora, dia, mês, dia da semana), ou seja, 00:00 e 12:00 em America/Sao_Paulo, `UNPAUSED` |
| Concorrência | `max_concurrent_runs: 1`, fila ativada |
| Retentativa, notificação, parâmetros | Nenhum. `anonimizar_atendente` fica no padrão `false` do widget do `Gold_To_CSV` |
| Duração típica | 7 a 8 min (maior observada: 17 min, em execução manual) |

**Execuções observadas** ([`evidencias/job-execucoes.png`](evidencias/job-execucoes.png)): 7, todas com sucesso, das quais 5
incluem a tarefa `Gold_To_CSV` (as duas primeiras ainda não tinham essa tarefa). A lista mostra 3 execuções com gatilho **"By scheduler"**
(duas em 21/10 e uma em 22/10), o que comprova o disparo automático. Elas batem com o histórico Delta de `chamados_hora_silver`: a
versão 5 (22/10 02:01 UTC, 21/10 23:01 em Brasília) e a versão 6 (03:01 UTC, 22/10 00:01 em Brasília) vieram de execuções agendadas;
a versão 7 (04:42 UTC, 22/10 01:42 em Brasília) foi disparada à mão com *Executar agora*.

**Histórico do agendamento** (informado pelo grupo). Durante os testes o Job rodou de hora em hora (cron `20 0 * * * ?`). Depois foi trocado
para 12 em 12 horas (`20 0 0/12 * * ?`), que é o definitivo; a execução agendada das 23h de 21/10 só se explica pela frequência antiga.

**Limites e riscos conhecidos**
- Sem retentativa nem notificação por e-mail: uma falha só aparece ao abrir o Job. Como cada notebook grava tabela por tabela, uma falha no meio deixa camadas em estados diferentes até a próxima execução.
- Cada execução regrava o `pacote_powerbi.zip` no Volume: **não baixe o zip entre 12:00 e 12:10** (nem entre 00:00 e 00:10).

## Idempotência: evidência

Critério do enunciado: reexecutar o pipeline sobre os mesmos dados dá o mesmo resultado, sem duplicar nem alterar registros.

**Mecanismos**

| Camada | Mecanismo |
|---|---|
| Bronze | `overwrite` por tabela; sempre lê a mesma pasta de origem |
| Silver | `overwrite` por tabela; dedup determinístico por `id_chamado` / `id_custo` / `id_cliente` |
| Gold | `overwrite` / `CREATE OR REPLACE TABLE`; a gold não usa hora de processamento; chaves de dimensão determinísticas |
| Exportação | Cada CSV regravado por inteiro com linhas em ordem fixa; `checksum_linhas` (soma de `xxhash64` por linha, independente da ordem) no manifesto |

**a) Manifestos da exportação entre duas execuções** ([`evidencias/comparacao_manifestos.csv`](evidencias/comparacao_manifestos.csv))

| Rodada | Pacote | Exportado (UTC) | Versão Delta da gold |
|---|---|---|---|
| 1 | `exp_20261022_012729` | 22/10 01:27 (21/10 22:27 em Brasília) | 2 |
| 2 | `exp_20261022_044507` | 22/10 04:45 | 7 |

As **22 tabelas** exportadas têm o mesmo número de linhas e o mesmo `checksum_linhas`. Exemplo: `fato_atendimento`, 131.838 linhas,
checksum `-4679046429632531319894`. A rodada 1 foi uma exportação avulsa do `Gold_To_CSV` (25 minutos depois da gravação da gold), e a gold
foi regravada 5 vezes até a rodada 2 (versão Delta 2 → 7) sem mudar de conteúdo.

**b) Foto de todas as tabelas `_raw`, `_silver` e `_gold`** antes e depois de uma nova execução (linhas e checksum, sem `_ingestion_ts`), em
[`evidencias/Validacao_Idempotencia.ipynb`](evidencias/Validacao_Idempotencia.ipynb). Só `canais_silver` e `chamados_hora_silver` divergiram,
com o mesmo número de linhas.

**c) Causa e prova.** Cada uma dessas duas tem uma coluna de linhagem que muda por definição a cada execução: `canais_silver._treatment_ts`
(`current_timestamp()` do tratamento) e `chamados_hora_silver.versao_bronze` (versão Delta da bronze, que sobe a cada ingestão). Comparando as
versões Delta 6 e 7 sem essas colunas, `EXCEPT ALL` nos dois sentidos deu **0 diferenças** nas duas tabelas.

**Conclusão.** O conteúdo de negócio é idêntico entre execuções. Só mudam as colunas de linhagem `_ingestion_ts` (bronze), `_treatment_ts`
(`canais_silver`) e `versao_bronze` (`chamados_hora_silver`), que ficam fora da comparação de propósito.

**Limites da evidência**
- A prova cobre reexecução sobre os **mesmos CSVs de entrada**. Não testa mudança de entrada nem carga incremental (o enunciado não exige).
- A foto do item (b) lista 47 tabelas `_raw/_silver/_gold`. O Job escreve 41; as outras 6 (`canal_*_gold`) não têm notebook em `medalhao/`
  e, como o Job não as regrava, comparam iguais sem passar pelo pipeline. A origem delas ainda precisa ser documentada ou elas devem ser removidas.

**Escalabilidade.** Todas as tabelas são regravadas por inteiro (`overwrite`), adequado ao volume atual (cerca de 130 mil chamados). Para
volumes maiores, o caminho é carga incremental com `MERGE` e particionamento por data.
