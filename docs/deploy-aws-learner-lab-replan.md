# Replanejamento do deploy no AWS Learner Lab — M7/g05

Data: 24/09/2026. Base: [handoff do deploy](deploy-aws-learner-lab-handoff.md).

## Decisão proposta

Para uma demonstração operada em um único computador, usar **uma EC2 pública com
SSH por chave e túnel local**. Reaproveitar as duas imagens no ECR e o Compose
existentes. Publicar o frontend somente em `127.0.0.1:80` na EC2 e abrir a
aplicação em `http://localhost:8080` no computador do operador por um túnel SSH.
O backend continua acessível somente pelo Nginx e pela rede interna do Compose.
O frontend usa `getUserMedia` para gravar áudio; `localhost` é tratado pelo
navegador como contexto seguro, enquanto HTTP em um IP público não é.

```text
navegador do operador → localhost:8080 → túnel SSH (TCP/22)
                    → EC2:127.0.0.1:80 → Nginx → backend:8000
```

O caminho operacional deixa de depender de `ssm:StartSession` e
`ssm:SendCommand`, ambos negados no último relato. O SSH transporta também a
configuração de runtime e os comandos de diagnóstico, atualização e rollback.
O Security Group precisa permitir TCP/22 **apenas do IP público atual do
operador `/32`**. Não é necessário abrir TCP/80. A instância precisa ter IPv4
público, rota pelo Internet Gateway, `sshd` ativo e uma chave pública autorizada.

Essa escolha atende uma demo conduzida no computador do operador ou por
compartilhamento de tela. Outros integrantes também podem abrir o próprio
túnel SSH, cada um com chave e regra TCP/22 `/32` individual. Se o objetivo for
compartilhar um link sem configurar SSH em cada computador, um **Quick Tunnel
Cloudflare** pode fornecer um URL HTTPS temporário para o frontend ainda ligado
em `127.0.0.1`; o processo `cloudflared` pode rodar na EC2 após o acesso inicial
ou no computador do operador, apontando para o túnel SSH local. Isso não exige
abrir TCP/80 ou TCP/443 na EC2. O URL muda a cada execução e o processo precisa
ficar ativo. É um recurso de desenvolvimento sem garantia de disponibilidade.

Antes de compartilhar esse URL, adicionar um controle de acesso simples na
frente da aplicação ou usar um túnel com política de acesso. O endpoint
`/api/chat` atual aceita requisições sem `Authorization` quando a proatividade
está desativada e pode consumir a cota Gemini. A URL aleatória, sozinha, não é
uma barreira de acesso. Abrir HTTP pelo IP público também impediria a captura
de microfone no navegador, pois `getUserMedia` exige contexto seguro.

## O que reaproveitar e o que mudar

| Área | Ação |
| --- | --- |
| `compose.prod.yml` | Manter o bind padrão `127.0.0.1:80` e o backend privado. |
| ECR | Reaproveitar `m7-g05-backend` e `m7-g05-frontend`; conferir tags e digests reais antes do lançamento. |
| EC2 | Manter uma instância e o EBS criptografado; adicionar uma chave SSH existente à instância nova. |
| Security Group | Declarar TCP/22 com CIDR `/32` do operador no template. Remover a regra temporária TCP/80 do grupo antigo. |
| User Data | Manter bootstrap sem secrets; retirar instruções que pressupõem SSM como único acesso. O serviço inicia após envio do runtime pelo SSH. |
| CloudWatch | Pode ser mantido inicialmente porque já funcionou; simplificar só depois do acesso externo e do smoke test. |
| `deploy.ps1` e runbook | Trocar preflight SSM por validação da chave, CIDR, alcance TCP/22 e capacidade de criação, inspeção e remoção da stack. |
| `rollback.ps1` | Substituir execução remota por SSM por comando via SSH, ou documentar rollback SSH manual para este MVP. |

Adicionar `KeyName` a `AWS::EC2::Instance` exige **substituição da EC2** pelo
CloudFormation. Portanto, não contar com uma atualização sem interrupção da
instância atual. Uma nova stack/nova instância com a configuração corrigida é
mais previsível, desde que o saldo e as permissões permitam. Não excluir a
instância antiga até registrar o que precisa ser preservado.

