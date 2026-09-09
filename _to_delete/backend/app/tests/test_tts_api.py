from app.main import analyze_tts, create_tts_audio
from app.tts.schemas import TTSRequest


def test_create_tts_audio_returns_wav() -> None:
    response = create_tts_audio(TTSRequest(text="Teste de voz."))

    assert response.status_code == 200
    assert response.media_type == "audio/wav"
    assert response.body.startswith(b"RIFF")


def test_analyze_tts_returns_pipeline_details() -> None:
    body = analyze_tts(TTSRequest(text="TAP-01 em 75%."))

    assert body["normalized_text"] == "tap zero um em setenta e cinco por cento"
    assert body["duration_seconds"] > 0
    assert body["sample_count"] > 0
    assert len(body["syllables"]) > 0
