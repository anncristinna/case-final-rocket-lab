# Guia: estrutura do projeto no Databricks

Como o case V-Credit está organizado no workspace do grupo (Databricks Free Edition: só serverless, SQL warehouse
2X-Small, cota diária de uso). Os nomes de menus podem variar um pouco na interface.

O código oficial fica no GitHub (`main`, pasta [`../medalhao/`](../medalhao/)). O Databricks é o ambiente de execução: o que roda
aqui deve vir de um arquivo já revisado no repositório. **Sem Git folder** por enquanto: o fluxo é editar localmente →
*Workspace → Import* → rodar e testar → trazer a versão final de volta ao repositório.

## 1. Estrutura real

```
Workspace/Shared/case-final-rocket-lab/
├── dados/        os 8 CSVs originais (Workspace; ver 2 sobre o esquema file:)
├── medalhao/     Landing_To_Bronze, Bronze_To_Silver, Silver_To_Gold, Gold_To_CSV  (= repositório: medalhao/)
└── resultados/   prints e exportações de resultados                              (= repositório: resultados/)

Unity Catalog:  catálogo dados_vcredit › schema default
├── <tabela>_raw      bronze (8)
├── <tabela>_silver   silver (9) + base_silver
├── <tabela>_gold     gold: 7 dimensões, fato, qualidade e 14 analíticas
└── Volume exportacao_powerbi   saída de Gold_To_CSV (pacote_powerbi.zip)
```

Mantenha o nome do arquivo igual ao do repositório, para não perder o rastro de qual versão está onde.

## 2. Como os dados são lidos

`spark.read` em pasta do Workspace só funciona em leitura distribuída com o **esquema `file:` explícito** no caminho
(`file:/Workspace/Shared/case-final-rocket-lab/dados/<arquivo>.csv`); sem ele dá erro de permissão
(`INSUFFICIENT_PERMISSIONS ... SELECT on any file`). O `Landing_To_Bronze.ipynb` usa uma constante `BASE_PATH` fixa. Se
os CSVs migrarem para um Volume, troque a constante e tire o prefixo `file:`.

Encoding: `clientes.csv` e `Chamados_Hora.csv` são `ISO-8859-1` (cp1252); os demais, `UTF-8`. O arquivo original
era `Chamados_Hora.CSV`; o grupo padronizou para `.csv`, e a tabela de destino é sempre minúscula (`chamados_hora_raw`).

## 3. Passo a passo (montar do zero)

1. **Pastas**: em *Workspace > Shared*, crie `case-final-rocket-lab` e, dentro dela, `dados`, `medalhao` e `resultados`.
2. **Notebooks**: em *Import* (menu da pasta), importe os 4 `.ipynb` de `medalhao/` do repositório.
3. **Dados**: suba os 8 CSVs em `dados/` com os nomes originais (em minúsculo).
4. **Destino**: o catálogo `dados_vcredit` e o schema `default` já existem; o `Gold_To_CSV` cria o Volume
   `exportacao_powerbi` (`CREATE VOLUME IF NOT EXISTS`).
5. **Acesso**: compartilhe `Shared/case-final-rocket-lab` com **Can Edit** (ou **Can Run**). Nas tabelas/Volume, conceda
   `USE SCHEMA`, `SELECT` e `READ VOLUME` a quem precisar. Os dados são confidenciais: não compartilhe fora do grupo.
6. **Executar na ordem** (ou pelo Job, ver [`tecnico/notebooks-e-jobs.md`](tecnico/notebooks-e-jobs.md)):
   `Landing_To_Bronze` → `Bronze_To_Silver` → `Silver_To_Gold` → `Gold_To_CSV`.
7. **Baixar o pacote**: *Catálogo → `dados_vcredit` → `default` → Volumes → `exportacao_powerbi` → `pacote_powerbi.zip` → Baixar*.
   Guarde em `data/powerbi/` (fora do git).

## 4. Conferência dos números

Depois de rodar as camadas, confira:

| Tabela | Linhas |
|---|---|
| bronze `chamados_raw` / silver `chamados_silver` | 134.474 / 131.838 (2.636 duplicatas idênticas removidas) |
| `chamados_hora` | 131.838 |
| `clientes` | 47.705 |
| `custos` bronze | 131.069 (781 duplicatas removidas na silver) |
| `pesquisa_satisfacao` | 81.021 |
| `base_atendentes` / `base_motivos` / `canais` | 25 / 14 / 4 |
| gold: `fato_atendimento_gold`, `qualidade_chamado_gold` | 131.838 cada |
| gold: dimensões | calendário 731, hora 25, faixa de espera 6, canal 5, motivo 15, atendente 28, cliente 47.705 |
| `visao_geral_gold` | custo total R$ 1.450.617,85; CSAT 71,57%; TME 3,60 min; TMA 11,03 min; resolução 50,88%; abandono 2,59% |

Se algo divergir, **não ajuste o código para forçar o número**: anote a diferença e investigue (encoding, formato dos
timestamps, modo ANSI do serverless).

## 5. Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `INSUFFICIENT_PERMISSIONS ... SELECT on any file` | `spark.read` numa pasta do Workspace sem `file:` | Usar `file:/Workspace/...` no caminho |
| `Path does not exist` | Caminho com texto de exemplo ou nome errado | Copiar o caminho pelo Catalog / navegador de arquivos |
| Erro de permissão em tabela ou Volume | Falta `USE SCHEMA`, `SELECT` ou `READ VOLUME` | Pedir a quem criou |
| Acentos quebrados | Encoding errado (`clientes` e `Chamados_Hora` são ISO-8859-1) | Conferir o dicionário `ARQUIVOS` do `Landing_To_Bronze` |
| `Tabelas Gold ausentes ... Rode o Silver_To_Gold antes` | `Gold_To_CSV` rodou antes da gold | Respeitar a ordem das 4 etapas |
| Cota diária esgotada | Free Edition | Evitar rodar o pipeline inteiro várias vezes sem necessidade |

## 6. Regras de segurança e sincronia

- Nunca suba CSV, `.env` ou token para o GitHub. Nunca imprima `id_cliente` (CPF), nome ou e-mail de `clientes` em célula, doc ou print.
- Evite `collect()`/`toPandas()` em tabelas grandes (~130 mil linhas nas maiores); agregue no Spark antes de `display()`.
- Não edite no Databricks um arquivo que também é editado localmente. Mudou algo aqui? Leve ao GitHub por PR; mudou no repositório? Reimporte a versão revisada.
- Quando terminar de testar uma mudança, traga a versão final de volta para o repositório.
- Remova a pasta `dados` do Workspace quando o projeto terminar (os arquivos têm CPF, nome e e-mail).

## 7. Checklist

- [ ] Pastas `dados`, `medalhao` e `resultados` em `Shared/case-final-rocket-lab`
- [ ] 4 notebooks importados de `medalhao/`
- [ ] 8 CSVs em `dados/` com os nomes originais
- [ ] Acesso concedido ao grupo (pasta, tabelas, Volume)
- [ ] Pipeline rodado na ordem; contagens conferidas (seção 4)
- [ ] `pacote_powerbi.zip` baixado para `data/powerbi/`
