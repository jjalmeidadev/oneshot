"""Congela insumos antes da execucao e publica resultados auditaveis S4-31."""

import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parents[1]
OUTPUT = ROOT / "docs/evidencias/sprint-04/vhs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
OUTPUT.mkdir(parents=True, exist_ok=False)
COMMAND = [sys.executable, "-m", "pytest", "app/tests/test_vhs_integration.py",
           "app/tests/test_audio_upload.py", "-v", "-o", "junit_family=legacy",
           f"--junitxml={OUTPUT / 'pytest.xml'}"]
files = [*BACKEND.glob("app/audio/*.py"), BACKEND / "app/tests/test_vhs_integration.py",
         BACKEND / "app/tests/test_audio_upload.py", BACKEND / "app/tests/conftest.py",
         Path(__file__), ROOT / "docs/testes/sprint4/plano-vhs.md"]
manifest = {
    "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
    "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "working_tree": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
    "python": platform.python_version(), "platform": platform.platform(),
    "packages": {name: importlib.metadata.version(name) for name in ("pytest", "fastapi", "httpx")},
    "command": COMMAND, "cwd": "src/backend",
    "provider": "httpx.AsyncClient.post controlado; sem rede Azure",
    "mass": "WAV PCM sintetico: 16kHz, mono, 16 bits, 1s, amplitudes 8000/4000; pt-BR/en-US",
    "sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
}
(OUTPUT / "ambiente.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
run = subprocess.run(COMMAND, cwd=BACKEND, capture_output=True, text=True,
                     encoding="utf-8", errors="replace",
                     env={**os.environ, "PYTHONIOENCODING": "utf-8"})
(OUTPUT / "pytest.txt").write_text(run.stdout + run.stderr, encoding="utf-8")
results = []
if (OUTPUT / "pytest.xml").exists():
    for case in ElementTree.parse(OUTPUT / "pytest.xml").iter("testcase"):
        status = "aprovado"
        if case.find("failure") is not None or case.find("error") is not None:
            status = "falhou"
        elif case.find("skipped") is not None:
            status = "nao executado"
        results.append({"scenario": case.attrib["name"], "status": status,
                        "seconds": case.attrib.get("time"),
                        "metrics": {p.attrib["name"]: p.attrib["value"] for p in case.iter("property")}})
results.extend([
    {"scenario": "Azure real / S4-28", "status": "nao executado", "reason": "Rodada local controlada; requer ambiente publicado e audio de fala autorizado."},
    {"scenario": "Copilot / S4-22", "status": "nao executado", "reason": "Conector e autenticacao publicados nao exercitados nesta rodada."},
    {"scenario": "RNF05 e usabilidade", "status": "nao executado", "reason": "Testes funcionais locais nao medem carga nem uso humano."},
])
if run.returncode not in (0, 1):
    results.append({"scenario": "infraestrutura de teste", "status": "bloqueado", "reason": f"pytest exit={run.returncode}; consultar pytest.txt"})
(OUTPUT / "resultado.json").write_text(json.dumps({"exit_code": run.returncode, "scenarios": results}, indent=2, ensure_ascii=False), encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
print(run.stdout)
print(f"Evidencias: {OUTPUT}")
sys.exit(run.returncode)
