# Execuções de ponta a ponta do alerta de prazo

Extraído do banco em 24/09/2026 17:52 por `coletar_execucoes.py`,
somente com consultas de leitura. Horários de Brasília.

## Itens de cronograma avaliados

Marcos da carga atual da massa, gravada em 23/09 17:09:28. A carga apaga e recria os marcos, então os IDs de item das avaliações anteriores a ela são da carga anterior; nesses casos, o item aparece pelo nome no título da notificação e pela data planejada na chave do episódio (`inscrição:item:data planejada:bloco de reenvio`).

| Projeto | Item | Data planejada | Conclusão | Situação |
| --- | --- | --- | --- | --- |
| PRJ-0442 | Instalacao do primeiro lote de equipamentos de sinalizacao | 2026-09-20 | — | em_andamento |
| PRJ-0442 | Inicio da operacao assistida na Linha Azul | 2026-11-10 | — | planejado |
| PRJ-0442 | Aceite definitivo do sistema de sinalizacao | 2027-02-28 | — | planejado |
| PRJ-0510 | Ensaio integrado do centro de controle operacional | 2026-09-28 | — | planejado |
| PRJ-0510 | Corte para o novo centro de controle | 2026-12-05 | — | planejado |
| PRJ-0510 | Encerramento do plano de transicao operacional | 2027-03-15 | — | planejado |
| PRJ-0587 | Conclusao da especificacao tecnica dos elevadores | 2026-10-30 | — | planejado |
| PRJ-0587 | Contratacao do fornecedor de elevadores | 2026-12-15 | — | planejado |
| PRJ-0587 | Entrega da primeira estacao adaptada | 2027-05-30 | — | planejado |

## Resumo por inscrição

| Inscrição | Projeto | Limiar (dias) | Frequência | Reenvio (dias) | Avaliações | Pedidos de notificação publicados | Notificações criadas | Estado final |
| --- | --- | ---: | --- | ---: | --- | ---: | ---: | --- |
| `78f96e73` | PRJ-0587 | 3650 | daily | — | not_matched | 0 | 0 | cancelled |
| `1d38b0a1` | PRJ-0442 | 0 | daily | — | matched | 1 | 1 | cancelled |
| `2b362e94` | PRJ-0587 | 3650 | daily | — | not_matched | 0 | 0 | cancelled |
| `f2a3ae88` | PRJ-0442 | 0 | daily | — | matched | 1 | 1 | cancelled |
| `56e1d5bf` | PRJ-0587 | 3650 | daily | — | not_matched | 0 | 0 | cancelled |
| `39e41a0a` | PRJ-0442 | 0 | daily | — | matched | 1 | 1 | cancelled |
| `74c993bc` | PRJ-0442 | 3 | weekly | 7 | not_matched, not_matched | 0 | 0 | cancelled |
| `5f662bb3` | PRJ-0442 | 0 | daily | 7 | matched, matched | 2 | 1 | active |

## Inscrição `78f96e73-1840-4d5d-a71b-eb1e8dea1448`

- Correlação: `d8e6fb9a-b6c0-41c6-8f5b-2607e04c075d`
- Dono: `pmo-1`
- Regra: projeto PRJ-0587 (Adequacao de Acessibilidade das Estacoes), avisar com mais de 3650 dias corridos de atraso (`gt`), daily, reenvio desligado
- Criada em 22/09 12:40:35; estado `cancelled` desde 22/09 12:40:48
- Sessão guiada: `completed`, respostas `{"project": "e5f5b286-b5a4-4955-b16f-5ced25f4de2b", "resend": "none", "schedule": "daily", "threshold": 3650}`

**Avaliações**

- `32207c7b` em 22/09 12:40:46, data de referência 2026-09-22: **not_matched**, 0 de 3 itens elegíveis
  - item `e6a2ce66` da carga anterior: 0 dias de atraso → `not_matched`
  - item `49be9862` da carga anterior: 0 dias de atraso → `not_matched`
  - item `20c5e325` da carga anterior: 0 dias de atraso → `not_matched`

**Outbox (RabbitMQ)**

- `alert.subscription.created`: `published`, 1 tentativa(s), gravado 22/09 12:40:37, publicado 22/09 12:40:39
- `alert.evaluation.requested`: `published`, 1 tentativa(s), gravado 22/09 12:40:41, publicado 22/09 12:40:44

**Notificações**

- nenhuma

**Auditoria**

