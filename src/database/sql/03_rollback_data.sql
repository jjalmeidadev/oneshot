-- Rollback completo do modelo fisico - MVP Agente de IA para Portfolio Metro
-- Uso previsto apenas em ambiente de desenvolvimento/PoC, apos snapshot quando houver banco aplicado.

BEGIN;

DROP TABLE IF EXISTS public.intent_test_cases CASCADE;
DROP TABLE IF EXISTS public.out_of_scope_requests CASCADE;
DROP TABLE IF EXISTS public.audit_events CASCADE;
DROP TABLE IF EXISTS public.consulted_sources CASCADE;
DROP TABLE IF EXISTS public.ai_interactions CASCADE;
DROP TABLE IF EXISTS public.ai_conversations CASCADE;
DROP TABLE IF EXISTS public.prompt_templates CASCADE;
DROP TABLE IF EXISTS public.intent_catalog CASCADE;
DROP TABLE IF EXISTS public.access_rules CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;
DROP TABLE IF EXISTS public.change_records CASCADE;
DROP TABLE IF EXISTS public.risk_issue_history CASCADE;
DROP TABLE IF EXISTS public.risk_issue_items CASCADE;
DROP TABLE IF EXISTS public.project_benefits CASCADE;
DROP TABLE IF EXISTS public.project_closure_terms CASCADE;
DROP TABLE IF EXISTS public.project_charters CASCADE;
DROP TABLE IF EXISTS public.project_deliverables_milestones CASCADE;
DROP TABLE IF EXISTS public.project_status_updates CASCADE;
DROP TABLE IF EXISTS public.project_progress_updates CASCADE;
DROP TABLE IF EXISTS public.schedule_items CASCADE;
DROP TABLE IF EXISTS public.source_extracts CASCADE;
DROP TABLE IF EXISTS public.project_artifacts CASCADE;
DROP TABLE IF EXISTS public.subportfolio_status_updates CASCADE;
DROP TABLE IF EXISTS public.projects CASCADE;
DROP TABLE IF EXISTS public.subportfolios CASCADE;

DROP FUNCTION IF EXISTS public.set_updated_at() CASCADE;

COMMIT;
