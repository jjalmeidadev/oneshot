"""S5-31: critérios da Seção 9.2.3, sem credenciais ou serviços externos.

RNF07 requer aplicação humana. Falhas dos critérios permanecem falhas reais.
S5_31_EVIDENCE_DIR habilita a gravação dos artefatos da rodada.
"""

import copy
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil

from fastapi.openapi.models import OpenAPI
from fastapi.testclient import TestClient

from app.main import app
from app.rag.database import retrieve_context
from app.rag.sharepoint import DEFAULT_DATA_DIR, build_rag_input, load_sharepoint_documents

ROOT = Path(__file__).resolve().parents[4]
QUERY = "Como devo registrar um objeto perdido?"


def evidence(name, payload):
    observation = payload
    if name.startswith("openapi-"):
        observation = {"sha256": hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()}
    print(json.dumps({"artifact": name, "observation": observation}, ensure_ascii=True))
    target = os.getenv("S5_31_EVIDENCE_DIR")
    if target:
        directory = Path(target)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


def contract_errors(contract):
    """Checklist estrutural e de integração; não certifica toda a especificação."""
    errors = []
    try:
        OpenAPI.model_validate(contract)
    except ValueError:
        errors.append("estrutura OpenAPI inválida")
    for path, method in (("/health", "get"), ("/api/chat", "post"), ("/api/audio", "post")):
        operation = contract.get("paths", {}).get(path, {}).get(method)
        if not operation or "200" not in operation.get("responses", {}):
            errors.append(f"operação obrigatória ausente/incompleta: {method} {path}")
    message = contract.get("components", {}).get("schemas", {}).get("GeminiChatRequest", {}).get("properties", {}).get("message", {})
    if message.get("type") != "string":
        errors.append("GeminiChatRequest.message deve ser string")
    return errors


def live_contract():
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        response = client.get("/openapi.json")
        assert response.status_code == 200
        return response.json()


def check_rnf07(case):
    """Apura transcrições recebidas; não simula nem reaplica a sessão humana."""
    sample_path = ROOT / "docs/testes/sprint5/amostra-rnf07.csv"
    collection_path = ROOT / "docs/evidencias/sprint-05/rnf07-rnf09/coleta-rnf07-p01.csv"
    with sample_path.open(encoding="utf-8", newline="") as stream:
        sample = {row["id"]: row for row in csv.DictReader(stream)}
    with collection_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == len(sample) == 20
    assert len({row["id"] for row in rows}) == 20
    assert {row["id"] for row in rows} == set(sample)
    images_dir = collection_path.parent / "imagens"
    images = json.loads((images_dir / "manifesto-imagens.json").read_text(encoding="utf-8"))
    assert len(images) == 17
    assert {phrase for entry in images for phrase in entry["frases"]} == set(sample)
    for entry in images:
        assert hashlib.sha256((images_dir / entry["arquivo"]).read_bytes()).hexdigest() == entry["sha256"]
    for row in rows:
        assert row["pergunta_observada"] == sample[row["id"]]["frase"]
        assert row["caso"] == sample[row["id"]]["caso"]
        assert row["resposta_observada"] and row["evidencia"]
        assert row["avaliacao_tecnica_preliminar"] in {"compreendida", "orientacao_util", "falhou"}
    accepted = {"compreendida", "orientacao_util"}
    total_success = sum(row["avaliacao_tecnica_preliminar"] in accepted for row in rows)
    subset = [row for row in rows if row["caso"] == case]
    assert len(subset) == 10
    evidence(f"{case}.json", {
        "scope": "apuração técnica das transcrições visuais da sessão P01; revisão independente pendente",
        "collection": str(collection_path.relative_to(ROOT)),
        "ids": [row["id"] for row in subset],
        "subset_success": sum(row["avaliacao_tecnica_preliminar"] in accepted for row in subset),
        "subset_total": len(subset), "total_success": total_success,
        "total": len(rows), "percentage": 100 * total_success / len(rows),
        "required_success": 16, "protocol_confirmation": "pendente",
        "participant_ratings": "pendentes", "original_image_files": "17 arquivos incorporados; hashes verificados",
    })
    # A meta publicada é conjunta, não um novo limiar para cada subgrupo.
    assert total_success >= 16, f"RNF07: {total_success}/20 abaixo de 16/20; avaliação técnica preliminar"


def test_ct_rnf07_p():
    check_rnf07("CT-RNF07-P")


def test_ct_rnf07_n():
    check_rnf07("CT-RNF07-N")


