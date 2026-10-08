"""S5-36: reavaliação do RNF08 pelo critério revisado na S5-43 (#297).

Critério da Seção 9.2.2: contrato OpenAPI válido, cada componente do runtime
com equivalente Microsoft mapeado na Seção 6.4 e canal publicável no Teams e
acessível pelo Copilot via MCP, sem dependência do Copilot Studio.

Os componentes do backend são descobertos a partir de `src/backend/app`: um
pacote novo sem linha na Seção 6.4 reprova o caso positivo. Sem credenciais,
rede ou tenant. S5_36_EVIDENCE_DIR habilita a gravação dos artefatos. O
marcador `integration` coloca o teste no job `backend-api` da pipeline.
"""

import copy
import json
import os
from pathlib import Path
import re

import pytest
from fastapi.openapi.models import OpenAPI
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.integration

ROOT = Path(__file__).resolve().parents[4]
BACKEND_APP = ROOT / "src/backend/app"
PROJETO = ROOT / "docs/Projeto.md"
DIAGRAMA = ROOT / "docs/diagrams/componentes-metro-5.2.puml"

# Componentes do runtime que não são pacotes de `app`.
FIXED_COMPONENTS = {
    "frontend": "src/frontend",
    "api": "src/backend/app/main.py",
    "pipeline": "src/backend/app/pipeline.py",
    "implantacao": "compose.prod.yml",
}
# Configuração e empacotamento do runtime, examinados em busca do Copilot Studio.
RUNTIME_CONFIG = (
    ".env.example",
    "src/backend/.env.example",
    "compose.prod.yml",
    "compose.rabbitmq.yml",
    "src/backend/Dockerfile",
    "src/frontend/Dockerfile",
)
COPILOT_STUDIO = re.compile(r"copilot[\s_-]*studio", re.IGNORECASE)
# Dependência efetiva: variável de configuração ou endpoint do serviço, fora de comentário.
STUDIO_DEPENDENCY = (
    re.compile(r"\bCOPILOT_STUDIO_[A-Z0-9_]+"),
    re.compile(r"copilotstudio\.microsoft|directline\.botframework|api\.powerplatform\.com", re.IGNORECASE),
)
COMMENT = re.compile(r"^\s*(#|//|/?\*)")


def evidence(name, payload):
    print(json.dumps({"artifact": name, "observation": payload}, ensure_ascii=True))
    target = os.getenv("S5_36_EVIDENCE_DIR")
    if target:
        directory = Path(target)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


def contract_errors(contract):
    """Mesmo checklist estrutural da S5-31; não certifica toda a especificação."""
    errors = []
    try:
        OpenAPI.model_validate(contract)
    except ValueError:
        errors.append("estrutura OpenAPI inválida")
    for path, method in (("/health", "get"), ("/api/chat", "post"), ("/api/audio", "post")):
        operation = contract.get("paths", {}).get(path, {}).get(method)
        if not operation or "200" not in operation.get("responses", {}):
            errors.append(f"operação obrigatória ausente/incompleta: {method} {path}")
    message = (
        contract.get("components", {}).get("schemas", {})
        .get("GeminiChatRequest", {}).get("properties", {}).get("message", {})
    )
    if message.get("type") != "string":
        errors.append("GeminiChatRequest.message deve ser string")
    return errors


def live_contract():
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        response = client.get("/openapi.json")
        assert response.status_code == 200
        return response.json()


def runtime_components():
    """Pacotes de `app` (exceto testes) e os componentes fixos, com o trecho procurado."""
    components = dict(FIXED_COMPONENTS)
    for entry in sorted(BACKEND_APP.iterdir()):
        if entry.is_dir() and entry.name not in {"tests", "__pycache__"} and (entry / "__init__.py").exists():
            components[entry.name] = f"src/backend/app/{entry.name}/"
    return components


def mapping_rows(projeto_text):
    """Linhas das tabelas de-para das Seções 6.4.3 a 6.4.6: (componente, equivalente)."""
    start = projeto_text.index("### 6.4.3 ")
    end = projeto_text.index("### 6.4.7 ")
    rows = []
    for line in projeto_text[start:end].splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5 or set(cells[0]) <= {"-", ":"} or cells[0].startswith("Componente da PoC"):
            continue
        rows.append((cells[0], cells[1]))
    return rows


def unmapped_components(components, rows):
    """Componente sem linha cuja primeira coluna o cite, ou com equivalente vazio."""
    missing, mapped = [], {}
    for name, fragment in components.items():
        hits = [equivalent for component, equivalent in rows if fragment in component]
        valid = [equivalent for equivalent in hits if equivalent and equivalent not in {"—", "-"}]
        if valid:
            mapped[name] = valid[0][:160]
        else:
            missing.append(name)
    return missing, mapped


def copilot_studio_findings(files):
    """Dependências do Copilot Studio no código e na configuração do runtime: {arquivo: linhas}.

    Conta variável de configuração ou endpoint do serviço fora de comentário.
    Menções em texto, como "independente de Copilot Studio", ficam em `copilot_studio_mentions`.
    """
    findings = {}
    for relative, text in files.items():
        lines = [
            number for number, line in enumerate(text.splitlines(), 1)
            if not COMMENT.match(line) and any(pattern.search(line) for pattern in STUDIO_DEPENDENCY)
        ]
        if lines:
            findings[relative] = lines
    return findings


