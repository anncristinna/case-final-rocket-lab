> **Registro histórico.** Este é o README que acompanhou o pacote de revisão da silver e da gold (20 e 21/10/2026),
> trazido da antiga pasta `alteracoes-silver-gold/`. Os itens pendentes que ele cita (diagramas, PDF do guia da gold e
> notebook `Silver_To_Gold`) já foram resolvidos; o estado atual está em [`arquitetura-medalhao.md`](arquitetura-medalhao.md) e
> em [`../../medalhao/`](../../medalhao/). As referências a `bronze/` e `silver/` valem hoje para `medalhao/`.

# Revisão — Silver e modelagem Gold (V-Credit)

## Objetivo

Comparar os dois diagramas de modelagem (`modelagem-silver.png`, `modelagem-gold.png`) e o guia
`guia_camada_gold_vcredit_texto.pdf` contra o código **real** dos dois notebooks desta pasta, e
apontar tudo que estiver desatualizado, incorreto ou inconsistente — priorizado pelo que mais
importa (coisa que quebra a execução > coisa que dá número errado > coisa que é só documentação
desatualizada).

Os diagramas foram feitos em momentos diferentes da implementação e pelo menos uma parte já ficou
desatualizada depois de correções recentes — não assuma que o diagrama está certo e o código errado;
confira os dois lados.

## Contexto do projeto

Case V-Credit (Visagio / Rocket Lab 2026): a partir dos dados de atendimento de um call center,
chegar a recomendações pro Comitê Executivo. Arquitetura medalhão: bronze (ingestão fiel à origem) →
silver (limpeza, tipagem, junção) → gold (modelo em estrela pra BI/apresentação). Comunicação do
projeto é em português do Brasil.

## Arquivos neste pacote

| Arquivo | O que é |
|---|---|
| `Landing_To_Bronze.ipynb` | Notebook da camada bronze — ingestão das 8 tabelas originais, sem nenhuma limpeza (`inferSchema=false`, tudo string). Já rodado no Databricks. |
| `Bronze_To_Silver.ipynb` | Notebook da camada silver — **este é o notebook único e definitivo da silver**, não existe mais nenhum outro notebook de silver no projeto (os antigos, um por tabela, foram descartados). Faz a limpeza de cada tabela e, na última seção ("8. Consolidado"), junta tudo numa `base_silver`. Já rodado no Databricks (saídas de `print` preservadas; saídas de tabela HTML foram removidas deste pacote só pra não pesar o arquivo). |
| `Silver_To_Gold.ipynb` | Notebook da camada gold — **existe agora** (não existia nas rodadas anteriores). Lê as 9 tabelas silver, monta 7 dimensões + `fato_atendimento_gold` + `qualidade_chamado_gold`, e 14 tabelas analíticas. Revisado na quinta rodada (ver abaixo) — 2 achados, 1 já corrigido. |
| `modelagem-silver.png` | Diagrama da modelagem da camada silver (ER, campos, relacionamentos). **Refeito em 20/10/2026** conforme o código atual do `Bronze_To_Silver.ipynb`. |
| `modelagem-gold.png` | Diagrama da modelagem da camada gold (esquema estrela). **Ajustado na sexta rodada**: `id_cliente_hash` agora aparece como SHA-256 (sha2 puro), sem `!`. |
| `guia_camada_gold_vcredit_texto.pdf` | Guia célula-a-célula do `Silver_To_Gold.ipynb` — reconstruído na quarta rodada. **Ajustado na sexta rodada**: não fala mais em segredo/HMAC (seção "Privacidade" e demais menções). |

## O que já sabemos que está certo (não precisa reconferir do zero)

- `Bronze_To_Silver.ipynb` grava 9 tabelas a cada execução, todas com `overwrite` (idempotente):
  `chamados_silver`, `clientes_silver`, `atendentes_silver`, `motivos_silver`, `canais_silver`,
  `canais_depara_silver`, `custos_silver`, `pesquisa_satisfacao_silver`, `chamados_hora_silver`, e a
  junção final `base_silver`.
