# Fase 4 — preparação local da substituição da EC2 por SSH

Status: Ready for Review

## Story

Como operador da demonstração M7/g05 no AWS Learner Lab, quero preparar localmente a atualização da stack `m7-g05-mvp` e a operação da EC2 substituta por SSH, para poder inspecionar um change set antes de executá-lo e demonstrar a aplicação sem depender de SSM.

Esta story corrige os artefatos da [story anterior](phase-4-aws-mvp.md), à luz do [handoff](../deploy-aws-learner-lab-handoff.md) e do [replanejamento](../deploy-aws-learner-lab-replan.md). Seu escopo termina antes de qualquer mutação na AWS.

## Critérios de aceite

- [x] **AC1 — Rede e EC2.** `infra/aws/template.yaml` aceita `KeyPairName` e `OperatorSshCidr`; aplica `KeyName` à EC2; permite entrada TCP/22 somente do CIDR `/32` informado; permite saída TCP/7844 e UDP/7844 para o Cloudflare Tunnel; mantém saída necessária ao bootstrap e runtime; e corrige textos e outputs que ainda descrevem operação “SSM-only”. Não declara entrada HTTP pública. O `/32` é revalidado na janela de troca, sem reutilizar IP histórico.
- [x] **AC2 — Isolamento da aplicação.** O Compose e o bootstrap mantêm o frontend em `127.0.0.1:80`, o backend na rede privada e o notebook fora da inicialização e pull padrão. Nenhuma lógica funcional da aplicação muda.
- [x] **AC3 — Mudança controlada.** `scripts/aws/deploy.ps1` separa preflight, criação de change set `UPDATE` na stack existente, inspeção do change set e execução posterior explícita. Criar o change set jamais o executa automaticamente. O preflight não cria nem altera recursos. A substituição da EC2 por `KeyName` e a indisponibilidade correspondente ficam visíveis antes da execução.
- [x] **AC4 — Proveniência e ECR.** O deploy recebe tags imutáveis e digests esperados para backend e frontend, confirma repositórios imutáveis e correspondência real tag/digest no ECR, sem exigir que as tags coincidam com o HEAD. Registra a equivalência das árvores Git entre a tag `0ef613347a33131036e975bb74b5a3b4baa56fca` e o HEAD observado `bae2e9b27b70c6253fb2411bf0459d18a9f58531` como evidência limitada, sem usá-la isoladamente como prova do build. Reutiliza as imagens verificadas; não faz build nem push nesta fase.
- [x] **AC5 — Operação SSH e secrets.** `user-data.sh`, `rollback.ps1` e `docs/aws-operacao.md` descrevem e viabilizam SSH, envio protegido de `runtime.env` sem variáveis `AWS_*`, instalação remota como `root:root` com modo `0600`, inicialização do Compose, diagnóstico e rollback por SSH. Nenhum secret aparece em User Data, CloudFormation, Git, argumentos ou logs. `ssm:StartSession` e `ssm:SendCommand` não são etapas obrigatórias.
- [x] **AC6 — Demonstração externa.** O runbook deixa o Cloudflare Quick Tunnel para depois de SSH e `/health`, apontado a `127.0.0.1:80` na EC2. O URL temporário só é enviado ao cliente depois de teste real. A necessidade de controle de acesso antes de compartilhar o URL, documentada no replanejamento, permanece explícita.
- [x] **AC7 — Verificação local.** Template renderizado, Compose, sintaxe Bash e PowerShell, `git diff --check` e busca de secrets nos arquivos alterados passam. Os gates aplicáveis de lint, typecheck e testes do subprojeto são executados; qualquer comando de `AGENTS.md` ausente em `M7/g05` é registrado com clareza. Checklist e File List desta story são atualizados.
- [x] **AC8 — Limite da fase.** Nenhum recurso AWS é alterado, nenhuma EC2 é parada ou substituída, nenhum change set é criado nesta execução, e não há commit ou push. Valores de `.env` e conteúdo da chave privada não são exibidos.

## Tarefas / Subtarefas

