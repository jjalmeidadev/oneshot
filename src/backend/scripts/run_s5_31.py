"""Executa e preserva uma rodada local S5-31 sem carregar .env.

Uso (a partir de src/backend): python -m scripts.run_s5_31 --round rodada-02
O retorno do pytest é preservado; defeitos observados produzem exit code 1.
"""

import argparse
from datetime import datetime, timezone, timedelta
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
    output = root / "docs/evidencias/sprint-05/rnf07-rnf09" / args.round
    output.mkdir(parents=True, exist_ok=False)
    files = [root / "docs/testes/sprint5/amostra-rnf07.csv",
             root / "docs/testes/sprint5/protocolo-rnf07.md",
             root / "docs/evidencias/sprint-05/rnf07-rnf09/coleta-rnf07-p01.csv",
             root / "docs/evidencias/sprint-05/rnf07-rnf09/transcricao-rnf07-p01.md",
             root / "src/agent/README.md", root / "docs/Projeto.md",
             backend / "app/tests/test_rnf07_rnf09_s5_31.py",
             backend / "app/rag/sharepoint.py", backend / "app/rag/database.py",
             backend / "app/rag/errors.py", backend / "app/gemini/client.py",
             Path(__file__).resolve()]
    files += sorted((backend / "app/rag/data/sharepoint").glob("*.json"))
    files += sorted((root / "docs/evidencias/sprint-05/rnf07-rnf09/imagens").glob("*"))
    git = ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root)]
    manifest = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "user_date": datetime.now(timezone(timedelta(hours=-3))).date().isoformat(),
        "user_timezone": "America/Fortaleza",
        "commit": subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip(),
        "worktree": subprocess.check_output(git + ["status", "--short"], text=True),
        "python": platform.python_version(), "platform": platform.platform(),
        "packages": {name: version(name) for name in ("pytest", "fastapi", "pydantic", "httpx")},
        "sha256": {str(path.relative_to(root)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
        "scope": "API ASGI e RAG locais; RNF07 apura transcrições da sessão humana anterior, sem reaplicação ou novas chamadas ao LLM",
    }
    command = [sys.executable, "-m", "pytest", "app/tests/test_rnf07_rnf09_s5_31.py",
               "-v", "-s", "--tb=short", f"--junitxml={output / 'pytest.xml'}"]
    manifest["command"] = command
    (output / "manifesto.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    environment = dict(os.environ, PYTHON_DOTENV_DISABLED="1", PYTHONIOENCODING="utf-8",
                       PLN_WARMUP="0", S5_31_EVIDENCE_DIR=str(output))
    with (output / "pytest.txt").open("wb") as stream:
        result = subprocess.run(command, cwd=backend, env=environment, stdout=stream, stderr=subprocess.STDOUT)
    (output / "execucao.json").write_text(json.dumps({
        "finished_at_utc": datetime.now(timezone.utc).isoformat(), "exit_code": result.returncode,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Evidências: {output}\npytest exit code: {result.returncode}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
