"""Erros da API de recebimento de audio.

Cada erro carrega o `code` estavel (usado no corpo de resposta), a mensagem
legivel e o status HTTP correspondente, conforme a tabela da Secao 8.7.6 de
docs/Projeto.md.

O RNF11 exige que 100% dos cenarios de erro previstos retornem mensagens
controladas, sem expor detalhes tecnicos ao usuario final. Por isso a mensagem
e definida aqui, voltada a quem enviou o audio, e o campo `detail` carrega
apenas dados da propria requisicao — nunca vocabulario interno de formato,
nome de excecao ou mensagem de biblioteca.
"""

from __future__ import annotations


class AudioError(Exception):
    """Cenario de erro previsto para o endpoint de audio.

    Base de todos os erros da rota, inclusive os que nao vem da validacao
    local (autenticacao, concorrencia e falhas do provedor de transcricao).
    """

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

    def to_payload(self) -> dict[str, object]:
        """Monta o envelope unico da Secao 8.7.6.

        `detail` so entra quando ha conteudo, como no exemplo do contrato.
        """

        error: dict[str, object] = {"code": self.code, "message": self.message}
        if self.detail:
            error["detail"] = self.detail
        return {"error": error}


class AudioValidationError(AudioError):
    """Erro de validacao do audio recebido, anterior a qualquer chamada externa."""


class AudioMissingError(AudioValidationError):
    def __init__(self) -> None:
        super().__init__(
            code="AUDIO_MISSING",
            message="Envie o arquivo de audio no campo 'audio' da requisicao.",
            status_code=400,
        )


class AudioFormatUnsupportedError(AudioValidationError):
    def __init__(self, detail: dict[str, object] | None = None) -> None:
        super().__init__(
            code="AUDIO_FORMAT_UNSUPPORTED",
            message=(
                "Formato de audio nao suportado. Envie WAV/PCM ou OGG/OPUS "
                "a 16 kHz, mono."
            ),
            status_code=400,
            detail=detail,
        )


class AudioTooLongError(AudioValidationError):
    def __init__(self, duration_seconds: float, max_seconds: float) -> None:
        super().__init__(
            code="AUDIO_TOO_LONG",
            message=(
                f"A gravacao tem {duration_seconds:.1f} segundos e o limite e de "
                f"{int(max_seconds)} segundos. Grave uma pergunta mais curta."
            ),
            status_code=400,
            detail={
                "duration_seconds": round(duration_seconds, 2),
                "max_seconds": max_seconds,
            },
        )


class AudioTooLargeError(AudioValidationError):
    def __init__(self, max_bytes: int) -> None:
        super().__init__(
            code="AUDIO_TOO_LARGE",
            message=(
                "O arquivo excede o limite de "
                f"{max_bytes // (1024 * 1024)} MB aceito pela API."
            ),
            status_code=413,
            detail={"max_bytes": max_bytes},
        )


class NoSpeechDetectedError(AudioValidationError):
    def __init__(self) -> None:
        super().__init__(
            code="NO_SPEECH_DETECTED",
            message=(
                "Nao foi possivel identificar fala no audio enviado. Grave novamente."
            ),
            status_code=422,
        )


class UnauthenticatedError(AudioError):
    def __init__(self) -> None:
        super().__init__(
            code="UNAUTHENTICATED",
            message="Sessao nao autenticada. Entre novamente para enviar audio.",
            status_code=401,
        )


class RateLimitedError(AudioError):
    def __init__(self) -> None:
        super().__init__(
            code="RATE_LIMITED",
            message=(
                "Ja existe um audio em processamento para este usuario. "
                "Aguarde a resposta antes de enviar outro."
            ),
            status_code=429,
        )


class SttProviderFailedError(AudioError):
    def __init__(self) -> None:
        super().__init__(
            code="STT_PROVIDER_ERROR",
            message=(
                "Nao foi possivel transcrever o audio agora. "
                "Tente novamente em instantes."
            ),
            status_code=502,
        )


class SttProviderUnavailableError(AudioError):
    def __init__(self) -> None:
        super().__init__(
            code="STT_PROVIDER_UNAVAILABLE",
            message=(
                "O servico de transcricao esta indisponivel. "
                "Envie sua solicitacao por texto enquanto isso."
            ),
            status_code=503,
        )


class ProcessingProviderFailedError(AudioError):
    """Falha controlada ao gerar a resposta depois da transcricao."""

    def __init__(self) -> None:
        super().__init__(
            code="PROCESSING_PROVIDER_ERROR",
            message=(
                "Nao foi possivel processar a transcricao agora. "
                "Tente novamente em instantes."
            ),
            status_code=502,
        )


class ProcessingUnavailableError(AudioError):
    """Pipeline de PLN ou geracao indisponivel depois da transcricao."""

    def __init__(self) -> None:
        super().__init__(
            code="PROCESSING_UNAVAILABLE",
            message=(
                "O servico de processamento esta indisponivel. "
                "Tente novamente em instantes."
            ),
            status_code=503,
        )
