-- Resposta secundaria preparada na mesma chamada da resposta principal (#253).
-- A migracao recusa confirmar registros legados sem conteudo precomputado.

BEGIN;

ALTER TABLE public.pending_proactive_suggestions
    ADD COLUMN IF NOT EXISTS prepared_response TEXT,
    ADD COLUMN IF NOT EXISTS prepared_model VARCHAR(160),
    ADD COLUMN IF NOT EXISTS prepared_interaction_id VARCHAR(1024);

DELETE FROM public.pending_proactive_suggestions
WHERE prepared_response IS NULL OR prepared_model IS NULL;

ALTER TABLE public.pending_proactive_suggestions
    ALTER COLUMN prepared_response SET NOT NULL,
    ALTER COLUMN prepared_model SET NOT NULL;

COMMENT ON COLUMN public.pending_proactive_suggestions.prepared_response IS
    'Resposta secundaria gerada junto da resposta principal e liberada somente apos confirmacao.';

COMMIT;
