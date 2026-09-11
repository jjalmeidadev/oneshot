import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

/** Evento disparado pela pasta de fontes quando ela entra ou é aberta. */
export const SOURCE_FOCUS_EVENT = "oneshot:source-focus";

export type GhostKind = "page" | "gantt" | "table";

interface Ghost {
    id: string;
    kind: GhostKind;
    /** Posição vertical dentro da zona cinza inteira. */
    top: string;
    side: "left" | "right";
    width: string;
    rotate: number;
    /** Multiplicador do deslocamento no parallax. */
    speed: number;
    opacity: number;
}

const GHOSTS: Ghost[] = [
    { id: "tap", kind: "page", top: "3%", side: "right", width: "34vw", rotate: -5, speed: 0.4, opacity: 0.05 },
    { id: "cronograma", kind: "gantt", top: "22%", side: "left", width: "44vw", rotate: 3, speed: 0.75, opacity: 0.045 },
    { id: "planilha", kind: "table", top: "45%", side: "right", width: "40vw", rotate: -2, speed: 0.55, opacity: 0.04 },
    { id: "normativo", kind: "page", top: "66%", side: "left", width: "30vw", rotate: 6, speed: 0.9, opacity: 0.05 },
    { id: "anexo", kind: "table", top: "84%", side: "right", width: "36vw", rotate: -4, speed: 0.65, opacity: 0.035 },
];

function PageGlyph() {
    return (
        <svg viewBox="0 0 300 400" fill="none" stroke="white" strokeWidth="2" className="h-auto w-full">
            <rect x="6" y="6" width="288" height="388" rx="14" />
            <rect x="34" y="46" width="150" height="18" rx="4" fill="white" stroke="none" />
            <rect x="34" y="80" width="90" height="10" rx="3" fill="white" stroke="none" />
            {Array.from({ length: 9 }, (_, i) => (
                <line key={i} x1="34" y1={130 + i * 26} x2={i % 3 === 2 ? 200 : 266} y2={130 + i * 26} />
            ))}
        </svg>
    );
}

function GanttGlyph() {
    const rows = [
        [20, 150],
        [70, 120],
        [50, 210],
        [140, 110],
        [110, 180],
        [190, 90],
    ];
    return (
        <svg viewBox="0 0 400 260" fill="none" stroke="white" strokeWidth="2" className="h-auto w-full">
            <line x1="0" y1="30" x2="400" y2="30" />
            {rows.map(([x, w], i) => (
                <g key={i}>
                    <rect x={x} y={54 + i * 32} width={w} height="14" rx="7" fill="white" stroke="none" />
                    <line x1="0" y1={78 + i * 32} x2="400" y2={78 + i * 32} strokeOpacity="0.4" />
                </g>
            ))}
        </svg>
    );
}

function TableGlyph() {
    return (
        <svg viewBox="0 0 360 280" fill="none" stroke="white" strokeWidth="2" className="h-auto w-full">
            <rect x="4" y="4" width="352" height="272" rx="10" />
            <rect x="4" y="4" width="352" height="46" rx="10" fill="white" fillOpacity="0.35" stroke="none" />
            {Array.from({ length: 5 }, (_, i) => (
                <line key={`r${i}`} x1="4" y1={96 + i * 46} x2="356" y2={96 + i * 46} />
            ))}
            {[92, 180, 268].map((x) => (
                <line key={`c${x}`} x1={x} y1="4" x2={x} y2="276" />
            ))}
        </svg>
    );
}

const GLYPHS: Record<GhostKind, () => React.ReactElement> = {
    page: PageGlyph,
    gantt: GanttGlyph,
    table: TableGlyph,
};

/** Reaproveitado pelo carrossel cilíndrico da transição entre os chats. */
export function DocumentGlyph({ kind }: { kind: GhostKind }) {
    const Glyph = GLYPHS[kind];
    return <Glyph />;
}

/**
 * Camada de fundo da zona cinza: silhuetas enormes e quase invisíveis dos
 * documentos que o assistente lê — TAP, cronograma, planilhas, normativos.
 * Elas derivam em parallax com o scroll e uma delas pulsa quando a pasta de
 * fontes aparece na conversa, ligando o fundo ao que está sendo dito.
 */
export default function GhostDocuments() {
    const layerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const layer = layerRef.current;
        if (!layer) return;

        const ctx = gsap.context(() => {
            gsap.utils.toArray<HTMLElement>("[data-ghost]").forEach((ghost) => {
                const speed = Number(ghost.dataset.speed ?? 0.5);
                gsap.to(ghost, {
                    yPercent: -30 * speed,
                    rotate: `+=${(speed - 0.5) * 8}`,
                    ease: "none",
                    scrollTrigger: {
                        trigger: layer,
                        start: "top bottom",
                        end: "bottom top",
                        scrub: 1.2,
                    },
                });
            });

            // A pasta de fontes entrou em cena: o TAP acende por um instante.
            const pulse = () => {
                const tap = layer.querySelector<HTMLElement>('[data-ghost="tap"]');
                if (!tap) return;
                const base = Number(tap.dataset.opacity ?? 0.05);
                gsap.fromTo(
                    tap,
                    { opacity: base },
                    {
                        opacity: base * 4,
                        duration: 0.8,
                        ease: "power2.out",
                        yoyo: true,
                        repeat: 1,
                        overwrite: true,
                    },
                );
            };

            window.addEventListener(SOURCE_FOCUS_EVENT, pulse);
            return () => window.removeEventListener(SOURCE_FOCUS_EVENT, pulse);
        }, layer);

        return () => ctx.revert();
    }, []);

    return (
        <div
            ref={layerRef}
            aria-hidden
            className="pointer-events-none absolute inset-0 select-none overflow-hidden"
        >
            {GHOSTS.map((ghost) => {
                const Glyph = GLYPHS[ghost.kind];
                return (
                    <div
                        key={ghost.id}
                        data-ghost={ghost.id}
                        data-speed={ghost.speed}
                        data-opacity={ghost.opacity}
                        className="absolute"
                        style={{
                            top: ghost.top,
                            width: ghost.width,
                            opacity: ghost.opacity,
                            transform: `rotate(${ghost.rotate}deg)`,
                            [ghost.side === "left" ? "left" : "right"]: "-4vw",
                        }}
                    >
                        <Glyph />
                    </div>
                );
            })}
        </div>
    );
}
