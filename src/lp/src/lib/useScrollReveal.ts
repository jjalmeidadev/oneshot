import { useCallback, useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { claimHold, releaseHold } from "@/lib/scrollHold";

gsap.registerPlugin(ScrollTrigger);

const SCROLL_KEYS = new Set([
    "ArrowDown",
    "ArrowUp",
    "PageDown",
    "PageUp",
    "Home",
    "End",
    " ",
]);
const FORWARD_KEYS = new Set(["ArrowDown", "PageDown", "End", " "]);

/**
 * Ordem para todas as seções de conversa largarem a página. Com
 * `detail.complete`, a conversa também é dada por encerrada — é o que a
 * navbar dispara ao mandar o visitante para uma seção depois dos chats.
 */
export const RELEASE_HOLDS_EVENT = "oneshot:release-holds";

/** Scroll distance (px) that brings in the next message. */
const STEP_DISTANCE = 140;
/** Minimum gap between two consecutive messages, per the 0.5s pacing. */
const STEP_COOLDOWN = 500;

/**
 * Scroll-driven message reveal for a full-height section.
 *
 * The section takes the page over the moment it is entirely on screen — it is
 * `min-h-screen`, so "its top reaches the top of the viewport" is exactly that
 * moment — and from there each notch of scroll reveals one more message
 * instead of moving the page. The hold lifts when the conversation ends.
 *
 * The hold is positional, not just `preventDefault`: a fast flick (or inertial
 * scrolling, a scrollbar drag, a middle-click autoscroll) can carry the page
 * well past the section before any handler runs, which used to leave the
 * messages playing off-screen and the next animations firing far too early.
 * Pinning the scroll offset to the section makes those cases behave like a
 * normal one.
 *
 * Returns the props a `ChatMessages` in scroll-driven mode expects.
 */
export function useScrollReveal(sectionSelector: string) {
    const [active, setActive] = useState(false);
    const [step, setStep] = useState(0);
    /** Verdadeiro enquanto a seção está segurando a página. */
    const [holding, setHolding] = useState(false);
    const startedRef = useRef(false);
    // Refs (not state) so the scroll handlers can read them without being
    // re-registered on every message.
    const busyRef = useRef(false);
    const readyAtRef = useRef(0);
    const accumRef = useRef(0);
    const touchYRef = useRef(0);
    const releaseRef = useRef<(() => void) | null>(null);

    useEffect(() => {
        const section = document.querySelector<HTMLElement>(sectionSelector);
        if (!section) return;

        // Em tela de toque a página nunca é segurada. A coreografia foi
        // pensada para a roda do mouse, onde cada "marcha" revela uma
        // mensagem; no celular, uma página que se recusa a rolar é
        // indistinguível de uma página travada — e o visitante desiste antes
        // de achar o botão de pular. Aqui a conversa aparece inteira e a
        // rolagem continua sendo a nativa do sistema.
        const touchDevice =
            typeof window.matchMedia === "function" &&
            window.matchMedia("(pointer: coarse)").matches;

        // Mesmo caminho de quando a página carrega já dentro da seção.
        if (touchDevice || section.getBoundingClientRect().top <= 1) {
            startedRef.current = true;
            setActive(true);
            setStep(Number.MAX_SAFE_INTEGER);
            return;
        }

        let held = false;
        let lockY = 0;

        const advance = (delta: number) => {
            if (delta <= 0) return;
            accumRef.current += delta;
            if (busyRef.current || performance.now() < readyAtRef.current) {
                // Don't let scrolling during the pause queue up extra steps.
                accumRef.current = Math.min(accumRef.current, STEP_DISTANCE);
                return;
            }
            if (accumRef.current < STEP_DISTANCE) return;
            accumRef.current = 0;
            setStep((current) => current + 1);
        };

        const onWheel = (event: WheelEvent) => {
            event.preventDefault();
            advance(event.deltaY);
        };

        const onTouchStart = (event: TouchEvent) => {
            touchYRef.current = event.touches[0]?.clientY ?? 0;
        };

        const onTouchMove = (event: TouchEvent) => {
            event.preventDefault();
            const y = event.touches[0]?.clientY ?? 0;
            advance(touchYRef.current - y);
            touchYRef.current = y;
        };

        const onKeyDown = (event: KeyboardEvent) => {
            if (!SCROLL_KEYS.has(event.key)) return;
            event.preventDefault();
            if (FORWARD_KEYS.has(event.key)) advance(STEP_DISTANCE);
        };

        // The safety net: whatever slips past the handlers above (inertia,
        // scrollbar, autoscroll) is undone right away.
        const onScroll = () => {
            if (!held) return;
            if (Math.abs(window.scrollY - lockY) > 1) {
                window.scrollTo({ top: lockY, behavior: "instant" as ScrollBehavior });
            }
        };

        const release = () => {
            if (!held) return;
            held = false;
            releaseHold(sectionSelector);
            setHolding(false);
            window.removeEventListener("wheel", onWheel);
            window.removeEventListener("touchstart", onTouchStart);
            window.removeEventListener("touchmove", onTouchMove);
            window.removeEventListener("keydown", onKeyDown);
            window.removeEventListener("scroll", onScroll);
        };

        const engage = () => {
            if (startedRef.current) return;
            // Num scroll muito rápido, duas seções cruzam o próprio gatilho no
            // mesmo voo. Só uma pode assumir a página: a outra desiste e tenta
            // de novo na próxima passagem, já que o gatilho não é de uso único.
            if (!claimHold(sectionSelector)) return;
            startedRef.current = true;

            lockY = Math.round(window.scrollY + section.getBoundingClientRect().top);
            held = true;
            // Instant, not smooth: a smooth correction would still be
            // animating while the first messages played.
            window.scrollTo({ top: lockY, behavior: "instant" as ScrollBehavior });

            window.addEventListener("wheel", onWheel, { passive: false });
            window.addEventListener("touchstart", onTouchStart, { passive: true });
            window.addEventListener("touchmove", onTouchMove, { passive: false });
            window.addEventListener("keydown", onKeyDown, { passive: false });
            window.addEventListener("scroll", onScroll, { passive: true });

            setActive(true);
            setHolding(true);
        };

        releaseRef.current = release;

        const ctx = gsap.context(() => {
            ScrollTrigger.create({
                trigger: section,
                start: "top top",
                onEnter: engage,
            });
        }, section);

        return () => {
            ctx.revert();
            release();
            releaseRef.current = null;
        };
    }, [sectionSelector]);

    // Navegação por link: a seção larga a página na hora, e se o destino
    // fica depois dela a conversa é dada por concluída (o ChatMessages
    // detecta o salto e mostra tudo de uma vez).
    useEffect(() => {
        const onRelease = (event: Event) => {
            const complete = (event as CustomEvent<{ complete?: boolean }>).detail?.complete;
            if (complete) {
                startedRef.current = true;
                setActive(true);
                setStep(Number.MAX_SAFE_INTEGER);
            }
            releaseRef.current?.();
        };

        window.addEventListener(RELEASE_HOLDS_EVENT, onRelease);
        return () => window.removeEventListener(RELEASE_HOLDS_EVENT, onRelease);
    }, []);

    const onBusyChange = useCallback((busy: boolean) => {
        busyRef.current = busy;
        // A message just landed: hold the next one for half a second.
        if (!busy) readyAtRef.current = performance.now() + STEP_COOLDOWN;
    }, []);

    const onComplete = useCallback(() => {
        releaseRef.current?.();
    }, []);

    /**
     * Conclui a conversa na hora: o alvo salta para o fim (o ChatMessages
     * detecta o salto e mostra tudo de uma vez, sem os tempos de digitação) e
     * a página é liberada no mesmo instante.
     */
    const skip = useCallback(() => {
        setStep(Number.MAX_SAFE_INTEGER);
        releaseRef.current?.();
    }, []);

    return { active, step, holding, skip, onBusyChange, onComplete };
}
