/**
 * Rota de texto — `POST /api/chat` (`app/main.py`).
 *
 * O backend encadeia o contexto pelo `previous_interaction_id`: cada resposta
 * traz um `interaction_id` que deve voltar na proxima mensagem **da mesma
 * conversa**. Por isso a store guarda esse identificador por conversa e o
 * restaura ao trocar de conversa na barra lateral.
 */

import { parseError, requestJson } from './client';
import type { ChatRequest, ChatResponse, HealthResponse } from './schemas';

export type SendMessageInput = {
  message: string;
  previousInteractionId: string | null;
  /** Habilita a classificação local antes da resposta RAG. */
  useIntentClassifier: boolean;
  signal?: AbortSignal;
};

export async function sendChatMessage(input: SendMessageInput): Promise<ChatResponse> {
  const body: ChatRequest = {
    message: input.message,
    use_intent_classifier: input.useIntentClassifier,
    previous_interaction_id: input.previousInteractionId,
  };

  return requestJson<ChatResponse>('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal: input.signal,
  });
}

/**
 * `GET /health`. Usado pelo indicador de conexao do cabecalho.
 *
 * A rota fica fora do prefixo `/api`, entao `vite.config.ts` encaminha
 * `/health` para o backend junto com `/api`.
 */
export async function checkHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const response = await fetch('/health', { signal });
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as HealthResponse;
}
