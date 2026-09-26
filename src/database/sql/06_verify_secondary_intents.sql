-- Verificacao reproduzivel da issue #250.
-- Execute depois de 01_create_database.sql + 02_initial_data.sql em uma base
-- nova, ou apenas depois de 05_add_secondary_intents.sql em uma base existente.
-- O ROLLBACK final garante que os testes negativos nao alterem a base.

BEGIN;

DO $$
DECLARE
    covered_intents INTEGER;
    orphaned_intents INTEGER;
    duplicated_associations INTEGER;
BEGIN
    SELECT COUNT(DISTINCT catalog.specific_intent)
    INTO covered_intents
    FROM public.secondary_intents secondary
    JOIN public.intent_catalog catalog ON catalog.id = secondary.specific_intent_id
    WHERE catalog.macro_intent = 'CONSULTA'
      AND secondary.is_active;

    IF covered_intents <> 13 THEN
        RAISE EXCEPTION 'Esperadas 13 intencoes especificas cobertas; encontradas %.', covered_intents;
    END IF;

    SELECT COUNT(*)
    INTO orphaned_intents
    FROM public.secondary_intents secondary
    LEFT JOIN public.intent_catalog catalog ON catalog.id = secondary.specific_intent_id
    WHERE catalog.id IS NULL;

    IF orphaned_intents <> 0 THEN
        RAISE EXCEPTION 'Foram encontradas % intencoes secundarias orfas.', orphaned_intents;
    END IF;

    SELECT COUNT(*)
    INTO duplicated_associations
    FROM (
        SELECT specific_intent_id, secondary_intent
        FROM public.secondary_intents
        GROUP BY specific_intent_id, secondary_intent
        HAVING COUNT(*) > 1
    ) duplicates;

    IF duplicated_associations <> 0 THEN
        RAISE EXCEPTION 'Foram encontradas % associacoes duplicadas.', duplicated_associations;
    END IF;
END;
$$;

-- Leitura esperada pelo agente RAG: uma linha por sugestao ativa, agrupavel
-- pela intencao especifica que o classificador ja identificou.
SELECT
    catalog.specific_intent,
    secondary.secondary_intent,
    secondary.description,
    secondary.rag_instruction,
    secondary.display_message
FROM public.intent_catalog catalog
JOIN public.secondary_intents secondary
    ON secondary.specific_intent_id = catalog.id
WHERE catalog.macro_intent = 'CONSULTA'
  AND catalog.is_active
  AND secondary.is_active
ORDER BY catalog.specific_intent, secondary.secondary_intent;

-- A FK deve rejeitar uma intencao secundaria sem intencao especifica valida.
DO $$
BEGIN
    BEGIN
        INSERT INTO public.secondary_intents (
            specific_intent_id,
            secondary_intent,
            description,
            rag_instruction,
            display_message
        ) VALUES (
            '00000000-0000-0000-0000-000000000000'::uuid,
            'sugerir_teste_orfao',
            'Registro invalido para testar a chave estrangeira.',
            'Instrucao de teste que nunca deve ser persistida.',
            'Mensagem de teste que nunca deve ser persistida.'
        );
        RAISE EXCEPTION 'A chave estrangeira aceitou uma associacao orfa.';
    EXCEPTION
        WHEN foreign_key_violation THEN
            NULL;
    END;
END;
$$;

-- A unicidade deve rejeitar a mesma associacao duas vezes.
DO $$
DECLARE
    existing public.secondary_intents%ROWTYPE;
BEGIN
    SELECT * INTO existing
    FROM public.secondary_intents
    ORDER BY created_at, id
    LIMIT 1;

    BEGIN
        INSERT INTO public.secondary_intents (
            specific_intent_id,
            secondary_intent,
            description,
            rag_instruction,
            display_message
        ) VALUES (
            existing.specific_intent_id,
            existing.secondary_intent,
            existing.description,
            existing.rag_instruction,
            existing.display_message
        );
        RAISE EXCEPTION 'A restricao de unicidade aceitou uma associacao duplicada.';
    EXCEPTION
        WHEN unique_violation THEN
            NULL;
    END;
END;
$$;

ROLLBACK;
