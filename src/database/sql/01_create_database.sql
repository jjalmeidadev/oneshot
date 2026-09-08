-- Modelo fisico de dados - MVP Agente de IA para Portfolio Metro
-- Banco alvo: PostgreSQL 14+
-- Baseline consolidado com o inventario de listas do parceiro de 26/08/2026.

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE public.subportfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_source_id VARCHAR(120) UNIQUE,
    code VARCHAR(30) NOT NULL UNIQUE,
    title VARCHAR(180) NOT NULL,
    responsible_name VARCHAR(160),
    gpm_member_name VARCHAR(160),
    approver_name VARCHAR(160),
    support_name VARCHAR(160),
    description TEXT,
    strategic_objective TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE public.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subportfolio_id UUID NOT NULL REFERENCES public.subportfolios(id) ON DELETE RESTRICT,
    partner_source_id VARCHAR(120) UNIQUE,
    code VARCHAR(40) NOT NULL UNIQUE,
    title VARCHAR(220) NOT NULL,
    description TEXT,
    sponsor_name VARCHAR(160),
    project_manager_name VARCHAR(160),
    current_phase VARCHAR(80),
    program_project_status VARCHAR(120),
    status VARCHAR(40) NOT NULL DEFAULT 'planejado',
    priority VARCHAR(30),
    start_date DATE,
    planned_end_date DATE,
    actual_end_date DATE,
    sharepoint_site_url TEXT,
    sharepoint_list_item_id VARCHAR(120),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT projects_status_ck CHECK (status IN ('planejado', 'em_andamento', 'atencao', 'critico', 'concluido', 'suspenso', 'descontinuado'))
);

CREATE TABLE public.subportfolio_status_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subportfolio_id UUID NOT NULL REFERENCES public.subportfolios(id) ON DELETE CASCADE,
    partner_source_id VARCHAR(120),
    item VARCHAR(220),
    reference_date DATE NOT NULL,
    situation VARCHAR(120) NOT NULL,
    year_label VARCHAR(20),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT subportfolio_status_updates_unique_ref UNIQUE (subportfolio_id, reference_date, item)
);

CREATE TABLE public.project_artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    partner_source_id VARCHAR(120),
    artifact_type VARCHAR(60) NOT NULL,
    title VARCHAR(240) NOT NULL,
    description TEXT,
    sharepoint_url TEXT,
    sharepoint_library VARCHAR(160),
    sharepoint_item_id VARCHAR(120),
    file_name VARCHAR(260),
    file_extension VARCHAR(20),
    attachment_name VARCHAR(260),
    attachment_url TEXT,
    excel_sheet_name VARCHAR(120),
    excel_table_or_range VARCHAR(120),
    source_status_label VARCHAR(120),
    source_system VARCHAR(40) NOT NULL DEFAULT 'sharepoint',
    confidentiality_level VARCHAR(40) NOT NULL DEFAULT 'interno',
    extracted_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT project_artifacts_type_ck CHECK (artifact_type IN ('tap', 'cronograma_excel', 'relatorio', 'balanco', 'fechamento', 'lista_sharepoint', 'prompt', 'normativo', 'apresentacao', 'termo_encerramento', 'outro')),
    CONSTRAINT project_artifacts_confidentiality_ck CHECK (confidentiality_level IN ('publico', 'interno', 'restrito', 'confidencial'))
);

CREATE TABLE public.source_extracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artifact_id UUID NOT NULL REFERENCES public.project_artifacts(id) ON DELETE CASCADE,
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    extract_index INTEGER NOT NULL DEFAULT 1,
    section_title VARCHAR(220),
    content_text TEXT NOT NULL,
    source_locator TEXT,
    sharepoint_reference TEXT,
    source_sheet_name VARCHAR(120),
    source_row_number INTEGER,
    source_cell_range VARCHAR(80),
    token_count INTEGER,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT source_extracts_extract_index_ck CHECK (extract_index > 0),
    CONSTRAINT source_extracts_token_count_ck CHECK (token_count IS NULL OR token_count >= 0)
);

