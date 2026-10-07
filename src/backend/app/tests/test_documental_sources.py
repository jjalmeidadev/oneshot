"""Regressao D-04 (#280): fontes reais consultadas, inclusive fallback local."""
import json
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from app.database.tracing import TraceabilityError, trace_interaction
from app.gemini.schemas import GeminiChatRequest, GeminiChatResponse, GeminiUsage
from app.main import app
from app.rag.proactive_confirmation import clear_pending_suggestions, register_pending_suggestion
from app.rag.proactivity import SecondaryIntent
from test_response_references import evidence, provider_response
from test_traceability import FakeConnection, FakeCursor, _connect, _intent, _response_with_db_source


@pytest.fixture(autouse=True)
def synthetic_database(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://synthetic:synthetic@example.test/test")


def _source_calls(cursor):
    return [params for query, params in cursor.calls
            if "INSERT INTO public.consulted_sources" in query]


def _source_event(cursor):
    return json.loads(next(params[-2] for query, params in cursor.calls
                          if "INSERT INTO public.audit_events" in query
                          and params[1] == "database_rag_sources_retrieved"))


@pytest.mark.parametrize("fallbacks", [(True,), (False, True), (True, False), (True, True)])
def test_all_consulted_sources_are_persisted_in_order(monkeypatch, fallbacks):
    response = _response_with_db_source()
    response.trace_sources = [
        {**response.trace_sources[0],
         "artifact_id": None if fallback else "artifact-1",
         "extract_id": None if fallback else "extract-1",
         "project_id": None if fallback else "project-1",
         "citation_order": order,
         "source_locator": f"lista/item-{order}",
         "metadata": {"fallback": fallback, "source_id": f"fonte-{order}"}}
        for order, fallback in enumerate(fallbacks, 1)
    ]
    cursor = FakeCursor([("intent-1",), ("conversation-1",), ("interaction-1",)])
    connection = FakeConnection(cursor)
    trace_interaction(request=GeminiChatRequest(message="Consultar documentos"),
                      response=response, intent=_intent(), entities=[], processing_ms=1,
                      connect=_connect(connection))
    calls = _source_calls(cursor)
    assert len(calls) == len(fallbacks)
    assert [params[9] for params in calls] == list(range(1, len(fallbacks) + 1))
    for order, (params, fallback) in enumerate(zip(calls, fallbacks), 1):
        assert params[0] == "interaction-1"
        assert params[7] == f"lista/item-{order}"
        assert params[1:4] == ((None, None, None) if fallback else
                               ("artifact-1", "extract-1", "project-1"))
        assert json.loads(params[-1])["source_id"] == f"fonte-{order}"
        assert json.loads(params[-1])["fallback"] is fallback
    assert _source_event(cursor)["persistent_source_count"] == len(calls)
    assert connection.committed and connection.closed


def test_failure_writing_a_source_rolls_back_entire_interaction():
    class FailingCursor(FakeCursor):
        def execute(self, query, params=()):
            super().execute(query, params)
            if "INSERT INTO public.consulted_sources" in query:
                raise RuntimeError("falha simulada de escrita")

    response = _response_with_db_source()
    response.trace_sources[0]["metadata"]["fallback"] = True
    cursor = FailingCursor([("intent-1",), ("conversation-1",), ("interaction-1",)])
    connection = FakeConnection(cursor)
    with pytest.raises(TraceabilityError, match="Nao foi possivel registrar"):
        trace_interaction(request=GeminiChatRequest(message="Consultar documento"),
                          response=response, intent=_intent(), entities=[], processing_ms=1,
                          connect=_connect(connection))
    assert connection.rolled_back and connection.closed
    assert not connection.committed


@pytest.mark.parametrize("response", [None, GeminiChatResponse(
    text="Sem fontes suficientes.", model="rag-retriever", latency_ms=0,
    usage=GeminiUsage(), evidence_status="insufficient")])
def test_absence_or_error_does_not_invent_a_source(response):
    cursor = FakeCursor([("intent-1",), ("conversation-1",), ("interaction-1",)])
    connection = FakeConnection(cursor)
    trace_interaction(request=GeminiChatRequest(message="Documento inexistente"),
                      response=response, intent=_intent(), entities=[], processing_ms=1,
                      error_message="falha simulada" if response is None else None,
                      connect=_connect(connection))
    assert _source_calls(cursor) == []
    assert connection.committed


@pytest.mark.parametrize("routing", ["disabled", "low-confidence"])
def test_generic_rag_records_local_sources(monkeypatch, evidence, routing):
    local = replace(evidence, document=replace(evidence.document, fallback=True,
                    artifact_id=None, extract_id=None, project_id=None))
    monkeypatch.setattr("app.gemini.client.retrieve_context", lambda *a, **kw: [local])
    provider_response(monkeypatch, "gemini", "O prazo e 30/09/2026. [Fonte 1]")
    if routing == "low-confidence":
        from test_pipeline_api import _classification_result
        classification = _classification_result()
        classification.macrointencao = "INDEFINIDA"
        classification.intencao = None
        classification.confianca_macro = 0.1
        classification.roteada = False
        monkeypatch.setattr("app.nlp.inference.classify", lambda _: classification)
    cursor = FakeCursor([("conversation-1",), ("interaction-1",)])
    connection = FakeConnection(cursor)
    monkeypatch.setattr("app.pipeline.trace_interaction", lambda **kw:
                        trace_interaction(**kw, connect=_connect(connection)))
    with TestClient(app) as client:
        result = client.post("/api/chat", json={"message": "Qual o prazo?",
                             "use_intent_classifier": routing != "disabled"})
    assert result.status_code == 200, result.text
    assert result.json()["evidence_status"] == "referenced"
    assert len(_source_calls(cursor)) == 1
    assert result.json()["trace_id"] == _source_calls(cursor)[0][0]
    assert _source_event(cursor)["persistent_source_count"] == 1


@pytest.mark.parametrize("decision", ["accept", "decline"])
def test_proactive_confirmation_persists_only_accepted_documental_response(monkeypatch, evidence, decision):
    local = replace(evidence, document=replace(evidence.document, fallback=True,
                    artifact_id=None, extract_id=None, project_id=None))
    secondary = SecondaryIntent("sugerir_agilizacao_projeto", "Analisar prazo", "Analisar", "Analisar prazo")
    monkeypatch.setattr("app.rag.proactive_confirmation._database_is_configured", lambda: False)
    clear_pending_suggestions()
    try:
        suggestion_id = register_pending_suggestion(
            requester_id="legacy-test-user", conversation_id="issue-280-proactive",
            original_message="Qual o prazo?", secondary_intent=secondary, sources=[local],
            prepared_response="O prazo e 30/09/2026. [Fonte 1]", prepared_model="synthetic")
        cursor = FakeCursor([("intent-1",), None, ("conversation-1",), ("interaction-1",)])
        connection = FakeConnection(cursor)
        monkeypatch.setattr("app.pipeline.trace_interaction", lambda **kw:
                            trace_interaction(**kw, connect=_connect(connection)))
        with TestClient(app) as client:
            result = client.post("/api/chat/proactive-confirmation", headers={"Authorization": "Bearer token-de-teste"},
                                 json={"suggestion_id": suggestion_id,
                                       "conversation_id": "issue-280-proactive", "decision": decision})
        assert result.status_code == 200, result.text
        assert result.json()["status"] == ("accepted" if decision == "accept" else "declined")
        if decision == "accept":
            assert result.json()["result"]["evidence_status"] == "referenced"
            assert len(_source_calls(cursor)) == 1
            assert _source_calls(cursor)[0][1:4] == (None, None, None)
            assert _source_event(cursor)["persistent_source_count"] == 1
            assert connection.committed
        else:
            assert result.json()["result"] is None
            assert cursor.calls == []
    finally:
        clear_pending_suggestions()
