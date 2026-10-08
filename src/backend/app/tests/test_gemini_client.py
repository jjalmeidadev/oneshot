import json
from io import BytesIO
from urllib.error import HTTPError, URLError

import pytest

# Preserva a cobertura anterior do backend-api na selecao por marcador (#255).
pytestmark = pytest.mark.integration

from app.gemini.client import (
    GeminiAPIError,
    GeminiConfigurationError,
    generate_chat_response,
)
from app.gemini.schemas import GeminiChatRequest

BIKE_EVIDENCE = (
    "Na politica ficticia do MVP, bicicletas sao aceitas aos sabados, domingos e feriados "
    "durante toda a operacao, e nos dias uteis apos as 20h30. O passageiro deve usar o "
    "ultimo carro e respeitar a capacidade indicada pela equipe."
)


class FakeResponse:
    def __init__(self, body: dict) -> None:
        self.body = body

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.body).encode("utf-8")


def test_generate_chat_response_maps_text_context_and_usage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_request = None

    def fake_urlopen(request, timeout: int) -> FakeResponse:
        nonlocal captured_request
        captured_request = request
        assert timeout == 30
        return FakeResponse(
            {
                "id": "interaction-2",
                "model": "gemini-3.7-flash",
                "status": "completed",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [{"type": "text", "text": BIKE_EVIDENCE + " [Fonte 1]"}],
                    }
                ],
                "usage": {
                    "total_input_tokens": 12,
                    "total_output_tokens": 8,
                    "total_thought_tokens": 3,
                    "total_tokens": 23,
                },
            }
        )

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MAX_OUTPUT_TOKENS", "512")
    monkeypatch.setenv("GEMINI_THINKING_LEVEL", "low")
    monkeypatch.setattr("app.gemini.client.urlopen", fake_urlopen)

    response = generate_chat_response(
        GeminiChatRequest(
            message="Posso transportar bicicleta?",
            previous_interaction_id="interaction-1",
        )
    )

    assert response.text == BIKE_EVIDENCE + " [Fonte 1]"
    assert response.evidence_status == "referenced"
    assert response.interaction_id == "interaction-2"
    assert response.usage.total_tokens == 23
    assert response.latency_ms >= 0

    request_body = json.loads(captured_request.data.decode("utf-8"))
    assert "Pergunta do usuario: Posso transportar bicicleta?" in request_body["input"]
    assert request_body["previous_interaction_id"] == "interaction-1"
    assert request_body["generation_config"] == {
        "max_output_tokens": 512,
        "thinking_level": "low",
    }
    assert captured_request.headers["X-goog-api-key"] == "test-key"


def test_generate_chat_response_requires_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(GeminiConfigurationError):
        generate_chat_response(GeminiChatRequest(message="Teste"))


def test_generate_chat_response_injects_retrieved_sharepoint_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_request = None

    def fake_urlopen(request, timeout: int) -> FakeResponse:
        nonlocal captured_request
        captured_request = request
        return FakeResponse(
            {
                "id": "interaction-rag",
                "model": "gemini-3.7-flash",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [{"type": "text", "text": "Use o ultimo carro."}],
                    }
                ],
                "usage": {},
            }
        )

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr("app.gemini.client.urlopen", fake_urlopen)

    response = generate_chat_response(
        GeminiChatRequest(message="Posso transportar bicicleta?")
    )

    request_body = json.loads(captured_request.data.decode("utf-8"))
    assert "[Fonte 1] Transporte de bicicleta" in request_body["input"]
    assert "Pergunta do usuario: Posso transportar bicicleta?" in request_body["input"]
    assert response.sources[0].title == "Transporte de bicicleta"
    assert response.retrieval_ms >= 0


def test_generate_chat_response_retries_with_exponential_backoff(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = 0
    delays: list[float] = []

    def fake_urlopen(_request, timeout: int) -> FakeResponse:
        nonlocal attempts
        attempts += 1
        assert timeout == 30
        if attempts < 4:
            raise URLError("temporarily unavailable")
        return FakeResponse(
            {
                "id": "interaction-retried",
                "model": "gemini-3.7-flash",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [{"type": "text", "text": BIKE_EVIDENCE + " [Fonte 1]"}],
                    }
                ],
                "usage": {},
            }
        )

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr("app.gemini.client.urlopen", fake_urlopen)
    monkeypatch.setattr("app.gemini.client.sleep", delays.append)

    response = generate_chat_response(GeminiChatRequest(message="Posso transportar bicicleta?"))

    assert response.text == BIKE_EVIDENCE + " [Fonte 1]"
    assert attempts == 4
    assert delays == [2.0, 4.0, 8.0]


def test_generate_chat_response_stops_after_configured_retries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = 0
    delays: list[float] = []

    def fake_urlopen(_request, timeout: int) -> FakeResponse:
        nonlocal attempts
        attempts += 1
        raise URLError("temporarily unavailable")

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MAX_RETRIES", "2")
    monkeypatch.setattr("app.gemini.client.urlopen", fake_urlopen)
    monkeypatch.setattr("app.gemini.client.sleep", delays.append)

    with pytest.raises(GeminiAPIError, match="Nao foi possivel conectar ao Gemini"):
        generate_chat_response(GeminiChatRequest(message="bicicleta"))

    assert attempts == 3
    assert delays == [2.0, 4.0]


def test_generate_chat_response_does_not_retry_permanent_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = 0
    delays: list[float] = []

    def fake_urlopen(_request, timeout: int) -> FakeResponse:
        nonlocal attempts
        attempts += 1
        raise HTTPError(
            url="https://example.test",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=BytesIO(b'{"error":{"message":"Invalid request"}}'),
        )

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr("app.gemini.client.urlopen", fake_urlopen)
    monkeypatch.setattr("app.gemini.client.sleep", delays.append)

    with pytest.raises(GeminiAPIError, match="Invalid request"):
        generate_chat_response(GeminiChatRequest(message="bicicleta"))

    assert attempts == 1
    assert delays == []
