import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
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
  await userEvent.type(screen.getByLabelText('Senha'), 'test-password');
  await userEvent.click(screen.getByRole('button', { name: 'Entrar' }));
  await screen.findByLabelText('Mensagem para o agente');
}

function successfulResponse(url: string): Response {
  if (url.includes('/access/login')) {
    return new Response(
      JSON.stringify({ access_token: 'test-token', profile: accessProfile }),
    );
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
  it('exibe o reprodutor da resposta obtida pela rota de chat', async () => {
    const createObjectURL = vi.fn().mockReturnValue('blob:tts-answer');
    vi.stubGlobal('URL', { ...URL, createObjectURL, revokeObjectURL: vi.fn() });
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            ...response,
            speech: {
              status: 'available',
              media_type: 'audio/mpeg',
              data_base64: btoa('ID3audio'),
              warning: null,
            },
          }),
        ),
      ),
    );
    const view = render(<App />);
    fireEvent.change(screen.getByRole('textbox', { name: 'Mensagem para o agente' }), {
      target: { value: 'prazo' },
    });
    await userEvent.click(screen.getByRole('button', { name: 'Enviar mensagem' }));
    expect(await screen.findByLabelText('Resposta em áudio')).toHaveAttribute(
      'src',
      'blob:tts-answer',
    );
    expect(screen.getByRole('log')).toHaveTextContent(response.text);
    view.unmount();
    vi.unstubAllGlobals();
  });

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
    // O painel de fontes começa fechado e abre pelo botão do cabeçalho.
    await userEvent.click(screen.getByRole('button', { name: /da última resposta/ }));
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
  it('perfil aparece na engrenagem, sem campo de token, e AppShell anuncia falhas', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        if (
          url.includes('/access/login') ||
          url.includes('/notifications') ||
          url.includes('/alert-subscriptions')
        ) {
          return Promise.resolve(successfulResponse(url));
        }
        return Promise.reject(new TypeError('private error'));
      }),
    );
    render(<App />);
    await authenticate();
    expect(screen.queryByText('[DEMO] PMO')).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Ajustes do agente' }));
    const ajustes = screen.getByRole('dialog', { name: 'Ajustes do agente' });
    expect(within(ajustes).getByText('[DEMO] PMO')).toBeVisible();
    expect(within(ajustes).getByText('PMO · Portfólio completo')).toBeVisible();
    expect(within(ajustes).getByRole('button', { name: 'Sair' })).toBeVisible();
    expect(
      screen.queryByLabelText('Token de acesso da sessão'),
    ).not.toBeInTheDocument();
    expect(document.body).not.toHaveTextContent('test-password');
    expect(window.localStorage.getItem('test-token')).toBeNull();
    await userEvent.keyboard('{Escape}');
    fireEvent.change(screen.getByRole('textbox', { name: 'Mensagem para o agente' }), {
      target: { value: 'prazo' },
    });
    await userEvent.click(screen.getByRole('button', { name: 'Enviar mensagem' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Não foi possível');
  });
  it('sair pela engrenagem volta para a tela de entrada', async () => {
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockImplementation((url: string) => Promise.resolve(successfulResponse(url))),
    );
    render(<App />);
    await authenticate();
    await userEvent.click(screen.getByRole('button', { name: 'Ajustes do agente' }));
    await userEvent.click(screen.getByRole('button', { name: 'Sair' }));
    expect(await screen.findByLabelText('Persona')).toBeVisible();
    expect(screen.queryByLabelText('Mensagem para o agente')).not.toBeInTheDocument();
  });
  it('tela padrão sem detalhes técnicos, que voltam pelo modo técnico', async () => {
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockImplementation((url: string) => Promise.resolve(successfulResponse(url))),
    );
    render(<App />);
    await authenticate();
    expect(screen.queryByRole('switch')).not.toBeInTheDocument();
    expect(screen.queryByText(/Validação de intenção/)).not.toBeInTheDocument();
    expect(
      screen.queryByLabelText('Token de acesso da sessão'),
    ).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: /da última resposta/ })).toHaveAttribute(
      'aria-pressed',
      'false',
    );

    const input = screen.getByRole('textbox', { name: 'Mensagem para o agente' });
    fireEvent.change(input, { target: { value: 'prazo' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    await waitFor(() =>
      expect(screen.getByRole('log')).toHaveTextContent(response.text),
    );
    const log = screen.getByRole('log');
    expect(within(log).queryByText(response.model)).not.toBeInTheDocument();
    expect(within(log).queryByText(response.intent!.specific!)).not.toBeInTheDocument();
    expect(screen.queryByText(/Iniciada em/)).not.toBeInTheDocument();
    expect(screen.queryByRole('tab', { name: 'Resposta' })).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: 'Ajustes do agente' }));
    await userEvent.click(
      screen.getByRole('switch', { name: 'Mostrar detalhes técnicos' }),
    );
    await userEvent.keyboard('{Escape}');
    expect(within(log).getByText(response.model)).toBeVisible();
    expect(within(log).getByText(response.intent!.specific!)).toBeVisible();
    expect(screen.getByText(/Iniciada em/)).toBeVisible();
  });
  it('atalho de teclado leva o foco ao campo de mensagem', async () => {
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockImplementation((url: string) => Promise.resolve(successfulResponse(url))),
    );
    render(<App />);
    await authenticate();
    (document.activeElement as HTMLElement | null)?.blur();
    await userEvent.tab();
    const skip = screen.getByRole('link', { name: 'Pular para o campo de mensagem' });
    expect(skip).toHaveFocus();
    await userEvent.keyboard('{Enter}');
    expect(
      screen.getByRole('textbox', { name: 'Mensagem para o agente' }),
    ).toHaveFocus();
    expect(screen.getByRole('navigation', { name: 'Conversas' })).toBeVisible();
    expect(screen.getByRole('main')).toBeVisible();
  });
  it('entre 1024 e 1279 px as fontes deslizam e devolvem o foco ao fechar', async () => {
    vi.spyOn(window, 'matchMedia').mockImplementation(
      (query) =>
        ({
          matches: query.includes('1024'),
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
    // A barra de conversas continua fixa nessa faixa.
    expect(screen.getByRole('navigation', { name: 'Conversas' })).toBeVisible();
    const input = screen.getByRole('textbox', { name: 'Mensagem para o agente' });
    fireEvent.change(input, { target: { value: 'prazo' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    await waitFor(() =>
      expect(screen.getByRole('log')).toHaveTextContent(response.text),
    );
    const sources = screen.getByRole('button', { name: /da última resposta/ });
    sources.focus();
    await userEvent.keyboard('{Enter}');
    expect(screen.getByRole('dialog', { name: 'Fontes da resposta' })).toBeVisible();
    await userEvent.keyboard('{Escape}');
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
    expect(sources).toHaveFocus();
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
