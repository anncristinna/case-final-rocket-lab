# Top 10 atendentes por volume

> Conteúdo destinado ao Notion compartilhado do grupo. Números de `analise_geral_corrigida.py`, rodado
> localmente sobre os CSVs completos — reconfirmar no Databricks antes de publicar. Nomes são de
> atendentes (equipe interna), não de clientes — não há dado pessoal de cliente aqui.

| Atendente | Nível | Chamados | Resolução | TMA |
|---|---|---|---|---|
| Marilene Nascimento | 1 | 6.060 | 46,5% | 633,0 s |
| Daniel Fonseca | 1 | 6.046 | 47,5% | 555,6 s |
| Roberta Assunção | 1 | 6.013 | 49,2% | 648,0 s |
| Solange Silveira | 1 | 5.993 | 52,1% | 568,5 s |
| Josefa Brito | 1 | 5.988 | 51,5% | 420,0 s |
| Maria Eduarda Freitas | 1 | 5.980 | 50,7% | 524,8 s |
| Luiza Galvão | 1 | 5.954 | 52,1% | 475,6 s |
| Jaqueline Campos | 1 | 5.902 | 53,1% | 489,7 s |
| Eduardo Lacerda | 1 | 5.833 | 45,9% | 704,1 s |
| Marcos Torres | 1 | 5.832 | 51,7% | 504,8 s |

## Leitura

- Os 10 atendentes com mais chamados são **todos de nível 1** — esperado, já que o nível 1 recebe o
  primeiro contato e tem mais gente alocada; não dá pra comparar carga entre níveis só por este corte.
- Dentro do nível 1, a resolução varia de 45,9% a 53,1% e o TMA de 420 s a 704 s entre esses 10 — vale
  olhar se a diferença é por perfil de motivo atendido ou por desempenho individual antes de tirar
  conclusão (não investigado aqui).
- Josefa Brito tem o menor TMA (420 s) com resolução mediana (51,5%) — possível referência de eficiência
  a estudar; Eduardo Lacerda tem o maior TMA (704 s) e a segunda menor resolução (45,9%) — candidato a
  olhar de perto.
