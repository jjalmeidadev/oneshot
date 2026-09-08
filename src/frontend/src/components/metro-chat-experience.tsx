import { useEffect, useRef, useState } from 'react';

import { MetricsPanel, type MetricRun } from '@/components/metrics-panel';
import {
  AgentChat,
  type AgentMessage,
  type ChatStatus,
} from '@/components/ui/agent-chat';
import { type GeminiSource, sendGeminiMessage } from '@/lib/gemini-api';
import { cn } from '@/lib/utils';

function createUserMessage(content: string): AgentMessage {
  return {
    id: crypto.randomUUID(),
    role: 'user',
    parts: [{ type: 'text', text: content }],
  };
}

function createAssistantMessage(
  content: string,
  sources: GeminiSource[],
): AgentMessage {
  return {
    id: crypto.randomUUID(),
    role: 'assistant',
    parts: [{ type: 'text', text: content }],
    sources: sources.map((source) => ({
      id: source.id,
      title: source.title,
      detail: `${source.list_name} | atualizado em ${source.last_modified}`,
    })),
  };
}

function MetroChatExperience() {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [status, setStatus] = useState<ChatStatus>('ready');
  const [error, setError] = useState<{ message: string } | undefined>();
  const [interactionId, setInteractionId] = useState<string | null>(null);
  const [runs, setRuns] = useState<MetricRun[]>([]);
  const abortControllerRef = useRef<AbortController | null>(null);

  const hasStarted = messages.length > 0;

  useEffect(
    () => () => {
      abortControllerRef.current?.abort();
    },
    [],
  );

  const handleSend = async ({ content }: { role: 'user'; content: string }) => {
    const controller = new AbortController();
    const startedAt = performance.now();
    const runId = crypto.randomUUID();

    abortControllerRef.current = controller;
    setError(undefined);
    setMessages((current) => [...current, createUserMessage(content)]);
    setStatus('submitted');

    try {
      const response = await sendGeminiMessage(
        content,
        interactionId,
        controller.signal,
      );
      const totalLatencyMs = Math.round(performance.now() - startedAt);

      setMessages((current) => [
        ...current,
        createAssistantMessage(response.text, response.sources),
      ]);
      setInteractionId(response.interaction_id);
      setRuns((current) => [
        {
          id: runId,
          prompt: content,
          success: true,
          model: response.model,
          latencyMs: totalLatencyMs,
          providerLatencyMs: response.latency_ms,
          retrievalLatencyMs: response.retrieval_ms,
          sourceCount: response.sources.length,
          inputTokens: response.usage.input_tokens,
          outputTokens: response.usage.output_tokens,
          thoughtTokens: response.usage.thought_tokens,
          totalTokens: response.usage.total_tokens,
        },
        ...current,
      ]);
    } catch (requestError) {
      const wasCancelled =
        requestError instanceof DOMException && requestError.name === 'AbortError';
      const message =
        requestError instanceof Error
          ? requestError.message
          : 'Falha inesperada ao consultar o Gemini.';

      if (!wasCancelled) {
        setError({ message });
      }
      setRuns((current) => [
        {
          id: runId,
          prompt: content,
          success: false,
          model: '',
          latencyMs: Math.round(performance.now() - startedAt),
          providerLatencyMs: null,
          retrievalLatencyMs: null,
          sourceCount: 0,
          inputTokens: 0,
          outputTokens: 0,
          thoughtTokens: 0,
          totalTokens: 0,
          error: wasCancelled ? 'Execucao cancelada' : message,
        },
        ...current,
      ]);
    } finally {
      setStatus('ready');
      abortControllerRef.current = null;
    }
  };

  const handleStop = () => {
    abortControllerRef.current?.abort();
  };

  return (
    <section
      className={cn(
        'mx-auto flex min-h-screen w-full max-w-6xl flex-col px-4 py-6 transition-all duration-500 ease-out sm:px-6',
        hasStarted ? 'justify-start' : 'justify-center',
      )}
    >
      <div
        className={cn(
          'mx-auto flex w-full flex-col items-center transition-all duration-500 ease-out',
          hasStarted ? 'max-w-6xl gap-4' : 'max-w-3xl gap-8',
        )}
      >
        <header
          className={cn(
            'flex w-full items-center transition-all duration-500 ease-out',
            hasStarted ? 'justify-start' : 'justify-center',
          )}
        >
          <img
            src="/logo-metro-sp.png"
            alt="Metro de Sao Paulo"
            className={cn(
              'h-auto max-w-full transition-all duration-500 ease-out',
              hasStarted ? 'w-36 sm:w-44' : 'w-64',
            )}
          />
        </header>

        <div
          className={cn(
            'w-full overflow-hidden transition-all duration-500 ease-out',
            hasStarted
              ? 'h-[min(760px,calc(100vh-150px))] rounded-2xl border border-metro-line bg-white shadow-xl shadow-metro-blue/10 opacity-100'
              : 'h-24 rounded-none border border-transparent bg-transparent shadow-none opacity-100',
          )}
        >
          <div
            className={cn(
              'h-full min-h-0',
              hasStarted &&
                'grid grid-rows-[minmax(0,1fr)_auto] lg:grid-cols-[minmax(0,1fr)_17rem] lg:grid-rows-1',
            )}
          >
            <AgentChat
              messages={messages}
              status={status}
              error={error}
              onSend={handleSend}
              onStop={handleStop}
              emptyStatePosition="center"
              placeholder="Pergunte qualquer coisa ao Gemini..."
            />
            {hasStarted && (
              <MetricsPanel
                runs={runs}
                onClear={() => setRuns([])}
                className="max-h-44 lg:max-h-none"
              />
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

export { MetroChatExperience };
