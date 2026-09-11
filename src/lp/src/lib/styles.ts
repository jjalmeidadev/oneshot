/**
 * "Liquid glass": a casca translúcida usada na navbar. Fica aqui para que
 * navbar e CTA compartilhem exatamente o mesmo tratamento — se um dia mudar,
 * muda nos dois.
 */
export const GLASS =
    "rounded-2xl border border-white/10 bg-white/5 shadow-lg backdrop-blur-xl";

/** Variante interativa: reage ao hover sem sair do mesmo material. */
export const GLASS_INTERACTIVE =
    "transition-all duration-300 hover:-translate-y-1 hover:border-white/25 hover:bg-white/10 hover:shadow-[0_20px_48px_-16px_rgba(255,255,255,0.25)]";
