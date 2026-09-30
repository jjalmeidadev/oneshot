import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import App from '@/App';
import type { AccessProfile, ProfileKey } from '@/lib/api';
import { response as chatResponse } from '@/tests/fixtures';

function profile(
  profileKey: ProfileKey = 'pmo',
  overrides: Partial<AccessProfile> = {},
): AccessProfile {
  const roleNames: Record<ProfileKey, string> = {
    pmo: 'pmo',
    lider_subportfolio: 'lider_subportfolio',
    gerente_projeto: 'equipe_projeto',
    consulta: 'consulta',
  };
  return {
    display_name: '[DEMO] Usuario',
    email: 'mvp.usuario@oneshot.example.com',
    role_name: roleNames[profileKey],
    profile_key: profileKey,
    scope_label: 'Portfólio completo',
    can_read: true,
    can_write: false,
    can_export: true,
    ...overrides,
  };
}

async function enter(profileKey: ProfileKey = 'pmo', token = 'jwt-secret') {
  await userEvent.selectOptions(screen.getByLabelText('Persona'), profileKey);
  await userEvent.type(screen.getByLabelText('Access token JWT'), token);
  await userEvent.click(screen.getByRole('button', { name: 'Entrar' }));
}

function backgroundResponse(url: string): Response | null {
  if (url.includes('/notifications')) {
    return new Response(JSON.stringify({ items: [], unread_count: 0 }));
  }
  if (url.includes('/alert-subscriptions')) {
    return new Response(JSON.stringify([]));
  }
  return null;
}

