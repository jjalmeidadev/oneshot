"""S5-32 (#286): CT-RNF10 a CT-RNF12 da Seção 9.2.3, sem credenciais nem rede.

* RNF10 — manutenibilidade: limites entre interface, negócio e dados,
  API documentada, testes versionados e instruções reproduzíveis.
* RNF11 — falhas previstas e inesperadas com resposta controlada, auditoria
  preservada e sem *stack trace*, segredo ou corpo bruto do provedor.
* RNF12 — completude da massa sintética, pelo validador
  ``scripts/validar_massa_sintetica.py``.

Os negativos alteram apenas cópias temporárias; os arquivos reais são relidos
no fim para provar que ficaram intactos. Defeitos confirmados entram como
``xfail(strict=True)``, com o ID do defeito no motivo, como na S4-33.
``S5_32_EVIDENCE_DIR`` habilita a gravação dos artefatos da rodada.
"""

from __future__ import annotations

import ast
import hashlib
import io
import json
import logging
import os
from pathlib import Path
import re
import shutil
from urllib.error import HTTPError

from fastapi.openapi.models import OpenAPI
from fastapi.testclient import TestClient
import pytest

from app.gemini.client import OUT_OF_SCOPE_ANSWER
from app.main import app
from scripts.validar_massa_sintetica import (
    CATEGORIA_DOCUMENTOS,
    CATEGORIAS,
    CATEGORIAS_SQL,
    SHAREPOINT_PADRAO,
    SQL_PADRAO,
    validar_massa,
)

pytestmark = pytest.mark.integration

BACKEND = Path(__file__).resolve().parents[2]
ROOT = BACKEND.parents[1]
APP = BACKEND / "app"


def evidence(name: str, payload) -> None:
    print(json.dumps({"artifact": name, "observation": payload}, ensure_ascii=True, default=str)[:4000])
    target = os.getenv("S5_32_EVIDENCE_DIR")
    if target:
        directory = Path(target)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8"
        )


