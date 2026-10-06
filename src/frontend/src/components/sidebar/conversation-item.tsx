import { MessageSquare, Trash2 } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { formatTime } from '@/lib/format';
import type { Conversation } from '@/lib/domain';
import { cn } from '@/lib/utils';

export function ConversationItem({
  conversation,
  active,
  onSelect,
  onDelete,
}: {
  conversation: Conversation;
  active: boolean;
  onSelect: () => void;
  onDelete: () => void;
}) {
  const preview =
    conversation.messages.find((message) => message.role === 'assistant')?.content ??
    'Sem respostas ainda';

  return (
    <div
      className={cn(
        'group relative rounded-lg transition-colors',
        active ? 'bg-primary-soft' : 'hover:bg-muted',
      )}
    >
      <button
        type="button"
        onClick={onSelect}
        aria-current={active ? 'true' : undefined}
        className="flex w-full items-start gap-2.5 rounded-lg px-2.5 py-2 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        <MessageSquare
          size={15}
          className={cn('mt-0.5 shrink-0', active ? 'text-primary' : 'text-fg-subtle')}
        />
        <span className="min-w-0 flex-1 pr-7">
          <span
            className={cn(
              'block truncate text-xs font-medium',
              active ? 'text-primary' : 'text-fg',
            )}
          >
            {conversation.title}
          </span>
          <span className="mt-0.5 block truncate text-2xs text-fg-subtle">
            {formatTime(conversation.updatedAt)} · {preview.replace(/[#*_`]/g, '')}
          </span>
        </span>
      </button>

      <Button
        variant="ghost"
        size="icon-sm"
        aria-label={`Excluir conversa ${conversation.title}`}
        onClick={onDelete}
        // Em telas de toque nao ha hover: o botao fica sempre visivel ali.
        className="absolute right-1 top-1.5 transition-opacity hover:text-danger focus-visible:opacity-100 group-focus-within:opacity-100 group-hover:opacity-100 [@media(hover:hover)]:opacity-0"
      >
        <Trash2 size={14} />
      </Button>
    </div>
  );
}
