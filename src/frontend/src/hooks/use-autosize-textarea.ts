import { useLayoutEffect, useRef } from 'react';

/**
 * Faz o campo crescer com o conteudo ate um teto, mantendo a altura minima de
 * `rows` linhas. Acima do teto o proprio textarea rola.
 */
export function useAutosizeTextarea(value: string, rows = 1, maxHeight = 200) {
  const ref = useRef<HTMLTextAreaElement>(null);

  useLayoutEffect(() => {
    const element = ref.current;
    if (!element) return;

    const style = window.getComputedStyle(element);
    const lineHeight = Number.parseFloat(style.lineHeight) || 24;
    const padding =
      Number.parseFloat(style.paddingTop) + Number.parseFloat(style.paddingBottom);
    const minHeight = lineHeight * rows + padding;

    element.style.height = '0px';
    const next = Math.min(Math.max(element.scrollHeight, minHeight), maxHeight);
    element.style.height = `${next}px`;
    element.style.overflowY = element.scrollHeight > maxHeight ? 'auto' : 'hidden';
  }, [value, rows, maxHeight]);

  return ref;
}
