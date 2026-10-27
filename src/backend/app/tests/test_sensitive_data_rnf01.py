"""S5-27 (D-06, RNF01): barreira de dado sensivel antes do provedor de LLM.

Cobre os padroes acordados, o mascaramento dos documentos, o bloqueio da
pergunta, a guarda final antes da chamada e a auditoria sem o dado. Nenhum
teste usa rede ou banco: o provedor e substituido por um duplo de rede
(`urlopen`) e o banco por uma conexao falsa.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.database.tracing import trace_interaction
from app.gemini import client as gemini_client
from app.gemini.client import SensitiveDataBlockedError, generate_chat_response
from app.gemini.schemas import GeminiChatRequest
from app.main import app
from app.rag.sharepoint import (
    RetrievedDocument,
    SharePointDocument,
    build_rag_input,
    load_sharepoint_documents,
)
from app.security.sensitive_data import (
    SensitiveDataReport,
    describe_categories,
    protect_documents,
    scan,
)
from test_traceability import FakeConnection, FakeCursor, _connect

pytestmark = pytest.mark.integration

DATA_DIR = Path(__file__).resolve().parents[1] / "rag" / "data" / "sharepoint"

# Valores sinteticos com digito verificador valido. Nao pertencem a ninguem.
CPF = "529.982.247-25"
CNPJ = "11.222.333/0001-81"
CARTAO = "4111 1111 1111 1111"


# --------------------------------------------------------------------------
# Padroes acordados
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("texto", "categoria", "marcador"),
    [
        (f"meu CPF e {CPF}", "cpf", "[CPF]"),
        ("cpf sem pontuacao 52998224725", "cpf", "[CPF]"),
        (f"fornecedor {CNPJ}", "cnpj", "[CNPJ]"),
        ("escreva para joao.silva@metro.sp.gov.br", "email", "[E-MAIL]"),
        ("ligue (11) 98765-4321", "telefone", "[TELEFONE]"),
        (f"cartao {CARTAO}", "cartao", "[CARTÃO]"),
        ("chave " + "AIza" + "A" * 35, "credencial", "[CREDENCIAL]"),
        ("token sk-or-v1-abcdefghijklmnopqrstuvwxyz0123", "credencial", "[CREDENCIAL]"),
        ("senha: Metro@2026", "credencial", "[CREDENCIAL]"),
        ("documento CONFIDENCIAL do contrato", "marcador_classificacao", "[DADO CLASSIFICADO]"),
        ("Classificação: restrito", "marcador_classificacao", "[DADO CLASSIFICADO]"),
        ("DADO-SENSIVEL-CT-RNF01-N", "marcador_classificacao", "[DADO CLASSIFICADO]"),
    ],
)
def test_padroes_acordados_sao_mascarados(texto: str, categoria: str, marcador: str) -> None:
    resultado = scan(texto)

    assert resultado.counts == {categoria: 1}
    assert marcador in resultado.masked


@pytest.mark.parametrize(
    "texto",
    [
        "acesso restrito a via durante a manutencao",
        "documento confidencial so em minusculas nao e rotulo",
        "CPF com digito errado 123.456.789-00",
        "status do PRJ-0442 na Linha 15-Prata",
        "prazo de 2026-09-01 a 2026-12-31, custo R$ 1.234.567,89",
        "periodo 2025-2026 e protocolo 2026/0001",
        "cartao com Luhn invalido 4111 1111 1111 1112",
    ],
)
def test_texto_operacional_nao_e_falso_positivo(texto: str) -> None:
    assert scan(texto).counts == {}


def test_massa_sintetica_e_prompt_nao_tem_falso_positivo() -> None:
    documentos = load_sharepoint_documents(DATA_DIR)
    prompt = build_rag_input(
        "Pergunta de sondagem", [RetrievedDocument(documento, 1.0) for documento in documentos]
    )

    assert documentos
    assert all(not scan(d.title + " " + d.content).found for d in documentos)
    assert not scan(prompt).found


def test_categorias_descritas_para_o_usuario() -> None:
    assert describe_categories(["email", "cpf"]) == "CPF e e-mail"
    assert describe_categories(["cpf"]) == "CPF"


# --------------------------------------------------------------------------
# Documentos do RAG
# --------------------------------------------------------------------------


def _documento(source_id: str, conteudo: str, **extra) -> RetrievedDocument:
    return RetrievedDocument(
        SharePointDocument(
            source_id=source_id,
            title=extra.pop("title", "Documento de teste"),
            list_name="Projetos",
            content=conteudo,
            web_url="https://mock.sharepoint.local/item",
            last_modified="2026-09-09T12:00:00Z",
            search_text=conteudo,
            **extra,
        ),
        1.0,
    )


def test_documentos_sao_mascarados_e_classificados_ficam_de_fora() -> None:
    limpo = _documento("lista:1", "Entrega prevista para dezembro.")
    com_cpf = _documento(
        "lista:2",
        f"Responsavel CPF {CPF}.",
        attributes=(("Contato", "joao@metro.sp.gov.br"),),
    )
    confidencial = _documento("lista:3", "Texto qualquer.", confidentiality_level="confidencial")

    protegidos, relatorio = protect_documents([limpo, com_cpf, confidencial])

    assert [r.document.source_id for r in protegidos] == ["lista:1", "lista:2"]
    assert protegidos[0] is limpo
    assert protegidos[1].document.content == "Responsavel CPF [CPF]."
    assert protegidos[1].document.attributes == (("Contato", "[E-MAIL]"),)
    assert relatorio.masked_sources == ["lista:2"]
    assert relatorio.withheld_sources == ["lista:3"]
    assert relatorio.counts == {"cpf": 1, "email": 1, "marcador_classificacao": 1}

    payload = json.dumps(relatorio.audit_payload(), ensure_ascii=False)
    assert CPF not in payload and "joao@" not in payload


# --------------------------------------------------------------------------
# Duplo de rede: o que efetivamente sairia para o provedor
# --------------------------------------------------------------------------


class _FakeProviderResponse:
    def __init__(self, body: dict) -> None:
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self) -> bytes:
        return json.dumps(self.body).encode("utf-8")


@pytest.fixture
def provedor(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Substitui a rede do Gemini e guarda cada payload que sairia."""

    payloads: list[str] = []

    def fake_urlopen(request, timeout: int):
        payloads.append(request.data.decode("utf-8"))
        return _FakeProviderResponse(
            {
                "id": "interaction-s5-27",
                "model": "provedor-de-teste",
                "status": "completed",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [{"type": "text", "text": "Evidencia insuficiente."}],
                    }
                ],
                "usage": {"total_tokens": 1},
            }
        )

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setattr("app.gemini.client.urlopen", fake_urlopen)
    return payloads


