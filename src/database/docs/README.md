# Documentacao do banco de dados

## Objetivo

Esta pasta documenta os scripts de banco de dados do MVP do Agente de IA para o Portfolio de Projetos do Metro.

Os scripts atuais sao:

- `../sql/01_create_database.sql`: cria o baseline fisico em PostgreSQL 14+, ja alinhado ao inventario de listas do parceiro;
- `../sql/02_initial_data.sql`: insere uma carga sintetica minima para exercitar subportfolio, projeto, TAP, beneficios, avancos, entregas, riscos e catalogo de intencoes;
- `../sql/03_rollback_data.sql`: desfaz o baseline em ordem reversa de dependencia, para uso controlado em desenvolvimento/PoC.

## Banco-alvo

O modelo fisico foi escrito para **PostgreSQL 14+** e tambem e compativel com Supabase PostgreSQL. Ele utiliza:

- `UUID` como identificador tecnico;
- `gen_random_uuid()` via extensao `pgcrypto`;
- `JSONB` para metadados flexiveis de SharePoint, auditoria, extracao e campos ainda instaveis;
- `CHECK CONSTRAINTS` para dominios controlados;
- `FOREIGN KEYS` para integridade referencial;
- indices nos caminhos de consulta previstos para o MVP;
- indices unicos parciais para `partner_source_id` quando o registro tiver identificador externo;
- comentarios `COMMENT ON TABLE` para documentar a finalidade das tabelas no proprio banco.

## Escopo do modelo fisico

O script cria 25 tabelas:

| Grupo | Tabelas |
| --- | --- |
| Portfolio e projetos | `subportfolios`, `projects`, `subportfolio_status_updates`, `project_progress_updates`, `project_status_updates` |
| Artefatos, cronograma e conhecimento consultavel | `project_artifacts`, `source_extracts`, `schedule_items`, `project_deliverables_milestones` |
| Documentos estruturados do ciclo de vida | `project_charters`, `project_closure_terms`, `project_benefits` |
| Riscos, problemas e mudancas | `risk_issue_items`, `risk_issue_history`, `change_records` |
| Usuarios e acesso | `users`, `access_rules` |
| Intencoes e prompts | `intent_catalog`, `prompt_templates` |
| Conversas, fontes consultadas e auditoria | `ai_conversations`, `ai_interactions`, `consulted_sources`, `audit_events`, `out_of_scope_requests` |
| Avaliacao do PLN | `intent_test_cases` |

## Decisoes de modelagem

O modelo preserva uma chave tecnica `id UUID` e separa os identificadores vindos do parceiro em `partner_source_id`. Essa separacao evita acoplar o banco interno ao formato textual das listas do SharePoint e mantém rastreabilidade com a origem.

Nas tabelas alimentadas diretamente por listas ou anexos do parceiro, `partner_source_id` recebe unicidade parcial quando preenchido. Assim, cargas repetidas conseguem ser idempotentes sem impedir registros manuais, sinteticos ou ainda sem ID externo.

Riscos/problemas e mudancas aparecem nas bases do parceiro em dois niveis: projeto e subportfolio. Para evitar duplicacao de estrutura, o modelo usa `scope_type` com alvo exclusivo:

- `scope_type = 'projeto'` exige `project_id` preenchido e `subportfolio_id` nulo;
- `scope_type = 'subportfolio'` exige `subportfolio_id` preenchido e `project_id` nulo.

O TAP foi modelado em `project_charters` porque possui campos estruturados relevantes para consulta, geracao documental e Mapa de Beneficios. O documento/anexo original continua representado por `project_artifacts`.

O termo de encerramento foi modelado em `project_closure_terms`, também ligado a `project_artifacts` quando existir origem documental.

A tabela `project_benefits` foi adicionada porque o Mapa de Beneficios e parte central do recorte do MVP. Ela pode receber beneficios derivados do TAP ou de uma lista especifica de beneficios quando essa estrutura estiver disponivel.

## Tratamento de planilhas Excel do SharePoint

Algumas listas do SharePoint podem guardar apenas links ou anexos para planilhas Excel, especialmente cronogramas. O modelo trata esse caso da seguinte forma:

1. O link ou anexo da planilha e registrado em `project_artifacts.sharepoint_url`, `attachment_name` e `attachment_url`.
2. A aba ou intervalo esperado e registrado em `project_artifacts.excel_sheet_name` e `project_artifacts.excel_table_or_range`.
3. A rotina de extracao le a planilha e grava as linhas relevantes em `schedule_items`.
4. Extratos textuais derivados da planilha podem ser gravados em `source_extracts`.
5. A origem usada na resposta e registrada em `consulted_sources`, com documento, extrato, aba, linha ou intervalo.
6. A sincronizacao e os acessos as fontes sao auditados por `audit_events` e pelos metadados de `project_artifacts`.

## Execucao local sugerida

Em um banco PostgreSQL de desenvolvimento:

```bash
psql "$DATABASE_URL" -f src/database/sql/01_create_database.sql
psql "$DATABASE_URL" -f src/database/sql/02_initial_data.sql
```

Rollback completo da PoC:

```bash
psql "$DATABASE_URL" -f src/database/sql/03_rollback_data.sql
```

Antes de executar rollback em qualquer ambiente persistente, crie snapshot ou dump do schema/dados.

## Relacao com a documentacao principal

A Secao 4 de `docs/Projeto.md` descreve:

- modelo conceitual: entidades e relacionamentos de negocio;
- modelo logico: tabelas, atributos, PKs, FKs e regras de integridade;
- modelo fisico: referencia ao script `src/database/sql/01_create_database.sql`.

Os diagramas editaveis ficam em `docs/diagrams/` e devem ser atualizados junto com qualquer alteracao estrutural.
