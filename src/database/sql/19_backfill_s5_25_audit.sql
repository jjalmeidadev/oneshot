-- S5-25 / #279: repara os registros anteriores a correcao do backend.
-- Idempotente; executar apos publicar o backend corrigido.
BEGIN;

INSERT INTO public.out_of_scope_requests (
    interaction_id, user_prompt, predicted_macro_intent,
    predicted_specific_intent, confidence, reason
)
SELECT i.id, i.user_prompt, i.macro_intent_predicted,
       i.specific_intent_predicted,
       CASE
           WHEN i.macro_intent_predicted = 'FORA_DE_ESCOPO'
               THEN i.macro_intent_confidence
           WHEN i.specific_intent_predicted IS NULL
               THEN i.specific_intent_confidence
           ELSE i.macro_intent_confidence
       END,
       'retroativo_s5_25'
FROM public.ai_interactions i
WHERE (i.route_taken = 'fora_escopo'
       OR i.processing_status = 'fora_escopo'
       OR i.macro_intent_predicted = 'FORA_DE_ESCOPO')
  AND NOT EXISTS (
      SELECT 1 FROM public.out_of_scope_requests o
      WHERE o.interaction_id = i.id
  );

UPDATE public.audit_events e
SET correlation_id = COALESCE(
    (SELECT MIN(existing.correlation_id)
     FROM public.audit_events existing
     WHERE existing.interaction_id = e.interaction_id
       AND existing.correlation_id IS NOT NULL),
    e.interaction_id::text
)
WHERE e.interaction_id IS NOT NULL
  AND e.correlation_id IS NULL;

COMMIT;
