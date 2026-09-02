"""Orquestracao do upload de audio.

Esta task cobre o recebimento, a validacao local do audio e o tratamento dos
cenarios de erro da Secao 8.7. A integracao real com o Speech-to-Text (Secao
8.8) e com o pipeline de PLN e uma task separada (task 11 do backlog da Sprint
3, ver docs/GestaoProjeto.md). Ate la, ``_stub_response`` devolve uma resposta
no mesmo formato do contrato final (Secao 8.7.5), com ``pipeline_status``
igual a "stubbed" para deixar claro que o conteudo e um placeholder e nao uma
transcricao real.
"""

from __future__ import annotations

import uuid

from app.audio import transcription
from app.audio.errors import SttProviderFailedError, SttProviderUnavailableError
from app.audio.schemas import (
    AudioAnswer,
    AudioIntent,
    AudioTranscription,
    AudioUploadResponse,
)
from app.audio.validation import AudioProbe, validate_audio_upload

STUB_ANSWER_TEXT = (
    "Audio recebido e validado. A transcricao e a resposta do agente ainda "
    "nao estao disponiveis: a integracao com o Speech-to-Text (Secao 8.8) e o "
    "pipeline de PLN sao implementados em uma task separada."
)


def process_audio_upload(
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
    result = _transcribe(data, probe, language)

    if result is None:
        return _stub_response(probe, conversation_id=conversation_id)

    return _completed_response(result, conversation_id=conversation_id)


def _transcribe(
    data: bytes, probe: AudioProbe, language: str
) -> transcription.Transcription | None:
    """Chama o provedor e traduz as falhas dele para os codigos do contrato."""

    try:
        return transcription.transcribe(data, probe, language)
    except transcription.SttProviderUnavailable as error:
        raise SttProviderUnavailableError() from error
    except transcription.SttProviderError as error:
        raise SttProviderFailedError() from error


def _stub_response(
    probe: AudioProbe, *, conversation_id: str | None
) -> AudioUploadResponse:
    """Placeholder para a integracao real da task 11.

    Nao chama nenhum provedor externo. Serve para o restante do pipeline
    (frontend, testes de contrato, persistencia) ja poder ser desenvolvido
    contra o formato final da resposta antes da integracao com o Azure AI
    Speech estar disponivel.
    """

    return AudioUploadResponse(
        conversation_id=conversation_id or str(uuid.uuid4()),
        interaction_id=str(uuid.uuid4()),
        transcription=AudioTranscription(
            text="",
            confidence=0.0,
            duration_seconds=round(probe.duration_seconds, 2),
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
