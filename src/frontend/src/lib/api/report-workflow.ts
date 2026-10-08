import { API_BASE_URL, parseError, requestJson } from './client';
import { notifyUnauthorized } from './session-events';
import type { WorkflowSessionResponse, WorkflowStep } from './schemas';

function authHeaders(accessToken: string): HeadersInit {
  return {
    Authorization: `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  };
}

export function startReportWorkflow(input: {
  conversationId: string;
  interactionId: string | null;
  parameters: Record<string, unknown>;
  accessToken: string;
}): Promise<WorkflowSessionResponse> {
  return requestJson('/workflow-sessions', {
    method: 'POST',
    headers: authHeaders(input.accessToken),
    body: JSON.stringify({
      contract_version: '1.0',
      conversation_id: input.conversationId,
      interaction_id: input.interactionId,
      parameters: input.parameters,
    }),
  });
}

export function answerReportWorkflow(input: {
  sessionId: string;
  step: WorkflowStep;
  value: unknown;
  revision: number;
  accessToken: string;
}): Promise<WorkflowSessionResponse> {
  return requestJson(`/workflow-sessions/${input.sessionId}/answers`, {
    method: 'POST',
    headers: authHeaders(input.accessToken),
    body: JSON.stringify({
      step: input.step,
      value: input.value,
      revision: input.revision,
      client_action_id: crypto.randomUUID(),
    }),
  });
}

export function confirmReportWorkflow(input: {
  sessionId: string;
  revision: number;
  accessToken: string;
}): Promise<WorkflowSessionResponse> {
  return requestJson(`/workflow-sessions/${input.sessionId}/confirm`, {
    method: 'POST',
    headers: authHeaders(input.accessToken),
    body: JSON.stringify({
      revision: input.revision,
      client_action_id: crypto.randomUUID(),
    }),
  });
}

export function getReportWorkflow(
  sessionId: string,
  accessToken: string,
  signal?: AbortSignal,
): Promise<WorkflowSessionResponse> {
  return requestJson(`/workflow-sessions/${sessionId}`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    signal,
  });
}

export function cancelReportWorkflow(
  sessionId: string,
  accessToken: string,
): Promise<WorkflowSessionResponse> {
  return requestJson(`/workflow-sessions/${sessionId}/cancel`, {
    method: 'POST',
    headers: authHeaders(accessToken),
  });
}

export async function downloadReportArtifact(input: {
  executionId: string;
  fileName: string;
  accessToken: string;
}): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/report-requests/${input.executionId}/artifact`,
    { headers: { Authorization: `Bearer ${input.accessToken}` } },
  );
  if (!response.ok) {
    const error = await parseError(response);
    if (response.status === 401) notifyUnauthorized();
    throw error;
  }
  const url = URL.createObjectURL(await response.blob());
  try {
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = input.fileName;
    anchor.click();
  } finally {
    URL.revokeObjectURL(url);
  }
}
