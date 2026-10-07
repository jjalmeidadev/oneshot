# Evidência textual — webhooks e RabbitMQ (S5-09, S5-10 e S5-11)

**Data da verificação:** 25/09/2026; S5-09, S5-10 e S5-11 revalidadas em 07/10/2026
**Escopo:** contratos HTTP, autenticação, idempotência, outbox, topologia AMQP e handlers dos consumers.  
**Ambiente:** testes determinísticos com repositório em memória e doubles nas fronteiras externas.

## Comandos e resultados

Executados a partir de `src/backend`:

```powershell
.venv\Scripts\python.exe -m pytest app/tests/test_alerts.py -q
# 22 passed, 2 warnings in 1.00s

.venv\Scripts\python.exe -m pytest app/tests/test_reports.py -q
# 24 passed, 2 warnings in 2.35s

.venv\Scripts\python.exe -m pytest app/tests -q
# 488 passed, 25 skipped, 2 xfailed, 11 warnings in 433.45s
```

Revalidação focada depois da substituição do token de entrega por HMAC:

```powershell
.venv\Scripts\python.exe -m pytest app/tests/test_alerts.py -q
# 28 passed, 2 warnings in 0.61s
```

Implementação e validação do webhook do SharePoint simulado:

```powershell
.venv\Scripts\python.exe -m pytest app/tests/test_sharepoint_webhook.py app/tests/test_sharepoint_webhook_repository.py -q
# 18 passed, 2 warnings

.venv\Scripts\python.exe -m pytest app/tests/test_sharepoint_webhook.py app/tests/test_sharepoint_webhook_repository.py app/tests/test_alerts.py app/tests/test_sensitive_data_rnf01.py app/tests/test_rnf01_rnf03_s4_33.py -q
# 77 passed, 6 skipped, 2 warnings

.venv\Scripts\python.exe -m pytest app/tests/test_sharepoint_webhook_messaging.py app/tests/test_sharepoint_webhook.py app/tests/test_sharepoint_webhook_repository.py app/tests/test_sharepoint_reindex.py app/tests/test_alerts.py -q
# 66 passed, 2 warnings

docker compose -f compose.prod.yml config --quiet
docker compose -f compose.rabbitmq.yml config --quiet
# ambas as configurações foram aprovadas; o Docker apenas advertiu que não
# conseguiu ler C:\Users\Inteli\.docker\config.json neste ambiente restrito
```

As duas advertências vêm das dependências `starlette.testclient`/`httpx` e não
representam falha dos contratos. Os focados aprovaram 46 testes, e a suíte
completa daquela linha de base terminou sem falhas.

Quality gates atuais, executados em 07/10/2026:

```powershell
cd src/backend
.venv\Scripts\python.exe -m pytest -q
# 679 passed, 25 skipped, 4 failed, 11 warnings em 322,92 s

cd ../frontend
npm run lint
npm run typecheck
npm test -- --run
# 22 arquivos e 141 testes aprovados
npm run build
# build aprovado; 2.601 módulos transformados
```

As quatro falhas da regressão global são pendências preexistentes e não foram
introduzidas pelos webhooks: dois casos RNF07 registram 6/20 abaixo da meta, um
caso RNF08 registra a divergência do Copilot e um caso de síntese de áudio recebe
`speech=None`. O usuário autorizou prosseguir sem corrigi-las nesta frente.
O CodeRabbit não foi executado porque o único WSL disponível é
`docker-desktop`, sem `bash` nem ambiente compatível com o CLI configurado.

## Casos comprovados

