from datetime import datetime, timezone

import pytest

from app.database.connection import DatabaseConnectionError
from app.gemini.client import GeminiAPIError, generate_chat_response
from app.gemini.schemas import GeminiChatRequest
from app.nlp.schemas import AudioIntent, PublicEntity
from app.rag.database import retrieve_context, retrieve_database_context
from test_gemini_client import FakeResponse


class FakeCursor:
    def __init__(self, rows=None, error: Exception | None = None) -> None:
        self.rows = rows or []
        self.error = error
        self.executed_query = ""
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query: str, params: tuple[object, ...]) -> None:
        self.executed_query = query
        self.params = params
        if self.error:
            raise self.error

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self.cursor_instance = cursor
        self.closed = False

    def cursor(self) -> FakeCursor:
        return self.cursor_instance

    def close(self) -> None:
        self.closed = True


def _connect_with_rows(rows):
    cursor = FakeCursor(rows=rows)
    connection = FakeConnection(cursor)

    def connect(_database_url: str, **_kwargs):
        return connection

    return connect, connection


def _intent(specific: str = "consulta_status_projeto") -> AudioIntent:
    return AudioIntent(
        macro="CONSULTA",
        specific=specific,
        confidence_macro=0.9,
        confidence_specific=0.8,
    )


def _entity(value: str, entity_type: str = "projeto") -> PublicEntity:
    return PublicEntity(
        type=entity_type,
        value=value,
        text=value,
        start=0,
        end=len(value),
        types=[entity_type],
    )


def test_retrieves_source_extracts_from_database(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@example/postgres")
    connect, connection = _connect_with_rows(
        [
            (
                "extract-1",
                "artifact-1",
                "project-1",
                "sharepoint-mock:base-atendimento:303",
                "Transporte de bicicleta",
                "Base de Atendimento",
                "https://mock/sharepoint/303",
                datetime(2026, 8, 12, tzinfo=timezone.utc),
                "Bicicletas sao aceitas aos sabados, domingos e feriados.",
                "base-atendimento/303#Conteudo",
                None,
                None,
                {"validity": {"start": "2026-08-20", "end": "2026-09-05"}, "status": "Publicado", "line": "Todas", "category": "Regras de uso"},
                4.5,
            )
        ]
    )

    results = retrieve_database_context(
        "Posso transportar bicicleta?",
        intent=_intent(),
        connect=connect,
    )

    assert results[0].document.source_id == "sharepoint-mock:base-atendimento:303"
    assert results[0].document.title == "Transporte de bicicleta"
    assert results[0].document.list_name == "Base de Atendimento"
    assert results[0].score == 4.5
    # DEF-RNF04-01: vigencia, status, linha e categoria vivem em
    # source_extracts.metadata e precisam sobreviver ate o prompt.
    assert ("Vigencia", "de 2026-08-20 a 2026-09-05") in results[0].document.attributes
    assert ("Status", "Publicado") in results[0].document.attributes
    assert "se.metadata" in connection.cursor_instance.executed_query
    assert "source_extracts" in connection.cursor_instance.executed_query
    assert "project_artifacts" in connection.cursor_instance.executed_query
    assert connection.closed is True


def test_database_search_uses_project_or_line_entity(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@example/postgres")
    connect, connection = _connect_with_rows([])

    retrieve_database_context(
        "Qual e o status?",
        intent=_intent(),
        entities=[_entity("Linha 1-Azul", entity_type="linha")],
        connect=connect,
    )

    query_terms, entity_terms, *_rest = connection.cursor_instance.params
    assert "status" in query_terms
    assert "Linha 1-Azul" in entity_terms
    assert "linha" in entity_terms
    assert "azul" in entity_terms


def test_database_results_are_compatible_with_gemini_source(monkeypatch):
    captured_request = None
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@example/postgres")

    def fake_urlopen(request, timeout: int) -> FakeResponse:
        nonlocal captured_request
        captured_request = request
        assert timeout == 30
        return FakeResponse(
            {
                "id": "interaction-db-rag",
                "model": "gemini-3.7-flash",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [{"type": "text", "text": "Fonte recuperada."}],
                    }
                ],
                "usage": {},
            }
        )

    database_result = retrieve_database_context(
        "bicicleta",
        connect=_connect_with_rows(
            [
                    (
                        "extract-1",
                        "artifact-1",
                        "project-1",
                        "sharepoint-mock:base-atendimento:303",
                        "Transporte de bicicleta",
                        "Base de Atendimento",
                        "https://mock/sharepoint/303",
                        "2026-08-12 11:05:00+00",
                        "Bicicletas sao aceitas em horarios simulados.",
                        "base-atendimento/303#Conteudo",
                        None,
                        None,
                        {"validity": {"start": "2026-08-20", "end": "2026-09-05"}, "status": "Publicado", "line": "Todas", "category": "Regras de uso"},
                        3.0,
                )
            ]
        )[0],
    )
    monkeypatch.setattr("app.gemini.client.retrieve_context", lambda *_args, **_kwargs: database_result)
    monkeypatch.setattr("app.gemini.client.urlopen", fake_urlopen)

    response = generate_chat_response(
        GeminiChatRequest(message="Posso transportar bicicleta?"),
        intent=_intent(),
    )

    assert response.sources[0].title == "Transporte de bicicleta"
    assert response.sources[0].list_name == "Base de Atendimento"
    assert response.sources[0].excerpt == "Bicicletas sao aceitas em horarios simulados."
    assert "[Fonte 1] Transporte de bicicleta" in captured_request.data.decode("utf-8")


