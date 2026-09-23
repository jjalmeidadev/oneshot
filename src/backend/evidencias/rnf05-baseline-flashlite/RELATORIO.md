# RNF05 — desempenho · 22/09/2026 · commit `81c787d`

Issue [#231](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/231) (S4-35).
Casos `CT-RNF05-P` e `CT-RNF05-N`, Seção 9.2.4 do `Projeto.md`.

> **Superado.** A rodada definitiva do RNF05, no modelo da bancada em plano pago, está em
> [`rnf05-37flash/`](../rnf05-37flash/RELATORIO.md). Este relatório continua
> valendo pela **medição de controle** do piso do Free Tier, que mostra que o
> provedor gratuito da bancada, sozinho, não comporta o teto do RNF05.

## Resultado

> ## ❌ REPROVADO na configuração medida
>
> | Rota | P95 observado | Teto | |
> | --- | ---: | ---: | :---: |
> | Consulta simples | **26.000 ms** | 10.000 ms | reprova |
> | Comparação | **33.000 ms** | 20.000 ms | reprova |
> | Erros HTTP | **1** (HTTP 502) | 0 | reprova |
>
> Reprova nos três critérios. **Mas a causa dominante não é o produto** — ver
> a seção seguinte, que é a parte que importa deste relatório.

## A causa: o piso do Free Tier é maior que o teto do requisito

Antes de qualquer conclusão sobre o sistema, uma medição de controle. Chamada
**direta ao provedor**, sem RAG, sem classificador, sem banco, prompt de duas
palavras, `max_output_tokens=16` e `thinking_level=minimal` — ou seja, a
configuração mais rápida que o provedor aceita:

| Amostra | Latência |
| :---: | ---: |
| 1 | 14.726 ms |
| 2 | 37.729 ms |
| 3 | 24.460 ms |
| 4 | 35.737 ms |
| 5 | timeout (> 90.000 ms) |

Duas amostras isoladas colhidas antes, com `thinking_level=low`, ficaram em
19.670 ms (`gemini-3.1-flash-lite`) e 23.109 ms (`gemini-3.6-flash`).

**Uma chamada que não faz absolutamente nada custa de 15 a 37+ segundos.** O
teto do RNF05 é de 10 s para o pipeline inteiro — classificação, recuperação,
geração e serialização.

Baixar `thinking_level` de `low` para `minimal` **não teve efeito mensurável**:
a faixa permaneceu a mesma. A variável dominante é a fila do provedor, não a
configuração de geração.

### Por que isso encerra a discussão sobre otimizar o produto

O melhor tempo já observado no pipeline completo foi de 6.377 ms, na coleta do
RNF04. Isso pode sugerir que o sistema caberia no orçamento. **Não cabe**: essa
medida foi um momento de baixa congestão, e a distribuição acima mostra que o
piso típico está acima do teto inteiro do requisito.

Qualquer economia possível no produto — menos tokens de saída, menos fontes no
prompt, cache de recuperação — disputa uma fatia de 1,1 s em um total que a fila
do provedor sozinha leva a 15 s ou mais.

A decomposição do tempo dentro da aplicação confirma o mesmo:

| Etapa | Mediana | Participação |
| --- | ---: | --- |
| Recuperação RAG (Supabase) | 1.131 ms | ~4% do observado |
| Classificação PLN | ~4 ms (Seção 8.11) | desprezível |
| Chamada ao provedor | o restante | **essencialmente tudo** |

A conclusão honesta: **este resultado mede o provisionamento, não a
engenharia.** Reportar "o agente é lento" seria uma leitura errada da
evidência. O que se pode afirmar é que **o Free Tier, usado na bancada para não
gerar custo, não comporta o teto do RNF05**. Isso é característica do provedor
gratuito, e não do sistema: no ambiente do Metrô o agente usará o Copilot Studio
com modelos GPT.

## Ambiente

| Campo | Valor |
| --- | --- |
| Commit | `81c787d` |
| Data | 22/09/2026, 15:01 |
| Modelo | `gemini-3.1-flash-lite` |
| Retries do provedor | 0 (medição limpa, sem backoff no cronômetro) |
| Modalidade de cache | **frio** (sem aquecimento) |
| Máquina | Darwin 25.6.0, arm64 |
| Origem do RAG | banco — Supabase |

## `CT-RNF05-P` — rodada positiva

```bash
RNF05_SEM_AQUECIMENTO=1 PYTHONPATH=. locust \
    -f app/tests/performance/locustfile.py --host http://127.0.0.1:8000 \
    --headless -u 1 -r 1 -t 5m --csv evidencias/rnf05-baseline-flashlite/rnf05-baseline
```

| Rota | Requisições | Falhas | Mediana | P95 |
| --- | ---: | ---: | ---: | ---: |
| `[simples]` | 10 | 1 | 22.000 ms | 26.000 ms |
| `[comparacao]` | 3 | 0 | 31.000 ms | 33.000 ms |
| Agregado | 13 | 1 | 22.000 ms | 33.000 ms |

## `CT-RNF05-N` — rodada negativa: ✅ a medição enxerga a violação

```bash
# instância com atraso de 25 s injetado só na rota de comparação
uvicorn app.tests.performance.api_com_atraso:app --host 127.0.0.1 --port 8001

RNF05_SO_COMPARACAO=1 RNF05_SEM_AQUECIMENTO=1 PYTHONPATH=. locust \
    -f app/tests/performance/locustfile.py --host http://127.0.0.1:8001 \
    --headless -u 1 -r 1 -t 2m --csv evidencias/rnf05-baseline-flashlite/violacao/rnf05-violacao-flashlite
```

P95 comparativo: **58.000 ms**, contra teto de 20 s. A rodada reprova, que é
exatamente o que dela se exige.

A prova é aritmética: as duas amostras vieram em 33.773 ms e 58.467 ms. A
diferença é **24.694 ms**, praticamente o atraso de 25 s injetado. A medição
não só reprovou como reprovou pelo valor certo.

> ### Primeira tentativa do cenário negativo falhou, e por quê
>
> A rodada negativa inicial não validou nada: saíram 7 requisições e **nenhuma**
> caiu na rota de comparação, porque a mistura normal sorteia comparação em 1 de
> cada 4 tarefas. O atraso injetado nunca foi exercido.
>
> Um cenário negativo não pode depender de sorteio — se a violação só acontece
> quando o dado colabora, o teste não prova coisa alguma. Foi adicionada a
> variável `RNF05_SO_COMPARACAO=1`, que torna a rodada negativa determinística.
> A evidência acima é da rodada corrigida.

## Limitações — e são severas

1. **Amostra minúscula.** 13 requisições na positiva, 2 na negativa. Um P95
   sobre 13 pontos é praticamente o máximo observado. A quota do Free Tier não
   permitiu mais.
2. **Modelo não é o do MVP declarado.** O `.env` define `gemini-3.7-flash`;
   mediu-se `gemini-3.1-flash-lite`, porque a quota do primeiro estava esgotada
   e o limite é por modelo.
3. **Cache frio.** O aquecimento previsto na Seção 9.2.4 foi desligado para não
   gastar 14 unidades de quota. A rodada quente não foi executada, e cache frio
   e quente **não podem ser misturados** num mesmo resultado.
4. **A rodada de 5 usuários não foi executada.** Consumiria entre 100 e 150
   chamadas, muito além do Free Tier. `CT-RNF05-P` está, portanto, **parcial**:
   só a linha de base de 1 usuário existe.
5. **Congestão do provedor durante as rodadas.** Os HTTP 502 são `503` do
   provedor ("high demand"), não falha do sistema. Eles reprovam o critério de
   zero erros, mas a causa é externa.

## Veredito por caso

| Caso | Resultado | Ressalva |
| --- | --- | --- |
| `CT-RNF05-P` | **reprovado (parcial)** | Só 1 usuário; falta a rodada de 5 usuários e a rodada quente |
| `CT-RNF05-N` | **validado** | A medição detecta a violação pelo valor exato injetado |

## O que resolveria

1. **Medir com provedor pago.** É a única forma de medir o sistema, e não o
   limite do plano gratuito: no Free Tier, nenhuma otimização de produto coloca o
   P95 abaixo de 10 s, porque o piso do provedor sozinho já está em ~20 s. As
   rodadas definitivas foram feitas assim, em
   [`rnf05-37flash/`](../rnf05-37flash/RELATORIO.md).
2. **Módulo VHS/cache** (`S4-31`, issue #226): muda o quadro em *cache hit*,
   mas o requisito mede *cache miss*, que continua dependendo do provedor.
3. Reduzir `GEMINI_MAX_OUTPUT_TOKENS` e `GEMINI_THINKING_LEVEL`: **testado e
   descartado**. Com `thinking_level=minimal` e 16 tokens de saída, a chamada
   trivial continuou entre 14,7 s e 37,7 s. As respostas reais usam cerca de 130
   tokens contra um teto de 512, então o limite nunca foi o gargalo.

Nenhuma dessas ações foi executada nesta task. `DEF-RNF05-01` permanece aberto,
agora com causa identificada.
