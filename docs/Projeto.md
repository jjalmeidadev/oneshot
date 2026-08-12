<Table>
  <tr>
    <td><a href= "https://www.btgpactual.com/"><img src="img/logo-btg.png" alt="Centro Paula Souza" border="0"></td>
    <td>
      <a href= "https://www.inteli.edu.br/"><img src="img/logo-Inteli.png" alt="Inteli - Instituto de Tecnologia e Liderança" border="0"></a>
    </td>
  </tr>
</table>

# Nome do Projeto: <nome do projeto>

## Nome do Grupo: <nome do grupo>

## Integrantes:

- <a href="https://www.linkedin.com/in/username/">Nome</a>
- <a href="https://www.linkedin.com/in/username/">Nome</a>
- <a href="https://www.linkedin.com/in/username/">Nome</a>
- <a href="https://www.linkedin.com/in/username/">Nome</a>
- <a href="https://www.linkedin.com/in/username/">Nome</a>
- <a href="https://www.linkedin.com/in/username/">Nome</a>
- <a href="https://www.linkedin.com/in/username/">Nome</a>
- <a href="https://www.linkedin.com/in/username/">Nome</a>

# Sumário

- [1. Introdução](#1-introdução)
  - [1.1 Termos e Abreviações](#11-termos-e-abreviações)
  - [1.2 Objetivo do Documento](#12-objetivo-do-documento)
- [2. Entendimento do Projeto e do Negócio](#2-entendimento-do-projeto-e-do-negócio)
  - [2.1 Contexto da Indústria do Parceiro](#21-contexto-da-indústria-do-parceiro)
  - [2.2 Problema](#22-problema)
  - [2.3 Visão do Projeto e do Produto](#23-visão-do-projeto-e-do-produto)
  - [2.4 Personas e Jornada do Usuário](#24-personas-e-jornada-do-usuário)
  - [2.5 Modelagem do Fluxo de Negócio](#25-modelagem-do-fluxo-de-negócio)
    - [2.5.1 Cadeia de Valor](#251-cadeia-de-valor)
    - [2.5.2 Fluxo de Negócio Proposto (AS-IS e TO-BE)](#252-fluxo-de-negócio-proposto-as-is-e-to-be)
  - [2.6 Matriz de Risco do Projeto](#26-matriz-de-risco-do-projeto)
  - [2.7 Ideação](#27-ideação)
  - [2.8 Canvas do Projeto](#28-canvas-do-projeto)
- [3. Requisitos do Projeto](#3-requisitos-do-projeto)
  - [3.1 Requisitos Funcionais (RFs)](#31-requisitos-funcionais-rfs)
  - [3.2 Requisitos Não Funcionais (RNFs)](#32-requisitos-não-funcionais-rnfs)
  - [3.3 Correlação RFs e RNFs](#33-correlação-rfs-e-rnfs)
  - [3.4 Casos de Uso](#34-casos-de-uso)
  - [3.5 Casos de Uso x Requisitos Funcionais](#35-casos-de-uso-x-requisitos-funcionais)
- [4. Modelagem de Dados](#4-modelagem-de-dados)
  - [4.1 Especificação da Base de Dados para Modelo de Recomendação](#41-especificação-da-base-de-dados-para-modelo-de-recomendação)
  - [4.2 Modelo Conceitual de Dados](#42-modelo-conceitual-de-dados)
  - [4.3 Modelo Lógico de Dados](#43-modelo-lógico-de-dados)
  - [4.4 Modelo Físico de Dados](#44-modelo-físico-de-dados)
- [5. Solução Técnica (Design)](#5-solução-técnica-design)
  - [5.1 Diagrama de Classes](#51-diagrama-de-classes)
  - [5.2 Diagrama de Componentes da UML](#52-diagrama-de-componentes-da-uml)
  - [5.3 Diagramas de Sequência da UML](#53-diagramas-de-sequência-da-uml)
- [6. Mapeamento Técnico de Infraestrutura e Implantação](#6-mapeamento-técnico-de-infraestrutura-e-implantação)
  - [6.1 Diagrama de Implantação da UML](#61-diagrama-de-implantação-da-uml)
  - [6.2 Justificativa das Escolhas de Implantação](#62-justificativa-das-escolhas-de-implantação)
  - [6.3 Considerações sobre Desempenho e Segurança](#63-considerações-sobre-desempenho-e-segurança)
- [7. Projeto Visual da Solução](#7-projeto-visual-da-solução)
  - [7.1 Desenvolvimento de Wireframes](#71-desenvolvimento-de-wireframes)
  - [7.2 Desenvolvimento de Mockups](#72-desenvolvimento-de-mockups)
  - [7.3 Guia Visual](#73-guia-visual)
- [8. Desenvolvimento do Projeto](#8-desenvolvimento-do-projeto)
  - [8.1 Arquitetura de Codificação e Estrutura de Diretórios](#81-arquitetura-de-codificação-e-estrutura-de-diretórios)
  - [8.2 Modelo de Recomendação](#82-modelo-de-recomendação)
  - [8.3 Desenvolvimento de Features](#83-desenvolvimento-de-features)
    - [8.3.1 Sprint 3](#831-sprint-3)
    - [8.3.2 Sprint 4](#832-sprint-4)
    - [8.3.3 Sprint 5](#833-sprint-5)
  - [8.4 Testes Unitários e de Integração](#84-testes-unitários-e-de-integração)
  - [8.5 Documentações automáticas](#85-documentações-automáticas)
- [9. Planejamento e Execução de Testes](#9-planejamento-e-execução-de-testes)
  - [9.1 Testes Funcionais](#91-testes-funcionais)
    - [9.1.1 Planejamento](#911-planejamento)
    - [9.1.2 Resultados](#912-resultados)
  - [9.2 Testes de RNFs](#92-testes-de-rnfs)
    - [9.2.1 Planejamento](#921-planejamento)
    - [9.2.2 Resultados](#922-resultados)
  - [9.3 Testes de Usabilidade](#93-testes-de-usabilidade)
    - [9.3.1 Planejamento](#931-planejamento)
    - [9.3.2 Resultados](#932-resultados)
- [10. Procedimentos de Implantação](#10-procedimentos-de-implantação)
  - [10.1 Implantação e Configuração do Banco de Dados](#101-implantação-e-configuração-do-banco-de-dados)
  - [10.2 Implantação do Protótipo para uso por equipe de desenvolvimento](#102-implantação-do-protótipo-para-uso-por-equipe-de-desenvolvimento)
- [Referências](#referências)


# 1. Introdução
Este documento apresenta a especificação da solução desenvolvida para a Plataforma Tecnológica do Metrô de São Paulo, no contexto do projeto acadêmico realizado em parceria entre o Instituto de Tecnologia e Liderança (Inteli) e a Companhia do Metropolitano de São Paulo (Metrô).

A proposta consiste no desenvolvimento de um agente inteligente para apoio à Gestão de Portfólio de Projetos (PMO), capaz de utilizar Inteligência Artificial e processamento de linguagem natural para facilitar o acesso às informações estratégicas do portfólio, apoiar consultas em linguagem natural e reduzir atividades operacionais atualmente realizadas de forma manual.

Ao longo deste documento são apresentados o contexto do problema, a visão do produto, os requisitos levantados junto ao parceiro, a arquitetura proposta, a modelagem da solução, os processos de desenvolvimento adotados e os resultados obtidos durante o projeto.

Além de servir como registro técnico do desenvolvimento realizado pela equipe, este documento busca consolidar as principais decisões arquiteturais, funcionais e estratégicas que fundamentam a construção da solução, permitindo sua compreensão, evolução e futura manutenção.

---
## 1.1 Termos e Abreviações
A Tabela 1 apresenta os principais termos e abreviações utilizados ao longo deste documento.

| Termo | Descrição |
|---------|-----------|
| AI | Artificial Intelligence (Inteligência Artificial). |
| Copilot | Assistente de Inteligência Artificial da Microsoft utilizado como interface conversacional da solução. |
| IA | Inteligência Artificial. |
| LLM | Large Language Model, modelo de linguagem utilizado para compreensão e geração de linguagem natural. |
| PLN | Processamento de Linguagem Natural, conjunto de técnicas utilizadas para interpretação das solicitações dos usuários. |
| PMO | Project Management Office (Escritório de Gestão de Projetos). |
| Portfólio | Conjunto de projetos gerenciados pela área de Gestão de Portfólio do Metrô. |
| Projeto | Iniciativa acompanhada pelo PMO, composta por cronograma, TAP, indicadores, documentos e demais artefatos de gestão. |
| TAP | Termo de Abertura do Projeto. |
| Teams | Plataforma Microsoft Teams utilizada como principal interface de interação com o agente. |
| MVP | Minimum Viable Product (Produto Mínimo Viável), correspondente à primeira versão funcional da solução. |
| RAG | Retrieval-Augmented Generation, abordagem utilizada para geração de respostas fundamentadas em bases documentais. |
| SharePoint | Plataforma Microsoft utilizada para armazenamento e organização de documentos corporativos. |
| Power Platform | Conjunto de ferramentas Microsoft utilizado para desenvolvimento da solução, incluindo Power Automate, Copilot Studio e demais componentes do ecossistema. |

---

## 1.2 Objetivo do Documento
Este documento tem como objetivo especificar a solução proposta para o desenvolvimento do Agente Inteligente para Gestão de Portfólio de Projetos do Metrô, consolidando os aspectos estratégicos, funcionais e técnicos necessários para sua compreensão e implementação.

Além de apoiar o desenvolvimento da solução ao longo das diferentes etapas do projeto, este documento também estabelece uma base de referência para validação junto aos representantes do Metrô, registro das decisões tomadas pela equipe e documentação das principais características da plataforma desenvolvida, favorecendo sua evolução e futura manutenção.

---

# 2. Entendimento do Projeto e do Negócio
_conteúdo_

---

## 2.1 Contexto da Indústria do Parceiro

O transporte metroviário desempenha um papel estratégico na mobilidade urbana das grandes metrópoles, sendo responsável pelo deslocamento diário de milhões de passageiros com elevados requisitos de segurança, confiabilidade e eficiência. Além da operação da infraestrutura ferroviária, o setor envolve projetos contínuos de expansão da malha, modernização tecnológica, manutenção e renovação de ativos, acessibilidade e melhoria da experiência dos passageiros. Nesse cenário, destacam-se tendências como a digitalização das operações, o uso crescente de dados e Inteligência Artificial (IA) como apoio à gestão, a automação de processos e a busca por maior integração das informações organizacionais.

Ao mesmo tempo, o setor enfrenta desafios relacionados à complexidade e ao alto custo dos projetos de infraestrutura, à necessidade de modernização contínua dos sistemas, ao gerenciamento de grandes volumes de informações e à coordenação de projetos com diferentes objetivos, prazos e partes interessadas. No contexto de organizações públicas, somam-se ainda requisitos de governança, transparência, prestação de contas e uso eficiente dos recursos públicos. Dessa forma, a capacidade de organizar, consultar e utilizar informações confiáveis sobre projetos torna-se relevante tanto para a eficiência operacional quanto para a tomada de decisões estratégicas.

Inserida nesse setor, a Companhia do Metropolitano de São Paulo (Metrô) é uma empresa pública vinculada ao Governo do Estado de São Paulo e possui papel relevante no sistema de transporte de alta capacidade da Região Metropolitana de São Paulo. A companhia atua na operação de parte da rede metroviária e no planejamento e execução de investimentos estratégicos relacionados à expansão, modernização e melhoria da infraestrutura de transporte. Seu posicionamento não se caracteriza por uma participação de mercado tradicional, mas por sua relevância como operador público e agente de desenvolvimento da infraestrutura metroviária paulista, atendendo diariamente uma parcela significativa da demanda por transporte coletivo da região e administrando projetos de elevada complexidade e impacto social.

Nesse contexto, o Escritório Corporativo de Projetos (PMO) desempenha a função de coordenar e acompanhar o portfólio de projetos da organização, lidando com informações relacionadas a objetivos, cronogramas, riscos, indicadores e documentação técnica. Conforme identificado junto ao parceiro, a quantidade de projetos e a dispersão das informações em diferentes documentos dificultam a localização e a consolidação do conhecimento necessário para consultas e análises. Além disso, experiências anteriores com ferramentas de IA generativa apresentaram limitações relacionadas à confiabilidade das respostas, reforçando a necessidade de uma solução que utilize como referência a documentação oficial do Metrô.

Diante desse cenário, o projeto propõe o desenvolvimento de um agente inteligente baseado em Processamento de Linguagem Natural (PLN) para apoiar o PMO na gestão e consulta das informações do portfólio de projetos. A solução busca permitir consultas rápidas e contextualizadas sobre a documentação disponibilizada, reduzindo o esforço necessário para localizar informações e aumentando a confiabilidade das respostas. Dessa forma, o projeto se alinha às tendências de digitalização e aplicação de IA no setor, ao mesmo tempo em que atende às necessidades específicas de governança, gestão do conhecimento e apoio à tomada de decisão do Metrô de São Paulo.

---


## 2.2 Problema
_conteúdo_

---

## 2.3 Visão do Projeto e do Produto
Este tópico apresenta a visão estratégica do produto proposto, sua proposta de valor e os objetivos que orientam seu desenvolvimento, estabelecendo o alinhamento entre a solução, os desafios identificados pela área de Gestão de Portfólio de Projetos (PMO) do Metrô e as necessidades do negócio. A definição desses elementos busca orientar as decisões arquiteturais, funcionais e de priorização do projeto, delimitando claramente seu escopo, as capacidades esperadas e o valor agregado aos diferentes perfis de usuários.

A proposta surge em um contexto de evolução da plataforma tecnológica utilizada pelo PMO, que já dispõe de ferramentas corporativas para armazenamento, organização e acompanhamento das informações do portfólio, mas ainda depende de atividades manuais para localizar documentos, consolidar informações, interpretar normativos, produzir relatórios e acompanhar o andamento dos projetos. Como consequência, parte significativa do conhecimento institucional permanece distribuída entre diferentes repositórios e depende da experiência dos profissionais para ser acessada de forma eficiente.

Nesse cenário, o produto busca transformar a forma como gestores e colaboradores interagem com esse conjunto de informações, incorporando recursos de Inteligência Artificial capazes de compreender solicitações em linguagem natural, interpretar diferentes intenções de uso e disponibilizar respostas contextualizadas, seguras e fundamentadas nas fontes oficiais da organização.

Mais do que introduzir um novo canal de consulta, a solução propõe uma camada inteligente de apoio à gestão do portfólio, capaz de integrar diferentes fontes de conhecimento, reduzir esforços operacionais, apoiar processos de acompanhamento dos projetos e ampliar a capacidade analítica das equipes responsáveis pela tomada de decisão. Ao mesmo tempo, preserva o ecossistema tecnológico já adotado pela organização, permitindo que a evolução da plataforma ocorra de forma incremental, escalável e alinhada às práticas de governança existentes.

---

### 2.3.1 Visão do Produto

A visão do produto é transformar a interação entre os colaboradores e o portfólio de projetos do Metrô em uma experiência conversacional inteligente, integrada e orientada ao contexto de cada usuário, permitindo que informações estratégicas sejam acessadas por meio de linguagem natural de forma rápida, segura, rastreável e aderente às diretrizes de governança da organização.

Atualmente, embora a gestão do portfólio seja suportada por um conjunto consolidado de ferramentas corporativas, atividades relacionadas ao acompanhamento do avanço dos projetos, consulta a cronogramas, Termos de Abertura do Projeto (TAP), indicadores, documentos normativos e demais registros institucionais ainda exigem navegação entre diferentes plataformas, buscas manuais e interpretação de informações distribuídas em múltiplas fontes. Como consequência, essas atividades tornam-se mais demoradas, suscetíveis a inconsistências e dependentes do conhecimento especializado das equipes.

O produto propõe a criação de um agente inteligente integrado ao ambiente corporativo da organização, atuando como principal ponto de interação entre os usuários e o ecossistema de informações do portfólio. Por meio dessa interface conversacional, gestores e equipes poderão consultar informações dos projetos, esclarecer dúvidas sobre processos e normativos, localizar documentos, acompanhar cronogramas e obter respostas contextualizadas utilizando linguagem natural, reduzindo significativamente a necessidade de navegar entre diferentes sistemas ou conhecer previamente onde cada informação está armazenada.

Conceitualmente, a solução funciona como uma camada de inteligência sobre os ativos informacionais já existentes, estruturando, relacionando e disponibilizando conhecimentos provenientes de diferentes fontes de maneira unificada. Como núcleo da solução, será desenvolvido um mecanismo responsável por compreender a intenção das solicitações, interpretar o contexto das interações e direcionar automaticamente cada consulta aos fluxos de negócio mais adequados.

---

### 2.3.2 Proposta de Valor

A proposta de valor do produto fundamenta-se na utilização de Inteligência Artificial para transformar a maneira como gestores e equipes acessam, interpretam e utilizam as informações do portfólio de projetos, reduzindo barreiras operacionais e ampliando a capacidade de tomada de decisão baseada em dados.

O produto entrega valor ao:

- Centralizar o acesso às informações do portfólio em uma única interface conversacional integrada ao ambiente corporativo;
- Reduzir o tempo necessário para localizar documentos, cronogramas, indicadores, normativos e demais informações relevantes para a gestão dos projetos;
- Diminuir a dependência de consultas distribuídas entre diferentes plataformas e documentos institucionais;
- Facilitar a interpretação de processos e normativos por meio de respostas contextualizadas em linguagem natural;
- Disponibilizar informações fundamentadas em fontes oficiais, promovendo maior confiabilidade e rastreabilidade das respostas;
- Adaptar automaticamente o nível de detalhamento das informações conforme o perfil, as responsabilidades e as permissões de cada usuário;
- Apoiar gestores e equipes na obtenção rápida de informações estratégicas para acompanhamento do portfólio e tomada de decisão;
- Favorecer a padronização das consultas, reduzindo a dependência do conhecimento tácito das equipes;
- Estabelecer uma base evolutiva preparada para incorporar novas funcionalidades inteligentes conforme a maturidade da plataforma.

Mais do que responder perguntas, o agente busca atuar como uma camada inteligente de apoio à gestão do portfólio, reduzindo esforços operacionais, aumentando a disponibilidade das informações e contribuindo para uma gestão mais eficiente, padronizada e orientada à tomada de decisão.

### 2.3.3 O que o Produto Faz e Não Faz

#### O que o Produto Faz

O produto implementa um agente inteligente de apoio à Gestão de Portfólio de Projetos do Metrô, concebido para centralizar o acesso às informações institucionais e apoiar gestores e equipes por meio de uma interface conversacional integrada ao ecossistema Microsoft.

Ao invés de substituir as plataformas atualmente utilizadas pela organização, a solução atua como uma camada inteligente de interação, permitindo que os usuários acessem informações, consultem documentos e obtenham análises por meio de linguagem natural, reduzindo a necessidade de navegar entre diferentes sistemas corporativos.

#### O que o Produto Não Faz

Embora proponha uma evolução significativa na forma como os usuários interagem com o portfólio de projetos, a solução possui um escopo claramente delimitado para esta etapa de desenvolvimento.

O produto não tem como objetivo:

- Substituir as plataformas corporativas atualmente utilizadas para gerenciamento do portfólio;
- Alterar os processos de governança, metodologias ou fluxos organizacionais adotados pelo PMO;
- Executar decisões de negócio ou substituir a atuação dos gestores responsáveis pelos projetos;
- Disponibilizar informações incompatíveis com as permissões de acesso definidas para cada perfil de usuário;
- Integrar-se, nesta etapa, a sistemas externos que não façam parte do ambiente tecnológico disponibilizado pela organização;
- Realizar implantação definitiva em ambiente produtivo, restringindo-se ao desenvolvimento e validação de uma prova de conceito no contexto acadêmico.

Da mesma forma, funcionalidades que envolvam automações de maior complexidade, ampliação das integrações entre processos corporativos ou expansão do escopo funcional do agente serão implementadas de forma incremental, respeitando o roadmap do produto e as prioridades definidas em conjunto com o PMO.

### 2.3.4 Objetivos Estratégicos e Mensuráveis

O sucesso do produto será acompanhado por indicadores relacionados à eficiência operacional, qualidade das informações disponibilizadas, experiência dos usuários e capacidade de apoiar a gestão do portfólio de projetos.

Os objetivos apresentados representam os resultados estratégicos esperados para a solução e servirão como referência para avaliação de sua contribuição à evolução da plataforma tecnológica do PMO.

#### Eficiência Operacional

- Reduzir em **50%** o tempo médio necessário para localizar informações relacionadas aos projetos do portfólio;
- Reduzir em **40%** o número de consultas manuais realizadas em diferentes plataformas para obtenção de uma mesma informação;
- Diminuir o esforço operacional associado à busca, consolidação e interpretação de documentos institucionais;
- Reduzir o tempo necessário para elaboração de consultas recorrentes realizadas pelo PMO.

#### Qualidade da Informação

- Disponibilizar respostas fundamentadas em fontes oficiais para **100%** das consultas suportadas pelo agente;
- Garantir rastreabilidade das respostas por meio da apresentação das respectivas referências documentais;
- Promover maior padronização das informações disponibilizadas aos diferentes perfis de usuários;
- Reduzir inconsistências decorrentes da consulta manual a documentos distribuídos entre diferentes repositórios.

#### Apoio à Gestão do Portfólio

- Facilitar o acompanhamento do avanço dos projetos por meio de consultas rápidas e contextualizadas;
- Disponibilizar acesso simplificado a cronogramas, TAPs, indicadores, documentos normativos e demais informações estratégicas;
- Disponibilizar respostas compatíveis com o nível de responsabilidade e as permissões de cada perfil de usuário;
- Apoiar gestores na identificação de informações relevantes para acompanhamento dos projetos e tomada de decisão.

#### Experiência dos Usuários

- Diminuir a dependência do conhecimento tácito das equipes para localização de documentos e interpretação de processos;
- Aumentar a autonomia dos usuários na obtenção de informações relacionadas ao portfólio;
- Favorecer maior adoção dos recursos de Inteligência Artificial no contexto da gestão de projetos.

#### Evolução da Plataforma

- Estabelecer uma arquitetura escalável preparada para incorporar novas capacidades inteligentes de forma incremental;
- Facilitar a manutenção da solução utilizando recursos aderentes ao ecossistema Microsoft e acessíveis a equipes com perfil predominantemente funcional;
- Promover uma solução sustentável, preparada para acompanhar a evolução das necessidades da Gestão de Portfólio de Projetos ao longo do tempo.

---

### 2.3.5 Ownership e Accountability Estratégico

O desenvolvimento da solução envolve responsabilidades compartilhadas entre os representantes do Metrô e a equipe responsável pelo projeto, garantindo que as decisões técnicas permaneçam alinhadas às necessidades de negócio e às diretrizes institucionais da organização.

**Representantes do Metrô**

Os representantes da organização exercem o papel de patrocinadores e especialistas de negócio, sendo responsáveis por:

- Disponibilizar informações, documentos e dados necessários ao desenvolvimento da solução;
- Avaliar a aderência das funcionalidades desenvolvidas aos processos organizacionais;

**Equipe do Projeto**

A equipe de desenvolvimento é responsável por:

- Definir a arquitetura da solução;
- Projetar os componentes responsáveis pela interpretação das solicitações e pelo processamento das informações;
- Implementar as funcionalidades previstas para o MVP;
- Conduzir testes técnicos e validações funcionais;
- Documentar decisões arquiteturais, funcionais e técnicas;
- Propor evoluções que agreguem valor ao produto, respeitando as prioridades estabelecidas pelos representantes do Metrô.

---

A visão e os objetivos apresentados consolidam o direcionamento estratégico da solução proposta, evidenciando seu papel como uma camada inteligente de apoio à gestão do portfólio de projetos. Mais do que automatizar consultas ou simplificar o acesso às informações, o produto busca estabelecer uma nova forma de interação entre usuários, processos e conhecimento organizacional, permitindo que gestores e equipes obtenham informações confiáveis, contextualizadas e alinhadas às suas responsabilidades.

Ao preservar o ecossistema tecnológico já adotado pelo Metrô e incorporar recursos de Inteligência Artificial de maneira integrada e escalável, a solução contribui para fortalecer a governança das informações, reduzir esforços operacionais e ampliar a capacidade analítica do PMO. 

---


## 2.4 Personas e Jornada do Usuário

As personas desenvolvidas representam diferentes perfis de usuários envolvidos na gestão do portfólio de projetos do Metrô. Elas ajudam a compreender como a solução proposta impacta rotinas distintas, desde a tomada de decisão estratégica até o acompanhamento operacional e a consolidação de informações. Considerando que o projeto propõe um agente inteligente para consulta, análise e apoio à gestão do portfólio, as personas evidenciam necessidades relacionadas à confiabilidade das respostas, redução de tarefas manuais, acesso rápido a indicadores e melhor organização das informações distribuídas entre documentos e plataformas corporativas.

### 2.4.1 Personas

### 2.4.1.1 Roberto

<div align="center">
  <img src="img/Persona - Roberto.png" alt="Persona Roberto" width="800">
  <p><strong>Figura X</strong> - Persona Roberto.</p>
</div>

Roberto é Diretor de Planejamento e Gestão Estratégica, tem 54 anos e atua em São Paulo. Sua rotina é marcada pelo acompanhamento executivo do portfólio de projetos, com foco em decisões estratégicas, riscos, resultados e alinhamento das iniciativas às prioridades organizacionais do Metrô. Por ocupar uma posição de diretoria, Roberto não dispõe de tempo para analisar documentos extensos ou acompanhar detalhes operacionais de cada projeto. Ele precisa receber informações sintetizadas, confiáveis e apresentadas em linguagem executiva, com destaque para projetos críticos, tendências, decisões pendentes e impactos organizacionais. No dia a dia, utiliza ferramentas como Word, Excel, PowerPoint, Teams e SharePoint, mas prefere soluções integradas ao ambiente corporativo que já utiliza.

### 2.4.1.2 Mariana

<div align="center">
  <img src="img/Persona - Mariana.png" alt="Persona Roberto" width="800">
  <p><strong>Figura X</strong> - Persona Mariana.</p>
</div>

Mariana é Analista Sênior de Gestão de Portfólio no PMO do Metrô, tem 38 anos e atua diretamente na qualidade, atualização e desempenho das informações do portfólio. Seu dia a dia envolve consolidar dados de diferentes projetos, identificar inconsistências, acompanhar indicadores e produzir análises para gestores e diretoria. Por ser organizada, analítica e orientada a processos, Mariana valoriza informações claras, rastreáveis e confiáveis, especialmente porque suas entregas dependem da consistência dos dados disponíveis. Entre seus principais desafios estão o esforço manual para comparar projetos, produzir relatórios e obter respostas rápidas sobre status, riscos, marcos e pendências. Ela possui alta afinidade tecnológica, domina o ecossistema Microsoft e utiliza diariamente Power BI, SharePoint, Excel e PowerPoint, embora dependa de ferramentas intuitivas e confiáveis para reduzir retrabalho.

### 2.4.1.3 Carlos

<div align="center">
  <img src="img/Persona - Carlos.png" alt="Persona Roberto" width="800">
  <p><strong>Figura X</strong> - Persona Carlos.</p>
</div>

Carlos é Gerente de Portfólio de Projeto, tem 44 anos e coordena um conjunto de projetos relacionados à sua área de atuação. Sua rotina envolve acompanhar o desempenho do subportfólio, identificar dependências entre projetos, orientar líderes, priorizar recursos e reportar informações ao PMO. Por atuar em uma posição intermediária entre a operação dos projetos e a gestão corporativa, Carlos precisa transformar informações dispersas em uma visão consolidada que apoie decisões táticas. No dia a dia, enfrenta desafios como dependências difíceis de acompanhar, disputa de recursos e demora para reunir informações sobre desvios e impactos. Ele utiliza SharePoint, Power BI, Excel e ferramentas corporativas, interpreta dashboards com facilidade e possui familiaridade intermediária com automações e agentes de IA, valorizando alertas, informações consolidadas e apoio para priorizar ações.

### 2.4.2 Jornada de Usuário

## 2.5 Modelagem do Fluxo de Negócio
_conteúdo_

## 2.5.1 Cadeia de Valor
_conteúdo_

## 2.5.2 Fluxo de Negócio Proposto (AS-IS e TO-BE)
_conteúdo_

## 2.6 Matriz de Risco do Projeto
_conteúdo_

## 2.7 Ideação

Esta seção consolida o processo de ideação realizado pela equipe durante as etapas de entendimento do negócio, brainstorming e validação inicial com os representantes do Metrô. O objetivo é registrar as funcionalidades identificadas como oportunidades para o produto, independentemente de sua implementação imediata, preservando um histórico das necessidades levantadas e das possibilidades de evolução da solução.

As ideias foram priorizadas considerando dois critérios principais:

- **Importância para o negócio:** potencial de geração de valor para o PMO e para os diferentes perfis de usuários;
- **Viabilidade para o MVP:** possibilidade de implementação dentro do escopo, prazo e recursos disponíveis para a primeira versão da solução.

Essa priorização orienta o roadmap do produto, permitindo que funcionalidades estratégicas sejam incorporadas progressivamente sem comprometer os objetivos centrais do MVP.

---

### 2.7.1 Matriz de Priorização das Features

| Prioridade | Feature | Justificativa |
|---|---|---|
| 🔴 Muito Alta | Consulta de informações dos projetos | Principal necessidade identificada pelo PMO e base de funcionamento do agente. |
| 🔴 Muito Alta | Ingestão de informações dos projetos | Permite estruturar e manter atualizada a base de conhecimento utilizada pelo agente. |
| 🔴 Muito Alta | Autenticação e definição de perfis | Garante controle de acesso e personalização das respostas conforme o usuário. |
| 🔴 Muito Alta | Integração com Microsoft Teams | Interface oficial de utilização do agente dentro da organização. |
| 🔴 Muito Alta | Transcrição de áudio | Facilita consultas durante deslocamentos e reuniões externas. |
| 🔴 Muito Alta | Perfil de linguagem executivo | Adapta automaticamente o nível de profundidade das respostas conforme o cargo do usuário. |
| 🟠 Alta | Diferença de profundidade de pesquisa | Permite consultas rápidas ou análises detalhadas conforme a intenção do usuário. |
| 🟠 Alta | Fluxo de lembretes de atualização dos projetos | Reduz cobranças manuais realizadas pelo PMO aos responsáveis pelos projetos. |
| 🟠 Alta | Relatório anual automático | Automatiza parte da produção documental da diretoria e do PMO. |
| 🟡 Média | Apresentações automáticas por template | Gera apresentações executivas reutilizando modelos institucionais. |
| 🟡 Média | Fluxo de avaliação das respostas | Coleta feedback para evolução contínua do agente e da base de conhecimento. |
| 🟡 Média | Interface personalizada e intuitiva | Fundamental para adoção por usuários sem perfil técnico. |
| 🟢 Evolução | Integração com Power BI | Amplia o acesso a indicadores estratégicos já existentes na organização. |
| 🟢 Evolução | Edição das configurações do agente por menu | Permite manutenção funcional sem necessidade de desenvolvimento técnico. |
| 🟢 Evolução | Fluxo de notificações de riscos | Comunica automaticamente eventos críticos identificados no portfólio. |

### 2.7.2 Descrição das Features Priorizadas

As funcionalidades levantadas durante o processo de ideação foram analisadas considerando sua relevância para os objetivos do produto, o valor potencial para os usuários e a viabilidade de desenvolvimento dentro das diferentes etapas do projeto. A seguir, são apresentadas as descrições das features priorizadas, organizadas de acordo com o nível de prioridade estabelecido na matriz de ideação.

#### 🔴 Muito Alta

**Consulta de informações dos projetos**

Permite que o usuário consulte informações relacionadas aos projetos do portfólio por meio de linguagem natural, incluindo dados de acompanhamento, cronogramas, Termos de Abertura do Projeto (TAP), indicadores e demais informações disponibilizadas pelas fontes integradas à solução. Essa funcionalidade constitui o principal ponto de interação entre o usuário e o agente.

**Ingestão de informações dos projetos**

Responsável por incorporar à base de conhecimento da solução as informações provenientes das fontes utilizadas pelo PMO. A funcionalidade permite estruturar os dados e documentos necessários para que o agente consiga realizar consultas contextualizadas e fornecer respostas fundamentadas nas informações disponibilizadas pela organização.

**Autenticação e definição de perfis**

Permite identificar o usuário e associá-lo ao respectivo perfil de acesso, possibilitando que as informações apresentadas pelo agente sejam compatíveis com suas responsabilidades e permissões. A funcionalidade também fornece a base necessária para diferenciação do nível de detalhamento das respostas conforme o perfil de utilização.

**Integração com Microsoft Teams**

Disponibiliza o agente no ambiente Microsoft Teams, utilizando uma plataforma já presente no ecossistema tecnológico da organização como canal de interação com os usuários. A integração busca facilitar a adoção da solução e incorporá-la ao ambiente de trabalho utilizado pelas equipes.

**Transcrição de áudio**

Permite que solicitações realizadas por meio de áudio sejam convertidas em texto para posterior interpretação pelo agente. A funcionalidade amplia as possibilidades de interação com a solução, permitindo consultas em situações nas quais a entrada textual não seja a forma mais conveniente de utilização.

**Perfil de linguagem executivo**

Permite adaptar a forma de apresentação das respostas conforme o perfil do usuário, priorizando uma comunicação mais objetiva e orientada a informações estratégicas para usuários executivos. Para perfis envolvidos diretamente no acompanhamento dos projetos, o agente poderá apresentar informações com maior nível de detalhamento.

#### 🟠 Alta

**Diferença de profundidade de pesquisa**

Permite que o agente realize consultas com diferentes níveis de profundidade, adequando o esforço de pesquisa e o volume de informações apresentado ao contexto da solicitação. Dessa forma, consultas simples podem receber respostas objetivas, enquanto questões mais complexas podem utilizar uma análise mais aprofundada das fontes disponíveis.

**Fluxo de lembretes de atualização dos projetos**

Possibilita a criação de mecanismos de comunicação para lembrar os responsáveis pela necessidade de atualização das informações dos projetos. A funcionalidade busca apoiar o PMO na manutenção da atualidade da base de informações e reduzir a necessidade de cobranças realizadas manualmente.

**Relatório anual automático**

Permite utilizar as informações consolidadas do portfólio para apoiar a geração automatizada de relatórios anuais. A funcionalidade busca reduzir o esforço associado à consolidação manual das informações e facilitar a preparação de materiais recorrentes utilizados pela gestão.

#### 🟡 Média

**Apresentações automáticas por template**

Permite gerar apresentações a partir de informações disponíveis no portfólio, utilizando modelos previamente definidos pela organização. A funcionalidade busca facilitar a preparação de materiais executivos e reduzir atividades repetitivas relacionadas à organização das informações em apresentações.

**Fluxo de avaliação das respostas**

Disponibiliza mecanismos para que os usuários avaliem as respostas fornecidas pelo agente. Os registros obtidos podem ser utilizados para identificar problemas recorrentes, avaliar a qualidade das interações e orientar futuras melhorias da solução.

**Interface personalizada e intuitiva**

Busca proporcionar uma experiência de interação simples, clara e adequada aos diferentes perfis de usuários. A interface deve reduzir barreiras de utilização e permitir que usuários com diferentes níveis de familiaridade tecnológica consigam interagir com o agente de maneira natural.

#### 🟢 Evolução

**Integração com Power BI**

Possibilita a utilização de informações e indicadores disponibilizados no Power BI como parte da experiência de consulta do agente. A funcionalidade amplia o conjunto de fontes utilizadas pela solução e pode facilitar o acesso conversacional a indicadores estratégicos já existentes no ambiente corporativo.

**Edição das configurações do agente por menu**

Permite que configurações relacionadas ao comportamento e à utilização do agente sejam ajustadas por meio de uma interface funcional, reduzindo a necessidade de alterações diretamente na implementação técnica. Essa capacidade favorece a manutenção e a evolução da solução por usuários responsáveis pela administração do produto.

**Fluxo de notificações de riscos**

Permite identificar situações relacionadas a riscos dos projetos e utilizar essas informações para apoiar o envio de notificações aos responsáveis. A funcionalidade amplia o caráter proativo do agente, passando de um modelo baseado exclusivamente em consultas realizadas pelo usuário para uma experiência capaz de comunicar informações relevantes de forma contextualizada.



O processo de ideação resultou em um conjunto de funcionalidades que contempla tanto as necessidades centrais identificadas para a primeira versão do produto quanto oportunidades de evolução para versões posteriores. A priorização realizada não representa o descarte das funcionalidades classificadas em níveis inferiores, mas estabelece uma sequência de implementação baseada na importância, no valor esperado e na viabilidade de cada iniciativa.

Dessa forma, esta estabelece não apenas um conjunto de funcionalidades possíveis, mas também uma visão evolutiva para o produto, permitindo que novas capacidades sejam incorporadas progressivamente sem perder de vista o objetivo central da solução: **utilizar Inteligência Artificial para tornar o acesso às informações e o acompanhamento do portfólio de projetos mais simples, contextualizado, eficiente e alinhado às necessidades dos diferentes usuários do Metrô.**

---

## 2.8 Canvas do Projeto
_conteúdo_

# 3. Requisitos do Projeto
_conteúdo_

## 3.1 Requisitos Funcionais

Os requisitos funcionais definem as funcionalidades que deverão ser contempladas pela prova de conceito desenvolvida no MVP. Sua definição considera o escopo estabelecido para o projeto e as oportunidades levantadas durante o processo de ideação apresentado na Seção 2.7, priorizando as funcionalidades diretamente relacionadas ao pipeline de Processamento de Linguagem Natural (PLN).

O núcleo do MVP consiste em um pipeline de PLN capaz de receber comandos em linguagem natural, interpretar as solicitações dos usuários, identificar suas intenções e classificá-las em categorias como consulta, transação e alerta. A partir dessa classificação, a solução deve processar informações de documentos de projetos e retornar respostas estruturadas que apoiem atividades operacionais, análises e a obtenção de informações para tomada de decisão.

Por se tratar de uma prova de conceito em contexto acadêmico, o funcionamento do MVP será validado sobre dados sintéticos. Integrações com dados reais do portfólio do Metrô de São Paulo e demais funcionalidades corporativas identificadas durante a ideação são consideradas possibilidades de evolução da solução e não constituem requisitos obrigatórios para a validação do núcleo funcional do MVP.

| ID | Requisito Funcional | Feature relacionada | Prioridade | Status |
| :---: | --- | --- | :---: | :---: |
| RF01 | O sistema deve receber comandos textuais em linguagem natural relacionados à gestão de projetos e portfólio. | Consulta de informações dos projetos | Muito Alta | Não iniciado |
| RF02 | O sistema deve processar semanticamente os comandos recebidos e identificar a intenção expressa pelo usuário. | Consulta de informações dos projetos | Muito Alta | Não iniciado |
| RF03 | O sistema deve classificar as solicitações recebidas de acordo com as categorias de intenção previstas pelo MVP, incluindo consulta, transação e alerta. | Consulta de informações dos projetos | Muito Alta | Não iniciado |
| RF04 | O sistema deve recuperar informações relevantes dos documentos e dados sintéticos disponibilizados ao pipeline de acordo com a solicitação realizada. | Ingestão de informações dos projetos | Muito Alta | Não iniciado |
| RF05 | O sistema deve responder a consultas sobre as informações disponíveis nos documentos de projetos utilizados na prova de conceito. | Consulta de informações dos projetos | Muito Alta | Não iniciado |
| RF06 | O sistema deve realizar análises e comparações entre informações de diferentes projetos quando solicitado pelo usuário. | Consulta de informações dos projetos | Muito Alta | Não iniciado |
| RF07 | O sistema deve executar ou simular ações compatíveis com a intenção classificada, incluindo operações de consulta, transação e alerta previstas para validação do pipeline. | Ingestão de informações dos projetos | Muito Alta | Não iniciado |
| RF08 | O sistema deve gerar respostas estruturadas e fundamentadas nas informações disponíveis nos dados sintéticos, indicando quando não houver informações suficientes para atender à solicitação. | Consulta de informações dos projetos | Muito Alta | Não iniciado |

### 3.1.1 User Stories dos Requisitos Funcionais

As User Stories apresentadas nesta subseção estão diretamente integradas aos respectivos requisitos funcionais da Seção 3.1. Cada história segue a estrutura "Como [usuário], quero [necessidade], para [valor]", estabelecendo a necessidade que fundamenta o requisito e o benefício esperado pelo usuário.

Os critérios de aceitação estabelecem condições verificáveis para validação das funcionalidades dentro dos limites da prova de conceito, considerando a utilização de dados sintéticos e o desenvolvimento do pipeline de PLN como núcleo do MVP.

#### RF01 — Entrada de comandos em linguagem natural

**User Story — US01**

Como usuário da solução, quero realizar solicitações utilizando linguagem natural, para interagir com as informações dos projetos sem precisar utilizar comandos técnicos ou conhecer a estrutura dos dados.

**Critérios de aceitação:**
- O sistema deve aceitar solicitações textuais em linguagem natural.
- O usuário não deve precisar utilizar uma sintaxe técnica específica.
- A solicitação recebida deve ser encaminhada ao pipeline de PLN para processamento.

**Feature relacionada:** Consulta de informações dos projetos.

---

#### RF02 — Identificação de intenção

**User Story — US02**

Como usuário da solução, quero que o sistema compreenda a intenção da minha solicitação, para que ela seja processada de acordo com a ação que desejo realizar.

**Critérios de aceitação:**
- O sistema deve processar semanticamente a solicitação recebida.
- O sistema deve identificar a intenção presente no comando do usuário.
- A intenção identificada deve ser utilizada nas etapas seguintes do pipeline.

**Feature relacionada:** Consulta de informações dos projetos.

---

#### RF03 — Classificação das solicitações

**User Story — US03**

Como usuário da solução, quero que minha solicitação seja classificada de acordo com sua finalidade, para que o sistema utilize o fluxo de processamento adequado.

**Critérios de aceitação:**
- O sistema deve classificar as solicitações conforme as categorias previstas no MVP.
- A classificação deve contemplar, no mínimo, as categorias de consulta, transação e alerta previstas para validação.
- A categoria identificada deve determinar o fluxo de processamento da solicitação.

**Feature relacionada:** Consulta de informações dos projetos.

---

#### RF04 — Recuperação de informações

**User Story — US04**

Como usuário da solução, quero que o sistema localize informações relevantes nos documentos de projetos, para obter respostas relacionadas ao contexto da minha solicitação.

**Critérios de aceitação:**
- O sistema deve consultar os documentos e dados sintéticos disponibilizados para a prova de conceito.
- O sistema deve recuperar informações relacionadas à solicitação realizada.
- As informações recuperadas devem ser utilizadas como contexto para o processamento da resposta.

**Feature relacionada:** Ingestão de informações dos projetos.

---

#### RF05 — Consulta de informações dos projetos

**User Story — US05**

Como usuário da solução, quero consultar informações sobre os projetos utilizando linguagem natural, para acessar rapidamente os dados necessários para acompanhamento e análise.

**Critérios de aceitação:**
- O sistema deve responder a consultas relacionadas às informações disponíveis nos dados sintéticos.
- A resposta deve considerar o projeto ou contexto solicitado pelo usuário.
- A resposta deve utilizar as informações recuperadas pelo pipeline.
- Quando a informação solicitada não estiver disponível, o sistema deve indicar essa limitação.

**Feature relacionada:** Consulta de informações dos projetos.

---

#### RF06 — Análise e comparação de projetos

**User Story — US06**

Como gestor do portfólio, quero solicitar análises e comparações entre projetos, para identificar diferenças, semelhanças e informações relevantes que apoiem a tomada de decisão.

**Critérios de aceitação:**
- O sistema deve identificar quando a solicitação exigir análise ou comparação.
- O sistema deve permitir comparar informações disponíveis de dois ou mais projetos.
- A comparação deve considerar os critérios informados pelo usuário quando aplicável.
- O resultado deve ser fundamentado nos dados sintéticos disponíveis.

**Feature relacionada:** Consulta de informações dos projetos.

---

#### RF07 — Tratamento das intenções classificadas

**User Story — US07**

Como usuário da solução, quero que o sistema direcione minha solicitação para o fluxo correspondente à intenção identificada, para obter um comportamento adequado ao tipo de operação solicitada.

**Critérios de aceitação:**
- Solicitações classificadas como consulta devem ser encaminhadas ao fluxo de recuperação de informações.
- Solicitações classificadas como transação devem ser encaminhadas ao fluxo correspondente previsto na prova de conceito.
- Solicitações classificadas como alerta devem ser encaminhadas ao fluxo correspondente previsto na prova de conceito.
- O comportamento de cada fluxo deve poder ser demonstrado utilizando dados sintéticos.

**Feature relacionada:** Ingestão de informações dos projetos.

---

#### RF08 — Geração de respostas estruturadas e fundamentadas

**User Story — US08**

Como usuário da solução, quero receber respostas estruturadas e fundamentadas nas informações disponíveis, para compreender os resultados apresentados pelo agente e utilizá-los com maior confiança.

**Critérios de aceitação:**
- A resposta deve considerar as informações recuperadas dos dados sintéticos disponibilizados ao pipeline.
- O sistema não deve apresentar como fato informações que não estejam sustentadas pelos dados disponíveis.
- Quando não houver informações suficientes, o sistema deve indicar a limitação ao usuário.
- A resposta deve ser estruturada de forma coerente com a intenção identificada.
- Em solicitações analíticas, o sistema deve diferenciar informações recuperadas de interpretações produzidas pelo agente.

**Feature relacionada:** Consulta de informações dos projetos.

## 3.2 Requisitos Não Funcionais (RNFs)
_conteúdo_

## 3.3 Correlação RFs e RNFs
_conteúdo_

## 3.4 Casos de Uso
_conteúdo_

## 3.5 Casos de Uso x Requisitos Funcionais
_conteúdo_

# 4. Modelagem de Dados
_conteúdo_

## 4.1 Especificação da Base de Dados para Modelo de Recomendação
_conteúdo_
Obs.: Insira aqui informações sobre a construção do artefato da Sprint 1. 

## 4.2 Modelo Conceitual de Dados
_conteúdo_

## 4.3 Modelo Lógico de Dados
_conteúdo_

## 4.4 Modelo Físico de Dados
_conteúdo_

**Nota:** Insira uma explicação e direcionamento para o readme.md da pasta database.

# 5. Solução Técnica (Design)
_conteúdo_

## 5.1 Diagrama de Classes
_conteúdo_

## 5.2 Diagrama de Componentes da UML
_conteúdo_

## 5.3 Diagramas de Sequência da UML
_conteúdo_

# 6. Mapeamento Técnico de Infraestrutura e Implantação
_conteúdo_

## 6.1 Diagrama de Implantação da UML
_conteúdo_

## 6.2 Justificativa das Escolhas de Implantação
_conteúdo_

## 6.3 Considerações sobre Desempenho e Segurança
_conteúdo_

# 7. Projeto Visual da Solução
_conteúdo_

## 7.1 Desenvolvimento de Wireframes
_conteúdo_

## 7.2 Desenvolvimento de Mockups
_conteúdo_

## 7.3 Guia Visual
_conteúdo_

# 8. Desenvolvimento do Projeto
_conteúdo_

## 8.1 Arquitetura de Codificação e Estrutura de Diretórios
_conteúdo_

## 8.2 Modelo de Recomendação
_conteúdo_

## 8.3 Desenvolvimento de Features
_conteúdo_

**Nota:** Insira uma explicação de entregas em cada Sprint.

## 8.3.1 Sprint 3
_conteúdo_

## 8.3.2 Sprint 4
_conteúdo_

## 8.3.3 Sprint 5
_conteúdo_

## 8.4 Testes Unitários e de Integração
_conteúdo_
Obs.: Insira informações sobre estratégias para realização dos testes

## 8.5 Documentações automáticas
_conteúdo_
Obs.: Insira informações sobre quais frameworks foram usados e como acessar.

# 9. Planejamento e Execução de Testes
_conteúdo_

## 9.1 Testes Funcionais
_conteúdo_

## 9.1.1 Planejamento
_conteúdo_

## 9.1.2 Resultados
_conteúdo_

## 9.2 Testes de RNFs
_conteúdo_

## 9.2.1 Planejamento
_conteúdo_

## 9.2.2 Resultados
_conteúdo_

## 9.3 Testes de Usabilidade
_conteúdo_

## 9.3.1 Planejamento
_conteúdo_

## 9.3.2 Resultados
_conteúdo_

# 10. Procedimentos de Implantação
_conteúdo_

## 10.1 Implantação e Configuração do Banco de Dados
_conteúdo_

## 10.2 Implantação do Protótipo para uso por equipe de desenvolvimento
_conteúdo_

# Referências
_conteúdo_

