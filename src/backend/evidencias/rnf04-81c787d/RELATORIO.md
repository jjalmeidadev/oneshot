# RNF04 — rodada 1 · 21/09/2026 · commit `81c787d`

Casos `CT-RNF04-P` e `CT-RNF04-N` da Seção 9.2 do `Projeto.md`.

> **Histórico.** Rodada superada. A definitiva está em
> [`rnf04-v12-37flash/`](../rnf04-v12-37flash/RELATORIO.md); o índice de todas as rodadas, em
> [`evidencias/README.md`](../README.md).

## Resultado

> ## 🚫 RODADA INVALIDADA — não mede o requisito
>
> **13 das 24 perguntas não obtiveram resposta.** O provedor do LLM devolveu
> HTTP 429 (quota diária esgotada) a partir da décima segunda pergunta e não se
> recuperou. Restaram 11 pontos, abaixo do mínimo de 20 que a Seção 9.2.3 exige.
>
> **O RNF04 permanece NÃO EXECUTADO.** Nenhum número desta rodada pode ser
> apresentado como taxa de fundamentação ou de alucinação do produto.

## Ambiente

| Campo | Valor |
| --- | --- |
| Commit | `81c787d` |
| Data | 21/09/2026, 20:08 UTC |
| Sistema | Darwin 25.6.0 (arm64) |
| Python | 3.13.15 |
| Modelo | `gemini-3.7-flash` |
| Origem do RAG | banco — `public.source_extracts` no Supabase |
| `RAG_MAX_SOURCES` | 3 |
| Amostra | v1.0 (24 perguntas) |

> A ficha `ambiente.json` gravada durante a rodada estava **incorreta**: o
> coletor não carregava o `.env` e descreveu o próprio processo em vez da API.
> O arquivo foi anotado com a correção e a causa; o instrumento foi corrigido
> para as rodadas seguintes. Os valores acima são os reais, e a justificativa
> de como se sabe disso está em `ambiente.json`.

## Comandos

```bash
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
.venv/bin/python -m app.tests.rnf04.executar_rnf04 \
    --host http://127.0.0.1:8000 --saida evidencias/rnf04-81c787d
```

## O que aconteceu

| Faixa | Resultado |
| --- | --- |
| P-01 a P-11 | HTTP 200, resposta completa com fontes |
| P-12 em diante (13 casos) | HTTP 429 do provedor, sem resposta |

O log da API registra 24 ocorrências de `429 Too Many Requests`. A quota não se
recuperou após 20 minutos de tentativas espaçadas, o que caracteriza limite
**diário** e não limite por minuto.

**Os 13 casos perdidos incluem os 12 cenários negativos inteiros.** Essa é a
razão principal de a rodada não valer: o cenário negativo é justamente o que
mede alucinação. Sobraram só casos positivos, e nenhum deles pressiona o agente
a inventar. Um resultado apurado sobre esse recorte pareceria excelente e não
diria nada sobre o requisito.

## Leitura preliminar dos 11 casos coletados

Não vale como medição. Serve para orientar a reexecução.

| Rótulo | Casos |
| --- | ---: |
| `fundamentada` | 11 |
| `alucinacao` | 0 |
| `nao_fundamentada` | 0 |

Todas as onze respostas citaram `[Fonte N]`, trouxeram o aviso de dado fictício
e não afirmaram nada que a fonte não sustentasse. Duas delas (`P-07` e `P-10`)
declararam corretamente que o contexto era insuficiente — e foi isso que expôs
o defeito abaixo.

## Defeito encontrado

### `DEF-RNF04-01` · severidade alta · metadados não chegam ao prompt

`build_rag_input` ([`app/rag/sharepoint.py:143`](../../app/rag/sharepoint.py))
monta cada bloco `[Fonte N]` com `title`, `list_name`, `last_modified` e
`content`. Os campos `ValidadeInicio`, `ValidadeFim`, `Status`, `Linha` e
`Categoria` vivem em `source_extracts.metadata` e **são descartados antes do
prompt**.

