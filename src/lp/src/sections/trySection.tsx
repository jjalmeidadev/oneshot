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
                           <h2 className="text-3xl font-medium text-white lg:text-4xl">
                        Converse com o OneShot
                    </h2>
                </div>

                <div data-chat-slot="try" aria-hidden className="min-h-0 w-full max-w-6xl flex-1" />
            </div>
        </section>
    );
}
