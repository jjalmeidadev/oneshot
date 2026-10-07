import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ConversationSidebar } from './conversation-sidebar';
import { ThemeProvider } from '@/state/theme-provider';
import { TooltipProvider } from '@/components/ui/tooltip';
import type { Conversation } from '@/lib/domain';

const store = vi.hoisted(() => ({
  conversations: [] as Conversation[],
  activeConversation: null as Conversation | null,
  newConversation: vi.fn(),
  selectConversation: vi.fn(),
  deleteConversation: vi.fn(),
  accessToken: '',
  setAccessToken: vi.fn(),
}));
vi.mock('@/state/chat-store', () => ({ useChatStore: () => store }));

function conversation(id: string, title: string, daysAgo: number): Conversation {
  const date = new Date();
  date.setDate(date.getDate() - daysAgo);
  return {
    id,
    lastInteractionId: null,
    title,
    createdAt: date.toISOString(),
    updatedAt: date.toISOString(),
    status: 'ativa',
    channel: 'webchat',
    messages: [
      {
        id: `m-${id}`,
        role: 'user',
        content: 'Pergunta sobre orçamento',
        createdAt: date.toISOString(),
        status: 'complete',
        origin: 'text',
      },
    ],
  };
}

function mountSidebar(onClose?: () => void) {
  return render(
    <ThemeProvider>
      <TooltipProvider>
        <ConversationSidebar onClose={onClose} />
      </TooltipProvider>
    </ThemeProvider>,
  );
}

describe('ConversationSidebar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    store.conversations = [];
    store.activeConversation = null;
    store.accessToken = '';
    localStorage.clear();
  });

  it('apresenta ausência de histórico, cria conversa e fecha o menu', async () => {
    const close = vi.fn();
    mountSidebar(close);
    expect(screen.getByText('Nenhuma conversa ainda')).toBeVisible();
    await userEvent.click(screen.getByRole('button', { name: 'Nova conversa' }));
    await userEvent.click(screen.getByRole('button', { name: 'Fechar menu' }));
    expect(store.newConversation).toHaveBeenCalledOnce();
    expect(close).toHaveBeenCalledOnce();
  });

  it('agrupa dias, seleciona e exclui sem selecionar novamente', async () => {
    store.conversations = [
      conversation('old', 'Contrato', 35),
      conversation('today', 'Prazo', 0),
      conversation('yesterday', 'Custos', 1),
      conversation('week', 'Riscos', 3),
      conversation('month', 'Avanço', 15),
    ];
    store.activeConversation = store.conversations[1];
    mountSidebar();
    expect(
      screen
        .getAllByRole('heading', { level: 2 })
        .map((heading) => heading.textContent),
    ).toEqual(['Hoje', 'Ontem', 'Últimos 7 dias', 'Últimos 30 dias', 'Mais antigas']);
    await userEvent.click(screen.getByRole('button', { name: /Prazo.*Sem respostas/ }));
    expect(store.selectConversation).toHaveBeenCalledWith('today');
    await userEvent.click(
      screen.getByRole('button', { name: 'Excluir conversa Prazo' }),
    );
    expect(store.deleteConversation).toHaveBeenCalledWith('today');
    expect(store.selectConversation).toHaveBeenCalledOnce();
  });

  it('busca por título ou conteúdo ignorando caixa e espaços, e informa ausência', async () => {
    store.conversations = [
      conversation('a', 'Prazo', 0),
      { ...conversation('b', 'Riscos', 0), messages: [] },
    ];
    mountSidebar();
    const search = screen.getByRole('searchbox', { name: 'Buscar nas conversas' });
    await userEvent.type(search, '  PRAZO  ');
    expect(screen.getByRole('button', { name: /Prazo.*Sem respostas/ })).toBeVisible();
    expect(screen.queryByRole('button', { name: /^Riscos/ })).not.toBeInTheDocument();
    await userEvent.clear(search);
    await userEvent.type(search, 'orçamento');
    expect(screen.getByRole('button', { name: /Prazo.*Sem respostas/ })).toBeVisible();
    await userEvent.clear(search);
    await userEvent.type(search, 'inexistente');
    expect(screen.getByText('Nenhuma conversa encontrada')).toBeVisible();
  });
});
