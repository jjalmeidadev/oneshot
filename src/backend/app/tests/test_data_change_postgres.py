"""Integracao da alteracao pelo chat com PostgreSQL real (S5-06).

Roda somente com `DATA_CHANGE_TEST_DATABASE_URL` apontando para um banco com
`01`, `02`, `13`, `20` e `22` aplicados; na CI sem banco, os testes sao pulados.
Cada teste cria um usuario sintetico, restaura os valores alterados e apaga as
linhas que criou.

    DATA_CHANGE_TEST_DATABASE_URL=postgresql://... python -m pytest app/tests/test_data_change_postgres.py -v
"""

from __future__ import annotations

import os
import threading
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from app.data_changes import repository as repository_module
from app.data_changes.errors import DataChangeError
from app.data_changes.extractor import extract_change
from app.data_changes.repository import PostgresDataChangeRepository
from app.data_changes.service import DataChangeService
from app.security.access import AccessContext, AccessGrant

DATABASE_URL = os.getenv("DATA_CHANGE_TEST_DATABASE_URL", "").strip()
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="DATA_CHANGE_TEST_DATABASE_URL nao configurada")


def _connect():
    import psycopg

    return psycopg.connect(DATABASE_URL)


def _scalar(sql, params=()):
    with _connect() as connection, connection.cursor() as cursor:
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return row[0] if row else None


def _execute(sql, params=()):
    with _connect() as connection, connection.cursor() as cursor:
        cursor.execute(sql, params)


@pytest.fixture()
def db():
    if _scalar("SELECT to_regclass('public.pending_data_changes')::text") is None:
        pytest.skip("Aplique 22_data_change_previews.sql antes deste teste.")
    project = _scalar("SELECT id::text FROM public.projects WHERE code = 'PRJ-0442'")
    if project is None:
        pytest.skip("Aplique 02 e 13 antes deste teste.")
    original_end = _scalar("SELECT planned_end_date FROM public.projects WHERE id = %s", (project,))
    activity = _scalar(
        "SELECT id::text FROM public.schedule_items WHERE project_id = %s AND wbs_code = '1.3'", (project,)
    )
    original_progress = _scalar("SELECT progress_percent FROM public.schedule_items WHERE id = %s", (activity,)) \
        if activity else None

    user_id = str(uuid4())
    _execute(
        "INSERT INTO public.users (id, entra_object_id, display_name, email, role_name) "
        "VALUES (%s, %s, '[TESTE S5-06] Gerente', %s, 'equipe_projeto')",
        (user_id, str(uuid4()), f"s5-06-{user_id}@oneshot.example.com"),
    )
    context = AccessContext(
        user_id=UUID(user_id),
        auth_subject=uuid4(),
        role_name="equipe_projeto",
        allowed_subportfolio_ids=frozenset(),
        allowed_project_ids=frozenset({UUID(project)}),
        can_read=True,
        can_write=True,
        can_export=True,
        grants=(AccessGrant("projeto", None, UUID(project), True, True, True, project_code="PRJ-0442"),),
        allowed_project_codes=frozenset({"prj-0442"}),
        display_name="[TESTE S5-06] Gerente",
    )
    service = DataChangeService(PostgresDataChangeRepository(_connect))
    try:
        yield service, context, project, activity
    finally:
        _execute("UPDATE public.projects SET planned_end_date = %s WHERE id = %s", (original_end, project))
        if activity:
            _execute("UPDATE public.schedule_items SET progress_percent = %s WHERE id = %s",
                     (original_progress, activity))
        _execute("DELETE FROM public.audit_events WHERE user_id = %s", (user_id,))
        _execute("DELETE FROM public.pending_data_changes WHERE user_id = %s", (user_id,))
        _execute("DELETE FROM public.change_records WHERE metadata->>'user_id' = %s", (user_id,))
        _execute("DELETE FROM public.users WHERE id = %s", (user_id,))


def _preview(service, context, message):
    extracted = extract_change(message, service.today())
    outcome = service.handle_message(extracted, context, conversation_id="s5-06-postgres").outcome
    assert outcome.status == "preview", outcome
    return outcome.preview


