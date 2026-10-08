-- S5-05 / issue #259 - Conferencia do contrato de alteracao pelo chat
-- (Projeto.md, Secao 8.5.13) contra o schema versionado.
--
-- Pre-requisito: 01_create_database.sql, 02_initial_data.sql,
-- 13_seed_portfolio_report_data.sql e 20_auth_access_foundation.sql aplicados.
-- Tudo roda em uma transacao encerrada com ROLLBACK: nenhum dado fica gravado.
-- Qualquer divergencia interrompe o script com EXCEPTION.

\set ON_ERROR_STOP on
BEGIN;

-- 1. As onze colunas editaveis existem com o tipo esperado ------------------
DO $$
DECLARE
    expected CONSTANT text[][] := ARRAY[
        ['projects', 'status', 'character varying'],
        ['projects', 'planned_end_date', 'date'],
        ['schedule_items', 'planned_end_date', 'date'],
        ['schedule_items', 'status', 'character varying'],
        ['schedule_items', 'progress_percent', 'numeric'],
        ['project_deliverables_milestones', 'planned_date', 'date'],
        ['project_deliverables_milestones', 'status', 'character varying'],
        ['project_deliverables_milestones', 'completed_date', 'date'],
        ['risk_issue_items', 'status', 'character varying'],
        ['risk_issue_items', 'owner_name', 'character varying'],
        ['risk_issue_items', 'due_date', 'date']
    ];
    item text[];
    found text;
BEGIN
    FOREACH item SLICE 1 IN ARRAY expected LOOP
        SELECT data_type INTO found
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = item[1] AND column_name = item[2];
        IF found IS DISTINCT FROM item[3] THEN
            RAISE EXCEPTION 'Coluna %.% esperada como %, encontrada como %', item[1], item[2], item[3], found;
        END IF;
    END LOOP;
    RAISE NOTICE '1. Onze colunas editaveis conferidas.';
END $$;

-- 2. Os conjuntos de status do contrato cabem nas restricoes do banco -------
DO $$
DECLARE
    v_project_id uuid := (SELECT id FROM public.projects WHERE code = 'PRJ-0442');
    v_risk_id uuid := (
        SELECT r.id FROM public.risk_issue_items r
        JOIN public.projects p ON p.id = r.project_id
        WHERE p.code = 'PRJ-0442' ORDER BY r.title LIMIT 1
    );
    value text;
BEGIN
    FOREACH value IN ARRAY ARRAY['planejado', 'em_andamento', 'atencao', 'critico', 'suspenso'] LOOP
        UPDATE public.projects SET status = value WHERE id = v_project_id;
    END LOOP;
    FOREACH value IN ARRAY ARRAY['aberto', 'em_tratamento', 'mitigado', 'resolvido', 'aceito', 'cancelado'] LOOP
        UPDATE public.risk_issue_items SET status = value WHERE id = v_risk_id;
    END LOOP;
    -- concluido e descontinuado sao aceitos pelo banco: a restricao e do contrato.
    IF pg_get_constraintdef((SELECT oid FROM pg_constraint WHERE conname = 'projects_status_ck')) NOT LIKE '%descontinuado%' THEN
        RAISE EXCEPTION 'projects_status_ck mudou; revise o contrato.';
    END IF;
    IF pg_get_constraintdef((SELECT oid FROM pg_constraint WHERE conname = 'schedule_items_status_ck')) NOT LIKE '%bloqueado%'
       OR pg_get_constraintdef((SELECT oid FROM pg_constraint WHERE conname = 'schedule_items_progress_ck')) NOT LIKE '%100%' THEN
        RAISE EXCEPTION 'Restricoes de schedule_items mudaram; revise o contrato.';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid = 'public.project_deliverables_milestones'::regclass AND contype = 'c') THEN
        RAISE EXCEPTION 'project_deliverables_milestones ganhou restricao CHECK; revise o conjunto de marco.status.';
    END IF;
    RAISE NOTICE '2. Status de projeto e risco aceitos; restricoes de cronograma e marco conferidas.';
END $$;
ROLLBACK;
BEGIN;

