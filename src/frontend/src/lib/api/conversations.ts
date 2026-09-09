/**
 * Historico de conversas — CONTRATO PROPOSTO, AINDA NAO IMPLEMENTADO.
 *
 * O backend nao expoe nenhuma rota de conversas hoje. A modelagem, porem, ja
 * existe em `src/database/sql/01_create_database.sql`:
 *
 *   ai_conversations  (id, user_id, channel, started_at, ended_at,
 *                      conversation_status, external_conversation_id, metadata)
 *   ai_interactions   (id, conversation_id, user_prompt, response_text,
 *                      macro_intent_predicted, macro_intent_confidence,
 *                      specific_intent_predicted, specific_intent_confidence,
 *                      handler_selected, route_taken, top_k_alternatives,
 *                      limitation_response, processing_status, processing_ms)
 *   consulted_sources (id, interaction_id, source_type, source_title,
 *                      source_url, source_locator, relevance_score,
 *                      citation_order)
 *
 * Os tipos abaixo derivam dessas tabelas, com os mesmos nomes de coluna, para
 * que a rota possa ser escrita sem renomear nada. Enquanto ela nao existe, a
 * barra lateral trabalha com a store em memoria e os dados de `src/data/mock.ts`.
 *
 * As funcoes lancam de proposito: nenhuma tela chama nenhuma delas. Ligar o
 * historico e trocar essas implementacoes por `requestJson` e apagar a
 * hidratacao do mock em `state/chat-store.tsx` — ver README, "Ponto de
 * integracao 4".
 */

import type { MacroIntent } from './schemas';

/** Linha de `ai_conversations`, no recorte que a barra lateral precisa. */
export type ConversationSummary = {
  id: string;
  /** Derivado do primeiro `user_prompt`; nao ha coluna de titulo na tabela. */
  title: string;
  channel: string;
  started_at: string;
  ended_at: string | null;
  conversation_status: 'ativa' | 'finalizada' | 'abandonada' | 'erro';
  interaction_count: number;
  /** Ultimo `ai_interactions.id`, para retomar o encadeamento no Gemini. */
  last_interaction_id: string | null;
};

/** Linha de `ai_interactions` com as fontes de `consulted_sources`. */
export type StoredInteraction = {
  id: string;
  conversation_id: string;
  user_prompt: string;
  response_text: string | null;
  limitation_response: string | null;
  macro_intent_predicted: MacroIntent | null;
  macro_intent_confidence: number | null;
  specific_intent_predicted: string | null;
  specific_intent_confidence: number | null;
  handler_selected: string | null;
  route_taken: string;
  processing_status: string;
  processing_ms: number | null;
  created_at: string;
  consulted_sources: StoredConsultedSource[];
};

/** Linha de `consulted_sources`. */
export type StoredConsultedSource = {
  id: string;
  source_type: string;
  source_title: string | null;
  source_url: string | null;
  source_locator: string | null;
  relevance_score: number | null;
  citation_order: number;
};

const NOT_IMPLEMENTED =
  'O backend ainda não expõe rotas de conversas. Ver src/lib/api/conversations.ts.';

/** `GET /api/conversations` — proposto. */
export async function listConversations(): Promise<ConversationSummary[]> {
  throw new Error(NOT_IMPLEMENTED);
}

/** `GET /api/conversations/{id}/interactions` — proposto. */
export async function loadConversation(): Promise<StoredInteraction[]> {
  throw new Error(NOT_IMPLEMENTED);
}

/** `DELETE /api/conversations/{id}` — proposto. */
export async function deleteConversation(): Promise<void> {
  throw new Error(NOT_IMPLEMENTED);
}
