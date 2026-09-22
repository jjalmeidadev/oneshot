-- 14_rollback_portfolio_report_data.sql
-- Reverte 13_seed_portfolio_report_data.sql. Remove os dados de portfolio dos tres
-- projetos e os projetos adicionados pelo seed (PRJ-0510, PRJ-0587). O PRJ-0442 e o
-- subportfolio MOD sao preservados como base anterior.

BEGIN;

DELETE FROM public.project_progress_updates
WHERE project_id IN (SELECT id FROM public.projects WHERE code IN ('PRJ-0442','PRJ-0510','PRJ-0587'));

DELETE FROM public.project_status_updates
WHERE project_id IN (SELECT id FROM public.projects WHERE code IN ('PRJ-0442','PRJ-0510','PRJ-0587'));

DELETE FROM public.project_deliverables_milestones
WHERE project_id IN (SELECT id FROM public.projects WHERE code IN ('PRJ-0442','PRJ-0510','PRJ-0587'));

DELETE FROM public.project_benefits
WHERE project_id IN (SELECT id FROM public.projects WHERE code IN ('PRJ-0442','PRJ-0510','PRJ-0587'));

DELETE FROM public.change_records
WHERE project_id IN (SELECT id FROM public.projects WHERE code IN ('PRJ-0442','PRJ-0510','PRJ-0587'));

DELETE FROM public.risk_issue_items
WHERE project_id IN (SELECT id FROM public.projects WHERE code IN ('PRJ-0442','PRJ-0510','PRJ-0587'));

-- Remove apenas os projetos adicionados pelo seed.
DELETE FROM public.projects WHERE code IN ('PRJ-0510', 'PRJ-0587');

COMMIT;
