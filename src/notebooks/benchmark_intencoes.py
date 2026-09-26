"""Compara classificadores de intenção sem consultar o conjunto de teste.

O benchmark usa os splits versionados em ``artefatos/dataset_intencoes.csv``.
Treino e validação são empregados na seleção; o teste só é aberto quando a
opção ``--avaliar-teste`` é informada, depois de escolhida a configuração.

O pré-processamento é deliberadamente conservador para português: normaliza
Unicode e espaços, converte para minúsculas e preserva acentos, negação e
demais stopwords. O TF-IDF de caracteres recebe o texto com a grafia original.

Uso:

    python src/notebooks/benchmark_intencoes.py
    python src/notebooks/benchmark_intencoes.py --avaliar-teste
"""

from __future__ import annotations

import argparse
import json
import time
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.naive_bayes import ComplementNB
from sklearn.svm import LinearSVC


SEED = 42
RAIZ = Path(__file__).resolve().parent
ARTEFATOS = RAIZ / "artefatos"
DATASET = ARTEFATOS / "dataset_intencoes.csv"
SINTETICOS = ARTEFATOS / "consultas_sinteticas_issue_251.csv"
RESULTADO = ARTEFATOS / "benchmark_intencoes.json"
MODELO = ARTEFATOS / "classificador_intencoes_v2.joblib"


def normalizar_portugues(texto: str) -> str:
    """Normalização mínima que não apaga informação lexical do português."""

    texto = unicodedata.normalize("NFC", str(texto)).lower()
    return " ".join(texto.split())


@dataclass(frozen=True)
class EspecificacaoRepresentacao:
    nome: str
    word_ngram: tuple[int, int]
    char_ngram: tuple[int, int] | None
    min_df: int = 1
    max_word_features: int | None = 50_000
    max_char_features: int | None = 80_000


REPRESENTACOES = (
    EspecificacaoRepresentacao("palavras_1_2", (1, 2), None, min_df=1),
    EspecificacaoRepresentacao("palavras_1_3", (1, 3), None, min_df=1),
    EspecificacaoRepresentacao("palavras_1_2_caracteres_3_5", (1, 2), (3, 5)),
    EspecificacaoRepresentacao("palavras_1_3_caracteres_2_6", (1, 3), (2, 6)),
    EspecificacaoRepresentacao(
        "palavras_1_2_caracteres_3_6_min_df_2", (1, 2), (3, 6), min_df=2
    ),
)


def criar_vetorizadores(especificacao: EspecificacaoRepresentacao) -> dict[str, TfidfVectorizer]:
    vetorizadores = {
        "palavras": TfidfVectorizer(
            preprocessor=normalizar_portugues,
            lowercase=False,
            strip_accents=None,
            stop_words=None,
            ngram_range=especificacao.word_ngram,
            min_df=especificacao.min_df,
            max_features=especificacao.max_word_features,
            sublinear_tf=True,
            norm="l2",
        )
    }
    if especificacao.char_ngram is not None:
        vetorizadores["caracteres"] = TfidfVectorizer(
            preprocessor=normalizar_portugues,
            lowercase=False,
            strip_accents=None,
            analyzer="char_wb",
            ngram_range=especificacao.char_ngram,
            min_df=especificacao.min_df,
            max_features=especificacao.max_char_features,
            sublinear_tf=True,
            norm="l2",
        )
    return vetorizadores


def ajustar_representacao(
    vetorizadores: dict[str, TfidfVectorizer], textos: pd.Series
) -> sparse.csr_matrix:
    partes = [vetorizador.fit_transform(textos) for vetorizador in vetorizadores.values()]
    return sparse.hstack(partes, format="csr") if len(partes) > 1 else partes[0].tocsr()


def transformar(
    vetorizadores: dict[str, TfidfVectorizer], textos: pd.Series
) -> sparse.csr_matrix:
    partes = [vetorizador.transform(textos) for vetorizador in vetorizadores.values()]
    return sparse.hstack(partes, format="csr") if len(partes) > 1 else partes[0].tocsr()


class ClassificadorHierarquico:
    """Prediz a macrointenção e delega a intenção a um especialista."""

    def __init__(self, fabrica: Callable[[], object], intencao2macro: dict[str, str]):
        self.fabrica = fabrica
        self.intencao2macro = intencao2macro
        self.macro = None
        self.especialistas: dict[str, object] = {}

    def fit(self, x, y_intencao):
        y_intencao = np.asarray(y_intencao)
        y_macro = macro_da_intencao(y_intencao, self.intencao2macro)
        self.macro = self.fabrica().fit(x, y_macro)
        for macro in sorted(set(y_macro)):
            mascara = y_macro == macro
            self.especialistas[macro] = self.fabrica().fit(
                x[mascara], y_intencao[mascara]
            )
        return self

    def predict(self, x) -> np.ndarray:
        macros = self.macro.predict(x)
        predicoes = np.empty(len(macros), dtype=object)
        for macro in sorted(set(macros)):
            mascara = macros == macro
            predicoes[mascara] = self.especialistas[macro].predict(x[mascara])
        return predicoes


