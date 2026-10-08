# Agente de IA para o Portfólio de Projetos do Metrô

## Nome do grupo: Oneshot

## Integrantes:

- <a href="https://www.linkedin.com/in/ntsfelipe/">Felipe Neves</a>
- <a href="https://www.linkedin.com/in/henrique-rodrigues-diniz-b7b011319/">Henrique Diniz</a>
- <a href="https://www.linkedin.com/in/jaimeandradedealmeida/">Jaime Almeida</a>
- <a href="https://www.linkedin.com/in/leonardoramosvieira">Leonardo Ramos</a>
- <a href="https://www.linkedin.com/in/pedro-uchoaa/">Pedro Uchoa</a>
- <a href="https://www.linkedin.com/in/wendel-feitosa-975bb1346/">Wendel Feitosa</a>

---

## 📝 Descrição

O projeto consiste no desenvolvimento de um **Agente de IA para o Portfólio de Projetos do Metrô**, desenvolvido no contexto da parceria acadêmica entre o Inteli e a Companhia do Metropolitano de São Paulo (Metrô).

A solução é um agente conversacional que opera sobre a documentação e os dados de portfólio já mantidos pelo Metrô, permitindo que gestores e demais usuários consultem informações do portfólio por meio de linguagem natural, com indicação da fonte de cada resposta.

O agente busca reduzir o esforço necessário para localizar e interpretar informações distribuídas entre diferentes fontes, apoiando atividades relacionadas ao acompanhamento dos projetos, consulta a Termos de Abertura do Projeto (TAP), cronogramas, documentos normativos e demais informações relevantes para a gestão do portfólio.

---

## 📁 Estrutura de pastas

O repositório do projeto segue a seguinte organização:

As pastas padrão de entrega são `docs` (documentação) e `src` (código), com
`src/frontend`, `src/backend` e `src/database`. `src/lp` e `src/notebooks`
preservam artefatos complementares de prototipação e PLN. O banco tem
[README próprio](src/database/README.md); não existe `src/backend/database`.

```text
📦 g05
 ┣ 📂 .githooks                       hooks de validação de commits e pushes
 ┣ 📂 .gitlab                         templates de issues e merge requests
 ┣ 📂 docs                            documentação, diagramas, evidências, stories e testes
 ┃ ┣ 📂 backlog                       backlog exportado da Sprint 5
 ┃ ┣ 📂 diagrams                      fontes editáveis dos diagramas
 ┃ ┣ 📂 evidencias                    evidências consolidadas por sprint
 ┃ ┣ 📂 img                           imagens usadas na documentação
 ┃ ┣ 📂 stories                       stories técnicas de infraestrutura
 ┃ ┣ 📂 testes                        planos e relatórios de testes
 ┃ ┣ 📂 usabilidade                   instrumentos e resultados de usabilidade
 ┃ ┣ 📄 Index.md                      índice de todos os documentos Markdown
 ┃ ┣ 📄 Manual-instalacao.md          manual completo de instalação e execução
 ┃ ┗ 📄 Projeto.md                    documentação consolidada do projeto
 ┣ 📂 infra
 ┃ ┗ 📂 aws                           CloudFormation, User Data e CloudWatch Agent
 ┣ 📂 scripts
 ┃ ┣ 📂 aws                           deploy, atualização e rollback na AWS
 ┃ ┣ 📄 audit-repo.ps1                auditoria de conformidade do repositório
 ┃ ┣ 📄 docker-build.ps1              build das imagens da aplicação
 ┃ ┗ 📄 docker-up.ps1                 inicialização da stack em contêineres
 ┣ 📂 src
 ┃ ┣ 📂 agent                         artefatos do workflow de relatório
 ┃ ┣ 📂 backend                       API FastAPI, PLN, RAG, integrações e testes
 ┃ ┣ 📂 database                      scripts SQL, documentação e snapshots
 ┃ ┣ 📂 frontend                      aplicação React principal e testes
 ┃ ┣ 📂 lp                            landing page e demonstração RAG
 ┃ ┗ 📂 notebooks                     experimentos, treinamento e artefatos de PLN
 ┣ 📄 .dockerignore                   exclusões do contexto de build
 ┣ 📄 .env.example                    variáveis de ambiente de referência
 ┣ 📄 .gitignore                      arquivos e pastas não versionados
 ┣ 📄 .gitlab-ci.yml                  pipeline de integração contínua
 ┣ 📄 compose.prod.yml                stack de execução da aplicação
 ┣ 📄 compose.rabbitmq.yml            stack isolada do RabbitMQ
 ┗ 📄 README.md                       visão geral e início rápido
```

