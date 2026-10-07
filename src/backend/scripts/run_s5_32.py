"""Executa e preserva uma rodada S5-32 (RNF10 a RNF12) sem carregar .env.

Uso (a partir de src/backend): python -m scripts.run_s5_32 --round rodada-01

Grava em ``src/backend/evidencias/rnf10-rnf12/<rodada>``: manifesto com commit,
ambiente e SHA-256 dos arquivos usados; saída e JUnit do pytest; o JSON de cada
caso; e o relatório do validador da massa. O retorno do pytest é preservado.
"""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--round", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", args.round):
        parser.error("Use um identificador simples de rodada, sem caminho.")
    backend = Path(__file__).resolve().parents[1]
    root = backend.parents[1]
    output = backend / "evidencias/rnf10-rnf12" / args.round
    output.mkdir(parents=True, exist_ok=False)

    files = [backend / "app/tests/test_rnf10_rnf12_s5_32.py",
             backend / "scripts/validar_massa_sintetica.py", Path(__file__).resolve(),
             backend / "README.md", backend / "app/main.py", backend / "app/pipeline.py",
             backend / "app/gemini/client.py", root / "docs/Projeto.md"]
    files += sorted((root / "src/database/sql").glob("0[24]_*.sql"))
    files += [root / "src/database/sql/13_seed_portfolio_report_data.sql"]
    files += sorted((backend / "app/rag/data/sharepoint").glob("*.json"))
    # autocrlf alinha a leitura da árvore com o checkout do Windows usado pela equipe.
    git = ["git", "-c", f"safe.directory={root.as_posix()}", "-c", "core.autocrlf=true", "-C", str(root)]
    manifest = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "user_date": datetime.now(timezone(timedelta(hours=-3))).date().isoformat(),
        "user_timezone": "America/Sao_Paulo",
        "commit": subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip(),
        "worktree": subprocess.check_output(git + ["status", "--short"], text=True),
        "python": platform.python_version(), "platform": platform.platform(),
        "packages": {name: version(name) for name in ("pytest", "fastapi", "pydantic", "httpx", "starlette")},
        "sha256": {str(path.relative_to(root)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in files if path.exists()},
        "scope": ("API ASGI local via TestClient, com duplos na fronteira do provedor e da fonte; análise estática "
                  "de imports; validador da massa sobre SQL de carga e listas simuladas. Sem banco, rede ou LLM."),
    }
    command = [sys.executable, "-m", "pytest", "app/tests/test_rnf10_rnf12_s5_32.py", "-v", "-s", "-rxX",
               "--tb=short", "-p", "no:cacheprovider", f"--junitxml={output / 'pytest.xml'}"]
    manifest["command"] = command
    (output / "manifesto.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    environment = dict(os.environ, PYTHON_DOTENV_DISABLED="1", PYTHONIOENCODING="utf-8",
                       PYTHONDONTWRITEBYTECODE="1", PLN_WARMUP="0", S5_32_EVIDENCE_DIR=str(output))
    with (output / "pytest.txt").open("wb") as stream:
        result = subprocess.run(command, cwd=backend, env=environment, stdout=stream, stderr=subprocess.STDOUT)
    validator = subprocess.run(
        [sys.executable, "-m", "scripts.validar_massa_sintetica", "--saida", str(output / "validador-massa.json")],
        cwd=backend, env=environment, capture_output=True, text=True,
    )
    (output / "execucao.json").write_text(json.dumps({
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "pytest_exit_code": result.returncode, "validador_exit_code": validator.returncode,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Evidências: {output}\npytest exit code: {result.returncode}\nvalidador exit code: {validator.returncode}")
    return result.returncode or validator.returncode


if __name__ == "__main__":
    raise SystemExit(main())
