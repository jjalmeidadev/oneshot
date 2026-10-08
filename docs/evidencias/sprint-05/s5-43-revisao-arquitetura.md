# S5-43 (#297) — Revisão da arquitetura e da interação entre os componentes

Data: 07/10/2026. Base: `develop` em `568a1c1`, que já inclui a S5-11
(mensageria e webhooks). Revisão documental assistida por IA; revisão humana
de outra frente: pendente.

## Motivo

A arquitetura documentada ainda era a da Sprint 1: Teams como canal e o
Copilot Studio como orquestrador dos tópicos. O Metrô não disponibilizou o
Copilot Studio (Seção 6.4.1 e Frente D da Seção 6.4.2 de `GestaoProjeto.md`),
e a solução foi construída com chat web, workflows guiados no backend,
RabbitMQ e deploy em EC2. A tabela de-para da S5-44
([`tabela-de-para-microsoft.md`](tabela-de-para-microsoft.md)) apontou essa
divergência e a deixou para esta task.

## O que mudou

### Diagramas

Os três diagramas foram redesenhados a partir do código. A convenção é a
mesma nos três: o que existe no código aparece em cor, e o que está apenas
previsto aparece em cinza tracejado com o estereótipo `<<previsto>>`.

| Figura | Antes | Depois | Fonte |
|---|---|---|---|
| 22 — Componentes | Arquitetura-alvo com Teams, Copilot Studio, conector personalizado, embeddings e índice vetorial | Solução implementada em sete camadas: canal, API, PLN, RAG/geração, processamento assíncrono, dados e serviços externos. A aba no Teams, o Copilot via MCP, o Entra ID e o SharePoint corporativo aparecem como previstos | [`componentes-metro-5.2.puml`](../../diagrams/componentes-metro-5.2.puml) |
| 25 — Sequência do fluxo funcional | O Copilot Studio executava o tópico e acionava o Power Automate | O workflow guiado do backend conduz as perguntas, pede confirmação e executa localmente ou despacha ao Power Automate, que devolve o resultado por webhook | [`sequencia-workflow-guiado.puml`](../../diagrams/sequencia-workflow-guiado.puml), que substitui `sequencia-copilot-fluxo.puml` |
| 27 — Implantação | Planejamento anterior ao deploy, com Azure como destino futuro | Implantação executada: Cloudflare Quick Tunnel, EC2 com Docker Compose (frontend, backend, RabbitMQ e workers), imagens no ECR, Supabase, Azure Speech e provedor de LLM. O ambiente Microsoft do Metrô aparece como alvo previsto | [`implantacao-poc.puml`](../../diagrams/implantacao-poc.puml) |

Para regerar as imagens, a partir da raiz do repositório:

```bash
java -jar plantuml.jar -charset UTF-8 -tpng -o ../img docs/diagrams/componentes-metro-5.2.puml
java -jar plantuml.jar -charset UTF-8 -tpng -o ../img docs/diagrams/sequencia-workflow-guiado.puml
java -jar plantuml.jar -charset UTF-8 -tpng -o ../img docs/diagrams/implantacao-poc.puml
```

O `@startuml` do diagrama de componentes se chama `componentes-metro-5.2`, e o
PlantUML corta o nome no ponto; se a saída sair como `componentes-metro-5.png`,
basta renomear para `componentes-metro-5.2.png`.

### RNF08

| | Texto |
|---|---|
| **Antes** | "A solução deve priorizar tecnologias compatíveis com o ecossistema Microsoft já utilizado pelo Metrô, incluindo Teams, Copilot Studio, Power Platform, SharePoint e Azure." Critério: Teams como canal principal, OpenAPI e componentes homologáveis. |
| **Depois** | Prioriza tecnologias compatíveis com o ecossistema Microsoft já usado pelo Metrô (Teams, SharePoint, Entra ID e Azure), sem depender de serviços que o parceiro não disponibilizou, como o Copilot Studio. Critério: OpenAPI válido, cada componente do runtime com equivalente Microsoft mapeado na Seção 6.4 e canal web publicável no Teams e acessível pelo Copilot por MCP, sem exigir Copilot Studio. |

