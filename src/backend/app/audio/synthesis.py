"""Sintese opcional da resposta final com Azure AI Speech."""

from __future__ import annotations

import base64
import logging
import os
from time import monotonic
from urllib.parse import urlparse
from xml.sax.saxutils import escape

import httpx

from app.gemini.schemas import SpeechResponse

LOGGER = logging.getLogger(__name__)
VOICE = "pt-BR-FranciscaNeural"
OUTPUT_FORMAT = "audio-24khz-48kbitrate-mono-mp3"
WARNING = "Não foi possível gerar o áudio agora. A resposta em texto continua disponível."
MAX_TEXT_CHARS = 4000
MAX_AUDIO_BYTES = 4_000_000
DEFAULT_TIMEOUT_SECONDS = 8.0
TRANSIENT_STATUS_CODES = frozenset({408, 500, 502, 503, 504})


class SynthesisUnavailable(RuntimeError):
    """Falha controlada; a resposta textual permanece válida."""


def synthesize_optional(text: str) -> SpeechResponse:
    """Devolve MP3 ou aviso, sem permitir que TTS interrompa o chat."""
    started = monotonic()
    try:
        audio = _synthesize(text)
    except SynthesisUnavailable as error:
        LOGGER.warning("TTS indisponível: %s", error)
        return SpeechResponse(status="unavailable", warning=WARNING)
    except Exception:
        LOGGER.exception("Falha inesperada na síntese de fala")
        return SpeechResponse(status="unavailable", warning=WARNING)
    LOGGER.info("TTS concluído: duração_ms=%d bytes=%d", round((monotonic() - started) * 1000), len(audio))
    return SpeechResponse(
        status="available", media_type="audio/mpeg",
        data_base64=base64.b64encode(audio).decode("ascii"),
    )


def _synthesize(text: str) -> bytes:
    if not text.strip() or len(text) > MAX_TEXT_CHARS:
        raise SynthesisUnavailable("Comprimento de texto incompatível com TTS")
    key = os.getenv("AZURE_SPEECH_KEY", "").strip()
    if not key:
        raise SynthesisUnavailable("Chave Azure ausente")
    url = _tts_url()
    ssml = (
        '<speak version="1.0" xml:lang="pt-BR">'
        f'<voice xml:lang="pt-BR" name="{VOICE}">{escape(text)}</voice>'
        '</speak>'
    )
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": OUTPUT_FORMAT,
        "User-Agent": "agente-metro-portfolio",
    }
    deadline = monotonic() + _timeout_seconds()
    with httpx.Client() as client:
        for attempt in range(2):
            remaining = deadline - monotonic()
            if remaining <= 0:
                raise SynthesisUnavailable("Prazo total de TTS excedido")
            try:
                response = client.post(url, content=ssml.encode("utf-8"), headers=headers, timeout=remaining)
            except (httpx.TimeoutException, httpx.TransportError) as error:
                if attempt == 0:
                    continue
                raise SynthesisUnavailable("Falha de conexão com TTS") from error
            if response.status_code in TRANSIENT_STATUS_CODES and attempt == 0:
                continue
            if response.status_code != 200:
                raise SynthesisUnavailable(f"Status TTS {response.status_code}")
            audio = response.content
            if not audio or len(audio) > MAX_AUDIO_BYTES:
                raise SynthesisUnavailable("Resposta de áudio vazia ou excessiva")
            if not audio.startswith(b"ID3") and not (
                len(audio) > 1 and audio[0] == 0xFF and audio[1] & 0xE0 == 0xE0
            ):
                raise SynthesisUnavailable("Resposta não contém MP3")
            return audio
    raise SynthesisUnavailable("TTS indisponível")


def _tts_url() -> str:
    region = os.getenv("AZURE_SPEECH_REGION", "").strip().lower()
    endpoint = os.getenv("AZURE_SPEECH_ENDPOINT", "").strip()
    resource = os.getenv("AZURE_SPEECH_RESOURCE", "").strip().lower()
    if region:
        if not region.replace("-", "").isalnum():
            raise SynthesisUnavailable("Região Azure inválida")
        return f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    if endpoint:
        parsed = urlparse(endpoint)
        host = parsed.hostname or ""
        if parsed.scheme != "https" or parsed.port or parsed.username or parsed.password:
            raise SynthesisUnavailable("Endpoint Azure inválido")
        for suffix in (".api.cognitive.microsoft.com", ".stt.speech.microsoft.com"):
            if host.endswith(suffix):
                inferred_region = host.removesuffix(suffix)
                if inferred_region and inferred_region.replace("-", "").isalnum():
                    return f"https://{inferred_region}.tts.speech.microsoft.com/cognitiveservices/v1"
        if host.endswith(".cognitiveservices.azure.com") and host.removesuffix(".cognitiveservices.azure.com"):
            return f"https://{host}/tts/cognitiveservices/v1"
        raise SynthesisUnavailable("Host Azure incompatível com TTS")
    if resource and resource.replace("-", "").isalnum():
        return f"https://{resource}.cognitiveservices.azure.com/tts/cognitiveservices/v1"
    raise SynthesisUnavailable("Recurso Azure não configurado")


def _timeout_seconds() -> float:
    try:
        return min(max(float(os.getenv("AZURE_TTS_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)), 1.0), 30.0)
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS
