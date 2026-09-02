import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { AnimatePresence, motion } from "motion/react";
import { cn } from "@/lib/utils";

gsap.registerPlugin(ScrollTrigger);

interface Integration {
    id: string;
    name: string;
    logo: string;
    detail: string;
    points: string[];
}

const INTEGRATIONS: Integration[] = [
    {
        id: "copilot-studio",
        name: "Copilot Studio",
        logo: "/copilot.png",
        detail: "Orquestra o agente que responde sobre o portfólio.",
        points: [
            "Fluxos de conversa e tópicos do assistente.",
            "Conexão com a base de documentos do portfólio.",
        ],
    },
    {
        id: "teams",
        name: "Microsoft Teams",
        logo: "/teams.svg",
        detail: "Leva o OneShot para o canal onde o time já conversa.",
        points: [
            "Perguntas direto no chat, sem trocar de ferramenta.",
            "Respostas com a fonte anexada na própria conversa.",
        ],
    },
    {
        id: "power-bi",
        name: "Power BI",
        logo: "/power-bi.svg",
        detail: "Alimenta os painéis com os indicadores do portfólio.",
        points: [
            "Indicadores de andamento consolidados por projeto.",
            "Mesma base de dados que sustenta as respostas.",
        ],
    },
];

/** Uma "cópia" do loop: itens suficientes para cobrir telas largas. */
const SEQUENCE = [...INTEGRATIONS, ...INTEGRATIONS, ...INTEGRATIONS];

export default function IntegrationSection() {
    const sectionRef = useRef<HTMLElement>(null);
    const trackRef = useRef<HTMLDivElement>(null);
    const cardsRef = useRef<Record<string, HTMLDivElement | null>>({});
    const [expanded, setExpanded] = useState<string | null>(null);

    useEffect(() => {
        const section = sectionRef.current;
        const track = trackRef.current;
        if (!section || !track) return;

        const ctx = gsap.context(() => {
            // Loop infinito: o track tem duas cópias idênticas, então deslocar
            // 50% da própria largura recoloca a segunda exatamente onde a
            // primeira começou — a emenda não aparece.
            const loop = gsap.timeline({ repeat: -1 }).to(track, {
                xPercent: -50,
                duration: 30,
                ease: "none",
            });

            // A faixa reage ao scroll: acelera conforme a velocidade da
            // rolagem, inverte quando a página sobe e volta sozinha ao ritmo
            // base quando o scroll para.
            const speedFor = gsap.utils.clamp(1, 8);
            ScrollTrigger.create({
                trigger: section,
                start: "top bottom",
                end: "bottom top",
                onUpdate: (self) => {
                    const direction = self.direction || 1;
                    const boost = speedFor(1 + Math.abs(self.getVelocity()) / 400);
                    loop.timeScale(direction * boost);
                    gsap.to(loop, {
                        timeScale: direction,
                        duration: 1.1,
                        ease: "power2.out",
                        overwrite: true,
                    });
                },
            });

            gsap.from("[data-integration-card]", {
                y: 40,
                opacity: 0,
                duration: 0.8,
                ease: "power3.out",
                stagger: 0.12,
                scrollTrigger: { trigger: "[data-integration-cards]", start: "top 85%" },
            });
        }, section);

        return () => ctx.revert();
    }, []);

    const focusCard = (id: string) => {
        setExpanded(id);
        cardsRef.current[id]?.scrollIntoView({ behavior: "smooth", block: "center" });
    };

    return (
        <section
            ref={sectionRef}
            id="integracao"
            className="relative flex w-full flex-col gap-16 overflow-hidden py-24"
        >
            <div className="mx-auto flex w-full max-w-6xl flex-col gap-3 px-6 md:px-16">

                <h2 className="max-w-2xl text-3xl font-medium text-indigo-300 lg:text-4.5xl">
                    Onde o OneShot vai viver
                </h2>
            </div>

            {/* Faixa em loop — clicar em qualquer logo leva ao card dela. */}
            <div className="relative w-full overflow-hidden py-4">
                <div ref={trackRef} className="flex w-max items-center">
                    {[0, 1].map((copy) => (
                        <div key={copy} className="flex w-max items-center" aria-hidden={copy === 1}>
                            {SEQUENCE.map((item, index) => (
                                <button
                                    key={`${copy}-${item.id}-${index}`}
                                    type="button"
                                    onClick={() => focusCard(item.id)}
                                    className="group flex shrink-0 items-center gap-5 px-6"
                                >
                                    <span className="flex size-14 items-center justify-center rounded-2xl bg-white p-2.5 transition-transform duration-300 group-hover:-translate-y-1">
                                        <img src={item.logo} alt="" className="h-full w-full object-contain" />
                                    </span>
                                    <span className="whitespace-nowrap text-3xl font-medium text-white/80 transition-colors duration-300 group-hover:text-white lg:text-5xl">
                                        {item.name}
                                    </span>
                                    <span className="text-2xl text-indigo-300/60 lg:text-3xl" aria-hidden>
                                        ✛
                                    </span>
                                </button>
                            ))}
                        </div>
                    ))}
                </div>
            </div>

            <div
                data-integration-cards
                className="mx-auto grid w-full max-w-6xl gap-6 px-6 md:grid-cols-3 md:px-16"
            >
                {INTEGRATIONS.map((item) => {
                    const isOpen = expanded === item.id;
                    return (
                        <div
                            key={item.id}
                            data-integration-card
                            ref={(node) => {
                                cardsRef.current[item.id] = node;
                            }}
                        >
                            <button
                                type="button"
                                onClick={() => setExpanded(isOpen ? null : item.id)}
                                aria-expanded={isOpen}
                                className={cn(
                                    "flex h-full w-full flex-col items-start gap-4 rounded-2xl border p-6 text-left transition-all duration-300",
                                    isOpen
                                        ? "border-indigo-400/60 bg-white/10 shadow-[0_24px_64px_-16px_rgba(79,70,229,0.45)]"
                                        : "border-white/10 bg-white/5 hover:border-white/25 hover:bg-white/10",
                                )}
                            >
                                <span className="flex size-12 items-center justify-center rounded-xl bg-white p-2">
                                    <img src={item.logo} alt="" className="h-full w-full object-contain" />
                                </span>

                                <span className="text-lg font-medium text-white">{item.name}</span>
                                <span className="text-sm font-normal leading-relaxed text-white/60">
                                    {item.detail}
                                </span>

                                <AnimatePresence initial={false}>
                                    {isOpen && (
                                        <motion.ul
                                            initial={{ height: 0, opacity: 0 }}
                                            animate={{ height: "auto", opacity: 1 }}
                                            exit={{ height: 0, opacity: 0 }}
                                            transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
                                            className="flex w-full flex-col gap-2 overflow-hidden text-sm font-normal text-white/70"
                                        >
                                            {item.points.map((point) => (
                                                <li key={point} className="flex gap-2 pt-2">
                                                    <span className="text-indigo-300">—</span>
                                                    <span>{point}</span>
                                                </li>
                                            ))}
                                        </motion.ul>
                                    )}
                                </AnimatePresence>

                                <span className="mt-auto pt-4 text-xs font-medium uppercase tracking-widest text-indigo-300">
                                    {isOpen ? "Fechar" : "Ver detalhes"}
                                </span>
                            </button>
                        </div>
                    );
                })}
            </div>
        </section>
    );
}
