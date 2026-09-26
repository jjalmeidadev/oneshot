"""Aquecimento da API antes de uma rodada de desempenho do RNF05.

A Secao 9.2.4 do `Projeto.md` pede para "reiniciar a API e aquecer uma vez cada
prompt" antes de medir. Isso e um passo separado da medicao, e precisa ser.

O aquecimento morava no `test_start` do `locustfile`, e o relogio do `-t` do
Locust corre durante esse evento. Na execucao de 22/09/2026 isso produziu dois
estragos: as rodadas positivas "de 5 minutos" mediram cerca de 3 min 40 s,
porque os 14 prompts de aquecimento consumiram ~77 s da janela; e a rodada
negativa mediu zero requisicoes, porque aquecer a instancia com atraso de 25 s
consumiu os 3 minutos inteiros.

Rodado a parte, o aquecimento nao toca na janela de medicao.

Uso, a partir de `src/backend`:

    .venv/bin/python -m app.tests.performance.aquecer --host http://127.0.0.1:8000

Para uma rodada de cache frio, simplesmente nao rode este passo, e reinicie a
API antes de medir.
"""

from __future__ import annotations

import argparse
from time import perf_counter

import httpx

from app.tests.performance.prompts import TODOS_OS_PROMPTS

TIMEOUT_SEGUNDOS = 60


def main() -> int:
    parser = argparse.ArgumentParser(description="Aquece a API antes do RNF05.")
    parser.add_argument("--host", default="http://127.0.0.1:8000")
    argumentos = parser.parse_args()

    print(f"[RNF05] aquecendo {len(TODOS_OS_PROMPTS)} prompts em {argumentos.host}")
    falhas = 0
    with httpx.Client(base_url=argumentos.host, timeout=TIMEOUT_SEGUNDOS) as cliente:
        for indice, mensagem in enumerate(TODOS_OS_PROMPTS, start=1):
            inicio = perf_counter()
            try:
                resposta = cliente.post(
                    "/api/chat",
                    json={"message": mensagem, "use_intent_classifier": True},
                )
                situacao = str(resposta.status_code)
                if resposta.status_code != 200:
                    falhas += 1
            except Exception as error:
                situacao = type(error).__name__
                falhas += 1
            tempo = round((perf_counter() - inicio) * 1000)
            print(f"  [{indice:>2}/{len(TODOS_OS_PROMPTS)}] {situacao} em {tempo} ms")

    if falhas:
        print(
            f"[RNF05] {falhas} prompt(s) falharam no aquecimento. Investigar antes "
            "de medir: uma API que falha no aquecimento vai falhar na rodada."
        )
        return 1
    print("[RNF05] aquecimento concluido; a janela de medicao comeca limpa")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
