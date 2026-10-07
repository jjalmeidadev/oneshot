from __future__ import annotations

import json

import pytest

from app.rag import reindex
from scripts import reindex_sharepoint_mock as cli


VALID_COVERAGE = [
    ("PRJ-0442", 1, 1),
    ("PRJ-0510", 1, 1),
    ("PRJ-0587", 1, 1),
]


class FakeCursor:
    def __init__(self, connection: "FakeConnection") -> None:
        self.connection = connection
        self.query = ""

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *_args) -> None:
        return None

    def execute(self, query: str, params=None) -> None:
        self.query = query
        self.connection.executions.append((query, params))
        if self.connection.fail_seed and "BEGIN;" in query:
            raise RuntimeError("seed failure")

    def fetchall(self):
        if self.query == reindex.COVERAGE_QUERY:
            return self.connection.coverage
        raise AssertionError("fetchall inesperado")

    def fetchone(self):
        if self.query == reindex.DUPLICATE_EXTRACTS_QUERY:
            return (self.connection.duplicate_groups,)
        raise AssertionError("fetchone inesperado")


class FakeConnection:
    def __init__(
        self,
        *,
        coverage=VALID_COVERAGE,
        duplicate_groups: int = 0,
        fail_seed: bool = False,
    ) -> None:
        self.coverage = coverage
        self.duplicate_groups = duplicate_groups
        self.fail_seed = fail_seed
        self.executions: list[tuple[str, object]] = []
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def cursor(self) -> FakeCursor:
        return FakeCursor(self)

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1

    def close(self) -> None:
        self.closed = True


def test_seed_updates_existing_extracts_and_inserts_only_missing_ones() -> None:
    sql = reindex.DEFAULT_SEED_PATH.read_text(encoding="utf-8")

    assert "updated_extracts AS" in sql
    assert "UPDATE public.source_extracts existing" in sql
    assert "FROM updated_extracts updated" in sql
    assert "WHERE NOT EXISTS" in sql
    assert "DELETE FROM public.source_extracts" not in sql


def test_reapplying_seed_keeps_the_same_valid_coverage() -> None:
    connection = FakeConnection()

    reindex.apply_sharepoint_mock_seed(connection)
    first = reindex.inspect_sharepoint_mock_coverage(connection)
    reindex.apply_sharepoint_mock_seed(connection)
    second = reindex.inspect_sharepoint_mock_coverage(connection)

    seed_executions = [
        query for query, _params in connection.executions if "BEGIN;" in query
    ]
    assert len(seed_executions) == 2
    assert connection.commits == 2
    assert first == second
    assert second["duplicate_extract_groups"] == 0


@pytest.mark.parametrize(
    ("coverage", "duplicate_groups", "message"),
    [
        (VALID_COVERAGE[:2], 0, "PRJ-0587"),
        (VALID_COVERAGE, 1, "extratos duplicados"),
    ],
)
def test_coverage_validation_rejects_missing_or_duplicate_documents(
    coverage, duplicate_groups: int, message: str
) -> None:
    connection = FakeConnection(
        coverage=coverage,
        duplicate_groups=duplicate_groups,
    )

    with pytest.raises(reindex.SharePointMockCoverageError, match=message):
        reindex.inspect_sharepoint_mock_coverage(connection)


def test_seed_rolls_back_when_database_execution_fails() -> None:
    connection = FakeConnection(fail_seed=True)

    with pytest.raises(RuntimeError, match="seed failure"):
        reindex.apply_sharepoint_mock_seed(connection)

    assert connection.commits == 0
    assert connection.rollbacks == 1


def test_reindex_operation_applies_validates_and_closes(monkeypatch) -> None:
    connection = FakeConnection()
    monkeypatch.setenv("DATABASE_URL", "postgresql://test.invalid/test")

    result = reindex.reindex_sharepoint_mock(connect=lambda *_args, **_kwargs: connection)

    assert result["valid"] is True
    assert connection.commits == 1
    assert connection.closed is True


@pytest.mark.parametrize("command", ["apply", "status"])
def test_cli_prints_machine_readable_status(monkeypatch, capsys, command: str) -> None:
    expected = {"valid": True, "command": command}
    monkeypatch.setattr(cli, "_load_environment", lambda: None)
    monkeypatch.setattr(cli, "reindex_sharepoint_mock", lambda: expected)
    monkeypatch.setattr(cli, "sharepoint_mock_status", lambda: expected)
    monkeypatch.setattr("sys.argv", ["reindex_sharepoint_mock.py", command])

    assert cli.main() == 0
    assert json.loads(capsys.readouterr().out) == expected
