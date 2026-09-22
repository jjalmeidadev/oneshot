BEGIN;

ALTER TABLE public.workflow_sessions DROP CONSTRAINT IF EXISTS workflow_sessions_name_ck;
ALTER TABLE public.workflow_sessions ADD CONSTRAINT workflow_sessions_name_ck
    CHECK (workflow_name IN ('transacao_gerar_relatorio', 'alerta_prazo_atraso'));

ALTER TABLE public.workflow_sessions DROP CONSTRAINT IF EXISTS workflow_sessions_status_ck;
ALTER TABLE public.workflow_sessions ADD CONSTRAINT workflow_sessions_status_ck
    CHECK (workflow_status IN ('active','ready_for_confirmation','executing','completed','cancelled'));

ALTER TABLE public.audit_events DROP CONSTRAINT IF EXISTS audit_events_component_ck;
ALTER TABLE public.audit_events ADD CONSTRAINT audit_events_component_ck CHECK (component IN (
    'api','pln','guided_workflow','power_automate','m365_copilot','sharepoint',
    'database','supabase_storage','alert_workflow','alert_scheduler',
    'alert_evaluator','message_bus','notification_dispatcher'
));

CREATE TABLE public.alert_subscriptions (
    subscription_id UUID PRIMARY KEY,
    owner_subject VARCHAR(160) NOT NULL,
    project_id VARCHAR(120) NOT NULL,
    status VARCHAR(30) NOT NULL,
    next_evaluation_at TIMESTAMPTZ NOT NULL,
    revision INTEGER NOT NULL DEFAULT 0,
    idempotency_key VARCHAR(160) NOT NULL,
    correlation_id VARCHAR(120) NOT NULL,
    subscription_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT alert_subscriptions_status_ck CHECK (status IN ('active','paused','cancelled','blocked')),
    CONSTRAINT alert_subscriptions_owner_idempotency_uk UNIQUE (owner_subject,idempotency_key)
);
CREATE INDEX alert_subscriptions_due_idx ON public.alert_subscriptions(status,next_evaluation_at);
CREATE INDEX alert_subscriptions_owner_idx ON public.alert_subscriptions(owner_subject,created_at DESC);

CREATE TABLE public.alert_evaluations (
    evaluation_id UUID PRIMARY KEY,
    subscription_id UUID NOT NULL REFERENCES public.alert_subscriptions(subscription_id) ON DELETE CASCADE,
    correlation_id VARCHAR(120) NOT NULL,
    as_of_date DATE NOT NULL,
    outcome VARCHAR(30) NOT NULL,
    snapshot_hash CHAR(64) NOT NULL,
    evaluation_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT alert_evaluations_outcome_ck CHECK (outcome IN ('matched','not_matched','indeterminate','failed'))
);
CREATE INDEX alert_evaluations_subscription_idx ON public.alert_evaluations(subscription_id,created_at DESC);

CREATE TABLE public.alert_occurrences (
    occurrence_id UUID PRIMARY KEY,
    subscription_id UUID NOT NULL REFERENCES public.alert_subscriptions(subscription_id) ON DELETE CASCADE,
    item_id VARCHAR(160) NOT NULL,
    episode_key VARCHAR(500) NOT NULL UNIQUE,
    first_detected_at TIMESTAMPTZ NOT NULL,
    last_seen_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,
    state VARCHAR(30) NOT NULL,
    CONSTRAINT alert_occurrences_state_ck CHECK (state IN ('open','resolved','suppressed'))
);

CREATE TABLE public.alert_notifications (
    notification_id UUID PRIMARY KEY,
    occurrence_id UUID NOT NULL REFERENCES public.alert_occurrences(occurrence_id) ON DELETE CASCADE,
    subscription_id UUID NOT NULL REFERENCES public.alert_subscriptions(subscription_id) ON DELETE CASCADE,
    recipient_subject VARCHAR(160) NOT NULL,
    status VARCHAR(30) NOT NULL,
    notification_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    read_at TIMESTAMPTZ,
    CONSTRAINT alert_notifications_status_ck CHECK (status IN ('pending','available','read','failed'))
);
CREATE INDEX alert_notifications_recipient_idx ON public.alert_notifications(recipient_subject,status,created_at DESC);

CREATE TABLE public.notification_delivery_attempts (
    attempt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notification_id UUID NOT NULL REFERENCES public.alert_notifications(notification_id) ON DELETE CASCADE,
    channel VARCHAR(30) NOT NULL DEFAULT 'in_app',
    attempt_number INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL,
    error_code VARCHAR(120),
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT notification_delivery_attempts_status_ck CHECK (status IN ('available','failed')),
    CONSTRAINT notification_delivery_attempts_uk UNIQUE (notification_id,attempt_number)
);

CREATE TABLE public.message_outbox (
    event_id UUID PRIMARY KEY,
    event_type VARCHAR(120) NOT NULL,
    correlation_id VARCHAR(120) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    attempts INTEGER NOT NULL DEFAULT 0,
    available_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT message_outbox_status_ck CHECK (status IN ('pending','publishing','published','failed'))
);
CREATE INDEX message_outbox_pending_idx ON public.message_outbox(status,available_at,created_at);

ALTER TABLE public.alert_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alert_evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alert_occurrences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alert_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.message_outbox ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notification_delivery_attempts ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.alert_subscriptions,public.alert_evaluations,public.alert_occurrences,public.alert_notifications,public.notification_delivery_attempts,public.message_outbox FROM anon,authenticated;

COMMIT;
