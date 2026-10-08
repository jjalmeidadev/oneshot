"""S4-31: fronteira HTTP controlada; nenhuma chamada real ao Azure."""

import asyncio
import runpy
from pathlib import Path

import httpx
import pytest

# Preserva a cobertura anterior do backend-api na selecao por marcador (#255).
pytestmark = pytest.mark.integration
from fastapi.testclient import TestClient

from app.audio import transcription
from app.audio.validation import validate_audio_upload
from app.audio.vhs import ResponseCache
from app.main import app
from app.tests.test_audio_upload import (
    AUTH_HEADER, _build_wav, post_audio, reset_concurrency_control,  # noqa: F401
)
from scripts.verify_audio_stt_pln_live import _delta, _p95

SUCCESS = {"RecognitionStatus": "Success", "NBest": [
    {"Display": "Qual o prazo do projeto?", "Confidence": 0.94}
]}


@pytest.fixture
def provider(monkeypatch, reset_concurrency_control, record_property):
    monkeypatch.setenv("AZURE_SPEECH_RESOURCE", "vhs-synthetic")
    monkeypatch.setenv("AZURE_SPEECH_KEY", "synthetic-key")
    monkeypatch.setenv("AZURE_SPEECH_MAX_ATTEMPTS", "1")
    state = {"calls": 0, "status": 200, "payload": SUCCESS}

    async def post(self, url, **kwargs):
        state["calls"] += 1
        if state.get("timeout"):
            raise httpx.ReadTimeout("internal-secret")
        if state.get("invalid_json"):
            return httpx.Response(200, content=b"not-json")
        return httpx.Response(state["status"], json=state["payload"])

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    yield state
    record_property("http_calls", state["calls"])
    for name, value in transcription.response_cache.metrics().items():
        record_property(name, value)


def send(client, data=None):
    return post_audio(client, data or _build_wav(), "synthetic.wav", "audio/wav")


def test_record_and_hit(provider):
    with TestClient(app) as client:
        first, second = send(client), send(client)
    assert first.status_code == second.status_code == 200
    assert first.json()["transcription"] == second.json()["transcription"]
    assert provider["calls"] == 1
    metrics = transcription.response_cache.metrics()
    assert (metrics["miss"], metrics["record"], metrics["hit"]) == (1, 1, 1)


def test_authenticated_metrics_quantify_cache_benefit(provider):
    with TestClient(app) as client:
        assert send(client).status_code == 200
        assert send(client).status_code == 200
        response = client.get("/api/audio/vhs/metrics", headers=AUTH_HEADER)

    assert response.status_code == 200
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["topology"] == "single-worker-per-container"
    assert len(payload["worker_id"]) == 32
    assert payload["entries"] == 1
    assert payload["pending"] == 0
    assert payload["counters"]["provider_call"] == 1
    assert payload["counters"]["hit"] == 1
    assert payload["hit_ratio"] == 0.5
    assert payload["estimated_provider_calls_avoided"] == 1


def test_metrics_reject_unauthenticated_access(provider):
    with TestClient(app) as client:
        response = client.get("/api/audio/vhs/metrics")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


def test_container_runtime_uses_one_api_worker():
    entrypoint = Path(__file__).resolve().parents[2] / "docker-entrypoint.py"
    command = runpy.run_path(str(entrypoint))["runtime_command"]()
    workers_index = command.index("--workers")
    assert command[workers_index + 1] == "1"


def test_live_evidence_helpers_calculate_delta_and_nearest_rank_p95():
    assert _delta({"hit": 7, "miss": 3}, {"hit": 2, "miss": 2}) == {
        "hit": 5,
        "miss": 1,
    }
    assert _p95([1, 2, 3, 4, 5]) == 5


def test_miss_different_audio(provider):
    with TestClient(app) as client:
        assert send(client).status_code == 200
        assert send(client, _build_wav(amplitude=4000)).status_code == 200
    assert provider["calls"] == transcription.response_cache.metrics()["miss"] == 2


def test_language_and_resource_isolation(provider, monkeypatch):
    data = _build_wav()
    probe = validate_audio_upload(data)
    for language in ("pt-BR", "en-US"):
        asyncio.run(transcription.transcribe(data, probe, language))
    monkeypatch.setenv("AZURE_SPEECH_RESOURCE", "other-resource")
    asyncio.run(transcription.transcribe(data, probe))
    assert provider["calls"] == 3