CREATE TABLE public.schedule_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    artifact_id UUID REFERENCES public.project_artifacts(id) ON DELETE SET NULL,
    parent_item_id UUID REFERENCES public.schedule_items(id) ON DELETE SET NULL,
    wbs_code VARCHAR(80),
    activity_name VARCHAR(260) NOT NULL,
    responsible_name VARCHAR(160),
    planned_start_date DATE,
    planned_end_date DATE,
    actual_start_date DATE,
    actual_end_date DATE,
    progress_percent NUMERIC(5,2) NOT NULL DEFAULT 0,
    status VARCHAR(40) NOT NULL DEFAULT 'planejado',
    criticality VARCHAR(30),
    source_sheet_name VARCHAR(120),
    source_row_number INTEGER,
    source_cell_range VARCHAR(80),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT schedule_items_progress_ck CHECK (progress_percent >= 0 AND progress_percent <= 100),
    CONSTRAINT schedule_items_status_ck CHECK (status IN ('planejado', 'em_andamento', 'atrasado', 'concluido', 'cancelado', 'bloqueado'))
);

CREATE TABLE public.project_progress_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    partner_source_id VARCHAR(120),
    reference_date DATE NOT NULL,
    planned_physical NUMERIC(7,2),
    actual_physical NUMERIC(7,2),
    planned_economic NUMERIC(7,2),
    actual_economic NUMERIC(7,2),
    situation VARCHAR(120),
    year_label VARCHAR(20),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT project_progress_updates_values_ck CHECK (
        (planned_physical IS NULL OR planned_physical >= 0)
        AND (actual_physical IS NULL OR actual_physical >= 0)
        AND (planned_economic IS NULL OR planned_economic >= 0)
        AND (actual_economic IS NULL OR actual_economic >= 0)
    ),
    CONSTRAINT project_progress_updates_unique_ref UNIQUE (project_id, reference_date)
);

CREATE TABLE public.project_status_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    reference_date DATE NOT NULL,
    overall_status VARCHAR(40) NOT NULL,
    progress_percent NUMERIC(5,2),
    executive_summary TEXT,
    achievements TEXT,
    blockers TEXT,
    next_steps TEXT,
    reported_by VARCHAR(160),
    artifact_id UUID REFERENCES public.project_artifacts(id) ON DELETE SET NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT project_status_updates_status_ck CHECK (overall_status IN ('verde', 'amarelo', 'vermelho', 'concluido', 'suspenso')),
    CONSTRAINT project_status_updates_progress_ck CHECK (progress_percent IS NULL OR (progress_percent >= 0 AND progress_percent <= 100))
);

CREATE TABLE public.project_deliverables_milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    planned_date DATE,
    completed_date DATE,
    status VARCHAR(80),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE public.project_charters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    subportfolio_id UUID REFERENCES public.subportfolios(id) ON DELETE SET NULL,
    artifact_id UUID REFERENCES public.project_artifacts(id) ON DELETE SET NULL,
    partner_source_id VARCHAR(120),
    status VARCHAR(120),
    item VARCHAR(220),
    leader_name VARCHAR(160),
    team_text TEXT,
    objective TEXT,
    justification TEXT,
    non_scope_text TEXT,
    threat_risks TEXT,
    opportunity_risks TEXT,
    expected_benefits TEXT,
    assumptions TEXT,
    constraints_text TEXT,
    strategic_alignment TEXT,
    stakeholders TEXT,
    start_date DATE,
    end_date DATE,
    cost_brl NUMERIC(16,2),
    funding_source VARCHAR(180),
    sponsor_name VARCHAR(160),
    scope_text TEXT,
    submit_approval VARCHAR(120),
    revision_number INTEGER NOT NULL DEFAULT 1,
    revision_date DATE,
    revision_reason TEXT,
    tap_situation VARCHAR(120),
    release_status VARCHAR(120),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT project_charters_revision_ck CHECK (revision_number > 0),
    CONSTRAINT project_charters_cost_ck CHECK (cost_brl IS NULL OR cost_brl >= 0),
    CONSTRAINT project_charters_unique_revision UNIQUE (project_id, revision_number)
);

