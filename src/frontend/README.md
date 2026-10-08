# Frontend integrado — bancada do agente

A interface web em React 19 e TypeScript permite testar o agente por texto ou áudio, exibir a resposta, consultar as fontes e inspecionar a classificação. A entrega da issue #131 integra a base visual da MR !72 aos endpoints existentes. A interface corporativa prevista no projeto continua sendo o Microsoft Teams; esta aplicação é a bancada web de desenvolvimento e validação.

## Alertas proativos

Quando o classificador devolve `alerta_prazo_atraso`, a interface abre o card
guiado para projeto, limiar, recorrência, repetição e confirmação. A central
“Alertas” consulta notificações persistentes a cada 30 segundos, anuncia a
quantidade não lida e permite marcar notificações, pausar, retomar ou cancelar
inscrições. Toda ação usa o token da sessão e as APIs internas; não há webhook
nem dependência de Power Automate.

## Instalação e execução

Requisitos: Node.js 24, npm, Python 3.12 ou 3.13 e acesso às dependências documentadas. Os comandos abaixo partem da raiz do repositório, no PowerShell:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r src/backend/requirements.txt -r src/backend/requirements-pln.txt
Copy-Item src/backend/.env.example src/backend/.env
```

Edite o arquivo local `.env`: informe `GEMINI_API_KEY`, o recurso e a chave Azure Speech. Não versione credenciais. Para entrar na bancada, selecione uma das quatro personas sintéticas e informe a senha cadastrada para a respectiva conta no Supabase Auth. O backend obtém o JWT e o frontend o mantém somente na memória da sessão. Nunca informe chaves do Azure, Gemini ou Supabase na tela de login. Depois da entrada, nome, perfil, escopo e o botão **Sair** ficam na engrenagem **Ajustes do agente**, no canto superior direito do chat.

`PLN_WARMUP=1` prepara o classificador na inicialização. A primeira execução baixa o encoder ONNX publicado no repositório Hugging Face documentado pelo backend. Aguarde a aplicação concluir a inicialização antes de abrir a bancada. Sem esse ajuste, a carga acontece na primeira pergunta com classificação habilitada.

Abra dois terminais:

```powershell
# Terminal 1, na raiz
.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir src/backend --host 127.0.0.1 --port 8000
```

```powershell
# Terminal 2
cd src/frontend
npm ci
npm run dev
```

Abra `http://localhost:5173`. O Vite encaminha `/api` e `/health` para `http://127.0.0.1:8000`. A variável `API_PROXY_TARGET` permite trocar o destino no ambiente de desenvolvimento/teste. Em uma publicação do build estático, configure um proxy de mesma origem para essas rotas; `npm run preview` serve somente o build e não substitui esse proxy.

## Uso e navegabilidade

1. Digite uma pergunta ou selecione uma sugestão. **Enter** envia; **Shift + Enter** quebra a linha. A interface recusa texto vazio ou acima de 20.000 caracteres.
2. A engrenagem **Ajustes do agente**, no canto superior direito, reúne os controles que estendem o modelo e os dados técnicos: **Validação de intenção**, **Sugestões proativas**, **Mostrar detalhes técnicos** e o perfil da sessão, com o botão **Sair**. A tela padrão não exibe detalhes técnicos; ligar **Mostrar detalhes técnicos** traz de volta o selo de intenção, o modelo, a data e o canal da conversa e a aba **Resposta** do painel de fontes. O controle **Validação de intenção** liga ou desliga a classificação local. Quando ligado, os limiares de 0,55 e 0,70 orientam a apresentação da classificação. Perguntas fora de escopo ou sem confiança suficiente recebem resposta controlada sem chamar o Gemini. Identificar uma intenção não significa executar uma transação no portfólio.
3. Durante a chamada, o chat anuncia processamento e impede envios duplicados. **Interromper resposta** aborta a espera HTTP e descarta respostas tardias. Uma chamada já recebida pelo provedor pode continuar no backend.
4. Para voz, entre com uma persona que tenha acesso, clique no microfone, permita a captura, grave e use **Concluir gravação**. Ouça a prévia antes de clicar em **Enviar áudio**. **Descartar** elimina a captura. A gravação para em 60 segundos e é convertida para WAV PCM mono, 16 bits e 16 kHz, com corte por amostras e limite de 2 MB.
5. A transcrição aparece como mensagem do usuário e a resposta como mensagem do agente. As fontes numeradas abaixo da resposta abrem o documento correspondente no painel **Fontes**, que começa fechado; no modo técnico, a aba **Resposta** mostra métricas e classificação fornecidas pela API. O sino ao lado da engrenagem abre as notificações de alerta.
6. Quando o PLN identifica `transacao_gerar_relatorio`, o chat abre um cartão
   guiado. Selecione escopo, período, público, finalidade e ênfases, revise a
   confirmação e acompanhe o processamento. Ao concluir, o DOCX é baixado pelo
   botão **Baixar no chat**; não há redirecionamento para SharePoint.
