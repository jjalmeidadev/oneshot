from fastapi.testclient import TestClient

from app.gemini.schemas import GeminiChatResponse, GeminiUsage
from app.main import app
from app.nlp.entities import Entidade
from app.nlp.inference import LIMITATION_ANSWER, UNDEFINED_MACRO, Classificacao
from app.nlp.pipeline import NlpPipelineResult, OUT_OF_SCOPE_ANSWER


client = TestClient(app)


def classificacao(
    *,
    macro: str = "CONSULTA",
    intencao: str | None = "consulta_status_projeto",
    resposta_sugerida: str | None = None,
) -> Classificacao:
    return Classificacao(
        texto="status da Linha 5-Lilas",
        macrointencao=macro,
        confianca_macro=0.91,
        intencao=intencao,
        confianca_intencao=0.82 if intencao else 0.41,
        fluxo=f"fluxo generico de {macro}",
        handler=f"handler:{intencao}" if intencao else f"fluxo generico de {macro}",
        alternativas=[("consulta_status_projeto", 0.82)],
        resposta_sugerida=resposta_sugerida,
    )


def resposta_gemini() -> GeminiChatResponse:
    return GeminiChatResponse(
        text="A Linha 5-Lilas esta em acompanhamento.",
        model="gemini-test",
        interaction_id="interaction-1",
        latency_ms=12,
        retrieval_ms=4,
        usage=GeminiUsage(total_tokens=9),
        sources=[],
    )


def resultado_pipeline(
    *,
    macro: str = "CONSULTA",
    intencao: str | None = "consulta_status_projeto",
    resposta_controlada: str | None = None,
    entidades: list[Entidade] | None = None,
) -> NlpPipelineResult:
    return NlpPipelineResult(
        classification=classificacao(
            macro=macro,
            intencao=intencao,
            resposta_sugerida=resposta_controlada,
        ),
        entities=entidades or [],
        nlp_ms=0,
        controlled_answer=resposta_controlada,
    )


def test_texto_valido_retorna_intencao_e_entidades(
    monkeypatch,
) -> None:
    chamadas = {"gemini": 0}

    def fake_generate(_request):
        chamadas["gemini"] += 1
        return resposta_gemini()

    monkeypatch.setattr(
        "app.main.process_text_pipeline",
        lambda _texto: resultado_pipeline(
            entidades=[
                Entidade(
                    tipo="projeto",
                    valor="Linha 5-Lilas",
                    texto="Linha 5-Lilas",
                    inicio=10,
                    fim=23,
                )
            ]
        ),
    )
    monkeypatch.setattr("app.main.generate_chat_response", fake_generate)

    response = client.post("/api/chat", json={"message": "status da Linha 5-Lilas"})

    assert response.status_code == 200
    body = response.json()
    assert chamadas["gemini"] == 1
    assert body["text"] == "A Linha 5-Lilas esta em acompanhamento."
    assert body["intent"]["macro"] == "CONSULTA"
    assert body["intent"]["specific"] == "consulta_status_projeto"
    assert body["entities"] == [
        {
            "type": "projeto",
            "value": "Linha 5-Lilas",
            "text": "Linha 5-Lilas",
            "start": 10,
            "end": 23,
            "types": ["projeto"],
            "ambiguous": False,
        }
    ]
    assert body["latency_ms"] == 12
    assert body["retrieval_ms"] == 4


def test_texto_fora_do_catalogo_nao_chama_gemini(monkeypatch) -> None:
    chamadas = {"gemini": 0}

    def fake_generate(_request):
        chamadas["gemini"] += 1
        return resposta_gemini()

    monkeypatch.setattr(
        "app.main.process_text_pipeline",
        lambda _texto: resultado_pipeline(
            macro="FORA_DE_ESCOPO",
            intencao=None,
            resposta_controlada=OUT_OF_SCOPE_ANSWER,
        ),
    )
    monkeypatch.setattr("app.main.generate_chat_response", fake_generate)

    response = client.post("/api/chat", json={"message": "bom dia, tudo certo?"})

    assert response.status_code == 200
    body = response.json()
    assert chamadas["gemini"] == 0
    assert body["model"] == "pln-router"
    assert body["intent"]["macro"] == "FORA_DE_ESCOPO"
    assert "fora do escopo" in body["text"]
    assert body["retrieval_ms"] == 0


def test_baixa_confianca_retorna_mensagem_controlada(monkeypatch) -> None:
    chamadas = {"gemini": 0}

    def fake_generate(_request):
        chamadas["gemini"] += 1
        return resposta_gemini()

    monkeypatch.setattr(
        "app.main.process_text_pipeline",
        lambda _texto: resultado_pipeline(
            macro=UNDEFINED_MACRO,
            intencao=None,
            resposta_controlada=LIMITATION_ANSWER,
        ),
    )
    monkeypatch.setattr("app.main.generate_chat_response", fake_generate)

    response = client.post("/api/chat", json={"message": "preciso disso ai"})

    assert response.status_code == 200
    body = response.json()
    assert chamadas["gemini"] == 0
    assert body["intent"]["macro"] == UNDEFINED_MACRO
    assert body["text"] == LIMITATION_ANSWER
    assert body["latency_ms"] == 0


def test_resposta_inclui_tempo_do_pipeline(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.main.process_text_pipeline",
        lambda _texto: resultado_pipeline(),
    )
    monkeypatch.setattr("app.main.generate_chat_response", lambda _request: resposta_gemini())

    response = client.post("/api/chat", json={"message": "status da Linha 5-Lilas"})

    assert response.status_code == 200
    metrics = response.json()["pipeline_metrics"]
    assert set(metrics) == {"nlp_ms", "route_ms"}
    assert isinstance(metrics["nlp_ms"], int)
    assert isinstance(metrics["route_ms"], int)
    assert metrics["route_ms"] >= metrics["nlp_ms"]


def test_erro_controlado_nao_vaza_detalhe_tecnico(monkeypatch) -> None:
    chamadas = {"gemini": 0}

    def fake_classify(_texto):
        raise RuntimeError(
            "Falha em C:\\repo\\app\\nlp\\classifier.py na classe ClassificadorX"
        )

    def fake_generate(_request):
        chamadas["gemini"] += 1
        return resposta_gemini()

    monkeypatch.setattr("app.nlp.pipeline.classify", fake_classify)
    monkeypatch.setattr("app.main.generate_chat_response", fake_generate)

    response = client.post("/api/chat", json={"message": "status da Linha 5-Lilas"})

    assert response.status_code == 200
    body_text = response.json()["text"]
    assert chamadas["gemini"] == 0
    assert "classifier.py" not in body_text
    assert "ClassificadorX" not in body_text
    assert "C:\\repo" not in body_text
    assert "stack" not in body_text.lower()