| Caso | Evidência automatizada | Resultado |
| --- | --- | --- |
| Callback de relatório aceito | `test_power_automate_callback_is_authenticated_and_idempotent` | `200`, execução concluída e callback correlacionado. |
| Token inválido no relatório | mesmo teste | `401 REPORT_CALLBACK_UNAUTHORIZED`. |
| Repetição do relatório | mesmo teste | `200`, mesma execução e sem novo processamento. |
| Conflito do relatório | mesmo teste | `409 REPORT_CONFLICT` para o mesmo `callback_id` com conteúdo diferente. |
| Execução de relatório inexistente | `test_power_automate_callback_rejects_unknown_execution` | `404 REPORT_NOT_FOUND`. |
| Payload de relatório inválido | `test_power_automate_callback_rejects_invalid_payload` | `422 REPORT_INVALID_INPUT`. |
| Callback de entrega aceito | `test_delivery_callback_succeeds` | `200`, callback persistido e um evento criado na outbox. |
| Assinatura ausente ou malformada | `test_delivery_callback_rejects_invalid_signature` | `401 NOTIFICATION_CALLBACK_UNAUTHORIZED`. |
| Corpo adulterado | `test_delivery_callback_rejects_signature_for_another_body` | Assinatura válida para outro corpo recebe `401`. |
| Segredo ausente | `test_delivery_callback_requires_configured_secret` | `503 ALERT_CONFIGURATION_ERROR`. |
| Repetição da entrega | `test_delivery_callback_is_idempotent` | `200`, um callback, um evento e uma tentativa após consumo repetido. |
| Conflito da entrega | `test_delivery_callback_rejects_conflicting_callback_id` | `409 ALERT_CONFLICT`. |
| Notificação inexistente | `test_delivery_callback_rejects_unknown_notification` | `404 NOTIFICATION_NOT_FOUND`. |
| Payload inválido | `test_delivery_callback_rejects_invalid_payload` | `422 ALERT_INVALID_INPUT`. |
| Topologia preservada | `test_rabbitmq_topology_keeps_existing_routes_and_adds_delivery` | As duas routing keys anteriores e a nova estão configuradas. |
| Publisher | `test_publisher_uses_delivery_routing_key_without_real_rabbitmq` | Publicação usa `notification.delivery.received`. |
| Consumer: sucesso | `test_delivery_consumer_records_success` | `delivered` vira tentativa persistida `available`. |
| Consumer: falha | `test_delivery_consumer_records_failure` | `failed` e `error_code` são preservados. |
| Evento inválido | `test_delivery_consumer_rejects_invalid_event` | Falha controlada `ALERT_INVALID_MESSAGE`; no broker, a exceção ativa retry/DLQ. |
| Handshake SharePoint | `test_handshake_returns_validation_token_as_plain_text` | `200 text/plain` com o mesmo `validationToken`. |
| `clientState` inválido | `test_invalid_client_state_is_rejected_without_exposing_secrets` | `401`, sem devolver o valor recebido ou esperado. |
| Payload SharePoint inválido | testes de contrato em `test_sharepoint_webhook.py` | `422` para ausência, tipo ou identificador incoerente. |
| Repetição SharePoint | `test_repeated_event_is_accepted_without_duplication` | `202`, primeira chamada cria um evento e a segunda informa uma duplicata. |
| Concorrência SharePoint | `test_concurrent_repetition_creates_exactly_one_event` | 16 gravações simultâneas resultam em uma criação e 15 duplicatas. |
| Colisão de `eventId` | `test_reused_event_id_with_different_content_is_rejected` | `409`, sem substituir o evento original. |
| Segredo não persistido | `test_repository_does_not_persist_client_state` | Payload armazenado e pendente não contém `clientState`. |
| Inbox para S5-11 | `test_pending_event_is_exposed_once_until_marked_as_published` | Evento fica `pending` até `mark_published`, sem reindexação na requisição. |
| Produtor SharePoint | testes `test_publish_*` em `test_sharepoint_webhook_messaging.py` | Publica payload sanitizado em `sharepoint.change.received` e só então marca `published`; falha mantém `pending`. |
| Consumer SharePoint | testes `test_consume_*` em `test_sharepoint_webhook_messaging.py` | Valida envelope/hash, reivindica uma vez, chama a reindexação e termina em `processed`. |
| Repetição no consumer | `test_consumer_does_not_reindex_an_already_processed_event` | Redelivery de evento processado não repete o efeito. |
| Retry e falha | `test_consumer_retries_once_and_then_marks_event_as_failed` | Primeira falha retorna a `published`; segunda termina em `failed`. |
| DLQ SharePoint | `test_worker_rejects_invalid_message_without_requeue` | Mensagem inválida é rejeitada com `requeue=False`, permitindo o roteamento para a DLQ declarada. |
| Compose dos workers | `test_compose_declares_sharepoint_workers_with_database_repository` | Produção declara publisher e consumer separados em modo `database`. |

