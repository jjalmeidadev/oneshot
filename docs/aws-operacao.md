# Operação AWS Learner Lab — M7/g05

## Arquitetura e limites

A stack existente `m7-g05-mvp` em `us-east-1` tem uma EC2 `t3.large`, EBS raiz gp3 criptografado de 50 GiB, Security Group e Log Group. VPC, subnet, `LabInstanceProfile` e os repositórios ECR são externos. O frontend fica em `127.0.0.1:80` no host, o backend só na rede privada do Compose e o notebook não inicia nem é puxado por padrão. Não há entrada HTTP pública. SSH TCP/22 aceita somente o IPv4 atual do operador `/32`. O Cloudflare Tunnel, se usado na EC2, precisa de saída TCP e UDP/7844. TCP/80 e TCP/443 de saída continuam necessários ao bootstrap e runtime.

O User Data não recebe secrets. A instância usa a instance profile para pull ECR e logs. O `runtime.env` é transferido por SSH depois do bootstrap. A troca de `KeyName` no CloudFormation **substitui a EC2**, causando indisponibilidade; o volume raiz antigo será removido. O operador confirmou que não é necessário preservar seus artefatos.

O `GroupDescription` legado (`M7/g05 SSM-only MVP; no inbound network access.`) e a tag `Name` com sufixo `-ssm-only` permanecem literalmente iguais aos do template implantado para evitar a substituição do Security Group. Esses textos históricos não descrevem as novas regras: a entrada SSH `/32` e a saída TCP/UDP 7844 estão declaradas no template. A inspeção deve rejeitar qualquer change set que proponha substituir o SG.

## Evidência das imagens

Os repositórios `m7-g05-backend` e `m7-g05-frontend` usam tags imutáveis. A tag de reuso é `0ef613347a33131036e975bb74b5a3b4baa56fca`. Digests observados no preflight de 24/09/2026:

| Imagem | Digest esperado |
| --- | --- |
| Backend | `sha256:a36625c35ce19f2fbbba96769d474597ba9227f6ff332cca86735c86ca89ee06` |
| Frontend | `sha256:feac52befdf953df04df75abdf1ac79b07fa6abd59f4e3b2a31169fa1d538723` |

O commit da tag e o HEAD observado `bae2e9b27b70c6253fb2411bf0459d18a9f58531` tinham a árvore Git `20dfce2c29db8be07a79eb4f94ff8b5223abdec0`. Essa igualdade é evidência limitada: sozinha, não comprova como as imagens foram construídas. O deploy consulta novamente imutabilidade e tag/digest no ECR. Não há rebuild ou push nesta fase.

## Atualização da aplicação na EC2 existente

Depois da substituição da EC2, atualizações de Compose e imagens da aplicação usam `scripts/aws/update-app.ps1` por SSH. Esse fluxo não cria change set, não altera CloudFormation e não substitui a instância. Passe o `InstanceId` atual obtido da stack, a chave privada correspondente à key pair importada, tags e digests imutáveis que já existam no ECR e um `runtime.env` protegido fora do repositório. A atualização local desta story não cria nem publica essas imagens. Antes de uma janela real, confirme que a imagem backend escolhida contém `app.alerts.worker` e que o esquema de alertas no banco está aplicado; o health check HTTP não prova o fluxo de alertas.

O `runtime.env` deve conter as variáveis já exigidas para Gemini e Azure Speech, além de `DATABASE_URL` **ou** `SUPABASE_DATABASE_URL`, `ALERT_CONFIRMATION_SECRET`, `RABBITMQ_USER`, `RABBITMQ_PASSWORD`, `RABBITMQ_URL`, `DATABASE_POOL_MAX_SIZE` e `DATABASE_STATEMENT_TIMEOUT_MS`. Use uma URL `amqp://` com host `rabbitmq`, porta 5672 e usuário/senha compatíveis com `RABBITMQ_USER` e `RABBITMQ_PASSWORD`; escolha usuário diferente de `guest` e codifique caracteres reservados da senha na URL. Não inclua `AWS_*`. O Compose injeta explicitamente as variáveis em API e workers; `--env-file` sozinho apenas fornece valores para interpolação. O broker usa a imagem `rabbitmq:4.1.8-alpine`, volume persistente e somente `app-private`, sem publicação de 5672 ou 15672. Scheduler, publisher, evaluator e notifier usam a mesma imagem backend; o notebook continua fora da subida padrão.

