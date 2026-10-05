import { BellOff, Check, LoaderCircle, Sparkles, X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

import { Button } from '@/components/ui/button';
import type { ProactiveDecision } from '@/lib/api';
import type { ProactiveSuggestionState } from '@/lib/domain';

/**
 * Card da sugestao proativa (ocorrencia O8 da usabilidade).
 *
 * Na Sprint 4, um participante leu a sugestao como parte da resposta e outro
 * nao achou onde desligar a proatividade. Por isso o card se apresenta como uma
 * acao que precisa de confirmacao e reune, no mesmo lugar, aceitar, recusar e
 * desativar as proximas sugestoes. Desativar recusa a sugestao atual sem
 * executar nada e desliga o modo, que pode ser religado na engrenagem.
 */
export function ProactiveSuggestion({
  suggestion,
  onResolve,
  onDisable,
}: {
  suggestion: ProactiveSuggestionState;
  onResolve: (decision: ProactiveDecision) => void;
  /** Desliga as proximas sugestoes. Sem ele, o botao nao aparece. */
  onDisable?: () => void;
}) {
  const [disabledHere, setDisabledHere] = useState(false);
  const [actedHere, setActedHere] = useState(false);
  const statusRef = useRef<HTMLDivElement>(null);
  const resolving =
    suggestion.status === 'accepting' || suggestion.status === 'declining';
  const resolved = suggestion.status === 'accepted' || suggestion.status === 'declined';

  // Os botoes somem quando a sugestao e resolvida. Se o usuario agiu por aqui,
  // o foco vai para o resultado, em vez de cair no inicio da pagina.
  useEffect(() => {
    if (resolved && actedHere) statusRef.current?.focus();
  }, [resolved, actedHere]);

  const resolve = (decision: ProactiveDecision) => {
    setActedHere(true);
    onResolve(decision);
  };

  const disable = () => {
    setDisabledHere(true);
    setActedHere(true);
    onDisable?.();
    if (suggestion.status === 'pending') onResolve('decline');
  };

  return (
    <section
      aria-label="Ação sugerida"
      className="mt-4 rounded-xl border border-dashed border-primary/50 bg-primary-soft/40 p-3.5"
    >
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs font-semibold text-primary">
        <Sparkles size={14} />
        Ação sugerida
        <span className="font-normal text-fg-muted">· precisa da sua confirmação</span>
      </div>
      <p className="mt-2 text-sm leading-5 text-fg">{suggestion.description}</p>
      <p className="mt-1 text-xs leading-5 text-fg-muted">
        {suggestion.displayMessage}
      </p>

      {!resolved ? (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <Button
            type="button"
            size="sm"
            onClick={() => resolve('accept')}
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
            onClick={() => resolve('decline')}
            disabled={resolving}
          >
            {suggestion.status === 'declining' ? (
              <LoaderCircle size={13} className="animate-spin" />
            ) : (
              <X size={13} />
            )}
            Recusar sugestão
          </Button>
          {onDisable && (
            <Button
              type="button"
              size="sm"
              variant="ghost"
              onClick={disable}
              disabled={resolving}
              className="sm:ml-auto"
            >
              <BellOff size={13} />
              Não sugerir mais
            </Button>
          )}
        </div>
      ) : (
        <div
          ref={statusRef}
          tabIndex={-1}
          className="mt-3 space-y-2 rounded-md focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <p className="text-xs font-medium text-fg-muted" role="status">
            {suggestion.status === 'accepted'
              ? 'Sugestão aceita e executada.'
              : 'Sugestão recusada sem execução.'}
          </p>
          {disabledHere && <DisabledNotice />}
        </div>
      )}

      {disabledHere && !resolved && (
        <div className="mt-2">
          <DisabledNotice />
        </div>
      )}
    </section>
  );
}

function DisabledNotice() {
  return (
    <p className="text-xs text-fg-muted" role="status">
      Sugestões desligadas. Para religar, use{' '}
      <span className="font-medium text-fg">Ajustes do agente</span> no canto superior
      direito.
    </p>
  );
}
