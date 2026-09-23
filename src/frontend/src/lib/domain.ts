/**
 * Tipos de dominio da interface.
 *
 * Os schemas de `lib/api/schemas.ts` seguem o backend ao pe da letra, com
 * `snake_case` e campos opcionais como a API os entrega. Os tipos deste arquivo
 * sao os que os componentes consomem, em `camelCase` e ja resolvidos.
 *
 * As funcoes no fim do arquivo sao a fronteira entre os dois mundos: sao o
 * unico ponto que precisa mudar se o formato da API mudar, e o unico ponto que
 * precisa existir quando o mock for trocado pela API de verdade.
 */

import { INTENT_MACRO_THRESHOLD, INTENT_SPECIFIC_THRESHOLD } from './api/constants';
import {
  UNDEFINED_MACRO,
  type AudioIntent,
  type ChatPipelineMetrics,
  type ChatResponse,
  type ChatSource,
  type MacroIntent,
  type PipelineEntity,
  type ProactiveSuggestion,
  type WorkflowSessionResponse,
} from './api/schemas';

/* -------------------------------------------------------------------------
 * Documento recuperado pelo RAG
 * ---------------------------------------------------------------------- */

export type RetrievedDocument = {
  /** `<lista>:<item>`, por exemplo `base-atendimento:301`. */
  id: string;
  title: string;
  /** Nome de exibicao da lista do SharePoint de origem. */
  listName: string;
  webUrl: string;
  lastModified: string;
  /** Score bruto do recuperador — nao normalizado. Ver `ChatSource`. */
  score: number;
  /** Posicao na citacao `[Fonte N]` montada por `build_rag_input`. */
  citationOrder: number;
  /** Trecho do documento. Indefinido enquanto o backend nao devolver o campo. */
  excerpt?: string;
};

/* -------------------------------------------------------------------------
 * Resultado do classificador de intencoes
 * ---------------------------------------------------------------------- */

export type IntentAlternative = {
  intent: string;
  confidence: number;
};

export type IntentResult = {
  macro: MacroIntent | typeof UNDEFINED_MACRO | string;
  macroConfidence: number;
  /** `null` quando a confianca ficou abaixo do limiar da intencao. */
  specific: string | null;
  specificConfidence: number;
  /** `handler:<intencao>`, `fluxo generico de <macro>` ou `limitacao`. */
  handler: string;
  /** Descricao do fluxo, vinda do `catalogo_intencoes.json`. */
  flow: string;
  alternatives: IntentAlternative[];
};

export type ExtractedEntity = {
  type: string;
  value: string;
  text: string;
  start: number;
  end: number;
  types: string[];
  ambiguous: boolean;
};

/** A macrointencao passou do limiar e a solicitacao segue no pipeline. */
export function isRouted(intent: IntentResult): boolean {
  return intent.macro !== UNDEFINED_MACRO;
}

/** A intencao passou do limiar e um handler dedicado pode ser acionado. */
export function hasSpecificHandler(intent: IntentResult): boolean {
  return intent.specific !== null;
}

/** Como a UI rotula o desfecho do roteamento. */
export type IntentOutcome = 'handler' | 'generic' | 'limitation' | 'out-of-scope';

export function intentOutcome(intent: IntentResult): IntentOutcome {
  if (!isRouted(intent)) return 'limitation';
  if (intent.macro === 'FORA_DE_ESCOPO') return 'out-of-scope';
  return hasSpecificHandler(intent) ? 'handler' : 'generic';
}

export const INTENT_THRESHOLDS = {
  macro: INTENT_MACRO_THRESHOLD,
  specific: INTENT_SPECIFIC_THRESHOLD,
} as const;

/* -------------------------------------------------------------------------
 * Metricas da resposta
 * ---------------------------------------------------------------------- */

export type ResponseMetrics = {
  model: string;
  /** Tempo da chamada ao provedor, medido pelo backend. */
  latencyMs: number;
  /** Tempo da recuperacao no RAG, medido pelo backend. */
  retrievalMs: number;
  /** Tempo total medido pelo navegador, incluindo rede. */
  roundTripMs: number;
  /** Tempo do nucleo de PLN medido pelo backend. */
  nlpMs?: number;
  /** Tempo de roteamento total medido em `process_message`. */
  routeMs?: number;
  /** Tempo de validacao local do audio, quando a entrada veio por voz. */
  validationMs?: number;
  /** Tempo de transcricao STT, quando a entrada veio por voz. */
  sttMs?: number;
  /** Tempo total do pipeline de audio no backend. */
  backendTotalMs?: number;
  inputTokens: number;
  outputTokens: number;
  thoughtTokens: number;
  totalTokens: number;
};

type PipelineMetricsEnvelope = ChatPipelineMetrics & {
  validation_ms?: number;
  stt_ms?: number;
  total_ms?: number;
};

/* -------------------------------------------------------------------------
 * Mensagens e conversas
 * ---------------------------------------------------------------------- */

export type MessageRole = 'user' | 'assistant';

/** Como a mensagem entrou: digitada ou transcrita de um audio. */
export type MessageOrigin = 'text' | 'audio';

export type MessageStatus = 'pending' | 'complete' | 'error';

export type TranscriptionInfo = {
  confidence: number;
  durationSeconds: number;
};

export type ProactiveSuggestionStatus =
  'pending' | 'accepting' | 'declining' | 'accepted' | 'declined';

export type ProactiveSuggestionState = {
  id: string;
  intent: string;
  description: string;
  displayMessage: string;
  requiresConfirmation: boolean;
  status: ProactiveSuggestionStatus;
};

