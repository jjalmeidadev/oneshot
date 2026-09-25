import { useEffect, useState } from 'react';
import { BellRing, Check, X } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { useChatStore } from '@/state/chat-store';
import type { AlertWorkflowResponse } from '@/lib/api';

export function AlertWorkflowCard({ workflow }: { workflow: AlertWorkflowResponse }) {
  const { answerWorkflow, confirmWorkflow, cancelWorkflow } = useChatStore();
  const [number, setNumber] = useState('7');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    if (workflow.current_step === 'threshold') {
      const candidate = workflow.answers.threshold_candidate;
      setNumber(typeof candidate === 'number' ? String(candidate) : '7');
    }
  }, [workflow.answers, workflow.current_step]);

  async function run(action: () => Promise<void>) {
    setBusy(true);
    setError(null);
    try {
      await action();
    } catch {
      setError('Nao foi possivel atualizar o alerta.');
    } finally {
      setBusy(false);
    }
  }

  const question = workflow.question;
  return (
    <section
      aria-label="Configuracao do alerta"
      className="mt-4 rounded-xl border border-border bg-surface-muted p-4"
    >
      <div className="flex items-center gap-2 text-sm font-semibold">
        <BellRing size={16} /> Alerta de prazo
      </div>
      <p className="mt-1 text-xs text-fg-muted">
        Sessao {workflow.session_id.slice(0, 8)} · etapa {workflow.current_step}
      </p>
      {question && (
        <div className="mt-4">
          <p className="text-sm">{question.prompt}</p>
          {question.input_type === 'single_select' ? (
            <div className="mt-3 flex flex-wrap gap-2">
              {question.options.map((option) => (
                <Button
                  key={option.value}
                  disabled={busy}
                  variant="outline"
                  onClick={() =>
                    void run(() =>
                      answerWorkflow(workflow, question.step, option.value),
                    )
                  }
                >
                  {option.label}
                </Button>
              ))}
            </div>
          ) : (
            <form
              className="mt-3 flex gap-2"
              onSubmit={(event) => {
                event.preventDefault();
                void run(() => answerWorkflow(workflow, question.step, Number(number)));
              }}
            >
              <label className="sr-only" htmlFor={`threshold-${workflow.session_id}`}>
                Dias de atraso
              </label>
              <input
                id={`threshold-${workflow.session_id}`}
                type="number"
                min="0"
                max="3650"
                required
                value={number}
                onChange={(event) => setNumber(event.target.value)}
                className="w-28 rounded-md border border-border bg-surface px-3 py-2 text-sm"
              />
              <Button disabled={busy} type="submit">
                Continuar
              </Button>
            </form>
          )}
        </div>
      )}
      {workflow.status === 'ready_for_confirmation' && (
        <div className="mt-4 rounded-lg border border-primary/30 bg-primary-soft p-3">
          <p className="text-sm">{workflow.confirmation_summary}</p>
          <div className="mt-3 flex gap-2">
            <Button
              disabled={busy}
              onClick={() => void run(() => confirmWorkflow(workflow))}
            >
              <Check size={14} /> Ativar alerta
            </Button>
            <Button
              disabled={busy}
              variant="outline"
              onClick={() => void run(() => cancelWorkflow(workflow))}
            >
              <X size={14} /> Cancelar
            </Button>
          </div>
        </div>
      )}
      {workflow.status === 'completed' && workflow.subscription && (
        <p role="status" className="mt-4 text-sm text-success">
          Alerta ativo. Proxima verificacao:{' '}
          {new Date(workflow.subscription.next_evaluation_at).toLocaleString('pt-BR')}.
        </p>
      )}
      {workflow.status === 'cancelled' && (
        <p className="mt-4 text-sm text-fg-muted">Configuracao cancelada.</p>
      )}
      {error && (
        <p role="alert" className="mt-3 text-sm text-danger">
          {error}
        </p>
      )}
    </section>
  );
}
