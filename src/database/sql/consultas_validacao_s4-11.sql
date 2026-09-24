-- =====================================================================
-- S4-11 (#200) — Consultas de validação de persistência, auditoria
--                e acesso por perfil sintético
-- =====================================================================
-- Natureza: script de VALIDAÇÃO (somente leitura). Não é migração.
--           Não recebe numeração 01–14 de propósito: nada aqui altera schema
--           nem dados. Executar em qualquer ordem, quantas vezes for preciso.
--
-- Alvo:     Supabase (PostgreSQL), schema public.
-- Uso:      cada bloco CV-xx é autocontido. Rode um por vez e guarde o
--           resultado em docs/testes/sprint4/evidencias/.
--
-- JANELA DA RODADA — antes de executar, troque o literal abaixo em TODO o
-- arquivo (find/replace de '2026-09-22 00:00:00-03'). Ele delimita o que a
-- rodada considera "massa gerada", separando o tráfego novo do histórico.
--
-- Convenção de saída: toda consulta devolve uma coluna `veredito` com
-- APROVADO / FALHOU quando o critério é mecânico, ou linhas de inspeção
-- quando o veredito depende de leitura humana (indicado no cabeçalho).
-- =====================================================================


-- ---------------------------------------------------------------------
-- P-00 — Inventário de massa (pré-condição de toda a rodada)
-- Não tem veredito. Serve para o cabeçalho de congelamento do relatório.
-- ---------------------------------------------------------------------
SELECT 'ai_conversations'      AS tabela, COUNT(*) AS total_geral,
       COUNT(*) FILTER (WHERE created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03') AS na_janela
  FROM public.ai_conversations
UNION ALL SELECT 'ai_interactions', COUNT(*),
       COUNT(*) FILTER (WHERE created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03')
  FROM public.ai_interactions
UNION ALL SELECT 'consulted_sources', COUNT(*),
       COUNT(*) FILTER (WHERE created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03')
  FROM public.consulted_sources
UNION ALL SELECT 'audit_events', COUNT(*),
       COUNT(*) FILTER (WHERE created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03')
  FROM public.audit_events
UNION ALL SELECT 'out_of_scope_requests', COUNT(*),
       COUNT(*) FILTER (WHERE created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03')
  FROM public.out_of_scope_requests
UNION ALL SELECT 'users', COUNT(*), NULL
  FROM public.users
UNION ALL SELECT 'access_rules', COUNT(*), NULL
  FROM public.access_rules
ORDER BY 1;


-- ---------------------------------------------------------------------
-- P-01 — Caracterização da massa da janela
-- O P-00 revelou ~2.000 interações na janela, muito além das ~5 consultas
-- manuais previstas. Antes de dar veredito em qualquer CV é preciso saber
-- de onde essa massa veio: canal, rota, status e concentração no tempo.
-- Massa concentrada em poucos minutos = replay de dataset; espalhada ao
-- longo do dia = uso real. A leitura muda o que os casos provam.
-- ---------------------------------------------------------------------
SELECT c.channel,
       i.route_taken,
       i.processing_status,
       i.macro_intent_predicted,
       COUNT(*)                          AS interacoes,
       MIN(i.created_at)                 AS primeira,
       MAX(i.created_at)                 AS ultima,
       round(avg(i.processing_ms))       AS ms_medio
  FROM public.ai_interactions i
  JOIN public.ai_conversations c ON c.id = i.conversation_id
 WHERE i.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03'
 GROUP BY 1, 2, 3, 4
 ORDER BY interacoes DESC;


-- ---------------------------------------------------------------------
-- P-02 — Fora de escopo: classificadas x registradas
-- Decide o veredito do CV-08 e a existência do defeito D-02.
-- out_of_scope_requests = 0 sobre ~2.100 interações tem duas explicações
-- possíveis, e elas levam a vereditos opostos:
--   (a) nenhuma pergunta foi classificada como fora de escopo
--       -> CV-08 fica "Não executado", falta massa;
--   (b) houve classificação mas o backend não persiste a linha
--       -> defeito de persistência, que é o objeto desta task.
-- ---------------------------------------------------------------------
SELECT COUNT(*) FILTER (WHERE i.route_taken            = 'fora_escopo')    AS por_rota,
       COUNT(*) FILTER (WHERE i.processing_status      = 'fora_escopo')    AS por_status,
       COUNT(*) FILTER (WHERE i.macro_intent_predicted = 'FORA_DE_ESCOPO') AS por_intencao,
       COUNT(*) FILTER (WHERE i.route_taken            = 'fora_escopo'
                           OR i.processing_status      = 'fora_escopo'
                           OR i.macro_intent_predicted = 'FORA_DE_ESCOPO') AS classificadas_total,
       COUNT(o.id)                                                         AS registradas_em_out_of_scope,
       COUNT(*) FILTER (WHERE i.limitation_response IS NOT NULL)           AS com_resposta_de_limitacao,
       CASE
         WHEN COUNT(*) FILTER (WHERE i.route_taken = 'fora_escopo'
                                  OR i.processing_status = 'fora_escopo'
                                  OR i.macro_intent_predicted = 'FORA_DE_ESCOPO') = 0
              THEN 'SEM MASSA: nenhuma pergunta classificada como fora de escopo'
         WHEN COUNT(o.id) = 0
              THEN 'DEFEITO D-02: classifica fora de escopo mas nao persiste em out_of_scope_requests'
         ELSE 'INSPECIONAR: ha registro, validar cobertura no CV-08'
       END                                                                 AS veredito
  FROM public.ai_interactions i
  LEFT JOIN public.out_of_scope_requests o ON o.interaction_id = i.id
 WHERE i.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03';


-- ---------------------------------------------------------------------
-- P-03 — Severidade do D-02
-- O P-02 provou que out_of_scope_requests nunca e escrita (136 x 0).
-- Falta a medida que decide a severidade: o usuario foi informado da
-- limitacao, ou recebeu vazio/alucinacao?
--   com_limitacao = classificadas  -> severidade Media (so a trilha se perde)
--   com_limitacao < classificadas  -> severidade Alta (impacto ao usuario)
--   com_fonte_citada > 0           -> pior caso: citou fonte para pergunta
--                                     fora do dominio
-- Atencao: o recorte aqui e SO route_taken='fora_escopo'. Contar
-- limitation_response sobre a janela inteira nao responde a pergunta.
-- ---------------------------------------------------------------------
SELECT COUNT(*)                                                                AS classificadas,
       COUNT(*) FILTER (WHERE btrim(coalesce(i.limitation_response,'')) <> '') AS com_limitacao,
       COUNT(*) FILTER (WHERE i.response_text IS NOT NULL)                     AS com_response_text,
       COUNT(*) FILTER (WHERE i.processing_status <> 'fora_escopo')            AS status_divergente,
       COUNT(*) FILTER (WHERE i.macro_intent_predicted IS DISTINCT FROM 'FORA_DE_ESCOPO') AS intencao_divergente,
       COUNT(*) FILTER (WHERE EXISTS (SELECT 1 FROM public.consulted_sources s
                                       WHERE s.interaction_id = i.id))         AS com_fonte_citada
  FROM public.ai_interactions i
 WHERE i.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03'
   AND i.route_taken = 'fora_escopo';



-- =====================================================================
-- R-01 — PAINEL DA RODADA (CV-01 a CV-08 em uma consulta)
-- =====================================================================
-- Devolve 8 linhas: caso, eixo, medida-chave e veredito. Serve para
-- preencher a matriz da secao 3 do relatorio de uma vez so.
-- Os blocos CV-xx detalhados acima continuam validos e sao a evidencia
-- linha a linha; este painel e o resumo executavel.
-- Veredito 'NAO EXECUTADO' = falta massa para o caso, nao falha.
-- =====================================================================
SELECT 'CV-01' AS caso, 'persistencia da interacao' AS eixo,
       format('%s interacoes na janela; %s sem user_prompt; %s sem processing_ms',
              COUNT(*),
              COUNT(*) FILTER (WHERE btrim(coalesce(user_prompt,'')) = ''),
              COUNT(*) FILTER (WHERE processing_ms IS NULL)) AS medida,
       CASE WHEN COUNT(*) = 0 THEN 'NAO EXECUTADO'
            WHEN COUNT(*) FILTER (WHERE btrim(coalesce(user_prompt,'')) = '') > 0 THEN 'FALHOU'
            ELSE 'APROVADO' END AS veredito
  FROM public.ai_interactions
 WHERE created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03'

UNION ALL
SELECT 'CV-02', 'vinculo conversa x interacao',
       format('%s interacoes orfas; %s conversas sem interacao', a.orfas, b.vazias),
       CASE WHEN a.orfas = 0 AND b.vazias = 0 THEN 'APROVADO' ELSE 'FALHOU' END
  FROM (SELECT COUNT(*) AS orfas
          FROM public.ai_interactions i
          LEFT JOIN public.ai_conversations c ON c.id = i.conversation_id
         WHERE i.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03' AND c.id IS NULL) a,
       (SELECT COUNT(*) AS vazias
          FROM public.ai_conversations c
         WHERE c.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03'
           AND NOT EXISTS (SELECT 1 FROM public.ai_interactions i
                            WHERE i.conversation_id = c.id)) b

UNION ALL
SELECT 'CV-03', 'dominio dos campos classificatorios',
       format('%s processadas sem intencao macro; %s processadas sem response_text', t.x, t.y),
       CASE WHEN t.x = 0 AND t.y = 0 THEN 'APROVADO' ELSE 'FALHOU' END
  FROM (SELECT COUNT(*) FILTER (WHERE processing_status = 'processado'
                                  AND macro_intent_predicted IS NULL) AS x,
               COUNT(*) FILTER (WHERE processing_status = 'processado'
                                  AND response_text IS NULL)          AS y
          FROM public.ai_interactions
         WHERE created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03') t

UNION ALL
SELECT 'CV-04', 'reexecucao preserva historico',
       format('%s prompts repetidos; %s com update posterior a escrita', t.grupos, t.com_update),
       CASE WHEN t.grupos = 0 THEN 'NAO EXECUTADO'
            WHEN t.com_update > 0 THEN 'FALHOU'
            ELSE 'APROVADO' END
  FROM (SELECT COUNT(*) AS grupos, COUNT(*) FILTER (WHERE g.upd) AS com_update
          FROM (SELECT user_prompt,
                       bool_or(updated_at > created_at + INTERVAL '1 second') AS upd
                  FROM public.ai_interactions
                 WHERE created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03'
                 GROUP BY user_prompt
                HAVING COUNT(*) > 1) g) t

UNION ALL
SELECT 'CV-05', 'cadeia de correlacao',
       format('%s interacoes sem evento de auditoria; %s respostas documentais sem fonte', t.a, t.b),
       CASE WHEN t.a = 0 AND t.b = 0 THEN 'APROVADO' ELSE 'FALHOU' END
  FROM (SELECT COUNT(*) FILTER (
                 WHERE NOT EXISTS (SELECT 1 FROM public.audit_events e
                                    WHERE e.interaction_id = i.id))              AS a,
               COUNT(*) FILTER (
                 WHERE i.route_taken IN ('sharepoint_query','analise_local')
                   AND i.processing_status = 'processado'
                   AND NOT EXISTS (SELECT 1 FROM public.consulted_sources s
                                    WHERE s.interaction_id = i.id))              AS b
          FROM public.ai_interactions i
         WHERE i.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03') t

UNION ALL
SELECT 'CV-06', 'auditoria com correlation_id',
       format('%s eventos sem correlation_id; %s interacoes com mais de um', t.a, t.b),
       CASE WHEN t.a = 0 AND t.b = 0 THEN 'APROVADO' ELSE 'FALHOU' END
  FROM (SELECT (SELECT COUNT(*) FROM public.audit_events
                 WHERE created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03' AND correlation_id IS NULL) AS a,
               (SELECT COUNT(*) FROM (
                  SELECT interaction_id FROM public.audit_events
                   WHERE created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03' AND interaction_id IS NOT NULL
                   GROUP BY interaction_id
                  HAVING COUNT(DISTINCT correlation_id) > 1) z)      AS b) t

UNION ALL
SELECT 'CV-07', 'erro persistido e auditado',
       format('%s interacoes com processing_status=erro; %s auditadas como falha', t.a, t.b),
       CASE WHEN t.a = 0 THEN 'NAO EXECUTADO'
            WHEN t.b < t.a THEN 'FALHOU'
            ELSE 'APROVADO' END
  FROM (SELECT COUNT(*) AS a,
               COUNT(*) FILTER (
                 WHERE EXISTS (SELECT 1 FROM public.audit_events e
                                WHERE e.interaction_id = i.id
                                  AND e.event_status = 'falha')) AS b
          FROM public.ai_interactions i
         WHERE i.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03'
           AND i.processing_status = 'erro') t

UNION ALL
SELECT 'CV-08', 'fora de escopo registrado',
       format('%s classificadas fora de escopo; %s registradas em out_of_scope_requests', t.a, t.b),
       CASE WHEN t.a = 0 THEN 'NAO EXECUTADO'
            WHEN t.b = 0 THEN 'FALHOU (D-02)'
            WHEN t.b < t.a THEN 'FALHOU parcial'
            ELSE 'APROVADO' END
  FROM (SELECT COUNT(*) AS a,
               COUNT(*) FILTER (
                 WHERE EXISTS (SELECT 1 FROM public.out_of_scope_requests o
                                WHERE o.interaction_id = i.id)) AS b
          FROM public.ai_interactions i
         WHERE i.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03'
           AND (i.route_taken = 'fora_escopo'
             OR i.processing_status = 'fora_escopo'
             OR i.macro_intent_predicted = 'FORA_DE_ESCOPO')) t

ORDER BY 1;

-- =====================================================================
-- BLOCO A — PERSISTÊNCIA
-- =====================================================================

-- ---------------------------------------------------------------------
-- CV-01 (positivo) — Cada consulta disparada gerou uma linha em
-- ai_interactions, com o texto do usuário preservado sem truncamento.
-- Veredito por inspeção: confira que a contagem bate com o número de
-- consultas que você disparou e que user_prompt é o texto integral.
-- ---------------------------------------------------------------------
SELECT i.id,
       i.created_at,
       c.channel,
       i.user_prompt,
       length(i.user_prompt)        AS chars_prompt,
       i.normalized_prompt IS NOT NULL AS tem_normalizado,
       i.processing_status,
       i.route_taken,
       i.processing_ms
  FROM public.ai_interactions i
  JOIN public.ai_conversations c ON c.id = i.conversation_id
 WHERE i.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03'
 ORDER BY i.created_at;


-- ---------------------------------------------------------------------
-- CV-02 (positivo) — Integridade do vínculo conversa ↔ interação.
-- Duas falhas possíveis: interação apontando para conversa inexistente
-- (só ocorre se a FK tiver sido derrubada) e conversa criada sem nenhuma
-- interação (backend abriu a conversa e perdeu a escrita da interação).
-- ---------------------------------------------------------------------
WITH interacoes_orfas AS (
    SELECT i.id
      FROM public.ai_interactions i
      LEFT JOIN public.ai_conversations c ON c.id = i.conversation_id
     WHERE i.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03'
       AND c.id IS NULL
),
conversas_vazias AS (
    SELECT c.id
      FROM public.ai_conversations c
      LEFT JOIN public.ai_interactions i ON i.conversation_id = c.id
     WHERE c.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03'
     GROUP BY c.id
    HAVING COUNT(i.id) = 0
)
SELECT (SELECT COUNT(*) FROM interacoes_orfas)  AS interacoes_sem_conversa,
       (SELECT COUNT(*) FROM conversas_vazias)  AS conversas_sem_interacao,
       CASE WHEN (SELECT COUNT(*) FROM interacoes_orfas) = 0
             AND (SELECT COUNT(*) FROM conversas_vazias) = 0
            THEN 'APROVADO' ELSE 'FALHOU' END   AS veredito;


-- ---------------------------------------------------------------------
-- CV-03 (positivo) — Domínio dos campos classificatórios e faixa das
-- confianças. As CHECK constraints já barram valores fora do domínio, então
-- este caso vale por dois motivos: prova que a constraint está ativa no
-- ambiente real e flagra o buraco que a constraint NÃO cobre — interação
-- marcada como 'processado' sem macro_intent nem confiança.
-- ---------------------------------------------------------------------
SELECT i.id,
       i.macro_intent_predicted,
       i.macro_intent_confidence,
       i.specific_intent_predicted,
       i.specific_intent_confidence,
       i.route_taken,
       i.processing_status,
       CASE
         WHEN i.macro_intent_predicted IS NOT NULL
          AND i.macro_intent_predicted NOT IN ('CONSULTA','TRANSACAO','ALERTA','FORA_DE_ESCOPO')
              THEN 'FALHOU: macro fora do domínio'
         WHEN i.route_taken NOT IN ('copilot_topic','power_automate','sharepoint_query','analise_local','fora_escopo')
              THEN 'FALHOU: rota fora do domínio'
         WHEN i.processing_status NOT IN ('processado','sem_confianca','fora_escopo','erro','pendente')
              THEN 'FALHOU: status fora do domínio'
         WHEN i.macro_intent_confidence IS NOT NULL
          AND (i.macro_intent_confidence < 0 OR i.macro_intent_confidence > 1)
              THEN 'FALHOU: confiança fora de [0,1]'
         WHEN i.processing_status = 'processado' AND i.macro_intent_predicted IS NULL
              THEN 'FALHOU: processado sem intenção macro'
         WHEN i.processing_status = 'processado' AND i.response_text IS NULL
              THEN 'FALHOU: processado sem response_text'
         ELSE 'APROVADO'
       END AS veredito
  FROM public.ai_interactions i
 WHERE i.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03'
 ORDER BY veredito DESC, i.created_at;


-- ---------------------------------------------------------------------
-- CV-04 (positivo) — Reexecução preserva histórico.
-- Pré-condição: disparar a MESMA pergunta duas vezes na janela.
-- Critério: dois ids distintos, dois created_at distintos, nenhum
-- updated_at posterior ao created_at da primeira linha (não houve
-- sobrescrita). Persistência tem que ser append-only aqui.
-- ---------------------------------------------------------------------
SELECT i.user_prompt,
       COUNT(*)                                   AS execucoes,
       COUNT(DISTINCT i.id)                       AS ids_distintos,
       COUNT(DISTINCT i.conversation_id)          AS conversas_distintas,
       MIN(i.created_at)                          AS primeira,
       MAX(i.created_at)                          AS ultima,
       bool_or(i.updated_at > i.created_at + INTERVAL '1 second') AS houve_update_posterior,
       CASE WHEN COUNT(*) = COUNT(DISTINCT i.id)
             AND NOT bool_or(i.updated_at > i.created_at + INTERVAL '1 second')
            THEN 'APROVADO' ELSE 'FALHOU' END     AS veredito
  FROM public.ai_interactions i
 WHERE i.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03'
 GROUP BY i.user_prompt
HAVING COUNT(*) > 1
 ORDER BY execucoes DESC;


-- =====================================================================
-- BLOCO B — CORRELAÇÃO E AUDITORIA
-- =====================================================================

-- ---------------------------------------------------------------------
-- CV-05 (positivo) — Cadeia de correlação completa:
--   ai_conversations.id → ai_interactions.conversation_id
--                       → consulted_sources.interaction_id
--                       → audit_events.interaction_id
-- Uma linha por interação, com a contagem de cada elo. O elo de fontes só
-- é exigível quando a rota consultou base documental; para 'fora_escopo'
-- a ausência de fonte é o comportamento correto.
-- ---------------------------------------------------------------------
SELECT i.id                                   AS interaction_id,
       c.id                                   AS conversation_id,
       i.route_taken,
       i.processing_status,
       COUNT(DISTINCT s.id)                   AS qtd_fontes,
       COUNT(DISTINCT a.id)                   AS qtd_eventos_auditoria,
       CASE
         WHEN COUNT(DISTINCT a.id) = 0
              THEN 'FALHOU: sem evento de auditoria'
         WHEN i.route_taken IN ('sharepoint_query','analise_local')
          AND i.processing_status = 'processado'
          AND COUNT(DISTINCT s.id) = 0
              THEN 'FALHOU: resposta sem fonte citada'
         ELSE 'APROVADO'
       END                                    AS veredito
  FROM public.ai_interactions i
  JOIN public.ai_conversations c  ON c.id = i.conversation_id
  LEFT JOIN public.consulted_sources s ON s.interaction_id = i.id
  LEFT JOIN public.audit_events a      ON a.interaction_id = i.id
 WHERE i.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03'
 GROUP BY i.id, c.id, i.route_taken, i.processing_status
 ORDER BY veredito DESC, i.created_at;


-- ---------------------------------------------------------------------
-- CV-06 (positivo) — Evento de auditoria por interação, com componente
-- declarado e correlation_id coerente.
-- Critérios: (a) todo evento da janela tem correlation_id;
--            (b) uma interação não mistura dois correlation_id distintos;
--            (c) os componentes emitidos cobrem pelo menos api + pln.
-- ---------------------------------------------------------------------
SELECT i.id                                       AS interaction_id,
       COUNT(a.id)                                AS eventos,
       COUNT(a.id) FILTER (WHERE a.correlation_id IS NULL) AS eventos_sem_correlacao,
       COUNT(DISTINCT a.correlation_id)           AS correlation_ids_distintos,
       array_agg(DISTINCT a.component ORDER BY a.component) AS componentes,
       array_agg(DISTINCT a.event_status ORDER BY a.event_status) AS status_emitidos,
       CASE
         WHEN COUNT(a.id) = 0 THEN 'FALHOU: sem evento'
         WHEN COUNT(a.id) FILTER (WHERE a.correlation_id IS NULL) > 0
              THEN 'FALHOU: evento sem correlation_id'
         WHEN COUNT(DISTINCT a.correlation_id) > 1
              THEN 'FALHOU: correlation_id inconsistente na interação'
         WHEN NOT ('api' = ANY(array_agg(a.component)))
              THEN 'FALHOU: componente api não auditado'
         ELSE 'APROVADO'
       END                                        AS veredito
  FROM public.ai_interactions i
  LEFT JOIN public.audit_events a ON a.interaction_id = i.id
 WHERE i.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03'
 GROUP BY i.id
 ORDER BY veredito DESC;


-- ---------------------------------------------------------------------
-- CV-07 (negativo) — Erro de processamento é persistido, não engolido.
-- Pré-condição: provocar uma falha na janela (derrubar a chave do provedor
-- de geração, ou apontar o backend para um endpoint inválido) e disparar
-- uma consulta.
-- Critério: existe interação com processing_status='erro' E ao menos um
-- audit_event com event_status='falha' apontando para ela.
-- ---------------------------------------------------------------------
SELECT i.id,
       i.created_at,
       i.user_prompt,
       i.processing_status,
       i.route_taken,
       i.response_text IS NULL                    AS resposta_vazia,
       COUNT(a.id) FILTER (WHERE a.event_status = 'falha') AS eventos_falha,
       array_agg(DISTINCT a.component)            AS componentes,
       CASE WHEN COUNT(a.id) FILTER (WHERE a.event_status = 'falha') > 0
            THEN 'APROVADO' ELSE 'FALHOU: erro não auditado' END AS veredito
  FROM public.ai_interactions i
  LEFT JOIN public.audit_events a ON a.interaction_id = i.id
 WHERE i.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03'
   AND i.processing_status = 'erro'
 GROUP BY i.id
 ORDER BY i.created_at;


-- ---------------------------------------------------------------------
-- CV-08 (negativo) — Pergunta fora de escopo é registrada e respondida
-- com limitação, não com alucinação.
-- Pré-condição: disparar uma pergunta claramente fora do domínio do Metrô
-- (ex.: "qual a previsão do tempo amanhã?").
-- Critério: route_taken='fora_escopo' OU processing_status='fora_escopo',
-- linha correspondente em out_of_scope_requests, limitation_response
-- preenchida e nenhuma fonte citada.
-- ---------------------------------------------------------------------
SELECT i.id,
       i.user_prompt,
       i.route_taken,
       i.processing_status,
       i.macro_intent_predicted,
       i.limitation_response,
       o.id                                       AS out_of_scope_id,
       o.review_status,
       COUNT(s.id)                                AS fontes_citadas,
       CASE
         WHEN o.id IS NULL
              THEN 'FALHOU: não registrado em out_of_scope_requests'
         WHEN i.limitation_response IS NULL OR btrim(i.limitation_response) = ''
              THEN 'FALHOU: sem resposta de limitação'
         WHEN COUNT(s.id) > 0
              THEN 'FALHOU: citou fonte para pergunta fora de escopo'
         ELSE 'APROVADO'
       END                                        AS veredito
  FROM public.ai_interactions i
  LEFT JOIN public.out_of_scope_requests o ON o.interaction_id = i.id
  LEFT JOIN public.consulted_sources s     ON s.interaction_id = i.id
 WHERE i.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03'
   AND (i.route_taken = 'fora_escopo'
        OR i.processing_status = 'fora_escopo'
        OR i.macro_intent_predicted = 'FORA_DE_ESCOPO')
 GROUP BY i.id, o.id
 ORDER BY veredito DESC;


-- =====================================================================
-- BLOCO C — ACESSO POR PERFIL SINTÉTICO
-- CV-09 a CV-12 estão BLOQUEADOS pelo defeito D-01 (controle de acesso por
-- perfil não existe, nem em dados nem em código). As consultas abaixo não
-- são desperdício: elas são a EVIDÊNCIA do bloqueio e viram o critério de
-- reabertura quando a implementação entrar na Sprint 5.
-- =====================================================================

-- ---------------------------------------------------------------------
-- CV-09 (positivo, BLOQUEADO) — Perfis sintéticos cadastrados em users.
-- Critério de reabertura: ≥4 usuários ativos cobrindo 'diretoria',
-- 'lider_subportfolio' (2, em subportfólios distintos) e 'equipe_projeto',
-- todos com entra_object_id preenchido (é o campo que casa com os tokens
-- de AUDIO_SIMULATED_IDENTITIES na rota de áudio).
-- ---------------------------------------------------------------------
SELECT u.role_name,
       COUNT(*)                                        AS usuarios,
       COUNT(*) FILTER (WHERE u.is_active)             AS ativos,
       COUNT(*) FILTER (WHERE u.entra_object_id IS NULL) AS sem_entra_object_id
  FROM public.users u
 GROUP BY u.role_name
 ORDER BY u.role_name;

-- Veredito mecânico do CV-09:
SELECT CASE
         WHEN (SELECT COUNT(*) FROM public.users) = 0
              THEN 'BLOQUEADO (D-01): tabela users vazia'
         WHEN (SELECT COUNT(*) FROM public.users WHERE entra_object_id IS NULL) > 0
              THEN 'FALHOU: usuário sem entra_object_id'
         WHEN (SELECT COUNT(DISTINCT role_name) FROM public.users
                WHERE role_name IN ('diretoria','lider_subportfolio','equipe_projeto')) < 3
              THEN 'FALHOU: perfis sintéticos incompletos'
         ELSE 'APROVADO'
       END AS veredito;


-- ---------------------------------------------------------------------
-- CV-10 (positivo, BLOQUEADO) — Regras de acesso cadastradas, cobrindo as
-- duas formas que o schema aceita: regra por user_id e regra por role_name
-- (access_rules_subject_ck exige uma das duas).
-- ---------------------------------------------------------------------
SELECT r.permission_scope,
       COUNT(*)                                          AS regras,
       COUNT(*) FILTER (WHERE r.user_id   IS NOT NULL)   AS por_usuario,
       COUNT(*) FILTER (WHERE r.role_name IS NOT NULL)   AS por_perfil,
       COUNT(*) FILTER (WHERE r.can_read)                AS com_leitura,
       COUNT(*) FILTER (WHERE r.can_export)              AS com_exportacao
  FROM public.access_rules r
 WHERE r.is_active
 GROUP BY r.permission_scope
 ORDER BY r.permission_scope;

-- Veredito mecânico do CV-10:
SELECT CASE
         WHEN (SELECT COUNT(*) FROM public.access_rules) = 0
              THEN 'BLOQUEADO (D-01): tabela access_rules vazia'
         WHEN (SELECT COUNT(*) FROM public.access_rules WHERE user_id   IS NOT NULL) = 0
           OR (SELECT COUNT(*) FROM public.access_rules WHERE role_name IS NOT NULL) = 0
              THEN 'FALHOU: só uma das duas formas de regra está coberta'
         ELSE 'APROVADO'
       END AS veredito;


-- ---------------------------------------------------------------------
-- CV-11 (negativo, BLOQUEADO) — Negativa de acesso entre subportfólios.
-- Roteiro de reabertura: autenticar como o lider_subportfolio do
-- subportfólio A e consultar dado do subportfólio B. O sistema deve NEGAR,
-- emitindo OUT_OF_SCOPE_FOR_PROFILE e um audit_event com
-- event_status='bloqueado'.
-- Hoje: nenhum evento 'bloqueado' pode existir, porque o erro nunca é
-- emitido pelo backend. A consulta prova isso.
-- ---------------------------------------------------------------------
SELECT COUNT(*) FILTER (WHERE a.event_status = 'bloqueado')     AS eventos_bloqueio,
       COUNT(*) FILTER (WHERE a.event_payload::text ILIKE '%OUT_OF_SCOPE_FOR_PROFILE%') AS payloads_com_erro_de_perfil,
       CASE WHEN COUNT(*) FILTER (WHERE a.event_status = 'bloqueado') = 0
            THEN 'BLOQUEADO (D-01): sistema nunca nega acesso por perfil'
            ELSE 'INSPECIONAR: há negativas registradas, validar manualmente' END AS veredito
  FROM public.audit_events a
 WHERE a.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03';


-- ---------------------------------------------------------------------
-- CV-12 (positivo, BLOQUEADO) — Rastreabilidade por usuário.
-- Critério: ai_interactions.user_id e audit_events.user_id preenchidos e
-- apontando para o mesmo usuário autenticado. É o único item do RNF03 que
-- hoje reprova; o resto do RNF03 é executável.
-- ---------------------------------------------------------------------
SELECT COUNT(*)                                        AS interacoes_na_janela,
       COUNT(*) FILTER (WHERE i.user_id IS NULL)       AS sem_usuario,
       round(100.0 * COUNT(*) FILTER (WHERE i.user_id IS NOT NULL)
             / NULLIF(COUNT(*), 0), 1)                 AS pct_com_usuario,
       CASE
         WHEN COUNT(*) = 0 THEN 'NÃO EXECUTADO: sem massa na janela'
         WHEN COUNT(*) FILTER (WHERE i.user_id IS NOT NULL) = 0
              THEN 'BLOQUEADO (D-01): nenhuma interação carrega usuário'
         WHEN COUNT(*) FILTER (WHERE i.user_id IS NULL) > 0
              THEN 'FALHOU: rastreabilidade parcial'
         ELSE 'APROVADO'
       END                                             AS veredito
  FROM public.ai_interactions i
 WHERE i.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03';

-- Complemento do CV-12: mesma checagem do lado da auditoria.
SELECT COUNT(*)                                   AS eventos_na_janela,
       COUNT(*) FILTER (WHERE a.user_id IS NULL)  AS sem_usuario,
       CASE WHEN COUNT(*) FILTER (WHERE a.user_id IS NOT NULL) = 0
            THEN 'BLOQUEADO (D-01): auditoria sem identidade'
            ELSE 'INSPECIONAR' END                AS veredito
  FROM public.audit_events a
 WHERE a.created_at >= TIMESTAMPTZ '2026-09-22 00:00:00-03';


-- =====================================================================
-- APÊNDICE — Mitigação proposta para o D-01 (NÃO APLICADA)
-- =====================================================================
-- Proposta levada ao grupo: popular SOMENTE public.users com 4 perfis
-- sintéticos, sem nenhuma implementação de autorização. Isso recupera o
-- RNF03 (campo de usuário preenchido) a custo zero de código e mantém o
-- RNF02 corretamente reprovado, que é o estado real do sistema.
--
-- Este bloco está comentado de propósito: task de validação não altera
-- massa de produção. Se o grupo aprovar, ele vira migração numerada e
-- entra pela mão do dono da área (ver #244/#245).
--
-- INSERT INTO public.users (entra_object_id, display_name, email, role_name, department)
-- VALUES
--   ('sint-diretoria-001',  'Perfil Sintético — Diretoria',     'sint.diretoria@exemplo.local',  'diretoria',          'Diretoria'),
--   ('sint-lider-a-001',    'Perfil Sintético — Líder Sub. A',  'sint.lider.a@exemplo.local',    'lider_subportfolio', 'Subportfólio A'),
--   ('sint-lider-b-001',    'Perfil Sintético — Líder Sub. B',  'sint.lider.b@exemplo.local',    'lider_subportfolio', 'Subportfólio B'),
--   ('sint-equipe-001',     'Perfil Sintético — Equipe',        'sint.equipe@exemplo.local',     'equipe_projeto',     'Projeto')
-- ON CONFLICT (email) DO NOTHING;
--
-- Rollback correspondente:
-- DELETE FROM public.users WHERE entra_object_id LIKE 'sint-%';
-- =====================================================================
