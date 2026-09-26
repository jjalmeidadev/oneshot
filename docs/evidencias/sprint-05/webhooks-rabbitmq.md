# Evidência textual — webhooks e RabbitMQ (S5-09, S5-10 e S5-11)

**Data da verificação:** 25/09/2026  
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

As duas advertências vêm das dependências `starlette.testclient`/`httpx` e não
representam falha dos contratos. Os focados aprovaram 46 testes, e a suíte
completa terminou sem falhas.

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
| Token inválido na entrega | `test_delivery_callback_rejects_invalid_token` | `401 NOTIFICATION_CALLBACK_UNAUTHORIZED`. |
| Repetição da entrega | `test_delivery_callback_is_idempotent` | `200`, um callback, um evento e uma tentativa após consumo repetido. |
| Conflito da entrega | `test_delivery_callback_rejects_conflicting_callback_id` | `409 ALERT_CONFLICT`. |
| Notificação inexistente | `test_delivery_callback_rejects_unknown_notification` | `404 NOTIFICATION_NOT_FOUND`. |
| Payload inválido | `test_delivery_callback_rejects_invalid_payload` | `422 ALERT_INVALID_INPUT`. |
| Topologia preservada | `test_rabbitmq_topology_keeps_existing_routes_and_adds_delivery` | As duas routing keys anteriores e a nova estão configuradas. |
| Publisher | `test_publisher_uses_delivery_routing_key_without_real_rabbitmq` | Publicação usa `notification.delivery.received`. |
| Consumer: sucesso | `test_delivery_consumer_records_success` | `delivered` vira tentativa persistida `available`. |
| Consumer: falha | `test_delivery_consumer_records_failure` | `failed` e `error_code` são preservados. |
| Evento inválido | `test_delivery_consumer_rejects_invalid_event` | Falha controlada `ALERT_INVALID_MESSAGE`; no broker, a exceção ativa retry/DLQ. |

## Exemplos reprodutíveis

### Sucesso — entrega de notificação

```http
POST /api/integrations/notifications/delivery-results HTTP/1.1
Content-Type: application/json
X-Callback-Token: notification-test-token

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
para `failed` mantendo `callback_id` produz `409`. Trocar o token produz `401`.

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

## Limites da evidência

- Não houve chamada real ao Power Automate, Teams, SharePoint corporativo ou
  Copilot Studio. O relatório usa o simulador/duplo controlado.
- `aio-pika` não estava instalado na `.venv` desta rodada; o publisher e o
  exchange foram exercitados com double, sem conexão a um RabbitMQ real.
- O handler do consumer, a validação, a idempotência e a persistência em memória
  foram executados diretamente. A topologia declarativa confirma filas, retry e
  DLQ, mas esta rodada não é evidência de tráfego em broker externo.
- A central de notificações continua sendo consultada pelo navegador via REST.
  O navegador não chama o webhook de entrega.
- O scheduler continua sendo o disparador das avaliações de alerta. Scheduler,
  eventos de outbox e mensagens AMQP não são webhooks.
