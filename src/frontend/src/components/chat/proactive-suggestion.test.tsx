import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { ProactiveSuggestion } from './proactive-suggestion';
import { TypingIndicator } from './typing-indicator';
import { toAssistantMessage } from '@/lib/domain';
import { response } from '@/tests/fixtures';

const suggestion = toAssistantMessage(response, {
  roundTripMs: 10,
  intentLayerEnabled: true,
}).proactiveSuggestion!;

describe('Sugestão proativa e espera', () => {
  it('encaminha aceitar e recusar sem execução automática', async () => {
    const resolve = vi.fn();
    render(
      <ProactiveSuggestion
        suggestion={{ ...suggestion, status: 'pending' }}
        onResolve={resolve}
      />,
    );
    expect(screen.getByRole('region', { name: 'Sugestão opcional' })).toHaveTextContent(
      suggestion.description,
    );
    expect(resolve).not.toHaveBeenCalled();
    await userEvent.click(screen.getByRole('button', { name: 'Aceitar sugestão' }));
    await userEvent.click(screen.getByRole('button', { name: 'Recusar sugestão' }));
    expect(resolve.mock.calls).toEqual([['accept'], ['decline']]);
  });

  it.each(['accepting', 'declining'] as const)(
    'impede decisão concorrente em %s',
    async (status) => {
      const resolve = vi.fn();
      render(
        <ProactiveSuggestion
          suggestion={{ ...suggestion, status }}
          onResolve={resolve}
        />,
      );
      for (const button of screen.getAllByRole('button')) {
        expect(button).toBeDisabled();
        await userEvent.click(button);
      }
      expect(resolve).not.toHaveBeenCalled();
    },
  );

  it.each([
    ['accepted', 'Sugestão aceita e executada.'],
    ['declined', 'Sugestão recusada sem execução.'],
  ] as const)('anuncia %s e remove ações', (status, label) => {
    render(
      <ProactiveSuggestion
        suggestion={{ ...suggestion, status }}
        onResolve={vi.fn()}
      />,
    );
    expect(screen.getByRole('status')).toHaveTextContent(label);
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('TypingIndicator atualiza a etapa exibida', () => {
    const { rerender } = render(<TypingIndicator label="Consultando fontes" />);
    expect(screen.getByText('Consultando fontes')).toBeVisible();
    rerender(<TypingIndicator label="Preparando resposta" />);
    expect(screen.getByText('Preparando resposta')).toBeVisible();
    expect(screen.queryByText('Consultando fontes')).not.toBeInTheDocument();
  });
});