- 22/09 12:40:36 `alert.subscription.created` (alert_workflow, sucesso): `{"subscription_id": "78f96e73-1840-4d5d-a71b-eb1e8dea1448"}`
- 22/09 12:40:46 `alert.evaluation.completed` (alert_evaluator, sucesso): `{"evaluation_id": "32207c7b-04eb-4a60-a951-6d1f3c069541", "outcome": "not_matched"}`

## Inscrição `1d38b0a1-2ccc-4e2c-8a2f-ff5305dbf52d`

- Correlação: `50516857-33cf-42ae-9553-dbe788462f7d`
- Dono: `pmo-1`
- Regra: projeto PRJ-0442 (Modernizacao do Sistema de Sinalizacao da Linha Azul), avisar com mais de 0 dias corridos de atraso (`gt`), daily, reenvio desligado
- Criada em 22/09 12:46:34; estado `cancelled` desde 22/09 12:46:55
- Sessão guiada: `completed`, respostas `{"project": "fe091a56-310d-4465-8a13-5940d5765e1e", "resend": "none", "schedule": "daily", "threshold": 0}`

**Avaliações**

- `560f6858` em 22/09 12:46:44, data de referência 2026-09-22: **matched**, 1 de 3 itens elegíveis
  - item `f3f93342` da carga anterior: 2 dias de atraso → `matched`
  - item `1da05ecd` da carga anterior: 0 dias de atraso → `not_matched`
  - item `6e92d691` da carga anterior: 0 dias de atraso → `not_matched`

**Outbox (RabbitMQ)**

- `alert.subscription.created`: `published`, 1 tentativa(s), gravado 22/09 12:46:36, publicado 22/09 12:46:40
- `alert.evaluation.requested`: `published`, 1 tentativa(s), gravado 22/09 12:46:40, publicado 22/09 12:46:43
- `alert.notification.requested`: `published`, 1 tentativa(s), gravado 22/09 12:46:47, publicado 22/09 12:46:48

**Notificações**

- `5823ac57` "Prazo atrasado: Instalacao do primeiro lote de equipamentos de sinalizacao", 2 dias de atraso; `read`, criada 22/09 12:46:46, lida 22/09 12:46:50; 1 tentativa de entrega; episódio `1d38b0a1-2ccc-4e2c-8a2f-ff5305dbf52d:f3f93342-2bbd-4382-b3c8-a1f29f25cb0f:2026-09-20:0`

**Auditoria**

- 22/09 12:46:35 `alert.subscription.created` (alert_workflow, sucesso): `{"subscription_id": "1d38b0a1-2ccc-4e2c-8a2f-ff5305dbf52d"}`
- 22/09 12:46:45 `alert.evaluation.completed` (alert_evaluator, sucesso): `{"evaluation_id": "560f6858-6b85-4296-82e6-cf4860930cb7", "outcome": "matched"}`
- 22/09 12:46:49 `alert.notification.available` (notification_dispatcher, sucesso): `{"notification_id": "5823ac57-b8e0-4d2f-92ab-60531745fa42"}`

## Inscrição `2b362e94-8c09-434d-847b-d339b5574e38`

- Correlação: `fa36475d-6e86-4435-af09-a17c9a127866`
- Dono: `pmo-1`
- Regra: projeto PRJ-0587 (Adequacao de Acessibilidade das Estacoes), avisar com mais de 3650 dias corridos de atraso (`gt`), daily, reenvio desligado
- Criada em 22/09 14:42:20; estado `cancelled` desde 22/09 14:42:34
- Sessão guiada: `completed`, respostas `{"project": "e5f5b286-b5a4-4955-b16f-5ced25f4de2b", "resend": "none", "schedule": "daily", "threshold": 3650}`

**Avaliações**

- `85ca8fd0` em 22/09 14:42:30, data de referência 2026-09-22: **not_matched**, 0 de 3 itens elegíveis
  - item `e6a2ce66` da carga anterior: 0 dias de atraso → `not_matched`
  - item `49be9862` da carga anterior: 0 dias de atraso → `not_matched`
  - item `20c5e325` da carga anterior: 0 dias de atraso → `not_matched`

**Outbox (RabbitMQ)**

- `alert.subscription.created`: `published`, 1 tentativa(s), gravado 22/09 14:42:23, publicado 22/09 14:42:26
- `alert.evaluation.requested`: `published`, 1 tentativa(s), gravado 22/09 14:42:27, publicado 22/09 14:42:29

