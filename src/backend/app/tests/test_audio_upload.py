"""Cenarios de validacao e de erro do POST /api/audio (Secao 8.7 de Projeto.md)."""

import struct
from hashlib import sha256

import pytest
from fastapi.testclient import TestClient

from app.audio import security, transcription
from app.audio.errors import (
    AudioFormatUnsupportedError,
    AudioTooLargeError,
    AudioTooLongError,
    NoSpeechDetectedError,
)
from app.audio.validation import (
    DEFAULT_MAX_DURATION_SECONDS,
    DEFAULT_MAX_SIZE_BYTES,
    validate_audio_upload,
)
from app.main import app

TOKEN = "token-de-teste"
AUTH_HEADER = {"Authorization": f"Bearer {TOKEN}"}


@pytest.fixture(autouse=True)
def reset_concurrency_control() -> None:
    security._active_users.clear()


def _build_wav(
    *,
    sample_rate: int = 16_000,
    channels: int = 1,
    bits_per_sample: int = 16,
    duration_seconds: float = 1.0,
    amplitude: int = 8_000,
    format_code: int = 1,
) -> bytes:
    """Monta um WAV/PCM sintetico com onda quadrada audivel."""

    num_frames = int(sample_rate * duration_seconds)
    if bits_per_sample == 16:
        frames = b"".join(
            struct.pack("<h", amplitude if (index // 40) % 2 == 0 else -amplitude)
            * channels
            for index in range(num_frames)
        )
    else:
        frames = bytes([128]) * num_frames * channels

    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    fmt_chunk = struct.pack(
        "<HHIIHH", format_code, channels, sample_rate, byte_rate, block_align,
        bits_per_sample,
    )

    chunks = (
        b"fmt " + struct.pack("<I", len(fmt_chunk)) + fmt_chunk
        + b"data" + struct.pack("<I", len(frames)) + frames
    )
    return b"RIFF" + struct.pack("<I", 4 + len(chunks)) + b"WAVE" + chunks


def _build_extensible_wav(duration_seconds: float = 1.0) -> bytes:
    """WAV com WAVE_FORMAT_EXTENSIBLE e sub-formato PCM, como o Windows grava."""

    sample_rate, channels, bits = 16_000, 1, 16
    frames = b"".join(
        struct.pack("<h", 8_000 if (index // 40) % 2 == 0 else -8_000)
        for index in range(int(sample_rate * duration_seconds))
    )
    fmt_chunk = (
        struct.pack(
            "<HHIIHH", 0xFFFE, channels, sample_rate,
            sample_rate * channels * bits // 8, channels * bits // 8, bits,
        )
        + struct.pack("<H", 22)          # cbSize
        + struct.pack("<H", bits)        # valid bits per sample
        + struct.pack("<I", 4)           # channel mask
        + struct.pack("<H", 1)           # sub-formato: PCM
        + b"\x00" * 14                   # restante do GUID
    )
    chunks = (
        b"fmt " + struct.pack("<I", len(fmt_chunk)) + fmt_chunk
        + b"data" + struct.pack("<I", len(frames)) + frames
    )
    return b"RIFF" + struct.pack("<I", 4 + len(chunks)) + b"WAVE" + chunks


def _build_ogg_opus(
    *,
    channels: int = 1,
    input_sample_rate: int = 16_000,
    granule_position: int = 48_000,
    pre_skip: int = 0,
) -> bytes:
    opus_head = (
        b"OpusHead"
        + bytes([1])  # version
        + bytes([channels])
        + struct.pack("<H", pre_skip)
        + struct.pack("<I", input_sample_rate)
        + struct.pack("<h", 0)  # output gain
        + bytes([0])  # channel mapping family
    )

    def _page(granule: int, payload: bytes) -> bytes:
        segment_table = bytes([len(payload)]) if len(payload) < 255 else bytes([255, 0])
        header = (
            b"OggS"
            + bytes([0])  # version
            + bytes([0])  # header type
            + struct.pack("<q", granule)
            + struct.pack("<I", 1)  # serial
            + struct.pack("<I", 0)  # page sequence
            + struct.pack("<I", 0)  # checksum (nao verificado pelo parser)
            + bytes([len(segment_table)])
            + segment_table
        )
        return header + payload

    return _page(0, opus_head) + _page(granule_position, b"\x00" * 10)


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


class TestValidateAudioUpload:
    """Formatos aceitos e limites da Secao 8.7.3."""

    def test_valid_wav_is_accepted(self) -> None:
        probe = validate_audio_upload(_build_wav(duration_seconds=2.0))
        assert probe.container == "wav"
        assert probe.codec == "pcm"
        assert probe.sample_rate_hz == 16_000
        assert probe.channels == 1
        assert probe.duration_seconds == pytest.approx(2.0, abs=0.05)

    def test_valid_ogg_opus_is_accepted(self) -> None:
        probe = validate_audio_upload(_build_ogg_opus(granule_position=16_000))
        assert probe.container == "ogg"
        assert probe.codec == "opus"
        assert probe.sample_rate_hz == 16_000
        assert probe.channels == 1
        assert probe.duration_seconds == pytest.approx(16_000 / 48_000, abs=0.01)

    def test_extensible_wav_with_pcm_subformat_is_accepted(self) -> None:
        probe = validate_audio_upload(_build_extensible_wav(duration_seconds=2.0))
        assert probe.codec == "pcm"
        assert probe.duration_seconds == pytest.approx(2.0, abs=0.05)

    def test_browser_opus_at_48khz_is_accepted(self) -> None:
        """MediaRecorder grava a 48 kHz; recusar rejeitaria todo audio do frontend."""

        probe = validate_audio_upload(
            _build_ogg_opus(input_sample_rate=48_000, granule_position=48_000)
        )
        assert probe.sample_rate_hz == 48_000

    def test_opus_duration_discounts_pre_skip(self) -> None:
        probe = validate_audio_upload(
            _build_ogg_opus(granule_position=48_000 + 312, pre_skip=312)
        )
        assert probe.duration_seconds == pytest.approx(1.0, abs=0.001)

    def test_audio_at_the_duration_limit_is_accepted(self) -> None:
        probe = validate_audio_upload(
            _build_wav(duration_seconds=DEFAULT_MAX_DURATION_SECONDS)
        )
        assert probe.duration_seconds == pytest.approx(
            DEFAULT_MAX_DURATION_SECONDS, abs=0.05
        )

    def test_unknown_binary_is_rejected(self) -> None:
        with pytest.raises(AudioFormatUnsupportedError):
            validate_audio_upload(b"\xff\xfb\x90\x00" + b"\x00" * 100)

    def test_wrong_sample_rate_is_rejected(self) -> None:
        with pytest.raises(AudioFormatUnsupportedError):
            validate_audio_upload(_build_wav(sample_rate=44_100))

    def test_stereo_is_rejected(self) -> None:
        with pytest.raises(AudioFormatUnsupportedError):
            validate_audio_upload(_build_wav(channels=2))

    def test_eight_bit_depth_is_rejected(self) -> None:
        """O teto de 2 MB da Secao 8.7.3 deriva de 60 s a 16 kHz, 16 bits, mono."""

        with pytest.raises(AudioFormatUnsupportedError):
            validate_audio_upload(_build_wav(bits_per_sample=8, duration_seconds=2.0))

    def test_non_pcm_wav_codec_is_rejected(self) -> None:
        with pytest.raises(AudioFormatUnsupportedError):
            validate_audio_upload(_build_wav(format_code=17))  # ADPCM

    def test_stereo_opus_is_rejected(self) -> None:
        with pytest.raises(AudioFormatUnsupportedError):
            validate_audio_upload(_build_ogg_opus(channels=2))

    def test_ogg_without_opus_stream_is_rejected(self) -> None:
        with pytest.raises(AudioFormatUnsupportedError):
            validate_audio_upload(b"OggS" + b"\x00" * 60)

    def test_too_long_wav_is_rejected(self) -> None:
        with pytest.raises(AudioTooLongError):
            validate_audio_upload(_build_wav(duration_seconds=61.0))

    def test_too_large_file_is_rejected(self) -> None:
        oversized = _build_wav(duration_seconds=0.1) + b"\x00" * (3 * 1024 * 1024)
        with pytest.raises(AudioTooLargeError):
            validate_audio_upload(oversized)

    def test_silent_recording_is_rejected(self) -> None:
        with pytest.raises(NoSpeechDetectedError):
            validate_audio_upload(_build_wav(duration_seconds=2.0, amplitude=0))

    def test_data_lookup_follows_the_riff_chunk_structure(self) -> None:
        """Um chunk LIST/INFO com a palavra 'data' nao pode confundir a busca."""

        sample_rate, frames_count = 16_000, 32_000
        frames = b"".join(
            struct.pack("<h", 8_000 if (index // 40) % 2 == 0 else -8_000)
            for index in range(frames_count)
        )
        fmt_chunk = struct.pack("<HHIIHH", 1, 1, sample_rate, sample_rate * 2, 2, 16)
        info = b"data do arquivo aqui........"
        chunks = (
            b"fmt " + struct.pack("<I", len(fmt_chunk)) + fmt_chunk
            + b"LIST" + struct.pack("<I", len(info)) + info
            + b"data" + struct.pack("<I", len(frames)) + frames
        )
        wav = b"RIFF" + struct.pack("<I", 4 + len(chunks)) + b"WAVE" + chunks

        probe = validate_audio_upload(wav)
        assert probe.duration_seconds == pytest.approx(2.0, abs=0.05)

    def test_wav_without_audio_data_is_rejected(self) -> None:
        with pytest.raises(NoSpeechDetectedError):
            validate_audio_upload(_build_wav(duration_seconds=0.0))


class TestAudioUploadEndpoint:
    """Codigos de resposta da tabela da Secao 8.7.6."""

    def setup_method(self) -> None:
        self.client = TestClient(app)

    def test_missing_audio_field_returns_400(self) -> None:
        response = self.client.post("/api/audio", data={}, headers=AUTH_HEADER)
        assert_error(response, 400, "AUDIO_MISSING")

    def test_request_without_multipart_body_returns_400(self) -> None:
        response = self.client.post("/api/audio", headers=AUTH_HEADER)
        assert_error(response, 400, "AUDIO_MISSING")

    def test_unsupported_format_returns_400(self) -> None:
        response = post_audio(
            self.client, b"\xff\xfb\x90\x00" + b"\x00" * 50, "p.mp3", "audio/mpeg"
        )
        error = assert_error(response, 400, "AUDIO_FORMAT_UNSUPPORTED")
        assert error["detail"] == {"received": "audio/mpeg"}

    def test_too_long_audio_returns_400(self) -> None:
        content = _build_wav(duration_seconds=61.0)
        assert_error(
            post_audio(self.client, content, "p.wav", "audio/wav"), 400, "AUDIO_TOO_LONG"
        )

    def test_request_without_authorization_returns_401(self) -> None:
        response = self.client.post(
            "/api/audio", files={"audio": ("p.wav", _build_wav(), "audio/wav")}
        )
        assert_error(response, 401, "UNAUTHENTICATED")

    def test_token_outside_the_allowed_list_returns_401(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AUDIO_API_TOKENS", "token-valido")
        response = self.client.post(
            "/api/audio",
            files={"audio": ("p.wav", _build_wav(), "audio/wav")},
            headers={"Authorization": "Bearer token-invalido"},
        )
        assert_error(response, 401, "UNAUTHENTICATED")

    def test_too_large_file_returns_413(self) -> None:
        oversized = _build_wav(duration_seconds=0.1) + b"\x00" * (3 * 1024 * 1024)
        assert_error(
            post_audio(self.client, oversized, "p.wav", "audio/wav"),
            413,
            "AUDIO_TOO_LARGE",
        )

    def test_oversized_upload_returns_413_before_draining_the_stream(self) -> None:
        """O corte na leitura evita carregar em memoria o que ja seria recusado."""

        import asyncio

        from app.main import DEFAULT_MAX_SIZE_BYTES, _read_upload

        class CountingUpload:
            """Fluxo de 64 MB que registra quanto foi efetivamente lido."""

            def __init__(self, total_bytes: int) -> None:
                self.remaining = total_bytes
                self.bytes_read = 0

            async def read(self, size: int = -1) -> bytes:
                if self.remaining <= 0:
                    return b""
                chunk_size = self.remaining if size < 0 else min(size, self.remaining)
                self.remaining -= chunk_size
                self.bytes_read += chunk_size
                return b"\x00" * chunk_size

        upload = CountingUpload(64 * 1024 * 1024)
        with pytest.raises(AudioTooLargeError):
            asyncio.run(_read_upload(upload))

        # Para de ler logo apos ultrapassar o teto, em vez de drenar os 64 MB.
        assert upload.bytes_read <= DEFAULT_MAX_SIZE_BYTES + 64 * 1024
        assert upload.remaining > 0

    def test_silent_audio_returns_422(self) -> None:
        content = _build_wav(duration_seconds=2.0, amplitude=0)
        assert_error(
            post_audio(self.client, content, "p.wav", "audio/wav"),
            422,
            "NO_SPEECH_DETECTED",
        )

    def test_concurrent_request_for_the_same_user_returns_429(self) -> None:
        security._active_users.add(sha256(TOKEN.encode("utf-8")).hexdigest())
        assert_error(
            post_audio(self.client, _build_wav(), "p.wav", "audio/wav"),
            429,
            "RATE_LIMITED",
        )

    def test_concurrency_slot_is_released_after_a_rejected_request(self) -> None:
        post_audio(self.client, b"\xff\xfb\x90\x00", "p.mp3", "audio/mpeg")
        assert security._active_users == set()

    def test_provider_failure_returns_502(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def fail(*_args: object, **_kwargs: object):
            raise transcription.SttProviderError("connection reset by peer")

        monkeypatch.setattr(transcription, "transcribe", fail)
        error = assert_error(
            post_audio(self.client, _build_wav(), "p.wav", "audio/wav"),
            502,
            "STT_PROVIDER_ERROR",
        )
        assert "connection reset" not in error["message"]

    def test_provider_unavailable_returns_503(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def unavailable(*_args: object, **_kwargs: object):
            raise transcription.SttProviderUnavailable("fora do ar")

        monkeypatch.setattr(transcription, "transcribe", unavailable)
        assert_error(
            post_audio(self.client, _build_wav(), "p.wav", "audio/wav"),
            503,
            "STT_PROVIDER_UNAVAILABLE",
        )

    def test_valid_wav_upload_returns_200_with_stub_pipeline(self) -> None:
        response = self.client.post(
            "/api/audio",
            data={"conversation_id": "1f5c9a24-1c2e-4a8f-9a3e-2b6d8c0f1a77"},
            files={"audio": ("p.wav", _build_wav(duration_seconds=3.0), "audio/wav")},
            headers=AUTH_HEADER,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["conversation_id"] == "1f5c9a24-1c2e-4a8f-9a3e-2b6d8c0f1a77"
        assert body["pipeline_status"] == "stubbed"
        assert body["transcription"]["duration_seconds"] == pytest.approx(3.0, abs=0.05)

    def test_valid_ogg_upload_returns_200(self) -> None:
        content = _build_ogg_opus(granule_position=32_000)
        response = post_audio(self.client, content, "p.ogg", "audio/ogg")
        assert response.status_code == 200
        assert response.json()["pipeline_status"] == "stubbed"

    def test_generates_conversation_id_when_absent(self) -> None:
        response = post_audio(self.client, _build_wav(), "p.wav", "audio/wav")
        assert response.status_code == 200
        assert response.json()["conversation_id"]

    def test_returns_the_real_transcription_when_the_provider_answers(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            transcription,
            "transcribe",
            lambda *_args, **_kwargs: transcription.Transcription(
                text="qual o prazo do projeto", confidence=0.94, duration_seconds=2.0
            ),
        )
        response = post_audio(self.client, _build_wav(), "p.wav", "audio/wav")
        assert response.status_code == 200
        assert response.json()["transcription"]["text"] == "qual o prazo do projeto"


class TestControlledErrorMessages:
    """RNF11: mensagens controladas, sem detalhe tecnico interno."""

    def setup_method(self) -> None:
        self.client = TestClient(app)

    def test_error_body_never_carries_the_framework_validation_detail(self) -> None:
        response = self.client.post("/api/audio", headers=AUTH_HEADER)
        assert "detail" not in response.json()

    def test_detail_is_omitted_when_there_is_nothing_to_report(self) -> None:
        response = self.client.post("/api/audio", data={}, headers=AUTH_HEADER)
        assert "detail" not in response.json()["error"]

    def test_format_detail_does_not_leak_container_vocabulary(self) -> None:
        response = post_audio(
            self.client, _build_wav(format_code=17), "p.wav", "audio/wav"
        )
        error = assert_error(response, 400, "AUDIO_FORMAT_UNSUPPORTED")
        assert "format-code" not in str(error)
        assert "cabecalho" not in str(error)

    @pytest.mark.parametrize(
        "request_kwargs",
        [
            pytest.param({"headers": {}}, id="401"),
            pytest.param({"headers": AUTH_HEADER}, id="200-ou-erro-de-conteudo"),
        ],
    )
    def test_no_response_exposes_internal_identifiers(self, request_kwargs: dict) -> None:
        forbidden = ("Traceback", "app.audio", "Exception", "struct.error", "urllib")
        response = self.client.post(
            "/api/audio",
            files={"audio": ("p.wav", _build_wav(), "audio/wav")},
            **request_kwargs,
        )
        assert not any(term in response.text for term in forbidden)
