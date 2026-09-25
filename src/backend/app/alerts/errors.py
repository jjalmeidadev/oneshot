"""Erros controlados do dominio de alertas."""


class AlertError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class AlertAccessDeniedError(AlertError):
    def __init__(self) -> None:
        super().__init__("ALERT_ACCESS_DENIED", "Alerta inexistente ou sem acesso.", 404)


class AlertNotFoundError(AlertError):
    def __init__(self) -> None:
        super().__init__("ALERT_NOT_FOUND", "Alerta nao encontrado.", 404)


class AlertConflictError(AlertError):
    def __init__(self, message: str) -> None:
        super().__init__("ALERT_CONFLICT", message, 409)


class AlertConfigurationError(AlertError):
    def __init__(self, message: str = "Fluxo de alerta indisponivel.") -> None:
        super().__init__("ALERT_CONFIGURATION_ERROR", message, 503)

