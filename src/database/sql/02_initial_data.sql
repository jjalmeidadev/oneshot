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
    ('CONSULTA', 'consulta_marcos_entregas', 'Marcos, entregas e etapas planejadas ou concluidas.', 'RecuperadorInformacao -> Estruturador de Resposta', 'sharepoint_query', 'consulta_marcos_entregas'),
    ('CONSULTA', 'consulta_orcamento_custo', 'Orcamento aprovado, custo realizado, saldo e desvio financeiro.', 'RecuperadorInformacao -> Estruturador de Resposta', 'sharepoint_query', 'consulta_orcamento_custo'),
    ('CONSULTA', 'consulta_escopo_tap', 'Escopo, objetivos, premissas e restricoes registrados no TAP.', 'RecuperadorInformacao -> Estruturador de Resposta', 'sharepoint_query', 'consulta_escopo_tap'),
    ('CONSULTA', 'consulta_responsavel_equipe', 'Gerente responsavel, equipe, area ou patrocinador do projeto.', 'RecuperadorInformacao -> Estruturador de Resposta', 'sharepoint_query', 'consulta_responsavel_equipe'),
    ('CONSULTA', 'consulta_indicadores_kpi', 'Indicadores de desempenho, avanco e aderencia.', 'RecuperadorInformacao -> Estruturador de Resposta', 'sharepoint_query', 'consulta_indicadores_kpi'),
    ('CONSULTA', 'consulta_riscos_projeto', 'Riscos registrados, criticidade e planos de acao.', 'RecuperadorInformacao -> Estruturador de Resposta', 'sharepoint_query', 'consulta_riscos_projeto'),
    ('CONSULTA', 'consulta_pendencias_projeto', 'Pendencias, acoes em aberto e itens aguardando resposta.', 'RecuperadorInformacao -> Estruturador de Resposta', 'sharepoint_query', 'consulta_pendencias_projeto'),
    ('CONSULTA', 'consulta_documentos_fonte', 'Localizacao e origem de documentos e referencias.', 'RecuperadorInformacao -> Estruturador de Resposta', 'sharepoint_query', 'consulta_documentos_fonte'),
    ('CONSULTA', 'consulta_visao_portfolio', 'Visao agregada do portfolio ou de um subportfolio.', 'RecuperadorInformacao -> Estruturador de Resposta', 'sharepoint_query', 'consulta_visao_portfolio'),
    ('CONSULTA', 'comparacao_entre_projetos', 'Comparacao explicita entre dois ou mais projetos.', 'RecuperadorInformacao -> Estruturador de Resposta', 'local_analysis', 'comparacao_entre_projetos'),
    ('CONSULTA', 'analise_tendencia_desempenho', 'Evolucao temporal, tendencia, projecao e causas de variacao.', 'RecuperadorInformacao -> Estruturador de Resposta', 'local_analysis', 'analise_tendencia_desempenho'),
    ('TRANSACAO', 'transacao_atualizar_cronograma', 'Repactuar datas e replanejar marcos.', 'Executor de Transacao -> Confirmacao -> Registro', 'power_automate', 'transacao_atualizar_cronograma'),
    ('FORA_DE_ESCOPO', 'fora_escopo_social', 'Saudacoes e conversa social fora do dominio do portfolio.', 'Resposta padrao de limitacao', 'out_of_scope', 'fora_escopo_social')
ON CONFLICT (macro_intent, specific_intent) DO UPDATE SET
    description = EXCLUDED.description,
    flow_description = EXCLUDED.flow_description,
    target_component = EXCLUDED.target_component,
    handler_name = EXCLUDED.handler_name,
    updated_at = NOW();

