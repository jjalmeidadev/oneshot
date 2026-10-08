"""Contrato 1.2.0: blocos rastreaveis, texto legado e ambos os canais."""

from dataclasses import replace
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import TypeAdapter, ValidationError

from app.gemini.blocks import ResponseBlock
from app.gemini.client import generate_chat_response
from app.gemini.schemas import GeminiChatRequest, GeminiChatResponse
from app.main import app
from test_audio_upload import AUTH_HEADER, _build_wav
from test_response_references import evidence, provider_response  # noqa: F401


def block_response(monkeypatch, evidence, provider="gemini"):
    attributes = (("Avanço", "42,5%"), ("Status", "Em execução"))
    result = replace(evidence, document=replace(evidence.document, attributes=attributes))
    monkeypatch.setattr("app.gemini.client.retrieve_context", lambda *a, **kw: [result])
    provider_response(monkeypatch, provider,
        "Avanço: 42,5% [Fonte 1]\nStatus: Em execução [Fonte 1]")
    return generate_chat_response(GeminiChatRequest(message="Status e avanço?"))


def test_each_block_has_data_and_citations(monkeypatch, evidence):
    response = block_response(monkeypatch, evidence)
    assert response.contract_version == "1.2.0"
    assert response.text == "Avanço: 42,5% [Fonte 1]\nStatus: Em execução [Fonte 1]"
    table, highlight, indicator, status = response.model_dump()["blocks"]
    assert table == {
        "type": "table", "columns": ["Informação", "Valor"], "rows": [
            {"cells": ["Avanço", "42,5%"], "citation_ids": ["Fonte 1"]},
            {"cells": ["Status", "Em execução"], "citation_ids": ["Fonte 1"]},
        ],
    }
    assert indicator == {"type": "indicator", "label": "Avanço", "value": 42.5,
                         "unit": "%", "citation_ids": ["Fonte 1"]}
    assert highlight["text"] == "Avanço: 42,5%"
    assert status["text"] == "Status: Em execução"
    assert highlight["citation_ids"] == status["citation_ids"] == ["Fonte 1"]


@pytest.mark.parametrize("provider", ["gemini", "openrouter"])
@pytest.mark.parametrize("channel", ["chat", "audio"])
def test_blocks_survive_both_providers_and_channels(monkeypatch, evidence, provider, channel):
    expected = block_response(monkeypatch, evidence, provider)
    monkeypatch.setattr("app.pipeline.trace_interaction", lambda **kw: None)
    with TestClient(app) as client:
        if channel == "chat":
            response = client.post("/api/chat", json={"message": "Status e avanço?"})
        else:
            response = client.post("/api/audio", headers=AUTH_HEADER,
                files={"audio": ("test.wav", _build_wav(), "audio/wav")},
                data={"conversation_id": "blocks-270"})
    assert response.status_code == 200, response.text
    body = response.json()
    chat = body if channel == "chat" else body["chat"]
    assert body["contract_version"] == "1.2.0"
    assert chat["blocks"] == expected.model_dump()["blocks"]
    assert chat["text"] == expected.text
    if channel == "audio":
        assert body["answer"]["blocks"] == chat["blocks"]
        assert body["answer"]["text"] == chat["text"]


@pytest.mark.parametrize("kind", ["table", "indicator", "highlight"])
@pytest.mark.parametrize("tamper", ["data", "citation"])
def test_tampered_block_is_rejected(monkeypatch, evidence, kind, tamper):
    payload = block_response(monkeypatch, evidence).model_dump()
    block = next(item for item in payload["blocks"] if item["type"] == kind)
    if tamper == "citation":
        (block["rows"][0] if kind == "table" else block)["citation_ids"] = ["Fonte 99"]
    elif kind == "table":
        block["rows"][0]["cells"][1] = "100%"
    elif kind == "indicator":
        block["value"] = 100
    else:
        block["text"] = "Status: Concluído"
    with pytest.raises(ValidationError, match="Bloco deve corresponder"):
        GeminiChatResponse.model_validate(payload)


