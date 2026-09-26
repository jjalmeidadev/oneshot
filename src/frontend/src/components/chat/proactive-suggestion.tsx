import { Check, LoaderCircle, Sparkles, X } from 'lucide-react';

import { Button } from '@/components/ui/button';
import type { ProactiveDecision } from '@/lib/api';
import type { ProactiveSuggestionState } from '@/lib/domain';

export function ProactiveSuggestion({
  suggestion,
  onResolve,
}: {
  suggestion: ProactiveSuggestionState;
  onResolve: (decision: ProactiveDecision) => void;
}) {
  const resolving =
    suggestion.status === 'accepting' || suggestion.status === 'declining';
  const resolved = suggestion.status === 'accepted' || suggestion.status === 'declined';

  return (
    <section
      aria-label="Sugestão opcional"
      className="mt-4 rounded-xl border border-primary/30 bg-primary-soft/40 p-3.5"
    >
      <div className="flex items-center gap-2 text-xs font-semibold text-primary">
        <Sparkles size={14} />
        Sugestão opcional
      </div>
      <p className="mt-2 text-sm leading-5 text-fg">{suggestion.description}</p>
      <p className="mt-1 text-xs leading-5 text-fg-muted">
        {suggestion.displayMessage}
      </p>

      {!resolved ? (
        <div className="mt-3 flex flex-wrap gap-2">
          <Button
            type="button"
            size="sm"
            onClick={() => onResolve('accept')}
            disabled={resolving}
          >
            {suggestion.status === 'accepting' ? (
              <LoaderCircle size={13} className="animate-spin" />
            ) : (
              <Check size={13} />
            )}
            Aceitar sugestão
          </Button>
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => onResolve('decline')}
            disabled={resolving}
          >
            {suggestion.status === 'declining' ? (
              <LoaderCircle size={13} className="animate-spin" />
            ) : (
              <X size={13} />
            )}
            Recusar sugestão
          </Button>
        </div>
      ) : (
        <p className="mt-3 text-xs font-medium text-fg-muted" role="status">
          {suggestion.status === 'accepted'
            ? 'Sugestão aceita e executada.'
            : 'Sugestão recusada sem execução.'}
        </p>
      )}
    </section>
  );
}
