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
 *   /api/data-change-previews, /api/data-changes -> app/data_changes/schemas.py
 *   GET  /health     -> app/main.py
 *
 */

/* -------------------------------------------------------------------------
 * POST /api/chat  —  app/gemini/schemas.py
 * ---------------------------------------------------------------------- */

/** `GeminiChatRequest`. `message` tem min_length=1 e max_length=20000. */
export type ChatRequest = {
  message: string;
  include_audio?: boolean;
  conversation_id?: string | null;
  use_intent_classifier?: boolean;
  proactivity_enabled?: boolean;
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
  citation_id?: string | null;
  artifact_id?: string | null;
  extract_id?: string | null;
  project_id?: string | null;
  source_locator?: string | null;
  registration_period?: { start?: string | null; end?: string | null } | null;
  validity?: { start?: string | null; end?: string | null } | null;
  attributes?: Record<string, string>;
};

export type ClaimEvidence = {
  citation_id: string;
  field: 'excerpt' | 'attribute';
  attribute: string | null;
  quote: string;
};
export type FactualClaim = {
  text: string;
  citation_ids: string[];
  evidence?: ClaimEvidence[];
};
export type EvidenceStatus = 'referenced' | 'insufficient' | 'not_applicable';

export type ProactiveSuggestion = {
  suggestion_id: string;
  intent: string;
  description: string;
  display_message: string;
  requires_confirmation: boolean;
};

export type ProactiveDecision = 'accept' | 'decline';

export type ProactiveConfirmationRequest = {
  suggestion_id: string;
  conversation_id: string;
  decision: ProactiveDecision;
};

export type ProactiveConfirmationResponse = {
  status: 'accepted' | 'declined';
  result?: ChatResponse | null;
};

/** `GeminiChatResponse`. */
export type ChatResponse = {
  contract_version?: '1.1.0';
  trace_id?: string | null;
  intent?: AudioIntent | null;
  entities?: PipelineEntity[];
  pipeline_metrics?: ChatPipelineMetrics;
  text: string;
  speech?: SpeechResponse | null;
  model: string;
  interaction_id: string | null;
  latency_ms: number;
  retrieval_ms: number;
  usage: ChatUsage;
  sources: ChatSource[];
  claims?: FactualClaim[];
  evidence_status?: EvidenceStatus;
  /** Presente so na resposta secundaria confirmada: analise rotulada, nao fato. */
  recommendation?: string | null;
  proactive_suggestion?: ProactiveSuggestion | null;
  workflow?: WorkflowDirective | null;
  /** Alteracao de dados pelo chat (S5-06): previa, pergunta ou recusa. */
  data_change?: DataChangeOutcome | null;
};

export type SpeechResponse = {
  status: 'available' | 'unavailable';
  media_type: 'audio/mpeg' | null;
  data_base64: string | null;
  warning: string | null;
};

/* -------------------------------------------------------------------------
 * Alteracao de dados pelo chat  —  app/data_changes/schemas.py
 * Contrato: docs/Projeto.md, Secao 8.5.13 (S5-05).
 * ---------------------------------------------------------------------- */

export type DataChangeEntity = 'projeto' | 'cronograma' | 'marco' | 'risco';

/** `FieldRef`: chave do contrato (`projeto.prazo_final`) e rotulo exibivel. */
export type DataChangeField = { key: string; label: string };

/** `ValueView`: valor canonico (para comparar) e exibido (para a pessoa). */
export type DataChangeValue = { value: string | null; display: string };

export type DataChangeTarget = { entity: DataChangeEntity; id: string; label: string };

/** `DataChangePreview`. Nada foi gravado quando a previa existe. */
export type DataChangePreview = {
  pending_change_id: string;
  project: { code: string; title: string };
  target: DataChangeTarget;
  field: DataChangeField;
  before: DataChangeValue;
  after: DataChangeValue;
  warnings: string[];
  expires_at: string;
  undo_window_minutes: number;
};

/** `DataChangeDraft`: o que ja foi entendido do pedido. */
export type DataChangeDraft = {
  project_code?: string | null;
  entity?: DataChangeEntity | null;
  field?: string | null;
  target_id?: string | null;
  item_reference?: string | null;
  raw_value?: string | null;
};

/** `DataChangeOutcome`: campo `data_change` da resposta do chat. */
export type DataChangeOutcome = {
  status: 'preview' | 'needs_input' | 'rejected';
  preview?: DataChangePreview | null;
  missing?: 'project' | 'target' | 'field' | 'value' | null;
  question?: string | null;
  candidates?: { id: string; label: string }[];
  draft?: DataChangeDraft | null;
  code?: string | null;
  message?: string | null;
};

/** `PreviewRequest`: completa a proposta escolhida no cartao. */
export type DataChangePreviewRequest = {
  project_code: string;
  entity?: DataChangeEntity | null;
  field: string;
  target_id?: string | null;
  item_reference?: string | null;
  raw_value?: string | null;
  conversation_id?: string | null;
};

/** `ConfirmResponse`. */
export type DataChangeConfirmResponse = {
  change_id: string;
  status: 'aplicada';
  field: DataChangeField;
  target: DataChangeTarget;
  before: DataChangeValue;
  after: DataChangeValue;
  applied_at: string;
  undo_available_until: string;
  correlation_id: string;
};

/** `UndoResponse`. */
export type DataChangeUndoResponse = {
  change_id: string;
  status: 'desfeita';
  restored: DataChangeValue;
  undone_at: string;
};

/** `HistoryItem`. */
export type DataChangeHistoryItem = {
  change_id: string;
  field: DataChangeField;
  target: DataChangeTarget;
  before: DataChangeValue;
  after: DataChangeValue;
  requested_by: string;
  applied_at: string;
  status: 'aplicada' | 'desfeita';
  undone_at?: string | null;
  can_undo: boolean;
  undo_available_until?: string | null;
};

