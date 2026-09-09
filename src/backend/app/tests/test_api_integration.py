"""Integracao dos fluxos HTTP com o pipeline de PLN da task #126."""

import struct
from time import perf_counter

from fastapi.testclient import TestClient

from app.audio import transcription
from app.gemini.schemas import GeminiChatResponse, GeminiUsage
from app.main import app
from app.nlp.entities import Entidade
from app.nlp.inference import UNDEFINED_MACRO, Classificacao

AUTH_HEADER = {"Authorization": "Bearer token-integracao"}


def resposta_gemini() -> GeminiChatResponse:
    return GeminiChatResponse(
        text="Resposta fundamentada pelo RAG.",
        model="gemini-test",
        interaction_id="interaction-test",
        latency_ms=11,
        retrieval_ms=3,
        usage=GeminiUsage(
            input_tokens=1,
            output_tokens=1,
            thought_tokens=0,
            total_tokens=2,
        ),
        sources=[],
    )


def classificacao(
    *,
    macro: str = "CONSULTA",
    intencao: str | None = "consulta_status_projeto",
    resposta_sugerida: str | None = None,
) -> Classificacao:
    return Classificacao(
        texto="qual o status da Linha 5-Lilas",
        macrointencao=macro,
        confianca_macro=0.93,
        intencao=intencao,
        confianca_intencao=0.88 if intencao else 0.0,
        fluxo=f"fluxo generico de {macro}",
        handler=f"handler:{intencao}" if intencao else f"fluxo generico de {macro}",
        alternativas=[("consulta_status_projeto", 0.88)],
        resposta_sugerida=resposta_sugerida,
    )


def entidades_do_texto(texto: str) -> list[Entidade]:
    inicio = texto.find("Linha 5-Lilas")
    if inicio < 0:
        return []
    return [
        Entidade(
            tipo="projeto",
            valor="Linha 5-Lilas",
            texto="Linha 5-Lilas",
            inicio=inicio,
            fim=inicio + len("Linha 5-Lilas"),
        )
    ]


def transcricao_fixa(texto: str):
    async def _transcrever(*_args: object, **_kwargs: object):
        return transcription.Transcription(
            text=texto,
            confidence=0.94,
            duration_seconds=1.0,
        )

    return _transcrever


