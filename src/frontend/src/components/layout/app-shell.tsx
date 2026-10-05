import { BookOpen } from 'lucide-react';
import { useRef, useState } from 'react';

import { ChatEmptyState } from '@/components/chat/chat-empty-state';
import { ChatHeader } from '@/components/chat/chat-header';
import { MessageList } from '@/components/chat/message-list';
import { Composer } from '@/components/composer/composer';
import { DocumentPanel } from '@/components/documents/document-panel';
import { NotificationCenter } from '@/components/notifications/notification-center';
import { AgentSettings } from '@/components/settings/agent-settings';
import { ConversationSidebar } from '@/components/sidebar/conversation-sidebar';
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog';
import { useIsDesktop, useIsWide } from '@/hooks/use-media-query';
import { useChatStore } from '@/state/chat-store';
import { cn } from '@/lib/utils';

/**
 * Disposicao dos tres paineis.
 *
 *   +--------------+------------------------------------+-------------+
 *   |  conversas   |  titulo        Fontes  sino  ajustes|  fontes     |
 *   |  (esquerda)  |  mensagens                          |  da resposta|
 *   |              |  campo de texto + audio             |  (direita,  |
 *   |              |                                     |  fechado)   |
 *   +--------------+------------------------------------+-------------+
 *
 * A tela padrao nao mostra detalhes tecnicos (S5-20): validacao de intencao,
 * proatividade, modo tecnico e token ficam na engrenagem de ajustes, e o painel
 * de fontes so abre quando o usuario pede.
 *
 * Pontos de quebra (S5-21, ver `hooks/use-media-query.ts`): abaixo de 1024 px,
 * conversas e fontes viram paineis deslizantes e o chat ocupa a largura toda;
 * de 1024 a 1279 px, so as fontes deslizam; a partir de 1280 px, os tres
 * paineis ficam lado a lado.
 */
