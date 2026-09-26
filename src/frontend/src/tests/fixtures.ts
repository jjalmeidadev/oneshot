import type { ChatResponse } from '@/lib/api/schemas';
export const response: ChatResponse = {
  text: 'O projeto está em andamento. [Fonte 1]',
  model: 'teste',
  interaction_id: 'interaction-1',
  latency_ms: 5,
  retrieval_ms: 2,
  usage: { input_tokens: 10, output_tokens: 5, thought_tokens: 0, total_tokens: 15 },
  sources: [
    {
      id: 'projetos:1',
      title: 'Projeto Linha Verde',
      list_name: 'Projetos',
      web_url: 'https://example.org/projeto',
      last_modified: '2026-09-09T12:00:00Z',
      score: 1.5,
      excerpt: 'Entrega prevista para dezembro.',
    },
  ],
  intent: {
    macro: 'CONSULTA',
    specific: 'consulta_status_projeto',
    confidence_macro: 0.9,
    confidence_specific: 0.85,
    flow: 'Consulta documental',
    handler: 'handler:consulta_status_projeto',
    alternatives: [{ intent: 'consulta_status_projeto', confidence: 0.85 }],
  },
  entities: [
    {
      type: 'projeto',
      value: 'Projeto Linha Verde',
      text: 'Projeto Linha Verde',
      start: 0,
      end: 19,
      types: ['projeto'],
      ambiguous: false,
    },
  ],
  pipeline_metrics: { nlp_ms: 3, route_ms: 2 },
  proactive_suggestion: {
    suggestion_id: '00000000-0000-0000-0000-000000000250',
    intent: 'sugerir_agilizacao_projeto',
    description: 'Identificar o principal gargalo documentado.',
    display_message: 'Quer que eu sugira uma forma de agilizar o projeto?',
    requires_confirmation: true,
  },
};
