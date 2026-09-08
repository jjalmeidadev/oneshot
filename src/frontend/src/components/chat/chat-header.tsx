import { FileStack, Menu, PanelRightClose } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { formatDate } from '@/lib/format';
import type { Conversation } from '@/lib/domain';

export function ChatHeader({
  conversation,
  sourceCount,
  documentPanelOpen,
  onToggleDocumentPanel,
  onOpenSidebar,
}: {
  conversation: Conversation | null;
  sourceCount: number;
  documentPanelOpen: boolean;
  onToggleDocumentPanel: () => void;
  onOpenSidebar: () => void;
}) {
  return (
    <header className="flex items-center gap-2 border-b border-border bg-surface px-3 py-2.5 sm:px-4">
      <Button
        variant="ghost"
        size="icon-sm"
        className="lg:hidden"
        onClick={onOpenSidebar}
        aria-label="Abrir conversas"
      >
        <Menu size={17} />
      </Button>

      <div className="min-w-0 flex-1">
        <h1 className="truncate text-sm font-semibold text-fg">
          {conversation?.title ?? 'Nova conversa'}
        </h1>
        {conversation && conversation.messages.length > 0 && (
          <p className="truncate text-2xs text-fg-subtle">
            Iniciada em {formatDate(conversation.createdAt)} · canal{' '}
            {conversation.channel}
          </p>
        )}
      </div>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant={documentPanelOpen ? 'secondary' : 'outline'}
            size="sm"
            onClick={onToggleDocumentPanel}
            aria-pressed={documentPanelOpen}
            // O rotulo textual some em telas estreitas, entao o nome acessivel
            // do botao precisa vir daqui.
            aria-label={`Documentos recuperados (${sourceCount})`}
          >
            {documentPanelOpen ? (
              <PanelRightClose size={14} />
            ) : (
              <FileStack size={14} />
            )}
            <span className="hidden sm:inline">Documentos</span>
            {sourceCount > 0 && (
              <Badge tone={documentPanelOpen ? 'primary' : 'neutral'}>
                {sourceCount}
              </Badge>
            )}
          </Button>
        </TooltipTrigger>
        <TooltipContent side="bottom" align="end">
          Documentos que o RAG recuperou para a última resposta
        </TooltipContent>
      </Tooltip>
    </header>
  );
}