describe('Sessão de acesso em memória', () => {
  it('não monta a aplicação antes da validação e exige persona e token', async () => {
    const fetch = vi.fn();
    vi.stubGlobal('fetch', fetch);
    render(<App />);

    expect(screen.queryByLabelText('Mensagem para o agente')).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Entrar' }));

    expect(screen.getByRole('alert')).toHaveTextContent(
      'Selecione uma persona e informe o token',
    );
    expect(fetch).not.toHaveBeenCalled();
    expect(screen.getByLabelText('Persona')).toHaveFocus();
  });

  it('abre a aplicação quando persona e perfil real correspondem sem expor o token', async () => {
    const fetch = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(profile('pmo')), { status: 200 }),
    );
    vi.stubGlobal('fetch', fetch);
    render(<App />);

    await enter('pmo', 'jwt-secret');

    expect(await screen.findByLabelText('Mensagem para o agente')).toBeVisible();
    expect(screen.getByText('[DEMO] Usuario')).toBeVisible();
    expect(screen.getByText('PMO')).toBeVisible();
    expect(screen.getByText('Portfólio completo')).toBeVisible();
    expect(document.body).not.toHaveTextContent('jwt-secret');
    expect(screen.queryByLabelText('Access token JWT')).not.toBeInTheDocument();
    expect(window.localStorage.length).toBe(0);
    expect(window.sessionStorage.length).toBe(0);
    expect(fetch.mock.calls[0][1].headers.Authorization).toBe('Bearer jwt-secret');
  });

  it('recusa token válido de outra persona e descarta o valor informado', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify(
            profile('gerente_projeto', {
              display_name: '[DEMO] Gerente de Projeto',
              scope_label: 'Projeto PRJ-0442',
            }),
          ),
        ),
      ),
    );
    render(<App />);

    await enter('pmo');

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'pertence ao perfil Gerente de projeto, mas foi selecionado PMO',
    );
    expect(screen.getByLabelText('Access token JWT')).toHaveValue('');
    expect(screen.queryByLabelText('Mensagem para o agente')).not.toBeInTheDocument();
  });

  it('mantém a entrada para token inválido e limpa o campo', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            error: { code: 'INVALID_ACCESS_TOKEN', message: 'controlada' },
          }),
          { status: 401 },
        ),
      ),
    );
    render(<App />);

    await enter('consulta');

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'token informado é inválido ou expirou',
    );
    expect(screen.getByLabelText('Access token JWT')).toHaveValue('');
  });

  it('logout desmonta o ChatStore e remove a conversa da persona anterior', async () => {
    const fetch = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      const background = backgroundResponse(url);
      if (background) return Promise.resolve(background);
      if (url.includes('/access/me')) {
        const authorization = (init?.headers as Record<string, string>)?.Authorization;
        const selected = authorization === 'Bearer jwt-consulta'
          ? profile('consulta', {
              display_name: '[DEMO] Consulta',
              scope_label: 'Projeto PRJ-0510',
              can_export: false,
            })
          : profile('pmo');
        return Promise.resolve(new Response(JSON.stringify(selected)));
      }
      return Promise.resolve(new Response(JSON.stringify(chatResponse)));
    });
    vi.stubGlobal('fetch', fetch);
    render(<App />);
    await enter('pmo');
    const composer = await screen.findByLabelText('Mensagem para o agente');
    fireEvent.change(composer, { target: { value: 'prazo' } });
    await userEvent.click(screen.getByRole('button', { name: 'Enviar mensagem' }));
    expect(await screen.findByText(chatResponse.text)).toBeVisible();

    await userEvent.click(screen.getByRole('button', { name: 'Sair' }));
    expect(screen.queryByText(chatResponse.text)).not.toBeInTheDocument();
    await enter('consulta', 'jwt-consulta');
    expect(await screen.findByText('[DEMO] Consulta')).toBeVisible();
    expect(screen.queryByText(chatResponse.text)).not.toBeInTheDocument();
  });

  it('401 encerra a sessão, enquanto 403 preserva o perfil validado', async () => {
    const fetch401 = vi.fn().mockImplementation((url: string) => {
      const background = backgroundResponse(url);
      if (background) return Promise.resolve(background);
      if (url.includes('/access/me')) {
        return Promise.resolve(new Response(JSON.stringify(profile('pmo'))));
      }
      return Promise.resolve(
        new Response(
          JSON.stringify({ error: { code: 'INVALID_ACCESS_TOKEN', message: 'x' } }),
          { status: 401 },
        ),
      );
    });
    vi.stubGlobal('fetch', fetch401);
    const first = render(<App />);
    await enter('pmo');
    fireEvent.change(await screen.findByLabelText('Mensagem para o agente'), {
      target: { value: 'prazo' },
    });
    await userEvent.click(screen.getByRole('button', { name: 'Enviar mensagem' }));
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Sua sessão expirou ou não é mais válida',
    );
    first.unmount();

    const fetch403 = vi.fn().mockImplementation((url: string) => {
      const background = backgroundResponse(url);
      if (background) return Promise.resolve(background);
      if (url.includes('/access/me')) {
        return Promise.resolve(new Response(JSON.stringify(profile('pmo'))));
      }
      return Promise.resolve(
        new Response(
          JSON.stringify({
            error: { code: 'OUT_OF_SCOPE_FOR_PROFILE', message: 'x' },
          }),
          { status: 403 },
        ),
      );
    });
    vi.stubGlobal('fetch', fetch403);
    render(<App />);
    await enter('pmo');
    fireEvent.change(await screen.findByLabelText('Mensagem para o agente'), {
      target: { value: 'fora do escopo' },
    });
    await userEvent.click(screen.getByRole('button', { name: 'Enviar mensagem' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('não tem acesso');
    expect(screen.getByRole('button', { name: 'Sair' })).toBeVisible();
  });

  it('recarregar a árvore exige nova entrada e o formulário funciona por teclado', async () => {
    const fetch = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(profile('pmo')), { status: 200 }),
    );
    vi.stubGlobal('fetch', fetch);
    const view = render(<App />);
    expect(screen.getByLabelText('Persona')).toHaveFocus();
    await userEvent.selectOptions(screen.getByLabelText('Persona'), 'pmo');
    await userEvent.tab();
    await userEvent.type(screen.getByLabelText('Access token JWT'), 'keyboard-jwt');
    await userEvent.keyboard('{Enter}');
    expect(await screen.findByLabelText('Mensagem para o agente')).toBeVisible();

    view.unmount();
    render(<App />);
    expect(screen.getByLabelText('Access token JWT')).toHaveValue('');
    expect(screen.queryByLabelText('Mensagem para o agente')).not.toBeInTheDocument();
  });
});
