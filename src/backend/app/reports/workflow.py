"""Workflow guiado de relatorio, independente de Copilot Studio."""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from threading import RLock
from typing import Any
from uuid import uuid4

from pydantic import ValidationError

from app.database.connection import open_database_connection
from app.reports.errors import (
    ReportAccessDeniedError,
    ReportConfigurationError,
    ReportConflictError,
    ReportError,
    ReportNotFoundError,
)
from app.reports.schemas import (
    AnswerWorkflowRequest,
    Audience,
    ConfirmWorkflowRequest,
    CreateReportRequest,
    Emphasis,
    Purpose,
    ReportOptions,
    ReportPeriod,
    ReportScope,
    ScopeType,
    StartWorkflowRequest,
    WorkflowAnswer,
    WorkflowOption,
    WorkflowQuestion,
    WorkflowSession,
    WorkflowSessionResponse,
    WorkflowStatus,
    WorkflowStep,
)
from app.reports.security import ReportIdentity, can_access_scope
from app.reports.service import ReportService, get_report_service
from app.reports.sources import SyntheticPortfolioSource


class WorkflowRepository(ABC):
    @abstractmethod
    def create(self, session: WorkflowSession) -> WorkflowSession: ...

    @abstractmethod
    def get(self, session_id: str) -> WorkflowSession: ...

    @abstractmethod
    def save(
        self, session: WorkflowSession, *, previous_revision: int
    ) -> WorkflowSession: ...


class InMemoryWorkflowRepository(WorkflowRepository):
    def __init__(self) -> None:
        self._sessions: dict[str, WorkflowSession] = {}
        self._lock = RLock()

    def create(self, session: WorkflowSession) -> WorkflowSession:
        with self._lock:
            self._sessions[session.session_id] = deepcopy(session)
        return deepcopy(session)

    def get(self, session_id: str) -> WorkflowSession:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise ReportNotFoundError()
            return deepcopy(session)

    def save(
        self, session: WorkflowSession, *, previous_revision: int
    ) -> WorkflowSession:
        with self._lock:
            current = self._sessions.get(session.session_id)
            if current is None:
                raise ReportNotFoundError()
            if current.revision != previous_revision:
                raise ReportConflictError(
                    "O workflow foi atualizado em outra solicitacao. Recarregue o estado."
                )
            self._sessions[session.session_id] = deepcopy(session)
        return deepcopy(session)


