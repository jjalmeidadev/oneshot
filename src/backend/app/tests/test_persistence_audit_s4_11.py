"""Invariantes de persistencia e auditoria no Supabase (S4-11, issue #200).

Estes testes cruzam a fronteira backend <-> Supabase, que ate a Sprint 4 nao
tinha cobertura automatizada nenhuma (achado A-02 do relatorio S4-11).

Cada teste corresponde a um caso CV do relatorio em
docs/testes/sprint4/relatorio-s4-11.md. O relatorio registra a rodada; estes
testes registram a invariante, que vale em qualquer rodada.

Regras que este modulo respeita:
- somente leitura. A conexao e colocada em read_only antes de qualquer query;
  nenhum teste escreve, cria ou apaga dado.
- sem credencial embutida. A URL vem de DATABASE_URL ou SUPABASE_DATABASE_URL,
  e o modulo inteiro e ignorado quando elas nao estao no ambiente.
- defeito conhecido vira xfail(strict=True), nao assert comentado. Quando o
  defeito for corrigido o teste passa inesperadamente e o strict acusa,
  lembrando de remover o marcador.
"""

from __future__ import annotations

from typing import Any

import pytest

from app.database.connection import (
    DatabaseConfigurationError,
    open_database_connection,
)

pytestmark = pytest.mark.integration

# Escrita de uma interacao nao e atomica com a da conversa: a conversa nasce
# primeiro. Sem esta folga, uma interacao em voo no instante da consulta
# derrubaria o teste sem que houvesse defeito algum.
JANELA_DE_ESCRITA_SEGUNDOS = 300

_FOLGA = f"NOW() - INTERVAL '{JANELA_DE_ESCRITA_SEGUNDOS} seconds'"

# Corte historico da auditoria completa.
#
# A rodada de linha de base da #228 encontrou 2 interacoes sem nenhum evento de
# auditoria, ambas de 11/09/2026 (Sprint 3), do caminho de baixa confianca:
# "qa final baixa confianca indefinida" e "verificacao controlada baixa
# confianca". Sao sondagens manuais de QA daquela data.
#
# Nao ha reincidencia: em ~2.600 interacoes posteriores, todas tem auditoria. O
# codigo atual de _insert_audit_events sempre emite ao menos o evento
# api_interaction_processed, qualquer que seja o status.
#
# Sem este corte, o invariante reprovaria para sempre por causa de dois
# registros de uma versao anterior do codigo, e deixaria de servir para o que
# importa: acusar uma ocorrencia NOVA. Os dois registros historicos estao
# documentados no relatorio da #228; o corte nao os esconde, apenas tira do
# teste um fato ja fechado.
INICIO_DA_AUDITORIA_COMPLETA = "2026-09-12"

_APOS_O_CORTE = f"i.created_at >= DATE '{INICIO_DA_AUDITORIA_COMPLETA}'"


@pytest.fixture(scope="module")
def connection() -> Any:
    try:
        conn = open_database_connection()
    except DatabaseConfigurationError as error:
        pytest.skip(f"Banco nao configurado neste ambiente: {error}")
    except Exception as error:  # rede, DNS, credencial invalida
        pytest.skip(f"Supabase inacessivel: {type(error).__name__}")

    try:
        conn.read_only = True
    except Exception:
        # Driver sem suporte a read_only: os testes continuam sendo apenas
        # SELECT, mas sem a garantia do lado do servidor.
        pass

    try:
        yield conn
    finally:
        conn.close()