def test_ct_rnf08_p():
    contract = live_contract()
    errors = contract_errors(contract)
    evidence("openapi-real.json", contract)
    agent_readme = (ROOT / "src/agent/README.md").read_text(encoding="utf-8")
    removed = "O Copilot Studio foi removido da arquitetura de execucao" in agent_readme
    evidence("CT-RNF08-P.json", {
        "health_http": 200, "openapi_http": 200, "contract_errors": errors,
        "architecture_reference": "src/agent/README.md",
        "copilot_removed_from_runtime": removed,
        "criterion": "Seção 9.2.3 exige Teams/Copilot/SharePoint/Azure previstos",
        "scope": "ASGI local com lifespan; sem homologação no tenant Microsoft",
    })
    assert not errors, errors
    assert not removed, "DEF-S5-31-01: arquitetura vigente remove Copilot exigido pelo critério ainda publicado"


def test_ct_rnf08_n():
    original = live_contract()
    assert not contract_errors(original)
    missing = copy.deepcopy(original)
    del missing["paths"]["/api/chat"]["post"]
    incompatible = copy.deepcopy(original)
    incompatible["components"]["schemas"]["GeminiChatRequest"]["properties"]["message"]["type"] = "integer"
    missing_errors, type_errors = contract_errors(missing), contract_errors(incompatible)
    evidence("openapi-sem-chat.json", missing)
    evidence("openapi-tipo-incompativel.json", incompatible)
    evidence("CT-RNF08-N.json", {"missing_operation": missing_errors, "incompatible_type": type_errors})
    assert missing_errors and type_errors
    assert live_contract() == original, "Contrato real deve permanecer intacto"


def test_ct_rnf09_p(monkeypatch, tmp_path):
    baseline = retrieve_context(QUERY)
    assert baseline
    alternate = tmp_path / "origem-alternativa"
    shutil.copytree(DEFAULT_DATA_DIR, alternate)
    # Marca exclusiva comprova que a configuração foi consumida pelo núcleo.
    source = alternate / "procedimentos_operacionais.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["list"]["id"] = "s5-31-alternativa"
    source.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setenv("SHAREPOINT_MOCK_DATA_DIR", str(alternate))
    results = retrieve_context(QUERY)
    prompt = build_rag_input(QUERY, results)
    evidence("CT-RNF09-P.json", {
        "query": QUERY, "configuration": "SHAREPOINT_MOCK_DATA_DIR",
        "baseline_ids": [r.document.source_id for r in baseline],
        "alternate_ids": [r.document.source_id for r in results],
        "baseline_contents": [r.document.content for r in baseline],
        "alternate_contents": [r.document.content for r in results],
        "prompt": prompt, "scope": "núcleo RAG local, sem classificador, LLM, contêiner ou publicação",
    })
    assert results and results[0].document.source_id == "s5-31-alternativa:101"
    assert [r.document.content for r in results] == [r.document.content for r in baseline]
    assert results[0].document.content in prompt


def test_ct_rnf09_n(monkeypatch, tmp_path):
    malformed = tmp_path / "formato-invalido"
    malformed.mkdir()
    (malformed / "origem.json").write_text("{invalid", encoding="utf-8")
    wrong_shape = tmp_path / "estrutura-invalida"
    wrong_shape.mkdir()
    (wrong_shape / "origem.json").write_text("[]", encoding="utf-8")
    observations = {}
    for name, path in (("diretorio_ausente", tmp_path / "ausente"),
                       ("arquivo_ausente", tmp_path / "ausente.json"),
                       ("json_malformado", malformed), ("estrutura_invalida", wrong_shape)):
        monkeypatch.setenv("SHAREPOINT_MOCK_DATA_DIR", str(path))
        stages = {}
        for stage, operation in (("carregamento", load_sharepoint_documents),
                                 ("consulta", lambda: retrieve_context(QUERY))):
            try:
                result = operation()
                stages[stage] = {"returned_count": len(result), "exception": None}
            except Exception as exc:
                stages[stage] = {"exception": type(exc).__name__, "message": str(exc)}
        observations[name] = stages
    evidence("CT-RNF09-N.json", observations)
    expected = {
        "diretorio_ausente": {"RagSourceError"},
        "arquivo_ausente": {"RagSourceError"},
        "json_malformado": {"RagSourceError"},
        "estrutura_invalida": {"RagSourceError"},
    }
    assert all(stage["exception"] in expected[name] for name, stages in observations.items() for stage in stages.values()), (
        "Origem inválida deve produzir erro de domínio localizado", observations
    )
