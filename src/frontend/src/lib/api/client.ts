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

  const messages: Record<number, string> = {
    400: 'Entrada inválida. Confira o texto ou o formato do áudio.',
    401: 'Sua sessão não foi reconhecida. Confira o token de acesso.',
    403: 'Você não tem acesso a esta informação.',
    413: 'O áudio deve ter no máximo 2 MB.',
    422: 'Confira a entrada. Para áudio, grave uma fala audível de até 60 segundos.',
    429: 'Já existe uma solicitação em andamento. Aguarde e tente novamente.',
    502: 'Não foi possível obter uma resposta do serviço. Tente novamente.',
    503: 'O serviço está indisponível. Tente novamente em instantes.',
    504: 'O processamento demorou mais que o esperado. Tente novamente.',
  };
  const code = body && 'error' in body && body.error ? body.error.code : null;
  return new ApiError(messages[response.status] ?? FALLBACK_MESSAGE, {
    status: response.status,
    code,
  });
}

export async function requestJson<T>(
  path: string,
  init: RequestInit & { signal?: AbortSignal } = {},
): Promise<T> {
  const signal = AbortSignal.any([
    ...(init.signal ? [init.signal] : []),
    AbortSignal.timeout(120_000),
  ]);
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, signal });

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
  if (error instanceof Error && error.message === 'REPORT_ACCESS_TOKEN_REQUIRED') {
    return 'Informe o token de acesso da sessao para iniciar o fluxo de relatorio.';
  }
  if (error instanceof Error && error.message === 'REPORT_PROCESSING_TIMEOUT') {
    return 'O relatorio continua em processamento. Consulte novamente em alguns instantes.';
  }
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof DOMException && error.name === 'TimeoutError') {
    return 'O processamento demorou mais que o esperado. Tente novamente.';
  }
  return FALLBACK_MESSAGE;
}