export function AppShell() {
  const {
    activeConversation,
    status,
    intentLayerEnabled,
    setIntentLayerEnabled,
    proactivityEnabled,
    setProactivityEnabled,
    showTechnicalDetails,
    setShowTechnicalDetails,
    accessToken,
    setAccessToken,
    activeSources,
    selectedDocument,
    selectDocument,
    documentPanelOpen,
    setDocumentPanelOpen,
    documentSheetOpen,
    setDocumentSheetOpen,
    sidebarOpen,
    setSidebarOpen,
    sendMessage,
    sendAudio,
    resolveProactiveSuggestion,
    stop,
    error,
  } = useChatStore();

  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const draftId = activeConversation?.id ?? 'new';
  const draft = drafts[draftId] ?? '';
  const setDraft = (value: string) =>
    setDrafts((current) => ({ ...current, [draftId]: value }));
  const isDesktop = useIsDesktop();
  const isWide = useIsWide();

  // Os paineis deslizantes abrem por botoes que nao sao `DialogTrigger`; ao
  // fechar, o foco volta para quem os abriu, e nao para o inicio da pagina.
  const returnFocus = useRef<HTMLElement | null>(null);
  const rememberFocus = () => {
    returnFocus.current =
      document.activeElement instanceof HTMLElement ? document.activeElement : null;
  };
  const restoreFocus = (event: Event) => {
    if (returnFocus.current?.isConnected) {
      event.preventDefault();
      returnFocus.current.focus();
    }
    returnFocus.current = null;
  };
  const openSourcesSheet = () => {
    rememberFocus();
    setDocumentSheetOpen(true);
  };

  const messages = activeConversation?.messages ?? [];
  const isSending = status === 'sending';

  const lastAssistantMessage =
    [...messages].reverse().find((message) => message.role === 'assistant') ?? null;

  const submit = (content?: string) => {
    const text = content ?? draft;
    if (!text.trim()) return;
    void sendMessage(text).then((sent) => {
      if (sent)
        setDrafts((current) =>
          current[draftId] === text ? { ...current, [draftId]: '' } : current,
        );
    });
  };

  const showDocumentPanel = isWide && documentPanelOpen;

  return (
    <div className="flex h-dvh w-full overflow-hidden bg-app p-0 lg:gap-3 lg:p-3">
      <a
        href="#mensagem-para-o-agente"
        onClick={(event) => {
          // A ancora so rola a pagina; o atalho precisa levar o foco ao campo.
          const field = document.getElementById('mensagem-para-o-agente');
          if (field) {
            event.preventDefault();
            field.focus();
          }
        }}
        className="sr-only z-50 rounded-lg bg-primary px-3 py-2 text-sm font-medium text-primary-fg focus:not-sr-only focus:fixed focus:left-3 focus:top-3 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
      >
        Pular para o campo de mensagem
      </a>

      {isDesktop ? (
        <div className="w-64 shrink-0 overflow-hidden rounded-xl border border-border shadow-panel xl:w-72">
          <ConversationSidebar />
        </div>
      ) : (
        <Dialog open={sidebarOpen} onOpenChange={setSidebarOpen}>
          <DialogContent
            side="left"
            showClose={false}
            className="p-0"
            aria-describedby={undefined}
            onCloseAutoFocus={restoreFocus}
          >
            <DialogTitle className="sr-only">Conversas</DialogTitle>
            <ConversationSidebar onClose={() => setSidebarOpen(false)} />
          </DialogContent>
        </Dialog>
      )}

      <main
        className={cn(
          'flex min-w-0 flex-1 flex-col overflow-hidden bg-surface lg:rounded-xl lg:border lg:border-border lg:shadow-panel',
        )}
      >
        <ChatHeader
          conversation={activeConversation}
          sourceCount={activeSources.length}
          documentPanelOpen={isWide ? documentPanelOpen : documentSheetOpen}
          onToggleDocumentPanel={() =>
            isWide ? setDocumentPanelOpen(!documentPanelOpen) : openSourcesSheet()
          }
          onOpenSidebar={() => {
            rememberFocus();
            setSidebarOpen(true);
          }}
          showTechnicalDetails={showTechnicalDetails}
          actions={
            <>
              <NotificationCenter />
              <AgentSettings
                intentLayerEnabled={intentLayerEnabled}
                onIntentLayerChange={setIntentLayerEnabled}
                proactivityEnabled={proactivityEnabled}
                onProactivityChange={setProactivityEnabled}
                showTechnicalDetails={showTechnicalDetails}
                onShowTechnicalDetailsChange={setShowTechnicalDetails}
                accessToken={accessToken}
                onAccessTokenChange={setAccessToken}
                disabled={isSending}
              />
            </>
          }
        />

        <div className="min-h-0 flex-1">
          {messages.length === 0 && !isSending ? (
            <ChatEmptyState onPick={(prompt) => submit(prompt)} />
          ) : (
            <MessageList
              messages={messages}
              isSending={isSending}
              intentLayerEnabled={intentLayerEnabled}
              selectedSourceId={selectedDocument?.id ?? null}
              onSelectSource={(id) => {
                selectDocument(id);
                if (!isWide) openSourcesSheet();
              }}
              onResolveProactiveSuggestion={(messageId, decision) => {
                void resolveProactiveSuggestion(messageId, decision);
              }}
              onDisableProactivity={() => setProactivityEnabled(false)}
              showTechnicalDetails={showTechnicalDetails}
            />
          )}
        </div>

        {error && (
          <p
            role="alert"
            className="mx-4 rounded-lg bg-danger-soft p-3 text-sm text-danger"
          >
            {error}
          </p>
        )}
        <Composer
          conversationId={activeConversation?.id ?? null}
          onSendAudio={sendAudio}
          value={draft}
          onChange={setDraft}
          onSubmit={() => submit()}
          onStop={stop}
          isSending={isSending}
        />
      </main>

      {showDocumentPanel && (
        <aside
          aria-label="Fontes da resposta"
          className="w-80 shrink-0 overflow-hidden rounded-xl border border-border shadow-panel 2xl:w-96"
        >
          <DocumentPanel
            documents={activeSources}
            selectedDocument={selectedDocument}
            onSelect={selectDocument}
            lastAssistantMessage={lastAssistantMessage}
            showResponseDetails={showTechnicalDetails}
          />
        </aside>
      )}

      {!isWide && (
        <Dialog open={documentSheetOpen} onOpenChange={setDocumentSheetOpen}>
          <DialogContent
            side="right"
            className="p-0"
            aria-describedby={undefined}
            onCloseAutoFocus={restoreFocus}
          >
            <DialogTitle className="flex h-12 shrink-0 items-center gap-1.5 px-4 text-xs">
              <BookOpen size={14} className="text-primary" aria-hidden />
              Fontes da resposta
            </DialogTitle>
            <div className="min-h-0 flex-1">
              <DocumentPanel
                showHeading={false}
                documents={activeSources}
                selectedDocument={selectedDocument}
                onSelect={selectDocument}
                lastAssistantMessage={lastAssistantMessage}
                showResponseDetails={showTechnicalDetails}
              />
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
