import { BookOpen, Menu, PanelRightClose } from 'lucide-react';
import type { ReactNode } from 'react';

import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { formatDate } from '@/lib/format';
import type { Conversation } from '@/lib/domain';

/**
 * Cabecalho do chat: titulo da conversa a esquerda; fontes, alertas e ajustes
 * a direita. A linha "Iniciada em ... · canal" so aparece no modo tecnico.
 */
export function ChatHeader({
  conversation,
  sourceCount,
  documentPanelOpen,
  onToggleDocumentPanel,
  onOpenSidebar,
  showTechnicalDetails = false,
  actions,
}: {
  conversation: Conversation | null;
  sourceCount: number;
  documentPanelOpen: boolean;
  onToggleDocumentPanel: () => void;
  onOpenSidebar: () => void;
  showTechnicalDetails?: boolean;
  /** Sino de alertas e engrenagem de ajustes, que dependem do estado global. */
  actions?: ReactNode;
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
        {showTechnicalDetails && conversation && conversation.messages.length > 0 && (
          <p className="truncate text-2xs text-fg-subtle">
            Iniciada em {formatDate(conversation.createdAt)} · canal{' '}
            {conversation.channel}
          </p>
        )}
      </div>

      <div className="flex shrink-0 items-center gap-1">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant={documentPanelOpen ? 'secondary' : 'ghost'}
              size="sm"
              onClick={onToggleDocumentPanel}
              aria-pressed={documentPanelOpen}
            >
              {documentPanelOpen ? (
                <PanelRightClose size={15} aria-hidden />
              ) : (
                <BookOpen size={15} aria-hidden />
              )}
              {/*
               * O nome acessivel vem do proprio conteudo ("Fontes 2 da ultima
               * resposta"), para que o texto visivel esteja contido nele
               * (WCAG 2.5.3). Em telas estreitas a palavra so fica oculta.
               */}
              <span className="sr-only sm:not-sr-only">Fontes</span>
              {sourceCount > 0 && (
                <Badge tone={documentPanelOpen ? 'primary' : 'neutral'}>
                  {sourceCount}
                </Badge>
              )}
              <span className="sr-only">da última resposta</span>
            </Button>
          </TooltipTrigger>
          <TooltipContent side="bottom" align="end">
            Documentos usados na última resposta
          </TooltipContent>
        </Tooltip>

        {actions}
      </div>
    </header>
  );
}
