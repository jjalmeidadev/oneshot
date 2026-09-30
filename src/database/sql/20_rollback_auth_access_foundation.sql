-- Rollback especifico e sem remocao de tabelas ou dados para
-- 19_auth_access_foundation.sql.
-- Interrompe sem alterar o schema se usuarios com role_name = 'consulta'
-- tiverem sido criados depois da migration.

BEGIN;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM public.users
        WHERE role_name = 'consulta'
    ) THEN
        RAISE EXCEPTION
            'Rollback bloqueado: existem usuarios com role_name = consulta';
    END IF;
END;
$$;

ALTER TABLE public.users
    DROP CONSTRAINT IF EXISTS users_role_ck;

ALTER TABLE public.users
    ADD CONSTRAINT users_role_ck CHECK (
        role_name IN (
            'diretoria',
            'pmo',
            'lider_subportfolio',
            'equipe_projeto',
            'gti',
            'admin'
        )
    );

DROP INDEX IF EXISTS public.uq_access_rules_subject_scope;

ALTER TABLE public.secondary_intents DISABLE ROW LEVEL SECURITY;
GRANT ALL ON TABLE public.secondary_intents TO anon, authenticated;

COMMENT ON COLUMN public.users.entra_object_id IS NULL;
COMMENT ON TABLE public.access_rules IS
    'Regras de acesso por usuario, perfil, projeto, subportfolio ou escopo de permissao.';
COMMENT ON TABLE public.secondary_intents IS
    'Sugestoes proativas vinculadas a intencoes especificas e enviadas ao RAG como proximo passo opcional.';

COMMIT;
