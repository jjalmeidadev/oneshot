import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

const COLS = 4;
const ROWS = 3;
const TILES = Array.from({ length: COLS * ROWS }, (_, index) => ({
    row: Math.floor(index / COLS),
    col: index % COLS,
}));

/** Suavização do progresso, no mesmo espírito da janela de chat. */
const SMOOTHING = 0.14;
/** Fração do percurso em que os cacos começam a se separar. */
const BREAK_AT = 0.3;
/** Tamanho de cada caco em relação à sua célula — a folga vira a fresta. */
const TILE_SCALE = 0.9;

const clamp01 = (value: number) => Math.min(1, Math.max(0, value));
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

/**
 * A janela de chat se fragmentando nos blocos das integrações.
 *
 * Os cacos são peças reais posicionadas exatamente sobre a janela, com o
 * mesmo material dela: a janela apaga nos primeiros instantes e o mosaico
 * assume o lugar sem que se perceba a troca. Depois cada caco se solta, gira
 * um pouco e viaja até o card da integração correspondente, apagando na
 * chegada — os cards entram justamente nesse momento, então a leitura é que
 * a janela virou os blocos.
 *
 * Como o destino é medido a cada quadro, os cacos acompanham os cards mesmo
 * enquanto a página continua rolando.
 */
export default function ChatFragments() {
    const rootRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const root = rootRef.current;
        if (!root) return;

        const integration = document.querySelector<HTMLElement>("#integracao");
        const chatWindow = document.querySelector<HTMLElement>('[data-chat-panel="to"]');
        if (!integration || !chatWindow) return;

        const ctx = gsap.context(() => {
            const tiles = gsap.utils.toArray<HTMLElement>("[data-fragment]", root);
            // Busca fora do escopo do gsap.context: dentro dele todo seletor
            // é resolvido apenas entre os descendentes do root desta camada,
            // e os cards estão em outra seção — a busca voltava vazia e a
            // animação nem chegava a começar.
            const cards = Array.from(
                document.querySelectorAll<HTMLElement>("[data-integration-card]"),
            );
            if (tiles.length === 0 || cards.length === 0) return;

            let targetProgress = 0;
            let progress = 0;
            let lastWindowFade = 1;

            const trigger = ScrollTrigger.create({
                trigger: integration,
                start: "top bottom",
                end: "top 15%",
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

                // A janela apaga no começo do percurso; o mosaico entra no
                // lugar dela. A opacidade só é escrita quando muda, para não
                // disputar com a timeline que traz a janela da seção 1 para a 2.
                // Fade longo e sobreposto ao dos cacos: a janela e o mosaico
                // se cruzam em vez de um substituir o outro num quadro.
                const windowFade = 1 - clamp01((p - 0.04) / 0.26);
                if (Math.abs(windowFade - lastWindowFade) > 0.001) {
                    gsap.set(chatWindow, { opacity: windowFade });
                    lastWindowFade = windowFade;
                }

                if (p <= 0.001 || p >= 0.999) {
                    gsap.set(root, { autoAlpha: 0 });
                    return;
                }
                gsap.set(root, { autoAlpha: 1 });

                const source = chatWindow.getBoundingClientRect();
                const cellWidth = source.width / COLS;
                const cellHeight = source.height / ROWS;
                const tileWidth = cellWidth * TILE_SCALE;
                const tileHeight = cellHeight * TILE_SCALE;

                tiles.forEach((tile, index) => {
                    const { row, col } = TILES[index];

                    // Quebra em cascata, a partir do canto superior esquerdo.
                    const stagger = (row + col) * 0.03;
                    const local = ease(clamp01((p - BREAK_AT - stagger) / (0.62 - stagger)));
                    // Entrada: cada caco surge no seu tempo, ainda por cima da
                    // janela acesa — o mosaico se forma, não aparece pronto.
                    const appear = ease(clamp01((p - 0.03 - stagger * 0.4) / 0.3));

                    // Cada coluna de cacos vai para um card; com quatro
                    // colunas e três cards, o meio se divide entre os dois
                    // centrais, o que embaralha um pouco as trajetórias.
                    const card = cards[Math.min(cards.length - 1, Math.round((col / (COLS - 1)) * (cards.length - 1)))];
                    const destination = card.getBoundingClientRect();

                    const homeX = source.left + col * cellWidth + (cellWidth - tileWidth) / 2;
                    const homeY = source.top + row * cellHeight + (cellHeight - tileHeight) / 2;
                    const targetWidth = tileWidth * 0.22;
                    const targetHeight = tileHeight * 0.22;
                    const targetX =
                        destination.left + destination.width / 2 - targetWidth / 2 + (col - 1.5) * 10;
                    const targetY =
                        destination.top + destination.height / 2 - targetHeight / 2 + (row - 1) * 10;

                    gsap.set(tile, {
                        left: lerp(homeX, targetX, local),
                        top: lerp(homeY, targetY, local),
                        width: lerp(tileWidth, targetWidth, local),
                        height: lerp(tileHeight, targetHeight, local),
                        rotation: lerp(0, (col - 1.5) * 9 + (row - 1) * 4, local),
                        borderRadius: lerp(6, 14, local),
                        opacity: appear * (1 - clamp01((local - 0.55) / 0.45)),
                    });
                });
            };

            render();
            gsap.ticker.add(render);

            return () => {
                gsap.ticker.remove(render);
                trigger.kill();
                gsap.set(chatWindow, { opacity: 1 });
            };
        }, root);

        return () => ctx.revert();
    }, []);

    return (
        <div
            ref={rootRef}
            aria-hidden
            className="pointer-events-none fixed inset-0 z-0 overflow-hidden opacity-0"
        >
            {TILES.map(({ row, col }) => (
                <div
                    key={`${row}-${col}`}
                    data-fragment
                    // Mesmo material da janela de chat, para a troca entre ela
                    // e o mosaico não aparecer.
                    className="absolute border border-white/10 bg-gradient-to-b from-zinc-900 to-zinc-950 shadow-[0_16px_40px_-16px_rgba(0,0,0,0.6)] backdrop-blur-sm"
                />
            ))}
        </div>
    );
}
