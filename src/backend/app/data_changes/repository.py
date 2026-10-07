"""Persistencia transacional da alteracao pelo chat.

O servico enxerga uma unica interface, `DataChangeUnitOfWork`, aberta por
`repository.transaction()`. Tudo o que acontece dentro do bloco e gravado junto
ou desfeito junto, como pede o principio "tudo ou nada" do contrato.

- `PostgresDataChangeRepository`: uma conexao por transacao, com
  `SELECT ... FOR UPDATE` no registro alterado e na previa.
- `InMemoryDataChangeRepository`: a mesma semantica para os testes, com trava
  global e restauracao do estado anterior quando o bloco falha.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from threading import RLock
from typing import Any, Protocol
from uuid import uuid4

from app.data_changes.fields import ENTITIES, FIELDS


@dataclass
class Project:
    id: str
    code: str
    title: str
    subportfolio_id: str | None


@dataclass
class TargetRecord:
    entity: str
    id: str
    project_id: str
    label: str
    values: dict[str, Any]


@dataclass
class PendingChange:
    id: str
    user_id: str
    correlation_id: str
    project_id: str
    entity: str
    target_id: str
    field_key: str
    before: str | None
    after: str | None
    expires_at: datetime
    created_at: datetime
    external_conversation_id: str | None = None
    interaction_id: str | None = None
    status: str = "pendente"
    change_record_id: str | None = None
    reason: str | None = None
    decided_at: datetime | None = None


@dataclass
class ChangeRecord:
    id: str
    project_id: str
    change_type: str
    title: str
    impact_summary: str
    requested_by: str
    status: str
    registration_date: Any
    decided_at: datetime
    metadata: dict[str, Any]
    reason: str | None = None


@dataclass
class AuditEvent:
    event_type: str
    event_status: str
    payload: dict[str, Any]
    user_id: str | None
    correlation_id: str | None
    interaction_id: str | None = None
    component: str = "api"


class DataChangeUnitOfWork(Protocol):
    def project_by_code(self, code: str) -> Project | None: ...
    def project_by_id(self, project_id: str) -> Project | None: ...
    def list_targets(self, entity: str, project_id: str) -> list[tuple[str, str]]: ...
    def get_target(self, entity: str, target_id: str, *, lock: bool = False) -> TargetRecord | None: ...
    def update_target(self, entity: str, target_id: str, column: str, value: Any) -> None: ...
    def insert_pending(self, pending: PendingChange) -> None: ...
    def get_pending(self, pending_id: str, *, lock: bool = False) -> PendingChange | None: ...
    def save_pending(self, pending: PendingChange) -> None: ...
    def insert_change_record(self, record: ChangeRecord) -> None: ...
    def get_change_record(self, change_id: str, *, lock: bool = False) -> ChangeRecord | None: ...
    def save_change_record(self, record: ChangeRecord) -> None: ...
    def list_change_records(
        self, project_id: str, field_key: str, target_id: str | None, limit: int
    ) -> list[ChangeRecord]: ...
    def insert_audit(self, event: AuditEvent) -> None: ...
    def attach_interaction(self, correlation_id: str, interaction_id: str) -> None: ...


class DataChangeRepository(Protocol):
    def transaction(self) -> Any: ...


# --------------------------------------------------------------------------
# Em memoria (testes)
# --------------------------------------------------------------------------


@dataclass
class _MemoryState:
    projects: dict[str, Project] = field(default_factory=dict)
    targets: dict[str, dict[str, TargetRecord]] = field(
        default_factory=lambda: {entity: {} for entity in ENTITIES}
    )
    pending: dict[str, PendingChange] = field(default_factory=dict)
    change_records: dict[str, ChangeRecord] = field(default_factory=dict)
    audit: list[AuditEvent] = field(default_factory=list)


class InMemoryDataChangeRepository:
    """Repositorio de testes com a mesma garantia de tudo ou nada."""

    def __init__(self) -> None:
        self.state = _MemoryState()
        self._lock = RLock()
        #: Permite simular falha no meio da transacao (ex.: na auditoria).
        self.fail_on: str | None = None

    def add_project(self, project: Project, values: dict[str, Any]) -> None:
        self.state.projects[project.id] = project
        self.state.targets["projeto"][project.id] = TargetRecord(
            "projeto", project.id, project.id, project.code, dict(values)
        )

    def add_target(self, entity: str, target_id: str, project_id: str, label: str, values: dict[str, Any]) -> None:
        self.state.targets[entity][target_id] = TargetRecord(entity, target_id, project_id, label, dict(values))

    @contextmanager
    def transaction(self) -> Iterator["_MemoryUnitOfWork"]:
        with self._lock:
            snapshot = copy.deepcopy(self.state)
            try:
                yield _MemoryUnitOfWork(self)
            except BaseException:
                self.state = snapshot
                raise


class _MemoryUnitOfWork:
    def __init__(self, repository: InMemoryDataChangeRepository) -> None:
        self._repo = repository

    @property
    def _state(self) -> _MemoryState:
        return self._repo.state

    def _maybe_fail(self, operation: str) -> None:
        if self._repo.fail_on == operation:
            raise RuntimeError(f"falha simulada em {operation}")

    def project_by_code(self, code: str) -> Project | None:
        return next(
            (copy.copy(p) for p in self._state.projects.values() if p.code.upper() == code.upper()),
            None,
        )

    def project_by_id(self, project_id: str) -> Project | None:
        project = self._state.projects.get(project_id)
        return copy.copy(project) if project else None

    def list_targets(self, entity: str, project_id: str) -> list[tuple[str, str]]:
        return sorted(
            ((t.id, t.label) for t in self._state.targets[entity].values() if t.project_id == project_id),
            key=lambda item: item[1],
        )

    def get_target(self, entity: str, target_id: str, *, lock: bool = False) -> TargetRecord | None:
        record = self._state.targets[entity].get(target_id)
        return copy.deepcopy(record) if record else None

    def update_target(self, entity: str, target_id: str, column: str, value: Any) -> None:
        self._maybe_fail("update_target")
        self._state.targets[entity][target_id].values[column] = value

    def insert_pending(self, pending: PendingChange) -> None:
        self._state.pending[pending.id] = copy.deepcopy(pending)

    def get_pending(self, pending_id: str, *, lock: bool = False) -> PendingChange | None:
        pending = self._state.pending.get(pending_id)
        return copy.deepcopy(pending) if pending else None

    def save_pending(self, pending: PendingChange) -> None:
        self._state.pending[pending.id] = copy.deepcopy(pending)

    def insert_change_record(self, record: ChangeRecord) -> None:
        self._maybe_fail("insert_change_record")
        self._state.change_records[record.id] = copy.deepcopy(record)

    def get_change_record(self, change_id: str, *, lock: bool = False) -> ChangeRecord | None:
        record = self._state.change_records.get(change_id)
        return copy.deepcopy(record) if record else None

    def save_change_record(self, record: ChangeRecord) -> None:
        self._state.change_records[record.id] = copy.deepcopy(record)

    def list_change_records(
        self, project_id: str, field_key: str, target_id: str | None, limit: int
    ) -> list[ChangeRecord]:
        records = [
            copy.deepcopy(record)
            for record in self._state.change_records.values()
            if record.project_id == project_id
            and record.metadata.get("origin") == "chat"
            and record.metadata.get("field") == field_key
            and (target_id is None or record.metadata.get("target_id") == target_id)
        ]
        return sorted(records, key=lambda record: record.decided_at, reverse=True)[:limit]

    def insert_audit(self, event: AuditEvent) -> None:
        self._maybe_fail(f"audit:{event.event_type}")
        self._state.audit.append(copy.deepcopy(event))

    def attach_interaction(self, correlation_id: str, interaction_id: str) -> None:
        for event in self._state.audit:
            if event.correlation_id == correlation_id and event.interaction_id is None:
                event.interaction_id = interaction_id
        for pending in self._state.pending.values():
            if pending.correlation_id == correlation_id and pending.interaction_id is None:
                pending.interaction_id = interaction_id


# --------------------------------------------------------------------------
# PostgreSQL
# --------------------------------------------------------------------------


class PostgresDataChangeRepository:
    """Uma conexao por transacao; commit no fim do bloco, rollback na falha."""

    def __init__(self, open_connection: Callable[[], Any] | None = None) -> None:
        if open_connection is None:
            from app.database.connection import open_database_connection

            open_connection = open_database_connection
        self._open_connection = open_connection

    @contextmanager
    def transaction(self) -> Iterator["_PostgresUnitOfWork"]:
        connection = self._open_connection()
        try:
            with connection.cursor() as cursor:
                yield _PostgresUnitOfWork(cursor)
            connection.commit()
        except BaseException:
            try:
                connection.rollback()
            except Exception:
                pass
            raise
        finally:
            connection.close()


_PENDING_COLUMNS = (
    "id::text, user_id::text, correlation_id, project_id::text, entity, target_id::text, "
    "field_key, before_value, after_value, expires_at, created_at, external_conversation_id, "
    "interaction_id::text, status, change_record_id::text, reason, decided_at"
)
_CHANGE_COLUMNS = (
    "id::text, project_id::text, change_type, title, impact_summary, requested_by, status, "
    "registration_date, decided_at, metadata, reason"
)


class _PostgresUnitOfWork:
    def __init__(self, cursor: Any) -> None:
        self._cursor = cursor

    def _one(self, sql: str, params: tuple[Any, ...]) -> tuple[Any, ...] | None:
        self._cursor.execute(sql, params)
        return self._cursor.fetchone()

    def project_by_code(self, code: str) -> Project | None:
        row = self._one(
            "SELECT id::text, code, title, subportfolio_id::text FROM public.projects "
            "WHERE upper(code) = upper(%s)",
            (code,),
        )
        return Project(*row) if row else None

    def project_by_id(self, project_id: str) -> Project | None:
        row = self._one(
            "SELECT id::text, code, title, subportfolio_id::text FROM public.projects WHERE id = %s",
            (project_id,),
        )
        return Project(*row) if row else None

    def list_targets(self, entity: str, project_id: str) -> list[tuple[str, str]]:
        spec = ENTITIES[entity]
        where = f"{spec.project_column} = %s" + (f" AND {spec.extra_where}" if spec.extra_where else "")
        self._cursor.execute(
            f"SELECT id::text, {spec.label_sql} FROM public.{spec.table} WHERE {where} ORDER BY 2",
            (project_id,),
        )
        return [(str(row[0]), str(row[1] or "")) for row in self._cursor.fetchall()]

    def get_target(self, entity: str, target_id: str, *, lock: bool = False) -> TargetRecord | None:
        spec = ENTITIES[entity]
        where = "id = %s" + (f" AND {spec.extra_where}" if spec.extra_where else "")
        columns = ", ".join(spec.columns)
        row = self._one(
            f"SELECT id::text, {spec.project_column}::text, {spec.label_sql}, {columns} "
            f"FROM public.{spec.table} WHERE {where}" + (" FOR UPDATE" if lock else ""),
            (target_id,),
        )
        if row is None:
            return None
        values = dict(zip(spec.columns, row[3:]))
        return TargetRecord(entity, str(row[0]), str(row[1]), str(row[2] or ""), values)

    def update_target(self, entity: str, target_id: str, column: str, value: Any) -> None:
        spec = ENTITIES[entity]
        # A coluna vem sempre da tabela de campos do contrato, nunca do usuario.
        if not any(f.entity == entity and f.column == column for f in FIELDS.values()):
            raise ValueError("Coluna fora do contrato.")
        self._cursor.execute(
            f"UPDATE public.{spec.table} SET {column} = %s WHERE id = %s",
            (value, target_id),
        )

    def insert_pending(self, pending: PendingChange) -> None:
        self._cursor.execute(
            """
            INSERT INTO public.pending_data_changes (
                id, user_id, correlation_id, project_id, entity, target_id, field_key,
                before_value, after_value, expires_at, created_at, external_conversation_id,
                interaction_id, status, reason
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s, %s)
            """,
            (
                pending.id, pending.user_id, pending.correlation_id, pending.project_id,
                pending.entity, pending.target_id, pending.field_key,
                json.dumps(pending.before), json.dumps(pending.after),
                pending.expires_at, pending.created_at, pending.external_conversation_id,
                pending.interaction_id, pending.status, pending.reason,
            ),
        )

    def get_pending(self, pending_id: str, *, lock: bool = False) -> PendingChange | None:
        row = self._one(
            f"SELECT {_PENDING_COLUMNS} FROM public.pending_data_changes WHERE id = %s"
            + (" FOR UPDATE" if lock else ""),
            (pending_id,),
        )
        if row is None:
            return None
        return PendingChange(
            id=row[0], user_id=row[1], correlation_id=row[2], project_id=row[3],
            entity=row[4], target_id=row[5], field_key=row[6],
            before=_canonical(row[7]), after=_canonical(row[8]),
            expires_at=row[9], created_at=row[10], external_conversation_id=row[11],
            interaction_id=row[12], status=row[13], change_record_id=row[14],
            reason=row[15], decided_at=row[16],
        )

    def save_pending(self, pending: PendingChange) -> None:
        self._cursor.execute(
            """
            UPDATE public.pending_data_changes
               SET status = %s, change_record_id = %s, reason = %s, decided_at = %s,
                   interaction_id = COALESCE(interaction_id, %s)
             WHERE id = %s
            """,
            (
                pending.status, pending.change_record_id, pending.reason, pending.decided_at,
                pending.interaction_id, pending.id,
            ),
        )

    def insert_change_record(self, record: ChangeRecord) -> None:
        self._cursor.execute(
            """
            INSERT INTO public.change_records (
                id, scope_type, project_id, change_type, title, source_label, reason,
                impact_summary, requested_by, status, registration_date, requested_at,
                decided_at, metadata
            ) VALUES (%s, 'projeto', %s, %s, %s, 'chat', %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            """,
            (
                record.id, record.project_id, record.change_type, record.title, record.reason,
                record.impact_summary, record.requested_by, record.status,
                record.registration_date, record.decided_at, record.decided_at,
                json.dumps(record.metadata, ensure_ascii=False, default=str),
            ),
        )

    def get_change_record(self, change_id: str, *, lock: bool = False) -> ChangeRecord | None:
        row = self._one(
            f"SELECT {_CHANGE_COLUMNS} FROM public.change_records "
            "WHERE id = %s AND metadata->>'origin' = 'chat'" + (" FOR UPDATE" if lock else ""),
            (change_id,),
        )
        return _change_record(row) if row else None

    def save_change_record(self, record: ChangeRecord) -> None:
        self._cursor.execute(
            "UPDATE public.change_records SET status = %s, metadata = %s::jsonb WHERE id = %s",
            (record.status, json.dumps(record.metadata, ensure_ascii=False, default=str), record.id),
        )

    def list_change_records(
        self, project_id: str, field_key: str, target_id: str | None, limit: int
    ) -> list[ChangeRecord]:
        sql = (
            f"SELECT {_CHANGE_COLUMNS} FROM public.change_records "
            "WHERE project_id = %s AND metadata->>'origin' = 'chat' AND metadata->>'field' = %s"
        )
        params: list[Any] = [project_id, field_key]
        if target_id:
            sql += " AND metadata->>'target_id' = %s"
            params.append(target_id)
        sql += " ORDER BY decided_at DESC LIMIT %s"
        params.append(limit)
        self._cursor.execute(sql, tuple(params))
        return [_change_record(row) for row in self._cursor.fetchall()]

    def insert_audit(self, event: AuditEvent) -> None:
        self._cursor.execute(
            """
            INSERT INTO public.audit_events (
                interaction_id, user_id, event_type, component, event_status,
                event_payload, correlation_id
            ) VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s)
            """,
            (
                event.interaction_id, event.user_id, event.event_type, event.component,
                event.event_status, json.dumps(event.payload, ensure_ascii=False, default=str),
                event.correlation_id,
            ),
        )

    def attach_interaction(self, correlation_id: str, interaction_id: str) -> None:
        self._cursor.execute(
            "UPDATE public.audit_events SET interaction_id = %s "
            "WHERE correlation_id = %s AND interaction_id IS NULL",
            (interaction_id, correlation_id),
        )
        self._cursor.execute(
            "UPDATE public.pending_data_changes SET interaction_id = %s "
            "WHERE correlation_id = %s AND interaction_id IS NULL",
            (interaction_id, correlation_id),
        )


def _canonical(value: Any) -> str | None:
    """O psycopg ja decodifica o JSONB; o valor canonico e sempre texto."""

    return None if value is None else str(value)


def _change_record(row: tuple[Any, ...]) -> ChangeRecord:
    metadata = row[9] if isinstance(row[9], dict) else json.loads(row[9] or "{}")
    return ChangeRecord(
        id=row[0], project_id=row[1], change_type=row[2], title=row[3],
        impact_summary=row[4] or "", requested_by=row[5] or "", status=row[6],
        registration_date=row[7], decided_at=row[8], metadata=metadata, reason=row[10],
    )


def new_id() -> str:
    return str(uuid4())
