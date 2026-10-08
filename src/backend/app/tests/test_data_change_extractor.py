"""Extrator deterministico e regras de campo da alteracao pelo chat (S5-06)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.data_changes.extractor import extract_change
from app.data_changes.fields import FIELDS, InvalidValueError, canonical, parse_value, validate

TODAY = date(2026, 10, 6)


@pytest.mark.parametrize(
    ("message", "entity", "field", "reference", "raw_value"),
    [
        ("Prorroga o prazo do PRJ-0442 para 31/03/2027",
         "projeto", "projeto.prazo_final", None, "31/03/2027"),
        # O classificador leva esta frase para consulta (Secao 8.11.6); o extrator nao depende dele.
        ("prorroga o prazo do PRJ-0442 até 31 de março de 2027",
         "projeto", "projeto.prazo_final", None, "31 de março de 2027"),
        ("Muda o status do risco Interferência com a operação comercial do PRJ-0442 para em tratamento",
         "risco", "risco.status", "Interferência com a operação comercial", "em_tratamento"),
        ("Marca o marco Início da operação assistida na Linha Azul do PRJ-0442 como em andamento",
         "marco", "marco.status", "Início da operação assistida na Linha Azul", "em_andamento"),
        ("Atualiza o progresso da atividade Instalação do lote 2 do PRJ-0442 para 60%",
         "cronograma", "cronograma.progresso", "Instalação do lote 2", "60"),
        ("Muda o responsável do risco Compatibilidade com equipamentos legados do PRJ-0442 para Gerência de Engenharia",
         "risco", "risco.responsavel", "Compatibilidade com equipamentos legados", "Gerência de Engenharia"),
        ("Registra a conclusão do marco Instalação do primeiro lote do PRJ-0442 em 05/10/2026",
         "marco", "marco.data_conclusao", "Instalação do primeiro lote", "05/10/2026"),
        ("Adia a data prevista do marco Aceite definitivo no PRJ-0442 para 15/03/2027",
         "marco", "marco.data_prevista", "Aceite definitivo", "15/03/2027"),
        ('Atualiza o prazo do risco "Restricao de janela operacional" no PRJ-0442 para 30/11',
         "risco", "risco.prazo", "Restricao de janela operacional", "30/11"),
        ("Marca a atividade Testes integrados no PRJ-0442 como concluída",
         "cronograma", "cronograma.status", "Testes integrados", "concluido"),
        ("Pode mudar o status do PRJ-0510 para atenção?",
         "projeto", "projeto.status", None, "atencao"),
    ],
)
def test_pedidos_reconhecidos(message, entity, field, reference, raw_value):
    extracted = extract_change(message, TODAY)
    assert extracted is not None
    assert (extracted.entity, extracted.field, extracted.item_reference, extracted.raw_value) == (
        entity, field, reference, raw_value,
    )
    assert extracted.problem is None


@pytest.mark.parametrize(
    "message",
    [
        "Qual o prazo do PRJ-0442?",
        "Quando termina o PRJ-0442?",
        "Como está o status do PRJ-0442?",
        "Mostre o status do PRJ-0442",
        "Atualize o PRJ-0442",
        "Quais riscos do PRJ-0442 mudaram de status?",
        "Resuma o cronograma do PRJ-0442",
    ],
)
def test_perguntas_e_pedidos_sem_campo_seguem_o_fluxo_normal(message):
    assert extract_change(message, TODAY) is None


@pytest.mark.parametrize(
    ("message", "problem"),
    [
        ("Altera o orçamento do PRJ-0442 para 2 milhões", "FIELD_NOT_EDITABLE"),
        ("Muda o gerente do PRJ-0442 para Ana", "FIELD_NOT_EDITABLE"),
        ("Atualiza o progresso do PRJ-0442 para 50%", "FIELD_NOT_EDITABLE"),
        ("Muda o status e o prazo do PRJ-0442", "MULTIPLE_CHANGES"),
        ("Muda o status do PRJ-0442 e do PRJ-0510 para crítico", "MULTIPLE_CHANGES"),
    ],
)
def test_problemas_identificados_no_texto(message, problem):
    extracted = extract_change(message, TODAY)
    assert extracted is not None and extracted.problem == problem


def test_mes_sem_dia_e_pedido_sem_projeto_ficam_incompletos():
    sem_dia = extract_change("Prorroga o prazo do PRJ-0442 até março", TODAY)
    assert sem_dia.missing_day is True and sem_dia.raw_value is None

    sem_projeto = extract_change("Altera o prazo final para 31/03/2027", TODAY)
    assert sem_projeto.project_code is None and sem_projeto.raw_value == "31/03/2027"

    sem_registro = extract_change("Altera o prazo do risco do PRJ-0442 para 30/11/2026", TODAY)
    assert sem_registro.item_reference is None


@pytest.mark.parametrize(
    ("field", "raw", "expected"),
    [
        ("projeto.prazo_final", "31/03/2027", date(2027, 3, 31)),
        ("projeto.prazo_final", "31/03/27", date(2027, 3, 31)),
        ("projeto.prazo_final", "2027-03-31", date(2027, 3, 31)),
        ("projeto.prazo_final", "31 de março de 2027", date(2027, 3, 31)),
        # Sem ano: a proxima ocorrencia da data.
        ("projeto.prazo_final", "30/11", date(2026, 11, 30)),
        ("projeto.prazo_final", "05/01", date(2027, 1, 5)),
        ("cronograma.progresso", "60", Decimal("60")),
        ("cronograma.progresso", "62,5%", Decimal("62.5")),
        ("risco.status", "em tratamento", "em_tratamento"),
        ("marco.status", "finalizado", "concluido"),
        ("risco.responsavel", "  Gerência   de Operação. ", "Gerência de Operação"),
    ],
)
def test_parse_de_valores(field, raw, expected):
    assert parse_value(FIELDS[field], raw, TODAY) == expected


@pytest.mark.parametrize(
    ("field", "raw", "fragment"),
    [
        ("projeto.status", "concluído", "processo formal do PMO"),
        ("projeto.status", "descontinuado", "processo formal do PMO"),
        ("marco.status", "bloqueado", "Status do marco aceita"),
        ("risco.status", "atrasado", "Status do risco aceita"),
        ("cronograma.progresso", "62,555", "duas casas decimais"),
        ("cronograma.progresso", "-5", "entre 0 e 100"),
        ("projeto.prazo_final", "31/04/2027", "não existe no calendário"),
        ("projeto.prazo_final", "em breve", "dd/mm/aaaa"),
        ("risco.responsavel", "A", "de 2 a 160 caracteres"),
        ("risco.responsavel", "Fulano 11 99999-8888", "dado pessoal ou sensível"),
    ],
)
def test_valores_invalidos(field, raw, fragment):
    with pytest.raises(InvalidValueError) as error:
        parse_value(FIELDS[field], raw, TODAY)
    assert fragment in str(error.value)


def test_regras_que_dependem_do_registro():
    prazo = FIELDS["projeto.prazo_final"]
    with pytest.raises(InvalidValueError):
        validate(prazo, date(2026, 1, 1), {"start_date": date(2026, 1, 15), "status": "em_andamento"}, TODAY)
    with pytest.raises(InvalidValueError):
        validate(prazo, date(2027, 1, 1), {"start_date": None, "status": "concluido"}, TODAY)
    atividade = FIELDS["cronograma.prazo"]
    with pytest.raises(InvalidValueError):
        validate(atividade, date(2026, 9, 1), {"planned_start_date": date(2026, 9, 21)}, TODAY)
    conclusao = FIELDS["marco.data_conclusao"]
    assert validate(conclusao, TODAY, {}, TODAY).canonical == "2026-10-06"
    with pytest.raises(InvalidValueError):
        validate(conclusao, date(2026, 10, 7), {}, TODAY)


def test_forma_canonica_e_estavel_para_comparar_antes_e_depois():
    progresso = FIELDS["cronograma.progresso"]
    assert canonical(progresso, Decimal("35.00")) == canonical(progresso, Decimal("35")) == "35"
    assert canonical(progresso, Decimal("62.50")) == "62.5"
    assert canonical(FIELDS["projeto.prazo_final"], date(2026, 12, 20)) == "2026-12-20"
    assert canonical(FIELDS["risco.prazo"], None) is None


# --------------------------------------------------------------------------
# Regressao da revisao do MR da #260: o numero vai inteiro para a validacao
# --------------------------------------------------------------------------

PROGRESSO = "Atualiza o progresso da atividade Instalação do lote 2 de equipamentos de sinalização do PRJ-0442 para "


@pytest.mark.parametrize(
    ("value", "raw"),
    [
        ("-10%", "-10"),
        ("−10%", "-10"),  # sinal de menos tipografico
        ("1000%", "1000"),
        ("35,555%", "35,555"),
        ("1.000%", "1.000"),
        ("62,5%", "62,5"),
        ("100%", "100"),
    ],
)
def test_extrator_preserva_sinal_e_casas_decimais_do_progresso(value, raw):
    assert extract_change(PROGRESSO + value, TODAY).raw_value == raw


@pytest.mark.parametrize(
    ("raw", "fragment"),
    [
        ("-10", "entre 0 e 100"),
        ("1000", "entre 0 e 100"),
        ("35,555", "duas casas decimais"),
        ("1.000", "duas casas decimais"),
        ("35.5550", "duas casas decimais"),
        ("1.000,5", "número de 0 a 100"),
    ],
)
def test_progresso_fora_do_intervalo_ou_com_tres_casas_e_recusado(raw, fragment):
    with pytest.raises(InvalidValueError) as error:
        parse_value(FIELDS["cronograma.progresso"], raw, TODAY)
    assert fragment in str(error.value)


@pytest.mark.parametrize(
    ("message", "raw"),
    [
        ("Prorroga o prazo do PRJ-0442 para 31/03/20277", "31/03/20277"),
        ("Prorroga o prazo do PRJ-0442 para 31 de março de 20277", "31 de março de 20277"),
    ],
)
def test_data_com_ano_invalido_nao_vira_data_sem_ano(message, raw):
    extracted = extract_change(message, TODAY)
    # Antes, "31/03/20277" casava como "31/03" e virava 31/03/2027 sem aviso,
    # e "março" sem data valida era lido como marco do projeto.
    assert (extracted.entity, extracted.field, extracted.raw_value) == ("projeto", "projeto.prazo_final", raw)
    with pytest.raises(InvalidValueError):
        parse_value(FIELDS["projeto.prazo_final"], extracted.raw_value, TODAY)