CREATE TABLE public.project_closure_terms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    artifact_id UUID REFERENCES public.project_artifacts(id) ON DELETE SET NULL,
    partner_source_id VARCHAR(120),
    closure_status VARCHAR(120),
    closure_reason TEXT,
    remaining_scope_or_pending_items TEXT,
    actual_cost_brl NUMERIC(16,2),
    closure_date DATE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT project_closure_terms_cost_ck CHECK (actual_cost_brl IS NULL OR actual_cost_brl >= 0)
);

CREATE TABLE public.project_benefits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    charter_id UUID REFERENCES public.project_charters(id) ON DELETE SET NULL,
    description TEXT NOT NULL,
    benefit_type VARCHAR(80),
    expected_value VARCHAR(120),
    measurement_indicator VARCHAR(180),
    source_artifact_id UUID REFERENCES public.project_artifacts(id) ON DELETE SET NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE public.risk_issue_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scope_type VARCHAR(20) NOT NULL,
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    subportfolio_id UUID REFERENCES public.subportfolios(id) ON DELETE CASCADE,
    partner_source_id VARCHAR(120),
    item VARCHAR(220),
    updated_on DATE,
    item_type VARCHAR(20) NOT NULL,
    criticality VARCHAR(80),
    risk_or_issue_text TEXT NOT NULL,
    title VARCHAR(240),
    description TEXT,
    probability VARCHAR(30),
    impact VARCHAR(30),
    severity VARCHAR(30),
    status VARCHAR(40) NOT NULL DEFAULT 'aberto',
    owner_name VARCHAR(160),
    action_plan TEXT,
    mitigation_plan TEXT,
    planned_resolution_date DATE,
    due_date DATE,
    should_escalate BOOLEAN,
    closed_at TIMESTAMPTZ,
    source_artifact_id UUID REFERENCES public.project_artifacts(id) ON DELETE SET NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT risk_issue_items_scope_ck CHECK (scope_type IN ('projeto', 'subportfolio')),
    CONSTRAINT risk_issue_items_scope_target_ck CHECK (
        (scope_type = 'projeto' AND project_id IS NOT NULL AND subportfolio_id IS NULL)
        OR (scope_type = 'subportfolio' AND subportfolio_id IS NOT NULL AND project_id IS NULL)
    ),
    CONSTRAINT risk_issue_items_type_ck CHECK (item_type IN ('risco', 'problema')),
    CONSTRAINT risk_issue_items_status_ck CHECK (status IN ('aberto', 'em_tratamento', 'mitigado', 'resolvido', 'aceito', 'cancelado'))
);

CREATE TABLE public.risk_issue_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_issue_id UUID NOT NULL REFERENCES public.risk_issue_items(id) ON DELETE CASCADE,
    reference_date DATE NOT NULL,
    previous_status VARCHAR(40),
    new_status VARCHAR(40),
    previous_criticality VARCHAR(80),
    new_criticality VARCHAR(80),
    comment_text TEXT,
    source_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE public.change_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scope_type VARCHAR(20) NOT NULL,
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    subportfolio_id UUID REFERENCES public.subportfolios(id) ON DELETE CASCADE,
    partner_source_id VARCHAR(120),
    applies_to_subportfolio BOOLEAN,
    change_type VARCHAR(50) NOT NULL DEFAULT 'outro',
    title VARCHAR(240) NOT NULL,
    registration_date DATE,
    approval_date DATE,
    source_label VARCHAR(180),
    reason TEXT,
    non_approval_impact TEXT,
    approval_impact TEXT,
    impact_summary TEXT,
    requested_by VARCHAR(160),
    approved_by VARCHAR(160),
    status VARCHAR(40) NOT NULL DEFAULT 'solicitada',
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decided_at TIMESTAMPTZ,
    source_artifact_id UUID REFERENCES public.project_artifacts(id) ON DELETE SET NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT change_records_scope_ck CHECK (scope_type IN ('projeto', 'subportfolio')),
    CONSTRAINT change_records_scope_target_ck CHECK (
        (scope_type = 'projeto' AND project_id IS NOT NULL AND subportfolio_id IS NULL)
        OR (scope_type = 'subportfolio' AND subportfolio_id IS NOT NULL AND project_id IS NULL)
    ),
    CONSTRAINT change_records_type_ck CHECK (change_type IN ('prazo', 'escopo', 'custo', 'prioridade', 'responsavel', 'outro')),
    CONSTRAINT change_records_status_ck CHECK (status IN ('solicitada', 'em_analise', 'aprovada', 'rejeitada', 'implementada', 'cancelada'))
);

CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entra_object_id VARCHAR(120) UNIQUE,
    display_name VARCHAR(180) NOT NULL,
    email VARCHAR(220) NOT NULL UNIQUE,
    role_name VARCHAR(80) NOT NULL,
    department VARCHAR(120),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT users_role_ck CHECK (role_name IN ('diretoria', 'pmo', 'lider_subportfolio', 'equipe_projeto', 'gti', 'admin'))
);

CREATE TABLE public.access_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    role_name VARCHAR(80),
    subportfolio_id UUID REFERENCES public.subportfolios(id) ON DELETE CASCADE,
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    permission_scope VARCHAR(40) NOT NULL,
    can_read BOOLEAN NOT NULL DEFAULT TRUE,
    can_write BOOLEAN NOT NULL DEFAULT FALSE,
    can_export BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT access_rules_scope_ck CHECK (permission_scope IN ('portfolio', 'subportfolio', 'projeto', 'artefato', 'auditoria')),
    CONSTRAINT access_rules_subject_ck CHECK (user_id IS NOT NULL OR role_name IS NOT NULL)
);

CREATE TABLE public.intent_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    macro_intent VARCHAR(40) NOT NULL,
    specific_intent VARCHAR(120) NOT NULL,
    description TEXT NOT NULL,
    flow_description TEXT,
    target_component VARCHAR(60) NOT NULL,
    handler_name VARCHAR(120) NOT NULL,
    required_entities JSONB NOT NULL DEFAULT '[]'::jsonb,
    macro_confidence_threshold NUMERIC(5,4) NOT NULL DEFAULT 0.5500,
    intent_confidence_threshold NUMERIC(5,4) NOT NULL DEFAULT 0.7000,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT intent_catalog_unique_intent UNIQUE (macro_intent, specific_intent),
    CONSTRAINT intent_catalog_macro_ck CHECK (macro_intent IN ('CONSULTA', 'TRANSACAO', 'ALERTA', 'FORA_DE_ESCOPO')),
    CONSTRAINT intent_catalog_target_ck CHECK (target_component IN ('copilot_topic', 'power_automate', 'sharepoint_query', 'local_analysis', 'generic_macro_flow', 'out_of_scope')),
    CONSTRAINT intent_catalog_thresholds_ck CHECK (
        macro_confidence_threshold >= 0 AND macro_confidence_threshold <= 1
        AND intent_confidence_threshold >= 0 AND intent_confidence_threshold <= 1
    )
);

CREATE TABLE public.prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intent_id UUID REFERENCES public.intent_catalog(id) ON DELETE SET NULL,
    template_key VARCHAR(120) NOT NULL UNIQUE,
    title VARCHAR(180) NOT NULL,
    prompt_text TEXT NOT NULL,
    channel VARCHAR(40) NOT NULL DEFAULT 'copilot_studio',
    purpose VARCHAR(80) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT prompt_templates_channel_ck CHECK (channel IN ('copilot_studio', 'm365_copilot', 'power_automate', 'pln_local')),
    CONSTRAINT prompt_templates_purpose_ck CHECK (purpose IN ('resposta', 'geracao_documental', 'classificacao', 'alerta', 'transacao', 'avaliacao'))
);