def test_confirmar_e_desfazer_gravam_valor_change_records_e_audit_events(db):
    service, context, project, _activity = db
    preview = _preview(service, context, "Prorroga o prazo do PRJ-0442 para 31/03/2027")
    assert _scalar("SELECT planned_end_date FROM public.projects WHERE id = %s", (project,)) == date(2026, 12, 20)

    change = service.confirm(preview.pending_change_id, context, "Teste de integracao S5-06")

    assert _scalar("SELECT planned_end_date FROM public.projects WHERE id = %s", (project,)) == date(2027, 3, 31)
    assert _scalar(
        "SELECT status || '|' || source_label || '|' || change_type || '|' || (metadata->>'before') || '|' "
        "|| (metadata->>'after') FROM public.change_records WHERE id = %s",
        (change.change_id,),
    ) == "implementada|chat|prazo|2026-12-20|2027-03-31"
    assert _scalar(
        "SELECT count(*) FROM public.audit_events WHERE correlation_id = %s "
        "AND event_type IN ('project_data.change_previewed', 'project_data.change_applied')",
        (change.correlation_id,),
    ) == 2
    assert _scalar("SELECT status FROM public.pending_data_changes WHERE id = %s",
                   (preview.pending_change_id,)) == "confirmada"

    service.undo(change.change_id, context)

    assert _scalar("SELECT planned_end_date FROM public.projects WHERE id = %s", (project,)) == date(2026, 12, 20)
    assert _scalar("SELECT status FROM public.change_records WHERE id = %s", (change.change_id,)) == "cancelada"
    assert _scalar(
        "SELECT count(*) FROM public.audit_events WHERE correlation_id = %s AND event_type = 'project_data.change_undone'",
        (change.correlation_id,),
    ) == 1


def test_falha_na_auditoria_desfaz_a_escrita(db, monkeypatch):
    service, context, project, _activity = db
    preview = _preview(service, context, "Prorroga o prazo do PRJ-0442 para 31/03/2027")
    original = repository_module._PostgresUnitOfWork.insert_audit

    def failing_audit(self, event):
        if event.event_type == "project_data.change_applied":
            raise RuntimeError("falha simulada na auditoria")
        return original(self, event)

    monkeypatch.setattr(repository_module._PostgresUnitOfWork, "insert_audit", failing_audit)
    with pytest.raises(DataChangeError) as error:
        service.confirm(preview.pending_change_id, context)

    assert error.value.code == "DATA_CHANGE_UNAVAILABLE"
    assert _scalar("SELECT planned_end_date FROM public.projects WHERE id = %s", (project,)) == date(2026, 12, 20)
    assert _scalar("SELECT count(*) FROM public.change_records WHERE metadata->>'pending_change_id' = %s",
                   (preview.pending_change_id,)) == 0
    assert _scalar("SELECT status FROM public.pending_data_changes WHERE id = %s",
                   (preview.pending_change_id,)) == "pendente"


