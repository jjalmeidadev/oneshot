# Referências nas respostas — evidências e critérios de aceite

Atualizado em 25/09/2026. Contrato: `1.1.0`.

## Resultado final

| Validação | Resultado |
| --- | --- |
| Backend ampliado, incluindo avaliação do corpus de PLN | **287 aprovados**, zero falhas/erros/ignorados, 41,16 s — [saída](backend-tests.txt) |
| Backend focado nas camadas afetadas, incluindo os testes com classificador real | **262 aprovados**, zero falhas/erros/ignorados, 4,15 s — [saída](backend-final.txt), [JUnit](backend-junit.xml) |
| Frontend: domínio, fontes, componentes e estado do chat | **33 aprovados**, 4 arquivos — [saída](frontend-tests.txt) |
| TypeScript (`tsc --noEmit`) | Código de saída 0 |
| ESLint dos arquivos frontend afetados | Código de saída 0, sem avisos |

A rodada focada não repete a avaliação completa do corpus em
`test_nlp_inference.py`, incluída na rodada ampliada.

## Matriz de aceite

| Requisito | Implementação e comprovação |
| --- | --- |
| Artefato, trecho e IDs disponíveis | `GeminiSource`, referências completas em `answer.sources` e `chat.sources`; `test_references_survive_provider_api_and_audit` |
| Atualização e período de registro quando disponíveis | `last_modified` da origem, `registration_period` distinto de `validity`; testes de metadados completos/ausentes; painel de fontes da interface, com períodos na data local |
| Cada informação factual associada à fonte que a sustenta | `claims[].evidence` contém a unidade integral; a validação extrativa rejeita número alterado, negação invertida, condição omitida e empréstimo de evidência de outra fonte, e aceita apenas variações de apresentação (`test_presentation_variants_of_a_complete_copy_are_accepted`) |
| Resposta sem evidência suficiente | `evidence_status=insufficient`, sem claims; fontes recuperadas preservadas e sinalizadas na interface como sem evidência para a resposta; sem recuperação, não chama o LLM mesmo com classificador desligado |
| Sugestão proativa sustentada por evidência | Resposta secundária com evidências verificadas e uma linha `Sugestão:` sem números ou datas, exposta em `recommendation`; sugestão sem evidência, com número novo ou com evidência parafraseada não é oferecida (`test_unsupported_secondary_response_is_not_offered`) |
| Cenários positivo e de falha automatizados | Texto/áudio × Gemini/OpenRouter; citações inexistentes, fatos inventados com citação existente e falha de recuperação |
| Evidência correlacionada entre camadas | Recuperação → provedor → API → persistência de interação/fontes/eventos e commit; `trace_id` comum e snapshot de claims, sugestão e fontes |
| Contrato e exemplos atualizados | [Contrato](../../../contrato-referencias.md), Seções 8.7.5 e 8.11.9 do `Projeto.md`, schemas OpenAPI, tipos/adaptadores frontend e exemplos de sucesso/limitação |
| Independência do modelo generativo | Validação e metadados montados após adaptação comum; testes com ambos os provedores; confirmação proativa revalida a fonte armazenada |
| Texto e áudio compatíveis e versionados | `contract_version=1.1.0`; equivalência de campos testada nas duas rotas |
| Rota de status e fonte do projeto correto | Roteamento `consulta_status_projeto`; código de projeto explícito filtra antes do limite SQL, com verificação adicional; nome do léxico só filtra quando corresponde a projeto cadastrado; sufixo de código composto (`POP-MVP-001`) não é tratado como projeto; testes de outro projeto, projeto ausente, nome fora do cadastro e código composto |
| Interface preserva rastreabilidade | Adaptador conserva claims, IDs, período e trace; extratos do mesmo artefato possuem seleção distinta; testes de domínio e componentes |

A fidelidade à fonte é verificável por igualdade de conteúdo; a veracidade dos
dados da própria fonte depende da curadoria.

## Reprodução

Backend: instalar `requirements.txt` e `requirements-pln.txt`. Para os testes
do classificador real, usar o BERTimbau na revisão imutável
`94d69c95f98f7d5b2a8700c420230ae10def0baa`. A execução local utilizou cache
existente, `HF_HUB_OFFLINE=1`, `OMP_NUM_THREADS=2` e `MKL_NUM_THREADS=2`, sem
`DATABASE_URL`.

```sh
cd src/backend
python -m pytest app/tests/test_response_references.py app/tests/test_database_rag.py app/tests/test_nlp_entities.py app/tests/test_gemini_client.py app/tests/test_rag_proactivity.py app/tests/test_pipeline_api.py app/tests/test_traceability.py app/tests/test_sharepoint_rag.py app/tests/test_llm_provider.py app/tests/test_audio_upload.py app/tests/test_rag_atributos_no_prompt.py app/tests/test_alerts.py -q -p no:warnings --junitxml=../../docs/evidencias/sprint-04/referencias-respostas/backend-junit.xml
```

Para reproduzir a rodada ampliada, incluir também `app/tests/test_nlp_inference.py`.

Frontend, a partir de `src/frontend`:

```sh
node node_modules/vitest/vitest.mjs run src/lib/domain.test.ts src/components/documents/references.test.tsx src/components/components.test.tsx src/state/chat-store.test.tsx --maxWorkers=1 --pool=forks
node node_modules/typescript/bin/tsc --noEmit
node node_modules/eslint/bin/eslint.js src/lib/domain.ts src/lib/domain.test.ts src/lib/format.ts src/lib/api/schemas.ts src/components/documents/document-viewer.tsx src/components/documents/response-details.tsx src/components/documents/references.test.tsx src/components/chat/source-citations.tsx src/components/chat/message-bubble.tsx --max-warnings=0
```

## Escopo da evidência

Os testes de contrato usam massa sintética e simulam o transporte do LLM,
o STT e a conexão do banco; executam as rotas, a adaptação, a validação e a
persistência reais do código. Os testes específicos do PLN executam o
classificador real. Não houve escrita de dados de teste no Supabase nem
chamada ao LLM ou ao STT.
