'use client';

import { FileText, Paperclip, SendHorizontal, Square, X } from 'lucide-react';
import {
  memo,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';

import { cn } from '@/lib/utils';

export type ChatStatus = 'ready' | 'streaming' | 'submitted' | 'idle';

export type MessagePart =
  { type: 'text'; text: string } | { type: 'error'; title?: string; message: string };

export type MessageSource = {
  id: string;
  title: string;
  detail?: string;
};

export type AgentMessage = {
  id: string;
  role: 'user' | 'assistant';
  parts: MessagePart[];
  sources?: MessageSource[];
};

export type AttachedImage = {
  id: string;
  filename: string;
  url: string;
  size?: number;
};

export type AttachedFile = {
  id: string;
  filename: string;
  size?: number;
};

export type AgentChatProps = {
  messages: AgentMessage[];
  onSend?: (message: { role: 'user'; content: string }) => void;
  onStop?: () => void;
  status?: ChatStatus;
  error?: { message: string; title?: string };
  emptyStatePosition?: 'default' | 'center';
  placeholder?: string;
  attachments?: {
    onAttach?: () => void;
    images?: AttachedImage[];
    files?: AttachedFile[];
    onRemoveImage?: (id: string) => void;
    onRemoveFile?: (id: string) => void;
  };
  className?: string;
};

function UserBubble({ text }: { text: string }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[82%] rounded-2xl bg-metro-blue px-4 py-2.5 text-sm leading-6 text-white shadow-sm shadow-metro-blue/20 whitespace-pre-wrap break-words">
        {text}
      </div>
    </div>
  );
}

function AssistantText({ text }: { text: string }) {
  return (
    <div className="flex justify-start">
      <div className="max-w-[90%] text-sm leading-7 text-slate-700 whitespace-pre-wrap break-words">
        {text}
      </div>
    </div>
  );
}

function SourceList({ sources }: { sources?: MessageSource[] }) {
  if (!sources?.length) {
    return null;
  }

  return (
    <div className="mt-3 flex flex-wrap gap-2">
      {sources.map((source) => (
        <button
          key={source.id}
          type="button"
          className="inline-flex max-w-full items-center gap-2 rounded-lg border border-metro-line bg-metro-background px-2.5 py-1.5 text-left text-xs text-metro-text transition-colors hover:border-metro-blue hover:bg-white"
          title={source.detail}
        >
          <FileText size={14} className="shrink-0 text-metro-blue" />
          <span className="truncate">{source.title}</span>
        </button>
      ))}
    </div>
  );
}

function ErrorBubble({
  title = 'Algo deu errado',
  message,
}: {
  title?: string;
  message: string;
}) {
  return (
    <div className="flex justify-start">
      <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-2.5 text-sm">
        <div className="font-medium text-red-950">{title}</div>
        <div className="mt-0.5 text-red-700">{message}</div>
      </div>
    </div>
  );
}

function ThinkingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="inline-flex items-center gap-2 rounded-2xl bg-metro-background px-4 py-2.5 text-sm text-metro-text">
        <span className="h-2 w-2 animate-pulse rounded-full bg-metro-blue" />
        Consultando Gemini
      </div>
    </div>
  );
}

function MessageList({
  messages,
  status,
}: {
  messages: AgentMessage[];
  status: ChatStatus;
}) {
  const listRef = useRef<HTMLDivElement>(null);
  const isWaiting = status === 'submitted' || status === 'streaming';

  useEffect(() => {
    listRef.current?.scrollTo({
      top: listRef.current.scrollHeight,
      behavior: 'smooth',
    });
  }, [messages.length, status]);

  return (
    <div ref={listRef} className="min-h-0 flex-1 overflow-y-auto px-4 py-6">
      <div className="mx-auto flex max-w-3xl flex-col gap-5">
        {messages.map((message) => (
          <div key={message.id} className="flex flex-col gap-2">
            {message.parts.map((part, index) => {
              if (part.type === 'error') {
                return (
                  <ErrorBubble
                    key={`${message.id}-${index}`}
                    title={part.title}
                    message={part.message}
                  />
                );
              }

              if (message.role === 'user') {
                return <UserBubble key={`${message.id}-${index}`} text={part.text} />;
              }

              return (
                <div key={`${message.id}-${index}`}>
                  <AssistantText text={part.text} />
                  <SourceList sources={message.sources} />
                </div>
              );
            })}
          </div>
        ))}
        {isWaiting && <ThinkingIndicator />}
      </div>
    </div>
  );
}