def _contar(connection: Any, sql: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchone()
        return int(row[0]) if row else 0


# --------------------------------------------------------------------------
# CV-02 — integridade do vinculo conversa <-> interacao
# --------------------------------------------------------------------------


def test_toda_interacao_pertence_a_uma_conversa_existente(connection: Any) -> None:
    orfas = _contar(
        connection,
        """
        SELECT COUNT(*)
          FROM public.ai_interactions i
          LEFT JOIN public.ai_conversations c ON c.id = i.conversation_id
         WHERE c.id IS NULL
        """,
    )

    assert orfas == 0, f"{orfas} interacoes apontam para conversa inexistente"


def test_conversa_nao_fica_sem_interacao(connection: Any) -> None:
    vazias = _contar(
        connection,
        f"""
        SELECT COUNT(*)
          FROM public.ai_conversations c
         WHERE c.created_at < {_FOLGA}
           AND NOT EXISTS (SELECT 1
                             FROM public.ai_interactions i
                            WHERE i.conversation_id = c.id)
        """,
    )

    assert vazias == 0, (
        f"{vazias} conversas foram abertas sem que a interacao fosse gravada"
    )


# --------------------------------------------------------------------------
# CV-03 — o que o schema nao consegue garantir sozinho
# --------------------------------------------------------------------------


def test_interacao_processada_tem_intencao_e_resposta(connection: Any) -> None:
    # O classificador pode ser desativado explicitamente na requisicao. Eventos
    # antigos nao registravam a flag; neles, a presenca de evento PLN indica
    # que a classificacao era esperada.
    incompletas = _contar(
        connection,
        """
        SELECT COUNT(*)
          FROM public.ai_interactions
         WHERE processing_status = 'processado'
           AND (
               response_text IS NULL
               OR (macro_intent_predicted IS NULL AND COALESCE(
                   (SELECT (e.event_payload->>'intent_classifier_enabled')::boolean
                      FROM public.audit_events e
                     WHERE e.interaction_id = ai_interactions.id
                       AND e.event_type = 'api_interaction_processed'
                     ORDER BY e.occurred_at DESC
                     LIMIT 1),
                   EXISTS (SELECT 1 FROM public.audit_events e
                            WHERE e.interaction_id = ai_interactions.id
                              AND e.event_type = 'pln_intent_classified')
               ))
           )
        """,
    )

    assert incompletas == 0, (
        f"{incompletas} interacoes processadas sem resposta ou sem intencao "
        "macro quando a classificacao era esperada"
    )


# --------------------------------------------------------------------------
# CV-04 — a persistencia e append-only
# --------------------------------------------------------------------------


def test_reexecucao_nao_sobrescreve_registro_anterior(connection: Any) -> None:
    # Reexecutar a mesma pergunta tem que criar uma linha nova. Se alguma
    # interacao tiver updated_at bem depois do created_at, alguem reescreveu
    # historico em vez de acrescentar.
    sobrescritas = _contar(
        connection,
        """
        SELECT COUNT(*)
          FROM public.ai_interactions
         WHERE updated_at > created_at + INTERVAL '1 second'
        """,
    )

    assert sobrescritas == 0, (
        f"{sobrescritas} interacoes foram alteradas apos a escrita inicial"
    )


# --------------------------------------------------------------------------
# CV-05 / CV-06 — cadeia de correlacao e auditoria
# --------------------------------------------------------------------------


def test_toda_interacao_gera_evento_de_auditoria(connection: Any) -> None:
    sem_auditoria = _contar(
        connection,
        f"""
        SELECT COUNT(*)
          FROM public.ai_interactions i
         WHERE i.created_at < {_FOLGA}
           AND {_APOS_O_CORTE}
           AND NOT EXISTS (SELECT 1
                             FROM public.audit_events e
                            WHERE e.interaction_id = i.id)
        """,
    )

    assert sem_auditoria == 0, (
        f"{sem_auditoria} interacoes nao produziram nenhum evento de auditoria"
    )


def test_evento_de_auditoria_carrega_identificador_de_correlacao(
    connection: Any,
) -> None:
    sem_correlacao = _contar(
        connection,
        """
        SELECT COUNT(*)
          FROM public.audit_events
         WHERE interaction_id IS NOT NULL
           AND correlation_id IS NULL
        """,
    )

    assert sem_correlacao == 0, (
        f"{sem_correlacao} eventos ligados a uma interacao nao tem correlation_id"
    )


def test_interacao_nao_mistura_dois_identificadores_de_correlacao(
    connection: Any,
) -> None:
    inconsistentes = _contar(
        connection,
        """
        SELECT COUNT(*)
          FROM (SELECT interaction_id
                  FROM public.audit_events
                 WHERE interaction_id IS NOT NULL
                   AND correlation_id IS NOT NULL
                 GROUP BY interaction_id
                HAVING COUNT(DISTINCT correlation_id) > 1) t
        """,
    )

    assert inconsistentes == 0, (
        f"{inconsistentes} interacoes tem eventos com correlation_id divergente, "
        "o que quebra a reconstrucao da cadeia"
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "D-04: rodada 1 encontrou 6 respostas de rota documental sem nenhuma "
        "fonte citada. Causa ainda nao diagnosticada. Ver secao 8.1 do "
        "relatorio S4-11."
    ),
)
def test_resposta_documental_cita_pelo_menos_uma_fonte(connection: Any) -> None:
    # Rota documental que responde sem citar fonte e resposta sem lastro.
    sem_fonte = _contar(
        connection,
        """
        SELECT COUNT(*)
          FROM public.ai_interactions i
         WHERE i.route_taken IN ('sharepoint_query', 'analise_local')
           AND i.processing_status = 'processado'
           AND NOT EXISTS (SELECT 1
                             FROM public.consulted_sources s
                            WHERE s.interaction_id = i.id)
        """,
    )

    assert sem_fonte == 0, (
        f"{sem_fonte} respostas de rota documental nao citaram nenhuma fonte"
    )