def fabricas_modelos(
    intencao2macro: dict[str, str] | None = None,
) -> dict[str, Callable[[], object]]:
    modelos: dict[str, Callable[[], object]] = {}
    for c in (0.5, 1.0, 2.0, 4.0):
        modelos[f"regressao_logistica_C_{c:g}"] = lambda c=c: LogisticRegression(
            C=c,
            class_weight="balanced",
            max_iter=2_000,
            random_state=SEED,
            solver="liblinear",
        )
        modelos[f"linear_svc_C_{c:g}"] = lambda c=c: LinearSVC(
            C=c,
            class_weight="balanced",
            random_state=SEED,
        )
    for alpha in (1e-5, 3e-5, 1e-4):
        modelos[f"sgd_log_alpha_{alpha:g}"] = lambda alpha=alpha: SGDClassifier(
            loss="log_loss",
            alpha=alpha,
            class_weight="balanced",
            max_iter=3_000,
            random_state=SEED,
            tol=1e-4,
        )
    for alpha in (0.1, 0.5, 1.0):
        modelos[f"complement_nb_alpha_{alpha:g}"] = lambda alpha=alpha: ComplementNB(
            alpha=alpha
        )
    if intencao2macro is not None:
        for c in (0.5, 1.0, 2.0, 4.0):
            modelos[f"hierarquico_linear_svc_C_{c:g}"] = lambda c=c: ClassificadorHierarquico(
                lambda: LinearSVC(
                    C=c,
                    class_weight="balanced",
                    random_state=SEED,
                ),
                intencao2macro,
            )
    return modelos


def metricas(y_verdadeiro: pd.Series | np.ndarray, y_predito: np.ndarray) -> dict[str, float]:
    return {
        "acuracia": round(float(accuracy_score(y_verdadeiro, y_predito)), 6),
        "f1_macro": round(
            float(f1_score(y_verdadeiro, y_predito, average="macro", zero_division=0)),
            6,
        ),
    }


def macro_da_intencao(intencoes: pd.Series | np.ndarray, mapa: dict[str, str]) -> np.ndarray:
    return np.array([mapa[intencao] for intencao in intencoes])


def carregar_dataset() -> pd.DataFrame:
    dados = pd.read_csv(DATASET)
    dados["origem"] = "dataset_base"
    if SINTETICOS.exists():
        sinteticos = pd.read_csv(SINTETICOS)
        sinteticos["origem"] = "sintetico_issue_251"
        dados = pd.concat([dados, sinteticos], ignore_index=True)
    colunas = {"texto", "intencao", "macrointencao", "template_id", "split"}
    ausentes = colunas - set(dados.columns)
    if ausentes:
        raise ValueError(f"Dataset sem colunas obrigatórias: {sorted(ausentes)}")
    if set(dados["split"]) != {"treino", "validacao", "teste"}:
        raise ValueError("Os três splits fixos não estão presentes no dataset.")
    if dados["texto"].map(normalizar_portugues).duplicated().any():
        raise ValueError("Há textos duplicados depois da normalização conservadora.")
    return dados


