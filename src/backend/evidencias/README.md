# Evidências dos testes de RNF — Sprint 4

Issues [#230](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/230)
(RNF04) e [#231](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/231)
(RNF05). Planejamento na Seção 9.2 do [`Projeto.md`](../../../docs/Projeto.md).

## Resultado

| Requisito | Resultado | Rodada que vale |
| --- | :---: | --- |
| **RNF04** — fundamentação ≥ 90% e alucinação ≤ 5% | ✅ **aprovado** (91,67% · 4,17%) | [`rnf04-v12-37flash/`](rnf04-v12-37flash/RELATORIO.md) |
| **RNF05** — P95 simples ≤ 10 s e comparativo ≤ 20 s, zero erros | ✅ **atendido na 3ª rodada**, com cache quente e com cache frio (P95 simples de 7,0 a 7,6 s nas quatro janelas; zero erro). O P95 comparativo mede pedidos de comparação tratados com a limitação declarada, porque a massa tem um único projeto. A 1ª e a 2ª rodadas continuam registradas como não atendidas | [`rnf05-rodada3/`](rnf05-rodada3/RELATORIO.md) |

**Entre as rodadas do RNF05.** Os tetos nunca foram alterados. O protocolo foi revisado
antes da 2ª rodada: mínimo de 40 amostras por tipo de consulta, porque com 10 amostras o
P95 do Locust é a pior requisição. A 2ª rodada, conclusiva, reprovou por um erro e por P95
simples de 11,0 s sob carga, e mostrou que a gravação síncrona da auditoria do RNF03 é o
que levava o total acima do teto (`DEF-RNF05-02`). Antes da 3ª rodada entrou uma única
correção: limite de 5 s por consulta ao banco e *keepalive* de TCP nas conexões. Na 3ª
rodada, a distância entre o P95 do cliente e o do pipeline caiu de 4,1 s para 1,8 s sob
carga. Origem das metas e registro da revisão no `Projeto.md`, Seções 3.2.2 e 9.2.4.

As rodadas definitivas usam o **`gemini-3.7-flash`**, o modelo configurado
na bancada de teste, chamado pelo OpenRouter em plano pago. A bancada roda no Free
Tier do Gemini para não gerar custo, e esse plano limita a 20 requisições por dia
e impõe piso de 15 a 37 s por chamada, que não é característica do sistema.

No ambiente do Metrô, o agente usará o Copilot Studio com modelos GPT. Os
resultados abaixo valem para o modelo medido; fundamentação e latência dependem
do modelo e são medidas novamente na homologação, com a mesma amostra e o mesmo
protocolo.

## Código medido

A 3ª rodada do RNF05, com cache quente e frio, mediu a árvore de `src/backend/app`
do commit `d33d691`, cuja impressão digital é `71ee4895…`, a mesma gravada no
[protocolo congelado](rnf05-rodada3/PROTOCOLO-CONGELADO.md) antes da execução. O
commit está na branch `test/executar-rnf04-rnf05`, que recebeu a `develop` depois
por merge, sem reescrever os commits medidos. Enquanto ele existir no repositório,
a conferência é, a partir da raiz:

```bash
git ls-tree -r --name-only d33d691 -- src/backend/app | LC_ALL=C sort \
  | while read f; do printf '%s  %s\n' "$(git show "d33d691:$f" | shasum -a 256 | cut -d' ' -f1)" "$f"; done \
  | shasum -a 256
```

Como o grupo integra os merge requests com *squash*, o commit pode deixar de existir
depois da integração. A referência que não depende dele é o manifesto por arquivo do
protocolo congelado: comparado com a `develop`, mostra arquivo a arquivo o que mudou
depois da medição.

## Todas as rodadas, em ordem

Nenhuma rodada foi apagada. As que não valem continuam aqui, com o motivo.

| Diretório | Data | Modelo | Situação |
| --- | --- | --- | --- |
| [`rnf04-81c787d/`](rnf04-81c787d/RELATORIO.md) | 21/09 | `gemini-3.7-flash` direto | **Invalidada.** 13 de 24 perdidas por quota (HTTP 429). Expôs o `DEF-RNF04-01`. |
| [`rnf05-81c787d/`](rnf05-81c787d/RELATORIO.md) | 21/09 | `gemini-3.7-flash` direto | **Não executada.** Validação do `locustfile` e leitura das latências incidentais, contaminadas por backoff de retry. |
| `rnf04-v12-parte1/` | 22/09 | `gemini-3.7-flash` direto | **Invalidada.** 18 de 18 perdidas por quota. Sem relatório: não há resposta a analisar. |
| [`rnf04-v12-flashlite/`](rnf04-v12-flashlite/RELATORIO.md) | 22/09 | `gemini-3.1-flash-lite` direto | Aprovada (95,83% · 4,17%), **em outro modelo**. Superada pela definitiva. |
| [`rnf05-baseline-flashlite/`](rnf05-baseline-flashlite/RELATORIO.md) | 22/09 | `gemini-3.1-flash-lite` direto | Reprovada no Free Tier. Contém a **medição de controle** do piso do provedor (15 a 37 s por chamada trivial). |
| [`rnf04-v12-37flash/`](rnf04-v12-37flash/RELATORIO.md) | 22/09 | `gemini-3.7-flash` via OpenRouter | ✅ **Definitiva do RNF04.** |
| [`rnf05-37flash/`](rnf05-37flash/RELATORIO.md) | 22/09 | `gemini-3.7-flash` via OpenRouter | ❌ **1ª rodada do RNF05.** Inclui a execução descartada em `descartada-aquecimento-na-janela/`. |
| [`rnf05-rodada2/`](rnf05-rodada2/RELATORIO.md) | 22/09 | `gemini-3.7-flash` via OpenRouter | ❌ **2ª rodada do RNF05**, com protocolo congelado antes da execução. Conclusiva. |
| [`rnf05-rodada3/`](rnf05-rodada3/RELATORIO.md) | 22/09 | `gemini-3.7-flash` via OpenRouter | ✅ **3ª rodada do RNF05**, com protocolo congelado antes da execução. Linha de base estendida pela regra de amostra mínima, registrada antes do resultado da carga. |
| [`rnf05-rodada3/cache-frio/`](rnf05-rodada3/cache-frio/RELATORIO.md) | 23/09 | `gemini-3.7-flash` via OpenRouter | ✅ **3ª rodada, cache frio**: API reiniciada e medida sem aquecimento, com 1 e 5 usuários. Mesmo código da 3ª rodada. |
| [`campanha-37flash/`](campanha-37flash/arvore-medida.md) | 22/09 | — | Impressão digital do código medido nas rodadas definitivas. |
| [`graficos_rnf05.ipynb`](graficos_rnf05.ipynb) | 22/09 | — | Gera as Figuras 27 e 28 do `Projeto.md` a partir dos CSVs do Locust deste diretório. |

## Defeitos encontrados

| ID | Severidade | Situação | Onde |
| --- | :---: | --- | --- |
| `DEF-RNF04-01` | alta | ✅ corrigido | Vigência, status e linha do extrato não chegavam ao prompt do LLM |
| `DEF-RNF04-02` | média | ⚠️ mecanismo confirmado, registrado em log | Respostas truncadas pelo limite de tokens entregues sem aviso; 8,0% das respostas da 2ª rodada e 5,8% das da 3ª no caminho do OpenRouter; nenhuma nas 35 do Gemini direto |
| `DEF-RNF05-02` | alta | ⚠️ parcialmente corrigido | Auditoria do RNF03 gravada de forma síncrona no caminho da resposta. Sob carga, na 2ª rodada: +2,5 s na mediana e +4,1 s no P95, e uma gravação presa segurou uma resposta por mais de 60 s. Corrigido: limite de 5 s por consulta e *keepalive*; na 3ª rodada, +1,8 s na mediana e no P95 sob carga, sem erro. Pendente: tirar a gravação do caminho da resposta, decisão do grupo |
| `DEF-RNF05-01` | — | característica da bancada | Piso de latência do Free Tier, usado na bancada por custo, acima do teto do requisito; as rodadas foram medidas com provedor pago |
| — | alta | ✅ corrigido | Duas conexões novas com o Supabase por requisição, ~2 s; pool de conexões reduziu ~1,2 s |
| — | média | ✅ corrigido | 21 testes do backend falhavam quando havia `.env` configurado |

## Nenhum segredo

Nenhum arquivo deste diretório contém chave, token, senha ou string de conexão.
As fichas de ambiente registram só se cada variável **estava presente**, nunca o
valor. Verificado por varredura antes de cada publicação.
