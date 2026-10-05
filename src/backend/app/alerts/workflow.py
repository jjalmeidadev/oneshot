"""Configuracao guiada da inscricao de alerta."""

from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from uuid import uuid4

from app.alerts.errors import AlertAccessDeniedError, AlertConflictError
from app.alerts.repository import AlertRepository, get_alert_repository
from app.alerts.schemas import (
    AlertRule, AlertWorkflowOption, AlertWorkflowQuestion, AlertWorkflowResponse,
    AlertWorkflowSession, AlertWorkflowStatus, AlertWorkflowStep,
    AnswerAlertWorkflowRequest, ConfirmAlertWorkflowRequest, CreateAlertRequest,
    PrepareAlertRequest, StartAlertWorkflowRequest,
)
from app.alerts.service import AlertService, get_alert_service
from app.reports.security import ReportIdentity
from app.reports.security import can_access_scope
from app.reports.schemas import ScopeType

STEPS = [AlertWorkflowStep.PROJECT, AlertWorkflowStep.THRESHOLD, AlertWorkflowStep.SCHEDULE, AlertWorkflowStep.RESEND]


class AlertWorkflowService:
    def __init__(self, repository: AlertRepository, alerts: AlertService) -> None:
        self.repository = repository; self.alerts = alerts

    def start(self, request: StartAlertWorkflowRequest, identity: ReportIdentity) -> AlertWorkflowResponse:
        now=_now(); answers={}
        candidates=request.parameters.get("scope_candidates", [])
        threshold=request.parameters.get("threshold_days")
        if candidates: answers["project_candidate"]=candidates[0].get("value")
        if isinstance(threshold,int): answers["threshold_candidate"]=threshold
        value=AlertWorkflowSession(session_id=str(uuid4()),requested_by=identity.subject,conversation_id=request.conversation_id,interaction_id=request.interaction_id,correlation_id=str(uuid4()),status=AlertWorkflowStatus.ACTIVE,current_step=AlertWorkflowStep.PROJECT,revision=0,answers=answers,action_ids=[],created_at=now,updated_at=now)
        self.repository.create_workflow(value); return self.response(value,identity)

    def get(self, session_id: str, identity: ReportIdentity) -> AlertWorkflowResponse:
        return self.response(self._authorized(session_id,identity),identity)

    def answer(self, session_id: str, request: AnswerAlertWorkflowRequest, identity: ReportIdentity) -> AlertWorkflowResponse:
        value=self._authorized(session_id,identity)
        if request.client_action_id in value.action_ids: return self.response(value,identity)
        if value.status != AlertWorkflowStatus.ACTIVE or value.current_step != request.step or value.revision != request.revision: raise AlertConflictError("A etapa informada nao corresponde ao workflow atual.")
        answer=self._validate(request.step,request.value)
        if request.step == AlertWorkflowStep.PROJECT:
            allowed = {
                item["id"]
                for item in self.alerts.source.list_projects()
                if can_access_scope(
                    identity, ScopeType.PROJECT, item["id"], operation="read"
                )
            }
            if answer not in allowed:
                raise AlertConflictError("O projeto informado nao esta disponivel.")
        previous=value.revision; value.answers[request.step.value]=answer; value.action_ids.append(request.client_action_id); value.revision+=1; value.updated_at=_now()
        index=STEPS.index(request.step)
        if index+1 < len(STEPS): value.current_step=STEPS[index+1]
        else:
            value.current_step=AlertWorkflowStep.CONFIRMATION; value.status=AlertWorkflowStatus.READY_FOR_CONFIRMATION
            value.prepared=self.alerts.prepare(self._prepare(value),identity)
        value=self.repository.save_workflow(value,previous); return self.response(value,identity)

    def confirm(self, session_id: str, request: ConfirmAlertWorkflowRequest, identity: ReportIdentity) -> AlertWorkflowResponse:
        value=self._authorized(session_id,identity)
        if request.client_action_id in value.action_ids or value.subscription_id: return self.response(value,identity)
        if value.status != AlertWorkflowStatus.READY_FOR_CONFIRMATION or value.prepared is None or value.revision != request.revision: raise AlertConflictError("Revise o alerta antes de confirmar.")
        subscription,_=self.alerts.create(CreateAlertRequest(prepared_alert=value.prepared.prepared_alert,confirmation_hash=value.prepared.confirmation_hash,idempotency_key=f"workflow:{value.session_id}:confirm"),identity)
        previous=value.revision; value.subscription_id=subscription.subscription_id; value.status=AlertWorkflowStatus.COMPLETED; value.current_step=AlertWorkflowStep.COMPLETED; value.action_ids.append(request.client_action_id); value.revision+=1; value.updated_at=_now()
        value=self.repository.save_workflow(value,previous); return self.response(value,identity)

    def cancel(self, session_id: str, identity: ReportIdentity) -> AlertWorkflowResponse:
        value=self._authorized(session_id,identity)
        if value.subscription_id: raise AlertConflictError("A inscricao confirmada deve ser cancelada pela rota de inscricoes.")
        if value.status != AlertWorkflowStatus.CANCELLED:
            previous=value.revision; value.status=AlertWorkflowStatus.CANCELLED; value.revision+=1; value.updated_at=_now(); value=self.repository.save_workflow(value,previous)
        return self.response(value,identity)

    def response(self,value: AlertWorkflowSession,identity: ReportIdentity) -> AlertWorkflowResponse:
        subscription=self.alerts.get(value.subscription_id,identity) if value.subscription_id else None
        return AlertWorkflowResponse(session_id=value.session_id,status=value.status,current_step=value.current_step,revision=value.revision,question=self._question(value, identity),answers=value.answers,confirmation_summary=value.prepared.confirmation_summary if value.prepared else None,warnings=value.prepared.warnings if value.prepared else [],subscription=subscription)

    def _authorized(self,session_id: str,identity: ReportIdentity) -> AlertWorkflowSession:
        value=self.repository.get_workflow(session_id)
        if value.requested_by != identity.subject: raise AlertAccessDeniedError()
        return value

    def _question(self,value: AlertWorkflowSession, identity: ReportIdentity) -> AlertWorkflowQuestion | None:
        if value.status != AlertWorkflowStatus.ACTIVE: return None
        if value.current_step==AlertWorkflowStep.PROJECT:
            options=[
                AlertWorkflowOption(value=item["id"], label=item["label"])
                for item in self.alerts.source.list_projects()
                if can_access_scope(
                    identity, ScopeType.PROJECT, item["id"], operation="read"
                )
            ]
            return AlertWorkflowQuestion(step=value.current_step,prompt="Qual projeto deve ser monitorado?",input_type="single_select",options=options)
        if value.current_step==AlertWorkflowStep.THRESHOLD: return AlertWorkflowQuestion(step=value.current_step,prompt="Depois de quantos dias corridos de atraso devo avisar?",input_type="number")
        if value.current_step==AlertWorkflowStep.SCHEDULE: return AlertWorkflowQuestion(step=value.current_step,prompt="Com que frequencia devo verificar?",input_type="single_select",options=[AlertWorkflowOption(value="daily",label="Diariamente as 08:00"),AlertWorkflowOption(value="weekly",label="Toda segunda as 08:00")])
        return AlertWorkflowQuestion(step=value.current_step,prompt="Deseja repetir o aviso enquanto o atraso continuar?",input_type="single_select",options=[AlertWorkflowOption(value="none",label="Nao repetir"),AlertWorkflowOption(value="7",label="Repetir a cada 7 dias")])

    def _prepare(self,value: AlertWorkflowSession) -> PrepareAlertRequest:
        project_id=str(value.answers["project"]); projects={item["id"]:item["label"] for item in self.alerts.source.list_projects()}
        weekly=value.answers["schedule"]=="weekly"
        return PrepareAlertRequest(conversation_id=value.conversation_id,interaction_id=value.interaction_id,rule=AlertRule(project_id=project_id,project_label=projects[project_id],threshold_days=int(value.answers["threshold"]),trigger_type="weekly" if weekly else "daily",weekday=0 if weekly else None,resend_interval_days=None if value.answers["resend"]=="none" else int(value.answers["resend"])))

    @staticmethod
    def _validate(step: AlertWorkflowStep, raw: object) -> object:
        if step==AlertWorkflowStep.THRESHOLD:
            try: value=int(raw)
            except (TypeError,ValueError) as error: raise AlertConflictError("Informe um limiar entre 0 e 3650 dias.") from error
            if value<0 or value>3650: raise AlertConflictError("Informe um limiar entre 0 e 3650 dias.")
            return value
        value=str(raw)
        allowed={AlertWorkflowStep.SCHEDULE:{"daily","weekly"},AlertWorkflowStep.RESEND:{"none","7"}}
        if step in allowed and value not in allowed[step]: raise AlertConflictError("Opcao invalida para a etapa.")
        return value


def _now() -> datetime: return datetime.now(timezone.utc)

@lru_cache(maxsize=1)
def get_alert_workflow_service() -> AlertWorkflowService: return AlertWorkflowService(get_alert_repository(),get_alert_service())
