import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AlertWorkflowCard } from './alert-workflow-card';
import type { AlertWorkflowResponse } from '@/lib/api';

const actions = vi.hoisted(() => ({
  answerWorkflow: vi.fn(),
  confirmWorkflow: vi.fn(),
  cancelWorkflow: vi.fn(),
}));
vi.mock('@/state/chat-store', () => ({ useChatStore: () => actions }));
const base: AlertWorkflowResponse = {
  contract_version: '1.0',
  session_id: 'session-alert-1',
  workflow: 'alerta_prazo_atraso',
  status: 'active',
  current_step: 'threshold',
  revision: 2,
  answers: {},
  warnings: [],
};

describe('Interações de AlertWorkflowCard', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    actions.answerWorkflow.mockResolvedValue(undefined);
    actions.confirmWorkflow.mockResolvedValue(undefined);
    actions.cancelWorkflow.mockResolvedValue(undefined);
  });

  it('encaminha opção da etapa atual', async () => {
    const workflow: AlertWorkflowResponse = {
      ...base,
      current_step: 'project',
      question: {
        step: 'project',
        prompt: 'Qual projeto?',
        input_type: 'single_select',
        options: [{ value: 'p1', label: 'Projeto Um' }],
      },
    };
    render(<AlertWorkflowCard workflow={workflow} />);
    await userEvent.click(screen.getByRole('button', { name: 'Projeto Um' }));
    expect(actions.answerWorkflow).toHaveBeenCalledWith(workflow, 'project', 'p1');
  });

  it.each([undefined, 12])(
    'permite editar limiar inicial %s e envia número',
    async (candidate) => {
      const workflow: AlertWorkflowResponse = {
        ...base,
        answers: { threshold_candidate: candidate },
        question: {
          step: 'threshold',
          prompt: 'Quantos dias?',
          input_type: 'number',
          options: [],
        },
      };
      render(<AlertWorkflowCard workflow={workflow} />);
      expect(screen.getByRole('spinbutton', { name: 'Dias de atraso' })).toHaveValue(
        candidate ?? 7,
      );
      fireEvent.change(screen.getByRole('spinbutton'), { target: { value: '15' } });
      await userEvent.click(screen.getByRole('button', { name: 'Continuar' }));
      expect(actions.answerWorkflow).toHaveBeenCalledWith(workflow, 'threshold', 15);
    },
  );

  it('bloqueia confirmação concorrente, comunica falha e permite tentar novamente', async () => {
    let reject!: (reason: Error) => void;
    actions.confirmWorkflow.mockImplementationOnce(
      () =>
        new Promise<void>((_, rejectPromise) => {
          reject = rejectPromise;
        }),
    );
    const workflow: AlertWorkflowResponse = {
      ...base,
      status: 'ready_for_confirmation',
      confirmation_summary: 'Ativar alerta para Projeto Um?',
    };
    render(<AlertWorkflowCard workflow={workflow} />);
    const activate = screen.getByRole('button', { name: 'Ativar alerta' });
    await userEvent.click(activate);
    expect(activate).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Cancelar' })).toBeDisabled();
    reject(new Error('Interno'));
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Nao foi possivel atualizar o alerta.',
    );
    expect(activate).toBeEnabled();
    await userEvent.click(activate);
    await waitFor(() => expect(screen.queryByRole('alert')).not.toBeInTheDocument());
    expect(actions.confirmWorkflow).toHaveBeenCalledTimes(2);
    await userEvent.click(screen.getByRole('button', { name: 'Cancelar' }));
    expect(actions.cancelWorkflow).toHaveBeenCalledWith(workflow);
  });

  it('informa cancelamento sem oferecer confirmação', () => {
    render(<AlertWorkflowCard workflow={{ ...base, status: 'cancelled' }} />);
    expect(screen.getByText('Configuracao cancelada.')).toBeVisible();
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });
});
