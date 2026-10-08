"""API autenticada do fluxo interno de alertas."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, Response, status

from app.alerts.schemas import (
    AlertNotification,
    AlertSubscriptionResponse,
    AlertWorkflowResponse,
    AnswerAlertWorkflowRequest,
    ChangeSubscriptionRequest,
    ConfirmAlertWorkflowRequest,
    NotificationDeliveryCallbackRequest,
    NotificationDeliveryCallbackResponse,
    NotificationListResponse,
    StartAlertWorkflowRequest,
    SubscriptionStatus,
)
from app.alerts.security import validate_notification_callback_signature
from app.alerts.service import get_alert_service
from app.alerts.workflow import get_alert_workflow_service
from app.reports.security import report_identity_from_access_context
from app.security import AccessContext, require_read_access

router = APIRouter(prefix="/api", tags=["alertas"])
# Inscricao, pausa e leitura de notificacao sao preferencias do proprio usuario
# e nao alteram dado de projeto: exigem leitura no escopo do projeto, e o
# servico confere que a inscricao pertence a quem a altera.
ReadAccess = Annotated[AccessContext, Depends(require_read_access)]


@router.post(
    "/alert-workflow-sessions",
    response_model=AlertWorkflowResponse,
    status_code=201,
)
def start_alert_workflow(
    request: StartAlertWorkflowRequest,
    access: ReadAccess,
) -> AlertWorkflowResponse:
    return get_alert_workflow_service().start(
        request, report_identity_from_access_context(access)
    )


@router.get(
    "/alert-workflow-sessions/{session_id}",
    response_model=AlertWorkflowResponse,
)
def get_alert_workflow(
    session_id: str,
    access: ReadAccess,
) -> AlertWorkflowResponse:
    return get_alert_workflow_service().get(
        session_id, report_identity_from_access_context(access)
    )


@router.post(
    "/alert-workflow-sessions/{session_id}/answers",
    response_model=AlertWorkflowResponse,
)
def answer_alert_workflow(
    session_id: str,
    request: AnswerAlertWorkflowRequest,
    access: ReadAccess,
) -> AlertWorkflowResponse:
    return get_alert_workflow_service().answer(
        session_id, request, report_identity_from_access_context(access)
    )


@router.post(
    "/alert-workflow-sessions/{session_id}/confirm",
    response_model=AlertWorkflowResponse,
)
def confirm_alert_workflow(
    session_id: str,
    request: ConfirmAlertWorkflowRequest,
    response: Response,
    access: ReadAccess,
) -> AlertWorkflowResponse:
    value = get_alert_workflow_service().confirm(
        session_id, request, report_identity_from_access_context(access)
    )
    response.status_code = status.HTTP_200_OK
    return value


@router.post(
    "/alert-workflow-sessions/{session_id}/cancel",
    response_model=AlertWorkflowResponse,
)
def cancel_alert_workflow(
    session_id: str,
    access: ReadAccess,
) -> AlertWorkflowResponse:
    return get_alert_workflow_service().cancel(
        session_id, report_identity_from_access_context(access)
    )


@router.get("/alert-subscriptions", response_model=list[AlertSubscriptionResponse])
def list_alert_subscriptions(access: ReadAccess) -> list[AlertSubscriptionResponse]:
    identity = report_identity_from_access_context(access)
    return [
        AlertSubscriptionResponse(subscription=item)
        for item in get_alert_service().list(identity)
    ]


@router.get(
    "/alert-subscriptions/{subscription_id}",
    response_model=AlertSubscriptionResponse,
)
def get_alert_subscription(
    subscription_id: str,
    access: ReadAccess,
) -> AlertSubscriptionResponse:
    return AlertSubscriptionResponse(
        subscription=get_alert_service().get(
            subscription_id, report_identity_from_access_context(access)
        )
    )


def _change(
    subscription_id: str,
    target: SubscriptionStatus,
    request: ChangeSubscriptionRequest,
    access: AccessContext,
) -> AlertSubscriptionResponse:
    return AlertSubscriptionResponse(
        subscription=get_alert_service().change_status(
            subscription_id,
            target,
            request,
            report_identity_from_access_context(access),
        )
    )


@router.post(
    "/alert-subscriptions/{subscription_id}/pause",
    response_model=AlertSubscriptionResponse,
)
def pause_alert_subscription(
    subscription_id: str,
    request: ChangeSubscriptionRequest,
    access: ReadAccess,
) -> AlertSubscriptionResponse:
    return _change(subscription_id, SubscriptionStatus.PAUSED, request, access)


@router.post(
    "/alert-subscriptions/{subscription_id}/resume",
    response_model=AlertSubscriptionResponse,
)
def resume_alert_subscription(
    subscription_id: str,
    request: ChangeSubscriptionRequest,
    access: ReadAccess,
) -> AlertSubscriptionResponse:
    return _change(subscription_id, SubscriptionStatus.ACTIVE, request, access)


@router.post(
    "/alert-subscriptions/{subscription_id}/cancel",
    response_model=AlertSubscriptionResponse,
)
def cancel_alert_subscription(
    subscription_id: str,
    request: ChangeSubscriptionRequest,
    access: ReadAccess,
) -> AlertSubscriptionResponse:
    return _change(subscription_id, SubscriptionStatus.CANCELLED, request, access)


@router.get("/notifications", response_model=NotificationListResponse)
def list_notifications(access: ReadAccess) -> NotificationListResponse:
    return get_alert_service().notifications(
        report_identity_from_access_context(access)
    )


@router.post("/notifications/{notification_id}/read", response_model=AlertNotification)
def read_notification(
    notification_id: str,
    access: ReadAccess,
) -> AlertNotification:
    return get_alert_service().mark_notification_read(
        notification_id, report_identity_from_access_context(access)
    )


@router.post(
    "/integrations/notifications/delivery-results",
    response_model=NotificationDeliveryCallbackResponse,
    summary="Receber confirmacao idempotente de entrega de notificacao",
)
async def receive_notification_delivery_result(
    request: Request,
    callback: NotificationDeliveryCallbackRequest,
    webhook_signature: str | None = Header(
        default=None, alias="X-Webhook-Signature"
    ),
) -> NotificationDeliveryCallbackResponse:
    validate_notification_callback_signature(await request.body(), webhook_signature)
    return get_alert_service().apply_delivery_callback(callback)
