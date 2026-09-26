import { AlertTriangle, AudioLines, Sparkles, User } from 'lucide-react';

import { IntentBadge } from '@/components/chat/intent-badge';
import { MarkdownMessage } from '@/components/chat/markdown-message';
import { ProactiveSuggestion } from '@/components/chat/proactive-suggestion';
import { ReportWorkflowCard } from '@/components/chat/report-workflow-card';
import { AlertWorkflowCard } from '@/components/chat/alert-workflow-card';
import { SourceCitations } from '@/components/chat/source-citations';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { formatConfidence, formatDuration, formatTime } from '@/lib/format';
import type { ProactiveDecision } from '@/lib/api';
import type { ChatMessage } from '@/lib/domain';

export function MessageBubble({
  message,
  selectedSourceId,
  onSelectSource,
  onResolveProactiveSuggestion,
}: {
  message: ChatMessage;
  selectedSourceId: string | null;
  onSelectSource: (id: string) => void;
  onResolveProactiveSuggestion: (
    messageId: string,
    decision: ProactiveDecision,
  ) => void;
}) {
  if (message.role === 'user') {
    return <UserMessage message={message} />;
  }

  return (
    <AssistantMessage
      message={message}
      selectedSourceId={selectedSourceId}
      onSelectSource={onSelectSource}
      onResolveProactiveSuggestion={onResolveProactiveSuggestion}
    />
  );
}

function UserMessage({ message }: { message: ChatMessage }) {
  return (
    <div className="flex justify-end">
      <div className="flex max-w-[85%] flex-col items-end gap-1">
        <div className="rounded-2xl rounded-br-md bg-primary px-3.5 py-2.5 text-sm leading-6 text-primary-fg">
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>
        <div className="flex items-center gap-2 pr-1 text-2xs text-fg-subtle">
          {message.origin === 'audio' && message.transcription && (
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  className="rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <Badge tone="outline">
                    <AudioLines size={11} />
                    Transcrito
                  </Badge>
                </button>
              </TooltipTrigger>
              <TooltipContent side="bottom" align="end">
                <p className="font-medium">Transcrição do áudio</p>
                <p className="mt-1 text-fg-muted">
                  {formatDuration(message.transcription.durationSeconds)} de gravação,
                  confiança de {formatConfidence(message.transcription.confidence)},
                  devolvida por <code>POST /api/audio</code>.
                </p>
              </TooltipContent>
            </Tooltip>
          )}
          <span>{formatTime(message.createdAt)}</span>
          <User size={11} />
        </div>
      </div>
    </div>
  );
}

function AssistantMessage({
  message,
  selectedSourceId,
  onSelectSource,
  onResolveProactiveSuggestion,
}: {
  message: ChatMessage;
  selectedSourceId: string | null;
  onSelectSource: (id: string) => void;
  onResolveProactiveSuggestion: (
    messageId: string,
    decision: ProactiveDecision,
  ) => void;
}) {
  const isError = message.status === 'error';

  return (
    <div className="flex items-start gap-3">
      <span
        className={
          isError
            ? 'mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-danger-soft text-danger'
            : 'mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary-soft text-primary'
        }
      >
        {isError ? <AlertTriangle size={14} /> : <Sparkles size={14} />}
      </span>

      <div className="min-w-0 flex-1">
        {isError ? (
          <div className="rounded-xl border border-danger/40 bg-danger-soft px-3.5 py-2.5">
            <p className="text-xs font-medium text-danger">
              Não foi possível responder
            </p>
            <p className="mt-1 text-xs leading-5 text-fg-muted">{message.error}</p>
          </div>
        ) : (
          <>
            <MarkdownMessage content={message.content} />
            {message.workflow?.workflow === 'transacao_gerar_relatorio' && (
              <ReportWorkflowCard workflow={message.workflow} />
            )}
            {message.workflow?.workflow === 'alerta_prazo_atraso' && (
              <AlertWorkflowCard workflow={message.workflow} />
            )}
          </>
        )}

        {message.sources && (
          <SourceCitations
            sources={message.sources}
            selectedId={selectedSourceId}
            onSelect={onSelectSource}
            unused={message.evidenceStatus === 'insufficient'}
          />
        )}

        {message.proactiveSuggestion && (
          <ProactiveSuggestion
            suggestion={message.proactiveSuggestion}
            onResolve={(decision) => onResolveProactiveSuggestion(message.id, decision)}
          />
        )}

        <div className="mt-2.5 flex flex-wrap items-center gap-2 text-2xs text-fg-subtle">
          <span>{formatTime(message.createdAt)}</span>
          {message.intent && (
            <>
              <span aria-hidden>·</span>
              <IntentBadge intent={message.intent} />
            </>
          )}
          {message.metrics && (
            <>
              <span aria-hidden>·</span>
              <span className="font-mono">{message.metrics.model}</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