CREATE TABLE public.ai_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    channel VARCHAR(40) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    conversation_status VARCHAR(40) NOT NULL DEFAULT 'ativa',
    external_conversation_id VARCHAR(160),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ai_conversations_channel_ck CHECK (channel IN ('teams', 'webchat', 'copilot_studio', 'api', 'teste')),
    CONSTRAINT ai_conversations_status_ck CHECK (conversation_status IN ('ativa', 'finalizada', 'abandonada', 'erro'))
);

CREATE TABLE public.ai_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES public.ai_conversations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    intent_id UUID REFERENCES public.intent_catalog(id) ON DELETE SET NULL,
    prompt_template_id UUID REFERENCES public.prompt_templates(id) ON DELETE SET NULL,
    user_prompt TEXT NOT NULL,
    normalized_prompt TEXT,
    macro_intent_predicted VARCHAR(40),
    macro_intent_confidence NUMERIC(6,5),
    specific_intent_predicted VARCHAR(120),
    specific_intent_confidence NUMERIC(6,5),
    handler_selected VARCHAR(120),
    route_taken VARCHAR(60) NOT NULL,
    top_k_alternatives JSONB NOT NULL DEFAULT '[]'::jsonb,
    response_text TEXT,
    limitation_response TEXT,
    processing_status VARCHAR(40) NOT NULL DEFAULT 'processado',
    processing_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ai_interactions_macro_ck CHECK (macro_intent_predicted IS NULL OR macro_intent_predicted IN ('CONSULTA', 'TRANSACAO', 'ALERTA', 'FORA_DE_ESCOPO')),
    CONSTRAINT ai_interactions_route_ck CHECK (route_taken IN ('copilot_topic', 'power_automate', 'sharepoint_query', 'analise_local', 'fora_escopo')),
    CONSTRAINT ai_interactions_status_ck CHECK (processing_status IN ('processado', 'sem_confianca', 'fora_escopo', 'erro', 'pendente')),
    CONSTRAINT ai_interactions_confidence_ck CHECK (
        (macro_intent_confidence IS NULL OR (macro_intent_confidence >= 0 AND macro_intent_confidence <= 1))
        AND (specific_intent_confidence IS NULL OR (specific_intent_confidence >= 0 AND specific_intent_confidence <= 1))
    )
);

CREATE TABLE public.consulted_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interaction_id UUID NOT NULL REFERENCES public.ai_interactions(id) ON DELETE CASCADE,
    artifact_id UUID REFERENCES public.project_artifacts(id) ON DELETE SET NULL,
    extract_id UUID REFERENCES public.source_extracts(id) ON DELETE SET NULL,
    project_id UUID REFERENCES public.projects(id) ON DELETE SET NULL,
    source_type VARCHAR(60) NOT NULL,
    source_title VARCHAR(240),
    source_url TEXT,
    source_locator TEXT,
    relevance_score NUMERIC(6,5),
    citation_order INTEGER NOT NULL DEFAULT 1,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT consulted_sources_type_ck CHECK (source_type IN ('documento', 'planilha_excel', 'lista_sharepoint', 'linha_planilha', 'extrato', 'normativo', 'prompt')),
    CONSTRAINT consulted_sources_order_ck CHECK (citation_order > 0),
    CONSTRAINT consulted_sources_score_ck CHECK (relevance_score IS NULL OR (relevance_score >= 0 AND relevance_score <= 1))
);

CREATE TABLE public.audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interaction_id UUID REFERENCES public.ai_interactions(id) ON DELETE SET NULL,
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    event_type VARCHAR(80) NOT NULL,
    component VARCHAR(60) NOT NULL,
    event_status VARCHAR(40) NOT NULL DEFAULT 'sucesso',
    event_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    correlation_id VARCHAR(120),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT audit_events_component_ck CHECK (component IN ('api', 'pln', 'copilot_studio', 'power_automate', 'm365_copilot', 'sharepoint', 'database')),
    CONSTRAINT audit_events_status_ck CHECK (event_status IN ('sucesso', 'falha', 'bloqueado', 'pendente'))
);

