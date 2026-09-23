# RNF05 — 3ª rodada · 22/09/2026

Issue [#231](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/231) (S4-35).
Protocolo revisado da Seção 9.2.4 do `Projeto.md`, congelado às 22:22 UTC, antes da
execução: [`PROTOCOLO-CONGELADO.md`](PROTOCOLO-CONGELADO.md).
Modelo `gemini-3.7-flash`, o mesmo das rodadas anteriores, em plano pago.

## Resultado

> ## ✅ ATENDIDO
>
> | Rodada | Rota | Amostras | Falhas | P95 | Teto | Veredito |
> | --- | --- | ---: | ---: | ---: | ---: | --- |
> | 1 usuário, 35 min | simples | 181 | 0 | 7.600 ms | 10.000 | ✅ aprovado |
> | 1 usuário, 35 min | comparação | 82 | 0 | 8.400 ms | 20.000 | ✅ aprovado |
> | 5 usuários, 8 min | simples | 245 | 0 | 7.300 ms | 10.000 | ✅ aprovado |
> | 5 usuários, 8 min | comparação | 78 | 0 | 7.600 ms | 20.000 | ✅ aprovado |
>
> Apurado por `apurar_rnf05.py` ([`apuracao-final.txt`](apuracao-final.txt)). Todas
> as rotas tiveram as 40 amostras exigidas e nenhuma requisição falhou.
>
> `CT-RNF05-N` foi **validado**: 50 requisições, todas entre 29,4 s e 34,3 s, P95 de
> 34,0 s contra o teto de 20 s. A medição enxerga a violação.

As rodadas anteriores continuam registradas como não atendidas:
[1ª rodada](../rnf05-37flash/RELATORIO.md) e [2ª rodada](../rnf05-rodada2/RELATORIO.md).

## Cache frio

As janelas acima são de cache quente: API reiniciada e aquecida antes da medição.
Com o mesmo código, a API foi medida também **com cache frio** — reiniciada e
medida direto, sem aquecimento —, com protocolo próprio congelado antes:

| Janela fria | Rota | Amostras | Falhas | P95 | Veredito |
| --- | --- | ---: | ---: | ---: | --- |
| 1 usuário, 35 min | simples | 208 | 0 | 7.600 ms | ✅ aprovado |
| 1 usuário, 35 min | comparação | 64 | 0 | 8.300 ms | ✅ aprovado |
| 5 usuários, 8 min | simples | 239 | 0 | 7.000 ms | ✅ aprovado |
| 5 usuários, 8 min | comparação | 86 | 0 | 7.400 ms | ✅ aprovado |

O custo do cache frio aparece só na primeira requisição depois do reinício, de
0,6 s a 1,6 s de pipeline, e não chega ao P95. Detalhe em
[`cache-frio/RELATORIO.md`](cache-frio/RELATORIO.md).

## O que mudou desde a 2ª rodada

Uma única correção no código, feita depois da 2ª rodada e antes do congelamento:
limite de 5 s por consulta ao banco (`statement_timeout`) e *keepalive* de TCP nas
conexões, em `app/database/connection.py`. É a primeira das correções indicadas
no `DEF-RNF05-02`. A gravação da auditoria do RNF03 continua síncrona, no caminho
da resposta.

## A linha de base foi estendida

A linha de base de 25 minutos terminou com 37 amostras comparativas. A proporção
de 75/25 é sorteada a cada requisição, e o protocolo exige 40. Pela regra 2, a
linha de base ficou **inconclusiva** ([`apuracao.txt`](apuracao.txt)).

A forma da extensão foi registrada em
[`EXTENSAO-LINHA-DE-BASE.md`](EXTENSAO-LINHA-DE-BASE.md) às 22:50 UTC, antes de o
resultado da carga ser conhecido: uma nova janela de 35 minutos, com o mesmo
código, em que um erro em qualquer das duas janelas reprovaria a linha de base e
sem direito a uma terceira janela. O Locust exporta percentis, e não o tempo de
cada requisição, por isso as duas janelas não podem ser reunidas num P95 único.

| Janela | Rota | Amostras | Falhas | P95 | Situação |
| --- | --- | ---: | ---: | ---: | --- |
| 25 min | simples | 159 | 0 | 7.600 ms | aprovado |
| 25 min | comparação | **37** | 0 | 8.200 ms | inconclusivo |
| 35 min | simples | 181 | 0 | 7.600 ms | aprovado |
| 35 min | comparação | 82 | 0 | 8.400 ms | aprovado |

Nenhuma das 459 requisições das duas janelas falhou.

## Onde está o ganho

A comparação entre o tempo que o pipeline gravou na auditoria
(`ai_interactions.processing_ms`) e o tempo medido pelo cliente, como na 2ª
rodada, com todas as rotas juntas:

| Janela | Cliente — mediana | Pipeline — mediana | Distância | Cliente — P95 | Pipeline — P95 | Distância |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2ª rodada, 5 usuários | 6.400 ms | 3.920 ms | 2.480 ms | 11.000 ms | 6.933 ms | **4.067 ms** |
| 3ª rodada, 1 usuário, 25 min | 5.600 ms | 3.589 ms | 2.011 ms | 7.800 ms | 5.717 ms | 2.083 ms |
| 3ª rodada, 5 usuários | 5.300 ms | 3.496 ms | 1.804 ms | 7.300 ms | 5.519 ms | **1.781 ms** |
| 3ª rodada, 1 usuário, 35 min | 5.800 ms | 3.672 ms | 2.128 ms | 8.100 ms | 6.109 ms | 1.991 ms |

Sob carga, o P95 do cliente caiu 3,7 s. Duas coisas mudaram ao mesmo tempo:

- **O pipeline ficou mais rápido**: P95 de 5,5 a 6,1 s, contra 6,5 a 6,9 s na 2ª
  rodada, cerca de 1,4 s do ganho sob carga. O tempo do pipeline inclui a chamada
  ao LLM, cuja latência varia de uma hora para outra, e a recuperação no banco, que
  usa as mesmas conexões do pool. A auditoria não grava essas etapas em separado,
  e a rodada não distingue quanto veio de cada uma.
- **A cauda depois do pipeline encolheu**: a distância entre os P95 caiu de 4,1 s
  para 1,8 s. Isso é compatível com o *keepalive*, que mantém vivas as conexões
  ociosas do pool em vez de deixá-las ser derrubadas e reabertas no caminho da
  resposta. A rodada também não isola essa causa: o pool não registra reconexões.

O limite de 5 s não chegou a ser acionado: nenhuma consulta foi cancelada. Zero
erro nesta rodada significa que nenhuma gravação ficou presa, e não que o limite
evitou uma. Ele foi verificado à parte, contra o Supabase: uma consulta de 6 s é
cancelada pelo servidor em 5,3 s.

A gravação síncrona da auditoria **continua custando cerca de 2 s** na mediana. A
margem da consulta simples sob carga é de 2,7 s até o teto.

```sql
select count(*),
       percentile_cont(0.5)  within group (order by processing_ms),
       percentile_cont(0.95) within group (order by processing_ms)
from public.ai_interactions
where created_at >= '2026-09-22 22:49:36+00' and created_at < '2026-09-22 22:57:36+00';
```

## Outros registros da rodada

- **Rastreabilidade completa.** O banco tem 870 registros de auditoria para as 860
  respostas da campanha. Os 10 a mais são as requisições em andamento quando cada
  janela do Locust terminou — 1, 3, 5 e 1, nas quatro janelas: o cliente
  desconectou, o servidor concluiu o processamento e gravou a auditoria, e o
  uvicorn não registra resposta a cliente desconectado. Nenhuma requisição ficou
  sem registro, e o log não tem nenhuma falha ao gravar a rastreabilidade do RNF03.
- **Nenhuma nova tentativa contra o provedor**, em 860 respostas.
- **Respostas truncadas:** 50 de 860 (5,8%) terminaram por limite de tokens no
  caminho do OpenRouter, pelo mecanismo do `DEF-RNF04-02`. Não afeta o RNF05, que
  mede tempo.
- **Código conferido depois da execução:** o hash de `src/backend/app` e o do
  registro da extensão são os mesmos de antes.

Resumo do log: [`api-log-resumo.txt`](api-log-resumo.txt).

## Ambiente

| Campo | Valor |
| --- | --- |
| Janela | 22/09/2026, 22:22 a 23:40 UTC |
| Modelo | `google/gemini-3.7-flash`, pelo OpenRouter, plano pago |
| Retentativas / *timeout* do provedor | 3 / 30 s, padrão de produção |
| Banco | pool de conexões ligado, limite de 5 s por consulta, *keepalive* de TCP |
| Aquecimento | 14 prompts antes de cada linha de base, todos `200` |
| Máquina | Apple M5 Pro, 18 núcleos, 48 GB |
| Código medido | hash `71ee4895…`, manifesto em [`PROTOCOLO-CONGELADO.md`](PROTOCOLO-CONGELADO.md) |

## Alcance

**Ressalva da rota comparativa.** A massa tem um único projeto, o `PRJ-0442`, e
a comparação entre projetos foi adiada para a Sprint 5. Os prompts comparativos
pedem a comparação com o `PRJ-0518`, que não existe: o P95 comparativo mede o
sistema tratando o pedido e declarando a limitação, com chamada ao LLM, e **não**
demonstra o teto de 20 s para uma comparação produzida. A ressalva completa está
no cabeçalho de `app/tests/performance/prompts.py`.

O resultado vale para o sistema medido com o `gemini-3.7-flash` em provedor
pago. No ambiente do Metrô, com o Copilot Studio e modelos GPT, a latência
depende do modelo e da infraestrutura adotados e é medida novamente na
homologação, com a mesma massa e o mesmo protocolo.

## Arquivos

| Caminho | Conteúdo |
| --- | --- |
| `PROTOCOLO-CONGELADO.md` | Critérios, método e impressão digital do código, gravados antes da execução |
| `EXTENSAO-LINHA-DE-BASE.md` | Regra da extensão, gravada antes de conhecer o resultado da carga |
| `baseline/` | Linha de base de 25 minutos, inconclusiva |
| `baseline-estendida/` | Linha de base de 35 minutos e o seu aquecimento |
| `carga/`, `violacao/` | Ficha de ambiente, CSVs e log do Locust de cada rodada |
| `aquecimento.log` | Os 14 prompts de aquecimento da primeira linha de base |
| `apuracao.txt` | Apuração com a linha de base de 25 minutos: inconclusivo |
| `apuracao-final.txt` | Apuração com a linha de base estendida: atendido |
| `api-log-resumo.txt` | Contagens do log da API |
| `cache-frio/` | Janelas de 1 e 5 usuários com cache frio, com protocolo, CSVs, apuração e relatório próprios |
