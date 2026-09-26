# RNF05 — 3ª rodada: janelas com cache frio, protocolo congelado antes da execução

**Congelado em:** 2026-09-23T01:20Z, antes de iniciar qualquer instância da API.
**Código medido:** o mesmo da 3ª rodada, conferido agora — hash de `src/backend/app`
`71ee4895d5c3d65f2d3199a3edaa28a0149d2f9a7eb96cce69e095440b99ff41`, manifesto em
[`../PROTOCOLO-CONGELADO.md`](../PROTOCOLO-CONGELADO.md).

## Por que estas janelas existem

O planejamento da Sprint 4 pede rodadas de 1 e 5 usuários com cache frio e quente, e a
Seção 9.2.4 do `Projeto.md` determina que as duas modalidades nunca se misturem no
mesmo resultado. As rodadas anteriores foram todas com cache quente.

O *backend* não tem cache de respostas. Como definido em
`app/tests/performance/README.md`:

| Modalidade | Preparo |
| --- | --- |
| quente | reiniciar a API, rodar `aquecer.py`, medir |
| **frio** | **reiniciar a API e medir direto, sem `aquecer.py`** |

Com cache frio, a primeira requisição encontra o pool de conexões vazio e nenhuma
conexão aberta com o provedor. O classificador é carregado na inicialização
(`PLN_WARMUP=1`), antes de a API aceitar requisições.

## Método

| Janela | Usuários | Duração | Preparo |
| --- | ---: | --- | --- |
| linha de base fria | 1 | **35 min** | API reiniciada imediatamente antes, sem aquecimento |
| carga fria | 5 | 8 min | API reiniciada de novo imediatamente antes, sem aquecimento |

A linha de base fria tem 35 minutos desde o início, e não 25: na 3ª rodada, 25
minutos renderam 37 amostras comparativas, e uma extensão exigiria reiniciar a API
e repetir a janela. Massa, proporção, provedor e configuração da API são os da 3ª
rodada.

## Regra de decisão, fixada agora

1. Cada janela é apurada por `apurar_rnf05.py` com os mesmos critérios das
   rodadas de cache quente: zero erro, 40 amostras por rota e tetos de 10 s e 20 s
   para o P95.
2. O resultado é publicado por rota e janela, qualquer que seja, ao lado das
   janelas de cache quente e sem se misturar a elas.
3. Se alguma janela fria reprovar, o RNF05 passa a ser registrado como atendido
   **só com cache quente**, e a reprovação com cache frio vira defeito registrado.
4. Além do P95, registra-se o tempo da primeira requisição depois de cada
   reinício, que é onde o cache frio pesa.
