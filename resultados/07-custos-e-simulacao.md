# 07 — Custos e simulação de ganhos

Fonte: `visao_geral_gold`, `kpi_mensal_gold`, `funil_atendimento_gold`, `motivos_pareto_gold` e `simulacao_ganhos_gold`.
O custo é a soma dos lançamentos de `custos` **maiores que zero** (ver regra em
[`../docs/analitico/confiabilidade-dos-dados.md`](../docs/analitico/confiabilidade-dos-dados.md)).

## Custo do atendimento

| Métrica | Valor |
|---|---|
| Custo total (jan/25 a jul/26) | R$ 1.450.617,85 |
| Referência da entrevista (Gerente Financeiro) | R$ 1.400.000,00 |
| Diferença | + R$ 50.617,85 (+3,6%) |
| Custo mensal: jan/25 → jul/26 | R$ 46.260 → R$ 105.731 (+128,6%) |
| Custo por chamado: jan/25 → jul/26 | R$ 10,73 → R$ 11,18 (+4,2%) |
| Custo por chamado resolvido: jan/25 → jul/26 | R$ 19,74 → R$ 23,49 (+19,0%) |
| Run-rate de jul/26 × 12 | R$ 1,27 mi/ano |

O custo mensal cresce porque o **volume** cresce, não o preço unitário. O custo por chamado **resolvido** sobe 19%
porque a resolução caiu de 54,4% para 47,8%: mais dinheiro é gasto por problema de fato resolvido.

### Onde está o custo

| Etapa | % dos chamados | % do custo | Custo/chamado | Custo/chamado resolvido |
|---|---|---|---|---|
| Autosserviço: Chatbot | 26,9% | 1,4% | R$ 0,58 | R$ 1,18 |
| Autosserviço: URA | 30,0% | 5,0% | R$ 1,85 | R$ 4,08 |
| Nível 1 | 30,1% | 36,9% | R$ 13,69 | R$ 26,05 |
| Nível 2 | 13,0% | 56,8% | R$ 48,98 | R$ 76,55 |

Por motivo: cinco motivos (Problema com aplicativo, Compra não autorizada, Renegociação de dívida, Contestação de fatura, Cancelamento
de conta) são **43,0% dos chamados e 60,0% do custo** ([`03-motivos.md`](03-motivos.md)).

## Simulação de ganhos (`simulacao_ganhos_gold`)

Os dois cenários são **hipóteses de negócio** com premissa explícita; os percentuais (20% e 30%) não vêm dos dados e
precisam ser validados em piloto. A tabela da gold grava as premissas e o cálculo por motivo.

### Cenário A — Deflexão de chamados de baixa criticidade para o autosserviço

- **Base**: chamados de motivos de criticidade **baixa** (consulta de fatura, consulta de limite, alteração de dados cadastrais, dúvidas sobre programa de pontos) que **chegaram ao atendimento humano** (Nível 1 ou 2): **12.411 chamados** no período.
- **Premissa**: 20% desses chamados passam a ser resolvidos no autosserviço.
- **Ganho por chamado evitado** = custo médio do chamado humano do motivo **menos** o custo médio do chamado de autosserviço do mesmo motivo (R$ 19,22 a R$ 21,18; já é líquido do custo do autosserviço).

| Motivo | Base (humano) | Evitados (20%) | Ganho unitário | Economia no período | Economia anualizada |
|---|---|---|---|---|---|
| Consulta de fatura | 4.977 | 995 | R$ 19,22 | R$ 19.129,08 | R$ 12.081,53 |
| Consulta de limite | 4.332 | 866 | R$ 19,27 | R$ 16.691,43 | R$ 10.541,95 |
| Dúvidas gerais sobre programa de pontos | 2.017 | 403 | R$ 20,93 | R$ 8.442,38 | R$ 5.332,03 |
| Alteração de dados cadastrais | 1.085 | 217 | R$ 21,18 | R$ 4.595,93 | R$ 2.902,69 |
| **Total** | **12.411** | **2.482** | | **R$ 48.858,82** | **R$ 30.858,20** |

(Economia no período = 19 meses; mensal média R$ 2.571,52; anualizada = média mensal × 12.)

### Cenário B — Redução da reincidência (recontato do mesmo motivo em até 7 dias)

- **Base**: **55.999 chamados reincidentes** (mesmo cliente e mesmo motivo em até 7 dias do anterior), em 14 motivos. Para o cliente que reabre o chamado, o problema não foi resolvido no primeiro contato.
- **Premissa**: 30% desses recontatos deixam de ocorrer (por resolução na primeira interação).
- **Ganho por recontato evitado** = custo médio dos chamados reincidentes do motivo (R$ 20,31 a R$ 27,41, conforme o motivo).

