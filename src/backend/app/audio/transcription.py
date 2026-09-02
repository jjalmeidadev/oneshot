"""Fronteira entre a API de audio e o servico de Speech-to-Text.

A integracao real com o provedor da Secao 8.8 de docs/Projeto.md e a task 11
do backlog da Sprint 3. Este modulo existe para que a rota ja dependa de um
contrato interno estavel: quando a integracao chegar, apenas ``transcribe``
muda, e o mapeamento de erro do endpoint permanece o mesmo.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.audio.validation import AudioProbe


class SttProviderError(RuntimeError):
    """Falha na chamada ao servico de transcricao; vira 502 na resposta."""


class SttProviderUnavailable(RuntimeError):
    """Servico de transcricao fora do ar; vira 503 na resposta."""


@dataclass(frozen=True)
class Transcription:
    text: str
    confidence: float
    duration_seconds: float


def transcribe(
    data: bytes, probe: AudioProbe, language: str = "pt-BR"
) -> Transcription | None:
    """Transcreve o audio validado.

    Devolve ``None`` enquanto a integracao da task 11 nao existir, o que faz o
    endpoint responder no formato do contrato com ``pipeline_status``
    ``"stubbed"``. Quando o provedor real entrar, as falhas dele devem ser
    levantadas como ``SttProviderError`` ou ``SttProviderUnavailable``.
    """

    return None
