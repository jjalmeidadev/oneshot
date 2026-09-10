import { Activity, Brain, Coins, Database, Tags } from 'lucide-react';

import { EmptyState } from '@/components/ui/empty-state';
import { Meter } from '@/components/ui/meter';
import { Separator } from '@/components/ui/separator';
import { RESPONSE_BUDGET_MS } from '@/lib/api/constants';
import { INTENT_THRESHOLDS, intentOutcome, type ChatMessage } from '@/lib/domain';
import { formatConfidence, formatMilliseconds, formatNumber } from '@/lib/format';

const OUTCOME_LABEL: Record<ReturnType<typeof intentOutcome>, string> = {
  handler: 'Intenção específica identificada',
  generic: 'Fluxo genérico da macrointenção',
  limitation: 'Resposta de limitação (RF08)',
  'out-of-scope': 'Fora de escopo',
};

/**
 * Detalhes da ultima resposta: latencias, consumo de tokens e o resultado do
 * classificador. Todos os numeros vem da propria resposta da API — nenhum e
 * medido ou estimado pela interface, exceto `roundTripMs`, que e o tempo total
 * medido pelo navegador.
 */
export function ResponseDetails({ message }: { message: ChatMessage | null }) {
  if (!message) {
    return (
      <EmptyState
        compact
        icon={Activity}
        title="Sem resposta ainda"
        description="Os detalhes aparecem depois da primeira resposta do agente."
      />
    );
  }

  const { metrics, intent, entities } = message;

  return (
    <div className="space-y-4 px-3 py-3">
      {intent && (
        <section>
          <SectionTitle icon={Brain}>Classificação de intenção</SectionTitle>

          <div className="rounded-lg border border-border bg-surface p-2.5">
            <p className="text-2xs font-medium text-fg">
              {OUTCOME_LABEL[intentOutcome(intent)]}
            </p>
            <p className="pt-0.5 font-mono text-2xs text-fg-subtle">{intent.handler}</p>
            {intent.flow && (
              <p className="pt-1 text-2xs leading-4 text-fg-muted">{intent.flow}</p>
            )}

            <div className="space-y-2.5 pt-3">
              <ConfidenceRow
                label={`Macrointenção · ${intent.macro}`}
                value={intent.macroConfidence}
                threshold={INTENT_THRESHOLDS.macro}
              />
              <ConfidenceRow
                label={`Intenção · ${intent.specific ?? 'não confirmada'}`}
                value={intent.specificConfidence}
                threshold={INTENT_THRESHOLDS.specific}
              />
            </div>

            {intent.alternatives.length > 0 && (
              <>
                <Separator className="my-2.5" />
                <p className="pb-1.5 text-2xs font-semibold uppercase tracking-wide text-fg-subtle">
                  Alternativas consideradas
                </p>
                <ul className="space-y-1">
                  {intent.alternatives.map((alternative) => (
                    <li
                      key={alternative.intent}
                      className="flex items-center gap-2 text-2xs"
                    >
                      <span className="min-w-0 flex-1 truncate font-mono text-fg-muted">
                        {alternative.intent}
                      </span>
                      <span className="shrink-0 tabular-nums text-fg-subtle">
                        {formatConfidence(alternative.confidence)}
                      </span>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </div>
        </section>
      )}

      {entities && entities.length > 0 && (
        <section>
          <SectionTitle icon={Tags}>Entidades extraídas</SectionTitle>
          <div className="rounded-lg border border-border bg-surface p-2.5">
            <ul className="space-y-1.5">
              {entities.map((entity) => (
                <li
                  key={`${entity.type}:${entity.start}:${entity.end}`}
                  className="flex items-start justify-between gap-2 text-2xs"
                >
                  <span className="min-w-0">
                    <span className="font-medium text-fg">{entity.value}</span>
                    <span className="pl-1 text-fg-subtle">({entity.text})</span>
                  </span>
                  <span className="shrink-0 rounded-full bg-muted px-1.5 py-0.5 font-mono text-[10px] leading-none text-fg-muted">
                    {entity.ambiguous ? `${entity.type}*` : entity.type}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}

      {metrics ? (
        <>
          <section>
            <SectionTitle icon={Activity}>Latência</SectionTitle>
            <div className="rounded-lg border border-border bg-surface p-2.5">
              <MetricRow
                label="Chamada ao provedor"
                value={formatMilliseconds(metrics.latencyMs)}
              />
              <MetricRow
                label="Recuperação no RAG"
                value={formatMilliseconds(metrics.retrievalMs)}
              />
              <MetricRow
                label="Total, medido no navegador"
                value={formatMilliseconds(metrics.roundTripMs)}
              />
              {metrics.validationMs !== undefined && (
                <MetricRow
                  label="Validação do áudio"
                  value={formatMilliseconds(metrics.validationMs)}
                />
              )}
              {metrics.sttMs !== undefined && (
                <MetricRow
                  label="Transcrição STT"
                  value={formatMilliseconds(metrics.sttMs)}
                />
              )}
              {metrics.nlpMs !== undefined && (
                <MetricRow label="PLN" value={formatMilliseconds(metrics.nlpMs)} />
              )}
              {metrics.routeMs !== undefined && (
                <MetricRow
                  label="Roteamento"
                  value={formatMilliseconds(metrics.routeMs)}
                />
              )}
              {metrics.backendTotalMs !== undefined && (
                <MetricRow
                  label="Total no backend"
                  value={formatMilliseconds(metrics.backendTotalMs)}
                />
              )}
              <div className="pt-2">
                <Meter
                  value={metrics.roundTripMs / RESPONSE_BUDGET_MS}
                  tone={
                    metrics.roundTripMs > RESPONSE_BUDGET_MS
                      ? 'danger'
                      : metrics.roundTripMs > RESPONSE_BUDGET_MS * 0.7
                        ? 'warning'
                        : 'success'
                  }
                  label="Uso do orçamento de latência"
                />
                <p className="pt-1 text-2xs text-fg-subtle">
                  Orçamento de {formatMilliseconds(RESPONSE_BUDGET_MS)} por consulta
                  simples (RNF05)
                </p>
              </div>
            </div>
          </section>

          <section>
            <SectionTitle icon={Coins}>Consumo de tokens</SectionTitle>
            <div className="rounded-lg border border-border bg-surface p-2.5">
              <MetricRow label="Entrada" value={formatNumber(metrics.inputTokens)} />
              <MetricRow label="Saída" value={formatNumber(metrics.outputTokens)} />
              <MetricRow
                label="Raciocínio"
                value={formatNumber(metrics.thoughtTokens)}
              />
              <Separator className="my-1.5" />
              <MetricRow
                label="Total"
                value={formatNumber(metrics.totalTokens)}
                strong
              />
              <p className="pt-2 text-2xs text-fg-subtle">
                Modelo <span className="font-mono">{metrics.model}</span>
              </p>
            </div>
          </section>
        </>
      ) : (
        <section>
          <SectionTitle icon={Database}>Latência e tokens</SectionTitle>
          <p className="rounded-lg border border-dashed border-border-strong bg-muted px-2.5 py-2 text-2xs leading-4 text-fg-muted">
            Sem métricas: a solicitação não chegou ao modelo de linguagem.
          </p>
        </section>
      )}
    </div>
  );
}

function SectionTitle({
  icon: Icon,
  children,
}: {
  icon: typeof Activity;
  children: string;
}) {
  return (
    <h3 className="flex items-center gap-1.5 pb-1.5 text-2xs font-semibold uppercase tracking-wide text-fg-subtle">
      <Icon size={12} />
      {children}
    </h3>
  );
}

function MetricRow({
  label,
  value,
  strong = false,
}: {
  label: string;
  value: string;
  strong?: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-2 py-0.5 text-2xs">
      <span className="text-fg-muted">{label}</span>
      <span
        className={
          strong
            ? 'shrink-0 font-semibold tabular-nums text-fg'
            : 'shrink-0 tabular-nums text-fg'
        }
      >
        {value}
      </span>
    </div>
  );
}

function ConfidenceRow({
  label,
  value,
  threshold,
}: {
  label: string;
  value: number;
  threshold: number;
}) {
  return (
    <div>
      <div className="flex items-baseline justify-between gap-2 text-2xs">
        <span className="min-w-0 truncate text-fg-muted">{label}</span>
        <span className="shrink-0 tabular-nums text-fg">{formatConfidence(value)}</span>
      </div>
      <Meter
        value={value}
        threshold={threshold}
        tone={value >= threshold ? 'success' : 'warning'}
        label={label}
        className="mt-1"
      />
      <p className="pt-0.5 text-2xs text-fg-subtle">
        Limiar {threshold.toFixed(2)}
        {value >= threshold ? '' : ' — abaixo do limiar'}
      </p>
    </div>
  );
}
