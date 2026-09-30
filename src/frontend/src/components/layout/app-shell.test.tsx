import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import App from '@/App';
import { response } from '@/tests/fixtures';

const accessProfile = {
  display_name: '[DEMO] PMO',
  email: 'mvp.pmo@oneshot.example.com',
  role_name: 'pmo',
  profile_key: 'pmo',
  scope_label: 'Portfólio completo',
  can_read: true,
  can_write: false,
  can_export: true,
};

async function authenticate() {
  await userEvent.selectOptions(screen.getByLabelText('Persona'), 'pmo');
  await userEvent.type(screen.getByLabelText('Access token JWT'), 'test-token');
  await userEvent.click(screen.getByRole('button', { name: 'Entrar' }));
  await screen.findByLabelText('Mensagem para o agente');
}

function successfulResponse(url: string): Response {
  if (url.includes('/access/me')) {
    return new Response(JSON.stringify(accessProfile));
  }
  if (url.includes('/notifications')) {
    return new Response(JSON.stringify({ items: [], unread_count: 0 }));
  }
  if (url.includes('/alert-subscriptions')) {
    return new Response(JSON.stringify([]));
  }
  return new Response(JSON.stringify(response));
}

describe('AppShell, barra lateral, sessão e tema', () => {
  it('integra envio, fontes, busca, seleção, exclusão e tema', async () => {
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockImplementation((url: string) => Promise.resolve(successfulResponse(url))),
    );
    render(<App />);
    await authenticate();
    const input = screen.getByRole('textbox', { name: 'Mensagem para o agente' });
    fireEvent.change(input, { target: { value: 'prazo' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    await waitFor(() =>
      expect(screen.getByRole('log')).toHaveTextContent(response.text),
    );
    await waitFor(() =>
      expect(screen.getByText('Entrega prevista para dezembro.')).toBeVisible(),
    );
    const search = screen.getByRole('searchbox');
    fireEvent.change(search, { target: { value: 'inexistente' } });
    expect(screen.getByText('Nenhuma conversa encontrada')).toBeVisible();
    fireEvent.change(search, { target: { value: '' } });
    await userEvent.click(screen.getByRole('button', { name: 'Nova conversa' }));
    await userEvent.click(screen.getByRole('button', { name: /prazo.*O projeto/ }));
    expect(screen.getByRole('log')).toHaveTextContent(response.text);
    await userEvent.click(
      screen.getByRole('button', { name: 'Excluir conversa prazo' }),
    );
    expect(screen.queryByRole('log')).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Usar tema escuro' }));
    expect(document.documentElement).toHaveClass('dark');
    await userEvent.click(screen.getByRole('button', { name: 'Usar tema claro' }));
    expect(document.documentElement).not.toHaveClass('dark');
  });

  it('UserCard mostra perfil sem token e AppShell anuncia falhas', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        if (url.includes('/access/me')) {
          return Promise.resolve(new Response(JSON.stringify(accessProfile)));
        }
        if (url.includes('/notifications') || url.includes('/alert-subscriptions')) {
          return Promise.resolve(successfulResponse(url));
        }
        return Promise.reject(new TypeError('private error'));
      }),
    );
    render(<App />);
    await authenticate();
    expect(screen.getByText('[DEMO] PMO')).toBeVisible();
    expect(screen.getByText('Portfólio completo')).toBeVisible();
    expect(document.body).not.toHaveTextContent('test-token');
    expect(window.localStorage.getItem('test-token')).toBeNull();
    fireEvent.change(screen.getByRole('textbox', { name: 'Mensagem para o agente' }), {
      target: { value: 'prazo' },
    });
    await userEvent.click(screen.getByRole('button', { name: 'Enviar mensagem' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Não foi possível');
  });

  it('layout móvel abre e fecha o diálogo de conversas pelo teclado', async () => {
    vi.spyOn(window, 'matchMedia').mockImplementation(
      (query) =>
        ({
          matches: false,
          media: query,
          addEventListener: vi.fn(),
          removeEventListener: vi.fn(),
        }) as unknown as MediaQueryList,
    );
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockImplementation((url: string) => Promise.resolve(successfulResponse(url))),
    );
    render(<App />);
    await authenticate();
    await userEvent.click(screen.getByRole('button', { name: 'Abrir conversas' }));
    expect(screen.getByRole('dialog', { name: 'Conversas' })).toBeVisible();
    await userEvent.keyboard('{Escape}');
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
  });
});
