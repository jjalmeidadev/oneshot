"""Servico da alteracao pelo chat: os 12 cenarios de aceite da Secao 8.5.13.

Os testes usam o repositorio em memoria, que tem a mesma semantica de tudo ou
nada do PostgreSQL. A integracao com o banco real esta em
`test_data_change_postgres.py`.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.data_changes.errors import DataChangeError
from app.data_changes.extractor import extract_change
from app.data_changes.schemas import PreviewRequest
from app.tests.data_change_support import (
    ACTIVITY_LOTE2,
    MILESTONE_OPERACAO,
    PRJ_0442,
    PRJ_0510,
    RISK_INTERFERENCIA,
    Clock,
    build_repository,
    build_service,
    consulta,
    escrita_em_um_leitura_em_outro,
    gerente,
    lider,
    outro_gerente,
    pmo,
)

TODAY = date(2026, 10, 6)


def ask(service, message, context):
    extracted = extract_change(message, service.today())
    assert extracted is not None, message
    return service.handle_message(extracted, context, conversation_id="conversa-1")


def events(repo, event_type=None):
    return [e for e in repo.state.audit if event_type is None or e.event_type == event_type]


def project_value(repo, column, project_id=PRJ_0442):
    return repo.state.targets["projeto"][project_id].values[column]


@pytest.fixture()
def setup():
    clock = Clock()
    repo = build_repository()
    service = build_service(repo, clock)
    return service, repo, clock


# --------------------------------------------------------------------------
# Cenarios 1 a 3: sucesso, cancelamento e desfazer
# --------------------------------------------------------------------------


def test_cenario_1_prorrogar_prazo_e_confirmar_grava_com_trilha_completa(setup):
    service, repo, _clock = setup
    handled = ask(service, "Prorroga o prazo do PRJ-0442 para 31/03/2027", gerente())

    assert handled.outcome.status == "preview"
    preview = handled.outcome.preview
    assert preview.field.key == "projeto.prazo_final"
    assert (preview.before.value, preview.before.display) == ("2026-12-20", "20/12/2026")
    assert (preview.after.value, preview.after.display) == ("2027-03-31", "31/03/2027")
    # A previa nao grava nada no projeto.
    assert project_value(repo, "planned_end_date") == date(2026, 12, 20)
    assert [e.event_type for e in events(repo)] == ["project_data.change_previewed"]

    result = service.confirm(preview.pending_change_id, gerente(), "Replanejamento aprovado em 03/10")

    assert result.status == "aplicada"
    assert project_value(repo, "planned_end_date") == date(2027, 3, 31)
    record = repo.state.change_records[result.change_id]
    assert record.status == "implementada"
    assert record.change_type == "prazo"
    assert record.requested_by == "[DEMO] Gerente de Projeto"
    assert record.reason == "Replanejamento aprovado em 03/10"
    assert record.impact_summary == "Prazo final previsto: 20/12/2026 → 31/03/2027"
    assert record.metadata["origin"] == "chat"
    assert record.metadata["before"] == "2026-12-20"
    assert record.metadata["after"] == "2027-03-31"
    assert record.metadata["user_id"] == str(gerente().user_id)
    applied = events(repo, "project_data.change_applied")
    assert len(applied) == 1
    assert applied[0].event_status == "sucesso"
    assert applied[0].payload["change_id"] == result.change_id
    # O mesmo correlation_id liga previa e confirmacao.
    assert applied[0].correlation_id == handled.correlation_id
    assert repo.state.pending[preview.pending_change_id].status == "confirmada"


def test_cenario_2_cancelar_nao_grava_no_projeto(setup):
    service, repo, _clock = setup
    preview = ask(service, "Prorroga o prazo do PRJ-0442 para 31/03/2027", gerente()).outcome.preview

    assert service.cancel(preview.pending_change_id, gerente()).status == "cancelada"
    assert service.cancel(preview.pending_change_id, gerente()).status == "cancelada"

    assert project_value(repo, "planned_end_date") == date(2026, 12, 20)
    assert repo.state.change_records == {}
    assert len(events(repo, "project_data.change_cancelled")) == 1
    with pytest.raises(DataChangeError) as error:
        service.confirm(preview.pending_change_id, gerente())
    assert (error.value.code, error.value.status_code) == ("PREVIEW_CANCELLED", 409)


def test_cenario_3_desfazer_em_ate_15_minutos_restaura_o_valor(setup):
    service, repo, clock = setup
    preview = ask(service, "Prorroga o prazo do PRJ-0442 para 31/03/2027", gerente()).outcome.preview
    change = service.confirm(preview.pending_change_id, gerente())

    clock.advance(minutes=14, seconds=59)
    undone = service.undo(change.change_id, gerente())

    assert undone.status == "desfeita"
    assert undone.restored.value == "2026-12-20"
    assert project_value(repo, "planned_end_date") == date(2026, 12, 20)
    record = repo.state.change_records[change.change_id]
    assert record.status == "cancelada"
    assert record.metadata["undo"]["undone_by"] == str(gerente().user_id)
    assert len(events(repo, "project_data.change_undone")) == 1

    with pytest.raises(DataChangeError) as error:
        service.undo(change.change_id, gerente())
    assert error.value.code == "ALREADY_UNDONE"


def test_cenario_4_desfazer_depois_de_15_minutos_e_recusado(setup):
    service, repo, clock = setup
    preview = ask(service, "Prorroga o prazo do PRJ-0442 para 31/03/2027", gerente()).outcome.preview
    change = service.confirm(preview.pending_change_id, gerente())

    clock.advance(minutes=15, seconds=1)
    with pytest.raises(DataChangeError) as error:
        service.undo(change.change_id, gerente())

    assert (error.value.code, error.value.status_code) == ("UNDO_WINDOW_EXPIRED", 410)
    assert project_value(repo, "planned_end_date") == date(2027, 3, 31)
    assert repo.state.change_records[change.change_id].status == "implementada"
    assert events(repo, "project_data.undo_denied")[0].payload["code"] == "UNDO_WINDOW_EXPIRED"


# --------------------------------------------------------------------------
# Cenarios 5 e 6: negacao por perfil
# --------------------------------------------------------------------------


def test_cenario_5_gerente_nao_altera_outro_projeto(setup):
    service, repo, _clock = setup
    handled = ask(service, "Muda o status do PRJ-0510 para crítico", gerente())

    assert handled.outcome.status == "rejected"
    assert handled.outcome.code == "OUT_OF_SCOPE_FOR_PROFILE"
    assert repo.state.pending == {}
    assert project_value(repo, "status", PRJ_0510) == "atencao"
    denied = events(repo, "authorization.access_denied")
    assert denied[0].event_status == "bloqueado"
    assert denied[0].payload["operation"] == "write"


@pytest.mark.parametrize("context", [pmo, consulta, lider], ids=["pmo", "consulta", "lider"])
def test_cenario_6_perfis_sem_escrita_nao_alteram_nada(setup, context):
    service, repo, _clock = setup
    for message in (
        "Prorroga o prazo do PRJ-0442 para 31/03/2027",
        "Muda o status do PRJ-0510 para crítico",
    ):
        handled = ask(service, message, context())
        assert handled.outcome.status == "rejected"
        assert handled.outcome.code == "OUT_OF_SCOPE_FOR_PROFILE"
    assert repo.state.pending == {}
    assert project_value(repo, "planned_end_date") == date(2026, 12, 20)


def test_permissao_vem_da_regra_que_cobre_o_projeto_e_nao_do_agregado(setup):
    service, _repo, _clock = setup
    context = escrita_em_um_leitura_em_outro()
    assert context.can_write is True  # o agregado liberaria os dois projetos

    assert ask(service, "Prorroga o prazo do PRJ-0442 para 31/03/2027", context).outcome.status == "preview"
    denied = ask(service, "Prorroga o prazo do PRJ-0510 para 30/04/2027", context).outcome
    assert (denied.status, denied.code) == ("rejected", "OUT_OF_SCOPE_FOR_PROFILE")


def test_regra_de_subportfolio_com_escrita_alcanca_seus_projetos(setup):
    service, _repo, _clock = setup
    outcome = ask(service, "Muda o status do PRJ-0510 para crítico", lider(can_write=True)).outcome
    assert outcome.status == "preview"
    outcome = ask(service, "Muda o status do PRJ-DEMO-ACESSO para crítico", lider(can_write=True)).outcome
    assert outcome.code == "OUT_OF_SCOPE_FOR_PROFILE"


def test_permissao_revogada_entre_previa_e_confirmacao_bloqueia_a_escrita(setup):
    service, repo, _clock = setup
    preview = ask(service, "Prorroga o prazo do PRJ-0442 para 31/03/2027", gerente()).outcome.preview
    sem_escrita = gerente().__class__(**{**gerente().__dict__, "grants": tuple(
        g.__class__(**{**g.__dict__, "can_write": False}) for g in gerente().grants
    )})

    with pytest.raises(DataChangeError) as error:
        service.confirm(preview.pending_change_id, sem_escrita)

    assert error.value.code == "OUT_OF_SCOPE_FOR_PROFILE"
    assert project_value(repo, "planned_end_date") == date(2026, 12, 20)
    assert repo.state.pending[preview.pending_change_id].status == "pendente"


# --------------------------------------------------------------------------
# Cenarios 7 a 9: valor invalido e campo nao editavel
# --------------------------------------------------------------------------


def test_cenario_7_progresso_acima_de_100_e_recusado_sem_previa(setup):
    service, repo, _clock = setup
    outcome = ask(
        service,
        "Atualiza o progresso da atividade Instalação do lote 2 de equipamentos de sinalização do PRJ-0442 para 140%",
        gerente(),
    ).outcome

    assert (outcome.status, outcome.code) == ("rejected", "INVALID_VALUE")
    assert "entre 0 e 100" in outcome.message
    assert repo.state.pending == {}
    assert repo.state.targets["cronograma"][ACTIVITY_LOTE2].values["progress_percent"] == Decimal("35.00")
    assert events(repo, "project_data.change_rejected")[0].payload["code"] == "INVALID_VALUE"


def test_cenario_8_status_concluido_do_projeto_e_recusado(setup):
    service, repo, _clock = setup
    outcome = ask(service, "Muda o status do PRJ-0442 para concluído", gerente()).outcome

    assert (outcome.status, outcome.code) == ("rejected", "INVALID_VALUE")
    assert "processo formal do PMO" in outcome.message
    assert project_value(repo, "status") == "em_andamento"


def test_cenario_9_campo_fora_do_contrato_e_recusado(setup):
    service, repo, _clock = setup
    outcome = ask(service, "Altera o orçamento do PRJ-0442 para 2 milhões", gerente()).outcome

    assert (outcome.status, outcome.code) == ("rejected", "FIELD_NOT_EDITABLE")
    assert "status e prazo final do projeto" in outcome.message
    assert repo.state.pending == {}


@pytest.mark.parametrize(
    ("message", "fragment"),
    [
        ("Prorroga o prazo do PRJ-0442 para 30/02/2027", "não existe no calendário"),
        ("Prorroga o prazo do PRJ-0442 para 10/01/2026", "anterior ao início do projeto"),
        ("Prorroga o prazo do PRJ-0442 para 01/01/2040", "entre 01/01/2020 e 31/12/2036"),
        ("Registra a conclusão do marco Início da operação assistida na Linha Azul do PRJ-0442 em 10/10/2026",
         "posterior a hoje"),
        ("Muda o responsável do risco Interferência com a operação comercial do PRJ-0442 para fulano@metro.sp.gov.br",
         "dado pessoal ou sensível"),
    ],
)
def test_valores_invalidos_sao_recusados_com_a_regra_do_campo(setup, message, fragment):
    service, repo, _clock = setup
    outcome = ask(service, message, gerente()).outcome
    assert (outcome.status, outcome.code) == ("rejected", "INVALID_VALUE")
    assert fragment in outcome.message
    assert repo.state.pending == {}


def test_valor_igual_ao_atual_nao_cria_previa(setup):
    service, repo, _clock = setup
    outcome = ask(service, "Prorroga o prazo do PRJ-0442 para 20/12/2026", gerente()).outcome
    assert (outcome.status, outcome.code) == ("rejected", "NO_CHANGE")
    assert repo.state.pending == {}


def test_varias_alteracoes_na_mesma_mensagem_sao_recusadas(setup):
    service, _repo, _clock = setup
    outcome = ask(service, "Muda o status e o prazo do PRJ-0442", gerente()).outcome
    assert (outcome.status, outcome.code) == ("rejected", "MULTIPLE_CHANGES")


# --------------------------------------------------------------------------
# Cenarios 10 a 12: concorrencia, expiracao e clique duplo
# --------------------------------------------------------------------------


def test_cenario_10_confirmar_depois_que_o_campo_mudou_e_recusado(setup):
    service, repo, _clock = setup
    preview = ask(service, "Prorroga o prazo do PRJ-0442 para 31/03/2027", gerente()).outcome.preview
    repo.state.targets["projeto"][PRJ_0442].values["planned_end_date"] = date(2027, 1, 31)

    with pytest.raises(DataChangeError) as error:
        service.confirm(preview.pending_change_id, gerente())

    assert (error.value.code, error.value.status_code) == ("STALE_PREVIEW", 409)
    assert project_value(repo, "planned_end_date") == date(2027, 1, 31)
    assert repo.state.change_records == {}
    assert events(repo, "project_data.change_confirm_failed")[0].payload["code"] == "STALE_PREVIEW"


def test_cenario_11_confirmar_depois_de_10_minutos_e_recusado(setup):
    service, repo, clock = setup
    preview = ask(service, "Prorroga o prazo do PRJ-0442 para 31/03/2027", gerente()).outcome.preview

    clock.advance(minutes=10, seconds=1)
    with pytest.raises(DataChangeError) as error:
        service.confirm(preview.pending_change_id, gerente())

    assert (error.value.code, error.value.status_code) == ("PREVIEW_EXPIRED", 410)
    assert project_value(repo, "planned_end_date") == date(2026, 12, 20)


def test_cenario_12_confirmar_duas_vezes_grava_uma_vez(setup):
    service, repo, _clock = setup
    preview = ask(service, "Prorroga o prazo do PRJ-0442 para 31/03/2027", gerente()).outcome.preview

    first = service.confirm(preview.pending_change_id, gerente())
    second = service.confirm(preview.pending_change_id, gerente())

    assert first == second
    assert len(repo.state.change_records) == 1
    assert len(events(repo, "project_data.change_applied")) == 1


# --------------------------------------------------------------------------
# Garantias adicionais do contrato
# --------------------------------------------------------------------------


def test_falha_no_meio_da_confirmacao_desfaz_tudo(setup):
    service, repo, _clock = setup
    preview = ask(service, "Prorroga o prazo do PRJ-0442 para 31/03/2027", gerente()).outcome.preview
    repo.fail_on = "audit:project_data.change_applied"

    with pytest.raises(DataChangeError) as error:
        service.confirm(preview.pending_change_id, gerente())

    assert (error.value.code, error.value.status_code) == ("DATA_CHANGE_UNAVAILABLE", 503)
    # Valor, change_records e previa voltam ao estado anterior.
    assert project_value(repo, "planned_end_date") == date(2026, 12, 20)
    assert repo.state.change_records == {}
    assert repo.state.pending[preview.pending_change_id].status == "pendente"


def test_previa_e_desfazer_sao_so_do_autor(setup):
    service, repo, _clock = setup
    preview = ask(service, "Prorroga o prazo do PRJ-0442 para 31/03/2027", gerente()).outcome.preview

    with pytest.raises(DataChangeError) as error:
        service.confirm(preview.pending_change_id, outro_gerente())
    assert (error.value.code, error.value.status_code) == ("PREVIEW_NOT_FOUND", 404)

    change = service.confirm(preview.pending_change_id, gerente())
    with pytest.raises(DataChangeError) as error:
        service.undo(change.change_id, outro_gerente())
    assert (error.value.code, error.value.status_code) == ("UNDO_NOT_AUTHOR", 403)
    assert project_value(repo, "planned_end_date") == date(2027, 3, 31)


def test_desfazer_recusa_quando_o_valor_mudou_depois(setup):
    service, repo, _clock = setup
    preview = ask(service, "Prorroga o prazo do PRJ-0442 para 31/03/2027", gerente()).outcome.preview
    change = service.confirm(preview.pending_change_id, gerente())
    repo.state.targets["projeto"][PRJ_0442].values["planned_end_date"] = date(2027, 4, 30)

    with pytest.raises(DataChangeError) as error:
        service.undo(change.change_id, gerente())

    assert error.value.code == "VALUE_CHANGED_SINCE"
    assert project_value(repo, "planned_end_date") == date(2027, 4, 30)


def test_cancelar_previa_confirmada_e_recusado(setup):
    service, _repo, _clock = setup
    preview = ask(service, "Prorroga o prazo do PRJ-0442 para 31/03/2027", gerente()).outcome.preview
    service.confirm(preview.pending_change_id, gerente())
    with pytest.raises(DataChangeError) as error:
        service.cancel(preview.pending_change_id, gerente())
    assert error.value.code == "PREVIEW_ALREADY_CONFIRMED"


def test_justificativa_com_dado_sensivel_e_recusada_antes_de_gravar(setup):
    service, repo, _clock = setup
    preview = ask(service, "Prorroga o prazo do PRJ-0442 para 31/03/2027", gerente()).outcome.preview
    with pytest.raises(DataChangeError) as error:
        service.confirm(preview.pending_change_id, gerente(), "aprovado por fulano@metro.sp.gov.br")
    assert error.value.code == "INVALID_VALUE"
    assert project_value(repo, "planned_end_date") == date(2026, 12, 20)


@pytest.mark.parametrize(
    ("message", "field", "target", "before", "after"),
    [
        ("Muda o status do risco Interferência com a operação comercial do PRJ-0442 para em tratamento",
         "risco.status", RISK_INTERFERENCIA, "aberto", "em_tratamento"),
        ("Marca o marco Início da operação assistida na Linha Azul do PRJ-0442 como em andamento",
         "marco.status", MILESTONE_OPERACAO, "planejado", "em_andamento"),
        ("Atualiza o progresso da atividade Instalação do lote 2 de equipamentos de sinalização do PRJ-0442 para 60%",
         "cronograma.progresso", ACTIVITY_LOTE2, "35", "60"),
        ("Muda o responsável do risco Interferência com a operação comercial do PRJ-0442 para Gerência de Engenharia",
         "risco.responsavel", RISK_INTERFERENCIA, "Gerencia de Operacao", "Gerência de Engenharia"),
    ],
)
def test_exemplos_do_contrato_geram_previa_e_gravam(setup, message, field, target, before, after):
    service, repo, _clock = setup
    preview = ask(service, message, gerente()).outcome.preview

    assert (preview.field.key, preview.target.id) == (field, target)
    assert (preview.before.value, preview.after.value) == (before, after)

    service.confirm(preview.pending_change_id, gerente())
    entity = preview.target.entity
    column = {"risco.status": "status", "marco.status": "status",
              "cronograma.progresso": "progress_percent", "risco.responsavel": "owner_name"}[field]
    stored = repo.state.targets[entity][target].values[column]
    assert (format(stored.normalize(), "f") if isinstance(stored, Decimal) else str(stored)) == after


def test_alvo_ambiguo_pede_escolha_e_a_escolha_cria_a_previa(setup):
    service, _repo, _clock = setup
    outcome = ask(service, "Muda o status da atividade instalação do PRJ-0442 para atrasado", gerente()).outcome

    assert (outcome.status, outcome.missing) == ("needs_input", "target")
    # Concordancia de genero: "atividade" e feminino, "risco" e "marco" nao.
    assert outcome.question == "Encontrei mais de uma atividade parecida. Qual delas?"
    assert {c.label for c in outcome.candidates} == {
        "Instalacao do lote 1 de equipamentos de sinalizacao",
        "Instalacao do lote 2 de equipamentos de sinalizacao",
    }

    chosen = service.create_preview(
        PreviewRequest(project_code="PRJ-0442", field="cronograma.status",
                       target_id=ACTIVITY_LOTE2, raw_value="atrasado"),
        gerente(),
    )
    assert chosen.status == "preview"
    assert chosen.preview.target.id == ACTIVITY_LOTE2


def test_pedido_incompleto_vira_pergunta(setup):
    service, _repo, _clock = setup
    sem_projeto = ask(service, "Altera o prazo final para 31/03/2027", gerente()).outcome
    assert (sem_projeto.status, sem_projeto.missing) == ("needs_input", "project")
    assert [c.id for c in sem_projeto.candidates] == ["PRJ-0442"]

    sem_dia = ask(service, "Prorroga o prazo do PRJ-0442 até março", gerente()).outcome
    assert (sem_dia.status, sem_dia.missing) == ("needs_input", "value")
    assert "dia exato" in sem_dia.question

    sem_registro = ask(service, "Muda o status do risco do PRJ-0442 para mitigado", gerente()).outcome
    assert (sem_registro.status, sem_registro.missing) == ("needs_input", "target")
    assert len(sem_registro.candidates) == 3


def test_registro_inexistente_e_recusado_com_os_nomes_disponiveis(setup):
    service, _repo, _clock = setup
    outcome = ask(service, "Muda o status do risco Enchente na estação do PRJ-0442 para mitigado", gerente()).outcome
    assert (outcome.status, outcome.code) == ("rejected", "TARGET_NOT_FOUND")
    assert "Interferencia com a operacao comercial" in outcome.message


def test_historico_mostra_a_alteracao_e_quem_pode_desfazer(setup):
    service, _repo, clock = setup
    preview = ask(service, "Prorroga o prazo do PRJ-0442 para 31/03/2027", gerente()).outcome.preview
    change = service.confirm(preview.pending_change_id, gerente())

    history = service.history("PRJ-0442", "projeto.prazo_final", None, gerente())
    item = history.items[0]
    assert (item.change_id, item.status, item.can_undo) == (change.change_id, "aplicada", True)
    assert (item.before.display, item.after.display) == ("20/12/2026", "31/03/2027")

    # Outro perfil com leitura ve o historico, mas nao pode desfazer.
    assert service.history("PRJ-0442", "projeto.prazo_final", None, pmo()).items[0].can_undo is False

    service.undo(change.change_id, gerente())
    assert service.history("PRJ-0442", "projeto.prazo_final", None, gerente()).items[0].status == "desfeita"

    with pytest.raises(DataChangeError) as error:
        service.history("PRJ-0442", "projeto.prazo_final", None, consulta())
    assert error.value.code == "OUT_OF_SCOPE_FOR_PROFILE"
    clock.advance(minutes=1)


def test_avisos_da_previa(setup):
    service, _repo, _clock = setup
    outcome = ask(service, "Marca o marco Início da operação assistida na Linha Azul do PRJ-0442 como concluído",
                  gerente()).outcome
    assert any("sem data de conclusão" in warning for warning in outcome.preview.warnings)

    outcome = ask(service, "Altera o prazo do risco Interferência com a operação comercial do PRJ-0442 para 01/10/2026",
                  gerente()).outcome
    assert "A data informada já passou." in outcome.preview.warnings


@pytest.mark.parametrize("value", ["-10%", "1000%", "35,555%", "1.000%"])
def test_regressao_progresso_invalido_nao_gera_previa_nem_escrita(setup, value):
    """Revisao do MR da #260: -10%, 1000% e 35,555% gravavam 10, 0 e 5."""

    service, repo, _clock = setup
    outcome = ask(
        service,
        f"Atualiza o progresso da atividade Instalação do lote 2 de equipamentos de sinalização do PRJ-0442 para {value}",
        gerente(),
    ).outcome

    assert (outcome.status, outcome.code) == ("rejected", "INVALID_VALUE")
    assert repo.state.pending == {}
    assert repo.state.change_records == {}
    assert repo.state.targets["cronograma"][ACTIVITY_LOTE2].values["progress_percent"] == Decimal("35.00")


@pytest.mark.parametrize(
    "message",
    ["Prorroga o prazo do PRJ-0442 para 31/03/20277", "Prorroga o prazo do PRJ-0442 para 31 de março de 20277"],
)
def test_regressao_data_com_ano_invalido_e_recusada(setup, message):
    service, repo, _clock = setup
    outcome = ask(service, message, gerente()).outcome
    assert (outcome.status, outcome.code) == ("rejected", "INVALID_VALUE")
    assert repo.state.pending == {}
    assert project_value(repo, "planned_end_date") == date(2026, 12, 20)
