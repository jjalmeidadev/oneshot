import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useRef } from 'react';

import { MessageBubble } from '@/components/chat/message-bubble';
import { TypingIndicator } from '@/components/chat/typing-indicator';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { ChatMessage } from '@/lib/domain';

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
}: {
  messages: ChatMessage[];
  isSending: boolean;
  intentLayerEnabled: boolean;
  selectedSourceId: string | null;
  onSelectSource: (id: string) => void;
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
        className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-6 sm:px-6"
      >
        {messages.map((message) => (
          <motion.div key={message.id} {...ENTRY}>
            <MessageBubble
              message={message}
              selectedSourceId={selectedSourceId}
              onSelectSource={onSelectSource}
            />
          </motion.div>
        ))}

        <AnimatePresence>
          {isSending && (
            <motion.div {...ENTRY}>
              <TypingIndicator
                label={
                  intentLayerEnabled
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
