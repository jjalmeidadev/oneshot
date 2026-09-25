# Fase 4 — RabbitMQ privado, workers de alerta e atualização local da aplicação

Status: Ready for Review

## Story

Como operador do MVP M7/g05, quero preparar o Compose de produção com RabbitMQ e quatro workers de alerta, além de um comando de atualização da aplicação por SSH, para atualizar o serviço na EC2 existente sem mudar a stack CloudFormation ou substituir a instância.

Esta story começou com alterações e verificações locais e, depois da revisão, passou a registrar também a aplicação autorizada no Supabase, ECR e EC2. O trabalho sucede [a preparação de SSH](phase-4-ec2-ssh-replacement-preparation.md) e usa o runtime de alertas presente em `src/backend/app/alerts/`.

## Critérios de aceite

- [x] **AC1 — RabbitMQ privado.** `compose.prod.yml` inclui RabbitMQ com imagem de versão fixa, credenciais vindas do runtime protegido, volume persistente e healthcheck. O serviço usa somente `app-private`; as portas 5672 e 15672 não são publicadas no host. O `compose.rabbitmq.yml` local não define o padrão de produção.
- [x] **AC2 — Workers de alerta.** Scheduler, publisher, evaluator e notifier são quatro serviços independentes, reutilizam a imagem do backend e executam `python -m app.alerts.worker <command>` com o comando correspondente. Têm restart, limites de recursos, `read_only` onde compatível e dependência do RabbitMQ saudável. O notebook continua desligado e o frontend permanece em `127.0.0.1:80`.
- [x] **AC3 — Configuração explícita.** API e workers recebem `ALERT_REPOSITORY_MODE=database`, `ALERT_SCHEDULE_SOURCE=database`, `DATABASE_URL` ou `SUPABASE_DATABASE_URL`, `ALERT_CONFIRMATION_SECRET`, `RABBITMQ_URL`, configurações existentes de pool/timeout e demais variáveis necessárias ao runtime. As interpolações do Compose são explícitas; os secrets vêm somente do arquivo protegido e não são embutidos em imagem, template, User Data, Git, argumentos ou logs. Validar que `RABBITMQ_URL` e as credenciais do broker são coerentes.
- [x] **AC4 — Bootstrap e logs.** `infra/aws/user-data.sh` valida a nova configuração necessária, rejeita `AWS_*` em `runtime.env`, mantém esse arquivo como `root:root` modo `0600`, inicia API, frontend, RabbitMQ e quatro workers pelo Compose e acompanha logs de todos os sete serviços. O bootstrap não imprime os valores da configuração.
- [x] **AC5 — Atualização controlada.** `scripts/aws/update-app.ps1` separa preflight somente leitura de execução com confirmação explícita. O preflight valida identidade AWS, stack, EC2, key pair, tags imutáveis e digests ECR, host SSH e arquivos locais necessários. A execução usa staging protegido, salva cópias do Compose e de `deploy.env`, atualiza tags, faz pull e `up`, verifica health e restaura a configuração anterior se falhar. Nenhum secret aparece em argumentos, saídas ou logs.
- [x] **AC6 — Runbook.** `docs/aws-operacao.md` descreve a atualização da aplicação por SSH sem update de CloudFormation nem substituição da EC2, incluindo preflight, confirmação, verificação e rollback. O procedimento preserva a restrição de HTTP público e o notebook fora da subida padrão.
- [x] **AC7 — Gates locais.** Validar Compose renderizado, sintaxe PowerShell e Bash, `git diff --check`, busca de secrets nos arquivos alterados, lint, testes e build aplicáveis. Registrar comandos de `AGENTS.md` que não existam em `M7/g05`, sem tratar ausência como sucesso. Atualizar checklist e File List desta story com resultados.
- [x] **AC8 — Limites da preparação.** A implementação local foi revisada antes das operações remotas. As aplicações posteriores no Supabase, ECR e EC2 foram autorizadas, executadas em etapas e registradas nas Completion Notes; a atualização da aplicação não substituiu a EC2.
- [x] **AC9 — Migração 08 segura.** A migração remove somente confirmações legadas sem resposta/modelo preparados que estejam expiradas e não reivindicadas; qualquer outra linha incompleta aborta a transação antes de `NOT NULL`. A tabela recebe RLS e revogação de `anon`/`authenticated`, com `prepared_interaction_id` opcional.
- [x] **AC10 — Ordem e operação de migrações.** O gerenciamento e o runbook exigem 08 antes do novo runtime, reconhecem o schema 15 compatível sem reaplicá-lo, e tratam 16 como rollback destrutivo que exige decisão explícita. O backend usa a conexão PostgreSQL privada.
- [x] **AC11 — Verificação local da migração.** Testes focados cobrem linhas ativas e reivindicadas; gates aplicáveis passam sem acesso remoto. Testes focados, ensaio PostgreSQL e suíte completa do backend passaram.

