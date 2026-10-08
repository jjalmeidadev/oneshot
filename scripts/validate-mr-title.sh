#!/bin/sh

set -eu

title="${1:-${CI_MERGE_REQUEST_TITLE:-}}"
pattern='^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\([A-Za-z0-9._-]+\))?!?: .+ \(#[0-9]+(, #[0-9]+)*\)$'

if [ -z "$title" ]; then
  echo "Erro: CI_MERGE_REQUEST_TITLE não foi informado." >&2
  exit 2
fi

if printf '%s\n' "$title" | grep -Eq "$pattern"; then
  echo "Título de merge request válido: $title"
  exit 0
fi

printf 'Título de merge request recebido: <%s>\n' "$title" >&2
cat >&2 <<'EOF'
Título de merge request inválido.

Formato esperado:
  <tipo>(<escopo opcional>)!?: <descrição> (#<issue>)

Para mais de uma issue, separe as referências por vírgula:
  <tipo>: <descrição> (#123, #456)

Tipos aceitos:
  feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert

Exemplo:
  feat(api): integrar classificador de intenções (#126)
EOF

exit 1
