-- Migracao versionada da issue #250.
-- Adiciona intencoes secundarias proativas sem alterar o contrato das
-- macrointencoes e intencoes especificas existentes.

BEGIN;

CREATE TABLE IF NOT EXISTS public.secondary_intents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    specific_intent_id UUID NOT NULL REFERENCES public.intent_catalog(id) ON DELETE CASCADE,
    secondary_intent VARCHAR(120) NOT NULL,
    description TEXT NOT NULL,
    rag_instruction TEXT NOT NULL,
    display_message TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT secondary_intents_unique_association UNIQUE (specific_intent_id, secondary_intent),
    CONSTRAINT secondary_intents_name_ck CHECK (secondary_intent ~ '^[a-z][a-z0-9_]*$')
);

CREATE INDEX IF NOT EXISTS idx_secondary_intents_specific_intent_id
    ON public.secondary_intents(specific_intent_id);

DROP TRIGGER IF EXISTS trg_secondary_intents_updated_at ON public.secondary_intents;
CREATE TRIGGER trg_secondary_intents_updated_at
    BEFORE UPDATE ON public.secondary_intents
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at();

COMMENT ON TABLE public.secondary_intents IS
    'Sugestoes proativas vinculadas a intencoes especificas e enviadas ao RAG como proximo passo opcional.';

-- A migracao precisa deixar bancos existentes prontos para uso sem depender
-- da reexecucao do bootstrap 02_initial_data.sql.
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
