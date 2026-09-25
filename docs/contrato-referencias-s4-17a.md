# S4-17A — Referências na resposta

Atualizado em: 25/09/2026.

## Contrato

`POST /api/chat`, `POST /api/audio` e a confirmação de sugestão proativa
preservam as referências montadas pelo backend a partir dos documentos
recuperados. A escolha entre Gemini e OpenRouter não altera esse contrato.
Os schemas vigentes são `app/gemini/schemas.py`, `app/audio/schemas.py` e seu
espelho em `src/frontend/src/lib/api/schemas.ts`.

| Campo | Significado/origem |
| --- | --- |
| `contract_version` | `1.1.0`, comum às respostas de texto e áudio |
| `sources[].id` | Identificador externo da fonte; não necessariamente único por extrato |
| `citation_id` | `Fonte N`, único na resposta; acompanha a ordem do contexto enviado ao modelo |
| `title`, `list_name`, `web_url` | Artefato, biblioteca/lista e URL de origem |
| `artifact_id`, `extract_id`, `project_id` | IDs persistidos, ou `null` quando indisponíveis |
| `excerpt` | Trecho recuperado de `source_extracts.content_text` ou do JSON local |
| `source_locator` | Localizador do trecho (seção, planilha/célula etc.), quando disponível |
| `last_modified` | Atualização declarada pela origem (`lastModifiedDateTime`); `""` quando ausente, por compatibilidade |
| `registration_period` | `{start, end}` de `source_extracts.metadata.registration_period` ou `item.registration_period` no JSON local; `null` quando ausente |
| `validity` | Vigência, separada do período de registro; metadata `validity` ou campos `ValidadeInicio`/`ValidadeFim` |
| `attributes` | Atributos estruturados também fornecidos ao modelo, como status e vigência |
| `claims[]` | Afirmações retornadas, cada uma com `text` e `citation_ids` que apontam para `sources` |
| `claims[].evidence[]` | Suporte verificável: `citation_id`, `field` (`excerpt` ou `attribute`), nome do atributo quando aplicável e `quote` integral |
| `evidence_status` | `referenced`, `insufficient` ou `not_applicable` (roteamento de workflow) |
| `trace_id` | ID de `ai_interactions`, usado em `consulted_sources` e `audit_events`; `null` sem persistência disponível |
| `interaction_id` | ID do provedor, mantido para continuidade da conversa; não substitui `trace_id` |

Datas/períodos não são inferidos pelo modelo. Data de extração/ingestão não é
tratada como atualização da fonte. Extremos de períodos podem ser `null`.
O esquema atual não possui coluna própria de período de registro; esse dado
deve ser informado na metadata indicada, sem inventar um período a partir da
vigência. Nenhuma migração é necessária: a auditoria usa JSONB existente.

No áudio, `answer.sources` contém os mesmos campos de `chat.sources`, além dos
aliases legados `artifact=title` e `section=source_locator` (ou `list_name`
quando não há localizador). `answer.claims`, `answer.evidence_status` e
`trace_id` correspondem aos valores de `chat`.

O frontend conserva esses campos no histórico da conversa e mostra IDs,
localizador, atualização, período de registro, vigência e atributos no painel
da fonte. O ID interno de seleção usa o extrato quando disponível, para não
confundir dois extratos do mesmo artefato. O identificador externo continua
visível. O painel de detalhes exibe `trace_id` para localizar a auditoria.

## Exemplo sintético

Trecho relevante de uma resposta HTTP 200:

```json
{
  "contract_version": "1.1.0",
  "text": "O prazo e 30/09/2026. [Fonte 1]",
  "interaction_id": "provider-17",
  "trace_id": "trace-17",
  "evidence_status": "referenced",
  "claims": [{
    "text": "O prazo e 30/09/2026.",
    "citation_ids": ["Fonte 1"],
    "evidence": [{
      "citation_id": "Fonte 1", "field": "excerpt", "attribute": null,
      "quote": "O prazo e 30/09/2026."
    }]
  }],
  "sources": [{
    "id": "lista:17",
    "citation_id": "Fonte 1",
    "title": "Prazo sintetico",
    "list_name": "Projetos",
    "web_url": "https://example.test/17",
    "artifact_id": "artifact-17",
    "extract_id": "extract-17",
    "project_id": "project-17",
    "source_locator": "Planilha!B17",
    "excerpt": "O prazo e 30/09/2026.",
    "last_modified": "2026-09-24T12:00:00Z",
    "registration_period": {"start": "2026-09-01", "end": "2026-09-24"},
    "validity": {"start": "2026-09-01", "end": "2026-09-30"},
    "attributes": {"Vigencia": "de 2026-09-01 a 2026-09-30"},
    "score": 4.0
  }]
}
```

IDs simplificados no exemplo e nos testes; IDs do banco real são UUIDs.

## Evidência insuficiente e validação

