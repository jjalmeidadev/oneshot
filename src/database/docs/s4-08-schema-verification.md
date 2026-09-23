# S4-08 — aplicacao e verificacao do esquema fisico

No Supabase ja existente, aplique somente as migracoes versionadas que ainda
nao estejam presentes. Nesta entrega foram aplicadas `05_add_secondary_intents.sql`
e `07_add_pending_proactive_suggestions.sql`.

Use `scripts/verify-supabase.ps1` para consultar a versao do PostgreSQL,
contar tabelas, indices explicitos e triggers, e registrar a correlacao em
`audit_events`. A tentativa de reaplicar `01_create_database.sql` deve falhar:
ele e um baseline transacional destinado a banco vazio.