CREATE TABLE public.out_of_scope_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interaction_id UUID NOT NULL REFERENCES public.ai_interactions(id) ON DELETE CASCADE,
    user_prompt TEXT NOT NULL,
    predicted_macro_intent VARCHAR(40),
    predicted_specific_intent VARCHAR(120),
    confidence NUMERIC(6,5),
    reason TEXT,
    review_status VARCHAR(40) NOT NULL DEFAULT 'pendente',
    reviewed_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT out_of_scope_review_status_ck CHECK (review_status IN ('pendente', 'revisado', 'incorporar_catalogo', 'descartado')),
    CONSTRAINT out_of_scope_confidence_ck CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1))
);

CREATE TABLE public.intent_test_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intent_id UUID NOT NULL REFERENCES public.intent_catalog(id) ON DELETE CASCADE,
    template_id VARCHAR(120) NOT NULL,
    raw_text TEXT NOT NULL,
    normalized_text TEXT,
    surface_variation VARCHAR(120),
    dataset_split VARCHAR(20) NOT NULL,
    leakage_group VARCHAR(120),
    expected_macro_intent VARCHAR(40) NOT NULL,
    expected_specific_intent VARCHAR(120) NOT NULL,
    expected_handler VARCHAR(120),
    source_notebook VARCHAR(260) NOT NULL DEFAULT 'src/notebooks/classificador_intencoes_metro.ipynb',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT intent_test_cases_split_ck CHECK (dataset_split IN ('treino', 'validacao', 'teste')),
    CONSTRAINT intent_test_cases_macro_ck CHECK (expected_macro_intent IN ('CONSULTA', 'TRANSACAO', 'ALERTA', 'FORA_DE_ESCOPO'))
);

CREATE INDEX idx_projects_subportfolio_id ON public.projects(subportfolio_id);
CREATE INDEX idx_projects_status ON public.projects(status);
CREATE INDEX idx_subportfolio_status_updates_ref ON public.subportfolio_status_updates(subportfolio_id, reference_date DESC);
CREATE INDEX idx_project_artifacts_project_id ON public.project_artifacts(project_id);
CREATE INDEX idx_project_artifacts_type ON public.project_artifacts(artifact_type);
CREATE INDEX idx_source_extracts_artifact_id ON public.source_extracts(artifact_id);
CREATE INDEX idx_source_extracts_project_id ON public.source_extracts(project_id);
CREATE INDEX idx_schedule_items_project_id ON public.schedule_items(project_id);
CREATE INDEX idx_schedule_items_artifact_id ON public.schedule_items(artifact_id);
CREATE INDEX idx_schedule_items_dates ON public.schedule_items(planned_start_date, planned_end_date);
CREATE INDEX idx_project_progress_updates_project_date ON public.project_progress_updates(project_id, reference_date DESC);
CREATE INDEX idx_project_status_updates_project_date ON public.project_status_updates(project_id, reference_date DESC);
CREATE INDEX idx_project_deliverables_project_status ON public.project_deliverables_milestones(project_id, status);
CREATE INDEX idx_project_charters_project_revision ON public.project_charters(project_id, revision_number DESC);
CREATE INDEX idx_project_closure_terms_project_date ON public.project_closure_terms(project_id, closure_date DESC);
CREATE INDEX idx_project_benefits_project_id ON public.project_benefits(project_id);
CREATE INDEX idx_risk_issue_items_project_status ON public.risk_issue_items(project_id, status) WHERE scope_type = 'projeto';
CREATE INDEX idx_risk_issue_items_subportfolio_status ON public.risk_issue_items(subportfolio_id, status) WHERE scope_type = 'subportfolio';
CREATE INDEX idx_risk_issue_history_item_date ON public.risk_issue_history(risk_issue_id, reference_date DESC);
CREATE INDEX idx_change_records_project_status ON public.change_records(project_id, status) WHERE scope_type = 'projeto';
CREATE INDEX idx_change_records_subportfolio_status ON public.change_records(subportfolio_id, status) WHERE scope_type = 'subportfolio';
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_access_rules_user_id ON public.access_rules(user_id);
CREATE INDEX idx_access_rules_role_name ON public.access_rules(role_name);
CREATE INDEX idx_intent_catalog_macro ON public.intent_catalog(macro_intent);
CREATE INDEX idx_prompt_templates_intent_id ON public.prompt_templates(intent_id);
CREATE INDEX idx_ai_conversations_user_id ON public.ai_conversations(user_id);
CREATE INDEX idx_ai_interactions_conversation_id ON public.ai_interactions(conversation_id);
CREATE INDEX idx_ai_interactions_intent_id ON public.ai_interactions(intent_id);
CREATE INDEX idx_ai_interactions_created_at ON public.ai_interactions(created_at DESC);
CREATE INDEX idx_consulted_sources_interaction_id ON public.consulted_sources(interaction_id);
CREATE INDEX idx_consulted_sources_artifact_id ON public.consulted_sources(artifact_id);
CREATE INDEX idx_audit_events_interaction_id ON public.audit_events(interaction_id);
CREATE INDEX idx_audit_events_occurred_at ON public.audit_events(occurred_at DESC);
CREATE INDEX idx_out_of_scope_requests_review_status ON public.out_of_scope_requests(review_status);
CREATE INDEX idx_intent_test_cases_intent_split ON public.intent_test_cases(intent_id, dataset_split);

