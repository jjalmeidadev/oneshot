import json

import pytest

from app.gemini.client import confirm_proactive_suggestion, generate_chat_response
from app.gemini.schemas import GeminiChatRequest, ProactiveConfirmationRequest
from app.nlp.schemas import AudioIntent
from app.rag.proactive_confirmation import (
    PendingSuggestionNotFound,
    claim_pending_suggestion,
    clear_pending_suggestions,
    register_pending_suggestion,
)
from app.rag.proactivity import resolve_secondary_intent
from app.rag.sharepoint import RetrievedDocument, SharePointDocument
from test_gemini_client import FakeResponse


@pytest.fixture(autouse=True)
def isolate_pending_suggestions():
    clear_pending_suggestions()
    yield
    clear_pending_suggestions()


class FakeCursor:
    def __init__(self, row=None) -> None:
        self.row = row
        self.query = ""
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query: str, params: tuple[object, ...]) -> None:
        self.query = query
        self.params = params

    def fetchone(self):
        return self.row


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self.cursor_instance = cursor
        self.closed = False

    def cursor(self) -> FakeCursor:
        return self.cursor_instance

    def close(self) -> None:
        self.closed = True


def _intent(
    specific: str = "consulta_status_projeto",
    macro: str = "CONSULTA",
) -> AudioIntent:
    return AudioIntent(
        macro=macro,
        specific=specific,
        confidence_macro=0.9,
        confidence_specific=0.8,
    )


def _retrieved_document() -> RetrievedDocument:
    return RetrievedDocument(
        document=SharePointDocument(
            source_id="fonte:1",
            title="Status do projeto",
            list_name="Projetos",
            content="O fornecedor do equipamento critico registra atraso de 18 dias.",
            web_url="https://example.test/projeto",
            last_modified="2026-09-18",
            search_text="status projeto fornecedor atraso",
            attributes=(("Acao recomendada", "Acompanhar o plano do fornecedor"),),
        ),
        score=4.0,
    )


