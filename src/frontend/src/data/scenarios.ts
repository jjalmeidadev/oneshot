/**
 * Alternador de estados da interface.
 *
 * ESTE ARQUIVO E DESCARTAVEL, junto de `components/dev/scenario-switcher.tsx`.
 * Serve para revisar visualmente os estados que so aparecem em condicoes
 * especificas do backend, sem precisar provoca-las de verdade.
 *
 * A transformacao acontece num unico ponto (`applyScenario`), aplicada sobre o
 * estado da store na hora de renderizar. Nenhum componente sabe que cenarios
 * existem: todos recebem `Conversation`, `status` e `error` normais.
 */

import type { ChatMessage, Conversation } from '@/lib/domain';
import { INTENT_LIMITATION_ANSWER } from '@/lib/api/constants';

export type ScenarioId =
  | 'default'
  | 'loading'
  | 'error'
  | 'no-sources'
  | 'source-excerpt'
  | 'low-confidence'
  | 'empty';

export type ChatStatus = 'idle' | 'sending' | 'error';

export const SCENARIOS: {
  id: ScenarioId;
  label: string;
  description: string;
}[] = [
  {
    id: 'default',
    label: 'Padrão',
    description:
      'Conversas de exemplo com fontes recuperadas, exatamente no formato que /api/chat devolve hoje.',
  },
  {
    id: 'loading',
    label: 'Aguardando resposta',
    description:
      'Pergunta enviada e resposta em andamento. Exercita o indicador de digitação e o botão de interromper.',
  },
  {
    id: 'error',
    label: 'Erro do backend',
    description:
      'Resposta 503 de GeminiConfigurationError, quando GEMINI_API_KEY não está configurada.',
  },
  {
    id: 'no-sources',
    label: 'Sem fontes',
    description:
      'O recuperador não casou nenhum documento e sources volta vazio. O painel de documentos mostra o estado vazio.',
  },
  {
    id: 'source-excerpt',
    label: 'Fontes com trecho',
    description:
      'Como o painel ficaria se GeminiSource passasse a incluir o conteúdo do documento. Hoje o campo não vem — ver README, lacuna 1.',
  },
  {
    id: 'low-confidence',
    label: 'Confiança abaixo do limiar',
    description:
      'Macrointenção abaixo de 0,55: o classificador barra a solicitação antes do LLM e devolve a resposta de limitação do RF08.',
  },
  {
    id: 'empty',
    label: 'Sem histórico',
    description: 'Primeiro acesso do usuário: nenhuma conversa salva.',
  },
];

export type ScenarioResult = {
  conversations: Conversation[];
  activeConversationId: string | null;
  status: ChatStatus;
  error: string | null;
};

export function applyScenario(
  scenario: ScenarioId,
  base: ScenarioResult,
): ScenarioResult {
  if (scenario === 'default') {
    return base;
  }

  if (scenario === 'empty') {
    return {
      conversations: [],
      activeConversationId: null,
      status: 'idle',
      error: null,
    };
  }

  const active = base.conversations.find((c) => c.id === base.activeConversationId);
  if (!active) {
    return base;
  }

  const replace = (messages: ChatMessage[]): ScenarioResult => ({
    ...base,
    conversations: base.conversations.map((conversation) =>
      conversation.id === active.id ? { ...conversation, messages } : conversation,
    ),
  });

  const withoutLastAssistant = active.messages.filter(
    (message, index) =>
      !(message.role === 'assistant' && index === active.messages.length - 1),
  );

  switch (scenario) {
    case 'loading':
      return { ...replace(withoutLastAssistant), status: 'sending' };

    case 'error':
      return {
        ...replace([
          ...withoutLastAssistant,
          {
            id: 'scenario-error',
            role: 'assistant',
            content: '',
            createdAt: new Date().toISOString(),
            origin: 'text',
            status: 'error',
            error: 'A chave GEMINI_API_KEY nao foi configurada no backend.',
          },
        ]),
        status: 'error',
        error: 'A chave GEMINI_API_KEY nao foi configurada no backend.',
      };

    case 'no-sources':
      return replace(
        active.messages.map((message) =>
          message.role === 'assistant' ? { ...message, sources: [] } : message,
        ),
      );

    case 'source-excerpt':
      // O caso inverso e o padrao: o mock guarda o trecho e a store o remove
      // para refletir o contrato atual. Aqui ele volta.
      return replace(active.messages);

    case 'low-confidence':
      return replace([
        ...withoutLastAssistant,
        {
          id: 'scenario-low-confidence',
          role: 'assistant',
          content: INTENT_LIMITATION_ANSWER,
          createdAt: new Date().toISOString(),
          origin: 'text',
          status: 'complete',
          sources: [],
          intentLayerEnabled: true,
          intent: {
            macro: 'INDEFINIDA',
            macroConfidence: 0.4127,
            specific: null,
            specificConfidence: 0.2984,
            handler: 'limitacao',
            flow: 'Resposta padrão de limitação (RF08)',
            alternatives: [
              { intent: 'consulta_visao_portfolio', confidence: 0.2984 },
              { intent: 'consulta_indicadores_kpi', confidence: 0.2211 },
              { intent: 'comparacao_entre_projetos', confidence: 0.1502 },
            ],
          },
        },
      ]);

    default:
      return base;
  }
}

/**
 * Remove o trecho das fontes, para o padrao refletir o contrato atual de
 * `GeminiSource`. O cenario "Fontes com trecho" pula esta etapa.
 */
export function stripExcerpts(conversations: Conversation[]): Conversation[] {
  return conversations.map((conversation) => ({
    ...conversation,
    messages: conversation.messages.map((message) =>
      message.sources
        ? {
            ...message,
            sources: message.sources.map((source) => ({
              id: source.id,
              title: source.title,
              listName: source.listName,
              webUrl: source.webUrl,
              lastModified: source.lastModified,
              score: source.score,
              citationOrder: source.citationOrder,
            })),
          }
        : message,
    ),
  }));
}
