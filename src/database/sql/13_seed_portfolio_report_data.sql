-- 13_seed_portfolio_report_data.sql
-- Popula as tabelas de portfolio com massa sintetica realista, em portugues,
-- para que os relatorios executivos leiam dados do banco (REPORT_PORTFOLIO_SOURCE=database).
-- Idempotente: usa o subportfolio existente "MOD" e projetos por code, com ON CONFLICT
-- e limpeza previa dos dados de portfolio dos projetos afetados.

BEGIN;

-- ---------------------------------------------------------------------------
-- Subportfolio base
-- ---------------------------------------------------------------------------
UPDATE public.subportfolios
SET title = 'Modernizacao da Rede Metroviaria',
    strategic_objective = 'Elevar a confiabilidade, a capacidade e a qualidade percebida da operacao metroviaria.',
    responsible_name = COALESCE(responsible_name, 'Gerencia de Portfolio'),
    updated_at = now()
WHERE code = 'MOD';

-- ---------------------------------------------------------------------------
-- Projetos (PRJ-0442 ja existe; adiciona PRJ-0510 e PRJ-0587 no mesmo subportfolio)
-- ---------------------------------------------------------------------------
UPDATE public.projects
SET title = 'Modernizacao do Sistema de Sinalizacao da Linha Azul',
    project_manager_name = 'Carlos Almeida',
    current_phase = 'execucao',
    status = 'em_andamento',
    updated_at = now()
WHERE code = 'PRJ-0442';

INSERT INTO public.projects (subportfolio_id, code, title, project_manager_name, current_phase, status, start_date, planned_end_date)
SELECT sp.id, 'PRJ-0510', 'Renovacao do Centro de Controle Operacional',
       'Marina Costa', 'execucao', 'em_andamento', DATE '2026-02-10', DATE '2027-04-30'
FROM public.subportfolios sp WHERE sp.code = 'MOD'
ON CONFLICT (code) DO UPDATE SET
    title = EXCLUDED.title, project_manager_name = EXCLUDED.project_manager_name,
    current_phase = EXCLUDED.current_phase, status = EXCLUDED.status, updated_at = now();

INSERT INTO public.projects (subportfolio_id, code, title, project_manager_name, current_phase, status, start_date, planned_end_date)
SELECT sp.id, 'PRJ-0587', 'Adequacao de Acessibilidade das Estacoes',
       'Rafael Nunes', 'planejamento', 'em_andamento', DATE '2026-05-05', DATE '2027-09-15'
FROM public.subportfolios sp WHERE sp.code = 'MOD'
ON CONFLICT (code) DO UPDATE SET
    title = EXCLUDED.title, project_manager_name = EXCLUDED.project_manager_name,
    current_phase = EXCLUDED.current_phase, status = EXCLUDED.status, updated_at = now();

-- ---------------------------------------------------------------------------
-- Limpeza previa para reaplicacao idempotente
-- ---------------------------------------------------------------------------
DELETE FROM public.project_progress_updates WHERE project_id IN (SELECT id FROM public.projects WHERE code IN ('PRJ-0442','PRJ-0510','PRJ-0587'));
DELETE FROM public.project_status_updates   WHERE project_id IN (SELECT id FROM public.projects WHERE code IN ('PRJ-0442','PRJ-0510','PRJ-0587'));
DELETE FROM public.project_deliverables_milestones WHERE project_id IN (SELECT id FROM public.projects WHERE code IN ('PRJ-0442','PRJ-0510','PRJ-0587'));
DELETE FROM public.project_benefits        WHERE project_id IN (SELECT id FROM public.projects WHERE code IN ('PRJ-0442','PRJ-0510','PRJ-0587'));
DELETE FROM public.change_records          WHERE project_id IN (SELECT id FROM public.projects WHERE code IN ('PRJ-0442','PRJ-0510','PRJ-0587'));
DELETE FROM public.risk_issue_items        WHERE project_id IN (SELECT id FROM public.projects WHERE code IN ('PRJ-0442','PRJ-0510','PRJ-0587'));
DELETE FROM public.schedule_items          WHERE project_id IN (SELECT id FROM public.projects WHERE code IN ('PRJ-0442','PRJ-0510','PRJ-0587'));

