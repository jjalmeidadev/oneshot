import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import App from '@/App';
import { response } from '@/tests/fixtures';

describe('AppShell, barra lateral, sessão e tema', () => {
  it('integra envio, fontes, busca, seleção, exclusão e tema', async () => {
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockImplementation(() =>
          Promise.resolve(new Response(JSON.stringify(response))),
        ),
    );
    render(<App />);
    const input = screen.getByRole('textbox', { name: 'Mensagem para o agente' });
    fireEvent.change(input, { target: { value: 'prazo' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    await waitFor(() =>
      expect(screen.getByRole('log')).toHaveTextContent(response.text),
    );
    // O painel de fontes começa fechado e abre pelo botão do cabeçalho.
    await userEvent.click(screen.getByRole('button', { name: /Fontes da resposta/ }));
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
  it('UserCard guarda token apenas na sessão e AppShell anuncia falhas', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('private error')));
    render(<App />);
    await userEvent.click(screen.getByRole('button', { name: 'Ajustes do agente' }));
    fireEvent.change(screen.getByLabelText('Token de acesso da sessão'), {
      target: { value: 'test-token' },
    });
    expect(screen.getByLabelText('Token de acesso da sessão')).toHaveValue(
      'test-token',
    );
    expect(window.localStorage.getItem('test-token')).toBeNull();
    await userEvent.keyboard('{Escape}');
    fireEvent.change(screen.getByRole('textbox', { name: 'Mensagem para o agente' }), {
      target: { value: 'prazo' },
    });
    await userEvent.click(screen.getByRole('button', { name: 'Enviar mensagem' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Não foi possível');
  });
  it('tela padrão sem detalhes técnicos, que voltam pelo modo técnico', async () => {
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockImplementation(() =>
          Promise.resolve(new Response(JSON.stringify(response))),
        ),
    );
    render(<App />);
    expect(screen.queryByRole('switch')).not.toBeInTheDocument();
    expect(screen.queryByText(/Validação de intenção/)).not.toBeInTheDocument();
    expect(
      screen.queryByLabelText('Token de acesso da sessão'),
    ).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Fontes da resposta/ })).toHaveAttribute(
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
    render(<App />);
    await userEvent.click(screen.getByRole('button', { name: 'Abrir conversas' }));
    expect(screen.getByRole('dialog', { name: 'Conversas' })).toBeVisible();
    await userEvent.keyboard('{Escape}');
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
  });
});