- `id_cliente` (que é o próprio CPF do cliente) **já está incluído** em `clientes_silver` como chave
  de dedup (`dropDuplicates(["id_cliente"])`) e usado pra ligar com `chamados` na junção final —
  **mas nunca aparece em nenhuma saída de célula** (removido via `.drop()` antes de qualquer
  `display()`). Essa é a regra do projeto pra dado pessoal: nunca exibir CPF/nome/e-mail de
  `clientes`, mas pode usar como chave de junção internamente.
- `chamados_silver` usa `canal_chave`/`motivo_chave` — texto normalizado (minúsculo, sem acento) —
  como chave de ligação, **não** `id_canal`/`id_motivo` resolvidos como inteiro/FK direta. A
  resolução de `canal_chave` → `id_canal` acontece via join com `canais_depara_silver` (que tem 0
  variações sem correspondência, testado contra os dados reais). Não existe um de-para equivalente
  pra motivo — a chave de motivo é recalculada a partir de `nome_motivo` toda vez que precisa (função
  `norm_key`, igual em `chamados_silver` e na seção de junção).
- Duplicatas conhecidas nos dados originais: `chamados` tem 2.636 `id_chamado` duplicados
  (idênticos); `custos` tem 781 `id_custo` duplicados (idênticos, nunca lançamentos conflitantes).
- Nomes de tabela que **divergem** do que seria o nome "canônico"/esperado em outros documentos do
  projeto — isso é conhecido, não é novidade a reportar, só confirme se o guia da gold já leva em
  conta o nome real:
  - `atendentes_silver` (não `base_atendentes_silver`)
  - `motivos_silver` (não `base_motivos_silver`)
  - `canais_depara_silver` (não `canais_de_para`)
- A coluna `status_atendente` existe em **duas** tabelas com significados diferentes (status do
  `id_atendente` dentro do chamado vs. status de emprego do atendente no cadastro). **Decisão:** em
  `chamados_silver` ela continua se chamando **`status_atendente`** (é o nome que a gold lê); a
  renomeação para **`status_id_atendente`** acontece **só na `base_silver`** (seção 8), para não colidir
  com `atendentes_silver.status_atendente`. A gold deve ler `chamados_silver.status_atendente`.
- `base_silver` tem uma flag `dq_cliente_sem_correspondencia` — cerca de 1,0% dos chamados têm
  `id_cliente` que não existe em `clientes_silver` (achado real de qualidade de dado, não bug).

## O que focar na revisão

1. **`modelagem-silver.png` vs. `Bronze_To_Silver.ipynb`**: confira cada tabela do diagrama contra a
   seção correspondente do notebook — nome das colunas, chaves, se a limpeza/junção descrita como
   "TODO" ou "proposta" já foi implementada ou não.
2. **`modelagem-gold.png` e o PDF vs. a silver real**: o modelo gold assume certas colunas vindas da
   silver (ex.: `chamados_silver.status_atendente`, `chamados_silver.canal_chave`/`motivo_chave`,
   `clientes_silver.id_cliente`) — confira se essas colunas existem de verdade, com esse nome, na
   silver atual.
3. **Nomes de tabela**: o PDF/diagrama da gold leem de `DESTINO_*` (9 tabelas silver) — confirme se
   os nomes usados no guia batem com os nomes reais gravados pelo `Bronze_To_Silver.ipynb` (ver lista
   de divergências conhecidas acima).
4. Qualquer suposição de privacidade/regra de negócio que apareça no guia da gold mas não esteja
   implementada ou documentada na silver (ex.: tratamento de nome de atendente).

## Formato da resposta esperada

Uma lista objetiva de pontos a ajustar, cada um com: **onde está o problema** (arquivo/célula/seção),
**o que diz hoje** vs. **o que é verdade no código**, e se é **bloqueador** (quebra execução),
**número errado**, ou só **documentação desatualizada**.


## Correções aplicadas após a revisão (20/10/2026)

### Notebooks
- `Bronze_To_Silver.ipynb`: textos desatualizados (cabeçalho, seção 7, seção 8) corrigidos; `base_silver`
  agora traz `nota_ajustada` também quando `nota` é inválida; `base_silver.custo` soma só lançamentos > 0
  (igual à gold); ~~o `display` de `atendentes_silver` não mostra mais `nome_atendente`~~ (**revertido na terceira rodada**).
  **Para refletir na tabela, rodar de novo ao menos a seção 8** (as demais seções não mudaram de resultado).
