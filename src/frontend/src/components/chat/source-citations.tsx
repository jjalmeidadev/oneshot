import { FileText } from 'lucide-react';

import { cn } from '@/lib/utils';
import type { RetrievedDocument } from '@/lib/domain';

/**
 * Fontes citadas na resposta.
 *
 * A ordem e a mesma que `build_rag_input` usa ao numerar `[Fonte N]` no prompt,
 * entao o numero exibido aqui casa com a citacao que aparece no texto.
 * Clicar abre o documento no painel da direita. Quando a resposta se absteve
 * por falta de evidencia, as fontes continuam inspecionaveis, mas o rotulo
 * deixa claro que nao sustentam o texto exibido.
 */
export function SourceCitations({
  sources,
  selectedId,
  onSelect,
  unused = false,
}: {
  sources: RetrievedDocument[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  unused?: boolean;
}) {
  if (sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-3">
      <p className="pb-1.5 text-2xs font-semibold uppercase tracking-wide text-fg-subtle">
        {unused
          ? 'Fontes consultadas, sem evidência para esta resposta'
          : 'Fontes consultadas'}
      </p>
      <div className="flex flex-wrap gap-1.5">
        {sources.map((source) => {
          const selected = source.id === selectedId;
          return (
            <button
              key={source.id}
              type="button"
              onClick={() => onSelect(source.id)}
              title={`${source.title} — ${source.listName}`}
              className={cn(
                'inline-flex max-w-[19rem] items-center gap-1.5 rounded-lg border px-2 py-1 text-left text-2xs transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
                selected
                  ? 'border-primary bg-primary-soft text-primary'
                  : 'border-border bg-surface text-fg-muted hover:border-border-strong hover:text-fg',
              )}
            >
              <span
                className={cn(
                  'flex h-4 w-4 shrink-0 items-center justify-center rounded font-mono text-[10px] font-semibold',
                  selected ? 'bg-primary text-primary-fg' : 'bg-muted text-fg-subtle',
                )}
              >
                {source.citationOrder}
              </span>
              <FileText size={12} className="shrink-0" />
              <span className="truncate">{source.title}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
