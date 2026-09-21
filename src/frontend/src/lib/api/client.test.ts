import { describe, it, expect, vi } from 'vitest';
import { requestJson, toDisplayMessage, parseError } from './client';
import { sendChatMessage } from './chat';
import { uploadAudio } from './audio';

describe('Contrato HTTP', () => {
  it('envia texto, contexto e toggle no corpo JSON', async () => {
    const fetch = vi.fn().mockResolvedValue(new Response('{}'));
    vi.stubGlobal('fetch', fetch);
    await sendChatMessage({
      message: 'prazo',
      conversationId: 'conversation-250',
      accessToken: 'test',
      previousInteractionId: 'anterior',
      useIntentClassifier: true,
      proactivityEnabled: true,
    });
    const [url, init] = fetch.mock.calls[0];
    expect(url).toBe('/api/chat');
    expect(JSON.parse(init.body)).toEqual({
      message: 'prazo',
      conversation_id: 'conversation-250',
      previous_interaction_id: 'anterior',
      use_intent_classifier: true,
      proactivity_enabled: true,
    });
    expect(init.headers.Authorization).toBe('Bearer test');
  });
  it('envia áudio multipart com identidade sem forçar boundary', async () => {
    const fetch = vi.fn().mockResolvedValue(new Response('{}'));
    vi.stubGlobal('fetch', fetch);
    await uploadAudio({
      audio: new Blob(['wav']),
      accessToken: 'test',
      previousInteractionId: 'before',
      useIntentClassifier: false,
      proactivityEnabled: true,
    });
    const [url, init] = fetch.mock.calls[0];
    expect(url).toBe('/api/audio');
    expect(init.headers).toEqual({ Authorization: 'Bearer test' });
    expect(init.body.get('previous_interaction_id')).toBe('before');
    expect(init.body.get('use_intent_classifier')).toBe('false');
    expect(init.body.get('proactivity_enabled')).toBe('true');
  });
  it.each([400, 401, 403, 413, 422, 429, 500, 502, 503, 504])(
    'controla o erro HTTP %s sem expor detalhe interno',
    async (status) => {
      const error = await parseError(
        new Response(JSON.stringify({ detail: 'SECRET traceback' }), { status }),
      );
      expect(error.status).toBe(status);
      expect(toDisplayMessage(error)).not.toContain('SECRET');
      expect(error.message.length).toBeGreaterThan(15);
    },
  );
  it('controla queda de rede e resposta de erro sem JSON', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));
    await expect(requestJson('/chat')).rejects.toThrow();
    expect(toDisplayMessage(new TypeError('Failed to fetch'))).not.toContain('Failed');
    expect(
      (await parseError(new Response('proxy down', { status: 502 }))).message,
    ).not.toContain('proxy');
  });
  it('propaga cancelamento até fetch', async () => {
    const controller = new AbortController();
    const fetch = vi.fn().mockResolvedValue(new Response('{}'));
    vi.stubGlobal('fetch', fetch);
    await requestJson('/chat', { signal: controller.signal });
    controller.abort();
    expect(fetch.mock.calls[0][1].signal.aborted).toBe(true);
  });
});
