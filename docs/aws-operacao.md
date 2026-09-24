# AWS Learner Lab — MVP temporário M7/g05

Este runbook cobre somente backend, frontend, áudio via Azure Speech, relatórios
locais e notebook PLN sob demanda. A implantação dura aproximadamente quatro
dias. Landing page, RAG da landing page, Supabase, migrations, autenticação
real, domínio, HTTPS, Load Balancer, NAT Gateway e segunda EC2 ficam fora.

## Arquitetura

- Região `us-east-1`, uma EC2 `t3.large` e EBS raiz gp3 criptografado de 50 GiB.
- `t3.xlarge` é fallback explícito somente se o pico real de memória falhar na
  `t3.large`.
- A EC2 usa subnet pública e IPv4 público somente para saída direta a SSM, ECR,
  CloudWatch Logs, Azure Speech, Gemini e repositórios de pacotes.
- O Security Group não contém regra de entrada. Não há HTTP ou SSH público.
- O frontend/Nginx é publicado somente em `127.0.0.1:80` no host. O operador
  acessa `http://localhost:8080` por túnel SSM.
- Backend porta 8000 e notebook porta 8888 permanecem privados. O notebook não
  é iniciado nem puxado pelo bootstrap.
- A stack cria apenas uma EC2, seu EBS raiz, um Security Group e um Log Group
  com retenção de sete dias. VPC, subnet, instance profile e ECR já devem existir.

Os relatórios usam execução local, repositório em memória, armazenamento local
e carteira sintética. Reiniciar o backend perde IDs e estados em memória; o
volume Docker conserva os DOCX apenas enquanto a EC2 e seu EBS existirem.

## Parâmetros da stack

| Parâmetro | Regra |
| --- | --- |
| `VpcId` | VPC default existente em `us-east-1` |
| `SubnetId` | Subnet pública da VPC, com rota `0.0.0.0/0` para Internet Gateway |
| `AmiId` | Ubuntu Server 24.04 LTS amd64 da Canonical |
| `InstanceType` | padrão `t3.large`; permite `t3.xlarge` |
| `RootVolumeSize` | padrão e mínimo 50 GiB, gp3 |
| `InstanceProfileName` | profile existente validada para SSM, pull ECR e Logs |
| `EcrRegistryUri` | registry privado da conta em `us-east-1` |
| `BackendImageTag` | SHA completo de 40 caracteres |
| `FrontendImageTag` | SHA completo de 40 caracteres |

Os nomes dos dois repositórios são fixos: `m7-g05-backend` e
`m7-g05-frontend`. A stack não cria ECR nem IAM.

## Descoberta somente leitura

Carregue as quatro variáveis AWS do arquivo protegido somente no processo atual
e confirme primeiro `aws sts get-caller-identity`. Não passe credenciais em
argumentos e não imprima seus valores.

```powershell
aws ec2 describe-vpcs --filters Name=is-default,Values=true --region us-east-1
aws ec2 describe-subnets --filters Name=vpc-id,Values=<VPC_ID> --region us-east-1
aws ec2 describe-route-tables --filters Name=vpc-id,Values=<VPC_ID> --region us-east-1

aws ssm get-parameter `
  --name /aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id `
  --query Parameter.Value --output text --region us-east-1

aws iam list-instance-profiles
aws cloudformation list-stacks --region us-east-1
aws ecr describe-repositories --region us-east-1
```

Depois de identificar uma profile candidata, confira suas roles e políticas:

```powershell
aws iam get-instance-profile --instance-profile-name <PROFILE_NAME>
aws iam list-attached-role-policies --role-name <ROLE_NAME>
aws iam list-role-policies --role-name <ROLE_NAME>
```

Ela deve permitir os canais do SSM Agent, pull de `m7-g05-backend` e
`m7-g05-frontend`, além de `logs:CreateLogStream` e `logs:PutLogEvents` no Log
Group da stack. Não use `AdministratorAccess`, credenciais AWS dentro da EC2 ou
acesso amplo a S3 e secrets.

O CIDR administrativo não é usado pelo template SSM-only. Registre o IP atual
como `/32` somente para uma eventual proposta futura de fallback SSH:

```powershell
$operatorIp = (Invoke-RestMethod https://checkip.amazonaws.com).Trim()
$adminCidr = "$operatorIp/32"
```

Não adicione esse CIDR ao Security Group sem autorização. Se Session Manager ou
o plugin local não funcionarem, a implantação permanece pendente; não abra
porta 80 ou 22 como atalho.

## Validação local e preflight

```powershell
cfn-lint infra/aws/template.yaml
docker compose -f compose.prod.yml config --quiet
```