export type DataChangeHistoryResponse = { items: DataChangeHistoryItem[] };

export type WorkflowDirective = {
  kind: 'guided_workflow';
  action: 'start';
  workflow: 'transacao_gerar_relatorio' | 'alerta_prazo_atraso';
  contract_version: string;
  parameters: Record<string, unknown>;
};

export type WorkflowStep =
  | 'scope_type'
  | 'scope'
  | 'period'
  | 'audience'
  | 'purpose'
  | 'emphasis'
  | 'additional_context'
  | 'confirmation'
  | 'execution';

export type WorkflowOption = {
  value: string;
  label: string;
  description?: string | null;
};

export type WorkflowQuestion = {
  step: WorkflowStep;
  prompt: string;
  input_type: 'single_select' | 'multi_select' | 'date_range' | 'text';
  required: boolean;
  options: WorkflowOption[];
};

export type ReportArtifact = {
  artifact_id: string;
  file_name: string;
  content_type: string;
  size_bytes: number;
  sha256: string;
  download_url: string;
  storage_provider: 'local' | 'supabase';
  created_at: string;
};

export type ReportExecution = {
  contract_version: string;
  execution_id: string;
  correlation_id: string;
  status:
    | 'queued'
    | 'processing'
    | 'completed'
    | 'completed_with_warnings'
    | 'failed'
    | 'blocked'
    | 'cancelled';
  status_url: string;
  artifact?: ReportArtifact | null;
  warnings: string[];
  error?: { code: string; message: string } | null;
  created_at: string;
  updated_at: string;
};

export type WorkflowSessionResponse = {
  contract_version: string;
  session_id: string;
  workflow: 'transacao_gerar_relatorio';
  status: 'active' | 'ready_for_confirmation' | 'executing' | 'completed' | 'cancelled';
  current_step: WorkflowStep;
  revision: number;
  question?: WorkflowQuestion | null;
  answers: Record<string, unknown>;
  confirmation_summary?: string | null;
  warnings: string[];
  execution?: ReportExecution | null;
};

export type AlertWorkflowStep =
  'project' | 'threshold' | 'schedule' | 'resend' | 'confirmation' | 'completed';

export type AlertRule = {
  project_id: string;
  project_label: string;
  threshold_days: number;
  comparison_operator: 'gt' | 'gte';
  day_basis: 'calendar_days' | 'business_days';
  trigger_type: 'daily' | 'weekly';
  evaluation_time: string;
  weekday?: number | null;
  timezone: string;
  resend_interval_days?: number | null;
};

export type AlertSubscription = {
  subscription_id: string;
  correlation_id: string;
  idempotency_key: string;
  owner_subject: string;
  rule: AlertRule;
  status: 'active' | 'paused' | 'cancelled' | 'blocked';
  revision: number;
  next_evaluation_at: string;
  created_at: string;
  updated_at: string;
};

export type AlertSubscriptionResponse = {
  contract_version: string;
  subscription: AlertSubscription;
};

export type AlertWorkflowResponse = {
  contract_version: string;
  session_id: string;
  workflow: 'alerta_prazo_atraso';
  status: 'active' | 'ready_for_confirmation' | 'completed' | 'cancelled';
  current_step: AlertWorkflowStep;
  revision: number;
  question?: {
    step: AlertWorkflowStep;
    prompt: string;
    input_type: 'single_select' | 'number';
    options: WorkflowOption[];
  } | null;
  answers: Record<string, unknown>;
  confirmation_summary?: string | null;
  warnings: string[];
  subscription?: AlertSubscription | null;
};

export type GuidedWorkflowSession = WorkflowSessionResponse | AlertWorkflowResponse;

export type AlertNotification = {
  notification_id: string;
  correlation_id: string;
  subscription_id: string;
  occurrence_id: string;
  recipient_subject: string;
  project_id: string;
  item_id: string;
  title: string;
  body: string;
  reference_date: string;
  overdue_days: number;
  status: 'pending' | 'available' | 'read' | 'failed';
  created_at: string;
  read_at?: string | null;
};

export type NotificationListResponse = {
  items: AlertNotification[];
  unread_count: number;
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
  flow?: string;
  handler?: string;
  alternatives?: IntentAlternative[];
};

export type IntentAlternative = {
  intent: string;
  confidence: number;
};

export type PipelineEntity = {
  type: string;
  value: string;
  text: string;
  start: number;
  end: number;
  types: string[];
  ambiguous: boolean;
};

export type ChatPipelineMetrics = {
  nlp_ms: number;
  route_ms: number;
};

export type AudioPipelineMetrics = ChatPipelineMetrics & {
  validation_ms: number;
  stt_ms: number;
  total_ms: number;
};

/** Referencia completa com aliases legados; Partial aceita respostas anteriores ao contrato 1.1.0. */
export type AudioAnswerSource = Partial<ChatSource> & {
  artifact: string;
  section: string;
};

/** `AudioAnswer`. */
export type AudioAnswer = {
  text: string;
  sources: AudioAnswerSource[];
  claims?: FactualClaim[];
  evidence_status?: EvidenceStatus;
};

/** `AudioUploadResponse`. */
export type AudioUploadResponse = {
  contract_version?: '1.1.0';
  trace_id?: string | null;
  chat?: ChatResponse | null;
  conversation_id: string;
  interaction_id: string | null;
  transcription: AudioTranscription;
  intent: AudioIntent | null;
  entities?: PipelineEntity[];
  answer: AudioAnswer;
  /** Uma resposta utilizável exige pipeline concluído. */
  pipeline_status: string;
  pipeline_metrics?: AudioPipelineMetrics;
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
