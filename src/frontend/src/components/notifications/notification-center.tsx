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
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { useChatStore } from '@/state/chat-store';

const POLL_INTERVAL_MS = 30_000;

/**
 * Sino de alertas no cabecalho do chat (S5-20). Antes ocupava uma faixa
 * inteira acima da conversa; agora abre as notificacoes num painel suspenso.
 */
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

  const label =
    unread > 0
      ? `Alertas: ${unread} ${unread === 1 ? 'notificação não lida' : 'notificações não lidas'}`
      : 'Alertas: nenhuma notificação não lida';

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon-sm" aria-label={label} className="relative">
          <Bell size={16} />
          {unread > 0 && (
            <span
              aria-hidden
              className="absolute right-0.5 top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-danger px-1 text-[10px] font-semibold leading-none text-white"
            >
              {unread > 9 ? '9+' : unread}
            </span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent
        aria-label="Alertas"
        className="max-h-[min(28rem,calc(100vh-6rem))] w-[min(26rem,calc(100vw-1.5rem))] overflow-auto"
      >
        <p className="pb-2 text-xs font-semibold text-fg">Notificações</p>
        {items.length === 0 ? (
          <p className="text-xs text-fg-muted">Nenhuma notificação disponível.</p>
        ) : (
          items.map((item) => (
            <button
              key={item.notification_id}
              type="button"
              onClick={() => void read(item)}
              className="mb-2 block w-full rounded-lg border border-border p-3 text-left hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <span className="flex items-center gap-1.5 font-medium">
                {item.status !== 'read' && (
                  <span aria-hidden className="h-1.5 w-1.5 rounded-full bg-primary" />
                )}
                {item.title}
              </span>
              <span className="mt-1 block text-xs leading-5 text-fg-muted">
                {item.body}
              </span>
              <span className="mt-1 block text-2xs text-fg-subtle">
                {item.status === 'read' ? 'Lida' : 'Não lida'}
              </span>
            </button>
          ))
        )}
        <p className="mt-3 border-t border-border pt-3 text-xs font-semibold text-fg">
          Alertas configurados
        </p>
        {subscriptions.length === 0 ? (
          <p className="mt-2 text-xs text-fg-muted">Nenhum alerta ativo.</p>
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
      </PopoverContent>
    </Popover>
  );
}
