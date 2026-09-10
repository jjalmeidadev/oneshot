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
  - [5.4 Exclusão de branch](#54-exclusão-de-branch)
- [6. Fluxo de desenvolvimento](#6-fluxo-de-desenvolvimento)
  - [6.1 Fluxo de feature](#61-fluxo-de-feature)
  - [6.2 Fluxo de release](#62-fluxo-de-release)
  - [6.3 Fluxo de hotfix](#63-fluxo-de-hotfix)
- [7. Hooks de Git](#7-hooks-de-git)
  - [7.1 Como ativar, verificar e desativar](#71-como-ativar-verificar-e-desativar)
  - [7.2 Validações executadas](#72-validações-executadas)
  - [7.3 Auditoria do repositório](#73-auditoria-do-repositório)
- [8. Versionamento de artefatos de modelo](#8-versionamento-de-artefatos-de-modelo)
  - [8.1 O que é versionado e por quê](#81-o-que-é-versionado-e-por-quê)
  - [8.2 A restrição que vem junto](#82-a-restrição-que-vem-junto)
- [9. Exemplos práticos](#9-exemplos-práticos)
  - [9.1 Atualização da gestão de projeto](#91-atualização-da-gestão-de-projeto)
  - [9.2 Preparação de entrega](#92-preparação-de-entrega)
  - [9.3 Integração de entrega documental com renumeração de seções](#93-integração-de-entrega-documental-com-renumeração-de-seções)
  - [9.4 Hotfix](#94-hotfix)
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
- Exemplos práticos de aplicação do fluxo no contexto do projeto.

## 1.2 Escopo

Este documento cobre exclusivamente a gestão de branches e o fluxo GitFlow. Políticas detalhadas de daily, Kanban, contrato de trabalho, papéis e planejamento de sprint pertencem ao documento de gestão de projeto.

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
| `release/*` | Preparação de uma versão candidata à entrega. | `develop` | `hmg`, `main` e `develop` |
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

O grupo utiliza merge com squash, e o commit resultante é criado pelo servidor: ele **não passa pelos hooks locais** e herda o título do merge request, que por padrão vem do nome da branch. O efeito é direto sobre a rastreabilidade — na Sprint 1, 6 de 19 commits de squash seguiram a convenção; na Sprint 2, 4 de 13, sem que ninguém tivesse desobedecido nenhuma regra.

Por isso, **conferir o título do merge request é item obrigatório do checklist de revisão**, antes da aprovação. O revisor deve garantir que o título esteja no formato `<tipo>: <descrição curta> (#<issue>)`. Títulos como `feat/implementar-frontend-inicial-mockado` ou `Docs/comparacao das alternativas` indicam que o campo não foi editado.

Há um segundo efeito do squash que vale conhecer: o commit gerado registra no campo de committer o nome de quem aprovou o merge, e não o de quem escreveu o código. A autoria original é preservada no campo de autor, mas não aparece em contagens que usam o committer.

### 5.3.2 Marco de integração

Todo merge request aberto até **quarta-feira** deve estar revisado e mergeado até o fim daquele dia, ou ter o bloqueio declarado na issue correspondente. A regra existe porque, no fechamento da Sprint 2, quatro merge requests com entregas concluídas permaneceram abertos — o trabalho existia, mas não estava em `develop`, que é onde o repositório é avaliado. O risco correspondente está registrado como R11 no `GestaoProjeto.md`.

## 5.4 Exclusão de branch

Após o merge, a branch temporária deve ser excluída para manter o repositório limpo.

Pelo GitLab, a exclusão pode ser feita pela opção de remover a source branch após o merge.

Por comando:

```bash
git push origin --delete docs/gestao-projeto
git branch -d docs/gestao-projeto
```

Branches temporárias só devem permanecer abertas quando houver trabalho ainda em andamento ou revisão pendente.

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
- Se uma entrega estiver pronta e outra não, o grupo deve usar MR individual, feature flag ou branch de release para não bloquear promoção de trabalho concluído.

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

A validação de arquivos sensíveis bloqueia `.env`, `.env.*`, `*.pem`, `*.key` e nomes contendo `secret` ou `credential`. Desde a Sprint 2, arquivos terminados em `*.example`, `*.sample` e `*.template` são avaliados antes dessa regra e liberados: são templates de configuração sem segredo, feitos para serem versionados. A exceção foi acrescentada quando `src/backend/.env.example` — que já estava em `develop` — passou a bloquear qualquer commit local que tocasse a árvore. O arquivo entrou no repositório sem passar pela validação justamente porque foi integrado por squash no servidor.
| `.githooks/commit-msg` | Ao validar a mensagem de commit | Exige Conventional Commits, primeira linha com no máximo 72 caracteres e referência a issue no formato `#N`. |
| `.githooks/pre-push` | Antes do push | Bloqueia push direto para branches permanentes, valida prefixo da branch local e confere se commits novos seguem Conventional Commits e referenciam issue. |

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

# 8. Versionamento de artefatos de modelo

O repositório versiona os artefatos gerados pelo treinamento do classificador de intenções, em `src/notebooks/artefatos/`. A decisão foi tomada na Sprint 2, quando o notebook de classificação entrou no projeto, e é registrada aqui porque tem consequência permanente sobre o tamanho do repositório.

## 8.1 O que é versionado e por quê

| Artefato | Tamanho aproximado | Motivo |
| --- | ---: | --- |
| `classificador_intencoes.joblib` | 14,5 MB | Modelo serializado da execução de referência, mantido como evidência do resultado documentado na Seção 8.9 do `Projeto.md` |
| `word2vec_portfolio.model` | 0,9 MB | Representação treinada no corpus do projeto, necessária para reproduzir a inferência sem novo treinamento |
| `dataset_intencoes.csv` | 0,8 MB | Conjunto sintético que sustenta a separação por `template_id` descrita no protocolo de avaliação |
| `catalogo_intencoes.csv` e `.json` | poucos KB | Catálogo das intenções reconhecidas, consultado pelo roteamento |
| `metricas.json` | poucos KB | Métricas da execução de referência, citadas na documentação |

A escolha é deliberada: manter os artefatos permite conferir os números publicados sem reexecutar o notebook, o que importa em um projeto avaliado por evidência.

## 8.2 A restrição que vem junto

O Git preserva todas as versões de um arquivo binário. Cada nova versão do `.joblib` acrescenta cerca de 14 MB **permanentes** ao repositório, que todo integrante baixa a cada clone e que não podem ser removidos sem reescrever o histórico.

Por isso valem as regras abaixo.

- **Não commitar artefatos a cada retreino.** Execuções exploratórias, ajustes de hiperparâmetro e testes de configuração permanecem locais. Só entra no repositório o artefato correspondente à **execução de referência** citada na documentação.
- **Atualizar o artefato apenas quando o resultado documentado mudar.** Se a Seção 8.9 do `Projeto.md` continua reportando as mesmas métricas, não há motivo para substituir o binário.
- **Declarar a substituição no merge request.** Quando um artefato for atualizado, o MR deve informar qual execução o gerou e quais métricas mudaram, para que a troca de 14 MB tenha justificativa registrada.
- **Manter os arquivos leves sempre atualizados.** `catalogo_intencoes` e `metricas.json` são pequenos e devem acompanhar qualquer mudança, mesmo quando o modelo serializado não for substituído.

Caso o volume se torne um problema, a alternativa prevista é migrar os binários para Git LFS, preservando a rastreabilidade sem carregar o histórico. A avaliação dessa migração fica condicionada ao crescimento observado do repositório.

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

# 10. Regras de governança do GitFlow

- Não é permitido commitar diretamente em `main`, `develop` ou `hmg`;
- Os hooks também bloqueiam commits e pushes diretos em `develop` e `hmg`;
- Toda tarefa versionada deve ser desenvolvida em branch temporária;
- Cada branch temporária deve representar uma issue;
- Toda integração deve passar por Merge Request;
- O fluxo obrigatório de promoção é `feature/* -> develop -> hmg -> main`;
- `develop` recebe apenas MR aprovado;
- `hmg` recebe versão candidata para validação funcional;
- `main` recebe apenas MR aprovado, com pipeline verde quando disponível e DoD atendida;
- A revisão deve acontecer até quinta-feira como cadência interna, para reduzir risco de acúmulo no fechamento;
- O merge para `main` ocorre na sexta-feira como cadência padrão, sob responsabilidade do Scrum Master, mas entregas prontas podem ser promovidas antes por MR, pipeline e aprovação;
- Branches temporárias devem ser removidas após o merge;
- Hotfixes devem voltar para `develop` após serem aplicados em `main`;
- O histórico do Git deve permitir rastrear o que foi alterado, por quem, em qual branch e com qual finalidade.
