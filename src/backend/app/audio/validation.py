"""Validacao local do audio recebido pela API.

Os limites implementados aqui sao os declarados na Secao 8.7.3 do `Projeto.md`
e derivam do endpoint de audio curto do provedor de Speech-to-Text escolhido na
Secao 8.8. A validacao acontece antes de qualquer chamada externa: cada arquivo
recusado localmente e uma requisicao que nao consome a franquia do provedor nem
expoe conteudo a servico de terceiro.

O modulo nao depende do FastAPI. Ele recebe bytes e devolve os metadados do
audio ou levanta um `AudioError`, o que permite exercita-lo em teste sem subir a
aplicacao.
"""

import struct
from dataclasses import dataclass

from app.audio import errors

MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024
MAX_DURATION_SECONDS = 60
REQUIRED_SAMPLE_RATE_HZ = 16_000
REQUIRED_CHANNELS = 1
REQUIRED_BITS_PER_SAMPLE = 16

# Amplitude abaixo da qual o trecho e tratado como silencio (-60 dBFS em 16 bits).
SILENCE_AMPLITUDE_THRESHOLD = 32

# O Opus sempre decodifica a 48 kHz; a posicao granular das paginas Ogg e contada
# nessa taxa, independentemente da taxa de captura declarada no cabecalho.
OPUS_GRANULE_RATE_HZ = 48_000

WAVE_FORMAT_PCM = 0x0001
WAVE_FORMAT_EXTENSIBLE = 0xFFFE

FORMAT_REQUIREMENT_MESSAGE = (
    "Formato de audio nao suportado. Envie WAV/PCM ou OGG/OPUS a 16 kHz, mono."
)


@dataclass(frozen=True)
class AudioMetadata:
    """Caracteristicas extraidas do arquivo aprovado na validacao."""

    container: str
    codec: str
    sample_rate_hz: int
    channels: int
    duration_seconds: float
    size_bytes: int


def validate_audio(content: bytes, content_type: str | None = None) -> AudioMetadata:
    """Valida formato, taxa, canais, duracao e presenca de fala.

    A ordem das verificacoes acompanha a tabela de codigos da Secao 8.7.6:
    tamanho (413), formato (400), duracao (400) e, por ultimo, ausencia de fala
    (422). O `content_type` declarado pelo cliente e usado apenas para compor o
    `detail` da resposta, porque o conteudo real do arquivo e a unica fonte
    confiavel de formato.
    """

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise errors.audio_too_large(MAX_FILE_SIZE_BYTES)

    if not content:
        raise errors.audio_missing()

    metadata = _parse_metadata(content, content_type)

    if metadata.duration_seconds > MAX_DURATION_SECONDS:
        raise errors.audio_too_long(metadata.duration_seconds, MAX_DURATION_SECONDS)

    _reject_silence(content, metadata)

    return metadata


def _parse_metadata(content: bytes, content_type: str | None) -> AudioMetadata:
    if content.startswith(b"RIFF"):
        return _parse_wav(content)
    if content.startswith(b"OggS"):
        return _parse_ogg_opus(content)

    raise errors.audio_format_unsupported(
        FORMAT_REQUIREMENT_MESSAGE,
        detail=_received_detail(content_type),
    )


def _received_detail(content_type: str | None) -> dict[str, object] | None:
    if not content_type:
        return None
    return {"received": content_type}


def _parse_wav(content: bytes) -> AudioMetadata:
    if len(content) < 12 or content[8:12] != b"WAVE":
        raise errors.audio_format_unsupported(FORMAT_REQUIREMENT_MESSAGE)

    format_chunk: bytes | None = None
    data_size: int | None = None

    offset = 12
    while offset + 8 <= len(content):
        chunk_id = content[offset : offset + 4]
        (chunk_size,) = struct.unpack_from("<I", content, offset + 4)
        body_start = offset + 8

        if chunk_id == b"fmt ":
            format_chunk = content[body_start : body_start + chunk_size]
        elif chunk_id == b"data":
            # Alguns gravadores escrevem o tamanho declarado maior que o
            # conteudo efetivamente presente; a duracao usa o que existe.
            data_size = min(chunk_size, len(content) - body_start)
            break

        offset = body_start + chunk_size + (chunk_size % 2)

    if format_chunk is None or len(format_chunk) < 16 or data_size is None:
        raise errors.audio_format_unsupported(FORMAT_REQUIREMENT_MESSAGE)

    audio_format, channels, sample_rate, byte_rate, _block_align, bits_per_sample = (
        struct.unpack_from("<HHIIHH", format_chunk, 0)
    )

    if audio_format == WAVE_FORMAT_EXTENSIBLE and len(format_chunk) >= 40:
        (audio_format,) = struct.unpack_from("<H", format_chunk, 24)

    _reject_unsupported_encoding(
        is_expected_codec=audio_format == WAVE_FORMAT_PCM,
        sample_rate=sample_rate,
        channels=channels,
        bits_per_sample=bits_per_sample,
    )

    duration_seconds = data_size / byte_rate if byte_rate else 0.0

    return AudioMetadata(
        container="WAV",
        codec="PCM",
        sample_rate_hz=sample_rate,
        channels=channels,
        duration_seconds=duration_seconds,
        size_bytes=len(content),
    )


