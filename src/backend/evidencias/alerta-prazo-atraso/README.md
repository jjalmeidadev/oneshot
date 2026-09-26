# Evidências do fluxo de alerta de prazo em atraso

Evidências do workflow `alerta_prazo_atraso`, descrito na Seção 8.5.11 do
[`Projeto.md`](../../../../docs/Projeto.md) e operado conforme a Seção 3 de
[`IMPLEMENTATION.md`](../../../agent/support/IMPLEMENTATION.md).

## Arquivos

| Arquivo | Conteúdo |
| --- | --- |
| [`execucoes-e2e.md`](execucoes-e2e.md) | Execuções de ponta a ponta de 22/09/2026, extraídas do banco: inscrições, sessões guiadas, avaliações, outbox, notificações e auditoria, ligadas pelo `correlation_id` |
| [`reexecucao-regra.txt`](reexecucao-regra.txt) | Reexecução da regra com o commit `2fb95a2`, sobre os marcos do banco, em nove cenários com resultado esperado declarado |
| [`testes-alerta.txt`](testes-alerta.txt) | Saída dos dez testes automatizados de `app/tests/test_alerts.py` no mesmo commit |
| [`coletar_execucoes.py`](coletar_execucoes.py) | Script que gera `execucoes-e2e.md`, somente com consultas de leitura |
| [`reexecutar_regra.py`](reexecutar_regra.py) | Script que gera `reexecucao-regra.txt`, sem escrita no banco |

## Execuções de ponta a ponta

Em 22/09/2026, das 12:40 às 16:20 (horário de Brasília), o fluxo rodou com o
backend em modo banco, a identidade simulada `pmo-1` e a cadeia outbox →
RabbitMQ → evaluator e notifier. O ID de cada uma das dez avaliações é o ID do
evento `alert.evaluation.requested` publicado na outbox, que o evaluator recebe
da fila. Foram oito inscrições:

| Cenário | Inscrições | Regra | Resultado |
| --- | --- | --- | --- |
| Não elegível | `78f96e73`, `2b362e94`, `56e1d5bf` | PRJ-0587, limiar de 3650 dias | `not_matched`; nenhuma notificação |
| Elegível | `1d38b0a1`, `f2a3ae88`, `39e41a0a` | PRJ-0442, limiar de 0 dias | `matched`; uma notificação, marcada como lida |
| Limite estrito | `74c993bc` | PRJ-0442, limiar de 3 dias, semanal | `not_matched` nas duas avaliações; o item mais atrasado tinha 2 dias |
| Repetição | `5f662bb3` | PRJ-0442, limiar de 0 dias, reenvio a cada 7 dias | duas avaliações `matched` e dois pedidos de notificação publicados, que geraram uma única notificação |

O item atrasado é a instalação do primeiro lote de equipamentos de
sinalização, planejada para 20/09/2026, com 2 dias de atraso na data de
referência. Cada inscrição tem um único `correlation_id`, compartilhado pelos
eventos da outbox, pelas avaliações, pelas notificações e pelos eventos de
auditoria `alert.subscription.created`, `alert.evaluation.completed` e
`alert.notification.available`. Os 19 eventos da outbox foram publicados na
primeira tentativa, e cada notificação tem uma tentativa de entrega registrada.

As quatro primeiras inscrições ainda gravavam `alert.subscription.created` na
outbox. A versão final registra esse evento só na auditoria, porque nenhuma fila o
consome (teste `test_subscription_created_is_not_enqueued`). A massa foi
recarregada em 23/09, depois das execuções, e a carga recria os marcos com novos
IDs; por isso o relatório identifica o item das avaliações de 22/09 pelo título
da notificação e pela data planejada da chave do episódio.

## Reexecução com o código final

As execuções de 22/09 aconteceram durante o desenvolvimento. Para ligar as
evidências ao commit final, `reexecutar_regra.py` roda o `AlertService` e a
fonte de cronograma do banco com um repositório em memória, sem gravar no banco,
na mesma data de referência. O resultado foi de nove cenários conformes em nove:

