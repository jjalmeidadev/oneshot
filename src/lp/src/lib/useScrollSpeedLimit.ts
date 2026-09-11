import { useEffect } from "react";
import { isHolding, isProgrammaticScroll } from "@/lib/scrollHold";

/**
 * Deslocamento máximo por evento de scroll dentro da zona coreografada.
 * Uma "marcha" de roda do mouse anda ~100px, então o limite só morde em
 * lançadas rápidas e na inércia do trackpad.
 */
const MAX_STEP = 160;

/**
 * Limita a velocidade do scroll enquanto a zona coreografada está em tela.
 *
 * Sem isso, uma lançada rápida move a página centenas de pixels entre dois
 * quadros: os gatilhos disparam todos de uma vez, as animações presas ao
 * scroll pulam direto para o fim e depois voltam correndo. Com o teto, a
 * progressão é sempre a mesma — o gesto rápido vira um percurso rápido, não
 * um salto.
 *
 * Fica fora do caminho quando uma seção está segurando a página (a trava
 * dela é quem manda) e durante rolagens disparadas pelo próprio site.
 */
export function useScrollSpeedLimit(zoneSelector: string) {
    useEffect(() => {
        // O teto de velocidade existe para domar a inércia do trackpad. No
        // celular ele brigaria com a rolagem por impulso do próprio sistema,
        // que é justamente como se rola um telefone.
        if (
            typeof window.matchMedia === "function" &&
            window.matchMedia("(pointer: coarse)").matches
        ) {
            return;
        }

        const zone = document.querySelector<HTMLElement>(zoneSelector);
        if (!zone) return;

        let last = window.scrollY;

        const onScroll = () => {
            const y = window.scrollY;

            if (isHolding() || isProgrammaticScroll()) {
                last = y;
                return;
            }

            const rect = zone.getBoundingClientRect();
            const inZone = rect.top < window.innerHeight && rect.bottom > 0;
            const delta = y - last;

            if (inZone && Math.abs(delta) > MAX_STEP) {
                last += Math.sign(delta) * MAX_STEP;
                window.scrollTo({ top: last, behavior: "instant" as ScrollBehavior });
                return;
            }

            last = y;
        };

        window.addEventListener("scroll", onScroll, { passive: true });
        return () => window.removeEventListener("scroll", onScroll);
    }, [zoneSelector]);
}
