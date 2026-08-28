export type GeminiUsage = {
  input_tokens: number;
  output_tokens: number;
  thought_tokens: number;
  total_tokens: number;
};

export type GeminiSource = {
  id: string;
  title: string;
  list_name: string;
  web_url: string;
  last_modified: string;
  score: number;
};

export type GeminiChatResponse = {
  text: string;
  model: string;
  interaction_id: string | null;
  latency_ms: number;
  retrieval_ms: number;
  usage: GeminiUsage;
  sources: GeminiSource[];
};

export async function sendGeminiMessage(
  message: string,
  previousInteractionId: string | null,
  signal: AbortSignal,
): Promise<GeminiChatResponse> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      previous_interaction_id: previousInteractionId,
    }),
    signal,
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as {
      detail?: string;
    } | null;
    throw new Error(body?.detail ?? 'Nao foi possivel obter uma resposta do Gemini.');
  }

  return (await response.json()) as GeminiChatResponse;
}
