"""Referencias nas respostas: evidencia sintetica entre recuperacao, provedores, API e auditoria."""
import json

import pytest
from fastapi.testclient import TestClient

from app.audio import transcription
from app.database.tracing import trace_interaction
from app.gemini.client import generate_chat_response
from app.gemini.schemas import GeminiChatRequest
from app.main import app
from app.nlp.schemas import AudioIntent
from app.rag.database import _row_to_result
from test_audio_upload import AUTH_HEADER, _build_wav, transcricao_fixa
from test_gemini_client import FakeResponse
from test_traceability import FakeCursor, FakeConnection
from test_pipeline_api import _classification_result


@pytest.fixture
def evidence(monkeypatch):
    result = _row_to_result(dict(
        extract_id="extract-17", artifact_id="artifact-17", project_id="project-17",
        partner_source_id="lista:17", artifact_title="Prazo sintetico",
        sharepoint_library="Projetos", sharepoint_url="https://example.test/17",
        last_modified="2026-09-24T12:00:00Z", content_text="O prazo e 30/09/2026.",
        source_locator="Planilha!B17", score=4,
        extract_metadata={
            "registration_period": {"start": "2026-09-01", "end": "2026-09-24"},
            "validity": {"start": "2026-09-01", "end": "2026-09-30"},
        },
    ))
    monkeypatch.setenv("GEMINI_API_KEY", "synthetic")
    monkeypatch.setenv("OPENROUTER_API_KEY", "synthetic")
    monkeypatch.setenv("AUDIO_SIMULATED_IDENTITIES", "token-de-teste=usuario-teste")
    monkeypatch.setattr("app.gemini.client.retrieve_context", lambda *a, **kw: [result])
    monkeypatch.setattr("app.nlp.inference.classify", lambda _: _classification_result())
    monkeypatch.setattr(transcription, "transcribe", transcricao_fixa(
        text="Qual o prazo?", confidence=.9, duration_seconds=1))
    return result


def provider_response(monkeypatch, provider, text):
    monkeypatch.setenv("LLM_PROVIDER", provider)
    payload = (
        {"id": "provider-17", "model": "synthetic-model", "choices": [{"message": {"content": text}}]}
        if provider == "openrouter" else
        {"id": "provider-17", "model": "synthetic-model", "steps": [
            {"type": "model_output", "content": [{"type": "text", "text": text}]}]}
    )
    monkeypatch.setattr("app.gemini.client.urlopen", lambda *a, **kw: FakeResponse(payload))


