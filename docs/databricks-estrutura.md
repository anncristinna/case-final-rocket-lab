# Guia: estrutura do projeto no Databricks

Como organizar pastas, notebooks e dados do case V-Credit no workspace do grupo (Databricks Free Edition).
Os nomes de menus podem variar um pouco na interface; se algo não estiver onde está escrito, procure o
equivalente. **Estrutura real do grupo em 19/10** (capturas de tela), que diverge um pouco do planejado
abaixo — ver nota em `bronze/README.md`.

## 1. Objetivo

- Tirar o projeto da pasta pessoal de uma pessoa e colocá-lo numa pasta compartilhada.
- Guardar os 8 CSVs num **Volume do Unity Catalog**, porque o Spark serverless **não lê CSV de pasta do
  Workspace** de forma distribuída (erro `INSUFFICIENT_PERMISSIONS ... SELECT on any file`).
- Deixar claro para todos qual é o `base_path` e quem pode acessar os dados.

O código oficial continua no GitHub (`main`). O Databricks é o ambiente de execução: o que for rodado
aqui deve vir de um arquivo já revisado no repositório.

## 2. Estrutura alvo (planejada)

```
Workspace/Shared/case-final-rocket-lab/
├── 00_base/        notebook base (carga + limpeza); só muda por PR combinado
├── analises/        um notebook por pessoa/tema (ex.: milton_custos_pesquisa)
└── resultados/      opcional: prints e exports de resultados

Catalog > workspace > <schema> > Volume: dados_vcredit
└── os 8 CSVs, com os nomes originais
```

**Estrutura real (19/10):** `analises/` tem `analise_geral_corrigida` e `analise_geral_primaria`
(no lugar de `00_base/`); existe uma pasta `medalhao/` à parte com `Landing_To_Bronze`; `dados/` ainda
tem os 8 CSVs soltos no Workspace (a remover depois de confirmar o Volume, ver 3.4.4).

## 3. Passo a passo

### 3.1 Criar as pastas
1. No navegador de arquivos, abra **Workspace > Shared**.
2. **Create > Folder**: `case-final-rocket-lab`.
3. Dentro dela, crie as pastas que o grupo for usar (ver estrutura real acima).

### 3.2 Colocar os notebooks
- **Mover** o notebook existente: menu de três pontos do arquivo > **Move**, ou arrastar; ou
- **Importar** um `.py`/`.ipynb` baixado do repositório: menu da pasta > **Import**. Um `.py` com o
  cabeçalho `# Databricks notebook source` vira notebook.
- O notebook base vai em `analises/` (ou `00_base/`, conforme o grupo decidir). Cada análise individual
  vai em `analises`, com o nome `<nome>_<tema>`.

### 3.3 Criar o Volume
1. Menu lateral **Catalog**, catálogo `workspace`, escolha um schema (pode ser `default`).
2. **Create > Volume**, tipo **managed**, nome `dados_vcredit`.
3. Anote o caminho completo: `/Volumes/workspace/<schema>/dados_vcredit` (copie pelo Catalog pra não
   errar o nome do schema).

### 3.4 Subir os CSVs
1. Abra o Volume e use **Upload to this volume**.
2. Suba os 8 arquivos com os nomes originais (incluindo `Chamados_Hora.CSV`, com extensão em
   maiúsculas): chamados, Chamados_Hora, clientes, custos, pesquisa_satisfacao, base_atendentes,
   base_motivos e canais.
3. Alternativa dentro do Databricks (pode não funcionar no serverless; se falhar, use o upload):
   `dbutils.fs.cp("file:/Workspace/Shared/case-final-rocket-lab/dados/<arquivo>.csv", "/Volumes/workspace/<schema>/dados_vcredit/<arquivo>.csv")`
4. Depois de confirmar que os 8 estão no Volume, **remova a pasta `dados` antiga do Workspace**. Os
   arquivos têm CPF, nome e e-mail; não mantenha cópia em pasta pessoal nem na pasta compartilhada.

### 3.5 Dar acesso ao grupo
- Pasta `Shared/case-final-rocket-lab`: **Share** e dar aos colegas pelo menos **Can Edit** (ou
  **Can Run**, se for só rodar).
