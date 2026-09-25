# Handoff do deploy AWS Learner Lab — M7/g05

Data do registro: 24/09/2026  
Repositório: `M7/g05`  
Branch local: `chore/deploy-ec2`

## 1. Objetivo deste documento

Este documento consolida o que foi implementado e executado durante a tentativa
de deploy do MVP na AWS Academy Learner Lab, o estado conhecido dos recursos,
as falhas encontradas e as restrições que precisam orientar um novo plano.

Ele não contém valores de credenciais, tokens, chaves de APIs ou conteúdo do
arquivo `.env`.

## 2. Resumo executivo

O backend e o frontend foram dockerizados, publicados em dois repositórios ECR
e inicializados em uma instância EC2. No último estado reportado, os dois
containers estavam `Up (healthy)`, o Docker estava ativo, o CloudWatch Agent
estava ativo e o arquivo `/etc/m7/runtime.env` havia sido criado com
`root:root` e modo `0600`.

O deploy, entretanto, não ficou utilizável para demonstração externa. A
arquitetura adotada dependia de AWS Systems Manager para acesso e operação
pós-bootstrap, mas a política gerenciada pelo Learner Lab chamada
`voc-cancel-cred` passou a retornar `explicit deny` para ações essenciais do
operador, incluindo `ssm:StartSession` e `ssm:SendCommand`.

O frontend foi publicado no host apenas em `127.0.0.1:80`. Sem Session Manager
e sem a possibilidade de executar um comando remoto para alterar o bind para
`0.0.0.0`, a aplicação permaneceu inacessível pelo navegador, mesmo após a
abertura manual de uma regra temporária de entrada TCP/80.

Portanto, o estado final é:

- infraestrutura criada;
- imagens publicadas;
- bootstrap concluído;
- containers saudáveis internamente;
- acesso externo, health check pelo cliente e smoke test de áudio na AWS não
  concluídos;
- instância possivelmente ainda ligada e gerando custo;
- regra temporária TCP/80 possivelmente ainda presente no Security Group;
- dois commits de correção ainda não enviados ao GitLab.

## 3. Escopo definido para o MVP

O escopo foi reduzido deliberadamente para uma implantação temporária de cerca
de quatro dias:

- uma EC2 `t3.large` em `us-east-1`;
- volume raiz EBS gp3 de 50 GiB, criptografado;
- backend e frontend executados com Docker Compose;
- duas imagens privadas no ECR;
- notebook PLN fora do deploy inicial e desligado por padrão;
- relatórios em modo local, memória e dados sintéticos;
- sem Supabase no runtime inicial;
- sem RDS, NAT Gateway, Load Balancer, domínio ou HTTPS;
- landing page fora desse deploy, prevista para Vercel;
- acesso inicialmente planejado apenas por túnel do Session Manager;
- duração curta e desligamento da EC2 fora das janelas de demonstração.

## 4. Arquitetura e artefatos implementados

### 4.1 Docker

Foram criados e validados:

- `.dockerignore` para excluir credenciais e arquivos locais do build context;
- `compose.prod.yml`;
- Dockerfile multi-stage do backend;
- entrypoint do backend com validação das variáveis obrigatórias;
- Dockerfile do frontend;
- configuração Nginx com proxy para backend e rota `/health`;
- Dockerfile e configuração do notebook, em profile opcional;
- scripts PowerShell de build e inicialização local;
- documentação operacional de Docker.

O Compose publica o frontend por meio da expressão:

```yaml
${APP_BIND_ADDRESS:-127.0.0.1}:${APP_PORT:-80}:8080
```

No bootstrap da EC2, `APP_BIND_ADDRESS` foi definido como `127.0.0.1`. Essa
decisão pressupunha que o acesso seria sempre feito por túnel SSM.

### 4.2 AWS e observabilidade

Foram criados:

- `infra/aws/template.yaml`;
- `infra/aws/user-data.sh`;
- `infra/aws/cloudwatch-agent.json`;
- `scripts/aws/common.ps1`;
- `scripts/aws/deploy.ps1`;
- `scripts/aws/rollback.ps1`;
- `docs/aws-operacao.md`;
- `docs/stories/phase-4-aws-mvp.md`.

