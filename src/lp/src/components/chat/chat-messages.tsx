"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Send, RotateCcw, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import SourceFolder from "@/components/chat/source-folder";
import { INTRO_MESSAGES } from "@/components/chat/messages";

export interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  content: string;
  timestamp?: string;
  /**
   * Documentos que sustentam a resposta. Quando presente, a bolha ganha a
   * pasta interativa de fontes — hoje só as mensagens do chat 2 usam isso.
   */
  sources?: {
    label: string;
    documents: string[];
  };
}

export interface ChatMessagesProps {
  messages?: ChatMessage[];
  autoPlay?: boolean;
  autoPlayDelay?: number;
  typingDuration?: number;
  showReplay?: boolean;
  interactive?: boolean;
  /**
   * Render every bubble immediately, without framer-motion's own mount
   * animation, so an external scroll animation (GSAP ScrollTrigger) can own
   * the reveal instead. Pair with `autoPlay={false}`.
   */
  scrollDriven?: boolean;
  /** Tighter paddings/gaps throughout, for a shorter overall footprint. */
  compact?: boolean;
  /**
   * Gate for `autoPlay`: while false, no message is revealed yet — the
   * sequence starts (or restarts) the moment this flips to true. Lets a
   * parent hold playback until, say, the section has scrolled into view.
   */
  active?: boolean;
  /**
   * Scroll-driven reveal. When provided, the component stops playing on a
   * timer and instead shows `revealStep + 1` messages: the parent turns
   * scroll gestures into steps, so each notch of scroll brings in the next
   * message. Step 0 (the moment `active` flips true) shows the greeting
   * whole, with no typing indicator.
   */
  revealStep?: number;
  /**
   * Fires while a step is being played out (typing indicator + bubble
   * entrance). The parent uses it to ignore further scroll steps until the
   * current message has fully landed.
   */
  onBusyChange?: (busy: boolean) => void;
  /**
   * Freezes the message list's own scrolling. Used while the window is still
   * growing into the screen: a wheel gesture over the chat has to keep
   * driving the page (and the expansion) instead of scrolling the
   * conversation inside a window that isn't in place yet.
   */
  lockScroll?: boolean;
  /** Fires once, right after the last message has been revealed. */
  onComplete?: () => void;
  /**
   * Handler for messages typed by the visitor (needs `interactive`). Return
   * the assistant's answer — this is the seam where the OneShot RAG backend
   * plugs in. Without it, a placeholder answer is used.
   */
  onSendMessage?: (message: string) => Promise<string> | string;
  className?: string;
}


const wait = (ms: number) => new Promise<void>((resolve) => setTimeout(resolve, ms));

/** Stand-in answer until the RAG backend is wired to `onSendMessage`. */
const PENDING_RAG_REPLY =
  "Ainda estou sendo conectado à base de conhecimento do OneShot. Em breve eu respondo essa pergunta com o conteúdo dos documentos do projeto e a fonte de cada trecho.";

function TypingIndicator({ className }: { className?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      className={cn(
        "inline-flex items-center gap-1 rounded-2xl rounded-tl-md border border-white/10 bg-zinc-800/90 px-4 py-3 backdrop-blur-sm",
        className,
      )}
    >
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          className="h-2 w-2 rounded-full bg-white/60"
          animate={{ opacity: [0.4, 1, 0.4], y: [0, -4, 0] }}
          transition={{
            duration: 0.8,
            repeat: Infinity,
            delay: i * 0.15,
            ease: "easeInOut",
          }}
        />
      ))}
    </motion.div>
  );
}