def test_absence_of_database_result_returns_rf08_explicit_response(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@example/postgres")
    monkeypatch.setattr("app.gemini.client.retrieve_context", lambda *_args, **_kwargs: [])

    response = generate_chat_response(
        GeminiChatRequest(message="Qual o prazo do projeto inexistente?"),
        intent=_intent("consulta_cronograma_prazo"),
    )

    assert response.model == "rag-retriever"
    assert response.sources == []
    assert response.text == (
        "Essa solicitação não está no escopo da base de conhecimento disponível."
    )


def test_generic_fallback_does_not_call_llm_without_rag_context(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr("app.gemini.client.retrieve_context", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(
        "app.gemini.client._call_llm",
        lambda *_args, **_kwargs: pytest.fail("LLM nao deve responder sem fonte RAG"),
    )

    response = generate_chat_response(
        GeminiChatRequest(message="pergunta ambigua"),
        intent=None,
        require_rag_context=True,
    )

    assert response.model == "rag-retriever"
    assert response.sources == []
    assert response.text == (
        "Essa solicitação não está no escopo da base de conhecimento disponível."
    )


def test_database_error_does_not_leak_secret_or_internal_detail(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret-token@example/postgres")

    def connect(_database_url: str, **_kwargs):
        return FakeConnection(
            FakeCursor(error=RuntimeError("password secret-token stack trace"))
        )

    with pytest.raises(DatabaseConnectionError) as error:
        retrieve_database_context("bicicleta", connect=connect)

    assert str(error.value) == "Nao foi possivel recuperar contexto no banco de dados."
    assert "secret-token" not in str(error.value)
    assert "stack trace" not in str(error.value)


def test_gemini_maps_database_error_to_controlled_provider_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret-token@example/postgres")
    monkeypatch.setattr(
        "app.gemini.client.retrieve_context",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            DatabaseConnectionError("password secret-token stack trace")
        ),
    )

    with pytest.raises(GeminiAPIError) as error:
        generate_chat_response(GeminiChatRequest(message="bicicleta"), intent=_intent())

    assert error.value.status_code == 503
    assert "secret-token" not in str(error.value)
    assert "stack trace" not in str(error.value)


def test_json_fallback_is_explicit_when_database_url_is_absent(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_DATABASE_URL", raising=False)

    results = retrieve_context("bicicleta")

    assert results
    assert results[0].document.title == "Transporte de bicicleta"


@pytest.mark.parametrize("use_entities", [True, False])
def test_explicit_project_excludes_other_projects_even_with_same_keywords(monkeypatch, use_entities):
    monkeypatch.setenv("DATABASE_URL", "postgresql://synthetic:synthetic@example.test/test")
    rows = [dict(extract_id=f"extract-{code}", artifact_id=f"artifact-{code}",
        project_id=f"project-{code}", project_code=code,
        artifact_title="Status do projeto", content_text="Status: Em andamento",
        extract_metadata={}, score=10) for code in ["PRJ-9999", "PRJ-0017"]]
    connect, connection = _connect_with_rows(rows)
    results = retrieve_database_context(
        "Qual o status?" if use_entities else "Qual o status do PRJ-0017?",
        entities=[_entity("PRJ-0017")] if use_entities else [], connect=connect)
    assert len(results) == 1
    assert results[0].document.project_id == "project-PRJ-0017"
    assert connection.cursor_instance.params[2] == ["prj-0017"]
    assert "requested_projects" in connection.cursor_instance.executed_query


def test_absent_project_never_uses_another_projects_source(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://synthetic:synthetic@example.test/test")
    rows = [dict(extract_id="extract-1", project_id="project-1", project_code="PRJ-9999",
                 content_text="Status: Em andamento", extract_metadata={}, score=10)]
    connect, _ = _connect_with_rows(rows)
    assert retrieve_database_context("Status PRJ-0017", connect=connect) == []


def test_local_fallback_without_project_identity_abstains():
    assert retrieve_context("Status e bicicleta no PRJ-0017") == []
