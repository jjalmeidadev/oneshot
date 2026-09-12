import { useEffect, useState } from "react";

export const APP_READY_EVENT = "oneshot:ready";

let ready = false;

/** Chamado pela cortina de abertura quando ela termina de sair. */
export function markAppReady() {
    if (ready) return;
    ready = true;
    window.dispatchEvent(new CustomEvent(APP_READY_EVENT));
}

export function isAppReady() {
    return ready;
}

/**
 * Verdadeiro depois que a cortina de abertura saiu de cena.
 *
 * Serve para animações que só fazem sentido sendo vistas: se elas rodam por
 * trás da cortina, terminam antes de a página aparecer e o visitante nunca
 * as vê. O tempo limite é uma rede de segurança — se a cortina for removida
 * ou falhar, a página continua funcionando.
 */
export function useAppReady(fallbackMs = 6000): boolean {
    const [value, setValue] = useState(isAppReady);

    useEffect(() => {
        if (value) return;

        const onReady = () => setValue(true);
        window.addEventListener(APP_READY_EVENT, onReady);
        const timer = window.setTimeout(() => {
            markAppReady();
            setValue(true);
        }, fallbackMs);

        return () => {
            window.removeEventListener(APP_READY_EVENT, onReady);
            window.clearTimeout(timer);
        };
    }, [value, fallbackMs]);

    return value;
}
