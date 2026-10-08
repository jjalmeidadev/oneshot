#!/bin/sh
# Mesma regex da Secao 5.3.3; verifica o indice, inclusive em stage parcial.
if git grep --cached -n -I -E '^(<<<<<<< .+|=======[[:space:]]*|>>>>>>> .+)$' --; then
  echo "gate: marcadores de conflito encontrados no indice." >&2
  exit 1
else
  status=$?
  if [ "$status" -ne 1 ]; then
    echo "gate: nao foi possivel verificar o indice (git grep: $status)." >&2
    exit "$status"
  fi
fi
echo "gate: nenhum marcador de conflito no indice."
