/**
 * Espelho dos schemas do backend.
 *
 * Cada tipo aqui corresponde a um `BaseModel` de `src/backend/app`. Alterar um
 * campo deste arquivo sem alterar o schema correspondente no backend quebra a
 * integracao em silencio, entao a origem esta anotada em cada bloco.
 *
 * O que **existe hoje** no backend:
 *   POST /api/chat   -> app/gemini/schemas.py
 *   POST /api/audio  -> app/audio/schemas.py
 *   GET  /health     -> app/main.py
 *
 */

/* -------------------------------------------------------------------------
 * POST /api/chat  —  app/gemini/schemas.py
 * ---------------------------------------------------------------------- */

/** `GeminiChatRequest`. `message` tem min_length=1 e max_length=20000. */
export type ChatRequest = {
  message: string;
  use_intent_classifier?: boolean;
  previous_interaction_id?: string | null;
};

/** `GeminiUsage`. Contagem de tokens devolvida pela API de interacoes. */
export type ChatUsage = {
  input_tokens: number;
  output_tokens: number;
  thought_tokens: number;
  total_tokens: number;
};

/**
 * `GeminiSource` — um documento recuperado pelo RAG.
 *
 * Montado em `app/gemini/client.py` a partir de `RetrievedDocument`
 * (`app/rag/sharepoint.py`). O `id` tem o formato `<lista>:<item>`, por exemplo
 * `base-atendimento:301`, e o `score` **nao** e normalizado entre 0 e 1: e a
 * soma de tokens casados + 2x tokens casados no titulo + cobertura da consulta.
 *
 * `excerpt` contém o trecho recuperado usado na resposta.
 */
export type ChatSource = {
  id: string;
  title: string;
  list_name: string;
  web_url: string;
  /** ISO 8601, vindo de `lastModifiedDateTime` da lista do SharePoint. */
  last_modified: string;
  score: number;
  excerpt?: string | null;
};

/** `GeminiChatResponse`. */
export type ChatResponse = {
  intent?: AudioIntent | null;
  text: string;
  model: string;
  interaction_id: string | null;
  latency_ms: number;
  retrieval_ms: number;
  usage: ChatUsage;
  sources: ChatSource[];
};

/* -------------------------------------------------------------------------
 * POST /api/audio  —  app/audio/schemas.py
 * ---------------------------------------------------------------------- */

/** `AudioTranscription`. */
export type AudioTranscription = {
  text: string;
  confidence: number;
  duration_seconds: number;
};

/**
 * `AudioIntent` — saida do classificador hierarquico de intencoes.
 *
 * Null na resposta quando a classificação está desligada.
 */
export type AudioIntent = {
  macro: MacroIntent | string;
  specific: string;
  confidence_macro: number;
  confidence_specific: number;
};

/** `AudioAnswerSource`. Formato diferente do `ChatSource` da rota de texto. */
export type AudioAnswerSource = {
  artifact: string;
  section: string;
};

/** `AudioAnswer`. */
export type AudioAnswer = {
  text: string;
  sources: AudioAnswerSource[];
};

/** `AudioUploadResponse`. */
export type AudioUploadResponse = {
  chat?: ChatResponse | null;
  conversation_id: string;
  interaction_id: string | null;
  transcription: AudioTranscription;
  intent: AudioIntent | null;
  answer: AudioAnswer;
  /** Uma resposta utilizável exige pipeline concluído. */
  pipeline_status: string;
};

/* -------------------------------------------------------------------------
 * Envelopes de erro
 * ---------------------------------------------------------------------- */

/**
 * `AudioErrorResponse` — envelope unico da rota de audio (Secao 8.7.6).
 * O RNF11 exige mensagem controlada, entao `message` ja vem pronta para exibir.
 */
export type AudioErrorEnvelope = {
  error: {
    code: AudioErrorCode | string;
    message: string;
    detail?: Record<string, unknown>;
  };
};

/** A rota de texto usa o corpo padrao do `HTTPException` do FastAPI. */
export type DetailErrorEnvelope = {
  detail: string;
};

/** Codigos previstos na tabela da Secao 8.7.6 de `docs/Projeto.md`. */
export const AUDIO_ERROR_CODES = [
  'AUDIO_MISSING',
  'AUDIO_FORMAT_UNSUPPORTED',
  'AUDIO_TOO_LONG',
  'AUDIO_TOO_LARGE',
  'NO_SPEECH_DETECTED',
  'UNAUTHENTICATED',
  'RATE_LIMITED',
  'STT_PROVIDER_ERROR',
  'STT_PROVIDER_UNAVAILABLE',
  'OUT_OF_SCOPE_FOR_PROFILE',
] as const;

export type AudioErrorCode = (typeof AUDIO_ERROR_CODES)[number];

/* -------------------------------------------------------------------------
 * Vocabulario de PLN  —  src/notebooks/artefatos/catalogo_intencoes.json
 * ---------------------------------------------------------------------- */

/** As quatro macrointencoes do catalogo, iguais ao CHECK de `intent_catalog`. */
export const MACRO_INTENTS = [
  'CONSULTA',
  'TRANSACAO',
  'ALERTA',
  'FORA_DE_ESCOPO',
] as const;

export type MacroIntent = (typeof MACRO_INTENTS)[number];

/** Valor que `app/nlp/inference.py` usa quando a macro fica abaixo do limiar. */
export const UNDEFINED_MACRO = 'INDEFINIDA';

/* -------------------------------------------------------------------------
 * GET /health  —  app/main.py
 * ---------------------------------------------------------------------- */

export type HealthResponse = {
  status: string;
};
