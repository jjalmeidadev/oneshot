"""Orquestracao do upload de audio."""

from __future__ import annotations

import uuid
from time import perf_counter

from app.audio import transcription
from app.audio.errors import (
    RateLimitedError,
    SttProviderFailedError,
    SttProviderUnavailableError,
)
from app.audio.schemas import (
    AudioAnswer,
    AudioEntity,
    AudioIntent,
    AudioPipelineMetrics,
    AudioTranscription,
    AudioUploadResponse,
)
from app.audio.validation import AudioProbe, validate_audio_upload
from app.nlp.entities import Entidade
from app.nlp.inference import Classificacao
from app.nlp.pipeline import NlpPipelineResult, process_text_pipeline

GENERIC_AUDIO_ANSWER_TEXT = (
    "Audio transcrito e classificado. A solicitacao foi encaminhada para o "
    "fluxo correspondente do portfolio."
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

    total_started_at = perf_counter()
    validation_started_at = perf_counter()
    probe = validate_audio_upload(data)
    validation_ms = _elapsed_ms(validation_started_at)

    stt_started_at = perf_counter()
    result = await _transcribe(data, probe, language)
    stt_ms = _elapsed_ms(stt_started_at)

    pipeline = process_text_pipeline(result.text)

    elapsed_total_ms = _elapsed_ms(total_started_at)
    measured_total_ms = validation_ms + stt_ms + pipeline.nlp_ms

    return _completed_response(
        result,
        pipeline=pipeline,
        conversation_id=conversation_id,
        metrics=AudioPipelineMetrics(
            validation_ms=validation_ms,
            stt_ms=stt_ms,
            nlp_ms=pipeline.nlp_ms,
            total_ms=max(elapsed_total_ms, measured_total_ms),
        ),
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


def _completed_response(
    result: transcription.Transcription,
    *,
    pipeline: NlpPipelineResult,
    conversation_id: str | None,
    metrics: AudioPipelineMetrics,
) -> AudioUploadResponse:
    """Resposta com transcricao real e classificacao do pipeline de PLN."""

    return AudioUploadResponse(
        conversation_id=conversation_id or str(uuid.uuid4()),
        interaction_id=str(uuid.uuid4()),
        transcription=AudioTranscription(
            text=result.text,
            confidence=result.confidence,
            duration_seconds=result.duration_seconds,
        ),
        intent=_serialize_intent(pipeline.classification),
        entities=_serialize_entities(pipeline.entities),
        answer=AudioAnswer(
            text=pipeline.controlled_answer or GENERIC_AUDIO_ANSWER_TEXT,
            sources=[],
        ),
        pipeline_status="completed",
        pipeline_metrics=metrics,
    )


def _serialize_intent(classification: Classificacao) -> AudioIntent:
    return AudioIntent(
        macro=classification.macrointencao,
        specific=classification.intencao or "",
        confidence_macro=classification.confianca_macro,
        confidence_specific=classification.confianca_intencao,
        flow=classification.fluxo,
        handler=classification.handler,
        alternatives=[
            {"intent": intent, "confidence": confidence}
            for intent, confidence in classification.alternativas
        ],
    )


def _serialize_entities(entities: list[Entidade]) -> list[AudioEntity]:
    return [
        AudioEntity(
            type=entity.tipo,
            value=entity.valor,
            text=entity.texto,
            start=entity.inicio,
            end=entity.fim,
            types=list(entity.tipos),
            ambiguous=entity.ambigua,
        )
        for entity in entities
    ]


def _elapsed_ms(started_at: float) -> int:
    return round((perf_counter() - started_at) * 1000)
