#!/bin/sh

set -eu

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

git config core.hooksPath .githooks

if command -v chmod >/dev/null 2>&1; then
  chmod +x .githooks/commit-msg .githooks/pre-commit .githooks/pre-push
fi

echo "Hooks Git instalados com sucesso."
echo "core.hooksPath configurado para .githooks"
echo "Repositorio: $repo_root"
