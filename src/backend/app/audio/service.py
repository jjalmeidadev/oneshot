"""Orquestracao do upload de audio.

Esta task cobre apenas o recebimento e a validacao local do audio (Secao
8.7). A integracao real com o Speech-to-Text (Secao 8.8) e com o pipeline de
PLN e uma task separada (task 11 do backlog da Sprint 3, ver
docs/GestaoProjeto.md). Ate la, ``_run_stub_pipeline`` devolve uma resposta
no mesmo formato do contrato final (Secao 8.7.5), com ``pipeline_status``
igual a "stubbed" para deixar claro que o conteudo e um placeholder e nao
uma transcricao real.
"""

from __future__ import annotations

import uuid

from app.audio.schemas import (
    AudioAnswer,
    AudioIntent,
    AudioTranscription,
    AudioUploadResponse,
)
from app.audio.validation import AudioProbe, validate_audio_upload


def process_audio_upload(
    data: bytes,
    *,
    conversation_id: str | None,
) -> AudioUploadResponse:
    """Valida o audio recebido e devolve a resposta no formato do contrato.

    Levanta ``AudioValidationError`` (ou subclasse) quando o audio nao passa
    pelas checagens locais da Secao 8.7.3. Nao ha chamada de rede aqui: a
    validacao acontece toda antes de qualquer integracao externa, conforme a
    Secao 8.7.1.
    """

    probe = validate_audio_upload(data)
    return _run_stub_pipeline(probe, conversation_id=conversation_id)


def _run_stub_pipeline(
    probe: AudioProbe,
    *,
    conversation_id: str | None,
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
        answer=AudioAnswer(
            text=(
                "Audio recebido e validado. A transcricao e a resposta do "
                "agente ainda nao estao disponiveis: a integracao com o "
                "Speech-to-Text (Secao 8.8) e o pipeline de PLN sao "
                "implementados em uma task separada."
            ),
            sources=[],
        ),
        pipeline_status="stubbed",
    )