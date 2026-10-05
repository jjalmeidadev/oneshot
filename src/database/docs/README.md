# Documentacao do banco de dados

## Objetivo

Esta pasta documenta os scripts de banco de dados do MVP do Agente de IA para o Portfolio de Projetos do Metro.

Os scripts atuais sao:

- `../sql/01_create_database.sql`: cria o baseline fisico em PostgreSQL 14+, ja alinhado ao inventario de listas do parceiro;
- `../sql/02_initial_data.sql`: insere uma carga sintetica minima para exercitar subportfolio, projeto, TAP, beneficios, avancos, entregas, riscos e catalogo de intencoes;
- `../sql/03_rollback_data.sql`: desfaz o baseline em ordem reversa de dependencia, para uso controlado em desenvolvimento/PoC.
- `../sql/04_rag_synthetic_data.sql`: carrega em `project_artifacts` e `source_extracts` os itens ficticios dos JSONs usados pelo RAG local em `src/backend/app/rag/data/sharepoint`.
- `../sql/05_add_secondary_intents.sql`: adiciona o catalogo de intencoes secundarias a bancos que ja possuem o baseline;
- `../sql/06_verify_secondary_intents.sql`: verifica leitura, unicidade, integridade referencial e reexecucao da carga sem persistir dados de teste.
- `../sql/07_add_pending_proactive_suggestions.sql`: cria o armazenamento compartilhado das sugestões pendentes;
- `../sql/08_add_prepared_proactive_response.sql`: adiciona a resposta secundária preparada na chamada principal e remove pendências legadas incompatíveis.
- `../sql/20_auth_access_foundation.sql`: adiciona o perfil `consulta`, garante unicidade de regras de acesso com `NULLS NOT DISTINCT`, documenta o vinculo com Supabase Auth e protege `secondary_intents` com RLS sem policies permissivas;
- `../sql/21_rollback_auth_access_foundation.sql`: reverte especificamente a fundacao da migration 20 sem remover tabelas ou dados e bloqueia a reversao se ja existirem usuarios `consulta`.

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

O script cria 27 tabelas:

| Grupo | Tabelas |
| --- | --- |
| Portfolio e projetos | `subportfolios`, `projects`, `subportfolio_status_updates`, `project_progress_updates`, `project_status_updates` |
| Artefatos, cronograma e conhecimento consultavel | `project_artifacts`, `source_extracts`, `schedule_items`, `project_deliverables_milestones` |
| Documentos estruturados do ciclo de vida | `project_charters`, `project_closure_terms`, `project_benefits` |
| Riscos, problemas e mudancas | `risk_issue_items`, `risk_issue_history`, `change_records` |
| Usuarios e acesso | `users`, `access_rules` |
| Intencoes e prompts | `intent_catalog`, `secondary_intents`, `prompt_templates` |
| Conversas, fontes consultadas e auditoria | `ai_conversations`, `pending_proactive_suggestions`, `ai_interactions`, `consulted_sources`, `audit_events`, `out_of_scope_requests` |
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

`secondary_intents` associa uma sugestao proativa a uma intencao especifica existente em `intent_catalog`. A chave estrangeira impede associacoes orfas, enquanto a restricao unica sobre `specific_intent_id` e `secondary_intent` torna a carga idempotente. Os campos `rag_instruction` e `display_message` separam a orientacao enviada ao RAG do texto curto apresentado na interface. A intencao secundaria complementa a consulta e nao altera a classificacao macro ou especifica original.

`pending_proactive_suggestions` guarda também `prepared_response`,
`prepared_model` e `prepared_interaction_id`. Esses campos comprovam que a
resposta secundária foi gerada junto da resposta principal; aceitar a sugestão
somente libera esse conteúdo e não consome uma segunda chamada ao provedor.

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
psql "$DATABASE_URL" -f src/database/sql/04_rag_synthetic_data.sql
psql "$DATABASE_URL" -f src/database/sql/06_verify_secondary_intents.sql
psql "$DATABASE_URL" -f src/database/sql/07_add_pending_proactive_suggestions.sql
psql "$DATABASE_URL" -f src/database/sql/08_add_prepared_proactive_response.sql
```

Em um banco que ja possui o baseline, execute
`05_add_secondary_intents.sql`. A propria migracao cria a tabela e carrega de
forma idempotente os 13 mapeamentos iniciais, sem exigir a reexecucao do
bootstrap. A verificacao `06_verify_secondary_intents.sql` deve
terminar sem erro e sempre executa `ROLLBACK`, inclusive para os registros de
prova usados nos testes de FK e unicidade.

Para comprovar a idempotencia da migracao, execute
`05_add_secondary_intents.sql` uma segunda vez antes de
`06_verify_secondary_intents.sql`. A contagem deve
permanecer em 13 associacoes ativas, sem duplicatas ou registros orfaos.

A carga `04_rag_synthetic_data.sql` deve ser executada depois da carga inicial,
pois reutiliza o projeto sintetico `PRJ-0442` quando um item de origem precisa de
contexto de projeto. Ela e idempotente: `project_artifacts` usa
`partner_source_id` com `ON CONFLICT`, e `source_extracts` evita duplicacao pelo
par `artifact_id` + `source_locator`.

Consultas simples de conferencia:

```bash
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM public.projects;"
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM public.project_artifacts WHERE metadata ->> 'source_file' IN ('base_atendimento.json', 'comunicados_servico.json', 'procedimentos_operacionais.json');"
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM public.source_extracts WHERE metadata ->> 'source_file' IN ('base_atendimento.json', 'comunicados_servico.json', 'procedimentos_operacionais.json');"
```

## Carga de identidades e acessos da S5-03

A autenticação, a carga idempotente das identidades sintéticas e o controle por
perfil e escopo estão consolidados na
[Seção 4.3.1 do Projeto](../../../docs/Projeto.md#431-autenticação-e-controle-de-acesso-do-mvp).

## Verificacao S4-08 e S4-09 no Supabase

No PowerShell, com `DATABASE_URL` ou `SUPABASE_DATABASE_URL` definido apenas
na sessao local e o cliente `psql` instalado, execute:

```powershell
./scripts/verify-supabase.ps1 -ApplySchema -TestSchemaReexecution
```

O comando aplica o baseline em um banco vazio, executa `02_initial_data.sql` e
`04_rag_synthetic_data.sql` duas vezes, compara as contagens por dominio e
registra um evento em `audit_events`. A evidencia sem segredos e gravada em
`docs/evidencias/` com o mesmo `correlation_id`.

O baseline atual deve retornar **27 tabelas, 47 indices explicitos e 27
triggers**. A expectativa anterior de 25/43/25 era do modelo antes das duas
evolucoes posteriores: `secondary_intents` (+1/+1/+1) e
`pending_proactive_suggestions` (+1/+2/+1); a fundacao de acesso acrescenta
um indice unico em `access_rules`. A reexecucao de
`01_create_database.sql` e um erro esperado, pois ele e um baseline para banco
vazio; a idempotencia requerida e comprovada pela carga repetida.

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