7. **Nova conversa** inicia outro contexto. A barra lateral permite buscar, selecionar e excluir conversas da sessão. Trocar de conversa cancela a espera atual; uma resposta atrasada não é inserida na conversa selecionada depois.
8. A interface tem três faixas de largura. Abaixo de 1024 px (celular e tablet), o botão **Abrir conversas** abre o menu em diálogo e **Fontes** abre o painel deslizante à direita. De 1024 a 1279 px, as conversas ficam fixas e as fontes continuam deslizantes, para o chat não ficar espremido. A partir de 1280 px, os três painéis ficam lado a lado. **Escape** fecha os diálogos e devolve o foco ao botão que os abriu.
9. O tema segue a preferência do sistema até uma escolha explícita. A escolha de tema pode ser persistida; mensagens e token não são gravados no armazenamento do navegador.

O histórico é da sessão em memória: recarregar a página o apaga. O backend documentado não possui rotas de persistência de conversas. Foram removidos os contratos propostos que lançavam exceção e os cenários fictícios de produção; o encadeamento real usa `previous_interaction_id` por conversa.

## Estrutura e estratégia do código

| Camada                           | Responsabilidade e componentes                                                                                      |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `src/App.tsx` e `state/`         | Provedores de tema e chat; reducer para conversas, fontes e estados; controle de concorrência e cancelamento.       |
| `components/layout/`             | `AppShell` organiza desktop e diálogos móveis; `ThemeToggle` alterna o tema.                                        |
| `components/sidebar/`            | `ConversationSidebar`, `ConversationItem` e `UserCard`: busca, seleção e exclusão; `UserCard` mostra o perfil.      |
| `components/settings/`           | `AgentSettings`: engrenagem com validação de intenção, sugestões proativas, modo técnico e perfil da sessão.        |
| `components/chat/`               | Mensagens, intenção, fontes, `ReportWorkflowCard` (relatório e DOCX) e `DataChangeCard` (alteração de dados).       |
| `components/composer/`           | `Composer`, `AudioButton`, `RecordingBar` e `RecordingPreview`: texto, gravação, revisão e envio.                   |
| `components/documents/`          | `DocumentPanel`, `DocumentCard`, `DocumentViewer` e `ResponseDetails`: fontes, trechos e métricas.                  |
| `components/ui/`                 | Primitivos Radix, botões, campos, diálogos, abas, indicadores e tooltips reutilizados pelos componentes de domínio. |
| `hooks/`                         | Captura e liberação do microfone, tamanho do campo, largura da tela e preferência de tema.                          |
| `lib/api/`                       | Contratos HTTP, cancelamento, prazo máximo de espera e mensagens de erro controladas.                               |
| `lib/domain.ts` e `lib/audio.ts` | Conversão de schemas para a interface e conversão de áudio para o contrato aceito.                                  |
| `data/prompts.ts`                | Sugestões de perguntas; não contém respostas nem histórico simulado.                                                |

