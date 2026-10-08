import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useRef } from 'react';

import { MessageBubble } from '@/components/chat/message-bubble';
import { TypingIndicator } from '@/components/chat/typing-indicator';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { ChatMessage } from '@/lib/domain';
import type { ProactiveDecision } from '@/lib/api';

/** Entrada discreta: a mensagem sobe alguns pixels ao aparecer. */
const ENTRY = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0 },
  transition: { duration: 0.18, ease: 'easeOut' as const },
};

export function MessageList({
  messages,
  isSending,
  intentLayerEnabled,
  selectedSourceId,
  onSelectSource,
  onResolveProactiveSuggestion,
  onDisableProactivity,
  showTechnicalDetails = false,
}: {
  messages: ChatMessage[];
  isSending: boolean;
  intentLayerEnabled: boolean;
  selectedSourceId: string | null;
  onSelectSource: (id: string) => void;
  onResolveProactiveSuggestion: (
    messageId: string,
    decision: ProactiveDecision,
  ) => void;
  onDisableProactivity?: () => void;
  showTechnicalDetails?: boolean;
}) {
  const viewportRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const viewport = viewportRef.current;
    if (viewport) {
      viewport.scrollTo({ top: viewport.scrollHeight, behavior: 'smooth' });
    }
  }, [messages.length, isSending]);

  return (
    <ScrollArea className="h-full" viewportRef={viewportRef}>
      <div
        role="log"
        aria-label="Mensagens da conversa"
        aria-live="polite"
        aria-busy={isSending}
        // Focavel para que quem usa teclado role uma resposta longa com as setas,
        // mesmo quando ela nao tem links nem botoes.
        tabIndex={0}
        className="mx-auto flex max-w-3xl flex-col gap-6 rounded-lg px-4 py-6 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ring sm:px-6"
      >
        {messages.map((message) => (
          <motion.div key={message.id} {...ENTRY}>
            <MessageBubble
              message={message}
              selectedSourceId={selectedSourceId}
              onSelectSource={onSelectSource}
              onResolveProactiveSuggestion={onResolveProactiveSuggestion}
              onDisableProactivity={onDisableProactivity}
              showTechnicalDetails={showTechnicalDetails}
            />
          </motion.div>
        ))}

        <AnimatePresence>
          {isSending && (
            <motion.div {...ENTRY}>
              <TypingIndicator
                label={
                  showTechnicalDetails && intentLayerEnabled
                    ? 'Classificando a intenção e consultando as fontes…'
                    : 'Consultando as fontes…'
                }
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </ScrollArea>
  );
}
