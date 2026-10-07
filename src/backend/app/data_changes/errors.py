"""Erros publicos da alteracao pelo chat (codigos da Secao 8.5.13)."""

from __future__ import annotations


class DataChangeError(Exception):
    """Erro esperado com codigo estavel, mensagem em portugues e status HTTP."""

    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code

    def to_payload(self) -> dict[str, dict[str, str]]:
        return {"error": {"code": self.code, "message": self.message}}


def unavailable() -> DataChangeError:
    return DataChangeError(
        "DATA_CHANGE_UNAVAILABLE",
        "A alteração de dados está indisponível no momento. Nada foi gravado.",
        503,
    )


def out_of_scope(project_code: str | None = None) -> DataChangeError:
    alvo = f" do {project_code}" if project_code else ""
    return DataChangeError(
        "OUT_OF_SCOPE_FOR_PROFILE",
        f"Seu perfil não tem permissão para alterar dados{alvo}.",
        403,
    )


def target_not_found(message: str = "O registro informado não foi encontrado no seu escopo.") -> DataChangeError:
    return DataChangeError("TARGET_NOT_FOUND", message, 404)


def field_not_editable(allowed: str) -> DataChangeError:
    return DataChangeError(
        "FIELD_NOT_EDITABLE",
        f"Esse campo não pode ser alterado pelo chat. Campos permitidos: {allowed}.",
        422,
    )


def invalid_value(message: str) -> DataChangeError:
    return DataChangeError("INVALID_VALUE", message, 422)


PREVIEW_NOT_FOUND = ("PREVIEW_NOT_FOUND", "A prévia não foi encontrada.", 404)
PREVIEW_CANCELLED = ("PREVIEW_CANCELLED", "Esta prévia foi cancelada. Peça a alteração de novo.", 409)
PREVIEW_EXPIRED = ("PREVIEW_EXPIRED", "A prévia expirou. Peça a alteração de novo para conferir o valor atual.", 410)
STALE_PREVIEW = ("STALE_PREVIEW", "O valor mudou depois da prévia. Peça a alteração de novo para conferir o valor atual.", 409)
CHANGE_NOT_FOUND = ("CHANGE_NOT_FOUND", "A alteração não foi encontrada.", 404)
UNDO_NOT_AUTHOR = ("UNDO_NOT_AUTHOR", "Só quem fez a alteração pode desfazê-la.", 403)
UNDO_WINDOW_EXPIRED = ("UNDO_WINDOW_EXPIRED", "O prazo de 15 minutos para desfazer terminou. Faça uma nova alteração, se precisar.", 410)
VALUE_CHANGED_SINCE = ("VALUE_CHANGED_SINCE", "O valor foi alterado de novo depois desta alteração, então ela não pode ser desfeita.", 409)
ALREADY_UNDONE = ("ALREADY_UNDONE", "Esta alteração já foi desfeita.", 409)


def error(spec: tuple[str, str, int]) -> DataChangeError:
    return DataChangeError(*spec)