- `Landing_To_Bronze.ipynb`: o `display` não mostra mais `id_cliente` (CPF) (a parte sobre `nome_atendente` foi revertida na terceira rodada); as saídas
  salvas da célula de verificação foram apagadas (continham CPF). Não é preciso reingerir.

### `modelagem-silver.png` (refeito)
- Todas as tabelas agora marcadas como gravadas por seção do notebook; sumiram os selos "PROPOSTA", "TODO",
  "AJUSTAR CHAVE" e "UNIFICAR NOMES".
- `chamados_silver`: colunas reais (`canal_chave`, `motivo_chave`, `status_resolucao`, `status_atendente`,
  flags `dq_*`, `*_bruto`); removidos `id_canal`/`id_motivo`/`canal_original`/`motivo_original`.
- `clientes_silver`: `id_cliente` (CPF) é a chave; tipos reais (`data_cadastro` string `yyyy/MM/dd`; idade e
  vencimento string).
- Nomes corrigidos: `motivos_silver` (não `base_motivos_silver`) e `canais_depara_silver` (não `canais_de_para`).
- `pesquisa_satisfacao_silver`: relação com chamados corrigida para 1 → 0..1.
- Incluída a `base_silver` (junção final, `status_id_atendente`, `dq_cliente_sem_correspondencia`).
- Ligações: a de `motivos_silver` fica tracejada porque a chave é recalculada (não existe de-para de motivo).

### `modelagem-gold.png` (refeito)
- `dim_cliente` deixou de ser "condicional": `clientes_silver` já traz `id_cliente`. `perfil_cliente` deixou de
  depender de algo que faltava. Notas sobre conversão de tipos (idade e datas chegam como string).
- `id_cliente_hash` marcado com `!` e descrito como HMAC-SHA256 com segredo (o `sha2` puro de um CPF é reversível).
- Proposto membro `SEM_CADASTRO` na `dim_cliente` para os 1.330 chamados (1,0%) sem cliente na silver.
- `dim_atendente`: o diagrama dizia "sem nome do atendente" e o guia usa o nome — agora marcado com `!`
  como **decisão pendente** (nome real ou "Atendente <id>"); redação ajustada na quarta rodada (vale só para o
  material do Comitê).
- **O que não mudou:** colunas da fato (22) e da qualidade (24), demais dimensões e tabelas OLAP.

### Pendente
- `guia_camada_gold_vcredit_texto.pdf` segue desatualizado; o que trocar está em
  `ajustes_gold_pdf_e_diagramas.md` (seção B). Decisões em aberto: nome do atendente e `status_atendente`
  (mantido sem renomear em `chamados_silver`).

## Segunda rodada de correções (21/10/2026) — já commitadas na `main`

Comparando os arquivos desta pasta com o estado real do projeto, achei e corrigi mais 4 pontos,
diretamente nos notebooks originais (`bronze/Landing_To_Bronze.ipynb` e `silver/Bronze_To_Silver.ipynb`)
— as cópias aqui na pasta foram atualizadas pra ficar idênticas:

- **CPF exposto de verdade (achado crítico)**: a célula de verificação da bronze fazia
  `display(tabela.limit(5))` pra todas as tabelas menos `clientes` — mas `chamados` e `Chamados_Hora`
  também têm `id_cliente`/`ID_Cliente` (o mesmo CPF). Como o notebook já tinha rodado no Databricks,
  CPFs reais foram exibidos na saída dessa célula. Corrigido: a amostra agora sempre tira `id_cliente`
  e `nome_atendente`, em qualquer tabela. As saídas antigas (com CPF) foram apagadas do notebook local.
- O bug do `nota_ajustada` (ponto já citado acima) foi de fato aplicado — validei rodando localmente:
  foi de 73.383 pra 74.592 em `base_silver`, batendo com o valor correto de `pesquisa_satisfacao_silver`.
