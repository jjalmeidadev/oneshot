"""Apuracao das rodadas do RNF05 pelo protocolo revisado a partir da 2a rodada.

A regra do protocolo (Secao 9.2.4 do `Projeto.md`, revisao de 22/09/2026) e
aplicada aqui, e nao por quem le o CSV. Para cada rodada e cada tipo de
consulta, nesta ordem:

1. **erros** — qualquer falha HTTP ou de contrato reprova. Nao depende do
   tamanho da amostra: a exigencia de zero erro nao e estatistica;
2. **amostra minima** — com menos de 40 amostras a rota e *inconclusiva*. O
   Locust calcula o percentil em `calculate_response_time_percentile`, e abaixo
   de 21 amostras o resultado coincide com a pior requisicao. Na Sprint 4, a
   rota comparativa da linha de base teve 10 amostras e uma requisicao de 37,7 s
   definiu o "P95";
3. **teto do P95** — 10 s para consulta simples e 20 s para comparacao.

O RNF05 so e atendido se todas as rotas de todas as rodadas forem aprovadas.

Uso, a partir de `src/backend`:

    .venv/bin/python -m app.tests.performance.apurar_rnf05 \
        evidencias/<campanha>/baseline/rnf05-baseline_stats.csv \
        evidencias/<campanha>/carga/rnf05-carga_stats.csv

Codigo de saida: 0 atendido, 1 nao atendido, 2 inconclusivo.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

AMOSTRA_MINIMA = 40
TETOS_MS = {"simples": 10_000, "comparacao": 20_000}

APROVADO = "aprovado"
REPROVADO = "reprovado"
INCONCLUSIVO = "inconclusivo"


@dataclass(frozen=True)
class ResultadoDaRota:
    rodada: str
    rota: str
    amostras: int
    falhas: int
    p95_ms: float
    veredito: str
    motivo: str


def _rota(nome: str) -> str | None:
    for rota in TETOS_MS:
        if f"[{rota}]" in nome:
            return rota
    return None


def apurar_rota(rodada: str, rota: str, amostras: int, falhas: int, p95_ms: float) -> ResultadoDaRota:
    """Aplica as tres verificacoes do protocolo, na ordem que o protocolo fixa."""

    teto = TETOS_MS[rota]
    if falhas > 0:
        veredito, motivo = REPROVADO, f"{falhas} erro(s); o criterio exige zero"
    elif amostras < AMOSTRA_MINIMA:
        veredito = INCONCLUSIVO
        motivo = (
            f"{amostras} amostras, abaixo do minimo de {AMOSTRA_MINIMA}; "
            "estender a rodada"
        )
    elif p95_ms > teto:
        veredito, motivo = REPROVADO, f"P95 {p95_ms:.0f} ms acima do teto de {teto} ms"
    else:
        veredito, motivo = APROVADO, f"P95 {p95_ms:.0f} ms dentro do teto de {teto} ms"
    return ResultadoDaRota(rodada, rota, amostras, falhas, p95_ms, veredito, motivo)


def ler_csv(caminho: Path) -> list[ResultadoDaRota]:
    """Le o `_stats.csv` do Locust e apura cada rota encontrada nele."""

    rodada = caminho.parent.name or caminho.stem
    resultados = []
    with caminho.open(encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            rota = _rota(linha.get("Name", ""))
            if rota is None:
                continue
            resultados.append(
                apurar_rota(
                    rodada,
                    rota,
                    int(linha["Request Count"]),
                    int(linha["Failure Count"]),
                    float(linha["95%"]) if linha["95%"] not in ("", "N/A") else 0.0,
                )
            )
    # Uma rota ausente do CSV nao pode passar em silencio: sem nenhuma amostra,
    # a rodada nao mediu aquele tipo de consulta.
    presentes = {r.rota for r in resultados}
    for rota in TETOS_MS:
        if rota not in presentes:
            resultados.append(apurar_rota(rodada, rota, 0, 0, 0.0))
    return resultados


def veredito_geral(resultados: list[ResultadoDaRota]) -> str:
    """Reprovado prevalece sobre inconclusivo, que prevalece sobre aprovado."""

    vereditos = {r.veredito for r in resultados}
    if REPROVADO in vereditos:
        return REPROVADO
    if INCONCLUSIVO in vereditos or not resultados:
        return INCONCLUSIVO
    return APROVADO


def main() -> int:
    parser = argparse.ArgumentParser(description="Apura as rodadas do RNF05.")
    parser.add_argument("csvs", nargs="+", type=Path, help="arquivos *_stats.csv do Locust")
    argumentos = parser.parse_args()

    resultados = [r for caminho in argumentos.csvs for r in ler_csv(caminho)]
    print(f"{'rodada':12} {'rota':11} {'amostras':>8} {'falhas':>6} {'P95':>9}  veredito")
    for r in resultados:
        print(
            f"{r.rodada:12} {r.rota:11} {r.amostras:>8} {r.falhas:>6} "
            f"{r.p95_ms:>7.0f}ms  {r.veredito} — {r.motivo}"
        )
    geral = veredito_geral(resultados)
    rotulo = {APROVADO: "ATENDIDO", REPROVADO: "NAO ATENDIDO", INCONCLUSIVO: "INCONCLUSIVO"}[geral]
    print(f"\nRNF05: {rotulo}")
    return {APROVADO: 0, REPROVADO: 1, INCONCLUSIVO: 2}[geral]


if __name__ == "__main__":
    raise SystemExit(main())
