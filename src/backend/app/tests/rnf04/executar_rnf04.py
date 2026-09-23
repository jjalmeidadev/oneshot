"""Coleta das respostas da amostra congelada do RNF04 (CT-RNF04-P e CT-RNF04-N).

O script nao julga nada: ele apenas envia cada pergunta da amostra para
`POST /api/chat`, grava a resposta integral com as fontes retornadas e produz a
planilha cega exigida pela Secao 9.2.2 do `Projeto.md`. A rotulagem e a apuracao
ficam em `avaliar_rnf04.py`, e a separacao existe para que quem rotula nao veja,
no momento da rotulagem, se a pergunta pertencia ao cenario positivo ou negativo.

Uso, a partir de `src/backend`, com a API ja respondendo em /health:

    .venv/bin/python -m app.tests.rnf04.executar_rnf04 \
        --host http://127.0.0.1:8000 \
        --saida evidencias/rnf04-<commit>

Saidas geradas no diretorio indicado:

  respostas.jsonl    registro integral por pergunta, com fontes e metricas
  planilha_cega.csv  id, pergunta, resposta e fontes, sem o cenario nem o fato
                     esperado — e o arquivo que vai para quem rotula
  ambiente.json      o que estava valendo no momento da coleta
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter, sleep

import httpx

AMOSTRA = Path(__file__).with_name("amostra_congelada.json")
TIMEOUT_SEGUNDOS = 120


def _commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:
        return "desconhecido"


def _ambiente(host: str) -> dict:
    """Registra a configuracao da rodada, sem incluir nenhum segredo.

    Apenas a presenca de cada variavel e registrada; valores de chave, senha e
    string de conexao nunca entram na evidencia (Secao 9.2.1).

    O `.env` e carregado aqui de proposito. Sem isso o coletor le apenas o
    ambiente do proprio processo e grava uma ficha que descreve o coletor, nao a
    API medida — foi o que aconteceu na rodada 1, cuja ficha registrou o RAG em
    fallback JSON enquanto a API respondia a partir do Supabase. Uma evidencia
    errada sobre o ambiente e pior do que nenhuma, porque parece auditavel.
    """

    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[3] / ".env")

    return {
        "coletado_em": datetime.now(timezone.utc).isoformat(),
        "host": host,
        "commit": _commit(),
        "python": sys.version.split()[0],
        "sistema": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "modelo_llm": os.getenv("GEMINI_MODEL", "nao definido"),
        "rag_max_sources": os.getenv("RAG_MAX_SOURCES", "nao definido"),
        "configuracao_presente": {
            "GEMINI_API_KEY": bool(os.getenv("GEMINI_API_KEY", "").strip()),
            "DATABASE_URL": bool(os.getenv("DATABASE_URL", "").strip()),
            "SUPABASE_DATABASE_URL": bool(
                os.getenv("SUPABASE_DATABASE_URL", "").strip()
            ),
        },
        "origem_do_rag": (
            "banco (public.source_extracts)"
            if os.getenv("DATABASE_URL", "").strip()
            or os.getenv("SUPABASE_DATABASE_URL", "").strip()
            else "fallback JSON local (app/rag/data/sharepoint)"
        ),
    }


#: HTTP 429 significa quota esgotada. Cada nova tentativa consome mais uma
#: unidade e devolve o mesmo erro, entao a rodada inteira aborta.
STATUS_DE_QUOTA = 429

#: HTTP 502 e o que a API devolve quando o provedor responde 503
#: ("high demand"). E congestao passageira, nao consome quota e merece nova
#: tentativa — o oposto exato do 429.
STATUS_TRANSITORIOS = frozenset({502, 503, 504})


def _consulta(
    cliente: httpx.Client,
    pergunta: str,
    tentativas_transitorias: int = 0,
    espera_base: float = 5.0,
) -> dict:
    """Envia a pergunta, repetindo apenas o que for congestao passageira.

    A latencia devolvida e a da tentativa que respondeu, nunca a soma com as
    esperas. Foi exatamente essa confusao que invalidou a leitura de desempenho
    da rodada 1: o sleep do backoff entrou no cronometro e transformou 9 s de
    processamento em 39 s de "latencia".
    """

    ultima = {}
    for tentativa in range(tentativas_transitorias + 1):
        inicio = perf_counter()
        try:
            resposta = cliente.post(
                "/api/chat",
                json={"message": pergunta, "use_intent_classifier": True},
            )
        except Exception as error:
            ultima = {
                "http_status": None,
                "erro_operacional": f"{type(error).__name__}: {error}",
                "latencia_medida_ms": round((perf_counter() - inicio) * 1000),
                "tentativas": tentativa + 1,
            }
            if tentativa < tentativas_transitorias:
                sleep(espera_base * (2**tentativa))
                continue
            return ultima

        medida_ms = round((perf_counter() - inicio) * 1000)
        if resposta.status_code == 200:
            break

        ultima = {
            "http_status": resposta.status_code,
            "erro_operacional": resposta.text[:400],
            "latencia_medida_ms": medida_ms,
            "tentativas": tentativa + 1,
        }
        if resposta.status_code == STATUS_DE_QUOTA:
            return ultima
        if (
            resposta.status_code in STATUS_TRANSITORIOS
            and tentativa < tentativas_transitorias
        ):
            sleep(espera_base * (2**tentativa))
            continue
        return ultima
    else:
        return ultima

    corpo = resposta.json()
    intencao = corpo.get("intent") or {}
    return {
        "http_status": 200,
        "erro_operacional": None,
        "texto": corpo.get("text", ""),
        "modelo": corpo.get("model"),
        "fontes": [
            {
                "id": fonte.get("id"),
                "titulo": fonte.get("title"),
                "lista": fonte.get("list_name"),
                "score": fonte.get("score"),
                "trecho": fonte.get("excerpt"),
            }
            for fonte in corpo.get("sources", [])
        ],
        "intencao_macro": intencao.get("macro"),
        "intencao_especifica": intencao.get("specific"),
        "confianca_especifica": intencao.get("confidence_specific"),
        "latencia_reportada_ms": corpo.get("latency_ms"),
        "recuperacao_ms": corpo.get("retrieval_ms"),
        "latencia_medida_ms": medida_ms,
        "tentativas": tentativa + 1,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Coleta as respostas do RNF04.")
    parser.add_argument("--host", default="http://127.0.0.1:8000")
    parser.add_argument("--saida", default="evidencias/rnf04")
    parser.add_argument(
        "--pausa",
        type=float,
        default=0.0,
        help=(
            "Segundos de espera entre perguntas. A rodada de 21/09/2026 perdeu 13 "
            "das 24 respostas para HTTP 429 do provedor: a quota estourou na "
            "decima segunda pergunta e derrubou todo o resto. Uma pausa aqui troca "
            "tempo de parede por uma rodada valida."
        ),
    )
    parser.add_argument(
        "--faixa",
        default="",
        help=(
            "Fatia continua da amostra a executar, no formato inicio-fim em base 1 "
            "(ex.: 1-18). Serve para partir a rodada em dias diferentes quando a "
            "quota diaria nao comporta as 24 perguntas. A fatia e sempre continua "
            "e segue a ordem congelada do arquivo: nao ha escolha de quais "
            "perguntas rodam, o que impede selecao oportunista. Cada parte grava "
            "em seu proprio diretorio e a apuracao junta as partes."
        ),
    )
    parser.add_argument(
        "--tentativas-transitorias",
        type=int,
        default=0,
        help=(
            "Quantas vezes repetir uma pergunta que falhou por congestao do "
            "provedor (HTTP 502/503). Essas falhas nao consomem quota. HTTP 429 "
            "nunca e repetido e aborta a rodada, porque cada tentativa custa "
            "uma unidade de quota e devolve o mesmo erro."
        ),
    )
    argumentos = parser.parse_args()

    amostra = json.loads(AMOSTRA.read_text(encoding="utf-8"))
    perguntas = amostra["perguntas"]

    if argumentos.faixa:
        try:
            inicio_texto, _, fim_texto = argumentos.faixa.partition("-")
            inicio, fim = int(inicio_texto), int(fim_texto)
        except ValueError:
            print(f"ERRO: faixa invalida {argumentos.faixa!r}. Use o formato 1-18.")
            return 2
        if not 1 <= inicio <= fim <= len(perguntas):
            print(
                f"ERRO: faixa {inicio}-{fim} fora dos limites "
                f"(a amostra tem {len(perguntas)} perguntas)."
            )
            return 2
        perguntas = perguntas[inicio - 1 : fim]
        print(f"[RNF04] faixa {inicio}-{fim} da ordem congelada da amostra")

    destino = Path(argumentos.saida)
    destino.mkdir(parents=True, exist_ok=True)

    ambiente = _ambiente(argumentos.host)
    ambiente["amostra_versao"] = amostra["versao"]
    ambiente["total_de_perguntas"] = len(perguntas)
    ambiente["faixa"] = argumentos.faixa or "completa"
    ambiente["retries_do_provedor"] = os.getenv("GEMINI_MAX_RETRIES", "padrao")
    ambiente["provedor_llm"] = os.getenv("LLM_PROVIDER", "gemini")
    (destino / "ambiente.json").write_text(
        json.dumps(ambiente, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[RNF04] origem do RAG: {ambiente['origem_do_rag']}")
    print(f"[RNF04] commit {ambiente['commit']} | {len(perguntas)} perguntas\n")

    registros = []
    with httpx.Client(base_url=argumentos.host, timeout=TIMEOUT_SEGUNDOS) as cliente:
        for indice, caso in enumerate(perguntas, start=1):
            if argumentos.pausa and indice > 1:
                sleep(argumentos.pausa)
            resultado = _consulta(
                cliente,
                caso["pergunta"],
                tentativas_transitorias=argumentos.tentativas_transitorias,
            )
            registro = {
                "id": caso["id"],
                "cenario": caso["cenario"],
                "pergunta": caso["pergunta"],
                **resultado,
            }
            registros.append(registro)
            marca = "ok " if resultado["http_status"] == 200 else "ERRO"
            repeticoes = resultado.get("tentativas", 1)
            sufixo = f" [{repeticoes} tentativas]" if repeticoes > 1 else ""
            print(
                f"  [{indice:>2}/{len(perguntas)}] {marca} {caso['id']} "
                f"({resultado['latencia_medida_ms']} ms) "
                f"{len(resultado.get('fontes', []))} fonte(s){sufixo}"
            )
            if resultado["http_status"] == STATUS_DE_QUOTA:
                print(
                    f"\n[RNF04] QUOTA ESGOTADA em {caso['id']}. Rodada abortada "
                    f"apos {indice} de {len(perguntas)} perguntas.\n"
                    "[RNF04] As perguntas restantes NAO foram enviadas: insistir "
                    "so gastaria quota para receber o mesmo 429.\n"
                    f"[RNF04] Retome com --faixa {indice + 1}-{len(perguntas)} "
                    "quando a quota voltar."
                )
                break

    with (destino / "respostas.jsonl").open("w", encoding="utf-8") as arquivo:
        for registro in registros:
            arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")

    # A ficha lida do `.env` descreve o processo coletor, nao a API. Se a API
    # subiu com variaveis de ambiente proprias — foi o caso da rodada no
    # flash-lite, iniciada com GEMINI_MODEL e GEMINI_MAX_RETRIES no comando —
    # a ficha registra o modelo errado e a evidencia mente com aparencia de
    # auditoria. O modelo que o provedor devolve em cada resposta e a unica
    # fonte que nao pode divergir do que foi medido; e ele que vale.
    modelos_observados = sorted(
        {registro.get("modelo") for registro in registros if registro.get("modelo")}
    )
    ambiente["modelo_observado_nas_respostas"] = modelos_observados
    # O OpenRouter devolve o modelo com prefixo de fornecedor
    # ("google/gemini-3.7-flash"). Comparar sem o prefixo evita acusar
    # divergencia entre dois nomes do mesmo modelo.
    sem_prefixo = {m.rsplit("/", 1)[-1] for m in modelos_observados}
    if modelos_observados and ambiente["modelo_llm"].rsplit("/", 1)[-1] not in sem_prefixo:
        ambiente["divergencia_de_modelo"] = (
            f"O `.env` diz {ambiente['modelo_llm']!r}, mas as respostas vieram de "
            f"{', '.join(modelos_observados)}. Vale o que as respostas dizem: a API "
            "foi iniciada com variaveis de ambiente proprias."
        )
        ambiente["modelo_llm"] = modelos_observados[0]
        print(f"\n[RNF04] AVISO: {ambiente['divergencia_de_modelo']}")
    if len(modelos_observados) > 1:
        ambiente["alerta"] = (
            "Respostas de modelos diferentes na mesma rodada. A medicao NAO e "
            "valida: cada modelo e uma configuracao distinta do produto."
        )
        print(f"[RNF04] ERRO: {ambiente['alerta']}")
    (destino / "ambiente.json").write_text(
        json.dumps(ambiente, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Planilha cega: sem 'cenario' e sem o fato esperado, para que a rotulagem
    # nao seja induzida pelo gabarito.
    with (destino / "planilha_cega.csv").open(
        "w", encoding="utf-8", newline=""
    ) as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(
            [
                "id",
                "pergunta",
                "resposta",
                "fontes_retornadas",
                "rotulo",
                "justificativa",
            ]
        )
        for registro in registros:
            fontes = " | ".join(
                str(fonte["titulo"]) for fonte in registro.get("fontes", [])
            )
            escritor.writerow(
                [
                    registro["id"],
                    registro["pergunta"],
                    registro.get("texto", registro.get("erro_operacional", "")),
                    fontes,
                    "",
                    "",
                ]
            )

    erros = [r for r in registros if r["http_status"] != 200]
    print(f"\n[RNF04] gravado em {destino}/")
    if erros:
        print(f"[RNF04] {len(erros)} requisicao(oes) com erro operacional:")
        for registro in erros:
            print(f"   - {registro['id']}: {registro['erro_operacional'][:160]}")
    print(
        "[RNF04] proximo passo: rotular 'planilha_cega.csv' com um dos valores "
        "fundamentada / alucinacao / nao_fundamentada, depois rodar avaliar_rnf04.py"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
