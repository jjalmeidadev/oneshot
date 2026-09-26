BEGIN;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM public.ai_interactions
        WHERE route_taken = 'guided_workflow'
    ) OR EXISTS (
        SELECT 1 FROM public.audit_events
        WHERE component IN ('guided_workflow', 'supabase_storage')
    ) THEN
        RAISE EXCEPTION USING
            MESSAGE = 'Rollback 08 abortado: existem registros de auditoria do workflow; preserve ou arquive-os antes da reversao.';
    END IF;
END $$;

DROP TABLE IF EXISTS public.workflow_answers;
DROP TABLE IF EXISTS public.workflow_sessions;

ALTER TABLE public.report_executions
    DROP COLUMN IF EXISTS snapshot_payload;

-- Nao reduz deliberadamente generated_reports_storage_ck: linhas existentes
-- com storage_provider='supabase' continuariam validas. O rollback integral
-- remove a tabela pela migracao 06 depois que o bucket estiver vazio.

ALTER TABLE public.ai_interactions
    DROP CONSTRAINT IF EXISTS ai_interactions_route_ck;
ALTER TABLE public.ai_interactions
    ADD CONSTRAINT ai_interactions_route_ck
    CHECK (route_taken IN (
        'copilot_topic', 'power_automate', 'sharepoint_query',
        'analise_local', 'fora_escopo'
    ));

ALTER TABLE public.audit_events
    DROP CONSTRAINT IF EXISTS audit_events_component_ck;
ALTER TABLE public.audit_events
    ADD CONSTRAINT audit_events_component_ck
    CHECK (component IN (
        'api', 'pln', 'copilot_studio', 'power_automate',
        'm365_copilot', 'sharepoint', 'database'
    ));

COMMIT;
