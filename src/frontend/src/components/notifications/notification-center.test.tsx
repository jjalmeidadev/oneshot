import { render, screen } from '@testing-library/react';
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
  expect(screen.getByLabelText('0 notificacoes nao lidas')).toBeInTheDocument();
});
