# S5-06 (#260) — Alteração de dados do projeto pelo chat com confirmação

Implementa o contrato da S5-05, publicado em
[`Projeto.md`, Seção 8.5.13](../../Projeto.md#8513-contrato-de-alteração-de-dados-pelo-chat-s5-05).
Esta evidência registra o que foi entregue, como reproduzir e os resultados.

## O que foi entregue

| Item | Onde |
|---|---|
| Campos editáveis, leitura e validação de valores | `src/backend/app/data_changes/fields.py` |
| Extrator determinístico do pedido, sem LLM | `src/backend/app/data_changes/extractor.py` |
| Prévia, confirmação, cancelamento, desfazer e histórico | `src/backend/app/data_changes/service.py` |
| Transação em PostgreSQL (`SELECT … FOR UPDATE`) e repositório em memória | `src/backend/app/data_changes/repository.py` |
| Rotas do cartão | `src/backend/app/data_changes/router.py` |
| Permissão de escrita pela regra que cobre o projeto | `authorize_project_write` em `src/backend/app/security/access.py` |
| Entrada pelo chat, antes do classificador | `_handle_data_change` em `src/backend/app/pipeline.py` |
| Tabela de prévias e índice do histórico | `src/database/sql/22_data_change_previews.sql` e `23_rollback_data_change_previews.sql` |
| Cinco atividades sintéticas do `PRJ-0442` | `src/database/sql/13_seed_portfolio_report_data.sql` |

Rotas:

| Método | Rota | Uso |
|---|---|---|
| `POST` | `/api/chat` | Pedido em linguagem natural; devolve `data_change` com prévia, pergunta ou recusa. |
| `POST` | `/api/data-change-previews` | Cria a prévia com a proposta completa (escolha de candidato). |
| `POST` | `/api/data-change-previews/{id}/confirm` | Única rota que grava no projeto. |
| `POST` | `/api/data-change-previews/{id}/cancel` | Descarta a prévia. |
| `POST` | `/api/data-changes/{change_id}/undo` | Desfaz em até 15 minutos. |
| `GET` | `/api/data-changes` | Histórico do campo. |

## DoD

| Critério | Como foi atendido |
|---|---|
| Alteração confirmada é gravada com trilha completa | Valor, `change_records` (`status = implementada`, `source_label = chat`) e `audit_events` (`project_data.change_applied`) são gravados na mesma transação. Prévia e eventos ficam ligados à interação do chat em `ai_interactions`. |
| Alteração sem permissão ou com valor inválido é recusada sem escrita | A permissão é verificada na prévia, na confirmação e no desfazer, pela regra que cobre o projeto. Valor inválido, campo fora do contrato e prévia desatualizada ou expirada são recusados; só o evento de auditoria é gravado. |
| Testes automatizados de sucesso, negação e desfazer | 123 testes novos: os 12 cenários de aceite, os demais casos listados abaixo e as regressões da revisão. |

## Execução dos testes

```bash
cd src/backend
python -m pytest app/tests/test_data_change_extractor.py app/tests/test_data_change_service.py \
  app/tests/test_data_change_api.py app/tests/test_data_change_postgres.py -v
```

| Arquivo | Testes | O que cobre |
|---|---:|---|
| `test_data_change_extractor.py` | 62 | Pedidos reconhecidos, perguntas que não são interceptadas, recusas identificadas no texto, leitura e validação de cada tipo de valor. |
| `test_data_change_service.py` | 44 | Os 12 cenários de aceite, a permissão por regra com duas regras divergentes, a regra de subportfólio, a permissão revogada entre prévia e confirmação, o rollback quando a auditoria falha, a autoria no desfazer, as perguntas e os avisos. |
| `test_data_change_api.py` | 11 | O fluxo pela API, do chat ao desfazer, sem nenhuma chamada ao provedor de LLM, mais os códigos HTTP das rotas e a resposta sem banco configurado. |
| `test_data_change_postgres.py` | 6 | Integração com PostgreSQL real: trilha completa, rollback, duas confirmações simultâneas do mesmo campo, prévia desatualizada, a atividade da carga sintética e a ligação com a interação do chat. |

O arquivo de PostgreSQL só roda com `DATA_CHANGE_TEST_DATABASE_URL` apontando para
um banco com `01`, `02`, `13`, `20` e `22` aplicados. Na CI, sem banco, ele é
pulado. Execução em 06/10/2026, em PostgreSQL 16 local:

```text
123 passed
```

Suíte do job `backend-api` com os quatro arquivos novos: **466 aprovados** (a
develop tem 373), 13 pulados e as 3 falhas conhecidas que dependem do
classificador real (`requirements-pln.txt`). Rodando a pasta inteira, as falhas
são um subconjunto das falhas da develop, sem nenhuma nova.

A migração `22` foi aplicada duas vezes seguidas sem erro, e o rollback `23`
remove a tabela e o índice. A carga `13` foi reaplicada depois do rollback `14`,
recriando as cinco atividades.

## Fluxo real contra o PostgreSQL

Execução pela API, com o provedor de LLM substituído por uma função que falha
se for chamada:

| Passo | Resultado |
|---|---|
| 1. Gerente: "Prorroga o prazo do PRJ-0442 para 31/03/2027" | `200`, `data_change.status = preview`, de 20/12/2026 para 31/03/2027. O banco continua com 20/12/2026. |
| 2. Gerente confirma com justificativa | `200`, `status = aplicada`, desfazer disponível até 15 minutos depois. O banco passa a 31/03/2027. |
| 3. Histórico do campo | Uma alteração, autor "[DEMO] Gerente de Projeto", `can_undo = true`. |
| 4. Gerente desfaz | `200`, `status = desfeita`. O banco volta a 20/12/2026. |
| 5. PMO pede a mesma alteração | `200`, `rejected` com `OUT_OF_SCOPE_FOR_PROFILE`, sem prévia. |
| 6. Gerente pede progresso de 140% | `200`, `rejected` com `INVALID_VALUE`: "O progresso deve estar entre 0 e 100%." |

Trilha gravada pelo fluxo:

```text
change_records:
  ('cancelada', 'chat', 'prazo', '[DEMO] Gerente de Projeto',
   'Prazo final previsto: 20/12/2026 → 31/03/2027',
   'Replanejamento aprovado na reunião de 03/10', tem_interacao=True, desfeita=True)
audit_events (tipo, status, do gerente, com interação):
  project_data.change_previewed   pendente   True   True
  project_data.chat_request       sucesso    True   True
  project_data.change_applied     sucesso    True   True
  project_data.change_undone      sucesso    True   True
  authorization.access_denied     bloqueado  False  True
  project_data.chat_request       sucesso    False  True
  project_data.change_rejected    falha      True   True
  project_data.chat_request       sucesso    True   True
pending_data_changes: confirmada = 1
```

## Correção após a revisão do MR

A revisão reproduziu, pela API, valores de progresso gravados errados: o
extrator usava `\d{1,3}(?:[.,]\d{1,2})?` e mandava para a validação só um
pedaço do número.

| Pedido | Antes da correção | Depois |
|---|---|---|
| `-10%` | Prévia e gravação de 10% | `INVALID_VALUE`: fora de 0 a 100 |
| `1000%` | Prévia e gravação de 0% | `INVALID_VALUE`: fora de 0 a 100 |
| `35,555%` | Prévia e gravação de 5% | `INVALID_VALUE`: mais de duas casas |
| `1.000%` | Prévia e gravação de 0% | `INVALID_VALUE`: mais de duas casas |
| `31/03/20277` | Prévia de 31/03/2027, sem aviso | `INVALID_VALUE`: data inválida |
| `31 de março de 20277` | Lido como marco do projeto | `INVALID_VALUE`: data inválida |

As duas últimas linhas são do mesmo tipo de defeito e foram encontradas na
conferência da correção. O extrator agora entrega o número inteiro, com sinal
e separador. As casas decimais são contadas no texto, porque `Decimal("1.000")`
não revela que foram escritas três casas. Os padrões de data não casam mais
parte de um número, e datas por extenso inválidas não são confundidas com
marcos.

Foram acrescentados 24 testes de regressão no extrator, no serviço e na API.
Contra o código anterior, 19 deles falham; os outros 5 testam a validação
direta, que já estava correta. Suíte do job `backend-api` depois da correção:
**490 aprovados**, 13 pulados e as 3 falhas conhecidas. Os 6 testes com
PostgreSQL continuam aprovados.

## Decisões tomadas na implementação

- **`correlation_id` na prévia.** A interação do chat só existe depois do
  rastreamento RNF03. Prévia e eventos nascem com o `correlation_id`, e o
  pipeline os liga à interação logo depois. Confirmação, cancelamento e desfazer
  herdam essa interação nos seus eventos.
- **Recusa grava só a auditoria.** Uma recusa prevista confirma a transação com
  o evento e nada mais. Um erro inesperado desfaz tudo e responde
  `DATA_CHANGE_UNAVAILABLE`.
- **`PREVIEW_ALREADY_CONFIRMED` e `DATA_CHANGE_INVALID_INPUT`** foram
  acrescentados à tabela de erros da Seção 8.5.13.
- **Orientação para as intenções de atualização.** Quando o classificador
  devolve `transacao_atualizar_cronograma` ou `transacao_atualizar_status` e o
  extrator não reconhece o pedido, a resposta traz exemplos em vez de ir ao RAG.

## Limites

- A interface do cartão é a S5-07 (#261). Até lá, o chat mostra a prévia em
  texto, e a confirmação acontece pelas rotas da API.
- Os limites do contrato continuam valendo: o RAG lê os documentos e não as
  tabelas, e a alteração não é sincronizada com o SharePoint.
- O teste formal com perfis negados e a reexecução dos RNFs são da S5-08 (#262).