def test_expiration(provider, monkeypatch):
    now = [0.0]
    cache = ResponseCache(ttl_seconds=10, clock=lambda: now[0])
    monkeypatch.setattr(transcription, "response_cache", cache)
    with TestClient(app) as client:
        assert send(client).status_code == 200
        now[0] = 9.99
        assert send(client).status_code == 200
        assert provider["calls"] == 1
        now[0] = 10.0
        assert send(client).status_code == 200
    assert provider["calls"] == 2
    assert cache.metrics()["expired"] == 1


def test_invalidation(provider):
    with TestClient(app) as client:
        assert send(client).status_code == 200
        assert transcription.response_cache.invalidate() == 1
        assert send(client).status_code == 200
    assert provider["calls"] == 2
    assert transcription.response_cache.metrics()["invalidation"] == 1


@pytest.mark.parametrize("status,payload,expected,code", [
    (400, {"secret": "internal-secret"}, 502, "STT_PROVIDER_ERROR"),
    (503, {}, 503, "STT_PROVIDER_UNAVAILABLE"),
    (429, {}, 429, "RATE_LIMITED"),
    (200, {"RecognitionStatus": "NoMatch"}, 422, "NO_SPEECH_DETECTED"),
    (200, {"RecognitionStatus": "Error"}, 502, "STT_PROVIDER_ERROR"),
    (200, [], 502, "STT_PROVIDER_ERROR"),
])
def test_provider_error_and_recovery(provider, status, payload, expected, code):
    provider.update(status=status, payload=payload)
    with TestClient(app) as client:
        for _ in range(2):
            response = send(client)
            assert response.status_code == expected
            assert response.json()["error"]["code"] == code
            assert "internal-secret" not in response.text
        assert provider["calls"] == 2
        assert transcription.response_cache.metrics()["record"] == 0
        provider.update(status=200, payload=SUCCESS)
        assert send(client).status_code == send(client).status_code == 200
    assert provider["calls"] == 3
    assert transcription.response_cache.metrics()["provider_error"] == 2


def test_disabled(provider, monkeypatch):
    monkeypatch.setenv("VHS_ENABLED", "0")
    with TestClient(app) as client:
        assert send(client).status_code == send(client).status_code == 200
    assert provider["calls"] == 2
    assert transcription.response_cache.metrics()["record"] == 0


@pytest.mark.parametrize("fault,status", [("timeout", 503), ("invalid_json", 502)])
def test_transport_failure(provider, fault, status):
    provider[fault] = True
    with TestClient(app) as client:
        for _ in range(2):
            response = send(client)
            assert response.status_code == status
            assert "internal-secret" not in response.text
    assert provider["calls"] == 2
    assert transcription.response_cache.metrics()["record"] == 0


def test_capacity(provider, monkeypatch):
    monkeypatch.setattr(transcription, "response_cache", ResponseCache(max_entries=1))
    with TestClient(app) as client:
        for amplitude in (8000, 4000, 8000):
            assert send(client, _build_wav(amplitude=amplitude)).status_code == 200
    assert provider["calls"] == 3
    assert transcription.response_cache.metrics()["eviction"] == 2


def test_concurrent_repetitions():
    async def scenario():
        cache = ResponseCache()
        calls = 0

        async def external():
            nonlocal calls
            calls += 1
            await asyncio.sleep(0.01)
            return "recorded"

        results = await asyncio.gather(*(cache.get_or_record("same", external) for _ in range(10)))
        assert results == ["recorded"] * 10
        assert calls == 1
        assert cache.metrics()["coalesced"] == 9
    asyncio.run(scenario())


def test_invalidation_during_request():
    async def scenario():
        cache = ResponseCache()
        started, finish = asyncio.Event(), asyncio.Event()

        async def external():
            started.set()
            await finish.wait()
            return "old"

        task = asyncio.create_task(cache.get_or_record("same", external))
        await started.wait()
        cache.invalidate()
        finish.set()
        assert await task == "old"
        assert cache.metrics()["record"] == 0
        await cache.get_or_record("same", external)
        assert cache.metrics()["provider_call"] == 2
    asyncio.run(scenario())
