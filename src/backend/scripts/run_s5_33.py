"""Executa e preserva a reexecução S5-33 (CT-RF02-01 e CT-RF03-02) sem .env.

Uso (a partir de src/backend, com requirements-pln.txt instalado):
    python -m scripts.run_s5_33 --round rodada-01

Grava em ``src/backend/evidencias/rf-reexecucao-s5-33/<rodada>``: manifesto com
commit, ambiente, versões de torch/transformers e SHA-256 dos artefatos do
classificador; saída e JUnit do pytest; e o JSON de cada caso. O retorno do
pytest é preservado. Os casos se ignoram se o classificador real não carregar.
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


def _version(name):
    try:
        return version(name)
    except Exception:
        return None


def _relative(path, root):
    try:
        return str(path.resolve().relative_to(root)).replace("\\", "/")
    except ValueError:
        return path.name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--round", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", args.round):
        parser.error("Use um identificador simples de rodada, sem caminho.")
    backend = Path(__file__).resolve().parents[1]
    root = backend.parents[1]
    output = backend / "evidencias/rf-reexecucao-s5-33" / args.round
    output.mkdir(parents=True, exist_ok=False)

    files = [backend / "app/tests/test_reexecucao_s5_33.py", Path(__file__).resolve(),
             backend / "app/main.py", backend / "app/pipeline.py", backend / "app/nlp/inference.py",
             backend / "app/nlp/routing.py", backend / "app/nlp/entities.py"]
    try:
        from app.nlp.classifier import ARTIFACT_DIR
        files += sorted(path for path in Path(ARTIFACT_DIR).glob("*") if path.is_file())
    except Exception:  # o manifesto continua útil mesmo sem o artefato
        pass
    # autocrlf alinha a leitura da árvore com o checkout do Windows usado pela equipe.
    git = ["git", "-c", f"safe.directory={root.as_posix()}", "-c", "core.autocrlf=true", "-C", str(root)]
    manifest = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "user_date": datetime.now(timezone(timedelta(hours=-3))).date().isoformat(),
        "user_timezone": "America/Sao_Paulo",
        "commit": subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip(),
        "worktree": subprocess.check_output(git + ["status", "--short"], text=True),
        "python": platform.python_version(), "platform": platform.platform(),
        "packages": {name: _version(name) for name in ("pytest", "fastapi", "pydantic", "torch", "transformers", "scikit-learn")},
        "sha256": {_relative(path, root): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in files if path.exists()},
        "scope": ("POST /api/chat via TestClient com classificador, roteamento e entidades reais; geração do LLM "
                  "substituída por duplo; sem banco. Mesmas entradas da rodada de 23/09 (evidencias/rf01-rf10)."),
    }
    command = [sys.executable, "-m", "pytest", "app/tests/test_reexecucao_s5_33.py", "-v", "-s", "-rxX",
               "--tb=short", "-p", "no:cacheprovider", f"--junitxml={output / 'pytest.xml'}"]
    manifest["command"] = command
    (output / "manifesto.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    environment = dict(os.environ, PYTHON_DOTENV_DISABLED="1", PYTHONIOENCODING="utf-8",
                       PYTHONDONTWRITEBYTECODE="1", PLN_WARMUP="0", S5_33_EVIDENCE_DIR=str(output))
    with (output / "pytest.txt").open("wb") as stream:
        result = subprocess.run(command, cwd=backend, env=environment, stdout=stream, stderr=subprocess.STDOUT)
    (output / "execucao.json").write_text(json.dumps({
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "pytest_exit_code": result.returncode,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Evidências: {output}\npytest exit code: {result.returncode}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