def test_documento_sensivel_sai_mascarado_para_o_provedor(
    monkeypatch: pytest.MonkeyPatch, provedor: list[str]
) -> None:
    monkeypatch.setattr(
        "app.gemini.client.retrieve_context",
        lambda *_a, **_k: [
            _documento("lista:1", f"Gestor do contrato, CPF {CPF}, aprovou o TAP."),
            _documento("lista:2", "Outro texto.", confidentiality_level="restrito"),
        ],
    )

    resposta = generate_chat_response(GeminiChatRequest(message="quem aprovou o TAP?"))

    assert len(provedor) == 1
    assert CPF not in provedor[0] and "[CPF]" in provedor[0]
    assert "Outro texto." not in provedor[0]
    assert all(CPF not in (fonte.excerpt or "") for fonte in resposta.sources)
    assert resposta.security_report["withheld_source_ids"] == ["lista:2"]
    assert resposta.security_report["masked_source_ids"] == ["lista:1"]


def test_so_documentos_classificados_nao_gera_chamada(
    monkeypatch: pytest.MonkeyPatch, provedor: list[str]
) -> None:
    monkeypatch.setattr(
        "app.gemini.client.retrieve_context",
        lambda *_a, **_k: [_documento("lista:9", "x", confidentiality_level="confidencial")],
    )

    resposta = generate_chat_response(GeminiChatRequest(message="status"))

    assert provedor == []
    assert resposta.evidence_status == "insufficient"
    assert resposta.security_report["action"] == "bloqueado"


