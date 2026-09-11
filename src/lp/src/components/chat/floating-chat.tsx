import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import ChatMessages from "@/components/chat/chat-messages";
import { useAgentChat } from "@/lib/useAgentChat";
import { SOURCE_MESSAGES } from "@/components/chat/messages";
import { useScrollReveal } from "@/lib/useScrollReveal";
import { LIVE_FOLLOW_EVENT } from "@/lib/useLivePresence";
import SkipRevealButton from "@/components/ui/skip-reveal-button";
import { cn } from "@/lib/utils";

gsap.registerPlugin(ScrollTrigger);

/** How quickly the window catches up with the scroll position (0-1). */
const SMOOTHING = 0.12;
/** Progress past which the window counts as filling the screen. */
const EXPANDED_AT = 0.995;

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

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
    // A janela só recebe gestos — e só rola a própria conversa — quando isso
    // não disputa com o scroll da página: parada no slot da seção 2 com a
    // conversa já revelada, ou depois de terminar de crescer. Durante a
    // expansão, todo gesto pertence à página.
    const [interactive, setInteractive] = useState(false);
    const interactiveRef = useRef(false);
    // Chat 2 has its own conversation — about where each answer came from —
    // and reveals it step by step while the swap section holds the page.
    const { active, step, holding, skip, onBusyChange, onComplete } = useScrollReveal(
        "[data-chat-swap-section]",
    );
    // Espelho para o laço de quadro, que não enxerga estado do React.
    const holdingRef = useRef(holding);
    useEffect(() => {
        holdingRef.current = holding;
    }, [holding]);

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
                left: lerp(a.left, b.left, p),
                top: lerp(a.top, b.top, p),
                width: lerp(a.width, b.width, p),
                height: lerp(a.height, b.height, p),
            });

            // Parada no slot da seção 2 (p ≈ 0) e sem a seção segurando a
            // página: a conversa pode ser rolada para cima e para baixo.
            // Em tela cheia (p ≈ 1), idem.
            const settled = p < 0.02 && !holdingRef.current;
            const isInteractive = p >= EXPANDED_AT || settled;
            if (isInteractive !== interactiveRef.current) {
                interactiveRef.current = isInteractive;
                setInteractive(isInteractive);
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

    // Enquanto alguém está sendo acompanhado ao vivo, a janela sai de cena:
    // o painel de acompanhamento cobre a tela e o chat atrás dele só
    // atrapalharia a leitura.
    useEffect(() => {
        const wrap = wrapRef.current;
        if (!wrap) return;

        const onFollow = (event: Event) => {
            const active = (event as CustomEvent<{ active?: boolean }>).detail?.active;
            gsap.to(wrap, {
                opacity: active ? 0 : 1,
                duration: 0.3,
                ease: "power2.out",
                overwrite: "auto",
            });
        };

        window.addEventListener(LIVE_FOLLOW_EVENT, onFollow);
        return () => window.removeEventListener(LIVE_FOLLOW_EVENT, onFollow);
    }, []);

    const handleSendMessage = useAgentChat();

    return (
        <>
        <div
            ref={wrapRef}
            data-chat-panel="to"
            className={cn(
                "fixed top-0 left-0 z-30 opacity-0",
                interactive ? "pointer-events-auto" : "pointer-events-none",
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
                lockScroll={!interactive}
                onSendMessage={handleSendMessage}
            />
        </div>

        {holding && <SkipRevealButton onSkip={skip} />}
        </>
    );
}
