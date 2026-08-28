from pathlib import Path

from app.rag.sharepoint import (
    build_rag_input,
    load_sharepoint_documents,
    retrieve_sharepoint_context,
)


DATA_DIR = (
    Path(__file__).resolve().parents[1] / "rag" / "data" / "sharepoint"
)


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


def test_builds_prompt_with_source_labels_and_disclaimer() -> None:
    documents = load_sharepoint_documents(DATA_DIR)
    results = retrieve_sharepoint_context("bicicleta", documents=documents)

    prompt = build_rag_input("Posso levar bicicleta?", results)

    assert "[Fonte 1] Transporte de bicicleta" in prompt
    assert "dados ficticios para o MVP" in prompt
    assert "Pergunta do usuario: Posso levar bicicleta?" in prompt
