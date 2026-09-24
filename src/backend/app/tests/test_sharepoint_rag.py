from pathlib import Path

import pytest

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

    prompt = build_rag_input("Posso levar bicicleta?", results)

    assert "[Fonte 1] Transporte de bicicleta" in prompt
    assert "dados ficticios para o MVP" in prompt
    assert "Pergunta do usuario: Posso levar bicicleta?" in prompt
