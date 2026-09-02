"""Endpoint `POST /api/audio` e o tratamento de erro previsto no RNF11.

A rota concentra a validacao descrita na Secao 8.7 do `Projeto.md`: autentica a
requisicao, aplica o limite de uma transcricao simultanea por usuario, le o
arquivo com corte no tamanho maximo, valida formato e duracao e so entao aciona
o servico de transcricao. Toda falha prevista sai como `AudioError`, convertida
no envelope unico de erro pelo handler registrado em `app.main`.
"""

import os
from hashlib import sha256
from threading import Lock
from uuid import uuid4

from fastapi import APIRouter, File, Form, Header, UploadFile

from app.audio import errors, transcription
from app.audio.schemas import (
    AudioErrorResponse,
    AudioTranscription,
    AudioUploadResponse,
)
from app.audio.validation import MAX_FILE_SIZE_BYTES, validate_audio

DEFAULT_LANGUAGE = "pt-BR"
UPLOAD_CHUNK_SIZE = 64 * 1024

ERROR_RESPONSES: dict[int | str, dict] = {
    status: {"model": AudioErrorResponse, "description": description}
    for status, description in {
        400: "Audio ausente, em formato nao suportado ou acima da duracao maxima.",
        401: "Token ausente, invalido ou expirado.",
        413: "Arquivo acima do limite de tamanho.",
        422: "Audio valido, porem sem fala reconhecivel.",
        429: "Ja existe uma transcricao em andamento para o usuario.",
        502: "Falha na chamada ao servico de transcricao.",
        503: "Servico de transcricao indisponivel.",
    }.items()
}

router = APIRouter(tags=["audio"])

_active_users: set[str] = set()
_active_users_lock = Lock()


@router.post(
    "/api/audio",
    response_model=AudioUploadResponse,
    responses=ERROR_RESPONSES,
    summary="Enviar audio para transcricao e processamento",
)
async def upload_audio(
    audio: UploadFile | None = File(default=None),
    conversation_id: str | None = Form(default=None),
    language: str | None = Form(default=None),
    authorization: str | None = Header(default=None),
) -> AudioUploadResponse:
    user_key = _authenticate(authorization)

    if audio is None or not audio.filename:
        raise errors.audio_missing()

    with _single_transcription_per_user(user_key):
        content = await _read_upload(audio)
        metadata = validate_audio(content, audio.content_type)
        result = _transcribe(content, metadata, language or DEFAULT_LANGUAGE)

    return AudioUploadResponse(
        conversation_id=conversation_id or str(uuid4()),
        interaction_id=str(uuid4()),
        transcription=AudioTranscription(
            text=result.text,
            confidence=result.confidence,
            duration_seconds=(
                result.duration_seconds
                if result.duration_seconds is not None
                else round(metadata.duration_seconds, 1)
            ),
        ),
    )


def _authenticate(authorization: str | None) -> str:
    """Valida o token da requisicao e devolve a chave que identifica o usuario.

    A autenticacao corporativa do RNF02 e simulada na prova de conceito, como
    registrado na Secao 3.2.3 do `Projeto.md`. Quando `AUDIO_API_TOKENS` esta
    definida, apenas os tokens listados sao aceitos; o cabecalho `Authorization`
    e sempre obrigatorio. O token nunca e guardado em memoria: o controle de
    simultaneidade usa apenas o seu resumo.
    """

    scheme, _, token = (authorization or "").partition(" ")
    token = token.strip()
    if scheme.lower() != "bearer" or not token:
        raise errors.unauthenticated()

    allowed = [
        item.strip()
        for item in os.getenv("AUDIO_API_TOKENS", "").split(",")
        if item.strip()
    ]
    if allowed and token not in allowed:
        raise errors.unauthenticated()

    return sha256(token.encode("utf-8")).hexdigest()


class _single_transcription_per_user:
    """Garante o limite de uma requisicao simultanea por usuario (Secao 8.7.3)."""

    def __init__(self, user_key: str) -> None:
        self._user_key = user_key

    def __enter__(self) -> "_single_transcription_per_user":
        with _active_users_lock:
            if self._user_key in _active_users:
                raise errors.rate_limited()
            _active_users.add(self._user_key)
        return self

    def __exit__(self, *_args: object) -> None:
        with _active_users_lock:
            _active_users.discard(self._user_key)


async def _read_upload(audio: UploadFile) -> bytes:
    """Le o arquivo em blocos e interrompe assim que o limite e ultrapassado.

    A leitura parcial evita carregar em memoria um arquivo que ja seria
    recusado, e o corte acontece um byte alem do limite apenas para diferenciar
    o arquivo no limite do arquivo acima dele.
    """

    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await audio.read(UPLOAD_CHUNK_SIZE)
        if not chunk:
            break
        chunks.append(chunk)
        total += len(chunk)
        if total > MAX_FILE_SIZE_BYTES:
            raise errors.audio_too_large(MAX_FILE_SIZE_BYTES)

    return b"".join(chunks)


def _transcribe(
    content: bytes, metadata, language: str
) -> transcription.Transcription:
    try:
        return transcription.transcribe(content, metadata, language)
    except transcription.SttProviderUnavailableError as error:
        raise errors.stt_provider_unavailable() from error
    except transcription.SttProviderError as error:
        raise errors.stt_provider_error() from error
