"""Validacao local do audio recebido, antes de qualquer chamada externa.

Implementa os limites da Secao 8.7.3 de docs/Projeto.md:

* Continer/codec: WAV com PCM ou OGG com OPUS;
* Taxa de amostragem: 16 kHz;
* Canais: 1 (mono);
* Duracao maxima: 60 segundos;
* Tamanho maximo do arquivo: 2 MB.

Nao ha dependencia de bibliotecas externas de audio: os cabecalhos WAV e OGG
sao lidos diretamente, o que mantem a validacao rapida e sem custo de rede,
por ser a barreira que evita gastar a franquia do provedor de STT (Secao
8.7.1) com um arquivo que ja seria rejeitado localmente.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

from app.audio.errors import (
    AudioFormatUnsupportedError,
    AudioTooLargeError,
    AudioTooLongError,
)

DEFAULT_MAX_SIZE_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_DURATION_SECONDS = 60.0
REQUIRED_SAMPLE_RATE_HZ = 16_000
REQUIRED_CHANNELS = 1
WAV_PCM_FORMAT_CODE = 1
OPUS_DECODE_RATE_HZ = 48_000


@dataclass(frozen=True)
class AudioProbe:
    """Metadados extraidos do audio apos validacao local bem-sucedida."""

    container: str
    codec: str
    sample_rate_hz: int
    channels: int
    duration_seconds: float
    size_bytes: int


def validate_audio_upload(
    data: bytes,
    *,
    max_size_bytes: int = DEFAULT_MAX_SIZE_BYTES,
    max_duration_seconds: float = DEFAULT_MAX_DURATION_SECONDS,
) -> AudioProbe:
    """Valida tamanho, continer/codec, taxa de amostragem, canais e duracao.

    Levanta uma subclasse de ``AudioValidationError`` no primeiro problema
    encontrado. Retorna um ``AudioProbe`` quando o arquivo esta dentro de
    todos os limites do endpoint de audio curto (Secao 8.7.3).
    """

    size_bytes = len(data)
    if size_bytes > max_size_bytes:
        raise AudioTooLargeError(size_bytes, max_size_bytes)

    if data[:4] == b"RIFF" and data[8:12] == b"WAVE":
        probe = _probe_wav(data)
    elif data[:4] == b"OggS":
        probe = _probe_ogg(data)
    else:
        raise AudioFormatUnsupportedError(received=_guess_received_label(data))

    if probe.sample_rate_hz != REQUIRED_SAMPLE_RATE_HZ or probe.channels != REQUIRED_CHANNELS:
        raise AudioFormatUnsupportedError(
            received=(
                f"{probe.container}/{probe.codec} "
                f"{probe.sample_rate_hz}Hz {probe.channels}ch"
            )
        )

    if probe.duration_seconds > max_duration_seconds:
        raise AudioTooLongError(probe.duration_seconds, max_duration_seconds)

    return probe


def _guess_received_label(data: bytes) -> str:
    if data[:3] == b"ID3" or data[:2] == b"\xff\xfb":
        return "audio/mpeg"
    if data[:4] == b"fLaC":
        return "audio/flac"
    if not data:
        return "empty"
    return "unknown"


def _probe_wav(data: bytes) -> AudioProbe:
    """Le os chunks 'fmt ' e 'data' de um arquivo WAV (RIFF)."""

    audio_format: int | None = None
    channels: int | None = None
    sample_rate: int | None = None
    bits_per_sample: int | None = None
    data_size: int | None = None

    offset = 12  # apos "RIFF" + tamanho (4) + "WAVE"
    while offset + 8 <= len(data):
        chunk_id = data[offset : offset + 4]
        (chunk_size,) = struct.unpack_from("<I", data, offset + 4)
        chunk_start = offset + 8

        if chunk_id == b"fmt " and chunk_start + 16 <= len(data):
            (
                audio_format,
                channels,
                sample_rate,
                _byte_rate,
                _block_align,
                bits_per_sample,
            ) = struct.unpack_from("<HHIIHH", data, chunk_start)
        elif chunk_id == b"data":
            data_size = min(chunk_size, len(data) - chunk_start)

        offset = chunk_start + chunk_size + (chunk_size % 2)

    if None in (audio_format, channels, sample_rate, bits_per_sample, data_size):
        raise AudioFormatUnsupportedError(received="audio/wav (cabecalho incompleto)")

    if audio_format != WAV_PCM_FORMAT_CODE:
        raise AudioFormatUnsupportedError(received=f"wav format-code={audio_format}")

    bytes_per_second = sample_rate * channels * (bits_per_sample / 8)
    duration_seconds = (data_size / bytes_per_second) if bytes_per_second else 0.0

    return AudioProbe(
        container="wav",
        codec="pcm",
        sample_rate_hz=sample_rate,
        channels=channels,
        duration_seconds=duration_seconds,
        size_bytes=len(data),
    )


def _probe_ogg(data: bytes) -> AudioProbe:
    """Le o pacote 'OpusHead' e as posicoes de granulo das paginas OGG."""

    channels: int | None = None
    input_sample_rate: int | None = None
    last_granule_position = 0

    offset = 0
    while True:
        page_start = data.find(b"OggS", offset)
        if page_start == -1:
            break
        if page_start + 27 > len(data):
            break

        (granule_position,) = struct.unpack_from("<q", data, page_start + 6)
        segment_count = data[page_start + 26]
        segment_table_start = page_start + 27
        segment_table_end = segment_table_start + segment_count
        if segment_table_end > len(data):
            break

        segment_table = data[segment_table_start:segment_table_end]
        payload_size = sum(segment_table)
        payload_start = segment_table_end
        payload = data[payload_start : payload_start + payload_size]

        if channels is None and payload[:8] == b"OpusHead":
            # OpusHead: magic(8) + version(1) + channels(1) + pre_skip(2)
            # + input_sample_rate(4) + ...
            if len(payload) >= 16:
                channels = payload[9]
                (input_sample_rate,) = struct.unpack_from("<I", payload, 12)

        if granule_position >= 0:
            last_granule_position = max(last_granule_position, granule_position)

        offset = payload_start + payload_size

    if channels is None or input_sample_rate is None:
        raise AudioFormatUnsupportedError(received="ogg (sem fluxo OpusHead)")

    duration_seconds = last_granule_position / OPUS_DECODE_RATE_HZ

    return AudioProbe(
        container="ogg",
        codec="opus",
        sample_rate_hz=input_sample_rate,
        channels=channels,
        duration_seconds=duration_seconds,
        size_bytes=len(data),
    )