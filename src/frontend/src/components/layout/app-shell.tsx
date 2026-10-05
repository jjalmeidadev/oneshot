import { useState } from 'react';

import { ChatEmptyState } from '@/components/chat/chat-empty-state';
import { ChatHeader } from '@/components/chat/chat-header';
import { MessageList } from '@/components/chat/message-list';
import { Composer } from '@/components/composer/composer';
import { DocumentPanel } from '@/components/documents/document-panel';
import { NotificationCenter } from '@/components/notifications/notification-center';
import { AgentSettings } from '@/components/settings/agent-settings';
import { ConversationSidebar } from '@/components/sidebar/conversation-sidebar';
import { UserCard } from '@/components/sidebar/user-card';
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog';
import { useIsDesktop } from '@/hooks/use-media-query';
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
 * proatividade, modo tecnico e perfil da sessao ficam na engrenagem de ajustes, e o painel
 * de fontes so abre quando o usuario pede. Abaixo de 1024 px, a barra lateral e
 * o painel de fontes viram paineis deslizantes; o chat ocupa a largura toda.
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

  const showDocumentPanel = isDesktop && documentPanelOpen;

  return (
    <div className="flex h-screen w-full overflow-hidden bg-app p-0 lg:gap-3 lg:p-3">
      {isDesktop ? (
        <div className="w-72 shrink-0 overflow-hidden rounded-xl border border-border shadow-panel">
          <ConversationSidebar />
        </div>
      ) : (
        <Dialog open={sidebarOpen} onOpenChange={setSidebarOpen}>
          <DialogContent side="left" showClose={false} className="p-0">
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
          documentPanelOpen={isDesktop ? documentPanelOpen : documentSheetOpen}
          onToggleDocumentPanel={() =>
            isDesktop
              ? setDocumentPanelOpen(!documentPanelOpen)
              : setDocumentSheetOpen(true)
          }
          onOpenSidebar={() => setSidebarOpen(true)}
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
                session={<UserCard />}
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
                if (!isDesktop) setDocumentSheetOpen(true);
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
        <div className="w-80 shrink-0 overflow-hidden rounded-xl border border-border shadow-panel xl:w-96">
          <DocumentPanel
            documents={activeSources}
            selectedDocument={selectedDocument}
            onSelect={selectDocument}
            lastAssistantMessage={lastAssistantMessage}
            showResponseDetails={showTechnicalDetails}
          />
        </div>
      )}

      {!isDesktop && (
        <Dialog open={documentSheetOpen} onOpenChange={setDocumentSheetOpen}>
          <DialogContent side="right" className="p-0">
            <DialogTitle className="sr-only">Fontes da resposta</DialogTitle>
            <div className="h-full pt-8">
              <DocumentPanel
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
