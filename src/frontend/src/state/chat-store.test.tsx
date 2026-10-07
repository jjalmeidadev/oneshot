import { act, renderHook, waitFor } from '@testing-library/react';
import type { ReactNode } from 'react';
import { describe, it, expect, vi } from 'vitest';
import { ChatStoreProvider, useChatStore } from './chat-store';
import { response } from '@/tests/fixtures';
import { responseBlocks } from '@/tests/response-blocks-fixture';

function AuthenticatedWrapper({ children }: { children: ReactNode }) {
  return <ChatStoreProvider accessToken="test">{children}</ChatStoreProvider>;
}

function UnauthenticatedWrapper({ children }: { children: ReactNode }) {
  return <ChatStoreProvider accessToken="">{children}</ChatStoreProvider>;
}

describe('Estado e integração do chat', () => {
  it('começa sem dados fictícios, cria conversa no primeiro envio e preserva contexto', async () => {
    const fetch = vi
      .fn()
      .mockImplementation(() =>
        Promise.resolve(new Response(JSON.stringify(response))),
      );
    vi.stubGlobal('fetch', fetch);
    const { result } = renderHook(useChatStore, { wrapper: AuthenticatedWrapper });
    expect(result.current.conversations).toHaveLength(0);
    act(() => result.current.setProactivityEnabled(true));
    await act(async () => {
      await result.current.sendMessage('prazo');
    });
    expect(JSON.parse(fetch.mock.calls[0][1].body).proactivity_enabled).toBe(true);
    expect(result.current.activeConversation?.messages).toHaveLength(2);
    expect(result.current.activeSources[0].excerpt).toBe(
      'Entrega prevista para dezembro.',
    );
    await act(async () => {
      await result.current.sendMessage('e o custo?');
    });
    expect(JSON.parse(fetch.mock.calls[1][1].body).previous_interaction_id).toBe(
      'interaction-1',
    );
    act(() => result.current.newConversation());
    await act(async () => {
      await result.current.sendMessage('outra pergunta');
    });
    expect(JSON.parse(fetch.mock.calls[2][1].body).previous_interaction_id).toBeNull();
  });
  it('não envia entrada inválida nem duplica requisição concorrente', async () => {
    let resolve!: (value: Response) => void;
    const fetch = vi.fn().mockImplementation(
      () =>
        new Promise<Response>((r) => {
          resolve = r;
        }),
    );
    vi.stubGlobal('fetch', fetch);
    const { result } = renderHook(useChatStore, { wrapper: AuthenticatedWrapper });
    await act(async () => {
      expect(await result.current.sendMessage('  ')).toBe(false);
    });
    expect(fetch).not.toHaveBeenCalled();
    let pending!: Promise<boolean>;
    act(() => {
      pending = result.current.sendMessage('prazo');
    });
    await act(async () => {
      expect(await result.current.sendMessage('duplicada')).toBe(false);
    });
    expect(fetch).toHaveBeenCalledTimes(1);
    await act(async () => {
      resolve(new Response(JSON.stringify(response)));
      await pending;
    });
  });
  it('descarta resposta atrasada após trocar de conversa', async () => {
    let resolve!: (value: Response) => void;
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation(
        () =>
          new Promise<Response>((r) => {
            resolve = r;
          }),
      ),
    );
    const { result } = renderHook(useChatStore, { wrapper: AuthenticatedWrapper });
    let pending!: Promise<boolean>;
    act(() => {
      pending = result.current.sendMessage('prazo');
    });
    act(() => result.current.newConversation());
    await act(async () => {
      resolve(new Response(JSON.stringify(response)));
      await pending;
    });
    expect(result.current.activeConversation?.messages).toHaveLength(0);
    expect(result.current.status).toBe('idle');
  });
  it('mostra falha, libera novo envio e mantém a pergunta', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('internal')));
    const { result } = renderHook(useChatStore, { wrapper: AuthenticatedWrapper });
    await act(async () => {
      await result.current.sendMessage('prazo');
    });
    await waitFor(() => expect(result.current.status).toBe('error'));
    expect(result.current.error).not.toContain('internal');
    expect(result.current.activeConversation?.messages[0].content).toBe('prazo');
  });
  it('exige token para áudio e usa transcrição e resultado reais', async () => {
    const fetch = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          pipeline_status: 'completed',
          chat: response,
          transcription: {
            text: 'pergunta falada',
            confidence: 0.9,
            duration_seconds: 1,
          },
          pipeline_metrics: {
            validation_ms: 2,
            stt_ms: 3,
            nlp_ms: 4,
            route_ms: 5,
            total_ms: 12,
          },
        }),
      ),
    );
    vi.stubGlobal('fetch', fetch);
    const { result } = renderHook(useChatStore, { wrapper: UnauthenticatedWrapper });
    await act(async () => {
      expect(await result.current.sendAudio(new Blob(['wav']))).toBe(false);
    });
    expect(fetch).not.toHaveBeenCalled();
    const authenticated = renderHook(useChatStore, {
      wrapper: AuthenticatedWrapper,
    });
    await act(async () => {
      await authenticated.result.current.sendAudio(new Blob(['wav']));
    });
    expect(authenticated.result.current.activeConversation?.messages[0].origin).toBe(
      'audio',
    );
    expect(authenticated.result.current.activeConversation?.messages[0].content).toBe(
      'pergunta falada',
    );
    expect(authenticated.result.current.activeConversation?.messages[1].content).toBe(
      response.text,
    );
    expect(
      authenticated.result.current.activeConversation?.messages[1].entities?.[0].value,
    ).toBe('Projeto Linha Verde');
    expect(
      authenticated.result.current.activeConversation?.messages[1].metrics?.sttMs,
    ).toBe(3);
    expect(
      authenticated.result.current.activeConversation?.messages[1].metrics
        ?.backendTotalMs,
    ).toBe(12);
  });
  it('aceita somente a sugestão vinculada e acrescenta a resposta confirmada', async () => {
    const confirmed = {
      ...response,
      text: 'O gargalo documentado é o fornecedor. [Fonte 1]',
      interaction_id: 'interaction-confirmed',
      proactive_suggestion: null,
    };
    const fetch = vi
      .fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(response)))
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ status: 'accepted', result: confirmed })),
      );
    vi.stubGlobal('fetch', fetch);
    const { result } = renderHook(useChatStore, { wrapper: AuthenticatedWrapper });
    await act(async () => {
      await result.current.sendMessage('status');
    });
    const suggestionMessage = result.current.activeConversation!.messages[1];
    const conversationId = result.current.activeConversation!.id;

    await act(async () => {
      await result.current.resolveProactiveSuggestion(suggestionMessage.id, 'accept');
    });

    const body = JSON.parse(fetch.mock.calls[1][1].body);
    expect(body).toEqual({
      suggestion_id: response.proactive_suggestion!.suggestion_id,
      conversation_id: conversationId,
      decision: 'accept',
    });
    expect(body).not.toHaveProperty('message');
    expect(fetch.mock.calls[1][1].headers.Authorization).toBe('Bearer test');
    expect(
      result.current.activeConversation!.messages[1].proactiveSuggestion?.status,
    ).toBe('accepted');
    expect(result.current.activeConversation!.messages[2].content).toBe(confirmed.text);
    expect(result.current.activeConversation!.messages[2].interactionId).toBeNull();
    expect(result.current.activeConversation!.lastInteractionId).toBe('interaction-1');
  });
  it('recusa a sugestão sem acrescentar resposta secundária', async () => {
    const fetch = vi
      .fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(response)))
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ status: 'declined', result: null })),
      );
    vi.stubGlobal('fetch', fetch);
    const { result } = renderHook(useChatStore, { wrapper: AuthenticatedWrapper });
    await act(async () => {
      await result.current.sendMessage('status');
    });
    const suggestionMessage = result.current.activeConversation!.messages[1];

    await act(async () => {
      await result.current.resolveProactiveSuggestion(suggestionMessage.id, 'decline');
    });

    expect(result.current.activeConversation!.messages).toHaveLength(2);
    expect(
      result.current.activeConversation!.messages[1].proactiveSuggestion?.status,
    ).toBe('declined');
  });
  it('restaura a sugestão pendente quando a confirmação é interrompida', async () => {
    const fetch = vi
      .fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(response)))
      .mockImplementationOnce(
        (_url, init: RequestInit) =>
          new Promise<Response>((_resolve, reject) => {
            init.signal?.addEventListener('abort', () =>
              reject(new DOMException('aborted', 'AbortError')),
            );
          }),
      );
    vi.stubGlobal('fetch', fetch);
    const { result } = renderHook(useChatStore, { wrapper: AuthenticatedWrapper });
    await act(async () => {
      await result.current.sendMessage('status');
    });
    const suggestionMessage = result.current.activeConversation!.messages[1];

    let confirmation!: Promise<boolean>;
    act(() => {
      confirmation = result.current.resolveProactiveSuggestion(
        suggestionMessage.id,
        'accept',
      );
    });
    expect(
      result.current.activeConversation!.messages[1].proactiveSuggestion?.status,
    ).toBe('accepting');

    act(() => result.current.stop());
    await act(async () => {
      await confirmation;
    });

    expect(
      result.current.activeConversation!.messages[1].proactiveSuggestion?.status,
    ).toBe('pending');
    expect(result.current.status).toBe('idle');
  });

  it('começa com a tela enxuta: sem modo técnico e com o painel de fontes fechado', () => {
    const { result } = renderHook(useChatStore, { wrapper: AuthenticatedWrapper });
    expect(result.current.showTechnicalDetails).toBe(false);
    expect(result.current.documentPanelOpen).toBe(false);
    act(() => result.current.setShowTechnicalDetails(true));
    expect(result.current.showTechnicalDetails).toBe(true);
  });
});

describe('Preservação de blocos estruturados nos canais', () => {
  it.each(['text', 'audio'] as const)(
    'preserva os três tipos no canal %s',
    async (channel) => {
      const chat = { ...response, contract_version: '1.2.0', blocks: responseBlocks };
      vi.stubGlobal(
        'fetch',
        vi.fn().mockResolvedValue(
          new Response(
            JSON.stringify(
              channel === 'text'
                ? chat
                : {
                    pipeline_status: 'completed',
                    chat,
                    transcription: {
                      text: 'avanço',
                      confidence: 1,
                      duration_seconds: 1,
                    },
                  },
            ),
          ),
        ),
      );
      const { result } = renderHook(useChatStore, { wrapper: AuthenticatedWrapper });
      await act(async () => {
        expect(
          await (channel === 'text'
            ? result.current.sendMessage('avanço')
            : result.current.sendAudio(new Blob(['wav']))),
        ).toBe(true);
      });
      expect(result.current.activeConversation?.messages[1].blocks).toEqual(
        responseBlocks,
      );
    },
  );
});