-- ---------------------------------------------------------------------------
-- Avanco fisico (historico mensal; o ultimo registro alimenta o relatorio)
-- ---------------------------------------------------------------------------
INSERT INTO public.project_progress_updates (project_id, reference_date, planned_physical, actual_physical, situation)
SELECT id, DATE '2026-06-30', 48.0, 46.0, 'em_dia'   FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT id, DATE '2026-07-31', 60.0, 57.0, 'em_dia'   FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT id, DATE '2026-08-31', 68.0, 64.5, 'atencao'  FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT id, DATE '2026-06-30', 30.0, 31.0, 'em_dia'   FROM public.projects WHERE code = 'PRJ-0510'
UNION ALL SELECT id, DATE '2026-07-31', 36.0, 37.5, 'em_dia'   FROM public.projects WHERE code = 'PRJ-0510'
UNION ALL SELECT id, DATE '2026-08-31', 42.0, 43.2, 'em_dia'   FROM public.projects WHERE code = 'PRJ-0510'
UNION ALL SELECT id, DATE '2026-07-31', 18.0, 15.0, 'atencao'  FROM public.projects WHERE code = 'PRJ-0587'
UNION ALL SELECT id, DATE '2026-08-31', 25.0, 22.0, 'atencao'  FROM public.projects WHERE code = 'PRJ-0587';

-- ---------------------------------------------------------------------------
-- Atualizacoes de status (conquistas e proximos passos)
-- ---------------------------------------------------------------------------
INSERT INTO public.project_status_updates (project_id, reference_date, overall_status, progress_percent, executive_summary, achievements, blockers, next_steps, reported_by)
SELECT id, DATE '2026-08-31', 'amarelo', 64.5,
       'Projeto avanca em ritmo adequado, com atencao a janela de instalacao noturna e a integracao com o centro de controle.',
       'Conclusao dos testes de bancada e liberacao do primeiro lote de equipamentos para instalacao em campo.',
       'Disponibilidade limitada de janelas operacionais para intervencao na via.',
       'Concluir a instalacao do primeiro lote e iniciar a operacao assistida com monitoramento reforcado.',
       'Carlos Almeida'
FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL
SELECT id, DATE '2026-08-31', 'verde', 43.2,
       'Renovacao do centro de controle dentro do previsto, com ambiente de homologacao estabilizado.',
       'Homologacao estabilizada e conclusao do treinamento da primeira turma de operadores.',
       'Nenhum impedimento critico no periodo.',
       'Executar o ensaio integrado dos subsistemas e consolidar o plano de transicao operacional.',
       'Marina Costa'
FROM public.projects WHERE code = 'PRJ-0510'
UNION ALL
SELECT id, DATE '2026-08-31', 'amarelo', 22.0,
       'Projeto em detalhamento, com replanejamento de escopo nas estacoes prioritarias da primeira etapa.',
       'Diagnostico de acessibilidade concluido em oito estacoes da primeira etapa.',
       'Definicao de fornecedor de elevadores pendente de homologacao tecnica.',
       'Fechar a especificacao tecnica dos elevadores e iniciar o processo de contratacao.',
       'Rafael Nunes'
FROM public.projects WHERE code = 'PRJ-0587';

-- ---------------------------------------------------------------------------
-- Riscos e pontos de atencao (3+ por projeto)
-- ---------------------------------------------------------------------------
INSERT INTO public.risk_issue_items (scope_type, project_id, item_type, title, criticality, risk_or_issue_text, mitigation_plan, owner_name, status, planned_resolution_date)
-- PRJ-0442
SELECT 'projeto', id, 'risco', 'Restricao de janela operacional para instalacao', 'Alta',
       'Numero limitado de janelas noturnas pode atrasar a instalacao dos lotes de sinalizacao.',
       'Replanejar a instalacao por lotes menores e manter janela de contingencia aos finais de semana.',
       'Coordenacao de Implantacao', 'em_tratamento', DATE '2026-10-15' FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT 'projeto', id, 'risco', 'Interferencia com a operacao comercial', 'Media',
       'Intervencoes na via podem impactar a pontualidade durante os testes de campo.',
       'Sincronizar os testes com o centro de controle e comunicar previamente as areas de operacao.',
       'Gerencia de Operacao', 'aberto', DATE '2026-11-30' FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT 'projeto', id, 'risco', 'Compatibilidade com equipamentos legados', 'Media',
       'Equipamentos legados podem exigir adaptacao adicional na integracao com a nova sinalizacao.',
       'Realizar testes de integracao antecipados e prever verba para adaptacoes.',
       'Engenharia de Sistemas', 'em_tratamento', DATE '2026-10-31' FROM public.projects WHERE code = 'PRJ-0442'
