import { useEffect, useState } from "react";
import {
    HAS_LIVE_BACKEND,
    LIVE_SESSIONS_PATH,
    liveApiUrl,
    liveWebsocketUrl,
} from "@/lib/liveBackend";

/** Disparado quando alguém passa a (ou deixa de) acompanhar uma sessão. */
export const LIVE_FOLLOW_EVENT = "oneshot:live-follow";

export interface LiveMessage {
    id: string;
    role: "user" | "assistant";
    content: string;
    at: number;
}

export interface LiveSession {
    id: string;
    name: string;
    /** Cor do participante, no espírito dos cursores do Miro. */
    color: string;
    status: "typing" | "thinking" | "idle";
    lastSeen: number;
    messages: LiveMessage[];
}

/** Intervalo do polling — usado só enquanto o WebSocket não estiver de pé. */
const POLL_INTERVAL = 2500;
/** Espera antes de tentar reabrir o canal que caiu. */
const RECONNECT_DELAY = 3000;
/** `?ao-vivo=1` (ou `?ao-vivo=3`) liga a simulação e define quantas sessões. */
const SIMULATION_PARAM = "ao-vivo";

const COLORS = ["#818cf8", "#34d399", "#fbbf24", "#f472b6", "#38bdf8"];

const SIMULATED_TURNS: Array<[string, string]> = [
    [
        "Qual o status do Portfólio XPTO?",
        "Em andamento. A última atualização do cronograma é de agosto e está anexada ao TAP.",
    ],
    [
        "Quais documentos sustentam esse status?",
        "O TAP, o cronograma físico-financeiro (rev. ago/2026) e a nota técnica 12/2026.",
    ],
    [
        "Tem algum marco atrasado?",
        "Dois marcos da fase de execução estão com data revisada; os demais seguem no prazo.",
    ],
    [
        "Consigo ver isso no Teams?",
        "A integração com o Teams está em preparação — hoje a consulta é por aqui.",
    ],
];

function simulatedSessions(count: number): LiveSession[] {
    const now = Date.now();
    return Array.from({ length: count }, (_, index) => ({
        id: `sim-${index}`,
        name: `Convidado ${index + 1}`,
        color: COLORS[index % COLORS.length],
        status: "idle" as const,
        lastSeen: now,
        messages: [],
    }));
}

/**
 * Quem está testando o assistente agora.
 *
 * Uma única porta de entrada para a interface, seja qual for a origem do
 * dado: o backend de presença quando há um configurado, o simulador de
 * `?ao-vivo=N` quando não há. Sem os dois, devolve lista vazia — e a página
 * se comporta exatamente como antes de o backend existir.
 *
 * Este hook só *observa*. Quem coloca o visitante na sala é `useLiveSession`.
 */
export function useLivePresence(): { sessions: LiveSession[] } {
    const [sessions, setSessions] = useState<LiveSession[]>([]);

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const simulationRaw = params.get(SIMULATION_PARAM);

        // --- Caminho real: WebSocket, com polling como rede de segurança -
        //
        // O polling sobe primeiro: ele garante conteúdo já na primeira
        // pintura e é para onde a interface cai se o canal não abrir. Assim
        // que o WebSocket conecta, o polling para; se o canal cair, o polling
        // volta e uma nova tentativa de conexão é agendada.
        if (HAS_LIVE_BACKEND) {
            let cancelled = false;
            let socket: WebSocket | null = null;
            let pollTimer: number | null = null;
            let reconnectTimer: number | null = null;

            const apply = (incoming: LiveSession[] | undefined) => {
                if (!cancelled) setSessions(incoming ?? []);
            };

            const poll = async () => {
                try {
                    const response = await fetch(liveApiUrl(LIVE_SESSIONS_PATH), {
                        cache: "no-store",
                    });
                    const data = (await response.json()) as { sessions?: LiveSession[] };
                    apply(data.sessions);
                } catch {
                    // Uma falha de rede não deve derrubar a página: mantém o
                    // último estado conhecido e tenta de novo no próximo ciclo.
                }
            };

            const startPolling = () => {
                if (cancelled || pollTimer !== null) return;
                void poll();
                pollTimer = window.setInterval(poll, POLL_INTERVAL);
            };

            const stopPolling = () => {
                if (pollTimer === null) return;
                window.clearInterval(pollTimer);
                pollTimer = null;
            };

            const connect = () => {
                if (cancelled) return;

                try {
                    socket = new WebSocket(liveWebsocketUrl());
                } catch {
                    startPolling();
                    return;
                }

                socket.onopen = () => stopPolling();

                socket.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data as string) as {
                            sessions?: LiveSession[];
                        };
                        apply(data.sessions);
                    } catch {
                        // Mensagem malformada não é motivo para limpar a sala.
                    }
                };

                // `onerror` é sempre seguido de `onclose`, então a reconexão
                // fica em um lugar só.
                socket.onclose = () => {
                    socket = null;
                    if (cancelled) return;
                    startPolling();
                    reconnectTimer = window.setTimeout(connect, RECONNECT_DELAY);
                };
            };

            startPolling();
            connect();

            return () => {
                cancelled = true;
                stopPolling();
                if (reconnectTimer !== null) window.clearTimeout(reconnectTimer);
                if (socket) {
                    socket.onclose = null;
                    socket.close();
                }
            };
        }

        // --- Modo simulado: valida a interface antes do backend ---------
        if (simulationRaw === null) return;
        const total = Math.min(4, Math.max(1, Number(simulationRaw) || 1));

        const timers: number[] = [];
        const pool = simulatedSessions(total);
        let turn = 0;

        // As sessões entram espaçadas, para dar para ver o layout se
        // reorganizando ao vivo — que é o efeito pretendido na apresentação.
        pool.forEach((session, index) => {
            timers.push(
                window.setTimeout(
                    () => setSessions((current) => [...current, session]),
                    2500 + index * 9000,
                ),
            );
        });

        const tick = window.setInterval(() => {
            setSessions((current) => {
                if (current.length === 0) return current;
                const targetIndex = turn % current.length;
                const [question, answer] = SIMULATED_TURNS[turn % SIMULATED_TURNS.length];
                turn += 1;
                const now = Date.now();

                return current.map((session, index) => {
                    if (index !== targetIndex) return { ...session, status: "idle" as const };
                    return {
                        ...session,
                        status: "typing" as const,
                        lastSeen: now,
                        messages: [
                            ...session.messages,
                            { id: `${session.id}-u-${now}`, role: "user" as const, content: question, at: now },
                            {
                                id: `${session.id}-a-${now}`,
                                role: "assistant" as const,
                                content: answer,
                                at: now + 1200,
                            },
                        ],
                    };
                });
            });
        }, 7000);
        timers.push(tick);

        return () => timers.forEach((timer) => window.clearTimeout(timer));
    }, []);

    return { sessions };
}
