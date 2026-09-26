<table>
  <tr>
    <td><a href="https://www.metro.sp.gov.br/"><img src="img/logo-metro.png" alt="Companhia do Metropolitano de Sao Paulo - Metro" border="0" width="180"></a></td>
    <td><a href="https://www.inteli.edu.br/"><img src="img/logo-Inteli.png" alt="Inteli - Instituto de Tecnologia e Lideranca" border="0" width="180"></a></td>
  </tr>
</table>

# Oneshot

## Grupo Oneshot

## Índice da documentação

Este arquivo indexa todos os documentos Markdown versionados no repositório. Os caminhos são relativos a este arquivo e estão agrupados por finalidade.

### Visão geral e documentação principal

| Documento | Conteúdo |
|---|---|
| [README do repositório](../README.md) | Apresentação do projeto, estrutura, início rápido e histórico de lançamentos. |
| [Projeto.md](Projeto.md) | Documentação consolidada do produto, requisitos, solução técnica, testes, implantação e viabilidade. |
| [Manual-instalacao.md](Manual-instalacao.md) | Instalação, configuração, execução e solução de problemas. |
| [prototipo-1-roteiro.md](prototipo-1-roteiro.md) | Roteiro do protótipo reativo sob demanda. |

### Gestão e processo de desenvolvimento

| Documento | Conteúdo |
|---|---|
| [GestaoProjeto.md](GestaoProjeto.md) | Sprints, papéis, riscos, planejamento e acompanhamento do projeto. |
| [GestaoConfiguracao.md](GestaoConfiguracao.md) | GitFlow, branches, commits, merge requests, hooks e versionamento. |
| [GuiaPadroesDesenvolvimento.md](GuiaPadroesDesenvolvimento.md) | Padrões e convenções adotados pela equipe. |

### Evidências da Sprint 4

- [Hipótese de economia de tokens](evidencias/sprint-04/hipotese-tokens/README.md)
- [Referências nas respostas](evidencias/sprint-04/referencias-respostas/README.md)
- [Evidência do RNF06](evidencias/sprint-04/rnf06/README.md)
- [Evidências de VHS/cache](evidencias/sprint-04/vhs/README.md)

### Evidências da Sprint 5

- [Webhooks e integração RabbitMQ](evidencias/sprint-05/webhooks-rabbitmq.md)

### Planejamento e relatórios de testes

- [Plano de VHS/cache de Speech-to-Text](testes/sprint4/plano-vhs.md)
- [Relatório S4-11 — persistência, auditoria e acesso](testes/sprint4/relatorio-s4-11.md)
- [Relatório S4-20 — E2E textual com RAG](testes/sprint4/relatorio-s4-20.md)
- [Relatório S4-32B — testes de integração](testes/sprint4/relatorio-s4-32b.md)
- [Relatório S4-33 — RNF01, RNF02 e RNF03](testes/sprint4/relatorio-s4-33.md)

### Testes de usabilidade

- [Índice dos testes de usabilidade](usabilidade/README.md)
- [Checklist de ambiente](usabilidade/checklist-ambiente.md)
- [Perfis e recrutamento dos participantes](usabilidade/perfis-participantes.md)
- [Questionário SUS](usabilidade/questionario-sus.md)
- [Roteiro do moderador](usabilidade/roteiro-moderador.md)
- [Termo de consentimento](usabilidade/termo-consentimento.md)

### Agente e workflows de relatório

- [Visão geral dos artefatos do agente](../src/agent/README.md)
- [Implementação dos workflows](../src/agent/support/IMPLEMENTATION.md)
- [Prompt: normalizar complemento do usuário](../src/agent/support/ai-builder/normalizar-complemento-usuario-v1.md)
- [Prompt: normalizar solicitação de relatório](../src/agent/support/ai-builder/normalizar-solicitacao-relatorio-v1.md)
- [Prompt: redigir resumo executivo](../src/agent/support/ai-builder/redigir-resumo-executivo-v1.md)
- [Prompt: revisar fundamentação do relatório](../src/agent/support/ai-builder/revisar-fundamentacao-relatorio-v1.md)

### Backend

- [README do backend](../src/backend/README.md)
- [Listas simuladas do SharePoint](../src/backend/app/rag/data/sharepoint/README.md)
- [Testes de desempenho do RNF05](../src/backend/app/tests/performance/README.md)
- [Testes de confiabilidade do RNF04](../src/backend/app/tests/rnf04/README.md)

### Evidências do backend

