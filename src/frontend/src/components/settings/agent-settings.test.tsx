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

  it('encaminha as trocas de modo', async () => {
    const props = setup();
    await userEvent.click(screen.getByRole('button', { name: 'Ajustes do agente' }));
    await userEvent.click(
      screen.getByRole('switch', { name: 'Validação de intenção' }),
    );
    await userEvent.click(screen.getByRole('switch', { name: 'Sugestões proativas' }));
    await userEvent.click(
      screen.getByRole('switch', { name: 'Mostrar detalhes técnicos' }),
    );
    expect(props.onIntentLayerChange).toHaveBeenCalledWith(false);
    expect(props.onProactivityChange).toHaveBeenCalledWith(true);
    expect(props.onShowTechnicalDetailsChange).toHaveBeenCalledWith(true);
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

  it('mostra o perfil da sessão numa seção própria', async () => {
    setup({ session: <p>[DEMO] PMO</p> });
    await userEvent.click(screen.getByRole('button', { name: 'Ajustes do agente' }));
    const sessao = screen.getByRole('region', { name: 'Sessão' });
    expect(sessao).toHaveTextContent('[DEMO] PMO');
  });

  it('sem sessão, não mostra a seção', async () => {
    setup();
    await userEvent.click(screen.getByRole('button', { name: 'Ajustes do agente' }));
    expect(screen.queryByRole('region', { name: 'Sessão' })).not.toBeInTheDocument();
  });
});
