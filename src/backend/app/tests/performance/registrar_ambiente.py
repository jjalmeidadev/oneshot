"""Registro do ambiente antes de uma rodada de desempenho do RNF05.

A Secao 9.2.4 do `Projeto.md` exige registrar CPU, memoria, sistema operacional,
versao do Python, commit, configuracao da API e modalidade de cache ANTES de
medir. Um P95 sem essa ficha nao e auditavel: nao ha como saber em que maquina
o numero foi produzido nem se duas rodadas sao comparaveis entre si.

Uso, a partir de `src/backend`:

    .venv/bin/python -m app.tests.performance.registrar_ambiente \
        --rodada baseline --cache frio --saida evidencias/rnf05-baseline
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _comando(argumentos: list[str]) -> str:
    try:
        return subprocess.run(
            argumentos, capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return "indisponivel"


def _memoria_total_gb() -> str:
    if platform.system() == "Darwin":
        bruto = _comando(["sysctl", "-n", "hw.memsize"])
    elif platform.system() == "Linux":
        try:
            with open("/proc/meminfo") as arquivo:
                bruto = str(int(arquivo.readline().split()[1]) * 1024)
        except Exception:
            bruto = "indisponivel"
    else:
        return "indisponivel"
    try:
        return f"{int(bruto) / (1024 ** 3):.1f} GB"
    except (TypeError, ValueError):
        return "indisponivel"


def _cpu() -> str:
    if platform.system() == "Darwin":
        return _comando(["sysctl", "-n", "machdep.cpu.brand_string"])
    return platform.processor() or platform.machine()


def coletar(rodada: str, cache: str, host: str) -> dict:
    """Monta a ficha do ambiente, sem incluir nenhum valor de segredo."""

    return {
        "registrado_em": datetime.now(timezone.utc).isoformat(),
        "rodada": rodada,
        "modalidade_de_cache": cache,
        "host_medido": host,
        "commit": _comando(["git", "rev-parse", "--short", "HEAD"]),
        "branch": _comando(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "arvore_limpa": _comando(["git", "status", "--porcelain"]) == "",
        "maquina": {
            "cpu": _cpu(),
            "nucleos_logicos": os.cpu_count(),
            "memoria_total": _memoria_total_gb(),
            "sistema": f"{platform.system()} {platform.release()}",
            "arquitetura": platform.machine(),
        },
        "python": sys.version.split()[0],
        "configuracao_da_api": {
            # O modelo efetivo depende do provedor. Registrar sempre GEMINI_MODEL
            # gravaria o modelo errado em rodadas pelo OpenRouter.
            "provedor_llm": os.getenv("LLM_PROVIDER", "gemini"),
            "modelo_llm": (
                os.getenv("OPENROUTER_MODEL", "google/gemini-3.7-flash")
                if os.getenv("LLM_PROVIDER", "gemini").strip().lower() == "openrouter"
                else os.getenv("GEMINI_MODEL", "nao definido")
            ),
            "retries_do_provedor": os.getenv("GEMINI_MAX_RETRIES", "3 (padrao)"),
            "pool_de_conexoes": os.getenv("DATABASE_POOL_ENABLED", "1") != "0",
            "max_output_tokens": os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "nao definido"),
            "thinking_level": os.getenv("GEMINI_THINKING_LEVEL", "nao definido"),
            "timeout_provedor_s": os.getenv(
                "GEMINI_REQUEST_TIMEOUT_SECONDS", "nao definido"
            ),
            "rag_max_sources": os.getenv("RAG_MAX_SOURCES", "nao definido"),
            "pln_warmup": os.getenv("PLN_WARMUP", "nao definido"),
            "origem_do_rag": (
                "banco (public.source_extracts)"
                if os.getenv("DATABASE_URL", "").strip()
                or os.getenv("SUPABASE_DATABASE_URL", "").strip()
                else "fallback JSON local (app/rag/data/sharepoint)"
            ),
        },
        "segredos_presentes": {
            "GEMINI_API_KEY": bool(os.getenv("GEMINI_API_KEY", "").strip()),
            "SUPABASE_DATABASE_URL": bool(
                os.getenv("SUPABASE_DATABASE_URL", "").strip()
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Registra o ambiente do RNF05.")
    parser.add_argument("--rodada", required=True, help="baseline, carga ou violacao")
    parser.add_argument("--cache", default="quente", choices=["frio", "quente"])
    parser.add_argument("--host", default="http://127.0.0.1:8000")
    parser.add_argument("--saida", required=True)
    argumentos = parser.parse_args()

    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[3] / ".env")

    destino = Path(argumentos.saida)
    destino.mkdir(parents=True, exist_ok=True)
    ficha = coletar(argumentos.rodada, argumentos.cache, argumentos.host)
    caminho = destino / "ambiente.json"
    caminho.write_text(json.dumps(ficha, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(ficha, indent=2, ensure_ascii=False))
    if not ficha["arvore_limpa"]:
        print(
            "\nAVISO: a arvore de trabalho tem alteracoes nao commitadas. "
            "O commit registrado nao descreve exatamente o codigo medido."
        )
    print(f"\nficha gravada em {caminho}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