- Volume: conceder **READ VOLUME**; no schema, **USE SCHEMA**. Sem isso, quem rodar recebe erro de
  permissão.
- Os dados são confidenciais: não compartilhe o Volume fora do grupo.

### 3.6 Informar o caminho
- Anote o `base_path` no README do repositório e no cabeçalho do notebook base.
- Avise o grupo no WhatsApp.

## 4. Como rodar um notebook

1. Selecione o compute **Serverless**.
2. Se o widget `base_path` não aparecer na barra do notebook, crie-o numa célula **antes** do `%run`
   (essa célula é só da sua sessão e não vai para o Git):
   ```python
   dbutils.widgets.text("base_path", "")
   ```
3. Preencha o `base_path` com `/Volumes/workspace/<schema>/dados_vcredit` e rode.
4. Os notebooks `.py` **não guardam a saída das células**. Copie os números para o `.md` do seu tema na
   hora.
5. A cota diária da Free Edition é limitada: evite rodar o notebook inteiro várias vezes sem necessidade.

## 5. Conferência dos números

Rode o notebook base uma vez com o Volume e compare:

| Base | Linhas no arquivo | Observação |
|---|---|---|
| chamados | 134.474 | 131.838 após remover duplicatas idênticas |
| chamados_hora | 131.838 | |
| clientes | 47.705 | |
| custos | 131.069 | 130.288 após remover duplicatas |
| pesquisa_satisfacao | 81.021 | |
| base_atendentes | 25 | |
| base_motivos | 14 | |
| canais | 4 | |

Outros valores de referência (medidos numa execução local; reconfirmar aqui):
- Custo total jan/25–jul/26: R$ 1.447.671,52.
- CSAT (notas 4 e 5 entre as válidas, de 1 a 5): 86,2% em jan/25 e 56,7% em jul/26.

Se algo divergir, **não ajuste o código para forçar o número**: anote a diferença e investigue
(encoding, formato dos timestamps, modo ANSI do serverless).

## 6. Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `INSUFFICIENT_PERMISSIONS ... SELECT on any file` | `spark.read` numa pasta do Workspace sem o esquema `file:` explícito no caminho | Usar `file:/Workspace/...` no `.load(...)` (testado, funciona em leitura distribuída) — ou, alternativas: ler com `pandas` (funciona sem o prefixo) ou usar um Volume em `/Volumes/...` |
| Widget `base_path` não aparece | Widget criado só dentro de `%run` | Criar a célula do widget antes do `%run` |
| `Path does not exist` | Caminho com texto de exemplo (`<seu-email>`) ou nome de Volume errado | Copiar o caminho pelo Catalog |
| Erro de permissão no Volume | Falta `READ VOLUME` ou `USE SCHEMA` | Pedir a quem criou o Volume |
| Acentos quebrados | Encoding errado: `clientes.csv` e `Chamados_Hora.CSV` são `cp1252` (lido como `iso-8859-1`); os demais são `utf-8` | Conferir a função de carga |

## 7. Regras de segurança e sincronia

- Nunca suba CSV, `.env` ou token para o GitHub.
- Não imprima linhas de `clientes` (CPF, nome, e-mail) em células, `.md` ou prints.
- Use `cliente_hash` (hash do `id_cliente`) quando precisar identificar clientes numa análise.
- Não edite no Databricks um arquivo que também é editado localmente. Se algo mudar aqui, leve a
  mudança para o GitHub por PR; se mudar no repositório, reimporte a versão revisada.
- Quando alguém atualizar o notebook base, avise o grupo para reimportarem a versão nova.

## 8. Checklist

- [ ] Pastas criadas em `Shared/case-final-rocket-lab`
- [ ] Notebook base importado
- [ ] Volume `dados_vcredit` criado
- [ ] 8 CSVs no Volume, com os nomes originais
- [ ] Pasta `dados` antiga removida do Workspace
- [ ] Acesso concedido ao grupo (pasta, Volume, schema)
- [ ] `base_path` registrado no README e avisado no grupo
- [ ] Notebook base rodado uma vez; contagens conferidas
