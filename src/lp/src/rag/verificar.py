"""Confere se está tudo pronto para publicar.

Existe para a hora em que a documentação final chegar: em vez de lembrar de
seis conferências separadas, é um comando que diz "pode empurrar" ou aponta
exatamente o que falta.

    python verificar.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

RAG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(RAG_DIR))


def _carregar_env() -> None:
    """Lê o `backend/.env`, como o serviço faz ao subir.

    Sem isto o verificador acusava a chave como ausente mesmo com ela
    configurada — e um verificador que grita sem motivo é pior que nenhum,
    porque na próxima vez o vermelho de verdade é ignorado.
    """

    arquivo = RAG_DIR / "backend" / ".env"
    if not arquivo.exists():
        return
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, _, valor = linha.partition("=")
        # `setdefault`: o que já veio do ambiente tem precedência sobre o
        # arquivo, que é a mesma ordem que o python-dotenv usa.
        os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


_carregar_env()

OK = "  ok  "
FALHA = " FALHA"


class Relatorio:
    def __init__(self) -> None:
        self.problemas: list[str] = []

    def checar(self, titulo: str, condicao: bool, dica: str = "") -> bool:
        print(f"[{OK if condicao else FALHA}] {titulo}")
        if not condicao:
            if dica:
                print(f"         → {dica}")
            self.problemas.append(titulo)
        return condicao


def rodar(comando: list[str], cwd: Path) -> tuple[bool, str]:
    try:
        processo = subprocess.run(
            comando, cwd=cwd, capture_output=True, text=True, timeout=600
        )
    except Exception as erro:  # noqa: BLE001
        return False, str(erro)
    return processo.returncode == 0, (processo.stdout + processo.stderr)


def main() -> int:
    from model.config import get_model_settings

    settings = get_model_settings()
    r = Relatorio()

    print("== Índice ==")
    indice_npz = settings.artifacts_dir / "index.npz"
    indice_json = settings.artifacts_dir / "index.json"
    r.checar(
        "o índice existe",
        indice_npz.exists() and indice_json.exists(),
        "rode: python -m model.index",
    )

    if indice_npz.exists():
        from model.store import VectorIndex

        indice = VectorIndex.load(settings.artifacts_dir)
        print(f"         {indice.size} trechos, impressão {indice.fingerprint}")

        from model.corpus import build_chunks, fingerprint

        _, documentos, ignorados = build_chunks(settings.corpus_dir)
        r.checar(
            "o índice está em dia com a documentação",
            fingerprint(documentos) == indice.fingerprint,
            "a documentação mudou desde a última indexação: python -m model.index",
        )
        r.checar(
            "nenhum documento ficou sem carregador",
            not ignorados,
            f"sem suporte de formato: {', '.join(ignorados[:5])}",
        )

        print("\n== Fontes para download ==")
        esperados = {d.name for d in documentos}
        presentes = {p.name for p in settings.documents_dir.glob("*") if p.is_file()}
        faltando = esperados - presentes
        r.checar(
            "todo documento indexado pode ser baixado",
            not faltando,
            f"faltam em documentsRAG: {', '.join(sorted(faltando)[:5])}",
        )

    print("\n== Testes ==")
    passou_modelo, saida_modelo = rodar([sys.executable, "-m", "pytest", "-q"], RAG_DIR / "model")
    r.checar("testes do modelo", passou_modelo, saida_modelo.strip().splitlines()[-1] if saida_modelo else "")
    passou_backend, saida_backend = rodar([sys.executable, "-m", "pytest", "-q"], RAG_DIR / "backend")
    r.checar("testes do backend", passou_backend, saida_backend.strip().splitlines()[-1] if saida_backend else "")

    print("\n== Configuração ==")
    r.checar(
        "a chave do Gemini está configurada",
        bool(settings.api_key),
        "preencha GEMINI_API_KEY em backend/.env (e nas variáveis do host, ao publicar)",
    )
    r.checar(
        "o modelo está ligado ao backend",
        os.getenv("RAG_MODEL_BACKEND", "").strip().lower() == "local",
        "defina RAG_MODEL_BACKEND=local em backend/.env, senão o chat responde 503",
    )

    print()
    if r.problemas:
        print(f"✗ {len(r.problemas)} pendência(s). Resolva antes de publicar.")
        return 1
    print("✓ Pronto para publicar. Não esqueça de commitar:")
    print("    src/lp/src/rag/model/artifacts/index.npz")
    print("    src/lp/src/rag/model/artifacts/index.json")
    print("    src/lp/src/rag/documentsRAG/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
