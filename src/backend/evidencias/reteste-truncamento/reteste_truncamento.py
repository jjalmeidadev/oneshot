"""Reteste do truncamento das respostas (DEF-RNF04-02, ocorrências O5 e O7).

Compara o limite anterior de 512 tokens com o corrigido de 1024, com o mesmo
prompt que a API monta: recuperação no banco e `build_rag_input`. Cada pergunta
roda nos dois limites, em ordem sorteada, para que a variação do provedor ao longo
do tempo não favoreça um dos lados.

Uso, a partir de `src/backend`:

    PYTHONPATH=. .venv/bin/python evidencias/reteste-truncamento/reteste_truncamento.py
"""

import csv
import os
import random
import sys
from pathlib import Path
from time import perf_counter

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
os.environ["LLM_PROVIDER"] = "openrouter"

from app.gemini import client  # noqa: E402
from app.tests.performance.prompts import TODOS_OS_PROMPTS  # noqa: E402

PERGUNTA_O7 = "me fale sobre os riscos e avancos da linha azul ou sobre algum projeto"
LIMITES = (512, 1024)
REPETICOES_O7 = 10
REPETICOES_MASSA = 2
SAIDA = Path(__file__).resolve().parent / "execucoes.csv"


def medir(pergunta: str, limite: int, prompt: str) -> dict:
    os.environ["GEMINI_MAX_OUTPUT_TOKENS"] = str(limite)
    inicio = perf_counter()
    resultado = client._call_llm(prompt, api_key=client._api_key())
    latencia_ms = round((perf_counter() - inicio) * 1000)
    aviso = client.AVISO_RESPOSTA_INTERROMPIDA
    return {
        "pergunta": pergunta,
        "limite": limite,
        "latencia_ms": latencia_ms,
        "truncada": resultado.text.endswith(aviso),
        "vazia": resultado.text == aviso,
        "tokens_saida": resultado.usage.output_tokens,
        "tokens_raciocinio": resultado.usage.thought_tokens,
    }


def main() -> int:
    random.seed(2026)
    plano = [(PERGUNTA_O7, REPETICOES_O7)] + [(p, REPETICOES_MASSA) for p in TODOS_OS_PROMPTS]
    linhas = []
    for pergunta, repeticoes in plano:
        prompt = client.build_rag_input(pergunta, client.retrieve_context(pergunta, intent=None, entities=[]))
        for _ in range(repeticoes):
            for limite in random.sample(LIMITES, k=len(LIMITES)):
                linhas.append(medir(pergunta, limite, prompt))
                print(f"{limite:>5} {linhas[-1]['latencia_ms']:>6} ms truncada={linhas[-1]['truncada']!s:5} {pergunta[:50]}")
    with SAIDA.open("w", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]), lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"{len(linhas)} execuções gravadas em {SAIDA.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
