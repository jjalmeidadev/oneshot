<<<<<<< HEAD
# Agente Inteligente para Gestão de Portfólio de Projetos do Metrô

## Grupo — Nome a definir

## Integrantes

- Felipe Teixeira
- Henrique Diniz
- Jaime Almeida
- Leonardo Ramos
- Pedro Uchoa
- Wendel Feitosa
=======
# Agente de IA para o Portfólio de Projetos do Metrô

## Nome do grupo: Oneshot

## Integrantes:

- <a href="https://www.linkedin.com/in/ntsfelipe/">Felipe Neves</a>
- <a href="https://www.linkedin.com/in/henrique-rodrigues-diniz-b7b011319/">Henrique Diniz</a>
- <a href="https://www.linkedin.com/in/jaimeandradedealmeida/">Jaime Almeida</a>
- <a href="https://www.linkedin.com/in/leonardoramosvieira">Leonardo Ramos</a>
- <a href="https://www.linkedin.com/in/pedro-uchoaa/">Pedro Uchoa</a>
- <a href="https://www.linkedin.com/in/wendel-feitosa-975bb1346/">Wendel Feitosa</a>
>>>>>>> 363ee167cc1a1ceb352f9aa77be25d2f08b63533

---

## 📝 Descrição

<<<<<<< HEAD
O projeto consiste no desenvolvimento de um **Agente Inteligente para Gestão de Portfólio de Projetos do Metrô**, desenvolvido no contexto da parceria acadêmica entre o Instituto de Tecnologia e Liderança (Inteli) e a Companhia do Metropolitano de São Paulo (Metrô).

A solução propõe uma camada inteligente de interação sobre as informações utilizadas pela área de Gestão de Portfólio de Projetos (PMO), permitindo que gestores e demais usuários consultem informações do portfólio por meio de linguagem natural.

O agente busca reduzir o esforço necessário para localizar e interpretar informações distribuídas entre diferentes fontes, apoiando atividades relacionadas ao acompanhamento dos projetos, consulta a Termos de Abertura do Projeto (TAP), cronogramas, documentos normativos e demais informações relevantes para a gestão do portfólio.

---

## 📁 Organização da Documentação

A documentação do projeto segue a seguinte organização:

```text
📦 Projeto
 ┣ 📂 documentos
 ┃ ┣ 📄 GestaoProjeto.md
 ┃ ┣ 📄 GestaoConfiguracao.md
 ┃ ┣ 📄 GuiaPadroesDesenvolvimento.md
 ┃ ┣ 📄 Projeto.md
 ┃ ┗ 📄 Manual-Instalacao.md
 ┗ 📄 README.md

=======
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
 ┃ ┣ 📂 diagrams                      diagramas editáveis e arquivos de modelagem
 ┃ ┃ ┣ 📄 analise-swot.pptx           matriz SWOT em formato editável
 ┃ ┃ ┣ 📄 componentes-metro-5.2.puml  diagrama de componentes atualizado em PlantUML
 ┃ ┃ ┗ 📄 componentes-mvp.puml        diagrama de componentes do MVP em PlantUML
 ┃ ┣ 📂 img                           imagens, diagramas, personas, jornadas e materiais visuais
 ┃ ┣ 📄 GestaoConfiguracao.md         políticas de versionamento, branches e configuração
 ┃ ┣ 📄 GestaoProjeto.md              planejamento, retrospectivas e acompanhamento do projeto
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
 ┃ ┣ 📂 database                      scripts de banco de dados
 ┃ ┃ ┣ 📄 01_create_database.sql      criação da estrutura inicial do banco
 ┃ ┃ ┣ 📄 02_initial_data.sql         carga inicial de dados sintéticos
 ┃ ┃ ┗ 📄 03_rollback_data.sql        rollback controlado do baseline
 ┃ ┗ 📂 notebooks                     notebooks de experimentação e validação técnica
 ┃   ┗ 📄 classificador_intencoes_metro.ipynb notebook do classificador de intenções
 ┣ 📄 .gitignore                      arquivos e pastas ignorados pelo Git
 ┗ 📄 README.md                       visão geral do projeto
>>>>>>> 363ee167cc1a1ceb352f9aa77be25d2f08b63533
```

---

## 📚 Documentação

A documentação do projeto está organizada de acordo com as diferentes dimensões necessárias para registrar a gestão, o processo de desenvolvimento e a construção do produto.

### Gestão do Projeto

<<<<<<< HEAD
- [`GestaoProjeto.md`](documentos/GestaoProjeto.md) — documentação relacionada à gestão e acompanhamento do projeto, incluindo informações referentes ao planejamento, organização e evolução das atividades da equipe.

### Processo de Desenvolvimento de Software

- [`GestaoConfiguracao.md`](documentos/GestaoConfiguracao.md) — documentação das práticas e diretrizes utilizadas para gerenciamento da configuração e controle dos artefatos do projeto.

- [`GuiaPadroesDesenvolvimento.md`](documentos/GuiaPadroesDesenvolvimento.md) — documentação dos padrões, convenções e diretrizes utilizados para orientar o desenvolvimento da solução.

### Desenvolvimento do Produto

- [`Projeto.md`](documentos/Projeto.md) — documentação principal do produto, contemplando o entendimento do projeto e do negócio, problema, visão do produto, proposta de valor, escopo e objetivos estratégicos da solução.

- [`Manual-Instalacao.md`](documentos/Manual-Instalacao.md) — documentação destinada a orientar a preparação do ambiente e os procedimentos necessários para instalação e execução da solução.

---

## 🔎 Prioridades da Primeira Versão
=======
- [`GestaoProjeto.md`](docs/GestaoProjeto.md) — documentação relacionada à gestão e acompanhamento do projeto, incluindo informações referentes ao planejamento, organização e evolução das atividades da equipe.

### Processo de Desenvolvimento de Software

- [`GestaoConfiguracao.md`](docs/GestaoConfiguracao.md) — documentação das práticas e diretrizes utilizadas para gerenciamento da configuração e controle dos artefatos do projeto.

- [`GuiaPadroesDesenvolvimento.md`](docs/GuiaPadroesDesenvolvimento.md) — documentação dos padrões, convenções e diretrizes utilizados para orientar o desenvolvimento da solução.

### Desenvolvimento do Produto

- [`Projeto.md`](docs/Projeto.md) — documentação principal do produto, contemplando o entendimento do projeto e do negócio, problema, visão do produto, proposta de valor, escopo e objetivos estratégicos da solução.

- [`Manual-instalacao.md`](docs/Manual-instalacao.md) — documentação destinada a orientar a preparação do ambiente e os procedimentos necessários para instalação e execução da solução.

---

## 🔎 Prioridades do MVP
>>>>>>> 363ee167cc1a1ceb352f9aa77be25d2f08b63533

Com base nas informações levantadas junto aos representantes do Metrô, a primeira versão da solução prioriza:

1. **Avanço dos projetos**
2. **Termo de Abertura do Projeto (TAP)**
3. **Cronograma**
4. Consulta a informações relacionadas ao portfólio;
5. Consulta a documentos e normativos;
6. Respostas contextualizadas e fundamentadas nas fontes disponíveis.

Funcionalidades adicionais poderão ser incorporadas progressivamente conforme as prioridades do PMO, os resultados das validações e a evolução do produto.

---

<<<<<<< HEAD
## 🚀 Evolução do Produto

#### Conteúdo à ser adicionado
=======
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
>>>>>>> 363ee167cc1a1ceb352f9aa77be25d2f08b63533
