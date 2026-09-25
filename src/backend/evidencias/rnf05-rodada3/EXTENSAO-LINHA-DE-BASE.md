# RNF05 — 3ª rodada: extensão da linha de base

**Registrado em:** 2026-09-22T22:50Z, depois da linha de base de 25 minutos e
**antes** de conhecer o resultado da rodada de carga, que estava em execução.

## O que aconteceu

A linha de base de 25 minutos, com um usuário, terminou assim:

| Rota | Amostras | Falhas | P95 | Teto | Situação pelo protocolo |
| --- | ---: | ---: | ---: | ---: | --- |
| simples | 159 | 0 | 7.600 ms | 10.000 | conclusiva |
| comparação | **37** | 0 | 8.200 ms | 20.000 | **inconclusiva: menos de 40 amostras** |

A proporção de 75/25 é sorteada a cada requisição. Na 2ª rodada, os mesmos 25
minutos renderam 41 amostras comparativas; nesta, 37.

Pela regra 2 do protocolo congelado, a linha de base é **inconclusiva** e deve
ser estendida.

## Como a extensão é feita

O Locust exporta percentis por rota, e não o tempo de cada requisição. Não há
como reunir as duas janelas num único P95 sem alterar o `locustfile`, que faz
parte do código congelado. Por isso a extensão é uma **nova janela, mais longa**,
com o mesmo código e a mesma configuração:

| Item | Valor |
| --- | --- |
| Aquecimento | `aquecer.py`, fora da janela, como na janela original |
| Usuários | 1 |
| Duração | **35 minutos**: cerca de 270 requisições; com 25% de comparações, a chance de ficar abaixo de 40 é desprezível |
| Código | o mesmo hash `71ee4895…`, conferido antes e depois |

## Regra de decisão da linha de base, fixada agora

1. **Um erro em qualquer das duas janelas reprova a linha de base.** A janela de
   25 minutos não é descartada: a exigência de zero erro não depende de amostra.
2. O P95 de cada rota é julgado na janela de 35 minutos, que é a que tem amostra
   suficiente nas duas rotas.
3. Se a janela de 35 minutos também ficar abaixo de 40 amostras em alguma rota, a
   linha de base é **inconclusiva** e o RNF05 não é declarado atendido nesta
   rodada. Não haverá uma terceira janela.
4. A janela de 25 minutos é publicada integralmente, em `baseline/`, ao lado da
   estendida, em `baseline-estendida/`.
