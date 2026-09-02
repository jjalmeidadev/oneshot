import struct

import pytest
from fastapi.testclient import TestClient

from app.audio.errors import (
    AudioFormatUnsupportedError,
    AudioMissingError,
    AudioTooLargeError,
    AudioTooLongError,
)
from app.audio.validation import validate_audio_upload
from app.main import app


def _build_wav(
    *,
    sample_rate: int = 16_000,
    channels: int = 1,
    bits_per_sample: int = 16,
    duration_seconds: float = 1.0,
) -> bytes:
    num_frames = int(sample_rate * duration_seconds)
    data = b"\x00\x00" * channels * num_frames

    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8

    fmt_chunk = struct.pack(
        "<HHIIHH",
        1,  # PCM
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
    )

    chunks = (
        b"fmt " + struct.pack("<I", len(fmt_chunk)) + fmt_chunk
        + b"data" + struct.pack("<I", len(data)) + data
    )
    riff_size = 4 + len(chunks)  # "WAVE" + chunks
    return b"RIFF" + struct.pack("<I", riff_size) + b"WAVE" + chunks


def _build_ogg_opus(
    *,
    channels: int = 1,
    input_sample_rate: int = 16_000,
    granule_position: int = 48_000,
) -> bytes:
    opus_head = (
        b"OpusHead"
        + bytes([1])  # version
        + bytes([channels])
        + struct.pack("<H", 0)  # pre-skip
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
            + struct.pack("<I", 0)  # checksum (unchecked by our parser)
            + bytes([len(segment_table)])
            + segment_table
        )
        return header + payload

    first_page = _page(0, opus_head)
    second_page = _page(granule_position, b"\x00" * 10)
    return first_page + second_page


class TestValidateAudioUpload:
    def test_valid_wav_is_accepted(self) -> None:
        probe = validate_audio_upload(_build_wav(duration_seconds=2.0))
        assert probe.container == "wav"
        assert probe.codec == "pcm"
        assert probe.sample_rate_hz == 16_000
        assert probe.channels == 1
        assert probe.duration_seconds == pytest.approx(2.0, abs=0.05)

    def test_valid_ogg_opus_is_accepted(self) -> None:
        probe = validate_audio_upload(
            _build_ogg_opus(granule_position=16_000)
        )
        assert probe.container == "ogg"
        assert probe.codec == "opus"
        assert probe.sample_rate_hz == 16_000
        assert probe.channels == 1
        assert probe.duration_seconds == pytest.approx(16_000 / 48_000, abs=0.01)

    def test_unknown_binary_is_rejected(self) -> None:
        with pytest.raises(AudioFormatUnsupportedError):
            validate_audio_upload(b"\xff\xfb\x90\x00" + b"\x00" * 100)

    def test_wrong_sample_rate_is_rejected(self) -> None:
        with pytest.raises(AudioFormatUnsupportedError):
            validate_audio_upload(_build_wav(sample_rate=44_100))

    def test_stereo_is_rejected(self) -> None:
        with pytest.raises(AudioFormatUnsupportedError):
            validate_audio_upload(_build_wav(channels=2))

    def test_too_long_wav_is_rejected(self) -> None:
        with pytest.raises(AudioTooLongError):
            validate_audio_upload(_build_wav(duration_seconds=61.0))

    def test_too_large_file_is_rejected(self) -> None:
        oversized = _build_wav(duration_seconds=0.1) + b"\x00" * (3 * 1024 * 1024)
        with pytest.raises(AudioTooLargeError):
            validate_audio_upload(oversized)


class TestAudioUploadEndpoint:
    def setup_method(self) -> None:
        self.client = TestClient(app)

    def test_missing_audio_field_returns_400(self) -> None:
        response = self.client.post("/api/audio", data={})
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "AUDIO_MISSING"

    def test_unsupported_format_returns_400(self) -> None:
        response = self.client.post(
            "/api/audio",
            files={"audio": ("pergunta.mp3", b"\xff\xfb\x90\x00" + b"\x00" * 50, "audio/mpeg")},
        )
        assert response.status_code == 400
        body = response.json()
        assert body["error"]["code"] == "AUDIO_FORMAT_UNSUPPORTED"
        assert "received" in body["error"]["detail"]

    def test_too_large_file_returns_413(self) -> None:
        oversized = _build_wav(duration_seconds=0.1) + b"\x00" * (3 * 1024 * 1024)
        response = self.client.post(
            "/api/audio",
            files={"audio": ("pergunta.wav", oversized, "audio/wav")},
        )
        assert response.status_code == 413
        assert response.json()["error"]["code"] == "AUDIO_TOO_LARGE"

    def test_too_long_audio_returns_400(self) -> None:
        response = self.client.post(
            "/api/audio",
            files={
                "audio": (
                    "pergunta.wav",
                    _build_wav(duration_seconds=61.0),
                    "audio/wav",
                )
            },
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "AUDIO_TOO_LONG"

    def test_valid_wav_upload_returns_200_with_stub_pipeline(self) -> None:
        response = self.client.post(
            "/api/audio",
            data={"conversation_id": "1f5c9a24-1c2e-4a8f-9a3e-2b6d8c0f1a77"},
            files={
                "audio": (
                    "pergunta.wav",
                    _build_wav(duration_seconds=3.0),
                    "audio/wav",
                )
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["conversation_id"] == "1f5c9a24-1c2e-4a8f-9a3e-2b6d8c0f1a77"
        assert body["pipeline_status"] == "stubbed"
        assert body["transcription"]["duration_seconds"] == pytest.approx(3.0, abs=0.05)

    def test_valid_ogg_upload_returns_200(self) -> None:
        response = self.client.post(
            "/api/audio",
            files={
                "audio": (
                    "pergunta.ogg",
                    _build_ogg_opus(granule_position=32_000),
                    "audio/ogg",
                )
            },
        )
        assert response.status_code == 200
        assert response.json()["pipeline_status"] == "stubbed"

    def test_generates_conversation_id_when_absent(self) -> None:
        response = self.client.post(
            "/api/audio",
            files={
                "audio": (
                    "pergunta.wav",
                    _build_wav(duration_seconds=1.0),
                    "audio/wav",
                )
            },
        )
        assert response.status_code == 200
        assert response.json()["conversation_id"]