/**
 * Estado da interface do agente.
 *
 * A store guarda conversas, mensagens, o estado do toggle de intencao e o que
 * o painel de documentos exibe. Ela **nao fala com o backend**: o unico ponto
 * que chamaria a API esta isolado em `sendMessage`, marcado com
 * `PONTO DE INTEGRACAO`. Toda a arvore de componentes le daqui, entao ligar a
 * API nao exige tocar em nenhum componente.
 */

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useReducer,
  type ReactNode,
} from 'react';

import { MOCK_ACTIVE_CONVERSATION_ID, MOCK_CONVERSATIONS } from '@/data/mock';
import {
  applyScenario,
  stripExcerpts,
  type ChatStatus,
  type ScenarioId,
} from '@/data/scenarios';
import { CONVERSATION_CHANNEL } from '@/lib/api/constants';
import {
  deriveConversationTitle,
  type ChatMessage,
  type Conversation,
  type RetrievedDocument,
} from '@/lib/domain';

/* -------------------------------------------------------------------------
 * Estado
 * ---------------------------------------------------------------------- */

type State = {
  conversations: Conversation[];
  activeConversationId: string | null;
  status: ChatStatus;
  error: string | null;
  /** Toggle da camada validadora de intencao, acima do campo de texto. */
  intentLayerEnabled: boolean;
  /** Documento aberto no painel da direita. */
  selectedDocumentId: string | null;
  /** Painel lateral fixo, em telas largas. Aberto por padrao. */
  documentPanelOpen: boolean;
  /** Painel deslizante, em telas estreitas. Fechado por padrao. */
  documentSheetOpen: boolean;
  sidebarOpen: boolean;
  scenario: ScenarioId;
};

type Action =
  | { type: 'new-conversation' }
  | { type: 'select-conversation'; id: string }
  | { type: 'delete-conversation'; id: string }
  | { type: 'append-message'; conversationId: string; message: ChatMessage }
  | { type: 'set-status'; status: ChatStatus; error?: string | null }
  | { type: 'toggle-intent-layer'; enabled: boolean }
  | { type: 'select-document'; id: string | null }
  | { type: 'set-document-panel'; open: boolean }
  | { type: 'set-document-sheet'; open: boolean }
  | { type: 'set-sidebar'; open: boolean }
  | { type: 'set-scenario'; scenario: ScenarioId };

function createConversation(): Conversation {
  const now = new Date().toISOString();
  return {
    id: crypto.randomUUID(),
    title: 'Nova conversa',
    createdAt: now,
    updatedAt: now,
    status: 'ativa',
    channel: CONVERSATION_CHANNEL,
    messages: [],
    lastInteractionId: null,
  };
}

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'new-conversation': {
      const conversation = createConversation();
      return {
        ...state,
        conversations: [conversation, ...state.conversations],
        activeConversationId: conversation.id,
        status: 'idle',
        error: null,
        selectedDocumentId: null,
        sidebarOpen: false,
      };
    }

    case 'select-conversation':
      return {
        ...state,
        activeConversationId: action.id,
        status: 'idle',
        error: null,
        selectedDocumentId: null,
        sidebarOpen: false,
      };

    case 'delete-conversation': {
      const conversations = state.conversations.filter((c) => c.id !== action.id);
      const activeConversationId =
        state.activeConversationId === action.id
          ? (conversations[0]?.id ?? null)
          : state.activeConversationId;
      return { ...state, conversations, activeConversationId };
    }

    case 'append-message': {
      const conversations = state.conversations.map((conversation) => {
        if (conversation.id !== action.conversationId) return conversation;

        const messages = [...conversation.messages, action.message];
        const isFirstUserMessage =
          action.message.role === 'user' && conversation.messages.length === 0;

        return {
          ...conversation,
          messages,
          updatedAt: action.message.createdAt,
          title: isFirstUserMessage
            ? deriveConversationTitle(action.message.content)
            : conversation.title,
          lastInteractionId:
            action.message.interactionId ?? conversation.lastInteractionId,
        };
      });
      return { ...state, conversations };
    }

    case 'set-status':
      return { ...state, status: action.status, error: action.error ?? null };

    case 'toggle-intent-layer':
      return { ...state, intentLayerEnabled: action.enabled };

    case 'select-document':
      return {
        ...state,
        selectedDocumentId: action.id,
        documentPanelOpen: action.id ? true : state.documentPanelOpen,
      };

    case 'set-document-panel':
      return { ...state, documentPanelOpen: action.open };

    case 'set-document-sheet':
      return { ...state, documentSheetOpen: action.open };

    case 'set-sidebar':
      return { ...state, sidebarOpen: action.open };

    case 'set-scenario':
      return { ...state, scenario: action.scenario, selectedDocumentId: null };

    default:
      return state;
  }
}

