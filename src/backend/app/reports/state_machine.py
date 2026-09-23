"""Transicoes permitidas para execucoes de relatorio."""

from app.reports.errors import ReportConflictError
from app.reports.schemas import ReportStatus

ALLOWED_TRANSITIONS: dict[ReportStatus, set[ReportStatus]] = {
    ReportStatus.CONFIRMED: {ReportStatus.QUEUED, ReportStatus.CANCELLED},
    ReportStatus.QUEUED: {
        ReportStatus.PROCESSING,
        ReportStatus.BLOCKED,
        ReportStatus.FAILED,
        ReportStatus.CANCELLED,
    },
    ReportStatus.PROCESSING: {
        ReportStatus.COMPLETED,
        ReportStatus.COMPLETED_WITH_WARNINGS,
        ReportStatus.BLOCKED,
        ReportStatus.FAILED,
        ReportStatus.CANCELLED,
    },
    ReportStatus.BLOCKED: {
        ReportStatus.COMPLETED,
        ReportStatus.COMPLETED_WITH_WARNINGS,
        ReportStatus.FAILED,
    },
    ReportStatus.FAILED: {
        ReportStatus.COMPLETED,
        ReportStatus.COMPLETED_WITH_WARNINGS,
        ReportStatus.BLOCKED,
    },
}


def validate_transition(current: ReportStatus, target: ReportStatus) -> None:
    if current == target:
        return
    if target not in ALLOWED_TRANSITIONS.get(current, set()):
        raise ReportConflictError(
            f"Transicao de estado invalida: {current.value} para {target.value}."
        )
