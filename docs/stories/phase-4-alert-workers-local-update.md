# Fase 4 — RabbitMQ privado, workers de alerta e atualização local da aplicação

Status: Ready for Review

## Story

Como operador do MVP M7/g05, quero preparar o Compose de produção com RabbitMQ e quatro workers de alerta, além de um comando de atualização da aplicação por SSH, para atualizar o serviço na EC2 existente sem mudar a stack CloudFormation ou substituir a instância.

Esta story cobre apenas alterações e verificações locais. Nenhuma operação AWS ou Supabase, commit ou push faz parte desta execução. O trabalho sucede [a preparação de SSH](phase-4-ec2-ssh-replacement-preparation.md) e usa o runtime de alertas já presente em `src/backend/app/alerts/`.

## Critérios de aceite

- [x] **AC1 — RabbitMQ privado.** `compose.prod.yml` inclui RabbitMQ com imagem de versão fixa, credenciais vindas do runtime protegido, volume persistente e healthcheck. O serviço usa somente `app-private`; as portas 5672 e 15672 não são publicadas no host. O `compose.rabbitmq.yml` local não define o padrão de produção.
- [x] **AC2 — Workers de alerta.** Scheduler, publisher, evaluator e notifier são quatro serviços independentes, reutilizam a imagem do backend e executam `python -m app.alerts.worker <command>` com o comando correspondente. Têm restart, limites de recursos, `read_only` onde compatível e dependência do RabbitMQ saudável. O notebook continua desligado e o frontend permanece em `127.0.0.1:80`.
- [x] **AC3 — Configuração explícita.** API e workers recebem `ALERT_REPOSITORY_MODE=database`, `ALERT_SCHEDULE_SOURCE=database`, `DATABASE_URL` ou `SUPABASE_DATABASE_URL`, `ALERT_CONFIRMATION_SECRET`, `RABBITMQ_URL`, configurações existentes de pool/timeout e demais variáveis necessárias ao runtime. As interpolações do Compose são explícitas; os secrets vêm somente do arquivo protegido e não são embutidos em imagem, template, User Data, Git, argumentos ou logs. Validar que `RABBITMQ_URL` e as credenciais do broker são coerentes.
- [x] **AC4 — Bootstrap e logs.** `infra/aws/user-data.sh` valida a nova configuração necessária, rejeita `AWS_*` em `runtime.env`, mantém esse arquivo como `root:root` modo `0600`, inicia API, frontend, RabbitMQ e quatro workers pelo Compose e acompanha logs de todos os sete serviços. O bootstrap não imprime os valores da configuração.
- [x] **AC5 — Atualização controlada.** `scripts/aws/update-app.ps1` separa preflight somente leitura de execução com confirmação explícita. O preflight valida identidade AWS, stack, EC2, key pair, tags imutáveis e digests ECR, host SSH e arquivos locais necessários. A execução usa staging protegido, salva cópias do Compose e de `deploy.env`, atualiza tags, faz pull e `up`, verifica health e restaura a configuração anterior se falhar. Nenhum secret aparece em argumentos, saídas ou logs.
- [x] **AC6 — Runbook.** `docs/aws-operacao.md` descreve a atualização da aplicação por SSH sem update de CloudFormation nem substituição da EC2, incluindo preflight, confirmação, verificação e rollback. O procedimento preserva a restrição de HTTP público e o notebook fora da subida padrão.
- [x] **AC7 — Gates locais.** Validar Compose renderizado, sintaxe PowerShell e Bash, `git diff --check`, busca de secrets nos arquivos alterados, lint, testes e build aplicáveis. Registrar comandos de `AGENTS.md` que não existam em `M7/g05`, sem tratar ausência como sucesso. Atualizar checklist e File List desta story com resultados.
- [x] **AC8 — Limites de execução.** A fase não acessa AWS ou Supabase, não cria change set, não para nem substitui EC2, não publica imagens em ECR e não faz commit/push Git. Builds de teste permanecem locais.

## Tarefas / Subtarefas

- [x] Integrar broker privado e quatro workers ao Compose de produção (AC1, AC2, AC3).
- [x] Adaptar validação de runtime, inicialização e encaminhamento de logs no User Data (AC4).
- [x] Criar `update-app.ps1` com preflight e execução separada, staging, backup, health e restauração (AC5).
- [x] Atualizar o runbook de operação SSH para atualização da aplicação (AC6).
- [x] Executar os gates locais e registrar evidências, limites e arquivos tocados (AC7, AC8).

## Dev Notes

