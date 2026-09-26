-- Resposta secundaria preparada na mesma chamada da resposta principal (#253).
-- Apenas confirmacoes legadas expiradas e nao reivindicadas podem ser removidas.
-- Qualquer registro incompleto restante aborta toda a transacao.

BEGIN;

ALTER TABLE public.pending_proactive_suggestions
    ADD COLUMN IF NOT EXISTS prepared_response TEXT,
    ADD COLUMN IF NOT EXISTS prepared_model VARCHAR(160),
    ADD COLUMN IF NOT EXISTS prepared_interaction_id VARCHAR(1024);

DELETE FROM public.pending_proactive_suggestions
WHERE (prepared_response IS NULL OR prepared_model IS NULL)
  AND expires_at < NOW()
  AND claimed_at IS NULL;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM public.pending_proactive_suggestions
        WHERE prepared_response IS NULL OR prepared_model IS NULL
    ) THEN
        RAISE EXCEPTION 'Registros pendentes sem resposta ou modelo preparado permanecem; migracao 08 cancelada';
    END IF;
END;
$$;

ALTER TABLE public.pending_proactive_suggestions
    ALTER COLUMN prepared_response SET NOT NULL,
    ALTER COLUMN prepared_model SET NOT NULL;

ALTER TABLE public.pending_proactive_suggestions ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.pending_proactive_suggestions FROM anon, authenticated;

COMMENT ON COLUMN public.pending_proactive_suggestions.prepared_response IS
    'Resposta secundaria gerada junto da resposta principal e liberada somente apos confirmacao.';

COMMIT;