A mudança vale nas três tabelas em que o RNF08 aparece: Seção 3.2, Seção 9.2.2
(critério) e Seção 9.2.3 (CT-RNF08-P/N).

**Efeito sobre a S5-31.** A rodada da S5-31 reprovou o CT-RNF08-P porque a
arquitetura não tinha mais o Copilot Studio. Pelo critério revisado, essa
ausência deixa de ser motivo de reprovação. A reavaliação do caso fica para a
consolidação final (S5-36, #290); esta task não reexecuta testes.

### Copilot e MCP

O Copilot Studio saiu da arquitetura. O acesso pelo Copilot do Metrô fica
previsto por um servidor MCP sobre a API REST (S5-18,
[#272](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/272)).
Na data desta revisão, a #272 está aberta, sem responsável e sem MR, por isso
o MCP aparece como previsto em todos os diagramas e tabelas. Os artefatos em
`src/agent` ficam como referência histórica.

## Afirmações revistas em `docs/Projeto.md`

As menções a "Copilot" passaram de 88 para 72. As que ficaram são de três
tipos: registro histórico das Sprints 1 e 2 (Seções 3.3 e 3.4, agora com nota
de leitura), negativas explícitas ("sem Copilot Studio") e o acesso previsto
por MCP.

| Seção | Mudança |
|---|---|
| 1.1, Glossário | "Copilot" e "Power Platform" descrevem o papel real na solução |
| 3.2, RNF08 | Requisito e critério revistos, como acima |
| 3.2.2, RNF05 | Provedor de produção descrito como o modelo Azure homologado pela GTI |
| 3.3 e 3.4 | Nota de leitura no início: registro da Sprint 1, com as decisões de canal revistas |
| 3.4.6 | Linha "Canal": chat web, com Teams e Copilot via MCP previstos |
| 4.1 a 4.4 | Contexto e prompts passam a ser do provedor de LLM, não do Copilot |
| 5.2 | Texto, Figura 22, tabela de componentes reescrita com situação e caminho no código, fluxo da 5.2.2 e decisões da 5.2.4 |
| 5.3.3 | Texto e Figura 25 trocados pelo workflow guiado |
| 6 e 6.1 | Mapeamento técnico e Figura 27 descrevem a implantação em EC2 |
| 6.2 e 6.3 | Nota de leitura (planejamento anterior ao deploy); fallback, passo 8 do processo, variáveis `COPILOT_STUDIO_*` removidas, métrica de fallback e checklist |
| 6.4.8 | Registro de que a conciliação foi feita nesta task |
| 8.5.5 | Teams, Entra ID e SharePoint como previstos; Copilot Studio fora da arquitetura |
| 9.2.2, 9.2.3 e 9.2.7 | Critério do RNF08, CT-RNF08 e linhas sobre o modelo de produção |

Também foram atualizados a linha final do R10 na matriz da Seção 3.18 de
`GestaoProjeto.md` e a seção "Reconciliação com os artefatos de arquitetura"
de [`tabela-de-para-microsoft.md`](tabela-de-para-microsoft.md).

## Fora do escopo

- `src/lp/src/rag/documentsRAG/Projeto.md` e o índice em
  `src/lp/src/rag/model/artifacts/index.json` são uma cópia antiga do
  documento usada como corpus da landing page. Eles ainda citam
  `sequencia-copilot-fluxo` e não foram alterados, porque regerar o corpus
  muda o comportamento do RAG da landing page.
- A Seção 9.6 mantém o resultado da S5-31 como foi registrado (RNF08-P
  reprovado pelo critério antigo). A nova leitura entra na S5-36.
