import ChatMessages from "@/components/chat/chat-messages";
import { SOURCE_MESSAGES } from "@/components/chat/messages";
import JoinQr from "@/components/live/join-qr";
import LivePresenceCard from "@/components/live/live-presence-card";
import { HAS_LIVE_BACKEND } from "@/lib/liveBackend";
import { useLivePresence } from "@/lib/useLivePresence";
import { useLiveSessionId } from "@/lib/liveSessionContext";
import { useAgentChat } from "@/lib/useAgentChat";
import { useCoarsePointer } from "@/lib/useCoarsePointer";
import { cn } from "@/lib/utils";

// A seção "Experimente" tem duas formas.
//
// No desktop ela é o fim da coreografia: a janela de chat (FloatingChat)
// chega morfando da seção anterior, a seção é muito mais alta que a tela e
// fica presa no topo, e a coluna da direita traz o QR e quem está na sala.
//
// No celular ela é a única seção de chat que existe, e é estática: a conversa
// já aparece inteira, o campo está sempre clicável e a página rola normal.
// A coreografia foi calibrada para tela larga e roda do mouse; no telefone ela
// prendia a rolagem e empurrava a tela ao focar o campo.
export default function TrySection() {
    const mobile = useCoarsePointer();
    const { sessions } = useLivePresence();
    // A entrada na sala acontece no provedor, no topo da página; aqui só se
    // lê o id. O celular continua entrando — é isso que faz a pergunta dele
    // aparecer na tela projetada — ele apenas não exibe o painel.
    const sessionId = useLiveSessionId();
    const enviarPergunta = useAgentChat();

    const live = sessions.some((session) => session.id !== sessionId);
    const showQr = HAS_LIVE_BACKEND && !mobile;
    const showAside = !mobile && (showQr || live);

    return (
        <section
            className={cn("relative w-full", mobile ? "min-h-screen" : "min-h-[240vh]")}
        >
            <div
                data-try-section
                className={cn(
                    "flex w-full flex-col items-center gap-6 px-6 py-14 md:px-10",
                    mobile ? "min-h-screen" : "sticky top-0 h-screen",
                )}
            >
                <div
                    data-try-heading
                    className={cn(
                        "flex max-w-2xl shrink-0 flex-col items-center gap-2 text-center",
                        // No desktop quem revela o título é o FloatingChat, a
                        // partir do mesmo progresso que faz a janela crescer.
                        // Sem ele, o título precisa nascer visível.
                        !mobile && "opacity-0",
                    )}
                >
                    <span className="text-sm font-medium uppercase tracking-widest text-indigo-300">
                        Experimente
                    </span>
                    <h2 className="text-3xl font-bold text-white lg:text-4xl">
                        Converse com o OneShot
                    </h2>
                </div>

                {mobile ? (
                    // Janela de verdade, no fluxo normal da página: nada de
                    // posicionamento fixo, nada de esperar a expansão terminar
                    // para o campo aceitar toque.
                    <div className="flex h-[70vh] w-full max-w-2xl">
                        <ChatMessages
                            className="h-full w-full"
                            messages={SOURCE_MESSAGES}
                            autoPlay={false}
                            compact
                            interactive
                            onSendMessage={enviarPergunta}
                        />
                    </div>
                ) : (
                    /* A coluna da direita é a sala: o convite para entrar em
                       cima, quem já está dentro embaixo. Quando ela aparece, o
                       slot do chat cede um terço da largura — e como a janela é
                       fixa e persegue o retângulo do slot a cada quadro, ela se
                       reacomoda sozinha, animada, sem coreografia nova. */
                    <div className="flex min-h-0 w-full max-w-6xl flex-1 gap-4">
                        <div data-chat-slot="try" aria-hidden className="min-h-0 flex-1" />

                        {showAside && (
                            <div className="hidden min-h-0 w-1/3 shrink-0 flex-col gap-4 md:flex">
                                {showQr && <JoinQr />}
                                {live && (
                                    <LivePresenceCard sessions={sessions} selfId={sessionId} />
                                )}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </section>
    );
}
