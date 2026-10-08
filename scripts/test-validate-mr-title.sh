#!/bin/sh

set -eu

validator="$(dirname "$0")/validate-mr-title.sh"

expect_valid() {
  title="$1"
  if ! sh "$validator" "$title" >/dev/null 2>&1; then
    echo "Esperava título válido: $title" >&2
    exit 1
  fi
}

expect_invalid() {
  title="$1"
  if sh "$validator" "$title" >/dev/null 2>&1; then
    echo "Esperava título inválido: $title" >&2
    exit 1
  fi
}

expect_valid 'feat(api): integrar classificador de intenções (#126)'
expect_valid 'docs: atualizar gestão da configuração (#144)'
expect_valid 'fix!: corrigir falha crítica no deploy (#256, #257)'
expect_valid 'refactor(core)!: reorganizar fluxo interno (#1, #2, #3)'

expect_invalid 'resolve merge'
expect_invalid 'feat/implementar-frontend'
expect_invalid 'Docs: atualizar modelagem (#144)'
expect_invalid 'feat: ajustar pipeline'
expect_invalid 'feat: ajustar pipeline (#1 #2)'
expect_invalid 'feat(escopo inválido): ajustar pipeline (#256)'

echo "Casos de validação de título executados com sucesso."
