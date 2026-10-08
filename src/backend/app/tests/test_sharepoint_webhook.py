"""Contrato HTTP inicial do webhook do SharePoint simulado."""

from copy import deepcopy

from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.sharepoint_webhooks.repository import reset_sharepoint_webhook_repository


PATH = "/api/integrations/sharepoint/change-notifications"
CLIENT_STATE = "segredo-compartilhado-com-pelo-menos-32-caracteres"


@pytest.fixture(autouse=True)
def isolated_repository(monkeypatch):
    monkeypatch.setenv("SHAREPOINT_WEBHOOK_REPOSITORY_MODE", "memory")
    reset_sharepoint_webhook_repository()
    yield
    reset_sharepoint_webhook_repository()


def valid_payload() -> dict:
    return {
        "value": [
            {
                "eventId": "d6a29bb6-9d2d-40dd-aa3f-20dc8d7a1218",
                "subscriptionId": "sharepoint-mock-documents",
                "clientState": CLIENT_STATE,
                "changeType": "updated",
                "resource": "lists/documentos_projetos/items/5101",
                "resourceData": {
                    "siteId": "metro-sp-mock",
                    "listId": "documentos_projetos",
                    "itemId": 5101,
                    "partnerSourceId": (
                        "sharepoint-mock:documentos_projetos:5101"
                    ),
                },
                "occurredAt": "2026-10-07T12:30:00-03:00",
            }
        ]
    }


def test_handshake_returns_validation_token_as_plain_text():
    with TestClient(app) as client:
        response = client.post(PATH, params={"validationToken": "validacao-123"})

    assert response.status_code == 200
    assert response.text == "validacao-123"
    assert response.headers["content-type"].startswith("text/plain")


def test_valid_payload_is_accepted_after_client_state_validation(monkeypatch):
    monkeypatch.setenv("SHAREPOINT_WEBHOOK_CLIENT_STATE", CLIENT_STATE)

    with TestClient(app) as client:
        response = client.post(PATH, json=valid_payload())

    assert response.status_code == 202
    assert response.json() == {
        "status": "accepted",
        "accepted": 1,
        "created": 1,
        "duplicates": 0,
    }


def test_repeated_event_is_accepted_without_duplication(monkeypatch):
    monkeypatch.setenv("SHAREPOINT_WEBHOOK_CLIENT_STATE", CLIENT_STATE)

    with TestClient(app) as client:
        first = client.post(PATH, json=valid_payload())
        repeated = client.post(PATH, json=valid_payload())

    assert first.status_code == repeated.status_code == 202
    assert first.json()["created"] == 1
    assert repeated.json()["created"] == 0
    assert repeated.json()["duplicates"] == 1


def test_reused_event_id_with_different_content_is_rejected(monkeypatch):
    monkeypatch.setenv("SHAREPOINT_WEBHOOK_CLIENT_STATE", CLIENT_STATE)
    changed = valid_payload()
    changed["value"][0]["changeType"] = "deleted"

    with TestClient(app) as client:
        first = client.post(PATH, json=valid_payload())
        conflict = client.post(PATH, json=changed)

    assert first.status_code == 202
    assert conflict.status_code == 409


def test_invalid_client_state_is_rejected_without_exposing_secrets(monkeypatch):
    monkeypatch.setenv("SHAREPOINT_WEBHOOK_CLIENT_STATE", CLIENT_STATE)
    payload = valid_payload()
    payload["value"][0]["clientState"] = "segredo-incorreto"

    with TestClient(app) as client:
        response = client.post(PATH, json=payload)

    assert response.status_code == 401
    assert CLIENT_STATE not in response.text
    assert "segredo-incorreto" not in response.text


def test_missing_client_state_is_rejected_by_contract(monkeypatch):
    monkeypatch.setenv("SHAREPOINT_WEBHOOK_CLIENT_STATE", CLIENT_STATE)
    payload = valid_payload()
    del payload["value"][0]["clientState"]

    with TestClient(app) as client:
        response = client.post(PATH, json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "SHAREPOINT_WEBHOOK_INVALID_INPUT"


def test_malformed_client_state_is_rejected_by_contract(monkeypatch):
    monkeypatch.setenv("SHAREPOINT_WEBHOOK_CLIENT_STATE", CLIENT_STATE)
    payload = valid_payload()
    payload["value"][0]["clientState"] = {"secret": CLIENT_STATE}

    with TestClient(app) as client:
        response = client.post(PATH, json=payload)

    assert response.status_code == 422
    assert CLIENT_STATE not in response.text


def test_invalid_field_type_is_rejected(monkeypatch):
    monkeypatch.setenv("SHAREPOINT_WEBHOOK_CLIENT_STATE", CLIENT_STATE)
    payload = valid_payload()
    payload["value"][0]["resourceData"]["itemId"] = "item-5101"

    with TestClient(app) as client:
        response = client.post(PATH, json=payload)

    assert response.status_code == 422


def test_resource_identifiers_must_be_consistent(monkeypatch):
    monkeypatch.setenv("SHAREPOINT_WEBHOOK_CLIENT_STATE", CLIENT_STATE)
    payload = deepcopy(valid_payload())
    payload["value"][0]["resourceData"]["partnerSourceId"] = (
        "sharepoint-mock:documentos_projetos:5102"
    )

    with TestClient(app) as client:
        response = client.post(PATH, json=payload)

    assert response.status_code == 422


def test_missing_server_configuration_returns_503():
    with TestClient(app) as client:
        response = client.post(PATH, json=valid_payload())

    assert response.status_code == 503
    assert CLIENT_STATE not in response.text


def test_unavailable_persistent_inbox_returns_503(monkeypatch):
    monkeypatch.setenv("SHAREPOINT_WEBHOOK_CLIENT_STATE", CLIENT_STATE)
    monkeypatch.setenv("SHAREPOINT_WEBHOOK_REPOSITORY_MODE", "database")
    reset_sharepoint_webhook_repository()

    with TestClient(app) as client:
        response = client.post(PATH, json=valid_payload())

    assert response.status_code == 503


def test_normal_notification_requires_payload():
    with TestClient(app) as client:
        response = client.post(PATH)

    assert response.status_code == 422