@pytest.mark.parametrize("provider", ["gemini", "openrouter"])
@pytest.mark.parametrize("channel", ["chat", "audio"])
def test_references_survive_provider_api_and_audit(monkeypatch, evidence, provider, channel):
    monkeypatch.setenv("DATABASE_URL", "postgresql://synthetic:synthetic@example.test/test")
    provider_response(monkeypatch, provider, "O prazo e 30/09/2026. [Fonte 1]")
    fetch_values = [("intent-17",), ("conversation-17",), ("trace-17",)]
    if channel == "audio":
        fetch_values = [("intent-17",), None, ("conversation-17",), ("trace-17",)]
    cursor = FakeCursor(fetch_values=fetch_values)
    connection = FakeConnection(cursor)

    def trace(**kwargs):
        return trace_interaction(**kwargs, connect=lambda *a, **kw: connection)

    monkeypatch.setattr("app.pipeline.trace_interaction", trace)
    with TestClient(app) as client:
        if channel == "chat":
            response = client.post("/api/chat", json={"message": "Qual o prazo?"})
        else:
            response = client.post("/api/audio", headers=AUTH_HEADER,
                files={"audio": ("test.wav", _build_wav(), "audio/wav")},
                data={"conversation_id": "conversation-17"})
    assert response.status_code == 200, response.text
    body = response.json()
    chat = body if channel == "chat" else body["chat"]
    assert body["trace_id"] == chat["trace_id"] == "trace-17"
    assert chat["interaction_id"] == "provider-17"
    assert body["contract_version"] == chat["contract_version"] == "1.1.0"
    assert chat["evidence_status"] == "referenced"
    assert chat["claims"][0]["citation_ids"] == ["Fonte 1"]
    source = chat["sources"][0]
    assert (source["artifact_id"], source["extract_id"], source["project_id"]) == (
        "artifact-17", "extract-17", "project-17")
    assert source["source_locator"] == "Planilha!B17"
    assert source["last_modified"] == evidence.document.last_modified
    assert source["registration_period"] == evidence.document.registration_period
    assert source["validity"] == evidence.document.validity
    assert chat["claims"][0]["evidence"] == [{
        "citation_id": "Fonte 1", "field": "excerpt", "attribute": None,
        "quote": source["excerpt"]}]
    params = next(params for query, params in cursor.calls
                  if "INSERT INTO public.consulted_sources" in query)
    assert connection.committed
    assert params[0] == body["trace_id"]
    metadata = json.loads(params[-1])
    assert metadata["excerpt"] == source["excerpt"]
    assert metadata["claims"] == chat["claims"]
    assert metadata["registration_period"] == source["registration_period"]
    interaction = next(params for query, params in cursor.calls
                       if "INSERT INTO public.ai_interactions" in query)
    assert interaction[6] == "consulta_status_projeto"
    assert interaction[11] == chat["text"]
    events = [params for query, params in cursor.calls if "INSERT INTO public.audit_events" in query]
    assert all(event[0] == body["trace_id"] for event in events)
    snapshot = json.loads(next(event[-2] for event in events
                              if event[1] == "database_rag_sources_retrieved"))
    assert snapshot["claims"] == chat["claims"]
    assert "trace_sources" not in chat
    if channel == "audio":
        assert body["answer"]["claims"] == chat["claims"]
        assert body["answer"]["evidence_status"] == chat["evidence_status"]
        assert body["answer"]["sources"][0] == {
            **source, "artifact": source["title"], "section": "Planilha!B17"}


@pytest.mark.parametrize("provider", ["gemini", "openrouter"])
@pytest.mark.parametrize("text", [
    "O prazo e amanha.", "O prazo e amanha [Fonte 99].",
    "O prazo e amanha [Fonte 1].\nO custo e zero.",
    "O custo e zero. O prazo e amanha [Fonte 1].", "[Fonte 1]",
])
def test_missing_or_invalid_citations_abstain(monkeypatch, evidence, provider, text):
    provider_response(monkeypatch, provider, text)
    response = generate_chat_response(GeminiChatRequest(message="Qual o prazo?"))
    assert response.evidence_status == "insufficient"
    assert response.claims == []
    assert "Não há evidência" in response.text
    assert response.sources[0].extract_id == "extract-17"


@pytest.mark.parametrize("with_intent", [True, False])
def test_empty_retrieval_abstains_without_generation(monkeypatch, evidence, with_intent):
    monkeypatch.setattr("app.gemini.client.retrieve_context", lambda *a, **kw: [])
    monkeypatch.setattr("app.gemini.client._call_llm", lambda *a, **kw: pytest.fail("Unexpected LLM"))
    intent = AudioIntent(macro="CONSULTA", specific="consulta_cronograma_prazo",
                         confidence_macro=0.9, confidence_specific=0.8)
    response = generate_chat_response(GeminiChatRequest(message="Prazo?"),
                                      intent=intent if with_intent else None)
    assert response.evidence_status == "insufficient"
    assert response.sources == response.claims == []


def test_missing_metadata_is_not_invented(monkeypatch, evidence):
    from dataclasses import replace
    result = replace(evidence, document=replace(evidence.document,
        artifact_id=None, extract_id=None, project_id=None, source_locator=None,
        last_modified="", registration_period=None, validity=None))
    monkeypatch.setattr("app.gemini.client.retrieve_context", lambda *a, **kw: [result])
    provider_response(monkeypatch, "gemini", "O prazo e 30/09/2026 [Fonte 1].")
    source = generate_chat_response(GeminiChatRequest(message="Prazo?")).sources[0]
    assert source.artifact_id is source.extract_id is source.registration_period is None
    assert source.last_modified == ""


