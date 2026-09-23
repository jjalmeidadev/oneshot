# RNF05 — desempenho · 21/09/2026 · commit `81c787d`

Issue [#231](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/231) (S4-35).
Casos `CT-RNF05-P` e `CT-RNF05-N`, Seção 9.2.4 do `Projeto.md`.

> **Histórico.** Rodada superada. A definitiva está em
> [`rnf05-37flash/`](../rnf05-37flash/RELATORIO.md); o índice de todas as rodadas, em
> [`evidencias/README.md`](../README.md).

## Resultado

> ## 🚫 MEDIÇÃO INVALIDADA — instrumentos prontos, rodada pendente
>
> As duas rodadas Locust obrigatórias **não foram executadas**: a quota diária
> do provedor esgotou durante a coleta do RNF04.
>
> As latências coletadas incidentalmente **não medem o produto**. Elas incluem
> o sleep do backoff de retry sobre HTTP 429 e, por isso, não podem sustentar
> nem aprovação nem reprovação.
>
> **O RNF05 permanece NÃO EXECUTADO.**

## Correção de uma conclusão anterior

A primeira versão deste relatório afirmava "indício forte de reprovação", com
base em mediana de 12,2 s e máxima de 57,2 s contra um teto de 10 s.

**Essa leitura estava errada.** `_send_request_with_retry`
([`app/gemini/client.py:297`](../../app/gemini/client.py)) reenvia a chamada até
3 vezes sobre HTTP 429, dormindo `2s → 4s → 8s` entre as tentativas — 14 s de
sleep no pior caso. Com a quota estourada, boa parte do tempo cronometrado foi
**espera de backoff, não processamento**.

A decomposição das 11 latências sustenta isso:

| Latência | Leitura provável |
| ---: | --- |
| 8.654 ms · 9.306 ms · 9.861 ms | sem retry — **as três abaixo do teto de 10 s** |
| 11.744 – 19.856 ms | ~1 retry: processamento + 2 s de sleep + tentativa perdida |
| 39.119 ms · 57.230 ms | múltiplos retries antes de passar |
| 13 × ~19.000 ms | 3 retries (14 s de sleep) e falha ao final |

As únicas três medidas plausivelmente limpas ficaram **em 8,6 s, 9,3 s e 9,9 s**
— abaixo do teto, ainda que com folga estreita. Isso não aprova o requisito,
porque três pontos sequenciais e sem concorrência não são uma medição. Mas
desautoriza a conclusão de reprovação que estava publicada aqui.

O que se pode afirmar com honestidade hoje: **a latência do produto é
desconhecida.** A rodada válida é que vai dizer.

## O que a rodada válida muda

`GEMINI_MAX_RETRIES=0` durante a medição, aplicado por
[`app/tests/executar_rodada_rnf.sh`](../../app/tests/executar_rodada_rnf.sh),
resolve os dois problemas de uma vez:

1. **Consumo de quota.** Cada pergunta passa a custar 1 unidade em vez de até 4.
   A amostra de 24 perguntas consome 24 chamadas, não até 96 — que foi o que
   esgotou a quota na décima segunda pergunta.
2. **Latência limpa.** Sem backoff, o cronômetro mede processamento.

O retry continua ligado em produção, onde resiliência vale mais que uma medida
limpa. A diferença fica registrada na ficha de ambiente e precisa ser declarada
no relatório da rodada.

## Onde o tempo é gasto

Esta parte **não** é afetada pelo retry, porque é medida dentro da aplicação:

| Etapa | Mediana | Leitura |
| --- | ---: | --- |
| Recuperação RAG (Supabase) | 1.107 ms | ~11% do orçamento de 10 s |
| Classificação PLN | ~4 ms (Seção 8.11) | Irrelevante |
| Chamada ao LLM | o restante | Onde o orçamento é consumido |

Conclusão que os dados autorizam: otimizar recuperação ou classificação não
move o ponteiro do RNF05. Se houver problema de latência, ele está na chamada
ao provedor.

## Instrumentos entregues e validados

| Arquivo | Estado |
| --- | --- |
| `app/tests/performance/locustfile.py` | ✅ criado e validado em execução real |
| `app/tests/performance/prompts.py` | ✅ massa congelada, 75% simples / 25% comparação |
| `app/tests/performance/api_com_atraso.py` | ✅ duplo do `CT-RNF05-N` |
| `app/tests/performance/registrar_ambiente.py` | ✅ ficha de CPU, memória, SO, commit, configuração |
| `app/tests/executar_rodada_rnf.sh` | ✅ rodada completa em um comando |

O `locustfile.py` era exigido nominalmente pela Seção 9.2.4 e **não existia** no
repositório antes desta task.

Validação executada (30 s, 1 usuário) — evidência em `rnf05-validacao_stats.csv`:

- separa `POST /api/chat [simples]` de `[comparacao]`, permitindo apurar os dois
  P95 sem misturar populações;
- marca o HTTP 429 como falha, provando que a validação de contrato funciona;
- produz a tabela de percentis e os CSVs;
- `RNF05_SEM_AQUECIMENTO=1` alterna cache frio e quente.

## Execução pendente

```bash
# com a quota disponível, a partir de src/backend
GEMINI_MAX_RETRIES=0 .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
bash app/tests/executar_rodada_rnf.sh
```

O cenário negativo `CT-RNF05-N` roda à parte, contra a instância com atraso
injetado, e **precisa reprovar**. Se passar, a medição não enxerga violação e as
rodadas positivas não valem nada.

## Ressalva do cenário comparativo

A massa tem **um único projeto** (`PRJ-0442`) e `comparacao_entre_projetos` foi
adiada para a Sprint 5 pela Seção 6.4.1 do `GestaoProjeto.md`. Os 25% de prompts
comparativos medem a latência da **recusa**, não a de uma comparação produzida.

Um P95 comparativo dentro dos 20 s nessas condições **não demonstra** que o
requisito é atendido para comparações reais. A ressalva está em `prompts.py` e
precisa acompanhar qualquer número publicado.

## Bloqueio: limite de 20 requisicoes por dia

O provedor devolveu a restricao textualmente:

```
Rate limit exceeded for model gemini-3.7-flash
(limit: 20 requests per day on Free Tier)
```

Isso dimensiona o problema com precisao:

| Necessidade | Chamadas | Cabe em 20/dia? |
| --- | ---: | :---: |
| Amostra do RNF04, com `GEMINI_MAX_RETRIES=0` | 24 | **nao** |
| Amostra do RNF04, com retry padrao (3) | ate 96 | nao |
| RNF05 — rodada de 1 usuario, 5 min | ~40 a 70 | **nao** |
| RNF05 — rodada de 5 usuarios, 5 min | ~100 a 150 | **nao** |
| RNF05 — rodada negativa, 2 min | ~15 a 25 | no limite |

Nenhuma das rodadas obrigatorias cabe no Free Tier. Nao e uma questao de
esperar o reset: com 20 chamadas por dia, a amostra de 24 perguntas nao fecha
nem em um dia inteiro, e as rodadas de carga sao inviaveis por uma ordem de
grandeza.

**O desbloqueio real e uma chave com tier pago.** Sem ela, RNF04 e RNF05 ficam
como nao executados com a dependencia nomeada, que e o tratamento previsto pela
Secao 9.2.7 do `Projeto.md`.

Alternativas consideradas e por que nao servem:

- **encolher a amostra para caber em 20**: a Secao 9.2.3 exige no minimo 20
  perguntas e proibe ajustar a massa para acomodar o resultado. Ficar
  exatamente em 20 eliminaria qualquer margem e, pior, seria mudar o teste para
  passar em vez de medir o produto;
- **dividir a amostra em dois dias**: viavel para o RNF04, com versao e commit
  congelados, e ja resolve aquela task. Nao resolve o RNF05, cujas rodadas de
  carga precisam de dezenas de chamadas concentradas em cinco minutos;
- **duplo deterministico no lugar do provedor**: mediria o pipeline sem o
  componente que consome o orcamento de latencia, produzindo um P95 confortavel
  e falso.
