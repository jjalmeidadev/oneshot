# Implementação dos workflows transacional e proativo

Este documento é a referência operacional dos dois workflows especializados do
projeto:

- `transacao_gerar_relatorio`: geração rastreável de relatório executivo;
- `alerta_prazo_atraso`: monitoramento recorrente de prazos e notificação interna.

Os dois começam no classificador de intenções, usam workflows guiados no chat,
exigem confirmação explícita e podem persistir seu estado no PostgreSQL. Depois
da confirmação, porém, seguem arquiteturas distintas: o relatório executa uma
tarefa delimitada e produz um DOCX; o alerta cria uma inscrição duradoura,
avaliada de forma assíncrona pelo scheduler e pelo RabbitMQ.

## 1. Visão comparativa

| Aspecto | `transacao_gerar_relatorio` | `alerta_prazo_atraso` |
| --- | --- | --- |
| Natureza | Transação sob demanda | Monitoramento proativo recorrente |
| Resultado | Artefato DOCX privado | Notificação disponível na aplicação |
| Execução principal | Backend local; adaptador Power Automate opcional | Backend, workers e RabbitMQ do próprio projeto |
| Persistência | Memória ou PostgreSQL; arquivo local ou Supabase Storage | Memória ou PostgreSQL; outbox transacional no modo persistente |
| Dependência externa obrigatória | Nenhuma no modo local | Nenhuma de Copilot Studio, Power Automate, Teams, e-mail ou webhook |
| Controle do usuário | Confirmar/cancelar workflow e baixar artefato | Confirmar/cancelar workflow; listar, pausar, retomar ou cancelar inscrição; ler notificação |

## 2. Workflow `transacao_gerar_relatorio`

### 2.1 Fluxo funcional

1. `POST /api/chat` classifica a intenção e devolve a diretiva
   `guided_workflow/start/transacao_gerar_relatorio` sem chamar o Gemini.
2. O frontend cria uma sessão e conduz `scope_type`, `scope`, `period`,
   `audience`, `purpose`, `emphasis`, `additional_context`, `confirmation` e
   `execution`.
3. Cada resposta envia a revisão observada e um `client_action_id`. Repetições
   são idempotentes e revisões obsoletas recebem `409`.
4. A preparação congela um snapshot autorizado das fontes e assina o pedido.
5. A confirmação HMAC cria uma execução idempotente.
6. No modo `local`, o backend redige e renderiza o DOCX. Nos modos opcionais de
   automação, envia o snapshot e valida o callback estruturado antes de renderizar.
7. O arquivo recebe SHA-256, é armazenado de forma privada e só é baixado por
   uma rota autenticada da própria API.

Nenhuma execução começa antes de `ready_for_confirmation`. O modo local é
completo e é o padrão; Copilot Studio não participa do runtime. Power Automate
é apenas um adaptador opcional já implementado, não uma dependência para gerar
relatórios no ambiente atual.

### 2.2 Contrato HTTP

- `POST /api/workflow-sessions`;
- `GET /api/workflow-sessions/{session_id}`;
- `POST /api/workflow-sessions/{session_id}/answers`;
- `POST /api/workflow-sessions/{session_id}/confirm`;
- `POST /api/workflow-sessions/{session_id}/cancel`;
- `POST /api/report-requests/prepare`;
- `POST /api/report-requests`;
- `GET /api/report-requests/{execution_id}`;
- `GET /api/report-requests/{execution_id}/artifact`;
- `POST /api/integrations/power-automate/report-results`, somente para o
  adaptador opcional.

O callback opcional usa `X-Callback-Token`, IDs de correlação e estado terminal.
Ele devolve JSON estruturado, nunca arquivo ou URL pública. Conteúdo automatizado
que não passa pelas validações é substituído pela redação determinística.

### 2.3 Documento e armazenamento

O backend gera o DOCX com `python-docx`, calcula SHA-256 e usa:

- `REPORT_STORAGE_MODE=local`: diretório privado do backend para desenvolvimento;
- `REPORT_STORAGE_MODE=supabase`: bucket privado `generated-reports`.

A service role nunca é entregue ao navegador. O download sempre passa por
`/api/report-requests/{execution_id}/artifact`, com autorização novamente
validada e sem URL pública permanente.

### 2.4 Banco, rastreabilidade e segurança

No modo `REPORT_REPOSITORY_MODE=database`, o fluxo usa:

- `report_executions`;
- `generated_reports`;
- `automation_callbacks`;
- `workflow_sessions`;
- `workflow_answers`;
- a trilha compartilhada em `audit_events`.

As migrations `05_report_generation.sql` e `07_guided_report_workflow.sql`
criam o modelo; `09_create_report_storage_bucket.sql` cria o bucket privado;
`11_secure_report_workflow_tables.sql` habilita RLS e revoga o acesso direto de
`anon` e `authenticated`. Os rollbacks correspondentes estão no mesmo diretório,
e o bucket usa `scripts/rollback_report_storage_bucket.py`, que recusa remover
um bucket com objetos.

