# Registro de estado anterior — infraestrutura de relatórios

- Criado em: 2026-09-21T15:08:31-03:00
- Escopo: objetos alterados pelas migrações 05, 07 e 09
- Conteúdo: evidência textual de metadados; **não é backup restaurável**
- Banco: Supabase configurado pelo backend (credenciais omitidas)

## Estado anterior

- `public.workflow_sessions`: ausente
- `public.workflow_answers`: ausente por consequência
- `public.report_executions`: ausente
- `public.generated_reports`: ausente por consequência
- `public.automation_callbacks`: ausente por consequência
- `public.report_executions.snapshot_payload`: ausente
- `storage.buckets['generated-reports']`: ausente
- Permissão de inserção em `storage.buckets`: disponível
- Permissão de remoção em `storage.buckets`: disponível

## Constraints preservadas pelo rollback 08

```sql
CHECK (route_taken IN (
    'copilot_topic', 'power_automate', 'sharepoint_query',
    'analise_local', 'fora_escopo'
))

CHECK (component IN (
    'api', 'pln', 'copilot_studio', 'power_automate',
    'm365_copilot', 'sharepoint', 'database'
))
```

## Estratégia de reversão

1. Executar `python -m scripts.rollback_report_storage_bucket`; a API oficial
   do Storage recusa remover um bucket que contenha objetos.
2. Executar `08_rollback_guided_report_workflow.sql`; ele restaura as
   constraints anteriores e remove somente os objetos adicionados pela 07.
3. Executar `06_rollback_report_generation.sql` para remover as tabelas-base
   adicionadas pela migração 05.