def _build_wav(duration_seconds: float = 1.0) -> bytes:
    sample_rate = 16_000
    frames = b"".join(
        struct.pack("<h", 8_000 if (index // 40) % 2 == 0 else -8_000)
        for index in range(int(sample_rate * duration_seconds))
    )
    fmt_chunk = struct.pack("<HHIIHH", 1, 1, sample_rate, sample_rate * 2, 2, 16)
    chunks = (
        b"fmt "
        + struct.pack("<I", len(fmt_chunk))
        + fmt_chunk
        + b"data"
        + struct.pack("<I", len(frames))
        + frames
    )
    return b"RIFF" + struct.pack("<I", 4 + len(chunks)) + b"WAVE" + chunks


def test_texto_valido_percorre_pln_e_retorna_resposta_estruturada(monkeypatch):
    chamadas = {"gemini": 0}
    monkeypatch.setattr("app.nlp.pipeline.classify", lambda _texto: classificacao())
    monkeypatch.setattr("app.nlp.pipeline.extract_entities", entidades_do_texto)

    def fake_generate(_request):
        chamadas["gemini"] += 1
        return resposta_gemini()

    monkeypatch.setattr("app.main.generate_chat_response", fake_generate)

    response = TestClient(app).post(
        "/api/chat",
        json={"message": "qual o status da Linha 5-Lilas"},
    )

    assert response.status_code == 200
    body = response.json()
    assert chamadas["gemini"] == 1
    assert body["intent"]["macro"] == "CONSULTA"
    assert body["intent"]["specific"] == "consulta_status_projeto"
    assert body["entities"][0]["value"] == "Linha 5-Lilas"
    assert body["pipeline_metrics"]["nlp_ms"] >= 0
    assert body["pipeline_metrics"]["route_ms"] >= body["pipeline_metrics"]["nlp_ms"]


def test_texto_fora_do_catalogo_retorna_mensagem_controlada_sem_gemini(monkeypatch):
    chamadas = {"gemini": 0}
    monkeypatch.setattr(
        "app.nlp.pipeline.classify",
        lambda _texto: classificacao(macro="FORA_DE_ESCOPO", intencao=None),
    )
    monkeypatch.setattr("app.nlp.pipeline.extract_entities", lambda _texto: [])
    monkeypatch.setattr(
        "app.main.generate_chat_response",
        lambda _request: chamadas.__setitem__("gemini", chamadas["gemini"] + 1),
    )

    response = TestClient(app).post(
        "/api/chat",
        json={"message": "qual a previsao do tempo?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert chamadas["gemini"] == 0
    assert body["intent"]["macro"] == "FORA_DE_ESCOPO"
    assert "fora do escopo" in body["text"]
    assert body["retrieval_ms"] == 0


def test_audio_valido_percorre_stt_pln_e_resposta_estruturada(monkeypatch):
    texto = "qual o status da Linha 5-Lilas"
    monkeypatch.setattr(transcription, "transcribe", transcricao_fixa(texto))
    monkeypatch.setattr("app.nlp.pipeline.classify", lambda received: classificacao())
    monkeypatch.setattr("app.nlp.pipeline.extract_entities", entidades_do_texto)

    response = TestClient(app).post(
        "/api/audio",
        files={"audio": ("pergunta.wav", _build_wav(), "audio/wav")},
        headers=AUTH_HEADER,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["pipeline_status"] == "completed"
    assert body["transcription"]["text"] == texto
    assert body["intent"]["macro"] == "CONSULTA"
    assert body["entities"][0]["value"] == "Linha 5-Lilas"
    assert set(body["pipeline_metrics"]) == {
        "validation_ms",
        "stt_ms",
        "nlp_ms",
        "total_ms",
    }
    assert body["pipeline_metrics"]["total_ms"] >= body["pipeline_metrics"]["nlp_ms"]


def test_rnf11_classification_failure_is_sanitized(monkeypatch):
    raw_provider_payload = '{"error":{"message":"segredo tecnico"}}'

    def falha_classificacao(_texto: str):
        raise RuntimeError(
            "Traceback app.nlp.classifier.ClassificadorX "
            "C:\\repo\\app\\nlp\\classifier.py "
            + raw_provider_payload
        )

    monkeypatch.setattr("app.nlp.pipeline.classify", falha_classificacao)

    response = TestClient(app).post(
        "/api/chat",
        json={"message": "qual o status da Linha 5-Lilas"},
    )

    assert response.status_code == 200
    serialized = response.text
    assert "Traceback" not in serialized
    assert "app.nlp" not in serialized
    assert "ClassificadorX" not in serialized
    assert "classifier.py" not in serialized
    assert raw_provider_payload not in serialized
    assert response.json()["intent"]["macro"] == UNDEFINED_MACRO


def test_rnf05_smoke_records_complete_flow_time(monkeypatch):
    monkeypatch.setattr("app.nlp.pipeline.classify", lambda _texto: classificacao())
    monkeypatch.setattr("app.nlp.pipeline.extract_entities", entidades_do_texto)
    monkeypatch.setattr("app.main.generate_chat_response", lambda _request: resposta_gemini())

    started_at = perf_counter()
    response = TestClient(app).post(
        "/api/chat",
        json={"message": "qual o status da Linha 5-Lilas"},
    )
    elapsed_ms = round((perf_counter() - started_at) * 1000)

    assert response.status_code == 200
    route_ms = response.json()["pipeline_metrics"]["route_ms"]
    assert route_ms >= 0
    assert elapsed_ms < 10_000
