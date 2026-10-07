"""Executa e preserva a reavaliação do RNF08 da S5-36, sem carregar .env.

Uso (a partir de src/backend): python -m scripts.run_s5_36 --round rodada-01
O retorno do pytest é preservado; uma reprovação produz exit code 1.
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
    output = root / "src/backend/evidencias/rnf08-s5-36" / args.round
    output.mkdir(parents=True, exist_ok=False)
    files = [root / "docs/Projeto.md",
             root / "docs/diagrams/componentes-metro-5.2.puml",
             root / ".env.example", root / "src/backend/.env.example",
             root / "compose.prod.yml", root / "compose.rabbitmq.yml",
             root / "src/backend/Dockerfile", root / "src/frontend/Dockerfile",
             backend / "app/tests/test_rnf08_s5_36.py",
             backend / "app/main.py",
             Path(__file__).resolve()]
    git = ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root)]
    manifest = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "user_date": datetime.now(timezone(timedelta(hours=-3))).date().isoformat(),
        "user_timezone": "America/Sao_Paulo",
        "commit": subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip(),
        "worktree": subprocess.check_output(git + ["status", "--short"], text=True),
        "python": platform.python_version(), "platform": platform.platform(),
        "packages": {name: version(name) for name in ("pytest", "fastapi", "pydantic", "httpx")},
        "sha256": {str(path.relative_to(root)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in files if path.exists()},
        "scope": "API ASGI local, código e configuração do runtime e Seções 5.2.1 e 6.4; sem tenant, rede ou credenciais",
    }
    command = [sys.executable, "-m", "pytest", "app/tests/test_rnf08_s5_36.py",
               "-v", "-s", "--tb=short", f"--junitxml={output / 'pytest.xml'}"]
    manifest["command"] = command
    (output / "manifesto.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    environment = dict(os.environ, PYTHON_DOTENV_DISABLED="1", PYTHONIOENCODING="utf-8",
                       PLN_WARMUP="0", S5_36_EVIDENCE_DIR=str(output))
    with (output / "pytest.txt").open("wb") as stream:
        result = subprocess.run(command, cwd=backend, env=environment, stdout=stream, stderr=subprocess.STDOUT)
    (output / "execucao.json").write_text(json.dumps({
        "finished_at_utc": datetime.now(timezone.utc).isoformat(), "exit_code": result.returncode,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Evidências: {output}\npytest exit code: {result.returncode}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
