import {
  AlertTriangle,
  ArrowRight,
  Check,
  CircleSlash,
  LoaderCircle,
  PencilLine,
  RotateCcw,
  Undo2,
  X,
} from 'lucide-react';
import { useEffect, useId, useRef, useState, type ReactNode } from 'react';

import { DataChangeHistory } from '@/components/chat/data-change-history';
import { Button } from '@/components/ui/button';
import {
  cancelDataChange,
  confirmDataChange,
  createDataChangePreview,
  toDataChangeFailure,
  undoDataChange,
  type DataChangeFailure,
  type DataChangeOutcome,
  type DataChangePreview,
  type DataChangeValue,
} from '@/lib/api';
import type { DataChangeState } from '@/lib/domain';
import { formatTime } from '@/lib/format';
import { cn } from '@/lib/utils';
import { useChatStore } from '@/state/chat-store';

type Busy = 'confirm' | 'cancel' | 'undo' | 'choose' | null;

/**
 * Cartao da alteracao de dados pelo chat (S5-07, contrato da Secao 8.5.13).
 *
 * O cartao e a unica via de escrita: a mensagem do chat so traz a previa, e o
 * valor muda apenas quando a pessoa confirma aqui. Estados tratados:
 *
 * - previa: antes e depois, avisos, justificativa opcional, Confirmar e Cancelar;
 * - confirmacao: valor gravado, com Desfazer enquanto a janela estiver aberta;
 * - cancelamento: nada gravado;
 * - erro: mensagem do backend, com nova tentativa so quando adianta repetir;
 * - pergunta: candidatos ou campo de valor para completar o pedido.
 *
 * O estado vive na mensagem (store) para nao voltar a oferecer Confirmar ao
 * reabrir a conversa.
 */
