"""Erros publicos e sanitizados da integracao com o Copilot Studio."""

from __future__ import annotations


class CopilotError(Exception):
    """Falha controlada que pode ser devolvida sem expor detalhes internos."""

    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class CopilotConfigurationError(CopilotError):
    def __init__(self) -> None:
        super().__init__(
            "COPILOT_CONFIGURATION_ERROR",
            "A integracao com o Copilot Studio esta indisponivel.",
            503,
        )


class CopilotUnauthenticatedError(CopilotError):
    def __init__(self) -> None:
        super().__init__(
            "UNAUTHENTICATED",
            "Credencial ausente, invalida ou expirada.",
            401,
        )


class CopilotForbiddenError(CopilotError):
    def __init__(self) -> None:
        super().__init__(
            "FORBIDDEN",
            "A credencial nao possui permissao para esta operacao.",
            403,
        )


class AuthenticationProviderUnavailableError(CopilotError):
    def __init__(self) -> None:
        super().__init__(
            "AUTH_PROVIDER_UNAVAILABLE",
            "Nao foi possivel validar a credencial neste momento.",
            503,
        )


class ModelRouteNotAllowedError(CopilotError):
    def __init__(self) -> None:
        super().__init__(
            "MODEL_ROUTE_NOT_ALLOWED",
            "A rota de modelo solicitada nao e reconhecida ou permitida.",
            422,
        )


class ModelRouteUnavailableError(CopilotError):
    def __init__(self) -> None:
        super().__init__(
            "MODEL_ROUTE_UNAVAILABLE",
            "A rota de modelo solicitada esta temporariamente indisponivel.",
            503,
        )


class UnsafeDispatchInputError(CopilotError):
    def __init__(self) -> None:
        super().__init__(
            "UNSAFE_DISPATCH_INPUT",
            "A solicitacao nao pode ser encaminhada para execucao automatica.",
            400,
        )


class DirectLineUnavailableError(CopilotError):
    def __init__(self) -> None:
        super().__init__(
            "DIRECT_LINE_UNAVAILABLE",
            "Nao foi possivel iniciar a conversa com o Copilot Studio.",
            503,
        )