O script renderiza o User Data, valida Compose, tenta `cfn-lint`, chama
`cloudformation:ValidateTemplate` e faz somente consultas de VPC, subnet, AMI,
IAM, ECR e stacks quando executado sem `-Provision`:

```powershell
.\\scripts\\aws\\deploy.ps1 `
  -VpcId <DEFAULT_VPC_ID> `
  -SubnetId <PUBLIC_SUBNET_ID> `
  -AmiId <UBUNTU_2404_AMD64_AMI> `
  -InstanceProfileName <EXACT_PROFILE_NAME> `
  -EcrRegistryUri <ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com `
  -BackendImageTag <40_HEX_SHA> `
  -FrontendImageTag <40_HEX_SHA>
```

Na Fase 4, `cloudformation:ValidateTemplate` retornou `AccessDenied`. Esse
estado é `AWS_TEMPLATE_VALIDATION_UNAVAILABLE`; não é um erro de sintaxe
detectado localmente. Não contorne a permissão. Provisionamento fica bloqueado
até a validação AWS funcionar.

## ECR na futura Fase 5

Somente após autorização:

1. Crie `m7-g05-backend` e `m7-g05-frontend` como repositórios privados com
   tags imutáveis.
2. Autentique o Docker local no ECR sem armazenar credenciais AWS na imagem.
3. Tagueie as duas imagens aprovadas com o SHA completo do commit.
4. Faça push e consulte `describe-images` para registrar os digests.
5. Informe as tags imutáveis ao preflight e confira os digests.
6. A EC2 fará pull pela instance profile usando o ECR credential helper.

Exemplo futuro, não executar na Fase 4:

```powershell
aws ecr create-repository --repository-name m7-g05-backend --image-tag-mutability IMMUTABLE --region us-east-1
aws ecr create-repository --repository-name m7-g05-frontend --image-tag-mutability IMMUTABLE --region us-east-1
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <REGISTRY>
docker tag m7-g05-backend:<SHA> <REGISTRY>/m7-g05-backend:<SHA>
docker tag m7-g05-frontend:<SHA> <REGISTRY>/m7-g05-frontend:<SHA>
docker push <REGISTRY>/m7-g05-backend:<SHA>
docker push <REGISTRY>/m7-g05-frontend:<SHA>
aws ecr describe-images --repository-name m7-g05-backend --image-ids imageTag=<SHA> --region us-east-1
aws ecr describe-images --repository-name m7-g05-frontend --image-ids imageTag=<SHA> --region us-east-1
```

Não publique o notebook inicialmente. Se ele for necessário, carregue sua imagem
posteriormente e inicie o profile `notebook` apenas durante o uso.

## Criação futura da infraestrutura

Após o preflight passar e existir autorização explícita para a Fase 5, o mesmo
comando aceita `-Provision -ConfirmProvisioning` e ainda pede confirmação
interativa. O script é first-create: não atualiza uma stack existente.

Após a criação, aguarde a instância aparecer `Online`:

```powershell
aws ssm describe-instance-information `
  --filters Key=InstanceIds,Values=<INSTANCE_ID> `
  --region us-east-1
```

Se ela não ficar online, confira a instance profile, saída TCP 443, SSM Agent e
disponibilidade do serviço no Learner Lab. Não habilite SSH automaticamente.

## Secrets e inicialização

O User Data cria `/etc/m7/runtime.env` vazio, pertencente a root e modo `0600`.
Abra uma sessão interativa SSM com gravação da sessão desabilitada para entrada
de secrets. Edite o arquivo como root; não coloque valores na linha de comando,
histórico, template, User Data, Dockerfile, imagem ou logs.

Inclua:

- `GEMINI_API_KEY`;
- `AZURE_SPEECH_RESOURCE`;
- `AZURE_SPEECH_ENDPOINT`;
- `AZURE_SPEECH_KEY`;
- `AZURE_SPEECH_TIMEOUT_SECONDS`;
- `AZURE_SPEECH_MAX_ATTEMPTS`;
- `AUDIO_SIMULATED_IDENTITIES`, no formato `token=entra_object_id`;
- `REPORT_SIMULATED_IDENTITIES`, no formato JSON aceito pelo backend.

`AZURE_SPEECH_RESOURCE` ou `AZURE_SPEECH_ENDPOINT` precisa estar preenchido.
Após salvar, valide apenas metadados e inicie:

```bash
sudo stat -c '%U %G %a' /etc/m7/runtime.env
sudo /usr/local/bin/m7-compose-up
sudo /usr/local/bin/m7-compose ps
```

As credenciais temporárias AWS nunca entram nesse arquivo. A aplicação usa:

```text
REPORT_EXECUTION_MODE=local
REPORT_REPOSITORY_MODE=memory
REPORT_STORAGE_MODE=local
REPORT_PORTFOLIO_SOURCE=synthetic
```

## Acesso e testes durante os quatro dias

Instale o Session Manager plugin na máquina do operador e mantenha este comando
aberto:

```powershell
aws ssm start-session `
  --target <INSTANCE_ID> `
  --document-name AWS-StartPortForwardingSession `
  --parameters '{"portNumber":["80"],"localPortNumber":["8080"]}' `
  --region us-east-1
