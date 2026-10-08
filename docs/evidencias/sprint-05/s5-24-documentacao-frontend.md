# S5-24 — Evidência da medição do front-end

Issue: [#278](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/278). Documentação: Seção 8.5.14 de [`docs/Projeto.md`](../../Projeto.md#8514-front-end-navegabilidade-estratégia-de-construção-e-testes-s5-24).

## Ambiente

| Item | Valor |
| --- | --- |
| Data e hora | 06/10/2026, 22h27 (horário de Brasília); `2026-10-07T01:27:11Z` no log |
| Commit medido | `f7ba157` (`develop` de 06/10/2026 mais a S5-07, branch `feat/previa-alteracao-interface`) |
| Node.js | 24.21.0 |
| Vitest | 5.0.0, cobertura V8 |
| Comando | `npm run test:coverage` em `src/frontend` |

## Resultado

106 testes aprovados em 16 arquivos, sem falhas.

| Métrica | Coberto / total | Percentual |
| --- | --- | --- |
| Linhas | 964 / 1.135 | 84,93% |
| Instruções | 1.025 / 1.248 | 82,13% |
| Funções | 307 / 382 | 80,36% |
| Ramificações | 814 / 1.078 | 75,51% |

## Arquivos

- [`s5-24/vitest-coverage.txt`](s5-24/vitest-coverage.txt): saída completa do Vitest, com a tabela de cobertura por arquivo.
- [`s5-24/coverage-summary.json`](s5-24/coverage-summary.json): resumo JSON por arquivo, gerado pelo próprio Vitest.
- [`docs/img/navegabilidade-frontend.png`](../../img/navegabilidade-frontend.png): Figura 28, gerada a partir de [`docs/diagrams/navegabilidade-frontend.dot`](../../diagrams/navegabilidade-frontend.dot) com `dot -Tpng -Gdpi=150`.

## Observações

- O Playwright não foi executado de novo nesta medição. O último resultado registrado é de 36 execuções aprovadas em 36, em 06/10/2026, na evidência da S5-07 ([`s5-07-interface-alteracao.md`](s5-07-interface-alteracao.md)).
- Com o Node.js 22, `client.test.ts › baixa o DOCX pelo backend e revoga a URL temporaria` falha por incompatibilidade entre o `Blob` do jsdom e o `Response` do Node. No Node.js 24, a versão do README e do pipeline, o arquivo aprova os 17 casos.
- A branch da S5-22 (`test/completar-testes-unitarios`) também foi mesclada localmente para conferência. Ela entra em conflito em `app-shell.test.tsx`, e 8 dos seus 48 casos novos falham contra a `develop` atual. Por isso ela ficou fora desta medição.
