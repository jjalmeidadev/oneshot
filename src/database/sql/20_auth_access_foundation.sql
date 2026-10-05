-- S5-03 / issue #257 and S5-04 / issue #258
-- Foundation for Supabase Auth identity mapping and per-user access rules.
-- PostgreSQL 17+ / Supabase project Oneshot.

BEGIN;

ALTER TABLE public.users
    DROP CONSTRAINT IF EXISTS users_role_ck;

ALTER TABLE public.users
    ADD CONSTRAINT users_role_ck CHECK (
        role_name IN (
            'diretoria',
            'pmo',
            'lider_subportfolio',
            'equipe_projeto',
            'consulta',
            'gti',
            'admin'
        )
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_access_rules_subject_scope
    ON public.access_rules (
        user_id,
        role_name,
        subportfolio_id,
        project_id,
        permission_scope
    )
    NULLS NOT DISTINCT;

COMMENT ON COLUMN public.users.entra_object_id IS
    'No MVP, armazena como texto o UUID auth.users.id recebido no claim JWT sub; nao armazena permissao nem custom claim.';

COMMENT ON TABLE public.access_rules IS
    'Regras de acesso por usuario, perfil, projeto, subportfolio ou escopo de permissao. No MVP, a autorizacao usa regras por user_id; role_name permanece para compatibilidade.';

COMMENT ON INDEX public.uq_access_rules_subject_scope IS
    'Impede regras duplicadas para o mesmo sujeito e escopo; NULLS NOT DISTINCT trata alvos nulos como iguais.';

-- O backend consulta esta tabela por conexao PostgreSQL (psycopg). Nao ha
-- consumidor direto confirmado pela Data API; sem policies, RLS bloqueia
-- anon/authenticated e preserva o acesso do backend privilegiado.
REVOKE ALL ON TABLE public.secondary_intents FROM anon, authenticated;
ALTER TABLE public.secondary_intents ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE public.secondary_intents IS
    'Sugestoes proativas internas, lidas pelo backend via PostgreSQL. RLS sem policies bloqueia acesso direto pela Data API.';

COMMIT;