WITH secondary_seed (
    specific_intent,
    secondary_intent,
    description,
    rag_instruction,
    display_message
) AS (
    VALUES
        (
            'consulta_status_projeto',
            'sugerir_agilizacao_projeto',
            'Identificar o principal gargalo documentado e sugerir uma acao para acelerar o projeto.',
            'Depois da resposta principal, identifique nas fontes o principal gargalo do projeto e sugira uma unica acao objetiva para agiliza-lo. Cite a evidencia e nao invente recomendacao quando faltar suporte.',
            'Quer que eu identifique o principal gargalo documentado e sugira uma forma de agilizar o projeto?'
        ),
        (
            'consulta_cronograma_prazo',
            'sugerir_recuperacao_prazo',
            'Apontar a atividade mais critica ou atrasada e sugerir uma acao de recuperacao do cronograma.',
            'Depois da resposta principal, identifique nas fontes a atividade mais critica ou atrasada e sugira uma unica acao de recuperacao do prazo. Cite a evidencia e preserve datas e responsaveis documentados.',
            'Quer que eu avalie o ponto mais critico do cronograma e sugira uma acao de recuperacao?'
        ),
        (
            'consulta_marcos_entregas',
            'sugerir_antecipacao_marco',
            'Identificar o proximo marco critico e sugerir uma preparacao que reduza o risco de atraso.',
            'Depois da resposta principal, identifique nas fontes o proximo marco critico e sugira uma preparacao objetiva para reduzir o risco de atraso. Cite a evidencia documental.',
            'Quer que eu identifique como preparar o proximo marco critico e reduzir o risco de atraso?'
        ),
        (
            'consulta_orcamento_custo',
            'sugerir_otimizacao_custo',
            'Destacar o maior desvio financeiro documentado e sugerir uma oportunidade de contencao ou otimizacao.',
            'Depois da resposta principal, identifique nas fontes o maior desvio financeiro documentado e sugira uma unica oportunidade de contencao ou otimizacao. Nao estime valores ausentes.',
            'Quer que eu analise o maior desvio documentado e sugira uma oportunidade de otimizacao de custo?'
        ),
        (
            'consulta_escopo_tap',
            'sugerir_clareza_escopo',
            'Identificar restricao, dependencia ou ambiguidade de escopo e sugerir como esclarece-la.',
            'Depois da resposta principal, identifique nas fontes uma restricao, dependencia ou ambiguidade de escopo e sugira uma forma objetiva de esclarece-la, sem propor alteracao de escopo como fato consumado.',
            'Quer que eu identifique uma restricao ou ambiguidade de escopo que mereca esclarecimento?'
        ),
        (
            'consulta_responsavel_equipe',
            'sugerir_coordenacao_equipe',
            'Sugerir o responsavel ou grupo que deve participar do proximo alinhamento.',
            'Depois da resposta principal, use apenas papeis e responsaveis presentes nas fontes para sugerir quem deve participar do proximo alinhamento e por que. Nao atribua responsabilidade inexistente.',
            'Quer que eu sugira quem deve participar do proximo alinhamento do projeto?'
        ),
        (
            'consulta_indicadores_kpi',
            'sugerir_melhoria_indicador',
            'Identificar o indicador mais desfavoravel e sugerir uma acao para melhora-lo.',
            'Depois da resposta principal, identifique nas fontes o indicador mais desfavoravel e sugira uma unica acao coerente para melhora-lo. Preserve valores e periodos documentados.',
            'Quer que eu identifique o indicador mais desfavoravel e sugira uma acao de melhoria?'
        ),
        (
            'consulta_riscos_projeto',
            'sugerir_mitigacao_risco',
            'Priorizar o risco aberto de maior exposicao e sugerir uma medida de mitigacao.',
            'Depois da resposta principal, priorize nas fontes o risco aberto de maior exposicao e sugira uma unica medida de mitigacao. Cite criticidade, impacto ou plano existente quando disponivel.',
            'Quer que eu priorize o risco mais relevante e sugira uma medida de mitigacao?'
        ),
        (
            'consulta_pendencias_projeto',
            'sugerir_resolucao_pendencia',
            'Priorizar a pendencia com maior impacto ou poder de bloqueio e sugerir o proximo passo.',
            'Depois da resposta principal, identifique nas fontes a pendencia com maior impacto ou poder de bloqueio e sugira um unico proximo passo. Respeite responsaveis e prazos documentados.',
            'Quer que eu priorize a pendencia mais bloqueadora e sugira o proximo passo?'
        ),
        (
            'consulta_documentos_fonte',
            'sugerir_regularizacao_documental',
            'Identificar documentos ausentes, desatualizados ou inconsistentes e sugerir qual revisar primeiro.',
            'Depois da resposta principal, identifique nas fontes um documento ausente, desatualizado ou inconsistente e sugira qual deve ser validado primeiro. Nao declare ausencia sem evidencia.',
            'Quer que eu verifique qual documento deve ser validado ou atualizado primeiro?'
        ),
        (
            'consulta_visao_portfolio',
            'sugerir_priorizacao_portfolio',
            'Identificar os projetos que mais precisam de intervencao e explicar o criterio de priorizacao.',
            'Depois da resposta principal, identifique nas fontes o projeto que mais precisa de intervencao e sugira uma prioridade objetiva, explicando o criterio usado sem criar dados comparativos.',
            'Quer que eu identifique qual projeto mais precisa de intervencao e explique o criterio?'
        ),
        (
            'comparacao_entre_projetos',
            'sugerir_pratica_replicavel',
            'Encontrar uma pratica associada ao melhor desempenho e sugerir sua adaptacao ao outro projeto.',
            'Depois da resposta principal, identifique nas fontes uma pratica associada ao projeto de melhor desempenho e sugira como adapta-la ao outro projeto. Diferencie evidencia de interpretacao.',
            'Quer que eu identifique uma pratica do projeto com melhor desempenho que possa ser adaptada?'
        ),
        (
            'analise_tendencia_desempenho',
            'sugerir_correcao_tendencia',
            'Identificar a tendencia desfavoravel mais relevante e sugerir uma acao corretiva antecipada.',
            'Depois da resposta principal, identifique nas fontes a tendencia desfavoravel mais relevante e sugira uma unica acao corretiva antecipada. Declare quando o historico for insuficiente.',
            'Quer que eu identifique a tendencia mais preocupante e sugira uma acao corretiva?'
        )
)
INSERT INTO public.secondary_intents (
    specific_intent_id,
    secondary_intent,
    description,
    rag_instruction,
    display_message
)
SELECT
    catalog.id,
    secondary_seed.secondary_intent,
    secondary_seed.description,
    secondary_seed.rag_instruction,
    secondary_seed.display_message
FROM secondary_seed
JOIN public.intent_catalog catalog
    ON catalog.macro_intent = 'CONSULTA'
    AND catalog.specific_intent = secondary_seed.specific_intent
ON CONFLICT (specific_intent_id, secondary_intent) DO UPDATE SET
    description = EXCLUDED.description,
    rag_instruction = EXCLUDED.rag_instruction,
    display_message = EXCLUDED.display_message,
    is_active = TRUE,
    updated_at = NOW();

COMMIT;
