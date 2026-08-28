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
    - [Artefato 1 — Desenvolvimento e Documentação Técnica do Projeto](#artefato-1-desenvolvimento-e-documentação-técnica-do-projeto)
    - [Artefato 2 — Planejamento de Testes Sistêmicos](#artefato-2-planejamento-de-testes-sistêmicos)
    - [Artefato 3 — Gestão de Projetos Evolutiva](#artefato-3-gestão-de-projetos-evolutiva)
    - [Sequenciamento](#sequenciamento)
    - [Distribuição das estimativas](#distribuição-das-estimativas)
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

**A sprint produziu decisão técnica com evidência, e não com preferência.** Tanto a escolha da API de transcrição quanto a do algoritmo de PLN foram registradas com benchmark, critério de comparação e limitações declaradas. A seção de PLN, em particular, publica a tabela completa das quatorze combinações avaliadas, declara que o resultado de 0,7401 de F1-macro na intenção específica fica abaixo do mínimo de 0,80 exigido pelo RNF06 e nomeia nove ressalvas antes de tratar a escolha como definitiva.

### 2.2.4 Pontos de melhoria

**O squash continua quebrando a rastreabilidade, e a ação definida não resolveu.** Apenas 7 dos 20 commits de squash seguem a convenção — 35%, praticamente o mesmo 32% da Sprint 1. E o número é generoso: ele considera apenas o prefixo `<tipo>:`. Aplicando a regra completa que o hook `commit-msg` exige, que inclui a referência `#N` à issue, restam 5 dos 20 — 25%. A ação registrada na Sprint 1 foi "padronizar o título do merge request antes de aprovar o merge", e ela não foi cumprida. Dos títulos gerados, aparecem casos como `feat/implementar-frontend-inicial-mockado` e `Docs/comparacao das alternativas e documentação`, que são nomes de branch e não mensagens de commit. A ação precisa deixar de depender de lembrança e virar verificação no fluxo.

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
| **R11** | 🔴 | Entregas concluídas que permanecem em merge requests não integrados ao `develop` | 4 | 4 | **16** | novo | 🟠 Alta | Leonardo Ramos | **Materializado** |
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
| R03 | 2 | O caminho de RAG passou a citar a fonte de cada resposta, e o classificador adotou limiares calibrados de 0,550 e 0,700 justamente para não acionar um handler com baixa confiança: no conjunto de teste, 26,9% dos pedidos são desviados para o fluxo genérico e a acurácia entre os aceitos sobe de 0,7383 para 0,8775. A mitigação foi implementada e medida, não apenas planejada. | Probabilidade de 4 para 3. Severidade de 20 para 15 |
| R05 | 2 | Não exercido na sprint, uma vez que a base utilizada é sintética e controlada pela própria equipe. | Probabilidade de 4 para 3. Severidade de 16 para 12 |
| R07 | 2 | Dois requisitos funcionais novos entraram no escopo, RF09 e RF10, tratando de sugestão proativa e controle da proatividade. A ampliação decorreu do artefato de prototipação exploratória, cuja questão era exatamente o regime de iniciativa do agente, e portanto foi deliberada. | Avaliação mantida. Registrado que a ampliação foi controlada |
| R08 | 2 | Quatro itens da Estratégia Técnica — deploy em nuvem, diagrama de classes, API de recebimento de áudio e detalhamento da API de Text-to-Speech — só fecharam nas últimas 48 horas da sprint. Todos entraram, mas a concentração no fim do prazo é exatamente o sinal que o risco descreve, e ela se confirmou nos indicadores: 26 dos 49 commits nos dois últimos dias. | Avaliação mantida em 16. Acompanhamento elevado para verificação diária até o fechamento |
| R10 | 2 | A Seção 5.2 do `Projeto.md` foi entregue descrevendo uma interface própria de chat como ponto de entrada da arquitetura, sem citar o Teams, enquanto as Seções 2.4.3 e 2.8 e o RNF08 mantinham o Teams como canal do produto. A mesma seção tratava o provedor de LLM da bancada de teste como decisão de produto. Nenhum dos dois foi detectado na revisão do merge request. | **Materializado.** Probabilidade de 3 para 4. Severidade de 9 para 12 |
| R11 | 2 | Quatro merge requests com entregas prontas — modelo lógico de dados, atualização dos requisitos funcionais, requisitos das APIs de voz e correção do feedback da Sprint 1 — permaneceram abertos até o último dia. O risco se concretizou: durante a maior parte da sprint esse trabalho existia e não era visível em `develop`. Os quatro foram integrados na revisão de fechamento. | **Materializado**, com contingência aplicada. Registrado com severidade 16. A mitigação estrutural é o marco de integração de quarta-feira definido na Seção 2.2.5 |
| R12 | 2 | A documentação passou a referir-se ao componente de geração como LLM genérico, sem provedor definido, após a constatação de que o provedor usado na bancada não constituía decisão de produto. A Sprint 3 exige integração funcional do STT com o algoritmo de PLN. | Risco novo, registrado com severidade 16 |
| O3 | 2 | A separação entre canal, núcleo de PLN, RAG e orquestração permitiu trocar o provedor de LLM na documentação sem alterar nenhum outro componente, e permitiu construir a bancada de teste sem depender da homologação do canal corporativo. A modularidade deixou de ser projeto e passou a ter demonstração. | Impacto de 4 para 5. Severidade de 15 para 20 |
| O7 | 2 | O pipeline autoral atingiu F1-macro de 0,9477 na macrointenção no conjunto de teste, suficiente para sustentar o roteamento entre consulta, transação e alerta, ainda que a intenção específica permaneça em 0,7401 — abaixo do mínimo de 0,80 do RNF06. | Oportunidade nova, registrada com severidade 16 |

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

**R08 — Tempo insuficiente.** A avaliação permanece em 16, mas o acompanhamento subiu. Quatro itens da Estratégia Técnica só fecharam nas últimas 48 horas, e o mais pesado deles — o deploy em nuvem com registro reproduzível e capturas de tela — é também o que menos se comprime em cima da hora. Tudo entrou, mas entrou no limite: 26 dos 49 commits da sprint estão nesses dois dias. A Sprint 3 acrescenta a implementação do backend de áudio e a integração do Speech-to-Text com o PLN. O tratamento não é trabalhar mais rápido: é dimensionar o que entra na sprint pela capacidade real e declarar cedo o que ficar fora, em vez de descobrir no fechamento.

**R11 — Entregas retidas em merge requests abertos.** É novo e materializou-se dentro da própria sprint em que foi identificado. O efeito é específico: o trabalho existe e não é contabilizado, porque quem avalia o repositório olha `develop`. Quatro merge requests com entregas concluídas — modelo lógico de dados, atualização dos requisitos funcionais, requisitos das APIs de voz e correção do feedback da Sprint 1 — ficaram retidos até o último dia. Nenhum deles era trabalho pendente; todos eram trabalho pronto e invisível.

A contingência funcionou: os quatro foram integrados na revisão de fechamento, e nenhum item da Estratégia Técnica ficou fora de `develop`. Mas a contingência é uma correção de última hora, não um controle — ela dependeu de alguém varrer os MRs abertos no dia do fechamento. A mitigação estrutural é o marco de integração de quarta-feira definido na Seção 2.2.5, com bloqueio declarado na issue quando a revisão não puder acontecer no prazo. O item segue em acompanhamento na Sprint 3 justamente porque o que resolveu na Sprint 2 não foi o processo, e sim a varredura manual.

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
| Felipe Neves | APIs de voz e planejamento | API de Text-to-Speech; API de recebimento de áudios; planejamento da Sprint 3 | ✅ Entregues. API de Text-to-Speech na Seção 8.9 e especificação da API de recebimento de áudios na Seção 8.7, ambas mergeadas. A implementação do endpoint de áudio permanece na Sprint 3, conforme o barema. Parte do esforço foi para a bancada de teste em React, que não constava da divisão inicial |
| Henrique Diniz | Prototipação exploratória e gestão evolutiva | Questão de projeto (#97); construção do Protótipo 1 e diário (#99); comparação das alternativas (#104, com Wendel); análise da Sprint 2; matriz de papéis; contrato de convivência; gestão do processo; gestão de configuração | ✅ Entregues. Assumiu também a atualização da documentação da Sprint 1, originalmente do Pedro |
| Jaime Almeida | Prototipação e projeto arquitetural | Definição das duas alternativas e formatos (#98); construção do Protótipo 2 e diário (#100); execução do Protótipo 2 (#102); registro visual do Protótipo 2 (#103); projeto técnico e arquitetural | ✅ Entregues. Diagrama de componentes e cinco diagramas de sequência mergeados |
| Leonardo Ramos | Modelagem de dados e planejamento das sprints | Modelagem conceitual e lógica dos dados (com Wendel); processo de deploy em nuvem comercial; estratégia de entrega das Sprints 3, 4 e 5 | ✅ Todos entregues. Modelo conceitual, estratégia de entrega e a Seção 6 completa, com 17 subseções cobrindo hospedagem, banco, artefatos, fallback, desempenho, segurança e pendências de provisionamento |
| Pedro Uchoa | APIs de transcrição e algoritmo de PLN | API de Speech-to-Text; algoritmo de NLP e sua implementação; atualização da documentação da Sprint 1 | ✅ STT e algoritmo mergeados. A atualização da documentação da Sprint 1 foi redistribuída para o Henrique durante a sprint |
| Wendel Feitosa | Prototipação e dados | Execução do Protótipo 1 (#101); registro visual do Protótipo 1; comparação das alternativas (#104, com Henrique); inventário de decisões em aberto (#105); repertório de situações (#106); pilha de tecnologias; modelagem lógica dos dados | ✅ Todos entregues e mergeados, incluindo o modelo lógico na Seção 4.3 |

Com a sprint encerrada e os merge requests integrados, os dez itens da Estratégia Técnica entraram em `develop`, incluindo a especificação da API de recebimento de áudios, que fechou na revisão final. O que a distribuição mostra é a concentração da prototipação em Wendel e Jaime, que a acumularam além de suas frentes técnicas. É isso que sustenta a reavaliação do risco R09 na Seção 3.2 e orienta a redistribuição da Sprint 3.

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

A capacidade considera 6 integrantes com 16 horas cada, totalizando 96 horas. A Sprint 2 fechou sem pendências: os dez itens da Estratégia Técnica entraram em `develop` e os quatro merge requests retidos foram integrados na revisão de fechamento. O backlog abaixo é, portanto, inteiramente novo, e a capacidade não precisa ser reservada para dívida da sprint anterior.

**Estimativa.** Na Sprint 2 todas as 48 tasks foram estimadas como `G`, o que torna a escala inútil para sequenciar trabalho. A ação de melhoria da Seção 2.2.5 previa quebrar as tasks até a faixa `M`. O board da Sprint 3 avança pouco nesse ponto — 16 tasks em `G` contra 10 em `M` —, e a apuração está registrada na Seção 6.2.

## 6.2 Backlog planejado no Kanban

As 26 tasks abaixo estão criadas como issue no GitLab, vinculadas à milestone `Sprint 03`, com tipo, prioridade, estimativa, DoR e DoD preenchidos. A numeração desta seção é a numeração real do board: cada linha aponta para a issue correspondente, de modo que o documento e o Kanban possam ser conferidos um contra o outro sem tradução.

### Artefato 1 — Desenvolvimento e Documentação Técnica do Projeto

| Issue | Task | Tipo | Est. | Prioridade | DoR | DoD |
| :---: | --- | :---: | :---: | :---: | --- | --- |
| [#119](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/119) | Implementar o endpoint de upload de áudio na API | Backend | G | Alta | Contrato da Seção 8.7 do `Projeto.md` mergeado em `develop` | Endpoint `POST /api/audio` recebendo `multipart/form-data` e devolvendo resposta estruturada |
| [#120](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/120) | Implementar a validação de formatos e o tratamento de erros do upload | Backend | M | Alta | Endpoint da #119 funcional | Formato, duração e tamanho validados antes da chamada externa, com os códigos 400, 413, 422 e 429 da Seção 8.7.6 |
| [#121](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/121) | Documentar a API de upload de áudio no Projeto.md | Documentação | M | Alta | Endpoint implementado e validações definidas | Seção 8.7 atualizada com o comportamento real, incluindo exemplos de requisição e resposta conferidos contra a implementação |
| [#122](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/122) | Integrar a API de Speech-to-Text ao fluxo de upload de áudio | Backend | G | Alta | Credencial do Azure AI Speech disponível e endpoint da #119 funcional | Áudio enviado retorna transcrição em `pt-BR` pela API da aplicação, com tratamento de falha do provedor |
| [#123](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/123) | Implementar o pré-processamento textual do pipeline de PLN | Código | G | Alta | `config_22` da Seção 8.10.3 confirmada como configuração vigente | `preprocess_text` reproduzindo no serviço exatamente a transformação ajustada no treino |
| [#124](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/124) | Implementar o classificador de intenções do núcleo de PLN | Código | G | Alta | Artefatos de `src/notebooks/artefatos` carregáveis fora do notebook | Classificador hierárquico carregado no serviço, com `joblib`, Word2Vec e encoder BERT resolvidos no boot |
| [#125](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/125) | Medir a acurácia do classificador de intenções com dados sintéticos | Teste | M | Alta | Classificador da #124 respondendo no serviço | Métricas do serviço comparadas às da Seção 8.10.3, com divergência explicada |
| [#126](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/126) | Integrar o pipeline de PLN à API de entrada | Backend | G | Alta | Classificador da #124 e endpoint da #119 funcionais | Solicitação textual ou transcrita retorna macrointenção, intenção e confiança, aplicando os limiares de 0,550 e 0,700 |
| [#127](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/127) | Integrar o pipeline de PLN ao banco de dados | Backend | G | Alta | Scripts de `src/database/sql` aplicados no ambiente | Cada interação grava em `ai_interactions`, `consulted_sources` e `audit_events`, atendendo ao RNF03 |
| [#128](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/128) | Atualizar a discussão sobre a escolha do algoritmo de PLN | Documentação | M | Alta | Medição da #125 concluída | Seção 8.10 revisada com características, vantagens e limitações observadas na implementação |
| [#129](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/129) | Documentar a implementação do PLN e a integração com exemplos e testes | Documentação | G | Alta | Integrações das #126 e #127 funcionais | Bibliotecas, processo de integração e exemplos de entrada e saída, com casos de sucesso e de falha |
| [#130](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/130) | Implementar a interface básica de interação com o sistema | Frontend | G | Alta | Endpoints estáveis | Envio de texto e áudio pela interface, com exibição de resultado, erro e estado de carregamento |
| [#131](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/131) | Integrar o frontend às APIs do backend com validações e feedback | Frontend | G | Alta | Interface da #130 navegável | Fluxo completo da interface ao PLN, com validação de entrada e mensagem de erro tratada |
| [#132](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/132) | Documentar a estrutura do frontend e as instruções de uso e teste | Documentação | M | Média | Frontend integrado | Componentes, integração com as APIs e passo a passo de execução e teste |

### Artefato 2 — Planejamento de Testes Sistêmicos

| Issue | Task | Tipo | Est. | Prioridade | DoR | DoD |
| :---: | --- | :---: | :---: | :---: | --- | --- |
| [#133](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/133) | Definir as ferramentas e bibliotecas de teste do projeto | Teste | M | Alta | Escopo de testes da sprint acordado | Lista com finalidade de cada ferramenta e onde é utilizada |
| [#134](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/134) | Planejar os testes de funcionalidade dos requisitos funcionais | Teste | G | Alta | Requisitos funcionais atualizados em `develop` | Cada RF de RF01 a RF10 com ao menos um cenário positivo e um negativo, propósito e instrução de execução |
| [#135](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/135) | Planejar os testes de requisitos não funcionais, incluindo desempenho | Teste | G | Alta | Critérios de aceitação dos RNFs revisados | Testes de desempenho com meta, ferramenta e critério de aprovação declarados, além dos demais RNFs |
| [#136](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/136) | Planejar os testes de integração com o módulo de VHS | Teste | G | Alta | Integração com o provedor de transcrição funcionando | Cenários de comunicação e de falha, com o cache comprovando ausência de nova chamada externa em requisição repetida |
| [#137](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/137) | Elaborar o roteiro de testes de usabilidade com usuários externos | Teste | G | Alta | Frontend integrado e navegável | Roteiro com cenários, perfis dos cinco participantes externos e questionário SUS |

### Artefato 3 — Gestão de Projetos Evolutiva

| Issue | Task | Tipo | Est. | Prioridade | DoR | DoD |
| :---: | --- | :---: | :---: | :---: | --- | --- |
| [#138](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/138) | Registrar a análise da Sprint 3 com ações de melhoria para a Sprint 4 | Documentação | M | Alta | Sprint encerrada e merge requests integrados | Pontos fortes, pontos de melhoria e ações verificáveis, com indicadores apurados após o fechamento |
| [#139](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/139) | Atualizar a matriz de risco com status, reavaliação e novos itens | Documentação | G | Alta | Retrospectiva realizada | Status revisado item a item, histórico acrescido e efetividade das ações apurada |
| [#140](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/140) | Montar a matriz de papéis e responsabilidades da Sprint 3 | Documentação | M | Alta | Frentes da sprint definidas | Matriz com rotação conferida contra as Sprints 1 e 2 |
| [#141](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/141) | Revisar o contrato de convivência, o SLA e os rituais da equipe | Documentação | M | Média | Retrospectiva realizada | Registro de revisões atualizado, com motivo de cada mudança |
| [#142](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/142) | Planejar o backlog da Sprint 4 no Kanban | Documentação | G | Alta | Barema da Sprint 4 lido | Tasks criadas como issue, estimadas, priorizadas e detalhadas com DoR e DoD |
| [#143](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/143) | Atualizar as políticas de dailies, uso do GitLab e commits | Documentação | M | Média | Práticas da sprint observadas | Políticas revisadas em coerência com o contrato de convivência |
| [#144](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/144) | Atualizar o fluxo de GitFlow e as políticas de branch | Documentação | G | Alta | Práticas da Sprint 3 observadas | `GestaoConfiguracao.md` atualizado com exemplos praticados na sprint |

### Sequenciamento

A cadeia crítica é **#119 → #120 → #122 → #126 → #127**, porque cada elo depende do anterior estar funcional: sem endpoint não há o que integrar ao Speech-to-Text, sem transcrição não há o que classificar e sem classificação não há o que persistir. Ela deve começar no primeiro dia e é o que define se a entrega existe.

Em paralelo à cadeia, e sem depender dela, correm três frentes:

- **Núcleo de PLN** (#123, #124): o pré-processamento e o carregamento do classificador podem ser construídos antes de existir entrada de áudio, usando as solicitações textuais já suportadas. É pré-requisito de #126, e por isso não pode esperar.
- **Frontend** (#130, #131): a interface pode ser construída contra o endpoint textual existente e só depois apontar para o de áudio.
- **Planejamento de testes** (#133 a #137): depende apenas dos requisitos já integrados em `develop`, que a Sprint 2 deixou prontos. Pode começar no dia 1 e é a folga que absorve atraso da implementação.

As tasks de documentação técnica (#121, #128, #129, #132) fecham depois da implementação que descrevem, porque documentam comportamento observado e não previsto — é a correção da divergência entre documentação e implementação registrada na Seção 2.2.4.

As tasks de gestão (#138 a #144) só podem fechar com a sprint encerrada e os merge requests integrados, conforme a ação de melhoria sobre apuração de indicadores. A exceção é #142, que pode ser adiantada porque o barema da Sprint 4 já está disponível.

### Distribuição das estimativas

| Faixa | Quantidade | Participação |
| :---: | :---: | :---: |
| G (60 a 120 min) | 16 | 62% |
| M (30 a 60 min) | 10 | 38% |
| P (até 30 min) | 0 | 0% |
| PP (até 15 min) | 0 | 0% |

A ação de melhoria da Seção 2.2.5 previa quebrar as tasks até caberem majoritariamente na faixa M. O board mostra que isso **não foi cumprido**: 62% das tasks continuam em G, e nenhuma foi estimada em P ou PP. O registro fica aqui porque a ação é verificável e o resultado é conferível no próprio Kanban — a quebra precisa acontecer no refinamento, antes de a task sair de `Open`, e será reapurada na análise da Sprint 3.

O mesmo vale para a priorização: 23 das 26 tasks estão como Alta e apenas 3 como Média. Uma distribuição em que quase tudo é prioritário não ordena trabalho, e o sequenciamento acima existe justamente para suprir o que a coluna de prioridade não está diferenciando.

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