CREATE UNIQUE INDEX uq_subportfolio_status_partner_source ON public.subportfolio_status_updates(partner_source_id) WHERE partner_source_id IS NOT NULL;
CREATE UNIQUE INDEX uq_project_artifacts_partner_source ON public.project_artifacts(partner_source_id) WHERE partner_source_id IS NOT NULL;
CREATE UNIQUE INDEX uq_project_progress_partner_source ON public.project_progress_updates(partner_source_id) WHERE partner_source_id IS NOT NULL;
CREATE UNIQUE INDEX uq_project_charters_partner_source ON public.project_charters(partner_source_id) WHERE partner_source_id IS NOT NULL;
CREATE UNIQUE INDEX uq_project_closure_partner_source ON public.project_closure_terms(partner_source_id) WHERE partner_source_id IS NOT NULL;
CREATE UNIQUE INDEX uq_risk_issue_items_partner_source ON public.risk_issue_items(partner_source_id) WHERE partner_source_id IS NOT NULL;
CREATE UNIQUE INDEX uq_change_records_partner_source ON public.change_records(partner_source_id) WHERE partner_source_id IS NOT NULL;

CREATE TRIGGER trg_subportfolios_updated_at BEFORE UPDATE ON public.subportfolios FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_projects_updated_at BEFORE UPDATE ON public.projects FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_subportfolio_status_updates_updated_at BEFORE UPDATE ON public.subportfolio_status_updates FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_project_artifacts_updated_at BEFORE UPDATE ON public.project_artifacts FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_source_extracts_updated_at BEFORE UPDATE ON public.source_extracts FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_schedule_items_updated_at BEFORE UPDATE ON public.schedule_items FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_project_progress_updates_updated_at BEFORE UPDATE ON public.project_progress_updates FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_project_status_updates_updated_at BEFORE UPDATE ON public.project_status_updates FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_project_deliverables_milestones_updated_at BEFORE UPDATE ON public.project_deliverables_milestones FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_project_charters_updated_at BEFORE UPDATE ON public.project_charters FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_project_closure_terms_updated_at BEFORE UPDATE ON public.project_closure_terms FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_project_benefits_updated_at BEFORE UPDATE ON public.project_benefits FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_risk_issue_items_updated_at BEFORE UPDATE ON public.risk_issue_items FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_risk_issue_history_updated_at BEFORE UPDATE ON public.risk_issue_history FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_change_records_updated_at BEFORE UPDATE ON public.change_records FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_access_rules_updated_at BEFORE UPDATE ON public.access_rules FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_intent_catalog_updated_at BEFORE UPDATE ON public.intent_catalog FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_prompt_templates_updated_at BEFORE UPDATE ON public.prompt_templates FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_ai_conversations_updated_at BEFORE UPDATE ON public.ai_conversations FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_ai_interactions_updated_at BEFORE UPDATE ON public.ai_interactions FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_consulted_sources_updated_at BEFORE UPDATE ON public.consulted_sources FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_audit_events_updated_at BEFORE UPDATE ON public.audit_events FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_out_of_scope_requests_updated_at BEFORE UPDATE ON public.out_of_scope_requests FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE TRIGGER trg_intent_test_cases_updated_at BEFORE UPDATE ON public.intent_test_cases FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