def sha256_tree(paths) -> dict[str, str]:
    return {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


# ==========================================================================
# RNF10 — manutenibilidade
# ==========================================================================

#: Interface HTTP: único lugar onde o framework web pode aparecer.
WEB = {"fastapi", "starlette"}
#: Acesso direto a banco e a serviços externos.
DRIVERS_BANCO = {"psycopg", "psycopg_pool"}
CLIENTES_REDE = {"httpx", "requests", "aio_pika", "pika", "urllib3"}
MODULOS_REDE = {"urllib.request"}

#: Instruções obrigatórias do README do backend (instalar, executar, testar).
INSTRUCOES_README = {
    "instalar dependencias": r"pip install -r requirements\.txt",
    "executar a API": r"uvicorn app\.main:app",
    "executar os testes": r"-m pytest app/tests",
}


def camada(relativo: Path) -> str:
    partes = relativo.parts
    nome = partes[-1]
    if nome == "main.py" and len(partes) == 1:
        return "interface"
    if nome == "router.py" or relativo.as_posix() == "security/http.py":
        return "interface"
    if partes[0] == "database" or nome == "repository.py" or relativo.as_posix() == "reports/sources.py":
        return "dados"
    return "negocio"


def importacoes(arquivo: Path) -> set[str]:
    arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
    nomes: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.level == 0 and no.module:
            nomes.add(no.module)
    return nomes


def violacoes_de_camada(app_dir: Path) -> list[str]:
    """Checklist objetivo da separação interface / negócio / dados."""

    violacoes = []
    for arquivo in sorted(app_dir.rglob("*.py")):
        relativo = arquivo.relative_to(app_dir)
        if relativo.parts[0] in {"tests", "__pycache__"}:
            continue
        nomes = importacoes(arquivo)
        topos = {nome.split(".")[0] for nome in nomes}
        tipo = camada(relativo)
        rede = (topos & CLIENTES_REDE) | (nomes & MODULOS_REDE)
        if tipo == "interface" and (topos & DRIVERS_BANCO or rede):
            violacoes.append(
                f"{relativo.as_posix()}: interface acessa banco/serviço externo diretamente "
                f"({', '.join(sorted((topos & DRIVERS_BANCO) | rede))})"
            )
        if tipo != "interface" and topos & WEB:
            violacoes.append(f"{relativo.as_posix()}: camada {tipo} depende do framework web")
        if tipo != "dados" and topos & DRIVERS_BANCO:
            violacoes.append(f"{relativo.as_posix()}: driver de banco fora da camada de dados")
    return violacoes


def instrucoes_ausentes(readme: Path) -> list[str]:
    texto = readme.read_text(encoding="utf-8")
    return [nome for nome, padrao in INSTRUCOES_README.items() if not re.search(padrao, texto)]


def contrato_documentado() -> dict:
    with TestClient(app) as client:
        docs = client.get("/docs")
        contrato = client.get("/openapi.json")
    assert contrato.status_code == 200
    payload = contrato.json()
    OpenAPI.model_validate(payload)
    sem_resposta = [
        f"{metodo.upper()} {caminho}"
        for caminho, operacoes in payload["paths"].items()
        for metodo, operacao in operacoes.items()
        if not operacao.get("responses")
    ]
    return {"docs_http": docs.status_code, "operacoes": sum(len(o) for o in payload["paths"].values()),
            "sem_resposta_documentada": sem_resposta}


def fetch_fora_da_camada_api() -> list[str]:
    origem = ROOT / "src/frontend/src"
    return sorted(
        str(arquivo.relative_to(origem)).replace("\\", "/")
        for arquivo in origem.rglob("*.ts*")
        if ".test." not in arquivo.name
        and "fetch(" in arquivo.read_text(encoding="utf-8")
        and "lib/api" not in arquivo.as_posix()
    )


def test_ct_rnf10_p():
    violacoes = violacoes_de_camada(APP)
    readme = BACKEND / "README.md"
    ausentes = instrucoes_ausentes(readme)
    contrato = contrato_documentado()
    testes_backend = sorted((APP / "tests").glob("test_*.py"))
    testes_frontend = sorted((ROOT / "src/frontend/src").rglob("*.test.ts*"))
    e2e = sorted((ROOT / "src/frontend/e2e").glob("*.spec.ts"))
    fetch_fora = fetch_fora_da_camada_api()
    distribuicao: dict[str, list[str]] = {"interface": [], "negocio": [], "dados": []}
    for arquivo in sorted(APP.rglob("*.py")):
        relativo = arquivo.relative_to(APP)
        if relativo.parts[0] not in {"tests", "__pycache__"}:
            distribuicao[camada(relativo)].append(relativo.as_posix())
    evidence("CT-RNF10-P.json", {
        "checklist": {
            "interface_sem_acesso_direto_a_banco_ou_rede": not any("interface acessa" in v for v in violacoes),
            "negocio_e_dados_sem_framework_web": not any("framework web" in v for v in violacoes),
            "driver_de_banco_isolado_na_camada_de_dados": not any("driver de banco" in v for v in violacoes),
            "frontend_acessa_api_somente_por_lib_api": not fetch_fora,
            "readme_com_instalar_executar_testar": not ausentes,
            "api_documentada_openapi_e_docs": contrato["docs_http"] == 200 and not contrato["sem_resposta_documentada"],
            "testes_versionados_backend_frontend_e2e": bool(testes_backend and testes_frontend and e2e),
        },
        "violacoes": violacoes, "instrucoes_ausentes": ausentes, "fetch_fora_de_lib_api": fetch_fora,
        "contrato": contrato,
        "quantidade_de_testes": {"backend_arquivos": len(testes_backend),
                                  "frontend_arquivos": len(testes_frontend), "e2e_specs": len(e2e)},
        "modulos_por_camada": distribuicao,
        "readme": str(readme.relative_to(ROOT)).replace("\\", "/"),
        "escopo": "análise estática dos imports de src/backend/app e do frontend; reprodução do README registrada à parte",
    })
    assert not violacoes, violacoes
    assert not ausentes, ausentes
    assert not fetch_fora, fetch_fora
    assert contrato["docs_http"] == 200 and not contrato["sem_resposta_documentada"], contrato
    assert testes_backend and testes_frontend and e2e


def test_ct_rnf10_n(tmp_path):
    referencia = sha256_tree([BACKEND / "README.md", APP / "reports/router.py"])

    # 1) Instrução obrigatória removida de uma cópia do README.
    readme = tmp_path / "README.md"
    texto = (BACKEND / "README.md").read_text(encoding="utf-8")
    readme.write_text(re.sub(r"(?m)^.*-m pytest app/tests.*$\n?", "", texto), encoding="utf-8")
    instrucao_removida = instrucoes_ausentes(readme)

    # 2) Dependência direta de acesso externo introduzida na rota de uma cópia.
    copia_app = tmp_path / "app"
    shutil.copytree(APP, copia_app, ignore=shutil.ignore_patterns("__pycache__", "tests", "data"))
    rota = copia_app / "reports/router.py"
    rota.write_text(
        "import httpx\nimport psycopg\n" + rota.read_text(encoding="utf-8")
        + "\n\ndef _atalho_indevido():\n    return httpx.get('https://exemplo.invalid/dados')\n",
        encoding="utf-8",
    )
    violacoes = violacoes_de_camada(copia_app)

    evidence("CT-RNF10-N.json", {
        "readme_sem_instrucao_de_teste": {"instrucoes_ausentes": instrucao_removida},
        "rota_com_acesso_externo_direto": {"arquivo_alterado": "reports/router.py (cópia)", "violacoes": violacoes},
        "arquivos_reais_intactos": sha256_tree([BACKEND / "README.md", APP / "reports/router.py"]) == referencia,
    })
    assert instrucao_removida == ["executar os testes"]
    assert any(v.startswith("reports/router.py: interface acessa") for v in violacoes), violacoes
    assert any(v.startswith("reports/router.py: driver de banco") for v in violacoes), violacoes
    assert violacoes_de_camada(APP) == [], "a estrutura real deve continuar sem violações"
    assert sha256_tree([BACKEND / "README.md", APP / "reports/router.py"]) == referencia


# ==========================================================================
# RNF11 — tratamento de falhas
# ==========================================================================

SEGREDO = "SEGREDO-CT-RNF11-NAO-PODE-SAIR"
CORPO_BRUTO = f'{{"error": {{"message": "quota interna {SEGREDO}", "debug": "stack interno"}}}}'
CONSULTA_COM_FONTE = "Como devo registrar um objeto perdido?"
SINAIS_DE_VAZAMENTO = ("Traceback", 'File "', SEGREDO, "stack interno", "sk-", "GEMINI_API_KEY")


@pytest.fixture
def auditoria(monkeypatch):
    registros: list[dict] = []
    monkeypatch.setattr("app.pipeline.trace_interaction", lambda **kwargs: registros.append(kwargs) or "trace-s5-32")
    return registros


@pytest.fixture
def provedor_configurado(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", f"chave-ficticia-{SEGREDO}")
    monkeypatch.setenv("GEMINI_MAX_RETRIES", "0")


def _sem_vazamento(texto: str) -> list[str]:
    return [sinal for sinal in SINAIS_DE_VAZAMENTO if sinal in texto]


def _cenario_classificacao(monkeypatch, tmp_path):
    def falha(_texto):
        raise RuntimeError(f"modelo corrompido em /opt/modelos {SEGREDO}")
    monkeypatch.setattr("app.nlp.inference.classify", falha)
    return {"message": "qual o status do PRJ-0442?", "use_intent_classifier": True}


def _cenario_sem_resultado(monkeypatch, tmp_path):
    monkeypatch.setattr("app.gemini.client.retrieve_context", lambda *a, **k: [])

    def proibido(*_a, **_k):
        raise AssertionError("o provedor não pode ser chamado sem fonte")
    monkeypatch.setattr("app.gemini.client.urlopen", proibido)
    return {"message": "qual a cor do trem da linha imaginaria 99?", "use_intent_classifier": False}


def _cenario_fonte_indisponivel(monkeypatch, tmp_path):
    monkeypatch.setenv("SHAREPOINT_MOCK_DATA_DIR", str(tmp_path / f"origem-ausente-{SEGREDO}"))
    return {"message": CONSULTA_COM_FONTE, "use_intent_classifier": False}


def _cenario_timeout(monkeypatch, tmp_path):
    def expira(*_a, **_k):
        raise TimeoutError(f"read timed out after 30s ({SEGREDO})")
    monkeypatch.setattr("app.gemini.client.urlopen", expira)
    return {"message": CONSULTA_COM_FONTE, "use_intent_classifier": False}


def _cenario_provedor_5xx(monkeypatch, tmp_path):
    def erro_http(request, *_a, **_k):
        raise HTTPError(request.full_url, 503, "Service Unavailable", {}, io.BytesIO(CORPO_BRUTO.encode()))
    monkeypatch.setattr("app.gemini.client.urlopen", erro_http)
    return {"message": CONSULTA_COM_FONTE, "use_intent_classifier": False}


#: Falha prevista -> (cenário, HTTP esperado, mensagem definida esperada).
FALHAS_PREVISTAS = {
    "falha_de_classificacao": (_cenario_classificacao, 503,
                               "O serviço de processamento está indisponível. Tente novamente em instantes."),
    "ausencia_de_resultado": (_cenario_sem_resultado, 200, OUT_OF_SCOPE_ANSWER),
    "fonte_indisponivel": (_cenario_fonte_indisponivel, 503,
                           "Não foi possível obter uma resposta. Tente novamente em instantes."),
    "timeout_do_provedor": (_cenario_timeout, 502,
                            "Não foi possível obter uma resposta. Tente novamente em instantes."),
    "provedor_5xx": (_cenario_provedor_5xx, 502,
                     "Não foi possível obter uma resposta. Tente novamente em instantes."),
}


@pytest.mark.parametrize("nome", list(FALHAS_PREVISTAS))
def test_ct_rnf11_p(nome, monkeypatch, tmp_path, auditoria, provedor_configurado, caplog):
    cenario, status_esperado, mensagem_esperada = FALHAS_PREVISTAS[nome]
    corpo = cenario(monkeypatch, tmp_path)
    caplog.set_level(logging.DEBUG)
    with TestClient(app) as client:
        resposta = client.post("/api/chat", json=corpo)
    payload = resposta.json()
    mensagem = payload.get("detail") if resposta.status_code >= 400 else payload.get("text")
    vazamentos = _sem_vazamento(resposta.text) + [f"log:{s}" for s in _sem_vazamento(caplog.text)]
    registro = auditoria[-1] if auditoria else {}
    observado = {
        "cenario": nome, "http": resposta.status_code, "http_esperado": status_esperado,
        "mensagem": mensagem, "mensagem_esperada": mensagem_esperada,
        "vazamentos": vazamentos, "auditoria_registros": len(auditoria),
        "auditoria_estado": "falha" if registro.get("error_message") else ("resposta" if registro.get("response") else None),
    }
    evidence(f"CT-RNF11-P-{nome}.json", observado)
    assert resposta.status_code == status_esperado, observado
    assert mensagem == mensagem_esperada, observado
    assert not vazamentos, observado
    assert len(auditoria) == 1 and observado["auditoria_estado"] in {"falha", "resposta"}, observado


def _excecao_inesperada(monkeypatch):
    def quebra(*_a, **_k):
        raise KeyError(f"campo interno ausente {SEGREDO}")
    monkeypatch.setattr("app.pipeline.generate_chat_response", quebra)


def _payload_invalido(monkeypatch):
    class RespostaInvalida:
        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

        def read(self):
            return f"<html>gateway {SEGREDO}</html>".encode()

    monkeypatch.setattr("app.gemini.client.urlopen", lambda *_a, **_k: RespostaInvalida())


def _observar_negativo(nome, preparar, monkeypatch, auditoria, caplog):
    preparar(monkeypatch)
    caplog.set_level(logging.DEBUG)
    with TestClient(app, raise_server_exceptions=False) as client:
        resposta = client.post("/api/chat", json={"message": CONSULTA_COM_FONTE, "use_intent_classifier": False})
    try:
        corpo = resposta.json()
        mensagem = corpo.get("detail")
    except ValueError:
        corpo, mensagem = None, None
    observado = {
        "cenario": nome, "http": resposta.status_code, "content_type": resposta.headers.get("content-type"),
        "corpo": resposta.text[:300], "mensagem_definida_pelo_projeto": mensagem,
        "vazamentos_na_resposta": _sem_vazamento(resposta.text),
        "vazamentos_no_log": _sem_vazamento(caplog.text),
        "auditoria_registros": len(auditoria),
        "auditoria_com_falha": bool(auditoria and auditoria[-1].get("error_message")),
    }
    evidence(f"CT-RNF11-N-{nome}.json", observado)
    return observado


def test_ct_rnf11_n_payload_invalido(monkeypatch, auditoria, provedor_configurado, caplog):
    observado = _observar_negativo("payload_invalido", _payload_invalido, monkeypatch, auditoria, caplog)
    assert observado["http"] == 502, observado
    assert observado["mensagem_definida_pelo_projeto"] == "Não foi possível obter uma resposta. Tente novamente em instantes."
    assert not observado["vazamentos_na_resposta"] and not observado["vazamentos_no_log"], observado
    assert observado["auditoria_com_falha"], observado


@pytest.mark.xfail(
    strict=True,
    reason=(
        "DEF-S5-32-01: exceção inesperada em /api/chat escapa do pipeline; a API responde o "
        "'Internal Server Error' genérico do Starlette, sem mensagem definida pelo projeto, e a "
        "interação não é auditada (RNF03/RNF11)."
    ),
)
def test_ct_rnf11_n_excecao_inesperada(monkeypatch, auditoria, provedor_configurado, caplog):
    observado = _observar_negativo("excecao_inesperada", _excecao_inesperada, monkeypatch, auditoria, caplog)
    # Mesmo no defeito, nada sensível pode sair: esta parte precisa passar.
    assert not observado["vazamentos_na_resposta"], observado
    assert observado["http"] == 500, observado
    assert observado["mensagem_definida_pelo_projeto"], observado
    assert observado["auditoria_com_falha"], observado


# ==========================================================================
# RNF12 — completude da massa sintética
# ==========================================================================


def test_ct_rnf12_p():
    relatorio = validar_massa()
    evidence("CT-RNF12-P.json", relatorio.como_dict())
    assert relatorio.aprovado, relatorio.como_dict()
    assert set(relatorio.contagens) == set(CATEGORIAS)
    assert all(relatorio.contagens[categoria] > 0 for categoria in CATEGORIAS)


def _copia_sem_categoria(categoria: str, destino: Path) -> tuple[list[Path], Path]:
    """Cópia temporária da massa sem uma categoria.

    Nas categorias SQL, o ``INSERT INTO`` da tabela passa a apontar para uma
    tabela inexistente: a linha deixa de entrar na categoria e o restante do
    arquivo continua igual. Nos documentos, as listas ficam vazias.
    """

    destino.mkdir(parents=True)
    sharepoint = destino / "sharepoint"
    shutil.copytree(SHAREPOINT_PADRAO, sharepoint, ignore=shutil.ignore_patterns("*.md"))
    arquivos = []
    for original in SQL_PADRAO:
        texto = original.read_text(encoding="utf-8")
        for tabela in CATEGORIAS_SQL.get(categoria, ()):
            texto = re.sub(rf"(INSERT\s+INTO\s+){re.escape(tabela)}\b", rf"\g<1>{tabela}_removida_ct_rnf12_n",
                           texto, flags=re.IGNORECASE)
        copia = destino / original.name
        copia.write_text(texto, encoding="utf-8")
        arquivos.append(copia)
    if categoria == CATEGORIA_DOCUMENTOS:
        for lista in sharepoint.glob("*.json"):
            conteudo = json.loads(lista.read_text(encoding="utf-8"))
            conteudo["value"] = []
            lista.write_text(json.dumps(conteudo, ensure_ascii=False), encoding="utf-8")
    return arquivos, sharepoint


def test_ct_rnf12_n(tmp_path):
    referencia = validar_massa().arquivos
    resultados = {}
    for categoria in CATEGORIAS:
        arquivos, sharepoint = _copia_sem_categoria(categoria, tmp_path / categoria)
        relatorio = validar_massa(arquivos, sharepoint)
        resultados[categoria] = {"aprovado": relatorio.aprovado, "ausentes": relatorio.ausentes,
                                 "contagens": relatorio.contagens}
    intacta = validar_massa()
    evidence("CT-RNF12-N.json", {"copias_sem_categoria": resultados,
                                 "massa_oficial_intacta": intacta.arquivos == referencia and intacta.aprovado})
    for categoria, resultado in resultados.items():
        assert not resultado["aprovado"], (categoria, resultado)
        assert resultado["ausentes"] == [categoria], (categoria, resultado)
    assert intacta.aprovado and intacta.arquivos == referencia
