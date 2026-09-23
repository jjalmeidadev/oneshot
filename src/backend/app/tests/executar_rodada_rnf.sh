#!/usr/bin/env bash
#
# Campanha completa de RNF04 e RNF05.
#
# A API precisa estar no ar ANTES deste script, em outro terminal, a partir de
# `src/backend`. O provedor e escolhido no comando que sobe a API, nao aqui:
#
#   # bancada (Gemini direto no Free Tier, configuracao do .env):
#   .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
#
#   # quando a quota do Free Tier do Gemini nao comporta a campanha:
#   LLM_PROVIDER=openrouter .venv/bin/python -m uvicorn app.main:app \
#       --host 127.0.0.1 --port 8000
#
# E a instancia com atraso injetado, para o cenario negativo do RNF05:
#
#   LLM_PROVIDER=openrouter .venv/bin/python -m uvicorn \
#       app.tests.performance.api_com_atraso:app --host 127.0.0.1 --port 8001
#
# Depois, a partir de `src/backend`:
#
#   LLM_PROVIDER=openrouter bash app/tests/executar_rodada_rnf.sh
#
# O LLM_PROVIDER passado a este script serve apenas para a ficha de ambiente
# registrar o provedor certo. Variaveis exportadas aqui NAO alcancam a API, que
# roda em outro processo — uma versao anterior deste script exportava
# GEMINI_MAX_RETRIES=0 e, com isso, gravava na ficha uma configuracao que a API
# nunca usou.

set -euo pipefail

PYTHON="${PYTHON:-.venv/bin/python}"
LOCUST="${LOCUST:-.venv/bin/locust}"
HOST="${HOST:-http://127.0.0.1:8000}"
HOST_VIOLACAO="${HOST_VIOLACAO:-http://127.0.0.1:8001}"
COMMIT="$(git rev-parse --short HEAD)"
DESTINO="evidencias/campanha-${COMMIT}-$(date +%Y%m%d-%H%M)"
export PYTHONPATH=.

echo "commit ....... ${COMMIT}"
echo "destino ...... ${DESTINO}"
echo "provedor ..... ${LLM_PROVIDER:-gemini}"
echo

if [ -n "$(git status --porcelain)" ]; then
    echo "AVISO: a arvore de trabalho tem alteracoes nao commitadas."
    echo "O commit ${COMMIT} nao descreve exatamente o codigo que sera medido."
    read -r -p "Continuar mesmo assim? [s/N] " resposta
    [ "${resposta}" = "s" ] || exit 1
fi

for alvo in "${HOST}" "${HOST_VIOLACAO}"; do
    curl -fsS "${alvo}/health" > /dev/null || {
        echo "ERRO: ${alvo}/health nao respondeu. Suba as duas instancias antes."
        exit 1
    }
done

mkdir -p "${DESTINO}"/{rnf04,baseline,carga,violacao}

echo "==> 1/6  RNF04 — 24 perguntas da amostra congelada"
${PYTHON} -m app.tests.rnf04.executar_rnf04 \
    --host "${HOST}" --saida "${DESTINO}/rnf04" --tentativas-transitorias 3

echo
echo "==> 2/6  RNF05 — aquecimento, FORA da janela de medicao"
# O relogio do -t do Locust corre durante o test_start. Aquecer dentro do
# locustfile fazia as rodadas "de 5 minutos" medirem ~3 min 40 s.
${PYTHON} -m app.tests.performance.aquecer --host "${HOST}"

echo
echo "==> 3/6  RNF05 — linha de base, 1 usuario, 25 minutos"
# 25 minutos, e nao 5: com um usuario e 25% de comparacoes, 5 minutos
# rendem cerca de 10 amostras comparativas, e o P95 do Locust vira a pior
# requisicao. O protocolo revisado exige 40 amostras por tipo de consulta.
${PYTHON} -m app.tests.performance.registrar_ambiente \
    --rodada baseline --cache quente --host "${HOST}" \
    --saida "${DESTINO}/baseline" > /dev/null
${LOCUST} -f app/tests/performance/locustfile.py --host "${HOST}" \
    --headless -u 1 -r 1 -t 25m --csv "${DESTINO}/baseline/rnf05-baseline" || true

echo
echo "==> 4/6  RNF05 — carga, 5 usuarios, 8 minutos"
${PYTHON} -m app.tests.performance.registrar_ambiente \
    --rodada carga --cache quente --host "${HOST}" \
    --saida "${DESTINO}/carga" > /dev/null
${LOCUST} -f app/tests/performance/locustfile.py --host "${HOST}" \
    --headless -u 5 -r 1 -t 8m --csv "${DESTINO}/carga/rnf05-carga" || true

echo
echo "==> 5/6  RNF05 — cenario negativo, so comparacao, 5 usuarios, 6 minutos"
# Sem aquecimento: aquecer a instancia com atraso de 25 s consome a janela.
# RNF05_SO_COMPARACAO=1 garante que o atraso seja exercido; com a mistura
# normal de 75/25, uma rodada curta pode nao sortear nenhuma comparacao.
# Cinco usuarios por 6 minutos: cada requisicao leva ~30 s com o atraso, e so
# assim a rodada reune as 40 amostras que o protocolo exige.
${PYTHON} -m app.tests.performance.registrar_ambiente \
    --rodada violacao --cache quente --host "${HOST_VIOLACAO}" \
    --saida "${DESTINO}/violacao" > /dev/null
RNF05_SO_COMPARACAO=1 ${LOCUST} -f app/tests/performance/locustfile.py \
    --host "${HOST_VIOLACAO}" --headless -u 5 -r 1 -t 6m \
    --csv "${DESTINO}/violacao/rnf05-violacao" || true

echo
echo "==> apuracao do RNF05 pelo protocolo revisado"
${PYTHON} -m app.tests.performance.apurar_rnf05 \
    "${DESTINO}/baseline/rnf05-baseline_stats.csv" \
    "${DESTINO}/carga/rnf05-carga_stats.csv" || true

echo
echo "==> 6/6  concluido — ${DESTINO}/"
echo
echo "Falta, e nao e automatico: rotular ${DESTINO}/rnf04/planilha_cega.csv"
echo "(fundamentada | alucinacao | nao_fundamentada, com justificativa) e apurar:"
echo "  ${PYTHON} -m app.tests.rnf04.avaliar_rnf04 --evidencias ${DESTINO}/rnf04"
echo
echo "A rodada de violacao PRECISA reprovar. Se passar, a medicao nao enxerga"
echo "violacao e as rodadas positivas tambem nao valem."