Os principais identificadores são `conversation_id`, `interaction_id`,
`session_id`, `correlation_id`, `execution_id`, `flow_run_id`, `callback_id`,
`artifact_id`, `idempotency_key` e `client_action_id`.

### 2.5 Fonte de dados do portfólio

`REPORT_PORTFOLIO_SOURCE` define a origem dos projetos, riscos, marcos,
benefícios, mudanças e avanços:

- `synthetic`: massa em `app/reports/data/synthetic_portfolio.json`;
- `database`: tabelas `projects`, `risk_issue_items`,
  `project_deliverables_milestones`, `project_benefits`, `change_records`,
  `project_status_updates` e `project_progress_updates`.

O identificador público do escopo é o `code`, como `PRJ-0442`. A carga
reproduzível está em `13_seed_portfolio_report_data.sql`, com rollback em `14`.
O workflow e o gerador compartilham a mesma fonte, evitando oferecer no chat um
escopo que não possa ser processado.

### 2.6 Configuração mínima local

```dotenv
REPORT_EXECUTION_MODE=local
REPORT_REPOSITORY_MODE=memory
REPORT_STORAGE_MODE=local
REPORT_PORTFOLIO_SOURCE=synthetic
REPORT_SIMULATED_IDENTITIES={"token-local":{"subject":"usuario-1","role":"pmo","can_export":true,"allow_all":true}}
REPORT_CONFIRMATION_SECRET=defina-no-ambiente
```

Para persistência real, use `REPORT_REPOSITORY_MODE=database`, configure
`DATABASE_URL` ou `SUPABASE_DATABASE_URL` e aplique as migrations. O modo
`supabase` de armazenamento também exige `SUPABASE_URL` e
`SUPABASE_SERVICE_ROLE_KEY`. Somente o adaptador opcional exige as variáveis
`POWER_AUTOMATE_*`, `REPORT_CALLBACK_BASE_URL` e `REPORT_CALLBACK_TOKEN`.

## 3. Workflow `alerta_prazo_atraso`

### 3.1 Escopo e fluxo funcional

O alerta é inteiramente operado pelo projeto. Não depende de Copilot Studio,
Power Automate, Teams, e-mail ou webhook.

1. `POST /api/chat` classifica `alerta_prazo_atraso` e devolve a diretiva.
2. O frontend inicia uma sessão própria e coleta projeto, limiar, frequência e
   política de reenvio.
3. A confirmação assinada cria uma inscrição idempotente.
4. O scheduler encontra inscrições vencidas e grava
   `alert.evaluation.requested` na outbox, na mesma transação da atualização da
   próxima avaliação.
5. O publisher envia o evento persistente ao RabbitMQ.
6. O evaluator revalida o acesso, lê o cronograma e persiste o resultado.
7. Casos elegíveis gravam `alert.notification.requested` na outbox.
8. O notifier cria ocorrência, tentativa e notificação idempotentes.
9. A central do frontend consulta as notificações e registra sua leitura.

“Mais de N dias” usa o comparador estrito `gt`. A implementação usa dias
corridos no fuso `America/Sao_Paulo`; dias úteis são rejeitados enquanto não
houver calendário corporativo confiável. Itens concluídos ou cancelados não
disparam alertas. Dados anteriores ao limite `ALERT_DATA_FRESHNESS_DAYS`
produzem resultado `indeterminate`.

### 3.2 Contrato HTTP

- `POST /api/alert-workflow-sessions`;
- `GET /api/alert-workflow-sessions/{session_id}`;
- `POST /api/alert-workflow-sessions/{session_id}/answers`;
- `POST /api/alert-workflow-sessions/{session_id}/confirm`;
- `POST /api/alert-workflow-sessions/{session_id}/cancel`;
- `GET /api/alert-subscriptions`;
- `GET /api/alert-subscriptions/{subscription_id}`;
- `POST /api/alert-subscriptions/{subscription_id}/pause`;
- `POST /api/alert-subscriptions/{subscription_id}/resume`;
- `POST /api/alert-subscriptions/{subscription_id}/cancel`;
- `GET /api/notifications`;
- `POST /api/notifications/{notification_id}/read`.

As rotas usam a mesma identidade resolvida pelo backend e filtram inscrições e
notificações pelo sujeito autenticado. O acesso ao projeto é revalidado durante
cada avaliação; se for revogado, a inscrição é bloqueada sem expor conteúdo.

### 3.3 RabbitMQ, outbox e tolerância a falhas

O exchange durável `metro.alerts` publica em:

| Routing key/fila | Produtor | Consumidor |
| --- | --- | --- |
| `alert.evaluation.requested` | scheduler/outbox | evaluator |
| `alert.notification.requested` | evaluator/outbox | notifier |

