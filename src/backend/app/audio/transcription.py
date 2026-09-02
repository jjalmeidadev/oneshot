"""Fronteira entre a API de audio e o servico de Speech-to-Text.

A integracao com o provedor descrito na Secao 8.8 do `Projeto.md` e entrega da
issue #122. Este modulo existe para que a API de audio ja dependa de um contrato
interno estavel: quando a integracao chegar, apenas `transcribe` muda, e o
tratamento de erro do endpoint permanece o mesmo.
"""

from dataclasses import dataclass

from app.audio.validation import AudioMetadata


class SttProviderError(RuntimeError):
    """Falha na chamada ao servico de transcricao (502)."""


class SttProviderUnavailableError(RuntimeError):
    """Servico de transcricao indisponivel ou nao configurado (503)."""


@dataclass(frozen=True)
class Transcription:
    text: str
    confidence: float | None = None
    duration_seconds: float | None = None


def transcribe(
    content: bytes, metadata: AudioMetadata, language: str = "pt-BR"
) -> Transcription:
    raise SttProviderUnavailableError(
        "A integracao de Speech-to-Text ainda nao esta configurada."
    )
