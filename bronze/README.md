# Bronze — Landing to Bronze

Início da camada bronze de verdade (não é mais rascunho — ver `medalhao_rascunho/` para o desenho
original, mantido só como referência histórica). Passo a passo completo de como montar isso no
workspace do grupo (pastas, Volume, permissões, troubleshooting) em `docs/databricks-estrutura.md`.

> No workspace do grupo, este notebook vive em `Shared/case-final-rocket-lab/medalhao/Landing_To_Bronze`
> (a estrutura real diverge um pouco do que o guia planejava — `medalhao/` em vez de `00_base/`).

## `Landing_To_Bronze.ipynb`

Notebook **único** — ingere as 8 tabelas num loop (mesma lógica pra todas: ler fiel à origem, escrever
com `overwrite`). Não tem lógica diferente por tabela, então, diferente de `analises/`, não faz sentido
uma cópia por pessoa aqui. **Mudar só por PR revisado**, igual ao notebook base em `analises/`.

Leitura 100% `spark.read` (padrão Databricks — segue o estilo que um colega já estava usando pra
`base_motivos`, com `_source_file`/`_source_file_mod_ts` vindo da coluna oculta `_metadata` em vez de
um valor fixo). **Exige um Volume do Unity Catalog** em `base_path`: o Spark serverless não lê CSV de
pasta do Workspace de forma distribuída. (Antes deste notebook lia com `pandas`, que funcionava em
qualquer caminho; voltamos pro `spark.read` puro a pedido do grupo, agora que os CSVs estão num Volume
de verdade.)

⚠️ **Catálogo/schema/sufixo de destino** (`CATALOGO = "dados_vcredit"`, `SCHEMA_BRONZE = "default"`,
`SUFIXO = "_raw"`) seguem o exemplo que já estava em uso para uma tabela
(`dados_vcredit.default.base_motivos_raw`) — confirmar com o grupo que é esse o padrão combinado pras
8 tabelas antes de rodar em produção; é só mudar essas 3 constantes na célula de configuração se
decidirem outro catálogo/schema.

Validado localmente (fora do Databricks, simulando o Volume com os CSVs de `data/raw/`): as 8
contagens batem exatamente com o esperado, e `_metadata.file_path`/`_metadata.file_modification_time`
resolvem certinho (é recurso padrão do Spark, não específico do Databricks). Nuance: sem o `pandas`,
célula vazia em `nota_atendimento` vira `NULL` de verdade (comportamento padrão do `spark.read` sem
`nullValue`), então ela e a string literal `"NULL"` aparecem iguais no `display()` — continuam sendo
valores diferentes por dentro, e isso não muda nada no tratamento (os dois já eram descartados como
inválidos). A linha `CREATE SCHEMA IF NOT EXISTS` não dá pra testar localmente no Windows (precisa de
`winutils.exe`) — é uma chamada Spark padrão, risco baixo, mas confirme que rodou sem erro na primeira
execução no Databricks.

Pra rodar: no Databricks, preencha o widget `base_path` com o caminho do Volume — copie pelo **Catalog**
pra não errar o nome do catálogo/schema (`/Volumes/<catalogo>/<schema>/<volume>`) — e rode todas as
células.

## Regras da bronze (resumo — completo em `CLAUDE.md`)

- Tudo como `string` (`inferSchema=false`), nenhuma correção de conteúdo aqui — isso é papel da silver,
  fase futura.
- `_source_file`, `_source_file_mod_ts` e `_ingestion_ts` em toda tabela, pra rastrear quando e de onde
  veio.
- `overwrite` — idempotente, rodar de novo dá o mesmo resultado.
- Nenhum `display()`/`show()` de linha inteira em tabelas com dado pessoal (`clientes`).
