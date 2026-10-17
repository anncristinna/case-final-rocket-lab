# Databricks ↔ GitHub (Git folder)

Como sincronizar os notebooks `.py` deste repositório com o workspace Databricks.
Nomes de menu podem variar entre contas/versões: ajuste esta página pelo grupo depois do primeiro teste.

## 1. Vincular a conta do GitHub

*User Settings → Linked accounts* e conecte sua conta do GitHub.

## 2. Criar o Git folder

*Workspace → Create → Git folder*, cole a URL do repositório (`https://github.com/<org>/<repo>`) e confirme.

## 3. Trabalhar em branch própria

Dentro do Git folder, **sempre** crie/selecione sua branch (`feat/<nome>-<assunto>`) antes de editar.
**Nunca** trabalhe direto na `main` — nem localmente, nem no Databricks.

## 4. Commit, push e pull

Pela própria interface do Git folder: botão de Git mostra o diff, permite commit com mensagem e push.
Puxe (`Pull`) antes de começar, para não sobrescrever o trabalho de outra pessoa.

## 5. Se o Git folder não estiver disponível no Free Edition

Alternativa manual: *Workspace → Import* dos arquivos `.py` (um a um ou a pasta), editar lá e
depois copiar as mudanças de volta para o repositório local.

## 6. Regra de dados pessoais

Antes de commitar/pushar, confira que nenhuma saída de célula mostra nome, e-mail ou CPF
(`id_cliente`). Limpe a saída da célula ou re-rode sem exibir essas colunas.
