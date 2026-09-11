import { HAS_LIVE_BACKEND, liveApiUrl } from "@/lib/liveBackend";

/** Uma fonte devolvida pelo backend, já com o link do documento original. */
export interface ChatApiSource {
    id: string;
    title: string;
    document: string;
    download_url: string | null;
    excerpt: string | null;
    score: number | null;
}

export interface ChatApiResponse {
    text: string;
    model: string;
    interaction_id: string | null;
    latency_ms: number;
    sources: ChatApiSource[];
}

/** Erro com o texto que o backend explicou, para a interface poder mostrá-lo. */
export class ChatApiError extends Error {
    readonly status: number;

    constructor(message: string, status: number) {
        super(message);
        this.name = "ChatApiError";
        this.status = status;
    }
}

export const CHAT_UNAVAILABLE =
    "O assistente ainda não está disponível nesta página.";

/**
 * Pergunta ao agente.
 *
 * `sessionId` é o que liga a pergunta ao painel ao vivo: com ele, quem estiver
 * acompanhando vê a pergunta no instante em que ela é enviada. Sem ele a
 * resposta vem igual, só não aparece para os observadores.
 */
export async function sendChatMessage(
    message: string,
    sessionId: string | null,
    previousInteractionId: string | null,
    signal?: AbortSignal,
): Promise<ChatApiResponse> {
    if (!HAS_LIVE_BACKEND) {
        throw new ChatApiError(CHAT_UNAVAILABLE, 0);
    }

    const response = await fetch(liveApiUrl("/api/chat"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            message,
            session_id: sessionId,
            previous_interaction_id: previousInteractionId,
        }),
        signal,
    });

    if (!response.ok) {
        // O backend explica o motivo em `detail` — inclusive o 503 de quando o
        // modelo ainda não está configurado. Mostrar isso é melhor do que um
        // "erro" genérico que não diz o que fazer.
        const corpo = (await response.json().catch(() => null)) as
            | { detail?: string }
            | null;
        throw new ChatApiError(
            corpo?.detail ?? "Não consegui falar com o assistente agora.",
            response.status,
        );
    }

    return (await response.json()) as ChatApiResponse;
}

/** Endereço absoluto de um documento-fonte, para o link de download. */
export function sourceDownloadUrl(source: ChatApiSource): string | undefined {
    return source.download_url ? liveApiUrl(source.download_url) : undefined;
}
