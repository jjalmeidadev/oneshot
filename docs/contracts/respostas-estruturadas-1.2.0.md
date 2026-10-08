# Respostas estruturadas — contrato 1.2.0

Entrega da [issue #270](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/270).
O contrato acrescenta `blocks` a `POST /api/chat`, à resposta de confirmação
proativa e a `chat.blocks` e `answer.blocks` de `POST /api/audio`.
O [JSON Schema versionado](chat-response-1.2.0.schema.json) é exportado do modelo
Pydantic de produção; o OpenAPI também apresenta a união discriminada por `type`.

## Compatibilidade e rastreabilidade

`text`, `sources`, `claims`, `evidence_status`, `interaction_id` e `trace_id`
mantêm seu significado. Clientes que exibem somente `text` continuam funcionando.
Quando `blocks` é omitido na construção de uma resposta, assume `[]`. Os tipos
do frontend aceitam `1.1.0` e `1.2.0` e mantêm os blocos opcionais para ler
respostas antigas. O backend emite `contract_version: "1.2.0"` nos dois canais.
Esta entrega disponibiliza os dados para apresentação; a renderização visual
dos blocos pelo frontend fica para a tarefa dessa frente.

Os blocos são construídos após a validação extrativa de `claims`. Cada destaque,
indicador ou linha de tabela leva `citation_ids` das afirmações que o originaram.
A validação da resposta rejeita blocos cujo conteúdo ou citações não correspondam
às afirmações verificadas. Não há chamada adicional ao modelo nem fatos extraídos
de fontes que não sustentaram a resposta. Abstenção, interrupção do provedor e
mensagens sem evidências retornam `blocks: []`.

## Tipos e regras de geração

| `type` | Campos | Quando é produzido |
|---|---|---|
| `table` | `columns: string[]`, `rows: {cells: string[], citation_ids: string[]}[]` | Duas ou mais afirmações verificadas; colunas `Informação` e `Valor`. Atributos viram chave/valor; trechos integrais usam `Informação` como chave. |
| `indicator` | `label: string`, `value: number`, `unit: "%" ou null`, `citation_ids: string[]` | Atributo citado cujo valor inteiro seja um número inequívoco, com sinal opcional, até 15 dígitos inteiros e até 2 decimais; percentual opcional. |
| `highlight` | `text: string`, `citation_ids: string[]` | Uma unidade para cada afirmação verificada, preservando o texto integral e suas condições. |

A tabela exige ao menos uma coluna e uma linha, com o mesmo número de células
por linha. Indicadores exigem número finito; destaques exigem texto não vazio.
Campos desconhecidos e citações vazias são recusados nos blocos.

`42,5%` vira `value: 42.5, unit: "%"`; `-2` vira `value: -2, unit: null`.
Datas, identificadores, separadores de milhar ambíguos e valores condicionais,
como `12 dias se aprovado`, continuam no destaque/tabela e não viram indicador.
Isso preserva o contexto e evita tratar um número incidental como uma métrica.

## Exemplo sintético

Para as afirmações verificadas `Avanço: 42,5%` e `Status: Em execução`, ambas
sustentadas pelos atributos da `Fonte 1`, o texto permanece:

```text
Avanço: 42,5% [Fonte 1]
Status: Em execução [Fonte 1]
```

O campo adicional contém:

```json
[
  {
    "type": "table",
    "columns": ["Informação", "Valor"],
    "rows": [
      {"cells": ["Avanço", "42,5%"], "citation_ids": ["Fonte 1"]},
      {"cells": ["Status", "Em execução"], "citation_ids": ["Fonte 1"]}
    ]
  },
  {"type": "highlight", "text": "Avanço: 42,5%", "citation_ids": ["Fonte 1"]},
  {"type": "indicator", "label": "Avanço", "value": 42.5, "unit": "%", "citation_ids": ["Fonte 1"]},
  {"type": "highlight", "text": "Status: Em execução", "citation_ids": ["Fonte 1"]}
]
```

## Como verificar

Em `src/backend`, execute:

```shell
python -m pytest app/tests/test_response_blocks.py app/tests/test_response_references.py -q -p no:cacheprovider
```

Esperado: testes aprovados para os três tipos, rejeição de dados/citações
adulterados, formatos inválidos, respostas textuais sem blocos, abstenção,
OpenAPI e paridade chat/áudio em Gemini e OpenRouter simulados.
O teste `test_published_json_schema_matches_runtime` também impede divergência
entre o contrato publicado e o modelo da API.
