"""Erros controlados da API de audio, conforme a Secao 8.7.6 do Projeto.md.

O RNF11 exige que 100% dos cenarios de erro previstos retornem mensagens
controladas, sem expor detalhes tecnicos internos ao usuario final. Por isso a
mensagem de cada erro e definida aqui, em portugues e voltada a quem enviou o
audio, e o campo `detail` carrega apenas dados da propria requisicao.
"""

from typing import Any


class AudioError(Exception):
    """Cenario de erro previsto para o endpoint de audio.

    Cada instancia carrega o codigo HTTP, o `code` estavel usado pelo canal e a
    mensagem exibida ao usuario. Nenhuma excecao de biblioteca chega ao cliente:
    o handler registrado em `app.main` converte esta classe no envelope de erro.
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        detail: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.detail = detail

    def to_payload(self) -> dict[str, Any]:
        error: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.detail:
            error["detail"] = self.detail
        return {"error": error}


def audio_missing() -> AudioError:
    return AudioError(
        status_code=400,
        code="AUDIO_MISSING",
        message="Envie o arquivo de audio no campo 'audio' da requisicao.",
    )


def audio_format_unsupported(
    message: str, detail: dict[str, Any] | None = None
) -> AudioError:
    return AudioError(
        status_code=400,
        code="AUDIO_FORMAT_UNSUPPORTED",
        message=message,
        detail=detail,
    )


def audio_too_long(duration_seconds: float, max_seconds: int) -> AudioError:
    return AudioError(
        status_code=400,
        code="AUDIO_TOO_LONG",
        message=(
            f"A gravacao tem {duration_seconds:.1f} segundos e o limite e de "
            f"{max_seconds} segundos. Grave uma pergunta mais curta."
        ),
        detail={
            "duration_seconds": round(duration_seconds, 1),
            "max_duration_seconds": max_seconds,
        },
    )


def unauthenticated() -> AudioError:
    return AudioError(
        status_code=401,
        code="UNAUTHENTICATED",
        message="Sessao nao autenticada. Entre novamente para enviar audio.",
    )


def audio_too_large(max_bytes: int) -> AudioError:
    return AudioError(
        status_code=413,
        code="AUDIO_TOO_LARGE",
        message=(
            "O arquivo excede o limite de "
            f"{max_bytes // (1024 * 1024)} MB aceito pela API."
        ),
        detail={"max_size_bytes": max_bytes},
    )


def no_speech_detected() -> AudioError:
    return AudioError(
        status_code=422,
        code="NO_SPEECH_DETECTED",
        message="Nao foi possivel identificar fala no audio enviado. Grave novamente.",
    )


def rate_limited() -> AudioError:
    return AudioError(
        status_code=429,
        code="RATE_LIMITED",
        message=(
            "Ja existe um audio em processamento para este usuario. "
            "Aguarde a resposta antes de enviar outro."
        ),
    )


def stt_provider_error() -> AudioError:
    return AudioError(
        status_code=502,
        code="STT_PROVIDER_ERROR",
        message="Nao foi possivel transcrever o audio agora. Tente novamente em instantes.",
    )


def stt_provider_unavailable() -> AudioError:
    return AudioError(
        status_code=503,
        code="STT_PROVIDER_UNAVAILABLE",
        message=(
            "O servico de transcricao esta indisponivel. "
            "Envie sua solicitacao por texto enquanto isso."
        ),
    )


def internal_error() -> AudioError:
    return AudioError(
        status_code=500,
        code="INTERNAL_ERROR",
        message="Nao foi possivel processar a solicitacao. Tente novamente.",
    )
