import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import App from '@/App';
import type { ChatResponse, DataChangePreview } from '@/lib/api';
import { toAssistantMessage } from '@/lib/domain';

/**
 * Fluxo completo da alteracao pelo chat na aplicacao real (store, lista de
 * mensagens e cartao), com a API simulada no `fetch`.
 */

const gerente = {
  display_name: '[DEMO] Gerente de Projeto',
  email: 'mvp.gerente-projeto@oneshot.example.com',
  role_name: 'equipe_projeto',
  profile_key: 'gerente_projeto',
  scope_label: 'Projeto PRJ-0442',
  can_read: true,
  can_write: true,
  can_export: true,
};

const preview: DataChangePreview = {
  pending_change_id: '7b022b89-6b47-4028-a3fd-e1e144846011',
  project: {
    code: 'PRJ-0442',
    title: 'Modernizacao do Sistema de Sinalizacao da Linha Azul',
  },
  target: {
    entity: 'projeto',
    id: 'f4022396-603b-416d-abe1-5f91e1fdc37f',
    label: 'PRJ-0442',
  },
  field: { key: 'projeto.prazo_final', label: 'Prazo final previsto' },
  before: { value: '2026-12-20', display: '20/12/2026' },
  after: { value: '2027-03-31', display: '31/03/2027' },
  warnings: [],
  expires_at: new Date(Date.now() + 10 * 60_000).toISOString(),
  undo_window_minutes: 15,
};

const chatResponse: ChatResponse = {
  text: 'Confira a alteração antes de confirmar. Prazo final previsto de PRJ-0442: 20/12/2026 → 31/03/2027. Nada foi gravado ainda; a prévia vale por 10 minutos.',
  model: 'alteracao-dados-chat',
  interaction_id: null,
  trace_id: 'aa077c94-0bdb-4538-90ce-a6c6c3b2de3e',
  latency_ms: 0,
  retrieval_ms: 0,
  usage: { input_tokens: 0, output_tokens: 0, thought_tokens: 0, total_tokens: 0 },
  sources: [],
  data_change: { status: 'preview', preview },
};

function api(url: string, init?: RequestInit): Response {
  const json = (body: unknown, status = 200) =>
    new Response(JSON.stringify(body), {
      status,
      headers: { 'Content-Type': 'application/json' },
    });
  if (url.includes('/access/login'))
    return json({ access_token: 'token-gerente', profile: gerente });
  if (url.includes('/notifications')) return json({ items: [], unread_count: 0 });
  if (url.includes('/alert-subscriptions')) return json([]);
  if (url.endsWith('/api/chat')) return json(chatResponse);
  if (url.endsWith('/confirm') && init?.method === 'POST') {
    return json({
      change_id: '312c0d1a-3959-4628-9be1-f834a49f26ab',
      status: 'aplicada',
      field: preview.field,
      target: preview.target,
      before: preview.before,
      after: preview.after,
      applied_at: new Date().toISOString(),
      undo_available_until: new Date(Date.now() + 15 * 60_000).toISOString(),
      correlation_id: 'correlacao-1',
    });
  }
  return json({ detail: 'nao encontrado' }, 404);
}

describe('alteração de dados pelo chat na aplicação', () => {
  it('a resposta do chat vira cartão; confirmado, ele não volta a pedir confirmação', async () => {
    const fetchMock = vi.fn((url: string, init?: RequestInit) =>
      Promise.resolve(api(url, init)),
    );
    vi.stubGlobal('fetch', fetchMock);
    render(<App />);

    await userEvent.selectOptions(screen.getByLabelText('Persona'), 'gerente_projeto');
    await userEvent.type(screen.getByLabelText('Senha'), 'test-password');
    await userEvent.click(screen.getByRole('button', { name: 'Entrar' }));
    const input = await screen.findByLabelText('Mensagem para o agente');

    fireEvent.change(input, {
      target: { value: 'Prorroga o prazo do PRJ-0442 para 31/03/2027' },
    });
    fireEvent.keyDown(input, { key: 'Enter' });

    const cardRegion = await screen.findByRole('region', {
      name: 'Alteração de dados',
    });
    expect(within(cardRegion).getByText('Depois').nextElementSibling).toHaveTextContent(
      '31/03/2027',
    );
    await userEvent.click(
      within(cardRegion).getByRole('button', { name: 'Confirmar alteração' }),
    );
    expect(await within(cardRegion).findByRole('status')).toHaveTextContent(
      'Alteração gravada',
    );

    // Trocar de conversa e voltar nao pode reabrir a confirmacao.
    await userEvent.click(screen.getByRole('button', { name: 'Nova conversa' }));
    await userEvent.click(
      screen.getByRole('button', { name: /^Prorroga o prazo do PRJ-0442/ }),
    );
    const reopened = await screen.findByRole('region', { name: 'Alteração de dados' });
    expect(within(reopened).getByRole('heading')).toHaveTextContent(
      'Alteração gravada',
    );
    expect(
      within(reopened).queryByRole('button', { name: 'Confirmar alteração' }),
    ).not.toBeInTheDocument();

    const confirmCalls = fetchMock.mock.calls.filter(([url]) =>
      String(url).endsWith('/confirm'),
    );
    expect(confirmCalls).toHaveLength(1);
    await waitFor(() =>
      expect(screen.getByRole('log')).toHaveTextContent('Nada foi gravado ainda'),
    );
  });

  it('resposta sem data_change continua sem cartão (backend anterior à S5-06)', () => {
    const message = toAssistantMessage(
      { ...chatResponse, data_change: undefined, model: 'teste' },
      { roundTripMs: 1, intentLayerEnabled: true },
    );
    expect(message.dataChange).toBeUndefined();
    const withChange = toAssistantMessage(chatResponse, {
      roundTripMs: 1,
      intentLayerEnabled: true,
    });
    expect(withChange.dataChange).toEqual({
      outcome: chatResponse.data_change,
      phase: 'idle',
    });
  });
});