- [Índice de evidências dos RNFs](../src/backend/evidencias/README.md)
- [Fluxo de alerta de prazo](../src/backend/evidencias/alerta-prazo-atraso/README.md)
- [Execuções E2E do alerta](../src/backend/evidencias/alerta-prazo-atraso/execucoes-e2e.md)
- [Árvore do código medido](../src/backend/evidencias/campanha-37flash/arvore-medida.md)
- [Reteste de truncamento](../src/backend/evidencias/reteste-truncamento/RELATORIO.md)
- [Testes funcionais RF01 a RF10](../src/backend/evidencias/rf01-rf10/README.md)
- [RNF04 — rodada 1](../src/backend/evidencias/rnf04-81c787d/RELATORIO.md)
- [RNF04 — rodada definitiva](../src/backend/evidencias/rnf04-v12-37flash/RELATORIO.md)
- [RNF04 — rodada 2](../src/backend/evidencias/rnf04-v12-flashlite/RELATORIO.md)
- [RNF05 — rodada definitiva](../src/backend/evidencias/rnf05-37flash/RELATORIO.md)
- [RNF05 — rodadas descartadas por aquecimento](../src/backend/evidencias/rnf05-37flash/descartada-aquecimento-na-janela/LEIA.md)
- [RNF05 — rodada inicial](../src/backend/evidencias/rnf05-81c787d/RELATORIO.md)
- [RNF05 — linha de base Flash Lite](../src/backend/evidencias/rnf05-baseline-flashlite/RELATORIO.md)
- [RNF05 — protocolo congelado da rodada 2](../src/backend/evidencias/rnf05-rodada2/PROTOCOLO-CONGELADO.md)
- [RNF05 — relatório da rodada 2](../src/backend/evidencias/rnf05-rodada2/RELATORIO.md)
- [RNF05 — extensão da linha de base](../src/backend/evidencias/rnf05-rodada3/EXTENSAO-LINHA-DE-BASE.md)
- [RNF05 — protocolo congelado da rodada 3](../src/backend/evidencias/rnf05-rodada3/PROTOCOLO-CONGELADO.md)
- [RNF05 — relatório da rodada 3](../src/backend/evidencias/rnf05-rodada3/RELATORIO.md)
- [RNF05 — protocolo de cache frio](../src/backend/evidencias/rnf05-rodada3/cache-frio/PROTOCOLO-CONGELADO.md)
- [RNF05 — relatório de cache frio](../src/backend/evidencias/rnf05-rodada3/cache-frio/RELATORIO.md)

### Banco de dados

- [Documentação do banco](../src/database/docs/README.md)
- [Evidências locais do banco](../src/database/docs/evidencias/README.md)
- [Verificação do esquema físico](../src/database/docs/s4-08-schema-verification.md)
- [Carga sintética idempotente](../src/database/docs/s4-09-idempotent-seed.md)
- [Snapshot anterior à infraestrutura de relatórios](../src/database/snapshots/20260921_150831_pre_guided_report_infrastructure.md)
- [Snapshot posterior à infraestrutura de relatórios](../src/database/snapshots/20260921_151356_post_guided_report_infrastructure.md)

### Frontend

- [README do frontend](../src/frontend/README.md)
- [Evidências de testes do frontend](../src/frontend/TESTES.md)

### Landing page e RAG

- [README da landing page](../src/lp/README.md)
- [Backend de presença ao vivo](../src/lp/src/rag/backend/README.md)
- [Modelo RAG da landing page](../src/lp/src/rag/model/README.md)

#### Documentos usados pela base RAG da landing page

- [Gestão de configuração](../src/lp/src/rag/documentsRAG/GestaoConfiguracao.md)
- [Gestão do projeto](../src/lp/src/rag/documentsRAG/GestaoProjeto.md)
- [Guia de padrões de desenvolvimento](../src/lp/src/rag/documentsRAG/GuiaPadroesDesenvolvimento.md)
- [Índice da base RAG](../src/lp/src/rag/documentsRAG/Index.md)
- [Manual de instalação](../src/lp/src/rag/documentsRAG/Manual-instalacao.md)
- [Documentação do projeto](../src/lp/src/rag/documentsRAG/Projeto.md)
- [Roteiro do protótipo](../src/lp/src/rag/documentsRAG/prototipo-1-roteiro.md)

### Templates do GitLab

- [Template de tarefa](../.gitlab/issue_templates/Tarefa.md)
- [Template de merge request](../.gitlab/merge_request_templates/Default.md)

### Recursos não Markdown

| Pasta | Conteúdo |
|---|---|
| [img/](img/) | Imagens usadas na documentação. |
| [diagrams/](diagrams/) | Fontes editáveis dos diagramas. |
| [../src/notebooks/](../src/notebooks/) | Notebooks, scripts de experimentação e artefatos treinados. |
