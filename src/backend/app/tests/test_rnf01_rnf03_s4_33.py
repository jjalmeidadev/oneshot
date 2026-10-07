"""RNF01 a RNF03 — confidencialidade, acesso por perfil e auditoria (S4-33, #209 → #229).

Casos conforme a Secao 9.2.3 do docs/Projeto.md: um positivo e um negativo por
requisito. Os IDs aqui seguem os do plano (CT-RNF01-P, CT-RNF01-N, ...).

Os casos de RNF01 nao precisam de banco nem de rede: trabalham sobre a massa
sintetica e sobre o prompt montado antes da chamada ao provedor. Os de RNF02 e
RNF03 conferem a persistencia e exigem SUPABASE_DATABASE_URL (ou DATABASE_URL);
sem ela, se ignoram sozinhos.

Defeitos conhecidos entram como xfail(strict=True), com a causa no reason.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest
from dotenv import load_dotenv

from app.database.connection import (
    DatabaseConfigurationError,
    open_database_connection,
)
from app.gemini.client import generate_chat_response
from app.gemini.schemas import GeminiChatRequest
from app.rag.sharepoint import (
    build_rag_input,
    load_sharepoint_documents,
    retrieve_sharepoint_context,
)

load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)

pytestmark = pytest.mark.integration

DATA_DIR = Path(__file__).resolve().parents[1] / "rag" / "data" / "sharepoint"

# Marcador inequivocamente sensivel, na forma que a Secao 9.2.3 pede para o
# cenario negativo do RNF01. Nao corresponde a nenhuma pessoa real.
MARCADOR_SENSIVEL = "DADO-SENSIVEL-CT-RNF01-N-NAO-DEVE-SAIR"


@pytest.fixture(scope="module")
def connection() -> Any:
    try:
        conn = open_database_connection()
    except DatabaseConfigurationError as error:
        pytest.skip(f"Banco nao configurado: {error}")
    except Exception as error:
        pytest.skip(f"Supabase inacessivel: {type(error).__name__}")

    try:
        conn.read_only = True
    except Exception:
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


# ==========================================================================
# RNF01 — confidencialidade
# Criterio: 100% da massa e sintetica/anonimizada e nenhum dado marcado como
# sensivel chega a servico nao homologado.
# ==========================================================================


# Listas simuladas que compoem a massa do MVP. O prefixo "sharepoint-mock:"
# so aparece no identificador gravado no banco pela carga SQL; o carregador de
# JSON monta o identificador como "<lista>:<item>".
LISTAS_SIMULADAS = frozenset(
    {
        "base-atendimento",
        "comunicados-servico",
        "documentos-projetos",
        "procedimentos-operacionais",
    }
)


def test_ct_rnf01_p_massa_e_integralmente_sintetica() -> None:
    documentos = load_sharepoint_documents(DATA_DIR)

    assert documentos, "massa sintetica nao encontrada no diretorio esperado"

    fora_do_dominio_simulado = [
        d.source_id for d in documentos if "mock.sharepoint.local" not in d.web_url
    ]
    assert not fora_do_dominio_simulado, (
        f"{len(fora_do_dominio_simulado)} documentos apontam para fora do dominio "
        f"simulado: {fora_do_dominio_simulado[:5]}"
    )

    fora_das_listas = [
        d.source_id
        for d in documentos
        if d.source_id.split(":", 1)[0] not in LISTAS_SIMULADAS
    ]
    assert not fora_das_listas, (
        f"{len(fora_das_listas)} documentos vieram de lista nao prevista na massa "
        f"sintetica: {fora_das_listas[:5]}"
    )


def test_ct_rnf01_p_prompt_declara_origem_ficticia() -> None:
    documentos = load_sharepoint_documents(DATA_DIR)
    resultados = retrieve_sharepoint_context("objeto perdido", documents=documentos)

    if not resultados:
        pytest.skip("consulta de sondagem nao recuperou documento")

    prompt = build_rag_input("Pergunta de sondagem", resultados)

    assert "dados ficticios para o MVP" in prompt, (
        "o prompt enviado ao provedor nao declara que o contexto e ficticio"
    )


def test_ct_rnf01_n_marcador_sensivel_nao_chega_ao_provedor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CT-RNF01-N, corrigido pela S5-27 (D-06).

    Segue a Secao 9.2.3: injeta o marcador numa copia temporaria da massa,
    repete o envio pelo caminho real (`generate_chat_response`) e captura com
    um duplo de rede tudo o que sairia para o provedor. O marcador nao pode
    aparecer em nenhum payload, e a contagem de chamadas externas com dado
    sensivel tem de ser zero.
    """

    # Copia temporaria da massa, como manda a Secao 9.2.3: o original nao e tocado.
    massa_temporaria = tmp_path / "sharepoint"
    shutil.copytree(DATA_DIR, massa_temporaria)

    # Injeta o marcador em todo item, para que qualquer documento recuperado
    # carregue o dado proibido.
    for arquivo in sorted(massa_temporaria.glob("*.json")):
        payload = json.loads(arquivo.read_text(encoding="utf-8"))
        for item in payload.get("value", []):
            campos = item.get("fields", {})
            for chave in ("Conteudo", "Conteudo0", "Descricao"):
                if chave in campos:
                    campos[chave] = f"{campos[chave]} {MARCADOR_SENSIVEL}"
        arquivo.write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )

    documentos = load_sharepoint_documents(massa_temporaria)
    assert documentos, "massa temporaria nao carregou"
    resultados = retrieve_sharepoint_context("objeto perdido", documents=documentos)
    if not resultados:
        pytest.skip("consulta de sondagem nao recuperou documento da copia")
    assert any(MARCADOR_SENSIVEL in r.document.content for r in resultados)

    # Duplo de rede: guarda o payload de cada chamada ao provedor.
    payloads: list[str] = []

    class _Resposta:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self) -> bytes:
            return json.dumps(
                {
                    "id": "ct-rnf01-n",
                    "model": "duplo-de-rede",
                    "status": "completed",
                    "steps": [
                        {
                            "type": "model_output",
                            "content": [{"type": "text", "text": "Evidencia insuficiente."}],
                        }
                    ],
                    "usage": {"total_tokens": 1},
                }
            ).encode("utf-8")

    def duplo_de_rede(request, timeout):
        payloads.append(request.data.decode("utf-8"))
        return _Resposta()

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setattr("app.gemini.client.urlopen", duplo_de_rede)
    monkeypatch.setattr(
        "app.gemini.client.retrieve_context", lambda *_a, **_k: resultados
    )

    resposta = generate_chat_response(
        GeminiChatRequest(message="Pergunta de sondagem", use_intent_classifier=False)
    )

    chamadas_com_dado_sensivel = [p for p in payloads if MARCADOR_SENSIVEL in p]
    assert chamadas_com_dado_sensivel == [], (
        "o marcador sensivel atravessou a montagem do prompt e seria enviado ao "
        "provedor externo"
    )
    assert all("[DADO CLASSIFICADO]" in p for p in payloads)
    assert all(MARCADOR_SENSIVEL not in (f.excerpt or "") for f in resposta.sources)
    assert resposta.security_report is not None
    assert resposta.security_report["categories"] == ["marcador_classificacao"]
    assert MARCADOR_SENSIVEL not in json.dumps(resposta.security_report)


