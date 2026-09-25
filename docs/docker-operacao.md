# Docker — aplicação principal M7/g05

Este ambiente executa o FastAPI e o frontend React/Vite no mesmo host. O Nginx
é o único serviço com porta publicada; `/api/*` e `/health` são encaminhados ao
backend na rede privada do Compose. A landing page `src/lp` não faz parte destas
imagens.

## Configuração em runtime

Defina no processo que executará Docker Compose, ou por um provedor seguro de
segredos no host:

- `GEMINI_API_KEY` para usar o chat;
- `AZURE_SPEECH_RESOURCE` ou `AZURE_SPEECH_ENDPOINT`, `AZURE_SPEECH_KEY`,
  `AZURE_SPEECH_TIMEOUT_SECONDS` e `AZURE_SPEECH_MAX_ATTEMPTS` para áudio;
- `AUDIO_SIMULATED_IDENTITIES` no formato `token=entra_object_id`;
- `REPORT_SIMULATED_IDENTITIES` como o mapa JSON esperado pelo backend;
- `APP_IMAGE_TAG` para builds locais, ou `BACKEND_IMAGE_TAG` e
  `FRONTEND_IMAGE_TAG` para selecionar versões imutáveis independentes no ECR.

Ao executar Compose na raiz do repositório, o CLI também lê o `.env` da raiz
para interpolação. Esse arquivo não entra nos contextos de build e não é copiado
para as imagens; somente as variáveis enumeradas no serviço backend são
entregues em runtime. `src/backend/.env` não é usado pelo Compose.

O mapa de áudio e o mapa de relatórios devem ser configurados em runtime; os
tokens não ficam no frontend. Essa identidade é simulada e não equivale a
autenticação real. O mapa de áudio usa `token=entra_object_id`; o de relatórios
é um objeto JSON conforme o contrato atual de `REPORT_SIMULATED_IDENTITIES`.
O backend recusa iniciar se os mapas estiverem ausentes/vazios ou se as
credenciais necessárias para speech/chat não estiverem configuradas. O frontend
envia o token digitado no campo da sessão e o backend encaminha a transcrição
ao fluxo de chat.

O Compose fixa `PLN_WARMUP=1`, os quatro modos locais/sintéticos de relatório e
`REPORT_ARTIFACTS_DIR=/var/lib/m7/reports`. Ele não configura `DATABASE_URL`,
`SUPABASE_DATABASE_URL` nem variáveis `SUPABASE_*`. As credenciais Azure são
acessadas somente pelo backend.

Não copie `.env` para a imagem nem use `.env` como build context sem o
`.dockerignore`. O carregamento local de dotenv no FastAPI não sobrescreve as
variáveis de processo. O modelo BERTimbau, identificado por revisão imutável, é
baixado durante o build e carregado offline no startup.

## Build e execução padrão

Escolha uma tag ligada ao commit que está sendo validado; `latest` é recusada
pelos scripts:

```powershell
$env:APP_IMAGE_TAG = (git rev-parse --short HEAD)
.\scripts\docker-build.ps1 -Tag $env:APP_IMAGE_TAG
docker compose -f compose.prod.yml config --quiet
.\scripts\docker-up.ps1 -Tag $env:APP_IMAGE_TAG
Invoke-RestMethod http://localhost/health
```

`docker compose up -d` inicia backend e frontend. O notebook não pertence ao
perfil padrão.

Para iniciar o notebook explicitamente, forneça `JUPYTER_TOKEN` em runtime e
execute:

```powershell
docker compose --profile notebook -f compose.prod.yml up -d
```

O serviço publica `8888` somente em `127.0.0.1` no host e não aceita conexões
pela interface pública. Em EC2, use um túnel Session Manager para a porta local
do host; não encaminhe a porta do container diretamente. A configuração de
rede e o procedimento SSM estão em [docs/aws-operacao.md](aws-operacao.md).
O Jupyter exige o token configurado em runtime.

## Áudio e relatórios

O frontend envia `POST /api/audio` como multipart, campo `audio`, mantendo o
header Bearer recebido na sessão. A conversão do navegador para WAV PCM mono,
16 kHz continua no frontend. Nginx aceita o multipart até 3 MiB para acomodar
o envelope; o backend segue limitando o arquivo de áudio a 2 MiB e 60 segundos,
aceitando WAV/PCM e OGG/OPUS. O timeout do proxy fica acima do timeout HTTP de
120 segundos do frontend; os defaults Azure continuam sendo 6 segundos e duas
tentativas.

Os DOCX são salvos em volume Docker persistente. Como o repositório de relatórios
permanece em memória, reiniciar/substituir o backend perde IDs, estados de
execução e sessões, embora os arquivos do volume permaneçam. Esse modo é somente
para demonstração controlada com dados sintéticos.

## Recursos, logs e rollback

- Backend: limite de 4 GiB e 2 CPUs; PLN usa PyTorch CPU e consome memória no
  warmup.
- Frontend/Nginx: limite de 512 MiB e 0,5 CPU.
- Notebook: limite de 4 GiB e 2 CPUs, sem restart automático. Não o mantenha
  ativo junto ao backend em hosts sem memória suficiente; reserve cerca de
  12 GiB de RAM para executar os três containers confortavelmente.
- Para o MVP temporário, comece com `t3.large` e EBS gp3 de 50 GiB. O notebook
  permanece desligado; use `t3.xlarge` somente se a medição real mostrar falta
  de memória ao executar o notebook sob demanda.
- No Learner Lab, mantenha o notebook desligado fora do uso e pare a EC2 quando
  a demonstração terminar. EBS e artefatos persistentes continuam ocupando
  armazenamento; tráfego para Azure Speech, Gemini e registries também pode
  gerar custo.
- Todos os serviços usam rotação Docker `json-file` (10 MiB × 3). O formato de
  acesso do Nginx registra método, caminho sem query, status e duração; não
  registra cabeçalhos nem corpo da requisição.
- A porta 8000 e a porta 5173 não são publicadas. O notebook, somente no profile
  explícito, vincula 8888 ao loopback do host. Na EC2, o Nginx também é
  vinculado ao loopback (`127.0.0.1:80`) e acessado por túnel SSM.

Para rollback local, selecione a tag anterior sem reconstruir:

```powershell
$env:APP_IMAGE_TAG = '<tag-anterior-aprovada>'
docker compose -f compose.prod.yml up -d --no-build --force-recreate
```

Registre e retenha a tag ou digest de cada imagem validada. Não use comandos de
remoção de volumes no rollback: eles apagariam os DOCX e os notebooks do volume.
O procedimento de rollback remoto por SSM está em [docs/aws-operacao.md](aws-operacao.md).