function ImageChip({ url, onRemove }: { url: string; onRemove?: () => void }) {
  return (
    <div className="group relative h-12 w-12 overflow-hidden rounded-md bg-metro-background">
      <img src={url} alt="" className="h-full w-full object-cover" />
      {onRemove && (
        <button
          type="button"
          onClick={onRemove}
          aria-label="Remover imagem"
          className="absolute right-0.5 top-0.5 inline-flex h-4 w-4 items-center justify-center rounded-full bg-metro-blue/80 text-white opacity-0 transition-opacity group-hover:opacity-100"
        >
          <X size={10} />
        </button>
      )}
    </div>
  );
}

function FileChip({
  filename,
  size,
  onRemove,
}: {
  filename: string;
  size?: number;
  onRemove?: () => void;
}) {
  const sizeText =
    size === undefined
      ? null
      : size < 1024
        ? `${size} B`
        : size < 1024 * 1024
          ? `${(size / 1024).toFixed(1)} KB`
          : `${(size / (1024 * 1024)).toFixed(1)} MB`;

  return (
    <div className="group inline-flex items-center gap-2 rounded-md bg-metro-background px-2 py-1.5">
      <span className="text-metro-blue">
        <FileText size={16} />
      </span>
      <div className="flex min-w-0 flex-col">
        <span className="max-w-[140px] truncate text-xs font-medium text-metro-text">
          {filename}
        </span>
        {sizeText && <span className="text-[10px] text-slate-500">{sizeText}</span>}
      </div>
      {onRemove && (
        <button
          type="button"
          onClick={onRemove}
          aria-label="Remover arquivo"
          className="inline-flex h-5 w-5 items-center justify-center rounded-full text-slate-500 opacity-0 transition-opacity hover:bg-metro-line group-hover:opacity-100"
        >
          <X size={12} />
        </button>
      )}
    </div>
  );
}