def test_pergunta_fora_de_escopo_nao_cita_fonte(connection: Any) -> None:
    # Negativo: citar fonte para pergunta fora do dominio e o pior resultado
    # possivel, porque da aparencia de lastro a uma resposta que nao tem.
    com_fonte = _contar(
        connection,
        """
        SELECT COUNT(*)
          FROM public.ai_interactions i
         WHERE i.route_taken = 'fora_escopo'
           AND EXISTS (SELECT 1
                         FROM public.consulted_sources s
                        WHERE s.interaction_id = i.id)
        """,
    )

    assert com_fonte == 0, (
        f"{com_fonte} perguntas fora de escopo vieram com fonte citada"
    )


# --------------------------------------------------------------------------
# CV-08 — defeito D-02, conhecido e documentado
# --------------------------------------------------------------------------


def test_pergunta_fora_de_escopo_e_registrada_para_curadoria(
    connection: Any,
) -> None:
    classificadas = _contar(
        connection,
        """
        SELECT COUNT(*)
          FROM public.ai_interactions
         WHERE route_taken = 'fora_escopo'
            OR processing_status = 'fora_escopo'
            OR macro_intent_predicted = 'FORA_DE_ESCOPO'
        """,
    )
    registradas = _contar(
        connection,
        """
        SELECT COUNT(*)
          FROM public.ai_interactions i
         WHERE (i.route_taken = 'fora_escopo'
             OR i.processing_status = 'fora_escopo'
             OR i.macro_intent_predicted = 'FORA_DE_ESCOPO')
           AND EXISTS (SELECT 1
                         FROM public.out_of_scope_requests o
                        WHERE o.interaction_id = i.id)
        """,
    )

    assert classificadas > 0, "sem massa fora de escopo para avaliar"
    assert registradas == classificadas, (
        f"{classificadas} perguntas classificadas como fora de escopo e apenas "
        f"{registradas} registradas em out_of_scope_requests: a fila de "
        "curadoria do intent_catalog fica sem entrada"
    )


# --------------------------------------------------------------------------
# CV-09 e CV-12 — defeito D-01, reprogramado para a Sprint 5
# --------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "D-01: users esta vazia. A carga da S4-09 cobre portfolio e intencoes, "
        "nunca identidade. Reprogramado para a Sprint 5."
    ),
)
def test_perfis_sinteticos_estao_cadastrados(connection: Any) -> None:
    perfis = _contar(
        connection,
        """
        SELECT COUNT(DISTINCT role_name)
          FROM public.users
         WHERE is_active
           AND role_name IN ('diretoria', 'lider_subportfolio', 'equipe_projeto')
        """,
    )

    assert perfis == 3, (
        f"apenas {perfis} dos 3 perfis sinteticos exigidos estao cadastrados"
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "D-01: a rota textual nao exige identidade, entao user_id fica nulo. "
        "E o unico item do RNF03 que reprova. Reprogramado para a Sprint 5."
    ),
)
def test_interacao_carrega_o_usuario_autenticado(connection: Any) -> None:
    sem_usuario = _contar(
        connection,
        """
        SELECT COUNT(*)
          FROM public.ai_interactions
         WHERE user_id IS NULL
        """,
    )

    assert sem_usuario == 0, (
        f"{sem_usuario} interacoes nao identificam o usuario, o que impede "
        "rastreabilidade por pessoa"
    )


# --------------------------------------------------------------------------
# D-05 — componente fora do dominio na auditoria do fluxo guiado
# Teste estatico: le o codigo e o schema, nao precisa de banco.
# Mesmo estilo de test_rag_synthetic_sql.py, que valida o texto do .sql.
# --------------------------------------------------------------------------

import re
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[3]
TRACING_PATH = SRC_ROOT / "backend" / "app" / "database" / "tracing.py"
SCHEMA_PATH = SRC_ROOT / "database" / "sql" / "01_create_database.sql"


def _componentes_aceitos_pelo_schema() -> set[str]:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    trecho = re.search(
        r"audit_events_component_ck CHECK \(component IN \(([^)]*)\)",
        sql,
    )
    assert trecho, "constraint audit_events_component_ck nao encontrada no schema"
    return set(re.findall(r"'([a-z0-9_]+)'", trecho.group(1)))


def _componente_do_evento_de_fluxo_guiado() -> str:
    codigo = TRACING_PATH.read_text(encoding="utf-8")
    trecho = re.search(
        r'"guided_workflow_dispatched",\s*\n\s*"([a-z0-9_]+)"',
        codigo,
    )
    assert trecho, "evento guided_workflow_dispatched nao encontrado em tracing.py"
    return trecho.group(1)


def test_componente_do_fluxo_guiado_esta_no_dominio_do_schema() -> None:
    aceitos = _componentes_aceitos_pelo_schema()
    usado = _componente_do_evento_de_fluxo_guiado()

    assert usado in aceitos, (
        f"tracing.py emite component={usado!r}, fora do dominio aceito pelo "
        f"schema ({sorted(aceitos)}). O INSERT viola a constraint e o rollback "
        "de trace_interaction descarta conversa, interacao, fontes e eventos."
    )
