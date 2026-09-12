import pytest

from app.database.connection import (
    DEFAULT_CONNECT_TIMEOUT_SECONDS,
    DatabaseConfigurationError,
    DatabaseConnectionError,
    probe_database_connection,
)


class FakeCursor:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query: str) -> None:
        self.queries.append(query)

    def fetchone(self) -> tuple[int]:
        return (1,)


class FakeConnection:
    def __init__(self) -> None:
        self.cursor_instance = FakeCursor()
        self.closed = False

    def cursor(self) -> FakeCursor:
        return self.cursor_instance

    def close(self) -> None:
        self.closed = True


def test_missing_database_env_raises_controlled_error(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_DATABASE_URL", raising=False)

    with pytest.raises(DatabaseConfigurationError) as error:
        probe_database_connection(connect=lambda *_args, **_kwargs: None)

    assert "DATABASE_URL" in str(error.value)


def test_successful_connection_executes_probe_query(monkeypatch):
    monkeypatch.setenv(
        "SUPABASE_DATABASE_URL",
        "postgresql://postgres.example:secret@pooler.supabase.com:5432/postgres",
    )
    calls = []
    fake_connection = FakeConnection()

    def connect(database_url: str, **kwargs):
        calls.append((database_url, kwargs))
        return fake_connection

    assert probe_database_connection(connect=connect) is True

    assert calls == [
        (
            "postgresql://postgres.example:secret@pooler.supabase.com:5432/postgres",
            {"connect_timeout": DEFAULT_CONNECT_TIMEOUT_SECONDS},
        )
    ]
    assert fake_connection.cursor_instance.queries == ["SELECT 1"]
    assert fake_connection.closed is True


def test_connection_error_returns_controlled_message(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://user:secret-token@example/postgres",
    )

    def connect(_database_url: str, **_kwargs):
        raise RuntimeError("could not connect to host with password secret-token")

    with pytest.raises(DatabaseConnectionError) as error:
        probe_database_connection(connect=connect)

    assert str(error.value) == (
        "Nao foi possivel conectar ao banco de dados. Tente novamente em instantes."
    )
    assert "secret-token" not in str(error.value)