Consequência observada: perguntado sobre o período da operação assistida na
Linha 1-Azul, o agente recuperou o extrato correto e respondeu que "o contexto
não é suficiente para informar o período completo de datas". As datas
24/08/2026 e 28/08/2026 estavam no registro recuperado, em `metadata.validity`.

O comportamento é **correto sob o RNF04** — o agente não inventou — e
**insuficiente sob o RNF07**, porque o usuário não tem como saber que o dado
existe e foi descartado no caminho. Atinge diretamente "Cronograma", uma das
três prioridades declaradas do MVP.

### ✅ Corrigido depois desta rodada

`build_rag_input` passou a incluir vigência, status, linha e categoria no bloco
`[Fonte N]`. Verificado contra o Supabase real — o prompt agora carrega:

```
[Fonte 1] Operacao assistida na Linha Azul
Lista: Comunicados de Servico / PRJ-0442
Atualizado em: 2026-08-01 12:00:00+00:00
Vigencia: de 2026-08-24 a 2026-08-28
Status: Programado
Linha: Linha 1-Azul
Categoria: Operacao
Conteudo: Durante o periodo ficticio, o intervalo entre trens podera ser ...
```

Dez testes de regressão em `app/tests/test_rag_atributos_no_prompt.py` fixam o
comportamento, incluindo o caso de atributos vazarem para o bloco da fonte
errada. A alteração toca a recuperação do RAG, desenvolvida por outro integrante, e
precisa ser comunicada antes do merge.

**A reclassificação de `P-07` e `P-10` para negativo permanece na amostra v1.1.**
Ela descreve o comportamento observado na rodada 1 e é o registro de que o
defeito existiu. Na próxima rodada, com a correção aplicada, as duas perguntas
devem passar a ser respondidas — e aí a amostra sobe para v1.2 reclassificando-as
de volta para positivo, com a mudança registrada no histórico de versões.

## Bloqueio para a reexecução

**Limite de 20 requisições por dia.** O provedor devolveu a restrição
textualmente:

```
Rate limit exceeded for model gemini-3.7-flash
(limit: 20 requests per day on Free Tier)
```

A amostra tem 24 perguntas. Mesmo com `GEMINI_MAX_RETRIES=0`, que faz cada
pergunta custar exatamente uma chamada, **ela não cabe em um único dia**. Com o
retry padrão de 3, uma pergunta consome até 4 unidades — foi o que esgotou a
quota na décima segunda.

Duas saídas, nesta ordem:

1. **chave com tier pago.** Resolve RNF04 e RNF05 de uma vez e é a única que
   viabiliza as rodadas de carga do RNF05;
2. **amostra em dois dias**, 12 perguntas por dia, com `GEMINI_MAX_RETRIES=0`,
   versão da amostra e commit congelados entre os dois dias. A Seção 9.2.1 não
   proíbe, desde que massa e critério não mudem. Fecha o RNF04, **não** o RNF05.

O que **não** é aceitável: encolher a amostra para caber em 20. A Seção 9.2.3
exige no mínimo 20 perguntas, e ajustar a massa ao limite da ferramenta seria
mudar o teste para ele passar, em vez de medir o produto.

O parâmetro `--pausa` foi adicionado ao coletor para espaçar as chamadas quando
o limite for por minuto em outro plano.

## Arquivos

| Arquivo | Conteúdo |
| --- | --- |
| `respostas.jsonl` | 24 registros: 11 com resposta e fontes, 13 com o erro |
| `planilha_cega.csv` | 24 linhas para rotulagem, sem o gabarito |
| `ambiente.json` | Ficha da rodada, com a correção anotada |

Nenhum arquivo contém chave, token ou string de conexão. Verificado por
varredura antes da publicação.