## Tarefas / Subtarefas

- [x] Integrar broker privado e quatro workers ao Compose de produção (AC1, AC2, AC3).
- [x] Adaptar validação de runtime, inicialização e encaminhamento de logs no User Data (AC4).
- [x] Criar `update-app.ps1` com preflight e execução separada, staging, backup, health e restauração (AC5).
- [x] Atualizar o runbook de operação SSH para atualização da aplicação (AC6).
- [x] Executar os gates locais e registrar evidências, limites e arquivos tocados (AC7, AC8).
- [x] Corrigir a migração 08, o script de gerenciamento, testes e runbook sem operações remotas (AC9–AC11).

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

Implantação real concluída em 25/09/2026. A migração 08 foi aplicada no Supabase antes do runtime; as imagens backend e frontend da tag imutável `f776feb352c3556d02e83dc14eea49b0d795f6b9` foram confirmadas no ECR e instaladas na EC2 `i-0f31228a6d73a765b`. O fluxo de atualização fez backup protegido, atualizou os sete serviços e concluiu o health check. RabbitMQ, backend e frontend ficaram saudáveis; scheduler, publisher, evaluator e notifier permaneceram em execução e a conexão PostgreSQL foi comprovada de dentro do contêiner backend.

O ensaio real encontrou e corrigiu três incompatibilidades: a chamada remota agora passa o diretório de staging exigido pelo executor; o backup aceita a configuração consumida do CloudWatch Agent quando o arquivo canônico ainda não existe; e os quatro `tmpfs` dos workers são strings YAML para preservar as opções separadas por vírgula. O Security Group recebeu saída TCP/5432 por change set CloudFormation inspecionado, sem substituição, para alcançar o session pooler do Supabase. O template local registra essa regra.

O Quick Tunnel foi instalado como serviço systemd protegido e ficou ativo sem reinícios. Pelo endereço HTTPS temporário, `/health` e `/` retornaram HTTP 200. Uma única chamada curta a `/api/chat` também retornou HTTP 200, com texto e modelo presentes. Nenhum secret foi impresso ou gravado no repositório.

Revisão local da migração 08: a limpeza agora exige linha incompleta, expirada e não reivindicada; uma guarda com `RAISE EXCEPTION` interrompe a transação antes de `NOT NULL` se restar qualquer linha incompleta. RLS e revogação de `anon`/`authenticated` entram na mesma transação. O gerenciador oferece `prepare-proactive` com confirmação explícita, exige 08 pronta para `apply`, recusa reaplicar 15 quando há qualquer tabela de alertas, e exige confirmação destrutiva para 16. O runbook registra a ordem e o acesso pela conexão PostgreSQL privada. Nenhuma operação remota foi feita nesta revisão.

Gates desta revisão: 12 testes focados passaram; `compileall` dos Python alterados e `git diff --check` passaram. Um PostgreSQL 17 local, em contêiner sem rede e com dados sintéticos, confirmou que 08 remove apenas o legado expirado não reivindicado, conserva a linha preparada, habilita RLS/revoga privilégios e aplica `NOT NULL`. No caso com registros ativos e reivindicados incompletos, `RAISE EXCEPTION` ocorreu e a transação desfez inclusive a exclusão provisória: três linhas e o schema anterior permaneceram. O contêiner temporário foi encerrado. O venv local recebeu `python-docx` e `psycopg-pool`, já declarados em `requirements.txt`, e `pip check` não encontrou requisitos quebrados. A configuração local do encoder foi alinhada ao BERTimbau e à revisão imutável documentados no `.env.example`; o snapshot foi armazenado no cache ignorado pelo Git. A suíte completa passou com 383 testes, 12 skips e 1 xfail. `M7/g05` não tem `package.json` raiz nem comandos npm aplicáveis a esta mudança de SQL/backend; nenhum arquivo frontend foi alterado.

