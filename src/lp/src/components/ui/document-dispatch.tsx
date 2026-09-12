import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { DocumentGlyph, type GhostKind } from "@/components/ui/ghost-documents";

gsap.registerPlugin(ScrollTrigger);

/** Suavização do progresso, no mesmo espírito da janela de chat. */
const SMOOTHING = 0.14;
/** Largura de cada documento em voo. */
const DOC_WIDTH = 200;
/** Altura do arco que cada documento descreve no caminho. */
const ARC = 140;

interface FlyingDoc {
    kind: GhostKind;
    /** Deslocamento horizontal no ponto de partida. */
    offset: number;
    /** Fração do progresso em que este documento parte. */
    delay: number;
    spin: number;
}

/** Um documento por integração, na ordem dos cards. */
const DOCS: FlyingDoc[] = [
    { kind: "page", offset: -150, delay: 0, spin: -180 },
    { kind: "gantt", offset: 0, delay: 0.12, spin: 180 },
    { kind: "table", offset: 150, delay: 0.24, spin: -180 },
];

const clamp01 = (value: number) => Math.min(1, Math.max(0, value));
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
/** easeInOutCubic — a saída e a chegada precisam ser macias. */
const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

/**
 * O fecho do arco dos documentos.
 *
 * Eles entram no chat 2 como fonte das respostas e saem aqui como destino:
 * ao deixar a última seção de conversa, as silhuetas sobem de novo, se
 * separam e voam — cada uma girando sobre o próprio eixo, como no carrossel
 * — até um dos cards de integração, onde se dissolvem. A leitura é o
 * conteúdo saindo do assistente para ocupar as ferramentas.
 *
 * Camada fixa, montada antes da seção de integrações no DOM, para os
 * documentos passarem por trás dos cards em vez de por cima.
 */
export default function DocumentDispatch() {
    const rootRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const root = rootRef.current;
        if (!root) return;

        const integration = document.querySelector<HTMLElement>("#integracao");
        if (!integration) return;

        const ctx = gsap.context(() => {
            const docs = gsap.utils.toArray<HTMLElement>("[data-flying-doc]", root);
            // Busca fora do escopo do gsap.context: dentro dele todo seletor
            // é resolvido apenas entre os descendentes do root desta camada,
            // e os cards estão em outra seção — a busca voltava vazia e a
            // animação nem chegava a começar.
            const cards = Array.from(
                document.querySelectorAll<HTMLElement>("[data-integration-card]"),
            );
            if (docs.length === 0 || cards.length < docs.length) return;

            let targetProgress = 0;
            let progress = 0;

            const trigger = ScrollTrigger.create({
                trigger: integration,
                // Começa quando a seção de integrações aponta no rodapé — ou
                // seja, quando a última seção de conversa está se soltando — e
                // termina com os cards já em quadro.
                start: "top bottom",
                // Termina antes de a janela se partir: primeiro sai o
                // conteúdo, depois o recipiente.
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
                // Fora da faixa não há nada para desenhar.
                if (p <= 0.001 || p >= 0.999) {
                    gsap.set(root, { autoAlpha: 0 });
                    return;
                }
                gsap.set(root, { autoAlpha: 1 });

                const startX = window.innerWidth / 2;
                const startY = window.innerHeight / 2;

                docs.forEach((doc, index) => {
                    const config = DOCS[index];
                    const card = cards[index].getBoundingClientRect();

                    // Cada documento parte num instante diferente: eles se
                    // separam em vez de viajar em bloco.
                    const local = ease(clamp01((p - config.delay) / (0.72 - config.delay * 0.4)));

                    const targetX = card.left + card.width / 2;
                    const targetY = card.top + card.height / 2;

                    const x = lerp(startX + config.offset, targetX, local);
                    const y =
                        lerp(startY, targetY, local) - Math.sin(local * Math.PI) * ARC;

                    const height = doc.offsetHeight || DOC_WIDTH;

                    gsap.set(doc, {
                        x: x - DOC_WIDTH / 2,
                        y: y - height / 2,
                        scale: lerp(1, 0.34, local),
                        rotationY: config.spin * local,
                        rotation: lerp(index * 4 - 4, 0, local),
                        // Aparecem ao sair, apagam ao ser absorvidos pelo card.
                        opacity: 0.16 * clamp01(local / 0.12) * (1 - clamp01((local - 0.82) / 0.18)),
                    });
                });
            };

            render();
            gsap.ticker.add(render);

            return () => {
                gsap.ticker.remove(render);
                trigger.kill();
            };
        }, root);

        return () => ctx.revert();
    }, []);

    return (
        <div
            ref={rootRef}
            aria-hidden
            className="pointer-events-none fixed inset-0 z-0 overflow-hidden opacity-0 [perspective:1200px]"
        >
            {DOCS.map((doc, index) => (
                <div
                    key={`${doc.kind}-${index}`}
                    data-flying-doc
                    className="absolute top-0 left-0 w-[200px] [transform-style:preserve-3d]"
                >
                    <DocumentGlyph kind={doc.kind} />
                </div>
            ))}
        </div>
    );
}
