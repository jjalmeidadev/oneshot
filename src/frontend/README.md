# Frontend — interface do agente

Interface visual do agente de IA do portfólio de projetos do Metrô. Cobre o
chat, a camada validadora de intenção, a visualização dos documentos que o RAG
recuperou e o envio de áudio.

**Esta camada ainda não está ligada ao backend.** A tela é funcional do ponto de
vista visual e de interação, e todo ponto que precisa de rede está isolado e
marcado — ver [Pontos de integração](#pontos-de-integração).

## Stack

React 19, TypeScript, Vite, Tailwind CSS, Radix UI (padrão shadcn/21st.dev),
framer-motion, react-markdown. ESLint e Prettier.

## Comandos

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # tsc --noEmit && vite build
npm run lint
npm run format
```

O Vite encaminha `/api` e `/health` para `http://127.0.0.1:8000`
(`vite.config.ts`), mantendo a chave do Gemini apenas no backend. Para ver o
backend respondendo, suba-o antes conforme `../backend/README.md`.

## Layout

```text
┌──────────────┬───────────────────────────────┬──────────────────┐
│  conversas   │  cabeçalho da conversa        │  documentos      │
│  do usuário  │                               │  recuperados     │
│              │  mensagens                    │  pelo RAG        │
│  busca       │  ├ resposta em markdown       │  ├ lista ordenada│
│  agrupamento │  ├ citações [Fonte N]         │  │  por citação  │
│  por data    │  └ selo de intenção           │  ├ metadados     │
│              │                               │  └ trecho        │
│  perfil      │  ── toggle de intenção ──     │                  │
│  tema        │  campo de texto + áudio       │  aba "Resposta": │
│              │                               │  latência,       │
│              │                               │  tokens, intenção│
└──────────────┴───────────────────────────────┴──────────────────┘
     280px              flexível                    320–384px
```

Abaixo de 1024 px a barra lateral e o painel de documentos viram painéis
deslizantes e o chat ocupa a largura inteira.

## Estrutura

```text
src/
├── lib/
│   ├── api/
│   │   ├── schemas.ts        espelho dos BaseModel do backend
│   │   ├── constants.ts      limites e limiares lidos do backend
│   │   ├── client.ts         fetch + ApiError (normaliza os dois envelopes)
│   │   ├── chat.ts           POST /api/chat, GET /health
│   │   ├── audio.ts          POST /api/audio
│   │   └── conversations.ts  contrato PROPOSTO, ainda não existe
│   ├── domain.ts             tipos que os componentes usam + conversões
│   ├── format.ts             datas, durações, tokens, confiança
│   └── utils.ts              cn()
├── state/
│   ├── chat-store.tsx        conversas, mensagens, toggle, seleção
│   └── theme-provider.tsx    tema claro/escuro
├── hooks/
│   ├── use-audio-recorder.ts captura via MediaRecorder
│   ├── use-theme.ts
│   ├── use-autosize-textarea.ts
│   └── use-media-query.ts
├── components/
│   ├── ui/                   primitivos (button, switch, tooltip, tabs…)
│   ├── layout/               app-shell, theme-toggle
│   ├── sidebar/              histórico de conversas
│   ├── chat/                 mensagens, markdown, citações, intenção
│   ├── composer/             toggle de intenção, campo, áudio
│   ├── documents/            painel do RAG e detalhes da resposta
│   └── dev/                  alternador de estados (descartável)
└── data/                     mock e cenários (descartáveis)
```

## O que já existe no backend e a interface consome

| Rota              | Origem                  | Uso na interface                    |
| ----------------- | ----------------------- | ----------------------------------- |
| `POST /api/chat`  | `app/gemini/schemas.py` | resposta, fontes, latências, tokens |
| `POST /api/audio` | `app/audio/schemas.py`  | transcrição, intenção, resposta     |
| `GET /health`     | `app/main.py`           | indicador de conexão                |

Os limites e limiares exibidos na interface — 60 s e 2 MB de áudio, limiares
0,55 e 0,70 do classificador, teto de 20.000 caracteres da mensagem, orçamento
de 10 s do RNF05 — **não** são escolha do frontend: estão em
`src/lib/api/constants.ts`, cada um com o arquivo de origem anotado ao lado.

## Pontos de integração

### 1. Enviar a mensagem — `src/state/chat-store.tsx`

`sendMessage` insere a mensagem do usuário e devolve uma resposta fixa. O bloco
comentado logo abaixo, marcado `PONTO DE INTEGRACAO 1`, tem o código exato a
colocar no lugar: `sendChatMessage` + `toAssistantMessage`. As conversões de
`sources`, `usage` e latências já estão prontas em `lib/domain.ts`, então
nenhum componente precisa ser tocado.

O encadeamento de contexto já está modelado: cada conversa guarda
`lastInteractionId`, que deve voltar como `previous_interaction_id`.

### 2. Toggle da camada de intenção — `src/lib/api/chat.ts`

`SendMessageInput.useIntentClassifier` carrega o estado do toggle, mas **não é
enviado**: `GeminiChatRequest` só aceita `message` e `previous_interaction_id`.
Para ligar de ponta a ponta, o backend precisa de:

```python
class GeminiChatRequest(BaseModel):
    message: str
    previous_interaction_id: str | None = None
    use_intent_classifier: bool = True     # novo

class GeminiChatResponse(BaseModel):
    ...
    intent: AudioIntent | None = None      # já existe em app/audio/schemas.py
```

Com o campo `intent` na resposta, `toIntentResult` (em `lib/domain.ts`) já
converte, e o selo de intenção e a aba "Resposta" passam a exibir dados reais
sem alteração de componente.

### 3. Envio do áudio — `src/components/composer/composer.tsx`

`handleSendAudio` para exatamente na fronteira: a captura já entrega um `Blob`
conferido contra duração, tamanho e contêiner. Falta chamar `uploadAudio`
(`lib/api/audio.ts`) e transformar `AudioUploadResponse` em duas mensagens — a
transcrição vira a do usuário, `answer.text` a do assistente.

O endpoint exige `Authorization: Bearer <token>`. A interface **não tem fonte de
identidade**: a autenticação vem do Microsoft Entra ID pelo canal (Seção 6.2.4),
e enquanto o ambiente corporativo não existe o backend usa o mapa simulado
`AUDIO_SIMULATED_IDENTITIES`. O perfil exibido na barra lateral vem de
`data/mock.ts` (`MOCK_USER`) e precisa ser trocado pelo que o canal entregar.

### 4. Histórico de conversas — `src/lib/api/conversations.ts`

Não existe rota de conversas no backend. O arquivo traz o contrato proposto,
derivado das tabelas `ai_conversations`, `ai_interactions` e `consulted_sources`
que já estão em `src/database/sql/01_create_database.sql`, com os mesmos nomes
de coluna. As funções lançam de propósito e nenhuma tela as chama.

Ao criar as rotas, troque `initialState()` em `chat-store.tsx` por lista vazia e
carregue o histórico com `listConversations()`.

## Lacunas do backend encontradas ao construir a interface

São incoerências reais entre o que a interface precisa exibir e o que a API
entrega hoje. Nenhuma foi contornada com dado inventado.

**1. O trecho do documento não acompanha a resposta.** `GeminiSource` tem
título, lista, URL, data e score, mas não o conteúdo. O texto existe do outro
lado — `RetrievedDocument.document.content` em `app/rag/sharepoint.py` — e é
descartado ao montar a resposta em `app/gemini/client.py`. Sem ele, o painel
mostra os metadados e o link, e declara que o trecho não veio, em vez de exibir
um texto que a API não garantiu. A correção é uma linha:

```python
GeminiSource(
    ...,
    score=result.score,
    excerpt=result.document.content,   # + o campo em GeminiSource
)
```

O tipo do frontend já aceita o campo (`ChatSource.excerpt`, opcional) e o painel
já renderiza quando ele chega — o cenário "Fontes com trecho", no alternador de
estados, mostra como fica.

**2. O contêiner que o Chrome grava é recusado.** A validação aceita WAV/PCM e
OGG/OPUS; o `MediaRecorder` do Chrome produz `audio/webm;codecs=opus`. O Firefox
grava OGG e passa. O gravador negocia o tipo e avisa antes do envio
(`containerAccepted`), mas a decisão é do backend: ou `app/audio/validation.py`
passa a aceitar WebM/Opus — o codec é o mesmo, muda só o contêiner — ou o
frontend precisa converter para WAV 16 kHz antes de enviar, o que custa uma
biblioteca de áudio no navegador.

**3. Duas formas de fonte para o mesmo conceito.** A rota de texto devolve
`GeminiSource` (id, título, lista, URL, data, score) e a de áudio devolve
`AudioAnswerSource` (artifact, section). Quando o pipeline de áudio passar a
responder de verdade, convém unificar, senão o painel de documentos precisa de
dois caminhos de renderização.

**4. Identidade exigida só em uma rota.** `POST /api/audio` recusa sem
`Authorization`; `POST /api/chat` não pede nada. Como observa o próprio
`app/audio/security.py`, quando a rota de texto também exigir identidade o
módulo deve subir para `app/security.py`.

## Estados da interface

O seletor no rodapé da barra lateral simula os estados que dependem do backend:
resposta em andamento, erro 503 sem `GEMINI_API_KEY`, resposta sem fontes,
fontes com trecho, confiança abaixo do limiar (resposta de limitação do RF08) e
primeiro acesso sem histórico.

**Remover ao integrar:** `src/data/mock.ts`, `src/data/scenarios.ts`,
`src/components/dev/scenario-switcher.tsx`, o campo `scenario` da store e a
chamada a `applyScenario` no provider.