def test_guarda_final_recusa_prompt_com_dado_sensivel(provedor: list[str]) -> None:
    with pytest.raises(SensitiveDataBlockedError) as erro:
        gemini_client._call_llm(f"Contexto com CPF {CPF}", api_key="test-key")

    assert provedor == []
    assert erro.value.status_code == 422
    assert erro.value.report.counts == {"cpf": 1}


# --------------------------------------------------------------------------
# Pergunta do usuario e auditoria
# --------------------------------------------------------------------------


def test_pergunta_com_dado_sensivel_e_bloqueada_sem_chamada(
    monkeypatch: pytest.MonkeyPatch, provedor: list[str]
) -> None:
    traces: list[dict] = []
    monkeypatch.setattr("app.pipeline.trace_interaction", lambda **kw: traces.append(kw))

    def classificador_nao_pode_rodar(_texto):
        raise AssertionError("pergunta bloqueada nao deve ser classificada")

    monkeypatch.setattr("app.nlp.inference.classify", classificador_nao_pode_rodar)

    with TestClient(app) as client:
        result = client.post(
            "/api/chat",
            json={"message": f"qual o status do PRJ-0442? meu CPF e {CPF}"},
        )

    assert result.status_code == 200
    body = result.json()
    assert body["model"] == "bloqueio-dado-sensivel"
    assert "CPF" in body["text"] and CPF not in body["text"]
    assert "security_report" not in body
    assert provedor == []

    (trace,) = traces
    assert trace["request"].message == "qual o status do PRJ-0442? meu CPF e [CPF]"
    assert trace["error_message"]
    assert trace["response"].security_report["stage"] == "mensagem"


def test_auditoria_registra_bloqueio_sem_expor_o_dado(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@example/postgres")
    cursor = FakeCursor([("conversation-id",), ("interaction-id",)])
    connection = FakeConnection(cursor)
    relatorio = SensitiveDataReport(stage="mensagem", action="bloqueado", counts={"cpf": 1})

    trace_interaction(
        request=GeminiChatRequest(message="meu CPF e [CPF]", conversation_id="c-1"),
        response=None,
        intent=None,
        entities=[],
        processing_ms=1,
        error_message="Dado sensivel bloqueado antes do provedor.",
        security_report=relatorio.audit_payload(),
        connect=_connect(connection),
    )

    eventos = [
        params for query, params in cursor.calls if "INSERT INTO public.audit_events" in query
    ]
    bloqueio = [params for params in eventos if params[1] == "sensitive_content_blocked"]
    assert len(bloqueio) == 1
    _interacao, _tipo, componente, status, _usuario, payload, _correlacao = bloqueio[0]
    assert (componente, status) == ("api", "bloqueado")
    assert json.loads(payload)["categories"] == ["cpf"]

    interacao = next(
        params for query, params in cursor.calls if "INSERT INTO public.ai_interactions" in query
    )
    assert interacao[2] == "meu CPF e [CPF]"
    assert interacao[13] == "erro"
    assert all(CPF not in str(params) for _query, params in cursor.calls)


def test_transcricao_com_dado_sensivel_tambem_e_bloqueada(
    monkeypatch: pytest.MonkeyPatch, provedor: list[str]
) -> None:
    """O audio vai ao STT antes de virar texto; a barreira vale para a transcricao."""

    from app.audio import transcription
    from test_audio_upload import AUTH_HEADER, TOKEN, _build_wav, transcricao_fixa

    traces: list[dict] = []
    monkeypatch.setattr("app.pipeline.trace_interaction", lambda **kw: traces.append(kw))
    monkeypatch.setenv("AUDIO_SIMULATED_IDENTITIES", f"{TOKEN}=usuario-teste")
    monkeypatch.setattr(
        transcription,
        "transcribe",
        transcricao_fixa(text=f"meu cpf e {CPF}", confidence=0.9, duration_seconds=1),
    )

    with TestClient(app) as client:
        result = client.post(
            "/api/audio",
            files={"audio": ("teste.wav", _build_wav(), "audio/wav")},
            headers=AUTH_HEADER,
            data={"conversation_id": "conversa", "use_intent_classifier": "false"},
        )

    assert result.status_code == 200
    assert result.json()["chat"]["model"] == "bloqueio-dado-sensivel"
    assert provedor == []
    assert traces[0]["request"].message == "meu cpf e [CPF]"
