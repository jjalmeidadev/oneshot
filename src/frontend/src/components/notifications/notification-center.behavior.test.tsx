import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { NotificationCenter } from './notification-center';
import type { AlertNotification, AlertSubscription } from '@/lib/api';

const mocks = vi.hoisted(() => ({
  token: ' token-test ',
  getNotifications: vi.fn(),
  getAlertSubscriptions: vi.fn(),
  markNotificationRead: vi.fn(),
  changeAlertSubscription: vi.fn(),
}));
vi.mock('@/state/chat-store', () => ({
  useChatStore: () => ({ accessToken: mocks.token }),
}));
vi.mock('@/lib/api', () => mocks);

const notification: AlertNotification = {
  notification_id: 'n1',
  correlation_id: 'c1',
  subscription_id: 's1',
  occurrence_id: 'o1',
  recipient_subject: 'user',
  project_id: 'p1',
  item_id: 'i1',
  title: 'Prazo ultrapassado',
  body: 'Marco atrasado em oito dias.',
  reference_date: '2026-10-05',
  overdue_days: 8,
  status: 'available',
  created_at: '2026-10-05T12:00:00Z',
};
const subscription: AlertSubscription = {
  subscription_id: 's1',
  correlation_id: 'c1',
  idempotency_key: 'key',
  owner_subject: 'user',
  status: 'active',
  revision: 3,
  next_evaluation_at: '2026-10-06T12:00:00Z',
  created_at: '2026-10-05T12:00:00Z',
  updated_at: '2026-10-05T12:00:00Z',
  rule: {
    project_id: 'p1',
    project_label: 'Projeto Um',
    threshold_days: 7,
    comparison_operator: 'gt',
    day_basis: 'calendar_days',
    trigger_type: 'daily',
    evaluation_time: '09:00:00',
    timezone: 'America/Sao_Paulo',
  },
};

describe('Comportamento de NotificationCenter', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.token = ' token-test ';
    mocks.getNotifications.mockResolvedValue({
      items: [notification],
      unread_count: 1,
    });
    mocks.getAlertSubscriptions.mockResolvedValue([
      { contract_version: '1.0', subscription },
    ]);
    mocks.markNotificationRead.mockResolvedValue({ ...notification, status: 'read' });
    mocks.changeAlertSubscription.mockResolvedValue({ subscription });
  });

  it('busca com token normalizado e atualiza resumo após marcar leitura', async () => {
    render(<NotificationCenter />);
    await userEvent.click(await screen.findByLabelText('1 notificacoes nao lidas'));
    expect(mocks.getNotifications).toHaveBeenCalledWith('token-test');
    expect(mocks.getAlertSubscriptions).toHaveBeenCalledWith('token-test');
    mocks.getNotifications.mockResolvedValue({
      items: [{ ...notification, status: 'read' }],
      unread_count: 0,
    });
    await userEvent.click(screen.getByRole('button', { name: /Prazo ultrapassado/ }));
    await waitFor(() =>
      expect(mocks.markNotificationRead).toHaveBeenCalledWith('n1', 'token-test'),
    );
    expect(await screen.findByLabelText('0 notificacoes nao lidas')).toBeVisible();
    await userEvent.click(screen.getByRole('button', { name: /Prazo ultrapassado/ }));
    expect(mocks.markNotificationRead).toHaveBeenCalledOnce();
  });

  it.each([
    ['active', 'Pausar', 'pause'],
    ['paused', 'Retomar', 'resume'],
    ['active', 'Cancelar', 'cancel'],
  ] as const)(
    'encaminha %s / %s com revisão e token',
    async (status, label, action) => {
      mocks.getAlertSubscriptions.mockResolvedValue([
        { subscription: { ...subscription, status } },
      ]);
      render(<NotificationCenter />);
      await userEvent.click(await screen.findByLabelText('1 notificacoes nao lidas'));
      await userEvent.click(screen.getByRole('button', { name: label }));
      await waitFor(() =>
        expect(mocks.changeAlertSubscription).toHaveBeenCalledWith({
          id: 's1',
          action,
          revision: 3,
          token: 'token-test',
        }),
      );
      await waitFor(() => expect(mocks.getNotifications).toHaveBeenCalledTimes(2));
    },
  );

  it('não apresenta controles para assinatura cancelada', async () => {
    mocks.getAlertSubscriptions.mockResolvedValue([
      { subscription: { ...subscription, status: 'cancelled' } },
    ]);
    render(<NotificationCenter />);
    await userEvent.click(await screen.findByLabelText('1 notificacoes nao lidas'));
    expect(screen.getByText(/Mais de 7 dias · cancelled/)).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Cancelar' })).not.toBeInTheDocument();
  });

  it('limpa notificações sem token e mantém a interface após falha de consulta', async () => {
    mocks.getNotifications.mockRejectedValue(new Error('Offline'));
    const { rerender } = render(<NotificationCenter />);
    await waitFor(() => expect(mocks.getNotifications).toHaveBeenCalledOnce());
    await userEvent.click(screen.getByLabelText('0 notificacoes nao lidas'));
    expect(screen.getByText('Nenhuma notificacao disponível.')).toBeVisible();
    mocks.token = ' ';
    rerender(<NotificationCenter />);
    expect(mocks.getNotifications).toHaveBeenCalledOnce();
  });

  it('consulta periodicamente e cancela o polling ao desmontar', async () => {
    const interval = vi.spyOn(window, 'setInterval');
    const clear = vi.spyOn(window, 'clearInterval');
    const { unmount } = render(<NotificationCenter />);
    await waitFor(() => expect(mocks.getNotifications).toHaveBeenCalledOnce());
    expect(interval).toHaveBeenCalledWith(expect.any(Function), 30_000);
    const callback = interval.mock.calls[0][0] as () => void;
    await act(async () => callback());
    expect(mocks.getNotifications).toHaveBeenCalledTimes(2);
    unmount();
    expect(clear).toHaveBeenCalledWith(interval.mock.results[0].value);
  });
});
