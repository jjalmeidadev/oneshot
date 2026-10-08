# Evidências — respostas estruturadas (#270)

Validação local em 05/10/2026, na branch `feature/270-blocos-resposta`, criada
a partir da `origin/develop` em `28337f4`. Dados, provedores, transcrição e banco
são simulados; nenhum resultado abaixo representa medição em produção.

## Entrega e critérios de aceite

| Critério da issue | Evidência observável |
|---|---|
| Definir os blocos no schema versionado | [JSON Schema 1.2.0](../../contracts/chat-response-1.2.0.schema.json), exportado do modelo da API, com união discriminada `table`, `indicator`, `highlight`. |
| Gerar os blocos a partir dos dados recuperados | `app/gemini/blocks.py` deriva os blocos das afirmações já verificadas; teste `test_each_block_has_data_and_citations` confere células, valor percentual e destaques com `Fonte 1`. |
| Manter compatibilidade com texto | `text` preservado, `blocks` opcional com padrão `[]`; testes `test_legacy_text_response_defaults_to_empty_blocks` e `test_verified_response_can_omit_blocks`. Tipos do frontend aceitam contratos 1.1.0 e 1.2.0. |
| Testes de contrato para cada bloco | Testes de conteúdo, citações adulteradas, formato, união no OpenAPI, schema publicado e integração Gemini/OpenRouter em chat/áudio em `app/tests/test_response_blocks.py`. |

## Verificações executadas

Os comandos Python abaixo foram executados em `src/backend`, usando o ambiente
virtual já existente do repositório.

```shell
python -m pytest app/tests/test_gemini_client.py app/tests/test_llm_provider.py app/tests/test_response_references.py -q -p no:cacheprovider
```

Resultado: **76 passed**. Referências, integração com auditoria e provedores
continuam funcionando após a atualização para o contrato 1.2.0.

```shell
python -m pytest app/tests/test_response_blocks.py app/tests/test_response_references.py app/tests/test_rag_proactivity.py app/tests/test_audio_upload.py app/tests/test_pipeline_api.py app/tests/test_vhs_integration.py -q -p no:cacheprovider
```

Resultado: **206 passed**, em 119,63 segundos. Inclui a nova suíte de blocos,
respostas proativas, áudio, roteamento e cache VHS. Os dois avisos apresentados
são de depreciação das dependências FastAPI/Starlette.

```shell
python -m pytest app/tests/test_response_blocks.py app/tests/test_response_references.py -q -p no:cacheprovider
```

Resultado final da suíte específica: **88 passed**. Conferida a igualdade do
schema publicado com o modelo de produção.

Em `src/frontend`:

```shell
node node_modules/typescript/bin/tsc --noEmit
node node_modules/vitest/vitest.mjs run src/lib/domain.test.ts
node node_modules/eslint/bin/eslint.js src/lib/api/schemas.ts --max-warnings=0
node node_modules/prettier/bin/prettier.cjs --check src/lib/api/schemas.ts
```

Resultados: tipos aprovados; **2 testes de domínio aprovados**; ESLint e
formatação aprovados. O teste do frontend foi reexecutado fora da restrição
de criação de subprocessos após a primeira tentativa retornar `spawn EPERM`.
As dependências locais existentes foram reutilizadas.

`git diff --check`: aprovado.

## Limites e decisão

Os resultados sustentam a entrega do contrato e de sua geração, com paridade
entre texto e áudio e rejeição de blocos sem correspondência nas evidências.
Indicadores são gerados somente para atributos numéricos inequívocos; datas,
IDs e valores condicionais permanecem como texto. Tabelas exigem pelo menos
duas afirmações na geração automática.

Não foram executados testes com provedores ou banco reais, implantação nem
testes visuais ponta a ponta: o escopo desta issue é o contrato e a geração dos
blocos, sem alteração dos componentes de apresentação. A suíte nova também
foi incluída no job `backend-api` da CI; execução remota depende da publicação.
A aprovação com comentário de outro membro permanece para a revisão do MR.


## Integração da autenticação e resolução de conflito

A `develop` em `d54c9ba` acrescentou a autenticação e controle de acesso das
issues #257/#258. O conflito com a #270 ocorreu somente na lista de testes
em `.gitlab-ci.yml`: a resolução mantém `test_response_blocks.py` e os novos
`test_access_security.py` e `test_seed_mvp_access.py`. A instalação CPU do
PyTorch introduzida na develop também foi preservada.

Após a resolução, em `src/backend`:

```shell
python -m pytest app/tests/test_response_blocks.py app/tests/test_response_references.py app/tests/test_access_security.py app/tests/test_pipeline_api.py app/tests/test_audio_upload.py app/tests/test_gemini_client.py -q -p no:cacheprovider
python -m pytest app/tests/test_seed_mvp_access.py -q -p no:cacheprovider
```

Resultados: **220 passed** e **6 passed**, respectivamente. A dependência
`psycopg[binary]`, já declarada pelo projeto e ausente do ambiente local, foi
instalada em um diretório isolado desta branch para a suíte de carga de acesso.
Não houve conexão com banco ou serviço de autenticação reais.

Em `src/frontend`, `tsc --noEmit` e a verificação Prettier de
`src/lib/api/schemas.ts` passaram. `git diff --check` também passou.
O contrato 1.2.0, os blocos de chat/áudio e a passagem do contexto de acesso
foram preservados na integração. O resultado remoto da nova pipeline ainda
não foi verificado neste registro.


## Resolução dos conflitos do MR !128 — 06/10/2026

Integração da `develop` em `9c7b6aa`, preservando os blocos do contrato 1.2.0
junto da proteção de dados sensíveis da #281. Em `client.py`, os imports da
geração de blocos e da proteção foram mantidos. A CI mantém os testes de
blocos, acesso e dados sensíveis, além da instalação CPU do PyTorch.
O schema publicado foi regenerado para acompanhar o campo interno de auditoria
introduzido na develop; esse campo permanece excluído da serialização.

Validação executada em `src/backend`:

```shell
python -m pytest app/tests/test_response_blocks.py app/tests/test_response_references.py app/tests/test_sensitive_data_rnf01.py app/tests/test_access_security.py app/tests/test_seed_mvp_access.py app/tests/test_gemini_client.py app/tests/test_pipeline_api.py app/tests/test_audio_upload.py -q -p no:cacheprovider
```

Resultado: **254 testes aprovados**, com dois avisos de depreciação do
FastAPI/Starlette. Os 35 testes de blocos também passaram isoladamente.
Em `src/frontend`, `npm run build` passou, incluindo a checagem TypeScript,
e Prettier aprovou `src/lib/api/schemas.ts`. As dependências foram instaladas
em diretório próprio desta worktree. `git diff --check` passou.
Não foram executados testes com serviços externos reais nem a suíte visual
ponta a ponta. O resultado da pipeline remota não é afirmado por estes testes locais.
