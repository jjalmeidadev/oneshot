'use client';

import { ArrowUpIcon } from 'lucide-react';
import type React from 'react';
import { createContext, useContext } from 'react';

import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useTextareaResize } from '@/hooks/use-textarea-resize';
import { cn } from '@/lib/utils';

interface ChatInputContextValue {
  value?: string;
  onChange?: React.ChangeEventHandler<HTMLTextAreaElement>;
  onSubmit?: () => void;
  loading?: boolean;
  onStop?: () => void;
  variant?: 'default' | 'unstyled';
  rows?: number;
}

const ChatInputContext = createContext<ChatInputContextValue>({});

interface ChatInputProps extends Omit<ChatInputContextValue, 'variant'> {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'unstyled';
  rows?: number;
}

function ChatInput({
  children,
  className,
  variant = 'default',
  value,
  onChange,
  onSubmit,
  loading,
  onStop,
  rows = 1,
}: ChatInputProps) {
  const contextValue: ChatInputContextValue = {
    value,
    onChange,
    onSubmit,
    loading,
    onStop,
    variant,
    rows,
  };

  return (
    <ChatInputContext.Provider value={contextValue}>
      <div
        className={cn(
          variant === 'default' &&
            'flex w-full items-end gap-2 rounded-2xl border border-metro-line bg-white p-2 shadow-sm shadow-metro-blue/10 focus-within:border-metro-blue focus-within:outline-none focus-within:ring-4 focus-within:ring-metro-blue/15',
          variant === 'unstyled' && 'flex w-full items-start gap-2',
          className,
        )}
      >
        {children}
      </div>
    </ChatInputContext.Provider>
  );
}

ChatInput.displayName = 'ChatInput';

interface ChatInputTextAreaProps extends React.ComponentProps<typeof Textarea> {
  value?: string;
  onChange?: React.ChangeEventHandler<HTMLTextAreaElement>;
  onSubmit?: () => void;
  variant?: 'default' | 'unstyled';
}

function ChatInputTextArea({
  onSubmit: onSubmitProp,
  value: valueProp,
  onChange: onChangeProp,
  className,
  variant: variantProp,
  ...props
}: ChatInputTextAreaProps) {
  const context = useContext(ChatInputContext);
  const value = valueProp ?? context.value ?? '';
  const onChange = onChangeProp ?? context.onChange;
  const onSubmit = onSubmitProp ?? context.onSubmit;
  const rows = context.rows ?? 1;
  const variant =
    variantProp ?? (context.variant === 'default' ? 'unstyled' : 'default');

  const textareaRef = useTextareaResize(value, rows);

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (!onSubmit) {
      return;
    }

    if (event.key === 'Enter' && !event.shiftKey) {
      if (typeof value !== 'string' || value.trim().length === 0) {
        return;
      }

      event.preventDefault();
      onSubmit();
    }
  };

  return (
    <Textarea
      ref={textareaRef}
      {...props}
      value={value}
      onChange={onChange}
      onKeyDown={handleKeyDown}
      className={cn(
        'max-h-[240px] min-h-0 min-w-0 flex-1 resize-none overflow-x-hidden text-metro-text placeholder:text-slate-400',
        variant === 'unstyled' &&
          'border-none shadow-none focus-visible:ring-0 focus-visible:ring-offset-0',
        className,
      )}
      rows={rows}
    />
  );
}

ChatInputTextArea.displayName = 'ChatInputTextArea';

interface ChatInputSubmitProps extends React.ComponentProps<typeof Button> {
  onSubmit?: () => void;
  loading?: boolean;
  onStop?: () => void;
}

function ChatInputSubmit({
  onSubmit: onSubmitProp,
  loading: loadingProp,
  onStop: onStopProp,
  className,
  ...props
}: ChatInputSubmitProps) {
  const context = useContext(ChatInputContext);
  const loading = loadingProp ?? context.loading;
  const onStop = onStopProp ?? context.onStop;
  const onSubmit = onSubmitProp ?? context.onSubmit;

  if (loading && onStop) {
    return (
      <Button
        aria-label="Parar resposta"
        onClick={onStop}
        className={cn(
          'h-9 w-9 shrink-0 rounded-full border border-metro-blue bg-white p-0 text-metro-blue hover:bg-metro-blue/10',
          className,
        )}
        {...props}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="currentColor"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <rect x="6" y="6" width="12" height="12" />
        </svg>
      </Button>
    );
  }

  const isDisabled =
    typeof context.value !== 'string' || context.value.trim().length === 0;

  return (
    <Button
      aria-label="Enviar mensagem"
      className={cn(
        'h-9 w-9 shrink-0 rounded-full border border-metro-blue bg-metro-blue p-0 text-white hover:bg-metro-blueDark disabled:border-slate-200 disabled:bg-slate-100 disabled:text-slate-400',
        className,
      )}
      disabled={isDisabled}
      onClick={(event) => {
        event.preventDefault();
        if (!isDisabled) {
          onSubmit?.();
        }
      }}
      {...props}
    >
      <ArrowUpIcon size={18} />
    </Button>
  );
}

ChatInputSubmit.displayName = 'ChatInputSubmit';

export { ChatInput, ChatInputSubmit, ChatInputTextArea };
