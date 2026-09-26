"""Reteste do CT-RF09-01 depois da correção do truncamento (DEF-RNF04-02).

Na rodada funcional, a resposta à sugestão aceita parou no meio: o modelo gastou
463 dos 508 tokens de saída raciocinando, com o limite de 512. Este reteste repete
o caso contra a API local, já com o limite de 1024, e grava a saída bruta de cada
chamada.

Cada repetição usa uma conversa nova e faz as duas etapas do caso:

1. `POST /api/chat` com a proatividade ativa e a mesma pergunta da rodada;
2. `POST /api/chat/proactive-confirmation` com `decision=accept`.

Critério, definido antes da execução: em todas as repetições, a resposta
principal chega, a sugestão vem com `requires_confirmation=true`, o aceite
retorna `status=accepted` e a resposta ao aceite chega inteira, sem o aviso de
resposta interrompida. O conteúdo da ação sugerida é lido na saída bruta.

O token da identidade simulada é lido de `AUDIO_SIMULATED_IDENTITIES`, no `.env`
do backend, e não é gravado na saída.

Uso, com a API em `http://127.0.0.1:8000` e a partir de `src/backend`:

    .venv/bin/python evidencias/rf01-rf10/rf09/reteste_ct_rf09_01.py --commit <hash> --limite 1024
"""

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

API = "http://127.0.0.1:8000"
PERGUNTA = "Qual é o prazo do projeto PRJ-0442?"
REPETICOES = 5
AVISO = "A resposta foi interrompida antes de terminar"
SAIDA = Path(__file__).resolve().parent / "CT-RF09-01-reteste.txt"


def token_simulado() -> str:
    load_dotenv(Path.cwd() / ".env")
    primeira = os.getenv("AUDIO_SIMULATED_IDENTITIES", "").split(",")[0]
    token = primeira.partition("=")[0].strip()
    if not token:
        raise SystemExit("AUDIO_SIMULATED_IDENTITIES não está configurado no .env.")
    return token


def post(caminho: str, corpo: dict, token: str) -> tuple[int, dict]:
    requisicao = urllib.request.Request(
        f"{API}{caminho}",
        data=json.dumps(corpo).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(requisicao, timeout=90) as resposta:
            return resposta.status, json.loads(resposta.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
        return erro.code, json.loads(erro.read().decode("utf-8") or "{}")


def repeticao(numero: int, token: str) -> tuple[list[str], bool]:
    conversa = f"ct-rf09-01-reteste-{numero}"
    status_chat, chat = post(
        "/api/chat",
        {"message": PERGUNTA, "conversation_id": conversa, "proactivity_enabled": True},
        token,
    )
    sugestao = chat.get("proactive_suggestion") or {}
    linhas = [
        f"=== REPETIÇÃO {numero} ===",
        f"POST /api/chat · conversation_id={conversa} · proactivity_enabled=true",
        f"STATUS: {status_chat}",
        json.dumps(chat, ensure_ascii=False),
    ]
    if not sugestao.get("suggestion_id"):
        linhas.append("Sem sugestão proativa: a etapa de aceite não foi executada.")
        return linhas, False

    status_aceite, aceite = post(
        "/api/chat/proactive-confirmation",
        {
            "suggestion_id": sugestao["suggestion_id"],
            "conversation_id": conversa,
            "decision": "accept",
        },
        token,
    )
    texto = (aceite.get("result") or {}).get("text", "")
    aprovada = (
        status_chat == 200
        and sugestao.get("requires_confirmation") is True
        and status_aceite == 200
        and aceite.get("status") == "accepted"
        and bool(texto)
        and AVISO not in texto
    )
    linhas += [
        "",
        "POST /api/chat/proactive-confirmation · decision=accept",
        f"STATUS: {status_aceite}",
        json.dumps(aceite, ensure_ascii=False),
        "",
        f"Resposta ao aceite inteira, sem aviso de interrupção: {'sim' if aprovada else 'não'}",
    ]
    return linhas, aprovada


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True, help="commit do backend em execução")
    parser.add_argument("--limite", required=True, help="GEMINI_MAX_OUTPUT_TOKENS do backend")
    args = parser.parse_args()

    token = token_simulado()
    inicio = datetime.now().astimezone()
    blocos, aprovadas = [], 0
    for numero in range(1, REPETICOES + 1):
        linhas, aprovada = repeticao(numero, token)
        aprovadas += aprovada
        blocos.append("\n".join(linhas))

    cabecalho = [
        "TIPO DE REGISTRO: SAÍDA BRUTA PRESERVADA",
        "",
        "Caso: CT-RF09-01 — reteste depois da correção do DEF-RNF04-02",
        "Requisito: RF09",
        "Cenário: Positivo",
        f"Início: {inicio:%d/%m/%Y %H:%M} (UTC{inicio:%z})",
        f"Commit do backend: {args.commit}",
        f"Limite de tokens de saída: {args.limite}",
        "Provedor: OpenRouter",
        "Autenticação: Bearer da identidade simulada do .env; valor omitido",
        "",
        "Comando, a partir de src/backend:",
        f"  .venv/bin/python evidencias/rf01-rf10/rf09/{Path(__file__).name}"
        f" --commit {args.commit} --limite {args.limite}",
        "",
        f"Resultado: {aprovadas} de {REPETICOES} repetições com a resposta ao aceite inteira.",
        "",
    ]
    SAIDA.write_text("\n".join(cabecalho) + "\n" + "\n\n".join(blocos) + "\n", encoding="utf-8")
    print(f"{aprovadas}/{REPETICOES} repetições aprovadas; saída em {SAIDA.name}")


if __name__ == "__main__":
    main()
