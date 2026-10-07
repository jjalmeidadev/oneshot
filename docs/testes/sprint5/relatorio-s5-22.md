# S5-22 — Inventário, cobertura e revisão QA

Data da medição: 05/10/2026. Issue: [#276](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/276). Branch de trabalho: `test/completar-testes-unitarios`.

## Descoberta com aiox-analyst

O produto é um agente conversacional para consulta ao portfólio do Metrô, com fontes documentais, entrada de texto/áudio e ações guiadas de relatório e alerta. `docs/Projeto.md` define o produto; `docs/GestaoProjeto.md` e `docs/backlog/sprint-05-issues.csv` vinculam a S5-22 ao barema, item 6, e às dependências S5-20 e S5-21.

O frontend principal (`src/frontend`) usa React, TypeScript, Vite, componentes Radix, Vitest e Testing Library. `App` compõe os providers de tema, tooltip e chat; `AppShell` organiza conversa, mensagens, entrada, documentos e notificações. A store coordena contratos HTTP, contexto, cancelamento e workflows. A API FastAPI (`src/backend/app`) contém módulos de áudio, PLN, RAG, banco, relatórios e alertas. `src/database`, `src/notebooks`, `src/agent`, `infra` e `scripts` mantêm dados, experimentos, workflow e operação. `src/lp` é uma landing page/demonstração separada, fora do job `frontend-unit` e do recorte de interface da S5-22.

O checkout contém os controles de proatividade, painéis responsivos e testes de navegação por teclado associados às S5-20/S5-21. Não se afirma o aceite remoto dessas dependências. O working tree estava limpo no início. Não havia `docs/stories/` neste checkout; a tarefa #276 foi espelhada em `docs/stories/s5-22-testes-unitarios.md` para acompanhar checklist e arquivos.

A pipeline já executava cobertura, mas não definia mínimos. A suíte possuía testes do chat, documentos, workflows, gravação, store e cliente HTTP. UI, barra lateral e tema eram principalmente exercitados de forma indireta; `Skeleton` não tinha teste. A central de notificações e o card de alerta possuíam apenas casos básicos. Não se usa a primeira rodada com timeout como baseline de cobertura válido.

## Inventário e rastreabilidade por componente

São 38 módulos em `src/components`, incluindo os componentes compostos abaixo. Os providers e `App` também participam da suíte. Os caminhos da tabela são relativos a `src/frontend/src`; arquivos de teste coletivos são válidos e evitam duplicar cenários já existentes. Reexports de Radix são exercitados pela composição real, sem mock dos próprios componentes.

| Módulo / componentes                                                                                               | Teste                                                                                                | Comportamento verificado                                                        |
| ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `chat/chat-empty-state.tsx` — ChatEmptyState                                                                       | `components/components.test.tsx`                                                                     | Sugestão selecionada encaminha prompt                                           |
| `chat/chat-header.tsx` — ChatHeader                                                                                | `components/components.test.tsx`                                                                     | Abre conversas e documentos com nome acessível                                  |
| `chat/intent-badge.tsx` — IntentBadge                                                                              | `components/components.test.tsx`                                                                     | Exibe classificação recebida                                                    |
| `chat/markdown-message.tsx` — MarkdownMessage                                                                      | `components/components.test.tsx`, `chat/message-rendering.test.tsx`                                  | Markdown sem execução de HTML; listas, tabela, código, citação e links          |
| `chat/message-bubble.tsx` — MessageBubble, UserMessage, AssistantMessage                                           | `components/components.test.tsx`, `chat/message-rendering.test.tsx`                                  | Erro controlado, transcrição e decisão proativa explícita                       |
| `chat/message-list.tsx` — MessageList                                                                              | `components/components.test.tsx`                                                                     | Log ocupado, mensagens e etapa de processamento                                 |
| `chat/source-citations.tsx` — SourceCitations                                                                      | `components/components.test.tsx`, `documents/references.test.tsx`, `chat/message-rendering.test.tsx` | Seleção, abstinência e ausência de fontes                                       |
| `chat/typing-indicator.tsx` — TypingIndicator                                                                      | `chat/proactive-suggestion.test.tsx`                                                                 | Atualiza texto da etapa                                                         |
| `chat/proactive-suggestion.tsx` — ProactiveSuggestion                                                              | `chat/proactive-suggestion.test.tsx`                                                                 | Aceitar/recusar, bloqueio durante resolução, estado final                       |
| `chat/report-workflow-card.tsx` — ReportWorkflowCard                                                               | `chat/report-workflow-card.test.tsx`                                                                 | Opção, intervalo, seleção múltipla, texto, confirmação, cancelamento e download |
| `chat/alert-workflow-card.tsx` — AlertWorkflowCard                                                                 | `chat/alert-workflow-card.test.tsx`, `chat/alert-workflow-card.behavior.test.tsx`                    | Opção, limiar, confirmação concorrente, erro/repetição e cancelamento           |
| `composer/audio-button.tsx` — AudioButton                                                                          | `components/components.test.tsx`                                                                     | Bloqueia captura sem suporte                                                    |
| `composer/composer.tsx` — Composer                                                                                 | `components/components.test.tsx`                                                                     | Enter, Shift+Enter, limite de texto e interrupção                               |
| `composer/intent-toggle.tsx` — IntentToggle                                                                        | `components/components.test.tsx`                                                                     | Encaminha alteração do switch                                                   |
| `composer/proactivity-toggle.tsx` — ProactivityToggle                                                              | `components/components.test.tsx`                                                                     | Ativa sugestão opcional                                                         |
| `composer/recording-bar.tsx` — RecordingBar, RecordingPreview                                                      | `components/components.test.tsx`                                                                     | Concluir/descartar e bloquear formato de áudio incompatível                     |
| `documents/document-card.tsx` — DocumentCard                                                                       | `components/components.test.tsx`                                                                     | Seleção indicada e abertura                                                     |
| `documents/document-panel.tsx` — DocumentPanel                                                                     | `components/components.test.tsx`                                                                     | Navegação por abas e detalhes da resposta                                       |
| `documents/document-viewer.tsx` — DocumentViewer                                                                   | `components/components.test.tsx`, `documents/references.test.tsx`                                    | Trecho, origem, períodos e falta de trecho                                      |
| `documents/response-details.tsx` — ResponseDetails                                                                 | `components/components.test.tsx`, `documents/references.test.tsx`                                    | Métricas disponíveis e ausência honesta                                         |
| `layout/app-shell.tsx` — AppShell                                                                                  | `layout/app-shell.test.tsx`                                                                          | Integração de envio, fontes, conversas, tema, erro e diálogo móvel              |
| `layout/theme-toggle.tsx` — ThemeToggle                                                                            | `state/theme-provider.test.tsx`                                                                      | Alternância por teclado e nome acessível                                        |
| `notifications/notification-center.tsx` — NotificationCenter                                                       | `notifications/notification-center.test.tsx`, `notifications/notification-center.behavior.test.tsx`  | Resumo, leitura, pausa/retomada/cancelamento, falha e polling                   |
| `sidebar/conversation-item.tsx` — ConversationItem                                                                 | `components/components.test.tsx`, `sidebar/sidebar.test.tsx`                                         | Seleção/exclusão e teclado                                                      |
| `sidebar/conversation-sidebar.tsx` — ConversationSidebar                                                           | `sidebar/sidebar.test.tsx`                                                                           | Agrupamento, busca por título/conteúdo, ausência, nova conversa e fechar        |
| `sidebar/user-card.tsx` — UserCard                                                                                 | `sidebar/sidebar.test.tsx`                                                                           | Campo protegido, edição e ausência de persistência                              |
| `ui/badge.tsx` — Badge                                                                                             | `ui/ui.test.tsx`                                                                                     | Conteúdo, tom e atributos                                                       |
| `ui/button.tsx` — Button                                                                                           | `ui/ui.test.tsx`                                                                                     | Clique, ref, disabled e asChild                                                 |
| `ui/dialog.tsx` — Dialog, DialogTrigger, DialogContent, DialogOverlay, DialogTitle, DialogDescription, DialogClose | `ui/ui.test.tsx`                                                                                     | Composição do diálogo, três posições, descrição, fechar, Escape e foco          |
| `ui/empty-state.tsx` — EmptyState                                                                                  | `ui/ui.test.tsx`                                                                                     | Descrição, ação e versão compacta                                               |
| `ui/meter.tsx` — Meter                                                                                             | `ui/ui.test.tsx`                                                                                     | Limites, valor acessível e marcador opcional                                    |
| `ui/scroll-area.tsx` — ScrollArea, ScrollBar                                                                       | `ui/ui.test.tsx`                                                                                     | Refs, conteúdo e orientações                                                    |
| `ui/separator.tsx` — Separator                                                                                     | `ui/ui.test.tsx`                                                                                     | Decoração e separador vertical acessível                                        |
| `ui/skeleton.tsx` — Skeleton                                                                                       | `ui/ui.test.tsx`                                                                                     | Estado decorativo e atributos                                                   |
| `ui/switch.tsx` — Switch                                                                                           | `ui/ui.test.tsx`                                                                                     | Teclado e disabled                                                              |
| `ui/tabs.tsx` — Tabs, TabsList, TabsTrigger, TabsContent                                                           | `ui/ui.test.tsx`                                                                                     | Associação de painel e seleção por setas                                        |
| `ui/textarea.tsx` — Textarea                                                                                       | `ui/ui.test.tsx`                                                                                     | Edição, ref e disabled                                                          |
| `ui/tooltip.tsx` — TooltipProvider, Tooltip, TooltipTrigger, TooltipContent                                        | `ui/ui.test.tsx`                                                                                     | Ajuda por foco e descrição acessível                                            |
| `state/theme-provider.tsx` — ThemeProvider                                                                         | `state/theme-provider.test.tsx`                                                                      | Tema na raiz móvel, preferência do sistema, armazenamento bloqueado e cleanup   |
| `state/chat-store.tsx` — ChatStoreProvider                                                                         | `state/chat-store.test.tsx`                                                                          | Estado inicial, envio/contexto, concorrência, áudio e cancelamento              |
| `App.tsx` — App                                                                                                    | `components/layout/app-shell.test.tsx`                                                               | Composição real de providers e interface                                        |

## Política de cobertura

O mínimo global é **80% de linhas, 80% de instruções, 75% de funções e 70% de ramificações**. A issue exige definir um mínimo, sem indicar percentual. Estes valores são a política técnica desta entrega, mantendo quatro métricas explícitas para componentes, hooks, bibliotecas e estado; não se apresentam como percentual imposto pelo barema. Funções e ramificações incluem caminhos de áudio e workflows que vão além do requisito de um teste por componente.

O glob `src/components/**/*.tsx` exige por arquivo ao menos 1% de linhas, instruções e funções. Esse piso detecta arquivos sem execução; não significa que 1% seja a meta global, nem comprova sozinho teste de todos os exports de um módulo. A tabela e as asserções da suíte fazem essa rastreabilidade. O `include` mantém arquivos não importados no denominador e passa a incluir `App.tsx`; não foram removidos arquivos de produção para elevar o resultado. Os únicos excludes são os já existentes, incluindo o barrel e os schemas de tipos da API.

Os limites são compartilhados por `npm run test:coverage` e pelo job `frontend-unit`. Resultado abaixo do mínimo encerra o Vitest com falha. O job não usa `allow_failure` ou supressão de exit code. JUnit é publicado em `test-results/unit/junit.xml`; HTML, JSON summary e Cobertura em `coverage/`. Os reports GitLab facilitam consulta no MR; a aprovação da pipeline remota precisa ser conferida após publicação.

Referência de configuração: [Vitest — coverage thresholds](https://vitest.dev/config/coverage.html#coverage-thresholds).

## Execução e evidência

**112 testes aprovados em 18 arquivos**, incluindo **48 casos novos em sete arquivos**. A cobertura contém os 38 módulos de componentes; nenhum tem zero funções executadas. No Windows deste ambiente, usa-se `npm.cmd` para contornar a política de execução do wrapper PowerShell; os scripts npm são os mesmos do Linux na pipeline.

| Métrica      | Coberto / total | Medição | Mínimo |
| ------------ | --------------- | ------- | ------ |
| Linhas       | 754 / 873       | 86,36%  | 80%    |
| Instruções   | 801 / 954       | 83,96%  | 80%    |
| Funções      | 254 / 296       | 85,81%  | 75%    |
| Ramificações | 590 / 784       | 75,25%  | 70%    |

Lint, typecheck, formatação, cobertura, `npm test` sem cobertura e build passaram. O único ajuste em teste existente foi um timeout de 15 segundos, restrito ao fluxo integrado de `AppShell`: sua execução instrumentada ultrapassou os 5 segundos padrão. As asserções e os timeouts de espera internos foram preservados.

A prova negativa adicionou temporariamente `src/components/ui/s5-22-uncovered-fixture.tsx`, sem teste, e executou a suíte de UI com cobertura restrita ao diretório UI. Os 18 casos passaram, o agregado ficou acima dos limites globais e o processo saiu com **código 1**, apontando linhas, instruções e funções em 0% na fixture contra o piso por arquivo de 1%. A fixture foi removida em `finally`; os relatórios da rodada completa foram preservados usando diretório e JUnit separados na prova negativa. Não há fixture sem teste na entrega.

Evidências finais: [pasta de evidências](evidencias-s5-22/), incluindo logs dos comandos, JSON com cobertura por arquivo e resultado negativo do gate. Os reports XML/HTML completos também são regenerados em `src/frontend/coverage/` e `src/frontend/test-results/unit/`, sem necessidade de versionar assets de relatório.

```powershell
cd src/frontend
npm.cmd run lint
npm.cmd run typecheck
npm.cmd test
npm.cmd run test:coverage
npm.cmd run format:check
npm.cmd run build
```

## Revisão QA final

**Veredito local: CONCERNS quanto ao fechamento administrativo; critérios técnicos aprovados.** Revisão de critérios e raciocínio feita após a produção, na mesma sessão QA, sem revisão independente por outro agente ou pessoa. Não equivale a revisão humana de outra frente. A revisão CodeRabbit foi rejeitada pelo mecanismo automático de aprovação por possível envio do diff a terceiro. Não houve envio nem resultado CodeRabbit.

| Critério da tarefa                       | Evidência / resultado                                                                                | Situação               |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------- |
| Levantar componentes sem teste           | Inventário dos 38 módulos e mapa de exports/testes acima                                             | Atendido               |
| Escrever testes faltantes                | 48 novos casos; 112 aprovados na suíte completa                                                      | Atendido               |
| Todo componente tem ao menos um teste    | Inventário, asserções de comportamento, execução dos 38 módulos, teste de providers e composição App | Atendido localmente    |
| Definir limite na pipeline               | Limites de quatro métricas no Vitest; job frontend-unit executa cobertura e falha abaixo deles       | Atendido no código     |
| Cobertura registrada no MR               | Medição e descrição prontas em `mr-s5-22.md`; MR remoto ainda não publicado                          | Pendente no GitLab     |
| Evidência registrada                     | Logs, resumo JSON, inventário e prova negativa                                                       | Atendido localmente    |
| Assignee, revisor, labels e milestone    | Planejamento local identificado; campos remotos não conferidos                                       | Pendente no GitLab     |
| Aprovação com comentário de outra frente | Não há aprovação produzida ou presumida                                                              | Pendente no GitLab     |
| Closes apontando a issue                 | `Closes #276` incluído na descrição preparada                                                        | Pendente de publicação |

A revisão confirma asserções de saída e interação, uso de componentes reais de UI, mocks limitados às bordas/store nos testes isolados e restauração de spies/globals pelo setup. Testes verificam decisões concorrentes, estados finais, callbacks, falhas, navegação por teclado e cleanup de listeners/polling. Nenhum código funcional ou dependência foi alterado. Não há snapshots de marcação usados como única evidência, `.skip`, `.only` ou supressão de erro para obter aprovação.

Riscos residuais: mínimo por arquivo detecta ausência total, mas não mede todos os exports sozinho; a matriz precisa acompanhar novos exports. Mocks de store/API validam contrato de interação de componente, não disponibilidade dos provedores nem persistência real. Permanecem caminhos sem cobertura em áudio, API de alerta e workflows da store; a medição global inclui esses caminhos. Não se afirma 100% de cobertura, validação E2E adicional (S5-23) ou conformidade integral de acessibilidade (S5-21).

O MR, seu comentário de revisão, aprovação, labels/milestone e aceite das dependências são condições externas que não podem ser marcadas como concluídas por esta execução local.
