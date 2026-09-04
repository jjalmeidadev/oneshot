"""Orquestracao do upload de audio.

O fluxo cobre o recebimento, a validacao local e a transcricao via
Speech-to-Text. A classificacao de intencao e a resposta fundamentada continuam
em task separada; por isso a resposta ainda usa ``pipeline_status`` igual a
``"stubbed"`` depois de transcrever o audio.
"""

from __future__ import annotations

import uuid

from app.audio import transcription
from app.audio.errors import (
    RateLimitedError,
    SttProviderFailedError,
    SttProviderUnavailableError,
)
from app.audio.schemas import (
    AudioAnswer,
    AudioIntent,
    AudioTranscription,
    AudioUploadResponse,
)
from app.audio.validation import AudioProbe, validate_audio_upload

STUB_ANSWER_TEXT = (
    "Audio recebido, validado e transcrito. A classificacao de intencao e a "
    "resposta do agente ainda nao estao disponiveis: o pipeline de PLN e "
    "implementado em uma task separada."
)


async def process_audio_upload(
    data: bytes,
    *,
    conversation_id: str | None,
    language: str = "pt-BR",
) -> AudioUploadResponse:
    """Valida o audio recebido e devolve a resposta no formato do contrato.

    Levanta ``AudioValidationError`` (ou subclasse) quando o audio nao passa
    pelas checagens locais da Secao 8.7.3. A validacao acontece toda antes de
    qualquer integracao externa, conforme a Secao 8.7.1.
    """

    probe = validate_audio_upload(data)
    result = await _transcribe(data, probe, language)

    return _completed_response(result, conversation_id=conversation_id)


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


def _completed_response(
    result: transcription.Transcription, *, conversation_id: str | None
) -> AudioUploadResponse:
    """Resposta com transcricao real; a intencao ainda vem do pipeline stub.

    A classificacao de intencao e a resposta fundamentada continuam a cargo da
    integracao do pipeline de PLN, entao `pipeline_status` so passa a
    "completed" quando aquela task tambem estiver concluida.
    """

    return AudioUploadResponse(
        conversation_id=conversation_id or str(uuid.uuid4()),
        interaction_id=str(uuid.uuid4()),
        transcription=AudioTranscription(
            text=result.text,
            confidence=result.confidence,
            duration_seconds=result.duration_seconds,
        ),
        intent=AudioIntent(
            macro="FORA_DE_ESCOPO",
            specific="pipeline_nao_implementado",
            confidence_macro=0.0,
            confidence_specific=0.0,
        ),
        answer=AudioAnswer(text=STUB_ANSWER_TEXT, sources=[]),
        pipeline_status="stubbed",
    )
