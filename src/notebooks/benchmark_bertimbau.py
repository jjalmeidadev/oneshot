"""Avalia o BERTimbau como extrator congelado no split de validação.

O teste permanece inacessado. Os embeddings são calculados com o texto cru,
preservando caixa e acentos para o tokenizador cased do BERTimbau, e então
comparados com classificadores lineares planos e hierárquicos.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import torch
from scipy import sparse
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import normalize
from sklearn.svm import LinearSVC
from transformers import AutoModel, AutoTokenizer

from benchmark_intencoes import (
    ARTEFATOS,
    SEED,
    ClassificadorHierarquico,
    REPRESENTACOES,
    ajustar_representacao,
    carregar_dataset,
    criar_vetorizadores,
    macro_da_intencao,
    transformar,
)


MODELO_BERTIMBAU = "neuralmind/bert-base-portuguese-cased"
RESULTADO = ARTEFATOS / "benchmark_bertimbau.json"
CACHE = ARTEFATOS / ".bertimbau_validacao_cache.npz"
BATCH_SIZE = 32
MAX_LENGTH = 64


def encode(textos: list[str]) -> np.ndarray:
    tokenizador = AutoTokenizer.from_pretrained(MODELO_BERTIMBAU)
    modelo = AutoModel.from_pretrained(MODELO_BERTIMBAU)
    modelo.eval()
    vetores: list[np.ndarray] = []
    with torch.inference_mode():
        for inicio in range(0, len(textos), BATCH_SIZE):
            lote = tokenizador(
                textos[inicio : inicio + BATCH_SIZE],
                padding=True,
                truncation=True,
                max_length=MAX_LENGTH,
                return_tensors="pt",
            )
            estados = modelo(**lote).last_hidden_state
            mascara = lote["attention_mask"].unsqueeze(-1)
            medias = (estados * mascara).sum(dim=1) / mascara.sum(dim=1).clamp(min=1)
            vetores.append(medias.cpu().numpy())
            print(f"BERTimbau: {min(inicio + BATCH_SIZE, len(textos))}/{len(textos)}")
    return normalize(np.vstack(vetores)).astype(np.float32)


def obter_embeddings(textos: list[str], chaves: list[str]) -> np.ndarray:
    if CACHE.exists():
        cache = np.load(CACHE, allow_pickle=False)
        if cache["chaves"].tolist() == chaves:
            return cache["embeddings"]
    embeddings = encode(textos)
    np.savez_compressed(CACHE, chaves=np.array(chaves), embeddings=embeddings)
    return embeddings


def metricas(y, pred) -> dict[str, float]:
    return {
        "acuracia": round(float(accuracy_score(y, pred)), 6),
        "f1_macro": round(float(f1_score(y, pred, average="macro", zero_division=0)), 6),
    }


def main() -> int:
    torch.manual_seed(SEED)
    dados = carregar_dataset()
    desenvolvimento = dados[dados["split"].isin(["treino", "validacao"])].copy()
    desenvolvimento["chave_cache"] = (
        desenvolvimento["origem"].astype(str)
        + ":"
        + desenvolvimento["template_id"].astype(str)
        + ":"
        + desenvolvimento.index.astype(str)
    )
    embeddings = obter_embeddings(
        desenvolvimento["texto"].astype(str).tolist(),
        desenvolvimento["chave_cache"].tolist(),
    )
    mascara_treino = desenvolvimento["split"].to_numpy() == "treino"
    x_treino, x_validacao = embeddings[mascara_treino], embeddings[~mascara_treino]
    y_treino = desenvolvimento.loc[mascara_treino, "intencao"].to_numpy()
    y_validacao = desenvolvimento.loc[~mascara_treino, "intencao"].to_numpy()
    macro_validacao = desenvolvimento.loc[~mascara_treino, "macrointencao"].to_numpy()
    mapa = dados.drop_duplicates("intencao").set_index("intencao")["macrointencao"].to_dict()

    candidatos = {}
    for c in (0.1, 0.5, 1.0, 2.0, 4.0):
        candidatos[f"linear_svc_C_{c:g}"] = lambda c=c: LinearSVC(
            C=c, class_weight="balanced", random_state=SEED
        )
        candidatos[f"hierarquico_linear_svc_C_{c:g}"] = lambda c=c: ClassificadorHierarquico(
            lambda: LinearSVC(C=c, class_weight="balanced", random_state=SEED),
            mapa,
        )
    for c in (0.5, 1.0, 2.0):
        candidatos[f"regressao_logistica_C_{c:g}"] = lambda c=c: LogisticRegression(
            C=c,
            class_weight="balanced",
            max_iter=2_000,
            random_state=SEED,
            solver="lbfgs",
        )

    resultados = []
    for nome, fabrica in candidatos.items():
        inicio = time.perf_counter()
        modelo = fabrica().fit(x_treino, y_treino)
        pred_intencao = modelo.predict(x_validacao)
        pred_macro = macro_da_intencao(pred_intencao, mapa)
        resultados.append(
            {
                "modelo": nome,
                "representacao": "bertimbau_congelado",
                "validacao_intencao": metricas(y_validacao, pred_intencao),
                "validacao_macro": metricas(macro_validacao, pred_macro),
                "segundos_treino": round(time.perf_counter() - inicio, 3),
            }
        )

    # O BERTimbau também é testado como bloco semântico auxiliar do melhor
    # espaço lexical da rodada anterior. O peso do bloco é escolhido apenas na
    # validação, como os demais hiperparâmetros.
    especificacao_lexical = next(
        item
        for item in REPRESENTACOES
        if item.nome == "palavras_1_2_caracteres_3_5"
    )
    vetorizadores = criar_vetorizadores(especificacao_lexical)
    treino = desenvolvimento[mascara_treino]
    validacao = desenvolvimento[~mascara_treino]
    x_lex_treino = ajustar_representacao(vetorizadores, treino["texto"])
    x_lex_validacao = transformar(vetorizadores, validacao["texto"])
    for peso_bert in (0.25, 0.5, 1.0, 2.0):
        x_hibrido_treino = sparse.hstack(
            [x_lex_treino, sparse.csr_matrix(x_treino * peso_bert)], format="csr"
        )
        x_hibrido_validacao = sparse.hstack(
            [x_lex_validacao, sparse.csr_matrix(x_validacao * peso_bert)],
            format="csr",
        )
        for c in (0.5, 1.0, 2.0, 4.0):
            inicio = time.perf_counter()
            modelo = ClassificadorHierarquico(
                lambda c=c: LinearSVC(
                    C=c, class_weight="balanced", random_state=SEED
                ),
                mapa,
            ).fit(x_hibrido_treino, y_treino)
            pred_intencao = modelo.predict(x_hibrido_validacao)
            pred_macro = macro_da_intencao(pred_intencao, mapa)
            resultados.append(
                {
                    "modelo": f"hierarquico_linear_svc_C_{c:g}",
                    "representacao": "tfidf_palavras_caracteres+bertimbau",
                    "peso_bertimbau": peso_bert,
                    "validacao_intencao": metricas(y_validacao, pred_intencao),
                    "validacao_macro": metricas(macro_validacao, pred_macro),
                    "segundos_treino": round(time.perf_counter() - inicio, 3),
                }
            )
            inicio = time.perf_counter()
            modelo_probabilistico = ClassificadorHierarquico(
                lambda c=c: LogisticRegression(
                    C=c,
                    class_weight="balanced",
                    max_iter=2_000,
                    random_state=SEED,
                    solver="liblinear",
                ),
                mapa,
            ).fit(x_hibrido_treino, y_treino)
            pred_intencao = modelo_probabilistico.predict(x_hibrido_validacao)
            pred_macro = macro_da_intencao(pred_intencao, mapa)
            resultados.append(
                {
                    "modelo": f"hierarquico_regressao_logistica_C_{c:g}",
                    "representacao": "tfidf_palavras_caracteres+bertimbau",
                    "peso_bertimbau": peso_bert,
                    "validacao_intencao": metricas(y_validacao, pred_intencao),
                    "validacao_macro": metricas(macro_validacao, pred_macro),
                    "segundos_treino": round(time.perf_counter() - inicio, 3),
                }
            )
            if c in (1.0, 4.0):
                inicio = time.perf_counter()
                modelo_calibrado = ClassificadorHierarquico(
                    lambda c=c: CalibratedClassifierCV(
                        LinearSVC(
                            C=c,
                            class_weight="balanced",
                            random_state=SEED,
                        ),
                        method="sigmoid",
                        cv=3,
                    ),
                    mapa,
                ).fit(x_hibrido_treino, y_treino)
                pred_intencao = modelo_calibrado.predict(x_hibrido_validacao)
                pred_macro = macro_da_intencao(pred_intencao, mapa)
                resultados.append(
                    {
                        "modelo": f"hierarquico_linear_svc_calibrado_C_{c:g}",
                        "representacao": "tfidf_palavras_caracteres+bertimbau",
                        "peso_bertimbau": peso_bert,
                        "validacao_intencao": metricas(y_validacao, pred_intencao),
                        "validacao_macro": metricas(macro_validacao, pred_macro),
                        "segundos_treino": round(time.perf_counter() - inicio, 3),
                    }
                )

    resultados.sort(
        key=lambda item: (
            item["validacao_intencao"]["acuracia"],
            item["validacao_intencao"]["f1_macro"],
        ),
        reverse=True,
    )
    saida = {
        "encoder": MODELO_BERTIMBAU,
        "estrategia": "embeddings congelados com mean pooling",
        "max_length": MAX_LENGTH,
        "teste_usado_na_selecao": False,
        "quantidade_treino": int(mascara_treino.sum()),
        "quantidade_validacao": int((~mascara_treino).sum()),
        "melhor_validacao": resultados[0],
        "resultados_validacao": resultados,
    }
    RESULTADO.write_text(
        json.dumps(saida, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(resultados[0], ensure_ascii=False, indent=2))
    print(f"Resultados gravados em {RESULTADO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
