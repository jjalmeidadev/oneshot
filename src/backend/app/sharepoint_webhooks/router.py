"""Endpoint do webhook de alteração do SharePoint simulado."""

from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Query, Response, status

from app.sharepoint_webhooks.schemas import (
    SharePointNotificationBatch,
    SharePointWebhookResponse,
)
from app.sharepoint_webhooks.repository import (
    SharePointWebhookConflictError,
    SharePointWebhookStorageError,
    get_sharepoint_webhook_repository,
)
from app.sharepoint_webhooks.security import validate_client_state


router = APIRouter(prefix="/api/integrations/sharepoint", tags=["integrações"])


@router.post(
    "/change-notifications",
    response_model=SharePointWebhookResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receber alterações do SharePoint simulado",
    responses={200: {"content": {"text/plain": {}}}},
)
def receive_sharepoint_change_notification(
    validation_token: Annotated[
        str | None,
        Query(alias="validationToken", min_length=1, max_length=2048),
    ] = None,
    payload: Annotated[SharePointNotificationBatch | None, Body()] = None,
) -> Response | SharePointWebhookResponse:
    """Responde ao handshake ou valida um lote para processamento posterior."""

    if validation_token is not None:
        return Response(
            content=validation_token,
            status_code=status.HTTP_200_OK,
            media_type="text/plain",
        )
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Payload de notificação ausente.",
        )

    validate_client_state(payload)
    try:
        result = get_sharepoint_webhook_repository().store_batch(payload.value)
    except SharePointWebhookConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="eventId já utilizado por outra notificação.",
        ) from error
    except SharePointWebhookStorageError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Persistência do webhook indisponível.",
        ) from error
    return SharePointWebhookResponse(
        accepted=result.received,
        created=result.created,
        duplicates=result.duplicates,
    )