| Motivo (maiores economias) | Base | Evitados (30%) | Ganho unitário | Economia no período | Economia anualizada |
|---|---|---|---|---|---|
| Compra não autorizada | 7.429 | 2.229 | R$ 26,93 | R$ 60.008,56 | R$ 37.900,14 |
| Problema com aplicativo | 7.609 | 2.283 | R$ 26,44 | R$ 60.358,59 | R$ 38.121,22 |
| Renegociação de dívida | 7.231 | 2.169 | R$ 27,41 | R$ 59.450,22 | R$ 37.547,51 |
| Contestação de fatura | 6.006 | 1.802 | R$ 25,56 | R$ 46.050,90 | R$ 29.084,78 |
| Consulta de fatura | 4.941 | 1.482 | R$ 20,31 | R$ 30.111,54 | R$ 19.017,82 |
| Cancelamento de conta | 3.339 | 1.002 | R$ 26,82 | R$ 26.865,68 | R$ 16.967,80 |
| Bloqueio de cartão | 4.246 | 1.274 | R$ 20,82 | R$ 26.525,42 | R$ 16.752,90 |
| Consulta de limite | 4.282 | 1.285 | R$ 20,44 | R$ 26.258,63 | R$ 16.584,40 |
| Outros 6 motivos | 10.916 | 3.275 | | R$ 72.965,09 | R$ 46.083,22 |
| **Total** | **55.999** | **16.800** | | **R$ 408.594,63** | **R$ 258.059,77** |

(Mensal média R$ 21.504,98; os totais usam os valores sem arredondar, então a soma das linhas pode diferir em R$ 0,01 ou em 1 chamado. A linha "Outros 6 motivos" soma Desbloqueio de cartão, Contratação de cartão adicional, Consulta de contrato,
Dúvidas sobre programa de pontos, Alteração de dados cadastrais e Transferência de agência.)

### Resumo e sensibilidade

| Cenário | Premissa | Economia anualizada |
|---|---|---|
| A — Deflexão | 20% | R$ 30,9 mil |
| B — Reincidência | 30% | R$ 258,1 mil |
| A + B **sem tratar a sobreposição** (teto, não usar como resultado) | | R$ 288,9 mil (~23% do run-rate anual de jul/26, de R$ 1,27 mi) |
| **A + B líquido da sobreposição** (estimativa derivada, do Claude Code) | | **R$ 258 a 279 mil** |

Sensibilidade (o ganho é linear na premissa, mantendo todo o resto):

| Premissa | A — anualizado | B — anualizado |
|---|---|---|
| 10% / 10% | R$ 15,4 mil | R$ 86,0 mil |
| 20% / 20% | R$ 30,9 mil | R$ 172,0 mil |
| 30% / 30% | R$ 46,3 mil | R$ 258,1 mil |

Notas e limitações:

- **A e B se sobrepõem quase por completo.** Dos 12.411 chamados da base de A (baixa criticidade que chegou ao humano), **12.172 (98,1%) também são reincidentes**, ou seja, já estão na base de B. Em linguagem simples: quase todo chamado humano de motivo simples é um recontato, em geral depois de o cliente tentar o autosserviço e não resolver. **Não some A e B.**
  - Pior caso (A inteiramente dentro de B): o líquido é só o B, **R$ 258 mil/ano**.
  - Se os dois cortes fossem independentes, a dupla contagem seria 6% (20% × 30%) de 12.172 chamados, ~730 chamados, ~R$ 9,5 mil/ano; o líquido seria ~**R$ 279 mil/ano**.
  - **Conferência (Databricks, 22/10/2026, ~03h):** `base_a` = 12.411 e `base_b` = 55.999 (iguais à `simulacao_ganhos`), e `a_dentro_de_b` = 12.172, ou seja, **98,1% de A já está em B**. O líquido de R$ 258 a 279 mil/ano continua sendo **estimativa derivada** (pior caso e independência), e os R$ 288,9 mil são só o teto. Query equivalente (a coluna `tambem_em_b` corresponde ao `a_dentro_de_b` conferido; `base_b` é a contagem de `reincidente_7d` na fato, igual à `simulacao_ganhos`):
    ```sql
    SELECT COUNT(*) AS base_a, COUNT_IF(f.reincidente_7d) AS tambem_em_b
    FROM dados_vcredit.default.fato_atendimento_gold f
    JOIN dados_vcredit.default.dim_motivo_gold m ON f.id_motivo = m.id_motivo
    JOIN dados_vcredit.default.dim_canal_gold ca ON f.id_canal = ca.id_canal
    WHERE m.criticidade = 'baixa' AND m.id_motivo > 0
      AND ca.etapa_funil IN ('Nível 1', 'Nível 2')
    ```
- O cálculo usa o **volume médio do período** (~6.940 chamados/mês). Como o volume de jul/26 (9.596) é 38% maior, no ritmo atual a economia seria maior, o que torna esta estimativa conservadora quanto a volume.
- **Não inclui custo de implantação** (desenvolvimento do autosserviço, treinamento, revisão de scripts); o payback depende dele. Estimar esse custo exige dados que o grupo não tem.
- A reincidência é medida pelos dados (mesmo cliente e motivo em até 7 dias), mas **nem todo recontato é evitável**. Neste conjunto todos os chamados têm id de cliente (a regra de elegibilidade não exclui ninguém), e a medida só compara com o chamado anterior imediato do mesmo cliente e motivo.
- Ganhos de satisfação, redução de abandono e liberação de capacidade do Nível 2 **não estão monetizados** aqui (ver [`../docs/analitico/propostas-e-priorizacao.md`](../docs/analitico/propostas-e-priorizacao.md)).
