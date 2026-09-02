"""Erros da API de recebimento de audio.

Cada erro carrega o `code` estavel (usado no corpo de resposta), a mensagem
legivel e o status HTTP correspondente, conforme a tabela da Secao 8.7.6 de
docs/Projeto.md.
"""

from __future__ import annotations


class AudioValidationError(Exception):
    """Erro de validacao do audio recebido, anterior a qualquer chamada externa."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        detail: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}


class AudioMissingError(AudioValidationError):
    def __init__(self) -> None:
        super().__init__(
            code="AUDIO_MISSING",
            message="Campo 'audio' ausente na requisicao.",
            status_code=400,
        )


class AudioFormatUnsupportedError(AudioValidationError):
    def __init__(self, received: str) -> None:
        super().__init__(
            code="AUDIO_FORMAT_UNSUPPORTED",
            message=(
                "Formato de audio nao suportado. Envie WAV/PCM ou OGG/OPUS "
                "a 16 kHz, mono."
            ),
            status_code=400,
            detail={"received": received},
        )


class AudioTooLongError(AudioValidationError):
    def __init__(self, duration_seconds: float, max_seconds: float) -> None:
        super().__init__(
            code="AUDIO_TOO_LONG",
            message=f"Gravacao acima de {int(max_seconds)} segundos.",
            status_code=400,
            detail={
                "duration_seconds": round(duration_seconds, 2),
                "max_seconds": max_seconds,
            },
        )


class AudioTooLargeError(AudioValidationError):
    def __init__(self, size_bytes: int, max_bytes: int) -> None:
        super().__init__(
            code="AUDIO_TOO_LARGE",
            message=f"Arquivo acima de {max_bytes // (1024 * 1024)} MB.",
            status_code=413,
            detail={"size_bytes": size_bytes, "max_bytes": max_bytes},
        )