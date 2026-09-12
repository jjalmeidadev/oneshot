import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { X } from "lucide-react";
import { LIVE_FOLLOW_EVENT, type LiveSession } from "@/lib/useLivePresence";
import { cn } from "@/lib/utils";
import { GLASS } from "@/lib/styles";

export interface LivePresenceCardProps {
    sessions: LiveSession[];
    /**
     * Sessão desta aba, quando ela também está na sala. Serve só para a
     * pessoa se reconhecer na lista — com vários dispositivos abertos, sem
     * isso não dá para saber qual dos pontos é você.
     */
    selfId?: string | null;
}

function statusLabel(session: LiveSession) {
    if (session.status === "typing") return "digitando…";
    if (session.status === "thinking") return "aguardando resposta…";
    const seconds = Math.max(0, Math.round((Date.now() - session.lastSeen) / 1000));
    if (seconds < 5) return "agora mesmo";
    if (seconds < 60) return `há ${seconds}s`;
    return `há ${Math.round(seconds / 60)}min`;
}

/**
 * O painel de quem está testando o assistente ao vivo.
 *
 * Recolhido, ocupa 1/3 da última seção ao lado da janela de chat e lista
 * quem está na sala. Ao clicar numa pessoa, abre em tela cheia e passa a
 * acompanhar a conversa dela em tempo real — o mesmo gesto de "seguir" um
 * participante no Miro. É somente leitura: quem observa não interfere.
 */
export default function LivePresenceCard({ sessions, selfId }: LivePresenceCardProps) {
    const [followingId, setFollowingId] = useState<string | null>(null);
    const feedRef = useRef<HTMLDivElement>(null);

    const following = sessions.find((session) => session.id === followingId) ?? null;

    // Some sozinho se a pessoa que estava sendo acompanhada sair da sala.
    useEffect(() => {
        if (followingId && !following) setFollowingId(null);
    }, [followingId, following]);

    // Avisa a página: enquanto se acompanha alguém, a janela de chat sai da
    // frente para não competir com a conversa que está sendo observada.
    useEffect(() => {
        const active = followingId !== null;
        window.dispatchEvent(new CustomEvent(LIVE_FOLLOW_EVENT, { detail: { active } }));
        return () => {
            if (active) {
                window.dispatchEvent(
                    new CustomEvent(LIVE_FOLLOW_EVENT, { detail: { active: false } }),
                );
            }
        };
    }, [followingId]);

    // Acompanha o fim da conversa conforme as mensagens chegam.
    useEffect(() => {
        const feed = feedRef.current;
        if (!feed) return;
        feed.scrollTo({ top: feed.scrollHeight, behavior: "smooth" });
    }, [following?.messages.length]);

    return (
        <>
            <motion.aside
                initial={{ opacity: 0, x: 40 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 40 }}
                transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                className={cn(GLASS, "flex h-full w-full flex-col overflow-hidden")}
            >
                <div className="flex items-center gap-2 border-b border-white/10 px-4 py-3">
                    <span className="relative flex size-2.5">
                        <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-60" />
                        <span className="relative inline-flex size-2.5 rounded-full bg-emerald-400" />
                    </span>
                    <span className="text-xs font-medium uppercase tracking-widest text-white/70">
                        Ao vivo
                    </span>
                    <span className="ml-auto text-xs text-white/40">
                        {sessions.length} {sessions.length === 1 ? "pessoa" : "pessoas"}
                    </span>
                </div>

                <div className="flex min-h-0 flex-1 flex-col gap-2 overflow-y-auto p-3">
                    {sessions.map((session) => {
                        const last = session.messages[session.messages.length - 1];
                        return (
                            <button
                                key={session.id}
                                type="button"
                                onClick={() => setFollowingId(session.id)}
                                className="flex w-full cursor-pointer flex-col gap-1 rounded-xl border border-white/5 bg-white/5 p-3 text-left transition-colors hover:border-white/20 hover:bg-white/10"
                            >
                                <span className="flex items-center gap-2">
                                    <span
                                        className="size-2.5 shrink-0 rounded-full"
                                        style={{ backgroundColor: session.color }}
                                    />
                                    <span className="text-sm font-medium text-white">
                                        {session.name}
                                    </span>
                                    {session.id === selfId && (
                                        <span className="rounded-full bg-white/10 px-2 py-0.5 text-[10px] font-normal uppercase tracking-widest text-white/50">
                                            você
                                        </span>
                                    )}
                                    <span className="ml-auto text-[11px] font-normal text-white/40">
                                        {statusLabel(session)}
                                    </span>
                                </span>
                                {last && (
                                    <span className="line-clamp-2 text-xs font-normal leading-relaxed text-white/50">
                                        {last.role === "user" ? "Perguntou: " : "Resposta: "}
                                        {last.content}
                                    </span>
                                )}
                            </button>
                        );
                    })}
                </div>

                <div className="border-t border-white/10 px-4 py-3 text-[11px] font-normal text-white/40">
                    Clique em alguém para acompanhar a conversa
                </div>
            </motion.aside>

            <AnimatePresence>
                {following && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.25 }}
                        className="fixed inset-0 z-40 flex items-center justify-center bg-neutral-950/90 p-6 backdrop-blur-md md:p-12"
                    >
                        <motion.section
                            initial={{ scale: 0.94, y: 20 }}
                            animate={{ scale: 1, y: 0 }}
                            exit={{ scale: 0.94, y: 20 }}
                            transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
                            className={cn(GLASS, "flex h-full w-full max-w-4xl flex-col overflow-hidden")}
                        >
                            <header className="flex items-center gap-3 border-b border-white/10 px-5 py-4">
                                <span
                                    className="size-3 rounded-full"
                                    style={{ backgroundColor: following.color }}
                                />
                                <span className="text-base font-medium text-white">
                                    {following.name}
                                </span>
                                <span className="rounded-full bg-white/10 px-2 py-0.5 text-[11px] font-normal text-white/60">
                                    acompanhando
                                </span>
                                <span className="text-xs font-normal text-white/40">
                                    {statusLabel(following)}
                                </span>
                                <button
                                    type="button"
                                    onClick={() => setFollowingId(null)}
                                    aria-label="Parar de acompanhar"
                                    className="ml-auto flex size-9 cursor-pointer items-center justify-center rounded-full border border-white/10 bg-white/5 text-white/60 transition-colors hover:bg-white/10 hover:text-white"
                                >
                                    <X className="size-4" />
                                </button>
                            </header>

                            <div ref={feedRef} className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto p-5">
                                {following.messages.length === 0 && (
                                    <p className="m-auto text-sm font-normal text-white/40">
                                        Ainda sem perguntas nesta sessão.
                                    </p>
                                )}
                                {following.messages.map((message) => (
                                    <div
                                        key={message.id}
                                        className={cn(
                                            "flex w-full",
                                            message.role === "user" ? "justify-end" : "justify-start",
                                        )}
                                    >
                                        <div
                                            className={cn(
                                                "w-fit max-w-[80%] rounded-2xl px-4 py-2.5 text-sm font-normal leading-relaxed",
                                                message.role === "user"
                                                    ? "rounded-tr-md bg-gradient-to-r from-indigo-600 to-violet-600 text-white"
                                                    : "rounded-tl-md border border-white/10 bg-zinc-800/90 text-zinc-100",
                                            )}
                                        >
                                            {message.content}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <footer className="border-t border-white/10 px-5 py-3 text-[11px] font-normal text-white/40">
                                Somente leitura — acompanhar não interfere na conversa
                            </footer>
                        </motion.section>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
