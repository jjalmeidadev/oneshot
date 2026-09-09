/**
 * Camada HTTP compartilhada.
 *
 * O Vite encaminha `/api` para `http://127.0.0.1:8000` em desenvolvimento
 * (`vite.config.ts`), entao as chamadas usam caminho relativo e a chave do
 * Gemini nunca sai do backend.
 *
 * As duas rotas existentes falham em formatos diferentes: a de audio usa o
 * envelope `{ error: { code, message, detail? } }` da Secao 8.7.6 e a de texto
 * usa o `{ detail }` padrao do FastAPI. `ApiError` normaliza os dois, para o
 * componente exibir sempre `error.message` sem saber de qual rota veio.
 */

import type { AudioErrorEnvelope, DetailErrorEnvelope } from './schemas';

export const API_BASE_URL = '/api';

export class ApiError extends Error {
  readonly status: number;
  /** Presente apenas nas respostas que usam o envelope da rota de audio. */
  readonly code: string | null;
  readonly detail: Record<string, unknown> | null;

  constructor(
    message: string,
    options: {
      status: number;
      code?: string | null;
      detail?: Record<string, unknown> | null;
    },
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = options.status;
    this.code = options.code ?? null;
    this.detail = options.detail ?? null;
  }

  /** O usuario pode tentar de novo sem mudar nada na solicitacao. */
  get isTransient(): boolean {
    return (
      this.status === 429 ||
      this.status === 502 ||
      this.status === 503 ||
      this.status === 504
    );
  }
}

const FALLBACK_MESSAGE =
  'Não foi possível concluir a solicitação. Tente novamente em instantes.';

export async function parseError(response: Response): Promise<ApiError> {
  const body = (await response.json().catch(() => null)) as
    AudioErrorEnvelope | DetailErrorEnvelope | null;

  if (body && typeof body === 'object' && 'error' in body && body.error) {
    return new ApiError(body.error.message || FALLBACK_MESSAGE, {
      status: response.status,
      code: body.error.code,
      detail: body.error.detail ?? null,
    });
  }

  if (body && typeof body === 'object' && 'detail' in body && body.detail) {
    return new ApiError(String(body.detail), { status: response.status });
  }

  return new ApiError(FALLBACK_MESSAGE, { status: response.status });
}

export async function requestJson<T>(
  path: string,
  init: RequestInit & { signal?: AbortSignal } = {},
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);

  if (!response.ok) {
    throw await parseError(response);
  }

  return (await response.json()) as T;
}

/** `true` quando a falha foi um cancelamento disparado pela propria interface. */
export function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError';
}

export function toDisplayMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return FALLBACK_MESSAGE;
}
