"""Cenarios de validacao e de erro do POST /api/audio (Secao 8.7 de Projeto.md)."""

import asyncio
import struct
from types import SimpleNamespace
from hashlib import sha256

import httpx
import pytest
from fastapi.testclient import TestClient

from app.audio import security, transcription
from app.audio.errors import (
    AudioFormatUnsupportedError,
    AudioTooLargeError,
    AudioTooLongError,
    NoSpeechDetectedError,
    RateLimitedError,
    UnauthenticatedError,
)
from app.audio.validation import (
    DEFAULT_MAX_DURATION_SECONDS,
    DEFAULT_MAX_SIZE_BYTES,
    validate_audio_upload,
)
from app.audio.schemas import MAX_CONVERSATION_ID_LENGTH
from app.main import app

TOKEN = "token-de-teste"
AUTH_HEADER = {"Authorization": f"Bearer {TOKEN}"}


class FakeAzureResponse:
    def __init__(self, status_code: int, payload: dict | None = None) -> None:
        self.status_code = status_code
        self._payload = payload or {}

    def json(self) -> dict:
        return self._payload


class FakeAzureClient:
    """Duplo do `httpx.AsyncClient`, com o mesmo protocolo assincrono."""

    def __init__(self, response: FakeAzureResponse, captured: dict) -> None:
        self.response = response
        self.captured = captured

    async def __aenter__(self) -> "FakeAzureClient":
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    async def post(self, url: str, *, content: bytes, headers: dict[str, str]):
        self.captured["url"] = url
        self.captured["content"] = content
        self.captured["headers"] = headers
        self.captured["tentativas"] = self.captured.get("tentativas", 0) + 1
        return self.response


def fake_azure_client_factory(response: FakeAzureResponse, captured: dict):
    def factory(*, timeout: float):
        captured["timeout"] = timeout
        return FakeAzureClient(response, captured)

    return factory


def transcrever(*args, **kwargs):
    """Executa a corrotina de transcricao a partir de um teste sincrono."""

    return asyncio.run(transcription.transcribe(*args, **kwargs))


def transcricao_fixa(**campos):
    """Substitui o provedor por uma corrotina que devolve sempre o mesmo texto."""

    async def _transcrever(*_args: object, **_kwargs: object):
        return transcription.Transcription(**campos)

    return _transcrever


def falha_do_provedor(excecao: Exception):
    """Substitui o provedor por uma corrotina que sempre levanta `excecao`."""

    async def _falhar(*_args: object, **_kwargs: object):
        raise excecao

    return _falhar


def classificacao_fixa(
    *,
    macro: str = "CONSULTA",
    intencao: str | None = "consulta_status_projeto",
    roteada: bool = True,
    resposta_sugerida: str | None = None,
):
    return SimpleNamespace(
        macrointencao=macro,
        intencao=intencao,
        confianca_macro=.9 if roteada else .3,
        confianca_intencao=.8,
        fluxo="Consulta documental",
        handler=f"handler:{intencao}" if intencao else "limitacao",
        alternativas=[(intencao or "fora_de_escopo", .8)],
        roteada=roteada,
        resposta_sugerida=resposta_sugerida,
    )