- `compose.prod.yml` hoje tem backend, frontend e notebook opcional. O frontend usa bind padrão `127.0.0.1:80`; o backend está em `app-private`. [Fonte: `compose.prod.yml`.]
- `compose.rabbitmq.yml` é usado para desenvolvimento local e expõe 5672 e 15672 com credenciais de exemplo. A implantação pedida requer configuração privada no Compose de produção. [Fonte: `compose.rabbitmq.yml`; pedido atual.]
- `src/backend/app/alerts/worker.py` já aceita os comandos `scheduler`, `publisher`, `evaluator` e `notifier`. `src/backend/app/alerts/messaging.py` exige `RABBITMQ_URL`. [Fonte: arquivos indicados.]
- `src/backend/.env.example` documenta os nomes de variáveis de banco, alertas, pool e timeout; valores de exemplo não são credenciais de produção. [Fonte: `src/backend/.env.example`, seções Database e Alerts.]
- A story SSH anterior define transferência protegida de `runtime.env`, frontend em loopback e operação sem SSM. Este trabalho acrescenta atualização da aplicação sem mutação da infraestrutura. [Fonte: `docs/stories/phase-4-ec2-ssh-replacement-preparation.md`; pedido atual.]

## Testes e gates previstos

- Renderizar Compose com valores fictícios protegidos e verificar que broker não publica portas, workers usam a imagem correta e notebook não inicia no profile padrão.
- Analisar sintaxe de PowerShell e Bash, renderização do User Data, `git diff --check` e ausência de secrets nos arquivos alterados.
- Executar lint, typecheck, testes e build aplicáveis no subprojeto; registrar comandos ausentes de `AGENTS.md`.
- Ensaiar apenas o preflight local do script com chamadas externas bloqueadas ou mocks, sem acesso AWS ou Supabase nesta execução.

## CodeRabbit Integration

- Tipo primário: Deployment; secundários: Integration e Security. Complexidade: média.
- Agentes: @aiox-dev para implementação; @aiox-devops para futura operação remota; @aiox-qa para avaliação de qualidade, se solicitada.
- Foco de revisão: não exposição do broker, proteção de secrets, separação entre preflight e execução, backup/restauração e isolamento dos serviços.
- Self-healing previsto para @dev: modo light, até 2 iterações e 15 minutos para issues CRITICAL; HIGH documentado. Nenhuma mudança remota automática.

## Dev Agent Record

### Completion Notes

Preparação local concluída. O Compose de produção declara RabbitMQ privado e quatro workers que reutilizam a imagem backend; o health check HTTP herdado da imagem foi desativado somente nesses workers. O User Data valida o runtime e prepara sete fluxos de log. `update-app.ps1` separa preflight somente leitura de execução confirmada e usa o executor remoto para staging privado, backup root-only, pull, subida, health check e tentativa de restauração em falha. Nenhuma execução do novo script foi feita contra AWS/EC2 ou Supabase nesta story; a imagem ECR futura e o esquema de alertas do banco ainda exigem validação na janela real.

Gates locais: Compose renderizado com valores fictícios e sete serviços no perfil padrão, sem portas do broker e com frontend em loopback; funções locais de validação do `update-app.ps1` ensaiadas sem AWS; sintaxe PowerShell e Bash válidas; User Data renderizado offline; JSON do CloudWatch Agent válido; `git diff --check` sem erro; busca de valores sensíveis nos arquivos alterados sem achados. Frontend: `npm run lint` passou, `npm test` passou (59 testes), `npm run build` passou (inclui `tsc --noEmit`). Backend: 41 testes focados passaram no venv local após instalar dependências já declaradas e `tzdata` para Windows; build Docker no alvo `test` passou com 377 testes, 12 skips e 1 xfail. `npm run typecheck` não existe em `src/frontend`; `M7/g05` não tem `package.json` raiz para os comandos npm genéricos de `AGENTS.md`. O primeiro teste frontend sob sandbox falhou por ACL do esbuild; a repetição fora do sandbox passou. O `bash` padrão do WSL foi negado neste ambiente; Git Bash validou os dois scripts.

### Checklist

- [x] Critérios AC1–AC8 verificados ou pendências registradas.
- [x] Gates locais e seus resultados registrados.
- [x] Nenhuma ação AWS/Supabase ou Git remota executada.
- [x] File List atualizada.

### File List

- `docs/stories/phase-4-alert-workers-local-update.md` (critérios, checklist, gates e File List)
- `compose.prod.yml` (RabbitMQ privado, configuração explícita e quatro workers)
- `infra/aws/user-data.sh` (validação do runtime, subida e logs dos sete serviços)
- `infra/aws/cloudwatch-agent.json` (fluxos de log dos sete serviços)
- `scripts/aws/common.ps1` (renderização do marcador User Data com CRLF)
- `scripts/aws/update-app.ps1` (preflight local/AWS/SSH e execução confirmada)
- `scripts/aws/update-app-remote.sh` (staging, backup, pull, health e restauração)
- `docs/aws-operacao.md` (fluxo de atualização sem CloudFormation)

## Change Log

| Data | Versão | Descrição | Autor |
| --- | --- | --- | --- |
| 2026-09-24 | 0.1 | Story Draft para RabbitMQ, workers de alerta e atualização local. | @aiox-sm |
| 2026-09-24 | 0.2 | Implementação local, gates e instruções operacionais para atualização SSH. | @aiox-dev |