@pytest.mark.parametrize("provider", ["gemini", "openrouter"])
def test_empty_provider_output_remains_a_controlled_error(monkeypatch, evidence, provider):
    from app.gemini.client import GeminiAPIError
    provider_response(monkeypatch, provider, "")
    with pytest.raises(GeminiAPIError, match="conteudo de texto"):
        generate_chat_response(GeminiChatRequest(message="Prazo?"))


def test_schema_rejects_dangling_claim_reference():
    from pydantic import ValidationError
    from app.gemini.schemas import GeminiChatResponse
    with pytest.raises(ValidationError, match="fonte inexistente"):
        GeminiChatResponse(text="Prazo [Fonte 99]", model="test", latency_ms=0,
            usage={}, evidence_status="referenced",
            claims=[{"text": "Prazo", "citation_ids": ["Fonte 99"]}])


@pytest.mark.parametrize("supported", [True, False])
def test_audit_snapshot_and_limitation_are_correlated(monkeypatch, evidence, supported):
    from app.database.tracing import _insert_audit_events, _limitation_response
    provider_response(monkeypatch, "gemini",
        "O prazo e 30/09/2026. [Fonte 1]" if supported else "Prazo sem fonte.")
    request = GeminiChatRequest(message="Prazo?")
    response = generate_chat_response(request)
    cursor = FakeCursor()
    _insert_audit_events(
        cursor, interaction_id="trace-17", correlation_id="correlation-17",
        request=request, response=response, intent=None, entities=[],
        status="processado", error_message=None, user_id=None, requester_id=None,
    )
    event = next(params for _, params in cursor.calls
                 if params[1] == "database_rag_sources_retrieved")
    assert event[0] == "trace-17"
    assert event[3] == ("sucesso" if supported else "pendente")
    assert event[-1] == "correlation-17"
    snapshot = json.loads(event[-2])
    assert snapshot["sources"] == [source.model_dump() for source in response.sources]
    assert snapshot["claims"] == [claim.model_dump() for claim in response.claims]
    assert snapshot["provider_interaction_id"] == "provider-17"
    assert _limitation_response(None, response, None) == (None if supported else response.text)


def test_multiple_extracts_of_same_source_have_distinct_citations(monkeypatch, evidence):
    from dataclasses import replace
    second = replace(evidence, document=replace(evidence.document,
        extract_id="extract-18", content="O custo e 10 reais."))
    monkeypatch.setattr("app.gemini.client.retrieve_context", lambda *a, **kw: [evidence, second])
    provider_response(monkeypatch, "gemini",
        "O prazo e 30/09/2026 [Fonte 1].\nO custo e 10 reais [Fonte 2].")
    response = generate_chat_response(GeminiChatRequest(message="Prazo e custo?"))
    assert response.evidence_status == "referenced"
    assert [claim.citation_ids for claim in response.claims] == [["Fonte 1"], ["Fonte 2"]]
    assert response.sources[0].id == response.sources[1].id
    assert response.sources[0].extract_id != response.sources[1].extract_id


@pytest.mark.parametrize("provider", ["gemini", "openrouter"])
@pytest.mark.parametrize("channel", ["chat", "audio"])
@pytest.mark.parametrize("invented", [
    "O prazo e 01/10/2026. [Fonte 1]",  # mesmo ID, data inventada
    "O prazo nao e 30/09/2026. [Fonte 1]",  # negacao invertida
    "O prazo e 30/09/2026 e o custo e zero. [Fonte 1]",  # fato adicional
])
def test_valid_citation_does_not_authorize_invented_fact(monkeypatch, evidence, provider, channel, invented):
    provider_response(monkeypatch, provider, invented)
    traces = []
    monkeypatch.setattr("app.pipeline.trace_interaction", lambda **kw: traces.append(kw))
    with TestClient(app) as client:
        if channel == "chat":
            result = client.post("/api/chat", json={"message": "Qual o prazo?"})
        else:
            result = client.post("/api/audio", headers=AUTH_HEADER,
                files={"audio": ("test.wav", _build_wav(), "audio/wav")},
                data={"conversation_id": "negative-17"})
    assert result.status_code == 200
    body = result.json()
    chat = body if channel == "chat" else body["chat"]
    assert chat["evidence_status"] == "insufficient"
    assert chat["claims"] == []
    assert "Não há evidência" in chat["text"]
    assert traces[0]["response"].text == chat["text"]
    if channel == "audio":
        assert body["answer"]["text"] == chat["text"]
        assert body["answer"]["evidence_status"] == "insufficient"


