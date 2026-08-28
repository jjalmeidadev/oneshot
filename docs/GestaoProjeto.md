<table>
  <tr>
    <td><a href="https://www.metro.sp.gov.br/"><img src="img/logo-metro.png" alt="Companhia do Metropolitano de Sao Paulo - Metro" border="0" width="180"></a></td>
    <td><a href="https://www.inteli.edu.br/"><img src="img/logo-Inteli.png" alt="Inteli - Instituto de Tecnologia e Lideranca" border="0" width="180"></a></td>
  </tr>
</table>

# Agente de IA para o Portfólio de Projetos do Metrô

## Nome do grupo: Oneshot

## Integrantes:

- <a href="https://www.linkedin.com/in/ntsfelipe/">Felipe Neves</a>
- <a href="https://www.linkedin.com/in/henrique-rodrigues-diniz-b7b011319/">Henrique Diniz</a>
- <a href="https://www.linkedin.com/in/jaimeandradedealmeida/">Jaime Almeida</a>
- <a href="https://www.linkedin.com/in/leonardoramosvieira">Leonardo Ramos</a>
- <a href="https://www.linkedin.com/in/pedro-uchoaa/">Pedro Uchoa</a>
- <a href="https://www.linkedin.com/in/wendel-feitosa-975bb1346/">Wendel Feitosa</a>

# Sumário