-- 3. Os exemplos da secao 8.5.13 correspondem a massa sintetica -------------
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public.projects WHERE code = 'PRJ-0442' AND planned_end_date = DATE '2026-12-20') THEN
        RAISE EXCEPTION 'Exemplo 1: PRJ-0442 deveria ter prazo final 2026-12-20.';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM public.risk_issue_items r JOIN public.projects p ON p.id = r.project_id
        WHERE p.code = 'PRJ-0442' AND r.title = 'Interferencia com a operacao comercial' AND r.status = 'aberto'
    ) THEN
        RAISE EXCEPTION 'Exemplo 2: risco de interferencia deveria estar aberto.';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM public.project_deliverables_milestones m JOIN public.projects p ON p.id = m.project_id
        WHERE p.code = 'PRJ-0442' AND m.description = 'Inicio da operacao assistida na Linha Azul' AND m.status = 'planejado'
    ) THEN
        RAISE EXCEPTION 'Exemplo 3: marco de operacao assistida deveria estar planejado.';
    END IF;
    RAISE NOTICE '3. Os tres exemplos conferem com a massa.';
    RAISE NOTICE '   schedule_items na massa versionada: % linha(s).', (SELECT count(*) FROM public.schedule_items);
END $$;

-- 4. Confirmacao do exemplo 1, no formato do contrato ------------------------
DO $$
DECLARE
    v_project_id uuid := (SELECT id FROM public.projects WHERE code = 'PRJ-0442');
    v_change_id uuid;
    v_before date;
BEGIN
    SELECT planned_end_date INTO v_before FROM public.projects WHERE id = v_project_id FOR UPDATE;
    UPDATE public.projects SET planned_end_date = DATE '2027-03-31' WHERE id = v_project_id;

    INSERT INTO public.change_records (
        scope_type, project_id, change_type, title, source_label, impact_summary,
        requested_by, status, registration_date, decided_at, metadata
    ) VALUES (
        'projeto', v_project_id, 'prazo',
        'Alteração pelo chat: Prazo final previsto de PRJ-0442', 'chat',
        'Prazo final previsto: 20/12/2026 → 31/03/2027',
        '[DEMO] Gerente de Projeto', 'implementada',
        (NOW() AT TIME ZONE 'America/Sao_Paulo')::date, NOW(),
        jsonb_build_object(
            'origin', 'chat', 'contract', 's5-05/v1',
            'field', 'projeto.prazo_final', 'table', 'projects', 'column', 'planned_end_date',
            'target_id', v_project_id, 'before', v_before, 'after', DATE '2027-03-31',
            'applied_at', NOW(), 'undo', NULL
        )
    ) RETURNING id INTO v_change_id;

    INSERT INTO public.audit_events (event_type, component, event_status, event_payload, correlation_id)
    VALUES ('project_data.change_applied', 'api', 'sucesso',
            jsonb_build_object('field', 'projeto.prazo_final', 'project_code', 'PRJ-0442',
                               'change_id', v_change_id, 'before', v_before, 'after', DATE '2027-03-31'),
            'conferencia-s5-05');

    -- 5. Desfazer: restaura o valor e marca o registro como cancelado --------
    PERFORM 1 FROM public.projects WHERE id = v_project_id AND planned_end_date = DATE '2027-03-31' FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'O valor atual deveria ser o gravado pela alteracao.';
    END IF;
    UPDATE public.projects SET planned_end_date = v_before WHERE id = v_project_id;
    UPDATE public.change_records
    SET status = 'cancelada',
        metadata = jsonb_set(metadata, '{undo}', jsonb_build_object('undone_at', NOW()))
    WHERE id = v_change_id;
    INSERT INTO public.audit_events (event_type, component, event_status, event_payload, correlation_id)
    VALUES ('project_data.change_undone', 'api', 'sucesso',
            jsonb_build_object('change_id', v_change_id), 'conferencia-s5-05');

    IF (SELECT planned_end_date FROM public.projects WHERE id = v_project_id) <> v_before THEN
        RAISE EXCEPTION 'O desfazer nao restaurou o valor anterior.';
    END IF;
    RAISE NOTICE '4. Confirmacao gravada em projects, change_records e audit_events.';
    RAISE NOTICE '5. Desfazer restaurou % e marcou o registro como cancelada.', v_before;
END $$;

-- 6. Os demais eventos e status de auditoria cabem nas restricoes ------------
INSERT INTO public.audit_events (event_type, component, event_status, correlation_id)
VALUES
    ('project_data.change_previewed', 'api', 'pendente', 'conferencia-s5-05'),
    ('project_data.change_rejected', 'api', 'falha', 'conferencia-s5-05'),
    ('authorization.access_denied', 'api', 'bloqueado', 'conferencia-s5-05'),
    ('project_data.change_cancelled', 'api', 'sucesso', 'conferencia-s5-05'),
    ('project_data.change_confirm_failed', 'api', 'falha', 'conferencia-s5-05'),
    ('project_data.undo_denied', 'api', 'bloqueado', 'conferencia-s5-05');
SELECT '6. Oito tipos de evento aceitos por audit_events: '
       || count(DISTINCT event_type) AS resultado
FROM public.audit_events WHERE correlation_id = 'conferencia-s5-05';

ROLLBACK;
