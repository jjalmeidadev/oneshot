# Referências nas respostas

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
| `recommendation` | Somente na resposta secundária confirmada: ação sugerida, rotulada como análise e não como fato; `null` nos demais casos |
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
da fonte; períodos sem horário são exibidos na data local. O ID interno de
seleção usa o extrato quando disponível, para não confundir dois extratos do
mesmo artefato, e o identificador externo continua visível. O painel de
detalhes exibe `trace_id` para localizar a auditoria. Quando a resposta é
`insufficient`, as fontes recuperadas continuam clicáveis sob o rótulo
"Fontes consultadas, sem evidência para esta resposta".

## Exemplo sintético

Trecho relevante de uma resposta HTTP 200:

```json
{
  "contract_version": "1.1.0",
  "text": "O prazo e 30/09/2026. [Fonte 1]",
  "interaction_id": "provider-17",
  "trace_id": "trace-17",
  "evidence_status": "referenced",
  "recommendation": null,
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

## Validação extrativa e evidência insuficiente

O modelo seleciona conteúdo, mas cada afirmação precisa reproduzir
integralmente o trecho recuperado ou um atributo completo (`Rótulo: valor`),
em uma linha terminada pelas citações. O backend compara a linha com as
unidades das fontes citadas sem usar outro modelo. A comparação desconsidera
apenas diferenças de apresentação; qualquer diferença de conteúdo leva à
abstenção.

| Variação na saída do modelo | Resultado |
| --- | --- |
| Espaços, acentos acrescentados, ponto final omitido antes da citação | Aceita |
| Marcador de lista (`-`, `*`, `1.`) e negrito (`**`) | Aceita |
| Citação `[Fonte N]`, `(Fonte N)`, `[Fonte 1, Fonte 2]` ou `[Fontes 1 e 2]` | Aceita; cada fonte citada precisa sustentar a linha |
| Cabeçalho sem citação terminado em `:` (por exemplo, "Segundo o cronograma:") | Descartado, sem afetar as demais linhas |
| Paráfrase, frase recortada do trecho, número alterado, negação invertida | Abstenção |
| Fato acrescentado a uma citação válida ou linha factual sem citação | Abstenção |
| Evidência tomada de outra fonte que não a citada | Abstenção |

O texto público é sempre remontado a partir das afirmações verificadas, no
formato canônico `[Fonte N]`, e a evidência integral usada é retornada em
`claims[].evidence` e registrada na auditoria. O schema também rejeita
evidências adulteradas, referências inexistentes e texto fora das afirmações
verificadas. Na abstenção, a resposta é HTTP 200 com:

```json
{
  "text": "Não há evidência recuperada suficiente para responder com rastreabilidade.",
  "evidence_status": "insufficient",
  "claims": []
}
```

Quando o provedor encerra a geração pelo limite de tokens, a última linha
fica incompleta e não pode ser verificada. Nesse caso, a resposta também volta
como `insufficient`, mas o texto é o aviso de interrupção ("A resposta foi
interrompida antes de terminar. Pergunte de novo, de forma mais específica."),
que orienta o usuário a reformular a pergunta.

As fontes recuperadas permanecem em `sources` para inspeção; sua presença não
significa que sustentaram uma resposta aceita. Sem resultados de recuperação,
inclusive com o classificador desligado, o LLM não é chamado e a mensagem de
fora de escopo existente é preservada, com `sources=[]` e
`evidence_status=insufficient`. Falhas de banco/provedor continuam usando os
erros HTTP existentes.

A garantia é de fidelidade ao conteúdo da origem, não de veracidade absoluta
da própria origem. `score` é relevância de recuperação, não um grau de certeza
factual.

## Sugestão proativa

A resposta secundária da proatividade (RF09) é análise, não cópia de fonte, e
por isso segue uma regra própria. Ela é composta por:

1. linhas de evidência copiadas das fontes, validadas pela mesma regra
   extrativa da resposta principal;
2. uma única linha iniciada por `Sugestão:` com a ação recomendada.

A sugestão só é oferecida quando há ao menos uma evidência verificada, e a
linha de sugestão não pode conter números, datas nem citações a fontes
inexistentes. Assim, uma recomendação não introduz prazo, valor ou percentual
que não esteja nas evidências exibidas acima dela. Quando a resposta secundária
não cumpre essas condições, a sugestão não é oferecida e somente a resposta
principal é devolvida. A resposta preparada é revalidada na confirmação, e o
resultado expõe a ação em `recommendation`, além de a incluir ao final de
`text`:

```json
{
  "text": "O fornecedor do equipamento critico registra atraso de 18 dias. [Fonte 1]\nSugestão: Acompanhar semanalmente o plano de recuperação do fornecedor.",
  "evidence_status": "referenced",
  "recommendation": "Acompanhar semanalmente o plano de recuperação do fornecedor."
}
```

A linha `Sugestão:` é aceita somente na resposta secundária. Na resposta
principal, ela é tratada como afirmação sem fonte e leva à abstenção.

## Escopo de projeto

Quando a pergunta cita um código de projeto (`ABC-123`, como `PRJ-0442`), o
recuperador restringe as fontes a esse projeto. O filtro SQL ocorre antes do
limite de resultados e há verificação adicional no backend. Código de projeto
inexistente resulta em abstenção, nunca em fonte de outro projeto. O código é
reconhecido também com o classificador desligado. Não é tratado como projeto o
sufixo de um código composto, como `POP-MVP-001`, que identifica um
procedimento.

Nomes reconhecidos pelo léxico do NER (linhas, estações e programas, como
"Linha 2-Verde") só restringem as fontes quando correspondem ao código ou ao
título de um projeto cadastrado. Caso contrário, continuam apenas pontuando a
busca, como antes do filtro. No JSON local, que não possui cadastro de
projetos, a associação usa `project_id`, `project_code` e `project_title` do
item, e fontes sem essa associação não respondem sobre um código de projeto.

## Evidência entre camadas

`test_response_references.py` usa uma linha sintética do banco, conversão RAG
real, adaptadores HTTP reais de ambos os provedores (transporte simulado),
rotas reais de texto/áudio e a função completa de persistência (interação,
fontes, eventos e commit) com conexão controlada. STT, classificador e conexão
externa são substituídos por dados controlados. Verifica IDs, trecho, datas,
períodos, claims e correlação por `trace_id`, além das variações da tabela de
validação.

`consulted_sources.metadata` conserva trecho, data, períodos, `citation_id`,
atributos e claims associados àquela fonte. O evento
`database_rag_sources_retrieved` conserva o snapshot público, a sugestão e o
ID do provedor, inclusive no fallback local, cujos IDs não são inseridos como
FKs no banco. Uma falha de auditoria mantém o comportamento existente: aviso
no log e `trace_id=null`, sem simular persistência bem-sucedida.

Os envelopes de erro existentes foram preservados: falha de recuperação
retorna HTTP 503 no texto e HTTP 502 com envelope de áudio; dados internos não
são expostos. Ausência/insuficiência de evidência é HTTP 200 controlado.

Executar a partir de `src/backend`:

```sh
python -m pytest app/tests/test_response_references.py app/tests/test_database_rag.py app/tests/test_nlp_entities.py app/tests/test_gemini_client.py app/tests/test_rag_proactivity.py app/tests/test_pipeline_api.py app/tests/test_traceability.py app/tests/test_sharepoint_rag.py app/tests/test_llm_provider.py -q
```

Resultados de execução e matriz de aceite:
[evidências das referências nas respostas](evidencias/sprint-04/referencias-respostas/README.md).
