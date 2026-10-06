import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, test, vi } from 'vitest';

import { NotificationCenter } from './notification-center';

vi.mock('@/state/chat-store', () => ({ useChatStore: () => ({ accessToken: '' }) }));
vi.mock('@/lib/api', () => ({
  changeAlertSubscription: vi.fn(),
  getAlertSubscriptions: vi.fn(),
  getNotifications: vi.fn(),
  markNotificationRead: vi.fn(),
}));

test('exposes an accessible notification summary', () => {
  render(<NotificationCenter />);
  expect(
    screen.getByRole('button', { name: 'Alertas: nenhuma notificação não lida' }),
  ).toBeInTheDocument();
});

test('abre as notificações em painel suspenso a partir do sino', async () => {
  render(<NotificationCenter />);
  expect(screen.queryByText('Alertas configurados')).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole('button', { name: /^Alertas/ }));
  expect(screen.getByRole('dialog', { name: 'Alertas' })).toBeVisible();
  expect(screen.getByText('Nenhuma notificação disponível.')).toBeVisible();
  expect(screen.getByText('Alertas configurados')).toBeVisible();
});
