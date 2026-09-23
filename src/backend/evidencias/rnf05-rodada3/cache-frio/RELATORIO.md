# RNF05 — 3ª rodada, janelas com cache frio · 23/09/2026

Issue [#231](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/231) (S4-35).
Protocolo congelado às 01:20 UTC, antes de iniciar a API:
[`PROTOCOLO-CONGELADO.md`](PROTOCOLO-CONGELADO.md). Mesmo código da 3ª rodada
(hash `71ee4895…`, conferido antes e depois), mesmo modelo e mesma massa.

## Resultado

> ## ✅ APROVADO também com cache frio
>
> | Janela | Rota | Amostras | Falhas | P95 | Teto | Veredito |
> | --- | --- | ---: | ---: | ---: | ---: | --- |
> | 1 usuário, 35 min | simples | 208 | 0 | 7.600 ms | 10.000 | ✅ aprovado |
> | 1 usuário, 35 min | comparação | 64 | 0 | 8.300 ms | 20.000 | ✅ aprovado |
> | 5 usuários, 8 min | simples | 239 | 0 | 7.000 ms | 10.000 | ✅ aprovado |
> | 5 usuários, 8 min | comparação | 86 | 0 | 7.400 ms | 20.000 | ✅ aprovado |
>
> Apurado por `apurar_rnf05.py` ([`apuracao.txt`](apuracao.txt)). Nenhuma das 597
> requisições falhou.

Cada janela começou com a API recém-reiniciada e sem `aquecer.py`: pool de
conexões vazio e nenhuma conexão aberta com o provedor.

## Onde o cache frio pesa

Na primeira requisição depois de cada reinício, e só nela:

| Janela | Primeira requisição, cliente | Primeira requisição, pipeline | Referência já sem o custo do primeiro acesso |
| --- | ---: | ---: | --- |
| 1 usuário | 7.152 ms | 5.070 ms | a mesma pergunta, 16 s depois: 3.477 ms de pipeline |
| 5 usuários | 5.792 ms | 4.049 ms | mediana de pipeline da janela: 3.398 ms |

O custo do primeiro acesso fica entre 0,6 s e 1,6 s de pipeline, compatível com a
abertura da primeira conexão do pool com o banco e da primeira conexão com o
provedor. Nas duas janelas, a primeira requisição ficou abaixo do teto de 10 s.

Diluído em 35 e 8 minutos, esse custo não aparece no P95: as janelas frias ficaram
no mesmo patamar das quentes da 3ª rodada (P95 simples de 7,6 s e 7,3 s com cache
quente).

## Outros registros

- **Rastreabilidade completa.** 273 e 329 registros de auditoria para 272 e 325
  respostas; os excedentes, 1 e 4, são as requisições em andamento quando cada
  janela do Locust terminou.
- **Nenhuma nova tentativa contra o provedor**, nenhuma falha ao gravar a
  rastreabilidade e nenhuma consulta cancelada pelo limite de 5 s.
- **Respostas truncadas:** 36 de 597 (6,0%), pelo mecanismo do `DEF-RNF04-02`.

Resumo do log: [`api-log-resumo.txt`](api-log-resumo.txt).

```sql
select created_at, processing_ms, route_taken
from public.ai_interactions
where created_at >= '2026-09-23 01:20:39+00'
order by created_at
limit 3;
```

## Ressalva da rota comparativa

A mesma da 3ª rodada: com um único projeto na massa, o P95 comparativo mede o
pedido de comparação tratado com a limitação declarada, e não uma comparação
produzida. Ver [`../RELATORIO.md`](../RELATORIO.md#alcance).

## Arquivos

| Caminho | Conteúdo |
| --- | --- |
| `PROTOCOLO-CONGELADO.md` | Método e regra de decisão, gravados antes da execução |
| `baseline/`, `carga/` | Ficha de ambiente (`modalidade_de_cache: frio`), CSVs e log do Locust |
| `apuracao.txt` | Saída do `apurar_rnf05.py` |
| `api-log-resumo.txt` | Contagens do log da API |
