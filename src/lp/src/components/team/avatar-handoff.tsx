import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { TEAM, teamInitials } from "@/lib/team";

gsap.registerPlugin(ScrollTrigger);

const SMOOTHING = 0.14;

const clamp01 = (value: number) => Math.min(1, Math.max(0, value));
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

/**
 * A passagem da seção de time para o rodapé.
 *
 * São as mesmas pessoas nos dois lugares — então, em vez de os avatares
 * sumirem de um lado e aparecerem do outro, eles viajam: cada um sai do card
 * e encolhe até virar exatamente a bolinha do rodapé, em cascata. É a mesma
 * medição quadro a quadro usada na janela de chat, e é o que dá ao terço
 * final da página o fio condutor que faltava.
 */
export default function AvatarHandoff() {
    const rootRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const root = rootRef.current;
        if (!root) return;

        const footer = document.querySelector<HTMLElement>("[data-footer-team]");
        if (!footer) return;

        const ctx = gsap.context(() => {
            const clones = gsap.utils.toArray<HTMLElement>("[data-handoff-avatar]", root);
            const sources = TEAM.map((member) =>
                document.querySelector<HTMLElement>(`[data-team-avatar="${member.name}"]`),
            );
            const targets = TEAM.map((member) =>
                document.querySelector<HTMLElement>(`[data-footer-avatar="${member.name}"]`),
            );
            if (sources.some((el) => !el) || targets.some((el) => !el)) return;

            let targetProgress = 0;
            let progress = 0;
            let lastSourceFade = 1;
            let lastTargetFade = 1;

            const trigger = ScrollTrigger.create({
                trigger: footer,
                start: "top bottom",
                end: "top 55%",
                onUpdate: (self) => {
                    targetProgress = self.progress;
                },
                onRefresh: (self) => {
                    targetProgress = self.progress;
                },
            });
            progress = targetProgress = trigger.progress;

            const render = () => {
                progress += (targetProgress - progress) * SMOOTHING;
                if (Math.abs(targetProgress - progress) < 0.0005) progress = targetProgress;
                const p = progress;

                // Os avatares reais cedem lugar às cópias em voo: os do card
                // apagam na largada, os do rodapé acendem na chegada.
                const sourceFade = 1 - clamp01(p / 0.12);
                if (Math.abs(sourceFade - lastSourceFade) > 0.001) {
                    sources.forEach((el) => el && gsap.set(el, { opacity: sourceFade }));
                    lastSourceFade = sourceFade;
                }
                const targetFade = clamp01((p - 0.82) / 0.18);
                if (Math.abs(targetFade - lastTargetFade) > 0.001) {
                    targets.forEach((el) => el && gsap.set(el, { opacity: targetFade }));
                    lastTargetFade = targetFade;
                }

                if (p <= 0.001 || p >= 0.999) {
                    gsap.set(root, { autoAlpha: 0 });
                    return;
                }
                gsap.set(root, { autoAlpha: 1 });

                clones.forEach((clone, index) => {
                    const from = sources[index]!.getBoundingClientRect();
                    const to = targets[index]!.getBoundingClientRect();
                    const delay = index * 0.05;
                    const local = ease(clamp01((p - delay) / (0.75 - delay * 0.5)));

                    gsap.set(clone, {
                        left: lerp(from.left, to.left, local),
                        top: lerp(from.top, to.top, local),
                        width: lerp(from.width, to.width, local),
                        height: lerp(from.height, to.height, local),
                        fontSize: lerp(24, 12, local),
                        borderWidth: lerp(4, 2, local),
                    });
                });
            };

            render();
            gsap.ticker.add(render);

            return () => {
                gsap.ticker.remove(render);
                trigger.kill();
                sources.forEach((el) => el && gsap.set(el, { opacity: 1 }));
                targets.forEach((el) => el && gsap.set(el, { opacity: 1 }));
            };
        }, root);

        return () => ctx.revert();
    }, []);

    return (
        <div
            ref={rootRef}
            aria-hidden
            className="pointer-events-none fixed inset-0 z-20 overflow-hidden opacity-0"
        >
            {TEAM.map((member) => (
                <span
                    key={member.name}
                    data-handoff-avatar
                    className="absolute flex items-center justify-center overflow-hidden rounded-full border-white/10 font-medium text-neutral-900"
                    style={{ backgroundColor: member.color, borderStyle: "solid" }}
                >
                    {member.imageSrc ? (
                        <img src={member.imageSrc} alt="" className="size-full object-cover" />
                    ) : (
                        teamInitials(member.name)
                    )}
                </span>
            ))}
        </div>
    );
}