/**
 * Estado inicial vindo do mock.
 *
 * AO LIGAR A API: troque por `{ conversations: [], activeConversationId: null }`
 * e carregue o historico com `listConversations()` num efeito. Ver README,
 * "Ponto de integracao 4".
 */
function initialState(): State {
  return {
    conversations: stripExcerpts(MOCK_CONVERSATIONS),
    activeConversationId: MOCK_ACTIVE_CONVERSATION_ID,
    status: 'idle',
    error: null,
    intentLayerEnabled: true,
    selectedDocumentId: null,
    documentPanelOpen: true,
    documentSheetOpen: false,
    sidebarOpen: false,
    scenario: 'default',
  };
}

/* -------------------------------------------------------------------------
 * Contexto
 * ---------------------------------------------------------------------- */

type ChatStoreValue = {
  conversations: Conversation[];
  activeConversation: Conversation | null;
  status: ChatStatus;
  error: string | null;
  intentLayerEnabled: boolean;
  documentPanelOpen: boolean;
  documentSheetOpen: boolean;
  sidebarOpen: boolean;
  scenario: ScenarioId;
  /** Fontes da ultima resposta do assistente na conversa ativa. */
  activeSources: RetrievedDocument[];
  selectedDocument: RetrievedDocument | null;
  sendMessage: (content: string) => void;
  newConversation: () => void;
  selectConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  setIntentLayerEnabled: (enabled: boolean) => void;
  selectDocument: (id: string | null) => void;
  setDocumentPanelOpen: (open: boolean) => void;
  setDocumentSheetOpen: (open: boolean) => void;
  setSidebarOpen: (open: boolean) => void;
  setScenario: (scenario: ScenarioId) => void;
};

const ChatStoreContext = createContext<ChatStoreValue | null>(null);