Cada fila possui dead-letter no exchange `metro.alerts.dlx`. As mensagens são
persistentes, usam confirmação manual e fazem uma nova entrega antes da DLQ.
Falhas de publicação permanecem na outbox com backoff. O publisher reivindica
lotes no PostgreSQL com `FOR UPDATE SKIP LOCKED`, permitindo mais de uma
instância sem publicar o mesmo item simultaneamente. Após cinco tentativas o
evento fica com estado terminal `failed` e deixa de ser reivindicado, ficando
disponível para inspeção manual. O reenvio de notificações é ancorado na virada
do limiar (`(overdue - threshold_days) // resend_interval_days`), de modo que a
primeira notificação corresponde ao episódio inicial e os reenvios respeitam o
intervalo desde o cruzamento do limiar, não o total de dias de atraso.

A outbox elimina a janela entre commit no PostgreSQL e publicação AMQP. A chave
única `episode_key` e os demais identificadores idempotentes impedem que uma
reentrega gere notificações duplicadas. RabbitMQ é acessado por AMQP, não por
webhook; as operações do navegador usam REST.

### 3.4 Banco, estados e auditoria

`15_alert_deadline_flow.sql` amplia o workflow compartilhado e cria:

- `alert_subscriptions`;
- `alert_evaluations`;
- `alert_occurrences`;
- `alert_notifications`;
- `notification_delivery_attempts`;
- `message_outbox`.

Todas as seis tabelas têm RLS habilitado e privilégios diretos revogados de
`anon` e `authenticated`; somente a conexão segura do backend as acessa. O
rollback está em `16_rollback_alert_deadline_flow.sql`.

Estados persistidos:

- inscrição: `active`, `paused`, `cancelled`, `blocked`;
- avaliação: `matched`, `not_matched`, `indeterminate`, `failed`;
- ocorrência: `open`, `resolved`, `suppressed`;
- notificação: `pending`, `available`, `read`, `failed`;
- outbox: `pending`, `publishing`, `published`, `failed`.

`correlation_id` e os IDs de inscrição, avaliação, ocorrência, notificação,
evento e tentativa permitem reconstruir a cadeia na auditoria.

### 3.5 Execução local

O RabbitMQ pode rodar em container sem dockerizar a API ou os workers:

```powershell
docker compose -f compose.rabbitmq.yml up -d
```

A partir de `src/backend`, execute em terminais separados:

```powershell
python -m app.alerts.worker scheduler
python -m app.alerts.worker publisher
python -m app.alerts.worker evaluator
python -m app.alerts.worker notifier
```

No Windows, o stack de desenvolvimento pode ser iniciado em segundo plano:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_alert_stack.ps1
```

O script gera um segredo efêmero para a sessão. Produção deve fornecer
`ALERT_CONFIRMATION_SECRET` por um gerenciador de segredos.

Para aplicar e inspecionar a infraestrutura persistente:

```powershell
python -m scripts.manage_alert_infrastructure apply
python -m scripts.manage_alert_infrastructure status
```

Configuração essencial:

```dotenv
ALERT_REPOSITORY_MODE=database
ALERT_SCHEDULE_SOURCE=database
ALERT_CONFIRMATION_SECRET=segredo-aleatorio-forte
RABBITMQ_URL=amqp://usuario:senha@host:5672/vhost
ALERT_SCHEDULER_INTERVAL_SECONDS=60
ALERT_OUTBOX_POLL_SECONDS=2
ALERT_DATA_FRESHNESS_DAYS=45
```

### 3.6 CLI e verificações operacionais

O fluxo funciona sem a interface:

```powershell
python -m app.alerts.cli create --project-id PRJ-SINALIZACAO --project-label "Projeto de Sinalização" --threshold 7
python -m app.alerts.cli list
python -m app.alerts.cli evaluate --subscription-id UUID --as-of 2026-09-22
```

Smokes seguros e inspeção não sensível:

```powershell
python -m scripts.smoke_alert_rabbitmq
python -m scripts.smoke_alert_flow --token TOKEN_SIMULADO --mode not-eligible
python -m scripts.smoke_alert_flow --token TOKEN_SIMULADO --mode eligible
python -m scripts.check_alert_runtime
```

O smoke AMQP usa uma fila temporária isolada e não limpa as filas funcionais.
Os cenários HTTP cancelam suas inscrições ao final; avaliações e notificações
permanecem como evidência auditável.

## 4. Testes e operação conjunta

Os testes de relatório cobrem autorização, confirmação HMAC, idempotência,
snapshot, callback opcional, fallback determinístico, armazenamento e workflow.
Os testes de alerta cobrem confirmação, limite estrito, elegível/não elegível,
exclusão de concluídos, deduplicação, reenvio, workflow, REST e componentes da
central de notificações.

```powershell
cd src/backend
python -m pytest

cd ../frontend
npm run lint
npm test
npm run build
```

Na operação do alerta, monitore profundidade das filas, idade do evento mais
antigo da outbox, avaliações atrasadas, DLQs e notificações falhas. Na operação
do relatório, monitore duração das execuções, callbacks tardios, falhas de
renderização, integridade SHA-256 e disponibilidade do armazenamento privado.

Nenhum segredo deve ser versionado. Os arquivos `.env` locais são configuração
de execução; `.env.example` documenta somente nomes e valores não sensíveis.