def test_complete_attribute_is_supported_but_rewording_is_not(monkeypatch, evidence):
    for answer, supported in [
        ("Vigencia: de 2026-09-01 a 2026-09-30 [Fonte 1]", True),
        ("Vigencia: de 2026-09-01 a 2026-10-30 [Fonte 1]", False),
        ("de 2026-09-01 a 2026-09-30 [Fonte 1]", False),
    ]:
        provider_response(monkeypatch, "gemini", answer)
        response = generate_chat_response(GeminiChatRequest(message="Vigencia?"))
        assert response.evidence_status == ("referenced" if supported else "insufficient")
        if supported:
            support = response.claims[0].evidence[0]
            assert support.field == "attribute"
            assert support.attribute == "Vigencia"
            assert support.quote == "Vigencia: de 2026-09-01 a 2026-09-30"


@pytest.mark.parametrize("answer", [
    "O projeto esta aprovado. [Fonte 1]",  # omite negacao anterior
    "Se houver licenca, o projeto esta aprovado. [Fonte 1]",  # omite contexto posterior
])
def test_partial_excerpt_cannot_drop_conditions(monkeypatch, evidence, answer):
    from dataclasses import replace
    document = replace(evidence.document, content=(
        "Se houver licenca, o projeto esta aprovado. A licenca ainda nao foi emitida."))
    monkeypatch.setattr("app.gemini.client.retrieve_context",
                        lambda *a, **kw: [replace(evidence, document=document)])
    provider_response(monkeypatch, "gemini", answer)
    response = generate_chat_response(GeminiChatRequest(message="Status?"))
    assert response.evidence_status == "insufficient"


def test_citation_cannot_borrow_evidence_from_another_source(monkeypatch, evidence):
    from dataclasses import replace
    second = replace(evidence, document=replace(evidence.document,
        extract_id="extract-18", content="O prazo e 01/10/2026."))
    monkeypatch.setattr("app.gemini.client.retrieve_context", lambda *a, **kw: [evidence, second])
    provider_response(monkeypatch, "gemini", "O prazo e 30/09/2026. [Fonte 2]")
    response = generate_chat_response(GeminiChatRequest(message="Prazo?"))
    assert response.evidence_status == "insufficient"


def test_schema_rejects_tampered_quote_and_unverified_text(monkeypatch, evidence):
    from pydantic import ValidationError
    from app.gemini.schemas import GeminiChatResponse
    provider_response(monkeypatch, "gemini", "O prazo e 30/09/2026. [Fonte 1]")
    response = generate_chat_response(GeminiChatRequest(message="Prazo?"))
    payload = response.model_dump()
    payload["claims"][0]["evidence"][0]["quote"] = "O prazo e 01/10/2026."
    with pytest.raises(ValidationError, match="integralmente"):
        GeminiChatResponse.model_validate(payload)
    payload = response.model_dump()
    payload["text"] += " O custo e zero."
    with pytest.raises(ValidationError, match="Texto deve corresponder"):
        GeminiChatResponse.model_validate(payload)


def test_retrieval_failure_is_controlled_in_both_channels(monkeypatch, evidence):
    from app.database.connection import DatabaseConnectionError
    def fail(*args, **kwargs):
        raise DatabaseConnectionError("internal-secret")
    monkeypatch.setattr("app.gemini.client.retrieve_context", fail)
    monkeypatch.setattr("app.pipeline.trace_interaction", lambda **kw: None)
    monkeypatch.setattr("app.gemini.client._call_llm", lambda *a, **kw: pytest.fail("Unexpected LLM"))
    with TestClient(app) as client:
        text = client.post("/api/chat", json={"message": "Prazo?"})
        audio = client.post("/api/audio", headers=AUTH_HEADER,
            files={"audio": ("test.wav", _build_wav(), "audio/wav")},
            data={"conversation_id": "error-17"})
    assert text.status_code == 503
    assert audio.status_code == 502  # envelope de erro de provedor do audio
    assert "internal-secret" not in text.text + audio.text


