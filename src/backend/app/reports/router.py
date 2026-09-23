"""Rotas HTTP do contrato de geracao de relatorios."""

from fastapi import APIRouter, BackgroundTasks, Header, Response, status

from app.reports.schemas import (
    CreateReportRequest,
    AnswerWorkflowRequest,
    ConfirmWorkflowRequest,
    PrepareReportRequest,
    PrepareReportResponse,
    ReportCallbackRequest,
    ReportExecutionResponse,
    StartWorkflowRequest,
    WorkflowSessionResponse,
)
from app.reports.security import resolve_report_identity, validate_callback_token
from app.reports.service import get_report_service
from app.reports.workflow import get_workflow_service

router = APIRouter(prefix="/api", tags=["relatorios"])


@router.post(
    "/report-requests/prepare",
    response_model=PrepareReportResponse,
    summary="Validar e preparar uma solicitacao de relatorio",
)
def prepare_report_request(
    request: PrepareReportRequest,
    authorization: str | None = Header(default=None),
) -> PrepareReportResponse:
    identity = resolve_report_identity(authorization)
    return get_report_service().prepare(request, identity)


@router.post(
    "/report-requests",
    response_model=ReportExecutionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Confirmar e enfileirar a geracao do relatorio",
)
def create_report_request(
    request: CreateReportRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    authorization: str | None = Header(default=None),
) -> ReportExecutionResponse:
    identity = resolve_report_identity(authorization)
    service = get_report_service()
    execution, created = service.create(request, identity)
    if not created:
        response.status_code = status.HTTP_200_OK
    elif service.execution_mode == "local":
        background_tasks.add_task(service.process_local, execution.execution_id)
    else:
        background_tasks.add_task(
            service.dispatch_power_automate, execution.execution_id
        )
    return service.response(execution)


@router.get(
    "/report-requests/{execution_id}",
    response_model=ReportExecutionResponse,
    summary="Consultar o estado de uma geracao",
)
def get_report_request(
    execution_id: str,
    authorization: str | None = Header(default=None),
) -> ReportExecutionResponse:
    identity = resolve_report_identity(authorization)
    service = get_report_service()
    return service.response(service.get(execution_id, identity))


@router.get(
    "/report-requests/{execution_id}/artifact",
    summary="Baixar o DOCX autorizado",
)
def download_report_artifact(
    execution_id: str,
    authorization: str | None = Header(default=None),
) -> Response:
    identity = resolve_report_identity(authorization)
    service = get_report_service()
    execution = service.get(execution_id, identity)
    artifact = service.artifact_content(execution_id, identity)
    return Response(
        content=artifact.data,
        media_type=artifact.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{artifact.file_name}"',
            "Cache-Control": "private, no-store",
        },
    )


@router.post(
    "/integrations/power-automate/report-results",
    response_model=ReportExecutionResponse,
    summary="Receber o callback idempotente do fluxo de relatorio",
)
def receive_report_callback(
    callback: ReportCallbackRequest,
    callback_token: str | None = Header(default=None, alias="X-Callback-Token"),
) -> ReportExecutionResponse:
    validate_callback_token(callback_token)
    service = get_report_service()
    return service.response(service.apply_callback(callback))


@router.post(
    "/workflow-sessions",
    response_model=WorkflowSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar o workflow guiado de relatorio",
)
def start_workflow_session(
    request: StartWorkflowRequest,
    authorization: str | None = Header(default=None),
) -> WorkflowSessionResponse:
    identity = resolve_report_identity(authorization)
    return get_workflow_service().start(request, identity)


@router.get(
    "/workflow-sessions/{session_id}",
    response_model=WorkflowSessionResponse,
    summary="Consultar o workflow e a execucao vinculada",
)
def get_workflow_session(
    session_id: str,
    authorization: str | None = Header(default=None),
) -> WorkflowSessionResponse:
    identity = resolve_report_identity(authorization)
    return get_workflow_service().get(session_id, identity)


@router.post(
    "/workflow-sessions/{session_id}/answers",
    response_model=WorkflowSessionResponse,
    summary="Responder a etapa atual do workflow",
)
def answer_workflow_session(
    session_id: str,
    request: AnswerWorkflowRequest,
    authorization: str | None = Header(default=None),
) -> WorkflowSessionResponse:
    identity = resolve_report_identity(authorization)
    return get_workflow_service().answer(session_id, request, identity)


@router.post(
    "/workflow-sessions/{session_id}/confirm",
    response_model=WorkflowSessionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Confirmar e executar o workflow",
)
def confirm_workflow_session(
    session_id: str,
    request: ConfirmWorkflowRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    authorization: str | None = Header(default=None),
) -> WorkflowSessionResponse:
    identity = resolve_report_identity(authorization)
    workflow = get_workflow_service()
    result, created = workflow.confirm(session_id, request, identity)
    if not created:
        response.status_code = status.HTTP_200_OK
        return result
    execution = result.execution
    if execution:
        service = get_report_service()
        task = (
            service.process_local
            if service.execution_mode == "local"
            else service.dispatch_power_automate
        )
        background_tasks.add_task(task, execution.execution_id)
    return result


@router.post(
    "/workflow-sessions/{session_id}/cancel",
    response_model=WorkflowSessionResponse,
    summary="Cancelar um workflow ainda nao confirmado",
)
def cancel_workflow_session(
    session_id: str,
    authorization: str | None = Header(default=None),
) -> WorkflowSessionResponse:
    identity = resolve_report_identity(authorization)
    return get_workflow_service().cancel(session_id, identity)
