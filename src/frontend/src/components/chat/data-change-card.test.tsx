import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type {
  DataChangeConfirmResponse,
  DataChangeHistoryItem,
  DataChangeOutcome,
  DataChangePreview,
} from '@/lib/api';
import type { DataChangeState } from '@/lib/domain';

const store = vi.hoisted(() => ({
  accessToken: 'token-gerente',
  activeConversation: { id: 'conversa-1' },
  updateDataChange: vi.fn(),
}));

vi.mock('@/state/chat-store', () => ({ useChatStore: () => store }));

import { DataChangeCard } from './data-change-card';

const FUTURE = new Date(Date.now() + 10 * 60_000).toISOString();

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
  expires_at: FUTURE,
  undo_window_minutes: 15,
};

const previewState: DataChangeState = {
  outcome: { status: 'preview', preview },
  phase: 'idle',
};

const confirmed: DataChangeConfirmResponse = {
  change_id: '312c0d1a-3959-4628-9be1-f834a49f26ab',
  status: 'aplicada',
  field: preview.field,
  target: preview.target,
  before: preview.before,
  after: preview.after,
  applied_at: new Date().toISOString(),
  undo_available_until: new Date(Date.now() + 15 * 60_000).toISOString(),
  correlation_id: 'correlacao-1',
};

type Route = { method: string; path: RegExp; status: number; body: unknown };

/** `fetch` falso que registra as chamadas e responde por metodo e caminho. */
function mockApi(routes: Route[]) {
  const calls: {
    method: string;
    url: string;
    body: unknown;
    headers: HeadersInit | undefined;
  }[] = [];
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = init?.method ?? 'GET';
      calls.push({
        method,
        url,
        body: init?.body ? JSON.parse(String(init.body)) : undefined,
        headers: init?.headers,
      });
      const route = routes.find(
        (item) => item.method === method && item.path.test(url),
      );
      if (!route) return new Response('{}', { status: 404 });
      return new Response(JSON.stringify(route.body), {
        status: route.status,
        headers: { 'Content-Type': 'application/json' },
      });
    }),
  );
  return calls;
}

function card(state: DataChangeState = previewState) {
  return render(<DataChangeCard messageId="mensagem-1" state={state} />);
}