## Gates antes de criar ou substituir recursos

1. **Estado e custo atuais.** No console do Learner Lab, confirmar estado da
   instância `i-0ee46033b616aeedc`, stack `m7-g05-mvp`, regra TCP/80,
   cobranças e digests das imagens. Desligar a instância fora da janela de
   trabalho e remover a regra temporária se ela ainda existir.
2. **Identidade do operador.** Renovar as credenciais temporárias do laboratório
   e confirmar `sts:GetCallerIdentity`. A identidade deve conseguir consultar
   instância, Security Group, key pair, stack e imagens ECR; criar/atualizar e
   excluir a stack; iniciar/parar a instância. Registrar `allowed`, `denied` ou
   `não testado` para cada operação. Uma simulação IAM não substitui uma chamada
   real feita pela identidade do aluno.
3. **Acesso SSH.** Confirmar uma key pair utilizável em `us-east-1` e a posse
   da chave privada correspondente. Se nenhuma existir, verificar a permissão
   de importar uma chave pública gerada localmente. Nunca colocar a chave
   privada no User Data, template, repositório ou instância. Validar o IP
   público atual do operador e a possibilidade de declarar TCP/22 `/32` no
   Security Group.
4. **Caminho de saída.** Confirmar AMI, subnet pública e route table, profile
   para pull ECR e CloudWatch, disponibilidade das imagens e capacidade da
   `t3.large`. O runtime continua precisando de HTTPS de saída para Azure
   Speech e Gemini. Se `cloudflared` rodar na EC2, o Security Group atual,
   que só permite saída TCP/80 e TCP/443, precisa também permitir saída
   TCP/7844 ou UDP/7844 para o túnel. A conectividade real deve ser testada
   na instância; sem essa saída, o link Cloudflare não funcionará.
5. **Critério de corte.** Se CloudFormation/EC2, key pair ou TCP/22 forem
   negados e não houver um caminho de acesso testável, parar. Usar uma conta
   AWS com permissões apropriadas, outra hospedagem, ou demo local. Não tentar
   contornar um `explicit deny` IAM.

### Verificação com a sessão AWS de 24/09/2026

O CLI não está no PATH, mas foi encontrado em
`C:\Program Files\Amazon\AWSCLIV2\aws.exe`. As credenciais temporárias foram
lidas de `src/backend/.env` pelo helper existente, sem imprimir valores. Foram
feitas apenas consultas e chamadas EC2 com `--dry-run`; nenhum recurso foi
alterado.

| Verificação | Resultado |
| --- | --- |
| `sts:GetCallerIdentity` | Sessão válida em `us-east-1`. |
| EC2 `i-0ee46033b616aeedc` | `running`, `t3.large`, IP público atual `18.208.209.142`, sem `KeyName`. |
| Security Group `sg-04006f6ca293dc55e` | Sem regras de entrada; saída somente TCP/80 e TCP/443. A antiga regra TCP/80 de entrada não aparece mais. |
| Stack `m7-g05-mvp` | `CREATE_COMPLETE`; três recursos descritos. |
| ECR | Repositórios backend e frontend presentes, tags imutáveis e imagens com tag `0ef613347a33131036e975bb74b5a3b4baa56fca`. |
| Key pairs | `spotlight-ec2-key` e `vockey` existem. Foi gerada e importada uma nova chave ED25519 `m7-g05-learner-lab-2026`; a chave privada está somente na pasta `.ssh` local e a chave pública registrada na AWS foi comparada com a local. |
| `cloudformation:ValidateTemplate` | Autorizado nesta sessão. |
| `ec2:AuthorizeSecurityGroupIngress` para TCP/22 | Autorizado em `--dry-run`. |
| `ec2:AuthorizeSecurityGroupEgress` para TCP/7844 | Autorizado em `--dry-run`. |
| `ec2:StopInstances` | Autorizado em `--dry-run`. |

