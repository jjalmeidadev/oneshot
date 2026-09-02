// The chat window itself lives in FloatingChat (a single, shared instance).
// This section only reserves the space it should occupy here — the floating
// window is laid over this slot — and keeps its own text column, which the
// cross-section timeline fades in after the previous section's text is gone.
export default function ChatSwapSection() {
    return (
        <section
            data-chat-swap-section
            className="relative mx-auto flex min-h-screen w-full max-w-6xl flex-col items-start justify-center gap-8 overflow-x-hidden px-6 py-24 md:flex-row-reverse md:items-center md:justify-center md:gap-12 md:px-16"
        >
            {/* DOM order stays [chat, text]; `flex-row-reverse` is what puts
                the chat on the right and the text on the left, mirroring the
                previous section without duplicating the layout markup. */}
            <div
                data-chat-slot="swap"
                aria-hidden
                className="h-[420px] w-full max-w-[360px] shrink-0 md:max-w-[33vw]"
            />

            <div
                data-chat-text="to"
                className="hidden max-w-[33vw] flex-col gap-4 text-left md:flex"
            >
                <h2 className="text-3xl font-medium text-white lg:text-4xl">
                    Cada resposta aponta de onde veio
                </h2>
                <p className="text-lg leading-relaxed text-gray-300">
                    Nenhuma resposta fica solta: cronogramas, TAPs e documentos
                    normativos citados pelo assistente sempre vêm com a
                    indicação da fonte original, pra você conferir com um
                    clique.
                </p>
            </div>
        </section>
    );
}
