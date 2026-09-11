/**
 * Coordenação entre as coisas que escrevem a posição de scroll.
 *
 * Duas seções podem cruzar o seu gatilho no mesmo "voo" de scroll rápido —
 * sem um porteiro, as duas assumiriam a página ao mesmo tempo e as
 * conversas rodariam sobrepostas. Só uma seção segura a página por vez; a
 * outra tenta de novo na próxima passagem.
 *
 * O mesmo módulo marca as rolagens que o próprio site dispara (links da
 * navbar, "voltar ao chat", foco num card), para o limitador de velocidade
 * não brigar com elas.
 */
let holder: string | null = null;
let programmaticUntil = 0;

/** Tenta assumir a página. Falha se outra seção já está segurando. */
export function claimHold(id: string): boolean {
    if (holder !== null && holder !== id) return false;
    holder = id;
    return true;
}

export function releaseHold(id: string) {
    if (holder === id) holder = null;
}

export function isHolding(): boolean {
    return holder !== null;
}

/** Marca uma janela de tempo em que a rolagem é do próprio site. */
export function beginProgrammaticScroll(duration = 1200) {
    programmaticUntil = performance.now() + duration;
}

export function isProgrammaticScroll(): boolean {
    return performance.now() < programmaticUntil;
}
