import ChatMessages from "@/components/chat/chat-messages";
import SkipRevealButton from "@/components/ui/skip-reveal-button";
import { INTRO_MESSAGES } from "@/components/chat/messages";
import { useScrollReveal } from "@/lib/useScrollReveal";

export default function ChatSection() {
    // Chat 1: conversa de apresentação, revelada a cada passo de scroll com a
    // página travada até a última mensagem.
    const { active, step, holding, skip, onBusyChange, onComplete } =
        useScrollReveal("[data-chat-section]");

    // The panel and text don't animate on their own here: once every message
    // has been scrolled in and the page unlocks, the fluid cross-section
    // transition (useChatSectionsTransition, wired up in App.tsx) carries
    // this panel out while the shared window slides in on the next section.
    return (
        <section
            id="modelo"
            data-chat-section
            className="relative mx-auto flex min-h-screen w-full max-w-6xl flex-col items-start justify-center gap-8 overflow-x-hidden px-6 py-24 md:flex-row md:items-center md:justify-center md:gap-12 md:px-16"
        >
            <div
                data-chat-panel="from"
                className="w-full max-w-[360px] shrink-0 md:max-w-[33vw]"
            >
                {/* Fixed height: the window stays the same size from the first
                    message to the last — new bubbles scroll inside it instead
                    of growing the panel and shifting the layout. */}
                <ChatMessages
                    className="h-[min(62vh,560px)] w-full"
                    messages={INTRO_MESSAGES}
                    autoPlay={false}
                    active={active}
                    revealStep={step}
                    typingDuration={250}
                    onBusyChange={onBusyChange}
                    onComplete={onComplete}
                    compact
                />
            </div>

            <div
                data-chat-text="from"
                className="hidden max-w-[33vw] flex-col gap-4 text-left md:flex"
            >
    
                <h2 className="text-3xl font-medium text-white lg:text-4xl">
                    Perguntas em linguagem natural, respostas com a fonte junto
                </h2>
                <p className="text-lg leading-relaxed text-gray-300">
                    O OneShot entende dúvidas sobre TAP, cronogramas, documentos
                    normativos e o andamento dos projetos do portfólio do Metrô — e
                    aponta de onde cada resposta veio, sem você precisar procurar
                    entre planilhas e pastas espalhadas.
                </p>
            </div>

            {holding && <SkipRevealButton onSkip={skip} />}
        </section>
    );
}