O template cria uma EC2, seu Security Group, volume raiz e Log Group. VPC,
subnet, instance profile e ECR são externos à stack.

O bootstrap instala Docker CE, Docker Compose, ECR credential helper, SSM
Agent e CloudWatch Agent; baixa as imagens; cria wrappers operacionais; prepara
`/etc/m7/runtime.env`; configura logs; e deixa a aplicação pronta para ser
iniciada após a injeção da configuração de runtime.

### 4.3 Configuração de runtime

Foram validados os seguintes requisitos de runtime, sem registrar seus valores:

- `GEMINI_API_KEY`;
- `AZURE_SPEECH_RESOURCE` ou `AZURE_SPEECH_ENDPOINT`;
- `AZURE_SPEECH_KEY`;
- `AZURE_SPEECH_TIMEOUT_SECONDS`;
- `AZURE_SPEECH_MAX_ATTEMPTS`;
- `AUDIO_SIMULATED_IDENTITIES`;
- `REPORT_SIMULATED_IDENTITIES`.

`REPORT_SIMULATED_IDENTITIES` usa um objeto JSON indexado pelo Bearer token e
contém, no mínimo, `subject` e `role`. Para o cenário demonstrativo também foram
usados `display_name`, `can_export` e `allow_all`.

O handoff de secrets acabou sendo realizado por um `SecureString` temporário.
Segundo o último relatório, o parâmetro e o arquivo temporário local foram
removidos após a injeção, e o arquivo remoto ficou com `root:root` e modo
`0600`.

## 5. Validações locais concluídas

Durante as fases locais, foram reportados como aprovados:

- recuperação e funcionamento do Docker Engine local;
- build das imagens de backend e frontend;
- `docker compose config`;
- inicialização local do Compose;
- endpoint `/health` local;
- carregamento local do frontend;
- restart dos containers;
- inspeção de logs e imagens;
- suíte de testes utilizada na fase de Dockerização;
- um smoke test local real de áudio com Azure;
- sintaxe PowerShell dos scripts de AWS;
- sintaxe do User Data;
- JSON do CloudWatch Agent;
- parâmetros do template CloudFormation;
- busca por valores sensíveis nos arquivos versionáveis.

O Session Manager Plugin foi instalado no Windows e validado na versão
`1.2.835.0`, no caminho padrão:

```text
C:\Program Files\Amazon\SessionManagerPlugin\bin\session-manager-plugin.exe
```

## 6. Recursos AWS criados e estado conhecido

### 6.1 Parâmetros utilizados

| Item | Valor conhecido |
| --- | --- |
| Região | `us-east-1` |
| VPC default | `vpc-071dbf8c393325483` |
| Subnet selecionada | `subnet-0a4ab0f965bbfa086` |
| Availability Zone | `us-east-1a` |
| AMI Ubuntu 24.04 amd64 | `ami-0045d7fc2ad003464` |
| Instance profile | `LabInstanceProfile` |
| Tipo | `t3.large` |
| EBS raiz | gp3, 50 GiB, criptografado |
| Stack | `m7-g05-mvp` |
| EC2 atual reportada | `i-0ee46033b616aeedc` |
| IPv4 público reportado pelo usuário | `32.192.181.192` |
| IP público do operador detectado | `177.92.77.170` |

Os endereços IPv4 são temporários e precisam ser novamente confirmados antes
de qualquer uso. O IPv4 da EC2 não deve ser confundido com o CIDR de origem do
operador.

### 6.2 ECR

Foram criados dois repositórios privados com tags imutáveis:

- `m7-g05-backend`;
- `m7-g05-frontend`.

O notebook não foi publicado.

As imagens do deploy associado ao commit `955bbc8e4d051331b7a52136399aa1afb8f3e118`
tiveram os seguintes digests registrados:

- backend: `sha256:26edd4806f3d34427a9d0ef1d6616f45810f6963088440e966e1510150fe0ee8`;
- frontend: `sha256:3502656026bd050d9e74d4057ca60a61343659f099ed2c8de10c5fae7142a958`.

Depois disso houve um novo commit, `0ef613347a33131036e975bb74b5a3b4baa56fca`,
e foi reportado que as imagens corretas desse HEAD foram baixadas pela EC2. Os
digests finais dessa tag não foram incluídos nos relatórios disponíveis e devem
ser consultados no ECR antes de qualquer novo deploy.

### 6.3 Estado operacional final reportado

- stack `m7-g05-mvp`: `CREATE_COMPLETE`;
- EC2: `running` e registrada como `Online` no SSM;
- cloud-init: concluído sem erros;
- Docker daemon: ativo;
- Docker Compose: `v5.5.1`;
- CloudWatch Agent: ativo;
- wrappers `m7-compose` e `m7-compose-up`: presentes;
- backend: `Up (healthy)`;
- frontend: `Up (healthy)`;
- `/etc/m7/runtime.env`: `root:root`, modo `0600`;
- health check externo: não executado;
- frontend no navegador: não validado;
- smoke test de áudio na AWS: não executado.

Esse estado é proveniente dos relatórios da execução. As políticas IAM passaram
a impedir consultas suficientes para reconfirmá-lo integralmente pela CLI.

## 7. Histórico de commits

O repositório local estava limpo no momento deste handoff. A branch
`chore/deploy-ec2` estava dois commits à frente de
`origin/chore/deploy-ec2`.

| Commit | Descrição | Situação em relação ao GitLab |
| --- | --- | --- |
| `4a3028c153cee730dae758ea808ba52d37922e77` | `chore: configura ambiente Docker e AWS temporário do MVP (#221)` | presente no remoto da branch |
| `dd837069700886816bd4886ca5e70f4799b39f41` | `feat: prepara publicação manual do backend (#222)` | presente no remoto da branch |
| `7f7cb9d7341a04f045e02542ca454c1978fd92cf` | `feat: prepara frontend com proxy para backend (#223)` | presente no remoto da branch |
| `0cf0bd0df4ad0a7033394f9be98ee5f5a6d64650` | `chore: prepara rollback manual do MVP (#224)` | presente no remoto da branch |
| `955bbc8e4d051331b7a52136399aa1afb8f3e118` | `fix: remove awscli from EC2 bootstrap` | somente local |
| `0ef613347a33131036e975bb74b5a3b4baa56fca` | `fix(infra): corrige bootstrap do Docker e CloudWatch` | somente local |

Nenhum push dos dois últimos commits foi realizado.

## 8. Falhas encontradas durante o bootstrap

### 8.1 `awscli` indisponível no APT

O primeiro bootstrap falhou com:

```text
E: Package 'awscli' has no installation candidate
```

Como o User Data usa `set -e`, a execução foi encerrada antes da instalação do
Docker e da preparação do runtime. O pacote foi removido do bootstrap porque o
ECR credential helper usa a role da instância e não depende do AWS CLI.

Correção versionada no commit `955bbc8e4d051331b7a52136399aa1afb8f3e118`.

### 8.2 Conflito entre `amazon-ecr-credential-helper` e Docker CE

O segundo bootstrap instalou `amazon-ecr-credential-helper` antes de adicionar
o repositório do Docker CE. O APT instalou `docker.io`, `containerd` e `runc`
como dependências. A instalação posterior do Docker CE removeu/substituiu esses
pacotes e deixou a ativação por socket inconsistente.

Erro observado:

```text
failed to load listeners: no sockets found via socket activation
```

A correção moveu `amazon-ecr-credential-helper` para a mesma transação que
instala Docker CE, CLI, containerd e plugins.

### 8.3 URL incorreta do CloudWatch Agent

O bucket foi inicialmente escrito como:

```text
amazon-cloudwatch-agent-$AWS_REGION
```

O nome correto é:

```text
amazoncloudwatch-agent-$AWS_REGION
```

O nome incorreto retornou HTTP 404 e interrompeu o User Data por causa de
`set -e`.

