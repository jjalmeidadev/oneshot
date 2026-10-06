# Revisão documental — S5-44 (#298)

**Data:** 06/10/2026 (America/Sao_Paulo). **Revisor:** Quinn, aiox-qa. **Resultado do conteúdo:** aprovado, sem correção documental obrigatória identificada. **Encerramento da issue:** pendente dos critérios externos; este parecer não aprova MR, não homologa arquitetura nem autoriza implantação.

## Escopo e referência

Revisão independente da nova [Seção 6.4 e sumário do Projeto.md](../Projeto.md#64-tabela-de-para-para-o-ecossistema-microsoft-do-metrô), do [registro S5-44](../stories/S5-44.md) e da [evidência técnica](../evidencias/sprint-05/tabela-de-para-microsoft.md). Base Git: `58da95da707e0ed05a4a3e0e676fa1d52250becc`, com alterações documentais locais não commitadas. Nenhum código foi alterado nesta revisão.

SHA-256 do `Projeto.md` examinado: `116b485735649aa08ed83930a00899fdda6329d13ee43318e69b3db39cb0a825`. O identificador registra a versão documental revisada; alterações posteriores exigem conferir novamente o conteúdo afetado.

A ativação utilizou `.codex/skills/aiox-qa/SKILL.md`, `.aiox-core/development/agents/qa.md` e `generate-greeting.js qa`; foram lidas a Constitution e as dependências `qa-review-story.md`/`qa-gate.md`. A execução é um parecer manual de documentação solicitado pelo usuário. O gate formal de encerramento não foi emitido: a issue ainda possui critérios externos não atendidos e a story registra `InReview` contextual. O fluxo formal exige transição acoplada para `Done` após PASS/CONCERNS, o que seria inadequado para esta entrega parcial dos critérios de encerramento. Status e Change Log foram preservados; somente QA Results foi atualizado.

## Rastreabilidade dos critérios

| Critério da task | Verificação independente | Resultado |
|---|---|---|
| Listar cada componente da PoC | Inventário cobre canal, API, PLN, catálogo, recuperação, resposta, confirmação, identidade, dados, auditoria, voz, relatório, alertas, mensageria, integrações, infraestrutura e engenharia. São 32 linhas nas quatro tabelas principais. Notebook e landing page são identificados como auxiliares; AIOX é ferramenta de desenvolvimento na evidência. | Atendido no conteúdo local |
| Componente, equivalente, reaproveitamento e observação no Projeto.md | Todas as 32 linhas possuem os cinco campos, incluindo esforço. A legenda diferencia Direto, Adaptado, Referência e Planejado; esforço qualitativo é condicionado ao caminho de migração. | Atendido |
| Coerência com arquitetura | Responsabilidades mantidas; divergências dos diagramas e do texto antigo explicitadas, com encaminhamento à S5-43. Estado executável separado da arquitetura-alvo. | Atendido no recorte; conferência final S5-43 pendente |
| Dependência S5-19 | Caminhos web, aba Teams, bot e Copilot/MCP distinguem pré-requisitos e bloqueios, sem afirmar publicação ou licença disponível. | Documentado; conclusão externa não comprovada |
| Evidência, MR aprovado, comentário do revisor e Closes | Evidência técnica existe e é rastreável. Não há evidência de aprovação humana/MR desta entrega ou conclusão das dependências. | Evidência local atendida; itens GitLab pendentes |

## Conferências factuais

- Git confirmou os oito heads e ausência de ancestralidade em `origin/develop`: !130 `43e763cc`, !129 `41140ea8`, !128 `32689d95`, !127 `ea572497`, !124 `7b8d5e15`, !123 `5216a2cb`, !120 `e1e1c307` e !117 `dff223b1`. Os arquivos modificados correspondem aos resumos da evidência; a ausência de integração não foi confundida com o estado atual de aprovação no GitLab.
- `gemini/schemas.py` confirma contrato integrado `1.1.0`. Blocos `1.2.0`, TTS, filtro de dado sensível e correções adicionais de auditoria são tratados como propostas de branches, não capacidades já integradas.
- `security/access.py` confirma validação server-side por Supabase Auth e autorização `read`/`write`/`export`; Entra ID não é afirmado como ativo. SQL de Storage contém referências específicas do Supabase, justificando adaptação na migração.
- `rag/database.py` recupera extratos sintéticos com pontuação lexical e filtro de escopo; `sharepoint.py` usa JSON local. O texto não afirma Graph autenticado, índice vetorial documental ou extratores genéricos implementados.
- `nlp/inference.py` fixa revisão imutável do BERTimbau, e `preprocessing.py` importa NLTK. O mapeamento evita confundir embeddings de classificação com RAG vetorial.
- `gemini/client.py` contém clientes Gemini e OpenRouter; não foi apresentado cliente Azure OpenAI já integrado. `compose.prod.yml` configura relatório `memory`/`local`, embora o código disponha de modos persistentes.
- `reports/service.py` e `src/agent/support/IMPLEMENTATION.md` distinguem execução local, simulador e Power Automate opcional. DOCX final é produzido pelo backend; blueprint e manifesto Word não são tratados como fluxo/template publicado.
- Alertas preservam inscrição, outbox, workers, idempotência e confirmação de entrega; `aio-pika` e RabbitMQ não são descritos como cliente/topologia Service Bus intercambiáveis.

## Verificação das correspondências Microsoft

Foi conferida independentemente a documentação oficial nos pontos com maior risco de equivalência indevida: [abas Teams](https://learn.microsoft.com/en-us/microsoftteams/platform/tabs/what-are-tabs) para incorporação web, [Service Bus AMQP 1.0](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-amqp-overview) para o protocolo de destino, [políticas de dados da Power Platform](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention) para governança de conectores, [conectores personalizados](https://learn.microsoft.com/en-us/connectors/custom-connectors/define-openapi-definition) para a exigência documentada de OpenAPI 2.0 e [validação de claims Entra](https://learn.microsoft.com/en-us/entra/identity-platform/claims-validation) para os controles da API sobre token/tenant/identidade. Esses limites estão corretamente representados. Hospedagem e serviços alternativos são apresentados como correspondências de responsabilidade, sem afirmar licença ou disponibilidade corporativa.

## Verificações e limitações

As quatro tabelas de componentes têm cinco colunas consistentes e 8, 7, 11 e 6 linhas de componentes, respectivamente. Os nove destinos de âncora da nova seção no sumário correspondem aos títulos. Todos os links relativos da Seção 6.4 apontam a arquivos existentes. `git diff --check` passou na revisão.

Os gates finais executados pelo agente responsável em `src/frontend`, após restauração da instalação local por `npm ci --ignore-scripts --prefer-offline`, passaram: `npm run lint` exit 0; `npm run build` exit 0, incluindo `tsc --noEmit` e build Vite; `npm test -- --pool=forks --maxWorkers=1 --testTimeout=10000 --hookTimeout=10000` exit 0, com 14 suites e 90 testes aprovados em 151,41 s. O script `typecheck` não existe no manifest atual; a verificação TypeScript foi cumprida pelo build. Manifest e lockfile permaneceram intactos.

As primeiras tentativas de build/tsc e quatro suites falharam por `@radix-ui/react-popover` ausente na instalação local, embora declarado; a restauração corrigiu a causa e os gates foram repetidos com sucesso. O pool padrão de Vitest foi interrompido sem resultados após cerca de quatro minutos, e o resultado conclusivo usa pool forks, sem alterar a configuração versionada. Esta revisão não repetiu testes longos nem avaliou cobertura/pipelines das branches. CodeRabbit não foi executado nesta revisão manual de documentação, e não foi emitido parecer de qualidade do código ou homologação corporativa.

## Pendências e encaminhamento

Não foi encontrada correção obrigatória no novo conteúdo. Preservar as ressalvas de homologação e conferir novamente a tabela após S5-19/S5-43. Assignee, revisor humano de outra frente, comentário de aprovação e MR com `Closes #298` continuam pendentes de confirmação no GitLab. A minuta de MR registrada na evidência é texto local para publicação futura, sem valor de aprovação. A revisão aiox-qa atende à revisão documental local solicitada e não substitui esses itens do DoD.

Arquivos modificados por QA: este parecer e apenas a seção QA Results de `docs/stories/S5-44.md`. O responsável pela entrega deve atualizar checklist e File List após receber o parecer.
