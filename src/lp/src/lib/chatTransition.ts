import { useEffect } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

/**
 * Drives a single fluid scroll-scrubbed transition between the two chat
 * sections. Instead of ChatSection and ChatSwapSection each animating their
 * own panel independently (two disjoint fling animations, only loosely in
 * sync), this hook queries both panels by their `data-chat-panel` markers
 * and moves them together on one shared ScrollTrigger/timeline — the "from"
 * panel slides out left while the "to" panel slides in from the right, in
 * one continuous motion.
 *
 * The accompanying text blocks (`data-chat-text`) are sequenced rather than
 * crossfaded: the outgoing text fades fully to opacity 0 first, and only
 * once that finishes does the incoming text begin fading up from 0 to 1.
 *
 * Call this once, at the App level, after both sections have mounted.
 */
export function useChatSectionsTransition() {
    useEffect(() => {
        const fromPanel = document.querySelector<HTMLElement>('[data-chat-panel="from"]');
        const toPanel = document.querySelector<HTMLElement>('[data-chat-panel="to"]');
        const fromText = document.querySelector<HTMLElement>('[data-chat-text="from"]');
        const toText = document.querySelector<HTMLElement>('[data-chat-text="to"]');
        const trigger = document.querySelector<HTMLElement>('[data-chat-swap-section]');
        const fromSection = document.querySelector<HTMLElement>("[data-chat-section]");
        if (!fromPanel || !toPanel || !trigger) return;

        const ctx = gsap.context(() => {
            // A janela não desliza mais de um lado para o outro: ela se
            // dissolve (desfoca, encolhe e apaga) enquanto o carrossel de
            // documentos gira por cima, e se recompõe do outro lado quando o
            // carrossel já passou.
            gsap.set(toPanel, { opacity: 0, scale: 0.92, filter: "blur(14px)" });
            if (toText) gsap.set(toText, { opacity: 0 });

            const tl = gsap.timeline({
                scrollTrigger: {
                    trigger,
                    // Mesma faixa do carrossel de documentos, para a
                    // dissolução e o giro andarem juntos. A faixa vive dentro
                    // da virada entre as duas seções, com folga nas duas
                    // pontas: descendo, a troca termina antes do chat 2
                    // enquadrar; subindo, ela se desfaz por completo antes do
                    // chat 1 voltar a ocupar a tela.
                    start: "top 85%",
                    end: "top 25%",
                    scrub: 0.8,
                },
            });

            // Primeiro terço: a janela do chat 1 se dissolve. Último terço:
            // a do chat 2 se materializa. No meio fica só o carrossel.
            tl.to(
                fromPanel,
                {
                    opacity: 0,
                    scale: 0.92,
                    filter: "blur(14px)",
                    ease: "power1.in",
                    duration: 0.35,
                },
                0,
            );
            tl.to(
                toPanel,
                {
                    opacity: 1,
                    scale: 1,
                    filter: "blur(0px)",
                    ease: "power2.out",
                    duration: 0.4,
                },
                0.6,
            );

            // Sequential text fade: outgoing text fades out over the first
            // half of the scroll range, incoming text only starts fading in
            // once that's complete.
            if (fromText) {
                tl.to(fromText, { opacity: 0, ease: "none", duration: 0.35 }, 0);
            }
            if (toText) {
                tl.to(toText, { opacity: 1, ease: "none", duration: 0.4 }, 0.6);
            }

            // Parallax de entrada dos textos: o da seção 1 chega pela direita,
            // o da seção 2 pela esquerda — cada um preso à entrada da sua
            // própria seção. Mexem só em `x`, então não disputam com as
            // opacidades da timeline acima.
            if (fromText && fromSection) {
                gsap.fromTo(
                    fromText,
                    { x: 140 },
                    {
                        x: 0,
                        ease: "none",
                        scrollTrigger: {
                            trigger: fromSection,
                            start: "top bottom",
                            end: "top 25%",
                            scrub: 0.8,
                        },
                    },
                );
            }

            if (toText) {
                gsap.fromTo(
                    toText,
                    { x: -140 },
                    {
                        x: 0,
                        ease: "none",
                        scrollTrigger: {
                            trigger,
                            start: "top bottom",
                            end: "top 25%",
                            scrub: 0.8,
                        },
                    },
                );
            }
        });

        return () => ctx.revert();
    }, []);
}
