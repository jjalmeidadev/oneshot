"""S5-33 (#287): reexecução de CT-RF02-01 e CT-RF03-02 após a S5-28 (#282).

Os dois casos são julgados pela classificação e pelo encaminhamento:

* CT-RF02-01 — "Mostre o status do projeto PRJ-0442" deve selecionar
  ``consulta_status_projeto`` como intenção primária e seguir ao catálogo.
* CT-RF03-02 — "Reserve uma sala de reunião para amanhã" não pode virar
  ``transacao_agendar_compromisso``; deve ser tratada como fora de escopo,
  sem chamar o provedor.

A entrada é a mesma da rodada de 23/09 (``evidencias/rf01-rf10``) e passa por
``POST /api/chat`` com classificador, roteamento e extração de entidades
reais. Só a geração do texto pelo LLM é substituída por um duplo, porque o
texto da resposta não é critério destes casos; o duplo registra se foi chamado
e com qual intenção. Os casos dependem do classificador real
(``requirements-pln.txt`` e BERTimbau) e se ignoram sem ele.

CT-RF06-01, CT-RF08-01 e a recuperação do RNF06 dependem da S5-12 (#266) e
estão registrados como bloqueados no relatório, não aqui.
``S5_33_EVIDENCE_DIR`` habilita a gravação dos artefatos da rodada.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

pytest.importorskip("torch", reason="instale requirements-pln.txt")
pytest.importorskip("transformers", reason="instale requirements-pln.txt")

from app.gemini.schemas import GeminiChatResponse, GeminiUsage  # noqa: E402
from app.main import app  # noqa: E402

pytestmark = pytest.mark.integration

TEXTO_DUPLO = "Resposta do duplo do provedor (S5-33): o texto não é critério deste caso."


def evidence(name: str, payload) -> None:
    print(json.dumps({"artifact": name, "observation": payload}, ensure_ascii=True, default=str))
    target = os.getenv("S5_33_EVIDENCE_DIR")
    if target:
        directory = Path(target)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8"
        )


@pytest.fixture
def provedor(monkeypatch):
    chamadas: list[dict] = []

    def duplo(request, **kwargs):
        intent = kwargs.get("intent")
        chamadas.append({
            "mensagem": request.message,
            "intencao_enviada_ao_provedor": intent.specific if intent else None,
            "macro_enviada_ao_provedor": intent.macro if intent else None,
        })
        return GeminiChatResponse(
            text=TEXTO_DUPLO, model="duplo-s5-33", interaction_id=None,
            latency_ms=0, retrieval_ms=0, usage=GeminiUsage(), sources=[],
        )

    monkeypatch.setattr("app.pipeline.generate_chat_response", duplo)
    monkeypatch.setattr("app.pipeline.trace_interaction", lambda **_kwargs: "trace-s5-33")
    return chamadas


def _executar(mensagem: str, conversa: str) -> tuple[int, dict]:
    with TestClient(app) as client:
        resposta = client.post("/api/chat", json={
            "message": mensagem, "conversation_id": conversa,
            "use_intent_classifier": True, "proactivity_enabled": False,
        })
    return resposta.status_code, resposta.json()


def _observacao(caso, mensagem, http, corpo, chamadas, esperado):
    intent = corpo.get("intent") or {}
    return {
        "caso": caso, "entrada": mensagem, "http": http,
        "intent": {chave: intent.get(chave) for chave in (
            "macro", "specific", "confidence_macro", "confidence_specific",
            "flow", "handler", "routing_rule")},
        "alternativas": intent.get("alternatives", [])[:3],
        "modelo_da_resposta": corpo.get("model"),
        "tokens_do_provedor": (corpo.get("usage") or {}).get("total_tokens"),
        "provedor_chamado": bool(chamadas), "chamadas_ao_provedor": chamadas,
        "texto": corpo.get("text"),
        "resultado_esperado": esperado,
        "rodada_anterior": "evidencias/rf01-rf10 (23/09/2026, commit be814f6): FALHOU",
        "protocolo": "POST /api/chat via TestClient; classificador, roteamento e entidades reais; LLM substituído por duplo",
    }


def test_ct_rf02_01_reexecucao(provedor):
    mensagem = "Mostre o status do projeto PRJ-0442"
    http, corpo = _executar(mensagem, "ct-rf02-01-s5-33")
    observado = _observacao(
        "CT-RF02-01", mensagem, http, corpo, provedor,
        "CONSULTA / consulta_status_projeto como intenção primária, encaminhada ao catálogo",
    )
    evidence("CT-RF02-01.json", observado)
    assert http == 200, observado
    assert observado["intent"]["macro"] == "CONSULTA", observado
    assert observado["intent"]["specific"] == "consulta_status_projeto", observado
    # Encaminhada ao catálogo: o provedor recebe a intenção específica, não o fallback genérico.
    assert provedor and provedor[-1]["intencao_enviada_ao_provedor"] == "consulta_status_projeto", observado


def test_ct_rf03_02_reexecucao(provedor):
    mensagem = "Reserve uma sala de reunião para amanhã"
    http, corpo = _executar(mensagem, "ct-rf03-02-s5-33")
    observado = _observacao(
        "CT-RF03-02", mensagem, http, corpo, provedor,
        "Sem associação a transacao_agendar_compromisso; fora de escopo ou pedido de reformulação, sem chamar o provedor",
    )
    evidence("CT-RF03-02.json", observado)
    assert http == 200, observado
    assert observado["intent"]["specific"] != "transacao_agendar_compromisso", observado
    assert observado["intent"]["macro"] == "FORA_DE_ESCOPO", observado
    assert not provedor, observado
    assert observado["tokens_do_provedor"] == 0 and corpo.get("text"), observado
