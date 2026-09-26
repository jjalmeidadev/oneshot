"""Treina, calibra e avalia o classificador selecionado na issue #251.

A seleção de representação, arquitetura e hiperparâmetros ocorre nos scripts
``benchmark_intencoes.py`` e ``benchmark_bertimbau.py``. Este script reproduz
apenas a configuração vencedora. O teste só é lido com ``--avaliar-teste``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import joblib
import numpy as np
from scipy import sparse
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.svm import LinearSVC


RAIZ = Path(__file__).resolve().parents[2]
BACKEND = RAIZ / "src" / "backend"
sys.path.insert(0, str(BACKEND))

from app.nlp.classifier import ClassificadorHierarquico  # noqa: E402
from app.nlp.preprocessing import SELECTED_CONFIG, normalizar_portugues  # noqa: E402
from benchmark_bertimbau import MODELO_BERTIMBAU, encode, obter_embeddings  # noqa: E402
from benchmark_intencoes import ARTEFATOS, carregar_dataset  # noqa: E402


SEED = 42
PESO_BERTIMBAU = 2.0
C_LINEAR_SVC = 1.0
CV_CALIBRACAO = 3
MAX_WORD_FEATURES = 50_000
MAX_CHAR_FEATURES = 80_000
ARTEFATO = ARTEFATOS / "classificador_intencoes.joblib"
METRICAS = ARTEFATOS / "metricas.json"
AVALIACAO = ARTEFATOS / "avaliacao_classificador_intencoes.json"
CACHE_TESTE = ARTEFATOS / ".bertimbau_teste_cache.npz"


def criar_vetorizadores() -> dict[str, TfidfVectorizer]:
    return {
        "palavras": TfidfVectorizer(
            preprocessor=normalizar_portugues,
            lowercase=False,
            strip_accents=None,
            stop_words=None,
            ngram_range=(1, 2),
            min_df=1,
            max_features=MAX_WORD_FEATURES,
            sublinear_tf=True,
            norm="l2",
        ),
        "caracteres": TfidfVectorizer(
            preprocessor=normalizar_portugues,
            lowercase=False,
            strip_accents=None,
            stop_words=None,
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=1,
            max_features=MAX_CHAR_FEATURES,
            sublinear_tf=True,
            norm="l2",
        ),
    }


def ajustar_vetorizadores(vetorizadores, textos, embeddings):
    return sparse.hstack(
        [
            vetorizadores["palavras"].fit_transform(textos),
            vetorizadores["caracteres"].fit_transform(textos),
            sparse.csr_matrix(embeddings * PESO_BERTIMBAU),
        ],
        format="csr",
    )


def transformar(vetorizadores, textos, embeddings):
    return sparse.hstack(
        [
            vetorizadores["palavras"].transform(textos),
            vetorizadores["caracteres"].transform(textos),
            sparse.csr_matrix(embeddings * PESO_BERTIMBAU),
        ],
        format="csr",
    )


def fabrica_modelo():
    return CalibratedClassifierCV(
        LinearSVC(
            C=C_LINEAR_SVC,
            class_weight="balanced",
            random_state=SEED,
        ),
        method="sigmoid",
        cv=CV_CALIBRACAO,
    )


def treinar_modelo(x, y_macro, y_intencao):
    return ClassificadorHierarquico(fabrica_modelo).fit(
        x,
        np.asarray(y_macro),
        np.asarray(y_intencao),
    )


def predizer(modelo, x):
    proba_intencao = modelo.predict_proba_intencao(x)
    pred_intencao = modelo.classes_[proba_intencao.argmax(axis=1)]
    classes_macro, proba_macro = modelo.predict_proba_macro(x)
    pred_macro = classes_macro[proba_macro.argmax(axis=1)]
    return pred_intencao, pred_macro, proba_intencao, proba_macro


def metricas(y_verdadeiro, y_predito) -> dict[str, float]:
    return {
        "acuracia": round(float(accuracy_score(y_verdadeiro, y_predito)), 6),
        "f1_macro": round(
            float(f1_score(y_verdadeiro, y_predito, average="macro", zero_division=0)),
            6,
        ),
    }


def escolher_limiar(confiancas, acertos, alvo: float) -> tuple[float, dict]:
    linhas = []
    for limiar in np.arange(0.0, 0.951, 0.025):
        aceitos = confiancas >= limiar
        linhas.append(
            {
                "limiar": round(float(limiar), 3),
                "cobertura": round(float(aceitos.mean()), 6),
                "acuracia_aceitos": round(
                    float(acertos[aceitos].mean()) if aceitos.any() else 0.0, 6
                ),
            }
        )
    elegiveis = [linha for linha in linhas if linha["acuracia_aceitos"] >= alvo]
    escolhida = max(elegiveis, key=lambda item: item["cobertura"]) if elegiveis else max(
        linhas, key=lambda item: (item["acuracia_aceitos"], item["cobertura"])
    )
    return escolhida["limiar"], escolhida


def embeddings_teste(textos: list[str]) -> np.ndarray:
    chaves = np.array([hashlib.sha256(texto.encode("utf-8")).hexdigest() for texto in textos])
    if CACHE_TESTE.exists():
        cache = np.load(CACHE_TESTE, allow_pickle=False)
        if cache["chaves"].tolist() == chaves.tolist():
            return cache["embeddings"]
    embeddings = encode(textos)
    np.savez_compressed(CACHE_TESTE, chaves=chaves, embeddings=embeddings)
    return embeddings


def hash_dados() -> str:
    digest = hashlib.sha256()
    for caminho in (
        ARTEFATOS / "dataset_intencoes.csv",
        ARTEFATOS / "consultas_sinteticas_issue_251.csv",
    ):
        digest.update(caminho.read_bytes())
    return digest.hexdigest()


def relatorio_por_classe(y_verdadeiro, y_predito, classes: list[str]) -> dict:
    precisao, recall, f1, suporte = precision_recall_fscore_support(
        y_verdadeiro, y_predito, labels=classes, zero_division=0
    )
    return {
        classe: {
            "precisao": round(float(precisao[indice]), 6),
            "recall": round(float(recall[indice]), 6),
            "f1": round(float(f1[indice]), 6),
            "suporte": int(suporte[indice]),
        }
        for indice, classe in enumerate(classes)
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--avaliar-teste",
        action="store_true",
        help="treina em desenvolvimento, abre o teste uma vez e exporta o artefato",
    )
    parser.add_argument(
        "--reparar-artefato",
        action="store_true",
        help="remove a fábrica de treino do joblib sem refazer a avaliação",
    )
    argumentos = parser.parse_args()
    if argumentos.reparar_artefato:
        dados_artefato = joblib.load(ARTEFATO)
        dados_artefato["modelo"].fabrica = None
        joblib.dump(dados_artefato, ARTEFATO)
        novo_hash = hashlib.sha256(ARTEFATO.read_bytes()).hexdigest()
        for caminho in (AVALIACAO, METRICAS):
            relatorio = json.loads(caminho.read_text(encoding="utf-8"))
            relatorio["artefato_sha256"] = novo_hash
            caminho.write_text(
                json.dumps(relatorio, ensure_ascii=False, indent=2, sort_keys=True)
                + "\n",
                encoding="utf-8",
            )
        print(f"Artefato reparado; SHA-256: {novo_hash}")
        return 0
    dados = carregar_dataset()
    desenvolvimento = dados[dados["split"].isin(["treino", "validacao"])].copy()
    chaves = (
        desenvolvimento["origem"].astype(str)
        + ":"
        + desenvolvimento["template_id"].astype(str)
        + ":"
        + desenvolvimento.index.astype(str)
    ).tolist()
    embeddings_dev = obter_embeddings(
        desenvolvimento["texto"].astype(str).tolist(), chaves
    )
    mascara_treino = desenvolvimento["split"].to_numpy() == "treino"
    treino = desenvolvimento[mascara_treino]
    validacao = desenvolvimento[~mascara_treino]

    vet_validacao = criar_vetorizadores()
    x_treino = ajustar_vetorizadores(
        vet_validacao, treino["texto"], embeddings_dev[mascara_treino]
    )
    x_validacao = transformar(
        vet_validacao, validacao["texto"], embeddings_dev[~mascara_treino]
    )
    modelo_validacao = treinar_modelo(
        x_treino, treino["macrointencao"], treino["intencao"]
    )
    pred_int_val, pred_macro_val, p_int_val, p_macro_val = predizer(
        modelo_validacao, x_validacao
    )
    limiar_macro, curva_macro = escolher_limiar(
        p_macro_val.max(axis=1),
        pred_macro_val == validacao["macrointencao"].to_numpy(),
        alvo=0.97,
    )
    limiar_intencao, curva_intencao = escolher_limiar(
        p_int_val.max(axis=1),
        pred_int_val == validacao["intencao"].to_numpy(),
        alvo=0.90,
    )
    validacao_resultado = {
        "intencao": metricas(validacao["intencao"], pred_int_val),
        "macrointencao": metricas(validacao["macrointencao"], pred_macro_val),
        "limiar_macro": limiar_macro,
        "limiar_intencao": limiar_intencao,
        "ponto_macro": curva_macro,
        "ponto_intencao": curva_intencao,
    }
    print(json.dumps(validacao_resultado, ensure_ascii=False, indent=2))
    if not argumentos.avaliar_teste:
        return 0

    teste = dados[(dados["split"] == "teste") & (dados["origem"] == "dataset_base")]
    emb_teste = embeddings_teste(teste["texto"].astype(str).tolist())
    vetorizadores = criar_vetorizadores()
    x_desenvolvimento = ajustar_vetorizadores(
        vetorizadores, desenvolvimento["texto"], embeddings_dev
    )
    x_teste = transformar(vetorizadores, teste["texto"], emb_teste)
    modelo = treinar_modelo(
        x_desenvolvimento,
        desenvolvimento["macrointencao"],
        desenvolvimento["intencao"],
    )
    pred_int, pred_macro, p_int, p_macro = predizer(modelo, x_teste)
    classes = sorted(dados["intencao"].unique().tolist())
    por_classe = relatorio_por_classe(teste["intencao"], pred_int, classes)
    avaliacao = {
        "versao": 2,
        "dados_sha256": hash_dados(),
        "encoder": MODELO_BERTIMBAU,
        "representacao": "TF-IDF palavras (1,2) + caracteres (3,5) + BERTimbau",
        "arquitetura": "hierarquica",
        "modelo": "LinearSVC calibrada",
        "hiperparametros": {
            "C": C_LINEAR_SVC,
            "cv_calibracao": CV_CALIBRACAO,
            "peso_bertimbau": PESO_BERTIMBAU,
        },
        "teste_usado_na_selecao": False,
        "tamanhos": {
            "treino_base": int(
                ((dados["split"] == "treino") & (dados["origem"] == "dataset_base")).sum()
            ),
            "sinteticos_adicionais": int(
                (dados["origem"] == "sintetico_issue_251").sum()
            ),
            "validacao": int((dados["split"] == "validacao").sum()),
            "teste": int(len(teste)),
        },
        "validacao": validacao_resultado,
        "teste": {
            "intencao": metricas(teste["intencao"], pred_int),
            "macrointencao": metricas(teste["macrointencao"], pred_macro),
        },
        "metricas_por_classe": por_classe,
        "matriz_confusao": {
            "labels": classes,
            "valores": confusion_matrix(
                teste["intencao"], pred_int, labels=classes
            ).astype(int).tolist(),
        },
        "roteamento": {
            "abaixo_limiar_macro": int((p_macro.max(axis=1) < limiar_macro).sum()),
            "abaixo_limiar_intencao": int(
                (
                    (p_macro.max(axis=1) >= limiar_macro)
                    & (p_int.max(axis=1) < limiar_intencao)
                ).sum()
            ),
        },
        "limitacoes": [
            "A base continua majoritariamente sintética e requer validação externa com consultas reais.",
            "O BERTimbau aumenta custo de carregamento e inferência em relação ao modelo lexical.",
            "A acurácia principal considera todos os exemplos antes de qualquer abstenção.",
        ],
    }
    # A fábrica é necessária apenas durante o fit. Mantê-la prenderia o
    # pickle ao ``__main__`` do script de treino e impediria o backend de
    # carregar o artefato em outro processo.
    modelo.fabrica = None
    joblib.dump(
        {
            "tfidf_palavras": vetorizadores["palavras"],
            "tfidf_caracteres": vetorizadores["caracteres"],
            "svd_palavras": None,
            "svd_caracteres": None,
            "scalers": {"bertimbau": PESO_BERTIMBAU},
            "modelo": modelo,
            "config_preprocessamento": dict(SELECTED_CONFIG),
            "representacao": avaliacao["representacao"],
            "blocos_da_representacao": [
                "tfidf_palavra",
                "tfidf_char",
                "bertimbau",
            ],
            "limiar_macro": limiar_macro,
            "limiar_intencao": limiar_intencao,
            "intencao2macro": dados.drop_duplicates("intencao")
            .set_index("intencao")["macrointencao"]
            .to_dict(),
        },
        ARTEFATO,
    )
    avaliacao["artefato_sha256"] = hashlib.sha256(ARTEFATO.read_bytes()).hexdigest()
    conteudo = json.dumps(avaliacao, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    AVALIACAO.write_text(conteudo, encoding="utf-8")
    METRICAS.write_text(conteudo, encoding="utf-8")
    print(json.dumps(avaliacao["teste"], ensure_ascii=False, indent=2))
    print(f"Artefato exportado em {ARTEFATO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
