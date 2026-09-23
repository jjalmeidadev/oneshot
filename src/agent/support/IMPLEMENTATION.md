# Implementacao do workflow `transacao_gerar_relatorio`

## Contrato conversacional

O frontend conduz as etapas `scope_type`, `scope`, `period`, `audience`,
`purpose`, `emphasis`, `additional_context`, `confirmation` e `execution`.
Cada resposta envia a revisao observada e um `client_action_id`; respostas
repetidas sao idempotentes e revisoes obsoletas recebem `409`.

Rotas:

- `POST /api/workflow-sessions`;
- `GET /api/workflow-sessions/{session_id}`;
- `POST /api/workflow-sessions/{session_id}/answers`;
- `POST /api/workflow-sessions/{session_id}/confirm`;
- `POST /api/workflow-sessions/{session_id}/cancel`.

A confirmacao usa o contrato HMAC ja existente. Nenhuma execucao comeca antes
de `ready_for_confirmation`.

## Power Automate

O backend chama o gatilho HTTP autenticado e recebe `202` com `flow_run_id`.
O fluxo recebe somente o pedido confirmado e o snapshot autorizado. AI Builder
pode normalizar o contexto, redigir uma sintese e revisar fundamentacao usando
os schemas fixos em `ai-builder/`.

O retorno e feito em:

`POST /api/integrations/power-automate/report-results`

com `X-Callback-Token`, `callback_id`, IDs de correlacao, estado terminal e
`result`. O callback nao envia arquivo nem URL externa. O backend valida fontes
e revisao; conteudo reprovado cai para a redacao deterministica.

## Documento e armazenamento

O backend gera o DOCX com `python-docx`, calcula SHA-256 e o envia ao bucket
privado `generated-reports` quando `REPORT_STORAGE_MODE=supabase`. A service
role nunca e entregue ao navegador. O download sempre passa pelo endpoint
autenticado `/api/report-requests/{execution_id}/artifact`, que transmite o
arquivo ao chat sem URL publica permanente.

## Persistencia e auditoria

As migrations `05` e `07` cobrem execucoes, artefatos, callbacks, snapshot,
sessoes e respostas. A migration `09` cria de forma idempotente o bucket
privado `generated-reports`; o rollback usa
`python -m scripts.rollback_report_storage_bucket` e a API oficial recusa
remover um bucket que contenha objetos. A migration `11` habilita RLS e revoga
todo acesso de `anon` e `authenticated` nas cinco tabelas internas. Os
principais IDs sao `conversation_id`, `interaction_id`,
`session_id`, `correlation_id`, `execution_id`, `flow_run_id`, `callback_id`,
`artifact_id`, `idempotency_key` e `client_action_id`.

## Fonte de dados de portfolio

A variavel `REPORT_PORTFOLIO_SOURCE` define de onde vem o conteudo do relatorio
(projetos, riscos, marcos, beneficios, mudancas e avanco):

- `synthetic` (padrao): massa em `app/reports/data/synthetic_portfolio.json`.
- `database`: tabelas reais do PostgreSQL (`projects`, `risk_issue_items`,
  `project_deliverables_milestones`, `project_benefits`, `change_records`,
  `project_status_updates`, `project_progress_updates`). O identificador publico
  de escopo e o `code` (ex.: `PRJ-0442`). Para popular a base, aplique o seed
  `src/database/sql/13_seed_portfolio_report_data.sql` (massa em portugues) e o
  rollback `14`.

O `WorkflowService` usa a mesma fonte do `ReportService`: a lista de escopos
apresentada no chat e a geracao do relatorio compartilham `REPORT_PORTFOLIO_SOURCE`,
evitando que o card ofereca um escopo que a geracao nao encontraria.

## Configuracao isolada

```dotenv
REPORT_EXECUTION_MODE=power_automate_simulator
REPORT_REPOSITORY_MODE=memory
REPORT_STORAGE_MODE=local
REPORT_PORTFOLIO_SOURCE=synthetic
REPORT_SIMULATED_IDENTITIES={"token-local":{"subject":"usuario-1","role":"pmo","can_export":true,"allow_all":true}}
REPORT_CONFIRMATION_SECRET=defina-no-ambiente
REPORT_CALLBACK_TOKEN=defina-no-ambiente
```

Para producao, use repositorio `database`, armazenamento `supabase`, aplique as
migrations e configure `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`,
`POWER_AUTOMATE_REPORT_TRIGGER_URL`, `POWER_AUTOMATE_TRIGGER_TOKEN` e
`REPORT_CALLBACK_BASE_URL` por referencias seguras.
