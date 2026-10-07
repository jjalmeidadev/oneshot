BEGIN;

CREATE TABLE public.sharepoint_webhook_events (
    event_id UUID PRIMARY KEY,
    subscription_id VARCHAR(160) NOT NULL,
    change_type VARCHAR(16) NOT NULL,
    resource VARCHAR(320) NOT NULL,
    site_id VARCHAR(160) NOT NULL,
    list_id VARCHAR(160) NOT NULL,
    item_id BIGINT NOT NULL,
    partner_source_id VARCHAR(240) NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    payload_hash CHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    processing_status VARCHAR(16) NOT NULL DEFAULT 'pending',
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    processed_at TIMESTAMPTZ,
    failure_count INTEGER NOT NULL DEFAULT 0,
    last_error_code VARCHAR(120),
    CONSTRAINT sharepoint_webhook_events_change_type_ck
        CHECK (change_type IN ('created', 'updated', 'deleted')),
    CONSTRAINT sharepoint_webhook_events_item_id_ck CHECK (item_id > 0),
    CONSTRAINT sharepoint_webhook_events_payload_hash_ck
        CHECK (payload_hash ~ '^[0-9a-f]{64}$'),
    CONSTRAINT sharepoint_webhook_events_processing_status_ck
        CHECK (processing_status IN ('pending', 'published', 'processing', 'processed', 'failed')),
    CONSTRAINT sharepoint_webhook_events_failure_count_ck CHECK (failure_count >= 0)
);

CREATE INDEX sharepoint_webhook_events_pending_idx
    ON public.sharepoint_webhook_events (received_at, event_id)
    WHERE processing_status = 'pending';

CREATE INDEX sharepoint_webhook_events_source_idx
    ON public.sharepoint_webhook_events (partner_source_id, occurred_at DESC);

ALTER TABLE public.sharepoint_webhook_events ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.sharepoint_webhook_events FROM anon, authenticated;

COMMIT;
