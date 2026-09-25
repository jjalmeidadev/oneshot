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

## Gestão de configuração

# Sumário

- [1. Introdução](#1-introdução)
  - [1.1 Objetivo do documento](#11-objetivo-do-documento)
  - [1.2 Escopo](#12-escopo)
- [2. Visão geral do GitFlow](#2-visão-geral-do-gitflow)
  - [2.1 Revisão do fluxo após a Sprint 3](#21-revisão-do-fluxo-após-a-sprint-3)
  - [2.2 Revisão do fluxo após a Sprint 4](#22-revisão-do-fluxo-após-a-sprint-4)
- [3. Estrutura de branches](#3-estrutura-de-branches)
  - [3.1 Branches permanentes](#31-branches-permanentes)
  - [3.2 Branches temporárias](#32-branches-temporárias)
- [4. Política de nomenclatura de branches](#4-política-de-nomenclatura-de-branches)
- [5. Procedimentos operacionais](#5-procedimentos-operacionais)
  - [5.1 Criação de branch](#51-criação-de-branch)
  - [5.2 Atualização da branch](#52-atualização-da-branch)
  - [5.3 Mesclagem por merge request](#53-mesclagem-por-merge-request)
    - [5.3.1 Padronização do título antes do merge](#531-padronização-do-título-antes-do-merge)
    - [5.3.2 Marco de integração](#532-marco-de-integração)
    - [5.3.3 Resolução de conflitos e gate de integridade](#533-resolução-de-conflitos-e-gate-de-integridade)
  - [5.4 Exclusão de branch](#54-exclusão-de-branch)
- [6. Fluxo de desenvolvimento](#6-fluxo-de-desenvolvimento)
  - [6.1 Fluxo de feature](#61-fluxo-de-feature)
  - [6.2 Fluxo de release](#62-fluxo-de-release)
  - [6.3 Fluxo de hotfix](#63-fluxo-de-hotfix)
- [7. Hooks de Git](#7-hooks-de-git)
  - [7.1 Como ativar, verificar e desativar](#71-como-ativar-verificar-e-desativar)
  - [7.2 Validações executadas](#72-validações-executadas)
  - [7.3 Auditoria do repositório](#73-auditoria-do-repositório)
  - [7.4 Auditoria final da Sprint 4](#74-auditoria-final-da-sprint-4)
- [8. Versionamento de artefatos técnicos](#8-versionamento-de-artefatos-técnicos)
  - [8.1 O que é versionado e por quê](#81-o-que-é-versionado-e-por-quê)
  - [8.2 A restrição que vem junto](#82-a-restrição-que-vem-junto)
  - [8.3 Fontes editáveis dos diagramas](#83-fontes-editáveis-dos-diagramas)
- [9. Exemplos práticos](#9-exemplos-práticos)
  - [9.1 Atualização da gestão de projeto](#91-atualização-da-gestão-de-projeto)
  - [9.2 Preparação de entrega](#92-preparação-de-entrega)
  - [9.3 Integração de entrega documental com renumeração de seções](#93-integração-de-entrega-documental-com-renumeração-de-seções)
  - [9.4 Hotfix](#94-hotfix)
  - [9.5 Correção de integração após conflito](#95-correção-de-integração-após-conflito)
  - [9.6 Promoção da release 0.4.0 depois de promoções com squash](#96-promoção-da-release-040-depois-de-promoções-com-squash)
- [10. Regras de governança do GitFlow](#10-regras-de-governança-do-gitflow)

# 1. Introdução

A gestão de configuração deste projeto define como o grupo organiza o versionamento do código-fonte e da documentação por meio do GitLab. Este arquivo reúne a documentação do GitFlow, o uso correto das branches, as convenções de nomenclatura e os procedimentos para criação, mesclagem e exclusão de branches.

## 1.1 Objetivo do documento

O objetivo deste documento é garantir que todos os integrantes utilizem o mesmo fluxo de trabalho no Git, reduzindo conflitos, perdas de rastreabilidade e integrações diretas em branches permanentes.

Este documento estabelece:

- Modelo GitFlow adotado pelo grupo;
- Finalidade de cada tipo de branch;
- Convenções para nomear branches;
- Procedimentos para criar, atualizar, mesclar e excluir branches;
- Hooks e gates que protegem commits, merge requests e integridade dos arquivos;
- Regras para versionar modelos, fontes `.puml` e imagens geradas;
- Exemplos práticos de aplicação do fluxo no contexto do projeto.

## 1.2 Escopo

Este documento cobre a gestão de branches, o fluxo GitFlow, hooks, gates de integração e versionamento dos artefatos técnicos editáveis. Políticas de daily, Kanban, contrato de trabalho, papéis e planejamento de sprint pertencem ao documento de gestão de projeto.

# 2. Visão geral do GitFlow

O GitFlow é um modelo de organização de branches que separa o desenvolvimento diário, a homologação e a versão estável do projeto. No G05, ele segue a orientação do Módulo 7 e do Dashboard Ágil, mantendo uma linha clara entre trabalho em andamento, revisão, homologação e entrega final.

O fluxo obrigatório do módulo é:

```text
feature/* -> develop -> hmg -> main
```

O fluxo operacional é:

1. A tarefa é criada no GitLab.
2. A issue nasce em `Open` e só avança após refinamento com DoR, DoD, labels, milestone e assignee.
3. O integrante cria uma branch temporária a partir de `develop`.
4. A branch representa uma única issue.
5. A alteração é desenvolvida, testada e enviada para o GitLab.
6. O integrante abre um Merge Request para `develop`.
7. Outro integrante revisa a entrega.
8. Após aprovação e validação, a branch é mesclada em `develop`.
9. A versão integrada é promovida de `develop` para `hmg` por Merge Request.
10. A versão homologada é promovida de `hmg` para `main` por Merge Request.

Promoções podem acontecer durante a sprint quando uma entrega estiver pronta. A sprint define a cadência de planejamento, mas não obriga a equipe a concentrar todos os merges no último dia.

## 2.1 Revisão do fluxo após a Sprint 3

A seção executa a issue [#144](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/144), mantendo os procedimentos de criação, mesclagem e exclusão e acrescentando os controles exigidos pelos fatos da Sprint 3.

A revisão de 10/09/2026 encontrou 30 commits em `origin/develop`: 15 de entrega sem merge e 15 merges. Nove dos quinze merges (60%) ocorreram nos dois últimos dias ativos, 08 e 09/09. Além disso, cinco arquivos foram integrados com marcadores de conflito: `README.md`, `.gitignore`, `.githooks/pre-commit`, o diagrama de componentes e o notebook do classificador. Portanto, o desenho do GitFlow permanece adequado, mas os controles de entrada em `develop` foram insuficientes.

As alterações desta revisão são:

- validação do título do MR deixa de depender apenas do checklist e passa a exigir gate no GitLab ou pipeline;
- quarta-feira passa a gerar inventário explícito de MRs, idade, revisor e bloqueio;
- busca de marcadores de conflito passa a integrar o gate de merge;
- diagramas `.puml` passam a ser reconhecidos formalmente como fonte editável das imagens;
- a auditoria de conformidade usa um único recorte e uma única regra nos dois documentos de gestão.

Não são criadas branches permanentes adicionais. `main`, `develop` e `hmg` continuam separando versão estável, integração e homologação; `feature/*`, `release/*` e `hotfix/*` preservam os papéis exigidos pelo artefato.

## 2.2 Revisão do fluxo após a Sprint 4

A seção executa a issue [#243](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/243). O recorte é o mesmo da Seção 2.4 do `GestaoProjeto.md`: de 11 a 25/09/2026, sobre `origin/develop@964cd8c`, com os dados de merge request extraídos da API do GitLab.

Na Sprint 4 entraram em `develop` 26 merge requests. O desenho do GitFlow continuou adequado, e a proteção das branches permanentes funcionou: `main`, `develop` e `hmg` não aceitam push direto e não receberam nenhum commit fora de MR. Os problemas estiveram nas bordas do fluxo:

- **Título e squash.** Dezessete MRs usaram squash, e só 8 dos 17 commits gerados pelo servidor atendem à regra completa do hook. Os outros nove MRs foram integrados sem squash e trouxeram 58 commits locais, dos quais 57 atendem à regra. O ponto fraco é o título do MR — apenas 7 de 26 no padrão da Seção 5.3.1 —, e a validação automática não foi configurada: o projeto não tem padrão de título definido, e a pipeline não tem job equivalente.
- **Gate de integridade.** A `develop` fechou sem marcadores de conflito, mas nem o `pre-commit` nem a pipeline aplicam a busca da Seção 5.3.3. Uma resolução de conflito descartou uma regra do `.gitignore`, restaurada depois em `fb15994`: o gate de marcadores não pegaria esse caso, que depende da revisão do diff resolvido.
- **Exclusão de branch.** Sete MRs foram integrados sem marcar a exclusão da branch de origem. No fechamento, o remoto tem 33 branches temporárias: 27 com MR já integrado, 1 com MR fechado sem merge e 5 sem MR.
- **Nomenclatura.** Três branches ativas no remoto fogem da Seção 4 por usarem maiúsculas ou acentos — `feat/Implementar-validação-de-formatos-e-tratamento`, `feature/S4-20-e2e-textual-rag` e `feature/S4-32B-testes-integracao` —, além de `docs/documentação-stt`, de sprint anterior. `test/232-reexecutar-benchmark-rnf06` é o exemplo a seguir: tipo, número da issue e escopo em minúsculas.
- **Promoção.** A release 0.3.0 foi promovida por MR direto de `develop` para `hmg` ([!84](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/merge_requests/84)) e de `hmg` para `main` ([!86](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/merge_requests/86)), ambos com squash. O squash de promoção recria a divergência de histórico corrigida na Sprint 2: `hmg` e `main` têm o mesmo conteúdo de `develop` em 11/09 (`aec6457`), mas não o seu histórico, e um merge direto de `develop` em `hmg` hoje produziria 65 arquivos em conflito. O procedimento correto está na Seção 9.6.

As alterações desta revisão são:

- MRs de promoção, de `release/*` para `hmg` e de `hmg` para `main`, **nunca usam squash**; o squash fica restrito às branches de trabalho;
- o padrão de título passa a aceitar mais de uma issue, como `(#214, #215, #220)`, porque um MR que entrega várias tasks é legítimo e já ocorreu quatro vezes no recorte da Sprint 4;
- merge sem squash passa a ser permitido quando todos os commits da branch passaram pelo hook `commit-msg`, e continua obrigatório o título no padrão;
- a validação do título e o gate de marcadores viram tasks do primeiro dia da Sprint 5 (S5-02 e S5-01), com a opção "Pipelines must succeed" ativada nas configurações do projeto depois que os jobs existirem;
- a exclusão da branch de origem é marcada na abertura do MR, e as 27 branches com MR integrado são removidas depois da promoção da release 0.4.0 (Seção 5.4).

# 3. Estrutura de branches

## 3.1 Branches permanentes

| Branch | Finalidade | Regra de uso |
| --- | --- | --- |
| `main` | Contém a versão estável e entregue do projeto. | Não recebe commits diretos. Recebe apenas Merge Requests aprovados a partir de `hmg`, com DoD atendida. |
| `develop` | Integra as entregas em desenvolvimento durante a sprint. | Recebe somente Merge Requests aprovados a partir de branches temporárias. |
| `hmg` | Representa o ambiente compartilhado de homologação. | Não recebe commits diretos. Recebe Merge Requests de `develop` para validação funcional antes da promoção para `main`. |

As branches `dev`, `homologacao` e `homologação` não fazem mais parte do fluxo oficial do projeto. O grupo removeu `dev` e padronizou a homologação como `hmg`, mantendo apenas `main`, `develop` e `hmg` como branches permanentes.

As branches permanentes não devem ser usadas para desenvolvimento direto. Qualquer alteração deve partir de uma branch temporária e entrar no fluxo por Merge Request.

## 3.2 Branches temporárias

| Tipo de branch | Finalidade | Branch de origem | Branch de destino |
| --- | --- | --- | --- |
| `feature/*` | Desenvolvimento de nova funcionalidade vinculada a uma issue. | `develop` | `develop` |
| `feat/*` | Alternativa aceita pelo Dashboard para desenvolvimento de nova funcionalidade. | `develop` | `develop` |
| `fix/*` | Correção de defeito não emergencial. | `develop` | `develop` |
| `bugfix/*` | Alternativa aceita para correção de defeito não emergencial. | `develop` | `develop` |
| `docs/*` | Alteração de documentação. | `develop` | `develop` |
| `doc/*` | Alternativa aceita para documentação. | `develop` | `develop` |
| `style/*` | Ajuste de formatação sem mudança de comportamento. | `develop` | `develop` |
| `refactor/*` | Reorganização técnica sem nova funcionalidade ou correção direta. | `develop` | `develop` |
| `test/*` | Criação ou ajuste de testes. | `develop` | `develop` |
| `chore/*` | Ajustes de configuração, scripts, organização ou manutenção. | `develop` | `develop` |
| `perf/*` | Melhoria de performance. | `develop` | `develop` |
| `ci/*` | Ajustes de pipeline e integração contínua. | `develop` | `develop` |
| `build/*` | Ajustes de build, empacotamento ou release. | `develop` | `develop` |
| `release/*` | Preparação de uma versão candidata à entrega. | `develop` | `hmg`; após a homologação, `hmg` é promovida a `main`, e ajustes da release retornam a `develop` |
| `hotfix/*` | Correção urgente em uma versão já estável. | `main` | `main` e `develop` |

# 4. Política de nomenclatura de branches

Todas as branches temporárias devem seguir o padrão:

```text
<tipo>/<descrição-curta-em-kebab-case>
```

Regras:

- O prefixo deve seguir a regex validada pelo Dashboard: `^(feature|feat|fix|bugfix|hotfix|docs|doc|style|refactor|test|chore|perf|ci|build|release)/`;
- Usar letras minúsculas;
- Separar palavras com hífen;
- Não usar espaços;
- Não usar nomes genéricos como `ajustes`, `teste`, `final` ou `coisas`;
- A descrição deve indicar o escopo da tarefa;
- Cada branch deve estar relacionada a uma única issue do GitLab.

Exemplos válidos:

```text
docs/gestao-configuracao
docs/gestao-projeto
feature/importar-dados-projetos
feat/importar-dados-projetos
fix/corrigir-query-inicial
test/validar-carga-dados
chore/automacoes-qualidade-repositorio
release/0.1.0
hotfix/corrigir-falha-env
```

# 5. Procedimentos operacionais

## 5.1 Criação de branch

Para tarefas comuns de desenvolvimento, documentação, testes ou manutenção, a issue deve existir antes da branch e estar vinculada à sprint por milestone.

```bash
git checkout develop
git pull origin develop
git checkout -b feature/login-com-google
git push -u origin feature/login-com-google
```

Para uma correção urgente em produção ou na versão estável:

```bash
git checkout main
git pull origin main
git checkout -b hotfix/corrigir-falha-env
git push -u origin hotfix/corrigir-falha-env
```

## 5.2 Atualização da branch

Durante a execução da tarefa, a branch temporária deve ser mantida atualizada com `develop` para reduzir conflitos no Merge Request.

```bash
git checkout docs/gestao-projeto
git fetch origin
git merge origin/develop
```

Quando houver conflito, o responsável pela branch deve resolvê-lo localmente, testar a alteração e registrar a correção em novo commit.

## 5.3 Mesclagem por merge request

Toda integração deve acontecer por Merge Request no GitLab. O Merge Request deve conter:

- Branch de origem e destino corretas;
- Título no formato `<tipo>: <descrição curta> (#<issue>)`, com mais de três palavras e sem `WIP:` ou `Draft:`;
- Descrição substantiva do que foi alterado;
- Issue ou tarefa relacionada;
- Evidências da entrega;
- Revisor definido;
- Confirmação de que a branch pode ser removida após o merge;
- Validação de pipeline, testes, lint, build ou validação manual conforme o tipo de entrega.

Critérios mínimos para merge:

- A entrega atende ao objetivo da tarefa;
- A revisão foi feita por outro integrante;
- Não há discussões pendentes;
- A branch está atualizada em relação ao destino;
- A DoD da issue está atendida;
- O responsável pelo merge confirma que a alteração não quebra a entrega da sprint.

### 5.3.1 Padronização do título antes do merge

O grupo utiliza merge com squash, e o commit resultante é criado pelo servidor: ele **não passa pelos hooks locais** e herda o título do merge request, que por padrão vem do nome da branch. O efeito é direto sobre a rastreabilidade — na Sprint 1, 6 de 19 commits de squash seguiram a convenção; na recontagem final da Sprint 2, foram 8 de 22 com tipo válido e 5 de 22 com tipo e referência à issue.

Na revisão da Sprint 3, foram encontrados 15 commits de entrega: 8 com tipo válido e 6 na regra completa. Essa nova apuração orienta o gate da Sprint 4 sem alterar os números publicados nas seções históricas.

Na Sprint 4, 7 dos 26 títulos de MR seguiram o padrão, e 8 dos 17 commits de squash atenderam à regra completa, contra 57 dos 58 commits locais trazidos por MRs sem squash (Seção 2.2). O problema está no título, e não nos commits.

Esses valores seguem a recontagem comunicada no feedback da avaliação para o recorte de `develop` entre 15 e 27/08 e são a linha de base única adotada pelos dois documentos de gestão.

O checklist humano permanece, mas deixa de ser a única barreira. O projeto deve configurar a validação de título do GitLab em **Settings → Merge requests → Title pattern**, quando o plano e a versão da instância oferecerem o recurso, usando RE2. A documentação oficial confirma que um título fora do padrão bloqueia o merge. Se o recurso não estiver disponível, um job do pipeline deve validar `$CI_MERGE_REQUEST_TITLE` e produzir o mesmo bloqueio. Na auditoria da Sprint 4, o projeto não tinha padrão configurado e a pipeline não tinha job equivalente; o job é a task S5-02, e a opção "Pipelines must succeed" é ativada em seguida. Referência: [Merge request title validation — GitLab Docs](https://docs.gitlab.com/user/project/merge_requests/title_validation/).

Padrão vigente, revisado na Sprint 4 para aceitar mais de uma issue:

```text
^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\([A-Za-z0-9._-]+\))?!?: .+ \(#[0-9]+(, #[0-9]+)*\)$
```

Exemplos apresentados no GitLab:

```text
feat(api): integrar classificador de intenções (#126)
feat: implementar o fluxo de alerta de prazo em atraso (#214, #215, #220)
```

Títulos como `resolve merge`, `feat/implementar-frontend` ou `Docs/atualizar-modelagem` não podem ser mergeados. A proteção do título é complementada pelas push rules de branch e commit, quando disponíveis, conforme a [documentação de Push Rules do GitLab](https://docs.gitlab.com/user/project/repository/push_rules/).

**Squash ou merge sem squash.** O squash continua sendo o padrão do projeto para branches de trabalho. O merge sem squash é permitido quando todos os commits da branch passaram pelo hook `commit-msg`, porque preserva commits já validados. Nos MRs de promoção — de `release/*` para `hmg` e de `hmg` para `main` — o squash é proibido, pelo motivo descrito na Seção 9.6.

Há um segundo efeito do squash que vale conhecer: o commit gerado registra no campo de committer o nome de quem aprovou o merge, e não o de quem escreveu o código. A autoria original é preservada no campo de autor, mas não aparece em contagens que usam o committer.

### 5.3.2 Marco de integração

Até **quarta-feira, antes da daily**, o Scrum Master publica na issue de gestão um inventário contendo MR, tempo desde a abertura, revisor, estado do pipeline e bloqueio. Todo MR com mais de 48 horas deve estar revisado e mergeado ou possuir impedimento e próxima ação registrados. A Sprint 3 mostrou que declarar apenas “mergear até quarta” não bastou: 60% dos merges ocorreram em 08–09/09.

### 5.3.3 Resolução de conflitos e gate de integridade

Resolver um conflito significa escolher e validar o conteúdo final; remover apenas o estado de conflito do índice não é suficiente. Antes do commit de resolução e novamente no pipeline, deve ser executada uma busca nos arquivos rastreados:

```bash
git grep -n -E '^(<<<<<<< .+|=======[[:space:]]*|>>>>>>> .+)$'
```

Critério de aprovação: nenhuma ocorrência. A alternativa `=======[[:space:]]*$` aceita apenas o separador de sete sinais de igual, seguido no máximo pelo caractere de fim de linha do arquivo. Assim, funciona também em arquivos CRLF no Windows sem confundir saídas legítimas, como `================ 10 passed...`, com um marcador de conflito.

Procedimento:

1. Atualizar a branch com o destino.
2. Abrir cada arquivo em conflito e comparar as duas versões com a documentação vigente.
3. Remover marcadores e conteúdo descartado.
4. Executar lint, testes, build ou renderização aplicável.
5. Executar a busca de marcadores.
6. Registrar no MR quais arquivos foram resolvidos e qual critério decidiu a versão final.
7. Solicitar nova revisão antes do merge.

O gate responde diretamente ao ocorrido na Sprint 3, quando cinco arquivos chegaram a `develop` com resíduos de merge: `README.md`, `.gitignore`, `.githooks/pre-commit`, `docs/diagrams/componentes-metro-5.2.puml` e `src/notebooks/classificador_intencoes_metro.ipynb`.

## 5.4 Exclusão de branch

Após o merge, a branch temporária deve ser excluída para manter o repositório limpo.

Pelo GitLab, a exclusão pode ser feita pela opção de remover a source branch após o merge.

Por comando:

```bash
git push origin --delete docs/gestao-projeto
git branch -d docs/gestao-projeto
```

Branches temporárias só devem permanecer abertas quando houver trabalho ainda em andamento ou revisão pendente.

A exclusão é marcada na abertura do MR, e não no momento do merge. No fechamento da Sprint 4, o remoto tinha 33 branches temporárias, 27 delas com MR já integrado (Seção 7.4). A limpeza é feita depois da promoção de cada release, pelo responsável pela conformidade do repositório, conferindo antes que a branch não tem MR aberto:

```bash
git fetch origin --prune
git push origin --delete test/executar-rnf04-rnf05   # exemplo: MR !96 integrado
```

# 6. Fluxo de desenvolvimento

## 6.1 Fluxo de feature

O fluxo de feature é usado para novas funcionalidades ou incrementos planejados.

```text
develop -> feature/nome-da-feature -> Merge Request -> develop
```

Etapas:

1. Criar a issue no GitLab.
2. Refinar a issue com DoR, DoD, labels, milestone e assignee.
3. Criar a branch `feature/*` a partir de `develop`.
4. Desenvolver e testar a funcionalidade.
5. Fazer commits semânticos vinculados à issue.
6. Enviar a branch para o GitLab.
7. Abrir Merge Request para `develop`.
8. Revisar e corrigir apontamentos.
9. Fazer merge após aprovação, validação e DoD atendida.
10. Excluir a branch temporária.

## 6.2 Fluxo de release

O fluxo de release é usado quando uma versão candidata precisa ser estabilizada sem misturar novas funcionalidades.

```text
develop -> release/x.y.z -> hmg -> main
```

Regras:

- Não entram novas funcionalidades em `release/*`;
- Só são permitidos ajustes finais, correções, documentação e validações;
- A versão deve ser validada em `hmg` antes de chegar à `main`;
- Depois do merge em `main`, qualquer ajuste feito na release deve voltar para `develop`;
- Se uma entrega estiver pronta e outra não, o grupo deve usar MR individual, feature flag ou branch de release para não bloquear promoção de trabalho concluído;
- Os MRs de `release/*` para `hmg` e de `hmg` para `main` não usam squash; a release 0.3.0 foi promovida com squash, e a correção está na Seção 9.6.

Procedimento de integração: abrir MR de `release/*` para `hmg`; homologar a versão; promover `hmg` para `main` por novo MR; retornar a `develop` qualquer correção criada na release; e excluir a branch temporária conforme a Seção 5.4. Não é permitido integrar `release/*` diretamente em `main`.

Exemplo:

```bash
git checkout develop
git pull origin develop
git checkout -b release/0.1.0
git push -u origin release/0.1.0
```

## 6.3 Fluxo de hotfix

O fluxo de hotfix é usado para corrigir rapidamente uma falha crítica encontrada na versão estável.

```text
main -> hotfix/nome-do-ajuste -> main
                              -> develop
```

Regras:

- A branch nasce de `main`;
- O escopo deve ser mínimo e focado na correção;
- O Merge Request deve ir para `main`;
- Depois da correção em `main`, o mesmo ajuste deve ser levado para `develop` e, quando aplicável, para `hmg`.

# 7. Hooks de Git

O repositório possui hooks versionados na pasta `.githooks/`. Eles funcionam como uma camada local de proteção antes de commits e pushes, reduzindo divergências entre o fluxo documentado, as regras dos professores e o que chega ao GitLab.

Os hooks não substituem revisão por pares nem Merge Request. Eles apenas bloqueiam erros objetivos, como commit direto em branch permanente, branch sem prefixo aceito, commit fora do padrão ou commit sem referência à issue.

## 7.1 Como ativar, verificar e desativar

Para ativar os hooks neste repositório:

```bash
git config core.hooksPath .githooks
```

Para verificar se os hooks estão ativos:

```bash
git config core.hooksPath
```

Resultado esperado:

```text
.githooks
```

Para desativar os hooks locais:

```bash
git config --unset core.hooksPath
```

Em macOS e Linux, ativar o `core.hooksPath` não é suficiente: o Git só executa hooks
que tenham permissão de execução. Por isso, use o script de instalação, que configura o
caminho e aplica o `chmod +x` nos três hooks:

```bash
sh scripts/install-hooks.sh
```

No Windows, use o script equivalente:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install-hooks.ps1
```

Para confirmar que os hooks estão executáveis:

```bash
ls -l .githooks/
```

O resultado esperado mostra o bit de execução (`x`) nos três arquivos:

```text
-rwxr-xr-x  commit-msg
-rwxr-xr-x  pre-commit
-rwxr-xr-x  pre-push
```

Se os arquivos aparecerem como `-rw-r--r--`, o Git ignora os hooks silenciosamente e
exibe apenas um aviso do tipo `hook was ignored because it's not set as executable`,
permitindo que commits fora do padrão sejam criados.

## 7.2 Validações executadas

| Hook | Momento de execução | Validações |
| --- | --- | --- |
| `.githooks/pre-commit` | Antes de criar um commit | Bloqueia commit direto em branch permanente, valida prefixo da branch, bloqueia arquivos sensíveis no stage e executa `git diff --cached --check`. |
| `.githooks/commit-msg` | Ao validar a mensagem de commit | Exige Conventional Commits, primeira linha com no máximo 72 caracteres e referência a issue no formato `#N`. |
| `.githooks/pre-push` | Antes do push | Bloqueia push direto para branches permanentes, valida prefixo da branch local e confere se commits novos seguem Conventional Commits e referenciam issue. |

A validação de arquivos sensíveis bloqueia `.env`, `.env.*`, `*.pem`, `*.key` e nomes contendo `secret` ou `credential`. Desde a Sprint 2, arquivos terminados em `*.example`, `*.sample` e `*.template` são avaliados antes dessa regra e liberados: são templates de configuração sem segredo, feitos para serem versionados. A exceção foi acrescentada quando `src/backend/.env.example` — que já estava em `develop` — passou a bloquear qualquer commit local que tocasse a árvore. O arquivo entrou no repositório sem passar pela validação justamente porque foi integrado por squash no servidor.

Após a ocorrência da Sprint 3, o `pre-commit` e o pipeline também devem bloquear marcadores de conflito conforme a Seção 5.3.3. Enquanto essa alteração ainda não estiver implementada no hook, a execução manual do comando é obrigatória e deve aparecer como evidência no MR.

A validação do `pre-push` considera apenas os commits criados na própria branch. Commits
de merge e commits que já existem em alguma branch remota do `origin` são ignorados, de
modo que atualizar a branch com `develop` não faz o hook reprovar o histórico já
integrado ao repositório.

Branches bloqueadas pelos hooks:

```text
main
develop
hmg
```

Tentativas de recriar ou usar `dev`, `homologacao` ou `homologação` devem ser tratadas como desvio do fluxo oficial e corrigidas antes da abertura do Merge Request.

Prefixos de branch aceitos pelos hooks:

```text
feature/
feat/
fix/
bugfix/
hotfix/
docs/
doc/
style/
refactor/
test/
chore/
perf/
ci/
build/
release/
```

Tipos de commit aceitos pelos hooks:

```text
feat
fix
docs
style
refactor
test
chore
perf
ci
build
revert
```

Formato aceito para commits:

```text
<tipo>(<escopo opcional>): <descrição curta> (#<issue>)
```

Exemplos válidos:

```text
docs(gestao-projeto): atualizar matriz da sprint (#12)
feat(auth): adicionar login com Google (#23)
fix(api): corrigir retorno de erro (#31)
```

O escopo opcional do commit aceita apenas letras sem acento, números, ponto, underline e hífen. Não use espaço nem acentos no escopo.

Exemplo rejeitado:

```text
docs(gestão projeto): atualizar matriz da sprint (#12)
```

## 7.3 Auditoria do repositório

Além dos hooks, o repositório possui o script `scripts/audit-repo.ps1`, que verifica a
aderência do repositório às regras de governança — nomes de branches, padrão das
mensagens de commit e vínculo com issues. Ele é executado sob demanda, antes de
fechamentos de sprint ou revisões de entrega, e não substitui os hooks nem a revisão
por pares.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/audit-repo.ps1
```

## 7.4 Auditoria final da Sprint 4

Auditoria executada em 25/09/2026 sobre `origin/develop@964cd8c`, depois da integração do último merge request da sprint, e sobre as configurações do projeto no GitLab. Cada divergência encontrada tem justificativa ou ação com destino definido.

| Verificação | Método | Resultado | Situação |
| --- | --- | --- | --- |
| Marcadores de conflito | `git grep -n -I -E '^(<<<<<<< .+\|=======[[:space:]]*\|>>>>>>> .+)$' 964cd8c` sobre os 764 arquivos versionados | Nenhuma ocorrência | ✅ Conforme |
| Segredos versionados | Busca por padrões de chave (AWS, OpenRouter, Google, GitLab, GitHub, chave privada) e por URLs de banco com senha | Nenhuma credencial. As URLs encontradas usam hosts fictícios de teste (`example`, `example.test`, `exemplo`). Os quatro `.env.example` têm valores vazios ou marcadores | ✅ Conforme |
| Identificadores de infraestrutura | Leitura da Seção 10.2 do `Projeto.md` | ID da conta AWS no endereço do ECR e IDs de instância EC2 e AMI documentados | ✅ Justificado: são identificadores, e não credenciais; o acesso depende das credenciais temporárias do Learner Lab, que não estão no repositório |
| Variáveis sem uso | Conferência de cada variável do `.env.example` da raiz contra o código | 11 variáveis de ferramentas externas sem nenhuma referência no repositório (por exemplo, `CLICKUP_API_KEY`, `RAILWAY_TOKEN` e `N8N_API_KEY`) | ⚠️ Divergência: removidas na conformidade do repositório (S5-48) |
| Links relativos da documentação | Resolução de cada link relativo do `README.md`, de `docs/*.md` e dos READMEs de `src/` | 9 links quebrados, 8 no `Projeto.md` e 1 em `src/backend/README.md`, para cinco arquivos removidos no [!108](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/merge_requests/108) (`aws-operacao.md`, `docker-operacao.md`, `deploy-aws-learner-lab-handoff.md`, `deploy-aws-learner-lab-replan.md` e `contrato-referencias.md`) | ⚠️ Divergência: corrigidos na conformidade do repositório (S5-48), apontando para a Seção 10.2 do `Projeto.md` ou restaurando os arquivos |
| Proteção das branches permanentes | Configuração de branches protegidas | `main`, `develop` e `hmg` sem push direto; merge por Developers e Maintainers | ✅ Conforme |
| Pipeline como condição de merge | Configurações de merge request do projeto | "Pipelines must succeed" desativada | ⚠️ Divergência: ativar depois dos jobs das tasks S5-01 e S5-02 |
| Padrão de título de MR | Configurações do projeto e `.gitlab-ci.yml` | Sem padrão configurado e sem job equivalente | ⚠️ Divergência: task S5-02 |
| Squash | Configuração do projeto e MRs integrados | Squash "ativado por padrão"; 9 de 26 MRs integrados sem squash | ✅ Justificado pela nova regra da Seção 2.2 |
| Branches temporárias remanescentes | `GET /repository/branches` e cruzamento com os MRs | 33 temporárias: 27 com MR integrado, 1 com MR fechado sem merge e 5 sem MR | ⚠️ Divergência: limpeza depois da promoção da release 0.4.0 |
| Nomenclatura de branches | Regex e regras da Seção 4 | 4 branches ativas com maiúsculas ou acentos | ⚠️ Divergência: removidas na limpeza; nenhuma branch nova fora da regra |
| Coerência entre `develop`, `hmg` e `main` | `git merge-base` e `git diff` | `hmg` e `main` idênticas entre si e ao conteúdo de `develop` em `aec6457` (11/09); histórico divergente desde `ca455b3` | ✅ Justificado: a release 0.4.0 é promovida depois desta entrega, pelo procedimento da Seção 9.6 |
| Cobertura automatizada | `.gitlab-ci.yml` | O job `backend-api` executa 13 arquivos nomeados; o marcador `integration` já existe, mas não é usado pela pipeline | ⚠️ Divergência: task S5-01 |

O script `scripts/audit-repo.ps1` da Seção 7.3 cobre nomes de branch, mensagens de commit e vínculo com issues. A auditoria acima acrescenta segredos, configurações do projeto e coerência entre as branches permanentes, que o script não verifica.

# 8. Versionamento de artefatos técnicos

O repositório versiona os artefatos gerados pelo treinamento do classificador de intenções, em `src/notebooks/artefatos/`. A decisão foi tomada na Sprint 2, quando o notebook de classificação entrou no projeto, e é registrada aqui porque tem consequência permanente sobre o tamanho do repositório.

## 8.1 O que é versionado e por quê

| Artefato | Tamanho aproximado | Motivo |
| --- | ---: | --- |
| `classificador_intencoes.joblib` | 14,5 MB | Modelo serializado da execução de referência, mantido como evidência do resultado documentado na Seção 8.10 do `Projeto.md` |
| `word2vec_portfolio.model` | 0,9 MB | Representação treinada no corpus do projeto, necessária para reproduzir a inferência sem novo treinamento |
| `dataset_intencoes.csv` | 0,8 MB | Conjunto sintético que sustenta a separação por `template_id` descrita no protocolo de avaliação |
| `catalogo_intencoes.csv` e `.json` | poucos KB | Catálogo das intenções reconhecidas, consultado pelo roteamento |
| `metricas.json` | poucos KB | Métricas da execução de referência, citadas na documentação |

A escolha é deliberada: manter os artefatos permite conferir os números publicados sem reexecutar o notebook, o que importa em um projeto avaliado por evidência.

## 8.2 A restrição que vem junto

O Git preserva todas as versões de um arquivo binário. Cada nova versão do `.joblib` acrescenta cerca de 14 MB **permanentes** ao repositório, que todo integrante baixa a cada clone e que não podem ser removidos sem reescrever o histórico.

Por isso valem as regras abaixo.

- **Não commitar artefatos a cada retreino.** Execuções exploratórias, ajustes de hiperparâmetro e testes de configuração permanecem locais. Só entra no repositório o artefato correspondente à **execução de referência** citada na documentação.
- **Atualizar o artefato apenas quando o resultado documentado mudar.** Se a Seção 8.10 do `Projeto.md` continua reportando as mesmas métricas, não há motivo para substituir o binário.
- **Declarar a substituição no merge request.** Quando um artefato for atualizado, o MR deve informar qual execução o gerou e quais métricas mudaram, para que a troca de 14 MB tenha justificativa registrada.
- **Manter os arquivos leves sempre atualizados.** `catalogo_intencoes` e `metricas.json` são pequenos e devem acompanhar qualquer mudança, mesmo quando o modelo serializado não for substituído.

Caso o volume se torne um problema, a alternativa prevista é migrar os binários para Git LFS, preservando a rastreabilidade sem carregar o histórico. A avaliação dessa migração fica condicionada ao crescimento observado do repositório.

## 8.3 Fontes editáveis dos diagramas

A pasta `docs/diagrams` contém os arquivos `.puml` que são a **fonte editável** dos diagramas publicados como imagem em `docs/img`. A imagem não substitui a fonte: sem o `.puml`, uma alteração futura exigiria reconstruir o diagrama manualmente.

Regras de versionamento:

- fonte `.puml` e imagem gerada devem entrar no mesmo MR;
- a descrição do MR informa o comando ou ferramenta usada para regenerar a imagem;
- a revisão compara a fonte com a arquitetura documentada e verifica que a imagem corresponde à fonte;
- marcador de conflito no `.puml` bloqueia o merge, mesmo que a imagem ainda seja renderizável;
- mudanças apenas visuais devem ser identificadas; mudanças arquiteturais precisam atualizar também o texto que explica o diagrama.

Comando de referência já usado no projeto:

```bash
java -jar plantuml.jar -charset UTF-8 -tpng -o ../img docs/diagrams/<arquivo>.puml
```

Na revisão da Sprint 3, o diretório contém quatorze fontes `.puml`. A decisão de mantê-las junto das imagens passa a integrar formalmente a gestão de configuração, e qualquer inclusão ou remoção deve ser explicada no MR.

# 9. Exemplos práticos

## 9.1 Atualização da gestão de projeto

```text
Issue: Estruturar documento de gestão de projeto
Branch: docs/gestao-projeto
Destino do MR: develop
Fluxo: develop -> docs/gestao-projeto -> develop
Após aprovação: excluir docs/gestao-projeto
```

Comandos:

```bash
git checkout develop
git pull origin develop
git checkout -b docs/gestao-projeto
git push -u origin docs/gestao-projeto
```

## 9.2 Preparação de entrega

```text
Branch de integração: develop
Branch de homologação: hmg
Branch final: main
Responsável pelo merge final: Scrum Master
Prazo de revisão: quinta-feira
Prazo de merge para main: sexta-feira como cadência padrão
```

Fluxo:

```text
branches temporárias -> develop -> hmg -> main
```

## 9.3 Integração de entrega documental com renumeração de seções

Situação real da Sprint 2. Quatro branches alteravam `docs/Projeto.md` ao mesmo tempo, e uma delas renumerava seções, deslocando `8.6` para `8.7` e `8.7` para `8.8`. Integrar fora de ordem produziria conflito em cada uma das seguintes.

```bash
# 1. Levantar quem toca o mesmo arquivo antes de abrir o merge
git fetch origin --prune
git branch -r --no-merged origin/develop
git diff --stat origin/develop...origin/docs/<branch>

# 2. Acordar a ordem: primeiro as que só acrescentam seções,
#    depois a que renumera, por último a que reescreve o sumário
# 3. Integrar na ordem acordada, atualizando a branch antes de cada merge
git checkout docs/<minha-branch>
git merge origin/develop
# resolver conflitos, regerar o sumário a partir dos títulos reais
git push origin docs/<minha-branch>
```

A regra prática: **branch que renumera seção entra depois das que só acrescentam, e a que regenera o sumário entra por último.** Quando duas pessoas precisam mexer no mesmo arquivo na mesma sprint, a ordem de merge é combinada na planning, não descoberta no conflito.

## 9.4 Hotfix

```text
Problema: arquivo de configuração impede execução da versão estável
Branch: hotfix/corrigir-configuracao-env
Origem: main
Destino: main e develop
```

## 9.5 Correção de integração após conflito

Situação derivada da Sprint 3: um merge foi concluído, mas resíduos permaneceram em arquivos de documentação, configuração, diagrama e notebook.

```bash
git checkout develop
git pull origin develop
git checkout -b fix/remover-marcadores-conflito

git grep -n -E '^(<<<<<<< .+|=======[[:space:]]*|>>>>>>> .+)$'
# resolver cada arquivo e executar as verificações aplicáveis
git diff --check
git grep -n -E '^(<<<<<<< .+|=======[[:space:]]*|>>>>>>> .+)$'
```

O segundo `git grep` deve retornar vazio. A branch segue por MR para `develop`, com lista dos arquivos corrigidos e evidência dos testes. Depois de homologada, a correção segue pelo fluxo normal até `main`; não se corrige diretamente a branch permanente.

## 9.6 Promoção da release 0.4.0 depois de promoções com squash

Situação real do fechamento da Sprint 4. A release 0.3.0 foi promovida com squash nos dois passos ([!84](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/merge_requests/84) e [!86](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/merge_requests/86)), e por isso `hmg` guarda o conteúdo de `develop` em 11/09, mas não o seu histórico. Um MR direto de `develop` para `hmg` conflitaria em 65 arquivos, porque o Git compara as duas pontas com uma base de 28/08.

Como a árvore de `hmg` é idêntica à de `aec6457`, que já está no histórico de `develop`, basta registrar `hmg` como ancestral na branch de release, sem alterar nenhum arquivo:

```bash
git fetch origin
git checkout -b release/0.4.0 origin/develop
git merge -s ours origin/hmg -m "chore(release): registrar hmg como ancestral da 0.4.0 (#243)"
git diff --stat origin/develop HEAD      # deve sair vazio: nenhum arquivo muda
git push -u origin release/0.4.0
# MR release/0.4.0 -> hmg, SEM squash; validar em hmg
# MR hmg -> main, SEM squash
```

A estratégia `-s ours` só é segura quando a árvore descartada já está contida no histórico recebido. Por isso, a verificação de conteúdo vem antes:

```bash
git diff --stat aec6457 origin/hmg       # vazio: hmg é igual a develop em 11/09
git diff --stat origin/hmg origin/main   # vazio: main é igual a hmg
```

O procedimento foi simulado sobre `964cd8c` antes desta entrega: a branch de release fica com a mesma árvore de `develop`, e os merges em `hmg` e depois em `main` terminam sem nenhum conflito. Com os dois MRs de promoção sem squash, `main` passa a conter o histórico de `develop`, e a próxima release volta a ser um merge comum, sem estratégia especial. Depois da promoção, as branches temporárias com MR integrado são removidas conforme a Seção 5.4.

# 10. Regras de governança do GitFlow

- Não é permitido commitar diretamente em `main`, `develop` ou `hmg`;
- Os hooks também bloqueiam commits e pushes diretos em `develop` e `hmg`;
- Toda tarefa versionada deve ser desenvolvida em branch temporária;
- Cada branch temporária deve representar uma issue;
- Toda integração deve passar por Merge Request;
- O título do MR deve ser validado automaticamente no GitLab ou pelo pipeline antes do squash;
- MRs de promoção não usam squash; merge sem squash em branch de trabalho só quando todos os commits passaram pelo hook;
- Nenhum MR pode ser aprovado enquanto houver marcador de conflito em arquivo rastreado;
- O fluxo obrigatório de promoção é `feature/* -> develop -> hmg -> main`;
- `develop` recebe apenas MR aprovado;
- `hmg` recebe versão candidata para validação funcional;
- `main` recebe apenas MR aprovado, com pipeline verde quando disponível e DoD atendida;
- O inventário de MRs ocorre na quarta-feira e a primeira revisão deve acontecer em até 48 horas;
- A revisão final deve acontecer até quinta-feira como cadência interna, para reduzir risco de acúmulo no fechamento;
- O merge para `main` ocorre na sexta-feira como cadência padrão, sob responsabilidade do Scrum Master, mas entregas prontas podem ser promovidas antes por MR, pipeline e aprovação;
- Branches temporárias devem ser removidas após o merge;
- Hotfixes devem voltar para `develop` após serem aplicados em `main`;
- Fontes `.puml` e imagens geradas devem ser versionadas e revisadas juntas;
- O histórico do Git deve permitir rastrear o que foi alterado, por quem, em qual branch e com qual finalidade.
