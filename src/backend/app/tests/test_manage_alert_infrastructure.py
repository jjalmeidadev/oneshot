"""Gates locais do gerenciador; nenhuma conexão externa é aberta."""

import sys

import pytest

from scripts import manage_alert_infrastructure as manager


def test_apply_requires_prepared_migration(monkeypatch):
    executed = []
    monkeypatch.setattr(manager, "schema_status", lambda: {"migration_08_ready": False})
    monkeypatch.setattr(manager, "execute", executed.append)
    monkeypatch.setattr(sys, "argv", ["manage_alert_infrastructure.py", "apply"])

    with pytest.raises(SystemExit):
        manager.main()
    assert executed == []


def test_apply_refuses_existing_alert_tables(monkeypatch):
    executed = []
    current = {"migration_08_ready": True, **dict.fromkeys(manager.ALERT_TABLES, False)}
    current["alert_subscriptions"] = True
    monkeypatch.setattr(manager, "schema_status", lambda: current)
    monkeypatch.setattr(manager, "execute", executed.append)
    monkeypatch.setattr(sys, "argv", ["manage_alert_infrastructure.py", "apply"])

    with pytest.raises(SystemExit):
        manager.main()
    assert executed == []


@pytest.mark.parametrize(
    ("command", "confirmation"),
    [("prepare-proactive", "--confirm-expired-cleanup"), ("rollback", "--confirm-destructive")],
)
def test_mutating_commands_require_explicit_confirmation(monkeypatch, command, confirmation):
    executed = []
    monkeypatch.setattr(manager, "execute", executed.append)
    monkeypatch.setattr(sys, "argv", ["manage_alert_infrastructure.py", command])
    with pytest.raises(SystemExit):
        manager.main()
    assert executed == []

    monkeypatch.setattr(sys, "argv", ["manage_alert_infrastructure.py", command, confirmation])
    assert manager.main() == 0
    assert executed == [manager.PREPARE if command == "prepare-proactive" else manager.ROLLBACK]
