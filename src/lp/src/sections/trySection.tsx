import JoinQr from "@/components/live/join-qr";
import LivePresenceCard from "@/components/live/live-presence-card";
import { HAS_LIVE_BACKEND } from "@/lib/liveBackend";
import { useLivePresence } from "@/lib/useLivePresence";
import { useLiveSessionId } from "@/lib/liveSessionContext";

// Last section: the shared chat window (FloatingChat) morphs from the swap
// section's slot into the slot below, ending up taking most of the screen.
// The heading is held at opacity 0 and only fades in once that expansion has
// finished — FloatingChat drives it from the same scroll progress.
//
// The section is deliberately much taller than the screen, with its content
// stuck to the viewport: after the window finishes expanding there is over a
// screenful of scrolling that changes nothing on the page, which is what
// gives the visitor time to actually talk to the model before the footer
// comes into view.
export default function TrySection() {
    const { sessions } = useLivePresence();
    // A entrada na sala acontece no provedor, no topo da página; aqui só
    // se lê o id, para marcar qual das pessoas do painel é você.
    const sessionId = useLiveSessionId();
    // O painel só abre quando há companhia: como a própria página entra na
    // sala, "1 pessoa" seria sempre você, e o layout nunca voltaria ao normal.
    const live = sessions.some((session) => session.id !== sessionId);
    // O convite por QR só faz sentido havendo sala de verdade para entrar;
    // no modo simulado de `?ao-vivo=N` ele levaria a lugar nenhum.
    const showQr = HAS_LIVE_BACKEND;
    const showAside = showQr || live;

    return (
        <section className="relative min-h-[240vh] w-full">
            <div
                data-try-section
                className="sticky top-0 flex h-screen w-full flex-col items-center gap-6 px-6 py-14 md:px-10"
            >
                <div
                    data-try-heading
                    className="flex max-w-2xl shrink-0 flex-col items-center gap-2 text-center opacity-0"
                >
                    <span className="text-sm font-medium uppercase tracking-widest text-indigo-300">
                        Experimente
                    </span>
                    <h2 className="text-3xl font-bold text-white lg:text-4xl">
                        Converse com o OneShot
                    </h2>
                </div>

                {/* A coluna da direita é a sala: o convite para entrar em
                    cima, quem já está dentro embaixo. Quando ela aparece, o
                    slot do chat cede um terço da largura — e como a janela é
                    fixa e persegue o retângulo do slot a cada quadro, ela se
                    reacomoda sozinha, animada, sem coreografia nova. */}
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
            </div>
        </section>
    );
}
