-- Armazenamento compartilhado das confirmacoes proativas (issue #250).
-- Seguro para reexecucao em ambientes que ja receberam a tabela.

BEGIN;

CREATE TABLE IF NOT EXISTS public.pending_proactive_suggestions (
    id UUID PRIMARY KEY,
    requester_id VARCHAR(120) NOT NULL,
    external_conversation_id VARCHAR(160) NOT NULL,
    original_message TEXT NOT NULL,
    secondary_intent JSONB NOT NULL,
    sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    prepared_response TEXT NOT NULL,
    prepared_model VARCHAR(160) NOT NULL,
    prepared_interaction_id VARCHAR(1024),
    expires_at TIMESTAMPTZ NOT NULL,
    claimed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT pending_proactive_secondary_object_ck CHECK (jsonb_typeof(secondary_intent) = 'object'),
    CONSTRAINT pending_proactive_sources_array_ck CHECK (jsonb_typeof(sources) = 'array')
);

CREATE INDEX IF NOT EXISTS idx_pending_proactive_scope
    ON public.pending_proactive_suggestions(requester_id, external_conversation_id);
CREATE INDEX IF NOT EXISTS idx_pending_proactive_expires_at
    ON public.pending_proactive_suggestions(expires_at);

DROP TRIGGER IF EXISTS trg_pending_proactive_updated_at
    ON public.pending_proactive_suggestions;
CREATE TRIGGER trg_pending_proactive_updated_at
    BEFORE UPDATE ON public.pending_proactive_suggestions
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

COMMENT ON TABLE public.pending_proactive_suggestions IS
    'Confirmacoes proativas efemeras, vinculadas a identidade e conversa e compartilhadas entre workers.';

COMMIT;
