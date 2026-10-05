import { useEffect, useState } from 'react';

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(
    () => typeof window !== 'undefined' && window.matchMedia(query).matches,
  );

  useEffect(() => {
    const media = window.matchMedia(query);
    const onChange = (event: MediaQueryListEvent) => setMatches(event.matches);
    setMatches(media.matches);
    media.addEventListener('change', onChange);
    return () => media.removeEventListener('change', onChange);
  }, [query]);

  return matches;
}

/**
 * Pontos de quebra do layout (S5-21), alinhados aos do Tailwind:
 *
 * - abaixo de 1024 px (celular e tablet): so o chat; conversas e fontes abrem
 *   como paineis deslizantes;
 * - de 1024 a 1279 px (tablet deitado e notebook pequeno): conversas fixas a
 *   esquerda; fontes como painel deslizante, para o chat nao ficar espremido;
 * - a partir de 1280 px: conversas, chat e fontes lado a lado.
 */
export const BREAKPOINTS = { desktop: 1024, wide: 1280 } as const;

/** `true` a partir do ponto em que a barra de conversas fica fixa. */
export function useIsDesktop(): boolean {
  return useMediaQuery(`(min-width: ${BREAKPOINTS.desktop}px)`);
}

/** `true` a partir do ponto em que os tres paineis cabem lado a lado. */
export function useIsWide(): boolean {
  return useMediaQuery(`(min-width: ${BREAKPOINTS.wide}px)`);
}