---

## 🚀 Início rápido

Pré-requisitos: Python 3.12 ou 3.13, Node.js 24 e npm. No PowerShell, execute a partir da raiz do repositório:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r src/backend/requirements.txt -r src/backend/requirements-pln.txt
Copy-Item src/backend/.env.example src/backend/.env

Set-Location src/frontend
npm ci
Set-Location ../..
```

Revise `src/backend/.env` e informe somente as credenciais necessárias para os serviços externos. Em dois terminais separados, inicie o back-end e o front-end:

```powershell
# Terminal 1 — raiz do repositório
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir src/backend --host 127.0.0.1 --port 8000

# Terminal 2 — raiz do repositório
Set-Location src/frontend
npm run dev
```

Abra `http://localhost:5173` e confirme a API em `http://127.0.0.1:8000/health`. Para configuração de banco, execução em contêineres e solução de problemas, consulte o [Manual de instalação](docs/Manual-instalacao.md).

Esses endereços são locais: funcionam depois de iniciar os dois servidores e
não representam links públicos de entrega. Para o fluxo autenticado completo,
configure Supabase Auth, banco e regras de acesso conforme o manual.

### Aplicação na nuvem

A versão de demonstração da Sprint 5 está disponível em
**[aptitude-exemplary-saddling.ngrok-free.dev](https://aptitude-exemplary-saddling.ngrok-free.dev)**.
O endereço usa um domínio gratuito fixo do ngrok e aponta para a aplicação na
EC2; não é necessário manter o computador de um integrante ligado. No primeiro
acesso pelo navegador, o ngrok mostra um aviso de segurança: confira o endereço
acima e clique em **Visit Site** para abrir a aplicação. Cada visitante poderá
ver esse aviso uma vez.

Para entrar na demonstração, selecione uma das personas na tela inicial e use
a senha correspondente:

| Persona | Senha de teste |
| --- | --- |
| PMO | `pmo1232026` |
| Líder de subportfólio | `leader1232026` |
| Gerente de projeto | `manager1232026` |
| Consulta | `consulta1232026` |

Essas credenciais são compartilhadas somente para a avaliação do MVP. Não use
essas contas para inserir dados pessoais ou informações confidenciais.

O link só responde enquanto a instância, os contêineres e o serviço ngrok
estiverem ativos. O plano gratuito tem limites de tráfego e requisições, por
isso o ambiente é destinado a testes controlados. O [Manual de instalação](docs/Manual-instalacao.md)
orienta a execução local; o processo de publicação e as verificações na nuvem
estão na [Seção 10 do Projeto.md](docs/Projeto.md#10-procedimentos-de-implantação).

---

## 📚 Documentação

A documentação do projeto está organizada de acordo com as diferentes dimensões necessárias para registrar a gestão, o processo de desenvolvimento e a construção do produto.

- [`Index.md`](docs/Index.md) — índice completo dos documentos Markdown versionados no repositório.

- [Fechamento das cinco sprints](docs/GestaoProjeto.md) — retrospectiva,
  métricas, riscos, papéis, contrato e post mortem.
- [Auditoria do Escritório de Projetos](docs/Projeto.md) —
  critério, correção e evidência para reavaliação.
- [Arquitetura detalhada e integrações](docs/Projeto.md).

### Gestão do Projeto

- [`GestaoProjeto.md`](docs/GestaoProjeto.md) — documentação relacionada à gestão e acompanhamento do projeto, incluindo informações referentes ao planejamento, organização e evolução das atividades da equipe.

### Processo de Desenvolvimento de Software

- [`GestaoConfiguracao.md`](docs/GestaoConfiguracao.md) — documentação das práticas e diretrizes utilizadas para gerenciamento da configuração e controle dos artefatos do projeto.

- [`GuiaPadroesDesenvolvimento.md`](docs/GuiaPadroesDesenvolvimento.md) — documentação dos padrões, convenções e diretrizes utilizados para orientar o desenvolvimento da solução.

### Desenvolvimento do Produto

- [`Projeto.md`](docs/Projeto.md) — documentação principal do produto, contemplando o entendimento do projeto e do negócio, problema, visão do produto, proposta de valor, escopo e objetivos estratégicos da solução.

- [`Manual-instalacao.md`](docs/Manual-instalacao.md) — documentação destinada a orientar a preparação do ambiente e os procedimentos necessários para instalação e execução da solução.

- [`webhooks-rabbitmq.md`](docs/evidencias/sprint-05/webhooks-rabbitmq.md) — evidência reproduzível dos dois webhooks, da outbox e do processamento RabbitMQ da Sprint 5.

---

## 🔎 Prioridades do MVP

Com base nas informações levantadas junto aos representantes do Metrô, a primeira versão da solução prioriza:

1. **Avanço dos projetos**
2. **Termo de Abertura do Projeto (TAP)**
3. **Cronograma**
4. Consulta a informações relacionadas ao portfólio;
5. Consulta a documentos e normativos;
6. Respostas contextualizadas e fundamentadas nas fontes disponíveis.

Funcionalidades adicionais poderão ser incorporadas progressivamente conforme as prioridades do PMO, os resultados das validações e a evolução do produto.

---

## 🗃 Histórico de lançamentos

* 0.1.0 - 14/08/2026
    * Entendimento do Negócio
    * Especificação de Requisitos Funcionais e Não Funcionais
    * Gestão de Projeto e Configuração
* 0.2.0 - 28/08/2026
    * Prototipação Exploratória
    * Estratégia Técnica da Solução
    * Gestão de Projetos Evolutiva
* 0.3.0 - 11/09/2026
    * Desenvolvimento e Documentação Técnica do Projeto
    * Planejamento de Testes Sistêmicos
    * Gestão de Projetos Evolutiva
* 0.4.0 - 25/09/2026
    * Desenvolvimento e Documentação Técnica do Projeto
    * Execução de Testes Sistêmicos
    * Gestão de Projetos Evolutiva
* 0.5.0 - 07/10/2026
    * Desenvolvimento e Documentação Técnica do Projeto
    * Documentação Técnica Final
    * Gestão de Projetos Evolutiva e Apresentação Final

## 📋 Licença

## Referências bibliográficas e técnicas

- FASTAPI. *Documentação oficial*. Disponível em: [FastAPI](https://fastapi.tiangolo.com/).
- SUPABASE. *Auth*. Disponível em: [documentação de autenticação](https://supabase.com/docs/guides/auth).
- RABBITMQ. *RabbitMQ Documentation*. Disponível em: [documentação oficial](https://www.rabbitmq.com/docs).
- MICROSOFT. *Azure Speech documentation*. Disponível em: [Microsoft Learn](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/).

Fontes consultadas na auditoria de fechamento. O uso de cada serviço e seus
limites estão na [arquitetura](docs/Projeto.md); manifests/locks fixam as
versões da aplicação. Não foi identificado repositório próprio auxiliar além
deste GitLab; as dependências externas são identificadas por essas referências.

## Atribuição e licença

<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="#">Oneshot</a> by <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://www.inteli.edu.br/">Inteli</a>, <a href="https://www.linkedin.com/in/ntsfelipe/">Felipe Neves</a>, <a href="https://www.linkedin.com/in/henrique-rodrigues-diniz-b7b011319/">Henrique Diniz</a>,  <a href="https://www.linkedin.com/in/jaimeandradedealmeida/">Jaime Almeida</a>, <a href="https://www.linkedin.com/in/leonardoramosvieira">Leonardo Ramos</a>, <a href="https://www.linkedin.com/in/pedro-uchoaa/">Pedro Uchoa</a>, <a href="https://www.linkedin.com/in/wendel-feitosa-975bb1346/">Wendel Feitosa</a> is licensed under <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1">