function InputBar({
  onSend,
  onStop,
  status = 'ready',
  placeholder = 'Pergunte sobre projetos do Metro de Sao Paulo...',
  attachments,
  className,
  value: controlledValue,
  onChange,
  disabled,
}: {
  onSend?: (message: { role: 'user'; content: string }) => void;
  onStop?: () => void;
  status?: ChatStatus;
  placeholder?: string;
  attachments?: AgentChatProps['attachments'];
  className?: string;
  value?: string;
  onChange?: (value: string) => void;
  disabled?: boolean;
}) {
  const [internal, setInternal] = useState('');
  const isControlled = controlledValue !== undefined;
  const input = isControlled ? controlledValue : internal;
  const ref = useRef<HTMLTextAreaElement>(null);
  const isWaiting = status === 'streaming' || status === 'submitted';
  const hasInput = input.trim().length > 0;

  const images = attachments?.images ?? [];
  const files = attachments?.files ?? [];
  const hasContext = images.length > 0 || files.length > 0;

  const setInput = useCallback(
    (value: string) => {
      if (isControlled) {
        onChange?.(value);
      } else {
        setInternal(value);
      }
    },
    [isControlled, onChange],
  );

  useEffect(() => {
    const textArea = ref.current;
    if (!textArea) {
      return;
    }

    textArea.style.height = '0';
    const nextHeight = Math.min(textArea.scrollHeight, 128);
    textArea.style.height = `${nextHeight}px`;
    textArea.style.overflowY = textArea.scrollHeight > 128 ? 'auto' : 'hidden';
  }, [input]);

  const submit = useCallback(() => {
    const trimmed = input.trim();
    if (!trimmed || isWaiting || disabled) {
      return;
    }

    onSend?.({ role: 'user', content: trimmed });
    setInput('');
  }, [disabled, input, isWaiting, onSend, setInput]);

  return (
    <div className={cn('w-full shrink-0 px-3 pb-3', className)}>
      <div className="mx-auto max-w-3xl">
        <div
          className="relative cursor-text rounded-2xl bg-white shadow-sm ring-1 ring-metro-line transition-shadow duration-200 focus-within:ring-4 focus-within:ring-metro-blue/15"
          onClick={(event) => {
            if (
              event.target === event.currentTarget ||
              !(event.target as HTMLElement).closest('button, textarea')
            ) {
              ref.current?.focus();
            }
          }}
        >
          <div
            className={cn(
              'grid transition-[grid-template-rows] duration-200 ease-out',
              hasContext ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]',
            )}
          >
            <div className="overflow-hidden">
              {hasContext && (
                <div className="flex flex-wrap items-center gap-1.5 px-2.5 pb-0.5 pt-2.5">
                  {images.map((image) => (
                    <ImageChip
                      key={image.id}
                      url={image.url}
                      onRemove={
                        attachments?.onRemoveImage
                          ? () => attachments.onRemoveImage?.(image.id)
                          : undefined
                      }
                    />
                  ))}
                  {files.map((file) => (
                    <FileChip
                      key={file.id}
                      filename={file.filename}
                      size={file.size}
                      onRemove={
                        attachments?.onRemoveFile
                          ? () => attachments.onRemoveFile?.(file.id)
                          : undefined
                      }
                    />
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="grid min-h-14 grid-cols-[1fr_auto] items-end gap-2 px-3 py-2">
            <textarea
              ref={ref}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault();
                  submit();
                }
              }}
              placeholder={placeholder}
              disabled={disabled}
              rows={1}
              className={cn(
                'min-h-10 min-w-0 resize-none border-0 bg-transparent py-2 text-sm leading-6 text-metro-text outline-none placeholder:text-slate-400',
                disabled && 'cursor-not-allowed opacity-50',
              )}
            />
            <div className="flex h-10 items-center">
              <button
                type="button"
                aria-label={isWaiting ? 'Parar resposta' : 'Enviar mensagem'}
                onClick={() => {
                  if (isWaiting) {
                    onStop?.();
                  } else if (hasInput) {
                    submit();
                  }
                }}
                className={cn(
                  'inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full transition-all duration-150',
                  isWaiting || hasInput
                    ? 'bg-metro-blue text-white hover:bg-metro-blueDark'
                    : 'bg-slate-100 text-slate-400',
                )}
              >
                {isWaiting ? (
                  <Square size={14} fill="currentColor" />
                ) : (
                  <SendHorizontal size={17} />
                )}
              </button>
            </div>
          </div>

          {attachments?.onAttach && (
            <div className="absolute bottom-2 left-2">
              <button
                type="button"
                onClick={attachments.onAttach}
                aria-label="Anexar arquivo"
                className="inline-flex h-8 w-8 items-center justify-center rounded-full text-slate-500 transition-colors hover:bg-metro-background"
              >
                <Paperclip size={18} />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export const AgentChat = memo(function AgentChat({
  messages,
  onSend,
  onStop,
  status = 'ready',
  error,
  emptyStatePosition = 'default',
  placeholder,
  attachments,
  className,
}: AgentChatProps) {
  const [draft, setDraft] = useState('');

  const messagesWithError: AgentMessage[] = useMemo(() => {
    if (!error) {
      return messages;
    }

    return [
      ...messages,
      {
        id: 'agent-chat-error',
        role: 'assistant' as const,
        parts: [
          {
            type: 'error' as const,
            title: error.title ?? 'Falha na requisicao',
            message: error.message,
          },
        ],
      },
    ];
  }, [messages, error]);

  const isEmpty = !error && messages.length === 0;
  const isCenteredEmpty = isEmpty && emptyStatePosition === 'center';

  const inputBarNode: ReactNode = (
    <InputBar
      onSend={onSend}
      onStop={onStop}
      status={status}
      attachments={attachments}
      value={draft}
      onChange={setDraft}
      placeholder={placeholder}
      className={isCenteredEmpty ? 'px-0 pb-0' : undefined}
    />
  );

  return (
    <div className={cn('flex h-full min-h-0 flex-col', className)}>
      {isCenteredEmpty ? (
        <div className="flex min-h-0 flex-1 items-center justify-center px-4 py-4">
          <div className="w-full max-w-3xl">{inputBarNode}</div>
        </div>
      ) : (
        <MessageList messages={messagesWithError} status={status} />
      )}
      {!isCenteredEmpty && inputBarNode}
    </div>
  );
});

export default AgentChat;
