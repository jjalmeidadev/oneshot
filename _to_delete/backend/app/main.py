from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from app.tts.schemas import TTSAnalysis, TTSRequest
from app.tts.synthesizer import synthesize_text, synthesize_wav_bytes

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

app = FastAPI(
    title="API de IA do Metro",
    description="Sintese de fala (TTS) para as respostas do agente do Metro.",
    version="0.1.0",
)

# Libera o frontend (Vite, outra origem/porta) a consumir a API durante o
# desenvolvimento. Em producao, restringir `allow_origins` ao(s) dominio(s)
# reais do frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/tts")
def create_tts_audio(request: TTSRequest) -> Response:
    """Sintetiza o texto da resposta do agente e devolve o audio em WAV.

    Pensado para o frontend tocar a resposta diretamente (ex.: elemento
    <audio> ou Web Audio API), por isso o Content-Disposition e `inline`
    em vez de `attachment`.
    """
    try:
        wav_bytes, _ = synthesize_wav_bytes(
            request.text,
            sample_rate=request.sample_rate,
            amplitude=request.amplitude,
        )
    except Exception as error:
        raise HTTPException(
            status_code=422,
            detail=f"Falha ao sintetizar audio: {error}",
        ) from error

    return Response(
        content=wav_bytes,
        media_type="audio/wav",
        headers={"Content-Disposition": 'inline; filename="tts-output.wav"'},
    )


@app.post("/tts/analyze", response_model=TTSAnalysis)
def analyze_tts(request: TTSRequest) -> dict:
    """Roda o mesmo pipeline de sintese, mas devolve metricas em JSON
    (texto normalizado, silabas, duracao etc.) em vez do audio bruto.
    Util para depurar o pipeline sem precisar ouvir o WAV.
    """
    try:
        _, metrics = synthesize_text(
            request.text,
            sample_rate=request.sample_rate,
            amplitude=request.amplitude,
        )
    except Exception as error:
        raise HTTPException(
            status_code=422,
            detail=f"Falha ao sintetizar audio: {error}",
        ) from error

    return metrics


# NOTE: os endpoints de chat (Gemini, /api/chat) e RAG existiam em uma
# branch anterior (feat/frontend-inicial), mas o codigo-fonte
# (app/gemini, app/rag) ainda nao foi trazido para a branch
# feature/tts-api. O fluxo completo de voz planejado para o produto e:
#
#   audio do usuario -> STT (Azure AI Speech, ja documentado em
#   docs/Projeto.md secao 8.6) -> texto -> pipeline de PLN / chat ->
#   texto de resposta do agente -> este endpoint /tts -> audio de volta
#   para o usuario.
#
# Quando o chat for reintegrado aqui, o endpoint /api/chat pode chamar
# `synthesize_wav_bytes` diretamente para devolver texto + audio numa
# unica resposta, ou o frontend pode encadear /api/chat -> /tts.
