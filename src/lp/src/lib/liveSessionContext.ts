import { createContext, useContext } from "react";

/**
 * A sessão desta aba na sala ao vivo, compartilhada pela página inteira.
 *
 * Duas partes precisam do mesmo id: o painel de presença, para marcar qual
 * das pessoas é você, e a janela de chat, para que a pergunta enviada apareça
 * na sala. Se cada uma chamasse `useLiveSession` por conta própria, a página
 * entraria duas vezes na sala e apareceria como duas pessoas.
 */
export const LiveSessionContext = createContext<string | null>(null);

/** Id da sessão desta aba, ou `null` sem backend configurado. */
export function useLiveSessionId(): string | null {
    return useContext(LiveSessionContext);
}
