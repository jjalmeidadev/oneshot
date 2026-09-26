BEGIN;

ALTER TABLE public.notification_delivery_attempts
    ADD COLUMN callback_id VARCHAR(160)
        REFERENCES public.notification_delivery_callbacks(callback_id)
        ON DELETE CASCADE;

CREATE UNIQUE INDEX notification_delivery_attempts_callback_uk
    ON public.notification_delivery_attempts (callback_id)
    WHERE callback_id IS NOT NULL;

COMMIT;
