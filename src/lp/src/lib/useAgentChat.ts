import { useCallback, useRef } from "react";
import type { ChatAnswer } from "@/components/chat/chat-messages";
import { sendChatMessage, sourceDownloadUrl } from "@/lib/chatApi";
import { useLiveSessionId } from "@/lib/liveSessionContext";

/**
 * O envio de uma pergunta ao agente, com as fontes de volta.
 *
 * Duas janelas de chat usam isto — a que morfa entre as seções no desktop e a
 * estática do celular — e as duas precisam do mesmo comportamento: a pergunta
 * entra na sala ao vivo, a resposta traz os documentos que a sustentam.
 */
export function useAgentChat() {
    // A sessão desta aba na sala. É ela que faz a pergunta digitada aqui
    // aparecer, no mesmo instante, no painel de quem está acompanhando.
    const sessionId = useLiveSessionId();
    // O encadeamento de turnos é do próprio Gemini: guardar o id da última
    // interação é o que faz a segunda pergunta lembrar da primeira.
    const previousInteractionId = useRef<string | null>(null);

    return useCallback(
        async (message: string): Promise<ChatAnswer> => {
            const resposta = await sendChatMessage(
                message,
                sessionId,
                previousInteractionId.current,
            );
            previousInteractionId.current = resposta.interaction_id;

            // Uma entrada por trecho recuperado, na mesma ordem em que o
            // modelo os numerou: assim "[Fonte 2]" no texto corresponde ao
            // segundo item da pasta.
            const documentos = resposta.sources.map((fonte) => ({
                name: fonte.document,
                url: sourceDownloadUrl(fonte),
                section: fonte.title,
            }));

            return {
                text: resposta.text,
                sources: documentos.length
                    ? { label: "Fontes desta resposta", documents: documentos }
                    : undefined,
            };
        },
        [sessionId],
    );
}