**Notificações**

- nenhuma

**Auditoria**

- 22/09 14:42:21 `alert.subscription.created` (alert_workflow, sucesso): `{"subscription_id": "2b362e94-8c09-434d-847b-d339b5574e38"}`
- 22/09 14:42:31 `alert.evaluation.completed` (alert_evaluator, sucesso): `{"evaluation_id": "85ca8fd0-6496-40d1-b340-47497aa2dbcd", "outcome": "not_matched"}`

## Inscrição `f2a3ae88-a0d0-4e9c-b03b-38c807b3425d`

- Correlação: `b6c9b62a-9315-418f-8320-f8b447e889e0`
- Dono: `pmo-1`
- Regra: projeto PRJ-0442 (Modernizacao do Sistema de Sinalizacao da Linha Azul), avisar com mais de 0 dias corridos de atraso (`gt`), daily, reenvio desligado
- Criada em 22/09 14:43:09; estado `cancelled` desde 22/09 14:43:32
- Sessão guiada: `completed`, respostas `{"project": "fe091a56-310d-4465-8a13-5940d5765e1e", "resend": "none", "schedule": "daily", "threshold": 0}`

**Avaliações**

- `8e464b4d` em 22/09 14:43:20, data de referência 2026-09-22: **matched**, 1 de 3 itens elegíveis
  - item `f3f93342` da carga anterior: 2 dias de atraso → `matched`
  - item `1da05ecd` da carga anterior: 0 dias de atraso → `not_matched`
  - item `6e92d691` da carga anterior: 0 dias de atraso → `not_matched`

**Outbox (RabbitMQ)**

- `alert.subscription.created`: `published`, 1 tentativa(s), gravado 22/09 14:43:12, publicado 22/09 14:43:15
- `alert.evaluation.requested`: `published`, 1 tentativa(s), gravado 22/09 14:43:16, publicado 22/09 14:43:19
- `alert.notification.requested`: `published`, 1 tentativa(s), gravado 22/09 14:43:23, publicado 22/09 14:43:25

**Notificações**

- `826c7630` "Prazo atrasado: Instalacao do primeiro lote de equipamentos de sinalizacao", 2 dias de atraso; `read`, criada 22/09 14:43:22, lida 22/09 14:43:28; 1 tentativa de entrega; episódio `f2a3ae88-a0d0-4e9c-b03b-38c807b3425d:f3f93342-2bbd-4382-b3c8-a1f29f25cb0f:2026-09-20:0`

**Auditoria**

- 22/09 14:43:10 `alert.subscription.created` (alert_workflow, sucesso): `{"subscription_id": "f2a3ae88-a0d0-4e9c-b03b-38c807b3425d"}`
- 22/09 14:43:21 `alert.evaluation.completed` (alert_evaluator, sucesso): `{"evaluation_id": "8e464b4d-6d9b-4ada-b2c1-232eda86dcb8", "outcome": "matched"}`
- 22/09 14:43:25 `alert.notification.available` (notification_dispatcher, sucesso): `{"notification_id": "826c7630-e335-4c71-90fb-7483ae01143c"}`

## Inscrição `56e1d5bf-3321-40f8-b4f8-208914f491a5`

- Correlação: `3c88f476-1e27-4758-bee9-569769f5024d`
- Dono: `pmo-1`
- Regra: projeto PRJ-0587 (Adequacao de Acessibilidade das Estacoes), avisar com mais de 3650 dias corridos de atraso (`gt`), daily, reenvio desligado
- Criada em 22/09 16:02:55; estado `cancelled` desde 22/09 16:03:09
- Sessão guiada: `completed`, respostas `{"project": "e5f5b286-b5a4-4955-b16f-5ced25f4de2b", "resend": "none", "schedule": "daily", "threshold": 3650}`

**Avaliações**

- `7f00438b` em 22/09 16:03:06, data de referência 2026-09-22: **not_matched**, 0 de 3 itens elegíveis
  - item `e6a2ce66` da carga anterior: 0 dias de atraso → `not_matched`
  - item `49be9862` da carga anterior: 0 dias de atraso → `not_matched`
  - item `20c5e325` da carga anterior: 0 dias de atraso → `not_matched`

**Outbox (RabbitMQ)**

- `alert.evaluation.requested`: `published`, 1 tentativa(s), gravado 22/09 16:03:01, publicado 22/09 16:03:04

**Notificações**

