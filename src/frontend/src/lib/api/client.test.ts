import { describe, it, expect, vi } from 'vitest';
import { requestJson, toDisplayMessage, parseError } from './client';
import { sendChatMessage } from './chat';
import { uploadAudio } from './audio';
import {
  answerReportWorkflow,
  cancelReportWorkflow,
  confirmReportWorkflow,
  downloadReportArtifact,
  getReportWorkflow,
  startReportWorkflow,
} from './report-workflow';

describe('Contrato HTTP', () => {
  it('envia texto, contexto e toggle no corpo JSON', async () => {
    const fetch = vi.fn().mockResolvedValue(new Response('{}'));
    vi.stubGlobal('fetch', fetch);
    await sendChatMessage({
      message: 'prazo',
      conversationId: 'conversation-1',
      accessToken: 'test',
      previousInteractionId: 'anterior',
      useIntentClassifier: true,
      proactivityEnabled: true,
    });
    const [url, init] = fetch.mock.calls[0];
    expect(url).toBe('/api/chat');
    expect(JSON.parse(init.body)).toEqual({
      message: 'prazo',
      conversation_id: 'conversation-1',
      previous_interaction_id: 'anterior',
      use_intent_classifier: true,
      proactivity_enabled: true,
      include_audio: true,
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
    expect(init.body.get('include_audio')).toBe('true');
  });
  it('inicia e responde o workflow com identidade, revisão e idempotência', async () => {
    const workflow = {
      contract_version: '1.0',
      session_id: 'session-1',
      workflow: 'transacao_gerar_relatorio',
      status: 'active',
      current_step: 'scope_type',
      revision: 0,
      answers: {},
      warnings: [],
    };
    const fetch = vi
      .fn()
      .mockImplementation(() =>
        Promise.resolve(new Response(JSON.stringify(workflow))),
      );
    vi.stubGlobal('fetch', fetch);

    await startReportWorkflow({
      conversationId: 'conversation-1',
      interactionId: 'interaction-1',
      parameters: { scope_candidates: [] },
      accessToken: 'report-token',
    });
    await answerReportWorkflow({
      sessionId: 'session-1',
      step: 'scope_type',
      value: 'project',
      revision: 0,
      accessToken: 'report-token',
    });

    expect(fetch.mock.calls[0][0]).toBe('/api/workflow-sessions');
    expect(fetch.mock.calls[0][1].headers.Authorization).toBe('Bearer report-token');
    expect(JSON.parse(fetch.mock.calls[1][1].body)).toMatchObject({
      step: 'scope_type',
      value: 'project',
      revision: 0,
    });
    expect(JSON.parse(fetch.mock.calls[1][1].body).client_action_id).toBeTruthy();
  });
  it('confirma, consulta e cancela o workflow autenticado', async () => {
    const workflow = {
      contract_version: '1.0',
      session_id: 'session-1',
      workflow: 'transacao_gerar_relatorio',
      status: 'executing',
      current_step: 'execution',
      revision: 8,
      answers: {},
      warnings: [],
    };
    const fetch = vi.fn().mockImplementation(() =>
      Promise.resolve(
        new Response(JSON.stringify(workflow), {
          headers: { 'Content-Type': 'application/json' },
        }),
      ),
    );
    vi.stubGlobal('fetch', fetch);

    await confirmReportWorkflow({
      sessionId: 'session-1',
      revision: 7,
      accessToken: 'report-token',
    });
    await getReportWorkflow('session-1', 'report-token');
    await cancelReportWorkflow('session-1', 'report-token');

    expect(fetch.mock.calls.map(([url]) => url)).toEqual([
      '/api/workflow-sessions/session-1/confirm',
      '/api/workflow-sessions/session-1',
      '/api/workflow-sessions/session-1/cancel',
    ]);
    expect(JSON.parse(fetch.mock.calls[0][1].body)).toMatchObject({ revision: 7 });
    expect(JSON.parse(fetch.mock.calls[0][1].body).client_action_id).toBeTruthy();
    expect(fetch.mock.calls[1][1].headers.Authorization).toBe('Bearer report-token');
  });
  it('baixa o DOCX pelo backend e revoga a URL temporaria', async () => {
    const fetch = vi.fn().mockResolvedValue(new Response(new Blob(['PK-report'])));
    const click = vi
      .spyOn(HTMLAnchorElement.prototype, 'click')
      .mockImplementation(() => undefined);
    const createObjectURL = vi.fn().mockReturnValue('blob:report');
    const revokeObjectURL = vi.fn();
    vi.stubGlobal('fetch', fetch);
    vi.stubGlobal('URL', { ...URL, createObjectURL, revokeObjectURL });

    await downloadReportArtifact({
      executionId: 'execution-1',
      fileName: 'relatorio.docx',
      accessToken: 'report-token',
    });

    expect(fetch).toHaveBeenCalledWith('/api/report-requests/execution-1/artifact', {
      headers: { Authorization: 'Bearer report-token' },
    });
    expect(click).toHaveBeenCalledOnce();
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:report');
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
