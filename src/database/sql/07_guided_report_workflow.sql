BEGIN;

ALTER TABLE public.report_executions
    ADD COLUMN IF NOT EXISTS snapshot_payload JSONB;

ALTER TABLE public.generated_reports
    DROP CONSTRAINT IF EXISTS generated_reports_storage_ck;
ALTER TABLE public.generated_reports
    ADD CONSTRAINT generated_reports_storage_ck
    CHECK (storage_provider IN ('local', 'supabase'));

ALTER TABLE public.ai_interactions
    DROP CONSTRAINT IF EXISTS ai_interactions_route_ck;
ALTER TABLE public.ai_interactions
    ADD CONSTRAINT ai_interactions_route_ck
    CHECK (route_taken IN (
        'guided_workflow', 'power_automate', 'sharepoint_query',
        'analise_local', 'fora_escopo'
    ));

ALTER TABLE public.audit_events
    DROP CONSTRAINT IF EXISTS audit_events_component_ck;
ALTER TABLE public.audit_events
    ADD CONSTRAINT audit_events_component_ck
    CHECK (component IN (
        'api', 'pln', 'guided_workflow', 'power_automate',
        'm365_copilot', 'sharepoint', 'database', 'supabase_storage'
    ));

CREATE TABLE public.workflow_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_name VARCHAR(80) NOT NULL,
    requested_by VARCHAR(160) NOT NULL,
    conversation_id VARCHAR(160) NOT NULL,
    interaction_id VARCHAR(160),
    correlation_id VARCHAR(120) NOT NULL,
    workflow_status VARCHAR(40) NOT NULL,
    current_step VARCHAR(60) NOT NULL,
    revision INTEGER NOT NULL DEFAULT 0,
    session_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT workflow_sessions_name_ck
        CHECK (workflow_name IN ('transacao_gerar_relatorio')),
    CONSTRAINT workflow_sessions_status_ck
        CHECK (workflow_status IN (
            'active', 'ready_for_confirmation', 'executing',
            'completed', 'cancelled'
        )),
    CONSTRAINT workflow_sessions_revision_ck CHECK (revision >= 0)
);

CREATE INDEX workflow_sessions_conversation_idx
    ON public.workflow_sessions (conversation_id, updated_at DESC);
CREATE INDEX workflow_sessions_requester_idx
    ON public.workflow_sessions (requested_by, updated_at DESC);

CREATE TABLE public.workflow_answers (
    answer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL
        REFERENCES public.workflow_sessions(session_id) ON DELETE CASCADE,
    step VARCHAR(60) NOT NULL,
    answer_payload JSONB,
    client_action_id VARCHAR(160) NOT NULL UNIQUE,
    answered_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX workflow_answers_session_idx
    ON public.workflow_answers (session_id, answered_at);

COMMIT;