def test_local_catalog_maps_primary_to_secondary_without_reclassification(
    monkeypatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_DATABASE_URL", raising=False)

    secondary = resolve_secondary_intent(_intent())

    assert secondary is not None
    assert secondary.name == "sugerir_agilizacao_projeto"
    assert "gargalo" in secondary.rag_instruction


def test_non_consultation_intent_has_no_secondary_suggestion(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_DATABASE_URL", raising=False)

    assert resolve_secondary_intent(
        _intent("transacao_atualizar_cronograma", macro="TRANSACAO")
    ) is None


def test_database_lookup_uses_specific_intent_and_closes_connection(
    monkeypatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@example/postgres")
    cursor = FakeCursor(
        row=(
            "sugerir_recuperacao_prazo",
            "Recuperar o prazo.",
            "Sugira uma acao documentada.",
            "Quer analisar a recuperacao?",
        )
    )
    connection = FakeConnection(cursor)

    secondary = resolve_secondary_intent(
        _intent("consulta_cronograma_prazo"),
        connect=lambda *_args, **_kwargs: connection,
    )

    assert secondary is not None
    assert secondary.name == "sugerir_recuperacao_prazo"
    assert cursor.params == ("consulta_cronograma_prazo",)
    assert "secondary_intents" in cursor.query
    assert connection.closed is True


def test_database_store_recovers_suggestion_for_another_worker(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_DATABASE_URL", raising=False)
    secondary = resolve_secondary_intent(_intent(), catalog_path=None)
    assert secondary is not None
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@example/postgres")
    register_cursor = FakeCursor()
    register_connection = FakeConnection(register_cursor)
    claim_cursor = FakeCursor()
    claim_connection = FakeConnection(claim_cursor)
    connections = iter((register_connection, claim_connection))
    monkeypatch.setattr(
        "app.rag.proactive_confirmation.open_database_connection",
        lambda: next(connections),
    )

    suggestion_id = register_pending_suggestion(
        requester_id="entra-user-250",
        conversation_id="conversation-250",
        original_message="status",
        secondary_intent=secondary,
        sources=[_retrieved_document()],
    )
    claim_cursor.row = (
        suggestion_id,
        "entra-user-250",
        "conversation-250",
        "status",
        {
            "name": secondary.name,
            "description": secondary.description,
            "rag_instruction": secondary.rag_instruction,
            "display_message": secondary.display_message,
        },
        [
            {
                "document": {
                    "source_id": "fonte:1",
                    "title": "Status do projeto",
                    "list_name": "Projetos",
                    "content": "O fornecedor do equipamento critico registra atraso de 18 dias.",
                    "web_url": "https://example.test/projeto",
                    "last_modified": "2026-09-18",
                    "search_text": "status projeto fornecedor atraso",
                    "artifact_id": None,
                    "extract_id": None,
                    "project_id": None,
                    "source_locator": None,
                    "fallback": True,
                },
                "score": 4.0,
            }
        ],
        "Resposta secundaria preparada [Fonte 1].",
        "gemini-3.7-flash",
        "interaction-proactive",
    )

    claimed = claim_pending_suggestion(
        suggestion_id,
        requester_id="entra-user-250",
        conversation_id="conversation-250",
    )

    assert "pending_proactive_suggestions" in register_cursor.query
    assert claimed.suggestion_id == suggestion_id
    assert claimed.sources[0].document.source_id == "fonte:1"
    assert claimed.prepared_response.startswith("Resposta secundaria")


def test_proactivity_prepares_secondary_response_in_single_provider_call(
    monkeypatch,
) -> None:
    captured_requests = []

    def fake_urlopen(request, timeout: int) -> FakeResponse:
        captured_requests.append(request)
        assert timeout == 30
        text = json.dumps(
            {
                "primary_response": "O fornecedor do equipamento critico registra atraso de 18 dias. [Fonte 1]",
                "prepared_secondary_response": (
                    "Acao recomendada: Acompanhar o plano do fornecedor [Fonte 1]"
                ),
            }
        )
        return FakeResponse(
            {
                "id": "interaction-proactive",
                "model": "gemini-3.7-flash",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [
                            {
                                "type": "text",
                                "text": text,
                            }
                        ],
                    }
                ],
                "usage": {},
            }
        )

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_DATABASE_URL", raising=False)
    monkeypatch.setattr(
        "app.gemini.client.retrieve_context",
        lambda *_args, **_kwargs: [_retrieved_document()],
    )
    monkeypatch.setattr("app.gemini.client.urlopen", fake_urlopen)

    response = generate_chat_response(
        GeminiChatRequest(
            message="Qual e o status do projeto?",
            conversation_id="conversation-250",
            proactivity_enabled=True,
        ),
        intent=_intent(),
        requester_id="user-250",
    )

    primary_payload = json.loads(captured_requests[0].data.decode("utf-8"))
    assert "macro=CONSULTA; especifica=consulta_status_projeto" in primary_payload["input"]
    assert "Intencao secundaria: sugerir_agilizacao_projeto" in primary_payload["input"]
    assert "principal gargalo" in primary_payload["input"]
    assert response.text == "O fornecedor do equipamento critico registra atraso de 18 dias. [Fonte 1]"
    assert response.proactive_suggestion is not None
    assert response.proactive_suggestion.intent == "sugerir_agilizacao_projeto"
    assert response.proactive_suggestion.requires_confirmation is True

    with pytest.raises(PendingSuggestionNotFound):
        confirm_proactive_suggestion(
            ProactiveConfirmationRequest(
                suggestion_id=response.proactive_suggestion.suggestion_id,
                conversation_id="conversation-250",
                decision="accept",
            ),
            requester_id="outro-usuario",
        )
    with pytest.raises(PendingSuggestionNotFound):
        confirm_proactive_suggestion(
            ProactiveConfirmationRequest(
                suggestion_id=response.proactive_suggestion.suggestion_id,
                conversation_id="outra-conversa",
                decision="accept",
            ),
            requester_id="user-250",
        )

    confirmation = confirm_proactive_suggestion(
        ProactiveConfirmationRequest(
            suggestion_id=response.proactive_suggestion.suggestion_id,
            conversation_id="conversation-250",
            decision="accept",
        ),
        requester_id="user-250",
    )

    assert confirmation.status == "accepted"
    assert confirmation.result is not None
    assert confirmation.result.text == "Acao recomendada: Acompanhar o plano do fornecedor [Fonte 1]"
    assert confirmation.result.claims[0].evidence[0].attribute == "Acao recomendada"
    assert confirmation.result.usage.total_tokens == 0
    assert confirmation.result.latency_ms == 0
    assert len(captured_requests) == 1
    with pytest.raises(PendingSuggestionNotFound):
        confirm_proactive_suggestion(
            ProactiveConfirmationRequest(
                suggestion_id=response.proactive_suggestion.suggestion_id,
                conversation_id="conversation-250",
                decision="accept",
            ),
            requester_id="user-250",
        )


def test_declining_suggestion_does_not_call_provider_again(monkeypatch) -> None:
    calls = []

    def fake_urlopen(request, timeout: int) -> FakeResponse:
        calls.append(request)
        return FakeResponse(
            {
                "id": "interaction-primary",
                "model": "gemini-3.7-flash",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(
                                    {
                                        "primary_response": "O fornecedor do equipamento critico registra atraso de 18 dias. [Fonte 1]",
                                        "prepared_secondary_response": (
                                            "Acao recomendada: Acompanhar o plano do fornecedor [Fonte 1]"
                                        ),
                                    }
                                ),
                            }
                        ],
                    }
                ],
                "usage": {},
            }
        )

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_DATABASE_URL", raising=False)
    monkeypatch.setattr(
        "app.gemini.client.retrieve_context",
        lambda *_args, **_kwargs: [_retrieved_document()],
    )
    monkeypatch.setattr("app.gemini.client.urlopen", fake_urlopen)
    response = generate_chat_response(
        GeminiChatRequest(
            message="status",
            conversation_id="conversation-250",
            proactivity_enabled=True,
        ),
        intent=_intent(),
        requester_id="user-250",
    )

    confirmation = confirm_proactive_suggestion(
        ProactiveConfirmationRequest(
            suggestion_id=response.proactive_suggestion.suggestion_id,
            conversation_id="conversation-250",
            decision="decline",
        ),
        requester_id="user-250",
    )

    assert confirmation.status == "declined"
    assert confirmation.result is None
    assert len(calls) == 1


def test_disabled_proactivity_preserves_primary_rag_prompt(monkeypatch) -> None:
    captured_request = None

    def fake_urlopen(request, timeout: int) -> FakeResponse:
        nonlocal captured_request
        captured_request = request
        assert timeout == 30
        return FakeResponse(
            {
                "id": "interaction-primary-only",
                "model": "gemini-3.7-flash",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [{"type": "text", "text": "Resposta principal."}],
                    }
                ],
                "usage": {},
            }
        )

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(
        "app.gemini.client.retrieve_context",
        lambda *_args, **_kwargs: [_retrieved_document()],
    )
    monkeypatch.setattr("app.gemini.client.urlopen", fake_urlopen)

    response = generate_chat_response(
        GeminiChatRequest(message="Qual e o status do projeto?"),
        intent=_intent(),
    )

    payload = json.loads(captured_request.data.decode("utf-8"))
    assert "macro=CONSULTA; especifica=consulta_status_projeto" in payload["input"]
    assert "Intencao secundaria:" not in payload["input"]
    assert response.proactive_suggestion is None