- O filtro de custo `> 0` também foi validado: `com custo` em `base_silver` caiu de 130.288 pra 129.744,
  diferença de 544 — bate exatamente com os 544 custos ≤ 0 já documentados (271 negativos + 273 zero).
- `Bronze_To_Silver.ipynb` tinha saídas HTML de tabela embutidas (1,7 MB) — removidas num commit à
  parte (os `print`s de contagem continuam intactos).

**Essas correções já foram commitadas direto na `main`** (commits `a31da59`, `26dc328`, `8e88707`) —
não é mais trabalho pendente de branch/PR. Os dois notebooks desta pasta (`Landing_To_Bronze.ipynb`,
`Bronze_To_Silver.ipynb`) são cópias exatas do que está na `main` agora.

## Terceira rodada (21/10/2026) — `nome_atendente` volta a aparecer

**Importante para quem for gerar/atualizar os diagramas e o PDF a partir daqui:** a rodada anterior
tinha escondido `nome_atendente` (tratando como "dado pessoal") tanto na verificação da bronze quanto
no `display` da seção 3 da silver. Isso foi **revertido** (commit `1e962c0`) — `nome_atendente` volta a
aparecer normalmente nos dois notebooks e em `base_silver`.

Motivo: a regra de dado pessoal do projeto é específica sobre `clientes` (CPF/nome/e-mail) —
`nome_atendente` nunca esteve nela, e o grupo já usa nome/identificação de atendente abertamente em
`analises/top_atendentes.md`. A ocultação anterior foi uma suposição acrescentada durante uma revisão,
não uma regra confirmada do projeto.

**O que isso muda nos diagramas/PDF, se forem regenerados:**
- `modelagem-silver.png`: `atendentes_silver` deixa de dizer "`nome_atendente` nunca é exibido nas
  saídas do notebook" — ele **é** exibido (seção 3 e `base_silver`). Só `id_cliente` (CPF) continua
  nunca sendo exibido em nenhuma célula.
- `modelagem-gold.png` / `guia_camada_gold_vcredit_texto.pdf`: o item marcado com `!` sobre
  "nome real ou rótulo anônimo" em `dim_atendente` **continua em aberto** — isso não muda. A decisão
  de mostrar o nome completo ou um rótulo tipo "Atendente 4" é só para o material que for pro Comitê
  Executivo (gold/apresentação), não para bronze/silver. Não há decisão tomada ainda sobre a gold.

## Quarta rodada (21/10/2026) — diagramas alinhados à terceira rodada

`modelagem-silver.png` e `modelagem-gold.png` foram **regenerados** para refletir o que a terceira rodada
decidiu. Os notebooks não foram alterados.

- `modelagem-silver.png`:
  - `atendentes_silver` não diz mais que `nome_atendente` nunca é exibido. A coluna aparece como `string`
    comum e a nota agora diz: "Só `id_cliente` (CPF) é restrito; `nome_atendente` aparece."
  - Na `base_silver`, saiu o "(dado pessoal)" ao lado de `nome_atendente`.
  - `custos_silver`: nota nova com os 544 lançamentos de custo ≤ 0 (271 negativos, 273 zeros), que ficam fora
    da soma de `custo` na `base_silver`.
- `modelagem-gold.png`:
  - `dim_atendente`: a nota do `!` passou a dizer que a decisão (nome real ou "Atendente <id>") vale **só para
    o material do Comitê**. Continua em aberto; nenhuma decisão foi tomada.
- `ajustes_gold_pdf_e_diagramas.md`: itens A-6 e B-9 reescritos no mesmo sentido (sem tratar o nome como dado
  pessoal).
- **Supera** os trechos da seção "Correções aplicadas após a revisão (20/10/2026)" que falavam em esconder
  `nome_atendente` ou chamá-lo de "dado pessoal".

### Pendente
- ~~`guia_camada_gold_vcredit_texto.pdf` continua sem correção~~ **Refeito em 21/10/2026** com todos os ajustes da seção B (o item 1, "mais 120", era falso alarme). O PDF novo foi reconstruído do zero (mesmo conteúdo e ordem; visual simples) e termina com a seção "Alterações desta versão".
- Decisão do grupo: nome real ou rótulo anônimo do atendente no material do Comitê.

