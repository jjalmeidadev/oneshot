/**
 * Limites e parametros lidos do backend.
 *
 * Nenhum valor aqui e escolha do frontend: todos vem de um arquivo do backend,
 * citado ao lado. Quando o backend mudar, este arquivo muda junto — e o unico
 * lugar da interface que precisa ser tocado.
 */

/* --- Rota de audio: app/audio/validation.py + docs/Projeto.md Secao 8.7.3 --- */

/** `DEFAULT_MAX_SIZE_BYTES` = 2 * 1024 * 1024. */
export const AUDIO_MAX_SIZE_BYTES = 2 * 1024 * 1024;

/** `DEFAULT_MAX_DURATION_SECONDS`. A UI corta a gravacao ao atingir o limite. */
export const AUDIO_MAX_DURATION_SECONDS = 60;

/** `REQUIRED_SAMPLE_RATE_HZ` — exigencia estrita no ramo WAV. */
export const AUDIO_REQUIRED_SAMPLE_RATE_HZ = 16_000;

/** `REQUIRED_CHANNELS`. */
export const AUDIO_REQUIRED_CHANNELS = 1;

/** `REQUIRED_BITS_PER_SAMPLE`. */
export const AUDIO_REQUIRED_BITS_PER_SAMPLE = 16;

/**
 * Contineres aceitos pela validacao local, em ordem de preferencia para o
 * `MediaRecorder`.
 *
 * O ramo Opus aceita `input_sample_rate` 0, 16000 ou 48000 justamente porque o
 * `MediaRecorder` grava declarando 48 kHz (RFC 7845). O ramo WAV exige 16 kHz.
 *
 * O WebM capturado pelo Chrome é convertido para WAV antes do envio.
 */
export const AUDIO_ACCEPTED_MIME_TYPES = [
  'audio/ogg;codecs=opus',
  'audio/ogg',
  'audio/wav',
] as const;

/** `DEFAULT_LANGUAGE` de `app/main.py`. */
export const AUDIO_DEFAULT_LANGUAGE = 'pt-BR';

/** Uma transcricao por identidade — `single_request_per_identity`. */
export const AUDIO_MAX_CONCURRENT_PER_USER = 1;

/* --- Classificador de intencoes: artefato + app/nlp/inference.py --- */

/**
 * Limiares calibrados na validacao (Secao 8.10.3) e gravados no artefato como
 * `limiar_macro` e `limiar_intencao`. Sao os mesmos defaults das colunas
 * `macro_confidence_threshold` e `intent_confidence_threshold` de
 * `intent_catalog`.
 */
export const INTENT_MACRO_THRESHOLD = 0.55;
export const INTENT_SPECIFIC_THRESHOLD = 0.7;

/** Numero de intencoes especificas do catalogo. */
export const INTENT_CATALOG_SIZE = 31;

/** Resposta controlada do RF08, em `app/nlp/inference.LIMITATION_ANSWER`. */
export const INTENT_LIMITATION_ANSWER =
  'Não consegui identificar com segurança o que você precisa dentro do ' +
  'portfólio ou nos temas da base. Pode reformular indicando o tema e a ' +
  "informação desejada? Por exemplo: 'Como funciona o Bilhete digital?' " +
  "ou 'Qual é o status do projeto PRJ-0442?'";

/* --- Rota de texto: app/gemini/schemas.py --- */

/** `max_length` de `GeminiChatRequest.message`. */
export const CHAT_MESSAGE_MAX_LENGTH = 20_000;

/** Orcamento de latencia ponta a ponta do RNF05, usado nos indicadores da UI. */
export const RESPONSE_BUDGET_MS = 10_000;

/* --- Canal --- */

/**
 * Valor de `ai_conversations.channel` para esta interface. O CHECK da tabela
 * aceita 'teams', 'webchat', 'copilot_studio', 'api' e 'teste'.
 */
export const CONVERSATION_CHANNEL = 'webchat';
