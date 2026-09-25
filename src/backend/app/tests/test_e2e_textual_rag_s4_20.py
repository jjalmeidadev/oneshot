"""E2E textual com RAG e verificacao de persistencia (S4-20, issue #209).

Diferente de app/tests/e2e_server.py, que substitui PLN, geracao e transcricao
por versoes deterministicas, este modulo fala com o backend REAL: PLN real,
recuperacao real, Gemini real, Supabase real. E a unica forma de atender o DoD
da #209, que exige que o cenario atravesse frontend, API, PLN, recuperacao e
resposta.

Por isso ele nao roda na suite normal. Precisa de:
  E2E_BASE_URL   endereco do backend ja no ar (ex.: http://localhost:8000)
  DATABASE_URL   ou SUPABASE_DATABASE_URL, para conferir a persistencia
Sem essas variaveis o modulo inteiro se ignora.

Como a API nao devolve o identificador da interacao gravada no banco (achado
A-04 do relatorio S4-20), a correlacao entre resposta e linha persistida e
feita por um marcador unico injetado no texto da pergunta.
"""

from __future__ import annotations

import os
import time
import uuid
from pathlib import Path
from typing import Any

import pytest
from dotenv import load_dotenv

# O backend carrega src/backend/.env pelo main.py. O pytest nao passa por la,
# entao carregamos o mesmo arquivo aqui. override=False para que uma variavel
# exportada no terminal continue tendo prioridade.
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)

from app.database.connection import (
    DatabaseConfigurationError,
    open_database_connection,
)

pytestmark = pytest.mark.integration

# Persistencia acontece depois que a resposta sai. Sem esta espera, a consulta
# ao banco pode chegar antes da escrita.
ESPERA_PERSISTENCIA_SEGUNDOS = 3

PERGUNTA_BASE = (
    "Qual e o status atual dos projetos do portfolio? "
    "Marcador de rastreio do teste E2E: {marcador}"
)


@pytest.fixture(scope="module")
def base_url() -> str:
    url = os.getenv("E2E_BASE_URL", "").strip()
    if not url:
        pytest.skip("E2E_BASE_URL nao definida: backend real nao esta no ar.")
    return url.rstrip("/")


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


@pytest.fixture(scope="module")
def resposta_e2e(base_url: str) -> dict[str, Any]:
    """Executa o cenario positivo uma vez e compartilha o resultado."""

    import httpx

    marcador = f"e2e-s4-20-{uuid.uuid4().hex[:12]}"
    pergunta = PERGUNTA_BASE.format(marcador=marcador)

    try:
        resposta = httpx.post(
            f"{base_url}/api/chat",
            json={"message": pergunta, "use_intent_classifier": True},
            timeout=60,
        )
    except Exception as error:
        pytest.skip(f"Backend nao respondeu em {base_url}: {type(error).__name__}")

    assert resposta.status_code == 200, (
        f"POST /api/chat devolveu {resposta.status_code}: {resposta.text[:300]}"
    )

    corpo = resposta.json()
    corpo["_marcador"] = marcador
    corpo["_pergunta"] = pergunta

    time.sleep(ESPERA_PERSISTENCIA_SEGUNDOS)
    return corpo


def _linhas(connection: Any, sql: str, params: tuple) -> list[tuple]:
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return list(cursor.fetchall())


# --------------------------------------------------------------------------
# E2E-01 — a pergunta atravessa API, PLN, recuperacao e geracao
# --------------------------------------------------------------------------


def test_resposta_traz_texto_e_modelo(resposta_e2e: dict[str, Any]) -> None:
    assert resposta_e2e.get("text"), "resposta sem texto gerado"
    assert resposta_e2e.get("model"), "resposta sem identificacao do modelo"


def test_camada_de_pln_foi_exercitada(resposta_e2e: dict[str, Any]) -> None:
    intent = resposta_e2e.get("intent")
    assert intent, "resposta sem intencao classificada: o PLN nao rodou"
    assert intent.get("macro"), "intencao sem macrointencao"

    metricas = resposta_e2e.get("pipeline_metrics") or {}
    assert metricas.get("nlp_ms", 0) > 0, (
        "nlp_ms igual a zero: a classificacao nao foi executada de fato"
    )


