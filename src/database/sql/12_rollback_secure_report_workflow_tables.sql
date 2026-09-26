BEGIN;

-- O rollback desativa o mecanismo de RLS, mas nao torna tabelas internas
-- publicas. Grants anteriores nao sao inferidos nem ampliados automaticamente.
REVOKE ALL ON TABLE public.report_executions FROM anon, authenticated;
REVOKE ALL ON TABLE public.generated_reports FROM anon, authenticated;
REVOKE ALL ON TABLE public.automation_callbacks FROM anon, authenticated;
REVOKE ALL ON TABLE public.workflow_sessions FROM anon, authenticated;
REVOKE ALL ON TABLE public.workflow_answers FROM anon, authenticated;

ALTER TABLE public.report_executions DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.generated_reports DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.automation_callbacks DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_sessions DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_answers DISABLE ROW LEVEL SECURITY;

COMMIT;
