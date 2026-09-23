# RNF04 — rodada definitiva · 22/09/2026

Casos `CT-RNF04-P` e `CT-RNF04-N`, Seção 9.2 do `Projeto.md`.
Amostra congelada v1.2, 24 perguntas, **no modelo da bancada de teste (`gemini-3.7-flash`)**.

## Resultado

> ## ✅ APROVADO
>
> | Métrica | Observado | Critério |
> | --- | ---: | ---: |
> | Respostas fundamentadas | **91,67%** (22/24) | ≥ 90% |
> | Taxa de alucinação | **4,17%** (1/24) | ≤ 5% |
>
> As 24 perguntas obtiveram resposta, sem nenhum erro operacional.
>
> **A margem é estreita nos dois critérios.** Mais uma resposta não
> fundamentada reprovaria a fundamentação (87,5%); mais uma alucinação
> reprovaria a alucinação (8,33%). O resultado atende ao requisito e não deve
> ser apresentado como folgado.

| Cenário | Fundamentadas | Não fundamentadas | Alucinação |
| --- | ---: | ---: | ---: |
| `CT-RNF04-P` (positivo) | 12/12 | 0 | 0 |
| `CT-RNF04-N` (negativo) | 10/12 | 1 | 1 |

Esta é a rodada que vale para o requisito. As anteriores ficam como histórico:
a rodada 1 foi invalidada por quota e a rodada 2 usou outro modelo
(`gemini-3.1-flash-lite`). O índice de todas as rodadas está em
[`evidencias/README.md`](../README.md).

## Ambiente

| Campo | Valor |
| --- | --- |
| Data | 22/09/2026, 18:44 UTC |
| **Modelo** | **`gemini-3.7-flash`**, o mesmo configurado na bancada |
| Caminho da chamada | OpenRouter (ver abaixo) |
| Retries do provedor | 3, padrão de produção |
| Origem do RAG | Supabase, `public.source_extracts` |
| `RAG_MAX_SOURCES` | 3 |
| Código medido | base `81c787d` + alterações não commitadas; hash `1ef17e89…` em [`campanha-37flash/arvore-medida.md`](../campanha-37flash/arvore-medida.md) |

### Alcance do resultado

A bancada de teste usa o Gemini direto, no Free Tier, para não gerar custo. Esta
rodada chamou **o mesmo modelo** pelo OpenRouter, em plano pago, porque o Free
Tier limita a 20 requisições por dia e a amostra tem 24 perguntas.

O caminho da chamada não altera o que o RNF04 mede. Fundamentação e alucinação
dependem do modelo, do prompt e do contexto recuperado, e os três são idênticos
nos dois caminhos: o adaptador do OpenRouter envia **exatamente o mesmo texto**
que o Gemini direto recebe, o que está fixado pelo teste
`test_prompt_chega_identico_ao_que_o_gemini_receberia`.

O resultado vale, portanto, para o `gemini-3.7-flash`. No ambiente do Metrô, o
agente usará o Copilot Studio com modelos GPT; como fundamentação e alucinação
dependem do modelo, elas são medidas novamente na homologação, com esta mesma
amostra e o mesmo protocolo.

## Comandos

```bash
LLM_PROVIDER=openrouter .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

.venv/bin/python -m app.tests.rnf04.executar_rnf04 \
    --host http://127.0.0.1:8000 --saida evidencias/rnf04-v12-37flash \
    --tentativas-transitorias 3 --pausa 1

.venv/bin/python -m app.tests.rnf04.avaliar_rnf04 --evidencias evidencias/rnf04-v12-37flash
```

## Critério de fronteira: descrever a fonte ≠ atribuir ao projeto

Os casos negativos que mencionam o `PRJ-0442` exigiram um critério explícito,
porque o único extrato vinculado ao projeto na base é o comunicado "Operação
assistida na Linha Azul", que tem **vigência e status próprios**.

| Formulação | Rótulo | Por quê |
| --- | --- | --- |
| "as informações disponíveis **sobre o PRJ-0442** tratam da operação assistida entre 24/08 e 28/08" (N-01) | fundamentada | Descreve o que a base tem vinculado ao projeto. Correto. |
| "o texto informa **seu** status como Programado para 24/08 a 28/08", com "seu" = PRJ-0442 (N-06) | alucinação | Atribui ao projeto o status e o período do comunicado. O projeto está "em andamento", de 15/01 a 20/12/2026. |

A mesma fronteira foi aplicada na rodada 2, em que o caso equivalente também foi
rotulado como alucinação. Manter a leitura estrita nas duas rodadas é o que torna
os resultados comparáveis.

## Os três casos que não são "fundamentada"

### `RNF04-N-06` · alucinação (limítrofe, leitura estrita)

Recusa a comparação corretamente e declara que o `PRJ-0518` não existe. Mas
afirma que a fonte informa **o status do PRJ-0442 como "Programado" para
24/08–28/08/2026**. Status e período são do comunicado, não do projeto.