- [1. Introdução](#1-introdução)
  - [1.1 Objetivo do documento](#11-objetivo-do-documento)
  - [1.2 Escopo do documento](#12-escopo-do-documento)
- [2. Análise das sprints](#2-análise-das-sprints)
  - [2.1 Sprint 1](#21-sprint-1)
    - [2.1.1 Contexto da sprint](#211-contexto-da-sprint)
    - [2.1.2 Linha de base medida](#212-linha-de-base-medida)
    - [2.1.3 Pontos fortes](#213-pontos-fortes)
    - [2.1.4 Pontos de melhoria](#214-pontos-de-melhoria)
    - [2.1.5 Ações de melhoria definidas para a Sprint 2](#215-ações-de-melhoria-definidas-para-a-sprint-2)
  - [2.2 Sprint 2](#22-sprint-2)
    - [2.2.1 Contexto da sprint](#221-contexto-da-sprint)
    - [2.2.2 Indicadores medidos e resultado das metas](#222-indicadores-medidos-e-resultado-das-metas)
    - [2.2.3 Pontos fortes](#223-pontos-fortes)
    - [2.2.4 Pontos de melhoria](#224-pontos-de-melhoria)
    - [2.2.5 Ações de melhoria para a Sprint 3](#225-ações-de-melhoria-para-a-sprint-3)
- [3. Matriz de risco](#3-matriz-de-risco)
  - [3.1 Critérios de avaliação](#31-critérios-de-avaliação)
  - [3.2 Registro consolidado e status na Sprint 2](#32-registro-consolidado-e-status-na-sprint-2)
  - [3.3 Histórico de acompanhamento e justificativa das reavaliações](#33-histórico-de-acompanhamento-e-justificativa-das-reavaliações)
  - [3.4 Efetividade das ações aplicadas](#34-efetividade-das-ações-aplicadas)
  - [3.5 Matriz probabilidade × impacto](#35-matriz-probabilidade-impacto)
  - [3.6 Análise dos três itens mais críticos](#36-análise-dos-três-itens-mais-críticos)
  - [3.7 Mecanismo contínuo de acompanhamento](#37-mecanismo-contínuo-de-acompanhamento)
- [4. Matriz de papéis e responsabilidades](#4-matriz-de-papéis-e-responsabilidades)
  - [4.1 Matriz da Sprint 1](#41-matriz-da-sprint-1)
  - [4.2 Matriz da Sprint 2](#42-matriz-da-sprint-2)
  - [4.3 Rotação de papéis entre as sprints](#43-rotação-de-papéis-entre-as-sprints)
- [5. Contrato de convivência, SLA e rituais](#5-contrato-de-convivência-sla-e-rituais)
  - [5.1 Regra de ouro](#51-regra-de-ouro)
  - [5.2 Dailies](#52-dailies)
  - [5.3 Evidências de entrega](#53-evidências-de-entrega)
  - [5.4 Entrega, revisão e fechamento](#54-entrega-revisão-e-fechamento)
  - [5.5 Resolução de impasses](#55-resolução-de-impasses)
  - [5.6 Gestão de conflitos](#56-gestão-de-conflitos)
  - [5.7 Comunicação oficial](#57-comunicação-oficial)
  - [5.8 Registro de revisões do contrato](#58-registro-de-revisões-do-contrato)
- [6. Planejamento da Sprint 3](#6-planejamento-da-sprint-3)
  - [6.1 Visão geral da planning](#61-visão-geral-da-planning)
  - [6.2 Backlog planejado no Kanban](#62-backlog-planejado-no-kanban)
    - [Pendentes da Sprint 2 — prioridade máxima](#pendentes-da-sprint-2-prioridade-máxima)
    - [Artefato 1 — Desenvolvimento e Documentação Técnica](#artefato-1-desenvolvimento-e-documentação-técnica)
    - [Artefato 2 — Planejamento de Testes Sistêmicos](#artefato-2-planejamento-de-testes-sistêmicos)
    - [Artefato 3 — Gestão de Projetos Evolutiva](#artefato-3-gestão-de-projetos-evolutiva)
    - [Sequenciamento](#sequenciamento)
  - [6.3 Escala de estimativa](#63-escala-de-estimativa)
- [7. Gestão do processo de desenvolvimento do grupo](#7-gestão-do-processo-de-desenvolvimento-do-grupo)
  - [7.1 Fluxo de trabalho no Kanban](#71-fluxo-de-trabalho-no-kanban)
  - [7.2 Regras obrigatórias para issues](#72-regras-obrigatórias-para-issues)
  - [7.3 Critérios de Ready e Done](#73-critérios-de-ready-e-done)
  - [7.4 Commits, merge requests e evidências](#74-commits-merge-requests-e-evidências)
  - [7.5 SLA operacional](#75-sla-operacional)
  - [7.6 Função do scrum master no merge](#76-função-do-scrum-master-no-merge)

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

# 2. Análise das sprints

Esta seção acumula a análise de cada sprint. As sprints anteriores permanecem registradas para que a evolução dos indicadores seja verificável, e não afirmada.

## 2.1 Sprint 1

### 2.1.1 Contexto da sprint

A Sprint 1 teve como foco principal a construção dos primeiros artefatos de entendimento do negócio, especificação de requisitos e organização do processo de trabalho do grupo. De forma geral, a equipe apresentou boa produtividade, conseguiu desenvolver as entregas dentro do prazo estipulado e manteve uma divisão clara das frentes individuais.

Cada integrante assumiu uma frente principal, mas o grupo também conseguiu revezar apoios pontuais entre as tarefas. Esse revezamento foi importante para evitar que as entregas ficassem isoladas demais e para permitir que os membros acompanhassem minimamente o que estava sendo produzido fora da própria frente.

Ao longo da sprint, o grupo também utilizou horários de desenvolvimento no Inteli para discutir ideias, fazer brainstorm de features e alinhar a visão inicial do produto. Esses momentos presenciais foram relevantes porque ajudaram a transformar percepções individuais em decisões coletivas, principalmente nas discussões sobre escopo, funcionalidades possíveis e forma de organização da equipe.

### 2.1.2 Linha de base medida

Os pontos fortes e os pontos de melhoria descritos a seguir são acompanhados dos números que os sustentam. A finalidade é prática: sem linha de base não há como saber, no fim da Sprint 2, se as ações de melhoria funcionaram. Todos os indicadores abaixo foram apurados sobre o histórico do repositório no período da Sprint 1 (05/08/2026 a 14/08/2026) e são reprodutíveis pelos comandos indicados.

| Indicador | Sprint 1 | Como foi apurado | Meta para a Sprint 2 |
| --- | :---: | --- | :---: |
| Commits no período | 69 | `git rev-list --count --until=2026-08-15 HEAD` | — |
| Merge requests integrados | 27 | `git rev-list --count --merges --until=2026-08-15 HEAD` | — |
| Commits nos dois últimos dias da sprint | 45 de 69 (65%) | distribuição diária obtida de `git log --date=short --format=%ad` | ≤ 40% |
| MRs integrados nos dois últimos dias | 19 de 27 (70%) | mesma apuração, restrita a merges | ≤ 40% |
| Commits no dia de maior concentração (13/08) | 29 de 69 (42%) | mesma apuração | ≤ 25% |
| Commits locais dentro da convenção | 22 de 23 (96%) | commits em que autor e committer coincidem | 100% |
| Commits de squash dentro da convenção | 6 de 19 (32%) | commits gerados no servidor pelo merge com squash | 100% |
| Integrantes que tocaram mais de um artefato | 3 de 6 | arquivos `.md` distintos alterados por autor | ≥ 5 de 6 |
| Amplitude de commits entre integrantes | 23 contra 5 (4,6×) | commits por autor no período | ≤ 2,5× |

### 2.1.3 Pontos fortes

**Entrega dentro do prazo, com volume distribuído entre todas as frentes.** Os seis integrantes produziram commits no período e todos os artefatos planejados foram entregues. O grupo integrou 27 merge requests em oito dias de atividade.

**Aproveitamento dos momentos presenciais de desenvolvimento.** O grupo usou esses períodos para discutir ideias de features, alinhar entendimento sobre o problema e formalizar combinados de trabalho. Isso foi especialmente importante porque a Sprint 1 ainda tinha um caráter exploratório, exigindo consenso sobre o caminho inicial do projeto.

**Aderência real à convenção de commits.** Dos 23 commits criados nas máquinas do grupo, 22 seguem o padrão `<tipo>: <descrição> (#issue)` — 96%. O número é consequência direta do hook `commit-msg` documentado na Seção 7 do `GestaoConfiguracao.md`: a regra não ficou no papel, ela bloqueia.

**Formalização do contrato de convivência.** Esse contrato surgiu a partir de uma dinâmica de liderança conduzida na aula do professor Filipe, em que o grupo refletiu sobre a própria aprendizagem em equipe. Durante essa reflexão, ficou claro que os integrantes estavam trabalhando de forma muito separada, o que dificultava o fluxo de desenvolvimento, a troca de contexto e a colaboração. A partir dessa percepção, o grupo definiu boas práticas de convivência, prazos de entrega, critérios de revisão e formato das dailies, transformando um problema percebido em um acordo operacional verificável.

### 2.1.4 Pontos de melhoria

**Revisão concentrada no fim da sprint.** Este é o ponto mais nítido dos dados: 45 dos 69 commits (65%) e 19 dos 27 merge requests (70%) ocorreram nos dois últimos dias do período, sendo 29 commits (42%) apenas em 13/08. Uma revisão que chega junto com o prazo tem pouco espaço para gerar correção, e é isso que explica as inconsistências entre seções encontradas na entrega. A meta da Sprint 2 é reduzir a concentração dos dois últimos dias para no máximo 40% dos commits.

**Trabalho isolado entre frentes.** Três dos seis integrantes alteraram apenas um arquivo `.md` durante toda a sprint, e a diferença entre quem mais e quem menos commitou foi de 4,6 vezes (23 contra 5). Os dois números medem a mesma coisa por ângulos diferentes: cada frente evoluiu dentro do seu próprio arquivo, com pouca troca durante o desenvolvimento. A meta é que ao menos cinco dos seis integrantes toquem mais de um artefato e que a amplitude caia para 2,5 vezes.

**Rituais pouco aproveitados.** O contrato de convivência, com o formato de registro da daily, só foi formalizado durante a própria Sprint 1, de modo que a maior parte do período correu sem o combinado em vigor. As dailies funcionaram como atualização de status, e não como sincronização: impedimentos e dependências entre frentes não eram levantados no ritual, mas descobertos depois, na revisão.

**Efeito colateral do squash sobre a rastreabilidade.** Dos 19 commits gerados pelo servidor ao aplicar squash nos merge requests, apenas 6 seguem a convenção — 32%. O commit de squash nasce no GitLab, não passa pelos hooks locais e herda o título do merge request, que por padrão vem do nome da branch. O efeito não é apenas cosmético: como o squash grava no campo de committer o nome de quem aprovou o merge, parte do trabalho de integrantes deixa de aparecer como autoria própria no histórico. A ação correspondente está na Seção 2.5.

**Visão coletiva sobre o projeto.** Mesmo que cada integrante tenha uma frente principal, todos devem conhecer minimamente o estado das entregas centrais, os riscos ativos e as decisões tomadas. Esse ponto é o que os dois primeiros indicadores produzem como consequência.

### 2.1.5 Ações de melhoria definidas para a Sprint 2

Com base na retrospectiva da Sprint 1, o grupo definiu as seguintes ações de melhoria para a Sprint 2:

| Ação de melhoria | Problema tratado | Como será verificada |
| --- | --- | --- |
| Usar as dailies para registrar o que foi feito, evidências, próximos passos e impedimentos. | Rituais pouco aproveitados e baixa visibilidade entre frentes. | Registro diário seguindo o modelo do contrato de convivência. |
| Antecipar entregas para quinta-feira e reservar tempo para revisão por pares. | Risco de revisão concentrada no fim da sprint. | Tarefas em revisão até quinta-feira, com evidências anexadas. |
| Promover maior integração entre frentes de trabalho. | Desenvolvimento muito separado entre integrantes. | Pelo menos um momento semanal de alinhamento coletivo sobre artefatos e dependências. |
| Registrar decisões relevantes em canal oficial ou issue do GitLab. | Perda de contexto e dificuldade de rastrear decisões. | Decisões importantes vinculadas a issues, documentos ou mensagens formais do grupo. |
| Reforçar o uso de DoR, DoD, labels, milestones e assignee nas issues. | Necessidade de aderência às regras do Dashboard Ágil. | Issues da sprint revisadas antes de avançarem de `Open` para `Backlog`. |
| Manter o contrato de convivência como referência prática. | Falta de combinados explícitos no início da sprint. | Contrato consultado durante dailies, revisões e fechamento semanal. |
| Padronizar o título do merge request na convenção de commit antes de aprovar o merge. | 32% dos commits de squash fora do padrão, por herdarem o nome da branch. | Verificação do título do MR pelo revisor antes do merge; ao fim da sprint, 100% dos commits de squash na convenção. |
| Distribuir revisão entre frentes diferentes daquela em que o revisor trabalhou. | Três integrantes tocaram um único artefato na Sprint 1. | Ao menos cinco dos seis integrantes com alteração em mais de um artefato ao fim da sprint. |

Essas ações conectam a análise da Sprint 1 ao planejamento da Sprint 2 e buscam tornar o processo menos individualizado, mais rastreável e mais consistente com as boas práticas exigidas pelo módulo.

## 2.2 Sprint 2

### 2.2.1 Contexto da sprint

A Sprint 2 teve três artefatos: Prototipação Exploratória, Estratégia Técnica da Solução e Gestão de Projetos Evolutiva. Diferente da Sprint 1, que foi integralmente documental, esta sprint produziu código: o pipeline de classificação de intenções, uma bancada de teste para o caminho de consulta do RAG e os primeiros scripts de dados.

A sprint também absorveu uma frente não planejada. O feedback da Sprint 1 chegou em 24/08, com apontamentos de recorte e coerência nos artefatos de entendimento do negócio e de gestão, e a correção foi tratada dentro desta sprint, na issue [#111](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/111).

### 2.2.2 Indicadores medidos e resultado das metas

A Sprint 1 fechou com nove indicadores medidos e uma meta para cada um. Esta é a apuração contra aquelas metas, no período de 15/08/2026 a 27/08/2026, sobre o histórico de `origin/develop`.

**Apuração final, com a sprint encerrada e todos os merge requests integrados.** Os números abaixo substituem a apuração parcial feita em 27/08, que considerava a sprint ainda aberta e superestimava o resultado de dois indicadores.

| Indicador | Sprint 1 | Meta da Sprint 2 | Sprint 2 | Resultado |
| --- | :---: | :---: | :---: | :---: |
| Commits no período | 69 | — | 49 | — |
| Merge requests integrados | 27 | — | 23 | — |
| Commits nos dois últimos dias | 45 de 69 (65%) | ≤ 40% | 26 de 49 (53%) | ❌ não atingida |
| Commits no dia de maior concentração | 29 de 69 (42%) | ≤ 25% | 15 de 49 (30%) | ❌ não atingida |
| Commits locais dentro da convenção | 22 de 23 (96%) | 100% | 6 de 6 (100%) | ✅ atingida |
| Commits de squash dentro da convenção | 6 de 19 (32%) | 100% | 7 de 20 (35%) | ❌ não atingida |
| Amplitude de commits entre integrantes | 23 contra 5 (4,6×) | ≤ 2,5× | 11 contra 5 (2,2×) | ✅ atingida |
| Integrantes que tocaram mais de um arquivo | 3 de 6 | ≥ 5 de 6 | 6 de 6 | ✅ atingida |
| Merge requests abertos no fechamento | não medido | — | 0 | novo indicador |

Duas ressalvas de método, para que a comparação não afirme mais do que os dados sustentam.

A primeira é que o indicador de dispersão mudou de definição. Na Sprint 1 ele contava arquivos `.md` distintos por integrante, porque a sprint era só documentação. Na Sprint 2 existe código, e contar apenas `.md` distorceria o resultado — o Felipe, por exemplo, tocou 44 arquivos, todos em `src/`, e apareceria como zero. O indicador passou a contar arquivos distintos em `docs/` e `src/`, e é assim que deve ser lido daqui em diante.

A segunda diz respeito à revisão desta própria seção. Uma apuração parcial, feita antes do fechamento, indicava 34% dos commits nos dois últimos dias e concluía que a meta de 40% havia sido atingida. Com a sprint encerrada e os quatro merge requests pendentes integrados, o número subiu para 53%. O registro do erro fica aqui porque ele ensina algo sobre o método: apurar indicador de concentração antes do fim do período mede o meio da sprint, não a sprint.

### 2.2.3 Pontos fortes

**A dispersão do trabalho aumentou e a meta foi superada.** Os seis integrantes tocaram mais de um arquivo, contra três na Sprint 1, e a amplitude entre quem mais e quem menos commitou caiu de 4,6× para 2,2×, abaixo da meta de 2,5×. O trabalho deixou de se concentrar em duas ou três pessoas, e foi a única meta de processo efetivamente cumprida na sprint.

**A convenção de commits locais chegou a 100%.** Os seis commits criados nas máquinas do grupo seguem o padrão, contra 96% na sprint anterior. O hook `commit-msg` continua sendo o que sustenta esse número.

**A sprint produziu decisão técnica com evidência, e não com preferência.** Tanto a escolha da API de transcrição quanto a do algoritmo de PLN foram registradas com benchmark, critério de comparação e limitações declaradas. A seção de PLN, em particular, declara que o resultado de 0,6777 de F1-macro na intenção específica é moderado e nomeia sete ressalvas antes de tratar a escolha como definitiva.

### 2.2.4 Pontos de melhoria

**O squash continua quebrando a rastreabilidade, e a ação definida não resolveu.** Apenas 4 dos 13 commits de squash seguem a convenção — 31%, praticamente o mesmo 32% da Sprint 1. A ação registrada na Sprint 1 foi "padronizar o título do merge request antes de aprovar o merge", e ela não foi cumprida. Dos títulos gerados, aparecem casos como `feat/implementar-frontend-inicial-mockado` e `Docs/comparacao das alternativas e documentação`, que são nomes de branch e não mensagens de commit. A ação precisa deixar de depender de lembrança e virar verificação no fluxo.

**Quatro merge requests seguem abertos no fechamento da sprint.** São entregas prontas que não estão em `develop`: o modelo lógico de dados, a atualização dos requisitos funcionais, os requisitos das APIs de voz e a correção do feedback da Sprint 1. O trabalho existe, mas quem avalia o repositório em `develop` não o encontra. Este é um risco novo, registrado como R11 na Seção 3.4.

**Documentação e implementação divergiram dentro da mesma sprint.** A Seção 5.2 do `Projeto.md` foi entregue descrevendo uma interface própria de chat como ponto de entrada da arquitetura, sem citar o Microsoft Teams em nenhum ponto da seção, enquanto a Seção 2.4.3, a matriz de priorização da 2.8 e o RNF08 mantinham o Teams como canal do produto. A mesma seção nomeava o provedor de LLM usado na bancada de teste como se fosse decisão de produto. Ambos foram corrigidos, mas só depois de uma revisão cruzada — não foram detectados por quem escreveu nem por quem revisou o merge request. É o risco R10 se materializando dentro da equipe, e não com o parceiro.

**A carga por integrante ficou desigual, e os indicadores de commit não capturam isso.** Os números da Seção 2.2.2 mostram distribuição melhor que a Sprint 1, mas medem volume de commit, não carga de entrega. A divisão por task da Seção 4.2 mostra outra coisa: dois integrantes absorveram a prototipação inteira além de suas frentes técnicas, enquanto quatro itens da Estratégia Técnica seguiam em andamento na data desta apuração, três deles sob o mesmo responsável. Independente de fecharem até o prazo, a concentração já indica que a carga não foi conferida durante a sprint. A planning da Sprint 3 precisa ter um ponto de verificação de carga no meio do período, e não só no fechamento.

**A antecipação de entregas não se sustentou até o fim.** A concentração nos dois últimos dias caiu de 65% para 53%, melhor que a Sprint 1 mas longe da meta de 40%. O dia de maior concentração ficou em 30%, contra a meta de 25%. A ação de adotar quinta-feira como marco de revisão produziu efeito na primeira metade da sprint, mas os quatro merge requests que ficaram abertos até o último dia concentraram 26 dos 49 commits em 48 horas. A causa é a mesma da Sprint 1: tarefas que só começam depois que a anterior fecha, em vez de avançarem em paralelo, agora somadas à revisão que se acumulou no fim.

### 2.2.5 Ações de melhoria para a Sprint 3

| Ação de melhoria | Problema tratado | Como será verificada |
| --- | --- | --- |
| Renomear o merge request para o formato `<tipo>: <descrição> (#issue)` como item obrigatório do checklist de revisão, antes da aprovação. | 31% dos commits de squash na convenção; a ação da Sprint 1 dependia de lembrança. | Ao fim da sprint, 100% dos commits de squash na convenção, apurado por `git log --no-merges` comparando autor e committer. |
| Definir quarta-feira como marco de integração: todo MR aberto até lá deve ser revisado e mergeado ou ter bloqueio declarado na issue. | Quatro MRs abertos no fechamento da Sprint 2. | Nenhum MR com mais de 48h sem revisão no fechamento da sprint. |
| Revisão cruzada obrigatória entre artefatos que se referenciam: quem revisa uma seção técnica confere a coerência com as seções de escopo que ela cita. | Divergência entre a Seção 5.2 e as Seções 2.4.3, 2.8 e RNF08. | Comentário de revisão citando explicitamente as seções conferidas, registrado no MR. |
| Quebrar tasks em unidades de até 60 minutos (faixa M) e permitir que frentes independentes avancem em paralelo. | 31% dos commits concentrados em um único dia. | Distribuição diária de commits, com no máximo 25% em um único dia. |
| Apurar os indicadores somente após o fechamento da sprint e a integração de todos os merge requests. | A apuração parcial da Sprint 2 indicou meta atingida em um indicador que, no fechamento, não foi. | Tabela comparativa das três sprints na análise da Sprint 3, com data de apuração declarada. |

# 3. Matriz de risco

A partir da Sprint 2, a matriz de risco atualizada passa a ser mantida neste documento. A versão original, produzida no artefato de entendimento de negócio, permanece registrada na Seção 2.7 do `Projeto.md` e não é alterada — é contra ela que a evolução dos itens pode ser conferida.

## 3.1 Critérios de avaliação

Probabilidade e impacto são avaliados de 1 a 5, e a severidade é o produto entre os dois.

| Faixa de severidade | Criticidade | Tratamento esperado |
| :---: | --- | --- |
| 20 a 25 | 🔴 Crítica | Ação de mitigação ativa e acompanhamento em toda daily |
| 12 a 16 | 🟠 Alta | Ação definida com responsável e verificação semanal |
| 6 a 10 | 🟡 Moderada | Monitoramento, com ação preparada mas não acionada |
| 1 a 5 | 🟢 Baixa | Registro, sem ação dedicada |

Os status possíveis são **Aberto**, **Em Monitoramento**, **Mitigado**, **Materializado** e **Encerrado**.

## 3.2 Registro consolidado e status na Sprint 2

As colunas P, I e Sev. trazem a avaliação vigente. A coluna de variação indica a mudança em relação à avaliação original do `Projeto.md`.

| ID | Tipo | Risco / Oportunidade | P | I | Sev. | Variação | Criticidade | Responsável | Status |
| :---: | :---: | --- | :---: | :---: | :---: | :---: | --- | --- | --- |
| **R01** | 🔴 | Indisponibilidade ou baixa qualidade das informações e documentos para a base de conhecimento | 3 | 5 | **15** | ↓ de 20 | 🟠 Alta | Jaime Almeida | Em Monitoramento |
| **R02** | 🔴 | Dificuldades ou limitações nas integrações com o ecossistema Microsoft | 4 | 5 | **20** | = | 🔴 Crítica | Felipe Neves | Em Monitoramento |
| **R03** | 🔴 | Respostas inadequadas, imprecisas ou não fundamentadas geradas pelo agente | 3 | 5 | **15** | ↓ de 20 | 🟠 Alta | Henrique Diniz | Em Monitoramento |
| **R04** | 🔴 | Limitações no controle de autenticação, permissões e acesso por perfil | 3 | 5 | **15** | = | 🟠 Alta | Wendel Feitosa | Em Monitoramento |
| **R05** | 🔴 | Alterações, inconsistências ou desatualização das fontes utilizadas | 3 | 4 | **12** | ↓ de 16 | 🟠 Alta | Leonardo Ramos | Em Monitoramento |
| **R06** | 🔴 | Indisponibilidade ou baixa participação dos representantes do Metrô | 3 | 4 | **12** | = | 🟠 Alta | Jaime Almeida | Aberto |
| **R07** | 🔴 | Ampliação do escopo por incorporação de novas funcionalidades | 4 | 4 | **16** | = | 🟠 Alta | Pedro Uchoa | Em Monitoramento |
| **R08** | 🔴 | Tempo insuficiente para implementar, validar e documentar o previsto | 4 | 4 | **16** | = | 🟠 Alta | Felipe Neves | Em Monitoramento |
| **R09** | 🔴 | Sobrecarga ou indisponibilidade de integrantes | 3 | 4 | **12** | = | 🟠 Alta | Henrique Diniz | Em Monitoramento |
| **R10** | 🔴 | Divergência de entendimento sobre requisitos e comportamento esperado | 4 | 3 | **12** | ↑ de 9 | 🟠 Alta | Pedro Uchoa | **Materializado** |
| **R11** | 🔴 | Entregas concluídas que permanecem em merge requests não integrados ao `develop` | 4 | 4 | **16** | novo | 🟠 Alta | Leonardo Ramos | Aberto |
| **R12** | 🔴 | Provedor de LLM ainda não definido nem homologado, com integração exigida na Sprint 3 | 4 | 4 | **16** | novo | 🟠 Alta | Henrique Diniz | Aberto |
| **O1** | 🟢 | Aproveitamento do ecossistema Microsoft já utilizado pelo parceiro | 4 | 4 | **16** | = | 🟢 Alta | Wendel Feitosa | Em Monitoramento |
| **O2** | 🟢 | Disponibilização de fontes oficiais e conhecimento do PMO | 3 | 5 | **15** | = | 🟢 Alta | Leonardo Ramos | Em Monitoramento |
| **O3** | 🟢 | Arquitetura modular e escalável para incorporar novos fluxos | 4 | 5 | **20** | ↑ de 15 | 🟢 Alta | Henrique Diniz | Em Monitoramento |
| **O4** | 🟢 | Automação proativa de pendências e acompanhamentos recorrentes | 4 | 4 | **16** | = | 🟢 Alta | Jaime Almeida | Em Monitoramento |
| **O5** | 🟢 | Reutilização estruturada do conhecimento institucional | 3 | 4 | **12** | = | 🟠 Alta | Leonardo Ramos | Em Monitoramento |
| **O6** | 🟢 | Ampliação da capacidade analítica do PMO | 3 | 5 | **15** | = | 🟢 Alta | Pedro Uchoa | Em Monitoramento |
| **O7** | 🟢 | Pipeline autoral de PLN com desempenho suficiente para sustentar o roteamento já na Sprint 3 | 4 | 4 | **16** | novo | 🟢 Alta | Pedro Uchoa | Em Monitoramento |

## 3.3 Histórico de acompanhamento e justificativa das reavaliações

Cada linha abaixo registra o que foi observado na sprint e o que sustentou a mudança de avaliação. Itens sem alteração não aparecem.

| ID | Sprint | O que foi observado | Decisão |
| :---: | :---: | --- | --- |
| R01 | 2 | O MVP passou a operar sobre dados sintéticos e mockados por decisão de escopo, e não por indisponibilidade. O classificador foi treinado com 5.353 exemplos gerados pela equipe. A dependência de dados reais deslocou-se para a fase de integração. | Probabilidade de 4 para 3. Severidade de 20 para 15 |
| R03 | 2 | O caminho de RAG passou a citar a fonte de cada resposta, e o classificador adotou limiares conservadores de 0,925 e 0,950 justamente para não acionar um handler com baixa confiança. A mitigação foi implementada, não apenas planejada. | Probabilidade de 4 para 3. Severidade de 20 para 15 |
| R05 | 2 | Não exercido na sprint, uma vez que a base utilizada é sintética e controlada pela própria equipe. | Probabilidade de 4 para 3. Severidade de 16 para 12 |
| R07 | 2 | Dois requisitos funcionais novos entraram no escopo, RF09 e RF10, tratando de sugestão proativa e controle da proatividade. A ampliação decorreu do artefato de prototipação exploratória, cuja questão era exatamente o regime de iniciativa do agente, e portanto foi deliberada. | Avaliação mantida. Registrado que a ampliação foi controlada |
| R08 | 2 | Na data desta apuração, com a sprint ainda em curso, quatro itens da Estratégia Técnica seguiam em andamento: deploy em nuvem, diagrama de classes, API de recebimento de áudio e detalhamento da API de Text-to-Speech. Todos estão previstos para o fechamento, mas a concentração de itens abertos próxima ao prazo é o sinal que o risco descreve. | Avaliação mantida em 16. Acompanhamento elevado para verificação diária até o fechamento |
| R10 | 2 | A Seção 5.2 do `Projeto.md` foi entregue descrevendo uma interface própria de chat como ponto de entrada da arquitetura, sem citar o Teams, enquanto as Seções 2.4.3 e 2.8 e o RNF08 mantinham o Teams como canal do produto. A mesma seção tratava o provedor de LLM da bancada de teste como decisão de produto. Nenhum dos dois foi detectado na revisão do merge request. | **Materializado.** Probabilidade de 3 para 4. Severidade de 9 para 12 |
| R11 | 2 | Quatro merge requests permaneceram abertos no fechamento, contendo entregas prontas: modelo lógico de dados, atualização dos requisitos funcionais, requisitos das APIs de voz e correção do feedback da Sprint 1. | Risco novo, registrado com severidade 16 |
| R12 | 2 | A documentação passou a referir-se ao componente de geração como LLM genérico, sem provedor definido, após a constatação de que o provedor usado na bancada não constituía decisão de produto. A Sprint 3 exige integração funcional do STT com o algoritmo de PLN. | Risco novo, registrado com severidade 16 |
| O3 | 2 | A separação entre canal, núcleo de PLN, RAG e orquestração permitiu trocar o provedor de LLM na documentação sem alterar nenhum outro componente, e permitiu construir a bancada de teste sem depender da homologação do canal corporativo. A modularidade deixou de ser projeto e passou a ter demonstração. | Impacto de 4 para 5. Severidade de 15 para 20 |
| O7 | 2 | O pipeline autoral atingiu F1-macro de 0,9379 na macrointenção no conjunto de teste, suficiente para sustentar o roteamento entre consulta, transação e alerta, ainda que a intenção específica permaneça em 0,6777. | Oportunidade nova, registrada com severidade 16 |

## 3.4 Efetividade das ações aplicadas

A Sprint 1 definiu seis ações de melhoria. Esta é a apuração de cada uma.

| Ação definida na Sprint 1 | Efetividade | Evidência |
| --- | :---: | --- |
| Antecipar entregas para quinta-feira e reservar tempo para revisão | ⚠️ Parcial | Concentração nos dois últimos dias caiu de 65% para 53%, sem atingir a meta de 40%. Reduziu, mas não resolveu |
| Promover maior integração entre frentes | ✅ Efetiva | Integrantes tocando mais de um arquivo subiu de 3 para 6 de 6; amplitude caiu de 4,6× para 2,2×, abaixo da meta |
| Reforçar DoR, DoD, labels, milestones e assignee nas issues | ✅ Efetiva | Os merge requests da sprint trazem checklist e milestone `Sprint 02` preenchidos |
| Padronizar o título do merge request antes do merge | ❌ Não efetiva | 7 de 20 commits de squash na convenção (35%), contra 6 de 19 (32%) na Sprint 1. Ação reformulada na Seção 2.2.5 |
| Usar as dailies para registrar feito, evidências, próximos passos e impedimentos | ✅ Efetiva | Registro mantido no Slack, canal oficial definido na Seção 5.7 |
| Registrar decisões relevantes em canal oficial ou issue | ⚠️ Parcial | Decisões técnicas ficaram registradas nas seções 8.6 e 8.7 com benchmark, mas a mudança de provedor de LLM e de canal não teve registro até ser detectada em revisão cruzada |

Das seis ações, três foram efetivas, duas foram parciais e uma não produziu efeito. A que falhou — padronizar o título do merge request — e as duas parciais têm a mesma causa: dependiam de alguém lembrar no momento certo, sem ponto de verificação no fluxo. As ações da Seção 2.2.5 foram reescritas para ter gatilho — item de checklist antes da aprovação, marco de integração na quarta-feira — em vez de intenção.

O contraste com o registro da daily é útil: essa ação funcionou porque o Slack já era o canal onde o grupo trabalha, e o registro não dependeu de disciplina adicional. Ações que se apoiam no fluxo existente sobrevivem; as que exigem um passo novo, não.

## 3.5 Matriz probabilidade × impacto

Posição vigente de cada item. Riscos em vermelho, oportunidades em verde.

| P \ I | 1 | 2 | 3 | 4 | 5 |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **5** | | | | | |
| **4** | | | 🔴 R10 | 🔴 R07 · 🔴 R08 · 🔴 R11 · 🔴 R12 · 🟢 O1 · 🟢 O4 · 🟢 O7 | 🔴 R02 · 🟢 O3 |
| **3** | | | | 🔴 R06 · 🔴 R09 · 🔴 R05 · 🟢 O5 | 🔴 R01 · 🔴 R03 · 🔴 R04 · 🟢 O2 · 🟢 O6 |
| **2** | | | | | |
| **1** | | | | | |

## 3.6 Análise dos três itens mais críticos

Aplicando severidade = probabilidade × impacto, o único risco em 20 é **R02**. Cinco itens empatam em 16, e os dois escolhidos como críticos são **R08** e **R11**, por serem os que já produziram efeito observável nesta sprint.

**R02 — Integrações com o ecossistema Microsoft.** Permanece em 20 e torna-se determinante na Sprint 3, que exige a API de recebimento de áudio integrada ao Speech-to-Text. A disponibilidade do Azure AI Speech no ambiente do parceiro continua dependendo de confirmação com a GTI, conforme registrado na Seção 3.4.2.1 do `Projeto.md`. A bancada de teste construída na Sprint 2 reduziu a exposição, por permitir validar o pipeline sem o canal homologado, mas não elimina a dependência: a entrega final precisa do ambiente.

**R08 — Tempo insuficiente.** A avaliação permanece em 16, mas o acompanhamento subiu. Na data desta apuração, com a sprint ainda aberta, quatro itens da Estratégia Técnica seguiam em andamento, e o mais pesado deles — o deploy em nuvem com registro reproduzível e capturas de tela — é também o que menos se comprime em cima da hora. A Sprint 3 acrescenta a implementação do backend de áudio e a integração do Speech-to-Text com o PLN. O tratamento não é trabalhar mais rápido: é dimensionar o que entra na sprint pela capacidade real e declarar cedo o que ficar fora, em vez de descobrir no fechamento.

**R11 — Entregas retidas em merge requests abertos.** É novo e já se manifestou. O efeito é específico: o trabalho existe e não é contabilizado, porque quem avalia o repositório olha `develop`. Na data desta apuração havia quatro merge requests abertos com entregas concluídas — modelo lógico de dados, atualização dos requisitos funcionais, requisitos das APIs de voz e correção do feedback da Sprint 1. Nenhum deles é trabalho pendente; todos são trabalho pronto e invisível. O tratamento é o marco de integração de quarta-feira definido na Seção 2.2.5, com bloqueio declarado na issue quando a revisão não puder acontecer no prazo.

## 3.7 Mecanismo contínuo de acompanhamento

O acompanhamento dos riscos será feito de forma contínua durante a sprint, com registro simples e verificável:

| Momento | Responsável | Ação esperada | Evidência |
| --- | --- | --- | --- |
| Daily | Responsável pela tarefa | Informar impedimentos, dependências e mudanças de probabilidade ou impacto. | Mensagem no canal oficial ou comentário na issue. |
| Revisão de quinta-feira | Revisor da entrega | Verificar se a tarefa possui risco aberto, evidência suficiente e pendências de integração. | Comentário de revisão ou checklist atualizado. |
| Fechamento da sprint | Scrum Master | Consolidar riscos materializados, riscos reduzidos e novos riscos para a sprint seguinte. | Atualização da seção de riscos em `GestaoProjeto.md` ou issue de retrospectiva. |

Um risco deve ser atualizado quando houver aumento de probabilidade, aumento de impacto, materialização do problema, remoção da causa ou definição de nova ação de mitigação. Quando o risco afetar prazo, escopo ou qualidade da entrega, ele deve ser comunicado no mesmo dia no canal oficial e vinculado à issue correspondente.

# 4. Matriz de papéis e responsabilidades

A matriz varia a cada sprint. A intenção não é fixar cargos permanentes para o módulo, mas registrar qual frente cada integrante assumiu na sprint corrente, deixando claro quem respondeu por cada artefato e reduzindo centralização de trabalho. As sprints anteriores permanecem registradas para que a rotação seja verificável.

## 4.1 Matriz da Sprint 1

Artefatos da Sprint 1:

- Entendimento do negócio;
- Especificação de requisitos funcionais e não funcionais;
- Gestão de projeto e configuração.

A coluna de issues liga cada integrante ao trabalho efetivamente registrado no board, e é por ela que a distribuição de carga pode ser conferida sem depender da descrição da frente.

| Integrante | Frente principal na Sprint 1 | Artefato relacionado | Issues no board | Responsabilidades e entregas esperadas |
| --- | --- | --- | --- | --- |
| Felipe Neves | Design: personas, jornadas do usuário e requisitos não funcionais | Entendimento do negócio / Requisitos | [#5](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/5), [#6](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/6), [#16](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/16) | Mapear perfis de usuário, consolidar personas, descrever jornadas e especificar os requisitos não funcionais da solução. |
| Henrique Diniz | Problema, análise SWOT e visão técnica da solução | Entendimento do negócio / base técnica | [#2](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/2), [#26](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/26) | Descrever o problema e a SWOT, explicar a visão técnica inicial, as tecnologias previstas e a relação entre arquitetura e necessidade do parceiro. |
| Jaime Almeida | Visão estratégica, ideação e estruturação do documento | Entendimento do negócio | [#4](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/4), [#37](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/37) | Estruturar a visão estratégica, registrar o brainstorm de features e organizar a estrutura do documento de projeto. |
| Leonardo Ramos | Gestão de projeto, configuração e automações do repositório | Gestão de projeto e configuração | [#9](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/9), [#20](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/20), [#22](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/22), [#24](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/24), [#25](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/25), [#26](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/26), [#27](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/27) | Estruturar `GestaoProjeto.md` e `GestaoConfiguracao.md`, implementar os hooks de qualidade e garantir aderência ao GitFlow e ao contrato de trabalho. |
| Pedro Uchoa | Requisitos funcionais, modelagem UML e business drivers | Requisitos / Entendimento do negócio | Sem vínculo recuperável¹ | Consolidar RF01–RF08 e as user stories, produzir a modelagem estática e dinâmica e documentar os business drivers e o contexto da indústria. |
| Wendel Feitosa | Modelagem do fluxo de negócio e matriz de riscos | Entendimento do negócio | [#10](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/10), [#34](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/34), [#35](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/35), [#36](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/36) | Modelar cadeia de valor e fluxos AS-IS e TO-BE, registrar riscos, classificar probabilidade e impacto e propor tratamento. |

¹ Os quatro commits de autoria do Pedro na Sprint 1 foram integrados por merge com squash e herdaram o título do merge request, sem o número da issue. O trabalho está no repositório e é atribuído a ele no campo de autor, mas não é recuperável pela busca por issue. É a mesma causa descrita na Seção 2.4, e a ação de correção está na Seção 2.5.


## 4.2 Matriz da Sprint 2

Artefatos da Sprint 2: Prototipação Exploratória, Estratégia Técnica da Solução e Gestão de Projetos Evolutiva.

| Integrante | Frente principal | Tasks sob sua responsabilidade | Situação da entrega |
| --- | --- | --- | --- |
| Felipe Neves | APIs de voz e planejamento | API de Text-to-Speech; API de recebimento de áudios; planejamento da Sprint 3 | ⚠️ API de Text-to-Speech entregue e mergeada na Seção 8.8. A especificação da API de recebimento de áudios não entrou nesta sprint e passa para a Sprint 3, onde o barema exige sua implementação. Parte do esforço foi para a bancada de teste em React, que não constava da divisão inicial |
| Henrique Diniz | Prototipação exploratória e gestão evolutiva | Questão de projeto (#97); construção do Protótipo 1 e diário (#99); comparação das alternativas (#104, com Wendel); análise da Sprint 2; matriz de papéis; contrato de convivência; gestão do processo; gestão de configuração | ✅ Entregues. Assumiu também a atualização da documentação da Sprint 1, originalmente do Pedro |
| Jaime Almeida | Prototipação e projeto arquitetural | Definição das duas alternativas e formatos (#98); construção do Protótipo 2 e diário (#100); execução do Protótipo 2 (#102); registro visual do Protótipo 2 (#103); projeto técnico e arquitetural | ✅ Entregues. Diagrama de componentes e cinco diagramas de sequência mergeados |
| Leonardo Ramos | Modelagem de dados e planejamento das sprints | Modelagem conceitual e lógica dos dados (com Wendel); processo de deploy em nuvem comercial; estratégia de entrega das Sprints 3, 4 e 5 | ✅ Todos entregues. Modelo conceitual, estratégia de entrega e a Seção 6 completa, com 17 subseções cobrindo hospedagem, banco, artefatos, fallback, desempenho, segurança e pendências de provisionamento |
| Pedro Uchoa | APIs de transcrição e algoritmo de PLN | API de Speech-to-Text; algoritmo de NLP e sua implementação; atualização da documentação da Sprint 1 | ✅ STT e algoritmo mergeados. A atualização da documentação da Sprint 1 foi redistribuída para o Henrique durante a sprint |
| Wendel Feitosa | Prototipação e dados | Execução do Protótipo 1 (#101); registro visual do Protótipo 1; comparação das alternativas (#104, com Henrique); inventário de decisões em aberto (#105); repertório de situações (#106); pilha de tecnologias; modelagem lógica dos dados | ✅ Todos entregues e mergeados, incluindo o modelo lógico na Seção 4.3 |

Com a sprint encerrada, dos dez itens da Estratégia Técnica um não entrou: a especificação da API de recebimento de áudios, que passa para a Sprint 3. O que a distribuição mostra é a concentração da prototipação em Wendel e Jaime, que a acumularam além de suas frentes técnicas. É isso que sustenta a reavaliação do risco R09 na Seção 3.2 e orienta a redistribuição da Sprint 3.

## 4.3 Rotação de papéis entre as sprints

A rotação é obrigatória. A tabela confronta a frente de cada integrante nas duas sprints.

| Integrante | Sprint 1 | Sprint 2 | Rotação |
| --- | --- | --- | :---: |
| Felipe Neves | Design: personas, jornadas e requisitos não funcionais | APIs de voz e planejamento de sprint | ✅ Mudança de frente |
| Henrique Diniz | Problema, análise SWOT e visão técnica da solução | Prototipação exploratória e gestão de projeto | ✅ Mudança de frente |
| Jaime Almeida | Visão estratégica, ideação e estruturação do documento | Prototipação e projeto arquitetural em UML | ✅ Mudança de frente |
| Leonardo Ramos | Gestão de projeto, configuração e hooks do repositório | Modelagem de dados, deploy e planejamento das sprints | ✅ Mudança de frente |
| Pedro Uchoa | Requisitos funcionais, modelagem UML e business drivers | APIs de transcrição e seleção do algoritmo de PLN | ⚠️ Rotação parcial: mudou o objeto, manteve a natureza de especificação técnica |
| Wendel Feitosa | Fluxo de negócio e matriz de riscos | Prototipação, pilha de tecnologias e modelo lógico de dados | ✅ Mudança de frente |

Duas observações para a distribuição da Sprint 3.

A rotação do Pedro é a única parcial: ele saiu da escrita de requisitos para a especificação técnica de APIs e algoritmos, o que muda o objeto mas mantém a natureza do trabalho. Na Sprint 3 ele deve ser alocado em implementação ou testes, e não em especificação.

O Henrique assumiu cinco dos seis itens da Gestão Evolutiva mais a atualização da documentação da Sprint 1, que era do Pedro. Concentrar um artefato inteiro em uma pessoa contraria o próprio objetivo da matriz, e a Sprint 3 deve distribuir os itens de gestão entre ao menos dois integrantes.

# 5. Contrato de convivência, SLA e rituais

O contrato define as regras práticas de trabalho do grupo. Ele prioriza comunicação clara, evidências objetivas, revisão antecipada e fechamento controlado da sprint.

## 5.1 Regra de ouro

Nenhuma entrega é considerada pronta sem evidência e revisão por outro integrante.

Isso vale para código, documentação, scripts, artefatos visuais e qualquer ajuste que impacte a entrega. A evidência pode ser um link, print, log de execução, trecho do GitLab, resumo de validação ou referência direta ao arquivo alterado.

## 5.2 Dailies

As dailies devem ser curtas, objetivas e focadas em visibilidade real do trabalho. Cada integrante deve responder aos quatro pontos abaixo:

1. O que fez desde a última daily;
2. Quais evidências comprovam o que foi feito;
3. O que vai fazer até a próxima daily;
4. Quais impedimentos existem.

Modelo de registro:

```text
Integrante:
O que fiz:
Evidências:
O que vou fazer:
Impedimentos:
```


Regras:

- A daily deve durar no máximo 15 minutos quando síncrona;
- Quem não puder participar deve registrar a atualização de forma assíncrona no canal oficial;
- Tarefas sem evidência não devem ser tratadas como concluídas;
- Impedimentos devem ser sinalizados no mesmo dia em que forem identificados.

## 5.3 Evidências de entrega

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

## 5.4 Entrega, revisão e fechamento

A equipe adota a seguinte regra de fechamento:

| Marco | Prazo | Regra |
| --- | --- | --- |
| Entrega das tarefas | Até quinta-feira | Cada responsável deve concluir sua parte e disponibilizar evidências. |
| Revisão por pares | Até quinta-feira | Outro integrante deve revisar a entrega antes do fechamento. |
| Ajustes finais | Quinta-feira, após revisão | Correções pequenas podem ser feitas após apontamentos. |
| Merge para main | Sexta-feira, como cadência padrão | O Scrum Master coordena o merge final da versão validada. Entregas prontas podem ser promovidas antes, desde que sigam MR, pipeline, aprovação e DoD. |
| Fechamento formal | Só se necessário | O fechamento deve ocorrer apenas quando houver necessidade real de consolidar versão, resolver pendências ou registrar decisão final. |

Essa regra existe para evitar acúmulo de revisão na sexta-feira e reduzir risco de merge apressado sem validação.

## 5.5 Resolução de impasses

Quando houver discordância técnica ou de escopo, o grupo deve seguir a ordem abaixo:

1. Discussão objetiva entre os envolvidos, usando evidências e critérios do barema;
2. Consulta ao responsável pela frente afetada;
3. Decisão por maioria simples quando houver mais de uma alternativa aceitável;
4. Em caso de empate ou risco relevante, consulta ao orientador.

A decisão final deve ser registrada no canal oficial ou na issue relacionada.

## 5.6 Gestão de conflitos

Atrasos, falta de engajamento ou ausência de evidências devem ser tratados cedo.

Fluxo de gestão:

1. Feedback direto na daily ou no canal oficial;
2. Redistribuição ou apoio na tarefa, se houver risco de atraso;
3. Registro formal na retrospectiva da sprint, quando o problema se repetir;
4. Escalonamento ao orientador se o comportamento comprometer a entrega do grupo.

O foco da gestão de conflitos é proteger a entrega e a colaboração, não expor integrantes.

## 5.7 Comunicação oficial

Os canais oficiais de comunicação da equipe são o **grupo do WhatsApp** e o **Slack do grupo**. O WhatsApp será usado para alinhamentos rápidos, avisos urgentes, confirmação de presença e sinalização imediata de impedimentos. O Slack será usado para registros mais estruturados, decisões de trabalho, links de evidências, acompanhamento assíncrono e organização de discussões por tema quando necessário.

As decisões relevantes devem ser registradas em um desses canais oficiais ou na própria issue do GitLab. Quando uma conversa começar de forma informal, a decisão final precisa ser consolidada no WhatsApp, no Slack ou na issue relacionada para manter rastreabilidade.

Devem ser registrados:

- Mudanças de escopo;
- Impedimentos;
- Decisões técnicas;
- Alteração de responsável;
- Critérios de aceite;
- Evidências de entrega;
- Aprovações e revisões.

Discussões informais podem acontecer em outros canais, mas a decisão final precisa ficar rastreável. Para conflitos entre registros, prevalece a ordem: issue do GitLab, Slack do grupo e, por fim, WhatsApp, desde que a mensagem identifique a decisão tomada, os responsáveis e a data do acordo.


## 5.8 Registro de revisões do contrato

O contrato firmado na Sprint 1 foi revisado ao fim da Sprint 2. Três regras foram alteradas, todas a partir de indicador medido, e não de percepção.

| Regra | Redação anterior | Nova redação | Motivo |
| --- | --- | --- | --- |
| Registro da daily (5.2) | Registro assíncrono no canal oficial apenas para quem não puder participar da daily síncrona | **O Slack passa a ser o canal de registro da daily para todos**, independentemente de participação na daily síncrona, que permanece como momento de alinhamento | Formalização da prática já adotada. O registro vinha sendo mantido no Slack por todo o grupo, e não apenas por quem faltava, mas o contrato ainda descrevia o registro como exceção |
| Fechamento semanal (5.4) | Antecipar entregas para quinta-feira e reservar tempo para revisão por pares | **Quarta-feira passa a ser o marco de integração:** todo merge request aberto até quarta deve estar revisado e mergeado, ou ter o bloqueio declarado na issue. Quinta permanece como marco de entrega | Quatro merge requests abertos no fechamento da Sprint 2, com entregas prontas invisíveis em `develop`. Antecipar a entrega não bastou, porque a integração continuou no fim |
| Evidências de entrega (5.3) | Lista do que conta como evidência | Acrescenta-se: **quem revisa uma seção que referencia outra deve conferir a coerência entre as duas e registrar no comentário de revisão quais seções conferiu** | A Seção 5.2 do `Projeto.md` foi aprovada contradizendo as Seções 2.4.3, 2.8 e o RNF08, sem que a revisão detectasse |

As demais regras foram mantidas sem alteração: a regra de ouro de 5.1, a resolução de impasses de 5.5, a gestão de conflitos de 5.6 e a comunicação oficial de 5.7 não apresentaram problema durante a Sprint 2 e seguem vigentes.

# 6. Planejamento da Sprint 3

## 6.1 Visão geral da planning

A Sprint 3 tem três artefatos:

- Desenvolvimento e Documentação Técnica do Projeto, com os itens marcados para S3: API de recebimento de áudio, início da implementação do algoritmo de PLN integrado ao Speech-to-Text e frontend básico integrado ao backend;
- Planejamento de Testes Sistêmicos, com testes funcionais, de requisitos não funcionais, de integração com módulo de cache e roteiro de usabilidade;
- Gestão de Projetos Evolutiva, com a análise da Sprint 3 e o planejamento da Sprint 4.

A capacidade considera 6 integrantes com 16 horas cada, totalizando 96 horas. Diferente da Sprint 2, o backlog carrega também os pendentes da sprint anterior, que entram com prioridade máxima por serem pré-requisito dos itens novos.

**Mudança na estimativa.** Na Sprint 2 todas as 48 tasks foram estimadas como `G`, o que torna a escala inútil para sequenciar trabalho. Nesta sprint as tasks foram quebradas até caberem majoritariamente nas faixas `P` e `M`, conforme a ação de melhoria registrada na Seção 2.2.5.

## 6.2 Backlog planejado no Kanban

Toda task abaixo deve ser criada como issue no GitLab, vinculada à milestone `Sprint 03`, com descrição, tipo, prioridade, estimativa, DoR e DoD preenchidos antes de sair de `Open`.

### Pendentes da Sprint 2 — prioridade máxima

| # | Task | Tipo | Est. | Prioridade | DoR | DoD |
| :---: | --- | :---: | :---: | :---: | --- | --- |
| 1 | Especificar a API de Text-to-Speech: endpoints, métodos, parâmetros, respostas e exemplos | Documentação | M | 🔴 Crítica | Provedor de síntese definido e requisitos da Seção 8.6 revisados | Seção com exemplos de requisição e resposta, códigos de erro e limites, revisada por par |
| 2 | Elaborar o diagrama de classes da solução | Documentação | G | 🔴 Crítica | Modelo lógico de dados mergeado em `develop` | Diagrama com arquivo-fonte versionado em `docs/diagrams`, seção 5.1 preenchida e referenciada no sumário |
| 3 | Documentar o processo de deploy do algoritmo em nuvem comercial | Documentação | G | 🔴 Crítica | Provedor de nuvem escolhido e conta criada | Passo a passo reproduzível com capturas de tela, seções 6.1 a 6.3 e 10.1 a 10.2 preenchidas |
| 4 | Acrescentar exemplos de código e bibliotecas à seção do algoritmo de PLN | Documentação | P | 🟠 Alta | Notebook do classificador mergeado | Seção 8.7 com bibliotecas nomeadas, passos de configuração e exemplos executáveis de entrada e saída |
| 5 | Complementar a pilha de tecnologias com plataforma de execução e escalabilidade | Documentação | P | 🟠 Alta | Arquitetura da Seção 5.2 estável | Pilha cobrindo web e mobile, com tratamento de confiabilidade e escalabilidade |
| 6 | Definir e documentar o modelo físico de dados | Documentação | M | 🟠 Alta | Modelo lógico aprovado | Seção 4.4 com tabelas, tipos, índices e script de criação em `src/database` |
| 7 | Integrar os quatro merge requests abertos da Sprint 2 em `develop` | Chore | M | 🔴 Crítica | Conflitos mapeados e ordem de merge acordada | Os quatro MRs mergeados, sumário do `Projeto.md` regenerado e sem âncora quebrada |

### Artefato 1 — Desenvolvimento e Documentação Técnica

| # | Task | Tipo | Est. | Prioridade | DoR | DoD |
| :---: | --- | :---: | :---: | :---: | --- | --- |
| 8 | Implementar o endpoint de upload de áudio no backend | Desenvolvimento | G | 🔴 Crítica | Formatos e limites definidos na task 1 da Sprint 2 | Endpoint funcional aceitando os formatos especificados, com validação e retorno de erro tratado |
| 9 | Implementar o tratamento de erros do endpoint de áudio | Desenvolvimento | M | 🔴 Crítica | Endpoint de upload existente | Respostas 400 e 413 para formato inválido e arquivo acima do limite, com corpo estruturado |
| 10 | Documentar a API de recebimento de áudio | Documentação | M | 🟠 Alta | Endpoint implementado | Endpoints, headers, payloads, códigos de resposta e estrutura de retorno, com exemplos |
| 11 | Integrar a API de Speech-to-Text ao endpoint de upload | Desenvolvimento | G | 🔴 Crítica | Credencial do Azure AI Speech disponível | Áudio enviado retorna transcrição em `pt-BR` pela API da aplicação |
| 12 | Integrar a transcrição ao pipeline de classificação de intenções | Desenvolvimento | G | 🔴 Crítica | Classificador serializado carregável no serviço | Transcrição classificada em macrointenção e intenção, com confiança retornada |
| 13 | Escrever testes de sucesso e falha da integração áudio → PLN | Teste | M | 🟠 Alta | Integração funcional | Casos cobrindo áudio válido, formato inválido, áudio sem fala e falha do provedor |
| 14 | Integrar o frontend às APIs do backend, com validação e feedback | Desenvolvimento | G | 🟠 Alta | Endpoints estáveis | Envio de texto e áudio pela interface, com exibição de resultado, erro e estado de carregamento |
| 15 | Documentar estrutura, componentes e instruções de uso do frontend | Documentação | M | 🟡 Média | Frontend integrado | Seção descrevendo componentes, integração com as APIs e passo a passo de execução |

### Artefato 2 — Planejamento de Testes Sistêmicos

| # | Task | Tipo | Est. | Prioridade | DoR | DoD |
| :---: | --- | :---: | :---: | :---: | --- | --- |
| 16 | Derivar os testes funcionais a partir de RF01 a RF10 | Documentação | G | 🔴 Crítica | Requisitos funcionais atualizados mergeados | Cada RF com ao menos um cenário positivo e um negativo, propósito e instrução de execução |
| 17 | Planejar os testes de desempenho dos requisitos não funcionais | Documentação | M | 🔴 Crítica | Métricas de aceitação dos RNFs revisadas | Testes de latência e carga com meta, ferramenta e critério de aprovação declarados |
| 18 | Planejar os demais testes de RNFs | Documentação | M | 🟠 Alta | RNFs revisados | Cenários positivos e negativos por RNF, com justificativa de abrangência |
| 19 | Planejar os testes de integração com serviços externos | Documentação | M | 🟠 Alta | Integrações da Sprint 3 definidas | Cenários de comunicação e de falha, com ferramentas e validação de resultado |
| 20 | Implementar o módulo de cache VHS para as respostas da API externa | Desenvolvimento | G | 🔴 Crítica | Integração com o provedor de transcrição funcionando | Requisições repetidas atendidas pelo cache, com teste comprovando a ausência de nova chamada externa |
| 21 | Elaborar o roteiro de testes de usabilidade com escala SUS | Documentação | M | 🟠 Alta | Frontend integrado e navegável | Roteiro com cenários, perfis dos cinco participantes externos e questionário SUS |
| 22 | Registrar as ferramentas e bibliotecas de teste adotadas | Documentação | P | 🟡 Média | Testes planejados | Lista com finalidade de cada ferramenta e onde é utilizada |

### Artefato 3 — Gestão de Projetos Evolutiva

| # | Task | Tipo | Est. | Prioridade | DoR | DoD |
| :---: | --- | :---: | :---: | :---: | --- | --- |
| 23 | Apurar os indicadores da Sprint 3 e comparar com as metas da Sprint 2 | Documentação | M | 🟠 Alta | Sprint encerrada e MRs integrados | Tabela comparativa das três sprints, com resultado de cada meta |
| 24 | Atualizar a matriz de risco com status, reavaliação e novos itens | Documentação | M | 🟠 Alta | Retrospectiva realizada | Status revisado item a item, histórico acrescido e efetividade das ações apurada |
| 25 | Montar a matriz de papéis da Sprint 3 com rotação evidenciada | Documentação | P | 🟠 Alta | Frentes da sprint definidas | Matriz com rotação conferida contra as Sprints 1 e 2 |
| 26 | Revisar o contrato de convivência e registrar alterações | Documentação | P | 🟡 Média | Retrospectiva realizada | Registro de revisões atualizado, com motivo de cada mudança |
| 27 | Planejar a Sprint 4 no Kanban | Documentação | M | 🟠 Alta | Barema da Sprint 4 lido | Tasks estimadas, priorizadas e detalhadas com DoR e DoD |
| 28 | Atualizar o fluxo de gitflow e as políticas de branch | Documentação | P | 🟡 Média | Práticas da Sprint 3 observadas | `GestaoConfiguracao.md` atualizado com exemplos praticados na sprint |

### Sequenciamento

As tasks 1 a 7 são pré-requisito e devem fechar na primeira metade da sprint. A cadeia crítica é **8 → 9 → 11 → 12 → 13**, porque cada elo depende do anterior estar funcional; ela deve começar imediatamente após a task 7. As tasks 16 a 22 dependem dos requisitos atualizados estarem em `develop`, o que a task 7 resolve. As tasks 23 a 28 só podem fechar com a sprint encerrada.

## 6.3 Escala de estimativa

| Tamanho | Critério |
| --- | --- |
| PP | Até 15 minutos |
| P | Até 30 minutos |
| M | De 30 a 60 minutos |
| G | De 60 a 120 minutos |

Tarefas maiores que G devem ser quebradas antes de entrarem na sprint.

# 7. Gestão do processo de desenvolvimento do grupo

## 7.1 Fluxo de trabalho no Kanban

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

## 7.2 Regras obrigatórias para issues

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

## 7.3 Critérios de Ready e Done

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

## 7.4 Commits, merge requests e evidências

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

## 7.5 SLA operacional

| Situação | SLA | Responsável por acionar |
| --- | --- | --- |
| Atualização de daily | Até o horário combinado da daily | Cada integrante |
| Registro de impedimento | No mesmo dia da identificação | Responsável pela tarefa |
| Primeira resposta a impedimento | Até 24 horas | Scrum Master ou responsável pela frente |
| Entrega para revisão | Até quinta-feira | Responsável pela tarefa |
| Revisão por pares | Até quinta-feira | Reviewer definido |
| Promoção para `hmg` | Quando a entrega estiver pronta e revisada | Responsável pela frente e Scrum Master |
| Merge final para `main` | Sexta-feira como cadência padrão, ou antes se houver entrega pronta e aprovada | Scrum Master |

## 7.6 Função do scrum master no merge

O Scrum Master não é o único responsável pela qualidade das entregas, mas é o responsável por coordenar o merge final da sprint.

Antes do merge para `main`, o Scrum Master deve verificar:

- Se as tarefas previstas para a versão estão revisadas;
- Se existem evidências mínimas de entrega;
- Se os Merge Requests necessários foram aprovados;
- Se não há impedimento crítico aberto;
- Se o conteúdo de `hmg` representa a versão que o grupo deseja entregar;
- Se a promoção seguiu o fluxo obrigatório `feature/* -> develop -> hmg -> main`.

Na sexta-feira, o Scrum Master executa ou coordena o merge para `main` e comunica o grupo sobre o estado final da entrega. Quando uma entrega estiver pronta antes da sexta-feira, o Scrum Master pode coordenar a promoção antecipada, desde que exista Merge Request, aprovação, evidência e validação.
