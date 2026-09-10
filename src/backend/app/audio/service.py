"""Validação e transcrição de áudio antes do pipeline comum de resposta."""

from __future__ import annotations

from app.audio import transcription
from app.audio.errors import (
    RateLimitedError,
    SttProviderFailedError,
    SttProviderUnavailableError,
)
from app.audio.schemas import AudioTranscription
from app.audio.validation import AudioProbe, validate_audio_upload

async def process_audio_upload(
    data: bytes,
    *,
    language: str = "pt-BR",
) -> AudioTranscription:
    """Valida o audio recebido e devolve a resposta no formato do contrato.

    Levanta ``AudioValidationError`` (ou subclasse) quando o audio nao passa
    pelas checagens locais da Secao 8.7.3. A validacao acontece toda antes de
    qualquer integracao externa, conforme a Secao 8.7.1.
    """

    probe = validate_audio_upload(data)
    result = await _transcribe(data, probe, language)

    return AudioTranscription(text=result.text, confidence=result.confidence, duration_seconds=result.duration_seconds)


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

