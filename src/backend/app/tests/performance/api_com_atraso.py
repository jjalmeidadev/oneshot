"""Instancia da API com atraso injetado, para o cenario negativo CT-RNF05-N.

A Secao 9.2.3 do `Projeto.md` pede que a rodada negativa faca "o duplo do
provedor adicionar atraso superior ao teto em uma rota identificada, sem alterar
as demais". Este modulo entrega exatamente isso e nada alem: ele envolve
`app.pipeline.generate_chat_response` com um retardo aplicado apenas aos pedidos
de comparacao, e deixa as consultas simples no caminho normal.

O atraso vive aqui, em codigo de teste, e nao no backend: nenhuma linha de
`app/` de producao e modificada para produzir a violacao.

Subir a instancia violada numa porta separada, a partir de `src/backend`:

    .venv/bin/python -m uvicorn app.tests.performance.api_com_atraso:app \
        --host 127.0.0.1 --port 8001

E entao medir contra ela:

    locust -f app/tests/performance/locustfile.py --host http://127.0.0.1:8001 \
        --headless -u 1 -r 1 -t 2m --csv evidencias/rnf05-violacao

O teste de desempenho so esta correto se esta rodada REPROVAR: o P95 comparativo
tem de estourar os 20 s. Um relatorio aprovado aqui significa que a medicao nao
enxerga a violacao e, portanto, que a rodada positiva nao vale nada.
"""

from __future__ import annotations

import os
from time import sleep

import app.pipeline as pipeline
from app.main import app
from app.tests.performance.prompts import COMPARACOES

#: Atraso injetado, em segundos. O padrao de 25 s fica acima do teto comparativo
#: de 20 s da Secao 9.2.4, garantindo que a violacao seja inequivoca.
ATRASO_SEGUNDOS = float(os.getenv("RNF05_ATRASO_SEGUNDOS", "25"))

#: A rota alvo e identificada pela propria massa congelada, e nao por
#: palavra-chave. A versao anterior procurava "compare" ou "comparar" no texto e
#: deixava passar "Entre o PRJ-0442 e o PRJ-0518, qual esta mais proximo do
#: prazo planejado?" — um quarto dos pedidos de comparacao chegava sem atraso, e
#: na rodada negativa de 22/09/2026 a maioria das requisicoes caiu justamente
#: nele. Comparar com a lista exata torna o duplo deterministico.
PEDIDOS_DE_COMPARACAO = frozenset(COMPARACOES)

_original = pipeline.generate_chat_response


def _com_atraso(request, *args, **kwargs):
    if (getattr(request, "message", "") or "") in PEDIDOS_DE_COMPARACAO:
        sleep(ATRASO_SEGUNDOS)
    return _original(request, *args, **kwargs)


pipeline.generate_chat_response = _com_atraso

__all__ = ["app", "ATRASO_SEGUNDOS"]
