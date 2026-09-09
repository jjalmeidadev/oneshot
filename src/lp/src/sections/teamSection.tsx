import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { TEAM, teamInitials, type TeamMember } from "@/lib/team";
import TeamProfile from "@/components/team/team-profile";
import { GLASS } from "@/lib/styles";
import { cn } from "@/lib/utils";

gsap.registerPlugin(ScrollTrigger);

/**
 * Os seis integrantes do projeto.
 *
 * Baseado no componente de time da comunidade, adaptado à paleta daqui — o
 * original usa os tokens do shadcn, que não existem neste projeto. Ficaram a
 * malha de fundo, o cabeçalho com a palavra espaçada, a onda que sobe no
 * hover e o anel do avatar.
 *
 * A chegada é toda presa ao scroll: o fundo cinza vai ganhando corpo
 * conforme a seção entra, e o conteúdo chega pela esquerda com um leve
 * repique, um card de cada vez.
 */
export default function TeamSection() {
    const sectionRef = useRef<HTMLElement>(null);
    const [selected, setSelected] = useState<TeamMember | null>(null);

    useEffect(() => {
        const section = sectionRef.current;
        if (!section) return;

        const ctx = gsap.context(() => {
            // O fundo cinza aparece aos poucos, preso ao scroll: no começo
            // ainda se vê o gradiente por baixo, e ele termina opaco junto com
            // a entrada do conteúdo.
            gsap.fromTo(
                "[data-team-backdrop]",
                { opacity: 0 },
                {
                    opacity: 1,
                    ease: "none",
                    scrollTrigger: {
                        trigger: section,
                        start: "top bottom",
                        end: "top 35%",
                        scrub: 0.8,
                    },
                },
            );

            // Entrada em cascata pela esquerda, com repique.
            //
            // O scroll é o gatilho, não a agulha: o repique precisa de duração
            // própria — com `scrub`, a curva do `back.out` seria percorrida
            // pela roda do mouse e o salto viraria arrasto.
            //
            // Fora de quadro tudo volta ao estado inicial (`pause(0)`): a
            // seção não existe antes de aparecer, e a entrada se refaz toda
            // vez que se chega nela, descendo ou subindo.
            const enterFromLeft = (
                targets: string,
                triggerSelector: string,
                options: { distance: number; stagger: number; duration: number },
            ) => {
                const elements = gsap.utils.toArray<HTMLElement>(targets);
                if (elements.length === 0) return;

                gsap.set(elements, { x: -options.distance, opacity: 0, rotate: -3 });

                const tween = gsap.to(elements, {
                    x: 0,
                    opacity: 1,
                    rotate: 0,
                    duration: options.duration,
                    ease: "back.out(1.7)",
                    stagger: { each: options.stagger, from: "start" },
                    paused: true,
                });

                ScrollTrigger.create({
                    trigger: triggerSelector,
                    start: "top bottom",
                    end: "bottom top",
                    onEnter: () => tween.restart(),
                    onEnterBack: () => tween.restart(),
                    onLeave: () => tween.pause(0),
                    onLeaveBack: () => tween.pause(0),
                    onRefresh: (self) => {
                        // Recarregou com a seção já em quadro: toca sem
                        // esperar um cruzamento que não vai acontecer.
                        if (self.isActive && !tween.isActive() && tween.progress() === 0) {
                            tween.restart();
                        }
                    },
                });
            };

            enterFromLeft("[data-team-heading] > *", "[data-team-heading]", {
                distance: 120,
                stagger: 0.1,
                duration: 1,
            });

            enterFromLeft("[data-team-card]", "[data-team-grid]", {
                distance: 140,
                stagger: 0.14,
                duration: 1.1,
            });

            // Inclinação seguindo o cursor: cada card responde ao ponteiro,
            // com `quickTo` para não criar um tween novo a cada movimento.
            gsap.utils.toArray<HTMLElement>("[data-team-card]").forEach((card) => {
                const tiltY = gsap.quickTo(card, "rotationY", { duration: 0.5, ease: "power3" });
                const tiltX = gsap.quickTo(card, "rotationX", { duration: 0.5, ease: "power3" });

                const onMove = (event: PointerEvent) => {
                    const rect = card.getBoundingClientRect();
                    const px = (event.clientX - rect.left) / rect.width - 0.5;
                    const py = (event.clientY - rect.top) / rect.height - 0.5;
                    tiltY(px * 12);
                    tiltX(-py * 12);
                };
                const onLeave = () => {
                    tiltY(0);
                    tiltX(0);
                };

                card.addEventListener("pointermove", onMove);
                card.addEventListener("pointerleave", onLeave);
                card.addEventListener("blur", onLeave);
            });
        }, section);

        return () => ctx.revert();
    }, []);

    return (
        <section
            ref={sectionRef}
            id="time"
            className="relative z-10 w-full overflow-hidden py-24 md:py-32"
        >
            {/* O cinza é uma camada própria: assim dá para trazê-lo com o
                scroll em vez de trocar de cor de um quadro para o outro. */}
            <div
                data-team-backdrop
                aria-hidden
                className="pointer-events-none absolute inset-0 bg-neutral-800 opacity-0"
            />

            {/* Malha de fundo, bem discreta */}
            <div aria-hidden className="pointer-events-none absolute inset-0 opacity-[0.07]">
                <svg className="h-full w-full" fill="none">
                    <defs>
                        <pattern id="team-grid" x="0" y="0" width="28" height="28" patternUnits="userSpaceOnUse">
                            <path d="M28 0L0 0 0 28" fill="none" stroke="white" strokeWidth="0.5" />
                        </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#team-grid)" />
                </svg>
            </div>

            <div className="relative mx-auto flex w-full max-w-6xl flex-col gap-12 px-6 md:px-16">
                <div data-team-heading className="flex flex-col gap-3">
                    <span className="text-sm font-medium uppercase tracking-[0.4em] text-indigo-300">
                        Nosso
                    </span>
                    <h2 className="text-4xl font-bold tracking-tight text-white lg:text-5xl">
                        Time
                    </h2>
                    <p className="max-w-2xl text-lg leading-relaxed text-white/60">
                        Seis pessoas construindo o OneShot — do modelo que responde à
                        interface que você acabou de percorrer.
                    </p>
                </div>

                <div
                    data-team-grid
                    className="grid grid-cols-1 gap-6 [perspective:1000px] sm:grid-cols-2 lg:grid-cols-3"
                >
                    {TEAM.map((member) => (
                        <button
                            key={member.name}
                            type="button"
                            data-team-card
                            onClick={() => setSelected(member)}
                            aria-label={`Ver perfil de ${member.name}`}
                            className={cn(
                                GLASS,
                                "group relative flex cursor-pointer flex-col items-center gap-4 overflow-hidden p-8 text-center [transform-style:preserve-3d] transition-colors duration-300 hover:border-white/25",
                            )}
                        >
                            {/* Onda que sobe no hover, na cor da pessoa */}
                            <span
                                aria-hidden
                                className="absolute inset-x-0 bottom-0 h-2/3 origin-bottom scale-y-0 rounded-t-[50%] transition-transform duration-500 ease-out group-hover:scale-y-100"
                                style={{
                                    background: `linear-gradient(to top, ${member.color}33, transparent)`,
                                }}
                            />

                            <span
                                data-team-avatar={member.name}
                                className="relative z-10 flex size-28 items-center justify-center overflow-hidden rounded-full border-4 border-white/10 text-2xl font-medium text-neutral-900 transition-transform duration-500 ease-out group-hover:scale-105"
                                style={{ backgroundColor: member.color }}
                            >
                                {member.imageSrc ? (
                                    <img
                                        src={member.imageSrc}
                                        alt={member.name}
                                        className="size-full object-cover transition-transform duration-500 ease-out group-hover:scale-110"
                                    />
                                ) : (
                                    teamInitials(member.name)
                                )}
                            </span>

                            <span className="relative z-10 flex flex-col gap-1">
                                <span className="text-lg font-medium text-white">{member.name}</span>
                                <span className="text-sm font-normal text-white/50">
                                    {member.designation}
                                </span>
                            </span>

                            <span className="relative z-10 text-[11px] font-normal uppercase tracking-widest text-indigo-300 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                                Ver perfil
                            </span>
                        </button>
                    ))}
                </div>
            </div>

            <TeamProfile member={selected} onClose={() => setSelected(null)} />
        </section>
    );
}