def _parse_ogg_opus(content: bytes) -> AudioMetadata:
    pages = list(_iter_ogg_pages(content))
    if not pages:
        raise errors.audio_format_unsupported(FORMAT_REQUIREMENT_MESSAGE)

    first_body = pages[0][1]
    if not first_body.startswith(b"OpusHead") or len(first_body) < 19:
        raise errors.audio_format_unsupported(
            FORMAT_REQUIREMENT_MESSAGE, detail={"received": "audio/ogg"}
        )

    channels = first_body[9]
    (pre_skip,) = struct.unpack_from("<H", first_body, 10)
    (input_sample_rate,) = struct.unpack_from("<I", first_body, 12)

    # O RFC 7845 permite declarar 0 quando a taxa original nao e conhecida pelo
    # codificador; nesse caso a taxa nao e usada para recusar o arquivo.
    sample_rate_declared = input_sample_rate or REQUIRED_SAMPLE_RATE_HZ

    _reject_unsupported_encoding(
        is_expected_codec=True,
        sample_rate=sample_rate_declared,
        channels=channels,
        bits_per_sample=REQUIRED_BITS_PER_SAMPLE,
    )

    last_granule = pages[-1][0]
    samples = max(last_granule - pre_skip, 0)
    duration_seconds = samples / OPUS_GRANULE_RATE_HZ

    return AudioMetadata(
        container="OGG",
        codec="OPUS",
        sample_rate_hz=input_sample_rate or REQUIRED_SAMPLE_RATE_HZ,
        channels=channels,
        duration_seconds=duration_seconds,
        size_bytes=len(content),
    )


def _iter_ogg_pages(content: bytes):
    """Percorre as paginas Ogg devolvendo posicao granular e corpo de cada uma."""

    offset = 0
    while offset + 27 <= len(content):
        if content[offset : offset + 4] != b"OggS":
            break

        (granule_position,) = struct.unpack_from("<q", content, offset + 6)
        segment_count = content[offset + 26]
        table_start = offset + 27
        table_end = table_start + segment_count
        if table_end > len(content):
            break

        body_size = sum(content[table_start:table_end])
        body_start = table_end
        body_end = body_start + body_size
        if body_end > len(content):
            break

        yield granule_position, content[body_start:body_end]
        offset = body_end


def _reject_unsupported_encoding(
    *,
    is_expected_codec: bool,
    sample_rate: int,
    channels: int,
    bits_per_sample: int,
) -> None:
    if (
        is_expected_codec
        and sample_rate == REQUIRED_SAMPLE_RATE_HZ
        and channels == REQUIRED_CHANNELS
        and bits_per_sample == REQUIRED_BITS_PER_SAMPLE
    ):
        return

    raise errors.audio_format_unsupported(
        FORMAT_REQUIREMENT_MESSAGE,
        detail={
            "sample_rate_hz": sample_rate,
            "channels": channels,
            "expected_sample_rate_hz": REQUIRED_SAMPLE_RATE_HZ,
            "expected_channels": REQUIRED_CHANNELS,
        },
    )


def _reject_silence(content: bytes, metadata: AudioMetadata) -> None:
    """Recusa gravacoes vazias ou sem sinal audivel.

    A ausencia de fala tambem pode ser identificada pelo provedor de
    transcricao; esta verificacao cobre o caso em que o arquivo sequer contem
    sinal, evitando a chamada externa.
    """

    if metadata.duration_seconds <= 0:
        raise errors.no_speech_detected()

    if metadata.codec != "PCM":
        return

    samples = _pcm_samples(content)
    if samples is None:
        return

    if max((abs(sample) for sample in samples), default=0) < SILENCE_AMPLITUDE_THRESHOLD:
        raise errors.no_speech_detected()


def _pcm_samples(content: bytes) -> tuple[int, ...] | None:
    marker = content.find(b"data", 12)
    if marker == -1:
        return None

    (declared_size,) = struct.unpack_from("<I", content, marker + 4)
    body_start = marker + 8
    size = min(declared_size, len(content) - body_start)
    usable = size - (size % 2)
    if usable <= 0:
        return ()

    return struct.unpack_from(f"<{usable // 2}h", content, body_start)
