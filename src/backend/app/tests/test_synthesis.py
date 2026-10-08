"""Contrato de TTS e preservação da resposta textual quando o provedor falha."""

import base64

import httpx
from fastapi.testclient import TestClient

from app.audio import synthesis
from app.gemini.schemas import GeminiChatResponse, GeminiUsage, SpeechResponse
from app.main import app
from app.audio import transcription
from test_audio_upload import _build_wav, AUTH_HEADER, transcricao_fixa


def _answer() -> GeminiChatResponse:
    return GeminiChatResponse(
        text="A & B < 3", model="teste", latency_ms=2,
        usage=GeminiUsage(), interaction_id="interaction-tts",
    )


def test_tts_request_escapes_ssml_and_returns_mp3(monkeypatch):
    sent = {}

    class Client:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def post(self, url, *, content, headers, timeout):
            sent.update(url=url, content=content, headers=headers, timeout=timeout)
            return httpx.Response(200, content=b"ID3audio", headers={"content-type": "audio/mpeg"})

    monkeypatch.setenv("AZURE_SPEECH_KEY", "test-key")
    monkeypatch.setenv("AZURE_SPEECH_REGION", "brazilsouth")
    monkeypatch.setattr(synthesis.httpx, "Client", Client)
    result = synthesis.synthesize_optional("A & B < 3")

    assert result.status == "available"
    assert base64.b64decode(result.data_base64) == b"ID3audio"
    assert sent["url"] == "https://brazilsouth.tts.speech.microsoft.com/cognitiveservices/v1"
    assert b"A &amp; B &lt; 3" in sent["content"]
    assert sent["headers"]["X-Microsoft-OutputFormat"] == synthesis.OUTPUT_FORMAT
    assert sent["headers"]["Ocp-Apim-Subscription-Key"] == "test-key"


def test_tts_timeout_and_provider_failures_keep_text(monkeypatch):
    monkeypatch.setenv("AZURE_SPEECH_KEY", "test-key")
    monkeypatch.setenv("AZURE_SPEECH_REGION", "brazilsouth")

    class Client:
        def __init__(self, response=None, error=None):
            self.response, self.error = response, error
            self.calls = 0

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def post(self, *_args, **_kwargs):
            self.calls += 1
            if self.error:
                raise self.error
            return self.response

    for response, error, attempts in [
        (None, httpx.ReadTimeout("timeout"), 2),
        (httpx.Response(503), None, 2),
        (httpx.Response(429), None, 1),
        (httpx.Response(401), None, 1),
        (httpx.Response(200, content=b""), None, 1),
    ]:
        client = Client(response, error)
        monkeypatch.setattr(synthesis.httpx, "Client", lambda: client)
        result = synthesis.synthesize_optional("Resposta")
        assert result.status == "unavailable"
        assert result.data_base64 is None
        assert result.warning == synthesis.WARNING
        assert client.calls == attempts


def test_tts_rejects_long_text_without_provider_call(monkeypatch):
    monkeypatch.setenv("AZURE_SPEECH_KEY", "test-key")
    monkeypatch.setenv("AZURE_SPEECH_REGION", "brazilsouth")
    monkeypatch.setattr(synthesis.httpx, "Client", lambda: (_ for _ in ()).throw(AssertionError("provider called")))
    result = synthesis.synthesize_optional("x" * (synthesis.MAX_TEXT_CHARS + 1))
    assert result.status == "unavailable"
    assert result.warning == synthesis.WARNING


def test_chat_audio_is_optional_and_failure_preserves_canonical_text(monkeypatch):
    monkeypatch.setattr("app.main.process_message", lambda *_args, **_kwargs: _answer())
    calls = []

    def fake_synthesis(text):
        calls.append(text)
        return synthesis.synthesize_optional(text)

    monkeypatch.delenv("AZURE_SPEECH_KEY", raising=False)
    monkeypatch.setattr("app.main.synthesize_optional", fake_synthesis)
    with TestClient(app) as client:
        plain = client.post("/api/chat", json={"message": "pergunta"})
        audio = client.post("/api/chat", json={"message": "pergunta", "include_audio": True})
    assert plain.status_code == audio.status_code == 200
    assert plain.json()["speech"] is None
    assert calls == ["A & B < 3"]
    assert audio.json()["text"] == plain.json()["text"]
    assert audio.json()["interaction_id"] == plain.json()["interaction_id"]
    assert audio.json()["speech"]["status"] == "unavailable"


def test_chat_and_uploaded_audio_deliver_playable_response(monkeypatch):
    monkeypatch.setattr("app.main.process_message", lambda *_args, **_kwargs: _answer())
    monkeypatch.setenv("AUDIO_SIMULATED_IDENTITIES", "token-de-teste=usuario-teste")
    monkeypatch.setattr(
        transcription, "transcribe",
        transcricao_fixa(text="pergunta falada", confidence=0.9, duration_seconds=1.0),
    )
    monkeypatch.setattr(
        "app.main.synthesize_optional",
        lambda _text: SpeechResponse(
            status="available", media_type="audio/mpeg",
            data_base64=base64.b64encode(b"ID3audio").decode(),
        ),
    )
    with TestClient(app) as client:
        text = client.post("/api/chat", json={"message": "pergunta", "include_audio": True})
        voice = client.post(
            "/api/audio", headers=AUTH_HEADER,
            data={"include_audio": "true"},
            files={"audio": ("pergunta.wav", _build_wav(), "audio/wav")},
        )
    assert text.status_code == voice.status_code == 200
    assert base64.b64decode(text.json()["speech"]["data_base64"]) == b"ID3audio"
    assert base64.b64decode(voice.json()["chat"]["speech"]["data_base64"]) == b"ID3audio"
    assert voice.json()["answer"]["text"] == voice.json()["chat"]["text"]
