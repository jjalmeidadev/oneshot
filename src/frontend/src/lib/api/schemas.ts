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
 * O que **ainda nao existe** e esta marcado como proposto:
 *   GET/POST/DELETE /api/conversations (ver `conversations.ts`)
 */

/* -------------------------------------------------------------------------
 * POST /api/chat  —  app/gemini/schemas.py
 * ---------------------------------------------------------------------- */

/** `GeminiChatRequest`. `message` tem min_length=1 e max_length=20000. */
export type ChatRequest = {
  message: string;
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
 * `excerpt` NAO e devolvido pelo backend hoje. O texto existe do lado de la em
 * `RetrievedDocument.document.content`, mas e descartado na montagem da
 * resposta. O painel de documentos exibe o trecho quando o campo aparecer e
 * mostra o estado de ausencia enquanto isso — ver `documents/document-viewer.tsx`
 * e a secao "Lacunas" do README.
 */
export type ChatSource = {
  id: string;
  title: string;
  list_name: string;
  web_url: string;
  /** ISO 8601, vindo de `lastModifiedDateTime` da lista do SharePoint. */
  last_modified: string;
  score: number;
  excerpt?: string;
};

/** `GeminiChatResponse`. */
export type ChatResponse = {
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
 * E o mesmo formato que `app/nlp/inference.Classificacao` produz. Enquanto
 * `pipeline_status` for `"stubbed"`, o backend preenche este bloco com
 * `FORA_DE_ESCOPO` / `pipeline_nao_implementado` e confiancas zeradas.
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
  conversation_id: string;
  interaction_id: string;
  transcription: AudioTranscription;
  intent: AudioIntent;
  answer: AudioAnswer;
  /** `"stubbed"` ate o pipeline de PLN ser ligado a rota; depois `"completed"`. */
  pipeline_status: 'stubbed' | 'completed' | string;
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
