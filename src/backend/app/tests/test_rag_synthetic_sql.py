from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SQL_PATH = REPO_ROOT / "database" / "sql" / "04_rag_synthetic_data.sql"


def test_rag_synthetic_sql_exists_and_uses_required_sources():
    sql = SQL_PATH.read_text(encoding="utf-8")

    assert "base_atendimento.json" in sql
    assert "comunicados_servico.json" in sql
    assert "procedimentos_operacionais.json" in sql
    assert "'sharepoint-mock:' || list_id || ':' || item_id" in sql
    assert "'base-atendimento'" in sql
    assert "'comunicados-servico'" in sql
    assert "'procedimentos-operacionais'" in sql
    assert "'301'" in sql
    assert "'201'" in sql
    assert "'101'" in sql


def test_rag_synthetic_sql_is_idempotent_without_populating_consulted_sources():
    sql = SQL_PATH.read_text(encoding="utf-8").lower()

    assert "on conflict (partner_source_id)" in sql
    assert "where not exists" in sql
    assert "insert into public.source_extracts" in sql
    assert "insert into public.consulted_sources" not in sql
    assert "'mock', mock" in sql
    assert "'ficticio', true" in sql
