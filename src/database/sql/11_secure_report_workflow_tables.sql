BEGIN;

ALTER TABLE public.report_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.generated_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.automation_callbacks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_answers ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.report_executions FROM anon, authenticated;
REVOKE ALL ON TABLE public.generated_reports FROM anon, authenticated;
REVOKE ALL ON TABLE public.automation_callbacks FROM anon, authenticated;
REVOKE ALL ON TABLE public.workflow_sessions FROM anon, authenticated;
REVOKE ALL ON TABLE public.workflow_answers FROM anon, authenticated;

COMMIT;