def test_duas_confirmacoes_simultaneas_do_mesmo_campo_gravam_uma_so(db):
    service, context, project, _activity = db
    first = _preview(service, context, "Prorroga o prazo do PRJ-0442 para 31/03/2027")
    second = _preview(service, context, "Prorroga o prazo do PRJ-0442 para 30/04/2027")
    results: list[object] = []
    barrier = threading.Barrier(2)

    def confirm(preview):
        barrier.wait()
        try:
            results.append(service.confirm(preview.pending_change_id, context))
        except DataChangeError as error:
            results.append(error.code)

    threads = [threading.Thread(target=confirm, args=(preview,)) for preview in (first, second)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    codes = sorted(item if isinstance(item, str) else "aplicada" for item in results)
    assert codes == ["STALE_PREVIEW", "aplicada"]
    final = _scalar("SELECT planned_end_date FROM public.projects WHERE id = %s", (project,))
    assert final in {date(2027, 3, 31), date(2027, 4, 30)}
    assert _scalar(
        "SELECT count(*) FROM public.change_records WHERE metadata->>'user_id' = %s", (str(context.user_id),)
    ) == 1


def test_previa_desatualizada_nao_grava(db):
    service, context, project, _activity = db
    preview = _preview(service, context, "Prorroga o prazo do PRJ-0442 para 31/03/2027")
    _execute("UPDATE public.projects SET planned_end_date = DATE '2027-01-31' WHERE id = %s", (project,))

    with pytest.raises(DataChangeError) as error:
        service.confirm(preview.pending_change_id, context)

    assert error.value.code == "STALE_PREVIEW"
    assert _scalar("SELECT planned_end_date FROM public.projects WHERE id = %s", (project,)) == date(2027, 1, 31)


def test_progresso_da_atividade_da_carga_sintetica(db):
    service, context, _project, activity = db
    if activity is None:
        pytest.skip("Aplique a versao de 13_seed_portfolio_report_data.sql com o cronograma.")
    preview = _preview(
        service, context,
        "Atualiza o progresso da atividade Instalação do lote 2 de equipamentos de sinalização do PRJ-0442 para 60%",
    )
    assert (preview.before.value, preview.after.value) == ("35", "60")

    service.confirm(preview.pending_change_id, context)

    assert _scalar("SELECT progress_percent FROM public.schedule_items WHERE id = %s", (activity,)) == Decimal("60.00")


def test_chat_com_rastreabilidade_liga_previa_e_eventos_a_interacao(db, monkeypatch):
    from fastapi.testclient import TestClient

    from app.data_changes.service import set_data_change_service
    from app.main import app
    from app.security import get_access_context

    _service, context, project, _activity = db
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)
    monkeypatch.setattr(
        "app.pipeline.generate_chat_response",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("sem provedor")),
    )
    set_data_change_service(None)  # usa o servico real com PostgreSQL
    app.dependency_overrides[get_access_context] = lambda: context
    try:
        client = TestClient(app)
        body = client.post(
            "/api/chat",
            json={"message": "Prorroga o prazo do PRJ-0442 para 31/03/2027", "conversation_id": "s5-06-rastreio"},
        ).json()
        preview = body["data_change"]["preview"]
        interaction_id = body["trace_id"]
        assert interaction_id

        assert _scalar("SELECT interaction_id::text FROM public.pending_data_changes WHERE id = %s",
                       (preview["pending_change_id"],)) == interaction_id
        assert _scalar(
            "SELECT interaction_id::text FROM public.audit_events "
            "WHERE event_type = 'project_data.change_previewed' AND event_payload->>'pending_change_id' = %s",
            (preview["pending_change_id"],),
        ) == interaction_id
        assert _scalar("SELECT user_id::text FROM public.ai_interactions WHERE id = %s",
                       (interaction_id,)) == str(context.user_id)

        change = client.post(f"/api/data-change-previews/{preview['pending_change_id']}/confirm").json()
        assert _scalar("SELECT metadata->>'interaction_id' FROM public.change_records WHERE id = %s",
                       (change["change_id"],)) == interaction_id
        assert _scalar(
            "SELECT count(*) FROM public.audit_events WHERE correlation_id = %s AND interaction_id = %s "
            "AND event_type IN ('project_data.change_previewed', 'project_data.change_applied')",
            (change["correlation_id"], interaction_id),
        ) == 2
        assert _scalar("SELECT planned_end_date FROM public.projects WHERE id = %s", (project,)) == date(2027, 3, 31)
    finally:
        app.dependency_overrides.pop(get_access_context, None)
        _execute(
            "DELETE FROM public.audit_events WHERE interaction_id IN ("
            "SELECT i.id FROM public.ai_interactions i WHERE i.user_id = %s)",
            (str(context.user_id),),
        )
        _execute("DELETE FROM public.pending_data_changes WHERE user_id = %s", (str(context.user_id),))
        _execute("DELETE FROM public.ai_interactions WHERE user_id = %s", (str(context.user_id),))
        _execute("DELETE FROM public.ai_conversations WHERE user_id = %s", (str(context.user_id),))