# ==========================================================================
# RNF02 — acesso por perfil
# Criterio: 100% das respostas de cada perfil contem somente recursos autorizados.
# ==========================================================================


@pytest.mark.xfail(
    strict=True,
    reason=(
        "D-01: users e access_rules estao vazias. A carga sintetica da S4-09 "
        "cobre portfolio e intencoes, nunca identidade. Reprogramado para a "
        "Sprint 5. Ver secao 5 do relatorio S4-11."
    ),
)
def test_ct_rnf02_p_perfis_e_regras_de_acesso_existem(connection: Any) -> None:
    perfis = _contar(
        connection,
        """
        SELECT COUNT(DISTINCT role_name)
          FROM public.users
         WHERE is_active
           AND role_name IN ('diretoria', 'lider_subportfolio', 'equipe_projeto')
        """,
    )
    regras = _contar(
        connection, "SELECT COUNT(*) FROM public.access_rules WHERE is_active"
    )

    assert perfis >= 3, f"apenas {perfis} dos 3 perfis exigidos estao cadastrados"
    assert regras > 0, "nenhuma regra de acesso cadastrada"


@pytest.mark.xfail(
    strict=True,
    reason=(
        "D-01: o backend nunca consulta access_rules e nunca emite "
        "OUT_OF_SCOPE_FOR_PROFILE, entao nenhuma negacao por perfil pode ser "
        "registrada. Reprogramado para a Sprint 5."
    ),
)
def test_ct_rnf02_n_negacao_por_perfil_e_auditada(connection: Any) -> None:
    # Atencao ao criterio: event_status = 'bloqueado' NAO serve como sinal de
    # negacao por perfil. _insert_audit_events marca o evento de PLN como
    # 'bloqueado' sempre que o status e 'sem_confianca' ou 'fora_escopo', que
    # sao recusas de classificacao, nao de autorizacao. Contar esse status
    # daria falso positivo. O sinal correto de negacao por perfil e o erro
    # OUT_OF_SCOPE_FOR_PROFILE, que o backend nunca emite.
    negacoes_por_perfil = _contar(
        connection,
        """
        SELECT COUNT(*)
          FROM public.audit_events
         WHERE event_payload::text ILIKE '%OUT_OF_SCOPE_FOR_PROFILE%'
            OR event_type ILIKE '%perfil%'
            OR event_type ILIKE '%profile%'
            OR event_type ILIKE '%authorization%'
        """,
    )

    assert negacoes_por_perfil > 0, (
        "nenhum evento de negacao por perfil registrado: o sistema nunca negou "
        "acesso com base no perfil do solicitante"
    )