Preparação local concluída. O Compose de produção declara RabbitMQ privado e quatro workers que reutilizam a imagem backend; o health check HTTP herdado da imagem foi desativado somente nesses workers. O User Data valida o runtime e prepara sete fluxos de log. `update-app.ps1` separa preflight somente leitura de execução confirmada e usa o executor remoto para staging privado, backup root-only, pull, subida, health check e tentativa de restauração em falha. Nenhuma execução do novo script foi feita contra AWS/EC2 ou Supabase nesta story; a imagem ECR futura e o esquema de alertas do banco ainda exigem validação na janela real.

Gates locais: Compose renderizado com valores fictícios e sete serviços no perfil padrão, sem portas do broker e com frontend em loopback; funções locais de validação do `update-app.ps1` ensaiadas sem AWS; sintaxe PowerShell e Bash válidas; User Data renderizado offline; JSON do CloudWatch Agent válido; `git diff --check` sem erro; busca de valores sensíveis nos arquivos alterados sem achados. Frontend: `npm run lint` passou, `npm test` passou (59 testes), `npm run build` passou (inclui `tsc --noEmit`). Backend: 41 testes focados passaram no venv local após instalar dependências já declaradas e `tzdata` para Windows; build Docker no alvo `test` passou com 377 testes, 12 skips e 1 xfail. `npm run typecheck` não existe em `src/frontend`; `M7/g05` não tem `package.json` raiz para os comandos npm genéricos de `AGENTS.md`. O primeiro teste frontend sob sandbox falhou por ACL do esbuild; a repetição fora do sandbox passou. O `bash` padrão do WSL foi negado neste ambiente; Git Bash validou os dois scripts.

### Checklist

- [x] Critérios AC1–AC11 verificados.
- [x] Gates locais e seus resultados registrados.
- [x] Nenhuma ação AWS/Supabase ou Git remota executada.
- [x] File List atualizada.
- [x] Migração 08, gerenciamento e documentação revisados; testes focados e suíte completa do backend passaram.
- [x] Atualização real executada na EC2; sete serviços e conexão PostgreSQL verificados.
- [x] Quick Tunnel verificado externamente em `/health`, frontend e chat.

### File List

- `docs/stories/phase-4-alert-workers-local-update.md` (critérios, checklist, gates e File List)
- `compose.prod.yml` (RabbitMQ privado, configuração explícita e quatro workers)
- `infra/aws/user-data.sh` (validação do runtime, subida e logs dos sete serviços)
- `infra/aws/template.yaml` (saída TCP/5432 para o session pooler PostgreSQL)
- `infra/aws/cloudwatch-agent.json` (fluxos de log dos sete serviços)
- `scripts/aws/common.ps1` (renderização do marcador User Data com CRLF)
- `scripts/aws/update-app.ps1` (preflight local/AWS/SSH e execução confirmada)
- `scripts/aws/update-app-remote.sh` (staging, backup, pull, health e restauração)
- `docs/aws-operacao.md` (fluxo de atualização sem CloudFormation)
- `src/database/sql/08_add_prepared_proactive_response.sql` (limpeza restrita, guarda transacional, RLS e revogação)
- `src/backend/scripts/manage_alert_infrastructure.py` (ordem 08/15 e confirmação destrutiva para 16)
- `src/backend/app/tests/test_secondary_intents_sql.py` (contrato do predicado e guarda da migração)
- `src/backend/app/tests/test_manage_alert_infrastructure.py` (gates locais do gerenciador)

## Change Log

| Data | Versão | Descrição | Autor |
| --- | --- | --- | --- |
| 2026-09-24 | 0.1 | Story Draft para RabbitMQ, workers de alerta e atualização local. | @aiox-sm |
| 2026-09-24 | 0.2 | Implementação local, gates e instruções operacionais para atualização SSH. | @aiox-dev |
| 2026-09-25 | 0.3 | Migração 08 segura, ordem operacional e testes locais. | @aiox-data-engineer |
| 2026-09-25 | 0.4 | Dependências locais corrigidas, BERTimbau alinhado e suíte completa aprovada. | @aiox-dev |
| 2026-09-25 | 0.5 | Atualização real da EC2, correções operacionais, Supabase e Quick Tunnel validados. | @aiox-devops |
