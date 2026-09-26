"""Executa o A/B da issue #253 via OpenRouter e persiste os JSONs observados."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.nlp.inference import classify  # noqa: E402
from app.nlp.schemas import AudioIntent, IntentAlternative  # noqa: E402
from app.rag.proactivity import resolve_secondary_intent  # noqa: E402
from app.rag.sharepoint import (  # noqa: E402
    RetrievedDocument,
    SharePointDocument,
    build_rag_input,
)


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemini-3.1-flash-lite"
DEFAULT_CASES = (
    REPO_ROOT
    / "docs"
    / "evidencias"
    / "sprint-04"
    / "hipotese-tokens"
    / "casos.json"
)
DEFAULT_OUTPUT_DIR = DEFAULT_CASES.parent / "execucao"


@dataclass(frozen=True)
class Variant:
    name: str
    classifier_enabled: bool
    inline_secondary_enabled: bool


VARIANTS = (
    Variant("classificador_desligado", False, False),
    Variant("classificador_ligado", True, False),
    Variant("classificador_e_secundaria_inline", True, True),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compara tokens com o classificador ligado e desligado."
    )
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--model", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_dotenv(BACKEND_ROOT / ".env")
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            "Configure OPENROUTER_API_KEY em src/backend/.env antes da execucao."
        )

    model = args.model or os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL).strip()
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    execution_dir = args.output_dir / datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )
    raw_dir = execution_dir / "json-bruto"
    raw_dir.mkdir(parents=True, exist_ok=False)

    results = []
    for case in cases:
        classification = classify(case["prompt"])
        intent = _public_intent(classification)
        sources = _sources(case.get("sources", []))
        for variant in VARIANTS:
            result = _run_variant(
                case=case,
                variant=variant,
                classification=classification,
                intent=intent,
                sources=sources,
                api_key=api_key,
                model=model,
                raw_dir=raw_dir,
            )
            results.append(result)

    report = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provider": "OpenRouter",
        "model_requested": model,
        "hypothesis": (
            "O classificador reduz tokens agregados por roteamento e a intencao "
            "secundaria preparada na chamada principal evita uma segunda chamada."
        ),
        "latency_in_scope": False,
        "cases_file": str(args.cases.relative_to(REPO_ROOT)),
        "results": results,
        "summary": _summarize(results),
    }
    _write_json(execution_dir / "resultado.json", report)
    print(execution_dir)
    return 0


def _run_variant(
    *,
    case: dict,
    variant: Variant,
    classification: object,
    intent: AudioIntent,
    sources: list[RetrievedDocument],
    api_key: str,
    model: str,
    raw_dir: Path,
) -> dict:
    skip_reason = _skip_reason(classification) if variant.classifier_enabled else None
    secondary = (
        resolve_secondary_intent(intent)
        if variant.inline_secondary_enabled and skip_reason is None
        else None
    )
    effective_intent = intent if variant.classifier_enabled else None
    prompt = build_rag_input(
        case["prompt"],
        sources,
        intent=effective_intent,
        secondary_intent=secondary,
    )
    request_payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": _max_output_tokens(),
    }
    raw_path = raw_dir / f"{_slug(case['id'])}--{variant.name}.json"

    if skip_reason is not None:
        raw = {
            "request": None,
            "response": None,
            "skipped": True,
            "skip_reason": skip_reason,
        }
        _write_json(raw_path, raw)
        return _result(
            case,
            variant,
            intent,
            secondary_name=None,
            raw_path=raw_path,
            prompt=prompt,
            usage={},
            response_text=getattr(classification, "resposta_sugerida", None) or "",
            llm_calls=0,
            status="roteado_sem_llm",
        )

    response = _call_openrouter(request_payload, api_key=api_key)
    raw = {"request": request_payload, "response": response, "skipped": False}
    _write_json(raw_path, raw)
    response_text = _response_text(response)
    primary_text, prepared_text = _split_inline_response(response_text, secondary is not None)
    status = "concluido"
    if secondary is not None and prepared_text is None:
        status = "secundaria_invalida"
    usage = response.get("usage") or {}
    result = _result(
        case,
        variant,
        intent,
        secondary_name=secondary.name if secondary else None,
        raw_path=raw_path,
        prompt=prompt,
        usage=usage,
        response_text=primary_text,
        llm_calls=1,
        status=status,
    )
    result["prepared_secondary_response"] = prepared_text
    result["model_returned"] = response.get("model")
    return result


def _call_openrouter(payload: dict, *, api_key: str) -> dict:
    request = Request(
        OPENROUTER_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-OpenRouter-Title": "G05 benchmark issue 253",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"OpenRouter recusou a requisicao ({error.code}): {detail}") from error
    except (URLError, TimeoutError) as error:
        raise RuntimeError("Nao foi possivel acessar o OpenRouter.") from error


def _public_intent(classification: object) -> AudioIntent:
    alternatives = getattr(classification, "alternativas", [])
    return AudioIntent(
        macro=classification.macrointencao,
        specific=classification.intencao or "",
        confidence_macro=classification.confianca_macro,
        confidence_specific=classification.confianca_intencao,
        flow=classification.fluxo,
        handler=classification.handler,
        alternatives=[
            IntentAlternative(intent=name, confidence=confidence)
            for name, confidence in alternatives
        ],
    )


def _skip_reason(classification: object) -> str | None:
    if not classification.roteada or classification.macrointencao == "FORA_DE_ESCOPO":
        return "limitacao_do_classificador"
    if classification.handler == "handler:transacao_gerar_relatorio":
        return "workflow_local_de_relatorio"
    return None


def _sources(payloads: list[dict]) -> list[RetrievedDocument]:
    return [
        RetrievedDocument(
            document=SharePointDocument(
                source_id=payload["id"],
                title=payload["title"],
                list_name=payload.get("list_name", "Massa controlada"),
                content=payload["content"],
                web_url=payload.get("web_url", "https://example.test/evidencia"),
                last_modified=payload.get("last_modified", "2026-09-23"),
                search_text=payload["content"],
            ),
            score=float(payload.get("score", 1.0)),
        )
        for payload in payloads
    ]


def _response_text(response: dict) -> str:
    choices = response.get("choices") or []
    if not choices:
        return ""
    content = (choices[0].get("message") or {}).get("content")
    return content.strip() if isinstance(content, str) else ""


def _split_inline_response(text: str, enabled: bool) -> tuple[str, str | None]:
    if not enabled:
        return text, None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text, None
    primary = payload.get("primary_response") if isinstance(payload, dict) else None
    prepared = payload.get("prepared_secondary_response") if isinstance(payload, dict) else None
    if not isinstance(primary, str) or not primary.strip():
        return text, None
    if not isinstance(prepared, str) or not prepared.strip():
        return primary.strip(), None
    return primary.strip(), prepared.strip()


def _result(
    case: dict,
    variant: Variant,
    intent: AudioIntent,
    *,
    secondary_name: str | None,
    raw_path: Path,
    prompt: str,
    usage: dict,
    response_text: str,
    llm_calls: int,
    status: str,
) -> dict:
    details = usage.get("completion_tokens_details") or {}
    reasoning_tokens = details.get("reasoning_tokens", usage.get("reasoning_tokens", 0))
    return {
        "case_id": case["id"],
        "variant": asdict(variant),
        "classification": intent.model_dump(),
        "secondary_intent": secondary_name,
        "llm_calls": llm_calls,
        "input_tokens": int(usage.get("prompt_tokens", 0) or 0),
        "output_tokens": int(usage.get("completion_tokens", 0) or 0),
        "reasoning_tokens": int(reasoning_tokens or 0),
        "total_tokens": int(usage.get("total_tokens", 0) or 0),
        "prompt_sha256": sha256(prompt.encode("utf-8")).hexdigest(),
        "source_count": len(case.get("sources", [])),
        "response_text": response_text,
        "has_expected_citation": (
            not case.get("sources") or "[Fonte 1]" in response_text
        ),
        "status": status,
        "raw_json": _display_path(raw_path),
    }


def _summarize(results: list[dict]) -> dict:
    variants = {}
    for variant in VARIANTS:
        selected = [item for item in results if item["variant"]["name"] == variant.name]
        variants[variant.name] = {
            "cases": len(selected),
            "llm_calls": sum(item["llm_calls"] for item in selected),
            "input_tokens": sum(item["input_tokens"] for item in selected),
            "output_tokens": sum(item["output_tokens"] for item in selected),
            "reasoning_tokens": sum(item["reasoning_tokens"] for item in selected),
            "total_tokens": sum(item["total_tokens"] for item in selected),
            "functional_successes": sum(
                item["status"] in {"concluido", "roteado_sem_llm"}
                for item in selected
            ),
        }
    baseline = variants["classificador_desligado"]["total_tokens"]
    for name, summary in variants.items():
        summary["token_reduction_vs_classifier_off"] = (
            round(1 - (summary["total_tokens"] / baseline), 6)
            if baseline
            else None
        )
    return variants


def _max_output_tokens() -> int:
    try:
        return min(max(int(os.getenv("OPENROUTER_MAX_OUTPUT_TOKENS", "256")), 64), 2048)
    except ValueError:
        return 256


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
