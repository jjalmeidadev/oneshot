"""Torna o artefato do classificador carregável fora do notebook.

O `joblib` produzido pelo notebook `classificador_intencoes_metro.ipynb` grava
referências a `__main__.identidade` e `__main__.ClassificadorHierarquico`,
porque as duas definições vivem no topo daquele notebook. Carregar o artefato
de qualquer código importável falha com:

    AttributeError: module '__main__' has no attribute 'identidade'

Este script resolve a origem do problema. Ele carrega o artefato antigo
declarando temporariamente as definições em `__main__`, reaponta os objetos
para `app.nlp.classifier` — o lar canônico delas — e grava de volta. O modelo
não é retreinado: os pesos, os vetorizadores e os limiares são exatamente os
que produziram as métricas registradas na Seção 8.10.3 do `Projeto.md`.

A versão do scikit-learn importa. O artefato foi serializado com a 1.6.1, e
carregá-lo com outra versão faz o próprio scikit-learn advertir que o resultado
pode ser inválido. O script recusa executar fora dessa versão.

Uso:

    cd src/backend
    .venv/bin/python ../notebooks/migrar_artefato_classificador.py

Com `--verificar`, apenas confere se o artefato já está migrado, sem gravar.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BACKEND = RAIZ / "src" / "backend"
sys.path.insert(0, str(BACKEND))

from app.nlp import classifier  # noqa: E402  (depende do sys.path acima)

VERSAO_SKLEARN_DO_ARTEFATO = "1.6.1"


def carregar_artefato_legado(caminho: Path):
    """Carrega o artefato preso ao notebook, suprindo os nomes em `__main__`."""

    import joblib

    principal = sys.modules["__main__"]
    anteriores = {
        nome: getattr(principal, nome, None)
        for nome in ("identidade", "ClassificadorHierarquico")
    }
    setattr(principal, "identidade", classifier.identidade)
    setattr(principal, "ClassificadorHierarquico", classifier.ClassificadorHierarquico)
    try:
        return joblib.load(caminho)
    finally:
        for nome, anterior in anteriores.items():
            if anterior is None:
                delattr(principal, nome)
            else:
                setattr(principal, nome, anterior)


def reapontar_para_o_modulo(dados: dict) -> dict:
    """Faz os objetos referenciarem `app.nlp.classifier` em vez de `__main__`.

    O estado dos objetos já foi restaurado pelo pickle; o que muda aqui é
    apenas de qual módulo a classe e o analyzer vêm.
    """

    modelo = dados["modelo"]
    modelo.__class__ = classifier.ClassificadorHierarquico
    for vetorizador in ("tfidf_palavras",):
        dados[vetorizador].analyzer = classifier.identidade
    return dados


def artefato_carrega_isoladamente(caminho: Path) -> bool:
    """Confere a migração em um processo limpo, sem nada em `__main__`.

    Verificar dentro deste processo não provaria nada: as definições já estão
    importadas aqui.
    """

    codigo = (
        "import sys; sys.path.insert(0, %r)\n"
        "from app.nlp.classifier import load_artifact\n"
        "from pathlib import Path\n"
        "artefato = load_artifact(Path(%r))\n"
        "assert artefato.modelo.macro_clf is not None\n"
        "print(artefato.representacao)\n" % (str(BACKEND), str(caminho))
    )
    resultado = subprocess.run(
        [sys.executable, "-c", codigo], capture_output=True, text=True
    )
    if resultado.returncode != 0:
        print(resultado.stderr.strip().splitlines()[-1], file=sys.stderr)
    return resultado.returncode == 0


def exigir_versao_do_sklearn() -> None:
    import sklearn

    if sklearn.__version__ != VERSAO_SKLEARN_DO_ARTEFATO:
        raise SystemExit(
            f"O artefato foi serializado com scikit-learn "
            f"{VERSAO_SKLEARN_DO_ARTEFATO} e o ambiente tem "
            f"{sklearn.__version__}. Carregar entre versões diferentes pode "
            "produzir um modelo inválido silenciosamente. Instale a versão "
            "declarada em requirements.txt antes de migrar."
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verificar",
        action="store_true",
        help="apenas confere se o artefato já carrega, sem gravar",
    )
    argumentos = parser.parse_args()
    caminho = classifier.ARTIFACT_PATH

    if artefato_carrega_isoladamente(caminho):
        print(f"{caminho.name} já carrega fora do notebook; nada a fazer.")
        return 0

    if argumentos.verificar:
        print(f"{caminho.name} ainda depende do notebook para carregar.")
        return 1

    exigir_versao_do_sklearn()

    import joblib

    reserva = caminho.with_suffix(caminho.suffix + ".notebook")
    if not reserva.exists():
        shutil.copy2(caminho, reserva)
        print(f"Cópia do artefato original guardada em {reserva.name}")

    dados = reapontar_para_o_modulo(carregar_artefato_legado(caminho))
    joblib.dump(dados, caminho)

    if not artefato_carrega_isoladamente(caminho):
        raise SystemExit("A migração não produziu um artefato carregável.")

    print(f"{caminho.name} migrado: agora carrega de qualquer processo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
