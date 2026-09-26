# Rodadas descartadas — aquecimento dentro da janela de medicao

Estas tres rodadas foram executadas em 22/09/2026 e **descartadas** antes de
qualquer apuracao formal. Ficam publicadas por transparencia.

O aquecimento dos 14 prompts rodava no `test_start` do `locustfile`, e o relogio
do `-t` do Locust corre durante esse evento:

- **baseline** e **carga**, anunciadas como rodadas de 5 minutos, mediram cerca
  de 3 min 40 s, porque o aquecimento consumiu ~77 s da janela. A linha de base
  produziu 29 requisicoes onde se esperavam ~40;
- **violacao** mediu **zero** requisicoes: aquecer a instancia com atraso de
  25 s nos 4 prompts de comparacao consumiu os 3 minutos inteiros.

Os numeros das duas rodadas positivas foram aprovados (P95 simples 6,6 s e
7,5 s; comparativo 7,9 s e 7,4 s; zero erros). Eles nao foram usados como
resultado porque a duracao declarada nao foi cumprida.

Correcao: o aquecimento saiu do `locustfile` e virou o passo separado
`app/tests/performance/aquecer.py`, executado antes da medicao. As rodadas
validas estao no diretorio pai.