export function DataChangeCard({
  messageId,
  state,
}: {
  messageId: string;
  state: DataChangeState;
}) {
  const { accessToken, activeConversation, updateDataChange } = useChatStore();
  const [current, setCurrent] = useState<DataChangeState>(state);
  const [busy, setBusy] = useState<Busy>(null);
  const [reason, setReason] = useState('');
  const [inlineError, setInlineError] = useState<DataChangeFailure | null>(null);
  const [historyKey, setHistoryKey] = useState(0);
  const resultRef = useRef<HTMLDivElement>(null);
  const [actedHere, setActedHere] = useState(false);
  const now = useNow(15_000);

  useEffect(() => setCurrent(state), [state]);

  // Os botoes somem depois da acao; o foco vai para o resultado, e nao para o
  // inicio da pagina (mesmo cuidado do cartao da sugestao proativa).
  useEffect(() => {
    if (actedHere && current.phase !== 'idle') resultRef.current?.focus();
  }, [actedHere, current.phase]);

  const commit = (next: DataChangeState) => {
    setCurrent(next);
    updateDataChange(messageId, next);
  };

  const token = accessToken.trim();
  const outcome = current.outcome;

  if (outcome.status === 'rejected') {
    return (
      <CardShell
        tone="muted"
        icon={<CircleSlash size={14} />}
        title="Nada foi alterado"
      >
        <p className="mt-1 text-xs leading-5 text-fg-muted">
          O pedido foi recusado antes da prévia. Nenhum dado do projeto mudou.
        </p>
      </CardShell>
    );
  }

  if (outcome.status === 'needs_input') {
    if (outcome.missing === 'field' || !outcome.draft) return null;
    return (
      <NeedsInput
        outcome={outcome}
        busy={busy === 'choose'}
        error={inlineError}
        onSubmit={async (choice) => {
          if (!token) {
            setInlineError(missingToken());
            return;
          }
          const draft = outcome.draft!;
          const projectCode =
            outcome.missing === 'project' ? choice : draft.project_code;
          if (!projectCode || !draft.field) return;
          setBusy('choose');
          setInlineError(null);
          try {
            const next = await createDataChangePreview(
              {
                project_code: projectCode,
                entity: draft.entity ?? null,
                field: draft.field,
                target_id: outcome.missing === 'target' ? choice : draft.target_id,
                item_reference:
                  outcome.missing === 'target' ? null : draft.item_reference,
                raw_value: outcome.missing === 'value' ? choice : draft.raw_value,
                conversation_id: activeConversation?.id ?? null,
              },
              token,
            );
            commit({ outcome: next, phase: 'idle' });
          } catch (cause) {
            setInlineError(toDataChangeFailure(cause));
          } finally {
            setBusy(null);
          }
        }}
      />
    );
  }

  const preview = outcome.preview;
  if (!preview) return null;

  const expired =
    current.phase === 'idle' && new Date(preview.expires_at).getTime() <= now;
  const failure = current.failure;
  const canAct =
    !expired &&
    (current.phase === 'idle' || (current.phase === 'failed' && failure?.retryable));

  async function run(
    kind: Exclude<Busy, null>,
    action: () => Promise<DataChangeState>,
  ) {
    if (!token) {
      commit({ ...current, phase: 'failed', failure: missingToken() });
      return;
    }
    setBusy(kind);
    setActedHere(true);
    setInlineError(null);
    try {
      commit(await action());
      setHistoryKey((key) => key + 1);
    } catch (cause) {
      const failed = toDataChangeFailure(cause);
      if (kind === 'undo') setInlineError(failed);
      else commit({ ...current, phase: 'failed', failure: failed });
    } finally {
      setBusy(null);
    }
  }

  const confirm = () =>
    run('confirm', async () => ({
      outcome,
      phase: 'applied',
      change: await confirmDataChange({
        pendingChangeId: preview.pending_change_id,
        reason,
        accessToken: token,
      }),
    }));
  const cancel = () =>
    run('cancel', async () => {
      await cancelDataChange(preview.pending_change_id, token);
      return { outcome, phase: 'cancelled' };
    });
  const undo = () =>
    run('undo', async () => ({
      ...current,
      phase: 'undone',
      undo: await undoDataChange(current.change!.change_id, token),
    }));

  const undoUntil = current.change
    ? new Date(current.change.undo_available_until)
    : null;
  const canUndo =
    current.phase === 'applied' && undoUntil !== null && undoUntil.getTime() > now;

  return (
    <CardShell
      tone={PHASE_TONES[current.phase]}
      icon={<PencilLine size={14} />}
      title={TITLES[current.phase]}
      subtitle={current.phase === 'idle' ? 'precisa da sua confirmação' : undefined}
    >
      <PreviewBody preview={preview} />

      {current.phase === 'idle' && preview.warnings.length > 0 && (
        <ul aria-label="Avisos" className="mt-3 space-y-1">
          {preview.warnings.map((warning) => (
            <li key={warning} className="flex gap-1.5 text-xs leading-5 text-warning">
              <AlertTriangle size={13} className="mt-0.5 shrink-0" aria-hidden />
              {warning}
            </li>
          ))}
        </ul>
      )}

      {canAct && (
        <>
          <ReasonField value={reason} onChange={setReason} disabled={busy !== null} />
          <p className="mt-2 text-2xs text-fg-subtle">
            Nada foi gravado ainda. A prévia vale até {formatTime(preview.expires_at)}.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <Button size="sm" onClick={() => void confirm()} disabled={busy !== null}>
              {busy === 'confirm' ? (
                <LoaderCircle size={13} className="animate-spin" />
              ) : (
                <Check size={13} />
              )}
              {current.phase === 'failed' ? 'Tentar de novo' : 'Confirmar alteração'}
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => void cancel()}
              disabled={busy !== null}
            >
              {busy === 'cancel' ? (
                <LoaderCircle size={13} className="animate-spin" />
              ) : (
                <X size={13} />
              )}
              Cancelar
            </Button>
          </div>
        </>
      )}

      <div
        ref={resultRef}
        tabIndex={-1}
        className="rounded-md focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        {expired && (
          <p role="status" className="mt-3 text-xs text-fg-muted">
            A prévia expirou e nada foi gravado. Peça a alteração de novo para conferir
            o valor atual.
          </p>
        )}
        {current.phase === 'failed' && failure && (
          <p role="alert" className="mt-3 text-xs leading-5 text-danger">
            {failure.message}
            {!failure.retryable && ' Nada foi gravado.'}
          </p>
        )}
        {current.phase === 'cancelled' && (
          <p role="status" className="mt-3 text-xs text-fg-muted">
            Alteração cancelada. Nada foi gravado.
          </p>
        )}
        {current.phase === 'applied' && current.change && (
          <p role="status" className="mt-3 text-xs leading-5 text-success">
            Alteração gravada às {formatTime(current.change.applied_at)}.
            {canUndo &&
              ` Você pode desfazer até ${formatTime(current.change.undo_available_until)}.`}
          </p>
        )}
        {current.phase === 'undone' && current.undo && (
          <p role="status" className="mt-3 text-xs leading-5 text-fg-muted">
            Alteração desfeita. {preview.field.label} voltou para{' '}
            <span className="font-medium text-fg">{current.undo.restored.display}</span>
            .
          </p>
        )}
      </div>

      {canUndo && (
        <div className="mt-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => void undo()}
            disabled={busy !== null}
          >
            {busy === 'undo' ? (
              <LoaderCircle size={13} className="animate-spin" />
            ) : (
              <Undo2 size={13} />
            )}
            Desfazer
          </Button>
        </div>
      )}
      {inlineError && (
        <p role="alert" className="mt-2 text-xs leading-5 text-danger">
          {inlineError.message}
        </p>
      )}

      {token && (
        <DataChangeHistory
          projectCode={preview.project.code}
          field={preview.field.key}
          targetId={preview.target.id}
          accessToken={token}
          refreshKey={historyKey}
        />
      )}
    </CardShell>
  );
}

