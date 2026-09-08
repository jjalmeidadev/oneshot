import { useEffect, useState } from "react";

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

/**
 * Endereço do backend de presença (lp/src/rag/backend), a ser preenchido
 * quando ele existir. Enquanto estiver vazio, a interface roda em modo
 * simulado — o suficiente para validar layout e interação.
 */
const PRESENCE_ENDPOINT = "";
/** Intervalo do polling, quando houver endpoint. */
const POLL_INTERVAL = 2500;
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
 * Uma única porta de entrada para a interface: hoje ela é alimentada por um
 * simulador, e passará a ser alimentada pelo polling do backend sem que os
 * componentes precisem mudar. Sem endpoint e sem o parâmetro de simulação,
 * devolve lista vazia — e a página se comporta exatamente como antes.
 */
export function useLivePresence(): { sessions: LiveSession[] } {
    const [sessions, setSessions] = useState<LiveSession[]>([]);

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const simulationRaw = params.get(SIMULATION_PARAM);

        // --- Caminho real: polling do backend de presença ---------------
        if (PRESENCE_ENDPOINT) {
            let cancelled = false;

            const poll = async () => {
                try {
                    const response = await fetch(PRESENCE_ENDPOINT, { cache: "no-store" });
                    const data = (await response.json()) as { sessions?: LiveSession[] };
                    if (!cancelled) setSessions(data.sessions ?? []);
                } catch {
                    // Uma falha de rede não deve derrubar a página: mantém o
                    // último estado conhecido e tenta de novo no próximo ciclo.
                }
            };

            void poll();
            const timer = window.setInterval(poll, POLL_INTERVAL);
            return () => {
                cancelled = true;
                window.clearInterval(timer);
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
