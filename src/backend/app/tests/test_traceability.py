from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.audio import transcription
from app.database.tracing import TraceabilityError, trace_interaction
from app.gemini.client import GeminiAPIError
from app.gemini.schemas import GeminiChatRequest, GeminiChatResponse, GeminiUsage
from app.main import app
from app.nlp.inference import get_classifier
from app.nlp.schemas import AudioIntent, IntentAlternative, PublicEntity
from test_audio_upload import AUTH_HEADER, _build_wav, transcricao_fixa


class FakeCursor:
    def __init__(self, fetch_values: list[tuple[str] | None] | None = None) -> None:
        self.fetch_values = fetch_values or []
        self.calls: list[tuple[str, tuple]] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query: str, params: tuple = ()) -> None:
        self.calls.append((query, params))

    def fetchone(self):
        return self.fetch_values.pop(0) if self.fetch_values else None


class FakeConnection:
    def __init__(self, cursor: FakeCursor, fail_commit: bool = False) -> None:
        self.cursor_instance = cursor
        self.fail_commit = fail_commit
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self) -> FakeCursor:
        return self.cursor_instance

    def commit(self) -> None:
        if self.fail_commit:
            raise RuntimeError("database password secret stack trace")
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


def _connect(connection: FakeConnection):
    def connect(_database_url: str, **_kwargs):
        return connection

    return connect


def _intent(
    macro: str = "CONSULTA",
    specific: str = "consulta_status_projeto",
    confidence_macro: float = 0.9,
) -> AudioIntent:
    return AudioIntent(
        macro=macro,
        specific=specific,
        confidence_macro=confidence_macro,
        confidence_specific=0.8,
        handler=f"handler:{specific}" if specific else "limitacao",
        alternatives=[
            IntentAlternative(
                intent=specific or "fora_de_escopo",
                confidence=0.8,
            )
        ],
    )


def _entity() -> PublicEntity:
    return PublicEntity(
        type="projeto",
        value="Linha 1-Azul",
        text="Linha 1-Azul",
        start=0,
        end=12,
        types=["projeto"],
    )


def _response_with_db_source() -> GeminiChatResponse:
    return GeminiChatResponse(
        text="Resposta fundamentada [Fonte 1]",
        model="teste",
        latency_ms=4,
        retrieval_ms=2,
        usage=GeminiUsage(),
        sources=[
            {
                "id": "sharepoint-mock:comunicados-servico:201",
                "title": "Operacao assistida na Linha Azul",
                "list_name": "Comunicados de Servico / PRJ-0442",
                "web_url": "https://mock/sharepoint/201",
                "last_modified": "2026-08-01T12:00:00Z",
                "score": 0.8,
                "excerpt": "Intervalo entre trens podera ser ampliado.",
            }
        ],
        trace_sources=[
            {
                "artifact_id": "artifact-1",
                "extract_id": "extract-1",
                "project_id": "project-1",
                "source_type": "lista_sharepoint",
                "source_title": "Operacao assistida na Linha Azul",
                "source_url": "https://mock/sharepoint/201",
                "source_locator": "comunicados-servico/201#Conteudo",
                "relevance_score": 0.8,
                "citation_order": 1,
                "metadata": {"fallback": False, "source_id": "source"},
            }
        ],
    )


#: Marcado pela #228 (S4-32B): este arquivo cruza fronteira entre
#: componentes (API, modelo, banco ou servico externo). Rodar so estes com
#: `pytest -m integration`.
pytestmark = pytest.mark.integration


