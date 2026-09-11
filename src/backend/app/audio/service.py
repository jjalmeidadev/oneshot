"""Validação e transcrição de áudio antes do pipeline comum de resposta."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from app.audio import transcription
from app.audio.errors import (
    RateLimitedError,
    SttProviderFailedError,
    SttProviderUnavailableError,
)
from app.audio.schemas import AudioTranscription
from app.audio.validation import AudioProbe, validate_audio_upload


@dataclass(frozen=True)
class AudioProcessingResult:
    transcription: AudioTranscription
    validation_ms: int
    stt_ms: int


async def process_audio_upload(
    data: bytes,
    *,
    language: str = "pt-BR",
) -> AudioProcessingResult:
    """Valida o audio recebido e devolve a resposta no formato do contrato.

    Levanta ``AudioValidationError`` (ou subclasse) quando o audio nao passa
    pelas checagens locais da Secao 8.7.3. A validacao acontece toda antes de
    qualquer integracao externa, conforme a Secao 8.7.1.
    """

    validation_started_at = perf_counter()
    probe = validate_audio_upload(data)
    validation_ms = _elapsed_ms(validation_started_at)

    stt_started_at = perf_counter()
    result = await _transcribe(data, probe, language)
    stt_ms = _elapsed_ms(stt_started_at)

    return AudioProcessingResult(
        transcription=AudioTranscription(
            text=result.text,
            confidence=result.confidence,
            duration_seconds=result.duration_seconds,
        ),
        validation_ms=validation_ms,
        stt_ms=stt_ms,
    )


async def _transcribe(
    data: bytes, probe: AudioProbe, language: str
) -> transcription.Transcription:
    """Chama o provedor e traduz as falhas dele para os codigos do contrato."""

    try:
        return await transcription.transcribe(data, probe, language)
    except transcription.SttProviderRateLimited as error:
        raise RateLimitedError() from error
    except transcription.SttProviderUnavailable as error:
        raise SttProviderUnavailableError() from error
    except transcription.SttProviderError as error:
        raise SttProviderFailedError() from error


def _elapsed_ms(started_at: float) -> int:
    return round((perf_counter() - started_at) * 1000)