class PostgresWorkflowRepository(WorkflowRepository):
    def create(self, session: WorkflowSession) -> WorkflowSession:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO public.workflow_sessions (
                        session_id, workflow_name, requested_by, conversation_id,
                        interaction_id, correlation_id, workflow_status,
                        current_step, revision, session_payload, created_at, updated_at
                    ) VALUES (
                        %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s::jsonb, %s, %s
                    );
                    """,
                    self._values(session),
                )
                self._audit(cursor, session, "workflow.session.started")
            connection.commit()
            return session.model_copy(deep=True)
        except Exception as error:
            connection.rollback()
            raise ReportConfigurationError() from error
        finally:
            connection.close()

    def get(self, session_id: str) -> WorkflowSession:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT session_payload
                    FROM public.workflow_sessions
                    WHERE session_id = %s::uuid;
                    """,
                    (session_id,),
                )
                row = cursor.fetchone()
            if row is None:
                raise ReportNotFoundError()
            return WorkflowSession.model_validate(row[0])
        except ReportNotFoundError:
            raise
        except Exception as error:
            raise ReportConfigurationError() from error
        finally:
            connection.close()

    def save(
        self, session: WorkflowSession, *, previous_revision: int
    ) -> WorkflowSession:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE public.workflow_sessions
                    SET workflow_status = %s, current_step = %s, revision = %s,
                        session_payload = %s::jsonb, updated_at = %s
                    WHERE session_id = %s::uuid AND revision = %s;
                    """,
                    (
                        session.status.value,
                        session.current_step.value,
                        session.revision,
                        _json(session.model_dump(mode="json")),
                        session.updated_at,
                        session.session_id,
                        previous_revision,
                    ),
                )
                if cursor.rowcount == 0:
                    raise ReportConflictError(
                        "O workflow foi atualizado em outra solicitacao. Recarregue o estado."
                    )
                if session.answer_history:
                    answer = session.answer_history[-1]
                    cursor.execute(
                        """
                        INSERT INTO public.workflow_answers (
                            session_id, step, answer_payload, client_action_id, answered_at
                        ) VALUES (%s::uuid, %s, %s::jsonb, %s, %s)
                        ON CONFLICT (client_action_id) DO NOTHING;
                        """,
                        (
                            session.session_id,
                            answer.step.value,
                            _json(answer.value),
                            answer.client_action_id,
                            answer.answered_at,
                        ),
                    )
                self._audit(cursor, session, "workflow.session.updated")
            connection.commit()
            return session.model_copy(deep=True)
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
    def _values(session: WorkflowSession) -> tuple[Any, ...]:
        return (
            session.session_id,
            session.workflow,
            session.requested_by,
            session.conversation_id,
            session.interaction_id,
            session.correlation_id,
            session.status.value,
            session.current_step.value,
            session.revision,
            _json(session.model_dump(mode="json")),
            session.created_at,
            session.updated_at,
        )

    @staticmethod
    def _audit(cursor: Any, session: WorkflowSession, event_type: str) -> None:
        cursor.execute(
            """
            INSERT INTO public.audit_events (
                event_type, component, event_status, event_payload,
                occurred_at, correlation_id
            ) VALUES (%s, 'guided_workflow', %s, %s::jsonb, %s, %s);
            """,
            (
                event_type,
                "sucesso" if session.status != WorkflowStatus.CANCELLED else "bloqueado",
                _json(
                    {
                        "session_id": session.session_id,
                        "step": session.current_step.value,
                        "revision": session.revision,
                        "status": session.status.value,
                    }
                ),
                session.updated_at,
                session.correlation_id,
            ),
        )


class WorkflowService:
    def __init__(
        self,
        repository: WorkflowRepository,
        report_service: ReportService | None = None,
        source: object | None = None,
    ) -> None:
        self.repository = repository
        self.report_service = report_service or get_report_service()
        # Usa a mesma fonte de portfolio do ReportService (selecionada por
        # REPORT_PORTFOLIO_SOURCE). Fixar SyntheticPortfolioSource aqui faria o
        # card listar escopos de uma fonte diferente da que gera o relatorio.
        self.source = source or self.report_service.source

    def start(
        self, request: StartWorkflowRequest, identity: ReportIdentity
    ) -> WorkflowSessionResponse:
        if not identity.can_export:
            raise ReportAccessDeniedError()
        now = _now()
        session = WorkflowSession(
            session_id=str(uuid4()),
            requested_by=identity.subject,
            conversation_id=request.conversation_id,
            interaction_id=request.interaction_id,
            correlation_id=str(uuid4()),
            created_at=now,
            updated_at=now,
        )
        self.repository.create(session)
        return self.response(session, identity)

    def get(self, session_id: str, identity: ReportIdentity) -> WorkflowSessionResponse:
        session = self._authorized(session_id, identity)
        if session.execution_id:
            execution = self.report_service.get(session.execution_id, identity)
            if execution.status.value in {
                "completed",
                "completed_with_warnings",
                "failed",
                "blocked",
                "cancelled",
            } and session.status != WorkflowStatus.COMPLETED:
                previous = session.revision
                session.status = WorkflowStatus.COMPLETED
                session.updated_at = _now()
                session.revision += 1
                session = self.repository.save(session, previous_revision=previous)
        return self.response(session, identity)

    def answer(
        self,
        session_id: str,
        request: AnswerWorkflowRequest,
        identity: ReportIdentity,
    ) -> WorkflowSessionResponse:
        session = self._authorized(session_id, identity)
        if any(
            item.client_action_id == request.client_action_id
            for item in session.answer_history
        ):
            return self.response(session, identity)
        if session.status != WorkflowStatus.ACTIVE:
            raise ReportConflictError("O workflow nao aceita novas respostas.")
        if request.revision != session.revision or request.step != session.current_step:
            raise ReportConflictError(
                "A etapa informada nao corresponde ao estado atual do workflow."
            )

        value = self._validate_answer(session, request.step, request.value, identity)
        previous = session.revision
        session.answers[request.step.value] = value
        session.answer_history.append(
            WorkflowAnswer(
                step=request.step,
                value=value,
                client_action_id=request.client_action_id,
                answered_at=_now(),
            )
        )
        session.current_step = _next_step(request.step)
        session.revision += 1
        session.updated_at = _now()
        if session.current_step == WorkflowStep.CONFIRMATION:
            prepared = self.report_service.prepare(
                self._prepare_request(session), identity
            )
            session.prepared = prepared
            session.status = WorkflowStatus.READY_FOR_CONFIRMATION
        session = self.repository.save(session, previous_revision=previous)
        return self.response(session, identity)

    def confirm(
        self,
        session_id: str,
        request: ConfirmWorkflowRequest,
        identity: ReportIdentity,
    ) -> tuple[WorkflowSessionResponse, bool]:
        session = self._authorized(session_id, identity)
        if session.execution_id:
            return self.response(session, identity), False
        if (
            session.status != WorkflowStatus.READY_FOR_CONFIRMATION
            or session.prepared is None
            or request.revision != session.revision
        ):
            raise ReportConflictError("Revise o workflow antes de confirmar.")
        execution, created = self.report_service.create(
            CreateReportRequest(
                prepared_request=session.prepared.prepared_request,
                confirmation_hash=session.prepared.confirmation_hash,
                # A confirmacao da sessao e uma unica operacao logica. O ID do
                # cliente identifica repeticoes HTTP, mas nao pode criar duas
                # execucoes para a mesma sessao em uma corrida concorrente.
                idempotency_key=f"workflow:{session.session_id}:confirm",
            ),
            identity,
        )
        previous = session.revision
        session.execution_id = execution.execution_id
        session.status = WorkflowStatus.EXECUTING
        session.current_step = WorkflowStep.EXECUTION
        session.revision += 1
        session.updated_at = _now()
        session = self.repository.save(session, previous_revision=previous)
        return self.response(session, identity), created

    def cancel(self, session_id: str, identity: ReportIdentity) -> WorkflowSessionResponse:
        session = self._authorized(session_id, identity)
        if session.execution_id:
            raise ReportConflictError("A execucao confirmada nao pode ser cancelada por esta rota.")
        if session.status == WorkflowStatus.CANCELLED:
            return self.response(session, identity)
        previous = session.revision
        session.status = WorkflowStatus.CANCELLED
        session.revision += 1
        session.updated_at = _now()
        session = self.repository.save(session, previous_revision=previous)
        return self.response(session, identity)

    def response(
        self, session: WorkflowSession, identity: ReportIdentity
    ) -> WorkflowSessionResponse:
        execution = None
        if session.execution_id:
            execution = self.report_service.response(
                self.report_service.get(session.execution_id, identity)
            )
        warnings = list(session.prepared.warnings if session.prepared else [])
        if execution:
            warnings.extend(item for item in execution.warnings if item not in warnings)
        return WorkflowSessionResponse(
            session_id=session.session_id,
            workflow=session.workflow,
            status=session.status,
            current_step=session.current_step,
            revision=session.revision,
            question=self._question(session, identity),
            answers=deepcopy(session.answers),
            confirmation_summary=(
                session.prepared.confirmation_summary if session.prepared else None
            ),
            warnings=warnings,
            execution=execution,
        )

    def _authorized(self, session_id: str, identity: ReportIdentity) -> WorkflowSession:
        session = self.repository.get(session_id)
        if session.requested_by != identity.subject:
            raise ReportAccessDeniedError()
        return session

    def _question(
        self, session: WorkflowSession, identity: ReportIdentity
    ) -> WorkflowQuestion | None:
        if session.status != WorkflowStatus.ACTIVE:
            return None
        step = session.current_step
        if step == WorkflowStep.SCOPE_TYPE:
            return WorkflowQuestion(
                step=step,
                prompt="O relatorio deve abranger um projeto ou um subportfolio?",
                input_type="single_select",
                options=[
                    WorkflowOption(value="project", label="Projeto"),
                    WorkflowOption(value="subportfolio", label="Subportfolio"),
                ],
            )
        if step == WorkflowStep.SCOPE:
            scope_type = ScopeType(session.answers[WorkflowStep.SCOPE_TYPE.value])
            options = [
                WorkflowOption(
                    value=item["id"],
                    label=f"{item.get('code') or item['id']} - {item['title']}",
                )
                for item in self.source.list_scopes(scope_type)
                if can_access_scope(identity, scope_type, item["id"])
            ]
            return WorkflowQuestion(
                step=step,
                prompt="Selecione o escopo autorizado para o relatorio.",
                input_type="single_select",
                options=options,
            )
        definitions: dict[WorkflowStep, WorkflowQuestion] = {
            WorkflowStep.PERIOD: WorkflowQuestion(
                step=step,
                prompt="Informe o inicio e o fim do periodo de referencia.",
                input_type="date_range",
            ),
            WorkflowStep.AUDIENCE: WorkflowQuestion(
                step=step,
                prompt="Quem e o publico principal do relatorio?",
                input_type="single_select",
                options=[
                    WorkflowOption(value="executive_board", label="Diretoria"),
                    WorkflowOption(value="pmo", label="PMO"),
                    WorkflowOption(value="project_team", label="Equipe do projeto"),
                ],
            ),
            WorkflowStep.PURPOSE: WorkflowQuestion(
                step=step,
                prompt="Qual e a finalidade principal?",
                input_type="single_select",
                options=[
                    WorkflowOption(value="monthly_governance", label="Governanca mensal"),
                    WorkflowOption(value="decision_support", label="Apoio a decisao"),
                    WorkflowOption(value="status_communication", label="Comunicacao de status"),
                ],
            ),
            WorkflowStep.EMPHASIS: WorkflowQuestion(
                step=step,
                prompt="Quais temas devem receber enfase?",
                input_type="multi_select",
                required=False,
                options=[
                    WorkflowOption(value=value.value, label=label)
                    for value, label in (
                        (Emphasis.SCHEDULE, "Cronograma"),
                        (Emphasis.RISKS, "Riscos"),
                        (Emphasis.BENEFITS, "Beneficios"),
                        (Emphasis.CHANGES, "Mudancas"),
                        (Emphasis.MILESTONES, "Marcos"),
                    )
                ],
            ),
            WorkflowStep.ADDITIONAL_CONTEXT: WorkflowQuestion(
                step=step,
                prompt="Deseja acrescentar algum contexto? Esta etapa e opcional.",
                input_type="text",
                required=False,
            ),
        }
        return definitions.get(step)

    def _validate_answer(
        self,
        session: WorkflowSession,
        step: WorkflowStep,
        value: Any,
        identity: ReportIdentity,
    ) -> Any:
        try:
            if step == WorkflowStep.SCOPE_TYPE:
                return ScopeType(value).value
            if step == WorkflowStep.SCOPE:
                scope_type = ScopeType(session.answers[WorkflowStep.SCOPE_TYPE.value])
                scope = ReportScope(type=scope_type, id=str(value))
                if not can_access_scope(identity, scope.type, scope.id):
                    raise ReportAccessDeniedError()
                self.source.scope_metadata(scope.type, scope.id)
                return scope.id
            if step == WorkflowStep.PERIOD:
                return ReportPeriod.model_validate(value).model_dump(mode="json")
            if step == WorkflowStep.AUDIENCE:
                return Audience(value).value
            if step == WorkflowStep.PURPOSE:
                return Purpose(value).value
            if step == WorkflowStep.EMPHASIS:
                if value is None:
                    return []
                if not isinstance(value, list):
                    raise ValueError
                return [item.value for item in dict.fromkeys(Emphasis(v) for v in value)]
            if step == WorkflowStep.ADDITIONAL_CONTEXT:
                if value is not None and not isinstance(value, str):
                    raise ValueError
                options = ReportOptions(
                    audience=Audience(session.answers[WorkflowStep.AUDIENCE.value]),
                    purpose=Purpose(session.answers[WorkflowStep.PURPOSE.value]),
                    emphasis=session.answers[WorkflowStep.EMPHASIS.value],
                    additional_context=value,
                )
                return options.additional_context
        except (ValueError, TypeError, ValidationError) as error:
            raise ReportError(
                "REPORT_INVALID_INPUT",
                "A resposta nao corresponde as opcoes permitidas para esta etapa.",
                422,
            ) from error
        raise ReportConflictError("A etapa informada nao aceita resposta.")

    @staticmethod
    def _prepare_request(session: WorkflowSession):
        from app.reports.schemas import PrepareReportRequest

        return PrepareReportRequest(
            conversation_id=session.conversation_id,
            interaction_id=session.interaction_id,
            correlation_id=session.correlation_id,
            scope={
                "type": session.answers[WorkflowStep.SCOPE_TYPE.value],
                "id": session.answers[WorkflowStep.SCOPE.value],
            },
            period=session.answers[WorkflowStep.PERIOD.value],
            options={
                "audience": session.answers[WorkflowStep.AUDIENCE.value],
                "purpose": session.answers[WorkflowStep.PURPOSE.value],
                "emphasis": session.answers[WorkflowStep.EMPHASIS.value],
                "additional_context": session.answers.get(
                    WorkflowStep.ADDITIONAL_CONTEXT.value
                ),
                "output_format": "docx",
            },
        )


@lru_cache(maxsize=1)
def get_workflow_repository() -> WorkflowRepository:
    mode = os.getenv("REPORT_REPOSITORY_MODE", "memory").strip().lower()
    if mode == "memory":
        return InMemoryWorkflowRepository()
    if mode == "database":
        return PostgresWorkflowRepository()
    raise ReportConfigurationError()


@lru_cache(maxsize=1)
def get_workflow_service() -> WorkflowService:
    return WorkflowService(get_workflow_repository())


def reset_workflow_service() -> None:
    get_workflow_service.cache_clear()
    get_workflow_repository.cache_clear()


def _next_step(step: WorkflowStep) -> WorkflowStep:
    order = [
        WorkflowStep.SCOPE_TYPE,
        WorkflowStep.SCOPE,
        WorkflowStep.PERIOD,
        WorkflowStep.AUDIENCE,
        WorkflowStep.PURPOSE,
        WorkflowStep.EMPHASIS,
        WorkflowStep.ADDITIONAL_CONTEXT,
        WorkflowStep.CONFIRMATION,
    ]
    try:
        return order[order.index(step) + 1]
    except (ValueError, IndexError) as error:
        raise ReportConflictError("Nao existe proxima etapa para o workflow.") from error


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
