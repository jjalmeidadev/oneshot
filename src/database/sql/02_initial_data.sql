-- Carga inicial sintetica - MVP Agente de IA para Portfolio Metro
-- Dados ficticios para demonstracao e validacao do modelo fisico.

BEGIN;

WITH upsert_subportfolio AS (
    INSERT INTO public.subportfolios (
        partner_source_id,
        code,
        title,
        responsible_name,
        gpm_member_name,
        approver_name,
        support_name,
        description,
        strategic_objective
    )
    VALUES (
        'SUB-MOCK-001',
        'MOD',
        'Modernizacao',
        'Mariana Souza',
        'Carlos Almeida',
        'Roberto Lima',
        'Equipe PMO',
        'Subportfolio sintetico usado para validacao da PoC.',
        'Aumentar confiabilidade operacional e qualidade da informacao do portfolio.'
    )
    ON CONFLICT (code) DO UPDATE SET
        title = EXCLUDED.title,
        responsible_name = EXCLUDED.responsible_name,
        gpm_member_name = EXCLUDED.gpm_member_name,
        approver_name = EXCLUDED.approver_name,
        support_name = EXCLUDED.support_name,
        description = EXCLUDED.description,
        strategic_objective = EXCLUDED.strategic_objective,
        updated_at = NOW()
    RETURNING id
),
upsert_project AS (
    INSERT INTO public.projects (
        subportfolio_id,
        partner_source_id,
        code,
        title,
        description,
        sponsor_name,
        project_manager_name,
        program_project_status,
        status,
        start_date,
        planned_end_date
    )
    SELECT
        id,
        'PRJ-MOCK-0442',
        'PRJ-0442',
        'Modernizacao do Sistema de Sinalizacao',
        'Projeto sintetico usado para consultas, auditoria e testes de fontes.',
        'Roberto Lima',
        'Carlos Almeida',
        'Em andamento',
        'em_andamento',
        DATE '2026-01-15',
        DATE '2026-12-20'
    FROM upsert_subportfolio
    WHERE TRUE
    ON CONFLICT (code) DO UPDATE SET
        title = EXCLUDED.title,
        description = EXCLUDED.description,
        sponsor_name = EXCLUDED.sponsor_name,
        project_manager_name = EXCLUDED.project_manager_name,
        program_project_status = EXCLUDED.program_project_status,
        status = EXCLUDED.status,
        start_date = EXCLUDED.start_date,
        planned_end_date = EXCLUDED.planned_end_date,
        updated_at = NOW()
    RETURNING id, subportfolio_id
),
insert_artifact AS (
    INSERT INTO public.project_artifacts (
        project_id,
        partner_source_id,
        artifact_type,
        title,
        description,
        sharepoint_url,
        attachment_name,
        source_status_label,
        metadata
    )
    SELECT
        id,
        'ART-MOCK-TAP-0442',
        'tap',
        'TAP - Modernizacao do Sistema de Sinalizacao',
        'Termo de abertura sintetico para demonstracao.',
        'https://mock.sharepoint.local/sites/portfolio/Lists/TAP/ART-MOCK-TAP-0442',
        'tap_prj_0442.docx',
        'Publicado',
        '{"mock": true}'::jsonb
    FROM upsert_project
    WHERE NOT EXISTS (
        SELECT 1 FROM public.project_artifacts
        WHERE partner_source_id = 'ART-MOCK-TAP-0442'
    )
    RETURNING id, project_id
),
artifact_ref AS (
    SELECT id, project_id FROM insert_artifact
    UNION ALL
    SELECT id, project_id
    FROM public.project_artifacts
    WHERE partner_source_id = 'ART-MOCK-TAP-0442'
    LIMIT 1
),
insert_charter AS (
    INSERT INTO public.project_charters (
        project_id,
        subportfolio_id,
        artifact_id,
        partner_source_id,
        status,
        item,
        leader_name,
        team_text,
        objective,
        justification,
        scope_text,
        non_scope_text,
        expected_benefits,
        start_date,
        end_date,
        cost_brl,
        funding_source,
        sponsor_name,
        revision_number,
        tap_situation,
        release_status
    )
    SELECT
        p.id,
        p.subportfolio_id,
        a.id,
        'TAP-MOCK-0442-R1',
        'Publicado',
        'TAP PRJ-0442',
        'Carlos Almeida',
        'PMO, Engenharia e Operacao',
        'Modernizar o sistema de sinalizacao em ambiente controlado.',
        'Reduzir riscos operacionais e melhorar previsibilidade de execucao.',
        'Atualizacao de componentes de sinalizacao e validacao operacional.',
        'Nao inclui intervencoes em sistemas fora do trecho piloto.',
        'Reducao de falhas operacionais e aumento da confiabilidade.',
        DATE '2026-01-15',
        DATE '2026-12-20',
        12500000.00,
        'Orcamento de modernizacao',
        'Roberto Lima',
        1,
        'Aprovado',
        'Liberado'
    FROM upsert_project p
    CROSS JOIN artifact_ref a
    WHERE TRUE
    ON CONFLICT (project_id, revision_number) DO UPDATE SET
        status = EXCLUDED.status,
        objective = EXCLUDED.objective,
        expected_benefits = EXCLUDED.expected_benefits,
        release_status = EXCLUDED.release_status,
        updated_at = NOW()
    RETURNING id, project_id
)
INSERT INTO public.project_benefits (
    project_id,
    charter_id,
    description,
    benefit_type,
    expected_value,
    measurement_indicator,
    metadata
)
SELECT
    project_id,
    id,
    'Aumento da confiabilidade do sistema de sinalizacao.',
    'operacional',
    'Reducao de falhas percebidas',
    'Quantidade de ocorrencias operacionais',
    '{"mock": true}'::jsonb