-- PRJ-0510
UNION ALL SELECT 'projeto', id, 'risco', 'Disponibilidade de equipe para ensaio integrado', 'Media',
       'Concorrencia de agenda entre operadores pode adiar o ensaio integrado do centro de controle.',
       'Confirmar a escala das equipes com duas semanas de antecedencia e prever recurso reserva.',
       'Gerencia de Operacao', 'aberto', DATE '2026-10-05' FROM public.projects WHERE code = 'PRJ-0510'
UNION ALL SELECT 'projeto', id, 'risco', 'Migracao de dados do sistema anterior', 'Alta',
       'Falhas na migracao dos dados historicos podem comprometer a transicao operacional.',
       'Executar migracao em ambiente de homologacao com validacao dupla antes do corte.',
       'Area de Tecnologia', 'em_tratamento', DATE '2026-11-15' FROM public.projects WHERE code = 'PRJ-0510'
UNION ALL SELECT 'projeto', id, 'risco', 'Curva de aprendizado dos operadores', 'Baixa',
       'Operadores podem levar tempo para dominar a nova interface do centro de controle.',
       'Ampliar as turmas de treinamento e disponibilizar suporte assistido nas primeiras semanas.',
       'Gerencia de Operacao', 'aberto', DATE '2026-12-10' FROM public.projects WHERE code = 'PRJ-0510'
-- PRJ-0587
UNION ALL SELECT 'projeto', id, 'risco', 'Homologacao de fornecedor de elevadores', 'Alta',
       'Atraso na homologacao tecnica dos elevadores pode comprometer o cronograma de acessibilidade.',
       'Antecipar a analise tecnica e manter fornecedor alternativo qualificado.',
       'Area de Contratacoes', 'em_tratamento', DATE '2026-12-20' FROM public.projects WHERE code = 'PRJ-0587'
UNION ALL SELECT 'projeto', id, 'risco', 'Interdicao parcial de estacoes durante as obras', 'Media',
       'Obras de acessibilidade podem exigir interdicao parcial de areas de circulacao.',
       'Planejar as obras por etapas e comunicar os usuarios com antecedencia.',
       'Coordenacao de Obras', 'aberto', DATE '2027-01-31' FROM public.projects WHERE code = 'PRJ-0587'
UNION ALL SELECT 'projeto', id, 'risco', 'Restricoes orcamentarias para a segunda etapa', 'Media',
       'Contingenciamento orcamentario pode limitar o avanco da segunda etapa de estacoes.',
       'Priorizar estacoes de maior demanda e buscar fontes de financiamento complementares.',
       'Gerencia de Portfolio', 'aberto', DATE '2027-02-28' FROM public.projects WHERE code = 'PRJ-0587';

-- ---------------------------------------------------------------------------
-- Marcos e entregas (3 por projeto)
-- ---------------------------------------------------------------------------
INSERT INTO public.project_deliverables_milestones (project_id, description, planned_date, status)
SELECT id, 'Instalacao do primeiro lote de equipamentos de sinalizacao', DATE '2026-09-20', 'em_andamento' FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT id, 'Inicio da operacao assistida na Linha Azul', DATE '2026-11-10', 'planejado' FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT id, 'Aceite definitivo do sistema de sinalizacao', DATE '2027-02-28', 'planejado' FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT id, 'Ensaio integrado do centro de controle operacional', DATE '2026-09-28', 'planejado' FROM public.projects WHERE code = 'PRJ-0510'
UNION ALL SELECT id, 'Corte para o novo centro de controle', DATE '2026-12-05', 'planejado' FROM public.projects WHERE code = 'PRJ-0510'
UNION ALL SELECT id, 'Encerramento do plano de transicao operacional', DATE '2027-03-15', 'planejado' FROM public.projects WHERE code = 'PRJ-0510'
UNION ALL SELECT id, 'Conclusao da especificacao tecnica dos elevadores', DATE '2026-10-30', 'planejado' FROM public.projects WHERE code = 'PRJ-0587'
UNION ALL SELECT id, 'Contratacao do fornecedor de elevadores', DATE '2026-12-15', 'planejado' FROM public.projects WHERE code = 'PRJ-0587'
UNION ALL SELECT id, 'Entrega da primeira estacao adaptada', DATE '2027-05-30', 'planejado' FROM public.projects WHERE code = 'PRJ-0587';