- nenhuma

**Auditoria**

- 22/09 16:02:57 `alert.subscription.created` (alert_workflow, sucesso): `{"subscription_id": "56e1d5bf-3321-40f8-b4f8-208914f491a5"}`
- 22/09 16:03:07 `alert.evaluation.completed` (alert_evaluator, sucesso): `{"evaluation_id": "7f00438b-879c-4592-98d1-737047c557ff", "outcome": "not_matched"}`

## Inscrição `39e41a0a-611e-4186-b801-c24fefd60bef`

- Correlação: `13b60fa2-f423-4b40-91e1-6653665829e9`
- Dono: `pmo-1`
- Regra: projeto PRJ-0442 (Modernizacao do Sistema de Sinalizacao da Linha Azul), avisar com mais de 0 dias corridos de atraso (`gt`), daily, reenvio desligado
- Criada em 22/09 16:03:37; estado `cancelled` desde 22/09 16:03:57
- Sessão guiada: `completed`, respostas `{"project": "fe091a56-310d-4465-8a13-5940d5765e1e", "resend": "none", "schedule": "daily", "threshold": 0}`

**Avaliações**

- `4bd426f8` em 22/09 16:03:47, data de referência 2026-09-22: **matched**, 1 de 3 itens elegíveis
  - item `f3f93342` da carga anterior: 2 dias de atraso → `matched`
  - item `1da05ecd` da carga anterior: 0 dias de atraso → `not_matched`
  - item `6e92d691` da carga anterior: 0 dias de atraso → `not_matched`

**Outbox (RabbitMQ)**

- `alert.evaluation.requested`: `published`, 1 tentativa(s), gravado 22/09 16:03:42, publicado 22/09 16:03:45
- `alert.notification.requested`: `published`, 1 tentativa(s), gravado 22/09 16:03:49, publicado 22/09 16:03:51

**Notificações**

- `bd80607b` "Prazo atrasado: Instalacao do primeiro lote de equipamentos de sinalizacao", 2 dias de atraso; `read`, criada 22/09 16:03:49, lida 22/09 16:03:53; 1 tentativa de entrega; episódio `39e41a0a-611e-4186-b801-c24fefd60bef:f3f93342-2bbd-4382-b3c8-a1f29f25cb0f:2026-09-20:0`

**Auditoria**

- 22/09 16:03:38 `alert.subscription.created` (alert_workflow, sucesso): `{"subscription_id": "39e41a0a-611e-4186-b801-c24fefd60bef"}`
- 22/09 16:03:48 `alert.evaluation.completed` (alert_evaluator, sucesso): `{"evaluation_id": "4bd426f8-a77d-437c-b610-e2e71119ed2d", "outcome": "matched"}`
- 22/09 16:03:51 `alert.notification.available` (notification_dispatcher, sucesso): `{"notification_id": "bd80607b-a067-48b0-95e4-04a45848a350"}`

## Inscrição `74c993bc-32a8-4ba4-976c-59d29e38e120`

- Correlação: `c54059fd-e247-4d04-aff5-129024d845ed`
- Dono: `pmo-1`
- Regra: projeto PRJ-0442 (Modernizacao do Sistema de Sinalizacao da Linha Azul), avisar com mais de 3 dias corridos de atraso (`gt`), weekly, reenvio 7
- Criada em 22/09 16:09:45; estado `cancelled` desde 22/09 16:20:01
- Sessão guiada: `completed`, respostas `{"project": "fe091a56-310d-4465-8a13-5940d5765e1e", "resend": "7", "schedule": "weekly", "threshold": 3, "threshold_candidate": 3}`

**Avaliações**

- `19c918e8` em 22/09 16:12:48, data de referência 2026-09-22: **not_matched**, 0 de 3 itens elegíveis
  - item `f3f93342` da carga anterior: 2 dias de atraso → `not_matched`
  - item `1da05ecd` da carga anterior: 0 dias de atraso → `not_matched`
  - item `6e92d691` da carga anterior: 0 dias de atraso → `not_matched`
- `bc3d90e1` em 22/09 16:13:21, data de referência 2026-09-22: **not_matched**, 0 de 3 itens elegíveis
  - item `f3f93342` da carga anterior: 2 dias de atraso → `not_matched`
  - item `1da05ecd` da carga anterior: 0 dias de atraso → `not_matched`
  - item `6e92d691` da carga anterior: 0 dias de atraso → `not_matched`

