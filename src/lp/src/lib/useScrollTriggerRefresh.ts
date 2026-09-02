import { useEffect } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

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

        return () => {
            timers.forEach((timer) => window.clearTimeout(timer));
            window.removeEventListener("load", refresh);
        };
    }, []);
}
