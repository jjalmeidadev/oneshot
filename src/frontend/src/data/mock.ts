/**
 * Dados ficticios para revisar a interface sem backend.
 *
 * ESTE ARQUIVO E DESCARTAVEL. Ao ligar a API, apague-o junto da chamada a
 * `hydrateFromMock` em `state/chat-store.tsx` — nenhum componente importa daqui.
 *
 * Os documentos abaixo sao os mesmos que o RAG indexa em
 * `src/backend/app/rag/data/sharepoint/*.json`: mesmos `id`, `webUrl`,
 * `lastModifiedDateTime` e conteudo. Assim o painel de documentos mostra
 * exatamente o que a rota `/api/chat` devolveria com o backend no ar.
 *
 * O `score` acompanha a formula de `retrieve_sharepoint_context`
 * (tokens casados + 2x casados no titulo + cobertura), que **nao** e
 * normalizada entre 0 e 1 — a interface nunca a exibe como porcentagem.
 */

import {
  deriveConversationTitle,
  type ChatMessage,
  type Conversation,
  type RetrievedDocument,
} from '@/lib/domain';

/** Identidade que o canal entregaria via Microsoft Entra ID (Secao 6.2.4). */
export const MOCK_USER = {
  displayName: 'Felipe Neves',
  email: 'felipe.neves@exemplo.metro.sp',
  roleName: 'pmo',
  department: 'Gestão de Portfólio',
} as const;

function hoursAgo(hours: number): string {
  return new Date(Date.now() - hours * 3_600_000).toISOString();
}

function daysAgo(days: number, hour = 10): string {
  const date = new Date(Date.now() - days * 86_400_000);
  date.setHours(hour, 15, 0, 0);
  return date.toISOString();
}

/* -------------------------------------------------------------------------
 * Documentos das listas simuladas do SharePoint
 * ---------------------------------------------------------------------- */

export const MOCK_DOCUMENTS: Record<string, RetrievedDocument> = {
  'procedimentos-operacionais:101': {
    id: 'procedimentos-operacionais:101',
    title: 'Atendimento a objeto perdido',
    listName: 'Procedimentos Operacionais',
    webUrl: 'https://mock.sharepoint.local/sites/metro-mvp/Lists/Procedimentos/101',
    lastModified: '2026-07-18T14:30:00Z',
    score: 6.667,
    citationOrder: 1,
    excerpt:
      'Registrar a descricao do objeto, local e horario informados pelo passageiro. ' +
      'Consultar o registro local de achados e perdidos e fornecer o protocolo ficticio. ' +
      'Objetos nao localizados no dia seguem para conferencia posterior.',
  },
  'procedimentos-operacionais:103': {
    id: 'procedimentos-operacionais:103',
    title: 'Comunicacao de indisponibilidade de escada rolante',
    listName: 'Procedimentos Operacionais',
    webUrl: 'https://mock.sharepoint.local/sites/metro-mvp/Lists/Procedimentos/103',
    lastModified: '2026-08-02T16:45:00Z',
    score: 3.333,
    citationOrder: 2,
    excerpt:
      'Sinalizar o equipamento como indisponivel, indicar a alternativa acessivel mais ' +
      'proxima e abrir um chamado de manutencao. Atualizar o comunicado ao passageiro ' +
      'quando o status do chamado mudar.',
  },
  'base-atendimento:303': {
    id: 'base-atendimento:303',
    title: 'Transporte de bicicleta',
    listName: 'Base de Atendimento',
    webUrl: 'https://mock.sharepoint.local/sites/metro-mvp/Lists/Atendimento/303',
    lastModified: '2026-08-12T11:05:00Z',
    score: 8.5,
    citationOrder: 1,
    excerpt:
      'Na politica ficticia do MVP, bicicletas sao aceitas aos sabados, domingos e ' +
      'feriados durante toda a operacao, e nos dias uteis apos as 20h30. O passageiro ' +
      'deve usar o ultimo carro e respeitar a capacidade indicada pela equipe.',
  },
  'comunicados-servico:202': {
    id: 'comunicados-servico:202',
    title: 'Acesso alternativo na Estacao Republica',
    listName: 'Comunicados de Servico',
    webUrl: 'https://mock.sharepoint.local/sites/metro-mvp/Lists/Comunicados/202',
    lastModified: '2026-08-10T09:25:00Z',
    score: 5.25,
    citationOrder: 1,
    excerpt:
      'Um dos acessos ficticios da Estacao Republica estara fechado para manutencao. ' +
      'Passageiros devem utilizar o acesso da Rua do Arouche, conforme sinalizacao ' +
      'temporaria no local.',
  },
  'comunicados-servico:201': {
    id: 'comunicados-servico:201',
    title: 'Operacao assistida na Linha Azul',
    listName: 'Comunicados de Servico',
    webUrl: 'https://mock.sharepoint.local/sites/metro-mvp/Lists/Comunicados/201',
    lastModified: '2026-08-01T12:00:00Z',
    score: 2.75,
    citationOrder: 2,
    excerpt:
      'Durante o periodo ficticio, o intervalo entre trens podera ser ampliado entre ' +
      '22h e o encerramento da operacao para testes de sinalizacao.',
  },
};