```

Acesse `http://localhost:8080` e teste:

```powershell
Invoke-RestMethod http://localhost:8080/health
```

Para áudio, use o frontend, informe o token de demonstração no campo de sessão
já existente e envie um único áudio curto válido. Confirme transcrição não vazia
e resposta do chat. O token simulado não é autenticação real. Use somente dados
sintéticos e nenhum dado pessoal, financeiro ou sensível.

Para acompanhar sem revelar variáveis:

```bash
sudo /usr/local/bin/m7-compose ps
sudo /usr/local/bin/m7-compose logs --no-color --tail 100 backend frontend
df -h /
free -h
```

Os logs têm rotação local de 10 MiB por arquivo, três cópias, e envio mínimo ao
Log Group com retenção de sete dias. Não habilite debug com headers, bodies,
áudio, tokens, prompts ou relatórios.

## Notebook sob demanda

O notebook não tem imagem no ECR inicial e não sobe no Compose padrão. Após
carregar uma imagem aprovada na EC2 e definir `JUPYTER_TOKEN` no runtime:

```bash
sudo /usr/local/bin/m7-compose --profile notebook up -d notebook
```

Abra outro túnel SSM de `localhost:8888` para a porta 8888 e desligue ao terminar:

```bash
sudo /usr/local/bin/m7-compose --profile notebook stop notebook
```

Se backend e notebook excederem a memória da `t3.large`, pare o notebook. Use
`t3.xlarge` somente após confirmar o problema de memória.

## Pausa diária e rollback

Pare containers antes de parar a EC2:

```bash
sudo /usr/local/bin/m7-compose stop
```

Depois, fora da sessão, pare a instância:

```powershell
aws ec2 stop-instances --instance-ids <INSTANCE_ID> --region us-east-1
aws ec2 wait instance-stopped --instance-ids <INSTANCE_ID> --region us-east-1
```

Parar a EC2 preserva o EBS e os artefatos, mas o EBS continua sendo cobrado.
O repositório de relatórios em memória não sobrevive ao reinício do backend.

O rollback possui preflight read-only por padrão:

```powershell
.\\scripts\\aws\\rollback.ps1 `
  -InstanceId <INSTANCE_ID> `
  -PreviousBackendImageTag <40_HEX_SHA> `
  -PreviousFrontendImageTag <40_HEX_SHA> `
  -EcrRegistryUri <REGISTRY>
```

A execução remota futura exige também `-ExecuteRollback -ConfirmRollback`.

## Encerramento após a demonstração

Faça backup apenas dos artefatos sintéticos que precisam ser preservados. Depois,
com autorização explícita:

1. Pare os containers e a EC2.
2. Execute `aws cloudformation delete-stack --stack-name m7-g05-mvp`.
3. Aguarde `aws cloudformation wait stack-delete-complete`.
4. Confirme que EC2, EBS raiz, Security Group e Log Group foram removidos.
5. Exclua imagens e os dois repositórios ECR somente quando não houver rollback.
6. Se a EC2 for mantida fora da stack, remova volumes Docker somente depois de
   confirmar que os DOCX e notebooks podem ser descartados.

O EBS raiz usa `DeleteOnTermination: true`. Excluir a stack remove junto os
volumes Docker armazenados nele. Não use `docker compose down -v` durante a
demonstração.

## Estimativa para quatro dias

Estimativa On-Demand em `us-east-1`, 96 horas:

| Item | `t3.large` | `t3.xlarge` |
| --- | ---: | ---: |
| EC2 | US$ 8,02 | US$ 16,03 |
| IPv4 público | US$ 0,48 | US$ 0,48 |
| gp3 50 GiB, proporcional a quatro dias | US$ 0,53 | US$ 0,53 |
| Total básico | **US$ 9,03** | **US$ 17,05** |

Acrescente ECR, aproximadamente US$ 0,10 por GB-mês armazenado, e poucos
centavos de CloudWatch Logs no volume esperado do MVP. Tráfego, APIs externas,
snapshots, impostos e créditos excedentes T3 podem elevar o custo. Confirme o
saldo no painel do Learner Lab; a API padrão não confirma os créditos. Pare a
EC2 fora das janelas de demonstração para reduzir computação e IPv4.
