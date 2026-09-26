"""Apuracao do RNF04 a partir da planilha cega rotulada.

Separado de `executar_rnf04.py` de proposito: a coleta acontece sem gabarito e a
rotulagem acontece sem saber o cenario, o que impede a selecao oportunista de
casos que a Secao 9.2.3 do `Projeto.md` proibe.

Uso, a partir de `src/backend`:

    .venv/bin/python -m app.tests.rnf04.avaliar_rnf04 \
        --evidencias evidencias/rnf04-<commit>

Rotulos aceitos na coluna `rotulo` da planilha cega:

  fundamentada        toda afirmacao factual se sustenta nas fontes retornadas;
                      declarar corretamente a ausencia de informacao tambem conta
  alucinacao          ao menos uma afirmacao apresentada como fato nao se
                      sustenta em nenhuma fonte retornada
  nao_fundamentada    resposta vaga ou evasiva: nao afirma fato incorreto, mas
                      tambem nao sustenta o que diz

Criterio de aprovacao (Secao 9.2.2): fundamentadas >= 90% E alucinacao <= 5%,
apurados sobre o conjunto completo. Reprovar em um dos dois reprova o requisito.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

AMOSTRA = Path(__file__).with_name("amostra_congelada.json")
ROTULOS_VALIDOS = {"fundamentada", "alucinacao", "nao_fundamentada"}
MINIMO_FUNDAMENTADAS = 90.0
MAXIMO_ALUCINACAO = 5.0


def _percentual(parte: int, total: int) -> float:
    return round(100.0 * parte / total, 2) if total else 0.0


def _apura(rotulos: list[str]) -> dict:
    total = len(rotulos)
    fundamentadas = rotulos.count("fundamentada")
    alucinacoes = rotulos.count("alucinacao")
    nao_fundamentadas = rotulos.count("nao_fundamentada")
    return {
        "denominador": total,
        "fundamentadas": fundamentadas,
        "alucinacoes": alucinacoes,
        "nao_fundamentadas": nao_fundamentadas,
        "percentual_fundamentadas": _percentual(fundamentadas, total),
        "percentual_alucinacao": _percentual(alucinacoes, total),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Apura fundamentacao e alucinacao.")
    parser.add_argument("--evidencias", required=True)
    argumentos = parser.parse_args()

    diretorio = Path(argumentos.evidencias)
    amostra = json.loads(AMOSTRA.read_text(encoding="utf-8"))
    cenario_por_id = {c["id"]: c["cenario"] for c in amostra["perguntas"]}

    erros_operacionais = []
    caminho_respostas = diretorio / "respostas.jsonl"
    if caminho_respostas.exists():
        for linha in caminho_respostas.read_text(encoding="utf-8").splitlines():
            if not linha.strip():
                continue
            registro = json.loads(linha)
            if registro.get("http_status") != 200:
                erros_operacionais.append(
                    {
                        "id": registro["id"],
                        "http_status": registro.get("http_status"),
                        "erro": (registro.get("erro_operacional") or "")[:300],
                    }
                )

    ids_com_erro = {e["id"] for e in erros_operacionais}
    linhas = list(csv.DictReader((diretorio / "planilha_cega.csv").open(encoding="utf-8")))

    rotulados: list[dict] = []
    sem_rotulo: list[str] = []
    invalidos: list[str] = []
    for linha in linhas:
        identificador = linha["id"]
        if identificador in ids_com_erro:
            continue
        rotulo = (linha.get("rotulo") or "").strip().lower()
        if not rotulo:
            sem_rotulo.append(identificador)
            continue
        if rotulo not in ROTULOS_VALIDOS:
            invalidos.append(f"{identificador}={rotulo}")
            continue
        rotulados.append(
            {
                "id": identificador,
                "cenario": cenario_por_id.get(identificador, "desconhecido"),
                "rotulo": rotulo,
                "justificativa": (linha.get("justificativa") or "").strip(),
            }
        )

    if invalidos:
        print("ERRO: rotulos invalidos -> " + ", ".join(invalidos))
        print("Aceitos: " + ", ".join(sorted(ROTULOS_VALIDOS)))
        return 2
    if sem_rotulo:
        print(f"ERRO: {len(sem_rotulo)} linha(s) sem rotulo -> " + ", ".join(sem_rotulo))
        return 2
    if not rotulados:
        print("ERRO: nenhuma linha rotulada.")
        return 2

    geral = _apura([r["rotulo"] for r in rotulados])
    positivo = _apura([r["rotulo"] for r in rotulados if r["cenario"] == "positivo"])
    negativo = _apura([r["rotulo"] for r in rotulados if r["cenario"] == "negativo"])

    passa_fundamentacao = geral["percentual_fundamentadas"] >= MINIMO_FUNDAMENTADAS
    passa_alucinacao = geral["percentual_alucinacao"] <= MAXIMO_ALUCINACAO
    aprovado = passa_fundamentacao and passa_alucinacao

    metricas = {
        "requisito": "RNF04",
        "amostra_versao": amostra["versao"],
        "criterio": {
            "fundamentadas_minimo_percentual": MINIMO_FUNDAMENTADAS,
            "alucinacao_maximo_percentual": MAXIMO_ALUCINACAO,
        },
        "geral": geral,
        "cenario_positivo_CT-RNF04-P": positivo,
        "cenario_negativo_CT-RNF04-N": negativo,
        "erros_operacionais": erros_operacionais,
        "resultado": "aprovado" if aprovado else "reprovado",
        "motivo_da_reprovacao": [
            motivo
            for motivo, falhou in (
                (
                    f"fundamentadas {geral['percentual_fundamentadas']}% < {MINIMO_FUNDAMENTADAS}%",
                    not passa_fundamentacao,
                ),
                (
                    f"alucinacao {geral['percentual_alucinacao']}% > {MAXIMO_ALUCINACAO}%",
                    not passa_alucinacao,
                ),
            )
            if falhou
        ],
        "rotulos": rotulados,
    }

    (diretorio / "metricas.json").write_text(
        json.dumps(metricas, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\nRNF04 — amostra v{amostra['versao']}")
    print(f"  denominador ............ {geral['denominador']}")
    print(
        f"  fundamentadas .......... {geral['fundamentadas']}"
        f" ({geral['percentual_fundamentadas']}%)  [minimo {MINIMO_FUNDAMENTADAS}%]"
    )
    print(
        f"  alucinacoes ............ {geral['alucinacoes']}"
        f" ({geral['percentual_alucinacao']}%)  [maximo {MAXIMO_ALUCINACAO}%]"
    )
    print(f"  nao fundamentadas ...... {geral['nao_fundamentadas']}")
    print(
        f"  positivo (CT-RNF04-P) .. {positivo['fundamentadas']}/{positivo['denominador']}"
        f" fundamentadas, {positivo['alucinacoes']} alucinacao"
    )
    print(
        f"  negativo (CT-RNF04-N) .. {negativo['fundamentadas']}/{negativo['denominador']}"
        f" fundamentadas, {negativo['alucinacoes']} alucinacao"
    )
    if erros_operacionais:
        print(f"  erros operacionais ..... {len(erros_operacionais)} (fora do denominador)")
    print(f"\n  RESULTADO: {metricas['resultado'].upper()}")
    for motivo in metricas["motivo_da_reprovacao"]:
        print(f"    - {motivo}")
    print(f"\n  metricas.json gravado em {diretorio}/")
    return 0 if aprovado else 1


if __name__ == "__main__":
    raise SystemExit(main())
