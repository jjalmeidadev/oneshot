import { useCallback, useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import ChatMessages from "@/components/chat/chat-messages";
import { SOURCE_MESSAGES } from "@/components/chat/messages";
import { useScrollReveal } from "@/lib/useScrollReveal";
import { cn } from "@/lib/utils";

gsap.registerPlugin(ScrollTrigger);

/** How quickly the window catches up with the scroll position (0-1). */
const SMOOTHING = 0.12;
/** Progress past which the window counts as filling the screen. */
const EXPANDED_AT = 0.995;

/**
 * The single chat window shared by the swap section and the "try it"
 * section. It is rendered once, positioned `fixed`, and every frame it is
 * laid over a slot element: `[data-chat-slot="swap"]` while the swap section
 * is on screen, `[data-chat-slot="try"]` once the page reaches the last
 * section, interpolating between the two rects in between.
 *
 * Because there is only ever one instance, the growth from the small panel
 * to the near-fullscreen window is a continuous morph of the same DOM node —
 * no crossfade between two separate chats, and the conversation carries
 * straight over.
 */
export default function FloatingChat() {
    const wrapRef = useRef<HTMLDivElement>(null);
    // Until the window has finished growing, it neither scrolls its own
    // conversation nor takes pointer events — every gesture over it belongs
    // to the page, which is what drives the expansion.
    const [expanded, setExpanded] = useState(false);
    const expandedRef = useRef(false);
    // Chat 2 has its own conversation — about where each answer came from —
    // and reveals it step by step while the swap section holds the page.
    const { active, step, onBusyChange, onComplete } = useScrollReveal(
        "[data-chat-swap-section]",
    );

    useEffect(() => {
        const wrap = wrapRef.current;
        const fromSlot = document.querySelector<HTMLElement>('[data-chat-slot="swap"]');
        const toSlot = document.querySelector<HTMLElement>('[data-chat-slot="try"]');
        const swapSection = document.querySelector<HTMLElement>("[data-chat-swap-section]");
        if (!wrap || !fromSlot || !toSlot || !swapSection) return;

        const heading = document.querySelector<HTMLElement>("[data-try-heading]");
        const setHeadingOpacity = heading ? gsap.quickSetter(heading, "opacity") : null;
        const setHeadingY = heading ? gsap.quickSetter(heading, "y", "px") : null;

        let targetProgress = 0;
        let progress = 0;

        const trigger = ScrollTrigger.create({
            trigger: swapSection,
            // Nothing moves until the swap section has been scrolled through
            // in full: it is `min-h-screen`, so "its bottom reaches the bottom
            // of the viewport" is the moment it has been seen end to end. The
            // morph then runs over the next screenful, finishing right as the
            // last section lands in place.
            start: "bottom bottom",
            end: "bottom top",
            onUpdate: (self) => {
                targetProgress = self.progress;
            },
            onRefresh: (self) => {
                targetProgress = self.progress;
            },
        });
        progress = targetProgress = trigger.progress;

        const render = () => {
            // Ease toward the scroll position instead of snapping to it, so
            // the morph keeps a bit of momentum — that's what makes it read
            // as fluid rather than glued to the wheel.
            progress += (targetProgress - progress) * SMOOTHING;
            if (Math.abs(targetProgress - progress) < 0.0005) progress = targetProgress;

            const a = fromSlot.getBoundingClientRect();
            const b = toSlot.getBoundingClientRect();
            const p = progress;

            gsap.set(wrap, {
                left: a.left + (b.left - a.left) * p,
                top: a.top + (b.top - a.top) * p,
                width: a.width + (b.width - a.width) * p,
                height: a.height + (b.height - a.height) * p,
            });

            const isExpanded = p >= EXPANDED_AT;
            if (isExpanded !== expandedRef.current) {
                expandedRef.current = isExpanded;
                setExpanded(isExpanded);
            }

            if (setHeadingOpacity && setHeadingY) {
                // The heading only shows up once the window has finished
                // expanding.
                const reveal = gsap.utils.clamp(0, 1, (p - 0.92) / 0.08);
                setHeadingOpacity(reveal);
                setHeadingY((1 - reveal) * 14);
            }
        };

        render();
        gsap.ticker.add(render);

        return () => {
            gsap.ticker.remove(render);
            trigger.kill();
        };
    }, []);

    // Seam for the RAG backend: this is the single place that has to change
    // once the model that answers about the OneShot project is available.
    const handleSendMessage = useCallback(async (message: string) => {
        await new Promise((resolve) => setTimeout(resolve, 600));
        return `Ainda não estou ligado à base de conhecimento do OneShot, então não consigo responder "${message}" de verdade. Assim que o modelo estiver conectado, a resposta vem dos documentos do projeto com a fonte junto.`;
    }, []);

    return (
        <div
            ref={wrapRef}
            data-chat-panel="to"
            className={cn(
                "fixed top-0 left-0 z-30 opacity-0",
                expanded ? "pointer-events-auto" : "pointer-events-none",
            )}
        >
            <ChatMessages
                className="h-full w-full"
                messages={SOURCE_MESSAGES}
                autoPlay={false}
                active={active}
                revealStep={step}
                typingDuration={250}
                onBusyChange={onBusyChange}
                onComplete={onComplete}
                compact
                interactive
                lockScroll={!expanded}
                onSendMessage={handleSendMessage}
            />
        </div>
    );
}