As correções 8.2 e 8.3 foram versionadas no commit
`0ef613347a33131036e975bb74b5a3b4baa56fca`.

## 9. Principal restrição: política IAM do Learner Lab

A política `voc-cancel-cred` retornou negação explícita para operações
necessárias ao fluxo. Foram observados bloqueios para:

- `ssm:StartSession`;
- `ssm:SendCommand`;
- `ec2:DescribeInstances` em uma etapa posterior;
- `cloudformation:DescribeStackResources` em uma etapa posterior.

Um `explicit deny` não pode ser superado por outra política `Allow` anexada à
mesma identidade. A correção depende de uma identidade diferente ou de alteração
da política por quem administra o Learner Lab.

Também é importante separar dois conjuntos de permissões:

1. **Role da EC2:** permissões usadas pela máquina para registrar o SSM Agent,
   baixar imagens do ECR, enviar logs e eventualmente ler parâmetros.
2. **Identidade temporária do aluno:** permissões usadas no computador local
   para iniciar uma sessão, enviar comandos, consultar a EC2, operar a stack e
   editar Security Groups.

O preflight validou por simulação as permissões da role da EC2. Isso não provou
que a identidade temporária do aluno podia usar `StartSession` ou `SendCommand`.
Essa diferença só ficou evidente depois do provisionamento.

## 10. Por que o acesso público improvisado não resolveu

Depois da negação do túnel SSM, foi considerada uma regra temporária TCP/80
restrita ao IP do operador. Entretanto:

- o frontend continuava publicado somente em `127.0.0.1:80` no host;
- seria necessário alterar `/etc/m7/deploy.env` para
  `APP_BIND_ADDRESS=0.0.0.0` e recriar o container;
- `ssm:SendCommand` foi negado explicitamente antes dessa alteração;
- as APIs necessárias para identificar e inspecionar o Security Group também
  foram negadas em uma etapa posterior;
- a regra TCP/80 adicionada manualmente não torna um processo ligado ao
  loopback acessível externamente.

Segundo o último relato, uma regra TCP/80 restrita ao IP
`177.92.77.170/32` foi adicionada manualmente e permaneceu no Security Group.
Isso não pôde ser confirmado pela CLI. Ela deve ser revisada ou removida pelo
console da AWS.

## 11. O que não foi concluído

- acesso ao frontend hospedado na EC2;
- health check HTTP a partir da máquina do operador;
- smoke test real de áudio no ambiente AWS;
- validação de latência e logs durante uma requisição real;
- teste efetivo de rollback remoto;
- desligamento ou exclusão confirmada dos recursos finais;
- confirmação do gasto real no Learner Lab;
- push dos dois commits de correção de bootstrap.

## 12. Erros de planejamento que não devem ser repetidos

1. A arquitetura SSM-only foi escolhida antes de testar as permissões efetivas
   de `ssm:StartSession` e `ssm:SendCommand` da identidade do aluno.
2. `PingStatus=Online` foi tratado como evidência de que Session Manager e Run
   Command estavam autorizados. Ele confirma apenas que o agente está
   registrado e comunicando com o serviço.
3. A simulação da instance profile foi usada como evidência insuficiente para
   ações que seriam executadas pela identidade local.
4. O caminho de acesso externo não tinha um fallback validado antes da criação
   da stack.
5. O User Data não havia sido testado integralmente em Ubuntu 24.04 limpo antes
   das primeiras recriações.
6. O deploy dependia de ações pós-bootstrap para secrets e bind de rede; essas
   ações ficaram impossíveis quando o controle remoto foi negado.
7. A abertura de TCP/80 foi considerada tarde demais, quando a aplicação já
   estava ligada exclusivamente ao loopback.
8. Houve sucessivas recriações da stack antes de estabilizar todos os pacotes e
   URLs do bootstrap.

## 13. Requisitos mínimos para um novo planejamento

Antes de criar qualquer novo recurso, o próximo agente deve produzir uma matriz
de permissões reais da identidade temporária, executando chamadas inofensivas ou
simulações equivalentes para, no mínimo:

