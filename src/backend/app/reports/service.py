"""Orquestracao do fluxo de relatorios e do duplo local controlado."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any
from uuid import uuid4

import httpx

from app.reports.errors import (
    ReportAccessDeniedError,
    ReportConfigurationError,
    ReportConflictError,
    ReportError,
)
from app.reports.rendering import DocxReportRenderer
from app.reports.repository import ReportRepository, get_report_repository
from app.reports.schemas import (
    CreateReportRequest,
    ExecutionEvent,
    PreparedReport,
    PrepareReportRequest,
    PrepareReportResponse,
    ReportCallbackRequest,
    ReportExecution,
    ReportExecutionResponse,
    ReportSource,
    ReportStatus,
)
from app.reports.security import ReportIdentity, authorize_scope
from app.reports.sources import PostgresPortfolioSource, SyntheticPortfolioSource
from app.reports.storage import ArtifactContent, ArtifactStore
from app.reports.state_machine import validate_transition

CONFIRMATION_TTL_MINUTES = 15
TERMINAL_STATUSES = {
    ReportStatus.COMPLETED,
    ReportStatus.COMPLETED_WITH_WARNINGS,
    ReportStatus.FAILED,
    ReportStatus.BLOCKED,
    ReportStatus.CANCELLED,
}


class ReportService:
    def __init__(
        self,
        repository: ReportRepository,
        source: "SyntheticPortfolioSource | PostgresPortfolioSource | None" = None,
        renderer: DocxReportRenderer | None = None,
        confirmation_secret: bytes | None = None,
        execution_mode: str | None = None,
        artifact_store: ArtifactStore | None = None,
    ) -> None:
        self.repository = repository
        self.source = source or SyntheticPortfolioSource()
        self.renderer = renderer or DocxReportRenderer()
        self.execution_mode = (
            (execution_mode or os.getenv("REPORT_EXECUTION_MODE", "local"))
            .strip()
            .lower()
        )
        if self.execution_mode not in {
            "local",
            "power_automate",
            "power_automate_simulator",
        }:
            raise ReportConfigurationError()
        if (
            confirmation_secret is None
            and self.execution_mode == "power_automate"
            and not os.getenv("REPORT_CONFIRMATION_SECRET", "").strip()
        ):
            raise ReportConfigurationError()
        self.confirmation_secret = confirmation_secret or _confirmation_secret()
        self.artifact_store = artifact_store or ArtifactStore()

    def prepare(
        self, request: PrepareReportRequest, identity: ReportIdentity
    ) -> PrepareReportResponse:
        authorize_scope(identity, request.scope)
        metadata = self.source.scope_metadata(request.scope.type, request.scope.id)
        expires_at = _now() + timedelta(minutes=CONFIRMATION_TTL_MINUTES)
        prepared = PreparedReport(
            contract_version=request.contract_version,
            requested_by=identity.subject,
            conversation_id=request.conversation_id,
            interaction_id=request.interaction_id,
            correlation_id=request.correlation_id or str(uuid4()),
            report_type=request.report_type,
            scope=request.scope,
            period=request.period,
            options=request.options,
            scope_title=metadata["title"],
            data_reference_at=metadata["updated_at"],
            confirmation_expires_at=expires_at,
        )
        warnings = []
        if prepared.data_reference_at.date() < prepared.period.end_date:
            warnings.append(
                "A ultima atualizacao disponivel e anterior ao fim do periodo solicitado."
            )
        return PrepareReportResponse(
            prepared_request=prepared,
            confirmation_summary=_confirmation_summary(prepared),
            confirmation_hash=self._confirmation_hash(prepared),
            expires_at=expires_at,
            warnings=warnings,
        )

    def create(
        self, request: CreateReportRequest, identity: ReportIdentity
    ) -> tuple[ReportExecution, bool]:
        prepared = request.prepared_request
        authorize_scope(identity, prepared.scope)
        if prepared.requested_by != identity.subject:
            raise ReportAccessDeniedError()
        if prepared.confirmation_expires_at < _now():
            raise ReportConflictError(
                "A confirmacao expirou. Revise os parametros e confirme novamente."
            )
        expected = self._confirmation_hash(prepared)
        if not hmac.compare_digest(expected, request.confirmation_hash):
            raise ReportConflictError(
                "Os parametros mudaram depois da confirmacao. Confirme novamente."
            )

        existing = self.repository.find_by_idempotency(
            identity.subject, request.idempotency_key
        )
        if existing is not None:
            existing_hash = self._confirmation_hash(existing.prepared_request)
            if not hmac.compare_digest(existing_hash, request.confirmation_hash):
                raise ReportConflictError(
                    "A chave de idempotencia pertence a outra solicitacao."
                )
            return existing, False

        now = _now()
        execution = ReportExecution(
            execution_id=str(uuid4()),
            correlation_id=prepared.correlation_id,
            idempotency_key=request.idempotency_key,
            requested_by=identity.subject,
            status=ReportStatus.QUEUED,
            confirmation_hash=request.confirmation_hash,
            prepared_request=prepared,
            created_at=now,
            updated_at=now,
            events=[
                _event("report.confirmed", "sucesso", "guided_workflow"),
                _event("report.queued", "pendente", "api"),
            ],
        )
        try:
            return self.repository.create(execution), True
        except ReportConflictError:
            # Duas confirmacoes concorrentes podem ultrapassar a consulta acima.
            # A unicidade do repositorio e a fonte de verdade; o perdedor recupera
            # a mesma execucao em vez de criar trabalho orfao.
            existing = self.repository.find_by_idempotency(
                identity.subject, request.idempotency_key
            )
            if existing is None:
                raise
            existing_hash = self._confirmation_hash(existing.prepared_request)
            if not hmac.compare_digest(existing_hash, request.confirmation_hash):
                raise ReportConflictError(
                    "A chave de idempotencia pertence a outra solicitacao."
                )
            return existing, False

    def process_local(self, execution_id: str) -> None:
        execution = self.repository.get(execution_id)
        if execution.status in TERMINAL_STATUSES:
            return
        try:
            self._transition(execution, ReportStatus.PROCESSING, "report.processing")
            snapshot = self.source.build_snapshot(execution.prepared_request)
            execution.snapshot_hash = _payload_hash(snapshot)
            execution.snapshot_payload = snapshot
            execution.sources = [
                ReportSource.model_validate(item) for item in snapshot["sources"]
            ]
            execution.warnings.extend(snapshot.get("limitations", []))
            artifact = self.renderer.render(
                execution.execution_id,
                execution.prepared_request,
                snapshot,
            )
            execution.artifact = self.artifact_store.persist(artifact)
            final_status = (
                ReportStatus.COMPLETED_WITH_WARNINGS
                if execution.warnings
                else ReportStatus.COMPLETED
            )
            execution.completed_at = _now()
            self._transition(execution, final_status, "report.completed")
        except ReportConfigurationError:
            self._fail(
                execution,
                ReportStatus.BLOCKED,
                "REPORT_DEPENDENCY_UNAVAILABLE",
                "A geracao foi bloqueada por uma dependencia indisponivel.",
            )
        except ReportError as error:
            self._fail(execution, ReportStatus.FAILED, error.code, error.message)
        except Exception:
            self._fail(
                execution,
                ReportStatus.FAILED,
                "REPORT_GENERATION_FAILED",
                "Nao foi possivel gerar o relatorio.",
            )

    def get(self, execution_id: str, identity: ReportIdentity) -> ReportExecution:
        execution = self.repository.get(execution_id)
        self._authorize_execution(execution, identity)
        return execution

    def artifact_content(
        self, execution_id: str, identity: ReportIdentity
    ) -> ArtifactContent:
        execution = self.get(execution_id, identity)
        if execution.artifact is None or not execution.artifact.storage_reference:
            raise ReportError(
                "REPORT_ARTIFACT_NOT_AVAILABLE",
                "O arquivo do relatorio ainda nao esta disponivel.",
                404,
            )
        return self.artifact_store.read(
            execution.artifact, self.renderer.artifact_directory
        )

    def recover_pending(
        self, *, stale_after_seconds: int = 60, limit: int = 50
    ) -> list[str]:
        """Retoma jobs duraveis deixados por reinicio do processo HTTP.

        O BackgroundTasks reduz latencia, mas a linha em report_executions e a
        fonte de verdade. Um worker unico chama este metodo periodicamente.
        Disparos externos reutilizam a mesma chave de idempotencia.
        """
        cutoff = _now() - timedelta(seconds=max(stale_after_seconds, 0))
        execution_ids = self.repository.list_pending(
            cutoff, min(max(limit, 1), 500)
        )
        processor = (
            self.process_local
            if self.execution_mode == "local"
            else self.dispatch_power_automate
        )
        for execution_id in execution_ids:
            processor(execution_id)
        return execution_ids

    def dispatch_power_automate(self, execution_id: str) -> None:
        execution = self.repository.get(execution_id)
        if execution.status in TERMINAL_STATUSES:
            return
        try:
            self._transition(execution, ReportStatus.PROCESSING, "report.processing")
            snapshot = self.source.build_snapshot(execution.prepared_request)
            execution.snapshot_hash = _payload_hash(snapshot)
            execution.snapshot_payload = snapshot
            execution.sources = [
                ReportSource.model_validate(item) for item in snapshot["sources"]
            ]
            self.repository.save(execution)
            if self.execution_mode == "power_automate_simulator":
                self.apply_callback(
                    ReportCallbackRequest(
                        callback_id=f"simulated-{uuid4()}",
                        execution_id=execution.execution_id,
                        correlation_id=execution.correlation_id,
                        flow_run_id=f"local-simulator-{uuid4()}",
                        status=ReportStatus.COMPLETED,
                        result={"schema_version": "1.0"},
                        warnings=[
                            "Processamento executado pelo simulador local do Power Automate."
                        ],
                    )
                )
                return

            trigger_url = os.getenv("POWER_AUTOMATE_REPORT_TRIGGER_URL", "").strip()
            trigger_token = os.getenv("POWER_AUTOMATE_TRIGGER_TOKEN", "").strip()
            callback_base_url = (
                os.getenv("REPORT_CALLBACK_BASE_URL", "").strip().rstrip("/")
            )
            if not trigger_url or not trigger_token or not callback_base_url:
                raise ReportConfigurationError()
            payload = {
                    "contract_version": "1.0",
                    "execution_id": execution.execution_id,
                    "correlation_id": execution.correlation_id,
                    "callback_url": (
                        f"{callback_base_url}/api/integrations/"
                        "power-automate/report-results"
                    ),
                    "prepared_request": execution.prepared_request.model_dump(mode="json"),
                    "snapshot": snapshot,
                }
            headers = {
                    "Authorization": f"Bearer {trigger_token}",
                    "Content-Type": "application/json",
                    "Idempotency-Key": execution.idempotency_key,
                }
            response = None
            for _attempt in range(_automation_attempts()):
                try:
                    candidate = httpx.post(
                        trigger_url,
                        json=payload,
                        headers=headers,
                        timeout=_automation_timeout(),
                    )
                except httpx.RequestError:
                    continue
                if candidate.status_code in {200, 202}:
                    response = candidate
                    break
                if candidate.status_code < 500:
                    raise ReportConfigurationError()
            if response is None:
                self._fail(
                    execution,
                    ReportStatus.BLOCKED,
                    "REPORT_AUTOMATION_DISPATCH_UNCERTAIN",
                    "O envio da automacao ficou sem confirmacao; o callback tardio continua aceito.",
                )
                return
            try:
                body = response.json()
            except ValueError:
                body = {}
            execution.flow_run_id = str(body.get("flow_run_id") or "") or None
            execution.events.append(
                _event("report.automation.dispatched", "pendente", "power_automate")
            )
            execution.updated_at = _now()
            self.repository.save(execution)
        except ReportConfigurationError:
            self._fail(
                execution,
                ReportStatus.BLOCKED,
                "REPORT_DEPENDENCY_UNAVAILABLE",
                "A automacao externa nao esta configurada ou disponivel.",
            )
        except Exception:
            self._fail(
                execution,
                ReportStatus.FAILED,
                "REPORT_AUTOMATION_DISPATCH_FAILED",
                "Nao foi possivel iniciar o processamento do relatorio.",
            )

    def apply_callback(self, callback: ReportCallbackRequest) -> ReportExecution:
        execution = self.repository.get(callback.execution_id)
        if callback.correlation_id != execution.correlation_id:
            raise ReportConflictError(
                "O callback nao corresponde a execucao informada."
            )
        payload = callback.model_dump(mode="json")
        payload_hash = _payload_hash(payload)
        existing_hash = self.repository.callback_payload_hash(callback.callback_id)
        if existing_hash is not None:
            if not hmac.compare_digest(existing_hash, payload_hash):
                raise ReportConflictError(
                    "O identificador do callback pertence a outro retorno."
                )
            return execution
        recoverable_dispatch = (
            execution.status in {ReportStatus.BLOCKED, ReportStatus.FAILED}
            and execution.error_code
            in {
                "REPORT_AUTOMATION_DISPATCH_UNCERTAIN",
                "REPORT_AUTOMATION_DISPATCH_FAILED",
            }
        )
        if execution.status in TERMINAL_STATUSES and not recoverable_dispatch:
            raise ReportConflictError("A execucao ja possui estado terminal.")

        if execution.status == ReportStatus.QUEUED:
            self._transition(execution, ReportStatus.PROCESSING, "report.processing")
        if execution.snapshot_payload is None:
            snapshot = self.source.build_snapshot(execution.prepared_request)
            execution.snapshot_payload = snapshot
            execution.snapshot_hash = _payload_hash(snapshot)
            execution.sources = [
                ReportSource.model_validate(item) for item in snapshot["sources"]
            ]
        execution.flow_run_id = callback.flow_run_id
        execution.callback_id = callback.callback_id
        if recoverable_dispatch:
            execution.events.append(
                _event("report.automation.late_callback", "sucesso", "power_automate")
            )
        execution.error_code = callback.error_code
        execution.error_message = callback.error_message
        execution.completed_at = _now()
        if callback.status in {
            ReportStatus.COMPLETED,
            ReportStatus.COMPLETED_WITH_WARNINGS,
        }:
            snapshot = execution.snapshot_payload
            if snapshot is None:
                raise ReportConflictError(
                    "A fotografia de dados da execucao nao esta disponivel."
                )
            trusted_result = self._validated_automation_result(callback, snapshot)
            artifact = self.renderer.render(
                execution.execution_id,
                execution.prepared_request,
                snapshot,
                automation_result=trusted_result,
            )
            execution.artifact = self.artifact_store.persist(artifact)
        execution.warnings.extend(callback.warnings)
        target_status = callback.status
        if target_status == ReportStatus.COMPLETED and execution.warnings:
            target_status = ReportStatus.COMPLETED_WITH_WARNINGS
        validate_transition(execution.status, target_status)
        execution.status = target_status
        execution.updated_at = _now()
        execution.events.append(
            _event("report.callback.received", "sucesso", "power_automate")
        )
        return self.repository.save_callback(
            callback.callback_id,
            execution,
            payload_hash,
            payload,
        )

    @staticmethod
    def _validated_automation_result(callback: ReportCallbackRequest, snapshot: dict):
        result = callback.result
        if result is None:
            return None
        review = result.foundation_review
        if review and (
            not review.approved
            or review.unsupported_claims
            or review.numeric_mismatches
            or review.missing_source_ids
        ):
            callback.warnings.append(
                "A redacao do AI Builder nao passou na validacao; foi usado o texto deterministico."
            )
            return None
        if result.executive_summary:
            allowed = {str(item.get("source_id")) for item in snapshot["sources"]}
            if not set(result.executive_summary.citation_source_ids).issubset(allowed):
                callback.warnings.append(
                    "Foram recebidas citacoes desconhecidas; foi usado o texto deterministico."
                )
                return None
            callback.warnings.extend(result.executive_summary.limitations)
        if result.normalized_context:
            callback.warnings.extend(result.normalized_context.warnings)
        return result

    def response(self, execution: ReportExecution) -> ReportExecutionResponse:
        error = None
        if execution.error_code:
            error = {
                "code": execution.error_code,
                "message": execution.error_message or "Falha ao gerar o relatorio.",
            }
        return ReportExecutionResponse(
            execution_id=execution.execution_id,
            correlation_id=execution.correlation_id,
            status=execution.status,
            status_url=f"/api/report-requests/{execution.execution_id}",
            artifact=execution.artifact,
            warnings=execution.warnings,
            error=error,
            created_at=execution.created_at,
            updated_at=execution.updated_at,
        )

    def _transition(
        self, execution: ReportExecution, status: ReportStatus, event_type: str
    ) -> None:
        validate_transition(execution.status, status)
        execution.status = status
        execution.updated_at = _now()
        if status == ReportStatus.PROCESSING and execution.started_at is None:
            execution.started_at = execution.updated_at
        event_status = "sucesso" if status in TERMINAL_STATUSES else "pendente"
        execution.events.append(_event(event_type, event_status, "api"))
        self.repository.save(execution)

    def _fail(
        self,
        execution: ReportExecution,
        status: ReportStatus,
        error_code: str,
        error_message: str,
    ) -> None:
        if execution.status in TERMINAL_STATUSES:
            return
        execution.error_code = error_code
        execution.error_message = error_message
        execution.completed_at = _now()
        self._transition(execution, status, "report.failed")

    def _confirmation_hash(self, prepared: PreparedReport) -> str:
        canonical = json.dumps(
            prepared.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hmac.new(self.confirmation_secret, canonical, hashlib.sha256).hexdigest()

    @staticmethod
    def _authorize_execution(
        execution: ReportExecution, identity: ReportIdentity
    ) -> None:
        if execution.requested_by == identity.subject:
            return
        authorize_scope(identity, execution.prepared_request.scope)


@lru_cache(maxsize=1)
def get_report_service() -> ReportService:
    return ReportService(get_report_repository(), source=get_portfolio_source())


def get_portfolio_source() -> Any:
    """Seleciona a fonte de dados de portfolio.

    ``REPORT_PORTFOLIO_SOURCE=database`` le das tabelas reais do PostgreSQL;
    qualquer outro valor (padrao) usa a massa sintetica em JSON, preservando o
    comportamento dos testes existentes.
    """

    mode = os.getenv("REPORT_PORTFOLIO_SOURCE", "synthetic").strip().lower()
    if mode == "database":
        return PostgresPortfolioSource()
    return SyntheticPortfolioSource()


def reset_report_service() -> None:
    get_report_service.cache_clear()


@lru_cache(maxsize=1)
def _confirmation_secret() -> bytes:
    configured = os.getenv("REPORT_CONFIRMATION_SECRET", "").strip()
    return configured.encode("utf-8") if configured else secrets.token_bytes(32)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _payload_hash(payload: Any) -> str:
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _automation_timeout() -> float:
    try:
        return max(
            1.0,
            min(float(os.getenv("POWER_AUTOMATE_TRIGGER_TIMEOUT_SECONDS", "20")), 120.0),
        )
    except ValueError as error:
        raise ReportConfigurationError() from error


def _automation_attempts() -> int:
    try:
        return min(
            max(int(os.getenv("POWER_AUTOMATE_DISPATCH_ATTEMPTS", "3")), 1), 5
        )
    except ValueError:
        return 3


def _event(
    event_type: str, status: str, component: str, payload: dict | None = None
) -> ExecutionEvent:
    return ExecutionEvent(
        event_type=event_type,
        status=status,
        component=component,
        occurred_at=_now(),
        payload=payload or {},
    )


def _confirmation_summary(prepared: PreparedReport) -> str:
    emphasis = (
        ", ".join(item.value for item in prepared.options.emphasis) or "visao geral"
    )
    period = prepared.period.label or (
        f"{prepared.period.start_date:%d/%m/%Y} a {prepared.period.end_date:%d/%m/%Y}"
    )
    return (
        f"Gerar relatorio executivo de {prepared.scope_title}, periodo {period}, "
        f"para {prepared.options.audience.value}, com enfase em {emphasis}, "
        "no formato DOCX."
    )
