# S5-25 — Auditoria de fora de escopo, correlação e fluxo guiado

Issue: #279. Origem: D-02, D-03 e D-05 em `docs/testes/sprint4/relatorio-s4-11.md`.

## Diagnóstico do repositório

- D-02: já havia `INSERT` em `out_of_scope_requests`, mas só para respostas `rag-retriever` sem fontes. Uma classificação `FORA_DE_ESCOPO` respondida por outro caminho não entrava na fila.
- D-03: `audit_events.correlation_id` existia no schema, mas o `INSERT` de `tracing.py` não preenchia a coluna.
- D-05: o schema inicial não aceita `component='guided_workflow'`. A migração `07_guided_report_workflow.sql` amplia o domínio, mas o teste estático da Sprint 4 lê o schema inicial. O evento agora usa `api`, aceito nas duas versões. A rota `guided_workflow` requer a migração 07, já prevista para o fluxo de relatórios.

## Correção

- Classificações `FORA_DE_ESCOPO` e `INDEFINIDA` entram na fila de curadoria, além das respostas RAG sem contexto.
- Cada chamada de `trace_interaction` gera um `correlation_id` compartilhado por todos os seus eventos.
- O evento `guided_workflow_dispatched` usa `component='api'`.
- Os marcadores xfail de D-02, D-03 e D-05 foram removidos.
- `src/database/sql/19_backfill_s5_25_audit.sql` repara registros históricos de forma idempotente; ainda precisa ser aplicado no banco de destino após publicar o backend.

## Verificação local

- `src/backend/.venv/Scripts/python.exe -m pytest app/tests/test_response_references.py app/tests/test_traceability.py app/tests/test_persistence_audit_s4_11.py -q`: 70 passed, 12 skipped. Os 12 testes que leem o banco foram ignorados porque não havia conexão configurada para a execução.
- `src/backend/.venv/Scripts/python.exe -m pytest app/tests -q`: 491 passed, 25 skipped, 1 xfailed, 11 warnings. O xfail remanescente é de outro defeito; D-02, D-03 e D-05 não têm mais marcador.
- Reexecução dos três testes focalizados de curadoria, correlação e fluxo guiado após o ajuste final do motivo: 3 passed.
- `git diff --check`: sem erros.
- Os gates `npm run lint`, `npm run typecheck`, `npm test` e `npm run build` não são executáveis na raiz: não existe `package.json` em `C:\Users\jaime\m07\g05`.

## Verificação no banco configurado no `.env`

Credenciais não foram copiadas para esta evidência. A verificação prévia encontrou 196 interações fora de escopo sem entrada na fila e 11.193 eventos de interação sem correlação. O schema implantado já aceita `guided_workflow` nas duas constraints relevantes.

O backfill `19_backfill_s5_25_audit.sql` foi aplicado em uma transação. Depois dele, as contagens de entradas ausentes, eventos sem correlação e interações com correlações divergentes foram todas **zero**.

Os três testes de aceitação de D-02, D-03 e D-05 rodaram contra esse banco com `--noconftest` (a fixture padrão limpa a URL do banco): **3 passed**.

A primeira rodada completa de `test_persistence_audit_s4_11.py` apontou duas interações históricas de 25/09/2026, rota `analise_local`, com status `processado` e intenção macro nula. Seus metadados mostram resposta persistida e ausência de evento PLN, coerente com a opção de desativar o classificador. Nenhum prompt ou resposta foi inspecionado. O teste foi ajustado para exigir intenção quando a classificação era esperada: eventos novos registram `intent_classifier_enabled`; para eventos antigos, o teste usa a presença de `pln_intent_classified`. A nova rodada completa terminou com **10 passed, 3 xfailed**.

Nos pacotes Node existentes, `src/frontend`: lint aprovado, 64 testes aprovados e build aprovado (inclui `tsc --noEmit`). `src/lp`: lint aprovado com avisos e build aprovado (inclui `tsc -b`). Os comandos da raiz continuam inaplicáveis por falta de `package.json`.

Após o ajuste da auditoria para o classificador opcional, a suíte completa do backend terminou com **492 passed, 25 skipped, 1 xfailed, 11 warnings**. O xfail remanescente pertence a outro defeito conhecido.

## Pendências de aceite externo

- Registrar revisão por pessoa de outra frente e, quando a equipe decidir publicar, MR com `Closes #279`. Por orientação do solicitante, esta execução não fará push nem publicará MR.
