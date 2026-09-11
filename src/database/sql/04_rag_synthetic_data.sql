-- Carga sintetica do RAG SharePoint - MVP Agente de IA para Portfolio Metro
-- Dados inteiramente ficticios derivados de src/backend/app/rag/data/sharepoint.
-- Pode ser executado apos 01_create_database.sql e 02_initial_data.sql.

BEGIN;

WITH source_items (
    source_file,
    odata_context,
    mock,
    site_id,
    site_display_name,
    list_id,
    list_display_name,
    item_id,
    created_at_source,
    modified_at_source,
    web_url,
    fields
) AS (
    VALUES
    (
        'procedimentos_operacionais.json',
        'https://mock.sharepoint.local/$metadata#lists/items',
        TRUE,
        'metro-mvp-site',
        'Portal Operacional - Dados Ficticios',
        'procedimentos-operacionais',
        'Procedimentos Operacionais',
        '101',
        TIMESTAMPTZ '2026-01-12T09:00:00Z',
        TIMESTAMPTZ '2026-07-18T14:30:00Z',
        'https://mock.sharepoint.local/sites/metro-mvp/Lists/Procedimentos/101',
        '{"Title":"Atendimento a objeto perdido","Codigo":"POP-MVP-001","Categoria":"Atendimento ao passageiro","Linha":"Todas","Status":"Vigente","Conteudo":"Registrar a descricao do objeto, local e horario informados pelo passageiro. Consultar o registro local de achados e perdidos e fornecer o protocolo ficticio. Objetos nao localizados devem permanecer registrados para consulta posterior.","PalavrasChave":"objeto perdido achados perdidos protocolo passageiro"}'::jsonb
    ),
    (
        'procedimentos_operacionais.json',
        'https://mock.sharepoint.local/$metadata#lists/items',
        TRUE,
        'metro-mvp-site',
        'Portal Operacional - Dados Ficticios',
        'procedimentos-operacionais',
        'Procedimentos Operacionais',
        '102',
        TIMESTAMPTZ '2026-02-03T11:15:00Z',
        TIMESTAMPTZ '2026-06-21T10:00:00Z',
        'https://mock.sharepoint.local/sites/metro-mvp/Lists/Procedimentos/102',
        '{"Title":"Apoio a passageiro com mobilidade reduzida","Codigo":"POP-MVP-002","Categoria":"Acessibilidade","Linha":"Todas","Status":"Vigente","Conteudo":"Confirmar a estacao de destino e comunicar a equipe ficticia de recepcao. Priorizar elevadores e rotas acessiveis sinalizadas. Em indisponibilidade de equipamento, orientar uma rota alternativa cadastrada e registrar o atendimento.","PalavrasChave":"acessibilidade cadeira rodas mobilidade elevador apoio"}'::jsonb
    ),
    (
        'procedimentos_operacionais.json',
        'https://mock.sharepoint.local/$metadata#lists/items',
        TRUE,
        'metro-mvp-site',
        'Portal Operacional - Dados Ficticios',
        'procedimentos-operacionais',
        'Procedimentos Operacionais',
        '103',
        TIMESTAMPTZ '2026-03-08T08:20:00Z',
        TIMESTAMPTZ '2026-08-02T16:45:00Z',
        'https://mock.sharepoint.local/sites/metro-mvp/Lists/Procedimentos/103',
        '{"Title":"Comunicacao de indisponibilidade de escada rolante","Codigo":"POP-MVP-003","Categoria":"Equipamentos","Linha":"Todas","Status":"Vigente","Conteudo":"Sinalizar o equipamento como indisponivel, indicar a alternativa acessivel mais proxima e abrir um chamado de manutencao. Atualizar o comunicado ao passageiro quando o status do chamado mudar.","PalavrasChave":"escada rolante falha indisponivel manutencao equipamento"}'::jsonb
    ),
    (
        'comunicados_servico.json',
        'https://mock.sharepoint.local/$metadata#lists/items',
        TRUE,
        'metro-mvp-site',
        'Portal Operacional - Dados Ficticios',
        'comunicados-servico',
        'Comunicados de Servico',
        '201',
        TIMESTAMPTZ '2026-08-01T12:00:00Z',
        TIMESTAMPTZ '2026-08-01T12:00:00Z',
        'https://mock.sharepoint.local/sites/metro-mvp/Lists/Comunicados/201',
        '{"Title":"Operacao assistida na Linha Azul","Tipo":"Operacao","Linha":"Linha 1-Azul","ValidadeInicio":"2026-08-24","ValidadeFim":"2026-08-28","Status":"Programado","Conteudo":"Durante o periodo ficticio, o intervalo entre trens podera ser ampliado entre 22h e o encerramento da operacao para testes de sinalizacao. Recomenda-se comunicar o tempo adicional de viagem nos canais de atendimento.","PalavrasChave":"linha azul intervalo trens sinalizacao horario noite"}'::jsonb
    ),
    (
        'comunicados_servico.json',
        'https://mock.sharepoint.local/$metadata#lists/items',
        TRUE,
        'metro-mvp-site',
        'Portal Operacional - Dados Ficticios',
        'comunicados-servico',
        'Comunicados de Servico',
        '202',
        TIMESTAMPTZ '2026-08-05T15:10:00Z',
        TIMESTAMPTZ '2026-08-10T09:25:00Z',
        'https://mock.sharepoint.local/sites/metro-mvp/Lists/Comunicados/202',
        '{"Title":"Acesso alternativo na Estacao Republica","Tipo":"Acessibilidade","Linha":"Linhas 3-Vermelha e 4-Amarela","ValidadeInicio":"2026-08-20","ValidadeFim":"2026-09-05","Status":"Programado","Conteudo":"Um dos acessos ficticios da Estacao Republica estara fechado para manutencao. Passageiros devem utilizar o acesso da Rua do Arouche, conforme sinalizacao temporaria no local.","PalavrasChave":"republica acesso fechado manutencao rua arouche"}'::jsonb
    ),
    (
        'comunicados_servico.json',
        'https://mock.sharepoint.local/$metadata#lists/items',
        TRUE,
        'metro-mvp-site',
        'Portal Operacional - Dados Ficticios',
        'comunicados-servico',
        'Comunicados de Servico',
        '203',
        TIMESTAMPTZ '2026-07-15T13:00:00Z',
        TIMESTAMPTZ '2026-07-16T08:40:00Z',
        'https://mock.sharepoint.local/sites/metro-mvp/Lists/Comunicados/203',
        '{"Title":"Campanha educativa de embarque","Tipo":"Campanha","Linha":"Todas","ValidadeInicio":"2026-07-20","ValidadeFim":"2026-09-30","Status":"Ativo","Conteudo":"A campanha ficticia reforca que passageiros devem aguardar o desembarque antes de entrar no trem e manter livre a faixa proxima das portas.","PalavrasChave":"embarque desembarque portas campanha seguranca"}'::jsonb
    ),
    (
        'base_atendimento.json',
        'https://mock.sharepoint.local/$metadata#lists/items',
        TRUE,
        'metro-mvp-site',
        'Portal Operacional - Dados Ficticios',
        'base-atendimento',
        'Base de Atendimento',
        '301',
        TIMESTAMPTZ '2026-01-10T10:00:00Z',
        TIMESTAMPTZ '2026-05-11T17:30:00Z',
        'https://mock.sharepoint.local/sites/metro-mvp/Lists/Atendimento/301',
        '{"Title":"Uso do bilhete digital no MVP","Categoria":"Bilhetes","Status":"Publicado","Conteudo":"No cenario ficticio do MVP, o bilhete digital pode ser apresentado na catraca pelo celular. Se a leitura falhar, aumentar o brilho da tela, confirmar que o codigo esta inteiramente visivel e procurar um agente de atendimento.","PalavrasChave":"bilhete digital celular codigo catraca leitura"}'::jsonb
    ),
    (
        'base_atendimento.json',
        'https://mock.sharepoint.local/$metadata#lists/items',
        TRUE,
        'metro-mvp-site',
        'Portal Operacional - Dados Ficticios',
        'base-atendimento',
        'Base de Atendimento',
        '302',
        TIMESTAMPTZ '2026-02-18T14:00:00Z',
        TIMESTAMPTZ '2026-06-09T12:15:00Z',
        'https://mock.sharepoint.local/sites/metro-mvp/Lists/Atendimento/302',
        '{"Title":"Canal de registro de sugestoes e reclamacoes","Categoria":"Relacionamento","Status":"Publicado","Conteudo":"Para a demonstracao, sugestoes e reclamacoes recebem um protocolo no canal digital ficticio. Solicitar estacao, data, horario aproximado e descricao do ocorrido, evitando registrar dados pessoais desnecessarios.","PalavrasChave":"reclamacao sugestao protocolo canal atendimento"}'::jsonb
    ),
    (
        'base_atendimento.json',
        'https://mock.sharepoint.local/$metadata#lists/items',
        TRUE,
        'metro-mvp-site',
        'Portal Operacional - Dados Ficticios',
        'base-atendimento',
        'Base de Atendimento',
        '303',
        TIMESTAMPTZ '2026-04-07T09:30:00Z',
        TIMESTAMPTZ '2026-08-12T11:05:00Z',
        'https://mock.sharepoint.local/sites/metro-mvp/Lists/Atendimento/303',
        '{"Title":"Transporte de bicicleta","Categoria":"Regras de uso","Status":"Publicado","Conteudo":"Na politica ficticia do MVP, bicicletas sao aceitas aos sabados, domingos e feriados durante toda a operacao, e nos dias uteis apos as 20h30. O passageiro deve usar o ultimo carro e respeitar a capacidade indicada pela equipe.","PalavrasChave":"bicicleta bike horario fim semana ultimo carro"}'::jsonb
    )
),
upsert_artifacts AS (
    INSERT INTO public.project_artifacts (
        project_id,
        partner_source_id,
        artifact_type,
        title,
        description,
        sharepoint_url,
        sharepoint_library,
        sharepoint_item_id,
        source_status_label,
        source_system,
        confidentiality_level,
        extracted_at,
        metadata
    )
    SELECT
        CASE
            WHEN source_file = 'comunicados_servico.json'
                AND item_id = '201'
            THEN (SELECT id FROM public.projects WHERE code = 'PRJ-0442')
            ELSE NULL
        END,
        'sharepoint-mock:' || list_id || ':' || item_id,
        'lista_sharepoint',
        fields ->> 'Title',
        fields ->> 'Conteudo',
        web_url,
        list_display_name,
        item_id,
        fields ->> 'Status',
        'sharepoint',
        'interno',
        modified_at_source,
        jsonb_build_object(
            'mock', mock,
            'ficticio', TRUE,
            'official_operational_guidance', FALSE,
            'source_file', source_file,
            'odata_context', odata_context,
            'site', jsonb_build_object(
                'id', site_id,
                'displayName', site_display_name
            ),
            'list', jsonb_build_object(
                'id', list_id,
                'displayName', list_display_name
            ),
            'item', jsonb_build_object(
                'id', item_id,
                'createdDateTime', created_at_source,
                'lastModifiedDateTime', modified_at_source,
                'webUrl', web_url
            ),
            'fields', fields,
            'usage_tags', jsonb_build_array(
                'rag_mock',
                'status',
                'prazo_cronograma',
                'risco_problema',
                'operacional_simulado'
            )
        )
    FROM source_items
    ON CONFLICT (partner_source_id) WHERE partner_source_id IS NOT NULL
    DO UPDATE SET
        project_id = COALESCE(EXCLUDED.project_id, public.project_artifacts.project_id),
        title = EXCLUDED.title,
        description = EXCLUDED.description,
        sharepoint_url = EXCLUDED.sharepoint_url,
        sharepoint_library = EXCLUDED.sharepoint_library,
        sharepoint_item_id = EXCLUDED.sharepoint_item_id,
        source_status_label = EXCLUDED.source_status_label,
        source_system = EXCLUDED.source_system,
        confidentiality_level = EXCLUDED.confidentiality_level,
        extracted_at = EXCLUDED.extracted_at,
        metadata = EXCLUDED.metadata,
        updated_at = NOW()
    RETURNING
        id,
        project_id,
        partner_source_id
)
INSERT INTO public.source_extracts (
    artifact_id,
    project_id,
    extract_index,
    section_title,
    content_text,
    source_locator,
    sharepoint_reference,
    token_count,
    metadata
)
SELECT
    artifact.id,
    artifact.project_id,
    1,
    item.fields ->> 'Title',
    item.fields ->> 'Conteudo',
    item.list_id || '/' || item.item_id || '#Conteudo',
    item.web_url,
    array_length(regexp_split_to_array(trim(item.fields ->> 'Conteudo'), '\s+'), 1),
    jsonb_build_object(
        'mock', item.mock,
        'ficticio', TRUE,
        'official_operational_guidance', FALSE,
        'source_file', item.source_file,
        'list_id', item.list_id,
        'list_display_name', item.list_display_name,
        'item_id', item.item_id,
        'field_name', 'Conteudo',
        'status', item.fields ->> 'Status',
        'line', item.fields ->> 'Linha',
        'category', COALESCE(item.fields ->> 'Categoria', item.fields ->> 'Tipo'),
        'validity', jsonb_strip_nulls(jsonb_build_object(
            'start', item.fields ->> 'ValidadeInicio',
            'end', item.fields ->> 'ValidadeFim'
        )),
        'keywords', item.fields ->> 'PalavrasChave',
        'query_affordances', jsonb_build_array(
            'status',
            'prazo_cronograma',
            'riscos_problemas',
            'informacao_operacional_simulada'
        )
    )
FROM source_items item
JOIN upsert_artifacts artifact
    ON artifact.partner_source_id = 'sharepoint-mock:' || item.list_id || ':' || item.item_id
WHERE NOT EXISTS (
    SELECT 1
    FROM public.source_extracts existing
    WHERE existing.artifact_id = artifact.id
      AND existing.source_locator = item.list_id || '/' || item.item_id || '#Conteudo'
);

COMMIT;

