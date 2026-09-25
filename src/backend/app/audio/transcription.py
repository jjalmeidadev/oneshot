"""Fronteira entre a API de audio e o servico de Speech-to-Text.

O endpoint de upload valida o arquivo antes de chegar aqui. Este modulo fica
responsavel apenas por chamar o provedor STT escolhido na Secao 8.8 de
docs/Projeto.md e traduzir a resposta para o contrato interno da aplicacao.

A chamada e assincrona por necessidade, nao por estilo. A rota de audio e
`async def`, e um cliente HTTP sincrono dentro dela bloquearia o laco de
eventos: enquanto o Azure nao respondesse, nenhuma outra requisicao seria
atendida — nem `/health`, nem `/api/chat`, nem outro upload.
"""

from __future__ import annotations

import asyncio
import os
import json
from hashlib import sha256
from dataclasses import dataclass
from urllib.parse import urlencode, urlparse
from uuid import uuid4

import httpx

from app.audio.errors import NoSpeechDetectedError
from app.audio.validation import AudioProbe
from app.audio.vhs import ResponseCache

AZURE_SPEECH_RESOURCE_ENV = "AZURE_SPEECH_RESOURCE"
AZURE_SPEECH_ENDPOINT_ENV = "AZURE_SPEECH_ENDPOINT"
AZURE_SPEECH_KEY_ENV = "AZURE_SPEECH_KEY"
AZURE_SPEECH_TIMEOUT_ENV = "AZURE_SPEECH_TIMEOUT_SECONDS"
AZURE_SPEECH_ATTEMPTS_ENV = "AZURE_SPEECH_MAX_ATTEMPTS"
DEFAULT_LANGUAGE = "pt-BR"

# O RNF05 da 10 segundos para uma consulta simples ponta a ponta, e a
# transcricao e apenas a primeira etapa. O limite abaixo, somado a uma
# retentativa curta, mantem o pior caso dentro do orcamento.
DEFAULT_TIMEOUT_SECONDS = 6.0
DEFAULT_MAX_ATTEMPTS = 2
RETRY_DELAY_SECONDS = 0.5

# Estados transitorios do provedor: uma nova tentativa pode ter sucesso.
TRANSIENT_STATUS_CODES = frozenset({408, 500, 502, 503, 504})

# Franquia ou concorrencia excedida. A Secao 8.7.6 reserva o 429 para este
# caso, com mensagem propria: o servico esta no ar, so pediu para esperar.
RATE_LIMIT_STATUS_CODE = 429

# O provedor devolve 200 com um estado de reconhecimento no corpo. `NoMatch` e
# os tempos de silencio significam audio sem fala aproveitavel; `Error` e falha
# do proprio servico e nao deve pedir ao usuario que grave de novo.
NO_SPEECH_STATUSES = frozenset(
    {"NoMatch", "InitialSilenceTimeout", "BabbleTimeout", "EndOfDictation"}
)
PROVIDER_FAILURE_STATUSES = frozenset({"Error"})


class SttProviderError(RuntimeError):
    """Falha na chamada ao servico de transcricao; vira 502 na resposta."""


class SttProviderUnavailable(RuntimeError):
    """Servico de transcricao fora do ar; vira 503 na resposta."""


class SttProviderRateLimited(RuntimeError):
    """Franquia ou concorrencia do provedor excedida; vira 429 na resposta."""


@dataclass(frozen=True)
class Transcription:
    text: str
    confidence: float
    duration_seconds: float


response_cache: ResponseCache[Transcription] = ResponseCache()
VHS_WORKER_ID = uuid4().hex


