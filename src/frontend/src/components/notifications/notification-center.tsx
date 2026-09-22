import { useCallback, useEffect, useState } from 'react';
import { Bell } from 'lucide-react';

import {
  changeAlertSubscription,
  getAlertSubscriptions,
  getNotifications,
  markNotificationRead,
  type AlertNotification,
  type AlertSubscription,
} from '@/lib/api';
import { useChatStore } from '@/state/chat-store';

const POLL_INTERVAL_MS = 30_000;

export function NotificationCenter() {
  const { accessToken } = useChatStore();
  const [items, setItems] = useState<AlertNotification[]>([]);
  const [unread, setUnread] = useState(0);
  const [subscriptions, setSubscriptions] = useState<AlertSubscription[]>([]);

  const refresh = useCallback(async () => {
    if (!accessToken.trim()) {
      setItems([]);
      setUnread(0);
      return;
    }
    try {
      const [value, configured] = await Promise.all([
        getNotifications(accessToken.trim()),
        getAlertSubscriptions(accessToken.trim()),
      ]);
      setItems(value.items);
      setUnread(value.unread_count);
      setSubscriptions(configured.map((item) => item.subscription));
    } catch {
      // O chat continua operacional; a proxima rodada tenta novamente.
    }
  }, [accessToken]);

  useEffect(() => {
    void refresh();
    const id = window.setInterval(() => void refresh(), POLL_INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [refresh]);

  async function read(item: AlertNotification) {
    if (item.status !== 'read') {
      await markNotificationRead(item.notification_id, accessToken.trim());
      await refresh();
    }
  }

  async function change(
    item: AlertSubscription,
    action: 'pause' | 'resume' | 'cancel',
  ) {
    await changeAlertSubscription({
      id: item.subscription_id,
      action,
      revision: item.revision,
      token: accessToken.trim(),
    });
    await refresh();
  }

  return (
    <details className="relative border-b border-border bg-surface px-4 py-2 text-sm">
      <summary
        className="ml-auto flex w-fit cursor-pointer list-none items-center gap-2 rounded-md px-2 py-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        aria-label={`${unread} notificacoes nao lidas`}
      >
        <Bell size={16} />
        <span>Alertas</span>
        {unread > 0 && (
          <span
            aria-live="polite"
            className="rounded-full bg-danger px-2 py-0.5 text-2xs text-white"
          >
            {unread}
          </span>
        )}
      </summary>
      <div className="absolute right-3 top-11 z-30 max-h-80 w-[min(26rem,calc(100vw-2rem))] overflow-auto rounded-xl border border-border bg-surface p-3 shadow-panel">
        {items.length === 0 ? (
          <p className="text-fg-muted">Nenhuma notificacao disponível.</p>
        ) : (
          items.map((item) => (
            <button
              key={item.notification_id}
              type="button"
              onClick={() => void read(item)}
              className="mb-2 block w-full rounded-lg border border-border p-3 text-left hover:bg-surface-muted"
            >
              <span className="font-medium">{item.title}</span>
              <span className="mt-1 block text-xs leading-5 text-fg-muted">
                {item.body}
              </span>
              <span className="mt-1 block text-2xs text-fg-subtle">
                {item.status === 'read' ? 'Lida' : 'Nao lida'}
              </span>
            </button>
          ))
        )}
        <h3 className="mt-4 border-t border-border pt-3 font-medium">
          Alertas configurados
        </h3>
        {subscriptions.length === 0 ? (
          <p className="mt-2 text-fg-muted">Nenhum alerta ativo.</p>
        ) : (
          subscriptions.map((item) => (
            <div
              key={item.subscription_id}
              className="mt-2 rounded-lg border border-border p-3"
            >
              <p className="font-medium">{item.rule.project_label}</p>
              <p className="text-xs text-fg-muted">
                Mais de {item.rule.threshold_days} dias · {item.status}
              </p>
              {item.status !== 'cancelled' && (
                <div className="mt-2 flex gap-2">
                  {item.status === 'active' ? (
                    <button
                      type="button"
                      className="text-xs text-primary underline"
                      onClick={() => void change(item, 'pause')}
                    >
                      Pausar
                    </button>
                  ) : (
                    <button
                      type="button"
                      className="text-xs text-primary underline"
                      onClick={() => void change(item, 'resume')}
                    >
                      Retomar
                    </button>
                  )}
                  <button
                    type="button"
                    className="text-xs text-danger underline"
                    onClick={() => void change(item, 'cancel')}
                  >
                    Cancelar
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </details>
  );
}
