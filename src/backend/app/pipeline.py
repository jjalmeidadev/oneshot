"""Entrada comum de texto e transcrição para classificação e resposta RAG."""

from app.gemini.client import GeminiConfigurationError, generate_chat_response
from app.gemini.schemas import GeminiChatRequest, GeminiChatResponse, GeminiUsage
from app.audio.schemas import AudioIntent


def process_message(request: GeminiChatRequest) -> GeminiChatResponse:
    intent = None
    if request.use_intent_classifier:
        try:
            from app.nlp.inference import classify
            result = classify(request.message)
        except Exception as error:
            raise GeminiConfigurationError("Classificador indisponível.") from error
        intent = AudioIntent(
            macro=result.macrointencao,
            specific=result.intencao or "",
            confidence_macro=result.confianca_macro,
            confidence_specific=result.confianca_intencao,
        )
        if not result.roteada or result.macrointencao == "FORA_DE_ESCOPO":
            return GeminiChatResponse(
                text=result.resposta_sugerida or "Posso ajudar com informações do portfólio. Reformule sua pergunta indicando um projeto ou documento.",
                model="classificador-local", latency_ms=0, usage=GeminiUsage(),
                intent=intent,
            )
    response = generate_chat_response(request)
    response.intent = intent
    return response