## Quinta rodada (21/10/2026) — `Silver_To_Gold.ipynb` chegou, revisado

O notebook da gold **passou a existir** nesta rodada (não existia antes, só o guia em PDF). Revisei célula
por célula contra as 9 tabelas silver reais. No geral está muito bem feito e bate com o PDF: resolução de
`id_atendente` (-1/-2/-3) correta, `fato_atendimento_gold` com as 22 colunas certas,
`qualidade_chamado_gold` com as 24, custo somando só `> 0`, nomes de tabela (`atendentes_silver`,
`motivos_silver`, `canais_depara_silver`) todos corretos.

Achei 2 pontos:

1. **`id_cliente_hash` usava `sha2` puro, sem HMAC/segredo** — o que contradizia o que o próprio PDF
   (`guia_camada_gold_vcredit_texto.pdf`) e o `ajustes_gold_pdf_e_diagramas.md` (item A-3) diziam que
   deveria ser feito. **Decisão do grupo: manter `sha2` puro mesmo** — o `id_cliente` do case é dado
   fictício, não CPF real de ninguém, então o risco que justificava o HMAC não se aplica. Já corrigi:
   - `Silver_To_Gold.ipynb` (células 5 e 21): comentário explicando a decisão (o código já estava certo,
     só não tinha o porquê documentado).
   - `ajustes_gold_pdf_e_diagramas.md`: item A-3 e B-8 atualizados pra registrar a decisão.
   - **Ainda faltam** (próxima rodada): `modelagem-gold.png` (tirar "HMAC-SHA256" e o `!` de `id_cliente_hash`
     em `dim_cliente`, e a frase correspondente em "Leitura do modelo") e
     `guia_camada_gold_vcredit_texto.pdf` (seção "Privacidade", tirar a menção a segredo).

2. **`dim_cliente_gold.data_cadastro` e `dia_vencimento_fatura` continuavam como texto** — decisão do
   grupo: corrigir o notebook (não a documentação). Já corrigido e validado localmente (`célula 21`):
   `data_cadastro` vira `date` (`to_date(data_cadastro, 'yyyy/MM/dd')`) e `dia_vencimento_fatura` vira
   `int` (`try_cast(... as int)`), tratando valor nulo/inválido como `NULL` em vez de quebrar. O PDF já
   descrevia esse comportamento certo — não precisou mudar nada nele. **Ainda falta**: conferir se
   `modelagem-gold.png` já mostra os tipos certos em `dim_cliente` (sem `!` de pendência nesses dois campos).

## Sexta rodada (21/10/2026) — diagrama gold e PDF alinhados à decisão do hash

- `modelagem-gold.png`: `id_cliente_hash` em `dim_cliente` agora é `PK` com tipo `string · SHA-256` (sem `!`);
  `data_cadastro` é `date` e `dia_vencimento_fatura` é `int` (já estavam assim, sem pendência); a nota de leitura
  diz que o hash é `sha2` puro por decisão do grupo (id fictício no case) e que a Gold converte idade e datas.
  Continuam como propostas/pendências: membro `SEM_CADASTRO` e nome do atendente no material do Comitê.
- `guia_camada_gold_vcredit_texto.pdf` (18 págs.): removidas todas as menções a HMAC/segredo; a regra de
  privacidade descreve o `sha2` puro e o motivo. A seção final "Alterações desta versão" foi atualizada.
- **Correção de um excesso meu na versão anterior do PDF:** eu tinha escrito que `dim_cliente` deixava de ser
  condicional e que `DIM_CLIENTE_CRIADA` sumia, mas o `Silver_To_Gold.ipynb` mantém a condição (hoje sempre
  atendida). O PDF voltou a descrever a condição, só sem o aviso "hoje não é criada".
- O notebook não cria membro desconhecido para clientes: os 1.330 chamados sem cadastro recebem um hash que não casa
  com a `dim_cliente` e ficam fora de `perfil_cliente`. O PDF agora diz isso como está; `SEM_CADASTRO` segue proposta.
