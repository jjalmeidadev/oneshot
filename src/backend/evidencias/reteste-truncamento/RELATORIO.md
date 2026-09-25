# Reteste do truncamento das respostas · 23/09/2026

Defeito `DEF-RNF04-02`, reencontrado no teste de usabilidade: duas respostas
chegaram cortadas no meio da frase (ocorrência O5) e uma pergunta sobre riscos
recebeu só o aviso de dados fictícios, sem conteúdo (O7). O log da API registrou
as três como encerradas pelo limite de 512 tokens.

## Causa

O limite de tokens da resposta inclui o raciocínio do modelo. Na maior parte das
chamadas o modelo não raciocina, mas, quando raciocina, consome até cerca de 490
tokens — quase todo o limite anterior — e o texto é cortado ou não chega a
começar.

## Correção

Em `app/gemini/client.py`:

| Mudança | Efeito |
| --- | --- |
| Limite padrão de 512 para 1024 tokens (`GEMINI_MAX_OUTPUT_TOKENS`) | O raciocínio deixa de esgotar o espaço do texto |
| Resposta encerrada pelo limite recebe o aviso "A resposta foi interrompida antes de terminar. Pergunte de novo, de forma mais específica." | O usuário deixa de receber uma resposta cortada como se fosse completa |
| Resposta vazia pelo limite vira o próprio aviso, e não um erro | A pergunta da O7 deixa de ficar sem resposta |

O aviso vale para o caminho do OpenRouter, onde o motivo de parada é informado. O
`.env.example` passou a trazer o limite de 1024.

## Método

Cada pergunta rodou nos dois limites, em ordem sorteada, com o mesmo prompt que a
API monta: recuperação no banco e `build_rag_input`. Foram a pergunta da O7, dez
vezes em cada limite, e as 14 perguntas da massa do RNF05, duas vezes em cada
limite. Modelo `google/gemini-3.7-flash`, pelo OpenRouter.

```bash
PYTHONPATH=. .venv/bin/python evidencias/reteste-truncamento/reteste_truncamento.py
```

## Resultado

> ## ✅ CORREÇÃO APROVADA NO RETESTE
>
> | Limite | Execuções | Cortadas | Vazias | Tempo do modelo — mediana | P95 aproximado |
> | ---: | ---: | ---: | ---: | ---: | ---: |
> | 512 | 38 | **4** | 0 | 2.920 ms | 5.044 ms |
> | 1024 | 38 | **0** | 0 | 3.099 ms | 5.628 ms |

| Pergunta | Limite | Execuções | Cortadas |
| --- | ---: | ---: | ---: |
| A da O7, sobre riscos e avanços | 512 | 10 | 1 |
| A da O7, sobre riscos e avanços | 1024 | 10 | 0 |
| Massa do RNF05 | 512 | 28 | 3 |
| Massa do RNF05 | 1024 | 28 | 0 |

A resposta vazia da O7 não se repetiu nas dez tentativas com o limite antigo: o
defeito é intermitente, porque depende de quanto o modelo raciocina em cada
chamada. O limite novo deixa espaço para o texto mesmo quando o modelo raciocina, e
nenhuma das 38 execuções com ele foi cortada; se ainda houver corte, o aviso ao
usuário cobre o caso.

## Efeito no desempenho

O limite maior acrescentou cerca de 0,2 s na mediana e 0,6 s no P95 do tempo da
chamada ao modelo, que é parte do tempo total de resposta. O RNF05 foi medido com o
limite de 512, com P95 de 7,3 a 7,6 s na consulta simples, uma margem de 2,4 a
2,7 s até o teto de 10 s. A diferença medida aqui é menor que essa margem, mas o
RNF05 com o limite novo não foi medido.

## Arquivos

| Arquivo | Conteúdo |
| --- | --- |
| `reteste_truncamento.py` | Script do reteste |
| `execucoes.csv` | As 76 execuções, com limite, latência, truncamento e tokens de raciocínio |
