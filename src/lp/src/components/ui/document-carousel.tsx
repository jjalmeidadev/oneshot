import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { DocumentGlyph, type GhostKind } from "@/components/ui/ghost-documents";

gsap.registerPlugin(ScrollTrigger);

/** Documentos no anel, na ordem em que passam pela frente. */
const RING: GhostKind[] = ["page", "gantt", "table", "page", "gantt"];
/** Raio do cilindro, em pixels. */
const RADIUS = 240;

/**
 * A passagem do chat 1 para o chat 2, vista pelo fundo.
 *
 * As silhuetas de documento sobem para um plano acima da conversa, giram
 * como um cilindro (um anel em torno do eixo X, tipo rolodex) enquanto
 * atravessam a tela da esquerda para a direita, e assentam atrás da janela
 * que chega do lado direito — onde ficam como fundo daquela conversa até a
 * seção seguinte começar.
 *
 * Vive numa camada fixa: as posições são de viewport, então a coreografia
 * não depende de onde as seções estão no documento.
 */
export default function DocumentCarousel() {
    const rootRef = useRef<HTMLDivElement>(null);
    const groupRef = useRef<HTMLDivElement>(null);
    const ringRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const root = rootRef.current;
        const group = groupRef.current;
        const ring = ringRef.current;
        if (!root || !group || !ring) return;

        const swapSection = document.querySelector<HTMLElement>("[data-chat-swap-section]");
        if (!swapSection) return;
        const tryStage = document.querySelector<HTMLElement>("[data-try-section]")?.parentElement;

        const ctx = gsap.context(() => {
            const timeline = gsap.timeline({
                scrollTrigger: {
                    trigger: swapSection,
                    // Mesma faixa da dissolução das janelas: começa depois de
                    // o chat 1 sair de quadro e termina antes de o chat 2
                    // entrar, nos dois sentidos do scroll.
                    start: "top 85%",
                    end: "top 25%",
                    scrub: 0.9,
                },
            });

            // Aparecem, giram uma volta inteira e cruzam a tela.
            timeline
                .fromTo(root, { opacity: 0 }, { opacity: 1, ease: "none", duration: 0.18 }, 0)
                .fromTo(
                    ring,
                    { rotationX: 0 },
                    { rotationX: 360, ease: "none", duration: 1 },
                    0,
                )
                .fromTo(
                    group,
                    { xPercent: -55 },
                    { xPercent: 55, ease: "power1.inOut", duration: 1 },
                    0,
                )
                // Sobem para um plano acima no meio do trajeto e voltam a
                // assentar, menores, ao chegar do lado direito.
                .fromTo(
                    group,
                    { scale: 0.72, yPercent: 6 },
                    { scale: 1.05, yPercent: -8, ease: "power2.out", duration: 0.5 },
                    0,
                )
                .to(
                    group,
                    { scale: 0.78, yPercent: 0, ease: "power2.in", duration: 0.5 },
                    0.5,
                );

            // Já como fundo do chat 2, saem de cena quando a última seção chega.
            if (tryStage) {
                gsap.to(root, {
                    opacity: 0,
                    ease: "none",
                    scrollTrigger: {
                        trigger: tryStage,
                        start: "top 85%",
                        end: "top 35%",
                        scrub: 0.9,
                    },
                });
            }
        }, root);

        return () => ctx.revert();
    }, []);

    return (
        <div
            ref={rootRef}
            aria-hidden
            className="pointer-events-none fixed inset-0 z-0 flex items-center justify-center overflow-hidden opacity-0"
        >
            <div
                ref={groupRef}
                className="relative h-[62vh] w-[26vw] min-w-[240px] [perspective:1400px]"
            >
                <div ref={ringRef} className="absolute inset-0 [transform-style:preserve-3d]">
                    {RING.map((kind, index) => (
                        <div
                            key={`${kind}-${index}`}
                            className="absolute inset-0 flex items-center justify-center [transform-style:preserve-3d]"
                            style={{
                                transform: `rotateX(${(360 / RING.length) * index}deg) translateZ(${RADIUS}px)`,
                            }}
                        >
                            <div className="w-full opacity-[0.09]">
                                <DocumentGlyph kind={kind} />
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
