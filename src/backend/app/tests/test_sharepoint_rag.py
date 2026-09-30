from pathlib import Path

import pytest

from app.nlp.schemas import AudioIntent
from app.rag.sharepoint import (
    SharePointDocument,
    build_rag_input,
    load_sharepoint_documents,
    retrieve_sharepoint_context,
)


DATA_DIR = (
    Path(__file__).resolve().parents[1] / "rag" / "data" / "sharepoint"
)


#: Marcado pela #228 (S4-32B): este arquivo cruza fronteira entre
#: componentes (API, modelo, banco ou servico externo). Rodar so estes com
#: `pytest -m integration`.
pytestmark = pytest.mark.integration


def test_loads_mock_sharepoint_list_exports() -> None:
    documents = load_sharepoint_documents(DATA_DIR)

    assert len(documents) == 9
    assert {document.list_name for document in documents} == {
        "Base de Atendimento",
        "Comunicados de Servico",
        "Procedimentos Operacionais",
    }
    assert all(document.source_id and document.web_url for document in documents)


def test_retrieves_relevant_sharepoint_items() -> None:
    documents = load_sharepoint_documents(DATA_DIR)

    results = retrieve_sharepoint_context(
        "Como devo registrar um objeto perdido?",
        documents=documents,
        limit=2,
    )

    assert results
    assert results[0].document.title == "Atendimento a objeto perdido"
    assert results[0].score > 0
    assert len(results) == 1


def test_does_not_inject_context_for_unrelated_question() -> None:
    documents = load_sharepoint_documents(DATA_DIR)

    results = retrieve_sharepoint_context(
        "Explique a formacao das galaxias",
        documents=documents,
    )

    assert results == []
    assert build_rag_input("Pergunta geral", results) == "Pergunta geral"


def test_filters_out_of_scope_sources_before_building_model_context() -> None:
    documents = [
        SharePointDocument(
            source_id="allowed",
            title="Status permitido",
            list_name="Projetos",
            content="status permitido",
            web_url="https://example.invalid/allowed",
            last_modified="2026-09-29",
            search_text="status projeto permitido",
            project_id="fe091a56-310d-4465-8a13-5940d5765e1e",
            project_code="PRJ-0442",
        ),
        SharePointDocument(
            source_id="denied",
            title="Status restrito",
            list_name="Projetos",
            content="conteudo que nao pode chegar ao modelo",
            web_url="https://example.invalid/denied",
            last_modified="2026-09-29",
            search_text="status projeto restrito",
            project_id="3162119e-f361-4907-9358-6d32a4e91909",
            project_code="PRJ-0510",
        ),
    ]

    results = retrieve_sharepoint_context(
        "status projeto",
        documents=documents,
        allowed_project_ids={"PRJ-0442"},
    )
    prompt = build_rag_input("status projeto", results)

    assert [result.document.source_id for result in results] == ["allowed"]
    assert "status permitido" in prompt
    assert "conteudo que nao pode chegar ao modelo" not in prompt


@pytest.mark.parametrize(
    ("query", "expected_source_id"),
    [
        ("Meu passe no celular nao funciona na barreira", "base-atendimento:301"),
        ("Quero abrir uma queixa sobre o servico", "base-atendimento:302"),
        ("Posso levar bike no domingo?", "base-atendimento:303"),
        (
            "Os comboios vao atrasar no fim da noite?",
            "comunicados-servico:201",
        ),
        ("Por onde entro perto do Arouche?", "comunicados-servico:202"),
        (
            "Devo dar passagem a quem esta saindo do vagao?",
            "comunicados-servico:203",
        ),
        ("Achei uma mochila; onde devolvo?", "procedimentos-operacionais:101"),
    ],
)
def test_retrieves_context_for_domain_paraphrases(
    query: str,
    expected_source_id: str,
) -> None:
    documents = load_sharepoint_documents(DATA_DIR)

    results = retrieve_sharepoint_context(query, documents=documents, limit=3)

    assert expected_source_id in {
        result.document.source_id for result in results
    }


def test_builds_prompt_with_source_labels_and_disclaimer() -> None:
    documents = load_sharepoint_documents(DATA_DIR)
    results = retrieve_sharepoint_context("bicicleta", documents=documents)

    prompt = build_rag_input(
        "Posso levar bicicleta?",
        results,
        intent=AudioIntent(
            macro="CONSULTA",
            specific="consulta_documentos_fonte",
            confidence_macro=0.9,
            confidence_specific=0.8,
            handler="handler:consulta_documentos_fonte",
        ),
    )

    assert "[Fonte 1] Transporte de bicicleta" in prompt
    assert "dados ficticios para o MVP" in prompt
    assert "macro=CONSULTA; especifica=consulta_documentos_fonte" in prompt
    assert "Pergunta do usuario: Posso levar bicicleta?" in prompt