/** Previa em azul (acao pendente); estados encerrados sem gravacao em cinza. */
const PHASE_TONES: Record<
  DataChangeState['phase'],
  'primary' | 'success' | 'danger' | 'muted'
> = {
  idle: 'primary',
  applied: 'success',
  failed: 'danger',
  cancelled: 'muted',
  undone: 'muted',
};

const TITLES: Record<DataChangeState['phase'], string> = {
  idle: 'Alteração de dados',
  applied: 'Alteração gravada',
  cancelled: 'Alteração cancelada',
  undone: 'Alteração desfeita',
  failed: 'Não foi possível alterar',
};

function CardShell({
  tone,
  icon,
  title,
  subtitle,
  children,
}: {
  tone: 'primary' | 'success' | 'danger' | 'muted';
  icon: ReactNode;
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  return (
    <section
      aria-label="Alteração de dados"
      className={cn(
        'mt-4 rounded-xl border p-3.5',
        tone === 'primary' && 'border-primary/50 bg-primary-soft/40',
        tone === 'success' && 'border-success/40 bg-success-soft/40',
        tone === 'danger' && 'border-danger/40 bg-danger-soft/40',
        tone === 'muted' && 'border-border bg-surface-muted',
      )}
    >
      <h3
        className={cn(
          'flex flex-wrap items-center gap-x-2 gap-y-1 text-xs font-semibold',
          tone === 'primary' && 'text-primary',
          tone === 'success' && 'text-success',
          tone === 'danger' && 'text-danger',
          tone === 'muted' && 'text-fg-muted',
        )}
      >
        {icon}
        {title}
        {subtitle && <span className="font-normal text-fg-muted">· {subtitle}</span>}
      </h3>
      {children}
    </section>
  );
}

function PreviewBody({ preview }: { preview: DataChangePreview }) {
  return (
    <div className="mt-2">
      <p className="text-sm font-medium text-fg">{preview.field.label}</p>
      <p className="text-xs leading-5 text-fg-muted">
        {preview.target.entity === 'projeto'
          ? `${preview.project.code} · ${preview.project.title}`
          : `${preview.target.label} · ${preview.project.title}`}
      </p>
      <dl className="mt-2.5 grid grid-cols-1 items-center gap-2 sm:grid-cols-[1fr_auto_1fr]">
        <ValueBox label="Antes" value={preview.before} variant="before" />
        <ArrowRight size={14} className="hidden text-fg-subtle sm:block" aria-hidden />
        <ValueBox label="Depois" value={preview.after} variant="after" />
      </dl>
    </div>
  );
}

function ValueBox({
  label,
  value,
  variant,
}: {
  label: string;
  value: DataChangeValue;
  variant: 'before' | 'after';
}) {
  return (
    <div
      className={cn(
        'rounded-lg border px-3 py-2',
        variant === 'before'
          ? 'border-border bg-surface'
          : 'border-primary/40 bg-surface',
      )}
    >
      <dt className="text-2xs font-medium uppercase tracking-wide text-fg-subtle">
        {label}
      </dt>
      <dd
        className={cn(
          'mt-0.5 break-words text-sm',
          variant === 'before' ? 'text-fg-muted line-through' : 'font-semibold text-fg',
        )}
      >
        {value.display}
      </dd>
    </div>
  );
}

function ReasonField({
  value,
  onChange,
  disabled,
}: {
  value: string;
  onChange: (value: string) => void;
  disabled: boolean;
}) {
  const id = useId();
  return (
    <div className="mt-3">
      <label htmlFor={id} className="text-xs font-medium text-fg-muted">
        Justificativa <span className="font-normal">(opcional)</span>
      </label>
      <textarea
        id={id}
        rows={2}
        maxLength={500}
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Ex.: replanejamento aprovado na reunião de acompanhamento"
        className="mt-1 w-full resize-none rounded-md border border-border bg-surface px-2.5 py-1.5 text-base leading-6 text-fg outline-none placeholder:text-fg-subtle focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-60 sm:text-sm"
      />
    </div>
  );
}

function NeedsInput({
  outcome,
  busy,
  error,
  onSubmit,
}: {
  outcome: DataChangeOutcome;
  busy: boolean;
  error: DataChangeFailure | null;
  onSubmit: (choice: string) => Promise<void>;
}) {
  const [value, setValue] = useState('');
  const inputId = useId();
  const candidates = outcome.candidates ?? [];

  return (
    <CardShell
      tone="primary"
      icon={<PencilLine size={14} />}
      title="Complete o pedido de alteração"
    >
      {outcome.question && (
        <p className="mt-2 text-sm leading-5 text-fg">{outcome.question}</p>
      )}
      {outcome.missing === 'value' ? (
        <form
          className="mt-3 flex flex-wrap gap-2"
          onSubmit={(event) => {
            event.preventDefault();
            if (value.trim()) void onSubmit(value.trim());
          }}
        >
          <label htmlFor={inputId} className="sr-only">
            Novo valor
          </label>
          <input
            id={inputId}
            value={value}
            maxLength={240}
            required
            disabled={busy}
            onChange={(event) => setValue(event.target.value)}
            aria-invalid={error ? true : undefined}
            className="min-w-0 flex-1 rounded-md border border-border bg-surface px-3 py-1.5 text-base text-fg outline-none focus-visible:ring-2 focus-visible:ring-ring sm:text-sm"
          />
          <Button size="sm" type="submit" disabled={busy}>
            {busy ? (
              <LoaderCircle size={13} className="animate-spin" />
            ) : (
              <Check size={13} />
            )}
            Ver prévia
          </Button>
        </form>
      ) : (
        candidates.length > 0 && (
          <ul aria-label="Opções" className="mt-3 flex flex-wrap gap-2">
            {candidates.map((candidate) => (
              <li key={candidate.id}>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={busy}
                  onClick={() => void onSubmit(candidate.id)}
                  className="h-auto min-h-8 whitespace-normal py-1.5 text-left"
                >
                  {candidate.label}
                </Button>
              </li>
            ))}
          </ul>
        )
      )}
      {busy && (
        <p
          role="status"
          className="mt-2 flex items-center gap-1.5 text-xs text-fg-muted"
        >
          <LoaderCircle size={12} className="animate-spin" />
          Preparando a prévia…
        </p>
      )}
      {error && (
        <p
          role="alert"
          className="mt-2 flex items-center gap-1.5 text-xs leading-5 text-danger"
        >
          {error.retryable && <RotateCcw size={12} aria-hidden />}
          {error.message}
        </p>
      )}
    </CardShell>
  );
}

function missingToken(): DataChangeFailure {
  return {
    code: 'UNAUTHENTICATED',
    message: 'Entre novamente para alterar dados.',
    retryable: false,
  };
}

/** Relogio de baixa frequencia para expirar a previa e a janela de desfazer. */
function useNow(intervalMs: number): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), intervalMs);
    return () => window.clearInterval(timer);
  }, [intervalMs]);
  return now;
}