O IP do operador, saldo e autorização para atualizar/substituir a stack ainda
não foram confirmados. Os `--dry-run` provam somente as ações EC2 testadas.
Mesmo com uma key pair existente na conta, a instância atual não foi lançada
com uma delas; adicioná-la pelo template substitui a instância. Nenhum secret
deve ser copiado para este documento.

A nova key pair já está pronta para a instância substituta. A criação da key
pair **não** alterou a EC2 atual. O arquivo privado local tem ACL restrita ao
usuário, Administradores e SYSTEM; não deve ser copiado para o repositório nem
compartilhado com integrantes do grupo.

O HEAD local agora é `bae2e9b27b70c6253fb2411bf0459d18a9f58531`, com a
mesma árvore de arquivos de `0ef613347a33131036e975bb74b5a3b4baa56fca`.
Porém, `deploy.ps1` exige tags ECR idênticas ao SHA do HEAD. A tag antiga não
passará nesse gate; a implementação precisa alinhar as tags e o script antes
do próximo provisionamento.

## Sequência de execução proposta

1. Concluir os gates e preparar a alteração mínima do template e do runbook.
   Validar a renderização do User Data, `docker compose config` e o template
   antes da criação. Registrar o SHA e os digests das imagens escolhidas.
2. Criar a instância com key pair e regra TCP/22 `/32` já declaradas. Não colocar
   secrets em parâmetros CloudFormation, User Data, tags ou logs.
3. Testar imediatamente `ssh ubuntu@<IP_ATUAL>` e o túnel:

   ```text
   ssh -N -L 8080:127.0.0.1:80 ubuntu@<IP_ATUAL>
   ```

   Se o SSH falhar, diagnosticar Security Group, subnet, IP, chave, `sshd` e
   cloud-init antes de qualquer novo deploy da aplicação.
4. Enviar `runtime.env` do computador do operador por SCP/SFTP, instalar na
   EC2 como `/etc/m7/runtime.env` com `root:root` e modo `0600`, apagar a cópia
   temporária e executar `sudo m7-compose-up`. Manter o arquivo local protegido
   e fora do Git. Não imprimir valores, passá-los em argumentos ou registrá-los
   no histórico do shell.
5. Com o túnel aberto, validar `http://localhost:8080/health`, frontend,
   requisição de chat, um áudio curto real e logs sem dados sensíveis. Confirmar
   status `healthy` dos dois containers e custo no painel do Learner Lab.
6. Para atualizar ou reverter: publicar tags imutáveis, conectar via SSH,
   alterar as duas tags em `/etc/m7/deploy.env`, fazer `pull` e executar
   `m7-compose-up`; verificar saúde pelo túnel. Guardar os digests anteriores.
7. Após a demo, remover a regra SSH, parar/excluir os recursos conforme a
   necessidade de preservar artefatos. Confirmar remoção de EC2, EBS, grupo de
   segurança e Log Group. ECR é externo à stack e requer limpeza separada.

## Condições para considerar o deploy concluído

- Permissões e acesso SSH comprovados com a identidade e a rede reais.
- Frontend acessível no navegador do operador pelo túnel, sem TCP/80 público.
- `/health`, chat e áudio funcionam a partir do navegador do operador.
- Rollback por SSH testado com uma tag anterior ou, no mínimo, ensaiado em uma
  janela de teste antes da demonstração.
- Estado e custo final dos recursos confirmados no Learner Lab.

## Fontes AWS usadas para validar o desenho

- [IAM: negação explícita prevalece sobre permissões Allow](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html).
- [CloudFormation: `KeyName` e substituição da EC2](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-ec2-instance.html).
- [EC2: restringir SSH ao IP necessário](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/changing-security-group.html).
- [EC2: não armazenar secrets em User Data](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html).
- [MDN: `getUserMedia` exige contexto seguro e aceita `localhost`](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia).
- [Cloudflare: Quick Tunnels, URL temporária e limites](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/).
- [Cloudflare: túnel usa conexões de saída, sem portas de entrada](https://developers.cloudflare.com/tunnel/).
- [Cloudflare: saída TCP/UDP 7844 exigida pelo túnel](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/tunnel-with-firewall/).