## Exemplos reprodutíveis

### Sucesso — entrega de notificação

```http
POST /api/integrations/notifications/delivery-results HTTP/1.1
Content-Type: application/json
X-Webhook-Signature: sha256=<HMAC_SHA256_DO_CORPO>

{
  "callback_id": "delivery-callback-001",
  "notification_id": "1674b3e9-ecba-4a78-a50f-848f5eaf0d79",
  "provider": "simulated",
  "status": "delivered",
  "attempted_at": "2026-09-25T12:00:00Z",
  "error_code": null
}
```

Resultado: `200`; a mesma requisição retorna `200` novamente. Trocar `status`
para `failed` mantendo `callback_id` e recalculando a assinatura produz `409`.
Enviar assinatura ausente, inválida ou calculada antes de alterar o corpo produz
`401`.

A assinatura do exemplo é gerada sobre os bytes exatos do JSON:

```python
import hashlib
import hmac
import os

secret = os.environ["NOTIFICATION_CALLBACK_SECRET"].encode("utf-8")
signature = "sha256=" + hmac.new(
    secret,
    body,
    hashlib.sha256,
).hexdigest()
```

### Sucesso — resultado de relatório

```http
POST /api/integrations/power-automate/report-results HTTP/1.1
Content-Type: application/json
X-Callback-Token: callback-test-token

{
  "contract_version": "1.0",
  "callback_id": "callback-report-001",
  "execution_id": "<execution-id-existente>",
  "correlation_id": "<correlation-id-da-execucao>",
  "flow_run_id": "flow-run-001",
  "status": "completed",
  "result": {"schema_version": "1.0"},
  "warnings": [],
  "error_code": null,
  "error_message": null
}
```

Resultado: `200`; a repetição idêntica retorna `200`. Alterar `flow_run_id`
mantendo `callback_id` produz `409`. Token ausente ou inválido produz `401`.

### Sucesso — alteração do SharePoint simulado

```http
POST /api/integrations/sharepoint/change-notifications HTTP/1.1
Content-Type: application/json

{
  "value": [{
    "eventId": "d6a29bb6-9d2d-40dd-aa3f-20dc8d7a1218",
    "subscriptionId": "sharepoint-mock-documents",
    "clientState": "<SHAREPOINT_WEBHOOK_CLIENT_STATE>",
    "changeType": "updated",
    "resource": "lists/documentos_projetos/items/5101",
    "resourceData": {
      "siteId": "metro-sp-mock",
      "listId": "documentos_projetos",
      "itemId": 5101,
      "partnerSourceId": "sharepoint-mock:documentos_projetos:5101"
    },
    "occurredAt": "2026-10-07T12:30:00-03:00"
  }]
}
```

Resultado inicial: `202` com `created: 1`. Repetir o corpo retorna `202` com
`duplicates: 1`. Alterar `changeType` mantendo `eventId` retorna `409`.
O handshake usa a mesma rota com `?validationToken=<valor>` e retorna `200`
em texto puro, sem exigir o corpo normal.

## Limites da evidência

- Não houve chamada real ao Power Automate, Teams, SharePoint corporativo ou
  Copilot Studio. O relatório usa o simulador/duplo controlado.
- A migration da inbox do SharePoint foi validada estaticamente e por doubles;
  não foi aplicada a um PostgreSQL/Supabase externo nesta rodada.
- O produtor, o envelope AMQP e o consumer de reindexação SharePoint foram
  exercitados com doubles controlados; não houve tráfego RabbitMQ externo.
- `aio-pika` não estava instalado na `.venv` desta rodada; o publisher e o
  exchange foram exercitados com double, sem conexão a um RabbitMQ real.
- O handler do consumer, a validação, a idempotência e a persistência em memória
  foram executados diretamente. A topologia declarativa confirma filas, retry e
  DLQ, mas esta rodada não é evidência de tráfego em broker externo.
- A central de notificações continua sendo consultada pelo navegador via REST.
  O navegador não chama o webhook de entrega.
- O scheduler continua sendo o disparador das avaliações de alerta. Scheduler,
  eventos de outbox e mensagens AMQP não são webhooks.