def benchmark_validacao(dados: pd.DataFrame) -> tuple[list[dict], dict]:
    treino = dados[dados["split"] == "treino"]
    validacao = dados[dados["split"] == "validacao"]
    mapa = dados.drop_duplicates("intencao").set_index("intencao")["macrointencao"].to_dict()
    resultados: list[dict] = []
    melhor: dict | None = None

    for especificacao in REPRESENTACOES:
        inicio_representacao = time.perf_counter()
        vetorizadores = criar_vetorizadores(especificacao)
        x_treino = ajustar_representacao(vetorizadores, treino["texto"])
        x_validacao = transformar(vetorizadores, validacao["texto"])
        segundos_representacao = time.perf_counter() - inicio_representacao

        for nome_modelo, fabrica in fabricas_modelos(mapa).items():
            inicio = time.perf_counter()
            modelo = fabrica()
            modelo.fit(x_treino, treino["intencao"])
            pred_int = modelo.predict(x_validacao)
            pred_macro = macro_da_intencao(pred_int, mapa)
            registro = {
                "representacao": especificacao.nome,
                "modelo": nome_modelo,
                "dimensoes": int(x_treino.shape[1]),
                "validacao_intencao": metricas(validacao["intencao"], pred_int),
                "validacao_macro": metricas(validacao["macrointencao"], pred_macro),
                "segundos": round(
                    segundos_representacao + time.perf_counter() - inicio, 3
                ),
            }
            resultados.append(registro)
            chave = (
                registro["validacao_intencao"]["acuracia"],
                registro["validacao_intencao"]["f1_macro"],
                registro["validacao_macro"]["acuracia"],
            )
            if melhor is None or chave > melhor["chave_selecao"]:
                melhor = {
                    "chave_selecao": chave,
                    "especificacao": especificacao,
                    "nome_modelo": nome_modelo,
                    "fabrica": fabrica,
                    "registro": registro,
                }

    assert melhor is not None
    resultados.sort(
        key=lambda item: (
            item["validacao_intencao"]["acuracia"],
            item["validacao_intencao"]["f1_macro"],
        ),
        reverse=True,
    )
    return resultados, melhor


def avaliar_teste_e_exportar(dados: pd.DataFrame, melhor: dict) -> dict:
    desenvolvimento = dados[dados["split"].isin(["treino", "validacao"])]
    teste = dados[dados["split"] == "teste"]
    mapa = dados.drop_duplicates("intencao").set_index("intencao")["macrointencao"].to_dict()

    vetorizadores = criar_vetorizadores(melhor["especificacao"])
    x_desenvolvimento = ajustar_representacao(vetorizadores, desenvolvimento["texto"])
    x_teste = transformar(vetorizadores, teste["texto"])
    modelo = melhor["fabrica"]()
    modelo.fit(x_desenvolvimento, desenvolvimento["intencao"])
    pred_int = modelo.predict(x_teste)
    pred_macro = macro_da_intencao(pred_int, mapa)

    # O artefato final exige probabilidades. LinearSVC é calibrado somente
    # depois da seleção, usando folds internos do conjunto de desenvolvimento.
    if isinstance(modelo, LinearSVC):
        modelo = CalibratedClassifierCV(modelo, method="sigmoid", cv=5)
        modelo.fit(x_desenvolvimento, desenvolvimento["intencao"])
        pred_int = modelo.predict(x_teste)
        pred_macro = macro_da_intencao(pred_int, mapa)

    teste_resultado = {
        "intencao": metricas(teste["intencao"], pred_int),
        "macrointencao_derivada": metricas(teste["macrointencao"], pred_macro),
        "matriz_confusao": {
            "labels": sorted(dados["intencao"].unique().tolist()),
            "valores": confusion_matrix(
                teste["intencao"],
                pred_int,
                labels=sorted(dados["intencao"].unique().tolist()),
            ).astype(int).tolist(),
        },
    }
    joblib.dump(
        {
            "versao": 2,
            "vetorizadores": vetorizadores,
            "modelo_intencao": modelo,
            "intencao2macro": mapa,
            "representacao": asdict(melhor["especificacao"]),
            "normalizacao": {
                "unicode": "NFC",
                "lowercase": True,
                "remove_acentos": False,
                "remove_stopwords": False,
                "preserva_negacao": True,
            },
        },
        MODELO,
    )
    return teste_resultado


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--avaliar-teste",
        action="store_true",
        help="abre o teste após selecionar a melhor configuração na validação",
    )
    argumentos = parser.parse_args()
    dados = carregar_dataset()
    resultados, melhor = benchmark_validacao(dados)
    saida = {
        "protocolo": {
            "selecao": "maior acurácia; desempate por F1-macro na validação",
            "teste_usado_na_selecao": False,
            "normalizacao": "NFC + lowercase + espaços; preserva acentos e stopwords",
            "tamanhos": dados.groupby("split").size().astype(int).to_dict(),
            "quantidade_sintetica_adicional": int(
                (dados["origem"] == "sintetico_issue_251").sum()
            ),
        },
        "melhor_validacao": melhor["registro"],
        "resultados_validacao": resultados,
    }
    if argumentos.avaliar_teste:
        saida["teste_final"] = avaliar_teste_e_exportar(dados, melhor)
    RESULTADO.write_text(
        json.dumps(saida, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(saida["melhor_validacao"], ensure_ascii=False, indent=2))
    if "teste_final" in saida:
        print(json.dumps(saida["teste_final"]["intencao"], ensure_ascii=False, indent=2))
    print(f"Resultados gravados em {RESULTADO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
