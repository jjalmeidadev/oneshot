# Gestão de Projeto

## Projeto G05

# Sumário

- [1. Introdução](#1-introdução)
  - [1.1 Objetivo do documento](#11-objetivo-do-documento)
  - [1.2 Escopo do documento](#12-escopo-do-documento)
- [2. Análise da sprint 1](#2-análise-da-sprint-1)
  - [2.1 Contexto da sprint](#21-contexto-da-sprint)
  - [2.2 Pontos fortes](#22-pontos-fortes)
  - [2.3 Pontos de melhoria](#23-pontos-de-melhoria)
  - [2.4 Ações de melhoria para a sprint 2](#24-ações-de-melhoria-para-a-sprint-2)
- [3. Matriz de papéis e responsabilidades](#3-matriz-de-papéis-e-responsabilidades)
  - [3.1 Matriz de responsabilidades - Sprint 1](#31-matriz-de-responsabilidades---sprint-1)
- [4. Contrato de convivência, SLA e rituais](#4-contrato-de-convivência-sla-e-rituais)
  - [4.1 Regra de ouro](#41-regra-de-ouro)
  - [4.2 Dailies](#42-dailies)
  - [4.3 Evidências de entrega](#43-evidências-de-entrega)
  - [4.4 Entrega, revisão e fechamento semanal](#44-entrega-revisão-e-fechamento-semanal)
  - [4.5 Resolução de impasses](#45-resolução-de-impasses)
  - [4.6 Gestão de conflitos](#46-gestão-de-conflitos)
  - [4.7 Comunicação oficial](#47-comunicação-oficial)
- [5. Planejamento da sprint 2](#5-planejamento-da-sprint-2)
  - [5.1 Pendência de preenchimento](#51-pendência-de-preenchimento)
  - [5.2 Estrutura esperada para a planning](#52-estrutura-esperada-para-a-planning)
- [6. Gestão do processo de desenvolvimento do grupo](#6-gestão-do-processo-de-desenvolvimento-do-grupo)
  - [6.1 Fluxo de trabalho no Kanban](#61-fluxo-de-trabalho-no-kanban)
  - [6.2 Regras obrigatórias para issues](#62-regras-obrigatórias-para-issues)
  - [6.3 Critérios de Ready e Done](#63-critérios-de-ready-e-done)
  - [6.4 Commits, merge requests e evidências](#64-commits-merge-requests-e-evidências)
  - [6.5 SLA Operacional](#65-sla-operacional)
  - [6.6 Função do Scrum Master no Merge](#66-função-do-scrum-master-no-merge)

# 1. Introdução

Este documento consolida as práticas de gestão de projeto do G05, cobrindo análise das sprints, matriz de papéis e responsabilidades, contrato de convivência, planejamento das sprints e gestão do processo de desenvolvimento do grupo.

O arquivo `docs/GestaoConfiguracao.md` fica reservado exclusivamente ao GitFlow e às política de branches.

## 1.1 Objetivo do documento

O objetivo deste documento é estabelecer uma forma clara de organização do trabalho da equipe, garantindo visibilidade das tarefas, previsibilidade de entregas, revisão por pares e comunicação objetiva ao longo da sprint.

Além de registrar o processo, este documento também funciona como acordo operacional do grupo: as regras aqui descritas devem orientar dailies, uso do Kanban, revisões, fechamento semanal e atuação do Scrum Master.

## 1.2 Escopo do documento

Este documento contempla:

- Retrospectiva e análise da Sprint 1;
- Ações de melhoria para a Sprint 2;
- Matriz de papéis e responsabilidades;
- Contrato de convivência, SLA e rituais;
- Planejamento da Sprint 2;
- Gestão do processo de desenvolvimento, incluindo Kanban, dailies, revisão e merge.

# 2. Análise da Sprint 1

## 2.1 Contexto da sprint

A Sprint 1 teve como foco principal a construção dos primeiros artefatos de entendimento do negócio, especificação de requisitos e organização do processo de trabalho do grupo. De forma geral, a equipe apresentou boa produtividade, conseguiu desenvolver as entregas dentro do prazo estipulado e manteve uma divisão clara das frentes individuais.

Cada integrante assumiu uma frente principal, mas o grupo também conseguiu revezar apoios pontuais entre as tarefas. Esse revezamento foi importante para evitar que as entregas ficassem isoladas demais e para permitir que os membros acompanhassem minimamente o que estava sendo produzido fora da própria frente.

Ao longo da sprint, o grupo também utilizou horários de desenvolvimento no Inteli para discutir ideias, fazer brainstorm de features e alinhar a visão inicial do produto. Esses momentos presenciais foram relevantes porque ajudaram a transformar percepções individuais em decisões coletivas, principalmente nas discussões sobre escopo, funcionalidades possíveis e forma de organização da equipe.

## 2.2 Pontos fortes

O principal ponto positivo da Sprint 1 foi a capacidade de entrega dentro do prazo. Mesmo com tarefas distribuídas entre frentes diferentes, os integrantes conseguiram cumprir suas responsabilidades e avançar nos artefatos planejados para a sprint.

Outro ponto forte foi o aproveitamento dos momentos presenciais de desenvolvimento. O grupo usou esses períodos para discutir ideias de features, alinhar entendimento sobre o problema e formalizar combinados de trabalho. Isso foi especialmente importante porque a Sprint 1 ainda tinha um caráter exploratório, exigindo consenso sobre o caminho inicial do projeto.

Também se destacou a formalização do contrato de convivência. Esse contrato surgiu a partir de uma dinâmica de liderança conduzida na aula do professor Filipe, em que o grupo refletiu sobre a própria aprendizagem em equipe. Durante essa reflexão, ficou claro que os integrantes estavam trabalhando de forma muito separada, o que dificultava o fluxo de desenvolvimento, a troca de contexto e a colaboração.

A partir dessa percepção, o grupo se reuniu para definir boas práticas de convivência, prazos de entrega, critérios de revisão e formato das dailies. A decisão de registrar essas regras representou uma evolução importante de maturidade, pois transformou um problema percebido em um acordo operacional verificável.

## 2.3 Pontos de melhoria

Apesar da produtividade, a Sprint 1 mostrou que o grupo ainda precisa melhorar a integração entre os integrantes. A execução individual funcionou para cumprir as tarefas, mas também evidenciou o risco de cada frente evoluir de forma isolada, com pouca troca durante o desenvolvimento.

Os rituais também podem ser melhor aproveitados. As dailies e momentos de alinhamento precisam deixar de ser apenas atualizações rápidas de status e passar a funcionar como espaços de sincronização real, com registro de evidências, identificação de impedimentos e conexão entre tarefas dependentes.

Outro ponto de melhoria está na antecipação das revisões. Como boa parte das entregas depende de documentação e alinhamento conceitual, revisar apenas no final aumenta o risco de inconsistências entre seções, retrabalho e divergência entre os artefatos.

Por fim, o grupo precisa fortalecer a visão coletiva sobre o projeto. Mesmo que cada integrante tenha uma frente principal, todos devem conhecer minimamente o estado das entregas centrais, os riscos ativos e as decisões tomadas.

## 2.4 Ações de melhoria para a Sprint 2

Com base na retrospectiva da Sprint 1, o grupo definiu as seguintes ações de melhoria para a Sprint 2:

| Ação de melhoria | Problema tratado | Como será verificada |
| --- | --- | --- |
| Usar as dailies para registrar o que foi feito, evidências, próximos passos e impedimentos. | Rituais pouco aproveitados e baixa visibilidade entre frentes. | Registro diário seguindo o modelo do contrato de convivência. |
| Antecipar entregas para quinta-feira e reservar tempo para revisão por pares. | Risco de revisão concentrada no fim da sprint. | Tarefas em revisão até quinta-feira, com evidências anexadas. |
| Promover maior integração entre frentes de trabalho. | Desenvolvimento muito separado entre integrantes. | Pelo menos um momento semanal de alinhamento coletivo sobre artefatos e dependências. |
| Registrar decisões relevantes em canal oficial ou issue do GitLab. | Perda de contexto e dificuldade de rastrear decisões. | Decisões importantes vinculadas a issues, documentos ou mensagens formais do grupo. |
| Reforçar o uso de DoR, DoD, labels, milestones e assignee nas issues. | Necessidade de aderência às regras do Dashboard Ágil. | Issues da sprint revisadas antes de avançarem de `Open` para `Backlog`. |
| Manter o contrato de convivência como referência prática. | Falta de combinados explícitos no início da sprint. | Contrato consultado durante dailies, revisões e fechamento semanal. |

Essas ações conectam a análise da Sprint 1 ao planejamento da Sprint 2 e buscam tornar o processo menos individualizado, mais rastreável e mais consistente com as boas práticas exigidas pelo módulo.

# 3. Matriz de papéis e responsabilidades

A matriz de responsabilidades deve variar a cada sprint. A intenção não é fixar cargos permanentes para todo o módulo, mas registrar qual foi a principal frente assumida por cada integrante na sprint corrente, deixando claro quem respondeu por cada artefato e reduzindo centralização de trabalho.

## 3.1 Matriz de responsabilidades - Sprint 1

Artefatos da Sprint 1:

- Entendimento do negócio;
- Especificação de requisitos funcionais e não funcionais;
- Gestão de projeto e configuração.

| Integrante | Frente principal na Sprint 1 | Artefato relacionado | Responsabilidades e entregas esperadas |
| --- | --- | --- | --- |
| Felipe | Design: personas e jornadas do usuário | Entendimento do negócio | Mapear perfis de usuário, consolidar personas, descrever jornadas e apoiar a conexão entre dores do usuário e proposta de solução. |
| Jaime | Documentação do problema e soluções mapeadas | Entendimento do negócio | Descrever o problema central, contextualizar as dores identificadas e registrar alternativas ou soluções analisadas pelo grupo. |
| Henrique | Documentação da parte técnica da solução | Entendimento do negócio / base técnica da solução | Explicar a visão técnica inicial da solução, tecnologias previstas, limitações técnicas e relação entre arquitetura proposta e necessidade do parceiro. |
| Leonardo | Documentação da gestão de projeto e configuração | Gestão de projeto e configuração | Estruturar os documentos GestaoProjeto.md e GestaoConfiguracao.md, garantindo aderência ao barema, ao contrato de trabalho e às regras de GitFlow. |
| Pedro | Documentação dos requisitos do projeto | Especificação de requisitos funcionais e não funcionais | Consolidar requisitos funcionais, requisitos não funcionais, critérios de aceite e relação dos requisitos com o escopo da solução. |
| Wendel | Modelagem do fluxo de negócios e matriz de riscos | Entendimento do negócio | Mapear o fluxo de negócio, registrar riscos iniciais, classificar impacto/probabilidade e propor mitigação para os riscos da Sprint 1. |

Essa matriz deve ser revisada a cada nova sprint, substituindo as frentes de acordo com os artefatos e prioridades planejados.

# 4. Contrato de convivência

O contrato de convivência define as regras práticas de trabalho do grupo. Ele prioriza comunicação clara, evidências objetivas, revisão antecipada e fechamento controlado da sprint.

## 4.1 Regra de ouro

Nenhuma entrega é considerada pronta sem evidência e revisão por outro integrante.

Isso vale para código, documentação, scripts, artefatos visuais e qualquer ajuste que impacte a entrega. A evidência pode ser um link, print, log de execução, trecho do GitLab, resumo de validação ou referência direta ao arquivo alterado.

## 4.2 Dailies

As dailies devem ser curtas, objetivas e focadas em visibilidade real do trabalho. Cada integrante deve responder aos quatro pontos abaixo:

1. O que fez desde a última daily;
2. Quais evidências comprovam o que foi feito;
3. O que vai fazer até a próxima daily;
4. Quais impedimentos existem.

Modelo de registro:

text
Integrante:
O que fiz:
Evidências:
O que vou fazer:
Impedimentos:


Regras:

- A daily deve durar no máximo 15 minutos quando síncrona;
- Quem não puder participar deve registrar a atualização de forma assíncrona no canal oficial;
- Tarefas sem evidência não devem ser tratadas como concluídas;
- Impedimentos devem ser sinalizados no mesmo dia em que forem identificados.

## 4.3 Evidências de entrega

Toda entrega deve ter evidência associada. O objetivo é reduzir ambiguidades como "finalizado" sem comprovação.

São evidências válidas:

- Link da issue no GitLab;
- Link do Merge Request;
- Print da tela ou do resultado;
- Log de execução;
- Arquivo alterado no repositório;
- Commit relacionado;
- Comentário de revisão;
- Checklist de DoD preenchido.

Critério mínimo: uma tarefa só pode avançar para revisão quando houver evidência suficiente para outro integrante validar o resultado.

## 4.4 Entrega, revisão e fechamento

A equipe adota a seguinte regra de fechamento:

| Marco | Prazo | Regra |
| --- | --- | --- |
| Entrega das tarefas | Até quinta-feira | Cada responsável deve concluir sua parte e disponibilizar evidências. |
| Revisão por pares | Até quinta-feira | Outro integrante deve revisar a entrega antes do fechamento. |
| Ajustes finais | Quinta-feira, após revisão | Correções pequenas podem ser feitas após apontamentos. |
| Merge para main | Sexta-feira, como cadência padrão | O Scrum Master coordena o merge final da versão validada. Entregas prontas podem ser promovidas antes, desde que sigam MR, pipeline, aprovação e DoD. |
| Fechamento formal | Só se necessário | O fechamento deve ocorrer apenas quando houver necessidade real de consolidar versão, resolver pendências ou registrar decisão final. |

Essa regra existe para evitar acúmulo de revisão na sexta-feira e reduzir risco de merge apressado sem validação.

## 4.5 Resolução de impasses

Quando houver discordância técnica ou de escopo, o grupo deve seguir a ordem abaixo:

1. Discussão objetiva entre os envolvidos, usando evidências e critérios do barema;
2. Consulta ao responsável pela frente afetada;
3. Decisão por maioria simples quando houver mais de uma alternativa aceitável;
4. Em caso de empate ou risco relevante, consulta ao orientador.

A decisão final deve ser registrada no canal oficial ou na issue relacionada.

## 4.6 Gestão de conflitos

Atrasos, falta de engajamento ou ausência de evidências devem ser tratados cedo.

Fluxo de gestão:

1. Feedback direto na daily ou no canal oficial;
2. Redistribuição ou apoio na tarefa, se houver risco de atraso;
3. Registro formal na retrospectiva da sprint, quando o problema se repetir;
4. Escalonamento ao orientador se o comportamento comprometer a entrega do grupo.

O foco da gestão de conflitos é proteger a entrega e a colaboração, não expor integrantes.

## 4.7 Comunicação oficial

As decisões relevantes devem ser registradas em canal oficial da equipe ou na própria issue do GitLab.

Devem ser registrados:

- Mudanças de escopo;
- Impedimentos;
- Decisões técnicas;
- Alteração de responsável;
- Critérios de aceite;
- Evidências de entrega;
- Aprovações e revisões.

Discussões informais podem acontecer em outros canais, mas a decisão final precisa ficar rastreável.

# 5. Planejamento da sprint 2

## 5.1 Pendência de preenchimento

O planejamento detalhado da Sprint 2 permanece como pendência assumida. Ele deve ser preenchido a partir do Kanban real, com issues criadas em `Open`, refinadas com DoR, DoD, labels, milestone e assignee antes de avançarem para o backlog.

## 5.2 Estrutura esperada para a planning

Quando preenchido, o planning deve seguir o modelo abaixo:

| ID | Tarefa | Tipo | Prioridade | Estimativa | Responsável | DoR | DoD | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A definir | A definir | A definir | A definir | PP/P/M/G | A definir | A definir | A definir | Pendente |

Escala de estimativa:

| Tamanho | Critério |
| --- | --- |
| PP | Até 30 minutos |
| P | Até 30 minutos |
| M | De 30 a 60 minutos |
| G | De 60 a 120 minutos |

Tarefas maiores que G devem ser quebradas antes de entrarem na sprint.

# 6. Gestão do processo de desenvolvimento do grupo

## 6.1 Fluxo de trabalho no Kanban

O Kanban do GitLab deve refletir o estado real das tarefas.

Fluxo recomendado:

```text
Open -> Backlog -> Doing -> Waiting Review -> Review -> Closed
```

Regras:

- Toda tarefa deve nascer como issue na coluna `Open`;
- A issue só deve avançar de `Open` para `Backlog` depois de refinada;
- A issue deve ter responsável único, tipo, estimativa, prioridade e milestone;
- O card deve ser atualizado sempre que houver mudança real de estado;
- Tarefas bloqueadas devem ser sinalizadas como impedimento na daily;
- Nenhuma tarefa deve ir para `Closed` sem evidência e revisão.

## 6.2 Regras obrigatórias para issues

As issues devem seguir as regras avaliadas pelo Dashboard Ágil do módulo.

| Critério | Regra |
| --- | --- |
| Coluna inicial | Toda issue nasce em `Open`. |
| Título | Deve usar verbo no infinitivo, por exemplo: `Criar diagrama de classes`. |
| Descrição | Deve conter contexto e objetivo, com mais de um parágrafo curto quando necessário. |
| Objetivo | Deve usar o cabeçalho `**Objetivo da tarefa:**`. |
| DoR | Deve usar `**DoR (Definition of Ready):**` com checklist de pré-condições. |
| DoD | Deve usar `**DoD (Definition of Done):**` com checklist verificável. |
| Assignee | Deve haver exatamente um responsável pela execução. |
| Labels | Deve conter tipo (`FEATURE`, `BUG FIX` ou `DOCUMENTATION`), tamanho (`SIZE_PP`, `SIZE_P`, `SIZE_M` ou `SIZE_G`) e prioridade (`PRIORIDADE ALTA` quando aplicável). |
| Milestone | Deve estar vinculada à sprint correspondente, como `Sprint 01` ou `Sprint 02`. |

Template mínimo:

```markdown
**Objetivo da tarefa:** <1-2 linhas>

**Contexto:** <por que estamos fazendo isso>

**DoR (Definition of Ready):**
- [ ] Dependências mapeadas
- [ ] Critérios de aceite definidos
- [ ] Ambiente ou documento base disponível

**DoD (Definition of Done):**
- [ ] Implementado ou documentado
- [ ] Evidências registradas
- [ ] MR aprovado por 1 revisor, quando aplicável
- [ ] Documentação atualizada, quando aplicável
```

## 6.3 Critérios de Ready e Done

Definition of Ready mínima:

- Objetivo da tarefa claro;
- Escopo delimitado;
- Responsável definido;
- Dependências conhecidas;
- Critérios de aceite registrados;
- Estimativa em PP, P, M ou G;
- Labels obrigatórias configuradas;
- Milestone da sprint vinculada.

Definition of Done mínima:

- Entrega concluída conforme objetivo;
- Evidência registrada;
- Revisão feita por outro integrante;
- Documentação atualizada, quando necessário;
- Merge Request aprovado, quando houver alteração versionada;
- Card atualizado no Kanban.

## 6.4 Commits, merge requests e evidências

O Dashboard Ágil avalia a conexão entre issue, commit, branch, Merge Request, milestone e revisão. Por isso, todo trabalho versionado deve manter rastreabilidade.

Regras de commits:

- Usar Conventional Commits;
- Referenciar a issue da sprint com `#N`;
- Manter a primeira linha com até 72 caracteres;
- Usar uma intenção por commit;
- Usar descrição no infinitivo, como `adicionar`, `corrigir`, `documentar` ou `validar`.

Formato:

```text
<tipo>(<escopo opcional>): <descrição curta> (#<issue>)
```

Exemplos:

```text
docs(projeto): documentar personas e jornadas (#12)
docs(requisitos): consolidar requisitos funcionais (#18)
chore(config): ajustar template de issues (#27)
```

Critérios mínimos para Merge Request:

- Título descritivo, com mais de três palavras, sem `WIP:` ou `Draft:`;
- Descrição substantiva com as mudanças realizadas;
- Issue vinculada;
- Evidências registradas;
- Reviewer definido;
- Aprovação por pelo menos um revisor;
- Pipeline, testes, lint ou validação manual registrados conforme o tipo de entrega;
- DoD atendida antes do merge.

## 6.5 SLA operacional

| Situação | SLA | Responsável por acionar |
| --- | --- | --- |
| Atualização de daily | Até o horário combinado da daily | Cada integrante |
| Registro de impedimento | No mesmo dia da identificação | Responsável pela tarefa |
| Primeira resposta a impedimento | Até 24 horas | Scrum Master ou responsável pela frente |
| Entrega para revisão | Até quinta-feira | Responsável pela tarefa |
| Revisão por pares | Até quinta-feira | Reviewer definido |
| Promoção para `hmg` | Quando a entrega estiver pronta e revisada | Responsável pela frente e Scrum Master |
| Merge final para `main` | Sexta-feira como cadência padrão, ou antes se houver entrega pronta e aprovada | Scrum Master |

## 6.6 Função do scrum master no merge

O Scrum Master não é o único responsável pela qualidade das entregas, mas é o responsável por coordenar o merge final da sprint.

Antes do merge para `main`, o Scrum Master deve verificar:

- Se as tarefas previstas para a versão estão revisadas;
- Se existem evidências mínimas de entrega;
- Se os Merge Requests necessários foram aprovados;
- Se não há impedimento crítico aberto;
- Se o conteúdo de `dev` representa a versão que o grupo deseja entregar;
- Se a promoção seguiu o fluxo obrigatório `feature/* -> dev -> hmg -> main`.

Na sexta-feira, o Scrum Master executa ou coordena o merge para `main` e comunica o grupo sobre o estado final da entrega. Quando uma entrega estiver pronta antes da sexta-feira, o Scrum Master pode coordenar a promoção antecipada, desde que exista Merge Request, aprovação, evidência e validação.