- [x] Ajustar template e conferir ausência de HTTP público (AC1, AC2).
- [x] Reestruturar deploy em preflight, criação, inspeção e execução separada de change set `UPDATE`; validar tags/digests e registrar equivalência Git com limite de evidência (AC3, AC4).
- [x] Ajustar bootstrap, rollback e runbook para SSH, transferência segura do runtime, Compose, diagnóstico e Quick Tunnel posterior (AC5, AC6).
- [x] Executar verificações locais e gates aplicáveis; registrar resultados, riscos e parâmetros da janela de troca (AC7, AC8).
- [x] Atualizar estes checkboxes e a File List antes de concluir (AC7).
- [x] Corrigir a inspeção de `DescribeChangeSet` sem `ChangeSetType` e rejeitar recursos inesperados ou substituição do Security Group.
- [x] Preservar `GroupDescription` e tag `Name` implantados; registrar o change set anterior como obsoleto e validar os cenários focados.

## Dev Notes

- A stack `m7-g05-mvp` já existe em `us-east-1`; a EC2 anterior não tem `KeyName`. A chave pública `m7-g05-learner-lab-2026` foi importada e comparada à chave local no preflight anterior. Revalidar estado, permissões, IP do operador e imagens que possam ter mudado sem exibir credenciais. [Fonte: replanejamento, “Verificação com a sessão AWS de 24/09/2026”; relatório de preflight mais recente na conversa.]
- O preflight anterior registrou repositórios imutáveis e os digests da tag existente: backend `sha256:a36625c35ce19f2fbbba96769d474597ba9227f6ff332cca86735c86ca89ee06`; frontend `sha256:feac52befdf953df04df75abdf1ac79b07fa6abd59f4e3b2a31169fa1d538723`. Reconsultar o ECR antes de usá-los. [Fonte: relatório de preflight mais recente na conversa.]
- O preflight comparou os commits `0ef613347a33131036e975bb74b5a3b4baa56fca` e `bae2e9b27b70c6253fb2411bf0459d18a9f58531` e encontrou a mesma árvore `20dfce2c29db8be07a79eb4f94ff8b5223abdec0`. Isso não comprova, por si, que os blobs ECR foram construídos daquele código. A verificação operacional usa também a imutabilidade das tags e os digests observados. [Fonte: solicitação atual e revalidação read-only comunicada nesta execução.]
- `compose.prod.yml` já publica o frontend em loopback e mantém backend e notebook privados; preservar essa configuração. [Fonte: `compose.prod.yml`; replanejamento, “O que reaproveitar e o que mudar”.]
- O volume antigo não contém artefatos que precisem ser preservados. Mesmo assim, o change set deve mostrar a substituição antes da execução. [Fonte: solicitação atual; replanejamento, “O que reaproveitar e o que mudar”.]
- O acesso por SSH e Quick Tunnel é descrito no replanejamento. Seu alerta sobre `/api/chat` sem autorização efetiva deve permanecer no runbook antes de compartilhar um link externo. [Fonte: replanejamento, “Decisão proposta” e “Sequência de execução proposta”.]
- O handoff documenta falhas do bootstrap e bloqueios para ações SSM. Usá-lo como histórico, não como roteiro operacional. [Fonte: handoff, seções 8–12.]

## Testes e gates previstos

- Validar localmente renderização do template e User Data, sintaxe do template, `docker compose config`, `bash -n`, parse PowerShell, `git diff --check` e varredura de secrets apenas nos arquivos alterados.
- Executar lint, typecheck e testes aplicáveis em `M7/g05`; registrar explicitamente scripts inexistentes. Não criar change set como parte da validação desta story.
- Revisar o modo default de `deploy.ps1` e `rollback.ps1` para garantir que nenhuma ação de AWS seja feita sem opção explícita e que os segredos não sejam interpolados em saídas.

## CodeRabbit Integration

- Tipo primário: Deployment; secundário: Security. Complexidade: média.
- Agentes: @aiox-dev para implementação; @aiox-devops para revisão operacional quando houver futura mudança remota; @aiox-qa para avaliação de qualidade, se solicitada.
- Gate pré-conclusão: revisão das mudanças locais, proteção de secrets, separação das fases do change set e rollback. Pre-PR e pré-deploy ficam fora desta execução.
- Self-healing previsto para @dev: modo light, até 2 iterações e 15 minutos para issues CRITICAL; HIGH documentado. Nenhuma mudança remota automática.

## Dev Agent Record

### Completion Notes

Preparação local implementada sem mutação AWS. O deploy agora consulta e valida a stack existente, o IPv4 público atual do operador, a key pair, ECR imutável e digests; cria um change set UPDATE só em chamada explícita; exige inspeção e execução em outra chamada. A inspeção imprime detalhes de todas as alterações de recursos e exige `ExecutionStatus=AVAILABLE`, stack `CREATE_COMPLETE` e substituição da EC2 por `KeyName`. Inspeção e execução rejeitam o change set se o `OperatorSshCidr` gravado não corresponde mais ao IP público atual do operador. O bootstrap rejeita `AWS_*` no runtime, e o runbook orienta transferência por diretório remoto privado, instalação root:root 0600, SSH, Compose, diagnóstico, rollback e Quick Tunnel após health check. A equivalência das árvores Git é verificada dinamicamente, mas não é tomada isoladamente como prova de build.

Gates: renderização local do template (18.762 bytes, sem marcadores pendentes) e `cloudformation:ValidateTemplate` read-only passaram; `cfn-lint` não estava instalado. `docker compose -f compose.prod.yml config --quiet` passou com avisos de ACL do Docker config local. `bash -n` via Git Bash e parse PowerShell passaram. Frontend: `npm run lint` passou, `npm test` passou (7 arquivos, 57 testes), `npm run build` passou incluindo `tsc --noEmit`. `npm run typecheck` não existe no frontend; `M7/g05` não tem `package.json` raiz para os três comandos de AGENTS.md. Teste e build inicialmente foram bloqueados por ACL do sandbox e passaram em uma única execução escalada cada. A primeira tentativa de ValidateTemplate falhou genericamente no sandbox; uma única chamada read-only escalada passou. WSL Bash estava bloqueado por E_ACCESSDENIED; Git Bash validou a sintaxe. `git diff --check` e busca de secrets em arquivos alterados passaram. Não houve criação de change set, alteração de recursos AWS, commit ou push.

Na janela de troca, revalidar IPv4 `/32` do operador, IP/estado da EC2, chave pública, VPC/subnet/rota, AMI, digests ECR, saldo/cota e permissão efetiva de UPDATE/EC2/SG. Uma simulação IAM não comprova execução. A execução do change set e a saúde do novo runtime ainda não foram testadas nesta fase.

Correção local posterior: `Assert-ChangeSet` não exige `ChangeSetType`, ausente na resposta real de `DescribeChangeSet`. Ele confere nome e ID da stack, nome do change set, `CREATE_COMPLETE/AVAILABLE`, CIDR `/32` atual, substituição da EC2 por `KeyName`, atualização do SG sem replacement e ausência de recursos inesperados. O `GroupDescription` e a tag `Name` do SG foram preservados literalmente após consulta read-only do template implantado. O change set `m7-g05-ssh-9435a35c3cb34a9e8c3459965ade114c` é **OBSOLETO**: foi criado com o template anterior, ainda estava `AVAILABLE` e não foi executado na última consulta; a alteração local não o corrige. A próxima fase requer criar e inspecionar um novo change set.

Gates desta correção passaram: sete verificações locais focadas em resposta sem `ChangeSetType`, EC2 `Replacement=True` por `KeyName`, rejeição de SG `Replacement=True`, CIDR defasado, recurso inesperado e identidade da stack; parse PowerShell de `deploy.ps1` e `test-change-set.ps1`; template renderizado (19.084 bytes) e `ValidateTemplate` somente leitura; `docker compose config --quiet`; e `git diff --check`. O Compose emitiu apenas avisos de ACL do config Docker local. `cfn-lint` permanece indisponível neste ambiente.

### File List

- `docs/stories/phase-4-ec2-ssh-replacement-preparation.md` (checklist, gates e File List)
- `infra/aws/template.yaml` (key pair, SSH /32 e saída Cloudflare)
- `infra/aws/user-data.sh` (bootstrap SSH e proteção de runtime)
- `scripts/aws/deploy.ps1` (preflight, UPDATE change set, inspeção e execução separada)
- `scripts/aws/rollback.ps1` (preflight e rollback por SSH)
- `docs/aws-operacao.md` (runbook SSH e Quick Tunnel)
- `scripts/aws/test-change-set.ps1` (verificações focadas e sem chamadas AWS)

## Change Log

| Data | Versão | Descrição | Autor |
| --- | --- | --- | --- |
| 2026-09-24 | 0.1 | Story Draft para preparação local da troca da EC2. | @aiox-sm |
| 2026-09-24 | 0.2 | Preparação local, gates e registro de riscos. | @aiox-dev |
| 2026-09-24 | 0.3 | Correção local do guard de change set e preservação do Security Group implantado. | @aiox-dev |