A causa provável é estrutural: a fonte chega ao prompt rotulada
`Comunicados de Servico / PRJ-0442`, o que aproxima o comunicado do projeto sem
indicar de qual entidade é cada atributo. O mesmo padrão apareceu na rodada 2
com outro modelo, o que reforça que a origem é o prompt, e não o modelo.

### `RNF04-N-05` · não fundamentada (truncada)

A resposta inteira é: *"Com base nos dados fictícios de demonstração
fornecidos, o contexto **não é suficiente** para"*. Termina no meio da frase.

Não afirma nada falso e sinaliza a limitação, por isso **não** é alucinação.
Poderia ser rotulada como fundamentada, já que declarar a ausência conta como
fundamentada. Foi rotulada de forma conservadora como `nao_fundamentada`, porque
não completa a resposta. Com a leitura leniente, a fundamentação seria 95,83%.

### `RNF04-N-04` · fundamentada, mas também truncada

A recusa está completa na primeira frase (*"o contexto fornecido não é
suficiente para responder quais riscos estão registrados para o projeto
PRJ-0442"*) e a resposta é cortada depois (*"O único registro"*). O trecho
entregue não afirma nada sem fonte.

## `DEF-RNF04-02` · respostas truncadas sem aviso

**2 de 24** respostas chegaram cortadas no meio e foram entregues como se
estivessem completas.

**Mecanismo confirmado:** no OpenRouter, os tokens de raciocínio do modelo
consomem o mesmo orçamento de `max_tokens` do texto visível. Numa chamada de
diagnóstico com o prompt da N-05, 245 dos 287 tokens de saída foram raciocínio.
A quantidade varia de 0 a 245+ entre chamadas idênticas.

**Confirmado depois, na 2ª rodada do RNF05:** com o motivo de parada registrado
em log, 36 de 451 respostas (8,0%) terminaram por `finish_reason=length` no
caminho do OpenRouter. Três reenvios isolados do prompt da N-05 tinham terminado
normalmente, o que é compatível com uma ocorrência de cerca de 1 em 12. As duas
truncagens desta rodada foram coletadas antes do registro existir.

**Correção aplicada após a rodada:** o adaptador do OpenRouter passou a registrar
em log toda resposta encerrada por `finish_reason=length`. Coberto por
`test_instrumentacao_rnf05.py`.

**Gemini direto.** O caminho usado pela bancada também não inspeciona o motivo
de parada. As 35 respostas coletadas por ele nas rodadas 1 (11) e 2 (24) foram
inspecionadas e nenhuma termina cortada, o que associa o truncamento ao
OpenRouter. A inspeção do motivo de parada nesse caminho é recomendação para a
Sprint 5.

## O que a correção do `DEF-RNF04-01` entregou

As perguntas sobre período de vigência, que na rodada 1 respondiam "contexto
insuficiente", agora respondem com a data certa:

| Caso | Rodada 1 | Rodada definitiva |
| --- | --- | --- |
| `P-07` operação assistida | "o contexto não é suficiente para informar o período" | "de **24/08/2026 a 28/08/2026**" |
| `P-10` comunicado República | "o contexto fornecido não é suficiente" | "até **05/09/2026** (vigência de 20/08 a 05/09)" |

## Caso-armadilha

`RNF04-N-11` (política para animais) recebeu entre as fontes a regra de
transporte de **bicicleta**. O agente não transpôs a regra e declarou a
ausência. Foi o mesmo comportamento da rodada 2: nas duas vezes em que o caso
rodou, em dois modelos diferentes, o agente resistiu à extrapolação. (Na rodada
1 os casos negativos se perderam por quota.)

## Limitações

1. **Margem estreita.** Um único caso a mais em qualquer direção reprova.
2. **Rotulagem não independente.** A planilha sai cega (sem cenário nem
   gabarito), mas quem rotulou foi quem construiu a amostra. Cada rótulo tem
   justificativa citando a fonte e pode ser auditado um a um. Mesmo assim, uma
   rotulagem feita por outro integrante daria garantia processual mais forte.
3. **Truncamento possivelmente específico do OpenRouter** (ver `DEF-RNF04-02`).
   Se for, a medição foi *pessimista* em relação à entrega: a N-05 contou contra
   a fundamentação por um defeito do caminho de teste.
4. **Massa pequena.** Nove extratos recuperáveis e um único projeto. O resultado
   não se extrapola para a base real do Metrô.
5. **Rodada anterior ao pool de conexões.** O pool só altera o tempo de acesso ao
   banco, não o conteúdo recuperado nem a resposta.

## Arquivos

| Arquivo | Conteúdo |
| --- | --- |
| `respostas.jsonl` | 24 respostas integrais, com fontes, intenção e tempos |
| `planilha_cega.csv` | 24 rótulos com justificativa por caso |
| `metricas.json` | Apuração com numerador e denominador |
| `ambiente.json` | Ficha da rodada, com provedor, modelo e retries corrigidos |

Nenhum arquivo contém chave, token ou string de conexão.
