import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { WorkflowSessionResponse } from '@/lib/api';

const actions = vi.hoisted(() => ({
  answerWorkflow: vi.fn(),
  confirmWorkflow: vi.fn(),
  cancelWorkflow: vi.fn(),
  downloadArtifact: vi.fn(),
}));

vi.mock('@/state/chat-store', () => ({ useChatStore: () => actions }));

import { ReportWorkflowCard } from './report-workflow-card';

const base: WorkflowSessionResponse = {
  contract_version: '1.0',
  session_id: 'session-report-1',
  workflow: 'transacao_gerar_relatorio',
  status: 'active',
  current_step: 'scope_type',
  revision: 2,
  answers: {},
  warnings: [],
};

describe('ReportWorkflowCard', () => {
  beforeEach(() => vi.clearAllMocks());

  it('envia uma opcao da pergunta atual', async () => {
    const workflow: WorkflowSessionResponse = {
      ...base,
      question: {
        step: 'scope_type',
        prompt: 'Projeto ou subportfolio?',
        input_type: 'single_select',
        required: true,
        options: [{ value: 'project', label: 'Projeto' }],
      },
    };
    render(<ReportWorkflowCard workflow={workflow} />);
    await userEvent.click(screen.getByRole('button', { name: 'Projeto' }));
    expect(actions.answerWorkflow).toHaveBeenCalledWith(
      workflow,
      'scope_type',
      'project',
    );
  });

  it('coleta intervalo, selecao multipla e texto opcional', async () => {
    const { rerender } = render(
      <ReportWorkflowCard
        workflow={{
          ...base,
          current_step: 'period',
          question: {
            step: 'period',
            prompt: 'Periodo',
            input_type: 'date_range',
            required: true,
            options: [],
          },
        }}
      />,
    );
    await userEvent.type(screen.getByLabelText('Inicio'), '2026-08-01');
    await userEvent.type(screen.getByLabelText('Fim'), '2026-08-31');
    await userEvent.click(screen.getByRole('button', { name: 'Continuar' }));
    expect(actions.answerWorkflow).toHaveBeenLastCalledWith(
      expect.objectContaining({ current_step: 'period' }),
      'period',
      { start_date: '2026-08-01', end_date: '2026-08-31' },
    );

    rerender(
      <ReportWorkflowCard
        workflow={{
          ...base,
          current_step: 'emphasis',
          question: {
            step: 'emphasis',
            prompt: 'Enfase',
            input_type: 'multi_select',
            required: false,
            options: [{ value: 'risks', label: 'Riscos' }],
          },
        }}
      />,
    );
    await userEvent.click(screen.getByLabelText('Riscos'));
    await userEvent.click(screen.getByRole('button', { name: 'Continuar' }));
    expect(actions.answerWorkflow).toHaveBeenLastCalledWith(
      expect.anything(),
      'emphasis',
      ['risks'],
    );

    rerender(
      <ReportWorkflowCard
        workflow={{
          ...base,
          current_step: 'additional_context',
          question: {
            step: 'additional_context',
            prompt: 'Contexto',
            input_type: 'text',
            required: false,
            options: [],
          },
        }}
      />,
    );
    await userEvent.click(
      screen.getByRole('button', { name: 'Continuar sem contexto' }),
    );
    expect(actions.answerWorkflow).toHaveBeenLastCalledWith(
      expect.anything(),
      'additional_context',
      null,
    );
  });

  it('confirma, cancela e baixa o artefato concluido', async () => {
    const ready: WorkflowSessionResponse = {
      ...base,
      status: 'ready_for_confirmation',
      current_step: 'confirmation',
      confirmation_summary: 'Resumo confirmado',
    };
    const { rerender } = render(<ReportWorkflowCard workflow={ready} />);
    await userEvent.click(
      screen.getByRole('button', { name: 'Confirmar e gerar DOCX' }),
    );
    await userEvent.click(screen.getByRole('button', { name: 'Cancelar' }));
    expect(actions.confirmWorkflow).toHaveBeenCalledWith(ready);
    expect(actions.cancelWorkflow).toHaveBeenCalledWith(ready);

    const completed: WorkflowSessionResponse = {
      ...base,
      status: 'completed',
      current_step: 'execution',
      warnings: ['Texto deterministico utilizado.'],
      execution: {
        contract_version: '1.0',
        execution_id: 'execution-1',
        correlation_id: 'correlation-1',
        status: 'completed_with_warnings',
        status_url: '/api/report-requests/execution-1',
        artifact: {
          artifact_id: 'artifact-1',
          file_name: 'relatorio.docx',
          content_type:
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          size_bytes: 2048,
          sha256: 'a'.repeat(64),
          download_url: '/api/report-requests/execution-1/artifact',
          storage_provider: 'local',
          created_at: '2026-09-21T12:00:00Z',
        },
        warnings: ['Texto deterministico utilizado.'],
        created_at: '2026-09-21T12:00:00Z',
        updated_at: '2026-09-21T12:01:00Z',
      },
    };
    rerender(<ReportWorkflowCard workflow={completed} />);
    expect(screen.getByText('Texto deterministico utilizado.')).toBeVisible();
    await userEvent.click(screen.getByRole('button', { name: /Baixar no chat/ }));
    expect(actions.downloadArtifact).toHaveBeenCalledWith(completed);
  });
});