def copilot_studio_mentions(files):
    """Menções textuais, registradas na evidência para leitura humana; não reprovam."""
    mentions = {}
    for relative, text in files.items():
        lines = [line.strip()[:160] for line in text.splitlines() if COPILOT_STUDIO.search(line)]
        if lines:
            mentions[relative] = lines
    return mentions


def runtime_files():
    files = {}
    sources = list((ROOT / "src/backend/app").rglob("*.py")) + list((ROOT / "src/frontend/src").rglob("*.ts*"))
    for path in sources:
        relative = path.relative_to(ROOT).as_posix()
        if "/tests/" in relative or ".test." in relative or "__pycache__" in relative:
            continue
        files[relative] = path.read_text(encoding="utf-8", errors="replace")
    for relative in RUNTIME_CONFIG:
        path = ROOT / relative
        if path.exists():
            files[relative] = path.read_text(encoding="utf-8", errors="replace")
    return files


def diagram_findings(puml_text):
    """Elementos da Figura 22 que citam o Copilot Studio fora da legenda."""
    findings, in_legend = [], False
    for number, line in enumerate(puml_text.splitlines(), 1):
        stripped = line.strip().lower()
        if stripped.startswith("legend"):
            in_legend = True
        elif stripped.startswith("endlegend"):
            in_legend = False
        elif not in_legend and COPILOT_STUDIO.search(line) and not stripped.startswith("'"):
            findings.append(number)
    return findings


def planned_channels(projeto_text):
    """Linhas da tabela 5.2.1 para os canais previstos: Teams e Copilot via MCP."""
    section = projeto_text[projeto_text.index("### 5.2.1 "):projeto_text.index("### 5.2.2 ")]
    teams = [line for line in section.splitlines() if "Teams" in line and "Previsto" in line]
    mcp = [line for line in section.splitlines() if "MCP" in line and "Previsto" in line]
    return {"teams": bool(teams), "copilot_mcp": bool(mcp)}


def test_ct_rnf08_p():
    contract = live_contract()
    errors = contract_errors(contract)
    projeto = PROJETO.read_text(encoding="utf-8")
    missing, mapped = unmapped_components(runtime_components(), mapping_rows(projeto))
    files = runtime_files()
    studio = copilot_studio_findings(files)
    diagram = diagram_findings(DIAGRAMA.read_text(encoding="utf-8"))
    channels = planned_channels(projeto)
    evidence("CT-RNF08-P.json", {
        "health_http": 200, "openapi_http": 200, "contract_errors": errors,
        "runtime_components": sorted(runtime_components()),
        "mapped": mapped, "unmapped": missing,
        "copilot_studio_in_runtime": studio,
        "copilot_studio_mentions": copilot_studio_mentions(files),
        "copilot_studio_in_figure_22_outside_legend": diagram,
        "planned_channels": channels,
        "criterion": "Seção 9.2.2, revisada na S5-43 (#297)",
        "scope": "ASGI local com lifespan; mapeamento documental; sem homologação no tenant Microsoft",
    })
    assert not errors, errors
    assert not missing, f"componentes do runtime sem equivalente na Seção 6.4: {missing}"
    assert not studio, f"dependência do Copilot Studio no runtime: {studio}"
    assert not diagram, f"Copilot Studio como componente na Figura 22: linhas {diagram}"
    assert all(channels.values()), channels


def test_ct_rnf08_n():
    original = live_contract()
    projeto = PROJETO.read_text(encoding="utf-8")
    components = runtime_components()
    rows = mapping_rows(projeto)
    assert not contract_errors(original)
    assert not unmapped_components(components, rows)[0]

    # 1. Contrato sem operação obrigatória e com tipo incompatível, em cópias.
    missing_operation = copy.deepcopy(original)
    del missing_operation["paths"]["/api/chat"]["post"]
    incompatible = copy.deepcopy(original)
    incompatible["components"]["schemas"]["GeminiChatRequest"]["properties"]["message"]["type"] = "integer"

    # 2. De-para sem as linhas dos alertas e com equivalente vazio para o PLN.
    without_alerts = [row for row in rows if "src/backend/app/alerts/" not in row[0]]
    blank_nlp = [(c, "—" if "src/backend/app/nlp/" in c else e) for c, e in rows]

    # 3. Configuração do runtime com dependência do Copilot Studio.
    files = runtime_files()
    tampered = dict(files)
    tampered[".env.example"] = files.get(".env.example", "") + "\nCOPILOT_STUDIO_ENDPOINT=https://exemplo\n"

    # 4. Figura 22 com o Copilot Studio como componente.
    puml = DIAGRAMA.read_text(encoding="utf-8")
    tampered_puml = puml.replace("@enduml", 'component "Copilot Studio" as CS\n@enduml')

    observed = {
        "missing_operation": contract_errors(missing_operation),
        "incompatible_type": contract_errors(incompatible),
        "without_alerts_rows": unmapped_components(components, without_alerts)[0],
        "blank_nlp_equivalent": unmapped_components(components, blank_nlp)[0],
        "copilot_studio_env": copilot_studio_findings(tampered),
        "copilot_studio_component": diagram_findings(tampered_puml),
    }
    evidence("CT-RNF08-N.json", observed)
    assert observed["missing_operation"] and observed["incompatible_type"]
    assert observed["without_alerts_rows"] == ["alerts"]
    assert observed["blank_nlp_equivalent"] == ["nlp"]
    assert ".env.example" in observed["copilot_studio_env"]
    assert observed["copilot_studio_component"]
    # As fontes reais não mudaram.
    assert live_contract() == original
    assert PROJETO.read_text(encoding="utf-8") == projeto
