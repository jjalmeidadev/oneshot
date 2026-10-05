import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import { AgentSettings } from './agent-settings';

function setup(overrides: Partial<Parameters<typeof AgentSettings>[0]> = {}) {
  const props = {
    intentLayerEnabled: true,
    onIntentLayerChange: vi.fn(),
    proactivityEnabled: false,
    onProactivityChange: vi.fn(),
    showTechnicalDetails: false,
    onShowTechnicalDetailsChange: vi.fn(),
    accessToken: '',
    onAccessTokenChange: vi.fn(),
    ...overrides,
  };
  render(<AgentSettings {...props} />);
  return props;
}

describe('AgentSettings', () => {
  it('fica recolhida até o usuário abrir a engrenagem', async () => {
    setup();
    expect(screen.queryByRole('switch')).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Ajustes do agente' }));
    expect(screen.getByRole('dialog', { name: 'Ajustes do agente' })).toBeVisible();
    expect(screen.getAllByRole('switch')).toHaveLength(3);
  });

  it('encaminha as trocas de modo e do token', async () => {
    const props = setup();
    await userEvent.click(screen.getByRole('button', { name: 'Ajustes do agente' }));
    await userEvent.click(
      screen.getByRole('switch', { name: 'Validação de intenção' }),
    );
    await userEvent.click(screen.getByRole('switch', { name: 'Sugestões proativas' }));
    await userEvent.click(
      screen.getByRole('switch', { name: 'Mostrar detalhes técnicos' }),
    );
    await userEvent.type(screen.getByLabelText('Token de acesso da sessão'), 'x');
    expect(props.onIntentLayerChange).toHaveBeenCalledWith(false);
    expect(props.onProactivityChange).toHaveBeenCalledWith(true);
    expect(props.onShowTechnicalDetailsChange).toHaveBeenCalledWith(true);
    expect(props.onAccessTokenChange).toHaveBeenCalledWith('x');
  });

  it('bloqueia a proatividade sem a validação de intenção', async () => {
    setup({ intentLayerEnabled: false });
    await userEvent.click(screen.getByRole('button', { name: 'Ajustes do agente' }));
    expect(screen.getByRole('switch', { name: 'Sugestões proativas' })).toBeDisabled();
    expect(screen.getByText('Requer a validação de intenção ligada.')).toBeVisible();
  });

  it('não troca de modo enquanto uma resposta está em andamento', async () => {
    setup({ disabled: true });
    await userEvent.click(screen.getByRole('button', { name: 'Ajustes do agente' }));
    expect(
      screen.getByRole('switch', { name: 'Validação de intenção' }),
    ).toBeDisabled();
    expect(
      screen.getByRole('switch', { name: 'Mostrar detalhes técnicos' }),
    ).toBeEnabled();
  });
});
