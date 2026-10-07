/**
 * Rotas do cartao de alteracao de dados (S5-06, contrato da Secao 8.5.13).
 *
 * O chat so devolve a previa; a escrita acontece apenas em `confirm`, chamado
 * pelo botao do cartao. Todas as rotas exigem o Bearer token da sessao.
 */

import { ApiError, requestJson, toDisplayMessage } from './client';
import type {
  DataChangeConfirmResponse,
  DataChangeHistoryResponse,
  DataChangeOutcome,
  DataChangePreviewRequest,
  DataChangeUndoResponse,
} from './schemas';

function headers(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
}

export function createDataChangePreview(
  request: DataChangePreviewRequest,
  accessToken: string,
): Promise<DataChangeOutcome> {
  return requestJson('/data-change-previews', {
    method: 'POST',
    headers: headers(accessToken),
    body: JSON.stringify(request),
  });
}

export function confirmDataChange(input: {
  pendingChangeId: string;
  reason?: string | null;
  accessToken: string;
}): Promise<DataChangeConfirmResponse> {
  const reason = input.reason?.trim();
  return requestJson(
    `/data-change-previews/${encodeURIComponent(input.pendingChangeId)}/confirm`,
    {
      method: 'POST',
      headers: headers(input.accessToken),
      body: JSON.stringify({ reason: reason ? reason : null }),
    },
  );
}

export function cancelDataChange(
  pendingChangeId: string,
  accessToken: string,
): Promise<{ status: 'cancelada' }> {
  return requestJson(
    `/data-change-previews/${encodeURIComponent(pendingChangeId)}/cancel`,
    { method: 'POST', headers: headers(accessToken) },
  );
}

export function undoDataChange(
  changeId: string,
  accessToken: string,
): Promise<DataChangeUndoResponse> {
  return requestJson(`/data-changes/${encodeURIComponent(changeId)}/undo`, {
    method: 'POST',
    headers: headers(accessToken),
  });
}

export function listDataChanges(input: {
  projectCode: string;
  field: string;
  targetId?: string | null;
  accessToken: string;
  signal?: AbortSignal;
}): Promise<DataChangeHistoryResponse> {
  const params = new URLSearchParams({
    project_code: input.projectCode,
    field: input.field,
  });
  if (input.targetId) params.set('target_id', input.targetId);
  return requestJson(`/data-changes?${params.toString()}`, {
    headers: headers(input.accessToken),
    signal: input.signal,
  });
}

/** Codigos em que repetir a mesma acao nao adianta: e preciso pedir de novo. */
const FINAL_CODES = new Set([
  'PREVIEW_EXPIRED',
  'PREVIEW_CANCELLED',
  'PREVIEW_NOT_FOUND',
  'PREVIEW_ALREADY_CONFIRMED',
  'STALE_PREVIEW',
  'OUT_OF_SCOPE_FOR_PROFILE',
  'TARGET_NOT_FOUND',
  'INVALID_VALUE',
  'FIELD_NOT_EDITABLE',
  'UNDO_WINDOW_EXPIRED',
  'UNDO_NOT_AUTHOR',
  'VALUE_CHANGED_SINCE',
  'ALREADY_UNDONE',
  'CHANGE_NOT_FOUND',
]);

export type DataChangeFailure = {
  code: string | null;
  message: string;
  /** A mesma acao pode ser repetida (falha de rede ou servico indisponivel). */
  retryable: boolean;
};

/** Mensagem do backend quando houver; ela ja explica o que fazer. */
export function toDataChangeFailure(error: unknown): DataChangeFailure {
  if (error instanceof ApiError) {
    return {
      code: error.code,
      message: error.serverMessage ?? error.message,
      retryable: !(error.code && FINAL_CODES.has(error.code)) && error.isTransient,
    };
  }
  return { code: null, message: toDisplayMessage(error), retryable: true };
}
