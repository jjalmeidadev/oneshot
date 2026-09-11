import { useEffect } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { APP_READY_EVENT } from "@/lib/appReady";

gsap.registerPlugin(ScrollTrigger);

/**
 * Recomputes every ScrollTrigger start/end once the page has really settled.
 *
 * The triggers are created on mount, when web fonts, the shader canvas and the
 * tall sticky section may not have their final heights yet. A trigger measured
 * against that early layout fires at the wrong scroll offset — which showed up
 * as animations running well before they should.
 */
export function useScrollTriggerRefresh() {
    useEffect(() => {
        const refresh = () => ScrollTrigger.refresh();

        const timers = [200, 800, 2000].map((delay) => window.setTimeout(refresh, delay));
        window.addEventListener("load", refresh);
        document.fonts?.ready.then(refresh).catch(() => undefined);

        // O mais importante deles: enquanto a cortina de abertura está em
        // cena o `body` fica com `overflow: hidden`, e os gatilhos medidos aí
        // saem errados — era o que fazia animações dispararem em posições que
        // não correspondiam à página. Aqui refazemos a conta depois que ela
        // sai, no quadro seguinte e mais uma vez logo em seguida.
        const onReady = () => {
            requestAnimationFrame(refresh);
            timers.push(window.setTimeout(refresh, 600));
        };
        window.addEventListener(APP_READY_EVENT, onReady);

        return () => {
            timers.forEach((timer) => window.clearTimeout(timer));
            window.removeEventListener("load", refresh);
            window.removeEventListener(APP_READY_EVENT, onReady);
        };
    }, []);
}
