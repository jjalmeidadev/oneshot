import { useEffect, useState } from "react";

/**
 * Verdadeiro em telas de toque (celular, tablet).
 *
 * Serve para desligar o que foi calibrado para tela larga e mouse: as camadas
 * de documentos voando, os cacos da janela, os avatares viajando. São enfeites
 * — num celular eles saem de proporção e não somam nada ao que o visitante
 * veio fazer, que é conversar com o agente.
 */
export function useCoarsePointer(): boolean {
    const [coarse, setCoarse] = useState(
        () =>
            typeof window !== "undefined" &&
            typeof window.matchMedia === "function" &&
            window.matchMedia("(pointer: coarse)").matches,
    );

    useEffect(() => {
        if (typeof window.matchMedia !== "function") return;
        const consulta = window.matchMedia("(pointer: coarse)");
        const aoMudar = (evento: MediaQueryListEvent) => setCoarse(evento.matches);
        consulta.addEventListener("change", aoMudar);
        return () => consulta.removeEventListener("change", aoMudar);
    }, []);

    return coarse;
}
