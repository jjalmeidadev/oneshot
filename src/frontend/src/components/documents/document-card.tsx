import { FileText } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { formatDate } from '@/lib/format';
import type { RetrievedDocument } from '@/lib/domain';
import { cn } from '@/lib/utils';

export function DocumentCard({
  document,
  selected,
  onSelect,
}: {
  document: RetrievedDocument;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      aria-current={selected ? 'true' : undefined}
      className={cn(
        'w-full rounded-lg border px-2.5 py-2 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
        selected
          ? 'border-primary bg-primary-soft'
          : 'border-border bg-surface hover:border-border-strong hover:bg-muted',
      )}
    >
      <div className="flex items-start gap-2">
        <span
          className={cn(
            'mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded font-mono text-[10px] font-semibold',
            selected ? 'bg-primary text-primary-fg' : 'bg-muted text-fg-subtle',
          )}
        >
          {document.citationOrder}
        </span>

        <span className="min-w-0 flex-1">
          <span
            className={cn(
              'block truncate text-xs font-medium',
              selected ? 'text-primary' : 'text-fg',
            )}
          >
            {document.title}
          </span>
          <span className="flex items-center gap-1.5 pt-1 text-2xs text-fg-subtle">
            <FileText size={11} className="shrink-0" />
            <span className="truncate">{document.listName}</span>
          </span>
          <span className="flex items-center gap-1.5 pt-1.5">
            <Badge tone="outline">{formatDate(document.lastModified)}</Badge>
            <Badge tone={selected ? 'primary' : 'neutral'}>
              score {document.score.toFixed(2)}
            </Badge>
          </span>
        </span>
      </div>
    </button>
  );
}