-- ---------------------------------------------------------------------------
-- Atividades do cronograma do PRJ-0442 (S5-06: campos cronograma.* do chat)
-- Nenhuma atividade esta vencida e aberta, para nao disparar o alerta de prazo.
-- ---------------------------------------------------------------------------
INSERT INTO public.schedule_items (project_id, wbs_code, activity_name, responsible_name,
                                   planned_start_date, planned_end_date, actual_start_date,
                                   actual_end_date, progress_percent, status, metadata)
SELECT id, '1.1', 'Projeto executivo da sinalizacao', 'Engenharia de Sistemas',
       DATE '2026-01-15', DATE '2026-04-30', DATE '2026-01-15', DATE '2026-05-08', 100, 'concluido',
       '{"mock": true}'::jsonb FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT id, '1.2', 'Instalacao do lote 1 de equipamentos de sinalizacao', 'Coordenacao de Implantacao',
       DATE '2026-05-04', DATE '2026-09-20', DATE '2026-05-11', DATE '2026-09-25', 100, 'concluido',
       '{"mock": true}'::jsonb FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT id, '1.3', 'Instalacao do lote 2 de equipamentos de sinalizacao', 'Coordenacao de Implantacao',
       DATE '2026-09-21', DATE '2026-11-15', DATE '2026-09-28', NULL, 35, 'em_andamento',
       '{"mock": true}'::jsonb FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT id, '1.4', 'Testes integrados de sinalizacao', 'Engenharia de Sistemas',
       DATE '2026-11-16', DATE '2026-12-10', NULL, NULL, 0, 'planejado',
       '{"mock": true}'::jsonb FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT id, '1.5', 'Preparacao da operacao assistida', 'Gerencia de Operacao',
       DATE '2026-11-23', DATE '2026-12-18', NULL, NULL, 0, 'planejado',
       '{"mock": true}'::jsonb FROM public.projects WHERE code = 'PRJ-0442';

-- ---------------------------------------------------------------------------
-- Beneficios esperados (2-3 por projeto)
-- ---------------------------------------------------------------------------
INSERT INTO public.project_benefits (project_id, description, benefit_type, expected_value, measurement_indicator)
SELECT id, 'Reducao de falhas em equipamentos criticos de sinalizacao', 'operacional', 'reducao de 12%', 'Falhas por milhao de quilometros rodados' FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT id, 'Aumento da disponibilidade da via', 'operacional', 'aumento de 5%', 'Indice de disponibilidade da linha' FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT id, 'Reducao do tempo medio entre trens', 'operacional', 'reducao de 6%', 'Headway medio em horario de pico' FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT id, 'Maior agilidade na resposta a ocorrencias', 'operacional', 'reducao de 8%', 'Tempo medio de resposta operacional' FROM public.projects WHERE code = 'PRJ-0510'
UNION ALL SELECT id, 'Melhoria na rastreabilidade de eventos operacionais', 'gestao', 'cobertura de 100%', 'Percentual de eventos registrados automaticamente' FROM public.projects WHERE code = 'PRJ-0510'
UNION ALL SELECT id, 'Ampliacao da acessibilidade universal nas estacoes', 'social', 'oito estacoes adaptadas', 'Numero de estacoes com acessibilidade plena' FROM public.projects WHERE code = 'PRJ-0587'
UNION ALL SELECT id, 'Aumento da satisfacao dos usuarios com mobilidade reduzida', 'social', 'aumento de 15%', 'Indice de satisfacao em pesquisa de acessibilidade' FROM public.projects WHERE code = 'PRJ-0587';

-- ---------------------------------------------------------------------------
-- Mudancas registradas
-- ---------------------------------------------------------------------------
INSERT INTO public.change_records (scope_type, project_id, change_type, title, status, impact_summary, registration_date)
SELECT 'projeto', id, 'prazo', 'Reprogramacao da instalacao do lote 2', 'aprovada',
       'Postergacao de 14 dias sem alteracao do marco final aprovado.', DATE '2026-08-20' FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT 'projeto', id, 'escopo', 'Inclusao de redundancia no enlace de comunicacao', 'aprovada',
       'Acrescimo de escopo para elevar a confiabilidade, com impacto controlado de custo.', DATE '2026-07-30' FROM public.projects WHERE code = 'PRJ-0442'
UNION ALL SELECT 'projeto', id, 'escopo', 'Inclusao de estacao adicional na primeira etapa', 'em_analise',
       'Avaliacao de impacto de custo e prazo para incluir uma estacao prioritaria.', DATE '2026-08-25' FROM public.projects WHERE code = 'PRJ-0587';

COMMIT;