function docs(...ids: string[]): RetrievedDocument[] {
  return ids.map((id, index) => ({
    ...MOCK_DOCUMENTS[id],
    citationOrder: index + 1,
  }));
}

/* -------------------------------------------------------------------------
 * Conversas
 * ---------------------------------------------------------------------- */

function userMessage(
  content: string,
  createdAt: string,
  origin: ChatMessage['origin'] = 'text',
  transcription?: ChatMessage['transcription'],
): ChatMessage {
  return {
    id: crypto.randomUUID(),
    role: 'user',
    content,
    createdAt,
    origin,
    status: 'complete',
    transcription,
  };
}

const CURRENT: Conversation = {
  id: 'c1f4b6b2-0f2a-4c0e-9a5e-1d4b0b3f7a01',
  title: deriveConversationTitle('Qual é o procedimento para objeto perdido?'),
  createdAt: hoursAgo(2),
  updatedAt: hoursAgo(2),
  status: 'ativa',
  channel: 'webchat',
  lastInteractionId: 'interactions/mock-0031',
  messages: [
    userMessage('Qual é o procedimento para objeto perdido?', hoursAgo(2)),
    {
      id: crypto.randomUUID(),
      role: 'assistant',
      content:
        'Segundo o procedimento vigente, o atendimento a objeto perdido segue três passos ' +
        '[Fonte 1]:\n\n' +
        '1. **Registrar** a descrição do objeto, o local e o horário informados pelo passageiro.\n' +
        '2. **Consultar** o registro local de achados e perdidos.\n' +
        '3. **Fornecer o protocolo** ao passageiro.\n\n' +
        'Objetos não localizados no mesmo dia seguem para conferência posterior. Quando o ' +
        'atendimento envolver deslocamento por equipamento indisponível, o comunicado ao ' +
        'passageiro deve ser atualizado a cada mudança de status do chamado [Fonte 2].\n\n' +
        '_Os trechos acima vêm de listas simuladas do SharePoint e são dados fictícios do MVP._',
      createdAt: hoursAgo(2),
      origin: 'text',
      status: 'complete',
      interactionId: 'interactions/mock-0031',
      sources: docs('procedimentos-operacionais:101', 'procedimentos-operacionais:103'),
      intent: {
        macro: 'CONSULTA',
        macroConfidence: 0.9127,
        specific: 'consulta_documentos_fonte',
        specificConfidence: 0.8214,
        handler: 'handler:consulta_documentos_fonte',
        flow: 'RecuperadorInformacao -> Estruturador de Resposta',
        alternatives: [
          { intent: 'consulta_documentos_fonte', confidence: 0.8214 },
          { intent: 'consulta_pendencias_projeto', confidence: 0.0712 },
          { intent: 'consulta_status_projeto', confidence: 0.0364 },
        ],
      },
      metrics: {
        model: 'gemini-3.7-flash',
        latencyMs: 2140,
        retrievalMs: 12,
        roundTripMs: 2318,
        inputTokens: 861,
        outputTokens: 214,
        thoughtTokens: 96,
        totalTokens: 1171,
      },
      intentLayerEnabled: true,
    },
  ],
};

const BICYCLE: Conversation = {
  id: 'a2d7c110-8b21-4f3d-9c77-6e5a0f2b1c02',
  title: deriveConversationTitle('Posso levar bicicleta no metrô em dia útil?'),
  createdAt: hoursAgo(26),
  updatedAt: hoursAgo(25),
  status: 'finalizada',
  channel: 'webchat',
  lastInteractionId: 'interactions/mock-0028',
  messages: [
    userMessage('Posso levar bicicleta no metrô em dia útil?', hoursAgo(26), 'audio', {
      confidence: 0.94,
      durationSeconds: 4.2,
    }),
    {
      id: crypto.randomUUID(),
      role: 'assistant',
      content:
        'Em dias úteis, o transporte de bicicleta é permitido **após as 20h30**. Aos sábados, ' +
        'domingos e feriados, durante toda a operação [Fonte 1].\n\n' +
        'O passageiro deve usar o último carro e respeitar a capacidade indicada pela equipe.',
      createdAt: hoursAgo(25),
      origin: 'text',
      status: 'complete',
      interactionId: 'interactions/mock-0028',
      sources: docs('base-atendimento:303'),
      intent: {
        macro: 'CONSULTA',
        macroConfidence: 0.7431,
        specific: null,
        specificConfidence: 0.5109,
        handler: 'fluxo genérico de CONSULTA',
        flow: 'RecuperadorInformacao -> Estruturador de Resposta',
        alternatives: [
          { intent: 'consulta_documentos_fonte', confidence: 0.5109 },
          { intent: 'consulta_escopo_tap', confidence: 0.1893 },
          { intent: 'consulta_status_projeto', confidence: 0.0954 },
        ],
      },
      metrics: {
        model: 'gemini-3.7-flash',
        latencyMs: 1755,
        retrievalMs: 9,
        roundTripMs: 1902,
        inputTokens: 512,
        outputTokens: 118,
        thoughtTokens: 44,
        totalTokens: 674,
      },
      intentLayerEnabled: true,
    },
  ],
};

