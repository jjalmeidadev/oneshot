"""Validacao local do audio recebido, antes de qualquer chamada externa.

Implementa os limites da Secao 8.7.3 de docs/Projeto.md:

* Continer/codec: WAV com PCM ou OGG com OPUS;
* Taxa de amostragem: 16 kHz;
* Canais: 1 (mono);
* Profundidade: 16 bits;
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
    NoSpeechDetectedError,
)

DEFAULT_MAX_SIZE_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_DURATION_SECONDS = 60.0
REQUIRED_SAMPLE_RATE_HZ = 16_000
REQUIRED_CHANNELS = 1
REQUIRED_BITS_PER_SAMPLE = 16
WAV_PCM_FORMAT_CODE = 1
WAV_EXTENSIBLE_FORMAT_CODE = 0xFFFE
OPUS_DECODE_RATE_HZ = 48_000

# Amplitude abaixo da qual o trecho e tratado como silencio (-60 dBFS em 16 bits).
SILENCE_AMPLITUDE_THRESHOLD = 32

# O Opus sempre decodifica a 48 kHz. O campo `input_sample_rate` do OpusHead e
# informativo (RFC 7845) e registra a taxa de captura: o MediaRecorder dos
# navegadores grava a 48 kHz e o valor 0 significa "nao declarada". Recusar
# esses casos rejeitaria toda gravacao vinda do frontend, entao o ramo Opus
# aceita as tres formas de declarar uma captura valida.
ACCEPTED_OPUS_INPUT_SAMPLE_RATES = frozenset(
    {0, REQUIRED_SAMPLE_RATE_HZ, OPUS_DECODE_RATE_HZ}
)


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
    """Valida tamanho, continer/codec, taxa, canais, profundidade e duracao.

    A ordem acompanha a tabela de codigos da Secao 8.7.6: tamanho (413),
    formato (400), duracao (400) e, por ultimo, ausencia de fala (422).
    Levanta uma subclasse de ``AudioValidationError`` no primeiro problema
    encontrado e retorna um ``AudioProbe`` quando o arquivo esta dentro de
    todos os limites do endpoint de audio curto.
    """

    if len(data) > max_size_bytes:
        raise AudioTooLargeError(max_size_bytes)

    if data[:4] == b"RIFF" and data[8:12] == b"WAVE":
        probe = _probe_wav(data)
    elif data[:4] == b"OggS":
        probe = _probe_ogg(data)
    else:
        raise AudioFormatUnsupportedError(detail=_received_detail(data))

    if probe.duration_seconds > max_duration_seconds:
        raise AudioTooLongError(probe.duration_seconds, max_duration_seconds)

    _reject_silence(data, probe)

    return probe


def _received_detail(data: bytes) -> dict[str, object]:
    """Descreve o que chegou usando apenas tipos de midia conhecidos do usuario.

    O RNF11 nao admite vocabulario interno de formato na resposta, entao o
    `detail` se limita ao tipo de midia identificado pela assinatura do
    arquivo, ou a `desconhecido` quando ela nao corresponde a nada previsto.
    """

    if data[:3] == b"ID3" or data[:2] == b"\xff\xfb":
        return {"received": "audio/mpeg"}
    if data[:4] == b"fLaC":
        return {"received": "audio/flac"}
    if data[:4] == b"RIFF":
        return {"received": "audio/wav"}
    if data[:4] == b"OggS":
        return {"received": "audio/ogg"}
    return {"received": "desconhecido"}


def _reject_unsupported_encoding(
    *,
    container_media_type: str,
    is_expected_codec: bool,
    sample_rate_accepted: bool,
    sample_rate_hz: int,
    channels: int,
    bits_per_sample: int,
) -> None:
    """Recusa o arquivo cuja codificacao esta fora do contrato da Secao 8.7.3.

    Quando o codec em si nao e o previsto, o `detail` se limita ao tipo de
    midia: a codificacao interna do contenor nao diz nada a quem gravou o
    audio. Quando o codec esta certo e o problema e a captura, o `detail`
    informa taxa e canais recebidos ao lado dos esperados, que e o que permite
    regravar corretamente.
    """

    if not is_expected_codec:
        raise AudioFormatUnsupportedError(detail={"received": container_media_type})

    if (
        sample_rate_accepted
        and channels == REQUIRED_CHANNELS
        and bits_per_sample == REQUIRED_BITS_PER_SAMPLE
    ):
        return

    raise AudioFormatUnsupportedError(
        detail={
            "sample_rate_hz": sample_rate_hz,
            "channels": channels,
            "bits_per_sample": bits_per_sample,
            "expected_sample_rate_hz": REQUIRED_SAMPLE_RATE_HZ,
            "expected_channels": REQUIRED_CHANNELS,
            "expected_bits_per_sample": REQUIRED_BITS_PER_SAMPLE,
        }
    )


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

            # WAVE_FORMAT_EXTENSIBLE e como o Windows e boa parte dos gravadores
            # escrevem PCM; o formato real fica no sub-formato do chunk estendido.
            if (
                audio_format == WAV_EXTENSIBLE_FORMAT_CODE
                and chunk_size >= 40
                and chunk_start + 26 <= len(data)
            ):
                (audio_format,) = struct.unpack_from("<H", data, chunk_start + 24)
        elif chunk_id == b"data":
            data_size = min(chunk_size, len(data) - chunk_start)

        offset = chunk_start + chunk_size + (chunk_size % 2)

    if None in (audio_format, channels, sample_rate, bits_per_sample, data_size):
        raise AudioFormatUnsupportedError(detail={"received": "audio/wav"})

    _reject_unsupported_encoding(
        container_media_type="audio/wav",
        is_expected_codec=audio_format == WAV_PCM_FORMAT_CODE,
        sample_rate_accepted=sample_rate == REQUIRED_SAMPLE_RATE_HZ,
        sample_rate_hz=sample_rate,
        channels=channels,
        bits_per_sample=bits_per_sample,
    )

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
    pre_skip = 0
    last_granule_position = 0

    offset = 0
    while True:
        page_start = data.find(b"OggS", offset)
        if page_start == -1 or page_start + 27 > len(data):
            break

        (granule_position,) = struct.unpack_from("<q", data, page_start + 6)
        segment_count = data[page_start + 26]
        segment_table_start = page_start + 27
        segment_table_end = segment_table_start + segment_count
        if segment_table_end > len(data):
            break

        payload_size = sum(data[segment_table_start:segment_table_end])
        payload_start = segment_table_end
        payload = data[payload_start : payload_start + payload_size]

        if channels is None and payload[:8] == b"OpusHead":
            # OpusHead: magic(8) + version(1) + channels(1) + pre_skip(2)
            # + input_sample_rate(4) + ...
            if len(payload) >= 16:
                channels = payload[9]
                (pre_skip,) = struct.unpack_from("<H", payload, 10)
                (input_sample_rate,) = struct.unpack_from("<I", payload, 12)

        if granule_position >= 0:
            last_granule_position = max(last_granule_position, granule_position)

        offset = payload_start + payload_size

    if channels is None or input_sample_rate is None:
        raise AudioFormatUnsupportedError(detail={"received": "audio/ogg"})

    _reject_unsupported_encoding(
        container_media_type="audio/ogg",
        is_expected_codec=True,
        sample_rate_accepted=input_sample_rate in ACCEPTED_OPUS_INPUT_SAMPLE_RATES,
        sample_rate_hz=input_sample_rate,
        channels=channels,
        # O Opus nao expoe profundidade de bits: e um codec com perdas cuja
        # saida e reconstruida na profundidade pedida pelo decodificador.
        bits_per_sample=REQUIRED_BITS_PER_SAMPLE,
    )

    # O `pre_skip` conta amostras que o decodificador descarta no inicio do
    # fluxo; elas nao fazem parte da gravacao (RFC 7845).
    samples = max(last_granule_position - pre_skip, 0)

    return AudioProbe(
        container="ogg",
        codec="opus",
        sample_rate_hz=input_sample_rate,
        channels=channels,
        duration_seconds=samples / OPUS_DECODE_RATE_HZ,
        size_bytes=len(data),
    )


def _reject_silence(data: bytes, probe: AudioProbe) -> None:
    """Recusa gravacoes vazias ou sem sinal audivel.

    A ausencia de fala tambem e identificada pelo provedor de transcricao, mas
    o arquivo sem sinal algum pode ser recusado aqui, evitando a chamada
    externa. Para Opus a verificacao se limita a duracao, porque medir
    amplitude exigiria decodificar o fluxo.
    """

    if probe.duration_seconds <= 0:
        raise NoSpeechDetectedError()

    if probe.codec != "pcm":
        return

    samples = _pcm_samples(data)
    if samples is None:
        return

    if max((abs(sample) for sample in samples), default=0) < SILENCE_AMPLITUDE_THRESHOLD:
        raise NoSpeechDetectedError()


def _find_data_chunk(data: bytes) -> tuple[int, int] | None:
    """Localiza o chunk 'data' percorrendo os chunks RIFF.

    Procurar a sequencia b"data" com `find` acharia tambem uma ocorrencia
    dentro do texto de um chunk LIST/INFO; por isso a busca acompanha a
    estrutura do arquivo, como em ``_probe_wav``.
    """

    offset = 12
    while offset + 8 <= len(data):
        chunk_id = data[offset : offset + 4]
        (chunk_size,) = struct.unpack_from("<I", data, offset + 4)
        chunk_start = offset + 8

        if chunk_id == b"data":
            return chunk_start, min(chunk_size, len(data) - chunk_start)

        offset = chunk_start + chunk_size + (chunk_size % 2)

    return None


def _pcm_samples(data: bytes) -> tuple[int, ...] | None:
    chunk = _find_data_chunk(data)
    if chunk is None:
        return None

    body_start, size = chunk
    usable = size - (size % 2)
    if usable <= 0:
        return ()

    return struct.unpack_from(f"<{usable // 2}h", data, body_start)