describe('DataChangeCard', () => {
  beforeEach(() => vi.clearAllMocks());

  it('estado de prévia: mostra antes e depois e pede confirmação sem gravar nada', () => {
    card();

    const section = screen.getByRole('region', { name: 'Alteração de dados' });
    expect(within(section).getByText('Prazo final previsto')).toBeInTheDocument();
    expect(within(section).getByText('Antes').nextElementSibling).toHaveTextContent(
      '20/12/2026',
    );
    expect(within(section).getByText('Depois').nextElementSibling).toHaveTextContent(
      '31/03/2027',
    );
    expect(within(section).getByText(/precisa da sua confirmação/)).toBeInTheDocument();
    expect(within(section).getByText(/Nada foi gravado ainda/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Confirmar alteração' })).toBeEnabled();
    expect(screen.getByRole('button', { name: 'Cancelar' })).toBeEnabled();
  });

  it('estado de confirmação: grava, mostra o resultado e oferece desfazer', async () => {
    const calls = mockApi([
      { method: 'POST', path: /\/confirm$/, status: 200, body: confirmed },
    ]);
    card();

    await userEvent.type(
      screen.getByLabelText(/Justificativa/),
      'Replanejamento aprovado em 03/10',
    );
    await userEvent.click(screen.getByRole('button', { name: 'Confirmar alteração' }));

    expect(
      await screen.findByRole('heading', { name: /Alteração gravada/ }),
    ).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveTextContent(/Alteração gravada às/);
    expect(screen.getByRole('status')).toHaveTextContent(/Você pode desfazer até/);
    expect(
      screen.queryByRole('button', { name: 'Confirmar alteração' }),
    ).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Desfazer' })).toBeInTheDocument();

    expect(calls[0].url).toBe(
      `/api/data-change-previews/${preview.pending_change_id}/confirm`,
    );
    expect(calls[0].body).toEqual({ reason: 'Replanejamento aprovado em 03/10' });
    expect(calls[0].headers).toMatchObject({ Authorization: 'Bearer token-gerente' });
    expect(store.updateDataChange).toHaveBeenLastCalledWith(
      'mensagem-1',
      expect.objectContaining({ phase: 'applied', change: confirmed }),
    );
  });

  it('estado de cancelamento: descarta a prévia e informa que nada foi gravado', async () => {
    const calls = mockApi([
      { method: 'POST', path: /\/cancel$/, status: 200, body: { status: 'cancelada' } },
    ]);
    card();

    await userEvent.click(screen.getByRole('button', { name: 'Cancelar' }));

    expect(await screen.findByRole('status')).toHaveTextContent(
      'Alteração cancelada. Nada foi gravado.',
    );
    expect(
      screen.queryByRole('button', { name: 'Confirmar alteração' }),
    ).not.toBeInTheDocument();
    expect(calls).toHaveLength(1);
    expect(calls[0].url).toMatch(/\/cancel$/);
    expect(store.updateDataChange).toHaveBeenLastCalledWith(
      'mensagem-1',
      expect.objectContaining({ phase: 'cancelled' }),
    );
  });

  it('estado de erro final: mostra a mensagem do backend e não oferece repetir', async () => {
    mockApi([
      {
        method: 'POST',
        path: /\/confirm$/,
        status: 409,
        body: {
          error: {
            code: 'STALE_PREVIEW',
            message:
              'O valor mudou depois da prévia. Peça a alteração de novo para conferir o valor atual.',
          },
        },
      },
    ]);
    card();

    await userEvent.click(screen.getByRole('button', { name: 'Confirmar alteração' }));

    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('O valor mudou depois da prévia');
    expect(alert).toHaveTextContent('Nada foi gravado.');
    expect(
      screen.getByRole('heading', { name: /Não foi possível alterar/ }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: /Confirmar|Tentar de novo/ }),
    ).not.toBeInTheDocument();
  });

  it('estado de erro transitório: mantém a prévia e permite tentar de novo', async () => {
    mockApi([
      {
        method: 'POST',
        path: /\/confirm$/,
        status: 503,
        body: {
          error: {
            code: 'DATA_CHANGE_UNAVAILABLE',
            message:
              'A alteração de dados está indisponível no momento. Nada foi gravado.',
          },
        },
      },
    ]);
    card();

    await userEvent.click(screen.getByRole('button', { name: 'Confirmar alteração' }));

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'indisponível no momento',
    );
    expect(screen.getByRole('button', { name: 'Tentar de novo' })).toBeEnabled();
    expect(screen.getByRole('button', { name: 'Cancelar' })).toBeEnabled();
  });

  it('desfaz a alteração gravada e mostra o valor restaurado', async () => {
    const calls = mockApi([
      {
        method: 'POST',
        path: /\/undo$/,
        status: 200,
        body: {
          change_id: confirmed.change_id,
          status: 'desfeita',
          restored: preview.before,
          undone_at: new Date().toISOString(),
        },
      },
    ]);
    card({ ...previewState, phase: 'applied', change: confirmed });

    await userEvent.click(screen.getByRole('button', { name: 'Desfazer' }));

    expect(await screen.findByRole('status')).toHaveTextContent(
      'Alteração desfeita. Prazo final previsto voltou para 20/12/2026.',
    );
    expect(screen.queryByRole('button', { name: 'Desfazer' })).not.toBeInTheDocument();
    expect(calls[0].url).toBe(`/api/data-changes/${confirmed.change_id}/undo`);
  });

  it('não oferece desfazer depois da janela de 15 minutos', () => {
    card({
      ...previewState,
      phase: 'applied',
      change: {
        ...confirmed,
        undo_available_until: new Date(Date.now() - 1000).toISOString(),
      },
    });
    expect(screen.getByRole('status')).toHaveTextContent('Alteração gravada');
    expect(screen.queryByRole('button', { name: 'Desfazer' })).not.toBeInTheDocument();
  });

  it('não oferece confirmar uma prévia expirada', () => {
    card({
      outcome: {
        status: 'preview',
        preview: { ...preview, expires_at: new Date(Date.now() - 1000).toISOString() },
      },
      phase: 'idle',
    });
    expect(screen.getByRole('status')).toHaveTextContent(
      'A prévia expirou e nada foi gravado.',
    );
    expect(
      screen.queryByRole('button', { name: 'Confirmar alteração' }),
    ).not.toBeInTheDocument();
  });

  it('exibe os avisos da prévia', () => {
    card({
      outcome: {
        status: 'preview',
        preview: { ...preview, warnings: ['A data informada já passou.'] },
      },
      phase: 'idle',
    });
    expect(screen.getByRole('list', { name: 'Avisos' })).toHaveTextContent(
      'A data informada já passou.',
    );
  });

  it('mostra o histórico do campo ao abrir', async () => {
    const item: DataChangeHistoryItem = {
      change_id: confirmed.change_id,
      field: preview.field,
      target: preview.target,
      before: preview.before,
      after: preview.after,
      requested_by: '[DEMO] Gerente de Projeto',
      applied_at: '2026-10-06T17:32:51Z',
      status: 'desfeita',
      undone_at: '2026-10-06T17:35:00Z',
      can_undo: false,
    };
    const calls = mockApi([
      {
        method: 'GET',
        path: /\/api\/data-changes\?/,
        status: 200,
        body: { items: [item] },
      },
    ]);
    card({ ...previewState, phase: 'applied', change: confirmed });

    const toggle = screen.getByRole('button', { name: 'Histórico do campo' });
    expect(toggle).toHaveAttribute('aria-expanded', 'false');
    await userEvent.click(toggle);

    const list = await screen.findByRole('list', { name: 'Alterações do campo' });
    expect(list).toHaveTextContent('20/12/2026');
    expect(list).toHaveTextContent('31/03/2027');
    expect(list).toHaveTextContent('[DEMO] Gerente de Projeto');
    expect(list).toHaveTextContent('Desfeita');
    expect(toggle).toHaveAttribute('aria-expanded', 'true');
    const url = new URL(calls[0].url, 'http://localhost');
    expect(url.pathname).toBe('/api/data-changes');
    expect(url.searchParams.get('project_code')).toBe('PRJ-0442');
    expect(url.searchParams.get('field')).toBe('projeto.prazo_final');
    expect(url.searchParams.get('target_id')).toBe(preview.target.id);
  });

  it('pedido recusado não mostra ações', () => {
    card({
      outcome: {
        status: 'rejected',
        code: 'OUT_OF_SCOPE_FOR_PROFILE',
        message: 'Seu perfil não tem permissão para alterar dados do PRJ-0442.',
      },
      phase: 'idle',
    });
    expect(
      screen.getByRole('region', { name: 'Alteração de dados' }),
    ).toHaveTextContent('Nada foi alterado');
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('pergunta com candidatos cria a prévia do registro escolhido', async () => {
    const outcome: DataChangeOutcome = {
      status: 'needs_input',
      missing: 'target',
      question: 'Encontrei mais de uma atividade parecida. Qual delas?',
      candidates: [
        {
          id: 'atividade-1',
          label: 'Instalacao do lote 1 de equipamentos de sinalizacao',
        },
        {
          id: 'atividade-2',
          label: 'Instalacao do lote 2 de equipamentos de sinalizacao',
        },
      ],
      draft: {
        project_code: 'PRJ-0442',
        entity: 'cronograma',
        field: 'cronograma.status',
        item_reference: 'instalação',
        raw_value: 'atrasado',
      },
    };
    const calls = mockApi([
      {
        method: 'POST',
        path: /\/api\/data-change-previews$/,
        status: 200,
        body: { status: 'preview', preview },
      },
    ]);
    card({ outcome, phase: 'idle' });

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Instalacao do lote 2 de equipamentos de sinalizacao',
      }),
    );

    expect(
      await screen.findByRole('button', { name: 'Confirmar alteração' }),
    ).toBeInTheDocument();
    expect(calls[0].body).toEqual({
      project_code: 'PRJ-0442',
      entity: 'cronograma',
      field: 'cronograma.status',
      target_id: 'atividade-2',
      item_reference: null,
      raw_value: 'atrasado',
      conversation_id: 'conversa-1',
    });
  });

  it('pergunta de valor mostra a regra quando o valor é inválido', async () => {
    mockApi([
      {
        method: 'POST',
        path: /\/api\/data-change-previews$/,
        status: 422,
        body: {
          error: {
            code: 'INVALID_VALUE',
            message: 'O progresso deve estar entre 0 e 100%.',
          },
        },
      },
    ]);
    card({
      outcome: {
        status: 'needs_input',
        missing: 'value',
        question: 'Qual o novo progresso, de 0 a 100%?',
        draft: {
          project_code: 'PRJ-0442',
          entity: 'cronograma',
          field: 'cronograma.progresso',
          target_id: 'atividade-2',
        },
      },
      phase: 'idle',
    });

    await userEvent.type(screen.getByLabelText('Novo valor'), '140');
    await userEvent.click(screen.getByRole('button', { name: 'Ver prévia' }));

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'O progresso deve estar entre 0 e 100%.',
    );
    await waitFor(() =>
      expect(screen.getByLabelText('Novo valor')).toHaveAttribute('aria-invalid'),
    );
  });

  it('orientação sem pedido reconhecível não desenha cartão', () => {
    const { container } = card({
      outcome: {
        status: 'needs_input',
        missing: 'field',
        question: 'Diga o projeto...',
      },
      phase: 'idle',
    });
    expect(container).toBeEmptyDOMElement();
  });
});
