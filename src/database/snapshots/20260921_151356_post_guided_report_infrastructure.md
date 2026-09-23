# Registro de estado posterior — infraestrutura de relatórios aplicada

- Criado em: 2026-09-21T15:13:56-03:00
- Atualizado após auditoria de segurança: 2026-09-21T15:28:03-03:00
- Migrações aplicadas: 05, 07, 09 e 11
- Conteúdo: evidência textual de metadados; **não é backup restaurável**
- Banco: Supabase configurado pelo backend (credenciais omitidas)

## Estado verificado

- `public.report_executions`: presente
- `public.generated_reports`: presente
- `public.automation_callbacks`: presente
- `public.workflow_sessions`: presente
- `public.workflow_answers`: presente
- `public.report_executions.snapshot_payload`: presente
- Bucket `generated-reports`: presente e privado
- Limite por arquivo: 10 MiB (`10485760` bytes)
- MIME permitido: DOCX
- RLS: ativa nas cinco tabelas internas
- Acesso `anon` e `authenticated`: revogado

## Constraints verificadas

- Rota: `guided_workflow`, `power_automate`, `sharepoint_query`,
  `analise_local` ou `fora_escopo`.
- Componente de auditoria: inclui `guided_workflow` e `supabase_storage`.
- Provedor de artefato: `local` ou `supabase`.

## Rollback

Este arquivo não restaura dados. Para reverter apenas o isolamento, executar
`12_rollback_secure_report_workflow_tables.sql`. Para remover integralmente a
feature, executar, nesta ordem:

1. `python -m scripts.rollback_report_storage_bucket` — requer a service role
   e a API oficial aborta se houver objetos;
2. `08_rollback_guided_report_workflow.sql`;
3. `06_rollback_report_generation.sql`.
