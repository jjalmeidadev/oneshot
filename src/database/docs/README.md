# Documentação do banco de dados

## Objetivo

Este arquivo centraliza a documentação técnica dos scripts de banco de dados do MVP do Agente de IA para Portfólio de Projetos do Metrô.

O primeiro script disponível:

- `../sql/01_create_database.sql`: cria o modelo físico inicial com tabelas, chaves primárias, chaves estrangeiras, restrições, índices e comentários.

Scripts previstos para evolução:

- `../sql/02_initial_data.sql`: carga inicial de dados sintéticos;
- `../sql/03_rollback_data.sql`: desfaz a criação ou alterações de estrutura quando houver necessidade de retorno controlado;
- scripts incrementais de migração, caso o modelo evolua nas próximas sprints.

## Banco-alvo

O modelo físico foi escrito para **PostgreSQL 14+**, utilizando:

- `UUID` como identificador técnico;
- `gen_random_uuid()` via extensão `pgcrypto`;
- `JSONB` para metadados flexíveis de artefatos, entidades extraídas, payloads de auditoria e campos variáveis do SharePoint;
- `CHECK CONSTRAINTS` para domínios controlados;
- `FOREIGN KEYS` para integridade referencial;
- `INDEXES` para consultas frequentes do MVP.

## Escopo do modelo físico

O script cria 18 tabelas:

| Grupo | Tabelas |
| --- | --- |
| Portfólio e projetos | `subportfolios`, `projects` |
| Fontes, documentos e planilhas | `project_artifacts`, `source_extracts` |
| Dados estruturados prioritários | `schedule_items`, `project_status_updates`, `risk_issue_items`, `change_records` |
| Usuários e acesso | `users`, `access_rules` |
| Intenções e prompts | `intent_catalog`, `prompt_templates` |
| Conversas, fontes consultadas e auditoria | `ai_conversations`, `ai_interactions`, `consulted_sources`, `audit_events`, `out_of_scope_requests` |
| Avaliação do PLN | `intent_test_cases` |

## Tratamento de planilhas Excel do SharePoint

Algumas listas do SharePoint podem guardar apenas links para planilhas Excel, especialmente cronogramas. O modelo trata esse caso da seguinte forma:

1. O link da planilha é registrado em `project_artifacts.sharepoint_url`.
2. A aba ou intervalo esperado é registrado em `project_artifacts.excel_sheet_name` e `project_artifacts.excel_table_or_range`.
3. A rotina de extração lê a planilha e grava as linhas relevantes em `schedule_items`.
4. Extratos textuais derivados da planilha podem ser gravados em `source_extracts` para consulta, referência e composição de contexto controlado no Copilot.
5. A origem usada na resposta é registrada em `consulted_sources`, com informação de documento, extrato, aba, linha ou intervalo.
6. A sincronização e os acessos às fontes são auditados por `audit_events` e pelos metadados flexíveis de `project_artifacts`.

## Relação com a documentação principal

A Seção 4 de `docs/Projeto.md` descreve:

- Modelo conceitual: entidades e relacionamentos de negócio;
- Modelo lógico: tabelas, atributos, PKs, FKs e regras de integridade;
- Modelo físico: referência ao script `src/database/sql/01_create_database.sql`.

Esta pasta complementa essa seção com instruções técnicas dos scripts executáveis.