function MessageBubble({
  message,
  scrollDriven,
  compact,
}: {
  message: ChatMessage;
  /**
   * When true, skip framer-motion's own mount animation (`initial={false}`)
   * so an external scroll animation (GSAP ScrollTrigger) is the only thing
   * moving opacity/position — otherwise the two fight over the same styles.
   */
  scrollDriven?: boolean;
  compact?: boolean;
}) {
  const isUser = message.sender === "user";
  return (
    <motion.div
      data-chat-bubble
      initial={scrollDriven ? false : { opacity: 0, y: 12, scale: 0.96, x: isUser ? 20 : -20 }}
      animate={{ opacity: 1, y: 0, scale: 1, x: 0 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
      className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}
    >
      <div
        className={cn(
          "flex min-w-0 max-w-[88%] items-end gap-2",
          isUser && "flex-row-reverse",
        )}
      >
        {!isUser && (
          <div
            className={cn(
              "flex shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600",
              compact ? "h-6 w-6" : "h-8 w-8",
            )}
          >
            <Sparkles className={compact ? "size-3 text-white" : "size-4 text-white"} />
          </div>
        )}
        <motion.div
          className={cn(
            "w-fit min-w-0 max-w-full whitespace-pre-wrap break-words rounded-2xl text-sm font-normal leading-relaxed",
            compact ? "px-3 py-1.5" : "px-4 py-2.5",
            isUser
              ? "rounded-tr-md bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-[0_8px_24px_-4px_rgba(99,102,241,0.4)]"
              : "rounded-tl-md border border-white/10 bg-zinc-800/90 text-zinc-100 backdrop-blur-sm shadow-[0_4px_12px_-2px_rgba(0,0,0,0.3)]",
          )}
          whileHover={{ scale: 1.01, y: -1 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
        >
          {message.content}
          {message.sources && (
            <SourceFolder
              label={message.sources.label}
              documents={message.sources.documents}
            />
          )}
        </motion.div>
      </div>
    </motion.div>
  );
}

export function ChatMessages({
  messages = INTRO_MESSAGES,
  autoPlay = true,
  autoPlayDelay = 1800,
  typingDuration = 1400,
  showReplay = false,
  interactive = false,
  scrollDriven = false,
  compact = false,
  active = true,
  lockScroll = false,
  revealStep,
  onBusyChange,
  onComplete,
  onSendMessage,
  className,
}: ChatMessagesProps) {
  const scrollControlled = revealStep !== undefined;
  const [visibleCount, setVisibleCount] = useState(
    autoPlay || scrollControlled ? 0 : messages.length,
  );
  const [isTyping, setIsTyping] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>(messages);
  const scrollRef = useRef<HTMLDivElement>(null);
  const isAutoPlaying = useRef(false);
  // Mirror of `visibleCount` for the scroll-driven loop, which needs to read
  // the current position between awaits without re-subscribing to state.
  const visibleCountRef = useRef(0);

  const scrollToBottom = useCallback(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, []);

  const revealNext = useCallback(
    async (index: number) => {
      if (index >= chatMessages.length) {
        isAutoPlaying.current = false;
        onComplete?.();
        return;
      }
      const message = chatMessages[index];
      if (message.sender === "assistant") {
        setIsTyping(true);
        await wait(typingDuration);
        setIsTyping(false);
      }
      setVisibleCount(index + 1);
      await wait(100);
      scrollToBottom();
      await wait(
        autoPlayDelay -
          (message.sender === "assistant" ? typingDuration : 0) -
          100,
      );
      if (isAutoPlaying.current) {
        revealNext(index + 1);
      }
    },
    [chatMessages, autoPlayDelay, typingDuration, scrollToBottom, onComplete],
  );

  const replay = useCallback(() => {
    setVisibleCount(0);
    setChatMessages(messages);
    isAutoPlaying.current = true;
    setTimeout(() => revealNext(0), 100);
  }, [messages, revealNext]);

  useEffect(() => {
    setChatMessages(messages);
    // Scroll-driven mode owns the reveal; the timer path stays out of it.
    if (scrollControlled) return;
    if (!autoPlay) {
      setVisibleCount(messages.length);
      return;
    }
    if (!active) {
      // Held: wait for `active` to flip true before playing anything.
      setVisibleCount(0);
      return;
    }
    setVisibleCount(0);
    isAutoPlaying.current = true;
    const timer = setTimeout(() => revealNext(0), 300);
    return () => {
      clearTimeout(timer);
      isAutoPlaying.current = false;
    };
  }, [messages, autoPlay, active, revealNext, scrollControlled]);

  // How many messages the current scroll position asks for: the greeting is
  // already there at step 0, every step after that adds one message.
  const target =
    scrollControlled && active
      ? Math.min((revealStep ?? 0) + 1, chatMessages.length)
      : 0;

  useEffect(() => {
    if (!scrollControlled) return;
    if (!active) {
      visibleCountRef.current = 0;
      setVisibleCount(0);
      return;
    }

    let cancelled = false;

    const run = async () => {
      if (visibleCountRef.current >= target) return;
      onBusyChange?.(true);

      // Um salto de mais de uma mensagem só acontece quando alguém pula a
      // animação (ou quando a página carrega já depois da seção): nesses
      // casos a conversa aparece inteira, sem os tempos de digitação.
      const instant = target - visibleCountRef.current > 1;

      while (!cancelled && visibleCountRef.current < target) {
        const index = visibleCountRef.current;
        const message = chatMessages[index];
        if (!message) break;

        // The greeting lands whole, the moment the section is reached; every
        // later model reply gets the typing indicator first.
        if (!instant && message.sender === "assistant" && index > 0) {
          setIsTyping(true);
          await wait(typingDuration);
          if (cancelled) return;
          setIsTyping(false);
        }

        visibleCountRef.current = index + 1;
        setVisibleCount(index + 1);
        if (instant) continue;
        await wait(120);
        if (cancelled) return;
        scrollToBottom();
      }

      if (instant) {
        setIsTyping(false);
        scrollToBottom();
      }

      if (cancelled) return;
      onBusyChange?.(false);
      if (visibleCountRef.current >= chatMessages.length) onComplete?.();
    };

    void run();
    return () => {
      cancelled = true;
    };
  }, [
    scrollControlled,
    active,
    target,
    chatMessages,
    typingDuration,
    scrollToBottom,
    onBusyChange,
    onComplete,
  ]);

  useEffect(() => {
    scrollToBottom();
  }, [visibleCount, isTyping, scrollToBottom]);

  // Released: bring the conversation back to the latest message, since it
  // couldn't follow along while the list was frozen.
  useEffect(() => {
    if (!lockScroll) scrollToBottom();
  }, [lockScroll, scrollToBottom]);

  const appendAssistant = useCallback((content: string) => {
    setChatMessages((prev) => [
      ...prev,
      { id: `assistant-${Date.now()}`, sender: "assistant", content },
    ]);
    setVisibleCount((prev) => prev + 1);
    visibleCountRef.current += 1;
  }, []);

  const handleSend = useCallback(() => {
    const text = inputValue.trim();
    if (!text || !interactive) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      content: text,
    };
    setChatMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setVisibleCount((prev) => prev + 1);
    visibleCountRef.current += 1;
    setIsTyping(true);

    // `onSendMessage` is where the RAG model will answer from; until it's
    // provided, a placeholder keeps the interaction complete.
    const answer = onSendMessage
      ? Promise.resolve(onSendMessage(text))
      : wait(typingDuration).then(() => PENDING_RAG_REPLY);

    answer
      .then((content) => appendAssistant(content))
      .catch(() =>
        appendAssistant(
          "Não consegui responder agora. Tente de novo em alguns instantes.",
        ),
      )
      .finally(() => setIsTyping(false));
  }, [inputValue, interactive, typingDuration, onSendMessage, appendAssistant]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      className={cn(
        "relative flex flex-col overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-zinc-900 to-zinc-950 shadow-[0_24px_64px_-16px_rgba(0,0,0,0.5)]",
        className,
      )}
    >
      {/* Header */}
      <div
        className={cn(
          "flex shrink-0 items-center justify-between border-b border-white/5",
          compact ? "px-3 py-2" : "px-4 py-3",
        )}
      >
        <div className="flex items-center gap-2">
          <div
            className={cn(
              "flex items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600",
              compact ? "h-6 w-6" : "h-8 w-8",
            )}
          >
            <Sparkles className={compact ? "size-3 text-white" : "size-4 text-white"} />
          </div>
          <div>
            <h3 className="text-sm font-medium text-white">OneShot AI</h3>
            <p className="text-xs text-white/40"></p>
          </div>
        </div>
        {showReplay && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={replay}
            aria-label="Replay conversation"
            className="flex items-center gap-1.5 rounded-lg bg-white/5 px-3 py-1.5 text-xs text-white/60 transition-colors hover:bg-white/10 hover:text-white"
          >
            <RotateCcw className="size-3.5" />
            Replay
          </motion.button>
        )}
      </div>
      {/* Messages */}
      <div
        ref={scrollRef}
        role="log"
        aria-label="Chat messages"
        aria-live="polite"
        className={cn(
          "min-h-0 flex-1 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent",
          lockScroll ? "overflow-hidden" : "overflow-y-auto",
          compact ? "space-y-2 p-3" : "space-y-3 p-4",
        )}
      >
        {chatMessages.slice(0, visibleCount).map((message) => (
          <MessageBubble key={message.id} message={message} scrollDriven={scrollDriven} compact={compact} />
        ))}
        <AnimatePresence>{isTyping && <TypingIndicator />}</AnimatePresence>
      </div>
      {/* Input */}
      <div className={cn("shrink-0 border-t border-white/5", compact ? "p-2" : "p-3")}>
        <div
          className={cn(
            "flex items-center gap-2 rounded-xl border border-white/10 bg-zinc-800/50 backdrop-blur-sm focus-within:border-white/20 focus-within:bg-zinc-800/70",
            compact ? "px-3 py-1.5" : "px-4 py-2",
          )}
        >
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={!interactive}
            placeholder={
              interactive
                ? "Pergunte sobre o projeto..."
                : "Modo demonstração"
            }
            aria-label={
              interactive ? "Escreva sua mensagem" : "Campo de mensagem (demonstração)"
            }
            className="flex-1 bg-transparent text-sm text-white outline-none placeholder:text-white/30 disabled:cursor-not-allowed"
          />
          <motion.button
            whileHover={{ scale: 1.08 }}
            whileTap={{ scale: 0.92 }}
            onClick={handleSend}
            disabled={!interactive || !inputValue.trim()}
            aria-label="Send message"
            className={cn(
              "flex h-8 w-8 items-center justify-center rounded-lg transition-colors",
              interactive && inputValue.trim()
                ? "bg-indigo-600 text-white hover:bg-indigo-500"
                : "bg-white/5 text-white/30",
            )}
          >
            <Send className="size-4" />
          </motion.button>
        </div>
      </div>
    </div>
  );
}

export default ChatMessages;
