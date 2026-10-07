import { ChevronDown, History, LoaderCircle, RotateCcw } from 'lucide-react';
import { useCallback, useEffect, useId, useRef, useState } from 'react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  listDataChanges,
  toDataChangeFailure,
  type DataChangeHistoryItem,
} from '@/lib/api';
import { formatDateTime } from '@/lib/format';
import { cn } from '@/lib/utils';

/**
 * Historico do campo alterado (S5-07), lido de `GET /api/data-changes`.
 *
 * Fica recolhido e so consulta a API quando a pessoa abre. `refreshKey` muda
 * depois de confirmar ou desfazer, para a lista refletir a ultima acao.
 */
export function DataChangeHistory({
  projectCode,
  field,
  targetId,
  accessToken,
  refreshKey = 0,
}: {
  projectCode: string;
  field: string;
  targetId?: string | null;
  accessToken: string;
  refreshKey?: number;
}) {
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<DataChangeHistoryItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const panelId = useId();
  const controller = useRef<AbortController | null>(null);

  const load = useCallback(async () => {
    controller.current?.abort();
    const current = new AbortController();
    controller.current = current;
    setLoading(true);
    setError(null);
    try {
      const response = await listDataChanges({
        projectCode,
        field,
        targetId,
        accessToken,
        signal: current.signal,
      });
      if (!current.signal.aborted) setItems(response.items);
    } catch (cause) {
      if (!current.signal.aborted) setError(toDataChangeFailure(cause).message);
    } finally {
      if (!current.signal.aborted) setLoading(false);
    }
  }, [accessToken, field, projectCode, targetId]);

  useEffect(() => {
    if (open) void load();
  }, [open, load, refreshKey]);

  useEffect(() => () => controller.current?.abort(), []);

  return (
    <div className="mt-3 border-t border-border pt-2">
      <button
        type="button"
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((value) => !value)}
        className="flex min-h-8 items-center gap-1.5 rounded-md px-1 text-xs font-medium text-fg-muted hover:text-fg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        <History size={13} />
        Histórico do campo
        <ChevronDown
          size={13}
          className={cn('transition-transform', open && 'rotate-180')}
          aria-hidden
        />
      </button>

      {open && (
        <div id={panelId} className="mt-2">
          {loading && !items && (
            <p
              role="status"
              className="flex items-center gap-1.5 text-xs text-fg-muted"
            >
              <LoaderCircle size={12} className="animate-spin" />
              Carregando o histórico…
            </p>
          )}
          {error && (
            <div
              role="alert"
              className="flex flex-wrap items-center gap-2 text-xs text-danger"
            >
              {error}
              <Button size="sm" variant="ghost" onClick={() => void load()}>
                <RotateCcw size={12} />
                Tentar de novo
              </Button>
            </div>
          )}
          {items && items.length === 0 && !error && (
            <p className="text-xs text-fg-muted">
              Nenhuma alteração feita pelo chat neste campo.
            </p>
          )}
          {items && items.length > 0 && (
            <ol aria-label="Alterações do campo" className="space-y-1.5">
              {items.map((item) => (
                <li
                  key={item.change_id}
                  className="rounded-md bg-surface px-2.5 py-2 text-xs leading-5"
                >
                  <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                    <span>
                      <span className="sr-only">De </span>
                      <span className="text-fg-muted line-through">
                        {item.before.display}
                      </span>
                      <span aria-hidden> → </span>
                      <span className="sr-only"> para </span>
                      <span className="font-medium text-fg">{item.after.display}</span>
                    </span>
                    {item.status === 'desfeita' && (
                      <Badge tone="outline">Desfeita</Badge>
                    )}
                  </div>
                  <p className="text-fg-muted">
                    {item.requested_by} · {formatDateTime(item.applied_at)}
                    {item.undone_at &&
                      ` · desfeita em ${formatDateTime(item.undone_at)}`}
                  </p>
                </li>
              ))}
            </ol>
          )}
        </div>
      )}
    </div>
  );
}
