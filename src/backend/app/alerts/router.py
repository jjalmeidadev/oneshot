"""API autenticada do fluxo interno de alertas."""

from fastapi import APIRouter, Header, Response, status

from app.alerts.schemas import (
    AlertNotification, AlertSubscriptionResponse, AlertWorkflowResponse,
    AnswerAlertWorkflowRequest, ChangeSubscriptionRequest,
    ConfirmAlertWorkflowRequest, NotificationListResponse,
    StartAlertWorkflowRequest, SubscriptionStatus,
)
from app.alerts.service import get_alert_service
from app.alerts.workflow import get_alert_workflow_service
from app.reports.security import resolve_report_identity

router=APIRouter(prefix="/api",tags=["alertas"])


@router.post("/alert-workflow-sessions",response_model=AlertWorkflowResponse,status_code=201)
def start_alert_workflow(request: StartAlertWorkflowRequest,authorization: str|None=Header(default=None)) -> AlertWorkflowResponse:
    return get_alert_workflow_service().start(request,resolve_report_identity(authorization))


@router.get("/alert-workflow-sessions/{session_id}",response_model=AlertWorkflowResponse)
def get_alert_workflow(session_id: str,authorization: str|None=Header(default=None)) -> AlertWorkflowResponse:
    return get_alert_workflow_service().get(session_id,resolve_report_identity(authorization))


@router.post("/alert-workflow-sessions/{session_id}/answers",response_model=AlertWorkflowResponse)
def answer_alert_workflow(session_id: str,request: AnswerAlertWorkflowRequest,authorization: str|None=Header(default=None)) -> AlertWorkflowResponse:
    return get_alert_workflow_service().answer(session_id,request,resolve_report_identity(authorization))


@router.post("/alert-workflow-sessions/{session_id}/confirm",response_model=AlertWorkflowResponse)
def confirm_alert_workflow(session_id: str,request: ConfirmAlertWorkflowRequest,response: Response,authorization: str|None=Header(default=None)) -> AlertWorkflowResponse:
    value=get_alert_workflow_service().confirm(session_id,request,resolve_report_identity(authorization))
    response.status_code=status.HTTP_200_OK
    return value


@router.post("/alert-workflow-sessions/{session_id}/cancel",response_model=AlertWorkflowResponse)
def cancel_alert_workflow(session_id: str,authorization: str|None=Header(default=None)) -> AlertWorkflowResponse:
    return get_alert_workflow_service().cancel(session_id,resolve_report_identity(authorization))


@router.get("/alert-subscriptions",response_model=list[AlertSubscriptionResponse])
def list_alert_subscriptions(authorization: str|None=Header(default=None)) -> list[AlertSubscriptionResponse]:
    identity=resolve_report_identity(authorization)
    return [AlertSubscriptionResponse(subscription=item) for item in get_alert_service().list(identity)]


@router.get("/alert-subscriptions/{subscription_id}",response_model=AlertSubscriptionResponse)
def get_alert_subscription(subscription_id: str,authorization: str|None=Header(default=None)) -> AlertSubscriptionResponse:
    return AlertSubscriptionResponse(subscription=get_alert_service().get(subscription_id,resolve_report_identity(authorization)))


def _change(subscription_id: str,target: SubscriptionStatus,request: ChangeSubscriptionRequest,authorization: str|None) -> AlertSubscriptionResponse:
    return AlertSubscriptionResponse(subscription=get_alert_service().change_status(subscription_id,target,request,resolve_report_identity(authorization)))


@router.post("/alert-subscriptions/{subscription_id}/pause",response_model=AlertSubscriptionResponse)
def pause_alert_subscription(subscription_id: str,request: ChangeSubscriptionRequest,authorization: str|None=Header(default=None)) -> AlertSubscriptionResponse:
    return _change(subscription_id,SubscriptionStatus.PAUSED,request,authorization)


@router.post("/alert-subscriptions/{subscription_id}/resume",response_model=AlertSubscriptionResponse)
def resume_alert_subscription(subscription_id: str,request: ChangeSubscriptionRequest,authorization: str|None=Header(default=None)) -> AlertSubscriptionResponse:
    return _change(subscription_id,SubscriptionStatus.ACTIVE,request,authorization)


@router.post("/alert-subscriptions/{subscription_id}/cancel",response_model=AlertSubscriptionResponse)
def cancel_alert_subscription(subscription_id: str,request: ChangeSubscriptionRequest,authorization: str|None=Header(default=None)) -> AlertSubscriptionResponse:
    return _change(subscription_id,SubscriptionStatus.CANCELLED,request,authorization)


@router.get("/notifications",response_model=NotificationListResponse)
def list_notifications(authorization: str|None=Header(default=None)) -> NotificationListResponse:
    return get_alert_service().notifications(resolve_report_identity(authorization))


@router.post("/notifications/{notification_id}/read",response_model=AlertNotification)
def read_notification(notification_id: str,authorization: str|None=Header(default=None)) -> AlertNotification:
    return get_alert_service().mark_notification_read(notification_id,resolve_report_identity(authorization))
