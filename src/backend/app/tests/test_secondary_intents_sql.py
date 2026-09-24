from pathlib import Path
import json
import re


REPO_ROOT = Path(__file__).resolve().parents[3]
SQL_DIR = REPO_ROOT / "database" / "sql"
BASELINE_SQL = SQL_DIR / "01_create_database.sql"
SEED_SQL = SQL_DIR / "02_initial_data.sql"
MIGRATION_SQL = SQL_DIR / "05_add_secondary_intents.sql"
VERIFICATION_SQL = SQL_DIR / "06_verify_secondary_intents.sql"
PENDING_MIGRATION_SQL = SQL_DIR / "07_add_pending_proactive_suggestions.sql"
PREPARED_RESPONSE_MIGRATION_SQL = SQL_DIR / "08_add_prepared_proactive_response.sql"
LOCAL_CATALOG = REPO_ROOT / "backend" / "app" / "rag" / "data" / "secondary_intents.json"

EXPECTED_MAPPINGS = {
    "consulta_status_projeto": "sugerir_agilizacao_projeto",
    "consulta_cronograma_prazo": "sugerir_recuperacao_prazo",
    "consulta_marcos_entregas": "sugerir_antecipacao_marco",
    "consulta_orcamento_custo": "sugerir_otimizacao_custo",
    "consulta_escopo_tap": "sugerir_clareza_escopo",
    "consulta_responsavel_equipe": "sugerir_coordenacao_equipe",
    "consulta_indicadores_kpi": "sugerir_melhoria_indicador",
    "consulta_riscos_projeto": "sugerir_mitigacao_risco",
    "consulta_pendencias_projeto": "sugerir_resolucao_pendencia",
    "consulta_documentos_fonte": "sugerir_regularizacao_documental",
    "consulta_visao_portfolio": "sugerir_priorizacao_portfolio",
    "comparacao_entre_projetos": "sugerir_pratica_replicavel",
    "analise_tendencia_desempenho": "sugerir_correcao_tendencia",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_baseline_and_migration_define_referential_contract() -> None:
    for sql in (_read(BASELINE_SQL), _read(MIGRATION_SQL)):
        normalized = re.sub(r"\s+", " ", sql.lower())

        assert "create table" in normalized
        assert "public.secondary_intents" in normalized
        assert "references public.intent_catalog(id) on delete cascade" in normalized
        assert "unique (specific_intent_id, secondary_intent)" in normalized
        assert "rag_instruction text not null" in normalized
        assert "display_message text not null" in normalized


def test_pending_confirmations_use_shared_scoped_storage() -> None:
    for path in (BASELINE_SQL, PENDING_MIGRATION_SQL):
        normalized = _read(path).lower()
        assert "public.pending_proactive_suggestions" in normalized
        assert "requester_id" in normalized
        assert "external_conversation_id" in normalized
        assert "expires_at" in normalized
        assert "claimed_at" in normalized


def test_pending_confirmations_persist_prepared_response() -> None:
    for path in (BASELINE_SQL, PENDING_MIGRATION_SQL, PREPARED_RESPONSE_MIGRATION_SQL):
        normalized = _read(path).lower()
        assert "prepared_response" in normalized
        assert "prepared_model" in normalized
        assert "prepared_interaction_id" in normalized


def test_initial_load_and_migration_cover_all_mappings_idempotently() -> None:
    seed_sql = _read(SEED_SQL)
    migration_sql = _read(MIGRATION_SQL)

    for sql in (seed_sql, migration_sql):
        for primary_intent, secondary_intent in EXPECTED_MAPPINGS.items():
            assert f"'{primary_intent}'" in sql
            assert f"'{secondary_intent}'" in sql

        normalized = re.sub(r"\s+", " ", sql.lower())
        assert "join public.intent_catalog catalog" in normalized
        assert "on conflict (specific_intent_id, secondary_intent) do update set" in normalized
        assert "rag_instruction = excluded.rag_instruction" in normalized
        assert "display_message = excluded.display_message" in normalized


def test_local_rag_fallback_matches_seeded_associations() -> None:
    payload = json.loads(_read(LOCAL_CATALOG))

    assert {
        primary: definition["secondary_intent"]
        for primary, definition in payload.items()
    } == EXPECTED_MAPPINGS


def test_verification_script_exercises_read_fk_uniqueness_and_rolls_back() -> None:
    sql = _read(VERIFICATION_SQL).lower()

    assert "join public.secondary_intents" in sql
    assert "foreign_key_violation" in sql
    assert "unique_violation" in sql
    assert "covered_intents <> 13" in sql
    assert sql.rstrip().endswith("rollback;")