Exemplo sem valores sensíveis na linha de comando:

```powershell
$update = @{
  InstanceId = '<INSTANCE_ID_ATUAL_DA_STACK>'
  PrivateKeyPath = '<CHAVE_PRIVADA_FORA_DO_REPO>'
  RuntimeEnvPath = '<RUNTIME_ENV_PROTEGIDO_FORA_DO_REPO>'
  EcrRegistryUri = '<CONTA>.dkr.ecr.us-east-1.amazonaws.com'
  BackendImageTag = '<SHA40_BACKEND>'
  FrontendImageTag = '<SHA40_FRONTEND>'
  BackendImageDigest = 'sha256:<DIGEST_BACKEND>'
  FrontendImageDigest = 'sha256:<DIGEST_FRONTEND>'
}
.\scripts\aws\update-app.ps1 @update
# Somente na janela autorizada, após revisar o preflight:
.\scripts\aws\update-app.ps1 @update -Action Execute -ConfirmUpdate
```

O preflight consulta STS, stack, EC2, key pair e ECR em leitura, renderiza o Compose localmente sem imprimi-lo, confirma a host key previamente registrada em `known_hosts` e testa acesso SSH somente em leitura. Verifique o fingerprint da host key por canal independente antes do primeiro SSH; não use `StrictHostKeyChecking=no`. O modo Execute exige `-ConfirmUpdate` e confirmação PowerShell. Ele cria um staging remoto privado, transfere Compose, `runtime.env`, configuração do CloudWatch Agent e o executor remoto, salva backup root-only do Compose, `deploy.env`, runtime e configuração anterior, atualiza tags, faz pull, inicia os sete serviços e verifica `/health` e processos. Em falha, restaura os arquivos anteriores e tenta voltar os containers à configuração salva. Verifique o estado manualmente antes de qualquer nova tentativa. O backup contém secrets e permanece root-only para recuperação controlada.

Após sucesso, confirme por SSH `sudo /usr/local/bin/m7-compose ps` e `curl --fail --silent --output /dev/null http://127.0.0.1:80/health`, além de um fluxo de alerta com dados sintéticos. Os logs locais e o CloudWatch Agent cobrem backend, frontend, RabbitMQ e quatro workers; revise-os antes de compartilhar qualquer trecho. O CloudWatch Agent da EC2 existente é atualizado pelo script de aplicação, pois editar User Data local não o reaplica à instância atual. Não rode `docker compose config` sem `--quiet` com runtime real em terminal, porque a configuração renderizada contém secrets.

## Histórico da troca da EC2: preflight e change set

Esta seção registra o procedimento da substituição já concluída. Para atualizar somente a aplicação na EC2 existente, use a seção anterior e não execute os change sets históricos.

Renove as credenciais temporárias em `src/backend/.env`; o helper carrega só as quatro variáveis AWS no processo e não imprime valores. Reconsulte stack, EC2, Key Pair, VPC, subnet, rota, AMI, ECR e permissões. Consulte o IPv4 público **atual** do operador, forme `/32`, e não use endereços de relatórios antigos. Confirme saldo e cota do Learner Lab para substituição. Confirme também que a chave pública importada `m7-g05-learner-lab-2026` corresponde à privada local. A simulação IAM não prova que a execução real será aceita.

Use `scripts/aws/deploy.ps1` com parâmetros `VpcId`, `SubnetId`, `AmiId`, `InstanceType`, `RootVolumeSize`, `InstanceProfileName`, `EcrRegistryUri`, `BackendImageTag`, `FrontendImageTag`, `BackendImageDigest`, `FrontendImageDigest`, `KeyPairName` e `OperatorSshCidr`. Os valores de VPC/subnet/AMI, o IP `/32` e os digests precisam ser revalidados na janela. Os valores ECR verificados acima podem ser reutilizados somente se o novo preflight passar.

Exemplo de mapeamento operacional, preenchido com valores reconsultados e sem secrets:

```powershell
$deploy = @{
  VpcId = '<VPC_DEFAULT_ATUAL>'
  SubnetId = '<SUBNET_PUBLICA_ATUAL>'
  AmiId = '<AMI_CANONICAL_ATUAL>'
  InstanceType = 't3.large'
  RootVolumeSize = 50
  InstanceProfileName = 'LabInstanceProfile'
  EcrRegistryUri = '<CONTA>.dkr.ecr.us-east-1.amazonaws.com'
  BackendImageTag = '0ef613347a33131036e975bb74b5a3b4baa56fca'
  FrontendImageTag = '0ef613347a33131036e975bb74b5a3b4baa56fca'
  BackendImageDigest = 'sha256:a36625c35ce19f2fbbba96769d474597ba9227f6ff332cca86735c86ca89ee06'
  FrontendImageDigest = 'sha256:feac52befdf953df04df75abdf1ac79b07fa6abd59f4e3b2a31169fa1d538723'
  KeyPairName = 'm7-g05-learner-lab-2026'
  OperatorSshCidr = '<IP_PUBLICO_ATUAL_DO_OPERADOR>/32'
}
.\scripts\aws\deploy.ps1 @deploy
.\scripts\aws\deploy.ps1 @deploy -Action CreateChangeSet
.\scripts\aws\deploy.ps1 -Action InspectChangeSet -ChangeSetName '<NOME_RETORNADO>'
# Somente após inspeção e autorização na janela:
.\scripts\aws\deploy.ps1 -Action ExecuteChangeSet -ChangeSetName '<NOME_RETORNADO>' -ConfirmExecution
```

1. Rode sem `-Action` para preflight **somente leitura**. Ele valida STS, Compose, template renderizado, stack, rede, AMI, profile, chave e ECR. `cloudformation:ValidateTemplate` precisa passar; `cfn-lint` roda se estiver instalado. Nesta preparação, `cfn-lint` não estava disponível, e o template renderizado passou em `ValidateTemplate`.
2. Rode novamente com `-Action CreateChangeSet` e os mesmos parâmetros. A chamada cria um change set `UPDATE`, imprime seu nome e **não o executa**.
3. Depois que estiver `CREATE_COMPLETE/AVAILABLE`, rode `-Action InspectChangeSet -ChangeSetName <NOME>`. A inspeção exige a substituição de `ApplicationInstance` por `KeyName`, atualização **sem substituição** de `ApplicationSecurityGroup`, CIDR ainda atual e nenhum outro recurso. Confira os detalhes antes de avançar. Se houver mudança inesperada, pare.
4. Somente na janela autorizada, em **nova invocação**, rode `-Action ExecuteChangeSet -ChangeSetName <NOME> -ConfirmExecution`. O script consulta novamente o change set e pede confirmação PowerShell. Acompanhe eventos da stack e obtenha o novo InstanceId e IPv4 pela EC2; outputs antigos podem estar defasados.

O change set `m7-g05-ssh-9435a35c3cb34a9e8c3459965ade114c`, criado com o template anterior, é **OBSOLETO**: ele propõe substituir também `ApplicationSecurityGroup` porque alterou `GroupDescription`. Ele não foi executado. O change set corrigido `m7-g05-ssh-d2fa39877cc7478292ca37fac513d12a` concluiu a substituição da EC2; não o execute novamente. A operação corrente de aplicação usa SSH e não requer novo change set. Não coloque secrets em parâmetros, tags, User Data, linha de comando ou logs.

## Bootstrap e acesso SSH

Após a substituição, confirme status da EC2, `sshd`, cloud-init e saída ECR. Use a chave privada fora do repositório, com ACL restrita. Na primeira conexão, obtenha o fingerprint da host key pelo console serial EC2 ou outro canal independente confiável e compare com o fingerprint exibido pelo SSH antes de aceitar e gravar em `known_hosts`. Um IPv4 reciclado pode ter chave diferente: pare e investigue em vez de desabilitar a verificação. Conexões posteriores devem usar `StrictHostKeyChecking=yes`. Exemplo de túnel no computador do operador:

```powershell
ssh -i <CAMINHO_DA_CHAVE> -o StrictHostKeyChecking=yes -N -L 8080:127.0.0.1:80 ubuntu@<IP_EC2_ATUAL>
```

Prepare `runtime.env` local em caminho protegido e fora do Git. Ele deve conter as variáveis da aplicação: `GEMINI_API_KEY`, `AZURE_SPEECH_RESOURCE` ou `AZURE_SPEECH_ENDPOINT`, `AZURE_SPEECH_KEY`, `AZURE_SPEECH_TIMEOUT_SECONDS`, `AZURE_SPEECH_MAX_ATTEMPTS`, `AUDIO_SIMULATED_IDENTITIES` e `REPORT_SIMULATED_IDENTITIES`. Nunca inclua `AWS_*`. Confirme ausência sem imprimir linhas nem valores:

```powershell
if (Select-String -LiteralPath <RUNTIME_ENV_LOCAL> -Pattern '^\s*(?:export\s+)?AWS_[A-Za-z0-9_]*\s*=' -Quiet) { throw 'Remova variáveis AWS_ do runtime.' }
```

Antes da cópia, crie por SSH um diretório temporário privado. Faça a cópia com `scp` usando a chave e host key conferida; o diretório `0700` impede a leitura durante a transferência, mesmo que o arquivo temporário nasça com modo mais amplo. Não imprima o conteúdo:

```powershell
ssh -i <CAMINHO_DA_CHAVE> -o StrictHostKeyChecking=yes ubuntu@<IP_EC2_ATUAL> 'umask 077; mkdir -m 700 -p ~/.runtime-stage; chmod 700 ~/.runtime-stage'
scp -i <CAMINHO_DA_CHAVE> -o StrictHostKeyChecking=yes <RUNTIME_ENV_LOCAL> ubuntu@<IP_EC2_ATUAL>:.runtime-stage/runtime.env.incoming
ssh -i <CAMINHO_DA_CHAVE> -o StrictHostKeyChecking=yes ubuntu@<IP_EC2_ATUAL>
```

Na EC2, execute sem inserir secrets na linha de comando. O `umask` protege cópias futuras; confira permissões e remova o temporário após a instalação:

```bash
umask 077
chmod 600 ~/.runtime-stage/runtime.env.incoming
sudo install -o root -g root -m 0600 ~/.runtime-stage/runtime.env.incoming /etc/m7/runtime.env
rm -f ~/.runtime-stage/runtime.env.incoming
rmdir ~/.runtime-stage
sudo stat -c '%U %G %a' /etc/m7/runtime.env
sudo /usr/local/bin/m7-compose-up
sudo /usr/local/bin/m7-compose ps
curl --fail --silent --output /dev/null http://127.0.0.1:80/health
```

A cópia local também precisa de ACL restrita. Se a transferência ou `install` falhar, elimine o temporário do diretório privado antes de prosseguir.

Com o túnel SSH aberto, verifique `http://localhost:8080/health`, frontend, chat e um áudio curto real. Use apenas dados sintéticos. O token simulado não é autenticação. Para diagnóstico sem expor configuração:

```bash
sudo /usr/local/bin/m7-compose ps
sudo /usr/local/bin/m7-compose logs --no-color --tail 100 backend frontend
sudo journalctl -u cloud-init --no-pager -n 100
df -h /
free -h
```

Revise logs antes de compartilhá-los. Não rode `docker compose config` com o runtime real em saída de terminal, pois ele pode revelar variáveis interpoladas.

## Quick Tunnel, rollback e encerramento

**Depois** de SSH e health check, um Quick Tunnel pode rodar na EC2 com `cloudflared tunnel --url http://127.0.0.1:80`. Instale `cloudflared` somente a partir da distribuição oficial verificada; teste conectividade TCP/UDP 7844. O URL HTTPS é temporário, muda entre execuções e exige processo ativo. Faça teste real de `/health`, frontend, chat e áudio pelo URL antes de enviá-lo ao cliente. Antes de compartilhar, aplique controle de acesso, pois `/api/chat` pode consumir cota Gemini sem `Authorization`; o URL aleatório não é controle de acesso.

`scripts/aws/rollback.ps1` faz preflight somente leitura por padrão: recebe InstanceId, tags e digests anteriores, EcrRegistryUri e PrivateKeyPath, valida EC2 e ECR. Para executar por SSH, use `-ExecuteRollback -ConfirmRollback` e confirme a operação. O wrapper remoto troca somente tags não secretas, puxa as imagens, inicia Compose e requer verificação posterior de `/health` e containers. `ssm:StartSession` e `ssm:SendCommand` não fazem parte do fluxo.

Pare os containers por SSH com `sudo /usr/local/bin/m7-compose stop` antes de parar a EC2. O EBS e ECR continuam gerando custo conforme retenção; acompanhe o saldo do Learner Lab. Após a demonstração, remova o acesso SSH e os recursos AWS em uma janela autorizada. Não use `docker compose down -v` se ainda precisar dos artefatos.
