# S5-22 — Testes unitários por componente com meta de cobertura

Status: Ready for Review — validação local concluída; DoD remoto pendente

Issue de origem: [#276](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/276).
Este registro acompanha a tarefa fornecida pelo solicitante; não altera seu escopo.

## Objetivo e critérios de aceite

Cobrir cada componente da interface com testes unitários e definir a cobertura mínima na pipeline, conforme barema, item 6, e planejamento em `docs/GestaoProjeto.md` (S5-22).

- [x] Todo componente tem ao menos um teste.
- [ ] Cobertura mínima aplicada na pipeline e registrada no MR.
- [ ] Evidência registrada, MR aprovado com comentário do revisor e `Closes #276`.

## Dependências e DoR

- [x] Componentes das S5-20 e S5-21 presentes no checkout: controles de proatividade, layout responsivo, diálogos e navegação por teclado. Esta constatação não comprova aceite das issues #274 e #275.
- [ ] Assignee, revisor de outra frente, labels e milestone conferidos no GitLab. O planejamento local lista natureza FEATURE, frente TEST, tamanho G e prioridade alta; não se presume configuração remota.

## Tasks

- [x] Estabilizar a verificação E2E de contraste dos blocos na pipeline, aguardando opacidade final da mensagem (#271, #302; job #125085).

- [x] Levantar componentes sem teste direto e registrar rastreabilidade.
- [x] Escrever testes faltantes com asserções de comportamento.
- [x] Definir limites globais e gate por arquivo em `vitest.config.ts`.
- [x] Aplicar os limites no job `frontend-unit` e publicar JUnit/Cobertura como reports.
- [x] Executar lint, typecheck, testes, cobertura, formatação e build.
- [x] Verificar a rejeição de componente sem teste.
- [x] Registrar medição, evidência e revisão QA final.
- [ ] Publicar MR com `Closes #276`, registrar execução remota e obter revisão de outra frente com comentário e aprovação.

## File List

- `src/frontend/e2e/response-blocks.spec.ts`
- `docs/evidencias/sprint-05/blocos-271.md`

- `.gitlab-ci.yml`
- `src/frontend/package.json`
- `src/frontend/vitest.config.ts`
- `src/frontend/src/components/ui/ui.test.tsx`
- `src/frontend/src/components/sidebar/sidebar.test.tsx`
- `src/frontend/src/state/theme-provider.test.tsx`
- `src/frontend/src/components/chat/proactive-suggestion.test.tsx`
- `src/frontend/src/components/chat/message-rendering.test.tsx`
- `src/frontend/src/components/chat/alert-workflow-card.behavior.test.tsx`
- `src/frontend/src/components/notifications/notification-center.behavior.test.tsx`
- `src/frontend/src/components/layout/app-shell.test.tsx`
- `src/frontend/TESTES.md`
- `docs/stories/s5-22-testes-unitarios.md`
- `docs/testes/sprint5/relatorio-s5-22.md`
- `docs/testes/sprint5/mr-s5-22.md`
- `docs/testes/sprint5/evidencias-s5-22/` (logs e resumo de cobertura da execução final)

## QA Results

CONCERNS para fechamento integral da issue; implementação técnica aprovada localmente. Foram aprovados 112 testes em 18 arquivos. Cobertura: linhas 86,36%, instruções 83,96%, funções 85,81%, ramificações 75,25%. Os 38 módulos de componentes têm execução. Lint, typecheck, formatação, build e prova negativa do gate passaram conforme esperado. Ver [revisão critério a critério](../testes/sprint5/relatorio-s5-22.md).

O MR remoto, o comentário e a aprovação de outra frente e os campos de planning permanecem pendentes. O CodeRabbit foi rejeitado pela aprovação automática por possível envio do diff a terceiro; nenhum resultado dessa ferramenta foi presumido. A verificação local não substitui aprovação de revisor de outra frente.

## Change Log

- 2026-10-05: registro da tarefa #276 e implementação dos testes e gates; validação em andamento.
- 2026-10-05: validação técnica concluída; Ready for Review, com pendências remotas preservadas e descrição de MR preparada.

- 2026-10-07: correção de sincronização no E2E de contraste (#271, #302); 18 cenários E2E e 169 unitários aprovados, lint, tipos, formatação e build aprovados. Evidência em `docs/evidencias/sprint-05/blocos-271.md`; nova pipeline remota pendente.