const PORTFOLIO: Conversation = {
  id: 'f9b3e5d4-4c18-49aa-8d21-2f7c9a1e5b03',
  title: deriveConversationTitle('Qual é o status da extensão da Linha 5-Lilás?'),
  createdAt: daysAgo(4, 15),
  updatedAt: daysAgo(4, 15),
  status: 'finalizada',
  channel: 'webchat',
  lastInteractionId: 'interactions/mock-0019',
  messages: [
    userMessage('Qual é o status da extensão da Linha 5-Lilás?', daysAgo(4, 15)),
    {
      id: crypto.randomUUID(),
      role: 'assistant',
      content:
        'Não encontrei, entre as listas disponíveis, nenhum registro sobre a extensão da ' +
        'Linha 5-Lilás. As listas simuladas hoje cobrem procedimentos operacionais, ' +
        'comunicados de serviço e base de atendimento — o portfólio de projetos ainda não ' +
        'está indexado.\n\n' +
        'Posso responder sobre os documentos disponíveis ou registrar essa consulta para a ' +
        'próxima carga de dados.',
      createdAt: daysAgo(4, 15),
      origin: 'text',
      status: 'complete',
      interactionId: 'interactions/mock-0019',
      // Sem fontes: e o que `retrieve_sharepoint_context` devolve quando
      // nenhum documento casa com a consulta.
      sources: [],
      intent: {
        macro: 'CONSULTA',
        macroConfidence: 0.9642,
        specific: 'consulta_status_projeto',
        specificConfidence: 0.9011,
        handler: 'handler:consulta_status_projeto',
        flow: 'RecuperadorInformacao -> Estruturador de Resposta',
        alternatives: [
          { intent: 'consulta_status_projeto', confidence: 0.9011 },
          { intent: 'consulta_cronograma_prazo', confidence: 0.0455 },
          { intent: 'analise_tendencia_desempenho', confidence: 0.0189 },
        ],
      },
      metrics: {
        model: 'gemini-3.7-flash',
        latencyMs: 1980,
        retrievalMs: 7,
        roundTripMs: 2115,
        inputTokens: 143,
        outputTokens: 132,
        thoughtTokens: 51,
        totalTokens: 326,
      },
      intentLayerEnabled: true,
    },
  ],
};

const OUT_OF_SCOPE: Conversation = {
  id: 'b6c2a908-71d5-4c7e-a1f0-3d8e4b2c6d04',
  title: deriveConversationTitle('Qual a previsão do tempo para amanhã?'),
  createdAt: daysAgo(12, 9),
  updatedAt: daysAgo(12, 9),
  status: 'finalizada',
  channel: 'webchat',
  lastInteractionId: null,
  messages: [
    userMessage('Qual a previsão do tempo para amanhã?', daysAgo(12, 9)),
    {
      id: crypto.randomUUID(),
      role: 'assistant',
      content:
        'Essa pergunta está fora do escopo do agente, que responde sobre o portfólio de ' +
        'projetos e a documentação do Metrô.',
      createdAt: daysAgo(12, 9),
      origin: 'text',
      status: 'complete',
      interactionId: null,
      sources: [],
      intent: {
        macro: 'FORA_DE_ESCOPO',
        macroConfidence: 0.8874,
        specific: null,
        specificConfidence: 0.6621,
        handler: 'fluxo genérico de FORA_DE_ESCOPO',
        flow: 'Resposta controlada de fora de escopo',
        alternatives: [
          { intent: 'fora_escopo_geral', confidence: 0.6621 },
          { intent: 'consulta_indicadores_kpi', confidence: 0.0512 },
          { intent: 'consulta_visao_portfolio', confidence: 0.0298 },
        ],
      },
      // Sem `metrics`: o classificador barrou a solicitacao antes do LLM, entao
      // nao houve chamada ao provedor para medir.
      intentLayerEnabled: true,
    },
  ],
};

export const MOCK_CONVERSATIONS: Conversation[] = [
  CURRENT,
  BICYCLE,
  PORTFOLIO,
  OUT_OF_SCOPE,
];

export const MOCK_ACTIVE_CONVERSATION_ID = CURRENT.id;

/** Sugestoes da tela inicial, alinhadas ao que as listas simuladas cobrem. */
export const SUGGESTED_PROMPTS = [
  'Qual é o procedimento para objeto perdido?',
  'Posso levar bicicleta no metrô em dia útil?',
  'Como registrar uma reclamação de passageiro?',
  'Quais acessos estão fechados na Estação República?',
] as const;
