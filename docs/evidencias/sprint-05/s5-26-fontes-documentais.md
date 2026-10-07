# S5-26 — Registrar as fontes das respostas documentais (#280)

A correção impede que fontes locais usadas pelo RAG desapareçam de `consulted_sources`. O registro mantém a identidade da fonte, sua origem, evidência, ordem de citação e vínculo com a interação, mesmo quando a fonte não possui artefato, extrato ou projeto cadastrados no banco.

## Diagnóstico do D-04

Os relatórios [S4-11](../../testes/sprint4/relatorio-s4-11.md#81-d-04--resposta-documental-sem-fonte-citada) e [S4-33](../../testes/sprint4/relatorio-s4-33.md#d-01-e-d-04--já-registrados) documentam 6 e 16 ocorrências, respectivamente. A inspeção do código identifica um caminho reproduzível: `SharePointDocument.fallback` é verdadeiro para documentos locais; `generate_chat_response` e a resposta proativa preparada incluem esses documentos em `trace_sources`; `_insert_consulted_sources` os descartava antes do INSERT. A contagem `persistent_source_count` aplicava o mesmo filtro.

O schema de `consulted_sources` permite `artifact_id`, `extract_id` e `project_id` nulos. Portanto, a ausência desses vínculos não impede registrar a fonte realmente consultada. Não se criam IDs fictícios nem fontes para respostas sem contexto.

A inspeção dos relatórios e a reprodução local não permitem afirmar que todas as 16 ocorrências históricas têm essa mesma causa. Não foi executada consulta ao Supabase: o ambiente local não possui configuração de banco. Os registros históricos não foram alterados e os testes S4 que verificam o histórico completo continuam preservados.

## Entrega e critérios observáveis

- Toda entrada em `trace_sources` é inserida na mesma transação da interação, incluindo fontes locais e conjuntos mistos.
- A auditoria informa a quantidade efetivamente encaminhada à persistência, incluindo fontes locais.
- Os registros preservam título, URL, localizador, ordem, origem e metadados de evidência; os vínculos de banco existentes permanecem intactos.
- Chat e áudio atravessam geração, validação de evidência, API e persistência nos testes com Gemini e OpenRouter simulados.
- RAG com classificador desligado ou com baixa confiança e confirmação proativa aceita também registram a fonte local. A recusa não produz resposta documental.
- Limitação sem fonte e erro não inventam registros em `consulted_sources`. Uma falha de escrita de fonte provoca rollback da transação inteira.
- A CI inclui `test_documental_sources.py` no job `backend-api`.

## Evidência de regressão

Execução em 06/10/2026, com Python 3.13 e o ambiente virtual do projeto. Provedores e banco são simulados; a geração e validação da resposta, o pipeline da API e o código que executa os INSERTs são reais.

Antes da correção, o comando abaixo produziu **4 falhas e 4 aprovações**. As quatro falhas foram `StopIteration` ao procurar um INSERT de fonte local inexistente: chat/áudio × Gemini/OpenRouter. Após a correção, os oito cenários passaram.

```powershell
# A partir de src/backend, usando o Python do ambiente virtual:
python -m pytest app/tests/test_response_references.py -k references_survive -q --tb=short -p no:cacheprovider
```

A validação focada de referências, rastreabilidade e proatividade produziu **85 aprovações**. A suíte adicional `test_documental_sources.py` produziu **11 aprovações**.

```powershell
python -m pytest app/tests/test_response_references.py app/tests/test_traceability.py app/tests/test_rag_proactivity.py -q --tb=short -p no:cacheprovider
python -m pytest app/tests/test_documental_sources.py -q --tb=short -p no:cacheprovider
```

## Validação ampliada e limitações

A lista de 19 módulos do job `backend-api`, incluindo a nova regressão, foi executada localmente: **417 aprovados, 6 ignorados, 1 falha e 1 erro**, em 146,08 segundos. O [JUnit sanitizado](../../../src/backend/evidencias/issue-280/backend-junit.xml) preserva os resultados de cada caso; detalhes internos do computador foram removidos.

- A falha em `test_sensitive_data_rnf01.py::test_auditoria_registra_bloqueio_sem_expor_o_dado` é preexistente: o teste desempacota seis valores, mas o INSERT de auditoria já possui sete em `develop`, incluindo `correlation_id`. Executar esse caso com o módulo de rastreabilidade original obtido de `origin/develop` reproduziu a mesma falha. Não se alterou esse teste nesta issue.
- O erro em `test_rnf01_rnf03_s4_33.py::test_ct_rnf01_n_marcador_sensivel_nao_chega_ao_provedor` foi uma restrição de acesso à pasta temporária do Windows. Reexecutado com acesso à pasta temporária isolada `.runtime/pytest-280-recheck-02`, **passou** em 0,35 segundo.
- Os seis casos ignorados dependem de um banco real configurado. Não houve verificação no Supabase nem publicação em ambiente de execução.
- A suíte ampliada não está integralmente verde por causa da falha preexistente acima. Os **96 casos** de referências, rastreabilidade, proatividade e regressão documental passaram também nessa execução ampliada.

Para reproduzir a execução ampliada, copie a lista de módulos do comando `python -m pytest` do job `backend-api` em `.gitlab-ci.yml`. Nesta execução, foram usados `--tb=short -p no:cacheprovider -o junit_family=legacy --junitxml=evidencias/issue-280/backend-junit.xml` além de `-q`.

## Verificação após publicação

Depois de publicar a correção, execute consultas documentais por chat, áudio e confirmação proativa. Consulte as interações novas por `trace_id` e compare as fontes retornadas com `consulted_sources` e o evento `database_rag_sources_retrieved`. Fontes locais podem ter FKs nulas, mas devem manter sua identidade nos demais campos. O valor `persistent_source_count` deve corresponder à contagem gravada.

A consulta abaixo deve retornar zero linhas para as respostas documentais novas concluídas sem limitação. Substitua o parâmetro pela data/hora real da publicação; não use o histórico inteiro para validar esta correção prospectiva.

```sql
SELECT i.id, i.route_taken, i.created_at
FROM public.ai_interactions i
WHERE i.created_at >= :inicio_validacao
  AND i.route_taken IN ('sharepoint_query', 'analise_local')
  AND i.processing_status = 'processado'
  AND i.limitation_response IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM public.consulted_sources s WHERE s.interaction_id = i.id
  );
```

A execução em ambiente real e a aprovação com comentário de @felipe.teixeira permanecem pendentes. Esta evidência comprova a regressão local; não comprova publicação ou aprovação do RNF03 completo.