async def transcribe(
    data: bytes, probe: AudioProbe, language: str = DEFAULT_LANGUAGE
) -> Transcription:
    """Reproduz somente transcricoes validas; VHS_ENABLED=0 desativa o cache."""
    if os.getenv("VHS_ENABLED", "1").strip() == "0":
        return await _transcribe_provider(data, probe, language)
    endpoint = os.getenv(AZURE_SPEECH_ENDPOINT_ENV, "").strip()
    resource = os.getenv(AZURE_SPEECH_RESOURCE_ENV, "").strip()
    credential = os.getenv(AZURE_SPEECH_KEY_ENV, "").strip()
    if not (endpoint or resource) or not credential:
        raise SttProviderUnavailable("Azure Speech nao configurado.")
    # O digest isola recursos e rotacoes de credencial sem guardar o segredo.
    context = json.dumps([
        "azure-stt-v1", _azure_stt_url(endpoint=endpoint, resource=resource,
                                       language=language),
        _content_type(probe), probe.duration_seconds, credential,
    ], ensure_ascii=True).encode()
    cache_key = sha256(context + b"\0" + data).hexdigest()
    return await response_cache.get_or_record(
        cache_key, lambda: _transcribe_provider(data, probe, language)
    )


async def _transcribe_provider(
    data: bytes, probe: AudioProbe, language: str = DEFAULT_LANGUAGE
) -> Transcription:
    """Transcreve o audio validado com Azure AI Speech.

    Falhas tecnicas sao agrupadas em ``SttProviderError``,
    ``SttProviderUnavailable`` ou ``SttProviderRateLimited`` para preservar o
    envelope de erro da rota. Audio valido, mas sem fala reconhecida pelo
    provedor, vira ``NoSpeechDetectedError``.
    """

    endpoint = os.getenv(AZURE_SPEECH_ENDPOINT_ENV, "").strip()
    resource = os.getenv(AZURE_SPEECH_RESOURCE_ENV, "").strip()
    key = os.getenv(AZURE_SPEECH_KEY_ENV, "").strip()
    if not (endpoint or resource) or not key:
        raise SttProviderUnavailable("Azure Speech nao configurado.")

    response = await _post_with_retry(
        url=_azure_stt_url(endpoint=endpoint, resource=resource, language=language),
        data=data,
        headers={
            "Accept": "application/json",
            "Content-Type": _content_type(probe),
            "Ocp-Apim-Subscription-Key": key,
        },
    )

    try:
        payload = response.json()
    except ValueError as error:
        raise SttProviderError("Azure Speech retornou JSON invalido.") from error
    if not isinstance(payload, dict):
        raise SttProviderError("Azure Speech retornou resposta invalida.")

    text, confidence = _extract_transcription(payload)
    if not text:
        raise NoSpeechDetectedError()

    return Transcription(
        text=text,
        confidence=confidence,
        duration_seconds=round(probe.duration_seconds, 2),
    )


async def _post_with_retry(
    *, url: str, data: bytes, headers: dict[str, str]
) -> httpx.Response:
    """Envia o audio, repetindo apenas o que pode melhorar numa nova tentativa.

    Erro permanente e limite de franquia nao sao repetidos: o primeiro nao
    mudaria de resultado e o segundo so pioraria a situacao no provedor.
    """

    tentativas = _max_attempts()
    ultimo_erro: Exception | None = None

    # O cliente vive fora do laco para que a retentativa reaproveite a conexao
    # ja estabelecida, em vez de repetir o handshake TLS. O compartilhamento
    # entre requisicoes diferentes exigiria fecha-lo no encerramento da
    # aplicacao, e cabe ao ciclo de vida do FastAPI.
    async with httpx.AsyncClient(timeout=_timeout_seconds()) as client:
        for tentativa in range(1, tentativas + 1):
            try:
                response = await client.post(url, content=data, headers=headers)
            except httpx.TimeoutException as error:
                ultimo_erro = SttProviderUnavailable("Timeout ao chamar Azure Speech.")
                ultimo_erro.__cause__ = error
            except httpx.HTTPError as error:
                ultimo_erro = SttProviderUnavailable(
                    "Falha de conexao com Azure Speech."
                )
                ultimo_erro.__cause__ = error
            else:
                if response.status_code == RATE_LIMIT_STATUS_CODE:
                    raise SttProviderRateLimited("Franquia do Azure Speech excedida.")
                if response.status_code in TRANSIENT_STATUS_CODES:
                    ultimo_erro = SttProviderUnavailable("Azure Speech indisponivel.")
                elif response.status_code >= 400:
                    raise SttProviderError("Azure Speech recusou a requisicao.")
                else:
                    return response

            if tentativa < tentativas:
                await asyncio.sleep(RETRY_DELAY_SECONDS)

    raise ultimo_erro if ultimo_erro else SttProviderUnavailable(
        "Azure Speech indisponivel."
    )


