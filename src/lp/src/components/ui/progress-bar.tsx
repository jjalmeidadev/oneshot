import { useEffect, useRef } from "react";

/**
 * Barra fina de progresso no topo da página.
 *
 * A barra de rolagem nativa está escondida, então não havia mais nenhuma
 * pista de "quanto falta" — isso devolve o sinal sem devolver o traço cinza
 * do navegador. Atualiza num rAF para não pesar durante as coreografias.
 */
export default function ProgressBar() {
    const barRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const bar = barRef.current;
        if (!bar) return;

        let frame = 0;
        let queued = false;

        const update = () => {
            queued = false;
            const max = document.documentElement.scrollHeight - window.innerHeight;
            const value = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
            bar.style.transform = `scaleX(${value})`;
        };

        const onScroll = () => {
            if (queued) return;
            queued = true;
            frame = requestAnimationFrame(update);
        };

        update();
        window.addEventListener("scroll", onScroll, { passive: true });
        window.addEventListener("resize", onScroll);

        return () => {
            cancelAnimationFrame(frame);
            window.removeEventListener("scroll", onScroll);
            window.removeEventListener("resize", onScroll);
        };
    }, []);

    return (
        <div
            aria-hidden
            className="pointer-events-none fixed inset-x-0 top-0 z-[60] h-[3px] bg-white/5"
        >
            <div
                ref={barRef}
                className="h-full origin-left bg-gradient-to-r from-indigo-400 to-violet-400"
                style={{ transform: "scaleX(0)" }}
            />
        </div>
    );
}
