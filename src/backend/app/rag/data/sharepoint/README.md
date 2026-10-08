# Listas simuladas do SharePoint

Este diretorio contem dados inteiramente ficticios para o MVP. Os arquivos JSON
representam snapshots normalizados de listas obtidas pelo Microsoft Graph, com
metadados da lista, IDs de itens, campos, datas de alteracao e URLs simuladas.

Listas disponiveis:

- `procedimentos_operacionais.json`: procedimentos de atendimento e operacao;
- `comunicados_servico.json`: avisos temporarios de servico;
- `base_atendimento.json`: perguntas e regras comuns de atendimento;
- `documentos_projetos.json`: status sintetico dos projetos `PRJ-0510` e
  `PRJ-0587`.

O item `201` de `comunicados_servico.json` representa o `PRJ-0442`. Com os dois
itens de `documentos_projetos.json`, os 11 documentos da massa cobrem os tres
projetos do portfolio sintetico.

## Contrato estrutural local

Este contrato foi adotado como referencia substituta porque o material
estrutural externo do Metro nao esta versionado no repositorio. Ele nao
representa integracao nem homologacao com um SharePoint real.

| JSON simulado | Banco | Uso |
|---|---|---|
| `site.id`, `site.displayName` | `project_artifacts.metadata.site` | identifica o site ficticio |
| `list.id`, `list.displayName` | `sharepoint_library` e `metadata.list` | identifica a lista ou biblioteca simulada |
| `value[].id` | `sharepoint_item_id` | identificador estavel do item |
| `value[].project_code` e `fields.CodigoProjeto` | `projects.code` -> `project_id` | vincula o documento ao projeto |
| `fields.Title` e `fields.Conteudo` | `project_artifacts` e `source_extracts` | titulo e trecho recuperavel |
| `webUrl`, `lastModifiedDateTime` | URL, data de extracao e metadados | rastreabilidade da fonte simulada |

O identificador de origem persistido e
`sharepoint-mock:<list.id>:<value[].id>`. A reaplicacao atualiza o artefato e o
extrato correspondentes e insere somente itens ainda ausentes.

O backend pesquisa esses arquivos localmente, injeta ate tres itens relevantes
no prompt do Gemini e devolve `sources` e `retrieval_ms` em `/api/chat`.
Consultas sem correspondencia continuam como perguntas gerais ao modelo.

Configuracao opcional:

- `RAG_MAX_SOURCES`: quantidade maxima de itens recuperados, de 1 a 8;
- `SHAREPOINT_MOCK_DATA_DIR`: diretorio alternativo contendo exports JSON.

Na integracao real, o adaptador do Microsoft Graph pode persistir snapshots com
o mesmo contrato. O campo `mock` deve permanecer `true` nestes arquivos, e os
dados nunca devem ser tratados como orientacao operacional oficial.

## Carga e validacao

Na pasta `src/backend`, configure `DATABASE_URL` ou
`SUPABASE_DATABASE_URL` e execute:

```powershell
.\.venv\Scripts\python.exe -m scripts.reindex_sharepoint_mock apply
.\.venv\Scripts\python.exe -m scripts.reindex_sharepoint_mock status
```

`apply` reaplica a carga SQL e valida o estado final. `status` nao altera dados:
confere se `PRJ-0442`, `PRJ-0510` e `PRJ-0587` possuem ao menos um artefato e
um extrato e se nao ha grupos duplicados por artefato/localizador. Sucesso
produz JSON com `valid: true`; ausencia ou duplicacao termina com erro.
