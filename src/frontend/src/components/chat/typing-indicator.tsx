import { Sparkles } from 'lucide-react';

/** Estado de espera entre o envio da pergunta e a chegada da resposta. */
export function TypingIndicator({ label }: { label: string }) {
  return (
    <div className="flex items-start gap-3">
      <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary-soft text-primary">
        <Sparkles size={14} />
      </span>
      <div className="flex items-center gap-2 pt-1.5">
        <span className="flex gap-1" aria-hidden>
          <span className="h-1.5 w-1.5 rounded-full bg-fg-subtle animate-pulse-dot" />
          <span
            className="h-1.5 w-1.5 rounded-full bg-fg-subtle animate-pulse-dot"
            style={{ animationDelay: '0.15s' }}
          />
          <span
            className="h-1.5 w-1.5 rounded-full bg-fg-subtle animate-pulse-dot"
            style={{ animationDelay: '0.3s' }}
          />
        </span>
        <span className="text-xs text-fg-muted">{label}</span>
      </div>
    </div>
  );
}
