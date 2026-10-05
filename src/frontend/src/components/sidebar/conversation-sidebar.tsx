import { MessagesSquare, PenSquare, Search, X } from 'lucide-react';
import { useMemo, useState } from 'react';

import { ThemeToggle } from '@/components/layout/theme-toggle';
import { ConversationItem } from '@/components/sidebar/conversation-item';
import { Button } from '@/components/ui/button';
import { EmptyState } from '@/components/ui/empty-state';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { relativeDayLabel } from '@/lib/format';
import type { Conversation } from '@/lib/domain';
import { useChatStore } from '@/state/chat-store';

const GROUP_ORDER = [
  'Hoje',
  'Ontem',
  'Últimos 7 dias',
  'Últimos 30 dias',
  'Mais antigas',
];

function groupByDay(conversations: Conversation[]) {
  const groups = new Map<string, Conversation[]>();

  for (const conversation of conversations) {
    const label = relativeDayLabel(conversation.updatedAt);
    const bucket = groups.get(label) ?? [];
    bucket.push(conversation);
    groups.set(label, bucket);
  }

  return GROUP_ORDER.filter((label) => groups.has(label)).map((label) => ({
    label,
    conversations: (groups.get(label) ?? []).sort(
      (a, b) => Date.parse(b.updatedAt) - Date.parse(a.updatedAt),
    ),
  }));
}

/** Histórico em memória da sessão atual. Não há API de persistência de conversas. */
export function ConversationSidebar({ onClose }: { onClose?: () => void }) {
  const {
    conversations,
    activeConversation,
    newConversation,
    selectConversation,
    deleteConversation,
  } = useChatStore();
  const [query, setQuery] = useState('');

  const filtered = useMemo(() => {
    const term = query.trim().toLowerCase();
    if (!term) return conversations;
    return conversations.filter(
      (conversation) =>
        conversation.title.toLowerCase().includes(term) ||
        conversation.messages.some((message) =>
          message.content.toLowerCase().includes(term),
        ),
    );
  }, [conversations, query]);

  const groups = useMemo(() => groupByDay(filtered), [filtered]);

  return (
    <nav aria-label="Conversas" className="flex h-full w-full flex-col bg-surface">
      <div className="flex items-center gap-2 px-3 pb-2 pt-3">
        <img
          src="/logo-metro-sp.png"
          alt="Metrô de São Paulo"
          className="h-7 w-auto rounded-sm"
        />
        <span className="min-w-0 flex-1 truncate text-xs font-semibold text-fg">
          ONESHOT
        </span>
        {onClose && (
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onClose}
            aria-label="Fechar menu"
          >
            <X size={16} />
          </Button>
        )}
      </div>

      <div className="px-3">
        <Button onClick={newConversation} className="w-full justify-start" size="md">
          <PenSquare size={15} />
          Nova conversa
        </Button>
      </div>

      <div className="px-3 pb-2 pt-3">
        <div className="flex items-center gap-2 rounded-lg border border-border bg-muted px-2.5 focus-within:border-primary">
          <Search size={14} className="shrink-0 text-fg-subtle" />
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Buscar nas conversas"
            aria-label="Buscar nas conversas"
            className="h-8 w-full min-w-0 bg-transparent text-xs text-fg outline-none placeholder:text-fg-subtle"
          />
        </div>
      </div>

      <ScrollArea className="min-h-0 flex-1 px-2">
        {groups.length === 0 ? (
          <EmptyState
            compact
            icon={MessagesSquare}
            title={query ? 'Nenhuma conversa encontrada' : 'Nenhuma conversa ainda'}
            description={
              query
                ? 'Ajuste o termo da busca.'
                : 'As perguntas feitas ao agente aparecem aqui.'
            }
          />
        ) : (
          <div className="space-y-4 pb-4">
            {groups.map((group) => (
              <section key={group.label}>
                <h2 className="px-2.5 pb-1 text-2xs font-semibold uppercase tracking-wide text-fg-subtle">
                  {group.label}
                </h2>
                <div className="space-y-0.5">
                  {group.conversations.map((conversation) => (
                    <ConversationItem
                      key={conversation.id}
                      conversation={conversation}
                      active={conversation.id === activeConversation?.id}
                      onSelect={() => selectConversation(conversation.id)}
                      onDelete={() => deleteConversation(conversation.id)}
                    />
                  ))}
                </div>
              </section>
            ))}
          </div>
        )}
      </ScrollArea>

      <Separator />

      <div className="flex items-center justify-between gap-1 p-2 pl-3">
        <span className="text-2xs text-fg-subtle">Tema</span>
        <ThemeToggle />
      </div>
    </nav>
  );
}
