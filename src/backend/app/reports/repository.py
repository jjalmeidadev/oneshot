"""Repositorios de execucao: memoria para isolamento e PostgreSQL para integracao."""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime
from functools import lru_cache
from threading import RLock
from typing import Any

from app.database.connection import open_database_connection
from app.reports.errors import (
    ReportConfigurationError,
    ReportConflictError,
    ReportNotFoundError,
)
from app.reports.schemas import ReportArtifact, ReportExecution, ReportStatus


class ReportRepository(ABC):
    @abstractmethod
    def create(self, execution: ReportExecution) -> ReportExecution:
        raise NotImplementedError

    @abstractmethod
    def get(self, execution_id: str) -> ReportExecution:
        raise NotImplementedError

    @abstractmethod
    def find_by_idempotency(
        self, requested_by: str, idempotency_key: str
    ) -> ReportExecution | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, execution: ReportExecution) -> ReportExecution:
        raise NotImplementedError

    @abstractmethod
    def callback_payload_hash(self, callback_id: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def save_callback(
        self,
        callback_id: str,
        execution: ReportExecution,
        payload_hash: str,
        payload: dict,
    ) -> ReportExecution:
        raise NotImplementedError

    @abstractmethod
    def list_pending(self, updated_before: datetime, limit: int) -> list[str]:
        """Lista jobs persistidos que podem ser retomados por um worker."""
        raise NotImplementedError


class InMemoryReportRepository(ReportRepository):
    def __init__(self) -> None:
        self._executions: dict[str, ReportExecution] = {}
        self._idempotency: dict[tuple[str, str], str] = {}
        self._callbacks: dict[str, str] = {}
        self._lock = RLock()

    def create(self, execution: ReportExecution) -> ReportExecution:
        key = (execution.requested_by, execution.idempotency_key)
        with self._lock:
            if key in self._idempotency:
                raise ReportConflictError("Chave de idempotencia ja utilizada.")
            self._executions[execution.execution_id] = deepcopy(execution)
            self._idempotency[key] = execution.execution_id
            return deepcopy(execution)

    def get(self, execution_id: str) -> ReportExecution:
        with self._lock:
            execution = self._executions.get(execution_id)
            if execution is None:
                raise ReportNotFoundError()
            return deepcopy(execution)

    def find_by_idempotency(
        self, requested_by: str, idempotency_key: str
    ) -> ReportExecution | None:
        with self._lock:
            execution_id = self._idempotency.get((requested_by, idempotency_key))
            return deepcopy(self._executions[execution_id]) if execution_id else None

    def save(self, execution: ReportExecution) -> ReportExecution:
        with self._lock:
            if execution.execution_id not in self._executions:
                raise ReportNotFoundError()
            self._executions[execution.execution_id] = deepcopy(execution)
            return deepcopy(execution)

    def callback_payload_hash(self, callback_id: str) -> str | None:
        with self._lock:
            return self._callbacks.get(callback_id)

    def save_callback(
        self,
        callback_id: str,
        execution: ReportExecution,
        payload_hash: str,
        payload: dict,
    ) -> ReportExecution:
        del payload
        with self._lock:
            if execution.execution_id not in self._executions:
                raise ReportNotFoundError()
            existing_hash = self._callbacks.get(callback_id)
            if existing_hash is not None:
                if existing_hash != payload_hash:
                    raise ReportConflictError(
                        "O identificador do callback pertence a outro retorno."
                    )
                return deepcopy(self._executions[execution.execution_id])
            self._executions[execution.execution_id] = deepcopy(execution)
            self._callbacks[callback_id] = payload_hash
            return deepcopy(execution)

    def list_pending(self, updated_before: datetime, limit: int) -> list[str]:
        with self._lock:
            return [
                item.execution_id
                for item in sorted(
                    self._executions.values(), key=lambda current: current.updated_at
                )
                if item.status in {ReportStatus.QUEUED, ReportStatus.PROCESSING}
                and item.updated_at <= updated_before
            ][:limit]


class PostgresReportRepository(ReportRepository):
    """Persistencia opcional ativada por REPORT_REPOSITORY_MODE=database."""

    def create(self, execution: ReportExecution) -> ReportExecution:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO public.report_executions (
                        execution_id, correlation_id, conversation_id,
                        interaction_id, idempotency_key, requested_by,
                        scope_type, scope_id, report_type, execution_status,
                        confirmation_hash, request_payload, warnings,
                        created_at, updated_at
                    ) VALUES (
                        %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s::jsonb, %s::jsonb, %s, %s
                    );
                    """,
                    (
                        execution.execution_id,
                        execution.correlation_id,
                        execution.prepared_request.conversation_id,
                        execution.prepared_request.interaction_id,
                        execution.idempotency_key,
                        execution.requested_by,
                        execution.prepared_request.scope.type.value,
                        execution.prepared_request.scope.id,
                        execution.prepared_request.report_type.value,
                        execution.status.value,
                        execution.confirmation_hash,
                        _json(execution.prepared_request.model_dump(mode="json")),
                        _json(execution.warnings),
                        execution.created_at,
                        execution.updated_at,
                    ),
                )
                self._insert_audit(cursor, execution)
            connection.commit()
            return execution.model_copy(deep=True)
        except Exception as error:
            connection.rollback()
            if _is_unique_violation(error):
                raise ReportConflictError(
                    "Chave de idempotencia ja utilizada."
                ) from error
            raise ReportConfigurationError() from error
        finally:
            connection.close()

    def get(self, execution_id: str) -> ReportExecution:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT execution_id::text, correlation_id, idempotency_key,
                           requested_by, execution_status, confirmation_hash, request_payload,
                           created_at, updated_at, started_at, completed_at,
                           flow_run_id, callback_id, snapshot_hash, snapshot_payload, sources,
                           warnings, error_code, error_message, events
                    FROM public.report_executions
                    WHERE execution_id = %s::uuid;
                    """,
                    (execution_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    raise ReportNotFoundError()
                cursor.execute(
                    """
                    SELECT artifact_id::text, file_name, content_type, size_bytes,
                           sha256, download_url, storage_provider,
                           storage_reference, created_at
                    FROM public.generated_reports
                    WHERE execution_id = %s::uuid;
                    """,
                    (execution_id,),
                )
                artifact_row = cursor.fetchone()
            return _execution_from_rows(row, artifact_row)
        except ReportNotFoundError:
            raise
        except Exception as error:
            raise ReportConfigurationError() from error
        finally:
            connection.close()

    def find_by_idempotency(
        self, requested_by: str, idempotency_key: str
    ) -> ReportExecution | None:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT execution_id::text
                    FROM public.report_executions
                    WHERE requested_by = %s AND idempotency_key = %s;
                    """,
                    (requested_by, idempotency_key),
                )
                row = cursor.fetchone()
            return self.get(str(row[0])) if row else None
        except ReportConfigurationError:
            raise
        except Exception as error:
            raise ReportConfigurationError() from error
        finally:
            connection.close()

    def list_pending(self, updated_before: datetime, limit: int) -> list[str]:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT execution_id::text
                    FROM public.report_executions
                    WHERE execution_status IN ('queued', 'processing')
                      AND updated_at <= %s
                    ORDER BY updated_at ASC
                    LIMIT %s;
                    """,
                    (updated_before, limit),
                )
                return [str(row[0]) for row in cursor.fetchall()]
        except Exception as error:
            raise ReportConfigurationError() from error
        finally:
            connection.close()

    def save(self, execution: ReportExecution) -> ReportExecution:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                self._update_execution(cursor, execution)
                if execution.artifact:
                    self._upsert_artifact(
                        cursor, execution.execution_id, execution.artifact
                    )
                self._insert_audit(cursor, execution)
            connection.commit()
            return execution.model_copy(deep=True)
        except ReportNotFoundError:
            connection.rollback()
            raise
        except Exception as error:
            connection.rollback()
            raise ReportConfigurationError() from error
        finally:
            connection.close()

    def callback_payload_hash(self, callback_id: str) -> str | None:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT payload_hash FROM public.automation_callbacks WHERE callback_id = %s;",
                    (callback_id,),
                )
                row = cursor.fetchone()
                return str(row[0]) if row else None
        except Exception as error:
            raise ReportConfigurationError() from error
        finally:
            connection.close()

    def save_callback(
        self,
        callback_id: str,
        execution: ReportExecution,
        payload_hash: str,
        payload: dict,
    ) -> ReportExecution:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT execution_status
                    FROM public.report_executions
                    WHERE execution_id = %s::uuid
                    FOR UPDATE;
                    """,
                    (execution.execution_id,),
                )
                current = cursor.fetchone()
                if current is None:
                    raise ReportNotFoundError()
                cursor.execute(
                    """
                    SELECT payload_hash
                    FROM public.automation_callbacks
                    WHERE callback_id = %s;
                    """,
                    (callback_id,),
                )
                existing = cursor.fetchone()
                if existing is not None:
                    if str(existing[0]) != payload_hash:
                        raise ReportConflictError(
                            "O identificador do callback pertence a outro retorno."
                        )
                    connection.rollback()
                    return self.get(execution.execution_id)
                if ReportStatus(str(current[0])) in {
                    ReportStatus.COMPLETED,
                    ReportStatus.COMPLETED_WITH_WARNINGS,
                    ReportStatus.FAILED,
                    ReportStatus.BLOCKED,
                    ReportStatus.CANCELLED,
                }:
                    raise ReportConflictError(
                        "A execucao ja possui estado terminal."
                    )
                cursor.execute(
                    """
                    INSERT INTO public.automation_callbacks (
                        callback_id, execution_id, payload_hash, payload
                    ) VALUES (%s, %s::uuid, %s, %s::jsonb)
                    ;
                    """,
                    (
                        callback_id,
                        execution.execution_id,
                        payload_hash,
                        _json(payload),
                    ),
                )
                self._update_execution(cursor, execution)
                if execution.artifact:
                    self._upsert_artifact(
                        cursor, execution.execution_id, execution.artifact
                    )
                self._insert_audit(cursor, execution)
            connection.commit()
            return execution.model_copy(deep=True)
        except (ReportConflictError, ReportNotFoundError):
            connection.rollback()
            raise
        except Exception as error:
            connection.rollback()
            raise ReportConfigurationError() from error
        finally:
            connection.close()

    @staticmethod
    def _connection() -> Any:
        try:
            return open_database_connection()
        except Exception as error:
            raise ReportConfigurationError() from error

    @staticmethod
    def _update_execution(cursor: Any, execution: ReportExecution) -> None:
        cursor.execute(
            """
            UPDATE public.report_executions
            SET execution_status = %s, updated_at = %s, started_at = %s,
                completed_at = %s, flow_run_id = %s, callback_id = %s,
                snapshot_hash = %s, snapshot_payload = %s::jsonb, sources = %s::jsonb,
                warnings = %s::jsonb, error_code = %s,
                error_message = %s, events = %s::jsonb
            WHERE execution_id = %s::uuid;
            """,
            (
                execution.status.value,
                execution.updated_at,
                execution.started_at,
                execution.completed_at,
                execution.flow_run_id,
                execution.callback_id,
                execution.snapshot_hash,
                _json(execution.snapshot_payload) if execution.snapshot_payload else None,
                _json([item.model_dump(mode="json") for item in execution.sources]),
                _json(execution.warnings),
                execution.error_code,
                execution.error_message,
                _json([item.model_dump(mode="json") for item in execution.events]),
                execution.execution_id,
            ),
        )
        if cursor.rowcount == 0:
            raise ReportNotFoundError()

    @staticmethod
    def _upsert_artifact(
        cursor: Any, execution_id: str, artifact: ReportArtifact
    ) -> None:
        cursor.execute(
            """
            INSERT INTO public.generated_reports (
                artifact_id, execution_id, file_name, content_type, size_bytes,
                sha256, download_url, storage_provider, storage_reference, created_at
            ) VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (execution_id) DO UPDATE SET
                artifact_id = EXCLUDED.artifact_id,
                file_name = EXCLUDED.file_name,
                content_type = EXCLUDED.content_type,
                size_bytes = EXCLUDED.size_bytes,
                sha256 = EXCLUDED.sha256,
                download_url = EXCLUDED.download_url,
                storage_provider = EXCLUDED.storage_provider,
                storage_reference = EXCLUDED.storage_reference,
                created_at = EXCLUDED.created_at;
            """,
            (
                artifact.artifact_id,
                execution_id,
                artifact.file_name,
                artifact.content_type,
                artifact.size_bytes,
                artifact.sha256,
                artifact.download_url,
                artifact.storage_provider,
                artifact.storage_reference,
                artifact.created_at,
            ),
        )

    @staticmethod
    def _insert_audit(cursor: Any, execution: ReportExecution) -> None:
        if not execution.events:
            return
        event = execution.events[-1]
        cursor.execute(
            """
            INSERT INTO public.audit_events (
                event_type, component, event_status, event_payload,
                occurred_at, correlation_id
            ) VALUES (%s, %s, %s, %s::jsonb, %s, %s);
            """,
            (
                event.event_type,
                event.component,
                event.status,
                _json(
                    {
                        "execution_id": execution.execution_id,
                        "report_status": execution.status.value,
                        **event.payload,
                    }
                ),
                event.occurred_at,
                execution.correlation_id,
            ),
        )


@lru_cache(maxsize=1)
def get_report_repository() -> ReportRepository:
    mode = os.getenv("REPORT_REPOSITORY_MODE", "memory").strip().lower()
    if mode == "memory":
        return InMemoryReportRepository()
    if mode == "database":
        return PostgresReportRepository()
    raise ReportConfigurationError()


def reset_report_repository() -> None:
    get_report_repository.cache_clear()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def _is_unique_violation(error: Exception) -> bool:
    return getattr(error, "sqlstate", None) == "23505"


def _execution_from_rows(row: tuple, artifact_row: tuple | None) -> ReportExecution:
    from app.reports.schemas import ExecutionEvent, PreparedReport, ReportSource

    artifact = None
    if artifact_row:
        artifact = ReportArtifact(
            artifact_id=artifact_row[0],
            file_name=artifact_row[1],
            content_type=artifact_row[2],
            size_bytes=artifact_row[3],
            sha256=artifact_row[4],
            download_url=artifact_row[5],
            storage_provider=artifact_row[6],
            storage_reference=artifact_row[7],
            created_at=artifact_row[8],
        )
    return ReportExecution(
        execution_id=row[0],
        correlation_id=row[1],
        idempotency_key=row[2],
        requested_by=row[3],
        status=ReportStatus(row[4]),
        confirmation_hash=row[5],
        prepared_request=PreparedReport.model_validate(row[6]),
        created_at=row[7],
        updated_at=row[8],
        started_at=row[9],
        completed_at=row[10],
        flow_run_id=row[11],
        callback_id=row[12],
        snapshot_hash=row[13],
        snapshot_payload=row[14],
        sources=[ReportSource.model_validate(item) for item in (row[15] or [])],
        warnings=list(row[16] or []),
        error_code=row[17],
        error_message=row[18],
        events=[ExecutionEvent.model_validate(item) for item in (row[19] or [])],
        artifact=artifact,
    )
