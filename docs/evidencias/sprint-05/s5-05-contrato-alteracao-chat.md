# S5-05 (#259) — Contrato de alteração de dados pelo chat

O contrato está publicado em [`Projeto.md`, Seção 8.5.13](../../Projeto.md#8513-contrato-de-alteração-de-dados-pelo-chat-s5-05).
Esta evidência registra as decisões tomadas, a conferência do DoR e a
verificação do contrato contra o schema versionado.

## Decisões

| Tema | Decisão | Alternativa descartada |
|---|---|---|
| Via de escrita | O cartão de prévia é a única via; a gravação só ocorre na rota de confirmação. | Escrita direta a partir da resposta do modelo. |
| Desfazer | Janela de 15 minutos, só pelo autor e só se o valor não mudou depois. | Desfazer sem prazo ou por qualquer perfil com escrita. |
| Campos | Status e prazo do projeto; prazo, status e progresso do cronograma; data prevista, status e conclusão de marcos; status, responsável e prazo de riscos. | Custo, escopo e demais campos descritivos. |
| Perfis | Segue a matriz da S5-03: escrita pela regra que cobre o projeto. Hoje, só o Gerente de projeto no `PRJ-0442`. | Dar escrita ao PMO ou definir perfil por campo. |
| Interpretação | Extrator determinístico, sem modelo de linguagem no caminho da escrita. | Extração por LLM em JSON ou LLM como fallback. |
| Encerramento | `projeto.status` não aceita `concluido` nem `descontinuado` pelo chat. | Aceitar os sete valores da restrição do banco. |

## Conferência do DoR

- **Tabelas de projeto, cronograma e riscos conferidas** em
  `src/database/sql/01_create_database.sql`: `projects`, `schedule_items`,
  `project_deliverables_milestones`, `risk_issue_items`, `change_records` e
  `audit_events`, com as restrições `CHECK` de status, progresso, escopo, componente
  e status de auditoria.
- **Perfis da S5-03 definidos** em `src/backend/scripts/seed_mvp_access.py` e na
  Seção 4.3.1: só a regra do Gerente de projeto tem `can_write = true`.
- **Achados que entram como limites do contrato:**
  - nenhum script versionado popula `schedule_items`, então a S5-06 precisa de
    atividades sintéticas para o `PRJ-0442`;
  - `project_deliverables_milestones.status` não tem restrição no banco, então o
    contrato fixa o conjunto de valores;
  - o classificador leva "prorroga o prazo do PRJ-0442 até março" para consulta
    (Seção 8.11.6), então a detecção do pedido não depende dele;
  - o RAG lê `source_extracts`, e não as tabelas alteradas.

## Verificação contra o schema

O script [`s5-05-conferencia-contrato.sql`](s5-05-conferencia-contrato.sql) roda
em transação com `ROLLBACK` e interrompe na primeira divergência. Ele confere:

1. as onze colunas editáveis e seus tipos;
2. os conjuntos de status do contrato contra as restrições do banco;
3. os três exemplos da Seção 8.5.13 contra a massa sintética;
4. a confirmação do exemplo 1 gravando `projects`, `change_records` e
   `audit_events` no formato do contrato;
5. o desfazer restaurando o valor e marcando o registro como `cancelada`;
6. os oito tipos de evento de auditoria do contrato.

```bash
psql "$DATABASE_URL" -f docs/evidencias/sprint-05/s5-05-conferencia-contrato.sql
```

Execução em 06/10/2026, em PostgreSQL 16 local com `01`, `02`, `13` e `20`
aplicados:

```text
NOTICE:  1. Onze colunas editaveis conferidas.
NOTICE:  2. Status de projeto e risco aceitos; restricoes de cronograma e marco conferidas.
NOTICE:  3. Os tres exemplos conferem com a massa.
NOTICE:     schedule_items na massa versionada: 0 linha(s).
NOTICE:  4. Confirmacao gravada em projects, change_records e audit_events.
NOTICE:  5. Desfazer restaurou 2026-12-20 e marcou o registro como cancelada.
 6. Oito tipos de evento aceitos por audit_events: 8
ROLLBACK
```

## Próximos passos

- S5-06 (#260): extrator, prévia, confirmação, desfazer, `pending_data_changes`
  e carga sintética de `schedule_items`, com os doze cenários de aceite.
- S5-07 (#261): cartão com antes e depois, confirmação, cancelamento, erro e
  histórico.
