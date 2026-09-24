import json
from pathlib import Path
from types import SimpleNamespace

from app.nlp.schemas import AudioIntent
from app.rag.sharepoint import RetrievedDocument, SharePointDocument
from scripts import benchmark_token_hypothesis as benchmark


def _classification(macro="CONSULTA", specific="consulta_status_projeto"):
    return SimpleNamespace(
        macrointencao=macro,
        intencao=specific,
        confianca_macro=0.9,
        confianca_intencao=0.8,
        fluxo="Consulta documental",
        handler=f"handler:{specific}",
        alternativas=[(specific, 0.8)],
        resposta_sugerida=None,
        roteada=True,
    )


def _intent() -> AudioIntent:
    return AudioIntent(
        macro="CONSULTA",
        specific="consulta_status_projeto",
        confidence_macro=0.9,
        confidence_specific=0.8,
        handler="handler:consulta_status_projeto",
    )


def _source() -> RetrievedDocument:
    return RetrievedDocument(
        document=SharePointDocument(
            source_id="fonte:1",
            title="Status",
            list_name="Massa controlada",
            content="Projeto em execucao.",
            web_url="https://example.test/status",
            last_modified="2026-09-23",
            search_text="status projeto",
        ),
        score=1.0,
    )


def test_run_variant_persists_request_response_and_usage(monkeypatch):
    monkeypatch.setattr(
        benchmark,
        "_call_openrouter",
        lambda *_args, **_kwargs: {
            "model": "google/gemini-3.1-flash-lite",
            "choices": [{"message": {"content": "Resposta [Fonte 1]."}}],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 20,
                "total_tokens": 120,
            },
        },
    )
    persisted = []
    monkeypatch.setattr(
        benchmark,
        "_write_json",
        lambda path, payload: persisted.append((path, payload)),
    )

    result = benchmark._run_variant(
        case={"id": "consulta", "prompt": "status", "sources": [{"id": "1"}]},
        variant=benchmark.VARIANTS[1],
        classification=_classification(),
        intent=_intent(),
        sources=[_source()],
        api_key="secret-not-persisted",
        model="google/gemini-3.1-flash-lite",
        raw_dir=Path("json-bruto"),
    )

    raw = persisted[0][1]
    assert raw["request"]["messages"][0]["content"].startswith("Voce e um assistente")
    assert "secret-not-persisted" not in json.dumps(raw)
    assert result["llm_calls"] == 1
    assert result["total_tokens"] == 120
    assert result["has_expected_citation"] is True


def test_classifier_skip_persists_zero_token_result(monkeypatch):
    classification = _classification(
        macro="FORA_DE_ESCOPO",
        specific="fora_de_escopo_externo",
    )
    classification.resposta_sugerida = "Solicitacao fora do escopo."
    persisted = []
    monkeypatch.setattr(
        benchmark,
        "_write_json",
        lambda path, payload: persisted.append((path, payload)),
    )

    result = benchmark._run_variant(
        case={"id": "fora", "prompt": "tempo", "sources": []},
        variant=benchmark.VARIANTS[1],
        classification=classification,
        intent=AudioIntent(
            macro="FORA_DE_ESCOPO",
            specific="",
            confidence_macro=0.9,
            confidence_specific=0.8,
        ),
        sources=[],
        api_key="unused",
        model="unused",
        raw_dir=Path("json-bruto"),
    )

    assert result["llm_calls"] == 0
    assert result["total_tokens"] == 0
    assert result["status"] == "roteado_sem_llm"
    assert persisted[0][1]["skipped"] is True


def test_summary_calculates_reduction_against_classifier_off():
    results = []
    for variant, total, calls in (
        ("classificador_desligado", 200, 2),
        ("classificador_ligado", 100, 1),
        ("classificador_e_secundaria_inline", 120, 1),
    ):
        results.append(
            {
                "variant": {"name": variant},
                "llm_calls": calls,
                "input_tokens": total,
                "output_tokens": 0,
                "reasoning_tokens": 0,
                "total_tokens": total,
                "status": "concluido",
            }
        )

    summary = benchmark._summarize(results)

    assert summary["classificador_ligado"]["token_reduction_vs_classifier_off"] == 0.5
    assert summary["classificador_e_secundaria_inline"][
        "token_reduction_vs_classifier_off"
    ] == 0.4