Os componentes recebem propriedades ou consomem o contexto; as chamadas HTTP ficam na camada de API. O backend concentra classificação e geração em `app/pipeline.py`, compartilhada por texto e áudio. O upload realiza validação e transcrição antes de executar o pipeline em uma thread, preservando o atendimento assíncrono. O build separa Markdown e animações em módulos próprios.

## Contratos de integração

| Endpoint                                 | Entrada enviada                                                                                                                                                      | Resultado usado                                                                                                                                                                                    |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST /api/chat`                         | JSON: `message`, `conversation_id`, `previous_interaction_id`, `use_intent_classifier`.                                                                              | Resposta textual e, para relatório, diretiva `workflow`.                                                                                                                                           |
| `POST /api/audio`                        | Multipart: `audio`, `conversation_id`, `language`, `previous_interaction_id`, `use_intent_classifier`; `Authorization: Bearer <token>`. O navegador gera o boundary. | `transcription`, `conversation_id`, `interaction_id`, `intent` rico, `entities`, `pipeline_metrics`, `answer`, `chat`, `pipeline_status=completed`. `chat` usa o mesmo schema da resposta textual. |
| `/api/workflow-sessions/*`               | Token Bearer, revisão, etapa, valor e `client_action_id`.                                                                                                            | Pergunta seguinte, confirmação, execução, alertas e artefato.                                                                                                                                      |
| `GET /api/report-requests/{id}/artifact` | Token Bearer da sessão.                                                                                                                                              | Blob DOCX privado usado pelo botão de download.                                                                                                                                                    |
| `/api/data-change-previews/*`            | Token Bearer; proposta completa na criação e `reason` opcional na confirmação.                                                                                       | Prévia, valor gravado com prazo para desfazer, ou cancelamento. Erros trazem `code` e `message` prontos para exibir.                                                                               |
| `/api/data-changes/*`                    | Token Bearer; `project_code`, `field` e `target_id` no histórico.                                                                                                    | Valor restaurado pelo desfazer e histórico do campo, com autor, data e alterações desfeitas.                                                                                                       |
| `GET /health`                            | Sem corpo; verificação operacional.                                                                                                                                  | `status=ok` após a inicialização. Não certifica credenciais dos provedores.                                                                                                                        |

`GeminiSource.excerpt` acompanha o conteúdo recuperado que fundamentou a resposta. As fontes preservam ID, título, lista, URL, data e score; não se inventam fontes quando a lista estiver vazia. A interface usa `handler`, `flow`, `alternatives`, `entities` e `pipeline_metrics` quando enviados pela API, com fallback para respostas antigas. O formato legado `answer.sources` do áudio é preservado, enquanto `chat.sources` fornece os metadados completos para a interface. Uma resposta de limitação pode não trazer `interaction_id`; nesse caso o último contexto válido da conversa é mantido.

O modo proatividade começa desligado. Ele só pode ser ativado com a classificação de intenção habilitada e exige o token da sessão nos fluxos de texto e áudio. Quando o backend retorna `proactive_suggestion`, a interface mantém a resposta principal, registra o estado pendente e apresenta, no card **Ação sugerida**, ações explícitas para aceitar, recusar ou **Não sugerir mais** (recusa a sugestão atual e desliga o modo, que volta pela engrenagem). A recusa encerra o bloco sem resposta secundária; a aceitação usa a rota dedicada, envia identidade e conversa e nunca transforma “sim” em uma nova mensagem comum. Interromper a requisição ou trocar de conversa restaura o bloco para o estado pendente, permitindo nova tentativa.

Quando a resposta do chat traz `data_change` (S5-06), a mensagem ganha o cartão **Alteração de dados** (`DataChangeCard`, S5-07). O cartão é a única via de escrita: a mensagem só mostra a prévia, com o valor antes e depois, os avisos e o prazo da prévia, e a gravação acontece apenas em **Confirmar alteração**, com justificativa opcional. Os estados tratados são prévia, confirmação (com **Desfazer** enquanto a janela de 15 minutos estiver aberta), cancelamento e erro. No erro, a mensagem vem do backend, e **Tentar de novo** só aparece quando repetir adianta, como em falha de rede ou serviço indisponível; prévia desatualizada, expirada ou sem permissão encerra o cartão sem ações. Pedidos incompletos mostram os candidatos ou um campo de valor, e a escolha cria a prévia pela rota dedicada, sem reinterpretar texto. **Histórico do campo** consulta `GET /api/data-changes` ao ser aberto. A fase do cartão fica na mensagem, então reabrir a conversa não oferece confirmar de novo. Sem `data_change` na resposta, como em um backend anterior à S5-06, nenhum cartão aparece.

### Validações e erros

- O frontend valida texto e gera áudio dentro do contrato antes de enviar. O backend revalida bytes, codec, taxa, canais, profundidade, duração, tamanho e fala audível; uma indicação MIME do navegador não substitui essa validação.
- Falhas 400, 401, 403, 413, 422, 429, 502, 503 e 504 recebem mensagens próprias. Respostas inesperadas, HTML de proxy e erros de rede usam uma mensagem genérica, sem traceback ou mensagem privada do provedor.
- A espera HTTP é limitada a 120 segundos. Esse teto evita espera infinita e não constitui evidência de cumprimento do RNF05 de 10 segundos.
- A API de áudio continua usando a identidade simulada documentada. A autenticação real Entra ID, autorização por `access_rules`, conexão com dados corporativos e persistência não são implementadas por esta integração.

## Acessibilidade e responsividade

O primeiro Tab revela **Pular para o campo de mensagem**, que leva o foco direto ao campo. A lista de mensagens recebe foco para ser rolada pelas setas, e os cards de sugestão e de alteração de dados levam o foco ao resultado quando os botões somem. Campos e botões têm nomes acessíveis, com o texto visível contido no nome (WCAG 2.5.3); mensagens usam `role=log`, `aria-live` e `aria-busy`; erros usam `role=alert`. Os diálogos Radix oferecem navegação por teclado e fechamento por Escape. O foco dos botões de classificação e transcrição permanece visível. As cores secundárias e o tema escuro foram ajustados para corrigir as violações de contraste encontradas pelo axe. A aplicação respeita `prefers-reduced-motion`.

Os testes automatizados cobrem 1440 × 900 e 390 × 844 em Chromium. Esse recorte não equivale a uma auditoria manual completa com leitores de tela nem garante outros navegadores.

## Testes e evidências

```powershell
# Em src/frontend
npm run lint
npm run format:check
npm run test:coverage
npm run build
npx playwright install chromium
npm run test:e2e
```

O Vitest executa testes por componente, hooks e integração da store com o cliente HTTP. `coverage/index.html` apresenta a cobertura e `coverage/coverage-summary.json` permite comparação automática. O Playwright inicia um frontend e um backend exclusivos nas portas 5174 e 8001. As rotas FastAPI e a validação WAV são reais; somente classificação e provedores externos são substituídos no servidor de teste `app/tests/e2e_server.py`. A gravação usa microfone sintético do Chromium.

O servidor E2E não é uma configuração de produção. Ele não usa chaves reais e não é importado por `app.main`. Os testes são determinísticos e não comprovam disponibilidade de Azure/Gemini nem desempenho em rede corporativa.

A automação de GitLab em `.gitlab-ci.yml` executa lint, formatação, testes com cobertura, build, contratos do backend e testes de navegador. O job de API usa o recorte determinístico; o benchmark completo do classificador pode ser executado localmente com as dependências de PLN e o encoder baixado.

Veja a [matriz de casos e os resultados registrados](TESTES.md). Para uma verificação real com provedores, configure as credenciais, rode `app.main`, envie uma pergunta por texto e por microfone e confira a resposta, as fontes e as métricas. Essa etapa deve ser registrada separadamente dos testes com substitutos.