def test_trace_uses_resolved_public_user_id_without_second_lookup(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test.invalid/postgres")
    public_user_id = "6e7d0df0-c96a-4076-b241-64f78a05997a"
    cursor = FakeCursor(fetch_values=[("conversation-1",), ("interaction-1",)])
    connection = FakeConnection(cursor)

    trace_interaction(
        request=GeminiChatRequest(
            message="status", use_intent_classifier=False
        ),
        response=_response_with_db_source(),
        intent=None,
        entities=[],
        processing_ms=5,
        requester_id="762a2bde-87b8-413f-8656-958a2f380574",
        user_id=public_user_id,
        connect=_connect(connection),
    )

    assert not any("FROM public.users" in query for query, _ in cursor.calls)
    conversation_params = next(
        params
        for query, params in cursor.calls
        if "INSERT INTO public.ai_conversations" in query
    )
    interaction_params = next(
        params
        for query, params in cursor.calls
        if "INSERT INTO public.ai_interactions" in query
    )
    audit_params = [
        params
        for query, params in cursor.calls
        if "INSERT INTO public.audit_events" in query
    ]
    assert conversation_params[0] == public_user_id
    assert interaction_params[-1] == public_user_id
    assert audit_params
    assert all(public_user_id in params for params in audit_params)


def test_chat_real_classifier_contract_and_minimal_persistence(monkeypatch):
    monkeypatch.setenv("PLN_WARMUP", "0")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@example/postgres")
    cursor = FakeCursor(
        fetch_values=[
            ("intent-1",),
            ("conversation-1",),
            ("interaction-1",),
        ]
    )
    connection = FakeConnection(cursor)
    provider_calls = []

    def fake_provider(request, intent=None, entities=None, **_kwargs):
        provider_calls.append((request, intent, entities))
        return _response_with_db_source()

    monkeypatch.setattr("app.pipeline.generate_chat_response", fake_provider)
    monkeypatch.setattr(
        "app.database.tracing.open_database_connection",
        lambda **_kwargs: connection,
    )

    with TestClient(app) as client:
        result = client.post(
            "/api/chat",
            json={
                "message": "qual é o status da extensão da Linha 5-Lilás?",
                "use_intent_classifier": True,
            },
        )

    assert result.status_code == 200
    data = result.json()
    intent = data["intent"]
    artifact = get_classifier().artefato
    assert artifact.limiar_macro == pytest.approx(0.525)
    assert artifact.limiar_intencao == pytest.approx(0.350)
    assert intent["macro"] == "CONSULTA"
    assert intent["specific"] == "consulta_status_projeto"
    assert intent["confidence_macro"] >= artifact.limiar_macro
    assert intent["confidence_specific"] >= artifact.limiar_intencao
    assert intent["flow"] == "RecuperadorInformacao -> Estruturador de Resposta"
    assert intent["handler"] == "handler:consulta_status_projeto"
    assert data["pipeline_metrics"]["nlp_ms"] >= 0
    assert data["pipeline_metrics"]["route_ms"] >= 0
    assert provider_calls[0][1].specific == "consulta_status_projeto"

    interaction_call = next(
        params
        for query, params in cursor.calls
        if "INSERT INTO public.ai_interactions" in query
    )
    assert interaction_call[4] == intent["macro"]
    assert interaction_call[5] == intent["confidence_macro"]
    assert interaction_call[6] == intent["specific"]
    assert interaction_call[7] == intent["confidence_specific"]
    assert interaction_call[8] == intent["handler"]
    assert interaction_call[9] == "sharepoint_query"
    assert connection.committed is True
    assert any(
        params[1:4] == ("pln_intent_classified", "pln", "sucesso")
        for query, params in cursor.calls
        if "INSERT INTO public.audit_events" in query
    )


def test_audio_real_classifier_contract_and_minimal_persistence(monkeypatch):
    transcript = "qual é o status da extensão da Linha 5-Lilás?"
    external_conversation_id = "s4-13-audio-success"
    monkeypatch.setenv("PLN_WARMUP", "0")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@example/postgres")
    cursor = FakeCursor(
        fetch_values=[
            ("intent-1",),
            None,
            ("conversation-1",),
            ("interaction-1",),
        ]
    )
    connection = FakeConnection(cursor)
    provider_calls = []

    def fake_provider(request, intent=None, entities=None, **_kwargs):
        provider_calls.append((request, intent, entities))
        return _response_with_db_source()

    monkeypatch.setattr(
        transcription,
        "transcribe",
        transcricao_fixa(text=transcript, confidence=.97, duration_seconds=1),
    )
    monkeypatch.setattr("app.pipeline.generate_chat_response", fake_provider)
    monkeypatch.setattr(
        "app.database.tracing.open_database_connection",
        lambda **_kwargs: connection,
    )

    with TestClient(app) as client:
        result = client.post(
            "/api/audio",
            files={"audio": ("teste.wav", _build_wav(), "audio/wav")},
            headers=AUTH_HEADER,
            data={
                "conversation_id": external_conversation_id,
                "use_intent_classifier": "true",
            },
        )

    assert result.status_code == 200
    data = result.json()
    intent = data["intent"]
    assert data["transcription"]["text"] == transcript
    assert intent["macro"] == "CONSULTA"
    assert intent["specific"] == "consulta_status_projeto"
    assert provider_calls[0][0].message == transcript
    assert provider_calls[0][1].specific == "consulta_status_projeto"
    conversation_call = next(
        params
        for query, params in cursor.calls
        if "INSERT INTO public.ai_conversations" in query
    )
    assert conversation_call[1] == "api"
    assert conversation_call[2] == external_conversation_id

    interaction_call = next(
        params
        for query, params in cursor.calls
        if "INSERT INTO public.ai_interactions" in query
    )
    assert interaction_call[4] == intent["macro"]
    assert interaction_call[6] == intent["specific"]
    assert interaction_call[8] == intent["handler"]
    assert connection.committed is True
    assert any(
        params[1:4] == ("pln_intent_classified", "pln", "sucesso")
        for query, params in cursor.calls
        if "INSERT INTO public.audit_events" in query
    )


def test_audio_classifier_failure_is_persisted_and_correlated(monkeypatch):
    external_conversation_id = "s4-13-audio-classifier-failure"
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@example/postgres")
    cursor = FakeCursor(
        fetch_values=[
            None,
            ("conversation-1",),
            ("interaction-1",),
        ]
    )
    connection = FakeConnection(cursor)

    def fail_classifier(_text):
        raise RuntimeError("private-model-path")

    monkeypatch.setattr(
        transcription,
        "transcribe",
        transcricao_fixa(text="prazo", confidence=.97, duration_seconds=1),
    )
    monkeypatch.setattr("app.nlp.inference.classify", fail_classifier)
    monkeypatch.setattr(
        "app.pipeline.generate_chat_response",
        lambda *_args, **_kwargs: pytest.fail("Provedor nao deveria ser chamado"),
    )
    monkeypatch.setattr(
        "app.database.tracing.open_database_connection",
        lambda **_kwargs: connection,
    )

    with TestClient(app) as client:
        result = client.post(
            "/api/audio",
            files={"audio": ("teste.wav", _build_wav(), "audio/wav")},
            headers=AUTH_HEADER,
            data={
                "conversation_id": external_conversation_id,
                "use_intent_classifier": "true",
            },
        )

    assert result.status_code == 503
    assert result.json()["error"]["code"] == "PROCESSING_UNAVAILABLE"
    conversation_call = next(
        params
        for query, params in cursor.calls
        if "INSERT INTO public.ai_conversations" in query
    )
    assert conversation_call[2] == external_conversation_id
    interaction_call = next(
        params
        for query, params in cursor.calls
        if "INSERT INTO public.ai_interactions" in query
    )
    assert interaction_call[2] == "prazo"
    assert interaction_call[13] == "erro"
    assert connection.committed is True
    assert any(
        params[1:4] == ("pipeline_controlled_failure", "api", "falha")
        for query, params in cursor.calls
        if "INSERT INTO public.audit_events" in query
    )


def test_trace_interaction_records_interaction_and_consulted_sources(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@example/postgres")
    cursor = FakeCursor(
        fetch_values=[
            ("intent-1",),
            ("conversation-1",),
            ("interaction-1",),
        ]
    )
    connection = FakeConnection(cursor)

    interaction_id = trace_interaction(
        request=GeminiChatRequest(message="status da Linha 1-Azul"),
        response=_response_with_db_source(),
        intent=_intent(),
        entities=[_entity()],
        processing_ms=12,
        connect=_connect(connection),
    )

    assert interaction_id == "interaction-1"
    assert connection.committed is True
    assert any("INSERT INTO public.ai_interactions" in query for query, _ in cursor.calls)
    source_call = next(
        params
        for query, params in cursor.calls
        if "INSERT INTO public.consulted_sources" in query
    )
    assert source_call[1:4] == ("artifact-1", "extract-1", "project-1")
    assert source_call[4] == "lista_sharepoint"


def test_trace_interaction_records_rf08_absence_as_limitation(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@example/postgres")
    cursor = FakeCursor(fetch_values=[("intent-1",), ("conversation-1",), ("interaction-1",)])
    connection = FakeConnection(cursor)
    response = GeminiChatResponse(
        text="Nao encontrei fontes suficientes para responder com seguranca.",
        model="rag-retriever",
        latency_ms=0,
        usage=GeminiUsage(),
        sources=[],
    )

    trace_interaction(
        request=GeminiChatRequest(message="prazo do projeto inexistente"),
        response=response,
        intent=_intent("CONSULTA", "consulta_cronograma_prazo"),
        entities=[],
        processing_ms=3,
        connect=_connect(connection),
    )

    interaction_call = next(
        params
        for query, params in cursor.calls
        if "INSERT INTO public.ai_interactions" in query
    )
    assert interaction_call[12] == response.text
    assert interaction_call[13] == "processado"
    out_of_scope_call = next(
        params
        for query, params in cursor.calls
        if "INSERT INTO public.out_of_scope_requests" in query
    )
    assert out_of_scope_call[0] == "interaction-1"
    assert out_of_scope_call[1] == "prazo do projeto inexistente"
    assert out_of_scope_call[2:4] == ("CONSULTA", "consulta_cronograma_prazo")
    assert out_of_scope_call[5] == "sem_contexto_rag"


@pytest.mark.parametrize(
    "intent,expected_macro,expected_status",
    [
        (_intent("CONSULTA", "consulta_status_projeto"), "CONSULTA", "processado"),
        (_intent("FORA_DE_ESCOPO", ""), "FORA_DE_ESCOPO", "fora_escopo"),
        (_intent("INDEFINIDA", ""), None, "sem_confianca"),
    ],
)
def test_trace_interaction_normalizes_macro_intent_for_database_check(
    monkeypatch,
    intent,
    expected_macro,
    expected_status,
):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@example/postgres")
    fetch_values = [("conversation-1",), ("interaction-1",)]
    if intent.specific:
        fetch_values.insert(0, ("intent-1",))
    cursor = FakeCursor(fetch_values=fetch_values)
    connection = FakeConnection(cursor)

    trace_interaction(
        request=GeminiChatRequest(message="pergunta controlada"),
        response=GeminiChatResponse(
            text="Resposta controlada",
            model="classificador-local",
            latency_ms=0,
            usage=GeminiUsage(),
            sources=[],
        ),
        intent=intent,
        entities=[],
        processing_ms=1,
        connect=_connect(connection),
    )

    interaction_call = next(
        params
        for query, params in cursor.calls
        if "INSERT INTO public.ai_interactions" in query
    )
    assert interaction_call[4] == expected_macro
    assert interaction_call[6] == (intent.specific or None)
    assert interaction_call[13] == expected_status


@pytest.mark.parametrize(
    "classification,status",
    [
        (SimpleNamespace(macrointencao="FORA_DE_ESCOPO", intencao=None, confianca_macro=0.9, confianca_intencao=0.0, fluxo="", handler="limitacao", alternativas=[], roteada=True, resposta_sugerida="Fora do escopo"), "fora_escopo"),
        (SimpleNamespace(macrointencao="INDEFINIDA", intencao=None, confianca_macro=0.3, confianca_intencao=0.0, fluxo="", handler="limitacao", alternativas=[], roteada=False, resposta_sugerida="Reformule"), "sem_confianca"),
    ],
)
def test_low_confidence_uses_generic_rag_and_preserves_classification_trace(
    monkeypatch,
    classification,
    status,
):
    traces = []
    provider_calls = []
    monkeypatch.setattr("app.nlp.inference.classify", lambda _text: classification)
    monkeypatch.setattr(
        "app.pipeline.generate_chat_response",
        lambda *_args, **kwargs: (
            provider_calls.append(kwargs)
            or GeminiChatResponse(
                text="Essa solicitação não está no escopo da base de conhecimento disponível.",
                model="rag-retriever",
                latency_ms=0,
                usage=GeminiUsage(),
                sources=[],
            )
        ),
    )
    monkeypatch.setattr(
        "app.pipeline.trace_interaction",
        lambda **kwargs: traces.append(kwargs),
    )

    with TestClient(app) as client:
        result = client.post("/api/chat", json={"message": "qualquer pergunta"})

    assert result.status_code == 200
    assert traces
    assert provider_calls[0]["intent"] is None
    assert traces[0]["response"].model == "rag-retriever"
    assert traces[0]["intent"].macro == classification.macrointencao


def test_trace_error_does_not_break_chat_response(monkeypatch):
    monkeypatch.setattr(
        "app.nlp.inference.classify",
        lambda _text: SimpleNamespace(
            macrointencao="CONSULTA",
            intencao="consulta_status_projeto",
            confianca_macro=0.9,
            confianca_intencao=0.8,
            fluxo="",
            handler="handler:consulta_status_projeto",
            alternativas=[],
            roteada=True,
            resposta_sugerida=None,
        ),
    )
    monkeypatch.setattr(
        "app.pipeline.generate_chat_response",
        lambda *_args, **_kwargs: GeminiChatResponse(
            text="Resposta preservada",
            model="teste",
            latency_ms=1,
            usage=GeminiUsage(),
        ),
    )
    monkeypatch.setattr(
        "app.pipeline.trace_interaction",
        lambda **_kwargs: (_ for _ in ()).throw(
            TraceabilityError("database password secret stack trace")
        ),
    )

    with TestClient(app) as client:
        result = client.post("/api/chat", json={"message": "status"})

    assert result.status_code == 200
    assert result.json()["text"] == "Resposta preservada"
    assert "secret" not in result.text
    assert "stack trace" not in result.text


def test_controlled_provider_error_is_traced_without_leaking_details(monkeypatch):
    traces = []
    monkeypatch.setattr(
        "app.pipeline.generate_chat_response",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            GeminiAPIError("database password secret stack trace", status_code=503)
        ),
    )
    monkeypatch.setattr(
        "app.pipeline.trace_interaction",
        lambda **kwargs: traces.append(kwargs),
    )

    with TestClient(app) as client:
        result = client.post(
            "/api/chat",
            json={"message": "status", "use_intent_classifier": False},
        )

    assert result.status_code == 503
    assert "secret" not in result.text
    assert "stack trace" not in result.text
    assert traces[0]["error_message"] == "database password secret stack trace"


def test_traceability_error_message_is_sanitized(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret-token@example/postgres")
    cursor = FakeCursor(fetch_values=[("intent-1",), ("conversation-1",), ("interaction-1",)])
    connection = FakeConnection(cursor, fail_commit=True)

    with pytest.raises(TraceabilityError) as error:
        trace_interaction(
            request=GeminiChatRequest(message="status"),
            response=_response_with_db_source(),
            intent=_intent(),
            entities=[],
            processing_ms=1,
            connect=_connect(connection),
        )

    assert str(error.value) == "Nao foi possivel registrar a rastreabilidade."
    assert "secret-token" not in str(error.value)
    assert "stack trace" not in str(error.value)


def test_workflow_directive_is_traced_as_guided_workflow(monkeypatch):
    from app.reports.schemas import WorkflowDirective

    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@example/postgres")
    cursor = FakeCursor(fetch_values=[("intent-1",), ("conversation-1",), ("interaction-1",)])
    connection = FakeConnection(cursor)
    response = GeminiChatResponse(
        text="Iniciar dialogo guiado.",
        model="workflow-router",
        latency_ms=0,
        usage=GeminiUsage(),
        workflow=WorkflowDirective(),
    )

    trace_interaction(
        request=GeminiChatRequest(message="gere um relatorio"),
        response=response,
        intent=_intent("TRANSACAO", "transacao_gerar_relatorio"),
        entities=[],
        processing_ms=1,
        connect=_connect(connection),
    )

    interaction_call = next(
        params
        for query, params in cursor.calls
        if "INSERT INTO public.ai_interactions" in query
    )
    assert interaction_call[9] == "guided_workflow"
    assert any(
        params[1:4]
        == ("guided_workflow_dispatched", "guided_workflow", "pendente")
        for query, params in cursor.calls
        if "INSERT INTO public.audit_events" in query
    )
