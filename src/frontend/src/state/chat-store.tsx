import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useReducer,
  useRef,
  useEffect,
  type ReactNode,
} from 'react';

import {
  confirmProactiveSuggestion,
  sendChatMessage,
  uploadAudio,
  toDisplayMessage,
  CHAT_MESSAGE_MAX_LENGTH,
  type AudioPipelineMetrics,
  type ProactiveDecision,
} from '@/lib/api';
import { toAssistantMessage } from '@/lib/domain';
type ChatStatus = 'idle' | 'sending' | 'error';
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
  /** Sugestao secundaria fundamentada, controlada pelo usuario. */
  proactivityEnabled: boolean;
  /** Documento aberto no painel da direita. */
  selectedDocumentId: string | null;
  /** Painel lateral fixo, em telas largas. Aberto por padrao. */
  documentPanelOpen: boolean;
  /** Painel deslizante, em telas estreitas. Fechado por padrao. */
  documentSheetOpen: boolean;
  sidebarOpen: boolean;
  accessToken: string;
};

type Action =
  | { type: 'new-conversation'; conversation: Conversation }
  | { type: 'select-conversation'; id: string }
  | { type: 'delete-conversation'; id: string }
  | { type: 'append-message'; conversationId: string; message: ChatMessage }
  | {
      type: 'update-proactive-suggestion';
      conversationId: string;
      messageId: string;
      status: NonNullable<ChatMessage['proactiveSuggestion']>['status'];
    }
  | { type: 'set-status'; status: ChatStatus; error?: string | null }
  | { type: 'toggle-intent-layer'; enabled: boolean }
  | { type: 'toggle-proactivity'; enabled: boolean }
  | { type: 'select-document'; id: string | null }
  | { type: 'set-document-panel'; open: boolean }
  | { type: 'set-document-sheet'; open: boolean }
  | { type: 'set-sidebar'; open: boolean }
  | { type: 'set-token'; token: string };

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
      const conversation = action.conversation;
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
      return {
        ...state,
        conversations,
        selectedDocumentId:
          action.message.role === 'assistant' ? null : state.selectedDocumentId,
      };
    }

    case 'update-proactive-suggestion':
      return {
        ...state,
        conversations: state.conversations.map((conversation) =>
          conversation.id !== action.conversationId
            ? conversation
            : {
                ...conversation,
                messages: conversation.messages.map((message) =>
                  message.id !== action.messageId || !message.proactiveSuggestion
                    ? message
                    : {
                        ...message,
                        proactiveSuggestion: {
                          ...message.proactiveSuggestion,
                          status: action.status,
                        },
                      },
                ),
              },
        ),
      };

    case 'set-status':
      return { ...state, status: action.status, error: action.error ?? null };

    case 'toggle-intent-layer':
      return {
        ...state,
        intentLayerEnabled: action.enabled,
        proactivityEnabled: action.enabled ? state.proactivityEnabled : false,
      };

    case 'toggle-proactivity':
      return { ...state, proactivityEnabled: action.enabled };

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

    case 'set-token':
      return { ...state, accessToken: action.token };

    default:
      return state;
  }
}

