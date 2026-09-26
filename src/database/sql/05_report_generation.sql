BEGIN;

CREATE TABLE public.report_executions (
    execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    correlation_id VARCHAR(120) NOT NULL,
    conversation_id VARCHAR(160) NOT NULL,
    interaction_id VARCHAR(160),
    idempotency_key VARCHAR(160) NOT NULL,
    requested_by VARCHAR(160) NOT NULL,
    scope_type VARCHAR(20) NOT NULL,
    scope_id VARCHAR(120) NOT NULL,
    report_type VARCHAR(60) NOT NULL,
    execution_status VARCHAR(40) NOT NULL,
    confirmation_hash VARCHAR(120) NOT NULL,
    request_payload JSONB NOT NULL,
    snapshot_hash VARCHAR(64),
    sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    warnings JSONB NOT NULL DEFAULT '[]'::jsonb,
    error_code VARCHAR(80),
    error_message VARCHAR(500),
    flow_run_id VARCHAR(160),
    callback_id VARCHAR(160),
    events JSONB NOT NULL DEFAULT '[]'::jsonb,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT report_executions_idempotency_uk UNIQUE (requested_by, idempotency_key),
    CONSTRAINT report_executions_scope_ck CHECK (scope_type IN ('project', 'subportfolio')),
    CONSTRAINT report_executions_type_ck CHECK (report_type IN ('executive_status')),
    CONSTRAINT report_executions_status_ck CHECK (
        execution_status IN (
            'confirmed', 'queued', 'processing', 'completed',
            'completed_with_warnings', 'failed', 'blocked', 'cancelled'
        )
    )
);

CREATE INDEX report_executions_correlation_idx
    ON public.report_executions (correlation_id);
CREATE INDEX report_executions_status_created_idx
    ON public.report_executions (execution_status, created_at DESC);

CREATE TABLE public.generated_reports (
    artifact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL UNIQUE
        REFERENCES public.report_executions(execution_id) ON DELETE CASCADE,
    file_name VARCHAR(260) NOT NULL,
    content_type VARCHAR(160) NOT NULL,
    size_bytes BIGINT NOT NULL,
    sha256 VARCHAR(64) NOT NULL,
    download_url TEXT NOT NULL,
    storage_provider VARCHAR(40) NOT NULL,
    storage_reference TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT generated_reports_size_ck CHECK (size_bytes >= 0),
    CONSTRAINT generated_reports_sha_ck CHECK (char_length(sha256) = 64),
    CONSTRAINT generated_reports_storage_ck CHECK (
        storage_provider IN ('local', 'sharepoint', 'onedrive')
    )
);

CREATE TABLE public.automation_callbacks (
    callback_id VARCHAR(160) PRIMARY KEY,
    execution_id UUID NOT NULL
        REFERENCES public.report_executions(execution_id) ON DELETE CASCADE,
    payload_hash VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT automation_callbacks_hash_ck CHECK (char_length(payload_hash) = 64)
);

CREATE INDEX automation_callbacks_execution_idx
    ON public.automation_callbacks (execution_id, received_at DESC);

COMMIT;
