import { CheckCircle2, FileDown, LoaderCircle, XCircle } from 'lucide-react';
import { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';
import { toDisplayMessage, type WorkflowSessionResponse } from '@/lib/api';
import { useChatStore } from '@/state/chat-store';

export function ReportWorkflowCard({
  workflow,
}: {
  workflow: WorkflowSessionResponse;
}) {
  const { answerWorkflow, confirmWorkflow, cancelWorkflow, downloadArtifact } =
    useChatStore();
  const [selected, setSelected] = useState<string[]>([]);
  const [text, setText] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setSelected([]);
    setText('');
    setStartDate('');
    setEndDate('');
    setError(null);
  }, [workflow.current_step]);

  const run = async (action: () => Promise<void>) => {
    setPending(true);
    setError(null);
    try {
      await action();
    } catch (cause) {
      setError(toDisplayMessage(cause));
    } finally {
      setPending(false);
    }
  };

  const question = workflow.question;
  const execution = workflow.execution;

  return (
    <section className="mt-4 rounded-xl border border-border bg-muted/40 p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-primary">
            Relatorio executivo
          </p>
          <p className="mt-1 text-2xs text-fg-subtle">
            Sessao {workflow.session_id.slice(0, 8)} · etapa {workflow.current_step}
          </p>
        </div>
        {workflow.status === 'executing' && (
          <LoaderCircle className="animate-spin text-primary" size={18} />
        )}
        {workflow.status === 'completed' && execution?.artifact && (
          <CheckCircle2 className="text-success" size={18} />
        )}
        {workflow.status === 'cancelled' && (
          <XCircle className="text-fg-subtle" size={18} />
        )}
      </div>

      {question && (
        <div className="mt-4">
          <p className="text-sm font-medium text-fg">{question.prompt}</p>
          {question.input_type === 'single_select' && (
            <div className="mt-3 flex flex-wrap gap-2">
              {question.options.map((option) => (
                <Button
                  key={option.value}
                  type="button"
                  variant="outline"
                  disabled={pending}
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
          )}

          {question.input_type === 'multi_select' && (
            <>
              <div className="mt-3 grid gap-2 sm:grid-cols-2">
                {question.options.map((option) => (
                  <label
                    key={option.value}
                    className="flex cursor-pointer items-center gap-2 rounded-lg border border-border bg-surface px-3 py-2 text-sm"
                  >
                    <input
                      type="checkbox"
                      checked={selected.includes(option.value)}
                      onChange={() =>
                        setSelected((current) =>
                          current.includes(option.value)
                            ? current.filter((value) => value !== option.value)
                            : [...current, option.value],
                        )
                      }
                    />
                    {option.label}
                  </label>
                ))}
              </div>
              <Button
                className="mt-3"
                type="button"
                disabled={pending}
                onClick={() =>
                  void run(() => answerWorkflow(workflow, question.step, selected))
                }
              >
                Continuar
              </Button>
            </>
          )}

          {question.input_type === 'date_range' && (
            <div className="mt-3 flex flex-wrap items-end gap-3">
              <label className="text-xs text-fg-muted">
                Inicio
                <input
                  type="date"
                  value={startDate}
                  onChange={(event) => setStartDate(event.target.value)}
                  className="mt-1 block rounded-md border border-border bg-surface px-3 py-2 text-sm text-fg"
                />
              </label>
              <label className="text-xs text-fg-muted">
                Fim
                <input
                  type="date"
                  value={endDate}
                  onChange={(event) => setEndDate(event.target.value)}
                  className="mt-1 block rounded-md border border-border bg-surface px-3 py-2 text-sm text-fg"
                />
              </label>
              <Button
                type="button"
                disabled={pending || !startDate || !endDate}
                onClick={() =>
                  void run(() =>
                    answerWorkflow(workflow, question.step, {
                      start_date: startDate,
                      end_date: endDate,
                    }),
                  )
                }
              >
                Continuar
              </Button>
            </div>
          )}

          {question.input_type === 'text' && (
            <div className="mt-3">
              <textarea
                value={text}
                maxLength={4000}
                rows={3}
                onChange={(event) => setText(event.target.value)}
                placeholder="Contexto adicional (opcional)"
                className="w-full resize-y rounded-lg border border-border bg-surface p-3 text-sm text-fg outline-none focus:border-primary"
              />
              <Button
                className="mt-2"
                type="button"
                disabled={pending}
                onClick={() =>
                  void run(() =>
                    answerWorkflow(workflow, question.step, text.trim() || null),
                  )
                }
              >
                {text.trim() ? 'Adicionar e continuar' : 'Continuar sem contexto'}
              </Button>
            </div>
          )}
        </div>
      )}

      {workflow.status === 'ready_for_confirmation' && (
        <div className="mt-4">
          <p className="text-sm font-medium text-fg">Revise antes de gerar</p>
          <p className="mt-2 rounded-lg bg-surface p-3 text-sm leading-6 text-fg-muted">
            {workflow.confirmation_summary}
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <Button
              type="button"
              disabled={pending}
              onClick={() => void run(() => confirmWorkflow(workflow))}
            >
              Confirmar e gerar DOCX
            </Button>
            <Button
              type="button"
              variant="outline"
              disabled={pending}
              onClick={() => void run(() => cancelWorkflow(workflow))}
            >
              Cancelar
            </Button>
          </div>
        </div>
      )}

      {workflow.status === 'executing' && (
        <p className="mt-4 text-sm text-fg-muted">
          O relatorio esta sendo processado. O resultado aparecera aqui.
        </p>
      )}

      {workflow.status === 'completed' && execution?.artifact && (
        <div className="mt-4 rounded-lg border border-border bg-surface p-3">
          <p className="text-sm font-medium text-fg">{execution.artifact.file_name}</p>
          <p className="mt-1 text-xs text-fg-muted">
            {(execution.artifact.size_bytes / 1024).toFixed(1)} KB · DOCX ·{' '}
            {execution.artifact.storage_provider}
          </p>
          <Button
            className="mt-3"
            type="button"
            disabled={pending}
            onClick={() => void run(() => downloadArtifact(workflow))}
          >
            <FileDown size={15} /> Baixar no chat
          </Button>
        </div>
      )}

      {workflow.status === 'completed' && execution?.error && (
        <p className="mt-4 rounded-lg bg-danger-soft p-3 text-sm text-danger">
          {execution.error.message}
        </p>
      )}
      {workflow.warnings.length > 0 && (
        <ul className="mt-3 list-disc space-y-1 pl-5 text-xs text-fg-muted">
          {workflow.warnings.map((warning) => (
            <li key={warning}>{warning}</li>
          ))}
        </ul>
      )}
      {error && <p className="mt-3 text-xs text-danger">{error}</p>}
    </section>
  );
}
