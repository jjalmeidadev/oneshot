import { Activity, CheckCircle2, Clock3, Hash, Trash2 } from 'lucide-react';

import { cn } from '@/lib/utils';

export type MetricRun = {
  id: string;
  prompt: string;
  success: boolean;
  model: string;
  latencyMs: number;
  providerLatencyMs: number | null;
  retrievalLatencyMs: number | null;
  sourceCount: number;
  inputTokens: number;
  outputTokens: number;
  thoughtTokens: number;
  totalTokens: number;
  error?: string;
};

type MetricsPanelProps = {
  runs: MetricRun[];
  onClear: () => void;
  className?: string;
};

function MetricsPanel({ runs, onClear, className }: MetricsPanelProps) {
  const successfulRuns = runs.filter((run) => run.success);
  const successRate = runs.length
    ? Math.round((successfulRuns.length / runs.length) * 100)
    : 0;
  const averageLatency = successfulRuns.length
    ? Math.round(
        successfulRuns.reduce((sum, run) => sum + run.latencyMs, 0) /
          successfulRuns.length,
      )
    : 0;
  const totalTokens = successfulRuns.reduce((sum, run) => sum + run.totalTokens, 0);

  const summaries = [
    { label: 'Execucoes', value: runs.length, icon: Activity },
    { label: 'Sucesso', value: `${successRate}%`, icon: CheckCircle2 },
    { label: 'Latencia media', value: `${averageLatency} ms`, icon: Clock3 },
    { label: 'Tokens totais', value: totalTokens, icon: Hash },
  ];

  return (
    <aside
      className={cn(
        'flex min-h-0 flex-col border-t border-metro-line bg-slate-50/80 lg:border-l lg:border-t-0',
        className,
      )}
      aria-label="Metricas dos testes"
    >
      <div className="flex h-12 shrink-0 items-center justify-between border-b border-metro-line px-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-metro-text">
          <Activity size={16} className="text-metro-blue" />
          Metricas de teste
        </div>
        <button
          type="button"
          onClick={onClear}
          disabled={!runs.length}
          aria-label="Limpar metricas"
          title="Limpar metricas"
          className="inline-flex h-8 w-8 items-center justify-center rounded-md text-slate-500 transition-colors hover:bg-white hover:text-red-600 disabled:cursor-not-allowed disabled:opacity-30"
        >
          <Trash2 size={15} />
        </button>
      </div>

      <div className="grid shrink-0 grid-cols-2 border-b border-metro-line sm:grid-cols-4 lg:grid-cols-2">
        {summaries.map(({ label, value, icon: Icon }) => (
          <div
            key={label}
            className="min-w-0 border-b border-r border-metro-line px-3 py-2.5 last:border-r-0 lg:last:border-r-0 lg:[&:nth-child(2n)]:border-r-0 lg:[&:nth-last-child(-n+2)]:border-b-0"
          >
            <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
              <Icon size={12} />
              <span className="truncate">{label}</span>
            </div>
            <div className="mt-1 truncate text-base font-semibold text-metro-text">
              {value}
            </div>
          </div>
        ))}
      </div>

      <div className="hidden min-h-0 flex-1 overflow-y-auto p-3 lg:block">
        {runs.length === 0 ? (
          <p className="px-1 py-3 text-xs text-slate-500">
            Nenhuma execucao registrada.
          </p>
        ) : (
          <div className="flex flex-col divide-y divide-metro-line">
            {runs.map((run, index) => (
              <div key={run.id} className="py-3 first:pt-1">
                <div className="flex items-start gap-2">
                  <span
                    className={cn(
                      'mt-1.5 h-2 w-2 shrink-0 rounded-full',
                      run.success ? 'bg-emerald-500' : 'bg-red-500',
                    )}
                  />
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-xs font-medium text-metro-text">
                      {runs.length - index}. {run.prompt}
                    </div>
                    <div className="mt-1 text-[11px] leading-5 text-slate-500">
                      {run.success ? (
                        <>
                          {run.model}
                          <br />
                          {run.latencyMs} ms total | {run.providerLatencyMs} ms Gemini
                          <br />
                          {run.retrievalLatencyMs} ms recuperacao | {run.sourceCount}{' '}
                          fontes
                          <br />
                          {run.totalTokens} tokens | {run.inputTokens} entrada |{' '}
                          {run.outputTokens} saida | {run.thoughtTokens} raciocinio
                        </>
                      ) : (
                        <span className="text-red-600">{run.error}</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}

export { MetricsPanel };
