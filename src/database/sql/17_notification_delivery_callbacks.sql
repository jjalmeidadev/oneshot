BEGIN;

ALTER TABLE public.notification_delivery_attempts
    DROP CONSTRAINT notification_delivery_attempts_status_ck;
ALTER TABLE public.notification_delivery_attempts
    ADD CONSTRAINT notification_delivery_attempts_status_ck
    CHECK (status IN ('available','delivered','failed'));

CREATE TABLE public.notification_delivery_callbacks (
    callback_id VARCHAR(160) PRIMARY KEY,
    notification_id UUID NOT NULL
        REFERENCES public.alert_notifications(notification_id) ON DELETE CASCADE,
    payload_hash CHAR(64) NOT NULL,
    callback_payload JSONB NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT notification_delivery_callbacks_hash_ck
        CHECK (char_length(payload_hash) = 64)
);

CREATE INDEX notification_delivery_callbacks_notification_idx
    ON public.notification_delivery_callbacks (notification_id, received_at DESC);

ALTER TABLE public.notification_delivery_callbacks ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.notification_delivery_callbacks FROM anon, authenticated;

COMMIT;