@pytest.mark.parametrize("block", [
    {"type": "unknown"},
    {"type": "table", "columns": [], "rows": []},
    {"type": "table", "columns": ["A", "B"], "rows": [{"cells": ["A"], "citation_ids": ["Fonte 1"]}]},
    {"type": "indicator", "label": "A", "value": float("nan"), "citation_ids": ["Fonte 1"]},
    {"type": "indicator", "label": "A", "value": True, "citation_ids": ["Fonte 1"]},
    {"type": "highlight", "text": "", "citation_ids": ["Fonte 1"]},
    {"type": "highlight", "text": "A", "citation_ids": []},
    {"type": "highlight", "text": "A", "citation_ids": ["Fonte 1"], "html": "unsafe"},
])
def test_malformed_block_contract_is_rejected(block):
    with pytest.raises(ValidationError):
        TypeAdapter(ResponseBlock).validate_python(block)


@pytest.mark.parametrize("value,number,unit", [
    ("12", 12, None), ("-2", -2, None), ("12.5", 12.5, None), ("42,5%", 42.5, "%"),
    ("30/09/2026", None, None), ("PRJ-0442", None, None),
    ("1.234", None, None), ("12 dias se aprovado", None, None),
    ("9" * 400, None, None),
])
def test_indicators_only_use_unambiguous_numeric_attributes(monkeypatch, evidence, value, number, unit):
    result = replace(evidence, document=replace(evidence.document, attributes=(("Métrica", value),)))
    monkeypatch.setattr("app.gemini.client.retrieve_context", lambda *a, **kw: [result])
    provider_response(monkeypatch, "gemini", f"Métrica: {value} [Fonte 1]")
    response = generate_chat_response(GeminiChatRequest(message="Métrica?"))
    indicators = [block for block in response.blocks if block.type == "indicator"]
    assert len(indicators) == (0 if number is None else 1)
    if indicators:
        assert indicators[0].value == number
        assert indicators[0].unit == unit


def test_legacy_text_response_defaults_to_empty_blocks():
    response = GeminiChatResponse(text="Resposta textual", model="test", latency_ms=0, usage={})
    assert response.blocks == []
    assert response.text == "Resposta textual"


def test_verified_response_can_omit_blocks(monkeypatch, evidence):
    payload = block_response(monkeypatch, evidence).model_dump()
    payload.pop("blocks")
    restored = GeminiChatResponse.model_validate(payload)
    assert restored.blocks == []
    assert restored.text == payload["text"]


@pytest.mark.parametrize("empty_retrieval", [True, False])
def test_insufficient_evidence_does_not_generate_blocks(monkeypatch, evidence, empty_retrieval):
    if empty_retrieval:
        monkeypatch.setattr("app.gemini.client.retrieve_context", lambda *a, **kw: [])
    else:
        provider_response(monkeypatch, "gemini", "Avanço: 100% [Fonte 1]")
    response = generate_chat_response(GeminiChatRequest(message="Avanço?"))
    assert response.evidence_status == "insufficient"
    assert response.blocks == []


def test_single_excerpt_is_highlight_without_inventing_indicator(monkeypatch, evidence):
    provider_response(monkeypatch, "gemini", "O prazo e 30/09/2026. [Fonte 1]")
    response = generate_chat_response(GeminiChatRequest(message="Prazo?"))
    assert [block.type for block in response.blocks] == ["highlight"]


def test_published_json_schema_matches_runtime():
    path = Path(__file__).resolve().parents[4] / "docs/contracts/chat-response-1.2.0.schema.json"
    assert json.loads(path.read_text(encoding="utf-8")) == GeminiChatResponse.model_json_schema()


def test_openapi_exposes_discriminated_blocks_in_both_channels():
    schema = app.openapi()["components"]["schemas"]
    for name in ["GeminiChatResponse", "AudioAnswer"]:
        block = schema[name]["properties"]["blocks"]["items"]
        assert block["discriminator"]["propertyName"] == "type"
        assert set(block["discriminator"]["mapping"]) == {"table", "indicator", "highlight"}