# ==========================================================================
# RNF03 — auditoria
# Criterio: 100% dos casos registram perfil, horario, intencao, fontes e
# resposta ou falha.
# ==========================================================================


def test_ct_rnf03_p_registro_tem_horario_intencao_e_resposta(
    connection: Any,
) -> None:
    incompletos = _contar(
        connection,
        """
        SELECT COUNT(*)
          FROM public.ai_interactions
         WHERE processing_status = 'processado'
           AND (created_at IS NULL
                OR macro_intent_predicted IS NULL
                OR response_text IS NULL)
        """,
    )

    assert incompletos == 0, (
        f"{incompletos} interacoes concluidas sem horario, intencao ou resposta"
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "D-04: respostas de rota documental sem nenhuma fonte registrada. "
        "Encontrado na rodada da #200 (6 ocorrencias) e confirmado aqui, com a "
        "massa maior. Causa ainda nao diagnosticada: ou a recuperacao nao achou "
        "nada e o sistema respondeu assim mesmo, ou a escrita das fontes falhou."
    ),
)
def test_ct_rnf03_p_resposta_com_fonte_registra_as_fontes(connection: Any) -> None:
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
        f"{sem_fonte} respostas de rota documental sem fonte registrada"
    )


def test_ct_rnf03_n_falha_registra_estado_de_erro_e_auditoria(
    connection: Any,
) -> None:
    com_erro = _contar(
        connection,
        "SELECT COUNT(*) FROM public.ai_interactions WHERE processing_status = 'erro'",
    )
    if com_erro == 0:
        pytest.skip("sem massa de erro na base para avaliar o cenario negativo")

    auditados = _contar(
        connection,
        """
        SELECT COUNT(*)
          FROM public.ai_interactions i
         WHERE i.processing_status = 'erro'
           AND EXISTS (SELECT 1
                         FROM public.audit_events e
                        WHERE e.interaction_id = i.id
                          AND e.event_status = 'falha')
        """,
    )

    assert auditados == com_erro, (
        f"{com_erro} interacoes com erro e apenas {auditados} auditadas como "
        "falha: houve falha sem registro"
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "D-01: a rota textual nao exige identidade, entao ai_interactions.user_id "
        "fica nulo. E o unico campo do criterio do RNF03 que reprova; horario, "
        "intencao, fontes e resposta estao todos registrados."
    ),
)
def test_ct_rnf03_p_registro_identifica_o_perfil(connection: Any) -> None:
    sem_perfil = _contar(
        connection,
        "SELECT COUNT(*) FROM public.ai_interactions WHERE user_id IS NULL",
    )

    assert sem_perfil == 0, (
        f"{sem_perfil} interacoes nao identificam o perfil do solicitante"
    )