COMMENT ON TABLE public.subportfolios IS 'Subportfolios estrategicos do portfolio, alinhados a lista Subportfolio do parceiro.';
COMMENT ON TABLE public.projects IS 'Projetos acompanhados pelo PMO, vinculados a subportfolio e fontes do SharePoint.';
COMMENT ON TABLE public.subportfolio_status_updates IS 'Situacoes historicas de subportfolio por data de referencia.';
COMMENT ON TABLE public.project_artifacts IS 'Artefatos do projeto, incluindo documentos, anexos, listas, prompts, normativos e planilhas vinculadas no SharePoint.';
COMMENT ON TABLE public.source_extracts IS 'Extratos consultaveis derivados de documentos, listas ou planilhas para composicao de contexto e rastreabilidade.';
COMMENT ON TABLE public.schedule_items IS 'Linhas estruturadas de cronograma, inclusive extraidas de planilhas Excel vinculadas no SharePoint.';
COMMENT ON TABLE public.project_progress_updates IS 'Medicoes historicas de avanco fisico e economico por projeto.';
COMMENT ON TABLE public.project_status_updates IS 'Atualizacoes narrativas de avanco, situacao e resumo executivo dos projetos.';
COMMENT ON TABLE public.project_deliverables_milestones IS 'Entregas e marcos dos projetos com datas previstas, realizadas e status.';
COMMENT ON TABLE public.project_charters IS 'Termos de abertura de projeto estruturados a partir da lista TAP do parceiro.';
COMMENT ON TABLE public.project_closure_terms IS 'Termos de encerramento de projeto com justificativa, pendencias e custo realizado.';
COMMENT ON TABLE public.project_benefits IS 'Beneficios esperados ou detalhados associados ao projeto e ao TAP.';
COMMENT ON TABLE public.risk_issue_items IS 'Riscos e problemas de projeto ou subportfolio, com escopo exclusivo controlado por constraint.';
COMMENT ON TABLE public.risk_issue_history IS 'Historico de mudancas de status e criticidade de riscos e problemas.';
COMMENT ON TABLE public.change_records IS 'Registros de mudancas de projeto ou subportfolio, com impactos e status de aprovacao.';
COMMENT ON TABLE public.users IS 'Usuarios simulados ou autenticados via Microsoft Entra ID em evolucao futura.';
COMMENT ON TABLE public.access_rules IS 'Regras de acesso por usuario, perfil, projeto, subportfolio ou escopo de permissao.';
COMMENT ON TABLE public.intent_catalog IS 'Catalogo hierarquico de macrointencoes, intencoes especificas, handlers e limiares do classificador.';
COMMENT ON TABLE public.prompt_templates IS 'Templates de prompts usados por Copilot Studio, Microsoft 365 Copilot, Power Automate ou PLN local.';
COMMENT ON TABLE public.ai_conversations IS 'Sessoes conversacionais agrupando interacoes de um usuario em um canal.';
COMMENT ON TABLE public.ai_interactions IS 'Interacoes processadas pelo agente, incluindo prompt, classificacao, rota, resposta e status.';
COMMENT ON TABLE public.consulted_sources IS 'Fontes consultadas para compor uma resposta, com vinculo a interacao, artefato, extrato e projeto.';
COMMENT ON TABLE public.audit_events IS 'Eventos de auditoria tecnica e funcional gerados durante o processamento.';
COMMENT ON TABLE public.out_of_scope_requests IS 'Solicitacoes fora do escopo suportado, registradas para revisao e evolucao do catalogo.';
COMMENT ON TABLE public.intent_test_cases IS 'Casos de teste rotulados para avaliacao do classificador de intencoes.';

COMMIT;