Foi adotado o modo estrito solicitado: o modelo seleciona conteúdo, mas cada
afirmação precisa copiar integralmente o trecho recuperado ou um atributo
completo (`Rótulo: valor`). O backend verifica igualdade, normalizando apenas
espaços de apresentação. Não aceita recortes que omitam condições, negações,
trocas de números ou paráfrases. A evidência integral usada é retornada em
`claims[].evidence` e registrada na auditoria.

O prompt pede uma unidade completa por linha, com citações `[Fonte N]` no
final. Cada fonte citada precisa sustentar aquela unidade. Citar uma fonte
existente não autoriza acrescentar fatos. O schema também rejeita evidências
adulteradas, referências inexistentes e texto fora das afirmações verificadas.
Nesse caso, retorna HTTP 200 com:

```json
{
  "text": "Nao ha evidencia recuperada suficiente para responder com rastreabilidade.",
  "evidence_status": "insufficient",
  "claims": []
}
```

As fontes recuperadas permanecem em `sources` para inspeção; sua presença não
significa que sustentaram uma resposta aceita. Sem resultados, inclusive com
o classificador desligado, não chama o LLM e preserva a mensagem RF08 existente, com `sources=[]` e
`evidence_status=insufficient`. Falhas de banco/provedor continuam usando os
erros HTTP existentes. Sugestões secundárias sem referências válidas não são
oferecidas; respostas já preparadas são revalidadas na confirmação.

A garantia é de fidelidade ao conteúdo da origem, não de veracidade absoluta
da própria origem. Paráfrases, sínteses e recomendações não documentadas
produzem abstenção conservadora, mesmo se plausíveis. `score` é relevância de
recuperação, não um grau de certeza factual. Isso não depende de um segundo
modelo generativo nem de uma avaliação probabilística de similaridade.

Quando a pergunta identifica um projeto, o recuperador filtra por código,
título ou ID correspondente. O filtro SQL ocorre antes do limite de resultados
e há verificação adicional no backend; fontes de outros projetos não são
aceitas por coincidência de palavras. Código explícito também funciona com
o classificador desligado. Fontes locais sem associação de projeto não são
usadas para responder sobre um projeto identificado. No JSON local, essa
associação usa `project_id`, `project_code` e `project_title` no item.

Os envelopes de erro existentes foram preservados: falha de recuperação
retorna HTTP 503 no texto e HTTP 502 com envelope de áudio; dados internos
não são expostos. Ausência/insuficiência de evidência é HTTP 200 controlado.

## Evidência entre camadas

`test_response_references.py` usa uma linha sintética do banco, conversão RAG
real, adaptadores HTTP reais de ambos os provedores (transporte simulado),
rotas reais de texto/áudio e a função completa de persistência (interação,
fontes, eventos e commit) com conexão controlada.
STT, classificador e conexão externa são substituídos por dados controlados.
Verifica IDs, trecho, datas, períodos, claims e correlação por `trace_id`.

`consulted_sources.metadata` conserva trecho, data, períodos, `citation_id`,
atributos e claims associados àquela fonte. O evento
`database_rag_sources_retrieved` conserva o snapshot público e o ID do provedor,
inclusive no fallback local, cujos IDs não são inseridos como FKs no banco.
Uma falha de auditoria mantém o comportamento existente: aviso no log e
`trace_id=null`, sem simular persistência bem-sucedida.

Executar a partir de `src/backend`:

```sh
python -m pytest app/tests/test_response_references.py app/tests/test_database_rag.py app/tests/test_gemini_client.py app/tests/test_rag_proactivity.py app/tests/test_pipeline_api.py app/tests/test_traceability.py app/tests/test_sharepoint_rag.py app/tests/test_llm_provider.py -q
```

As dependências técnicas estão identificadas em `docs/GestaoProjeto.md`:
S4-14A exige contrato compatível e versionado entre texto/áudio; S4-16 exige
roteamento de `consulta_status_projeto`, recuperação sintética e fontes
associadas ao projeto. Esses comportamentos são verificados pelos testes de
pipeline, referências e recuperação. Isso não representa alteração nem
confirmação do estado administrativo dessas issues no rastreador externo.

A task aceita teste automatizado **ou** execução ponta a ponta. A comprovação
usada aqui é a suíte automatizada entre camadas, com classificação real em
testes próprios e serviços externos controlados nos testes de contrato.
Homologação de credenciais, disponibilidade de Supabase/SharePoint/STT/LLM
reais e o E2E operacional completo pertencem a validações adicionais (S4-20).

## Evidência de execução e aceite

Resultados e matriz de aceite: [S4-17A](evidencias/sprint-04/s4-17a/README.md).
Os três testes anteriormente bloqueados por ausência de `torch` passaram
após instalar `requirements-pln.txt` e usar o snapshot imutável do BERTimbau.
A CI inclui os testes de referências e publica o relatório JUnit.