@pytest.fixture(autouse=True)
def reset_concurrency_control(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.gemini.schemas import GeminiChatResponse, GeminiUsage
    monkeypatch.setattr(
        "app.pipeline.generate_chat_response",
        lambda request, intent=None, entities=None: GeminiChatResponse(
            text="Resposta fundamentada de teste",
            model="teste",
            interaction_id="interaction-teste",
            latency_ms=1,
            usage=GeminiUsage(),
        ),
    )
    monkeypatch.setattr("app.nlp.inference.classify", lambda text: classificacao_fixa())
    monkeypatch.setattr("app.pipeline.trace_interaction", lambda **_kwargs: None)
    monkeypatch.setenv(
        "AUDIO_SIMULATED_IDENTITIES",
        f"{TOKEN}={sha256(TOKEN.encode('utf-8')).hexdigest()}",
    )
    security._active_identities.clear()
    monkeypatch.delenv(transcription.AZURE_SPEECH_RESOURCE_ENV, raising=False)
    monkeypatch.delenv(transcription.AZURE_SPEECH_ENDPOINT_ENV, raising=False)
    monkeypatch.delenv(transcription.AZURE_SPEECH_KEY_ENV, raising=False)


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

    def test_conversation_id_longer_than_database_contract_returns_400(self) -> None:
        response = self.client.post(
            "/api/audio",
            data={"conversation_id": "x" * (MAX_CONVERSATION_ID_LENGTH + 1)},
            files={"audio": ("p.wav", _build_wav(), "audio/wav")},
            headers=AUTH_HEADER,
        )

        assert_error(response, 400, "INVALID_INPUT")

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

    def test_token_outside_the_simulated_identities_returns_401(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(
            security.SIMULATED_IDENTITIES_ENV,
            "token-mariana=REDACTED_FOR_PUBLIC_RELEASE",
        )
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
        security._active_identities.add(sha256(TOKEN.encode("utf-8")).hexdigest())
        assert_error(
            post_audio(self.client, _build_wav(), "p.wav", "audio/wav"),
            429,
            "RATE_LIMITED",
        )

    def test_provider_quota_exceeded_returns_429(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A franquia do provedor e o outro caminho para o 429 da Secao 8.7.6."""

        monkeypatch.setattr(
            transcription,
            "transcribe",
            falha_do_provedor(
                transcription.SttProviderRateLimited("franquia excedida")
            ),
        )
        error = assert_error(
            post_audio(self.client, _build_wav(), "p.wav", "audio/wav"),
            429,
            "RATE_LIMITED",
        )
        assert "franquia excedida" not in error["message"]

    def test_concurrency_slot_is_released_after_a_rejected_request(self) -> None:
        post_audio(self.client, b"\xff\xfb\x90\x00", "p.mp3", "audio/mpeg")
        assert security._active_identities == set()

    def test_provider_failure_returns_502(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            transcription,
            "transcribe",
            falha_do_provedor(
                transcription.SttProviderError("connection reset by peer")
            ),
        )
        error = assert_error(
            post_audio(self.client, _build_wav(), "p.wav", "audio/wav"),
            502,
            "STT_PROVIDER_ERROR",
        )
        assert "connection reset" not in error["message"]

    def test_provider_unavailable_returns_503(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            transcription,
            "transcribe",
            falha_do_provedor(transcription.SttProviderUnavailable("fora do ar")),
        )
        assert_error(
            post_audio(self.client, _build_wav(), "p.wav", "audio/wav"),
            503,
            "STT_PROVIDER_UNAVAILABLE",
        )

    def test_valid_wav_upload_returns_200_with_transcription(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            transcription,
            "transcribe",
            transcricao_fixa(
                text="qual o prazo do projeto", confidence=0.94, duration_seconds=3.0
            ),
        )
        response = self.client.post(
            "/api/audio",
            data={"conversation_id": "1f5c9a24-1c2e-4a8f-9a3e-2b6d8c0f1a77"},
            files={"audio": ("p.wav", _build_wav(duration_seconds=3.0), "audio/wav")},
            headers=AUTH_HEADER,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["conversation_id"] == "1f5c9a24-1c2e-4a8f-9a3e-2b6d8c0f1a77"
        assert body["pipeline_status"] == "completed"
        assert body["answer"]["text"] == "Resposta fundamentada de teste"
        assert body["chat"]["interaction_id"] == "interaction-teste"
        assert body["transcription"]["text"] == "qual o prazo do projeto"
        assert body["transcription"]["confidence"] == 0.94
        assert body["transcription"]["duration_seconds"] == pytest.approx(3.0, abs=0.05)

    def test_valid_ogg_upload_returns_200(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            transcription,
            "transcribe",
            transcricao_fixa(
                text="consulta por voz", confidence=0.9, duration_seconds=0.67
            ),
        )
        content = _build_ogg_opus(granule_position=32_000)
        response = post_audio(self.client, content, "p.ogg", "audio/ogg")
        assert response.status_code == 200
        assert response.json()["pipeline_status"] == "completed"

    def test_generates_conversation_id_when_absent(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            transcription,
            "transcribe",
            transcricao_fixa(
                text="consulta por voz", confidence=0.9, duration_seconds=1.0
            ),
        )
        response = post_audio(self.client, _build_wav(), "p.wav", "audio/wav")
        assert response.status_code == 200
        assert response.json()["conversation_id"]

    def test_returns_the_real_transcription_when_the_provider_answers(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            transcription,
            "transcribe",
            transcricao_fixa(
                text="qual o prazo do projeto", confidence=0.94, duration_seconds=2.0
            ),
        )
        response = post_audio(self.client, _build_wav(), "p.wav", "audio/wav")
        assert response.status_code == 200
        assert response.json()["transcription"]["text"] == "qual o prazo do projeto"

    def test_audio_response_exposes_intent_entities_and_pipeline_metrics(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            transcription,
            "transcribe",
            transcricao_fixa(
                text="status do Linha 15-Prata", confidence=0.91, duration_seconds=1.5
            ),
        )

        response = post_audio(self.client, _build_wav(duration_seconds=1.5), "p.wav", "audio/wav")

        assert response.status_code == 200
        body = response.json()
        assert body["pipeline_status"] == "completed"
        assert body["intent"] == body["chat"]["intent"]
        assert body["entities"] == body["chat"]["entities"]
        assert body["intent"]["handler"] == "handler:consulta_status_projeto"
        assert body["entities"][0]["type"] == "projeto"
        assert body["entities"][0]["value"] == "Linha 15-Prata"
        assert body["pipeline_metrics"]["validation_ms"] >= 0
        assert body["pipeline_metrics"]["stt_ms"] >= 0
        assert body["pipeline_metrics"]["nlp_ms"] == body["chat"]["pipeline_metrics"]["nlp_ms"]
        assert body["pipeline_metrics"]["total_ms"] >= body["pipeline_metrics"]["stt_ms"]

    def test_audio_out_of_scope_finishes_with_controlled_answer_without_gemini(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fail_if_called(_request):
            raise AssertionError("Gemini/RAG should not run for out-of-scope audio")

        monkeypatch.setattr("app.pipeline.generate_chat_response", fail_if_called)
        monkeypatch.setattr(
            "app.nlp.inference.classify",
            lambda text: classificacao_fixa(
                macro="FORA_DE_ESCOPO",
                intencao=None,
                roteada=True,
            ),
        )
        monkeypatch.setattr(
            transcription,
            "transcribe",
            transcricao_fixa(
                text="qual a previsão do tempo amanhã", confidence=0.9, duration_seconds=1.0
            ),
        )

        response = post_audio(self.client, _build_wav(), "p.wav", "audio/wav")

        assert response.status_code == 200
        body = response.json()
        assert body["pipeline_status"] == "completed"
        assert body["interaction_id"] is None
        assert body["chat"]["interaction_id"] is None
        assert body["chat"]["sources"] == []
        assert body["intent"]["macro"] == "FORA_DE_ESCOPO"
        assert body["answer"]["text"] == body["chat"]["text"]
        assert "portfólio" in body["answer"]["text"]
        assert body["pipeline_metrics"]["nlp_ms"] >= 0
        assert body["pipeline_metrics"]["total_ms"] >= body["pipeline_metrics"]["nlp_ms"]


class TestAzureSpeechTranscription:
    """Integracao HTTP com Azure AI Speech sem chamada real de rede."""

    def test_transcribes_valid_wav_with_azure_detailed_response(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        audio = _build_wav(duration_seconds=2.0)
        probe = validate_audio_upload(audio)
        captured: dict = {}

        monkeypatch.setenv(transcription.AZURE_SPEECH_RESOURCE_ENV, "metro-speech")
        monkeypatch.setenv(transcription.AZURE_SPEECH_KEY_ENV, "secret-key")
        monkeypatch.setenv(transcription.AZURE_SPEECH_TIMEOUT_ENV, "12")
        monkeypatch.setattr(
            transcription.httpx,
            "AsyncClient",
            fake_azure_client_factory(
                FakeAzureResponse(
                    200,
                    {
                        "RecognitionStatus": "Success",
                        "NBest": [
                            {
                                "Confidence": 0.45,
                                "MaskedITN": "alternativa pior",
                            },
                            {
                                "Confidence": 0.94,
                                "MaskedITN": "qual o prazo do projeto",
                                "Lexical": "qual o prazo do projeto",
                            },
                        ],
                    },
                ),
                captured,
            ),
        )

        result = transcrever(audio, probe, "pt-BR")

        assert result == transcription.Transcription(
            text="qual o prazo do projeto",
            confidence=0.94,
            duration_seconds=2.0,
        )
        assert captured["timeout"] == 12
        assert "language=pt-BR" in captured["url"]
        assert "format=detailed" in captured["url"]
        assert captured["content"] == audio
        assert captured["headers"] == {
            "Accept": "application/json",
            "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
            "Ocp-Apim-Subscription-Key": "secret-key",
        }

    def test_transcribes_ogg_with_opus_content_type(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        audio = _build_ogg_opus(granule_position=48_000)
        probe = validate_audio_upload(audio)
        captured: dict = {}

        monkeypatch.setenv(transcription.AZURE_SPEECH_RESOURCE_ENV, "metro-speech")
        monkeypatch.setenv(transcription.AZURE_SPEECH_KEY_ENV, "secret-key")
        monkeypatch.setattr(
            transcription.httpx,
            "AsyncClient",
            fake_azure_client_factory(
                FakeAzureResponse(
                    200,
                    {
                        "RecognitionStatus": "Success",
                        "NBest": [{"Confidence": 0.88, "ITN": "texto do ogg"}],
                    },
                ),
                captured,
            ),
        )

        result = transcrever(audio, probe)

        assert result.text == "texto do ogg"
        assert captured["headers"]["Content-Type"] == "audio/ogg; codecs=opus"

    def test_prefers_configured_regional_endpoint(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        audio = _build_wav()
        probe = validate_audio_upload(audio)
        captured: dict = {}

        monkeypatch.setenv(transcription.AZURE_SPEECH_RESOURCE_ENV, "oneshot-stt")
        monkeypatch.setenv(
            transcription.AZURE_SPEECH_ENDPOINT_ENV,
            "https://eastus.api.cognitive.microsoft.com/",
        )
        monkeypatch.setenv(transcription.AZURE_SPEECH_KEY_ENV, "secret-key")
        monkeypatch.setattr(
            transcription.httpx,
            "AsyncClient",
            fake_azure_client_factory(
                FakeAzureResponse(
                    200,
                    {
                        "RecognitionStatus": "Success",
                        "NBest": [{"Confidence": 0.8, "Display": "texto regional"}],
                    },
                ),
                captured,
            ),
        )

        result = transcrever(audio, probe)

        assert result.text == "texto regional"
        assert captured["url"].startswith(
            "https://eastus.stt.speech.microsoft.com/speech/recognition/"
        )

    def test_missing_azure_configuration_is_unavailable(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv(transcription.AZURE_SPEECH_RESOURCE_ENV, raising=False)
        monkeypatch.delenv(transcription.AZURE_SPEECH_ENDPOINT_ENV, raising=False)
        monkeypatch.delenv(transcription.AZURE_SPEECH_KEY_ENV, raising=False)

        with pytest.raises(transcription.SttProviderUnavailable):
            transcrever(
                _build_wav(), validate_audio_upload(_build_wav())
            )

    def test_quota_exceeded_is_rate_limited(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A Secao 8.7.6 reserva o 429 para a franquia do provedor estourada.

        O projeto usa o nivel gratuito do Azure, entao o caso e provavel; dizer
        "servico indisponivel" mandaria o usuario para o texto quando bastava
        aguardar.
        """

        capturado: dict = {}
        monkeypatch.setenv(transcription.AZURE_SPEECH_RESOURCE_ENV, "metro-speech")
        monkeypatch.setenv(transcription.AZURE_SPEECH_KEY_ENV, "secret-key")
        monkeypatch.setattr(
            transcription.httpx,
            "AsyncClient",
            fake_azure_client_factory(FakeAzureResponse(429), capturado),
        )

        with pytest.raises(transcription.SttProviderRateLimited):
            transcrever(_build_wav(), validate_audio_upload(_build_wav()))

        # Repetir uma requisicao barrada por franquia so agravaria o limite.
        assert capturado["tentativas"] == 1

    def test_transient_status_is_unavailable(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        capturado: dict = {}
        monkeypatch.setenv(transcription.AZURE_SPEECH_RESOURCE_ENV, "metro-speech")
        monkeypatch.setenv(transcription.AZURE_SPEECH_KEY_ENV, "secret-key")
        monkeypatch.setattr(
            transcription.httpx,
            "AsyncClient",
            fake_azure_client_factory(FakeAzureResponse(503), capturado),
        )

        with pytest.raises(transcription.SttProviderUnavailable):
            transcrever(_build_wav(), validate_audio_upload(_build_wav()))

        assert capturado["tentativas"] == transcription.DEFAULT_MAX_ATTEMPTS

    def test_permanent_error_is_not_retried(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        capturado: dict = {}
        monkeypatch.setenv(transcription.AZURE_SPEECH_RESOURCE_ENV, "metro-speech")
        monkeypatch.setenv(transcription.AZURE_SPEECH_KEY_ENV, "secret-key")
        monkeypatch.setattr(
            transcription.httpx,
            "AsyncClient",
            fake_azure_client_factory(FakeAzureResponse(400), capturado),
        )

        with pytest.raises(transcription.SttProviderError):
            transcrever(_build_wav(), validate_audio_upload(_build_wav()))

        assert capturado["tentativas"] == 1

    def test_retry_reuses_the_same_http_client(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Repetir a chamada nao deve repetir o handshake TLS."""

        capturado: dict = {}
        criados = []

        def fabrica(*, timeout: float):
            capturado["timeout"] = timeout
            cliente = FakeAzureClient(FakeAzureResponse(503), capturado)
            criados.append(cliente)
            return cliente

        monkeypatch.setenv(transcription.AZURE_SPEECH_RESOURCE_ENV, "metro-speech")
        monkeypatch.setenv(transcription.AZURE_SPEECH_KEY_ENV, "secret-key")
        monkeypatch.setattr(transcription.httpx, "AsyncClient", fabrica)

        with pytest.raises(transcription.SttProviderUnavailable):
            transcrever(_build_wav(), validate_audio_upload(_build_wav()))

        assert capturado["tentativas"] == transcription.DEFAULT_MAX_ATTEMPTS
        assert len(criados) == 1

    def test_recognition_error_is_a_provider_failure(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """`Error` e falha do provedor, nao ausencia de fala.

        Devolver 422 mandaria o usuario regravar um audio que estava correto.
        """

        monkeypatch.setenv(transcription.AZURE_SPEECH_RESOURCE_ENV, "metro-speech")
        monkeypatch.setenv(transcription.AZURE_SPEECH_KEY_ENV, "secret-key")
        monkeypatch.setattr(
            transcription.httpx,
            "AsyncClient",
            fake_azure_client_factory(
                FakeAzureResponse(200, {"RecognitionStatus": "Error"}), {}
            ),
        )

        with pytest.raises(transcription.SttProviderError):
            transcrever(_build_wav(), validate_audio_upload(_build_wav()))

    def test_permanent_provider_error_is_failed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(transcription.AZURE_SPEECH_RESOURCE_ENV, "metro-speech")
        monkeypatch.setenv(transcription.AZURE_SPEECH_KEY_ENV, "secret-key")
        monkeypatch.setattr(
            transcription.httpx,
            "AsyncClient",
            fake_azure_client_factory(FakeAzureResponse(400), {}),
        )

        with pytest.raises(transcription.SttProviderError):
            transcrever(
                _build_wav(), validate_audio_upload(_build_wav())
            )

    def test_no_match_from_provider_is_no_speech(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(transcription.AZURE_SPEECH_RESOURCE_ENV, "metro-speech")
        monkeypatch.setenv(transcription.AZURE_SPEECH_KEY_ENV, "secret-key")
        monkeypatch.setattr(
            transcription.httpx,
            "AsyncClient",
            fake_azure_client_factory(
                FakeAzureResponse(200, {"RecognitionStatus": "NoMatch"}), {}
            ),
        )

        with pytest.raises(NoSpeechDetectedError):
            transcrever(
                _build_wav(), validate_audio_upload(_build_wav())
            )

    def test_timeout_is_unavailable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        class TimeoutClient:
            async def __aenter__(self) -> "TimeoutClient":
                return self

            async def __aexit__(self, *_args: object) -> None:
                return None

            async def post(self, *_args: object, **_kwargs: object):
                raise httpx.TimeoutException("timeout")

        monkeypatch.setenv(transcription.AZURE_SPEECH_RESOURCE_ENV, "metro-speech")
        monkeypatch.setenv(transcription.AZURE_SPEECH_KEY_ENV, "secret-key")
        monkeypatch.setattr(
            transcription.httpx,
            "AsyncClient",
            lambda *, timeout: TimeoutClient(),
        )

        with pytest.raises(transcription.SttProviderUnavailable):
            transcrever(
                _build_wav(), validate_audio_upload(_build_wav())
            )


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


class TestCorporateIdentity:
    """Identidade vinda do canal, conforme a Secao 6.2.4 do Projeto.md."""

    def test_simulated_map_yields_the_declared_entra_object_id(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        object_id = "REDACTED_FOR_PUBLIC_RELEASE"
        monkeypatch.setenv(
            security.SIMULATED_IDENTITIES_ENV, f"token-mariana={object_id}"
        )

        identity = security.resolve_identity("Bearer token-mariana")

        assert identity.object_id == object_id

    def test_identity_is_derived_and_stable_without_the_simulated_map(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv(security.SIMULATED_IDENTITIES_ENV, raising=False)

        first = security.resolve_identity("Bearer token-qualquer")
        second = security.resolve_identity("Bearer token-qualquer")

        assert first.object_id == second.object_id
        assert "token-qualquer" not in first.object_id

    def test_different_tokens_yield_different_identities(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv(security.SIMULATED_IDENTITIES_ENV, raising=False)

        assert (
            security.resolve_identity("Bearer token-a").object_id
            != security.resolve_identity("Bearer token-b").object_id
        )

    @pytest.mark.parametrize(
        "header",
        [
            pytest.param(None, id="ausente"),
            pytest.param("", id="vazio"),
            pytest.param("Bearer ", id="bearer-sem-token"),
            pytest.param("Basic dXNlcjpzZW5oYQ==", id="esquema-errado"),
        ],
    )
    def test_invalid_authorization_header_is_rejected(self, header: str | None) -> None:
        with pytest.raises(UnauthenticatedError):
            security.resolve_identity(header)

    def test_concurrency_is_keyed_by_identity_not_by_token(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Dois tokens da mesma pessoa disputam a mesma vaga de processamento."""

        object_id = "REDACTED_FOR_PUBLIC_RELEASE"
        monkeypatch.setenv(
            security.SIMULATED_IDENTITIES_ENV,
            f"token-web={object_id},token-teams={object_id}",
        )

        with security.single_request_per_identity(
            security.resolve_identity("Bearer token-web")
        ):
            with pytest.raises(RateLimitedError):
                with security.single_request_per_identity(
                    security.resolve_identity("Bearer token-teams")
                ):
                    pass
