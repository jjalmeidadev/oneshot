import { CircleSlash, Filter, ShieldAlert, Target } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Meter } from '@/components/ui/meter';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { formatConfidence } from '@/lib/format';
import { INTENT_THRESHOLDS, intentOutcome, type IntentResult } from '@/lib/domain';

const OUTCOME = {
  handler: {
    icon: Target,
    tone: 'success' as const,
    label: 'Handler específico',
    explanation:
      'As duas confianças passaram dos limiares: a solicitação aciona o handler dedicado da intenção.',
  },
  generic: {
    icon: Filter,
    tone: 'warning' as const,
    label: 'Fluxo genérico',
    explanation:
      'A macrointenção passou do limiar, mas a intenção específica não. A solicitação segue pelo fluxo genérico da macro, em vez de acionar um handler incerto.',
  },
  limitation: {
    icon: ShieldAlert,
    tone: 'danger' as const,
    label: 'Resposta de limitação',
    explanation:
      'A macrointenção ficou abaixo do limiar. O agente devolve a resposta controlada do RF08 sem chamar o modelo de linguagem.',
  },
  'out-of-scope': {
    icon: CircleSlash,
    tone: 'neutral' as const,
    label: 'Fora de escopo',
    explanation:
      'A solicitação foi classificada como fora do escopo do portfólio e recebe resposta controlada.',
  },
};

/** Selo compacto do resultado do classificador, exibido junto da resposta. */
export function IntentBadge({ intent }: { intent: IntentResult }) {
  const outcome = OUTCOME[intentOutcome(intent)];
  const Icon = outcome.icon;
  const label = intent.specific ?? intent.macro;

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <button type="button" className="focus-visible:outline-none">
          <Badge tone={outcome.tone}>
            <Icon size={11} />
            <span className="font-mono">{label}</span>
            <span className="opacity-70">
              {formatConfidence(
                intent.specific ? intent.specificConfidence : intent.macroConfidence,
              )}
            </span>
          </Badge>
        </button>
      </TooltipTrigger>
      <TooltipContent side="top" align="start" className="w-72">
        <p className="font-medium">{outcome.label}</p>
        <p className="mt-1 text-fg-muted">{outcome.explanation}</p>

        <dl className="mt-2.5 space-y-2">
          <div>
            <div className="flex items-baseline justify-between gap-2">
              <dt className="text-fg-muted">Macrointenção · {intent.macro}</dt>
              <dd className="font-mono text-2xs">
                {formatConfidence(intent.macroConfidence)}
              </dd>
            </div>
            <Meter
              value={intent.macroConfidence}
              threshold={INTENT_THRESHOLDS.macro}
              tone={
                intent.macroConfidence >= INTENT_THRESHOLDS.macro ? 'success' : 'danger'
              }
              label="Confiança da macrointenção"
              className="mt-1"
            />
          </div>
          <div>
            <div className="flex items-baseline justify-between gap-2">
              <dt className="text-fg-muted">Intenção específica</dt>
              <dd className="font-mono text-2xs">
                {formatConfidence(intent.specificConfidence)}
              </dd>
            </div>
            <Meter
              value={intent.specificConfidence}
              threshold={INTENT_THRESHOLDS.specific}
              tone={
                intent.specificConfidence >= INTENT_THRESHOLDS.specific
                  ? 'success'
                  : 'warning'
              }
              label="Confiança da intenção específica"
              className="mt-1"
            />
          </div>
        </dl>

        <p className="mt-2 text-2xs text-fg-subtle">
          Limiares calibrados na validação: {INTENT_THRESHOLDS.macro} para a
          macrointenção e {INTENT_THRESHOLDS.specific} para a intenção.
        </p>
      </TooltipContent>
    </Tooltip>
  );
}