- `ec2:DescribeInstances`;
- `ec2:DescribeSecurityGroups`;
- `ec2:AuthorizeSecurityGroupIngress` e revogação, se o desenho usar acesso
  público;
- `cloudformation:DescribeStacks`;
- `cloudformation:DescribeStackResources`;
- `ssm:StartSession`;
- `ssm:SendCommand`;
- `ssm:GetCommandInvocation`;
- operações ECR necessárias para publicação;
- operações necessárias para parar e excluir os recursos.

Se `StartSession` e `SendCommand` continuarem negados, o novo desenho não pode
depender de SSM para nenhuma etapa obrigatória. Nesse cenário, o acesso e a
configuração completa devem estar resolvidos no provisionamento inicial.

Possibilidades a avaliar, somente depois do preflight:

- EC2 pública com frontend ligado a `0.0.0.0`, Security Group restrito ao IP do
  operador e procedimento de remoção da regra;
- outro ambiente AWS/conta que permita as ações necessárias;
- outra plataforma de hospedagem compatível com Docker;
- execução local para demonstração e uso da AWS apenas como evidência de
  infraestrutura, caso as limitações acadêmicas impeçam acesso remoto.

Não incluir secrets em User Data, template, repositório ou histórico de
comandos apenas para contornar a política do laboratório.

## 14. Checklist imediato antes de abandonar ou retomar o ambiente

Como o estado atual não pode ser confirmado integralmente pela CLI, conferir no
console da AWS:

- se `i-0ee46033b616aeedc` continua ligada;
- se a stack `m7-g05-mvp` continua `CREATE_COMPLETE`;
- se existe regra temporária TCP/80 no Security Group;
- o IPv4 público atual da EC2;
- se o Log Group continua recebendo dados;
- se há cobranças acumulando.

Se o trabalho não for retomado imediatamente:

1. remover as regras temporárias de entrada;
2. parar a EC2 para reduzir custo de computação e IPv4;
3. lembrar que EBS e ECR continuam gerando custo enquanto existirem;
4. não excluir a stack antes de decidir se os artefatos locais da instância
   precisam ser preservados;
5. registrar os digests finais das imagens antes de qualquer limpeza do ECR.

## 15. Estimativa de custo usada no planejamento

A estimativa documentada para 96 horas em `us-east-1` foi aproximadamente:

- EC2 `t3.large`: US$ 8,02;
- IPv4 público: US$ 0,48;
- EBS gp3 de 50 GiB proporcional: US$ 0,53;
- total básico estimado: US$ 9,03;
- além de ECR, CloudWatch, tráfego e APIs externas.

O saldo informado do Learner Lab era de aproximadamente US$ 43. A API usada
durante o trabalho não confirmou o saldo nem o gasto real.

## 16. Arquivos principais para a próxima análise

- `compose.prod.yml`;
- `infra/aws/template.yaml`;
- `infra/aws/user-data.sh`;
- `infra/aws/cloudwatch-agent.json`;
- `scripts/aws/common.ps1`;
- `scripts/aws/deploy.ps1`;
- `scripts/aws/rollback.ps1`;
- `docs/aws-operacao.md`;
- `docs/docker-operacao.md`;
- `docs/stories/phase-4-aws-mvp.md`;
- `src/backend/Dockerfile`;
- `src/backend/docker-entrypoint.py`;
- `src/frontend/Dockerfile`;
- `src/frontend/nginx.conf`.

## 17. Conclusão para o próximo agente

O código e as imagens chegaram a um estado operacional interno na EC2. O ponto
de falha final não foi o Docker nem a aplicação: foi a incompatibilidade entre
uma arquitetura dependente de SSM e as permissões efetivas da identidade do
Learner Lab.

O novo planejamento deve começar pela matriz de permissões do operador, não
pelo template. Só depois disso deve escolher o método de acesso, de injeção de
configuração e de rollback. Nenhuma nova stack deve ser criada enquanto o
caminho de acesso da demonstração não tiver sido validado de ponta a ponta.
