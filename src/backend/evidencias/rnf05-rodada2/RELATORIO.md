# RNF05 — 2ª rodada · 22/09/2026

Protocolo revisado da Seção 9.2.4 do `Projeto.md`, congelado às 20:46 UTC, antes da
execução: [`PROTOCOLO-CONGELADO.md`](PROTOCOLO-CONGELADO.md).
Modelo `gemini-3.7-flash`, o mesmo configurado na bancada de teste, em plano pago.

## Resultado

> ## ❌ NÃO ATENDIDO — por dois critérios
>
> | Rodada | Rota | Amostras | Falhas | P95 | Teto | Veredito |
> | --- | --- | ---: | ---: | ---: | ---: | --- |
> | 1 usuário, 25 min | simples | 123 | **1** | 9.300 ms | 10.000 | ❌ reprovado: erro |
> | 1 usuário, 25 min | comparação | 41 | 0 | 12.000 ms | 20.000 | ✅ aprovado |
> | 5 usuários, 8 min | simples | 202 | 0 | **11.000 ms** | **10.000** | ❌ reprovado: P95 acima do teto |
> | 5 usuários, 8 min | comparação | 72 | 0 | 11.000 ms | 20.000 | ✅ aprovado |
>
> Apurado por `apurar_rnf05.py` ([`apuracao.txt`](apuracao.txt)). Todas as rotas
> tiveram as 40 amostras exigidas, então a rodada é conclusiva.
>
> `CT-RNF05-N` foi **validado**: 50 requisições, todas entre 30,1 s e 34,2 s.

A 1ª rodada ([`rnf05-37flash/`](../rnf05-37flash/RELATORIO.md)) continua registrada
como não atendida. As duas rodadas reprovaram, por motivos diferentes.

## A causa: a gravação de auditoria está no caminho da resposta

A rastreabilidade do RNF03 grava no banco o tempo que o pipeline levou em cada
interação (`ai_interactions.processing_ms`). Comparar esse tempo com o que o cliente
mediu separa o custo do sistema do custo do que vem depois dele:

| Rodada | Pipeline — mediana | Pipeline — P95 | Cliente — mediana | Cliente — P95 (simples) |
| --- | ---: | ---: | ---: | ---: |
| 1 usuário | 4.032 ms | 6.548 ms | 6.300 ms | 9.300 ms |
| 5 usuários | 3.920 ms | 6.933 ms | 6.300 ms | 11.000 ms |

O pipeline — classificação, recuperação e geração pelo LLM — tem **P95 de 6,5 a
6,9 s**, dentro do teto de 10 s, inclusive com cinco usuários. A diferença de cerca
de **2,3 s na mediana e de 3 a 4 s no P95** está no que acontece depois do pipeline
e antes de a resposta sair: a gravação síncrona da auditoria no Supabase, com
dezenas de idas e voltas a um servidor nos EUA.

É essa etapa que leva a consulta simples acima do teto sob carga.

```sql
select percentile_cont(0.95) within group (order by processing_ms)
from public.ai_interactions
where created_at between '2026-09-22 21:13:00+00' and '2026-09-22 21:21:00+00';
```

## O erro da linha de base

Às 20:57:02 UTC, uma consulta simples não respondeu em 60 s, o tempo máximo de
espera do cliente, e o Locust a registrou como falha (`HTTP 0`).

Os registros mostram que ela **não** travou no LLM:

- nenhuma nova tentativa contra o provedor foi registrada na rodada inteira;
- nenhuma interação da rodada passou de 24,8 s de pipeline;
- a API respondeu `200` a todas as 451 requisições, inclusive a essa, depois que o
  cliente já tinha desistido;
- o banco tem 163 registros de rastreabilidade para as 164 requisições da janela;
- o log registra uma falha ao gravar a rastreabilidade do RNF03 e duas conexões
  devolvidas ao pool com consulta ainda em andamento (estado `ACTIVE`).

Leitura: uma gravação de auditoria ficou presa no banco, falhou, e a falha foi
tratada. A resposta chegou certa, mas tarde demais. As consultas ao banco não têm
limite de tempo, então um problema de rede segura a resposta ao usuário sem prazo.
Conexões mantidas ociosas no pool podem ser derrubadas pelo *pooler* do Supabase
sem aviso, e o registro não permite separar essa causa de uma falha de rede comum.

Resumo do log, sem identificadores de infraestrutura:
[`api-log-resumo.txt`](api-log-resumo.txt).

## Correções que os dados indicam

| Correção | Efeito esperado |
| --- | --- |
| Limite de tempo nas consultas ao banco (`statement_timeout`) e *keepalive* de TCP nas conexões | Uma gravação presa deixa de segurar a resposta; o erro de 60 s não se repete |
| Gravar a auditoria fora do caminho da resposta, por fila ou tarefa em segundo plano | Remove de 2 a 4 s da latência percebida; encaixa no sistema de mensageria previsto para a Sprint 5 |
| Reunir as inserções da auditoria em uma única ida ao banco | Reduz o custo da gravação síncrona, caso ela continue no caminho |

A segunda correção muda a semântica da auditoria do RNF03, já verificada nos
testes desse requisito, e por isso é decisão do grupo.

## Outros registros da rodada

- **Nenhuma nova tentativa contra o provedor.** O travamento que explicou a
  requisição de 37,7 s da 1ª rodada não se repetiu.
- **Respostas truncadas:** 36 de 451 respostas (8,0%) terminaram por limite de
  tokens (`finish_reason=length`) no caminho do OpenRouter. Isso confirma o
  mecanismo do `DEF-RNF04-02`: o raciocínio do modelo consome o mesmo orçamento de
  512 tokens do texto. Não afeta o RNF05, que mede tempo, e sim a completude das
  respostas nesse caminho.
- **Duplo do cenário negativo corrigido:** a menor latência da rodada negativa foi
  30,1 s, então todos os prompts de comparação receberam o atraso, inclusive o que
  escapava da versão anterior.

## Ambiente

| Campo | Valor |
| --- | --- |
| Janela | 22/09/2026, 20:46 a 21:27 UTC |
| Modelo | `google/gemini-3.7-flash`, pelo OpenRouter, plano pago |
| Retentativas / *timeout* do provedor | 3 / 30 s, padrão de produção |
| Pool de conexões | ligado |
| Aquecimento | 14 prompts antes da janela, todos `200` |
| Máquina | Apple M5 Pro, 18 núcleos, 48 GB |
| Código medido | hash `10f53523…`, manifesto em [`PROTOCOLO-CONGELADO.md`](PROTOCOLO-CONGELADO.md) |

## Arquivos

| Caminho | Conteúdo |
| --- | --- |
| `PROTOCOLO-CONGELADO.md` | Critérios, método e impressão digital do código, gravados antes da execução |
| `baseline/`, `carga/`, `violacao/` | Ficha de ambiente, CSVs e log do Locust de cada rodada |
| `aquecimento.log` | Os 14 prompts de aquecimento |
| `apuracao.txt` | Saída do `apurar_rnf05.py` |
| `api-log-resumo.txt` | Contagens e linhas relevantes do log da API, sem identificadores |