1. elegível, com limiar de 0 dias: `matched` e uma notificação;
2. limite estrito, com limiar de 2 dias: `not_matched`, porque 2 dias não é mais que 2;
3. não elegível, PRJ-0442 com limiar de 3 dias: `not_matched`, sem notificação;
4. não elegível, PRJ-0587 com limiar de 3650 dias: `not_matched`, sem notificação;
5. repetição na mesma data: o novo pedido é ignorado pelo episódio já notificado;
6. reenvio a cada 7 dias: notificação em 22/09, nova em 29/09 e nenhuma em 30/09;
7. criação com a mesma chave de idempotência: a mesma inscrição, sem duplicar;
8. confirmação alterada depois da revisão: recusada;
9. dono sem identidade válida: acesso negado e inscrição no estado `blocked`.

A reexecução cobre a regra, a deduplicação, o reenvio, a confirmação e o
bloqueio; a passagem pelas filas está nas execuções de ponta a ponta.

## Critérios cobertos

| Critério | Evidência |
| --- | --- |
| Regra elegível e não elegível | Execuções de 22/09 e cenários 1 a 4 da reexecução |
| Validação de projeto, limiar e confirmação | Sessões guiadas em `execucoes-e2e.md`, cenário 8 e `test_tampered_confirmation_is_rejected` |
| Notificação e retorno ao usuário | Notificações disponíveis na central interna, com a leitura registrada em `read_at` |
| Repetição | Inscrição `5f662bb3` e cenários 5 e 6 |
| Armazenamento | Tabelas `alert_subscriptions`, `alert_evaluations`, `alert_occurrences`, `alert_notifications`, `notification_delivery_attempts` e `message_outbox` |
| Auditoria e correlação | Eventos de auditoria de cada inscrição, com o mesmo `correlation_id` da outbox e das notificações |
| Falha e bloqueio | Bloqueio no cenário 9. Falha de publicação fica na outbox, com nova tentativa e estado `failed` depois de cinco, guardando `last_error`; falha de consumo tem uma nova entrega e depois vai para a DLQ. Nenhuma falha ocorreu nas execuções de 22/09. As falhas ficam nesses estados e na DLQ, sem evento de auditoria próprio |
| Callback | Não se aplica: o fluxo não recebe retorno de sistema externo. Não usa Copilot Studio, Power Automate, Teams, e-mail nem webhook; a interface usa REST e os processos, AMQP |
| Segredos | Nenhum token, senha ou chave nos arquivos; a identidade aparece só pelo sujeito simulado |

> **Nota temporal:** a linha `Callback` descreve somente a execução histórica
> de 22/09/2026. Na Sprint 5 foi adicionado, depois dessa coleta, o webhook de
> confirmação de entrega chamado pelo provedor/simulador. A geração do alerta
> continua sendo iniciada pelo scheduler; REST, outbox e AMQP não são
> webhooks. Consulte a
> [evidência posterior](../../../../docs/evidencias/sprint-05/webhooks-rabbitmq.md).

## Como reproduzir

A partir de `src/backend`, com `SUPABASE_DATABASE_URL` e
`REPORT_SIMULATED_IDENTITIES` no `.env`:

```bash
PYTHONPATH=. .venv/bin/python evidencias/alerta-prazo-atraso/coletar_execucoes.py
PYTHONPATH=. .venv/bin/python evidencias/alerta-prazo-atraso/reexecutar_regra.py
.venv/bin/python -m pytest app/tests/test_alerts.py -v
```

Uma nova execução de ponta a ponta precisa do RabbitMQ e dos workers, conforme
as Seções 3.5 e 3.6 de `IMPLEMENTATION.md`, com
`scripts/smoke_alert_flow.py --mode eligible` e `--mode not-eligible`.