def _azure_stt_url(*, endpoint: str, resource: str, language: str) -> str:
    query = urlencode(
        {
            "language": language or DEFAULT_LANGUAGE,
            "format": "detailed",
            "profanity": "masked",
        }
    )
    base_url, path_prefix = _azure_stt_base(endpoint=endpoint, resource=resource)
    return (
        f"{base_url}{path_prefix}/speech/recognition/conversation/"
        f"cognitiveservices/v1?{query}"
    )


def _azure_stt_base(*, endpoint: str, resource: str) -> tuple[str, str]:
    if not endpoint:
        return f"https://{resource}.cognitiveservices.azure.com", "/stt"

    parsed = urlparse(endpoint)
    scheme = parsed.scheme or "https"
    host = parsed.netloc or parsed.path.split("/", 1)[0]
    normalized = f"{scheme}://{host}".rstrip("/")

    if host.endswith(".api.cognitive.microsoft.com"):
        region = host.removesuffix(".api.cognitive.microsoft.com")
        return f"{scheme}://{region}.stt.speech.microsoft.com", ""
    if host.endswith(".stt.speech.microsoft.com"):
        return normalized, ""

    return normalized, "/stt"


def _content_type(probe: AudioProbe) -> str:
    if probe.container == "ogg" and probe.codec == "opus":
        return "audio/ogg; codecs=opus"
    return "audio/wav; codecs=audio/pcm; samplerate=16000"


def _timeout_seconds() -> float:
    raw_value = os.getenv(AZURE_SPEECH_TIMEOUT_ENV, str(DEFAULT_TIMEOUT_SECONDS))
    try:
        return min(max(float(raw_value), 1.0), 120.0)
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS


def _max_attempts() -> int:
    raw_value = os.getenv(AZURE_SPEECH_ATTEMPTS_ENV, str(DEFAULT_MAX_ATTEMPTS))
    try:
        return min(max(int(raw_value), 1), 5)
    except ValueError:
        return DEFAULT_MAX_ATTEMPTS


def _extract_transcription(payload: dict) -> tuple[str, float]:
    estado = payload.get("RecognitionStatus")
    if estado in PROVIDER_FAILURE_STATUSES:
        raise SttProviderError("Azure Speech relatou falha no reconhecimento.")
    if estado is not None and estado not in NO_SPEECH_STATUSES and estado != "Success":
        raise SttProviderError("Azure Speech retornou estado desconhecido.")
    if estado in NO_SPEECH_STATUSES:
        return "", 0.0

    best = _best_alternative(payload)
    if best is not None:
        # `Display` traz pontuacao e maiusculas, e e a forma devolvida ao
        # usuario no campo `transcription.text`. As demais entram como reserva
        # quando o provedor nao envia a resposta detalhada completa.
        text = _first_text(
            best.get("Display"),
            best.get("MaskedITN"),
            best.get("ITN"),
            best.get("Lexical"),
        )
        return text, _confidence(best.get("Confidence"))

    return _first_text(payload.get("DisplayText")), 0.0


def _best_alternative(payload: dict) -> dict | None:
    alternatives = payload.get("NBest")
    if not isinstance(alternatives, list) or not alternatives:
        return None

    dictionaries = [item for item in alternatives if isinstance(item, dict)]
    if not dictionaries:
        return None

    return max(dictionaries, key=lambda item: _confidence(item.get("Confidence")))


def _first_text(*values: object) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _confidence(value: object) -> float:
    if isinstance(value, (int, float)):
        return min(max(float(value), 0.0), 1.0)
    return 0.0