# --------------------------------------------------------------------------
# E2E-02 — a interacao e localizavel no Supabase, com a cadeia completa
# --------------------------------------------------------------------------


def test_interacao_foi_persistida_no_supabase(
    connection: Any, resposta_e2e: dict[str, Any]
) -> None:
    linhas = _linhas(
        connection,
        """
        SELECT id, conversation_id, route_taken, processing_status
          FROM public.ai_interactions
         WHERE user_prompt LIKE %s
        """,
        (f"%{resposta_e2e['_marcador']}%",),
    )

    assert len(linhas) == 1, (
        f"esperava 1 interacao com o marcador, encontrei {len(linhas)}"
    )
    resposta_e2e["_interaction_id"] = linhas[0][0]
    resposta_e2e["_conversation_id"] = linhas[0][1]


def test_conversa_da_interacao_existe(
    connection: Any, resposta_e2e: dict[str, Any]
) -> None:
    interaction_id = resposta_e2e.get("_interaction_id")
    if not interaction_id:
        pytest.skip("interacao nao localizada no teste anterior")

    linhas = _linhas(
        connection,
        """
        SELECT c.id, c.channel
          FROM public.ai_conversations c
          JOIN public.ai_interactions i ON i.conversation_id = c.id
         WHERE i.id = %s
        """,
        (interaction_id,),
    )

    assert len(linhas) == 1, "a interacao nao esta ligada a uma conversa"


def test_fontes_da_resposta_foram_persistidas(
    connection: Any, resposta_e2e: dict[str, Any]
) -> None:
    interaction_id = resposta_e2e.get("_interaction_id")
    if not interaction_id:
        pytest.skip("interacao nao localizada")

    fontes_na_resposta = resposta_e2e.get("sources") or []
    if not fontes_na_resposta:
        pytest.skip("a resposta nao citou fonte: nada a conferir na persistencia")

    linhas = _linhas(
        connection,
        "SELECT id FROM public.consulted_sources WHERE interaction_id = %s",
        (interaction_id,),
    )

    assert len(linhas) >= 1, (
        f"a resposta citou {len(fontes_na_resposta)} fonte(s) e nenhuma foi "
        "gravada em consulted_sources"
    )


def test_auditoria_da_interacao_foi_registrada(
    connection: Any, resposta_e2e: dict[str, Any]
) -> None:
    interaction_id = resposta_e2e.get("_interaction_id")
    if not interaction_id:
        pytest.skip("interacao nao localizada")

    linhas = _linhas(
        connection,
        """
        SELECT component, event_status
          FROM public.audit_events
         WHERE interaction_id = %s
        """,
        (interaction_id,),
    )

    assert linhas, "nenhum evento de auditoria para a interacao"
    componentes = {linha[0] for linha in linhas}
    assert "api" in componentes, (
        f"auditoria sem o componente api; componentes vistos: {sorted(componentes)}"
    )


# --------------------------------------------------------------------------
# E2E-05 — achado A-04: a resposta nao devolve a alca de correlacao
# --------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "A-04: _trace_safely em app/pipeline.py descarta o retorno de "
        "trace_interaction, entao o id da linha no Supabase nunca chega a "
        "resposta. O campo interaction_id carrega o id do provedor de geracao. "
        "Ver secao 6 do relatorio S4-20."
    ),
)
def test_resposta_permite_localizar_a_interacao_no_banco(
    connection: Any, resposta_e2e: dict[str, Any]
) -> None:
    interaction_id_da_resposta = resposta_e2e.get("interaction_id")
    assert interaction_id_da_resposta, "resposta sem interaction_id"

    linhas = _linhas(
        connection,
        "SELECT id FROM public.ai_interactions WHERE id::text = %s",
        (str(interaction_id_da_resposta),),
    )

    assert len(linhas) == 1, (
        "o interaction_id devolvido pela API nao corresponde a nenhuma linha em "
        "ai_interactions: o cliente nao consegue localizar o proprio registro"
    )
