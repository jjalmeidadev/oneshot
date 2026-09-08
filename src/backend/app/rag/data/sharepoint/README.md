# Listas simuladas do SharePoint

Este diretorio contem dados inteiramente ficticios para o MVP. Os arquivos JSON
representam snapshots normalizados de listas obtidas pelo Microsoft Graph, com
metadados da lista, IDs de itens, campos, datas de alteracao e URLs simuladas.

Listas disponiveis:

- `procedimentos_operacionais.json`: procedimentos de atendimento e operacao;
- `comunicados_servico.json`: avisos temporarios de servico;
- `base_atendimento.json`: perguntas e regras comuns de atendimento.

O backend pesquisa esses arquivos localmente, injeta ate tres itens relevantes
no prompt do Gemini e devolve `sources` e `retrieval_ms` em `/api/chat`.
Consultas sem correspondencia continuam como perguntas gerais ao modelo.

Configuracao opcional:

- `RAG_MAX_SOURCES`: quantidade maxima de itens recuperados, de 1 a 8;
- `SHAREPOINT_MOCK_DATA_DIR`: diretorio alternativo contendo exports JSON.

Na integracao real, o adaptador do Microsoft Graph pode persistir snapshots com
o mesmo contrato. O campo `mock` deve permanecer `true` nestes arquivos, e os
dados nunca devem ser tratados como orientacao operacional oficial.
