"""Reexecuta o benchmark congelado do RNF06 e publica uma evidencia JSON.

Uso, a partir de ``src/backend``:

    ..\\..\\.venv\\Scripts\\python.exe scripts\\benchmark_rnf06.py

O comando valida os hashes definidos antes da medicao, executa o classificador
sem retreino sobre o split de teste e calcula recall@3 da recuperacao local.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import joblib
import numpy as np
import sklearn
import torch
import transformers
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.nlp.inference import (  # noqa: E402
    DEFAULT_BERT_MODEL,
    DEFAULT_BERT_REVISION,
    ClassificadorDeIntencoes,
)
from app.rag.sharepoint import (  # noqa: E402
    load_sharepoint_documents,
    retrieve_sharepoint_context,
)
from app.rag.evaluation import wilson_interval  # noqa: E402


EVIDENCE_DIR = REPO_ROOT / "docs" / "evidencias" / "sprint-04" / "rnf06"
MANIFEST_PATH = EVIDENCE_DIR / "massa-congelada.json"
OUTPUT_PATH = EVIDENCE_DIR / "resultado-rnf06.json"
MANIFEST_V2_PATH = EVIDENCE_DIR / "massa-congelada-v2.json"
OUTPUT_V2_PATH = EVIDENCE_DIR / "resultado-rnf06-v2.json"
CLASSIFICATION_DATASET = (
    REPO_ROOT / "src" / "notebooks" / "artefatos" / "dataset_intencoes.csv"
)
RETRIEVAL_CASES = (
    BACKEND_ROOT / "app" / "tests" / "data" / "rnf06_retrieval_cases.json"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def validar_massas(manifesto: dict) -> list[dict]:
    """Falha antes da medicao se qualquer massa divergir do congelamento."""

    registros = []
    entradas = list(manifesto["classificacao"]["arquivos"])
    entradas.extend(manifesto["recuperacao"]["fontes"])
    entradas.append(manifesto["recuperacao"]["massa"])
    if "implementacao" in manifesto["recuperacao"]:
        entradas.append(manifesto["recuperacao"]["implementacao"])
    for entrada in entradas:
        caminho = REPO_ROOT / entrada["caminho"]
        observado = _sha256(caminho)
        registro = {
            "caminho": entrada["caminho"],
            "sha256_esperado": entrada["sha256"],
            "sha256_observado": observado,
            "integro": observado == entrada["sha256"],
        }
        registros.append(registro)

    divergentes = [item["caminho"] for item in registros if not item["integro"]]
    if divergentes:
        raise RuntimeError(
            "Massa alterada depois do congelamento: " + ", ".join(divergentes)
        )
    return registros


def avaliar_classificacao(limiar: float = 0.8) -> dict:
    with CLASSIFICATION_DATASET.open(encoding="utf-8", newline="") as source:
        casos = [linha for linha in csv.DictReader(source) if linha["split"] == "teste"]

    classificador = ClassificadorDeIntencoes()
    atributos = classificador.vectorize([caso["texto"] for caso in casos])
    probabilidades = classificador.artefato.modelo.predict_proba_intencao(atributos)
    classes = classificador.artefato.modelo.classes_
    previstas = classes[probabilidades.argmax(axis=1)]
    esperadas = np.asarray([caso["intencao"] for caso in casos])

    precisao, recall, f1, suporte = precision_recall_fscore_support(
        esperadas,
        previstas,
        labels=classes,
        zero_division=0,
    )
    metricas_por_classe = [
        {
            "classe": str(classe),
            "precisao": round(float(precisao[indice]), 6),
            "recall": round(float(recall[indice]), 6),
            "f1": round(float(f1[indice]), 6),
            "suporte": int(suporte[indice]),
        }
        for indice, classe in enumerate(classes)
    ]
    metricas_por_classe.sort(
        key=lambda item: (item["f1"], item["recall"], item["classe"])
    )

    acuracia = round(float(accuracy_score(esperadas, previstas)), 6)
    f1_macro = round(
        float(f1_score(esperadas, previstas, average="macro", zero_division=0)),
        6,
    )
    return {
        "status": "aprovado" if f1_macro >= limiar else "reprovado",
        "criterio_f1_macro_minimo": limiar,
        "quantidade": len(casos),
        "acuracia": acuracia,
        "f1_macro": f1_macro,
        "modelo": "classificador_intencoes.joblib + BERTimbau congelado",
        "sem_retreino": True,
        "piores_classes": metricas_por_classe[:5],
    }


def avaliar_recuperacao(
    massa_path: Path = RETRIEVAL_CASES,
    *,
    limiar_recall: float = 0.8,
    limiar_confianca: float | None = None,
) -> dict:
    massa = json.loads(massa_path.read_text(encoding="utf-8"))
    documentos = load_sharepoint_documents()
    resultados = []
    agregados = defaultdict(lambda: {"relevantes": 0, "recuperadas": 0})

    for caso in massa["casos"]:
        encontrados = retrieve_sharepoint_context(
            caso["consulta"],
            documents=documentos,
            limit=massa["top_k"],
        )
        recuperadas = [item.document.source_id for item in encontrados]
        esperadas = caso["fontes_esperadas"]
        acertos = len(set(esperadas) & set(recuperadas))
        estrato = caso.get("tipo_variacao") or caso.get("cenario", "sem_estrato")
        agregados[estrato]["relevantes"] += len(esperadas)
        agregados[estrato]["recuperadas"] += acertos
        resultados.append(
            {
                "id": caso["id"],
                "estrato": estrato,
                "consulta": caso["consulta"],
                "fontes_esperadas": esperadas,
                "fontes_recuperadas": recuperadas,
                "recall": round(acertos / len(esperadas), 6),
                "status": "aprovado" if acertos == len(esperadas) else "reprovado",
            }
        )

    relevantes = sum(item["relevantes"] for item in agregados.values())
    recuperadas = sum(item["recuperadas"] for item in agregados.values())
    recall = round(recuperadas / relevantes, 6)
    intervalo = wilson_interval(recuperadas, relevantes)
    por_estrato = {
        estrato: {
            **contagens,
            "recall_at_3": round(
                contagens["recuperadas"] / contagens["relevantes"], 6
            ),
        }
        for estrato, contagens in sorted(agregados.items())
    }
    limite_inferior = round(intervalo[0], 6)
    limite_superior = round(intervalo[1], 6)
    confiabilidade_aprovada = (
        limiar_confianca is None or limite_inferior >= limiar_confianca
    )
    return {
        "status": "aprovado" if recall >= limiar_recall else "reprovado",
        "criterio_recall_at_3_minimo": limiar_recall,
        "confiabilidade": {
            "metodo": "intervalo de Wilson bilateral de 95%",
            "limite_inferior": limite_inferior,
            "limite_superior": limite_superior,
            "criterio_limite_inferior_minimo": limiar_confianca,
            "status": "aprovado" if confiabilidade_aprovada else "reprovado",
        },
        "top_k": massa["top_k"],
        "quantidade_casos": len(resultados),
        "fontes_relevantes": relevantes,
        "fontes_relevantes_recuperadas": recuperadas,
        "recall_at_3": recall,
        "por_estrato": por_estrato,
        "casos": resultados,
    }


def main(
    manifest_path: Path = MANIFEST_V2_PATH,
    output_path: Path = OUTPUT_V2_PATH,
) -> int:
    manifesto = json.loads(manifest_path.read_text(encoding="utf-8"))
    integridade = validar_massas(manifesto)
    criterios = manifesto["criterios"]
    classificacao = avaliar_classificacao(
        criterios["classificacao_f1_macro_minimo"]
    )
    recuperacao = avaliar_recuperacao(
        REPO_ROOT / manifesto["recuperacao"]["massa"]["caminho"],
        limiar_recall=criterios["recuperacao_recall_at_3_minimo"],
        limiar_confianca=criterios.get(
            "recuperacao_limite_inferior_wilson_95_minimo"
        ),
    )
    rnf06_aprovado = (
        classificacao["status"] == "aprovado"
        and recuperacao["status"] == "aprovado"
    )
    confiabilidade_aprovada = (
        recuperacao["confiabilidade"]["status"] == "aprovado"
    )
    aprovado = rnf06_aprovado and confiabilidade_aprovada

    evidencia = {
        "issue": 232,
        "protocolo": {
            "tipo_avaliacao": manifesto.get("tipo_avaliacao", "legado"),
            "manifesto": str(manifest_path.relative_to(REPO_ROOT)),
            "limitacao": manifesto.get("limitacao"),
        },
        "executado_em": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(
            timespec="seconds"
        ),
        "commit_execucao": _git_head(),
        "ambiente": {
            "sistema": platform.platform(),
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "numpy": np.__version__,
            "joblib": joblib.__version__,
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "encoder": DEFAULT_BERT_MODEL,
            "encoder_revisao": DEFAULT_BERT_REVISION,
        },
        "integridade_massas": integridade,
        "classificacao": classificacao,
        "recuperacao": recuperacao,
        "conclusao": {
            "status": "aprovado" if aprovado else "reprovado",
            "status_rnf06": "aprovado" if rnf06_aprovado else "reprovado",
            "status_confiabilidade": (
                "aprovado" if confiabilidade_aprovada else "reprovado"
            ),
            "regra": criterios.get("regra_rnf06")
            or criterios.get("regra_final"),
            "observacao": (
                "Os criterios do RNF06 e de confiabilidade foram atingidos."
                if aprovado
                else "Ao menos um criterio do RNF06 ou de confiabilidade falhou."
            ),
        },
    }
    output_path.write_text(
        json.dumps(evidencia, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(evidencia["classificacao"], ensure_ascii=False, indent=2))
    print(json.dumps(evidencia["recuperacao"], ensure_ascii=False, indent=2))
    print(json.dumps(evidencia["conclusao"], ensure_ascii=False, indent=2))
    print(f"Evidencia gravada em {output_path.relative_to(REPO_ROOT)}")
    return 0 if aprovado else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_V2_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_V2_PATH)
    args = parser.parse_args()
    raise SystemExit(main(args.manifest, args.output))
