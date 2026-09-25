# S4-17A — Evidências e critérios de aceite

Atualizado em 25/09/2026. Contrato: `1.1.0`.

## Resultado final

| Validação | Resultado |
| --- | --- |
| Backend ampliado, incluindo avaliação do corpus de PLN | **240 aprovados**, 1 aviso, 546,40 s — [saída](backend-tests.txt) |
| Backend focado nas camadas afetadas, incluindo os três testes com classificador real | **215 aprovados**, zero falhas/erros/ignorados, 39,72 s — [saída](backend-final.txt), [JUnit](backend-junit.xml) |
| Frontend: domínio, fontes, componentes e estado do chat | **32 aprovados**, 4 arquivos, 108,97 s — [saída](frontend-tests.txt) |
| TypeScript (`tsc --noEmit`) | Código de saída 0 |
| ESLint dos seis arquivos frontend afetados | Código de saída 0, sem avisos |
| `git diff --check` | Sem erros |

Os três testes anteriormente pendentes por falta de `torch` passaram com o
classificador real. Nenhum teste foi excluído na rodada final focada. A rodada
ampliada também terminou com sucesso; a focada apenas não repete a avaliação
completa do corpus em `test_nlp_inference.py`. O aviso do backend é uma
depreciação HTTPX/Starlette. O frontend foi executado com um único processo
após um timeout de inicialização de worker na tentativa concorrente.

## Matriz de aceite

| Requisito | Implementação e comprovação |
| --- | --- |
| Artefato, trecho e IDs disponíveis | `GeminiSource`, referências completas em `answer.sources` e `chat.sources`; `test_references_survive_provider_api_and_audit` |
| Atualização e período de registro quando disponíveis | `last_modified` da origem, `registration_period` distinto de `validity`; testes de metadados completos/ausentes; painel de fontes da interface |
| Cada informação factual associada à fonte que a sustenta | `claims[].evidence` contém a unidade integral; validação extrativa rejeita número alterado, negação invertida, condição omitida e empréstimo de evidência de outra fonte |
| Resposta sem evidência suficiente | `evidence_status=insufficient`, sem claims; fontes recuperadas preservadas; sem recuperação, não chama o LLM mesmo com classificador desligado |
| Cenários positivo e de falha automatizados | Texto/áudio × Gemini/OpenRouter; citações inexistentes, fatos inventados com citação existente e falha de recuperação |
| Evidência correlacionada entre camadas | Recuperação → provedor → API → persistência de interação/fontes/eventos e commit; `trace_id` comum e snapshot de claims/fontes |
| Contrato e exemplos atualizados | [Contrato](../../../contrato-referencias-s4-17a.md), schemas OpenAPI, tipos/adaptadores frontend e exemplos de sucesso/limitação |
| Independência do modelo generativo | Validação e metadados montados após adaptação comum; testes com ambos os provedores; confirmação proativa revalida a fonte armazenada |
| S4-14A: texto/áudio compatíveis e versionados | `contract_version=1.1.0`; equivalência de campos testada nas duas rotas |
| S4-16: rota de status e fonte do projeto correto | Roteamento `consulta_status_projeto`, filtro exato do projeto antes do limite SQL e verificação adicional; testes de outro projeto e projeto ausente |
| Interface preserva rastreabilidade | Adaptador conserva claims, IDs, período e trace; extratos do mesmo artefato possuem seleção distinta; testes de domínio e componentes |

O modo estrito foi escolhido pelo solicitante: aceita cópia integral do trecho
ou atributo estruturado, sem paráfrases livres. A fidelidade à fonte é verificável
por igualdade de conteúdo; a veracidade dos dados da própria fonte depende da
curadoria. Recomendações sem suporte documental também são omitidas.

## Reprodução

Backend: instalar `requirements.txt` e `requirements-pln.txt`. Para os testes
do classificador real, usar o BERTimbau na revisão imutável
`94d69c95f98f7d5b2a8700c420230ae10def0baa`. A execução local utilizou cache
existente, `HF_HUB_OFFLINE=1`, `OMP_NUM_THREADS=2` e `MKL_NUM_THREADS=2`.

```sh
cd src/backend
python -m pytest app/tests/test_response_references.py app/tests/test_database_rag.py app/tests/test_gemini_client.py app/tests/test_rag_proactivity.py app/tests/test_pipeline_api.py app/tests/test_traceability.py app/tests/test_sharepoint_rag.py app/tests/test_llm_provider.py app/tests/test_audio_upload.py app/tests/test_rag_atributos_no_prompt.py app/tests/test_alerts.py -q --tb=short --junitxml=../../docs/evidencias/sprint-04/s4-17a/backend-junit.xml
```

Para reproduzir a rodada ampliada, incluir também `app/tests/test_nlp_inference.py`.

Frontend, a partir de `src/frontend`:

```sh
node node_modules/vitest/vitest.mjs run src/lib/domain.test.ts src/components/documents/references.test.tsx src/components/components.test.tsx src/state/chat-store.test.tsx --maxWorkers=1 --pool=forks
node node_modules/typescript/bin/tsc --noEmit
node node_modules/eslint/bin/eslint.js src/lib/domain.ts src/lib/domain.test.ts src/lib/api/schemas.ts src/components/documents/document-viewer.tsx src/components/documents/response-details.tsx src/components/documents/references.test.tsx --max-warnings=0
```

## Escopo da evidência

Os testes de contrato usam massa sintética e simulam o transporte do LLM,
STT e a conexão do banco; executam as rotas, adaptação, validação e persistência
reais do código. Os testes específicos do PLN executam o classificador real.
Não houve escrita de dados de teste no Supabase nem chamada paga ao LLM/STT.

Os comportamentos técnicos das dependências são comprovados no repositório.
O estado administrativo das issues S4-14A/S4-16 não foi alterado/verificado no
rastreador externo. Homologação operacional com todos os serviços reais não é
apresentada como concluída: o DoD desta task admite testes automatizados entre
camadas, alternativa usada nesta entrega.
