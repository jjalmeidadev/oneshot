import { requestJson } from './client';
import type { AlertWorkflowResponse, AlertWorkflowStep } from './schemas';

function headers(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
}

export function startAlertWorkflow(input: {
  conversationId: string;
  interactionId: string | null;
  parameters: Record<string, unknown>;
  accessToken: string;
}): Promise<AlertWorkflowResponse> {
  return requestJson('/alert-workflow-sessions', {
    method: 'POST',
    headers: headers(input.accessToken),
    body: JSON.stringify({
      contract_version: '1.0',
      conversation_id: input.conversationId,
      interaction_id: input.interactionId,
      parameters: input.parameters,
    }),
  });
}

export function answerAlertWorkflow(input: {
  sessionId: string;
  step: AlertWorkflowStep;
  value: unknown;
  revision: number;
  accessToken: string;
}): Promise<AlertWorkflowResponse> {
  return requestJson(`/alert-workflow-sessions/${input.sessionId}/answers`, {
    method: 'POST',
    headers: headers(input.accessToken),
    body: JSON.stringify({
      step: input.step,
      value: input.value,
      revision: input.revision,
      client_action_id: crypto.randomUUID(),
    }),
  });
}

export function confirmAlertWorkflow(input: {
  sessionId: string;
  revision: number;
  accessToken: string;
}): Promise<AlertWorkflowResponse> {
  return requestJson(`/alert-workflow-sessions/${input.sessionId}/confirm`, {
    method: 'POST',
    headers: headers(input.accessToken),
    body: JSON.stringify({
      revision: input.revision,
      client_action_id: crypto.randomUUID(),
    }),
  });
}

export function cancelAlertWorkflow(
  sessionId: string,
  accessToken: string,
): Promise<AlertWorkflowResponse> {
  return requestJson(`/alert-workflow-sessions/${sessionId}/cancel`, {
    method: 'POST',
    headers: headers(accessToken),
  });
}