export function ChatStoreProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, undefined, initialState);

  // O cenario de revisao transforma o estado so na leitura. Ao remover o
  // alternador, esta linha vira `const view = { ...state }`.
  const view = useMemo(
    () =>
      applyScenario(state.scenario, {
        conversations:
          state.scenario === 'source-excerpt'
            ? MOCK_CONVERSATIONS
            : state.conversations,
        activeConversationId: state.activeConversationId,
        status: state.status,
        error: state.error,
      }),
    [
      state.scenario,
      state.conversations,
      state.activeConversationId,
      state.status,
      state.error,
    ],
  );

  const activeConversation = useMemo(
    () =>
      view.conversations.find(
        (conversation) => conversation.id === view.activeConversationId,
      ) ?? null,
    [view.conversations, view.activeConversationId],
  );

  const activeSources = useMemo(() => {
    if (!activeConversation) return [];
    for (let index = activeConversation.messages.length - 1; index >= 0; index -= 1) {
      const message = activeConversation.messages[index];
      if (message.role === 'assistant' && message.sources) {
        return message.sources;
      }
    }
    return [];
  }, [activeConversation]);

  // Sem escolha explicita, o painel ja abre no primeiro documento citado: e o
  // de maior score e o que a resposta cita como [Fonte 1].
  const selectedDocument = useMemo(
    () =>
      activeSources.find((document) => document.id === state.selectedDocumentId) ??
      activeSources[0] ??
      null,
    [activeSources, state.selectedDocumentId],
  );

  const sendMessage = useCallback(
    (content: string) => {
      const trimmed = content.trim();
      if (!trimmed) return;

      const conversationId = state.activeConversationId;
      if (!conversationId) return;

      dispatch({
        type: 'append-message',
        conversationId,
        message: {
          id: crypto.randomUUID(),
          role: 'user',
          content: trimmed,
          createdAt: new Date().toISOString(),
          origin: 'text',
          status: 'complete',
        },
      });
      dispatch({ type: 'set-status', status: 'sending' });

      /*
       * ===================== PONTO DE INTEGRACAO 1 =====================
       *
       * Esta interface ainda nao chama o backend. Substitua o bloco abaixo
       * por, literalmente:
       *
       *   const started = performance.now();
       *   try {
       *     const response = await sendChatMessage({
       *       message: trimmed,
       *       previousInteractionId: activeConversation?.lastInteractionId ?? null,
       *       useIntentClassifier: state.intentLayerEnabled,
       *       signal: controller.signal,
       *     });
       *     dispatch({
       *       type: 'append-message',
       *       conversationId,
       *       message: toAssistantMessage(response, {
       *         roundTripMs: performance.now() - started,
       *         intentLayerEnabled: state.intentLayerEnabled,
       *       }),
       *     });
       *     dispatch({ type: 'set-status', status: 'idle' });
       *   } catch (cause) {
       *     if (isAbortError(cause)) return;
       *     dispatch({ type: 'set-status', status: 'error',
       *                error: toDisplayMessage(cause) });
       *   }
       *
       * `sendChatMessage`, `toAssistantMessage`, `isAbortError` e
       * `toDisplayMessage` ja existem em `lib/api` e `lib/domain`, e
       * `toAssistantMessage` ja converte `sources`, `usage` e as latencias
       * para o formato que os componentes esperam.
       * =================================================================
       */
      const timeout = window.setTimeout(() => {
        dispatch({
          type: 'append-message',
          conversationId,
          message: {
            id: crypto.randomUUID(),
            role: 'assistant',
            content:
              'Interface ainda não conectada ao pipeline de PLN. Esta tela cobre apenas ' +
              'a camada visual: o envio da pergunta, a chamada ao classificador de ' +
              'intenções e a resposta fundamentada entram na task de integração.\n\n' +
              'Use o seletor de cenários, no rodapé da barra lateral, para revisar os ' +
              'demais estados da interface.',
            createdAt: new Date().toISOString(),
            origin: 'text',
            status: 'complete',
            sources: [],
            intentLayerEnabled: state.intentLayerEnabled,
          },
        });
        dispatch({ type: 'set-status', status: 'idle' });
      }, 900);

      return () => window.clearTimeout(timeout);
    },
    [state.activeConversationId, state.intentLayerEnabled],
  );

  const value = useMemo<ChatStoreValue>(
    () => ({
      conversations: view.conversations,
      activeConversation,
      status: view.status,
      error: view.error,
      intentLayerEnabled: state.intentLayerEnabled,
      documentPanelOpen: state.documentPanelOpen,
      documentSheetOpen: state.documentSheetOpen,
      sidebarOpen: state.sidebarOpen,
      scenario: state.scenario,
      activeSources,
      selectedDocument,
      sendMessage,
      newConversation: () => dispatch({ type: 'new-conversation' }),
      selectConversation: (id) => dispatch({ type: 'select-conversation', id }),
      deleteConversation: (id) => dispatch({ type: 'delete-conversation', id }),
      setIntentLayerEnabled: (enabled) =>
        dispatch({ type: 'toggle-intent-layer', enabled }),
      selectDocument: (id) => dispatch({ type: 'select-document', id }),
      setDocumentPanelOpen: (open) => dispatch({ type: 'set-document-panel', open }),
      setDocumentSheetOpen: (open) => dispatch({ type: 'set-document-sheet', open }),
      setSidebarOpen: (open) => dispatch({ type: 'set-sidebar', open }),
      setScenario: (scenario) => dispatch({ type: 'set-scenario', scenario }),
    }),
    [
      view.conversations,
      view.status,
      view.error,
      activeConversation,
      activeSources,
      selectedDocument,
      state.intentLayerEnabled,
      state.documentPanelOpen,
      state.documentSheetOpen,
      state.sidebarOpen,
      state.scenario,
      sendMessage,
    ],
  );

  return (
    <ChatStoreContext.Provider value={value}>{children}</ChatStoreContext.Provider>
  );
}

export function useChatStore(): ChatStoreValue {
  const value = useContext(ChatStoreContext);
  if (!value) {
    throw new Error('useChatStore precisa estar dentro de <ChatStoreProvider>.');
  }
  return value;
}
