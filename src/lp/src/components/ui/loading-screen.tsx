import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { markAppReady } from "@/lib/appReady";

gsap.registerPlugin(ScrollTrigger);

/** Tempo mínimo em tela, para a animação não piscar em conexões rápidas. */
const MIN_DURATION = 1400;

export default function LoadingScreen() {
    const curtainRef = useRef<HTMLDivElement>(null);
    const wordRef = useRef<HTMLSpanElement>(null);
    const metaRef = useRef<HTMLDivElement>(null);
    const [progress, setProgress] = useState(0);
    const [done, setDone] = useState(false);
    const [gone, setGone] = useState(false);

    // Progresso real: fontes prontas, página carregada e o tempo mínimo.
    // Nada de barra falsa — o número só chega a 100 quando os três fecham.
    useEffect(() => {
        const marks = { fonts: false, load: false, time: false };
        let target = 12;
        let shown = 0;
        let frame = 0;
        let finished = false;

        const recompute = () => {
            const all = marks.fonts && marks.load && marks.time;
            target = all
                ? 100
                : 12 + (marks.fonts ? 30 : 0) + (marks.load ? 34 : 0) + (marks.time ? 16 : 0);
        };

        document.fonts?.ready
            .then(() => {
                marks.fonts = true;
                recompute();
            })
            .catch(() => undefined);

        const onLoad = () => {
            marks.load = true;
            recompute();
        };
        if (document.readyState === "complete") onLoad();
        else window.addEventListener("load", onLoad, { once: true });

        const timer = window.setTimeout(() => {
            marks.time = true;
            recompute();
        }, MIN_DURATION);

        const tick = () => {
            shown += (target - shown) * 0.08;
            setProgress(Math.round(shown));
            if (!finished && target === 100 && shown > 99.4) {
                finished = true;
                setProgress(100);
                setDone(true);
                return;
            }
            frame = requestAnimationFrame(tick);
        };
        frame = requestAnimationFrame(tick);

        return () => {
            cancelAnimationFrame(frame);
            window.clearTimeout(timer);
            window.removeEventListener("load", onLoad);
        };
    }, []);

    // Segura a página no topo enquanto a cortina está em tela: as animações de
    // scroll não podem começar a contar antes do layout final.
    useEffect(() => {
        const previousOverflow = document.body.style.overflow;
        const previousRestoration = history.scrollRestoration;
        document.body.style.overflow = "hidden";
        history.scrollRestoration = "manual";
        window.scrollTo(0, 0);

        return () => {
            document.body.style.overflow = previousOverflow;
            history.scrollRestoration = previousRestoration;
        };
    }, []);

    // Saída: o wordmark encolhe até o lugar e o tamanho exatos do wordmark da
    // navbar (medição no estilo FLIP) e continua visível o tempo todo — quem
    // sobe é só a cortina, numa camada abaixo dele. Quando o loader sai de
    // cena, o wordmark real da navbar já está exatamente embaixo.
    useEffect(() => {
        if (!done) return;
        const curtain = curtainRef.current;
        const word = wordRef.current;
        if (!curtain || !word) return;

        const brand = document.querySelector<HTMLElement>("[data-brand-wordmark]");
        const from = word.getBoundingClientRect();
        let to = { x: 0, y: -60, scale: 0.12 };

        if (brand) {
            const target = brand.getBoundingClientRect();
            to = {
                x: target.left + target.width / 2 - (from.left + from.width / 2),
                y: target.top + target.height / 2 - (from.top + from.height / 2),
                scale: target.width / from.width,
            };
        }

        const timeline = gsap.timeline({
            onComplete: () => {
                document.body.style.overflow = "";
                window.scrollTo(0, 0);
                ScrollTrigger.refresh();
                setGone(true);
                // Libera as animações que precisam ser vistas para valer —
                // a escrita à mão do hero, por exemplo.
                markAppReady();
            },
        });

        timeline
            .to(metaRef.current, { opacity: 0, y: -16, duration: 0.35, ease: "power2.in" })
            .to(
                word,
                {
                    x: to.x,
                    y: to.y,
                    scale: to.scale,
                    duration: 1.2,
                    ease: "power4.inOut",
                },
                "-=0.15",
            )
            .to(curtain, { yPercent: -100, duration: 0.9, ease: "power4.inOut" }, "-=0.6");

        return () => {
            timeline.kill();
        };
    }, [done]);

    if (gone) return null;

    return (
        <>
            {/* Cortina: mesmo cinza das seções de chat, para a página não
                trocar de fundo no instante da entrega. */}
            <div ref={curtainRef} className="fixed inset-0 z-[100] bg-neutral-800">
                <div
                    ref={metaRef}
                    className="absolute inset-x-0 bottom-8 flex items-end justify-between px-6 text-xs uppercase tracking-widest text-white/40 md:px-10"
                >
                    <span>Carregando</span>
                    <span className="text-4xl leading-none font-medium tabular-nums text-white/70">
                        {progress}
                    </span>
                </div>
            </div>

            {/* O wordmark vive acima da cortina: ela sobe, ele fica. */}
            <div className="pointer-events-none fixed inset-0 z-[101] flex items-center justify-center overflow-hidden">
                <span
                    ref={wordRef}
                    className="block origin-center text-[22vw] leading-none font-medium tracking-tight text-white"
                >
                    OneShot
                </span>
            </div>
        </>
    );
}