@pytest.mark.parametrize("answer", [
    "O prazo e 30/09/2026 [Fonte 1]",  # sem o ponto final do trecho
    "O prazo é 30/09/2026. [Fonte 1]",  # acento acrescentado pelo modelo
    "- O prazo e 30/09/2026. [Fonte 1]",  # marcador de lista
    "1. O prazo e 30/09/2026. [Fonte 1]",  # lista numerada
    "**O prazo e 30/09/2026.** [Fonte 1]",  # negrito
    "O prazo e 30/09/2026. (Fonte 1)",  # citacao entre parenteses
    "Segundo o cronograma:\nO prazo e 30/09/2026. [Fonte 1]",  # cabecalho sem fato
])
def test_presentation_variants_of_a_complete_copy_are_accepted(monkeypatch, evidence, answer):
    provider_response(monkeypatch, "gemini", answer)
    response = generate_chat_response(GeminiChatRequest(message="Prazo?"))
    assert response.evidence_status == "referenced"
    assert response.text == "O prazo e 30/09/2026. [Fonte 1]"


def test_grouped_citation_requires_support_in_every_source(monkeypatch, evidence):
    from dataclasses import replace
    second = replace(evidence, document=replace(evidence.document,
        extract_id="extract-18", content="O prazo é 30/09/2026."))
    monkeypatch.setattr("app.gemini.client.retrieve_context", lambda *a, **kw: [evidence, second])
    provider_response(monkeypatch, "gemini", "O prazo e 30/09/2026. [Fontes 1 e 2]")
    response = generate_chat_response(GeminiChatRequest(message="Prazo?"))
    assert response.evidence_status == "referenced"
    assert response.claims[0].citation_ids == ["Fonte 1", "Fonte 2"]
    assert response.text == "O prazo e 30/09/2026. [Fonte 1] [Fonte 2]"


def test_recommendation_is_only_accepted_in_the_secondary_response(monkeypatch, evidence):
    provider_response(monkeypatch, "gemini",
        "O prazo e 30/09/2026. [Fonte 1]\nSugestão: Confirmar o prazo com o fornecedor.")
    response = generate_chat_response(GeminiChatRequest(message="Prazo?"))
    assert response.evidence_status == "insufficient"


def test_schema_rejects_recommendation_with_new_facts(monkeypatch, evidence):
    from pydantic import ValidationError
    from app.gemini.schemas import GeminiChatResponse
    provider_response(monkeypatch, "gemini", "O prazo e 30/09/2026. [Fonte 1]")
    payload = generate_chat_response(GeminiChatRequest(message="Prazo?")).model_dump()
    payload["recommendation"] = "Adiar para 15/10/2026."
    payload["text"] += "\nSugestão: Adiar para 15/10/2026."
    with pytest.raises(ValidationError, match="numeros ou datas"):
        GeminiChatResponse.model_validate(payload)


@pytest.mark.parametrize("content", ["O prazo e 30/09/2026. [Fonte 1]\nO custo e", ""])
def test_interrupted_answer_keeps_the_interruption_notice(monkeypatch, evidence, content):
    from app.gemini.client import AVISO_RESPOSTA_INTERROMPIDA
    monkeypatch.setenv("LLM_PROVIDER", "openrouter")
    payload = {"id": "provider-17", "model": "synthetic-model", "choices": [
        {"message": {"content": content}, "finish_reason": "length"}]}
    monkeypatch.setattr("app.gemini.client.urlopen", lambda *a, **kw: FakeResponse(payload))
    response = generate_chat_response(GeminiChatRequest(message="Prazo?"))
    assert response.evidence_status == "insufficient"
    assert response.claims == []
    assert response.text == AVISO_RESPOSTA_INTERROMPIDA
