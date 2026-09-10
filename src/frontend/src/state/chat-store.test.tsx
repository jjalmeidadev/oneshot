import { act, renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ChatStoreProvider, useChatStore } from './chat-store';
import { response } from '@/tests/fixtures';

describe('Estado e integração do chat', () => {
  it('começa sem dados fictícios, cria conversa no primeiro envio e preserva contexto', async () => {
    const fetch = vi
      .fn()
      .mockImplementation(() =>
        Promise.resolve(new Response(JSON.stringify(response))),
      );
    vi.stubGlobal('fetch', fetch);
    const { result } = renderHook(useChatStore, { wrapper: ChatStoreProvider });
    expect(result.current.conversations).toHaveLength(0);
    await act(async () => {
      await result.current.sendMessage('prazo');
    });
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
    const { result } = renderHook(useChatStore, { wrapper: ChatStoreProvider });
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
    const { result } = renderHook(useChatStore, { wrapper: ChatStoreProvider });
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
    const { result } = renderHook(useChatStore, { wrapper: ChatStoreProvider });
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
        }),
      ),
    );
    vi.stubGlobal('fetch', fetch);
    const { result } = renderHook(useChatStore, { wrapper: ChatStoreProvider });
    await act(async () => {
      expect(await result.current.sendAudio(new Blob(['wav']))).toBe(false);
    });
    expect(fetch).not.toHaveBeenCalled();
    act(() => result.current.setAccessToken('test'));
    await act(async () => {
      await result.current.sendAudio(new Blob(['wav']));
    });
    expect(result.current.activeConversation?.messages[0].origin).toBe('audio');
    expect(result.current.activeConversation?.messages[0].content).toBe(
      'pergunta falada',
    );
    expect(result.current.activeConversation?.messages[1].content).toBe(response.text);
  });
});