/** Conversas apenas da sessão atual; nenhum dado fictício é carregado. */
function initialState(): State {
  return {
    conversations: [],
    activeConversationId: null,
    status: 'idle',
    error: null,
    intentLayerEnabled: true,
    proactivityEnabled: false,
    selectedDocumentId: null,
    documentPanelOpen: true,
    documentSheetOpen: false,
    sidebarOpen: false,
    accessToken: '',
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
  proactivityEnabled: boolean;
  documentPanelOpen: boolean;
  documentSheetOpen: boolean;
  sidebarOpen: boolean;
  accessToken: string;
  /** Fontes da ultima resposta do assistente na conversa ativa. */
  activeSources: RetrievedDocument[];
  selectedDocument: RetrievedDocument | null;
  sendMessage: (content: string) => Promise<boolean>;
  sendAudio: (audio: Blob) => Promise<boolean>;
  resolveProactiveSuggestion: (
    messageId: string,
    decision: ProactiveDecision,
  ) => Promise<boolean>;
  stop: () => void;
  newConversation: () => void;
  selectConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  setIntentLayerEnabled: (enabled: boolean) => void;
  setProactivityEnabled: (enabled: boolean) => void;
  selectDocument: (id: string | null) => void;
  setDocumentPanelOpen: (open: boolean) => void;
  setDocumentSheetOpen: (open: boolean) => void;
  setSidebarOpen: (open: boolean) => void;
  setAccessToken: (token: string) => void;
};

const ChatStoreContext = createContext<ChatStoreValue | null>(null);

export function ChatStoreProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, undefined, initialState);

  const view = state;
  const pending = useRef<AbortController | null>(null);
  const pendingSuggestion = useRef<{
    conversationId: string;
    messageId: string;
  } | null>(null);
  const stop = useCallback(() => {
    const suggestion = pendingSuggestion.current;
    pending.current?.abort();
    pending.current = null;
    pendingSuggestion.current = null;
    if (suggestion) {
      dispatch({
        type: 'update-proactive-suggestion',
        conversationId: suggestion.conversationId,
        messageId: suggestion.messageId,
        status: 'pending',
      });
    }
    dispatch({ type: 'set-status', status: 'idle' });
  }, []);
  useEffect(() => () => pending.current?.abort(), []);

  const activeConversation = useMemo(
    () =>
      view.conversations.find(
        (conversation) => conversation.id === view.activeConversationId,
      ) ?? null,
    [view.conversations, view.activeConversationId],
  );

  const activeSources = useMemo(() => {
    if (!activeConversation) return [];
    if (state.selectedDocumentId) {
      const selected = [...activeConversation.messages]
        .reverse()
        .find((message) =>
          message.sources?.some((source) => source.id === state.selectedDocumentId),
        );
      if (selected?.sources) return selected.sources;
    }
    for (let index = activeConversation.messages.length - 1; index >= 0; index -= 1) {
      const message = activeConversation.messages[index];
      if (message.role === 'assistant' && message.sources) {
        return message.sources;
      }
    }
    return [];
  }, [activeConversation, state.selectedDocumentId]);

  // Sem escolha explicita, o painel ja abre no primeiro documento citado: e o
  // de maior score e o que a resposta cita como [Fonte 1].
  const selectedDocument = useMemo(
    () =>
      activeSources.find((document) => document.id === state.selectedDocumentId) ??
      activeSources[0] ??
      null,
    [activeSources, state.selectedDocumentId],
  );

  const send = useCallback(
    async (input: string | Blob): Promise<boolean> => {
      if (pending.current) return false;
      if (
        typeof input === 'string' &&
        (!input.trim() || input.length > CHAT_MESSAGE_MAX_LENGTH)
      ) {
        dispatch({
          type: 'set-status',
          status: 'error',
          error: 'Informe uma mensagem de 1 a 20.000 caracteres.',
        });
        return false;
      }
      if (input instanceof Blob && !state.accessToken.trim()) {
        dispatch({
          type: 'set-status',
          status: 'error',
          error: 'Informe o token de acesso da sessão antes de enviar áudio.',
        });
        return false;
      }
      if (
        typeof input === 'string' &&
        state.proactivityEnabled &&
        !state.accessToken.trim()
      ) {
        dispatch({
          type: 'set-status',
          status: 'error',
          error: 'Informe o token de acesso da sessão para usar a proatividade.',
        });
        return false;
      }
      const conversation = activeConversation ?? createConversation();
      if (!activeConversation) dispatch({ type: 'new-conversation', conversation });
      const controller = new AbortController();
      pending.current = controller;
      const started = performance.now();
      dispatch({ type: 'set-status', status: 'sending' });
      try {
        let response;
        let transcription;
        let pipelineMetrics: AudioPipelineMetrics | undefined;
        const text = typeof input === 'string' ? input.trim() : '';
        if (typeof input === 'string') {
          dispatch({
            type: 'append-message',
            conversationId: conversation.id,
            message: {
              id: crypto.randomUUID(),
              role: 'user',
              content: text,
              createdAt: new Date().toISOString(),
              origin: 'text',
              status: 'complete',
            },
          });
          response = await sendChatMessage({
            message: text,
            conversationId: conversation.id,
            accessToken: state.accessToken,
            previousInteractionId: conversation.lastInteractionId,
            useIntentClassifier: state.intentLayerEnabled,
            proactivityEnabled: state.proactivityEnabled,
            signal: controller.signal,
          });
        } else {
          const result = await uploadAudio({
            audio: input,
            filename: 'gravacao.wav',
            conversationId: conversation.id,
            accessToken: state.accessToken,
            previousInteractionId: conversation.lastInteractionId,
            useIntentClassifier: state.intentLayerEnabled,
            proactivityEnabled: state.proactivityEnabled,
            signal: controller.signal,
          });
          if (result.pipeline_status !== 'completed' || !result.chat)
            throw new Error('Incomplete pipeline');
          response = result.chat;
          transcription = result.transcription;
          pipelineMetrics = result.pipeline_metrics;
        }
        if (controller.signal.aborted || pending.current !== controller) return false;
        if (transcription)
          dispatch({
            type: 'append-message',
            conversationId: conversation.id,
            message: {
              id: crypto.randomUUID(),
              role: 'user',
              content: transcription.text,
              createdAt: new Date().toISOString(),
              origin: 'audio',
              status: 'complete',
              transcription: {
                confidence: transcription.confidence,
                durationSeconds: transcription.duration_seconds,
              },
            },
          });
        dispatch({
          type: 'append-message',
          conversationId: conversation.id,
          message: toAssistantMessage(response, {
            roundTripMs: performance.now() - started,
            intentLayerEnabled: state.intentLayerEnabled,
            pipelineMetrics,
          }),
        });
        dispatch({ type: 'set-status', status: 'idle' });
        return true;
      } catch (cause) {
        if (!controller.signal.aborted && pending.current === controller)
          dispatch({
            type: 'set-status',
            status: 'error',
            error: toDisplayMessage(cause),
          });
        return false;
      } finally {
        if (pending.current === controller) pending.current = null;
      }
    },
    [
      activeConversation,
      state.accessToken,
      state.intentLayerEnabled,
      state.proactivityEnabled,
    ],
  );
  const sendMessage = useCallback((content: string) => send(content), [send]);
  const sendAudio = useCallback((audio: Blob) => send(audio), [send]);
  const resolveProactiveSuggestion = useCallback(
    async (messageId: string, decision: ProactiveDecision): Promise<boolean> => {
      if (pending.current || !activeConversation) return false;
      const message = activeConversation.messages.find((item) => item.id === messageId);
      const suggestion = message?.proactiveSuggestion;
      if (!suggestion || suggestion.status !== 'pending') return false;

      const controller = new AbortController();
      pending.current = controller;
      pendingSuggestion.current = {
        conversationId: activeConversation.id,
        messageId,
      };
      const started = performance.now();
      dispatch({ type: 'set-status', status: 'sending' });
      dispatch({
        type: 'update-proactive-suggestion',
        conversationId: activeConversation.id,
        messageId,
        status: decision === 'accept' ? 'accepting' : 'declining',
      });

      try {
        const confirmation = await confirmProactiveSuggestion({
          suggestionId: suggestion.id,
          conversationId: activeConversation.id,
          accessToken: state.accessToken,
          decision,
          signal: controller.signal,
        });
        if (controller.signal.aborted || pending.current !== controller) return false;

        if (decision === 'accept') {
          if (confirmation.status !== 'accepted' || !confirmation.result) {
            throw new Error('Incomplete proactive confirmation');
          }
          dispatch({
            type: 'append-message',
            conversationId: activeConversation.id,
            message: {
              ...toAssistantMessage(confirmation.result, {
                roundTripMs: performance.now() - started,
                intentLayerEnabled: state.intentLayerEnabled,
              }),
              // A geracao proativa e uma rota isolada. A proxima pergunta deve
              // continuar encadeada a resposta primaria da conversa.
              interactionId: null,
            },
          });
        }
        dispatch({
          type: 'update-proactive-suggestion',
          conversationId: activeConversation.id,
          messageId,
          status: decision === 'accept' ? 'accepted' : 'declined',
        });
        dispatch({ type: 'set-status', status: 'idle' });
        return true;
      } catch (cause) {
        if (!controller.signal.aborted && pending.current === controller) {
          dispatch({
            type: 'update-proactive-suggestion',
            conversationId: activeConversation.id,
            messageId,
            status: 'pending',
          });
          dispatch({
            type: 'set-status',
            status: 'error',
            error: toDisplayMessage(cause),
          });
        }
        return false;
      } finally {
        if (pending.current === controller) {
          pending.current = null;
          pendingSuggestion.current = null;
        }
      }
    },
    [activeConversation, state.accessToken, state.intentLayerEnabled],
  );

  const value = useMemo<ChatStoreValue>(
    () => ({
      conversations: view.conversations,
      activeConversation,
      status: view.status,
      error: view.error,
      intentLayerEnabled: state.intentLayerEnabled,
      proactivityEnabled: state.proactivityEnabled,
      documentPanelOpen: state.documentPanelOpen,
      documentSheetOpen: state.documentSheetOpen,
      sidebarOpen: state.sidebarOpen,
      accessToken: state.accessToken,
      activeSources,
      selectedDocument,
      sendMessage,
      sendAudio,
      resolveProactiveSuggestion,
      stop,
      newConversation: () => {
        stop();
        dispatch({ type: 'new-conversation', conversation: createConversation() });
      },
      selectConversation: (id) => {
        stop();
        dispatch({ type: 'select-conversation', id });
      },
      deleteConversation: (id) => {
        stop();
        dispatch({ type: 'delete-conversation', id });
      },
      setIntentLayerEnabled: (enabled) =>
        dispatch({ type: 'toggle-intent-layer', enabled }),
      setProactivityEnabled: (enabled) =>
        dispatch({ type: 'toggle-proactivity', enabled }),
      selectDocument: (id) => dispatch({ type: 'select-document', id }),
      setDocumentPanelOpen: (open) => dispatch({ type: 'set-document-panel', open }),
      setDocumentSheetOpen: (open) => dispatch({ type: 'set-document-sheet', open }),
      setSidebarOpen: (open) => dispatch({ type: 'set-sidebar', open }),
      setAccessToken: (token) => dispatch({ type: 'set-token', token }),
    }),
    [
      view.conversations,
      view.status,
      view.error,
      activeConversation,
      activeSources,
      selectedDocument,
      state.intentLayerEnabled,
      state.proactivityEnabled,
      state.documentPanelOpen,
      state.documentSheetOpen,
      state.sidebarOpen,
      state.accessToken,
      sendMessage,
      sendAudio,
      resolveProactiveSuggestion,
      stop,
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
