-- S5-06 / issue #260 - Alteracao de dados do projeto pelo chat com confirmacao.
-- Contrato: docs/Projeto.md, Secao 8.5.13 (S5-05 / issue #259).
-- PostgreSQL 17+ / Supabase project Oneshot.
--
-- A previa de cada alteracao fica em pending_data_changes ate ser confirmada
-- ou cancelada. A escrita no registro do projeto so acontece na confirmacao,
-- junto com change_records e audit_events, na mesma transacao.

BEGIN;

CREATE TABLE IF NOT EXISTS public.pending_data_changes (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    correlation_id VARCHAR(120) NOT NULL,
    external_conversation_id VARCHAR(160),
    interaction_id UUID REFERENCES public.ai_interactions(id) ON DELETE SET NULL,
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    entity VARCHAR(20) NOT NULL,
    target_id UUID NOT NULL,
    field_key VARCHAR(60) NOT NULL,
    before_value JSONB NOT NULL DEFAULT 'null'::jsonb,
    after_value JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pendente',
    change_record_id UUID REFERENCES public.change_records(id) ON DELETE SET NULL,
    reason TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    decided_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT pending_data_changes_entity_ck
        CHECK (entity IN ('projeto', 'cronograma', 'marco', 'risco')),
    CONSTRAINT pending_data_changes_field_ck CHECK (field_key IN (
        'projeto.status', 'projeto.prazo_final',
        'cronograma.prazo', 'cronograma.status', 'cronograma.progresso',
        'marco.data_prevista', 'marco.status', 'marco.data_conclusao',
        'risco.status', 'risco.responsavel', 'risco.prazo'
    )),
    CONSTRAINT pending_data_changes_status_ck
        CHECK (status IN ('pendente', 'confirmada', 'cancelada')),
    CONSTRAINT pending_data_changes_confirmed_ck
        CHECK (status <> 'confirmada' OR change_record_id IS NOT NULL OR decided_at IS NOT NULL),
    CONSTRAINT pending_data_changes_reason_ck
        CHECK (reason IS NULL OR char_length(reason) <= 500)
);

CREATE INDEX IF NOT EXISTS idx_pending_data_changes_user_status
    ON public.pending_data_changes(user_id, status);
CREATE INDEX IF NOT EXISTS idx_pending_data_changes_correlation
    ON public.pending_data_changes(correlation_id);
CREATE INDEX IF NOT EXISTS idx_pending_data_changes_expires_at
    ON public.pending_data_changes(expires_at);

-- Historico por campo exibido pela S5-07.
CREATE INDEX IF NOT EXISTS idx_change_records_chat_field
    ON public.change_records(project_id, (metadata->>'field'), decided_at DESC)
    WHERE metadata->>'origin' = 'chat';

DROP TRIGGER IF EXISTS trg_pending_data_changes_updated_at ON public.pending_data_changes;
CREATE TRIGGER trg_pending_data_changes_updated_at
    BEFORE UPDATE ON public.pending_data_changes
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- O backend acessa a tabela pela conexao PostgreSQL privilegiada. Sem
-- policies, a RLS bloqueia anon e authenticated pela Data API.
REVOKE ALL ON TABLE public.pending_data_changes FROM anon, authenticated;
ALTER TABLE public.pending_data_changes ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE public.pending_data_changes IS
    'Previas de alteracao pelo chat (S5-06). Nada e gravado no projeto antes da confirmacao.';
COMMENT ON COLUMN public.pending_data_changes.before_value IS
    'Valor canonico lido na previa; a confirmacao exige que o valor atual ainda seja este.';

COMMIT;
