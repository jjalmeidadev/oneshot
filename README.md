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

```text
📦 g05
 ┣ 📂 .githooks                       hooks locais para validação de commits e pushes
 ┃ ┣ 📄 commit-msg                    validação do padrão de mensagem de commit
 ┃ ┣ 📄 pre-commit                    validações executadas antes do commit
 ┃ ┗ 📄 pre-push                      validações executadas antes do push
 ┣ 📂 .gitlab                         templates utilizados no GitLab
 ┃ ┣ 📂 issue_templates               modelos de issue do projeto
 ┃ ┃ ┗ 📄 Tarefa.md                   template padrão para tarefas
 ┃ ┗ 📂 merge_request_templates       modelos de merge request do projeto
 ┃   ┗ 📄 Default.md                  template padrão para merge requests
 ┣ 📂 docs                            documentação principal do projeto
 ┃ ┣ 📂 diagrams                      fontes editáveis dos diagramas em PlantUML
 ┃ ┣ 📂 img                           imagens, diagramas, personas, jornadas e materiais visuais
 ┃ ┣ 📄 GestaoConfiguracao.md         GitFlow, políticas de branch, hooks e versionamento
 ┃ ┣ 📄 GestaoProjeto.md              sprints, riscos, papéis, contrato e planejamento
 ┃ ┣ 📄 GuiaPadroesDesenvolvimento.md padrões e convenções de desenvolvimento da equipe
 ┃ ┣ 📄 Index.md                      índice de navegação da documentação
 ┃ ┣ 📄 Manual-instalacao.md          instruções de instalação e execução da solução
 ┃ ┣ 📄 Projeto.md                    documentação principal do produto e da solução
 ┃ ┗ 📄 prototipo-1-roteiro.md        roteiro do primeiro protótipo
 ┣ 📂 scripts                         scripts de apoio ao desenvolvimento e auditoria
 ┃ ┣ 📄 audit-repo.ps1                auditoria da estrutura e conformidade do repositório
 ┃ ┣ 📄 install-hooks.ps1             instalação dos hooks em ambiente Windows
 ┃ ┗ 📄 install-hooks.sh              instalação dos hooks em ambiente Unix/Linux
 ┣ 📂 src                             código-fonte e artefatos técnicos da solução
 ┃ ┣ 📂 backend                       API FastAPI: áudio, PLN, RAG, banco e integrações
 ┃ ┃ ┣ 📂 app
 ┃ ┃ ┃ ┣ 📂 audio                     recebimento, validação e transcrição do áudio
 ┃ ┃ ┃ ┣ 📂 database                  conexão PostgreSQL/Supabase e trilha do RNF03
 ┃ ┃ ┃ ┣ 📂 gemini                    cliente do provedor de LLM
 ┃ ┃ ┃ ┣ 📂 nlp                       núcleo de PLN: pré-processamento, entidades e inferência
 ┃ ┃ ┃ ┣ 📂 rag                       recuperação de contexto em JSON e no banco
 ┃ ┃ ┃ ┣ 📂 tests                     testes automatizados do backend
 ┃ ┃ ┃ ┣ 📄 main.py                   rotas /health, /api/chat e /api/audio
 ┃ ┃ ┃ ┗ 📄 pipeline.py               orquestração da classificação, resposta e rastreabilidade
 ┃ ┃ ┣ 📄 requirements.txt            dependências da API
 ┃ ┃ ┗ 📄 requirements-pln.txt        dependências da inferência do classificador
 ┃ ┣ 📂 frontend                      bancada web em React, TypeScript e Vite
 ┃ ┃ ┣ 📂 e2e                         testes de navegador com Playwright
 ┃ ┃ ┣ 📂 src                         componentes, hooks, estado e cliente HTTP
 ┃ ┃ ┗ 📄 TESTES.md                   matriz e evidências dos testes da interface
 ┃ ┣ 📂 database                      scripts e documentação do banco de dados
 ┃ ┃ ┣ 📂 docs                        dicionário de dados e decisões de modelagem
 ┃ ┃ ┗ 📂 sql
 ┃ ┃   ┣ 📄 01_create_database.sql    criação da estrutura do banco
 ┃ ┃   ┣ 📄 02_initial_data.sql       carga inicial de dados sintéticos
 ┃ ┃   ┣ 📄 03_rollback_data.sql      rollback controlado do baseline
 ┃ ┃   ┗ 📄 04_rag_synthetic_data.sql carga dos extratos consultáveis pelo RAG
 ┃ ┗ 📂 notebooks                     notebooks de experimentação e artefatos treinados
 ┃   ┣ 📂 artefatos                   dataset, catálogo, modelo e métricas da execução
 ┃   ┣ 📄 classificador_intencoes_metro.ipynb  benchmark do classificador de intenções
 ┃   ┗ 📄 preprocessamento_entidades.ipynb     medição do pré-processamento e das entidades
 ┣ 📄 .gitignore                      arquivos e pastas ignorados pelo Git
 ┣ 📄 .gitlab-ci.yml                  pipeline de testes do backend e do frontend
 ┗ 📄 README.md                       visão geral do projeto
```

---

## 📚 Documentação

A documentação do projeto está organizada de acordo com as diferentes dimensões necessárias para registrar a gestão, o processo de desenvolvimento e a construção do produto.

### Gestão do Projeto

- [`GestaoProjeto.md`](docs/GestaoProjeto.md) — documentação relacionada à gestão e acompanhamento do projeto, incluindo informações referentes ao planejamento, organização e evolução das atividades da equipe.

### Processo de Desenvolvimento de Software

- [`GestaoConfiguracao.md`](docs/GestaoConfiguracao.md) — documentação das práticas e diretrizes utilizadas para gerenciamento da configuração e controle dos artefatos do projeto.

- [`GuiaPadroesDesenvolvimento.md`](docs/GuiaPadroesDesenvolvimento.md) — documentação dos padrões, convenções e diretrizes utilizados para orientar o desenvolvimento da solução.

### Desenvolvimento do Produto

- [`Projeto.md`](docs/Projeto.md) — documentação principal do produto, contemplando o entendimento do projeto e do negócio, problema, visão do produto, proposta de valor, escopo e objetivos estratégicos da solução.

- [`Manual-instalacao.md`](docs/Manual-instalacao.md) — documentação destinada a orientar a preparação do ambiente e os procedimentos necessários para instalação e execução da solução.

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

<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="#">Oneshot</a> by <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://www.inteli.edu.br/">Inteli</a>, <a href="https://www.linkedin.com/in/ntsfelipe/">Felipe Neves</a>, <a href="https://www.linkedin.com/in/henrique-rodrigues-diniz-b7b011319/">Henrique Diniz</a>,  <a href="https://www.linkedin.com/in/jaimeandradedealmeida/">Jaime Almeida</a>, <a href="https://www.linkedin.com/in/leonardoramosvieira">Leonardo Ramos</a>, <a href="https://www.linkedin.com/in/pedro-uchoaa/">Pedro Uchoa</a>, <a href="https://www.linkedin.com/in/wendel-feitosa-975bb1346/">Wendel Feitosa</a> is licensed under <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1">
