import { render, screen } from '@testing-library/react';
import { expect, test, vi } from 'vitest';

import { AlertWorkflowCard } from './alert-workflow-card';

vi.mock('@/state/chat-store', () => ({
  useChatStore: () => ({
    answerWorkflow: vi.fn(),
    confirmWorkflow: vi.fn(),
    cancelWorkflow: vi.fn(),
  }),
}));

test('shows the next autonomous evaluation after confirmation', () => {
  render(
    <AlertWorkflowCard
      workflow={{
        contract_version: '1.0',
        session_id: 'session-12345678',
        workflow: 'alerta_prazo_atraso',
        status: 'completed',
        current_step: 'completed',
        revision: 5,
        answers: {},
        warnings: [],
        subscription: {
          subscription_id: 'subscription-1',
          correlation_id: 'correlation-1',
          idempotency_key: 'workflow:session:confirm',
          owner_subject: 'user-1',
          status: 'active',
          revision: 0,
          next_evaluation_at: '2026-09-23T11:00:00Z',
          created_at: '2026-09-22T10:00:00Z',
          updated_at: '2026-09-22T10:00:00Z',
          rule: {
            project_id: 'PRJ-1',
            project_label: 'Projeto Um',
            threshold_days: 7,
            comparison_operator: 'gt',
            day_basis: 'calendar_days',
            trigger_type: 'daily',
            evaluation_time: '08:00:00',
            timezone: 'America/Sao_Paulo',
          },
        },
      }}
    />,
  );
  expect(screen.getByRole('status')).toHaveTextContent('Alerta ativo');
});
