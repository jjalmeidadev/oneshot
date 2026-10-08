-- Reverte 22_data_change_previews.sql.
-- As linhas de change_records criadas pelo chat (metadata->>'origin' = 'chat')
-- sao preservadas: fazem parte da trilha de auditoria e nao dependem da tabela
-- de previas.

BEGIN;

DROP INDEX IF EXISTS public.idx_change_records_chat_field;
DROP TABLE IF EXISTS public.pending_data_changes;

COMMIT;