export type ChatMessage = {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: string;
  origin: MessageOrigin;
  status: MessageStatus;
  /** Identificador devolvido pelo backend; encadeia o contexto no Gemini. */
  interactionId?: string | null;
  sources?: RetrievedDocument[];
  intent?: IntentResult;
  entities?: ExtractedEntity[];
  metrics?: ResponseMetrics;
  /** Preenchido quando a mensagem veio de audio. */
  transcription?: TranscriptionInfo;
  /** Mensagem de erro ja pronta para exibir, quando `status` e `error`. */
  error?: string;
  /** `true` quando o classificador estava ligado no envio. */
  intentLayerEnabled?: boolean;
  /** Sugestao separada da resposta principal e vinculada a uma decisao explicita. */
  proactiveSuggestion?: ProactiveSuggestionState;
  /** Estado do fluxo guiado iniciado por esta resposta. */
  workflow?: WorkflowSessionResponse;
};

export type ConversationStatus = 'ativa' | 'finalizada' | 'abandonada' | 'erro';

export type Conversation = {
  id: string;
  /** Derivado da primeira pergunta; `ai_conversations` nao tem coluna de titulo. */
  title: string;
  createdAt: string;
  updatedAt: string;
  status: ConversationStatus;
  channel: string;
  messages: ChatMessage[];
  /**
   * Ultimo `interaction_id` recebido nesta conversa. Volta como
   * `previous_interaction_id` na proxima mensagem, e e o que faz o Gemini
   * manter o contexto ao retomar uma conversa da barra lateral.
   */
  lastInteractionId: string | null;
};

/* -------------------------------------------------------------------------
 * Conversao entre schema e dominio
 * ---------------------------------------------------------------------- */

export function toRetrievedDocument(
  source: ChatSource,
  index: number,
): RetrievedDocument {
  return {
    id: source.id,
    title: source.title,
    listName: source.list_name,
    webUrl: source.web_url,
    lastModified: source.last_modified,
    score: source.score,
    citationOrder: index + 1,
    excerpt: source.excerpt ?? undefined,
  };
}

export function toExtractedEntity(entity: PipelineEntity): ExtractedEntity {
  return {
    type: entity.type,
    value: entity.value,
    text: entity.text,
    start: entity.start,
    end: entity.end,
    types: entity.types,
    ambiguous: entity.ambiguous,
  };
}

export function toProactiveSuggestion(
  suggestion: ProactiveSuggestion,
): ProactiveSuggestionState {
  return {
    id: suggestion.suggestion_id,
    intent: suggestion.intent,
    description: suggestion.description,
    displayMessage: suggestion.display_message,
    requiresConfirmation: suggestion.requires_confirmation,
    status: 'pending',
  };
}

export function toIntentResult(intent: AudioIntent, flow = ''): IntentResult {
  const routed = intent.confidence_macro >= INTENT_MACRO_THRESHOLD;
  const specific =
    routed &&
    intent.macro !== 'FORA_DE_ESCOPO' &&
    intent.confidence_specific >= INTENT_SPECIFIC_THRESHOLD
      ? intent.specific || null
      : null;

  return {
    macro: routed ? intent.macro : UNDEFINED_MACRO,
    macroConfidence: intent.confidence_macro,
    specific,
    specificConfidence: intent.confidence_specific,
    handler:
      intent.handler ||
      (specific
        ? `handler:${specific}`
        : routed
          ? `fluxo genérico de ${intent.macro}`
          : 'limitacao'),
    flow: intent.flow ?? flow,
    alternatives: intent.alternatives ?? [],
  };
}

/** Monta a mensagem do assistente a partir da resposta de `POST /api/chat`. */
export function toAssistantMessage(
  response: ChatResponse,
  options: {
    roundTripMs: number;
    intentLayerEnabled: boolean;
    pipelineMetrics?: PipelineMetricsEnvelope;
  },
): ChatMessage {
  const pipelineMetrics: PipelineMetricsEnvelope | undefined =
    options.pipelineMetrics ?? response.pipeline_metrics;
  return {
    id: crypto.randomUUID(),
    role: 'assistant',
    content: response.text,
    createdAt: new Date().toISOString(),
    origin: 'text',
    status: 'complete',
    interactionId: response.interaction_id,
    sources: response.sources.map(toRetrievedDocument),
    intent: response.intent ? toIntentResult(response.intent) : undefined,
    entities: (response.entities ?? []).map(toExtractedEntity),
    metrics: {
      model: response.model,
      latencyMs: response.latency_ms,
      retrievalMs: response.retrieval_ms,
      roundTripMs: options.roundTripMs,
      nlpMs: pipelineMetrics?.nlp_ms,
      routeMs: pipelineMetrics?.route_ms,
      validationMs: pipelineMetrics?.validation_ms,
      sttMs: pipelineMetrics?.stt_ms,
      backendTotalMs: pipelineMetrics?.total_ms,
      inputTokens: response.usage.input_tokens,
      outputTokens: response.usage.output_tokens,
      thoughtTokens: response.usage.thought_tokens,
      totalTokens: response.usage.total_tokens,
    },
    intentLayerEnabled: options.intentLayerEnabled,
    proactiveSuggestion: response.proactive_suggestion
      ? toProactiveSuggestion(response.proactive_suggestion)
      : undefined,
  };
}

/** Titulo da conversa a partir da primeira pergunta, como a barra lateral exibe. */
export function deriveConversationTitle(firstMessage: string): string {
  const clean = firstMessage.replace(/\s+/g, ' ').trim();
  if (!clean) return 'Nova conversa';
  return clean.length <= 52 ? clean : `${clean.slice(0, 52).trimEnd()}…`;
}
