"""Erros publicos e controlados do fluxo de relatorios."""


class ReportError(RuntimeError):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class ReportNotFoundError(ReportError):
    def __init__(self) -> None:
        super().__init__("REPORT_NOT_FOUND", "Relatorio nao encontrado.", 404)


class ReportAccessDeniedError(ReportError):
    def __init__(self) -> None:
        super().__init__(
            "REPORT_ACCESS_DENIED",
            "Voce nao possui permissao para gerar ou consultar este relatorio.",
            403,
        )


class ReportConflictError(ReportError):
    def __init__(self, message: str) -> None:
        super().__init__("REPORT_CONFLICT", message, 409)


class ReportConfigurationError(ReportError):
    def __init__(self) -> None:
        super().__init__(
            "REPORT_SERVICE_UNAVAILABLE",
            "O servico de relatorios esta indisponivel. Tente novamente em instantes.",
            503,
        )