FROM insert_charter
WHERE NOT EXISTS (
    SELECT 1 FROM public.project_benefits
    WHERE description = 'Aumento da confiabilidade do sistema de sinalizacao.'
);

INSERT INTO public.project_progress_updates (
    project_id,
    partner_source_id,
    reference_date,
    planned_physical,
    actual_physical,
    planned_economic,
    actual_economic,
    situation,
    year_label,
    metadata
)
SELECT
    id,
    'AV-MOCK-0442-202608',
    DATE '2026-08-26',
    62.50,
    57.20,
    60.00,
    54.40,
    'Atencao',
    '2026',
    '{"mock": true}'::jsonb
FROM public.projects
WHERE code = 'PRJ-0442'
ON CONFLICT (project_id, reference_date) DO UPDATE SET
    planned_physical = EXCLUDED.planned_physical,
    actual_physical = EXCLUDED.actual_physical,
    planned_economic = EXCLUDED.planned_economic,
    actual_economic = EXCLUDED.actual_economic,
    situation = EXCLUDED.situation,
    updated_at = NOW();

INSERT INTO public.project_deliverables_milestones (
    project_id,
    description,
    planned_date,
    completed_date,
    status,
    metadata
)
SELECT
    id,
    'Concluir validacao operacional do trecho piloto.',
    DATE '2026-10-15',
    NULL,
    'em_andamento',
    '{"mock": true}'::jsonb
FROM public.projects
WHERE code = 'PRJ-0442'
AND NOT EXISTS (
    SELECT 1 FROM public.project_deliverables_milestones
    WHERE description = 'Concluir validacao operacional do trecho piloto.'
);

INSERT INTO public.risk_issue_items (
    scope_type,
    project_id,
    partner_source_id,
    item,
    updated_on,
    item_type,
    criticality,
    risk_or_issue_text,
    title,
    probability,
    impact,
    severity,
    status,
    action_plan,
    planned_resolution_date,
    should_escalate,
    metadata
)
SELECT
    'projeto',
    id,
    'RISK-MOCK-0442-001',
    'Risco de atraso em equipamento',
    DATE '2026-08-26',
    'risco',
    'Alta',
    'Possivel atraso no fornecimento de equipamento critico de sinalizacao.',
    'Atraso no fornecimento de equipamentos',
    'Alta',
    'Alto',
    'Alta',
    'em_tratamento',
    'Acompanhar fornecedor e preparar plano de contingencia.',
    DATE '2026-09-30',
    TRUE,
    '{"mock": true}'::jsonb
FROM public.projects
WHERE code = 'PRJ-0442'
AND NOT EXISTS (
    SELECT 1 FROM public.risk_issue_items
    WHERE partner_source_id = 'RISK-MOCK-0442-001'
);

INSERT INTO public.intent_catalog (
    macro_intent,
    specific_intent,
    description,
    flow_description,
    target_component,
    handler_name
)
VALUES
    ('CONSULTA', 'consulta_status_projeto', 'Situacao ou andamento atual de um projeto ou programa.', 'RecuperadorInformacao -> Estruturador de Resposta', 'sharepoint_query', 'consulta_status_projeto'),
    ('CONSULTA', 'consulta_cronograma_prazo', 'Datas, prazos, previsao de termino e atrasos.', 'RecuperadorInformacao -> Estruturador de Resposta', 'sharepoint_query', 'consulta_cronograma_prazo'),
    ('CONSULTA', 'consulta_riscos_projeto', 'Riscos registrados, criticidade e planos de acao.', 'RecuperadorInformacao -> Estruturador de Resposta', 'sharepoint_query', 'consulta_riscos_projeto'),
    ('TRANSACAO', 'transacao_atualizar_cronograma', 'Repactuar datas e replanejar marcos.', 'Executor de Transacao -> Confirmacao -> Registro', 'power_automate', 'transacao_atualizar_cronograma'),
    ('FORA_DE_ESCOPO', 'fora_escopo_social', 'Saudacoes e conversa social fora do dominio do portfolio.', 'Resposta padrao de limitacao', 'out_of_scope', 'fora_escopo_social')
ON CONFLICT (macro_intent, specific_intent) DO UPDATE SET
    description = EXCLUDED.description,
    flow_description = EXCLUDED.flow_description,
    target_component = EXCLUDED.target_component,
    handler_name = EXCLUDED.handler_name,
    updated_at = NOW();

COMMIT;