**Outbox (RabbitMQ)**

- `alert.evaluation.requested`: `published`, 1 tentativa(s), gravado 22/09 16:12:42, publicado 22/09 16:12:46
- `alert.evaluation.requested`: `published`, 1 tentativa(s), gravado 22/09 16:13:16, publicado 22/09 16:13:19

**Notificações**

- nenhuma

**Auditoria**

- 22/09 16:09:46 `alert.subscription.created` (alert_workflow, sucesso): `{"subscription_id": "74c993bc-32a8-4ba4-976c-59d29e38e120"}`
- 22/09 16:12:49 `alert.evaluation.completed` (alert_evaluator, sucesso): `{"evaluation_id": "19c918e8-a0be-48e9-ad75-c6f2b3df6a58", "outcome": "not_matched"}`
- 22/09 16:13:21 `alert.evaluation.completed` (alert_evaluator, sucesso): `{"evaluation_id": "bc3d90e1-51f5-4266-95ad-407a76e87a21", "outcome": "not_matched"}`

## Inscrição `5f662bb3-29e8-451c-a4f2-8b09d0629dae`

- Correlação: `0c755f49-3fb0-4d95-a33f-a97401f21087`
- Dono: `pmo-1`
- Regra: projeto PRJ-0442 (Modernizacao do Sistema de Sinalizacao da Linha Azul), avisar com mais de 0 dias corridos de atraso (`gt`), daily, reenvio 7
- Criada em 22/09 16:17:33; estado `active` desde 22/09 16:19:22
- Sessão guiada: `completed`, respostas `{"project": "fe091a56-310d-4465-8a13-5940d5765e1e", "resend": "7", "schedule": "daily", "threshold": 0, "threshold_candidate": 0}`

**Avaliações**

- `bed3d4fa` em 22/09 16:18:43, data de referência 2026-09-22: **matched**, 1 de 3 itens elegíveis
  - item `f3f93342` da carga anterior: 2 dias de atraso → `matched`
  - item `1da05ecd` da carga anterior: 0 dias de atraso → `not_matched`
  - item `6e92d691` da carga anterior: 0 dias de atraso → `not_matched`
- `47b0455a` em 22/09 16:19:28, data de referência 2026-09-22: **matched**, 1 de 3 itens elegíveis
  - item `f3f93342` da carga anterior: 2 dias de atraso → `matched`
  - item `1da05ecd` da carga anterior: 0 dias de atraso → `not_matched`
  - item `6e92d691` da carga anterior: 0 dias de atraso → `not_matched`

**Outbox (RabbitMQ)**

- `alert.evaluation.requested`: `published`, 1 tentativa(s), gravado 22/09 16:18:37, publicado 22/09 16:18:42
- `alert.notification.requested`: `published`, 1 tentativa(s), gravado 22/09 16:18:45, publicado 22/09 16:18:48
- `alert.evaluation.requested`: `published`, 1 tentativa(s), gravado 22/09 16:19:24, publicado 22/09 16:19:26
- `alert.notification.requested`: `published`, 1 tentativa(s), gravado 22/09 16:19:30, publicado 22/09 16:19:32

**Notificações**

- `891ae1e1` "Prazo atrasado: Instalacao do primeiro lote de equipamentos de sinalizacao", 2 dias de atraso; `read`, criada 22/09 16:18:45, lida 22/09 16:19:55; 1 tentativa de entrega; episódio `5f662bb3-29e8-451c-a4f2-8b09d0629dae:f3f93342-2bbd-4382-b3c8-a1f29f25cb0f:2026-09-20:0`

**Auditoria**

- 22/09 16:17:34 `alert.subscription.created` (alert_workflow, sucesso): `{"subscription_id": "5f662bb3-29e8-451c-a4f2-8b09d0629dae"}`
- 22/09 16:18:44 `alert.evaluation.completed` (alert_evaluator, sucesso): `{"evaluation_id": "bed3d4fa-a282-4a7e-b385-2296ec974948", "outcome": "matched"}`
- 22/09 16:18:48 `alert.notification.available` (notification_dispatcher, sucesso): `{"notification_id": "891ae1e1-a05a-4e27-962d-858a52ec1fe3"}`
- 22/09 16:19:29 `alert.evaluation.completed` (alert_evaluator, sucesso): `{"evaluation_id": "47b0455a-83b4-4563-b9e2-ed20dcad550a", "outcome": "matched"}`
