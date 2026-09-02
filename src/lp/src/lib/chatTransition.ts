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
        if (!fromPanel || !toPanel || !trigger) return;

        const ctx = gsap.context(() => {
            gsap.set(toPanel, { xPercent: 60, opacity: 0 });
            if (toText) gsap.set(toText, { opacity: 0 });

            const tl = gsap.timeline({
                scrollTrigger: {
                    trigger,
                    start: "top 90%",
                    end: "top 20%",
                    scrub: 0.8,
                },
            });

            // Fluid, continuous panel swap: both tweens share the same
            // timeline position and duration, so they play as one motion.
            tl.to(fromPanel, { xPercent: -60, opacity: 0, ease: "none", duration: 1 }, 0);
            tl.to(toPanel, { xPercent: 0, opacity: 1, ease: "none", duration: 1 }, 0);

            // Sequential text fade: outgoing text fades out over the first
            // half of the scroll range, incoming text only starts fading in
            // once that's complete.
            if (fromText) {
                tl.to(fromText, { opacity: 0, ease: "none", duration: 0.5 }, 0);
            }
            if (toText) {
                tl.to(toText, { opacity: 1, ease: "none", duration: 0.5 }, 0.5);
            }
        });

        return () => ctx.revert();
    }, []);
}
