"""Previa, confirmacao, cancelamento, desfazer e historico (S5-06).

Implementa o contrato da Secao 8.5.13 do Projeto.md:

- a mensagem do chat so produz uma previa; a escrita acontece apenas na
  confirmacao, chamada pelo cartao;
- a permissao vem da regra que cobre o projeto e e verificada na previa, na
  confirmacao e no desfazer;
- o novo valor, `change_records` e `audit_events` sao gravados na mesma
  transacao;
- recusas nao gravam nada no registro do projeto, apenas o evento de auditoria.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from app.data_changes import errors
from app.data_changes.errors import DataChangeError
from app.data_changes.extractor import ExtractedChange
from app.data_changes.fields import (
    ENTITIES,
    FIELDS,
    FieldSpec,
    InvalidValueError,
    STATUS_LABELS,
    canonical,
    display,
    fold,
    parse_value,
    typed_from_canonical,
    validate,
)
from app.data_changes.repository import (
    AuditEvent,
    ChangeRecord,
    DataChangeRepository,
    PendingChange,
    PostgresDataChangeRepository,
    Project,
    TargetRecord,
)
from app.data_changes.schemas import (
    DATA_CHANGE_CONTRACT,
    CancelResponse,
    Candidate,
    ConfirmResponse,
    DataChangeDraft,
    DataChangeOutcome,
    DataChangePreview,
    FieldRef,
    HistoryItem,
    HistoryResponse,
    PreviewRequest,
    ProjectRef,
    TargetView,
    UndoResponse,
    ValueView,
)
from app.security.access import (
    AccessContext,
    OutOfScopeForProfileError,
    authorize_operation,
    authorize_project_write,
)
from app.security.sensitive_data import describe_categories, scan

logger = logging.getLogger(__name__)

PREVIEW_TTL = timedelta(minutes=10)
UNDO_WINDOW = timedelta(minutes=15)
LOCAL_TIMEZONE = ZoneInfo("America/Sao_Paulo")
HISTORY_LIMIT = 20
MAX_CANDIDATES = 5

EDITABLE_FIELDS_TEXT = (
    "status e prazo final do projeto; prazo, status e progresso de atividades; "
    "data prevista, status e data de conclusão de marcos; status, responsável e prazo de riscos"
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class HandledMessage:
    outcome: DataChangeOutcome
    correlation_id: str | None
    text: str


class DataChangeService:
    def __init__(
        self,
        repository: DataChangeRepository,
        *,
        now: Callable[[], datetime] = _utcnow,
        preview_ttl: timedelta = PREVIEW_TTL,
        undo_window: timedelta = UNDO_WINDOW,
    ) -> None:
        self.repository = repository
        self._now = now
        self.preview_ttl = preview_ttl
        self.undo_window = undo_window

    # ------------------------------------------------------------------
    # Entrada pelo chat
    # ------------------------------------------------------------------

    def today(self) -> date:
        return self._now().astimezone(LOCAL_TIMEZONE).date()

    def handle_message(
        self,
        extracted: ExtractedChange,
        context: AccessContext,
        *,
        conversation_id: str | None = None,
    ) -> HandledMessage:
        """Transforma o pedido reconhecido em previa, pergunta ou recusa."""

        correlation_id = str(uuid4())
        draft = DataChangeDraft(
            project_code=extracted.project_code,
            entity=extracted.entity,  # type: ignore[arg-type]
            field=extracted.field,
            item_reference=extracted.item_reference,
            raw_value=extracted.raw_value,
        )
        if extracted.problem:
            outcome = self._run(lambda uow: self._reject_problem(uow, extracted.problem, draft, context, correlation_id))
        else:
            outcome = self._run(
                lambda uow: self._prepare(
                    uow, draft, context,
                    conversation_id=conversation_id,
                    correlation_id=correlation_id,
                    missing_day=extracted.missing_day,
                )
            )
        return HandledMessage(outcome, correlation_id, outcome_text(outcome))

    def create_preview(
        self,
        request: PreviewRequest,
        context: AccessContext,
    ) -> DataChangeOutcome:
        """Rota do cartao: cria a previa com a proposta completa."""

        spec = FIELDS.get(request.field)
        if spec is not None and request.entity is not None and request.entity != spec.entity:
            raise DataChangeError(
                "DATA_CHANGE_INVALID_INPUT",
                "O campo informado não pertence ao tipo de registro escolhido.",
                422,
            )
        draft = DataChangeDraft(
            project_code=request.project_code,
            entity=spec.entity if spec else None,
            field=request.field,
            target_id=request.target_id,
            item_reference=request.item_reference,
            raw_value=request.raw_value,
        )
        correlation_id = str(uuid4())
        outcome = self._run(
            lambda uow: self._prepare(
                uow, draft, context,
                conversation_id=request.conversation_id,
                correlation_id=correlation_id,
                readable_only=True,
            )
        )
        if outcome.status == "rejected":
            raise DataChangeError(outcome.code or "INVALID_VALUE", outcome.message or "", _status_for(outcome.code))
        return outcome

    def attach_interaction(self, correlation_id: str, interaction_id: str) -> None:
        """Liga previa e eventos a interacao registrada pelo rastreamento."""

        try:
            with self.repository.transaction() as uow:
                uow.attach_interaction(correlation_id, interaction_id)
        except Exception:
            logger.warning("Falha controlada ao ligar a alteracao a interacao.")

    # ------------------------------------------------------------------
    # Confirmacao, cancelamento e desfazer
    # ------------------------------------------------------------------

    def confirm(self, pending_id: str, context: AccessContext, reason: str | None = None) -> ConfirmResponse:
        reason = _clean_reason(reason)
        return self._run(lambda uow: self._confirm(uow, pending_id, context, reason), raise_failure=True)

    def cancel(self, pending_id: str, context: AccessContext) -> CancelResponse:
        return self._run(lambda uow: self._cancel(uow, pending_id, context), raise_failure=True)

    def undo(self, change_id: str, context: AccessContext) -> UndoResponse:
        return self._run(lambda uow: self._undo(uow, change_id, context), raise_failure=True)

    def history(
        self,
        project_code: str,
        field_key: str,
        target_id: str | None,
        context: AccessContext,
    ) -> HistoryResponse:
        spec = FIELDS.get(field_key)
        if spec is None:
            raise errors.field_not_editable(EDITABLE_FIELDS_TEXT)

        def run(uow: Any) -> HistoryResponse:
            project = uow.project_by_code(project_code)
            if project is None:
                raise errors.target_not_found("O projeto informado não foi encontrado.")
            try:
                authorize_operation(context, "read", project_id=project.code)
            except OutOfScopeForProfileError as error:
                raise errors.out_of_scope(project.code) from error
            now = self._now()
            items = []
            for record in uow.list_change_records(project.id, field_key, target_id, HISTORY_LIMIT):
                metadata = record.metadata
                applied_at = _parse_datetime(metadata.get("applied_at")) or record.decided_at
                undone = metadata.get("undo") or None
                deadline = applied_at + self.undo_window
                can_undo = (
                    undone is None
                    and record.status == "implementada"
                    and metadata.get("user_id") == str(context.user_id)
                    and now <= deadline
                )
                items.append(
                    HistoryItem(
                        change_id=record.id,
                        field=FieldRef(key=spec.key, label=spec.label),
                        target=TargetView(
                            entity=spec.entity,
                            id=str(metadata.get("target_id")),
                            label=str(metadata.get("target_label") or ""),
                        ),
                        before=ValueView(value=metadata.get("before"), display=display(spec, metadata.get("before"))),
                        after=ValueView(value=metadata.get("after"), display=display(spec, metadata.get("after"))),
                        requested_by=record.requested_by,
                        applied_at=applied_at,
                        status="desfeita" if undone else "aplicada",
                        undone_at=_parse_datetime(undone.get("undone_at")) if undone else None,
                        can_undo=can_undo,
                        undo_available_until=deadline if can_undo else None,
                    )
                )
            return HistoryResponse(items=items)

        return self._run(run, raise_failure=True)

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _run(self, operation: Callable[[Any], Any], *, raise_failure: bool = False) -> Any:
        """Executa em transacao. Recusas previstas saem como `_Failure`.

        Uma recusa grava somente o evento de auditoria e confirma a transacao;
        so depois o erro publico e levantado. Qualquer erro inesperado desfaz
        tudo e vira `DATA_CHANGE_UNAVAILABLE`.
        """

        try:
            with self.repository.transaction() as uow:
                result = operation(uow)
        except DataChangeError:
            raise
        except Exception as error:
            logger.warning("Falha controlada na alteracao pelo chat: %s", type(error).__name__)
            raise errors.unavailable() from error
        if isinstance(result, _Failure):
            raise result.error
        return result

    def _audit(
        self,
        uow: Any,
        event_type: str,
        status: str,
        payload: dict[str, Any],
        context: AccessContext,
        correlation_id: str | None,
        interaction_id: str | None = None,
    ) -> None:
        uow.insert_audit(
            AuditEvent(
                event_type=event_type,
                event_status=status,
                payload={"contract": DATA_CHANGE_CONTRACT, **payload},
                user_id=str(context.user_id),
                correlation_id=correlation_id,
                # Confirmacao, cancelamento e desfazer chegam por rotas proprias;
                # o evento herda a interacao da mensagem que gerou a previa.
                interaction_id=interaction_id,
            )
        )

    def _reject(
        self,
        uow: Any,
        error: DataChangeError,
        draft: DataChangeDraft,
        context: AccessContext,
        correlation_id: str,
        **extra: Any,
    ) -> DataChangeOutcome:
        if error.code == "OUT_OF_SCOPE_FOR_PROFILE":
            self._audit(
                uow, "authorization.access_denied", "bloqueado",
                {"code": error.code, "operation": "write", "project_code": draft.project_code,
                 "field": draft.field, **extra},
                context, correlation_id,
            )
        else:
            self._audit(
                uow, "project_data.change_rejected", "falha",
                {"code": error.code, "project_code": draft.project_code, "field": draft.field, **extra},
                context, correlation_id,
            )
        return DataChangeOutcome(status="rejected", code=error.code, message=error.message, draft=draft)

    def _reject_problem(
        self,
        uow: Any,
        problem: str,
        draft: DataChangeDraft,
        context: AccessContext,
        correlation_id: str,
    ) -> DataChangeOutcome:
        if problem == "MULTIPLE_CHANGES":
            error = DataChangeError(
                "MULTIPLE_CHANGES",
                "Faço uma alteração por vez: um campo de um registro. Envie cada mudança em uma mensagem.",
                422,
            )
        else:
            error = errors.field_not_editable(EDITABLE_FIELDS_TEXT)
        return self._reject(uow, error, draft, context, correlation_id)

    def _prepare(
        self,
        uow: Any,
        draft: DataChangeDraft,
        context: AccessContext,
        *,
        conversation_id: str | None,
        correlation_id: str,
        missing_day: bool = False,
        readable_only: bool = False,
    ) -> DataChangeOutcome:
        today = self.today()

        # 1. Projeto
        if not draft.project_code:
            codes = sorted({grant.project_code.upper() for grant in context.grants
                            if grant.can_write and grant.project_code})
            return DataChangeOutcome(
                status="needs_input",
                missing="project",
                question="Em qual projeto? Informe o código, por exemplo PRJ-0442.",
                candidates=[Candidate(id=code, label=code) for code in codes],
                draft=draft,
            )
        project = uow.project_by_code(draft.project_code)
        if project is None:
            return self._reject(
                uow, errors.target_not_found(f"O projeto {draft.project_code} não foi encontrado."),
                draft, context, correlation_id,
            )
        draft = draft.model_copy(update={"project_code": project.code})
        if readable_only:
            try:
                authorize_operation(context, "read", project_id=project.code)
            except OutOfScopeForProfileError:
                return self._reject(uow, errors.out_of_scope(project.code), draft, context, correlation_id)

        # 2. Permissao de escrita pela regra que cobre o projeto
        try:
            authorize_project_write(
                context,
                project_id=project.id,
                subportfolio_id=project.subportfolio_id,
                project_code=project.code,
                correlation_id=correlation_id,
            )
        except OutOfScopeForProfileError:
            return self._reject(uow, errors.out_of_scope(project.code), draft, context, correlation_id)

        # 3. Campo
        spec = FIELDS.get(draft.field or "")
        if spec is None:
            return self._reject(uow, errors.field_not_editable(EDITABLE_FIELDS_TEXT), draft, context, correlation_id)

        # 4. Registro
        target, outcome = self._resolve_target(uow, spec, project, draft, context, correlation_id)
        if outcome is not None:
            return outcome
        draft = draft.model_copy(update={"target_id": target.id})

        # 5. Valor
        if not draft.raw_value:
            return DataChangeOutcome(
                status="needs_input",
                missing="value",
                question=_value_question(spec, missing_day),
                draft=draft,
            )
        try:
            value = parse_value(spec, draft.raw_value, today)
            parsed = validate(spec, value, target.values, today)
        except InvalidValueError as error:
            return self._reject(uow, errors.invalid_value(str(error)), draft, context, correlation_id,
                                target_id=target.id)

        before = canonical(spec, target.values.get(spec.column))
        if before == parsed.canonical:
            return self._reject(
                uow,
                DataChangeError(
                    "NO_CHANGE",
                    f"{spec.label} já é {parsed.display}. Nada foi alterado.",
                    422,
                ),
                draft, context, correlation_id, target_id=target.id,
            )

        # 6. Previa
        now = self._now()
        pending = PendingChange(
            id=str(uuid4()),
            user_id=str(context.user_id),
            correlation_id=correlation_id,
            project_id=project.id,
            entity=spec.entity,
            target_id=target.id,
            field_key=spec.key,
            before=before,
            after=parsed.canonical,
            expires_at=now + self.preview_ttl,
            created_at=now,
            external_conversation_id=conversation_id,
        )
        uow.insert_pending(pending)
        self._audit(
            uow, "project_data.change_previewed", "pendente",
            {
                "pending_change_id": pending.id,
                "project_code": project.code,
                "field": spec.key,
                "target_id": target.id,
                "before": before,
                "after": parsed.canonical,
            },
            context, correlation_id,
        )
        return DataChangeOutcome(
            status="preview",
            draft=draft,
            preview=DataChangePreview(
                pending_change_id=pending.id,
                project=ProjectRef(code=project.code, title=project.title),
                target=TargetView(entity=spec.entity, id=target.id, label=_target_label(spec, target, project)),
                field=FieldRef(key=spec.key, label=spec.label),
                before=ValueView(value=before, display=display(spec, target.values.get(spec.column))),
                after=ValueView(value=parsed.canonical, display=parsed.display),
                warnings=list(parsed.warnings),
                expires_at=pending.expires_at,
                undo_window_minutes=int(self.undo_window.total_seconds() // 60),
            ),
        )

    def _resolve_target(
        self,
        uow: Any,
        spec: FieldSpec,
        project: Project,
        draft: DataChangeDraft,
        context: AccessContext,
        correlation_id: str,
    ) -> tuple[TargetRecord | None, DataChangeOutcome | None]:
        entity = ENTITIES[spec.entity]
        if spec.entity == "projeto":
            return uow.get_target("projeto", project.id), None

        if draft.target_id:
            try:
                target_id = str(UUID(draft.target_id))
            except ValueError:
                return None, self._reject(uow, errors.target_not_found(), draft, context, correlation_id)
            target = uow.get_target(spec.entity, target_id)
            if target is None or target.project_id != project.id:
                return None, self._reject(
                    uow, errors.target_not_found(), draft, context, correlation_id,
                )
            return target, None

        options = uow.list_targets(spec.entity, project.id)
        if not draft.item_reference:
            if not options:
                return None, self._reject(
                    uow,
                    errors.target_not_found(
                        f"O {project.code} não tem {entity.noun}s {_flex(entity, 'registrado')}s."
                    ),
                    draft, context, correlation_id,
                )
            return None, DataChangeOutcome(
                status="needs_input",
                missing="target",
                question=f"Qual {entity.noun} do {project.code}?",
                candidates=[Candidate(id=item_id, label=label) for item_id, label in options[:10]],
                draft=draft,
            )

        matches = _match_targets(draft.item_reference, options)
        if not matches:
            names = "; ".join(label for _id, label in options[:MAX_CANDIDATES])
            hint = f" Registros do {project.code}: {names}." if names else ""
            return None, self._reject(
                uow,
                errors.target_not_found(
                    f"Não encontrei {entity.article} {entity.noun} “{draft.item_reference}” no {project.code}.{hint}"
                ),
                draft, context, correlation_id,
            )
        if len(matches) > 1:
            return None, DataChangeOutcome(
                status="needs_input",
                missing="target",
                question=(
                    f"Encontrei mais de {_flex(entity, 'um', 'uma')} {entity.noun} "
                    f"{_flex(entity, 'parecido')}. Qual {_flex(entity, 'deles', 'delas')}?"
                ),
                candidates=[Candidate(id=item_id, label=label) for item_id, label in matches[:MAX_CANDIDATES]],
                draft=draft,
            )
        return uow.get_target(spec.entity, matches[0][0]), None

    def _confirm(
        self,
        uow: Any,
        pending_id: str,
        context: AccessContext,
        reason: str | None,
    ) -> ConfirmResponse | "_Failure":
        pending = uow.get_pending(pending_id, lock=True)
        if pending is None or pending.user_id != str(context.user_id):
            raise errors.error(errors.PREVIEW_NOT_FOUND)
        spec = FIELDS[pending.field_key]
        if pending.status == "confirmada" and pending.change_record_id:
            record = uow.get_change_record(pending.change_record_id)
            return self._confirm_response(spec, record)

        failure: DataChangeError | None = None
        target = None
        project = uow.project_by_id(pending.project_id)
        if pending.status == "cancelada":
            failure = errors.error(errors.PREVIEW_CANCELLED)
        elif self._now() > pending.expires_at:
            failure = errors.error(errors.PREVIEW_EXPIRED)
        elif project is None:
            failure = errors.target_not_found()
        else:
            try:
                authorize_project_write(
                    context,
                    project_id=project.id,
                    subportfolio_id=project.subportfolio_id,
                    project_code=project.code,
                    correlation_id=pending.correlation_id,
                )
            except OutOfScopeForProfileError:
                failure = errors.out_of_scope(project.code)
        if failure is None:
            target = uow.get_target(pending.entity, pending.target_id, lock=True)
            if target is None:
                failure = errors.target_not_found()
            elif canonical(spec, target.values.get(spec.column)) != pending.before:
                failure = errors.error(errors.STALE_PREVIEW)
            else:
                try:
                    validate(spec, typed_from_canonical(spec, pending.after), target.values, self.today())
                except InvalidValueError as error:
                    failure = errors.invalid_value(str(error))

        payload = {
            "pending_change_id": pending.id,
            "project_code": project.code if project else None,
            "field": spec.key,
            "target_id": pending.target_id,
        }
        if failure is not None:
            event = ("authorization.access_denied", "bloqueado") if failure.code == "OUT_OF_SCOPE_FOR_PROFILE" \
                else ("project_data.change_confirm_failed", "falha")
            self._audit(uow, event[0], event[1], {**payload, "code": failure.code, "operation": "write"},
                        context, pending.correlation_id, pending.interaction_id)
            return _Failure(failure)

        assert target is not None and project is not None
        now = self._now()
        after_value = typed_from_canonical(spec, pending.after)
        uow.update_target(spec.entity, target.id, spec.column, after_value)

        target_label = _target_label(spec, target, project)
        before_display = display(spec, target.values.get(spec.column))
        after_display = display(spec, after_value)
        record = ChangeRecord(
            id=str(uuid4()),
            project_id=project.id,
            change_type=spec.change_type,
            title=f"Alteração pelo chat: {spec.label} — {target_label}"[:240],
            impact_summary=f"{spec.label}: {before_display} → {after_display}",
            requested_by=(context.display_name or str(context.user_id))[:160],
            status="implementada",
            registration_date=now.astimezone(LOCAL_TIMEZONE).date(),
            decided_at=now,
            reason=reason,
            metadata={
                "origin": "chat",
                "contract": DATA_CHANGE_CONTRACT,
                "field": spec.key,
                "table": spec.entity_spec.table,
                "column": spec.column,
                "target_id": target.id,
                "target_label": target_label,
                "project_code": project.code,
                "before": pending.before,
                "after": pending.after,
                "user_id": str(context.user_id),
                "interaction_id": pending.interaction_id,
                "pending_change_id": pending.id,
                "correlation_id": pending.correlation_id,
                "applied_at": now.isoformat(),
                "undo": None,
            },
        )
        uow.insert_change_record(record)
        self._audit(
            uow, "project_data.change_applied", "sucesso",
            {**payload, "change_id": record.id, "before": pending.before, "after": pending.after},
            context, pending.correlation_id, pending.interaction_id,
        )
        pending.status = "confirmada"
        pending.change_record_id = record.id
        pending.decided_at = now
        pending.reason = reason
        uow.save_pending(pending)
        return self._confirm_response(spec, record)

    def _confirm_response(self, spec: FieldSpec, record: ChangeRecord) -> ConfirmResponse:
        metadata = record.metadata
        applied_at = _parse_datetime(metadata.get("applied_at")) or record.decided_at
        return ConfirmResponse(
            change_id=record.id,
            status="aplicada",
            field=FieldRef(key=spec.key, label=spec.label),
            target=TargetView(entity=spec.entity, id=str(metadata["target_id"]),
                              label=str(metadata.get("target_label") or "")),
            before=ValueView(value=metadata.get("before"), display=display(spec, metadata.get("before"))),
            after=ValueView(value=metadata.get("after"), display=display(spec, metadata.get("after"))),
            applied_at=applied_at,
            undo_available_until=applied_at + self.undo_window,
            correlation_id=str(metadata.get("correlation_id")),
        )

    def _cancel(self, uow: Any, pending_id: str, context: AccessContext) -> CancelResponse | "_Failure":
        pending = uow.get_pending(pending_id, lock=True)
        if pending is None or pending.user_id != str(context.user_id):
            raise errors.error(errors.PREVIEW_NOT_FOUND)
        if pending.status == "cancelada":
            return CancelResponse(status="cancelada")
        if pending.status == "confirmada":
            return _Failure(DataChangeError(
                "PREVIEW_ALREADY_CONFIRMED",
                "Esta alteração já foi confirmada. Use o desfazer, se ainda estiver no prazo.",
                409,
            ))
        pending.status = "cancelada"
        pending.decided_at = self._now()
        uow.save_pending(pending)
        self._audit(
            uow, "project_data.change_cancelled", "sucesso",
            {"pending_change_id": pending.id, "field": pending.field_key, "target_id": pending.target_id},
            context, pending.correlation_id, pending.interaction_id,
        )
        return CancelResponse(status="cancelada")

    def _undo(self, uow: Any, change_id: str, context: AccessContext) -> UndoResponse | "_Failure":
        record = uow.get_change_record(change_id, lock=True)
        if record is None or record.metadata.get("field") not in FIELDS:
            raise errors.error(errors.CHANGE_NOT_FOUND)
        metadata = dict(record.metadata)
        spec = FIELDS[metadata["field"]]
        applied_at = _parse_datetime(metadata.get("applied_at")) or record.decided_at
        now = self._now()
        project = uow.project_by_id(record.project_id)

        failure: DataChangeError | None = None
        target = None
        if metadata.get("user_id") != str(context.user_id):
            failure = errors.error(errors.UNDO_NOT_AUTHOR)
        elif metadata.get("undo") or record.status != "implementada":
            failure = errors.error(errors.ALREADY_UNDONE)
        elif now > applied_at + self.undo_window:
            failure = errors.error(errors.UNDO_WINDOW_EXPIRED)
        elif project is None:
            failure = errors.target_not_found()
        else:
            try:
                authorize_project_write(
                    context,
                    project_id=project.id,
                    subportfolio_id=project.subportfolio_id,
                    project_code=project.code,
                    correlation_id=metadata.get("correlation_id"),
                )
            except OutOfScopeForProfileError:
                failure = errors.out_of_scope(project.code)
        if failure is None:
            target = uow.get_target(spec.entity, str(metadata["target_id"]), lock=True)
            if target is None:
                failure = errors.target_not_found()
            elif canonical(spec, target.values.get(spec.column)) != metadata.get("after"):
                failure = errors.error(errors.VALUE_CHANGED_SINCE)

        payload = {"change_id": record.id, "field": spec.key, "target_id": metadata.get("target_id")}
        if failure is not None:
            self._audit(
                uow, "project_data.undo_denied", "bloqueado",
                {**payload, "code": failure.code}, context, metadata.get("correlation_id"),
                metadata.get("interaction_id"),
            )
            return _Failure(failure)

        restored = typed_from_canonical(spec, metadata.get("before"))
        uow.update_target(spec.entity, str(metadata["target_id"]), spec.column, restored)
        metadata["undo"] = {"undone_at": now.isoformat(), "undone_by": str(context.user_id)}
        record.metadata = metadata
        record.status = "cancelada"
        uow.save_change_record(record)
        self._audit(
            uow, "project_data.change_undone", "sucesso",
            {**payload, "restored": metadata.get("before")}, context, metadata.get("correlation_id"),
            metadata.get("interaction_id"),
        )
        return UndoResponse(
            change_id=record.id,
            status="desfeita",
            restored=ValueView(value=metadata.get("before"), display=display(spec, restored)),
            undone_at=now,
        )


@dataclass(frozen=True)
class _Failure:
    """Recusa prevista: a auditoria ja foi gravada e a transacao confirmada."""

    error: DataChangeError


# ----------------------------------------------------------------------
# Auxiliares
# ----------------------------------------------------------------------


def outcome_text(outcome: DataChangeOutcome) -> str:
    """Texto da resposta do chat, legivel mesmo sem o cartao."""

    if outcome.status == "preview" and outcome.preview:
        preview = outcome.preview
        text = (
            f"Confira a alteração antes de confirmar. {preview.field.label} de {preview.target.label}: "
            f"{preview.before.display} → {preview.after.display}."
        )
        if preview.warnings:
            text += " " + " ".join(preview.warnings)
        return text + " Nada foi gravado ainda; a prévia vale por 10 minutos."
    if outcome.status == "needs_input":
        return outcome.question or "Preciso de mais informações para preparar a alteração."
    return outcome.message or "Não foi possível preparar a alteração."


def _value_question(spec: FieldSpec, missing_day: bool) -> str:
    if spec.kind == "date":
        if missing_day:
            return f"Qual o dia exato para {spec.label.lower()}? Informe a data completa, como 31/03/2027."
        return f"Para qual data? Informe {spec.label.lower()} como dd/mm/aaaa."
    if spec.kind == "status":
        labels = ", ".join(STATUS_LABELS[code] for code in spec.allowed)
        return f"Qual o novo {spec.label.lower()}? Opções: {labels}."
    if spec.kind == "percent":
        return "Qual o novo progresso, de 0 a 100%?"
    return f"Qual o novo valor de {spec.label.lower()}?"


def _flex(entity: Any, masculine: str, feminine: str | None = None) -> str:
    """Concorda a palavra com o genero do registro ("um risco", "uma atividade")."""

    if entity.article != "a":
        return masculine
    return feminine if feminine is not None else masculine[:-1] + "a"


def _target_label(spec: FieldSpec, target: TargetRecord, project: Project) -> str:
    if spec.entity == "projeto":
        return project.code
    return f"{target.label} ({project.code})"


def _normalize_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", fold(value)).strip()


def _match_targets(reference: str, options: list[tuple[str, str]]) -> list[tuple[str, str]]:
    wanted = _normalize_label(reference)
    if not wanted:
        return []
    exact = [option for option in options if _normalize_label(option[1]) == wanted]
    if exact:
        return exact
    return [
        option for option in options
        if wanted in _normalize_label(option[1]) or _normalize_label(option[1]) in wanted
    ]


def _clean_reason(reason: str | None) -> str | None:
    if reason is None:
        return None
    text = re.sub(r"\s+", " ", reason).strip()
    if not text:
        return None
    found = scan(text)
    if found.found:
        raise errors.invalid_value(
            f"A justificativa contém {describe_categories(found.categories)}. Remova o dado e confirme de novo."
        )
    return text[:500]


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def _status_for(code: str | None) -> int:
    return {
        "OUT_OF_SCOPE_FOR_PROFILE": 403,
        "TARGET_NOT_FOUND": 404,
        "DATA_CHANGE_UNAVAILABLE": 503,
    }.get(code or "", 422)


# ----------------------------------------------------------------------
# Instancia usada pela API
# ----------------------------------------------------------------------

_service_override: DataChangeService | None = None


def set_data_change_service(service: DataChangeService | None) -> None:
    """Permite aos testes injetar o servico com repositorio em memoria."""

    global _service_override
    _service_override = service


def get_data_change_service() -> DataChangeService | None:
    """Servico com PostgreSQL, ou `None` quando nao ha banco configurado.

    A escrita exige o banco: sem ele, o chat responde que a alteracao esta
    indisponivel em vez de fingir uma gravacao em memoria.
    """

    if _service_override is not None:
        return _service_override
    if not (os.getenv("DATABASE_URL", "").strip() or os.getenv("SUPABASE_DATABASE_URL", "").strip()):
        return None
    return DataChangeService(PostgresDataChangeRepository())
