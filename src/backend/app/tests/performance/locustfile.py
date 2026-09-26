"""Cenario Locust do teste obrigatorio de desempenho do RNF05.

Arquivo exigido nominalmente pela Secao 9.2.4 do `Projeto.md`. O relogio medido
e o do proprio Locust: comeca no envio do `POST /api/chat` e termina quando a
resposta JSON chega. Renderizacao de frontend, digitacao, STT e TTS ficam fora,
como o requisito determina.

Duas rodadas positivas, a partir de `src/backend`:

    locust -f app/tests/performance/locustfile.py --host http://127.0.0.1:8000 \
        --headless -u 1 -r 1 -t 5m --csv evidencias/rnf05-baseline
    locust -f app/tests/performance/locustfile.py --host http://127.0.0.1:8000 \
        --headless -u 5 -r 1 -t 5m --csv evidencias/rnf05-carga

O nome de cada requisicao separa `[simples]` de `[comparacao]` no CSV, que e o
que permite apurar os dois P95 exigidos sem misturar as populacoes.

Aquecimento NAO acontece aqui. Ele roda antes, em `aquecer.py`, porque o relogio
do `-t` do Locust corre durante o `test_start`: com o aquecimento dentro deste
arquivo, as rodadas "de 5 minutos" mediam ~3 min 40 s e a rodada negativa nao
chegava a medir nada. Esta janela mede apenas carga.

Aprovacao (Secao 9.2.4): zero erro HTTP ou de contrato, P95 simples <= 10 s e
P95 comparativo <= 20 s, nas duas rodadas. Media, mediana, P90, P99 e RPS sao
registrados para diagnostico e nao substituem o P95.
"""

import os
import random

from locust import HttpUser, between, task

from app.tests.performance.prompts import COMPARACOES, CONSULTAS_SIMPLES

#: Campos que a Secao 8.11 fixa no contrato de `/api/chat`. A ausencia de
#: qualquer um deles e erro de contrato e reprova a rodada, mesmo com HTTP 200.
CAMPOS_OBRIGATORIOS = ("text", "model", "latency_ms", "usage", "pipeline_metrics")

#: Tempo maximo de espera do cliente. Fica acima do teto comparativo de 20 s
#: para que uma violacao apareca como latencia medida, e nao como timeout do
#: proprio Locust — o que esconderia o valor real no CSV.
TIMEOUT_SEGUNDOS = 60

#: Envia somente pedidos de comparacao, ignorando a proporcao de 75/25.
#:
#: Existe por causa do `CT-RNF05-N`. O duplo de `api_com_atraso.py` retarda
#: apenas a rota de comparacao, que a mistura normal sorteia em 1 de cada 4
#: tarefas. Na rodada negativa de 22/09/2026 saíram 7 requisicoes e **nenhuma**
#: caiu na comparacao: o atraso injetado nunca foi exercido e o cenario negativo
#: nao validou nada. Um cenario negativo nao pode depender de sorteio — se a
#: violacao so acontece quando o dado colabora, o teste nao prova que a medicao
#: enxerga violacoes.
SOMENTE_COMPARACAO = os.getenv("RNF05_SO_COMPARACAO") == "1"


def _valida_contrato(resposta) -> str | None:
    """Devolve a descricao do erro de contrato, ou None quando a resposta e valida."""

    if resposta.status_code != 200:
        return f"HTTP {resposta.status_code}"
    try:
        corpo = resposta.json()
    except ValueError:
        return "corpo nao e JSON"
    ausentes = [campo for campo in CAMPOS_OBRIGATORIOS if campo not in corpo]
    if ausentes:
        return "campos ausentes no contrato: " + ", ".join(ausentes)
    if not isinstance(corpo.get("text"), str) or not corpo["text"].strip():
        return "campo 'text' vazio"
    return None


class UsuarioDoPortfolio(HttpUser):
    """Usuario sintetico que alterna consultas simples e pedidos de comparacao.

    A espera de 1 a 3 segundos entre tarefas e a prevista na Secao 9.2.4 e
    aproxima o ritmo de uma conversa real, evitando que a medicao vire um teste
    de saturacao.
    """

    wait_time = between(1, 3)

    def _envia(self, mensagem: str, rotulo: str) -> None:
        with self.client.post(
            "/api/chat",
            json={"message": mensagem, "use_intent_classifier": True},
            name=f"POST /api/chat [{rotulo}]",
            timeout=TIMEOUT_SEGUNDOS,
            catch_response=True,
        ) as resposta:
            erro = _valida_contrato(resposta)
            if erro is None:
                resposta.success()
            else:
                resposta.failure(erro)

    @task(3)
    def consulta_simples(self) -> None:
        """75% da carga: perguntas respondiveis pela massa sintetica.

        Desligada em `RNF05_SO_COMPARACAO=1`, quando a rodada precisa exercer
        deterministicamente a rota de comparacao.
        """

        if SOMENTE_COMPARACAO:
            self._envia(random.choice(COMPARACOES), "comparacao")
            return
        self._envia(random.choice(CONSULTAS_SIMPLES), "simples")

    @task(1)
    def comparacao_entre_projetos(self) -> None:
        """25% da carga. Ver a ressalva de `prompts.py`: a massa tem um projeto."""

        self._envia(random.choice(COMPARACOES), "comparacao")
