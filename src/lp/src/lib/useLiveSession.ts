import { useEffect, useRef, useState } from "react";
import { HAS_LIVE_BACKEND, LIVE_SESSIONS_PATH, liveApiUrl } from "@/lib/liveBackend";

/** Ritmo do sinal de vida. O TTL do servidor é 90s, então sobra folga. */
const HEARTBEAT_INTERVAL = 30000;

/**
 * Coloca este visitante na sala ao vivo.
 *
 * É a contraparte de `useLivePresence`: aquele *observa* a sala, este *entra*
 * nela. Toda aba que abre a landing page com backend configurado passa a
 * aparecer no painel dos outros — que é o efeito de presença pretendido.
 *
 * Devolve o id da própria sessão, para a interface conseguir se reconhecer no
 * meio da lista. Sem backend configurado, não faz nada e devolve `null`.
 *
 * O que exige cuidado aqui é o celular: quando a tela bloqueia, o navegador
 * congela os temporizadores, o sinal de vida para e o servidor tira a sessão
 * da sala. Por isso o `heartbeat` que recebe 404 entra de novo em vez de
 * desistir, e voltar para a aba dispara um sinal imediato.
 */
export function useLiveSession(): { sessionId: string | null } {
    const [sessionId, setSessionId] = useState<string | null>(null);
    // O id também vive numa ref: os temporizadores precisam do valor atual
    // sem que renderizar de novo os recrie.
    const idRef = useRef<string | null>(null);

    useEffect(() => {
        if (!HAS_LIVE_BACKEND) return;

        let cancelled = false;
        let heartbeat: number | null = null;

        const forget = (id: string) => {
            // `keepalive` para o pedido sobreviver ao fechamento da aba.
            void fetch(liveApiUrl(`${LIVE_SESSIONS_PATH}/${id}`), {
                method: "DELETE",
                keepalive: true,
            }).catch(() => {
                // Se não der, o TTL do servidor limpa em até 90s.
            });
        };

        const join = async () => {
            try {
                const response = await fetch(liveApiUrl(LIVE_SESSIONS_PATH), {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({}),
                });
                if (!response.ok) return;

                const session = (await response.json()) as { id: string };

                // O efeito pode ter sido desmontado enquanto o pedido estava
                // no ar — em desenvolvimento o StrictMode monta duas vezes de
                // propósito. Sem isto, sobraria uma sessão órfã na sala.
                if (cancelled) {
                    forget(session.id);
                    return;
                }

                idRef.current = session.id;
                setSessionId(session.id);
            } catch {
                // Backend fora do ar não pode quebrar a página: ela
                // simplesmente não aparece na sala.
            }
        };

        const beat = async () => {
            const id = idRef.current;
            if (id === null) return;
            try {
                const response = await fetch(
                    liveApiUrl(`${LIVE_SESSIONS_PATH}/${id}/heartbeat`),
                    {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({}),
                    },
                );
                // 404: a sessão expirou (aba dormindo). Entrar de novo é o
                // certo — some da sala e volta, em vez de ficar invisível.
                if (response.status === 404 && !cancelled) {
                    idRef.current = null;
                    setSessionId(null);
                    await join();
                }
            } catch {
                // Rede instável: o próximo ciclo tenta de novo.
            }
        };

        const onVisible = () => {
            if (document.visibilityState === "visible") void beat();
        };

        const onPageHide = () => {
            const id = idRef.current;
            if (id !== null) forget(id);
        };

        void join();
        heartbeat = window.setInterval(() => void beat(), HEARTBEAT_INTERVAL);
        document.addEventListener("visibilitychange", onVisible);
        window.addEventListener("pagehide", onPageHide);

        return () => {
            cancelled = true;
            if (heartbeat !== null) window.clearInterval(heartbeat);
            document.removeEventListener("visibilitychange", onVisible);
            window.removeEventListener("pagehide", onPageHide);

            const id = idRef.current;
            idRef.current = null;
            if (id !== null) forget(id);
        };
    }, []);

    return { sessionId };
}
