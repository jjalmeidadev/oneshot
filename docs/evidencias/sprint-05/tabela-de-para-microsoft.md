# S5-44 (#298) — Evidência da tabela de-para Microsoft

Data do recorte: **06/10/2026 (America/Sao_Paulo)**. Entrega: [Projeto.md, Seção 6.4](../../Projeto.md#64-tabela-de-para-para-o-ecossistema-microsoft-do-metrô). Registro: [S5-44](../../stories/S5-44.md).

## Método e limites

Análise brownfield com `aiox-analyst`: requisitos e backlog → documentação e decisões de gestão → código, schemas, SQL e configuração → comparação das branches → correspondências verificadas no Microsoft Learn. O objetivo é documentar possibilidades de reaproveitamento; não selecionar unilateralmente uma nova arquitetura ou afirmar homologação Microsoft.

O checkout estava limpo em `docs/tabela-de-para-microsoft`, HEAD `58da95da707e0ed05a4a3e0e676fa1d52250becc`. Foram atualizadas as referências com `git fetch origin --prune`, sem merge ou checkout de outras branches. `origin/develop` aponta ao mesmo commit. `origin/hmg` = `9c11d9a5884a77210644a0e5f4bf44c51e04e533`; `origin/main` = `bc30be264464e884c6ae0436b683814bfb8638bd`. Esses ponteiros são evidência de Git, não do commit efetivamente rodando em um servidor.

Os heads dos MRs da imagem foram obtidos diretamente por `refs/merge-requests/<iid>/head`, preservados como `origin/mr/<iid>`. Cada um foi comparado por `git diff origin/develop...origin/mr/<iid>` e `git merge-base --is-ancestor`. Nenhum dos oito heads é ancestral do `develop` do recorte. A imagem registra MRs abertos quando capturada; Git permite verificar conteúdo/ancestralidade, não aprovação, assignee, pipeline atual ou estado aberto/fechado da interface GitLab. A consulta anônima à API das issues #273/#297/#298 retornou HTTP 404, sem permitir confirmar seus metadados atuais.

## Branches da imagem

Links dos MRs: `https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/merge_requests/<iid>`.

| MR / issue | Branch / head verificado | Mudança examinada | Consequência para a tabela |
|---|---|---|---|
| [!130](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/merge_requests/130) / #285 | `test/requisitos0709` / `43e763cc` | Protocolos/evidências RNF07–RNF09, teste de contrato RNF08 e validação de estrutura JSON da fonte RAG, com tratamento de erro. | É validação e robustez da fonte; não é SharePoint real, tenant Teams ou certificação Microsoft. |
| [!129](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/merge_requests/129) / #271 | `feature/271-renderizar-blocos` / `41140ea8` | Renderização de tabela, indicador e destaque, tipos frontend e testes/acessibilidade. | UI proposta depende dos blocos compatíveis; não é cartão Teams pronto. |
| [!128](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/merge_requests/128) / #270 | `feature/270-blocos-resposta` / `32689d95` | Contrato 1.2.0, `blocks`, schema e geração derivada das afirmações verificadas. | `develop` mantém 1.1.0; preservar citações ao integrar/adaptar. |
| [!127](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/merge_requests/127) / #281 | `fix/bloquear-dado-sensivel` / `ea572497` | `sensitive_data.py`, bloqueio de pergunta, mascaramento de fonte, barreira de prompt e auditoria sanitizada. | Controle preventivo ainda proposto; política DLP da Power Platform não o substitui no cliente Python. |
| [!124](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/merge_requests/124) / #276 | `test/completar-testes-unitarios` / `7b8d5e15` | Inventário/cobertura, testes de comportamento frontend e script typecheck. | Aproveitar cenários após integração; a cobertura daquela branch não caracteriza o checkout atual. |
| [!123](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/merge_requests/123) / #269 | `feat/s5-15-resposta-audio-tts` / `5216a2cb` | Síntese Azure, resposta com áudio e reprodução/testes no frontend. | Separar STT integrado de TTS proposto. |
| [!120](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/merge_requests/120) / #255 | `feature/255-gate-marcadores-integracao` / `e1e1c307` | Gate de marcadores de conflito, hook, testes e marcação de integração na CI. | Gate proposto é portátil como lógica; YAML GitLab precisa adaptação se houver troca de CI. |
| [!117](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/merge_requests/117) / #279 | `bugfix/corrigir-auditoria-fluxo-guiado` / `dff223b1` | Eventos fora de escopo e workflows, correlação, distinção de chamada sem classificador e SQL de backfill. | Reaproveitar semântica, mas não declarar correção já integrada. |

A branch adicional `origin/docs/documentacao-tecnica-final`, head `b9c45e0e`, não apresentou diferença no comparativo de conteúdo `git diff origin/develop...origin/docs/documentacao-tecnica-final` nesta coleta. Não foi localizada nela uma decisão nova de conclusão da S5-19. A ausência no conteúdo examinado não prova o estado da issue externa.

## Inventário técnico examinado

| Área | Evidências principais e comportamento observado |
|---|---|
| Canal/UI | `src/frontend/package.json`, `App.tsx`, componentes `chat`, `lib/api`, `state`; React/Vite/TypeScript, histórico, fontes, proatividade, workflows e central de notificações. `src/lp` é landing page separada, fora do fluxo de atendimento. |
| API e orquestração | `src/backend/app/main.py`, `pipeline.py`, `gemini/schemas.py`; FastAPI, entrada comum de texto/transcrição, diretivas guiadas e contrato 1.1.0. |
| PLN | `nlp/preprocessing.py`, `entities.py`, `classifier.py`, `inference.py`; normalização própria/NLTK, léxico, classificação hierárquica, TF-IDF + BERTimbau, limiares e catálogo. Encoder com revisão imutável. |
| Conhecimento | `rag/database.py`, `sharepoint.py`, JSON em `rag/data/sharepoint`, SQL `04_rag_synthetic_data.sql`; consulta SQL com filtro de acesso e fallback JSON quando banco não configurado. Busca lexical; montagem de contexto com atributos e localizadores. Não há conector Graph autenticado nem índice vetorial documental ativo. |
| Resposta e proatividade | `gemini/client.py`, `evidence.py`, schemas, `rag/proactivity.py`, `proactive_confirmation.py`; Gemini/OpenRouter, afirmações/citações verificadas e confirmação da sugestão. Não há cliente Azure OpenAI integrado. |
| Voz | `audio/service.py`, `validation.py`, `transcription.py`, `vhs.py`; validação, STT Azure, retry/cache local e pipeline comum. TTS somente no MR !123. |
| Identidade | `security/access.py`, `security/http.py`, SQL `20_auth_access_foundation.sql`, frontend `lib/api`; token confirmado no Supabase Auth, perfil/escopo resolvidos no servidor e operações read/write/export. Entra ID previsto, não integrado. |
| Relatório | `reports/workflow.py`, `state_machine.py`, `service.py`, `sources.py`, `repository.py`, `rendering.py`, `storage.py`; snapshot, confirmação, máquina de estados, callback, DOCX via python-docx, persistência configurável e download autorizado. |
| Artefatos Microsoft | `src/agent/README.md`, `support/IMPLEMENTATION.md`, blueprint JSON Power Automate, prompts AI Builder, OpenAPI 3.0.3, manifesto Word e fixtures; referências portáveis e modo real condicionado à homologação. `ONESHOT` é exportação legada, não runtime vigente. |
| Alertas/mensageria | `alerts/workflow.py`, `source.py`, `service.py`, `repository.py`, `messaging.py`, `worker.py`, `router.py`; inscrição, scheduler, outbox transacional, RabbitMQ, evaluator/notifier, DLQ, tentativa de entrega, webhook e central web. |
| Banco/auditoria | `database/connection.py`, `tracing.py`, scripts SQL e documentação em `src/database`; PostgreSQL/Supabase, pool, catálogo, fontes e rastreabilidade. Scripts de auth/storage/RLS exigem adaptação fora do Supabase. |
| Implantação/operação | `compose.prod.yml`, `compose.rabbitmq.yml`, Dockerfiles backend/frontend/notebook, Nginx, `infra/aws`, `scripts/aws`, Seção 10.2; EC2/ECR, workers, CloudWatch, segredos externos e túnel temporário. Compose mantém relatório memory/local. |
| Engenharia/avaliação | `.gitlab-ci.yml`, `app/tests`, Vitest/Playwright, benchmarks/RNFs e `src/notebooks`; CI existente, datasets sintéticos, treino/métricas/artefatos e notebook opcional. |
| Framework de apoio | `.aiox-core`, `.codex`, projeções de agentes e `AGENTS.md`; ferramentas de desenvolvimento/documentação, sem papel no runtime do agente do Metrô. Não se confundem com o componente de atendimento. |

## Reconciliação com os artefatos de arquitetura

- `docs/diagrams/componentes-metro-5.2.puml` descreve Teams, Entra, Copilot, SharePoint, embeddings/índice e extratores como desenho de responsabilidades. O código atual executa a substituição Copilot por workflows próprios e recuperação lexical.
- `docs/diagrams/implantacao-poc.puml` e Seções 6.1–6.3 preservam uma fase anterior, tratando Docker/CI/Azure como futuro. A Seção 10.2 e os arquivos de infraestrutura comprovam Docker/CI/AWS no recorte.
- `docs/GestaoProjeto.md` registra a indisponibilidade do Copilot Studio na Frente D e reafirma workflows próprios, RabbitMQ, Supabase e AWS no planejamento da Sprint 5.
- As afirmações sobre Copilot/GPT na Seção 9.2.7 precisam de reconciliação pela S5-43. A S5-44 não certifica esses diagramas nem substitui a task de revisão arquitetural.
- S5-19 (#273) e S5-18 (#272) são condicionantes de canal/integração, sem implementação ou homologação demonstrada na base e nos MRs examinados.

## Fontes Microsoft

Links oficiais ficam junto das respectivas linhas na Seção 6.4. Foram consultadas responsabilidades e limites de Teams tabs, Container Apps, Azure ML, Foundry, Microsoft Graph/SharePoint, AI Search, PostgreSQL Flexible Server, Blob Storage, Speech, Power Platform data policies, Word Online, prompts Microsoft, Service Bus/AMQP 1.0, custom connectors/OpenAPI, Key Vault, Application Insights e Azure Pipelines. As correspondências e o esforço são análise do projeto, não recomendação de implantação já aprovada pelo Metrô.

## Verificações locais

Parecer independente: [revisão aiox-qa](../../qa/S5-44-tabela-de-para-microsoft.md), com aprovação do conteúdo documental e ressalvas de encerramento externo.

- `git diff --check`: aprovado após inclusão da seção.
- Verificação programática da Seção 6.4: nove títulos/âncoras conferidos, todos os links locais resolvidos e tabelas com a quantidade correta de colunas.
- `npm.cmd run lint` em `src/frontend`: aprovado.
- `npm.cmd run typecheck`: script inexistente no checkout. `build` inclui `tsc --noEmit`, usado como alternativa disponível.
- `npm.cmd run build`: aprovado após restauração das dependências pelo lockfile; inclui `tsc --noEmit` aprovado e build Vite com 2.601 módulos transformados.
- `npm.cmd test -- --pool=forks --maxWorkers=1 --testTimeout=10000 --hookTimeout=10000`: aprovado após restauração das dependências; **14 suites e 90 testes passaram**, exit 0, duração de 151,41 s. A opção de pool foi aplicada somente à execução, sem alterar a configuração do repositório.
- A chamada `npm` simples foi bloqueada pela política PowerShell para `npm.ps1`; foi utilizada a entrada `npm.cmd`, sem alteração da política da máquina.

A primeira instalação local não continha `@radix-ui/react-popover`, embora declarado no manifest/lockfile. Isso causou TS2307 no build/tsc e erros de importação em quatro suites: dez suites e 68 testes executados passaram, mas a execução terminou com exit 1. A tentativa inicial Vitest também foi impedida pelo sandbox e a execução em threads foi interrompida após cerca de quatro minutos sem casos emitidos; o pool `forks` produziu resultados. As dependências foram restauradas com `npm.cmd ci --ignore-scripts --prefer-offline`, exit 0, sem alterar manifest ou lockfile; lint/build foram repetidos com sucesso. O cache temporário criado foi removido. O npm alertou que o Node local `24.14.0` está abaixo da versão `24.15.0` declarada por jsdom no lockfile; isso é um limite do ambiente de verificação, não alteração da task.

Os resultados de engenharia são do checkout e da instalação local; não reproduzem os pipelines das oito branches nem demonstram integração corporativa.

## Texto preparado para o MR

Título: `docs: mapear reaproveitamento da PoC no ecossistema Microsoft (#298)`

Descrição sugerida, a atualizar com o parecer QA e os resultados de verificação antes de publicação:

```markdown
A documentação não distinguia o reaproveitamento do código autoral da substituição das integrações da PoC por serviços Microsoft. A Seção 6.4 do Projeto.md passa a mapear componentes, equivalentes, reaproveitamento, esforço e limites com evidências do develop 58da95da e dos oito MRs de acompanhamento.

Inclui os caminhos condicionados para Teams, a indisponibilidade de Copilot Studio, a adaptação de identidade/dados/mensageria e a distinção entre mudanças integradas e propostas. Evidência e checklist: docs/evidencias/sprint-05/tabela-de-para-microsoft.md e docs/stories/S5-44.md. Parecer documental: docs/qa/S5-44-tabela-de-para-microsoft.md.

Validação: links/âncoras/tabelas, comparação das branches, git diff --check, lint e build (incluindo tsc --noEmit) aprovados. Resultado da suíte frontend e limites do ambiente estão registrados na evidência e no parecer QA. Nenhum código de execução foi alterado.

Para aprovação final: anexar decisão da S5-19, conferir revisão S5-43 e obter comentário do revisor de outra frente.

Closes #298
```

Este texto é uma preparação local. Não foi criado, aprovado ou publicado um MR nesta execução.
