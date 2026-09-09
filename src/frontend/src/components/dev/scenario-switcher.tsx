import { FlaskConical } from 'lucide-react';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { SCENARIOS, type ScenarioId } from '@/data/scenarios';
import { useChatStore } from '@/state/chat-store';

/**
 * Alternador de estados da interface.
 *
 * COMPONENTE DESCARTAVEL. Existe para revisar visualmente os estados que
 * dependem de condicoes especificas do backend. Ao integrar, remova este
 * componente, `data/scenarios.ts` e o campo `scenario` da store.
 */
export function ScenarioSwitcher() {
  const { scenario, setScenario } = useChatStore();
  const current = SCENARIOS.find((item) => item.id === scenario);

  return (
    <div className="rounded-lg border border-dashed border-border-strong bg-muted p-2">
      <div className="flex items-center gap-1.5 pb-1.5">
        <FlaskConical size={12} className="shrink-0 text-fg-subtle" />
        <span className="text-2xs font-semibold uppercase tracking-wide text-fg-subtle">
          Estado da interface
        </span>
        <Tooltip>
          <TooltipTrigger asChild>
            <button
              type="button"
              className="ml-auto rounded px-1 text-2xs text-fg-subtle underline decoration-dotted underline-offset-2 hover:text-fg"
            >
              o que é isto?
            </button>
          </TooltipTrigger>
          <TooltipContent side="top" align="end">
            Controle apenas de desenvolvimento, para revisar estados que dependem do
            backend sem provocá-los de verdade. Some quando a integração for feita.
          </TooltipContent>
        </Tooltip>
      </div>

      <select
        value={scenario}
        onChange={(event) => setScenario(event.target.value as ScenarioId)}
        aria-label="Estado da interface para revisão"
        className="h-8 w-full rounded-md border border-border bg-surface px-2 text-2xs text-fg outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        {SCENARIOS.map((item) => (
          <option key={item.id} value={item.id}>
            {item.label}
          </option>
        ))}
      </select>

      {current && (
        <p className="pt-1.5 text-2xs leading-4 text-fg-subtle">
          {current.description}
        </p>
      )}
    </div>
  );
}
