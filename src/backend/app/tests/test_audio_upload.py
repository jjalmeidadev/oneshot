"""Cenarios de validacao e de erro do `POST /api/audio` (Secao 8.7 do Projeto.md)."""

import struct
from hashlib import sha256

import pytest
from fastapi.testclient import TestClient

from app.audio import errors, router, transcription
from app.audio.errors import AudioError
from app.audio.validation import (
    MAX_DURATION_SECONDS,
    MAX_FILE_SIZE_BYTES,
    validate_audio,
)
from app.main import app

TOKEN = "token-de-teste"
AUTH_HEADER = {"Authorization": f"Bearer {TOKEN}"}


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_concurrency_control() -> None:
    router._active_users.clear()


def build_wav(
    duration_seconds: float = 2.0,
    sample_rate: int = 16_000,
    channels: int = 1,
    bits_per_sample: int = 16,
    amplitude: int = 8_000,
) -> bytes:
    """Monta um WAV/PCM sintetico com onda quadrada audivel."""

    bytes_per_sample = bits_per_sample // 8
    block_align = channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    frames = int(sample_rate * duration_seconds)

    samples = bytearray()
    for index in range(frames):
        value = amplitude if (index // 40) % 2 == 0 else -amplitude
        samples += struct.pack("<h", value) * channels

    data = bytes(samples)
    fmt_chunk = struct.pack(
        "<HHIIHH", 1, channels, sample_rate, byte_rate, block_align, bits_per_sample
    )
    body = (
        b"WAVE"
        + b"fmt "
        + struct.pack("<I", len(fmt_chunk))
        + fmt_chunk
        + b"data"
        + struct.pack("<I", len(data))
        + data
    )
    return b"RIFF" + struct.pack("<I", len(body)) + body


def _ogg_page(body: bytes, granule: int, sequence: int) -> bytes:
    segments = [255] * (len(body) // 255) + [len(body) % 255]
    header = (
        b"OggS"
        + bytes([0, 0])
        + struct.pack("<q", granule)
        + struct.pack("<II", 1, sequence)
        + struct.pack("<I", 0)
        + bytes([len(segments)])
        + bytes(segments)
    )
    return header + body


def build_ogg_opus(
    duration_seconds: float = 2.0, channels: int = 1, sample_rate: int = 16_000
) -> bytes:
    pre_skip = 312
    head = (
        b"OpusHead"
        + bytes([1, channels])
        + struct.pack("<H", pre_skip)
        + struct.pack("<I", sample_rate)
        + struct.pack("<h", 0)
        + bytes([0])
    )
    tags = b"OpusTags" + struct.pack("<I", 0) + struct.pack("<I", 0)
    granule = int(duration_seconds * 48_000) + pre_skip
    return (
        _ogg_page(head, 0, 0)
        + _ogg_page(tags, 0, 1)
        + _ogg_page(b"\x00" * 64, granule, 2)
    )


def post_audio(client: TestClient, content: bytes, filename: str, content_type: str):
    return client.post(
        "/api/audio",
        files={"audio": (filename, content, content_type)},
        headers=AUTH_HEADER,
    )


def assert_error(response, status_code: int, code: str) -> dict:
    assert response.status_code == status_code
    body = response.json()
    assert set(body) == {"error"}
    assert body["error"]["code"] == code
    assert body["error"]["message"]
    return body["error"]


# --- Validacao dos formatos aceitos (Secao 8.7.3) -------------------------------


def test_accepts_wav_pcm_16khz_mono() -> None:
    metadata = validate_audio(build_wav(duration_seconds=3.0), "audio/wav")

    assert (metadata.container, metadata.codec) == ("WAV", "PCM")
    assert metadata.sample_rate_hz == 16_000
    assert metadata.channels == 1
    assert metadata.duration_seconds == pytest.approx(3.0, abs=0.01)


def test_accepts_ogg_opus_16khz_mono() -> None:
    metadata = validate_audio(build_ogg_opus(duration_seconds=4.0), "audio/ogg")

    assert (metadata.container, metadata.codec) == ("OGG", "OPUS")
    assert metadata.channels == 1
    assert metadata.duration_seconds == pytest.approx(4.0, abs=0.01)


def test_accepts_audio_exactly_at_the_duration_limit() -> None:
    metadata = validate_audio(build_wav(duration_seconds=MAX_DURATION_SECONDS))

    assert metadata.duration_seconds == pytest.approx(MAX_DURATION_SECONDS, abs=0.01)


@pytest.mark.parametrize(
    "content",
    [
        pytest.param(b"ID3\x04\x00\x00" + b"\x00" * 512, id="mp3"),
        pytest.param(b"\x00" * 512, id="bytes-sem-container"),
        pytest.param(b"RIFF" + struct.pack("<I", 4) + b"AVI ", id="riff-nao-wave"),
    ],
)
def test_rejects_unsupported_container(content: bytes) -> None:
    with pytest.raises(AudioError) as raised:
        validate_audio(content, "audio/mpeg")

    assert raised.value.code == "AUDIO_FORMAT_UNSUPPORTED"
    assert raised.value.status_code == 400


@pytest.mark.parametrize(
    "kwargs",
    [
        pytest.param({"sample_rate": 44_100}, id="taxa-de-amostragem"),
        pytest.param({"channels": 2}, id="estereo"),
        pytest.param({"bits_per_sample": 8}, id="profundidade-de-bits"),
    ],
)
def test_rejects_wav_outside_the_declared_configuration(kwargs: dict) -> None:
    with pytest.raises(AudioError) as raised:
        validate_audio(build_wav(**kwargs))

    assert raised.value.code == "AUDIO_FORMAT_UNSUPPORTED"


def test_rejects_ogg_opus_outside_the_declared_configuration() -> None:
    with pytest.raises(AudioError) as raised:
        validate_audio(build_ogg_opus(channels=2), "audio/ogg")

    assert raised.value.code == "AUDIO_FORMAT_UNSUPPORTED"


def test_rejects_ogg_without_opus_identification_header() -> None:
    with pytest.raises(AudioError) as raised:
        validate_audio(_ogg_page(b"VorbisHead" + b"\x00" * 16, 0, 0), "audio/ogg")

    assert raised.value.code == "AUDIO_FORMAT_UNSUPPORTED"


# --- Limites de duracao, tamanho e ausencia de fala ----------------------------


def test_rejects_recording_above_sixty_seconds() -> None:
    with pytest.raises(AudioError) as raised:
        validate_audio(build_wav(duration_seconds=MAX_DURATION_SECONDS + 1))

    assert raised.value.status_code == 400
    assert raised.value.code == "AUDIO_TOO_LONG"
    assert raised.value.detail == {"duration_seconds": 61.0, "max_duration_seconds": 60}


def test_rejects_file_above_two_megabytes() -> None:
    with pytest.raises(AudioError) as raised:
        validate_audio(b"RIFF" + b"\x00" * MAX_FILE_SIZE_BYTES)

    assert raised.value.status_code == 413
    assert raised.value.code == "AUDIO_TOO_LARGE"


def test_rejects_recording_without_audible_signal() -> None:
    with pytest.raises(AudioError) as raised:
        validate_audio(build_wav(duration_seconds=2.0, amplitude=0))

    assert raised.value.status_code == 422
    assert raised.value.code == "NO_SPEECH_DETECTED"


def test_rejects_wav_without_audio_data() -> None:
    with pytest.raises(AudioError) as raised:
        validate_audio(build_wav(duration_seconds=0.0))

    assert raised.value.code == "NO_SPEECH_DETECTED"


# --- Codigos de resposta do endpoint (Secao 8.7.6) -----------------------------


def test_returns_400_when_audio_field_is_absent(client: TestClient) -> None:
    response = client.post("/api/audio", data={"language": "pt-BR"}, headers=AUTH_HEADER)

    assert_error(response, 400, "AUDIO_MISSING")


def test_returns_400_when_request_has_no_multipart_body(client: TestClient) -> None:
    response = client.post("/api/audio", headers=AUTH_HEADER)

    assert_error(response, 400, "AUDIO_MISSING")


def test_returns_400_for_unsupported_format(client: TestClient) -> None:
    response = post_audio(client, b"ID3\x04\x00\x00" + b"\x00" * 256, "p.mp3", "audio/mpeg")

    detail = assert_error(response, 400, "AUDIO_FORMAT_UNSUPPORTED")
    assert detail["detail"] == {"received": "audio/mpeg"}


def test_returns_400_for_recording_above_the_duration_limit(client: TestClient) -> None:
    content = build_wav(duration_seconds=MAX_DURATION_SECONDS + 1)

    assert_error(post_audio(client, content, "p.wav", "audio/wav"), 400, "AUDIO_TOO_LONG")


def test_returns_401_without_authorization_header(client: TestClient) -> None:
    response = client.post(
        "/api/audio", files={"audio": ("p.wav", build_wav(), "audio/wav")}
    )

    assert_error(response, 401, "UNAUTHENTICATED")


def test_returns_401_for_token_outside_the_allowed_list(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AUDIO_API_TOKENS", "token-valido")

    response = client.post(
        "/api/audio",
        files={"audio": ("p.wav", build_wav(), "audio/wav")},
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert_error(response, 401, "UNAUTHENTICATED")


def test_returns_413_for_file_above_the_size_limit(client: TestClient) -> None:
    content = b"RIFF" + b"\x00" * MAX_FILE_SIZE_BYTES

    assert_error(post_audio(client, content, "p.wav", "audio/wav"), 413, "AUDIO_TOO_LARGE")


def test_returns_422_when_no_speech_is_detected(client: TestClient) -> None:
    content = build_wav(duration_seconds=2.0, amplitude=0)

    assert_error(post_audio(client, content, "p.wav", "audio/wav"), 422, "NO_SPEECH_DETECTED")


def test_returns_429_when_the_user_already_has_a_transcription_in_progress(
    client: TestClient,
) -> None:
    router._active_users.add(sha256(TOKEN.encode("utf-8")).hexdigest())

    assert_error(post_audio(client, build_wav(), "p.wav", "audio/wav"), 429, "RATE_LIMITED")


def test_releases_the_concurrency_slot_after_a_rejected_request(
    client: TestClient,
) -> None:
    post_audio(client, b"ID3\x04\x00\x00", "p.mp3", "audio/mpeg")

    assert router._active_users == set()


def test_returns_502_when_the_transcription_service_fails(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(*_args: object, **_kwargs: object):
        raise transcription.SttProviderError("connection reset by peer")

    monkeypatch.setattr(transcription, "transcribe", fail)

    error = assert_error(
        post_audio(client, build_wav(), "p.wav", "audio/wav"), 502, "STT_PROVIDER_ERROR"
    )
    assert "connection reset" not in error["message"]


def test_returns_503_while_the_transcription_service_is_not_integrated(
    client: TestClient,
) -> None:
    assert_error(
        post_audio(client, build_wav(), "p.wav", "audio/wav"),
        503,
        "STT_PROVIDER_UNAVAILABLE",
    )


def test_returns_200_with_the_transcription_when_the_service_answers(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        transcription,
        "transcribe",
        lambda *_args, **_kwargs: transcription.Transcription(
            text="qual o prazo do projeto", confidence=0.94, duration_seconds=2.0
        ),
    )

    response = client.post(
        "/api/audio",
        files={"audio": ("p.wav", build_wav(), "audio/wav")},
        data={"conversation_id": "1f5c9a24-1c2e-4a8f-9a3e-2b6d8c0f1a77"},
        headers=AUTH_HEADER,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["conversation_id"] == "1f5c9a24-1c2e-4a8f-9a3e-2b6d8c0f1a77"
    assert body["transcription"]["text"] == "qual o prazo do projeto"
    assert body["interaction_id"]


# --- RNF11: mensagens controladas, sem detalhe tecnico interno -----------------


def test_every_predicted_error_returns_a_controlled_message() -> None:
    predicted = [
        errors.audio_missing(),
        errors.audio_format_unsupported("Formato nao suportado."),
        errors.audio_too_long(75.0, MAX_DURATION_SECONDS),
        errors.unauthenticated(),
        errors.audio_too_large(MAX_FILE_SIZE_BYTES),
        errors.no_speech_detected(),
        errors.rate_limited(),
        errors.stt_provider_error(),
        errors.stt_provider_unavailable(),
        errors.internal_error(),
    ]
    forbidden = ("Traceback", "app.", "Exception", "None", "urllib", "http.client")

    for error in predicted:
        payload = error.to_payload()
        assert set(payload) == {"error"}
        assert set(payload["error"]) <= {"code", "message", "detail"}
        assert payload["error"]["message"].endswith((".", "!"))
        assert not any(term in payload["error"]["message"] for term in forbidden)


def test_error_body_never_carries_the_framework_validation_detail(
    client: TestClient,
) -> None:
    response = client.post("/api/audio", headers=AUTH_HEADER)

    assert "detail" not in response.json()
