<table>
  <tr>
    <td><a href="https://www.metro.sp.gov.br/"><img src="img/logo-metro.png" alt="Companhia do Metropolitano de Sao Paulo - Metro" border="0" width="180"></a></td>
    <td><a href="https://www.inteli.edu.br/"><img src="img/logo-Inteli.png" alt="Inteli - Instituto de Tecnologia e Lideranca" border="0" width="180"></a></td>
  </tr>
</table>

# Agente de IA para o Portfólio de Projetos do Metrô

## Nome do grupo: Oneshot

## Integrantes:

- <a href="https://www.linkedin.com/in/ntsfelipe/">Felipe Neves</a>
- <a href="https://www.linkedin.com/in/henrique-rodrigues-diniz-b7b011319/">Henrique Diniz</a>
- <a href="https://www.linkedin.com/in/jaimeandradedealmeida/">Jaime Almeida</a>
- <a href="https://www.linkedin.com/in/leonardoramosvieira">Leonardo Ramos</a>
- <a href="https://www.linkedin.com/in/pedro-uchoaa/">Pedro Uchoa</a>
- <a href="https://www.linkedin.com/in/wendel-feitosa-975bb1346/">Wendel Feitosa</a>

# Sumário

- [1. Introdução](#1-introdução)
  - [1.1 Termos e Abreviações](#11-termos-e-abreviações)
  - [1.2 Objetivo do Documento](#12-objetivo-do-documento)
- [2. Entendimento do Projeto e do Negócio](#2-entendimento-do-projeto-e-do-negócio)
  - [2.1 Contexto da Indústria do Parceiro](#21-contexto-da-indústria-do-parceiro)
  - [2.2 Problema](#22-problema)
  - [2.3 Análise SWOT](#23-análise-swot)
    - [2.3.1 Forças](#231-forças)
    - [2.3.2 Fraquezas](#232-fraquezas)
    - [2.3.3 Oportunidades](#233-oportunidades)
    - [2.3.4 Ameaças](#234-ameaças)
  - [2.4 Visão do Projeto e do Produto](#24-visão-do-projeto-e-do-produto)
    - [2.4.1 Visão do Produto](#241-visão-do-produto)
    - [2.4.2 Proposta de Valor](#242-proposta-de-valor)
    - [2.4.3 O que o Produto Faz e Não Faz](#243-o-que-o-produto-faz-e-não-faz)
    - [2.4.4 Objetivos Estratégicos e Mensuráveis](#244-objetivos-estratégicos-e-mensuráveis)
    - [2.4.5 Ownership e Accountability Estratégico](#245-ownership-e-accountability-estratégico)
  - [2.5 Personas e Jornada do Usuário](#25-personas-e-jornada-do-usuário)
    - [2.5.1 Personas](#251-personas)
      - [2.5.1.1 Roberto](#2511-roberto)
      - [2.5.1.2 Mariana](#2512-mariana)
      - [2.5.1.3 Carlos](#2513-carlos)
    - [2.5.2 Jornadas do Usuário](#252-jornadas-do-usuário)
      - [2.5.2.1 Mapa de jornada - Roberto](#2521-mapa-de-jornada---roberto)
      - [2.5.2.2 Mapa de jornada - Mariana](#2522-mapa-de-jornada---mariana)
      - [2.5.2.3 Mapa de jornada - Carlos](#2523-mapa-de-jornada---carlos)
  - [2.6 Modelagem do Fluxo de Negócio](#26-modelagem-do-fluxo-de-negócio)
    - [2.6.1 Cadeia de Valor](#261-cadeia-de-valor)
    - [2.6.2 Fluxo de Negócio Proposto (AS-IS e TO-BE)](#262-fluxo-de-negócio-proposto-as-is-e-to-be)
  - [2.7 Matriz de Risco do Projeto](#27-matriz-de-risco-do-projeto)
    - [2.7.1 Critérios de Avaliação](#271-critérios-de-avaliação)
    - [2.7.2 Registro dos Riscos e Oportunidades](#272-registro-dos-riscos-e-oportunidades)
    - [2.7.3 Ações de Tratamento](#273-ações-de-tratamento)
    - [2.7.4 Oportunidades](#274-oportunidades)
    - [2.7.5 Matriz Probabilidade × Impacto](#275-matriz-probabilidade-impacto)
    - [2.7.6 Análise dos Três Itens Mais Críticos](#276-análise-dos-três-itens-mais-críticos)
    - [2.7.7 Acompanhamento da Matriz](#277-acompanhamento-da-matriz)
  - [2.8 Ideação](#28-ideação)
    - [2.8.1 Descrição das Features Priorizadas](#281-descrição-das-features-priorizadas)
  - [2.9 Canvas de Proposta de Valor](#29-canvas-de-proposta-de-valor)
  - [2.10 Business Drivers](#210-business-drivers)
    - [2.10.1 Business Drivers do Projeto](#2101-business-drivers-do-projeto)
    - [2.10.2 Indicadores Computacionais](#2102-indicadores-computacionais)
    - [2.10.3 Fluxos de Negócio Impactados](#2103-fluxos-de-negócio-impactados)
      - [2.10.3.1 Fluxo 1 — Consulta de Informações de Projetos](#21031-fluxo-1-consulta-de-informações-de-projetos)
      - [2.10.3.2 Fluxo 2 — Análise e Comparação entre Projetos](#21032-fluxo-2-análise-e-comparação-entre-projetos)
    - [2.10.4 Relação entre Business Drivers, Fluxos e Indicadores](#2104-relação-entre-business-drivers-fluxos-e-indicadores)
    - [2.10.5 Impacto Esperado no Negócio](#2105-impacto-esperado-no-negócio)
- [3. Requisitos do Projeto](#3-requisitos-do-projeto)
  - [3.1 Requisitos Funcionais](#31-requisitos-funcionais)
    - [3.1.1 User Stories dos Requisitos Funcionais](#311-user-stories-dos-requisitos-funcionais)
    - [3.1.2 Modelagem Estática Inicial dos Requisitos Funcionais](#312-modelagem-estática-inicial-dos-requisitos-funcionais)
    - [3.1.3 Modelagem Dinâmica Inicial dos Requisitos Funcionais](#313-modelagem-dinâmica-inicial-dos-requisitos-funcionais)
    - [3.1.3.1 Cenário 1 — Consulta de informação de um projeto](#3131-cenário-1-consulta-de-informação-de-um-projeto)
    - [3.1.3.2 Cenário 2 — Análise e comparação entre projetos](#3132-cenário-2-análise-e-comparação-entre-projetos)
    - [3.1.3.3 Cenário 3 — Roteamento híbrido e sugestão proativa](#3133-cenário-3-roteamento-híbrido-e-sugestão-proativa)
    - [3.1.4 Rastreabilidade entre User Stories e Modelagem UML](#314-rastreabilidade-entre-user-stories-e-modelagem-uml)
    - [3.1.5 Escopo dos requisitos funcionais](#315-escopo-dos-requisitos-funcionais)
  - [3.2 Requisitos Não Funcionais (RNFs)](#32-requisitos-não-funcionais-rnfs)
    - [3.2.1 RNFs descritos como histórias de usuário](#321-rnfs-descritos-como-histórias-de-usuário)
    - [3.2.2 Origem das metas e registro de revisões](#322-origem-das-metas-e-registro-de-revisões)
  - [3.3 Visão Inicial sobre a Solução Técnica de Engenharia](#33-visão-inicial-sobre-a-solução-técnica-de-engenharia)
    - [3.3.1 Organização em camadas](#331-organização-em-camadas)
    - [3.3.2 Diagrama de Componentes (UML)](#332-diagrama-de-componentes-uml)
    - [3.3.3 Fluxo principal entre os componentes](#333-fluxo-principal-entre-os-componentes)
    - [3.3.4 Decisões refletidas no esboço](#334-decisões-refletidas-no-esboço)
  - [3.4 Visão Inicial sobre Tecnologias e Ferramentas](#34-visão-inicial-sobre-tecnologias-e-ferramentas)
    - [3.4.1 Critérios de seleção](#341-critérios-de-seleção)
    - [3.4.2 Listagem organizada das tecnologias e ferramentas](#342-listagem-organizada-das-tecnologias-e-ferramentas)
      - [3.4.2.1 Camada de interface humano-computador](#3421-camada-de-interface-humano-computador)
      - [3.4.2.2 Camada de lógica de negócio: núcleo de PLN (Pilar 1)](#3422-camada-de-lógica-de-negócio-núcleo-de-pln-pilar-1)
      - [3.4.2.3 Camada de lógica de negócio: recursos de IA generativa (Pilar 2)](#3423-camada-de-lógica-de-negócio-recursos-de-ia-generativa-pilar-2)
      - [3.4.2.4 Camada de acesso a dados e serviços](#3424-camada-de-acesso-a-dados-e-serviços)
      - [3.4.2.5 Camada transversal: identidade, permissões e rastreabilidade](#3425-camada-transversal-identidade-permissões-e-rastreabilidade)
      - [3.4.2.6 Ferramentas de engenharia, gestão e qualidade](#3426-ferramentas-de-engenharia-gestão-e-qualidade)
    - [3.4.3 Alternativas avaliadas e não adotadas](#343-alternativas-avaliadas-e-não-adotadas)
    - [3.4.4 Riscos e dependências tecnológicas](#344-riscos-e-dependências-tecnológicas)
    - [3.4.5 Fora do escopo do MVP e evolução da solução](#345-fora-do-escopo-do-mvp-e-evolução-da-solução)
    - [3.4.6 Plataforma de execução, confiabilidade e escalabilidade](#346-plataforma-de-execução-confiabilidade-e-escalabilidade)
    - [3.4.7 Referências](#347-referências)
  - [3.5 Correlação RFs e RNFs](#35-correlação-rfs-e-rnfs)
  - [3.6 Casos de Uso](#36-casos-de-uso)
  - [3.7 Casos de Uso x Requisitos Funcionais](#37-casos-de-uso-x-requisitos-funcionais)
  - [3.8 Prototipação Exploratória](#38-prototipação-exploratória)
    - [3.8.1 Questão de Projeto](#381-questão-de-projeto)
    - [3.8.2 Alternativas e Formatos de Prototipação](#382-alternativas-e-formatos-de-prototipação)
      - [3.8.2.1 Protótipo 1 — Agente Reativo sob Demanda](#3821-protótipo-1-agente-reativo-sob-demanda)
      - [3.8.2.2 Protótipo 2 — Agente Proativo e Orientado à Jornada](#3822-protótipo-2-agente-proativo-e-orientado-à-jornada)
    - [3.8.3 Construção e Execução dos Protótipos](#383-construção-e-execução-dos-protótipos)
      - [3.8.3.1 Protótipo 1 — Agente Reativo sob Demanda](#3831-protótipo-1-agente-reativo-sob-demanda)
      - [3.8.3.2 Protótipo 2 — Agente Proativo e Orientado à Jornada](#3832-protótipo-2-agente-proativo-e-orientado-à-jornada)
    - [3.8.4 Comparação das Alternativas](#384-comparação-das-alternativas)
    - [3.8.5 Limites da Exploração](#385-limites-da-exploração)
    - [3.8.6 Insumos para a Equipe](#386-insumos-para-a-equipe)
      - [3.8.6.1 Inventário de Decisões em Aberto](#3861-inventário-de-decisões-em-aberto)
      - [3.8.6.2 Repertório de Situações](#3862-repertório-de-situações)
- [4. Modelagem de Dados](#4-modelagem-de-dados)
  - [4.1 Especificação da Base de Dados](#41-especificação-da-base-de-dados)
  - [4.2 Modelo Conceitual de Dados](#42-modelo-conceitual-de-dados)
  - [4.3 Modelo Lógico de Dados](#43-modelo-lógico-de-dados)
  - [4.4 Modelo Físico de Dados](#44-modelo-físico-de-dados)
- [5. Solução Técnica (Design)](#5-solução-técnica-design)
  - [5.1 Diagrama de Classes](#51-diagrama-de-classes)
    - [5.1.1 Modelo consolidado](#511-modelo-consolidado)
    - [5.1.2 O que mudou em relação à Seção 3.1.2](#512-o-que-mudou-em-relação-à-seção-312)
    - [5.1.3 Decisões refletidas no diagrama](#513-decisões-refletidas-no-diagrama)
    - [5.1.4 Correspondência com o modelo de dados](#514-correspondência-com-o-modelo-de-dados)
  - [5.2 Diagrama de Componentes da UML](#52-diagrama-de-componentes-da-uml)
    - [5.2.1 Componentes e responsabilidades](#521-componentes-e-responsabilidades)
    - [5.2.2 Fluxo de interação entre os componentes](#522-fluxo-de-interação-entre-os-componentes)
    - [5.2.3 Relação entre o catálogo de intenções e os fluxos da solução](#523-relação-entre-o-catálogo-de-intenções-e-os-fluxos-da-solução)
    - [5.2.4 Decisões arquiteturais refletidas no diagrama](#524-decisões-arquiteturais-refletidas-no-diagrama)
    - [5.2.5 Limite de representação](#525-limite-de-representação)
  - [5.3 Diagramas de Sequência da UML](#53-diagramas-de-sequência-da-uml)
    - [5.3.1 Consulta documental via RAG](#531-consulta-documental-via-rag)
    - [5.3.2 Análise e comparação entre projetos via RAG](#532-análise-e-comparação-entre-projetos-via-rag)
    - [5.3.3 Direcionamento para workflow funcional web](#533-direcionamento-para-workflow-funcional-web)
    - [5.3.4 Entrada por voz com Speech-to-Text](#534-entrada-por-voz-com-speech-to-text)
    - [5.3.5 Considerações sobre os cenários](#535-considerações-sobre-os-cenários)
- [6. Mapeamento técnico de infraestrutura e implantação](#6-mapeamento-técnico-de-infraestrutura-e-implantação)
  - [6.1 Diagrama de implantação da UML](#61-diagrama-de-implantação-da-uml)
  - [6.2 Justificativa das escolhas de implantação](#62-justificativa-das-escolhas-de-implantação)
    - [6.2.1 Estratégia de hospedagem](#621-estratégia-de-hospedagem)
    - [6.2.2 Banco de dados e armazenamento](#622-banco-de-dados-e-armazenamento)
    - [6.2.3 Modelo de PLN e artefatos](#623-modelo-de-pln-e-artefatos)
    - [6.2.4 Interface, autenticação e integração](#624-interface-autenticação-e-integração)
    - [6.2.5 Estratégia de fallback](#625-estratégia-de-fallback)
    - [6.2.6 Processo reprodutível proposto](#626-processo-reprodutível-proposto)
    - [6.2.7 Variáveis de ambiente previstas](#627-variáveis-de-ambiente-previstas)
    - [6.2.8 Comandos de execução local](#628-comandos-de-execução-local)
  - [6.3 Considerações sobre desempenho e segurança](#63-considerações-sobre-desempenho-e-segurança)
    - [6.3.1 Desempenho](#631-desempenho)
    - [6.3.2 Segurança](#632-segurança)
    - [6.3.3 Auditoria](#633-auditoria)
    - [6.3.4 Limitações e pendências de provisionamento](#634-limitações-e-pendências-de-provisionamento)
    - [6.3.5 Checklist de conclusão da implantação](#635-checklist-de-conclusão-da-implantação)
- [7. Projeto Visual da Solução](#7-projeto-visual-da-solução)
  - [7.1 Desenvolvimento de Wireframes](#71-desenvolvimento-de-wireframes)
  - [7.2 Desenvolvimento de Mockups](#72-desenvolvimento-de-mockups)
  - [7.3 Guia Visual](#73-guia-visual)
- [8. Desenvolvimento do Projeto](#8-desenvolvimento-do-projeto)
  - [8.1 Arquitetura de Codificação e Estrutura de Diretórios](#81-arquitetura-de-codificação-e-estrutura-de-diretórios)
  - [8.2 Modelo de Recomendação](#82-modelo-de-recomendação)
  - [8.3 Planejamento estratégico de desenvolvimento](#83-planejamento-estratégico-de-desenvolvimento)
    - [8.3.1 Sprint 3](#831-sprint-3)
    - [8.3.2 Sprint 4](#832-sprint-4)
    - [8.3.3 Sprint 5](#833-sprint-5)
  - [8.4 Testes Unitários e de Integração](#84-testes-unitários-e-de-integração)
  - [8.5 Documentação de front-end e back-end](#85-documentação-de-front-end-e-back-end)
    - [8.5.1 Escopo e estado da implementação](#851-escopo-e-estado-da-implementação)
    - [8.5.2 Arquitetura executável](#852-arquitetura-executável)
    - [8.5.3 Documentação automática da API](#853-documentação-automática-da-api)
    - [8.5.4 APIs consumidas pelo front-end](#854-apis-consumidas-pelo-front-end)
    - [8.5.5 Integrações e limites operacionais](#855-integrações-e-limites-operacionais)
    - [8.5.6 Banco de dados: modelo e integrações operacionais](#856-banco-de-dados-modelo-e-integrações-operacionais)
    - [8.5.7 Front-end: componentes e comportamento](#857-front-end-componentes-e-comportamento)
    - [8.5.8 Back-end: ciclo de processamento](#858-back-end-ciclo-de-processamento)
    - [8.5.9 Execução e verificação reproduzíveis](#859-execução-e-verificação-reproduzíveis)
    - [8.5.10 Geração rastreável de relatório executivo](#8510-geração-rastreável-de-relatório-executivo)
    - [8.5.11 Alerta autônomo de prazo](#8511-alerta-autônomo-de-prazo)
  - [8.6 Requisitos das APIs de voz (STT/TTS)](#86-requisitos-das-apis-de-voz-stttts)
    - [8.6.1 Objetivo e delimitação](#861-objetivo-e-delimitação)
    - [8.6.2 Entradas, saídas e formatos](#862-entradas-saídas-e-formatos)
    - [8.6.3 O que é buscado nas APIs](#863-o-que-é-buscado-nas-apis)
    - [8.6.4 Restrições e condições de validação](#864-restrições-e-condições-de-validação)
  - [8.7 API de recebimento de áudio](#87-api-de-recebimento-de-áudio)
    - [8.7.1 Posição no fluxo](#871-posição-no-fluxo)
    - [8.7.2 Endpoint](#872-endpoint)
    - [8.7.3 Formatos aceitos e limites](#873-formatos-aceitos-e-limites)
    - [8.7.4 Requisição](#874-requisição)
    - [8.7.5 Resposta de sucesso](#875-resposta-de-sucesso)
    - [8.7.6 Códigos de resposta e tratamento de erro](#876-códigos-de-resposta-e-tratamento-de-erro)
    - [8.7.7 Situação de implementação](#877-situação-de-implementação)
  - [8.8 Speech-to-Text](#88-speech-to-text)
    - [8.8.1 Introdução](#881-introdução)
    - [8.8.2 Benchmark das APIs](#882-benchmark-das-apis)
    - [8.8.3 API escolhida: Azure AI Speech](#883-api-escolhida-azure-ai-speech)
  - [8.9 Text-to-Speech](#89-text-to-speech)
    - [8.9.1 Introdução](#891-introdução)
    - [8.9.2 Benchmark das APIs](#892-benchmark-das-apis)
    - [8.9.3 API escolhida: Azure AI Speech](#893-api-escolhida-azure-ai-speech)
    - [8.9.4 Referências](#894-referências)
  - [8.10 Escolha de algoritmo PLN](#810-escolha-de-algoritmo-pln)
    - [8.10.1 Objetivo e protocolo de avaliação](#8101-objetivo-e-protocolo-de-avaliação)
    - [8.10.2 Benchmark e decisão](#8102-benchmark-e-decisão)
    - [8.10.3 Configuração e resultados atuais](#8103-configuração-e-resultados-atuais)
    - [8.10.4 Bibliotecas, configuração e exemplos de código](#8104-bibliotecas-configuração-e-exemplos-de-código)
    - [8.10.5 Limitações e próximos passos](#8105-limitações-e-próximos-passos)
    - [8.10.6 Revisão da decisão após a implementação](#8106-revisão-da-decisão-após-a-implementação)
  - [8.11 Implementação do núcleo de PLN](#811-implementação-do-núcleo-de-pln)
    - [8.11.1 Estrutura do módulo e responsabilidades](#8111-estrutura-do-módulo-e-responsabilidades)
    - [8.11.2 Bibliotecas, frameworks e dependências de execução](#8112-bibliotecas-frameworks-e-dependências-de-execução)
    - [8.11.3 Pré-processamento e extração de entidades](#8113-pré-processamento-e-extração-de-entidades)
    - [8.11.4 Carregamento do artefato treinado](#8114-carregamento-do-artefato-treinado)
    - [8.11.5 Inferência e roteamento por limiares](#8115-inferência-e-roteamento-por-limiares)
    - [8.11.6 Exemplos de execução: casos de sucesso e de falha](#8116-exemplos-de-execução-casos-de-sucesso-e-de-falha)
    - [8.11.7 Testes automatizados](#8117-testes-automatizados)
    - [8.11.8 Desempenho medido](#8118-desempenho-medido)
    - [8.11.9 Situação da integração](#8119-situação-da-integração)
  - [8.12 Histórico da integração da interface web](#812-histórico-da-integração-da-interface-web)
- [9. Planejamento e Execução de Testes](#9-planejamento-e-execução-de-testes)
  - [9.1 Testes Funcionais](#91-testes-funcionais)
    - [9.1.1 Estratégia e preparação](#911-estratégia-e-preparação)
    - [9.1.2 Matriz de rastreabilidade](#912-matriz-de-rastreabilidade)
    - [9.1.3 Casos de teste](#913-casos-de-teste)
    - [9.1.4 Abrangência e limitações](#914-abrangência-e-limitações)
    - [9.1.5 Execução e consolidação dos testes funcionais](#915-execução-e-consolidação-dos-testes-funcionais)
  - [9.2 Testes de RNFs](#92-testes-de-rnfs)
    - [9.2.1 Planejamento](#921-planejamento)
    - [9.2.2 Matriz de rastreabilidade e critérios](#922-matriz-de-rastreabilidade-e-critérios)
    - [9.2.3 Casos positivos e negativos](#923-casos-positivos-e-negativos)
    - [9.2.4 Teste obrigatório de desempenho do RNF05](#924-teste-obrigatório-de-desempenho-do-rnf05)
    - [9.2.5 Instruções gerais de execução e evidências](#925-instruções-gerais-de-execução-e-evidências)
    - [9.2.6 Abrangência e limitações](#926-abrangência-e-limitações)
    - [9.2.7 Resultados](#927-resultados)
  - [9.3 Testes de Usabilidade](#93-testes-de-usabilidade)
    - [9.3.1 Planejamento dos testes de usabilidade](#931-planejamento-dos-testes-de-usabilidade)
    - [9.3.2 Resultados](#932-resultados)
  - [9.4 Testes de Integração](#94-testes-de-integração)
    - [9.4.1 Planejamento](#941-planejamento)
    - [9.4.2 Resultados](#942-resultados)
- [10. Procedimentos de Implantação](#10-procedimentos-de-implantação)
  - [10.1 Implantação e Configuração do Banco de Dados](#101-implantação-e-configuração-do-banco-de-dados)
    - [10.1.1 Preflight do esquema](#1011-preflight-do-esquema)
    - [10.1.2 Aplicação da migração](#1012-aplicação-da-migração)
  - [10.2 Implantação do Protótipo para uso por equipe de desenvolvimento](#102-implantação-do-protótipo-para-uso-por-equipe-de-desenvolvimento)
    - [10.2.1 Restrições do Learner Lab e arquitetura adotada](#1021-restrições-do-learner-lab-e-arquitetura-adotada)
    - [10.2.2 Preparação dos contêineres](#1022-preparação-dos-contêineres)
    - [10.2.3 Build e publicação no ECR](#1023-build-e-publicação-no-ecr)
    - [10.2.4 Preparação da conta AWS](#1024-preparação-da-conta-aws)
    - [10.2.5 Criação da chave e substituição da EC2](#1025-criação-da-chave-e-substituição-da-ec2)
    - [10.2.6 Bootstrap da instância](#1026-bootstrap-da-instância)
    - [10.2.7 Instalação do runtime e inicialização da aplicação](#1027-instalação-do-runtime-e-inicialização-da-aplicação)
    - [10.2.8 Atualização e rollback](#1028-atualização-e-rollback)
    - [10.2.9 Publicação com Cloudflare Quick Tunnel](#1029-publicação-com-cloudflare-quick-tunnel)
    - [10.2.10 Validação e resultado da Sprint 4](#10210-validação-e-resultado-da-sprint-4)
    - [10.2.11 Operação após o deploy](#10211-operação-após-o-deploy)
- [11. Análise de Viabilidade Financeira](#11-análise-de-viabilidade-financeira)
  - [11.1 Escopo considerado no orçamento](#111-escopo-considerado-no-orçamento)
  - [11.2 Custos diretos do projeto](#112-custos-diretos-do-projeto)
  - [11.3 Despesas operacionais](#113-despesas-operacionais)
  - [11.4 Carga tributária estimada](#114-carga-tributária-estimada)
  - [11.5 Margem de lucro desejada](#115-margem-de-lucro-desejada)
  - [11.6 Preço final do projeto](#116-preço-final-do-projeto)
  - [11.7 Defesa das premissas e dos valores](#117-defesa-das-premissas-e-dos-valores)
  - [11.8 Fluxo de caixa sintético](#118-fluxo-de-caixa-sintético)
  - [11.9 Conclusão da viabilidade](#119-conclusão-da-viabilidade)
- [12. Benefícios Entregues e Aperfeiçoamentos Futuros](#12-benefícios-entregues-e-aperfeiçoamentos-futuros)
  - [12.1 Benefícios entregues](#121-benefícios-entregues)
  - [12.2 Aperfeiçoamentos futuros](#122-aperfeiçoamentos-futuros)
- [13. Plano de Adoção e Mobilização do Ecossistema](#13-plano-de-adoção-e-mobilização-do-ecossistema)
  - [13.1 Mapa de adoção e aculturamento organizacional](#131-mapa-de-adoção-e-aculturamento-organizacional)
    - [13.1.1 Público-alvo principal](#1311-público-alvo-principal)
    - [13.1.2 Barreiras culturais e técnicas esperadas](#1312-barreiras-culturais-e-técnicas-esperadas)
    - [13.1.3 Ações de onboarding e educação](#1313-ações-de-onboarding-e-educação)
  - [13.2 Mecanismos de incentivo e engajamento](#132-mecanismos-de-incentivo-e-engajamento)
    - [13.2.1 Utilidade e ganho de produtividade](#1321-utilidade-e-ganho-de-produtividade)
    - [13.2.2 Governança e voz ativa](#1322-governança-e-voz-ativa)
    - [13.2.3 Comunidade e reconhecimento](#1323-comunidade-e-reconhecimento)
    - [13.2.4 Indicadores de uso e qualidade](#1324-indicadores-de-uso-e-qualidade)
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
| TAPI | Termo de Abertura do Projeto Inteli, documento que formaliza o escopo, as restrições e as premissas acordadas entre o Metrô e o Inteli. |
| GTI | Gerência de Tecnologia da Informação do Metrô, responsável pelo provisionamento e homologação dos recursos tecnológicos. |
| NOR-00-223 | Normativo interno do Metrô que define a Gestão do Portfólio Organizacional. |
| Subportfólio | Categoria de agrupamento dos projetos e programas do portfólio organizacional. |
| Teams | Plataforma Microsoft Teams utilizada como principal interface de interação com o agente. |
| MVP | Minimum Viable Product (Produto Mínimo Viável), correspondente à primeira versão funcional da solução. |
| SharePoint | Plataforma Microsoft utilizada para armazenamento e organização de documentos corporativos. |
| Power Platform | Conjunto de ferramentas Microsoft utilizado para desenvolvimento da solução, incluindo Power Automate, Copilot Studio e demais componentes do ecossistema. |

---

## 1.2 Objetivo do Documento
Este documento tem como objetivo especificar a solução proposta para o desenvolvimento do Agente de IA para o Portfólio de Projetos do Metrô, consolidando os aspectos estratégicos, funcionais e técnicos necessários para sua compreensão e implementação.

Além de apoiar o desenvolvimento da solução ao longo das diferentes etapas do projeto, este documento também estabelece uma base de referência para validação junto aos representantes do Metrô, registro das decisões tomadas pela equipe e documentação das principais características da plataforma desenvolvida, favorecendo sua evolução e futura manutenção.

---

# 2. Entendimento do Projeto e do Negócio

---

## 2.1 Contexto da Indústria do Parceiro

O transporte metroviário desempenha um papel estratégico na mobilidade urbana das grandes metrópoles, sendo responsável pelo deslocamento diário de milhões de passageiros com elevados requisitos de segurança, confiabilidade e eficiência. Além da operação da infraestrutura ferroviária, o setor envolve projetos contínuos de expansão da malha, modernização tecnológica, manutenção e renovação de ativos, acessibilidade e melhoria da experiência dos passageiros. Nesse cenário, destacam-se tendências como a digitalização das operações, o uso crescente de dados e Inteligência Artificial (IA) como apoio à gestão, a automação de processos e a busca por maior integração das informações organizacionais.

Ao mesmo tempo, o setor enfrenta desafios relacionados à complexidade e ao alto custo dos projetos de infraestrutura, à necessidade de modernização contínua dos sistemas, ao gerenciamento de grandes volumes de informações e à coordenação de projetos com diferentes objetivos, prazos e partes interessadas. No contexto de organizações públicas, somam-se ainda requisitos de governança, transparência, prestação de contas e uso eficiente dos recursos públicos. Dessa forma, a capacidade de organizar, consultar e utilizar informações confiáveis sobre projetos torna-se relevante tanto para a eficiência operacional quanto para a tomada de decisões estratégicas.

Inserida nesse setor, a Companhia do Metropolitano de São Paulo (Metrô) é uma empresa pública vinculada ao Governo do Estado de São Paulo e possui papel relevante no sistema de transporte de alta capacidade da Região Metropolitana de São Paulo. A companhia atua na operação de parte da rede metroviária e no planejamento e execução de investimentos estratégicos relacionados à expansão, modernização e melhoria da infraestrutura de transporte. Seu posicionamento não se caracteriza por uma participação de mercado tradicional, mas por sua relevância como operador público e agente de desenvolvimento da infraestrutura metroviária paulista, atendendo diariamente uma parcela significativa da demanda por transporte coletivo da região e administrando projetos de elevada complexidade e impacto social.

Nesse contexto, o Escritório Corporativo de Projetos (PMO) desempenha a função de coordenar e acompanhar o portfólio de projetos da organização, lidando com informações relacionadas a objetivos, cronogramas, riscos, indicadores e documentação técnica. Conforme identificado junto ao parceiro, a quantidade de projetos e a dispersão das informações em diferentes documentos dificultam a localização e a consolidação do conhecimento necessário para consultas e análises. Além disso, experiências anteriores com ferramentas de IA generativa apresentaram limitações relacionadas à confiabilidade das respostas, reforçando a necessidade de uma solução que utilize como referência a documentação oficial do Metrô.

Diante desse cenário, o projeto propõe o desenvolvimento de um agente inteligente baseado em Processamento de Linguagem Natural (PLN) para apoiar o PMO na gestão e consulta das informações do portfólio de projetos. A solução busca permitir consultas rápidas e contextualizadas sobre a documentação disponibilizada, reduzindo o esforço necessário para localizar informações e aumentando a confiabilidade das respostas. Dessa forma, o projeto se alinha às tendências de digitalização e aplicação de IA no setor, ao mesmo tempo em que atende às necessidades específicas de governança, gestão do conhecimento e apoio à tomada de decisão do Metrô de São Paulo.

---


## 2.2 Problema

O Escritório Corporativo de Projetos (PMO) do Metrô de São Paulo é responsável por estabelecer e gerir a governança de estratégia, portfólio, programas, projetos e indicadores estratégicos da companhia, acompanhando iniciativas de expansão da malha, modernização tecnológica, manutenção de ativos e melhoria da experiência dos passageiros. As informações necessárias a esse acompanhamento — Termos de Abertura do Projeto (TAP), cronogramas, mapas de benefícios, entregas e marcos, riscos, mudanças, indicadores e normativos institucionais — encontram-se distribuídas entre o SharePoint, listas corporativas, relatórios do Power BI e documentos produzidos em Word, Excel e PowerPoint. Atualmente, a localização, a interpretação e a consolidação dessas informações ocorrem de forma predominantemente manual, sem uma camada unificada de consulta que relacione as diferentes fontes.

A ausência dessa camada faz com que responder a perguntas rotineiras de gestão — qual o avanço de um projeto, qual o prazo vigente, quais riscos estão em aberto, o que determina um normativo específico — exija navegação entre múltiplas plataformas e conhecimento prévio sobre onde cada informação está armazenada. Como consequência, atividades como a elaboração dos balanços mensais, o acompanhamento do andamento dos projetos e a consolidação dos relatórios de partida e de encerramento consomem parte significativa do tempo da equipe do PMO em tarefas administrativas de busca e compilação, reduzindo a capacidade de atuação analítica e estratégica da área e retardando a resposta às demandas de gestão.

Além da perda de eficiência, a consulta manual a fontes dispersas introduz riscos à confiabilidade da informação. Documentos com versões distintas, dados desatualizados e interpretações divergentes de um mesmo normativo podem gerar inconsistências entre os registros consultados e os efetivamente vigentes, comprometendo a rastreabilidade das informações utilizadas nas decisões. Conforme identificado junto ao parceiro, experiências anteriores com ferramentas de Inteligência Artificial generativa apresentaram limitações justamente nesse aspecto: as respostas obtidas nem sempre estavam fundamentadas na documentação oficial da companhia, o que reduziu a confiança das equipes no uso desse tipo de recurso. Soma-se a isso a restrição de confidencialidade, que impede que dados sensíveis de projeto sejam processados por serviços externos não homologados pelas áreas técnicas e de compliance.

O problema afeta tanto usuários internos quanto os processos de governança da organização. Internamente, a equipe do PMO e os gestores responsáveis pelos projetos permanecem sujeitos a processos manuais, retrabalho e forte dependência do conhecimento tácito de profissionais experientes, o que concentra a capacidade de consulta em poucas pessoas e fragiliza a continuidade das atividades. Externamente ao PMO, as demais áreas e instâncias que dependem dessas informações encontram maior dificuldade para acompanhar o portfólio de forma autônoma, o que reduz a agilidade da prestação de contas e do suporte à tomada de decisão. Em conjunto, esses fatores tornam a gestão do portfólio mais lenta, menos padronizada e mais suscetível a inconsistências, limitando o aproveitamento do conhecimento institucional já produzido pela companhia.

---

## 2.3 Análise SWOT

A Análise SWOT é uma ferramenta de planejamento estratégico utilizada para avaliar os fatores internos (forças e fraquezas) e externos (oportunidades e ameaças) que influenciam a posição competitiva e o desempenho de uma organização no longo prazo. No contexto deste projeto, a análise oferece uma visão estruturada do posicionamento da Companhia do Metropolitano de São Paulo no setor de mobilidade urbana sobre trilhos e evidencia como a melhoria da gestão e da consulta às informações do portfólio de projetos atua diretamente sobre suas fragilidades internas, apoiando os objetivos de eficiência, governança e modernização tecnológica.

<div align="center">
<img src="img/analise-swot.png" width="100%" alt="Análise SWOT da Companhia do Metropolitano de São Paulo">
  <p><strong>Figura 01</strong> - Análise SWOT da Companhia do Metropolitano de São Paulo.</p>
  <sup>Fonte: Material produzido pelos autores, 2026.</sup>
</div>

### 2.3.1 Forças

- **Operador consolidado de alta capacidade:** o Metrô opera quatro linhas próprias, somando 71,4 km de extensão e 63 estações, por onde circulam cerca de 3 milhões de passageiros por dia, com reconhecimento internacional pelos resultados de produção e qualidade do serviço prestado.

- **Governança de portfólio estruturada:** o PMO Corporativo (GPM) é responsável pela governança de estratégia, portfólio, programas, projetos e indicadores estratégicos, apoiado por normativo próprio (NOR-00-223) e por processos padronizados de partida, acompanhamento e encerramento.

- **Base tecnológica corporativa madura:** a companhia já dispõe de um ecossistema Microsoft implantado e sustentado pela equipe interna — SharePoint, Power Automate, Power BI e Copilot Studio —, o que reduz o custo de adoção de novas soluções e favorece a autonomia técnica da organização.

### 2.3.2 Fraquezas

- **Fragmentação da informação:** os dados do portfólio estão distribuídos entre listas, documentos, planilhas e normativos, sem uma camada unificada de consulta que relacione as diferentes fontes e permita acesso integrado ao conhecimento institucional.

- **Processos manuais e dependência de conhecimento tácito:** a consolidação de status, balanços mensais e relatórios de fechamento depende de esforço humano e da experiência de profissionais específicos, concentrando a capacidade de consulta e fragilizando a continuidade das atividades.

- **Ciclo de homologação restritivo:** a adoção de novas tecnologias depende do provisionamento de ambiente pela Gerência de Tecnologia da Informação (GTI) e da aprovação das áreas de compliance, o que alonga o tempo entre a concepção de uma solução e sua disponibilização efetiva.

### 2.3.3 Oportunidades

- **Maturidade do Processamento de Linguagem Natural e da IA generativa:** recursos já disponíveis e homologáveis no ecossistema Microsoft viabilizam interfaces de consulta em linguagem natural com baixo custo de sustentação, aproveitando a plataforma tecnológica existente.

- **Digitalização do setor metroviário:** a automação de processos e o uso de dados como apoio à gestão consolidam-se como tendência entre operadores de transporte de alta capacidade, criando referências e fornecedores maduros para iniciativas dessa natureza.

- **Agenda de transparência e eficiência no setor público:** a exigência crescente de prestação de contas, rastreabilidade e uso eficiente dos recursos públicos favorece investimentos em governança da informação e em ferramentas de apoio à decisão.

### 2.3.4 Ameaças

- **Exigências de confidencialidade e proteção de dados:** dados sensíveis de projeto não podem trafegar por serviços externos não homologados pelas áreas técnicas e de compliance, o que restringe o uso direto de soluções de mercado e impõe requisitos adicionais de arquitetura.

- **Dependência de orçamento público:** restrições fiscais e mudanças de prioridade governamental podem postergar investimentos em modernização tecnológica e em projetos de expansão, afetando a continuidade das iniciativas do portfólio.

- **Evolução acelerada das plataformas de mercado:** a eventual substituição ou complementação da plataforma atual de gestão de portfólio — por exemplo, pela adoção do Dynamics Project Operations — pode exigir readequação das soluções construídas sobre o ambiente vigente.

---

## 2.4 Visão do Projeto e do Produto
Este tópico apresenta a visão estratégica do produto proposto, sua proposta de valor e os objetivos que orientam seu desenvolvimento, estabelecendo o alinhamento entre a solução, os desafios identificados pela área de Gestão de Portfólio de Projetos (PMO) do Metrô e as necessidades do negócio. A definição desses elementos busca orientar as decisões arquiteturais, funcionais e de priorização do projeto, delimitando claramente seu escopo, as capacidades esperadas e o valor agregado aos diferentes perfis de usuários.

A proposta surge em um contexto de evolução da plataforma tecnológica utilizada pelo PMO, que já dispõe de ferramentas corporativas para armazenamento, organização e acompanhamento das informações do portfólio, mas ainda depende de atividades manuais para localizar documentos, consolidar informações, interpretar normativos, produzir relatórios e acompanhar o andamento dos projetos. Como consequência, parte significativa do conhecimento institucional permanece distribuída entre diferentes repositórios e depende da experiência dos profissionais para ser acessada de forma eficiente.

Nesse cenário, o produto busca transformar a forma como gestores e colaboradores interagem com esse conjunto de informações, incorporando recursos de Inteligência Artificial capazes de compreender solicitações em linguagem natural, interpretar diferentes intenções de uso e disponibilizar respostas contextualizadas, seguras e fundamentadas nas fontes oficiais da organização.

A solução é construída sobre o ecossistema Microsoft já adotado pela organização, e não ao lado dele. Isso mantém o custo de sustentação dentro do que a equipe interna do Metrô já opera, dispensa a introdução de uma nova plataforma no ciclo de homologação da GTI e permite que novas capacidades sejam incorporadas de forma incremental.

---

### 2.4.1 Visão do Produto

A visão do produto é transformar a interação entre os colaboradores e o portfólio de projetos do Metrô em uma experiência conversacional inteligente, integrada e orientada ao contexto de cada usuário, permitindo que informações estratégicas sejam acessadas por meio de linguagem natural de forma rápida, segura, rastreável e aderente às diretrizes de governança da organização.

Atualmente, embora a gestão do portfólio seja suportada por um conjunto consolidado de ferramentas corporativas, atividades relacionadas ao acompanhamento do avanço dos projetos, consulta a cronogramas, Termos de Abertura do Projeto (TAP), indicadores, documentos normativos e demais registros institucionais ainda exigem navegação entre diferentes plataformas, buscas manuais e interpretação de informações distribuídas em múltiplas fontes. Como consequência, essas atividades tornam-se mais demoradas, suscetíveis a inconsistências e dependentes do conhecimento especializado das equipes.

O produto propõe a criação de um agente inteligente integrado ao ambiente corporativo da organização, atuando como principal ponto de interação entre os usuários e o ecossistema de informações do portfólio. Por meio dessa interface conversacional, gestores e equipes poderão consultar informações dos projetos, esclarecer dúvidas sobre processos e normativos, localizar documentos, acompanhar cronogramas e obter respostas contextualizadas utilizando linguagem natural, reduzindo significativamente a necessidade de navegar entre diferentes sistemas ou conhecer previamente onde cada informação está armazenada.

O núcleo da solução é um mecanismo de Processamento de Linguagem Natural responsável por compreender a intenção de cada solicitação, classificá-la em consulta, transação ou alerta e direcioná-la ao fluxo de tratamento correspondente. É esse mecanismo que sustenta todas as demais capacidades do produto: sem a identificação correta da intenção, nenhuma consulta ou preenchimento assistido funciona.

---

### 2.4.2 Proposta de Valor

A proposta de valor do produto responde a duas condições observadas no PMO do Metrô. A primeira é operacional: as informações do portfólio estão distribuídas entre SharePoint, listas corporativas, Power BI e arquivos Office, e localizá-las exige saber de antemão onde cada uma está. A segunda é de confiança: conforme relatado pelo parceiro, experiências anteriores com IA generativa produziram respostas que nem sempre estavam fundamentadas na documentação oficial da companhia, e isso reduziu a confiança das equipes nesse tipo de recurso.

Essa segunda condição é o que determina a forma do produto. Não basta responder rápido: cada resposta precisa apontar de onde veio e precisa dizer quando não sabe. É por isso que a citação de fonte e a declaração explícita de limitação são requisitos do agente, e não boas práticas opcionais — a confiança que o produto precisa conquistar já foi quebrada uma vez naquele contexto.

Sobre essas duas condições, o produto entrega valor por meio das capacidades abaixo. Cada linha nomeia o que o agente faz e o efeito esperado sobre a rotina de quem usa.

| O que o agente faz | Efeito esperado |
| --- | --- |
| Responde em português corrente sobre status, prazos, entregas, marcos, riscos e normativos do portfólio | Elimina a necessidade de saber previamente em qual repositório cada informação está |
| Cita o documento que sustenta cada resposta e declara quando não há informação suficiente | Torna a resposta verificável e evita que o usuário receba conteúdo sem lastro documental |
| Compara projetos entre si em prazo, avanço, riscos e marcos | Substitui o cruzamento manual entre Power BI, planilhas e relatos dos líderes |
| Conduz entrevista guiada para preencher documentos do ciclo de vida do projeto | Reduz o esforço de preenchimento de formulários estáticos e padroniza o conteúdo registrado |
| Valida regras de preenchimento, como soma dos pesos do cronograma em 100%, coerência entre datas e campos obrigatórios | Impede que a inconsistência entre no registro, em vez de corrigi-la depois na consolidação |
| Aceita entrada por texto ou por voz dentro do Microsoft Teams | Permite consulta e atualização fora da estação de trabalho, em reunião ou deslocamento |
| Ajusta a profundidade da resposta ao perfil do usuário | Entrega síntese executiva à diretoria e detalhe operacional a quem acompanha o projeto |
| Gera prévia de relatório executivo mensal a partir dos dados consolidados | Reduz o tempo do PMO gasto em compilação para produzir material recorrente |
| Aciona lembretes de atualização de avanço e riscos via Teams | Diminui a cobrança manual que hoje o PMO faz aos responsáveis pelos projetos |

O detalhamento dessas capacidades, com a separação entre o que entra no MVP e o que fica para a evolução, está na Seção 2.4.3.

### 2.4.3 O que o Produto Faz e Não Faz

#### O que o Produto Faz

O produto é um agente conversacional disponível no Microsoft Teams que opera sobre a documentação e os dados de portfólio já mantidos pelo Metrô. Ele não substitui as plataformas corporativas: lê o que elas armazenam, responde a partir desse conteúdo e devolve o resultado no canal onde as equipes já trabalham. A arquitetura que sustenta essas capacidades está detalhada na Seção 5.2.

As capacidades estão organizadas em três blocos. Os dois primeiros compõem o MVP validado neste módulo; o terceiro está previsto para depois dele. A fronteira entre eles é a mesma declarada na matriz de priorização da Seção 2.8 e detalhada nos requisitos funcionais da Seção 3.1.

**Bloco 1 — Consulta e análise (MVP)**

| Capacidade | O que o agente faz |
| --- | --- |
| Entrada em linguagem natural | Recebe solicitações em português corrente, por texto ou por áudio transcrito, sem exigir sintaxe, comandos ou nomes técnicos de campos. |
| Identificação e classificação da intenção | Interpreta o pedido e o classifica em consulta, transação ou alerta, direcionando-o ao fluxo de tratamento correspondente. |
| Consulta a informações do projeto | Recupera status, avanço, prazos, entregas, marcos, riscos, indicadores e conteúdo de normativos a partir das fontes disponibilizadas ao pipeline. |
| Comparação entre projetos | Responde a perguntas que envolvem mais de uma iniciativa, confrontando prazo, avanço, riscos e marcos entre projetos do portfólio. |
| Resposta fundamentada com indicação de fonte | Apresenta, junto da resposta, o documento e o trecho que a sustentam, permitindo conferência pelo usuário. |
| Declaração explícita de limitação | Quando a base disponível não contém a informação pedida, responde que não há informação suficiente e indica o que faltou, em vez de preencher a lacuna. |
| Adaptação ao perfil do usuário | Ajusta o nível de detalhamento e o vocabulário da resposta conforme o perfil de quem pergunta, respeitando as permissões associadas a esse perfil. |

**Bloco 2 — Preenchimento assistido de documentos (MVP: Mapa de Benefícios)**

| Capacidade | O que o agente faz |
| --- | --- |
| Entrevista guiada | Conduz o líder do projeto por perguntas sequenciais que cobrem programa ou projeto, entregas, resultados, benefícios e objetivos estratégicos, adaptando as perguntas seguintes às respostas já dadas. |
| Sugestões a partir da base corporativa | Após o líder declarar as entregas, pergunta se ele deseja sugestões e, em caso afirmativo, consulta a base para propor resultados e benefícios relacionados a projetos comparáveis. |
| Validação de regras de preenchimento | Verifica a soma dos pesos do cronograma em 100%, a coerência entre datas de início e término e a presença dos campos obrigatórios antes de fechar o registro. |
| Geração do artefato estruturado | Produz o Mapa de Benefícios preenchido a partir das respostas coletadas e o disponibiliza para revisão e aprovação do líder, que permanece responsável pela validação final. |

O Mapa de Benefícios é o documento piloto deste bloco. A extensão do preenchimento assistido ao Termo de Abertura do Projeto, ao cronograma e aos registros de avanço está prevista como evolução.

**Bloco 3 — Acompanhamento e reporte (previsto para depois do MVP)**

| Capacidade | O que o agente faz |
| --- | --- |
| Lembrete proativo de atualização | Identifica pendências de preenchimento de avanço e de riscos e aciona os responsáveis via Teams, reduzindo a cobrança manual feita hoje pelo PMO. |
| Prévia de relatório executivo mensal | Consolida as informações do período em um relatório de status voltado à diretoria, destacando avanço, riscos e marcos relevantes. |
| Prévia de relatório anual de fechamento | Reúne as informações de encerramento do portfólio e de cada projeto em um documento de fechamento para revisão. |

Além das capacidades deste bloco, ficam fora do MVP a diferenciação da profundidade de pesquisa, o fluxo de avaliação das respostas, a interface personalizada e a geração de apresentações por template. Todas estão registradas na matriz de priorização da Seção 2.8 com a faixa e a justificativa correspondentes.

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

### 2.4.4 Objetivos Estratégicos e Mensuráveis

O sucesso do produto é acompanhado por cinco objetivos. Cada um traz a métrica que o acompanha, a meta assumida para o MVP, o experimento que produz o número e o item de escopo responsável por entregá-lo. A coluna de forma de verificação é a que impede a meta de ser apenas um número escolhido: ela descreve como o resultado será medido.

| Objetivo | Métrica de acompanhamento | Meta inicial do MVP | Forma de verificação | Relação com o escopo |
| --- | --- | --- | --- | --- |
| Reduzir esforço de localização de informações | Tempo médio para encontrar uma informação de projeto | Redução de 50% em cenário controlado | Comparação entre busca manual e consulta ao agente usando os mesmos casos sintéticos | Consulta de informações dos projetos |
| Aumentar confiabilidade das respostas | Percentual de respostas fundamentadas em fontes disponíveis | 100% das respostas do escopo devem indicar base documental ou limitação | Testes com perguntas de consulta, comparação e ausência de informação | Respostas estruturadas e fundamentadas |
| Melhorar autonomia dos usuários | Percentual de solicitações compreendidas sem sintaxe técnica | Pelo menos 80% das solicitações em português devem ser compreendidas ou orientadas para reformulação | Casos de teste com variações de linguagem natural | Entrada textual e interpretação de intenção |
| Apoiar decisões do PMO | Capacidade de comparar projetos, riscos, marcos e indicadores | Consultas analíticas demonstráveis com dados sintéticos | Cenários de comparação entre dois ou mais projetos | Fluxos de consulta e análise comparativa |
| Preservar governança e confidencialidade | Uso de dados sintéticos ou anonimizados e rastreio das interações | 100% da prova de conceito sem dados sensíveis reais | Auditoria da base utilizada e dos registros gerados pelo pipeline | Segurança, rastreabilidade e aderência tecnológica |

Duas observações sobre o recorte desta matriz.

A primeira é que as metas valem para o cenário controlado do MVP, sobre dados sintéticos. Elas medem se o pipeline funciona e se o comportamento esperado do agente se confirma, não o ganho em produção — que só pode ser apurado após a integração com o portfólio real, prevista como evolução.

A segunda é que a redução de 40% no número de consultas manuais a diferentes plataformas, considerada na etapa de entendimento do problema, não integra esta matriz. Ela depende de medir o comportamento das equipes no ambiente corporativo e, por isso, permanece como indicador de acompanhamento pós-implantação, fora do que este módulo consegue verificar.

### 2.4.5 Ownership e Accountability Estratégico

O desenvolvimento da solução envolve responsabilidades compartilhadas entre os representantes do Metrô e a equipe do projeto. A tabela abaixo registra quem responde por cada decisão e cada insumo. Ela existe para tornar visível a dependência entre os dois lados: as responsabilidades listadas na coluna do Metrô são, em vários casos, pré-requisito para que as da equipe possam ser cumpridas no prazo, e a última coluna aponta qual risco da Seção 2.7 se materializa quando a responsabilidade não é cumprida.

| Decisão ou insumo | Responsável pelo Metrô | Responsável pela equipe do projeto | Risco associado |
| --- | --- | --- | --- |
| Escopo e prioridade das funcionalidades | Decidir a prioridade entre funcionalidades concorrentes e aprovar mudanças de escopo | Apresentar o custo e o impacto técnico de cada alternativa antes da decisão | R07 |
| Fontes de informação e documentos | Disponibilizar documentos, normativos e dados de referência necessários ao desenvolvimento | Especificar quais fontes são necessárias, em que formato e até quando | R01, R05 |
| Acesso ao ambiente tecnológico | Prover acesso ao ambiente e conduzir a homologação junto à GTI | Declarar antecipadamente os recursos necessários e operar dentro do que for liberado | R02, R04 |
| Validação das entregas | Validar cada entrega quanto à aderência aos processos do PMO e registrar aceite ou ajuste | Preparar a entrega com evidência de execução e roteiro de validação | R06, R10 |
| Regras de negócio e interpretação de normativos | Confirmar a interpretação correta de normativos e regras do portfólio | Registrar a interpretação adotada e sinalizar divergências identificadas | R10 |
| Confidencialidade e uso de dados | Definir o que pode ser utilizado e sob quais restrições | Operar a prova de conceito apenas com dados sintéticos ou anonimizados | R04 |
| Arquitetura e implementação | Apontar restrições institucionais que limitem escolhas técnicas | Definir a arquitetura, implementar o MVP, testar e documentar as decisões | R02, R08 |
| Disponibilidade para rituais de acompanhamento | Participar das reuniões de validação acordadas no cronograma | Convocar com antecedência e enviar pauta e material prévio | R06 |

Quando uma responsabilidade da coluna do Metrô não é cumprida no prazo acordado, a equipe registra o bloqueio na issue correspondente e comunica o impacto sobre a sprint, conforme o mecanismo de acompanhamento de riscos descrito no documento de gestão de projeto.

#### Consolidação dos objetivos por métrica

Para reduzir ambiguidades entre objetivo estratégico, indicador e validação do MVP, os objetivos foram consolidados na matriz abaixo.

| Objetivo | Métrica de acompanhamento | Meta inicial do MVP | Forma de verificação | Relação com o escopo |
| --- | --- | --- | --- | --- |
| Reduzir esforço de localização de informações | Tempo médio para encontrar uma informação de projeto | Redução esperada de 50% em cenário controlado | Comparação entre busca manual e consulta ao agente usando os mesmos casos sintéticos | Consulta de informações dos projetos |
| Aumentar confiabilidade das respostas | Percentual de respostas fundamentadas em fontes disponíveis | 100% das respostas do escopo devem indicar base documental ou limitação | Testes com perguntas de consulta, comparação e ausência de informação | Respostas estruturadas e fundamentadas |
| Melhorar autonomia dos usuários | Percentual de solicitações compreendidas sem sintaxe técnica | Pelo menos 80% das solicitações em português devem ser compreendidas ou orientadas para reformulação | Casos de teste com variações de linguagem natural | Entrada textual e interpretação de intenção |
| Apoiar decisões do PMO | Capacidade de comparar projetos, riscos, marcos e indicadores | Consultas analíticas demonstráveis com dados sintéticos | Cenários de comparação entre dois ou mais projetos | Fluxos de consulta e análise comparativa |
| Preservar governança e confidencialidade | Uso de dados sintéticos/anonimizados e rastreio das interações | 100% da prova de conceito sem dados sensíveis reais | Auditoria da base utilizada e dos registros gerados pelo pipeline | Segurança, rastreabilidade e aderência tecnológica |

---

As capacidades da Seção 2.4.3, as metas da Seção 2.4.4 e a divisão de responsabilidades da Seção 2.4.5 formam o contrato de escopo deste projeto: o que o agente faz, como saberemos se funcionou e de quem depende cada parte. As seções seguintes detalham para quem o produto é construído (2.5), sobre qual processo de negócio ele atua (2.6) e quais riscos podem comprometer essa entrega (2.7).

---


## 2.5 Personas e Jornada do Usuário

As personas desenvolvidas representam diferentes perfis de usuários envolvidos na gestão do portfólio de projetos do Metrô. Elas ajudam a compreender como a solução proposta impacta rotinas distintas, desde a tomada de decisão estratégica até o acompanhamento operacional e a consolidação de informações. Considerando que o projeto propõe um agente inteligente para consulta, análise e apoio à gestão do portfólio, as personas evidenciam necessidades relacionadas à confiabilidade das respostas, redução de tarefas manuais, acesso rápido a indicadores e melhor organização das informações distribuídas entre documentos e plataformas corporativas.

### 2.5.1 Personas

#### 2.5.1.1 Roberto

<div align="center">
  <img src="img/Persona - Roberto.png" alt="Persona Roberto" width="800">
  <p><strong>Figura 02</strong> - Persona Roberto.</p>
</div>

Roberto é Diretor de Planejamento e Gestão Estratégica, tem 54 anos e atua em São Paulo. Sua rotina é marcada pelo acompanhamento executivo do portfólio de projetos, com foco em decisões estratégicas, riscos, resultados e alinhamento das iniciativas às prioridades organizacionais do Metrô. Por ocupar uma posição de diretoria, Roberto não dispõe de tempo para analisar documentos extensos ou acompanhar detalhes operacionais de cada projeto. Ele precisa receber informações sintetizadas, confiáveis e apresentadas em linguagem executiva, com destaque para projetos críticos, tendências, decisões pendentes e impactos organizacionais. No dia a dia, utiliza ferramentas como Word, Excel, PowerPoint, Teams e SharePoint, mas prefere soluções integradas ao ambiente corporativo que já utiliza.

#### 2.5.1.2 Mariana

<div align="center">
  <img src="img/Persona - Mariana.png" alt="Persona Mariana" width="800">
  <p><strong>Figura 03</strong> - Persona Mariana.</p>
</div>

Mariana é Analista Sênior de Gestão de Portfólio no PMO do Metrô, tem 38 anos e atua diretamente na qualidade, atualização e desempenho das informações do portfólio. Seu dia a dia envolve consolidar dados de diferentes projetos, identificar inconsistências, acompanhar indicadores e produzir análises para gestores e diretoria. Por ser organizada, analítica e orientada a processos, Mariana valoriza informações claras, rastreáveis e confiáveis, especialmente porque suas entregas dependem da consistência dos dados disponíveis. Entre seus principais desafios estão o esforço manual para comparar projetos, produzir relatórios e obter respostas rápidas sobre status, riscos, marcos e pendências. Ela possui alta afinidade tecnológica, domina o ecossistema Microsoft e utiliza diariamente Power BI, SharePoint, Excel e PowerPoint, embora dependa de ferramentas intuitivas e confiáveis para reduzir retrabalho.

#### 2.5.1.3 Carlos

<div align="center">
  <img src="img/Persona - Carlos.png" alt="Persona Carlos" width="800">
  <p><strong>Figura 04</strong> - Persona Carlos.</p>
</div>

Carlos é Gerente de Portfólio de Projeto, tem 44 anos e coordena um conjunto de projetos relacionados à sua área de atuação. Sua rotina envolve acompanhar o desempenho do subportfólio, identificar dependências entre projetos, orientar líderes, priorizar recursos e reportar informações ao PMO. Por atuar em uma posição intermediária entre a operação dos projetos e a gestão corporativa, Carlos precisa transformar informações dispersas em uma visão consolidada que apoie decisões táticas. No dia a dia, enfrenta desafios como dependências difíceis de acompanhar, disputa de recursos e demora para reunir informações sobre desvios e impactos. Ele utiliza SharePoint, Power BI, Excel e ferramentas corporativas, interpreta dashboards com facilidade e possui familiaridade intermediária com automações e agentes de IA, valorizando alertas, informações consolidadas e apoio para priorizar ações.

### 2.5.2 Jornadas do Usuário

As jornadas do usuário foram desenvolvidas para representar como diferentes perfis interagem com o processo de gestão e consulta das informações do portfólio de projetos. Elas evidenciam objetivos, ações, pensamentos, dores, emoções e oportunidades em cada etapa da experiência, permitindo compreender com mais clareza onde a solução proposta pode gerar valor. No contexto do agente inteligente para apoio à Gestão de Portfólio de Projetos do Metrô, as jornadas ajudam a identificar momentos em que a centralização das informações, a geração de respostas confiáveis e a redução de consultas manuais podem melhorar a tomada de decisão e a rotina dos usuários.

Foram mapeadas as jornadas das três personas, cobrindo os três níveis de uso da solução: Roberto representa o consumo executivo do resultado, Mariana a produção da informação consolidada e Carlos a coordenação tática entre os dois. A jornada de Mariana é a que se aproxima mais do problema descrito na Seção 2.2, porque é ela quem executa a consolidação dos balanços mensais e dos relatórios — a atividade que concentra o esforço manual que o projeto se propõe a reduzir.

Além dos mapas visuais, as jornadas foram sintetizadas em etapas funcionais para explicitar a relação entre necessidade do usuário, dor observada e oportunidade de produto.

| Persona | Etapa da jornada | Necessidade principal | Dor observada | Oportunidade para a solução |
| --- | --- | --- | --- | --- |
| Roberto | Identificar temas críticos do portfólio | Obter visão executiva rápida sobre riscos, atrasos e decisões pendentes | Relatórios extensos e pouco tempo para análise | Resumo executivo fundamentado em fontes disponíveis |
| Roberto | Avaliar cenários antes de decidir | Comparar impactos e priorizar ações estratégicas | Dependência de consolidação manual pelo PMO | Consulta analítica com diferenciação entre fato recuperado e interpretação |
| Roberto | Acompanhar efeitos das decisões | Verificar mudanças relevantes após direcionamentos anteriores | Dificuldade de recuperar histórico e mudanças recentes | Respostas rastreáveis com referência aos documentos consultados |
| Mariana | Consolidar o balanço mensal do portfólio | Reunir status, avanço, riscos e marcos de todos os projetos do período | Compilação manual a partir de SharePoint, listas, Power BI e planilhas | Consulta única sobre projetos e subportfólios, com consolidação assistida |
| Mariana | Conferir a consistência dos dados | Confirmar que os números usados são os vigentes | Versões divergentes de documentos, datas incoerentes e pesos de cronograma que não fecham | Validação de regras no momento do registro: soma dos pesos em 100%, coerência de datas e campos obrigatórios |
| Mariana | Responder às perguntas de gestores e diretoria | Sustentar cada número com sua origem documental | Baixa confiança em resposta automática sem lastro, após experiência anterior com IA generativa | Resposta com citação da fonte e declaração explícita quando a informação não existe |
| Mariana | Produzir a análise para decisão | Entregar material confiável e pronto para uso executivo | Retrabalho quando um dado muda depois da consolidação | Prévia de relatório executivo mensal gerada a partir dos dados já consolidados |
| Mariana | Acompanhar pendências do ciclo seguinte | Manter a base atualizada sem cobrar pessoa por pessoa | Cobrança manual repetida a cada ciclo mensal | Lembrete proativo via Teams das pendências de avanço e de riscos |
| Carlos | Preparar reunião de acompanhamento | Consolidar status, riscos e dependências do subportfólio | Informações distribuídas em diferentes fontes | Consulta por linguagem natural sobre projetos e subportfólios |
| Carlos | Investigar desvios | Aprofundar atrasos, riscos e impactos antes de acionar líderes | Retrabalho para cruzar Power BI, documentos e relatos | Comparação estruturada entre projetos e recuperação de evidências |
| Carlos | Coordenar ações do subportfólio | Direcionar responsáveis com base em informação confiável | Baixa confiança em respostas sem contexto | Respostas com fonte, limitação explícita e indicação de dados ausentes |

#### 2.5.2.1 Mapa de jornada - Roberto

<div align="center">
  <img src="img/User Journey Map - Roberto.png" alt="Mapa de Jornada do Usuário - Roberto" width="900">
  <p><strong>Figura 05</strong> - Mapa de jornada do usuário Roberto.</p>
</div>

A jornada de Roberto representa a experiência de um usuário com perfil executivo, que precisa compreender rapidamente quais temas exigem sua atenção e quais decisões estratégicas devem ser tomadas. No início da jornada, Roberto consulta indicadores, verifica pendências e acompanha projetos, mas enfrenta muitas demandas simultâneas e pouco tempo para análise. Em seguida, busca compreender o cenário antes de decidir, recorrendo a relatórios, dashboards, ao Copilot atual e ao apoio do PMO para obter contexto, o que evidencia sua dependência de sínteses e a dificuldade de lidar com relatórios extensos.

Com a introdução da solução, Roberto passa a buscar uma síntese rápida e confiável por meio de consultas ao novo agente, fazendo perguntas por texto ou voz e aprofundando pontos críticos conforme necessário. Nessa etapa, a principal oportunidade está em evidenciar a confiabilidade das fontes, oferecer respostas objetivas e guiar aprofundamentos. Ao avançar para a definição de prioridades e direcionamentos, Roberto compara cenários, discute com gestores e define ações com maior segurança, utilizando a solução para compreender impactos e apoiar decisões de alta responsabilidade. Por fim, ao verificar os impactos das decisões tomadas, ele acompanha mudanças relevantes, indicadores e direcionamentos anteriores, com a expectativa de antecipar novos riscos e avaliar se as decisões produziram os efeitos esperados.

#### 2.5.2.2 Mapa de jornada - Mariana

<div align="center">
  <img src="img/User Journey Map - Mariana.png" alt="Mapa de Jornada do Usuário - Mariana" width="900">
  <p><strong>Figura 06</strong> - Mapa de jornada do usuário Mariana.</p>
  <sup>Fonte: Material produzido pelos autores, 2026.</sup>
</div>

A jornada de Mariana percorre o ciclo mensal de consolidação do portfólio, a rotina que a Seção 2.2 identifica como a maior consumidora de tempo administrativo do PMO. Ela começa reunindo status, avanço, riscos e marcos de todos os projetos do período, o que hoje exige abrir SharePoint, listas corporativas e Power BI, baixar planilhas e compilar os dados manualmente. A dor dessa etapa não é a análise, é a coleta: o esforço se concentra antes de qualquer raciocínio sobre os números.

Na segunda fase, Mariana precisa confirmar que os dados reunidos são os vigentes. Compara versões de documentos, confere datas e pesos de cronograma e recorre aos líderes de projeto quando algo não fecha. É aqui que aparecem as inconsistências que a Seção 2.2 associa à consulta manual a fontes dispersas: versões divergentes do mesmo documento, datas incoerentes e pesos que não somam 100%. A oportunidade correspondente não é detectar o erro depois, mas impedir que ele entre — validar as regras no momento do registro, como descrito no Bloco 2 da Seção 2.4.3.

A terceira fase é a que mais depende da confiança. Ao consultar o agente para responder às perguntas de gestores e diretoria, Mariana traz consigo a experiência anterior do PMO com IA generativa, em que as respostas nem sempre estavam fundamentadas na documentação oficial. Por isso sua pergunta não é apenas se a resposta está certa, mas se ela consegue mostrar de onde veio. É essa etapa que sustenta a exigência de citação de fonte e de declaração explícita quando a informação não existe na base.

Nas duas fases finais, Mariana produz a análise para decisão e fecha o ciclo. Na quarta, monta o material executivo e revisa números e referências, sujeita a retrabalho sempre que um dado muda depois da consolidação — o que a prévia de relatório executivo mensal, gerada a partir dos dados já consolidados, reduz. Na quinta, levanta as pendências de preenchimento e aciona os responsáveis, tarefa hoje feita pessoa por pessoa a cada mês e que o lembrete proativo via Teams passa a executar. As cinco fases dessa jornada correspondem, nessa ordem, às cinco linhas de Mariana na tabela de etapas apresentada acima.

#### 2.5.2.3 Mapa de jornada - Carlos

<div align="center">
  <img src="img/User Journey Map - Carlos.png" alt="Mapa de Jornada do Usuário - Carlos" width="900">
  <p><strong>Figura 07</strong> - Mapa de jornada do usuário Carlos.</p>
</div>

A jornada de Carlos representa a experiência de um gerente de portfólio que precisa acompanhar os projetos sob sua responsabilidade e se preparar para reuniões com líderes do subportfólio. Na primeira fase, Carlos busca entender quais projetos exigem atenção, analisando indicadores, verificando entregas e prazos e preparando reuniões. Suas principais dores estão relacionadas à distribuição das informações entre diferentes projetos e à dificuldade de visualizar dependências, o que torna sua rotina mais complexa e exige esforço constante de consolidação.

Ao tentar obter rapidamente o status do subportfólio, Carlos consulta o agente atual, pergunta sobre riscos e atrasos e reformula perguntas para encontrar respostas mais úteis. Nesse momento, surgem frustrações associadas a respostas pouco contextualizadas e à baixa confiança nos resultados. Em seguida, ao confirmar riscos e desvios antes de agir, ele consulta Power BI, documentos e líderes de projeto, além de consolidar informações manualmente, o que revela retrabalho e dificuldade para cruzar fontes distintas. Com a nova solução, Carlos passa a consultar por texto ou voz, aprofundar riscos e dependências e comparar projetos de forma mais integrada. A jornada termina com a antecipação de problemas e a coordenação dos projetos, etapa em que alertas relevantes, histórico de riscos e identificação proativa de desvios ajudam Carlos a direcionar líderes e recursos com mais controle e confiança.


---

## 2.6 Modelagem do Fluxo de Negócio

A modelagem do fluxo de negócio tem como objetivo representar o processo de elaboração do Mapa de Benefícios, permitindo compreender o funcionamento atual da atividade e as mudanças propostas com a utilização do agente inteligente. Para isso, foram utilizados três artefatos complementares: a Cadeia de Valor, que apresenta uma visão consolidada do processo atual e futuro, e os diagramas BPMN dos fluxos AS-IS e TO-BE.

**Por que este processo, entre todos os do portfólio**

A gestão do portfólio do Metrô compreende uma sequência de processos de negócio que existe independentemente desta solução: aprovar o empreendimento, dar partida, executar, reportar avanço mensal, consolidar o portfólio e encerrar. A elaboração do Mapa de Benefícios foi escolhida como recorte de modelagem por três razões.

A primeira é que o parceiro a nomeou explicitamente. Entre os oito documentos do ciclo de vida citados no material de referência do Metrô, o Mapa de Benefícios aparece como o primeiro da lista e é o único acompanhado de uma história de usuário completa, com o roteiro de perguntas que o agente deveria conduzir. Modelar esse processo permite confrontar o fluxo desenhado com o comportamento que o parceiro já descreveu.

A segunda é a posição do artefato no ciclo. O Mapa de Benefícios é elaborado na partida do projeto e é o que liga entregas a resultados, benefícios e objetivos estratégicos. Todos os artefatos posteriores — cronograma, avanço, balanço mensal, relatório de fechamento — reportam contra essa ligação. Um erro de preenchimento aqui se propaga por todo o acompanhamento subsequente.

A terceira é que este processo concentra as duas capacidades que o MVP precisa demonstrar ao mesmo tempo: a consulta à base corporativa, quando o agente busca sugestões de resultados e benefícios em projetos comparáveis, e a transação, quando conduz a entrevista e gera o artefato. Um processo apenas de consulta não exercitaria o segundo caminho.

Os demais processos do portfólio permanecem fora deste recorte de modelagem, mas não fora do produto: as capacidades previstas para eles estão registradas no Bloco 3 da Seção 2.4.3 e na matriz de priorização da Seção 2.8.

O modelo AS-IS representa o processo atualmente realizado, caracterizado principalmente pela execução manual das atividades de levantamento, definição e preenchimento das informações. Já o modelo TO-BE representa o processo proposto pelo projeto, no qual o agente inteligente passa a apoiar o responsável pelo projeto na coleta, organização e geração das informações necessárias para elaboração do Mapa de Benefícios.

A modelagem também evidencia a mudança no papel do responsável pelo projeto. No cenário atual, grande parte do esforço está concentrada na execução operacional do processo, enquanto no cenário futuro o agente inteligente assume parte dessas atividades, permitindo que o responsável concentre sua atuação na interação com o sistema, revisão e validação do resultado.

Dessa forma, o fluxo proposto não busca retirar a participação humana do processo, mas utilizar a inteligência artificial como mecanismo de apoio à elaboração do artefato, mantendo a validação final sob responsabilidade do usuário.

---

### 2.6.1 Cadeia de Valor

A cadeia de valor evidencia como o processo de elaboração do mapa de benefícios evolui entre o cenário atual **(AS-IS)** e o cenário futuro **(TO-BE)**. No processo atual, grande parte das informações necessárias para construir o mapa é obtida manualmente, exigindo consulta a múltiplos documentos, interpretação do conhecimento tácito do gestor e preenchimento manual do artefato. No processo futuro, essas atividades permanecem sob condução do líder do projeto, mas passam a contar com o apoio de um agente inteligente capaz de consultar a documentação corporativa, recuperar informações relevantes, sugerir relações entre entregas, resultados e benefícios e gerar automaticamente o mapa para validação final do usuário.

<div align="center">
  <img src="img/Cadeia-de-valor-m07.png" alt="Cadeia de valor do processo de elaboração do Mapa de Benefícios nos cenários AS-IS e TO-BE" width="500">
  <p><strong>Figura 08</strong> - Cadeia de valor do processo de elaboração do Mapa de Benefícios.</p>
  <sup>Fonte: Material produzido pelos autores, 2026.</sup>
</div>

No cenário **AS-IS**, o processo é composto pelas etapas de **Identificação do Projeto**, **Definição das Entregas**, **Identificação dos Resultados**, **Definição dos Benefícios**, **Alinhamento Estratégico**, **Preenchimento Manual do Mapa** e **Revisão e Armazenamento**.

Nesse cenário, o processo depende principalmente da atuação manual do líder do projeto. A identificação das informações necessárias ocorre por meio da consulta e análise de diferentes fontes, exigindo a localização, a interpretação e a organização dos dados relevantes para a elaboração do mapa. A definição dos benefícios e o alinhamento estratégico também dependem de seu conhecimento e de sua análise. Ao final, o Mapa de Benefícios é preenchido manualmente e posteriormente revisado e armazenado, sem o mesmo nível de padronização proposto no cenário futuro.

No cenário **TO-BE**, o objetivo do processo permanece o mesmo: elaborar um **Mapa de Benefícios relacionado a um projeto**. A principal mudança está na forma como as informações são obtidas, organizadas e transformadas no artefato final. O agente inteligente passa a apoiar o líder do projeto, principalmente na **consulta da documentação corporativa, recuperação de informações relevantes, geração de sugestões e estruturação do mapa**.

A primeira etapa passa a ser a **Identificação do Projeto com apoio documental e do agente**, permitindo que as informações necessárias para contextualizar o mapa sejam obtidas com auxílio da base corporativa. Em seguida, a **Definição das Entregas** passa a contar com um levantamento assistido, reduzindo a necessidade de realizar manualmente a busca e organização das informações.

Na etapa de **Identificação dos Resultados**, o agente apoia a consulta à base corporativa para localizar informações relacionadas ao projeto e aos seus resultados esperados. A partir dessas informações, também são apresentadas **sugestões de benefícios baseadas nos documentos consultados**, auxiliando o usuário na identificação das relações entre resultados e benefícios.

O **Alinhamento Estratégico** também passa a receber apoio do agente por meio da sugestão de objetivos estratégicos relacionados às informações levantadas. Entretanto, essas sugestões possuem caráter de apoio e não substituem a análise ou a decisão do líder do projeto.

A principal transformação ocorre na etapa de **Geração Automática do Mapa**, que substitui o preenchimento manual do artefato pela geração estruturada do Mapa de Benefícios a partir das informações coletadas e das relações identificadas durante o processo. Dessa forma, o agente reduz o esforço operacional necessário para transformar as informações levantadas em um documento estruturado.

Por fim, a etapa de **Revisão e Armazenamento** do cenário atual é transformada em uma etapa de **Validação Padronizada** no cenário futuro. O líder do projeto continua realizando a conferência e a aprovação do conteúdo gerado, porém o processo passa a estabelecer uma forma mais estruturada e padronizada para a validação e publicação do documento.

Dessa forma, a Cadeia de Valor demonstra que o agente inteligente **não tem como objetivo criar ou gerenciar projetos**, mas apoiar o processo de elaboração do Mapa de Benefícios. Seu impacto está concentrado na redução do esforço manual necessário para **consultar documentos, localizar informações, organizar conhecimento, gerar sugestões e estruturar o artefato final**. As decisões e a validação das informações permanecem sob condução do líder do projeto.


A comparação evidenciada na imagem da cadeia, mostra que a proposta **não altera a finalidade do processo**, que continua sendo a elaboração de um Mapa de Benefícios válido e relacionado ao projeto analisado. A transformação ocorre principalmente na maneira como o conhecimento necessário é obtido e utilizado: atividades que anteriormente dependiam de buscas e organização manuais passam a contar com o apoio do agente inteligente, enquanto a geração e a validação do artefato tornam-se mais estruturadas e padronizadas.

Assim, a Cadeia de Valor complementa os fluxos **AS-IS** e **TO-BE**, demonstrando de forma visual e operacional **onde o agente agrega valor ao processo e quais atividades são impactadas pela sua utilização**.

---


---

### 2.6.2 Fluxo de Negócio Proposto (AS-IS e TO-BE)

Os fluxos de negócio apresentados a seguir detalham o processo de elaboração do Mapa de Benefícios nos cenários **AS-IS** e **TO-BE**, evidenciando como as atividades são executadas em cada contexto. A modelagem em BPMN complementa a Cadeia de Valor apresentada anteriormente ao representar a sequência das atividades, os participantes envolvidos, as interações com o repositório corporativo e os pontos de decisão que orientam a execução do processo.

Duas convenções de notação orientam a leitura dos diagramas. A primeira é que apenas participantes que executam e decidem aparecem como raia: o líder do projeto e o agente inteligente. O repositório corporativo é representado como **objeto de dados**, e não como raia, porque é consultado e gravado, mas nunca inicia ação — quem consulta é o agente, por meio de tarefas de serviço na própria raia. A segunda é que todo gateway representa uma decisão efetiva, com mais de um caminho de saída; pontos do fluxo que apenas registram informação são modelados como tarefa, não como losango.

### AS-IS — Fluxo Atual

<div align="center">
  <img src="img/fluxo-as-is.png" alt="Diagrama BPMN do fluxo AS-IS de elaboração do Mapa de Benefícios" width="700">
  <p><strong>Figura 09</strong> - Fluxo de negócio AS-IS: elaboração manual do Mapa de Benefícios.</p>
  <sup>Fonte: Material produzido pelos autores, 2026.</sup>
</div>

O fluxo **AS-IS** representa a elaboração manual do Mapa de Benefícios pelo líder do projeto ou usuário responsável. O processo inicia-se com a **identificação da necessidade do mapa**, seguida pela **consulta de documentos e normativos** que fornecem as informações necessárias para contextualizar a iniciativa.

Após essa consulta, o responsável realiza a **identificação do programa ou projeto** que será analisado e, posteriormente, define as **entregas**, os **resultados esperados** e os **benefícios** relacionados à iniciativa. Na sequência, são definidos os **objetivos estratégicos** associados ao mapa.

Com essas informações levantadas, o responsável realiza o **preenchimento manual do mapa**. Após o preenchimento, o documento passa pela etapa de **revisão**.

O fluxo possui um gateway de decisão **XOR** representado pela pergunta **"Mapa aprovado?"**. Caso a resposta seja **"Sim"**, o documento é armazenado e o processo é encerrado. Caso a resposta seja **"Não"**, o documento é encaminhado para **correção** e retorna ao fluxo de revisão, permitindo que o responsável realize novos ajustes até que o mapa seja aprovado.

### TO-BE — Fluxo Proposto

<div align="center">
  <img src="img/fluxo-to-be.png" alt="Diagrama BPMN do fluxo TO-BE de elaboração do Mapa de Benefícios com apoio do agente" width="700">
  <p><strong>Figura 10</strong> - Fluxo de negócio TO-BE: elaboração do Mapa de Benefícios com apoio do agente.</p>
  <sup>Fonte: Material produzido pelos autores, 2026.</sup>
</div>

O fluxo **TO-BE** representa o processo de elaboração do Mapa de Benefícios com o apoio do agente inteligente. O diagrama tem duas raias — **líder do projeto** e **agente inteligente** —, que são os dois participantes que executam atividades e tomam decisões. O **repositório corporativo** aparece como objeto de dados, alvo das tarefas de serviço executadas pelo agente.

O processo inicia-se na raia do **líder do projeto**, que acessa o assistente e **solicita a criação do mapa**. Essa solicitação corresponde à elaboração do Mapa de Benefícios para um programa ou projeto existente, não à criação ou desenvolvimento do próprio projeto.

Após a solicitação, o agente inicia a **entrevista guiada**. A primeira decisão do fluxo é o gateway XOR **"Programa ou projeto?"**, que bifurca de acordo com a natureza do componente do portfólio: no caminho **"Programa"**, o agente registra o programa e os projetos que o compõem, coletando um conjunto de informações por projeto; no caminho **"Projeto único"**, registra apenas o projeto e segue adiante. Os dois caminhos convergem antes da coleta das entregas. Essa bifurcação reproduz o comportamento descrito pelo parceiro na história de usuário do Mapa de Benefícios, em que a pergunta sobre os projetos componentes só é feita quando o componente é um programa.

Na sequência, o agente realiza a coleta das **entregas**. Nesse ponto, o gateway XOR **"Solicitar sugestões?"** verifica se o líder deseja apoio da base. Quando a resposta é **"Sim"**, o agente executa a tarefa de serviço **"Consultar base comparativa"**, que lê o repositório corporativo e devolve sugestões para complementar o registro das entregas. Quando é **"Não"**, o fluxo segue direto para o registro.

O processo continua com o registro das entregas e a coleta dos **resultados esperados** e dos **benefícios**. Para os benefícios há novamente a decisão **"Sugestões de benefícios?"**, cujo caminho afirmativo executa a tarefa de serviço **"Consultar base corporativa"** sobre o mesmo repositório.

Depois disso, o agente coleta os **objetivos estratégicos** e o gateway **"Incluir novos benefícios?"** permite retornar à coleta de benefícios quando o líder identifica algum benefício adicional durante a etapa de alinhamento estratégico. Com as informações consolidadas, o agente executa a **geração do Mapa de Benefícios** e a tarefa de serviço **"Salvar artefato no repositório"**.

A partir desse ponto, o fluxo retorna ao **líder do projeto**, que realiza a **revisão do mapa gerado**. O resultado é definido pelo gateway XOR **"Mapa aprovado?"**. Caso o mapa seja aprovado, o líder **exporta e salva o documento**, encerrando o processo. Caso não seja, ele **solicita ajuste** e o fluxo retorna à coleta de entregas, permitindo que as informações sejam complementadas e que um novo mapa seja gerado para revisão.

O código-fonte do diagrama está versionado em [`docs/diagrams/fluxo-to-be.svg`](diagrams/fluxo-to-be.svg).

---

## 2.7 Matriz de Risco do Projeto


A matriz de risco do projeto tem como objetivo registrar, avaliar e acompanhar eventos que possam afetar positiva ou negativamente a execução do desenvolvimento do **Agente de IA para o Portfólio de Projetos do Metrô**.

A identificação dos riscos foi realizada considerando o contexto atual do projeto, suas dependências técnicas e organizacionais, as características do produto proposto e o estágio de desenvolvimento da solução. Entre os principais fatores considerados estão a dependência de informações e documentos disponibilizados pelo parceiro, a utilização do ecossistema Microsoft, a necessidade de integração com diferentes fontes de conhecimento, o controle de acesso às informações e a necessidade de garantir respostas fundamentadas para os usuários.

A matriz também contempla **oportunidades**, representadas por eventos de natureza positiva que, caso ocorram ou sejam adequadamente explorados, podem contribuir para a evolução, qualidade ou eficiência da solução.

Como o projeto encontra-se em etapa de desenvolvimento e consolidação da documentação, os riscos identificados deverão ser revisados periodicamente conforme novas decisões arquiteturais, validações com o parceiro, disponibilização de dados e evolução do escopo.

---

### 2.7.1 Critérios de Avaliação

A avaliação dos riscos utiliza uma escala de **1 a 5** para probabilidade e impacto.

### Probabilidade

| Valor | Classificação | Descrição |
| :---: | --- | --- |
| **1** | Muito baixa | Evento improvável de ocorrer durante o projeto. |
| **2** | Baixa | Evento pouco provável, mas possível. |
| **3** | Média | Evento com possibilidade moderada de ocorrência. |
| **4** | Alta | Evento provável de ocorrer durante o projeto. |
| **5** | Muito alta | Evento muito provável ou recorrente durante o projeto. |

### Impacto

| Valor | Classificação | Descrição |
| :---: | --- | --- |
| **1** | Muito baixo | Consequências praticamente desprezíveis para o projeto. |
| **2** | Baixo | Pequeno impacto sobre uma atividade ou entrega, sem comprometer significativamente o projeto. |
| **3** | Médio | Impacto relevante sobre uma atividade, entrega ou prazo, exigindo intervenção da equipe. |
| **4** | Alto | Pode comprometer uma entrega importante, gerar retrabalho significativo ou afetar o cronograma. |
| **5** | Muito alto | Pode comprometer diretamente objetivos do projeto, funcionalidades centrais ou a viabilidade de uma entrega. |

A **severidade** é calculada pela seguinte regra:

> **Severidade = Probabilidade × Impacto**

A classificação resultante segue as seguintes faixas:

| Severidade | Criticidade | Interpretação |
| :---: | --- | --- |
| **1–4** | 🟢 Baixa | Risco deve ser acompanhado, mas não exige intervenção prioritária. |
| **5–9** | 🟡 Moderada | Requer acompanhamento e ações preventivas quando aplicável. |
| **10–14** | 🟠 Alta | Deve possuir acompanhamento ativo e ações planejadas. |
| **15–25** | 🔴 Crítica | Deve receber tratamento prioritário pela equipe. |

Para as oportunidades, a mesma pontuação é utilizada para representar o **potencial de aproveitamento** do evento positivo.

---

### 2.7.2 Registro dos Riscos e Oportunidades

A matriz abaixo consolida os riscos identificados para o projeto, contemplando riscos negativos e positivos, suas categorias, avaliação, responsáveis, ações planejadas e status.

| ID | Tipo | Categoria | Risco / Oportunidade | P | I | Sev. | Criticidade | Responsável | Status |
| :---: | :---: | --- | --- | :---: | :---: | :---: | --- | --- | --- |
| **R01** | 🔴 Risco | Dados | Indisponibilidade ou baixa qualidade das informações e documentos necessários para alimentar a base de conhecimento do agente. | 4 | 5 | **20** | 🔴 Crítica | Jaime Almeida | Em Monitoramento |
| **R02** | 🔴 Risco | Técnico | Dificuldades ou limitações nas integrações com Microsoft Teams, Power Platform ou demais componentes do ecossistema Microsoft. | 4 | 5 | **20** | 🔴 Crítica | Felipe Teixeira | Em Monitoramento |
| **R03** | 🔴 Risco | Técnico | Respostas inadequadas, imprecisas ou não suficientemente fundamentadas geradas pelo agente de IA. | 4 | 5 | **20** | 🔴 Crítica | Henrique Diniz | Em Monitoramento |
| **R04** | 🔴 Risco | Técnico | Limitações na implementação do controle de autenticação, permissões e acesso às informações conforme o perfil do usuário. | 3 | 5 | **15** | 🔴 Crítica | Wendel Feitosa | Em Monitoramento |
| **R05** | 🔴 Risco | Dados | Alterações, inconsistências ou desatualização das fontes utilizadas pelo agente durante o desenvolvimento. | 4 | 4 | **16** | 🔴 Crítica | Leonardo Ramos | Em Monitoramento |
| **R06** | 🔴 Risco | Stakeholders | Indisponibilidade ou baixa participação dos representantes do Metrô durante validações e esclarecimento de dúvidas de negócio. | 3 | 4 | **12** | 🟠 Alta | Jaime Almeida | Aberto |
| **R07** | 🔴 Risco | Escopo | Ampliação do escopo decorrente da incorporação de novas funcionalidades ou necessidades levantadas durante o projeto. | 4 | 4 | **16** | 🔴 Crítica | Pedro Uchoa | Em Monitoramento |
| **R08** | 🔴 Risco | Cronograma | Tempo insuficiente para implementar, validar e documentar todas as funcionalidades previstas para a solução. | 4 | 4 | **16** | 🔴 Crítica | Felipe Teixeira | Em Monitoramento |
| **R09** | 🔴 Risco | Equipe | Sobrecarga ou indisponibilidade de integrantes para execução simultânea das atividades de análise, documentação, desenvolvimento e validação. | 3 | 4 | **12** | 🟠 Alta | Henrique Diniz | Aberto |
| **R10** | 🔴 Risco | Comunicação | Divergência de entendimento entre equipe e stakeholders sobre requisitos, prioridades ou comportamento esperado do agente. | 3 | 3 | **9** | 🟡 Moderada | Pedro Uchoa | Em Monitoramento |
| **O1** | 🟢 Oportunidade | Técnico | Aproveitamento do ecossistema Microsoft já utilizado pelo parceiro para facilitar integração, adoção e disponibilização do agente. | 4 | 4 | **16** | 🟢 Alta oportunidade | Wendel Feitosa | Em Monitoramento |
| **O2** | 🟢 Oportunidade | Stakeholders / Dados | Disponibilização de fontes oficiais e conhecimento especializado do PMO para aumentar a qualidade e a contextualização das respostas do agente. | 3 | 5 | **15** | 🟢 Alta oportunidade | Leonardo Ramos | Em Monitoramento |
| **O3** | 🟢 Oportunidade | Técnico / Arquitetura | Aproveitamento de uma arquitetura modular e escalável para incorporar progressivamente novos fluxos, integrações e capacidades de IA sem reestruturar integralmente a solução. | 3 | 5 | **15** | 🟢 Alta oportunidade | Henrique Diniz | Em Monitoramento |
| **O4** | 🟢 Oportunidade | Processo | Automação proativa de pendências e acompanhamentos recorrentes, reduzindo cobranças manuais do PMO e aumentando a atualização das informações dos projetos. | 4 | 4 | **16** | 🟢 Alta oportunidade | Jaime Almeida | Em Monitoramento |
| **O5** | 🟢 Oportunidade | Dados / Negócio | Reutilização estruturada do conhecimento institucional para apoiar diferentes fluxos do portfólio, evitando duplicação de informações e ampliando o valor da base de conhecimento. | 3 | 4 | **12** | 🟠 Alta oportunidade | Leonardo Ramos | Em Monitoramento |
| **O6** | 🟢 Oportunidade | Análise / Stakeholders | Ampliação da capacidade analítica do PMO por meio de respostas comparativas, perguntas sugeridas e utilização integrada de indicadores e documentos do portfólio. | 3 | 5 | **15** | 🟢 Alta oportunidade | Pedro Uchoa | Em Monitoramento |

---

### 2.7.3 Ações de Tratamento

### R01  - Indisponibilidade ou baixa qualidade dos dados

**Categoria:** Dados  
**Probabilidade:** 4  
**Impacto:** 5  
**Severidade:** 20  - 🔴 Crítica

A solução depende de informações e documentos institucionais para que o agente consiga responder às consultas de maneira contextualizada e fundamentada. A indisponibilidade, incompletude ou baixa qualidade dessas informações pode comprometer diretamente a capacidade do agente de produzir respostas confiáveis.

**Mitigação:** identificar antecipadamente as fontes necessárias, validar sua disponibilidade com o parceiro e estabelecer critérios mínimos de qualidade e completude para os dados e documentos utilizados.

**Contingência:** restringir temporariamente o escopo das consultas às fontes disponíveis e sinalizar explicitamente ao usuário quando não houver informação suficiente para fundamentar uma resposta.

**Responsável:** Jaime Almeida.  
**Status:** Em Monitoramento.

---

### R02  - Dificuldades nas integrações com o ecossistema Microsoft

**Categoria:** Técnico  
**Probabilidade:** 4  
**Impacto:** 5  
**Severidade:** 20  - 🔴 Crítica

A solução está prevista para operar integrada ao ecossistema tecnológico Microsoft, incluindo Microsoft Teams e componentes da Power Platform. Dependências de configuração, permissões, conectores ou limitações das plataformas podem afetar a implementação do agente.

**Mitigação:** validar antecipadamente as integrações necessárias e realizar provas de conceito dos componentes críticos antes da implementação completa dos fluxos.

**Contingência:** utilizar uma interface ou fluxo alternativo disponível no ambiente de desenvolvimento para validar as funcionalidades centrais do agente, mantendo a integração definitiva como etapa posterior.

**Responsável:** Felipe Teixeira.  
**Status:** Em Monitoramento.

---

### R03  - Respostas inadequadas ou não fundamentadas

**Categoria:** Técnico  
**Probabilidade:** 4  
**Impacto:** 5  
**Severidade:** 20  - 🔴 Crítica

Como a solução utiliza Inteligência Artificial para interpretar consultas e gerar respostas, existe o risco de o agente apresentar informações incorretas, incompletas ou sem fundamentação suficiente. Esse risco é particularmente relevante porque a solução pretende apoiar atividades de gestão e disponibilizar informações provenientes das fontes oficiais do Metrô.

**Mitigação:** utilizar fontes documentais controladas, estruturar adequadamente a base de conhecimento, definir mecanismos de validação da qualidade das interações e estabelecer comportamento explícito para situações nas quais não existam informações suficientes.

**Contingência:** fazer com que o agente informe a ausência de informações suficientes e evite apresentar uma resposta como fato quando não houver fonte adequada para fundamentá-la.

**Responsável:** Henrique Diniz.  
**Status:** Em Monitoramento.

---

### R04  - Limitações de autenticação e controle de acesso

**Categoria:** Técnico  
**Probabilidade:** 3  
**Impacto:** 5  
**Severidade:** 15  - 🔴 Crítica

A solução deverá respeitar os diferentes níveis de acesso às informações do portfólio. Uma implementação inadequada das regras de autenticação ou autorização pode permitir acesso indevido ou limitar o acesso legítimo de determinados usuários.

**Mitigação:** definir previamente os perfis de acesso, as permissões associadas a cada perfil e os limites de informação que podem ser disponibilizados pelo agente.

**Contingência:** restringir o acesso às funcionalidades ou fontes que apresentem problemas de autorização até que a configuração seja corrigida e validada.

**Responsável:** Wendel Feitosa.  
**Status:** Em Monitoramento.

---

### R05  - Alteração ou desatualização das fontes

**Categoria:** Dados  
**Probabilidade:** 4  
**Impacto:** 4  
**Severidade:** 16  - 🔴 Crítica

Informações utilizadas pelo agente podem sofrer alterações, atualizações ou substituições ao longo do projeto. Caso a base utilizada pela solução não acompanhe essas mudanças, o agente poderá responder utilizando informações desatualizadas.

**Mitigação:** estabelecer uma estratégia de atualização das fontes e identificar quais documentos possuem caráter prioritário para atualização.

**Contingência:** suspender temporariamente a utilização de uma fonte identificada como desatualizada e informar a necessidade de atualização antes de utilizá-la novamente como referência.

**Responsável:** Leonardo Ramos.  
**Status:** Em Monitoramento.

---

### R06  - Indisponibilidade dos stakeholders

**Categoria:** Stakeholders  
**Probabilidade:** 3  
**Impacto:** 4  
**Severidade:** 12  - 🟠 Alta

A compreensão dos processos do PMO e a validação da solução dependem da participação dos representantes do Metrô. A baixa disponibilidade desses stakeholders pode atrasar decisões e dificultar a validação das funcionalidades.

**Mitigação:** organizar previamente os pontos que dependem de validação do parceiro e concentrar dúvidas e decisões em momentos de alinhamento previamente definidos.

**Contingência:** registrar as decisões pendentes, utilizar apenas informações previamente validadas e postergar funcionalidades cuja implementação dependa de uma definição do parceiro.

**Responsável:** Jaime Almeida.  
**Status:** Aberto.

---

### R07  - Ampliação do escopo

**Categoria:** Escopo  
**Probabilidade:** 4  
**Impacto:** 4  
**Severidade:** 16  - 🔴 Crítica

O levantamento de novas possibilidades para o agente pode gerar solicitações adicionais ao longo do projeto. A incorporação indiscriminada dessas funcionalidades pode aumentar o esforço de desenvolvimento e comprometer as entregas prioritárias.

**Mitigação:** manter uma priorização formal das funcionalidades e diferenciar claramente capacidades essenciais do MVP de oportunidades de evolução futura.

**Contingência:** retirar ou postergar funcionalidades de menor prioridade quando novas demandas forem incorporadas, preservando as funcionalidades essenciais do MVP.

**Responsável:** Pedro Uchoa.  
**Status:** Em Monitoramento.

---

### R08  - Tempo insuficiente para implementação e validação

**Categoria:** Cronograma  
**Probabilidade:** 4  
**Impacto:** 4  
**Severidade:** 16  - 🔴 Crítica

A quantidade de atividades necessárias para compreender o problema, definir requisitos, estruturar a solução, validar as decisões e produzir a documentação pode superar o tempo disponível para o projeto.

**Mitigação:** priorizar as funcionalidades e entregas de maior valor, acompanhar continuamente o progresso e antecipar atividades que possuam dependências com outras tarefas.

**Contingência:** reduzir o escopo da implementação para preservar as capacidades essenciais e registrar funcionalidades secundárias como oportunidades de evolução.

**Responsável:** Felipe Teixeira.  
**Status:** Em Monitoramento.

---

### R09  - Sobrecarga ou indisponibilidade da equipe

**Categoria:** Equipe  
**Probabilidade:** 3  
**Impacto:** 4  
**Severidade:** 12  - 🟠 Alta

A execução simultânea de atividades de análise, documentação, arquitetura, desenvolvimento e validação pode gerar concentração excessiva de trabalho em determinados integrantes.

**Mitigação:** distribuir responsabilidades antecipadamente, acompanhar a carga de trabalho e compartilhar conhecimento sobre atividades críticas.

**Contingência:** redistribuir tarefas entre os integrantes e priorizar atividades diretamente relacionadas às entregas do ciclo atual.

**Responsável:** Henrique Diniz.  
**Status:** Aberto.

---

### R10  - Divergência de entendimento

**Categoria:** Comunicação  
**Probabilidade:** 3  
**Impacto:** 3  
**Severidade:** 9  - 🟡 Moderada

Diferenças de interpretação entre equipe e stakeholders podem gerar requisitos inconsistentes, retrabalho ou desenvolvimento de funcionalidades diferentes da expectativa do parceiro.

**Mitigação:** registrar decisões, requisitos e validações realizadas e utilizar reuniões de alinhamento para esclarecer pontos ambíguos.

**Contingência:** interromper a implementação do item divergente, revisar o entendimento com os envolvidos e atualizar a documentação antes de prosseguir.

**Responsável:** Pedro Uchoa.  
**Status:** Em Monitoramento.

---

### 2.7.4 Oportunidades

### O1  - Aproveitamento do ecossistema Microsoft

**Categoria:** Técnico  
**Probabilidade:** 4  
**Impacto:** 4  
**Potencial:** 16  - 🟢 Alta oportunidade

A utilização de tecnologias já presentes no ambiente corporativo pode facilitar a integração do agente ao cotidiano dos usuários, reduzir barreiras de adoção e aproveitar recursos existentes na organização.

**Estratégia de aproveitamento:** priorizar componentes do ecossistema Microsoft já adotados pelo parceiro sempre que forem tecnicamente adequados ao escopo, validando antecipadamente suas capacidades e limitações.

**Responsável:** Wendel Feitosa.  
**Status:** Em Monitoramento.

---

### O2  - Disponibilização de fontes oficiais e conhecimento do PMO

**Categoria:** Stakeholders / Dados  
**Probabilidade:** 3  
**Impacto:** 5  
**Potencial:** 15  - 🟢 Alta oportunidade

A disponibilização de documentos oficiais, normativos e conhecimento especializado dos representantes do PMO pode aumentar significativamente a qualidade do contexto utilizado pelo agente e permitir respostas mais alinhadas à realidade organizacional.

**Estratégia de aproveitamento:** priorizar as fontes oficiais disponibilizadas pelo parceiro e utilizar o conhecimento dos stakeholders para validar a interpretação dos conteúdos e orientar a construção da base de conhecimento.

**Responsável:** Leonardo Ramos.  
**Status:** Em Monitoramento.

---

### O3  - Arquitetura modular e escalável

**Categoria:** Técnico / Arquitetura  
**Probabilidade:** 3  
**Impacto:** 5  
**Potencial:** 15  - 🟢 Alta oportunidade

A concepção de uma arquitetura modular e escalável pode permitir que novas capacidades de Inteligência Artificial, fluxos de negócio e integrações sejam incorporados progressivamente sem necessidade de reestruturar integralmente a solução.

Essa oportunidade é coerente com a necessidade de construir uma solução preparada para futuras melhorias e evoluções, mantendo flexibilidade para ampliar suas capacidades ao longo do tempo.

**Estratégia de aproveitamento:** definir componentes e responsabilidades de forma modular, mantendo interfaces e dependências suficientemente desacopladas para permitir substituições ou extensões futuras.

**Responsável:** Henrique Diniz.  
**Status:** Em Monitoramento.

---

### O4  - Automação proativa de pendências

**Categoria:** Processo  
**Probabilidade:** 4  
**Impacto:** 4  
**Potencial:** 16  - 🟢 Alta oportunidade

A solução possui potencial para evoluir de uma experiência predominantemente reativa, baseada em consultas dos usuários, para uma atuação proativa capaz de identificar pendências e apoiar sua resolução.

Essa oportunidade está diretamente alinhada à necessidade identificada para que o agente lembre e ofereça apoio em pendências de preenchimento e acompanhe informações dos projetos.

**Estratégia de aproveitamento:** identificar inicialmente os eventos recorrentes e de maior valor operacional que possam gerar lembretes ou ações proativas, priorizando aqueles que apresentem regras claras e baixo risco de interpretação.

**Responsável:** Jaime Almeida.  
**Status:** Em Monitoramento.

---

### O5  - Reutilização do conhecimento institucional

**Categoria:** Dados / Negócio  
**Probabilidade:** 3  
**Impacto:** 4  
**Potencial:** 12  - 🟠 Alta oportunidade

A organização estruturada do conhecimento utilizado pelo agente pode permitir seu reaproveitamento em diferentes fluxos de gestão do portfólio, reduzindo duplicação de informações e ampliando o valor dos mesmos conteúdos institucionais.

Essa oportunidade pode favorecer a expansão da solução para diferentes necessidades do ciclo de vida dos projetos sem exigir a construção independente de bases para cada nova funcionalidade.

**Estratégia de aproveitamento:** organizar as fontes e conceitos de maneira reutilizável, preservando metadados e relações que permitam sua utilização por diferentes fluxos do agente.

**Responsável:** Leonardo Ramos.  
**Status:** Em Monitoramento.

---

### O6  - Ampliação da capacidade analítica

**Categoria:** Análise / Stakeholders  
**Probabilidade:** 3  
**Impacto:** 5  
**Potencial:** 15  - 🟢 Alta oportunidade

O agente pode evoluir para além de consultas isoladas, apoiando análises comparativas entre projetos, perguntas sugeridas e utilização conjunta de documentos e indicadores do portfólio.

Essa oportunidade é especialmente relevante para aumentar o valor estratégico da solução para o PMO, uma vez que a proposta contempla apoio à análise e comparação de projetos e utilização de perguntas sugeridas para orientar os usuários.

**Estratégia de aproveitamento:** priorizar inicialmente análises com critérios claramente definidos e fontes confiáveis, evoluindo posteriormente para comparações mais abrangentes conforme a qualidade e disponibilidade das informações.

**Responsável:** Pedro Uchoa.  
**Status:** Em Monitoramento.

---

### 2.7.5 Matriz Probabilidade × Impacto

A representação gráfica abaixo utiliza a probabilidade no eixo vertical e o impacto no eixo horizontal. Os identificadores dos riscos são posicionados conforme suas respectivas avaliações:

<div align="center">
  <img src="img/Matriz-de-risco.png" alt="Matriz de probabilidade por impacto com o posicionamento dos riscos e oportunidades do projeto" width="800">
  <p><strong>Figura 11</strong> - Matriz Probabilidade × Impacto.</p>
  <sup>Fonte: Material produzido pelos autores, 2026.</sup>
</div>

---

### 2.7.6 Análise dos Três Itens Mais Críticos

A aplicação da regra **Severidade = Probabilidade × Impacto** identifica três itens com a maior pontuação da matriz: **R01, R02 e R03**, todos com severidade **20**, correspondendo à combinação de probabilidade alta (4) e impacto muito alto (5).

### R01  - Indisponibilidade ou baixa qualidade dos dados

O risco relacionado aos dados é considerado crítico porque o agente responde exclusivamente a partir das fontes que recebe como contexto. Não há conhecimento próprio a que recorrer quando a fonte falha.

Dessa forma, dados incompletos, indisponíveis ou inconsistentes não representam apenas um problema operacional de alimentação da solução, mas podem comprometer diretamente a principal finalidade do produto: disponibilizar informações confiáveis aos usuários.

Por esse motivo, a disponibilidade e a qualidade das fontes devem ser acompanhadas desde as primeiras etapas do projeto.

---

### R02  - Dificuldades nas integrações com o ecossistema Microsoft

A integração tecnológica também possui criticidade elevada porque a solução foi concebida para operar no ecossistema Microsoft, utilizando componentes como **Teams, SharePoint e Power Platform**.

Problemas relacionados a permissões, conectores, configurações ou limitações das plataformas podem impedir que funcionalidades que dependem dessas integrações sejam implementadas conforme planejado. Além disso, uma dificuldade de integração pode gerar impacto simultaneamente sobre desenvolvimento, validação e cronograma.

Por isso, a realização de validações técnicas antecipadas é uma das principais estratégias de redução desse risco.

---

### R03  - Respostas inadequadas ou não fundamentadas

O terceiro risco crítico está relacionado ao próprio comportamento da Inteligência Artificial. O agente deverá interpretar solicitações em linguagem natural e disponibilizar respostas contextualizadas, seguras e fundamentadas nas fontes oficiais.

Uma resposta incorreta ou sem fundamentação pode comprometer a confiança dos usuários na solução e reduzir seu valor para o PMO. Esse risco possui impacto elevado justamente porque a qualidade da resposta é um dos elementos centrais da proposta de valor do produto.

Por esse motivo, a estratégia deve priorizar fontes controladas, mecanismos de fundamentação, validação das respostas e comportamento explícito para situações nas quais não existam informações suficientes.

---

### 2.7.7 Acompanhamento da Matriz

A matriz deverá ser revisada durante a evolução do projeto, especialmente quando ocorrerem mudanças relevantes no escopo, arquitetura, disponibilidade de dados, integração com sistemas corporativos ou entendimento das necessidades dos stakeholders.

A atualização deverá considerar:

- inclusão de novos riscos identificados durante o desenvolvimento;
- alteração da probabilidade ou impacto de riscos existentes;
- atualização dos responsáveis;
- registro das ações de mitigação e contingência realizadas;
- atualização do status dos riscos;
- encerramento de riscos que deixarem de representar ameaça ao projeto;
- registro de novas oportunidades identificadas durante a evolução da solução.

Dessa forma, a matriz não deve ser tratada apenas como um artefato documental, mas como um instrumento de acompanhamento contínuo das condições que podem afetar a execução e os resultados do projeto.

A análise realizada evidencia que os principais pontos de atenção estão concentrados na **qualidade e disponibilidade dos dados, nas dependências de integração tecnológica e na confiabilidade das respostas produzidas pela Inteligência Artificial**. Esses fatores possuem relação direta com a proposta central do produto e, por isso, devem permanecer sob acompanhamento prioritário ao longo das próximas etapas do projeto.

---

## 2.8 Ideação

Esta seção consolida o processo de ideação realizado pela equipe durante as etapas de entendimento do negócio, brainstorming e validação inicial com os representantes do Metrô. O objetivo é registrar as funcionalidades identificadas como oportunidades para o produto, independentemente de sua implementação imediata, preservando um histórico das necessidades levantadas e das possibilidades de evolução da solução.

As ideias foram priorizadas por dois critérios, ambos avaliados em escala de 1 a 5:

- **Importância para o negócio:** potencial de geração de valor para o PMO e para os diferentes perfis de usuários;
- **Viabilidade para o MVP:** possibilidade de implementação dentro do escopo, prazo e recursos disponíveis para a primeira versão da solução.

#### Regra de priorização

A faixa de prioridade é o resultado do produto entre os dois critérios, conforme os intervalos abaixo. A regra é aplicada de forma uniforme a todas as features: nenhuma decisão da tabela foi tomada fora dela.

| Produto (Importância × Viabilidade) | Faixa |
| :---: | --- |
| 16 a 25 | 🔴 Muito Alta |
| 10 a 15 | 🟠 Alta |
| 6 a 9 | 🟡 Média |
| 1 a 5 | 🟢 Evolução |

**Regra de exceção — elevação por pré-requisito ou por escopo contratado.** Uma feature é elevada em uma faixa acima do resultado do produto, ainda que sua viabilidade seja baixa, quando se enquadra em um dos dois casos abaixo. A elevação é sinalizada na coluna de faixa e obrigatoriamente justificada; nenhuma outra feature da tabela foi movida de faixa.

1. **Pré-requisito de uso** — a feature é condição de acesso ao produto ou de aderência ao canal corporativo esperado pelo Metrô. Sua ausência impede o uso das demais, e não apenas reduz o valor entregue. Aplicada à **integração com o Microsoft Teams**, cuja viabilidade é 3 por depender de homologação da GTI, mas que é o canal onde o agente será efetivamente utilizado — sem ela, o produto não tem superfície de entrega.
2. **Escopo contratado** — a feature consta do escopo macro do Termo de Abertura do Projeto Inteli e, portanto, não é negociável por conveniência de implementação. Aplicada à **transcrição de áudio**, que o TAPI define como modalidade de entrada do agente e que, por isso, tem importância 5 mesmo com viabilidade 3. O benchmark de APIs e a escolha do provedor estão registrados na Seção 8.8.

#### Linha de corte do MVP

**A linha de corte do MVP é a faixa Muito Alta.** As sete features nessa faixa compõem o escopo desenvolvido e validado neste módulo e correspondem aos requisitos funcionais RF01 a RF08 da Seção 3.1. As faixas Alta e Média formam o backlog priorizado para depois do MVP: são features aceitas pelo produto, com valor reconhecido, cuja implementação depende de tempo ou de integrações ainda não disponíveis. A faixa Evolução reúne o que depende de condições fora do horizonte do projeto.

#### Matriz de priorização das features

| Feature | Importância | Viabilidade | Produto | Faixa | Escopo | Justificativa da priorização |
| --- | :---: | :---: | :---: | --- | --- | --- |
| Consulta de informações dos projetos | 5 | 5 | 25 | 🔴 Muito Alta | MVP | Resolve a dor central de acesso rápido às informações do portfólio e é a base de funcionamento do agente. |
| Ingestão de informações dos projetos | 5 | 4 | 20 | 🔴 Muito Alta | MVP | Sustenta a base de conhecimento consultada pelo agente, ainda que no MVP opere sobre dados sintéticos. |
| Preenchimento assistido de documentos | 5 | 4 | 20 | 🔴 Muito Alta | MVP | Entrevista guiada que gera o Mapa de Benefícios, artefato piloto das transações e processo modelado na Seção 2.6. |
| Autenticação e definição de perfis | 5 | 4 | 20 | 🔴 Muito Alta | MVP | Condição para que a resposta respeite as permissões de cada usuário, exigência de confidencialidade do parceiro. |
| Perfil de linguagem executivo | 4 | 4 | 16 | 🔴 Muito Alta | MVP | Adapta a profundidade da resposta ao cargo sem ampliar o núcleo funcional já construído. |
| Integração com Microsoft Teams | 5 | 3 | 15 | 🔴 Muito Alta *(elevada)* | MVP | Produto 15 posiciona na faixa Alta; elevada pela regra de exceção por ser o canal corporativo em que o agente é utilizado. |
| Transcrição de áudio | 5 | 3 | 15 | 🔴 Muito Alta *(elevada)* | MVP | Produto 15 posiciona na faixa Alta; elevada pela regra de exceção por ser modalidade de entrada prevista no escopo contratado. Viabilidade 3 reflete a dependência de API externa de transcrição, escolhida na Seção 8.8. |
| Diferença de profundidade de pesquisa | 4 | 3 | 12 | 🟠 Alta | Pós-MVP | Melhora a experiência de consulta, porém só faz sentido depois que a consulta básica estiver estável. |
| Fluxo de avaliação das respostas | 3 | 3 | 9 | 🟡 Média | Pós-MVP | Alimenta a melhoria contínua do agente, mas não bloqueia a validação da prova de conceito. |
| Interface personalizada e intuitiva | 3 | 3 | 9 | 🟡 Média | Pós-MVP | Relevante para a adoção por usuários sem perfil técnico; no MVP a interface é a do próprio Teams. |
| Fluxo de lembretes de atualização dos projetos | 4 | 2 | 8 | 🟡 Média | Pós-MVP | Reduz a cobrança manual do PMO, porém depende de regras de varredura e de integrações transacionais. |
| Relatório anual automático | 4 | 2 | 8 | 🟡 Média | Pós-MVP | Tem valor para a gestão, mas exige templates institucionais e consolidação documental mais madura. |
| Apresentações automáticas por template | 3 | 2 | 6 | 🟡 Média | Pós-MVP | Útil para a rotina executiva, secundária frente ao pipeline de consulta e à geração de documentos. |
| Integração com Power BI | 4 | 1 | 4 | 🟢 Evolução | Evolução | Depende de integração corporativa e de permissões fora do alcance do projeto acadêmico. |
| Edição das configurações do agente por menu | 2 | 2 | 4 | 🟢 Evolução | Evolução | Facilita a manutenção futura, mas não contribui para validar o valor do MVP. |
| Fluxo de notificações de riscos | 4 | 1 | 4 | 🟢 Evolução | Evolução | Exige automações e regras de alerta mais estáveis do que as previstas para a primeira versão. |

---

### 2.8.1 Descrição das Features Priorizadas

As funcionalidades levantadas durante o processo de ideação foram analisadas considerando sua relevância para os objetivos do produto, o valor potencial para os usuários e a viabilidade de desenvolvimento dentro das diferentes etapas do projeto. A seguir, são apresentadas as descrições das features priorizadas, organizadas de acordo com o nível de prioridade estabelecido na matriz de ideação.

#### 🔴 Muito Alta

**Consulta de informações dos projetos**

Permite que o usuário consulte informações relacionadas aos projetos do portfólio por meio de linguagem natural, incluindo dados de acompanhamento, cronogramas, Termos de Abertura do Projeto (TAP), indicadores e demais informações disponibilizadas pelas fontes integradas à solução. Essa funcionalidade constitui o principal ponto de interação entre o usuário e o agente.

**Ingestão de informações dos projetos**

Responsável por incorporar à base de conhecimento da solução as informações provenientes das fontes utilizadas pelo PMO. A funcionalidade permite estruturar os dados e documentos necessários para que o agente consiga realizar consultas contextualizadas e fornecer respostas fundamentadas nas informações disponibilizadas pela organização.

**Preenchimento assistido de documentos**

Conduz o líder do projeto por uma entrevista guiada que coleta programa ou projeto, entregas, resultados, benefícios e objetivos estratégicos, valida as regras de preenchimento e gera o documento estruturado ao final. O Mapa de Benefícios é o artefato piloto desta funcionalidade e o processo que ela apoia está modelado nos fluxos AS-IS e TO-BE da Seção 2.6.

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

#### 🟡 Média

**Fluxo de lembretes de atualização dos projetos**

Possibilita a criação de mecanismos de comunicação para lembrar os responsáveis pela necessidade de atualização das informações dos projetos. A funcionalidade busca apoiar o PMO na manutenção da atualidade da base de informações e reduzir a necessidade de cobranças realizadas manualmente.

**Relatório anual automático**

Permite utilizar as informações consolidadas do portfólio para apoiar a geração automatizada de relatórios anuais. A funcionalidade busca reduzir o esforço associado à consolidação manual das informações e facilitar a preparação de materiais recorrentes utilizados pela gestão.

**Apresentações automáticas por template**

Permite gerar apresentações a partir de informações disponíveis no portfólio, utilizando modelos previamente definidos pela organização. A funcionalidade busca facilitar a preparação de materiais executivos e reduzir atividades repetitivas relacionadas à organização das informações em apresentações.

**Fluxo de avaliação das respostas**

Disponibiliza mecanismos para que os usuários avaliem as respostas fornecidas pelo agente. Os registros obtidos podem ser utilizados para identificar problemas recorrentes, avaliar a qualidade das interações e orientar futuras melhorias da solução.

**Interface personalizada e intuitiva**

Busca proporcionar uma experiência de interação simples, clara e adequada aos diferentes perfis de usuários. No MVP a interface é a do próprio Microsoft Teams, o que já cobre a familiaridade das equipes com o ambiente; a personalização entra depois, quando o volume de uso justificar afastar-se do canal padrão.

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

## 2.9 Canvas de Proposta de Valor

O Canvas de Proposta de Valor funciona como um instrumento estratégico para conectar as funcionalidades de uma solução às necessidades reais dos seus usuários. Por meio dele, torna-se possível compreender com clareza quais são as tarefas, dores e ganhos esperados pelos clientes, permitindo que o produto seja desenhado para gerar valor de forma objetiva, mensurável e aderente ao contexto organizacional.

<div align="center">
  <img src="img/canvas-proposta-valor.png" alt="Canvas de Proposta de Valor do agente de IA para a gestão do portfólio de projetos do Metrô" width="900">
  <p><strong>Figura 12</strong> - Canvas de Proposta de Valor.</p>
  <sup>Fonte: Material produzido pelos autores, 2026.</sup>
</div>

A proposta de valor desenvolvida tem como foco apoiar o Metrô na otimização da gestão de seu portfólio de projetos, utilizando um agente com Processamento de Linguagem Natural integrado ao ecossistema Microsoft. A solução busca reduzir o esforço operacional envolvido no cadastro, acompanhamento e reporte de projetos, ao mesmo tempo em que aumenta a qualidade, a padronização e a disponibilidade das informações para tomada de decisão. Dessa forma, o perfil do cliente contempla principalmente o PMO, os líderes de projeto e a diretoria do Metrô.

Esses grupos correspondem às personas apresentadas na Seção 2.5. A diretoria é representada por Roberto, o PMO Corporativo por Mariana e a gerência de portfólio por Carlos. Os líderes de projeto formam o quarto grupo atendido pela solução e são os responsáveis por alimentar os documentos de cada projeto e manter o avanço atualizado.

**Ganhos esperados**: no canvas, aparecem como visão executiva do portfólio, relatórios gerados mais rápido e projetos atualizados com mais frequência. Eles destacam a busca por maior agilidade na gestão do portfólio, melhor qualidade das informações e maior visibilidade executiva sobre o andamento dos projetos. O principal desejo é transformar dados dispersos em informações confiáveis, acessíveis e acionáveis, permitindo que o PMO acompanhe pendências com mais eficiência, que líderes atualizem seus projetos com menos esforço e que a diretoria receba relatórios objetivos para apoiar decisões estratégicas.

**Tarefas do cliente**: no canvas, aparecem como cadastrar novos projetos, consolidar status para a diretoria e monitorar riscos e pendências. Elas giram em torno da necessidade de estruturar, acompanhar e reportar projetos de forma contínua. Os líderes de projeto precisam preencher documentos como o Termo de Abertura, o Mapa de Benefícios, cronogramas e atualizações de avanço físico-financeiro. O PMO precisa monitorar a qualidade desses registros, cobrar atualizações, consolidar dados e identificar riscos ou atrasos. Já a diretoria precisa consultar resumos executivos claros, com foco em status, riscos, marcos relevantes e evolução dos projetos do portfólio.

**Dores**: no canvas, aparecem como preenchimento manual demorado, relatórios executivos trabalhosos e cronogramas com inconsistências. Elas se traduzem no alto esforço manual para preencher documentos, consolidar planilhas e preparar relatórios executivos. Além disso, há dificuldade em manter as informações atualizadas no SharePoint, risco de inconsistências em cronogramas e avanços, baixa padronização dos registros e dependência de cobranças manuais por parte do PMO. Outro desafio relevante está na necessidade de interpretar rapidamente informações de múltiplas fontes, como arquivos Excel, listas do SharePoint e interações no Teams, sem comprometer a segurança e o controle de acesso corporativo.

Para responder a essas demandas, desenvolvemos uma solução composta por três frentes:

**Analgésicos**: no canvas, aparecem como entrevista guiada para documentos, redução do retrabalho do PMO e cobrança de atualizações via Teams. Eles atuam diretamente na redução das dores identificadas e incluem um agente conversacional capaz de conduzir entrevistas guiadas para preenchimento de documentos, diminuindo a complexidade de formulários estáticos. A solução também valida regras críticas, como a soma dos pesos do cronograma em 100%, coerência de datas e presença de campos obrigatórios. Além disso, o agente envia alertas proativos via Teams para cobrar atualizações de avanço e riscos, reduzindo a dependência de acompanhamento manual pelo PMO.

**Produtos e serviços**: no canvas, aparecem como agente conversacional com PLN, entrada de status por texto ou voz e geração de relatórios executivos. Eles são representados por um agente de IA integrado ao SharePoint, Teams e Excel. Esse agente permite a criação assistida de TAPs, Mapas de Benefícios e cronogramas, interpreta arquivos anexados, recebe atualizações por texto ou voz e gera relatórios executivos de status mensal. A solução também contempla filtros de segurança e escopo, adaptando o nível de detalhamento das respostas conforme o perfil do usuário, como líderes de projeto, PMO ou diretoria.

**Criadores de ganhos**: no canvas, aparecem como automatiza relatórios do portfólio, destaca riscos e marcos críticos e acelera a tomada de decisão. Eles agregam valor ao oferecer maior velocidade, consistência e inteligência ao ciclo de gestão de projetos. O agente gera rascunhos estruturados de documentos, recomenda melhorias no preenchimento, consolida informações físico-financeiras, destaca os principais riscos e marcos recentes e produz relatórios executivos de forma automatizada. Com isso, o PMO ganha tempo para atuar de forma mais estratégica, os líderes reduzem o esforço de atualização e a diretoria passa a contar com uma visão mais clara, confiável e atualizada do portfólio.

O canvas representa a proposta de valor completa do agente, considerando todo o ciclo de vida dos projetos no portfólio. O MVP desenvolvido neste módulo cobre um recorte dessa proposta, formalizado nos requisitos funcionais da Seção 3.1. As funcionalidades mínimas dessa primeira versão são receber comandos em linguagem natural, identificar a intenção do usuário e classificá-la em consulta, transação ou alerta, recuperar as informações dos documentos e dados sintéticos disponibilizados ao pipeline, responder às consultas, comparar informações entre projetos e devolver respostas estruturadas, indicando quando não houver informação suficiente para atender à solicitação.

Esse recorte se justifica por três motivos. O primeiro é que o pipeline de PLN sustenta todos os outros itens do canvas, já que sem a identificação correta da intenção nenhuma consulta ou transação funciona. O segundo é que a validação acontece sobre dados sintéticos, o que permite testar o ciclo completo sem depender da liberação de acesso ao portfólio real e sem tratar informações sensíveis fora de ambiente homologado. O terceiro é que o Mapa de Benefícios foi escolhido como documento piloto das transações do agente, por ser o artefato de entrada do ciclo de vida do projeto e por já estar modelado nos fluxos AS-IS e TO-BE apresentados na Seção 2.6.

Ficam como evolução prevista a integração com o portfólio real do Metrô, a cobrança automática de atualizações via Teams no ambiente corporativo, a extensão do preenchimento assistido aos demais documentos do ciclo e a integração com o Power BI.

Dessa forma, nosso principal objetivo é auxiliar o Metrô a otimizar a gestão de seu portfólio de projetos por meio de um agente inteligente, conversacional e integrado ao ambiente corporativo já utilizado pela organização. A solução fortalece a governança, reduz retrabalho, melhora a qualidade dos dados e apoia decisões mais rápidas e assertivas, contribuindo para uma gestão de projetos mais eficiente, padronizada e orientada por informações confiáveis.

---

## 2.10 Business Drivers

Os Business Drivers representam os principais fatores de negócio que motivam o desenvolvimento da solução e orientam os resultados esperados com sua implementação. No contexto deste projeto, esses direcionadores estabelecem a relação entre as necessidades identificadas na Gestão de Portfólio de Projetos do Metrô e as capacidades proporcionadas pelo Processamento de Linguagem Natural (PLN).

Atualmente, o PMO possui processos estruturados para gestão e acompanhamento do portfólio, porém atividades relacionadas à localização, consolidação e análise das informações ainda dependem de ações manuais. A distribuição das informações entre diferentes documentos e fontes aumenta o esforço necessário para responder consultas, acompanhar projetos e realizar análises envolvendo diferentes iniciativas do portfólio.

A aplicação de PLN busca modificar esse cenário ao permitir que o usuário expresse sua necessidade diretamente em linguagem natural. A solução passa a interpretar a solicitação, identificar sua intenção, recuperar as informações necessárias e produzir uma saída adequada ao contexto identificado. Dessa forma, a tecnologia atua como uma camada de acesso às informações do portfólio, reduzindo a necessidade de o usuário conhecer previamente a localização ou a estrutura dos dados consultados.

Além da eficiência na obtenção das informações, a confiabilidade constitui um aspecto relevante para o negócio. Como as respostas produzidas pelo agente podem ser utilizadas para acompanhamento dos projetos e apoio à tomada de decisão, é necessário reduzir a ocorrência de informações não sustentadas pelos dados disponíveis. Dessa forma, a avaliação da solução considera tanto indicadores positivos de desempenho quanto indicadores negativos, como a taxa de alucinação.

Considerando o problema identificado, os objetivos do projeto e os limites estabelecidos para o MVP, foram definidos os seguintes Business Drivers.

### 2.10.1 Business Drivers do Projeto

| ID   | Business Driver                                   | Necessidade de negócio                                                                                                               | Aplicação de PLN                                                                                                                                                                   | Resultado esperado                                                                                       |
| ---- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| BD01 | Agilizar o acesso às informações dos projetos     | Reduzir o esforço e o tempo empregados na localização e consolidação manual de informações distribuídas nos documentos dos projetos. | Interpretar consultas realizadas em linguagem natural, identificar a intenção do usuário e recuperar as informações relacionadas à solicitação.                                    | Acesso mais rápido às informações necessárias para acompanhamento dos projetos.                          |
| BD02 | Ampliar a capacidade de análise do portfólio      | Facilitar a obtenção de análises que atualmente exigem consulta e consolidação manual de informações de um ou mais projetos.         | Interpretar solicitações analíticas, recuperar informações relevantes e estruturar análises ou comparações entre projetos.                                                         | Maior agilidade na obtenção de informações para acompanhamento do portfólio e apoio à tomada de decisão. |
| BD03 | Aumentar a confiabilidade das respostas           | Reduzir inconsistências e o risco de respostas não sustentadas pelas informações disponibilizadas para processamento.                | Fundamentar as respostas nas informações recuperadas da base utilizada pelo pipeline e identificar situações nas quais não existam dados suficientes para responder adequadamente. | Respostas mais confiáveis, fundamentadas e adequadas às informações disponíveis.                         |
| BD04 | Tornar a interação com o portfólio mais acessível | Reduzir a dependência do conhecimento sobre a estrutura dos documentos e sistemas utilizados para localizar informações.             | Permitir que diferentes formulações em linguagem natural sejam interpretadas e associadas às intenções suportadas pelo agente.                                                     | Maior autonomia dos usuários para consultar informações relacionadas ao portfólio.                       |

### 2.10.2 Indicadores Computacionais

Para avaliar se as capacidades de PLN contribuem efetivamente para os direcionadores definidos, são utilizados indicadores computacionais associados às principais etapas do pipeline. Esses indicadores permitem verificar não apenas o funcionamento técnico da solução, mas também sua capacidade de produzir resultados compatíveis com as necessidades de negócio identificadas.

Os indicadores selecionados concentram-se na capacidade do sistema de compreender corretamente as solicitações, recuperar informações pertinentes, produzir respostas fundamentadas e realizar esse processamento de maneira eficiente. Também é considerada a ocorrência de alucinações como indicador negativo, uma vez que informações não sustentadas pela base utilizada podem comprometer a confiabilidade da solução.

| Indicador                              | O que avalia                                                                                                                                     | Relação com o negócio                                                                                                                                   |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Acurácia da classificação de intenção  | Percentual de solicitações cuja intenção é corretamente identificada pelo pipeline.                                                              | Indica a capacidade do agente de compreender a necessidade do usuário e direcioná-la ao fluxo adequado.                                                 |
| Precisão da recuperação de informações | Proporção das informações recuperadas que são relevantes para a solicitação realizada.                                                           | Contribui para respostas mais confiáveis e reduz informações irrelevantes durante consultas e análises.                                                 |
| Cobertura da recuperação               | Capacidade de recuperar as informações relevantes existentes na base para determinada solicitação.                                               | Reduz a possibilidade de informações importantes serem omitidas nas respostas.                                                                          |
| Taxa de respostas fundamentadas        | Proporção de respostas cujas informações podem ser relacionadas aos dados utilizados pelo pipeline.                                              | Avalia a confiabilidade e a rastreabilidade das informações apresentadas pelo agente.                                                                   |
| Taxa de alucinação ↓                   | Percentual de respostas que apresentam informações factuais não sustentadas ou contraditórias em relação aos dados disponibilizados ao pipeline. | Indicador negativo a ser minimizado, pois respostas não fundamentadas podem gerar desinformação e comprometer a confiança e a tomada de decisão do PMO. |
| Tempo de processamento                 | Tempo entre o recebimento da solicitação e a disponibilização da resposta.                                                                       | Permite avaliar a agilidade proporcionada pelo novo fluxo de consulta e análise.                                                                        |

A taxa de alucinação é tratada como um indicador negativo de qualidade, portanto, quanto menor seu valor, melhor o desempenho esperado da solução. Sua avaliação é especialmente relevante no contexto do projeto, uma vez que o agente deve utilizar as informações disponibilizadas como fundamento para suas respostas, evitando apresentar como fato informações inexistentes, não recuperadas ou contraditórias em relação à base utilizada.

Os indicadores deverão ser avaliados utilizando os dados sintéticos definidos para a prova de conceito, respeitando a delimitação estabelecida para o MVP. Caso a entrada por áudio seja incorporada à avaliação da solução, poderão ser utilizados adicionalmente indicadores específicos relacionados à qualidade da transcrição.

### 2.10.3 Fluxos de Negócio Impactados

A aplicação de PLN modifica principalmente a forma como os usuários acessam e analisam as informações relacionadas ao portfólio. Em vez de depender exclusivamente da localização manual de documentos e da consolidação das informações encontradas, o usuário passa a iniciar esses processos por meio de uma solicitação em linguagem natural.

Dentro do escopo definido para o MVP, dois fluxos representam diretamente essa transformação: a consulta de informações de um projeto e a análise e comparação de informações entre projetos.

#### 2.10.3.1 Fluxo 1 — Consulta de Informações de Projetos

No processo atual, a obtenção de uma informação específica sobre determinado projeto pode exigir que o usuário identifique onde a informação está armazenada, localize o documento correspondente e consulte seu conteúdo para encontrar o dado desejado. Dependendo da natureza da solicitação, também pode ser necessário consultar diferentes fontes ou consolidar informações manualmente.

Com a solução proposta, o usuário passa a iniciar o processo diretamente por meio de uma solicitação em linguagem natural. Uma pergunta como "Qual o prazo do Projeto XPTO?", por exemplo, é recebida pelo pipeline de PLN, que interpreta o comando, identifica a intenção correspondente, recupera as informações relacionadas ao projeto e estrutura a resposta.

O fluxo proposto pode ser representado da seguinte maneira:

**Solicitação em linguagem natural → processamento da linguagem → identificação e classificação da intenção → recuperação das informações → estruturação da resposta → apresentação ao usuário.**

| Elemento               | Descrição                                                                                                                                                               |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Entrada                | Solicitação do usuário em linguagem natural relacionada a informações disponíveis sobre determinado projeto.                                                            |
| Processamento esperado | Interpretação da solicitação, identificação e classificação da intenção, recuperação das informações relevantes e estruturação da resposta.                             |
| Saída                  | Resposta relacionada à informação solicitada e fundamentada nos dados disponíveis.                                                                                      |
| Indicadores            | Acurácia da classificação de intenção, precisão da recuperação, cobertura da recuperação, taxa de respostas fundamentadas, taxa de alucinação e tempo de processamento. |
| Ganho esperado         | Redução do esforço e do tempo necessários para localizar e consultar informações dos projetos, aumentando a autonomia do usuário.                                       |

Esse fluxo está diretamente relacionado aos Business Drivers BD01, BD03 e BD04.

A classificação correta da intenção é especialmente importante nesse processo, pois determina como a solicitação deverá ser tratada pelo pipeline. Da mesma forma, a precisão e a cobertura da recuperação permitem avaliar se o sistema encontrou as informações adequadas, enquanto a taxa de respostas fundamentadas e a taxa de alucinação permitem avaliar a confiabilidade do conteúdo apresentado.

#### 2.10.3.2 Fluxo 2 — Análise e Comparação entre Projetos

Além das consultas individuais, a gestão do portfólio exige a análise conjunta de informações provenientes de diferentes projetos. Atualmente, esse processo pode exigir a localização das informações de cada iniciativa e sua posterior consolidação para permitir a comparação dos elementos relevantes.

Com a utilização de PLN, o usuário poderá formular diretamente uma solicitação analítica, especificando os projetos e os aspectos que deseja comparar. A solicitação pode envolver, por exemplo, a comparação de status, riscos, marcos, prazos ou avanço entre diferentes projetos disponíveis na base utilizada pela solução.

O pipeline deverá interpretar a solicitação, identificar sua intenção, reconhecer os projetos e critérios envolvidos, recuperar as informações correspondentes e estruturar os resultados de maneira que facilite sua interpretação pelo usuário.

O fluxo proposto pode ser representado da seguinte maneira:

**Solicitação analítica em linguagem natural → identificação da intenção → identificação dos projetos e critérios → recuperação das informações → análise e comparação → estruturação dos resultados → apresentação ao usuário.**

| Elemento               | Descrição                                                                                                                                                                      |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Entrada                | Solicitação em linguagem natural contendo os projetos e/ou critérios que deverão ser analisados.                                                                               |
| Processamento esperado | Identificação da intenção analítica, identificação dos projetos e critérios relevantes, recuperação das informações correspondentes, comparação e estruturação dos resultados. |
| Saída                  | Resposta estruturada apresentando as informações relevantes para análise e comparação dos projetos.                                                                            |
| Indicadores            | Acurácia da classificação de intenção, precisão da recuperação, cobertura da recuperação, taxa de respostas fundamentadas, taxa de alucinação e tempo de processamento.        |
| Ganho esperado         | Redução do esforço necessário para consolidar informações e maior agilidade na realização de análises para acompanhamento do portfólio e apoio à tomada de decisão.            |

Esse fluxo está diretamente relacionado aos Business Drivers BD02 e BD03.

Nesse fluxo, a confiabilidade possui importância ainda maior, pois a resposta pode combinar informações provenientes de diferentes projetos. A redução da taxa de alucinação e a manutenção de uma elevada taxa de respostas fundamentadas contribuem para evitar que informações inexistentes ou inferências não sustentadas sejam apresentadas ao usuário como fatos durante uma análise comparativa.

### 2.10.4 Relação entre Business Drivers, Fluxos e Indicadores

Os Business Drivers, fluxos de negócio e indicadores computacionais estabelecem diferentes níveis de avaliação da transformação proposta. Os Business Drivers representam os resultados desejados para o negócio; os fluxos demonstram como a interação atual é modificada pela aplicação de PLN; e os indicadores permitem avaliar quantitativamente o desempenho das capacidades computacionais responsáveis por essa transformação.

| Business Driver                                          | Fluxo relacionado                   | Principais indicadores                                                                                               |
| -------------------------------------------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| BD01 — Agilizar o acesso às informações dos projetos     | Consulta de informações de projetos | Acurácia da intenção, precisão e cobertura da recuperação e tempo de processamento.                                  |
| BD02 — Ampliar a capacidade de análise do portfólio      | Análise e comparação entre projetos | Acurácia da intenção, precisão e cobertura da recuperação, tempo de processamento e taxa de respostas fundamentadas. |
| BD03 — Aumentar a confiabilidade das respostas           | Ambos os fluxos                     | Taxa de respostas fundamentadas e taxa de alucinação.                                                                |
| BD04 — Tornar a interação com o portfólio mais acessível | Consulta de informações de projetos | Acurácia da classificação de intenção e capacidade de interpretação das solicitações em linguagem natural.           |

Essa relação permite que a avaliação técnica do pipeline seja associada aos resultados esperados para o negócio. Uma elevada acurácia na identificação das intenções, por exemplo, possui valor para o PMO porque permite que as solicitações sejam direcionadas corretamente. Da mesma forma, uma elevada precisão na recuperação das informações contribui para respostas mais pertinentes, enquanto uma baixa taxa de alucinação contribui diretamente para a confiabilidade das informações apresentadas.

### 2.10.5 Impacto Esperado no Negócio

A principal transformação proposta pelo projeto não consiste na substituição dos processos de gestão de projetos existentes, mas na mudança da forma como os usuários interagem com as informações produzidas e utilizadas nesses processos. O PLN introduz uma camada capaz de transformar solicitações expressas naturalmente pelos usuários em operações estruturadas sobre as informações disponíveis.

Dessa forma, atividades que atualmente exigem busca, leitura e consolidação manual passam a ser apoiadas por um pipeline capaz de compreender a intenção da solicitação, recuperar informações e organizar os resultados. Essa transformação busca reduzir o esforço operacional associado às consultas, aumentar a agilidade das análises e ampliar a autonomia dos usuários no acesso às informações relacionadas ao portfólio.

Ao mesmo tempo, a aplicação de Inteligência Artificial introduz a necessidade de controlar a confiabilidade das respostas produzidas. Por esse motivo, o ganho de eficiência não deve ser analisado isoladamente. A solução deve equilibrar agilidade e qualidade, buscando maximizar indicadores relacionados à correta compreensão das solicitações, recuperação e fundamentação das respostas enquanto minimiza indicadores negativos, principalmente a taxa de alucinação.

No contexto acadêmico do MVP, esses resultados serão avaliados por meio do pipeline de PLN utilizando dados sintéticos. A integração com o portfólio real do Metrô e a execução de processos corporativos sobre dados reais são consideradas evoluções posteriores e não constituem condição necessária para a validação dos Business Drivers nesta etapa.

---

# 3. Requisitos do Projeto

## 3.1 Requisitos Funcionais

Os requisitos funcionais definem as funcionalidades que deverão ser contempladas pela prova de conceito desenvolvida no MVP. Sua definição considera o escopo estabelecido para o projeto e as oportunidades levantadas durante o processo de ideação, priorizando as funcionalidades diretamente relacionadas ao pipeline de Processamento de Linguagem Natural (PLN).

O núcleo do MVP consiste em um pipeline de PLN capaz de receber comandos em linguagem natural, interpretar semanticamente as solicitações dos usuários e identificar a intenção primária de cada interação. O catálogo de intenções determina então a rota de processamento: intenções com fluxo automatizado são executadas diretamente, sem passar por um LLM; intenções pertencentes ao escopo, mas sem automação cadastrada, são encaminhadas ao LLM com contexto estruturado e validado. Nesse segundo ramo, quando a proatividade estiver habilitada, o sistema associa à intenção primária uma intenção secundária compatível e a apresenta como sugestão opcional de próximo passo.

Por se tratar de uma prova de conceito em contexto acadêmico, o funcionamento do MVP será validado sobre dados sintéticos. Integrações com dados reais do portfólio do Metrô de São Paulo e demais funcionalidades corporativas identificadas durante a ideação são consideradas possibilidades de evolução da solução e não constituem requisitos obrigatórios para a validação do núcleo funcional do MVP.

|  ID  | Requisito Funcional                                                                                                                                                                           | Feature relacionada                  | Prioridade |    Status    |
| :--: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ | :--------: | :----------: |
| RF01 | O sistema deve receber comandos textuais em linguagem natural relacionados à gestão de projetos e portfólio.                                                                                  | Consulta de informações dos projetos | Muito Alta | Não iniciado |
| RF02 | O sistema deve processar semanticamente os comandos recebidos e identificar a intenção primária expressa pelo usuário.                                                                        | Consulta de informações dos projetos | Muito Alta | Não iniciado |
| RF03 | O sistema deve associar a intenção primária ao catálogo do MVP, incluindo sua categoria e a existência ou não de um fluxo automatizado correspondente.                                           | Consulta de informações dos projetos | Muito Alta | Não iniciado |
| RF04 | O sistema deve recuperar informações relevantes dos documentos e dados sintéticos disponibilizados ao pipeline de acordo com a solicitação realizada.                                         | Ingestão de informações dos projetos | Muito Alta | Não iniciado |
| RF05 | O sistema deve responder a consultas sobre as informações disponíveis nos documentos de projetos utilizados na prova de conceito.                                                             | Consulta de informações dos projetos | Muito Alta | Não iniciado |
| RF06 | O sistema deve realizar análises e comparações entre informações de diferentes projetos quando solicitado pelo usuário.                                                                       | Consulta de informações dos projetos | Muito Alta | Não iniciado |
| RF07 | O sistema deve encaminhar cada intenção pertencente ao escopo para a rota definida no catálogo: fluxo automatizado sem uso de LLM ou LLM com contexto estruturado e validado quando não houver automação correspondente. | Ingestão de informações dos projetos | Muito Alta | Em andamento (despacho determinístico de `transacao_gerar_relatorio` sem LLM implementado; demais handlers pendentes) |
| RF08 | O sistema deve retornar o resultado da rota executada de forma estruturada e fundamentada, preservando as referências disponíveis e indicando quando não houver informações suficientes.         | Consulta de informações dos projetos | Muito Alta | Não iniciado |
| RF09 | Para intenções sem fluxo automatizado, o sistema deve, quando a proatividade estiver habilitada, associar uma intenção secundária compatível e apresentá-la como sugestão opcional de próximo passo, sem executá-la sem confirmação do usuário. | Consulta de informações dos projetos | Muito Alta | Implementado |
| RF10 | O sistema deve permitir ao usuário ativar ou desativar as sugestões proativas sem alterar o processamento da intenção primária.                                                                 | Edição das configurações do agente por menu | Alta | Implementado |

### 3.1.1 User Stories dos Requisitos Funcionais

As User Stories apresentadas nesta subseção estão diretamente integradas aos respectivos requisitos funcionais da Seção 3.1. Cada história segue a estrutura "Como [usuário], quero [necessidade], para [valor]", estabelecendo a necessidade que fundamenta o requisito e o benefício esperado pelo usuário.

Os critérios de aceitação estabelecem condições verificáveis para validação das funcionalidades dentro dos limites da prova de conceito, considerando a utilização de dados sintéticos e o desenvolvimento do pipeline de PLN como núcleo do MVP.

### RF01 — Entrada de comandos em linguagem natural

**User Story — US01**

Como usuário da solução, quero realizar solicitações utilizando linguagem natural, para interagir com as informações dos projetos sem precisar utilizar comandos técnicos ou conhecer a estrutura dos dados.

**Critérios de aceitação:**

* O sistema deve aceitar solicitações textuais em linguagem natural.
* O sistema deve aceitar solicitações em áudio, convertendo-as em texto antes do processamento, conforme a modalidade de entrada descrita na Seção 8.8.
* O usuário não deve precisar utilizar uma sintaxe técnica específica.
* A solicitação recebida deve ser encaminhada ao pipeline de PLN para processamento.

**Features relacionadas:** Consulta de informações dos projetos; Transcrição de áudio.

---

### RF02 — Identificação semântica da intenção

**User Story — US02**

Como usuário da solução, quero que o sistema compreenda semanticamente o que desejo realizar, para que minha solicitação seja interpretada de acordo com seu contexto.

**Critérios de aceitação:**

* O sistema deve processar semanticamente a solicitação recebida.
* O sistema deve identificar a intenção primária presente no comando do usuário.
* A intenção identificada deve ser encaminhada para classificação nas categorias suportadas pelo MVP.

**Feature relacionada:** Consulta de informações dos projetos.

---

### RF03 — Classificação e associação da intenção ao catálogo

**User Story — US03**

Como usuário da solução, quero que a intenção primária seja associada ao catálogo de capacidades, para que o sistema determine corretamente como processar minha solicitação.

**Critérios de aceitação:**

* O sistema deve associar a intenção primária a uma entrada do catálogo do MVP.
* O catálogo deve contemplar, no mínimo, as categorias consulta, transação e alerta.
* A entrada do catálogo deve indicar se existe um fluxo automatizado correspondente.
* Quando a intenção não pertencer ao escopo suportado, o sistema deve orientar a reformulação ou informar o limite da solução.

**Feature relacionada:** Consulta de informações dos projetos.

---

### RF04 — Recuperação de informações

**User Story — US04**

Como usuário da solução, quero que o sistema localize informações relevantes nos documentos de projetos, para obter respostas relacionadas ao contexto da minha solicitação.

**Critérios de aceitação:**

* O sistema deve consultar os documentos e dados sintéticos disponibilizados para a prova de conceito.
* O sistema deve recuperar informações relacionadas à solicitação realizada.
* As informações recuperadas devem ser utilizadas como contexto para o processamento da resposta.

**Feature relacionada:** Ingestão de informações dos projetos.

---

### RF05 — Consulta de informações dos projetos

**User Story — US05**

Como usuário da solução, quero consultar informações sobre os projetos utilizando linguagem natural, para acessar rapidamente os dados necessários para acompanhamento e análise.

**Critérios de aceitação:**

* O sistema deve responder a consultas relacionadas às informações disponíveis nos dados sintéticos.
* A resposta deve considerar o projeto ou contexto solicitado pelo usuário.
* A resposta deve utilizar as informações recuperadas pelo pipeline.
* Quando a informação solicitada não estiver disponível, o sistema deve indicar essa limitação.

**Feature relacionada:** Consulta de informações dos projetos.

---

### RF06 — Análise e comparação de projetos

**User Story — US06**

Como gestor do portfólio, quero solicitar análises e comparações entre projetos, para identificar diferenças, semelhanças e informações relevantes que apoiem a tomada de decisão.

**Critérios de aceitação:**

* O sistema deve identificar quando a solicitação exigir análise ou comparação.
* O sistema deve permitir comparar informações disponíveis de dois ou mais projetos.
* A comparação deve considerar os critérios informados pelo usuário quando aplicável.
* O resultado deve ser fundamentado nos dados sintéticos disponíveis.

**Feature relacionada:** Consulta de informações dos projetos.

---

### RF07 — Roteamento híbrido das intenções

**User Story — US07**

Como usuário da solução, quero que minha solicitação siga a rota prevista para a intenção identificada, para que ações conhecidas sejam executadas diretamente e as demais solicitações válidas recebam tratamento pelo LLM.

**Critérios de aceitação:**

* Quando o catálogo indicar um fluxo automatizado, o sistema deve encaminhar a ele a intenção e os parâmetros estruturados necessários.
* Uma solicitação atendida por fluxo automatizado não deve ser enviada ao LLM para decisão de intenção, acesso, escopo, período, cálculo, seleção de registros ou conclusão factual.
* Dentro de um fluxo automatizado, prompts de IA (por exemplo, AI Builder) podem ser usados exclusivamente como transformadores limitados de texto livre — com saída JSON fixa, validação determinística e fallback não generativo — e nunca decidem intenção, acesso, escopo, período, cálculo, seleção de registros ou conclusão factual.
* Quando a intenção pertencer ao escopo, mas não possuir fluxo automatizado, o sistema deve encaminhar ao LLM somente a intenção e o contexto estruturado e validado necessário para produzir a resposta.
* O comportamento das duas rotas deve poder ser demonstrado utilizando dados sintéticos ou simulações controladas.

**Feature relacionada:** Ingestão de informações dos projetos.

---

### RF08 — Geração de respostas estruturadas e fundamentadas

**User Story — US08**

Como usuário da solução, quero receber respostas estruturadas e fundamentadas nas informações disponíveis, para compreender os resultados apresentados pelo agente e utilizá-los com maior confiança.

**Critérios de aceitação:**

* O resultado de um fluxo automatizado deve corresponder à ação executada ou simulada e informar seu estado de conclusão.
* A resposta produzida pelo LLM deve considerar apenas a intenção e as informações estruturadas e validadas disponibilizadas pelo pipeline.
* O sistema não deve apresentar como fato informações que não estejam sustentadas pelos dados disponíveis.
* Quando não houver informações suficientes, o sistema deve indicar a limitação ao usuário.
* O retorno deve ser estruturado de forma coerente com a rota executada e preservar as referências disponíveis.
* Em solicitações analíticas, o sistema deve diferenciar informações recuperadas de interpretações produzidas pelo agente.

**Feature relacionada:** Consulta de informações dos projetos.

---

### RF09 — Sugestão proativa de intenção secundária

**User Story — US09**

Como usuário da solução, quero receber uma sugestão opcional relacionada à minha solicitação, para identificar um próximo passo útil sem perder o controle da interação.

**Critérios de aceitação:**

* A sugestão deve ser considerada somente quando a intenção primária pertencer ao escopo, não possuir fluxo automatizado e a proatividade estiver habilitada.
* O sistema deve selecionar no catálogo uma intenção secundária compatível com a intenção primária e com as capacidades disponíveis.
* A sugestão deve ser apresentada separadamente da resposta principal e identificada como opcional.
* A intenção secundária não deve ser executada sem confirmação explícita do usuário.
* Caso o usuário recuse a sugestão, o sistema deve encerrá-la sem alterar a resposta da intenção primária.
* Quando não existir intenção secundária compatível, o sistema deve retornar somente a resposta principal, sem criar uma sugestão não cadastrada.

**Feature relacionada:** Consulta de informações dos projetos.

---

### RF10 — Controle da proatividade

**User Story — US10**

Como usuário da solução, quero ativar ou desativar as sugestões proativas, para controlar se o agente deve oferecer próximos passos durante minhas consultas.

**Critérios de aceitação:**

* O sistema deve disponibilizar na interface um controle com os estados ativado e desativado.
* O estado selecionado deve ser considerado nas interações iniciadas após a alteração.
* Com a proatividade desativada, o sistema não deve apresentar as sugestões previstas no RF09.
* A desativação da proatividade não deve impedir a identificação, o roteamento nem a resposta da intenção primária.

**Feature relacionada:** Edição das configurações do agente por menu.


### 3.1.2 Modelagem Estática Inicial dos Requisitos Funcionais

A modelagem estática apresentada nesta subseção representa as principais classes de domínio necessárias para descrever o comportamento previsto pelos requisitos funcionais do MVP. O objetivo nesta etapa não é definir integralmente a arquitetura ou a implementação do sistema, mas demonstrar a relação entre as histórias de usuário, os dados manipulados e as responsabilidades necessárias ao funcionamento do pipeline.

A modelagem considera a `Solicitacao` como elemento de entrada do sistema. Cada solicitação possui uma `Intencao` primária, identificada pelo pipeline e associada ao `CatalogoIntencoes`. O catálogo informa ao `RoteadorIntencao` se existe um fluxo automatizado: quando existe, o `ExecutorFluxoAutomatizado` processa a solicitação sem acionar o LLM; caso contrário, o `GeradorLLM` recebe somente o contexto estruturado e validado. Quando a proatividade está ativa, uma `SugestaoProativa` pode associar à intenção primária uma intenção secundária cadastrada, que depende da confirmação do usuário para ser executada.

<div align="center">
  <img src="img/modelagem-estatica.png" alt="Modelagem estática inicial dos requisitos funcionais" width="100%">
</div>

<p align="center"><strong>Figura 13</strong> - Modelagem estática inicial dos requisitos funcionais.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>

O código-fonte do diagrama está versionado em [`docs/diagrams/modelagem-estatica.puml`](diagrams/modelagem-estatica.puml) e pode ser regerado com PlantUML e Graphviz instalados:

```bash
java -jar plantuml.jar -charset UTF-8 -tpng -o ../img docs/diagrams/modelagem-estatica.puml
```

O modelo estático mantém relação direta com os requisitos funcionais. `Solicitacao` e `PipelinePLN` representam a entrada em linguagem natural prevista no RF01; `Intencao`, `ClassificadorIntencao` e `CatalogoIntencoes` representam os RF02 e RF03; `DocumentoProjeto`, `TrechoRecuperado` e `RecuperadorInformacao` representam o RF04; `Projeto` e `Resposta` sustentam o RF05; e `AnalisadorComparativo` representa o RF06. O `RoteadorIntencao`, as duas rotas e seus executores tornam explícita a separação exigida pelo RF07. As respostas produzidas em ambas as rotas atendem ao RF08. Por fim, `SugestaoProativa` representa a intenção secundária do RF09 e `ConfiguracaoProatividade` representa o controle previsto no RF10.

| Elemento da modelagem                                            | Requisitos relacionados |
| ---------------------------------------------------------------- | ----------------------- |
| `Solicitacao`                                                    | RF01                    |
| `ClassificadorIntencao`, `Intencao` e `CatalogoIntencoes`        | RF02, RF03              |
| `RecuperadorInformacao`, `DocumentoProjeto` e `TrechoRecuperado` | RF04                    |
| `Projeto` e `Resposta`                                           | RF05                    |
| `AnalisadorComparativo`                                          | RF06                    |
| `CategoriaIntencao`, `RoteadorIntencao` e `RotaProcessamento`    | RF03, RF07              |
| `ExecutorFluxoAutomatizado` e `GeradorLLM`                       | RF07, RF08              |
| `Resposta` fundamentada por `TrechoRecuperado`                   | RF08                    |
| `SugestaoProativa`                                               | RF09                    |
| `ConfiguracaoProatividade`                                       | RF10                    |

Essa modelagem representa uma visão inicial do domínio da solução. O modelo de classes definitivo, incluindo decisões de implementação, tipos de persistência, interfaces técnicas e demais entidades identificadas durante o desenvolvimento, será aprofundado na seção de Solução Técnica em uma etapa posterior do projeto.



### 3.1.3 Modelagem Dinâmica Inicial dos Requisitos Funcionais

A modelagem dinâmica apresenta os principais cenários de interação derivados das histórias de usuário. Para esta etapa foram selecionados três fluxos que, em conjunto, representam o funcionamento central previsto para o MVP: consulta de informações de um projeto, análise comparativa entre projetos e roteamento híbrido com sugestão proativa configurável.

Os diagramas representam o comportamento esperado do sistema em nível funcional. Componentes e integrações poderão ser refinados posteriormente conforme a arquitetura definitiva da solução for desenvolvida.

### 3.1.3.1 Cenário 1 — Consulta de informação de um projeto

Este cenário representa uma solicitação como **"Qual o prazo do projeto XPTO?"**, classificada como pertencente ao escopo, mas sem fluxo automatizado cadastrado. O fluxo cobre principalmente os requisitos RF01, RF02, RF03, RF04, RF05, RF07 e RF08.

<div align="center">
  <img src="img/sequencia-cenario-1.png" alt="Cenário 1 — Consulta de informação de um projeto" width="100%">
</div>

<p align="center"><strong>Figura 14</strong> - Cenário 1 — Consulta de informação de um projeto.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>

O código-fonte do diagrama está versionado em [`docs/diagrams/sequencia-cenario-1.puml`](diagrams/sequencia-cenario-1.puml) e pode ser regerado com PlantUML e Graphviz instalados:

```bash
java -jar plantuml.jar -charset UTF-8 -tpng -o ../img docs/diagrams/sequencia-cenario-1.puml
```

O cenário começa com o RF01, quando o usuário envia uma solicitação em linguagem natural. O RF02 é representado pela identificação semântica da intenção e o RF03 por sua associação ao catálogo. Como não existe fluxo automatizado, o RF07 determina que somente o contexto estruturado e validado seja encaminhado ao LLM. O RF04 determina a recuperação dos dados relevantes, o RF05 corresponde à resposta sobre o projeto solicitado e o RF08 exige que as informações recuperadas fundamentem o retorno ou que a insuficiência seja declarada.

### 3.1.3.2 Cenário 2 — Análise e comparação entre projetos

Este cenário representa uma solicitação como **"Compare os riscos e os prazos dos projetos XPTO e ABC"**, tratada como intenção analítica sem fluxo automatizado. O fluxo cobre principalmente os requisitos RF01, RF02, RF03, RF04, RF06, RF07 e RF08.

<div align="center">
  <img src="img/sequencia-cenario-2.png" alt="Cenário 2 — Análise e comparação entre projetos" width="100%">
</div>

<p align="center"><strong>Figura 15</strong> - Cenário 2 — Análise e comparação entre projetos.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>

O código-fonte do diagrama está versionado em [`docs/diagrams/sequencia-cenario-2.puml`](diagrams/sequencia-cenario-2.puml) e pode ser regerado com PlantUML e Graphviz instalados:

```bash
java -jar plantuml.jar -charset UTF-8 -tpng -o ../img docs/diagrams/sequencia-cenario-2.puml
```

Nesse cenário, o RF06 diferencia o fluxo de uma consulta simples, pois exige recuperar informações referentes a dois ou mais projetos e aplicar uma etapa adicional de comparação. O RF07 encaminha ao LLM o resultado estruturado dessa análise porque o catálogo não possui automação correspondente. O resultado continua sujeito ao RF08: somente informações sustentadas pelos dados disponíveis devem ser apresentadas como fato.

### 3.1.3.3 Cenário 3 — Roteamento híbrido e sugestão proativa

Este cenário representa o comportamento do pipeline após identificar a intenção primária. O catálogo diferencia uma intenção fora do escopo, uma intenção com fluxo automatizado e uma intenção válida sem automação. Somente o último ramo utiliza o LLM e pode apresentar uma intenção secundária quando a proatividade estiver habilitada. O cenário cobre principalmente RF01, RF02, RF03, RF07, RF08, RF09 e RF10.

<div align="center">
  <img src="img/sequencia-cenario-3.png" alt="Cenário 3 — Roteamento híbrido e sugestão proativa" width="100%">
</div>

<p align="center"><strong>Figura 16</strong> - Cenário 3 — Roteamento híbrido e sugestão proativa.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>

O código-fonte do diagrama está versionado em [`docs/diagrams/sequencia-cenario-3.puml`](diagrams/sequencia-cenario-3.puml) e pode ser regerado com PlantUML e Graphviz instalados:

```bash
java -jar plantuml.jar -charset UTF-8 -tpng -o ../img docs/diagrams/sequencia-cenario-3.puml
```

A separação entre identificação, catalogação e roteamento é importante nesse fluxo. O RF02 corresponde à compreensão da intenção primária e o RF03 associa essa intenção à categoria e à rota controladas pelo catálogo. O RF07 garante que a rota automatizada não utilize o LLM e que apenas intenções válidas sem automação recebam tratamento generativo. O RF08 rege o resultado das duas rotas.

No ramo não automatizado, o RF09 permite apresentar uma intenção secundária cadastrada junto à resposta principal, mas exige confirmação antes de executá-la. O RF10 mantém essa iniciativa sob controle do usuário: quando a proatividade está desativada, o sistema continua identificando, roteando e respondendo à intenção primária, mas não oferece o próximo passo. Dessa forma, a proatividade documentada depende da consulta atual e não pressupõe observação contínua da atividade do usuário.


### 3.1.4 Rastreabilidade entre User Stories e Modelagem UML

A tabela a seguir consolida a relação entre os requisitos funcionais, suas histórias de usuário e os elementos de modelagem estática e dinâmica apresentados nesta seção.

| RF   | User Story                                 | Elementos do diagrama de classes                                | Cenário de sequência |
| ---- | ------------------------------------------ | --------------------------------------------------------------- | -------------------- |
| RF01 | US01 — Entrada em linguagem natural        | `Solicitacao`, `PipelinePLN`                                    | Cenários 1, 2 e 3    |
| RF02 | US02 — Identificação da intenção primária  | `ClassificadorIntencao`, `Intencao`                             | Cenários 1, 2 e 3    |
| RF03 | US03 — Associação da intenção ao catálogo  | `Intencao`, `CategoriaIntencao`, `CatalogoIntencoes`             | Cenários 1, 2 e 3    |
| RF04 | US04 — Recuperação de informações          | `RecuperadorInformacao`, `DocumentoProjeto`, `TrechoRecuperado` | Cenários 1 e 2       |
| RF05 | US05 — Consulta de projetos                | `Projeto`, `Resposta`                                           | Cenário 1            |
| RF06 | US06 — Análise e comparação                | `AnalisadorComparativo`, `Projeto`                              | Cenário 2            |
| RF07 | US07 — Roteamento híbrido                  | `RoteadorIntencao`, `RotaProcessamento`, `ExecutorFluxoAutomatizado`, `GeradorLLM` | Cenários 1, 2 e 3 |
| RF08 | US08 — Resposta fundamentada               | `Resposta`, `TrechoRecuperado`, `ExecutorFluxoAutomatizado`, `GeradorLLM` | Cenários 1, 2 e 3 |
| RF09 | US09 — Sugestão de intenção secundária     | `SugestaoProativa`, `CatalogoIntencoes`                          | Cenário 3            |
| RF10 | US10 — Controle da proatividade            | `ConfiguracaoProatividade`                                      | Cenário 3            |

Essa rastreabilidade demonstra que os requisitos funcionais não estão isolados da modelagem: as classes representam os conceitos necessários para sua execução e os diagramas de sequência demonstram como esses elementos colaboram nos principais cenários previstos pelas histórias de usuário.

A modelagem apresentada nesta seção possui caráter inicial e está diretamente associada à Especificação de Requisitos da Sprint 1. Nas etapas posteriores do projeto, os diagramas poderão ser refinados na seção de Solução Técnica, incorporando as decisões definitivas de arquitetura, interfaces, componentes, persistência e implementação.



### 3.1.5 Escopo dos requisitos funcionais

Os dez requisitos funcionais não têm o mesmo horizonte de entrega, e a distinção precisa estar declarada para que a especificação não conflite com a matriz de priorização da Seção 2.8 nem com o recorte do MVP registrado na Seção 2.9.

| Requisito | Escopo | Justificativa |
|---|---|---|
| RF01 a RF08 | **MVP** | Compõem o pipeline de consulta e resposta fundamentada, que é o recorte declarado na Seção 2.9 e sustentado pelas features da faixa Muito Alta da Seção 2.8 |
| RF09 — Sugestão proativa de intenção secundária | **Implementado na Sprint 4** | A interface apresenta a sugestão em bloco separado e a rota dedicada executa somente a intenção vinculada após confirmação explícita; a recusa encerra a sugestão sem execução |
| RF10 — Controle da proatividade | **Implementado na Sprint 4** | O controle da interface ativa ou desativa as sugestões sem alterar o processamento da intenção primária |

A implementação de RF09 e RF10 concretiza a decisão produzida na prototipação exploratória: o agente pode sugerir, mas nunca executar sem confirmação. A sugestão fica vinculada no backend a um identificador opaco, às fontes recuperadas e a uma intenção catalogada; a interface oferece ações explícitas de aceitar e recusar.

Permanece como evolução de qualidade definir um critério quantitativo para intervenções proativas inadequadas. Essa lacuna não altera o contrato funcional entregue: a elegibilidade é decidida pelo catálogo e pela presença de fontes, e a geração secundária só ocorre após confirmação explícita.

## 3.2 Requisitos Não Funcionais (RNFs)

Os requisitos não funcionais definem os atributos de qualidade que a solução deve atender durante o desenvolvimento e a validação do MVP. Diferentemente dos requisitos funcionais, que descrevem o que o sistema deve fazer, os RNFs estabelecem condições de segurança, desempenho, confiabilidade, rastreabilidade, manutenibilidade e aderência tecnológica necessárias para que o agente possa ser utilizado de forma adequada no contexto do PMO do Metrô.

| ID | Categoria | Requisito Não Funcional | Critério de verificação | Prioridade | Status |
| :---: | --- | --- | --- | :---: | :---: |
| RNF01 | Confidencialidade | A solução não deve processar dados reais ou sensíveis do portfólio em serviços externos não homologados pelo Metrô. No MVP, o desenvolvimento e os testes devem utilizar dados sintéticos ou anonimizados. | Verificar que 100% da base utilizada na prova de conceito é sintética ou anonimizada e que o pipeline não depende do envio de dados sensíveis para serviços externos não homologados. | Muito Alta | Não iniciado |
| RNF02 | Controle de acesso | A solução deve respeitar os limites de permissão e acesso à informação de cada perfil de usuário. | Validar, em cenários simulados, que 100% das respostas retornadas a usuários com perfis distintos estejam compatíveis com suas permissões e responsabilidades. | Muito Alta | Não iniciado |
| RNF03 | Rastreabilidade | A solução deve registrar as consultas realizadas, a intenção classificada, as fontes consultadas e a resposta retornada, permitindo auditoria técnica das interações. | Verificar que 100% das interações testadas geram registros estruturados contendo identificação do usuário ou perfil simulado, carimbo de tempo, intenção identificada, documentos recuperados e resposta produzida. | Muito Alta | Não iniciado |
| RNF04 | Confiabilidade das respostas | As respostas geradas pelo agente devem ser fundamentadas nas informações recuperadas dos dados disponíveis, evitando apresentar como fato informações não sustentadas pela base. | Em testes com dados sintéticos, atingir taxa de respostas fundamentadas igual ou superior a 90% e taxa de alucinação igual ou inferior a 5% nas solicitações pertencentes ao escopo do MVP. | Muito Alta | Atendido na Sprint 4 |
| RNF05 | Desempenho | O pipeline deve processar solicitações textuais em tempo compatível com uma interação conversacional. | Em ambiente de MVP, responder consultas simples em até 10 segundos e análises comparativas em até 20 segundos, considerando o tempo entre o recebimento da solicitação pela API e o retorno da resposta estruturada. | Alta | Atendido na Sprint 4 (3ª rodada) |
| RNF06 | Qualidade do PLN | O núcleo de PLN deve apresentar desempenho mínimo aceitável na classificação de intenções e na recuperação de informações. | Em conjunto de teste sintético, atingir F1 macro igual ou superior a 0,80 na classificação de intenções e recall igual ou superior a 0,80 na recuperação de informações. | Muito Alta | Reprovado na Sprint 4: F1 0,832724; *recall*@3 0,555556; IC 95% [0,440874; 0,664609] |
| RNF07 | Usabilidade conversacional | A interação deve permitir solicitações em linguagem natural, sem exigir que o usuário conheça comandos técnicos, estrutura dos dados ou nomes internos dos componentes. | Validar, por meio de casos de teste e testes com usuários, que pelo menos 80% das solicitações formuladas em português sejam compreendidas corretamente ou recebam orientação adequada para reformulação. | Alta | Não iniciado |
| RNF08 | Aderência tecnológica | A solução deve priorizar tecnologias compatíveis com o ecossistema Microsoft já utilizado pelo Metrô, incluindo Teams, Copilot Studio, Power Platform, SharePoint e Azure. | Verificar que a arquitetura proposta utiliza o Teams como canal principal, API documentada em OpenAPI para integração e componentes compatíveis com o ambiente homologável pelo parceiro. | Muito Alta | Não iniciado |
| RNF09 | Portabilidade | O núcleo de PLN deve ser independente da plataforma final de gestão do portfólio, permitindo substituição futura da camada de dados sem reescrita do pipeline principal. | Verificar que o pipeline consome dados por interfaces ou formatos estruturados e pode ser executado localmente, em contêiner ou em serviço publicado. | Alta | Não iniciado |
| RNF10 | Manutenibilidade | O código e os artefatos técnicos devem ser organizados de forma a facilitar testes, evolução e manutenção pela equipe. | Validar a existência de separação entre interface, lógica de negócio e acesso a dados, documentação da API, testes automatizados e instruções de execução do serviço. | Alta | Não iniciado |
| RNF11 | Disponibilidade e tratamento de falhas | A solução deve tratar falhas de classificação, recuperação, indisponibilidade de fonte ou ausência de informação sem interromper a experiência do usuário. | Verificar que 100% dos cenários de erro previstos retornam mensagens controladas, indicando a limitação encontrada, sem expor detalhes técnicos desnecessários ao usuário final. | Alta | Não iniciado |
| RNF12 | Qualidade dos dados sintéticos | Os dados sintéticos utilizados no MVP devem representar a estrutura dos documentos e informações esperadas no contexto do portfólio do Metrô. | Validar que a massa sintética contempla projetos, subportfólios, marcos, riscos, indicadores e documentos compatíveis com os fluxos de consulta e análise previstos. | Alta | Não iniciado |

### 3.2.1 RNFs descritos como histórias de usuário

Para aproximar os RNFs do mesmo formato usado nos requisitos funcionais, os principais atributos de qualidade também foram descritos como histórias de usuário. Essas histórias não adicionam novas funcionalidades; elas tornam explícitas as condições de qualidade que devem ser observadas durante a implementação e validação dos RFs.

| História de usuário não funcional | RNFs relacionados | Critério de aceite resumido |
| --- | --- | --- |
| Como representante do PMO, quero que a solução use apenas dados sintéticos, anonimizados ou homologados no MVP, para evitar exposição de informações sensíveis do portfólio. | RNF01, RNF08, RNF12 | A base de testes não contém dados sensíveis reais e todos os cenários documentam a origem controlada das informações. |
| Como usuário com perfil definido, quero receber apenas informações compatíveis com minhas permissões, para que a consulta respeite responsabilidades e limites de acesso. | RNF02 | Cenários simulados com perfis distintos retornam respostas compatíveis com cada permissão. |
| Como auditor técnico, quero que cada interação registre intenção, fontes consultadas e resposta produzida, para permitir rastreabilidade das decisões do agente. | RNF03 | Todas as interações testadas geram registro estruturado com usuário/perfil, horário, intenção, documentos recuperados e resposta. |
| Como usuário do PMO, quero respostas fundamentadas e transparentes sobre limitações, para confiar no resultado e saber quando a base não possui informação suficiente. | RNF04, RNF11 | Respostas do escopo indicam fundamento ou limitação, sem apresentar inferências não sustentadas como fato. |
| Como usuário em rotina operacional, quero receber respostas em tempo compatível com uma conversa, para que o agente seja útil durante consultas e reuniões. | RNF05 | Consultas simples retornam em até 10 segundos e análises comparativas em até 20 segundos no ambiente de MVP. |
| Como equipe de desenvolvimento, quero avaliar a qualidade do núcleo de PLN com métricas objetivas, para saber se a classificação de intenções e a recuperação de informações são aceitáveis. | RNF06 | O conjunto sintético de teste atinge F1 macro e recall iguais ou superiores a 0,80. |
| Como usuário sem perfil técnico, quero formular solicitações em português natural, para não depender de comandos internos ou sintaxe específica. | RNF07 | Pelo menos 80% das solicitações testadas são compreendidas corretamente ou recebem orientação adequada de reformulação. |
| Como equipe responsável pela evolução da solução, quero um núcleo organizado e portável, para permitir manutenção, testes e futura troca da camada de dados. | RNF09, RNF10 | O pipeline possui separação entre interface, lógica e dados, além de instruções de execução e testes automatizados. |

As metas numéricas apresentadas nesta seção representam valores iniciais para validação do MVP em ambiente controlado e com dados sintéticos. Esses limites deverão ser revisados nas sprints seguintes conforme a base de testes for ampliada, os dados sintéticos forem validados com o PMO e a solução for aproximada do ambiente tecnológico homologado pelo Metrô.

Os RNFs definidos nesta seção atuam como critérios transversais para a validação do MVP. Assim, eles não se limitam a um único requisito funcional: aspectos como confidencialidade, rastreabilidade, confiabilidade das respostas e controle de acesso devem ser observados em todos os fluxos principais do agente, especialmente nas consultas de informações, análises comparativas e geração de respostas estruturadas.

No contexto da prova de conceito, alguns requisitos serão demonstrados por simulação, principalmente aqueles relacionados à autenticação corporativa, permissões reais do SharePoint e auditoria com valor legal. Ainda assim, a solução deve preservar a arquitetura e os contratos necessários para que esses mecanismos possam ser conectados ao ambiente homologado do Metrô em uma evolução posterior.

### 3.2.2 Origem das metas e registro de revisões

O parágrafo acima, escrito na Sprint 1, já declara que as metas numéricas desta seção são valores iniciais, a serem revisados nas sprints seguintes. Esta subseção registra de onde veio cada meta verificada e toda revisão aplicada, para que um número nunca mude sem data, motivo e evidência.

**RNF05 — hipótese do grupo, não acordo com o parceiro.** Os limites de 10 segundos para consulta simples e 20 segundos para análise comparativa foram definidos pelo grupo na Sprint 1 (*commit* `a511b90`), numa tarefa cuja definição de pronto exigia critérios mensuráveis. Os documentos do parceiro não fixam tempo de resposta: o TAPI e as histórias de usuário pedem acesso "rápido" e "obtenção rápida de análises", e o documento de plataforma tecnológica recomenda limitar a leitura de listas a 500 linhas para não degradar a experiência por latência. O próprio TAPI atribui às equipes o aprofundamento e o tratamento dos requisitos não funcionais. O grupo converteu a expectativa qualitativa em um número verificável; os valores específicos não têm *benchmark* anterior que os sustente, e o parceiro não indicou valores em reunião.

| Data | RNF | Situação anterior | Decisão | Motivo | Vigência |
| --- | --- | --- | --- | --- | --- |
| 22/09/2026 | RNF05 | Teto de 10 s e 20 s como hipótese inicial | **Teto mantido** | Com provedor pago, 241 de 242 requisições ficaram abaixo de 8,2 s: o teto é atingível. O *Free Tier* do Gemini, usado na bancada de teste apenas para não gerar custo, tem piso de 14,7 s a 37,7 s por chamada trivial; elevar o teto para acomodá-lo ajustaria o requisito a uma escolha de custo da bancada, e não à expectativa de rapidez do parceiro. | A partir da 2ª rodada (22/09/2026) |
| 22/09/2026 | RNF05 | P95 calculado sobre qualquer quantidade de amostras | Mínimo de 40 amostras por tipo de consulta e por rodada | Com 10 amostras, a rota comparativa da linha de base da Sprint 4 teve o P95 igual à pior requisição: a rodada mediu o máximo, não o P95 que o requisito define. Detalhe na Seção 9.2.4. | A partir da 2ª rodada (22/09/2026) |
| 22/09/2026 | RNF05 | Rodada inconclusiva "deve ser estendida", sem forma definida | Nova janela, mais longa, com o mesmo código; um erro em qualquer das janelas reprova; sem terceira janela | A linha de base da 3ª rodada terminou com 37 amostras comparativas. O Locust exporta percentis, e não o tempo de cada requisição, e as duas janelas não podem ser reunidas num P95 único. Registrada antes de conhecer o resultado da carga. Detalhe na Seção 9.2.4. | A partir da 3ª rodada (22/09/2026) |

**O que a revisão não altera.** O resultado da 1ª rodada foi medido com os critérios congelados antes da execução e permanece **não atendido** (Seção 9.2.7). A Seção 9.2.1 proíbe usar resultados observados para flexibilizar a meta depois da medição; por isso as decisões acima valem somente a partir da rodada indicada em cada uma, registradas antes de executá-la, e nenhuma é aplicada retroativamente a uma rodada anterior.

**Provedor da bancada e provedor de produção.** O RNF05 não foi restringido a um ambiente específico. A bancada de teste (Seção 3.4.2.1) usa o Gemini no *Free Tier* para não gerar custo, e esse provedor, sozinho, não comporta o teto: a chamada trivial mede de 14,7 s a 37,7 s. No ambiente do Metrô, o agente usará o Copilot Studio com modelos GPT, no ecossistema Microsoft, e a latência desse provedor é medida na homologação. O piso do *Free Tier* é, portanto, característica da bancada, e não do produto.

## 3.3 Visão Inicial sobre a Solução Técnica de Engenharia

Esta seção apresenta o esboço preliminar da solução como um conjunto de blocos conectados, organizados nas três camadas previstas para o projeto: interface humano-computador, lógica de negócio e acesso a dados e serviços. O objetivo é registrar **como os componentes se relacionam**, ou seja, quais falam com quais, em que sentido e por meio de qual interface. O detalhamento interno de cada bloco fica para as seções de modelagem e de solução técnica das próximas sprints.

O esboço traduz a divisão em dois pilares definida pelo parceiro no Termo de Abertura. O **Pilar 1** corresponde ao núcleo de Processamento de Linguagem Natural, construído e avaliado pela equipe, responsável por interpretar a solicitação do usuário, identificar sua intenção, validar se ela pertence ao catálogo aceitável de interações sobre o portfólio e extrair as entidades necessárias à consulta. O **Pilar 2** corresponde aos recursos de IA generativa do ecossistema Microsoft, aplicados sobre dados já filtrados e estruturados pelo Pilar 1 para produzir a resposta em linguagem natural e os documentos derivados.

### 3.3.1 Organização em camadas

| Camada | Papel na solução | Componentes previstos |
|---|---|---|
| **Interface humano-computador** | Recebe a solicitação do usuário em texto ou áudio e devolve a resposta, sem exigir novo aplicativo ou novo login. | Microsoft Teams (canal), agente no Copilot Studio (orquestrador), conversão de áudio em texto. |
| **Lógica de negócio (Pilar 1)** | Núcleo autoral. Interpreta a linguagem natural e devolve uma resposta estruturada, sem que o texto do usuário transite por serviço externo não homologado. | API de PLN (FastAPI), pré-processamento, classificador de intenções, validador de escopo, extração de entidades, busca semântica e análise comparativa. |
| **Lógica de negócio (Pilar 2)** | Transforma a resposta estruturada em linguagem natural e gera os artefatos solicitados pelo PMO. | Orquestração generativa do Copilot Studio, prompts do AI Builder, Microsoft 365 Copilot. |
| **Acesso a dados e serviços** | Fornece e persiste os dados do portfólio e integra a solução aos serviços já usados pelo parceiro. | Conector personalizado (OpenAPI), Power Automate, SharePoint e Listas, índice vetorial, extratores de documentos, gerador de dados sintéticos, Power BI e Fabric Activator. |
| **Transversal** | Atende dois requisitos que atravessam todas as camadas: permissão por perfil e rastreabilidade das consultas e ações. | Microsoft Entra ID, trilha de auditoria. |

### 3.3.2 Diagrama de Componentes (UML)

A Figura 17 representa os componentes da solução e suas conexões. O diagrama mostra a **estrutura**, isto é, quais componentes se conectam a quais e em que sentido. A sequência de uma solicitação típica está descrita em 3.3.3.

![Diagrama de componentes da solução, organizado nas camadas de interface humano-computador, lógica de negócio (Pilar 1 e Pilar 2), acesso a dados e serviços, e camada transversal](img/componentes-mvp.png)

<p align="center"><strong>Figura 17</strong> - Visão inicial da solução técnica: diagrama de componentes do MVP sobre dados sintéticos.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>

O código-fonte do diagrama está versionado em [`docs/diagrams/componentes-mvp.puml`](diagrams/componentes-mvp.puml). Para regerar a imagem é necessário ter o PlantUML e o Graphviz instalados:

```bash
java -jar plantuml.jar -charset UTF-8 -tpng -o ../img docs/diagrams/componentes-mvp.puml
```

### 3.3.3 Fluxo principal entre os componentes

O caminho percorrido por uma solicitação típica, como *"Qual o prazo do projeto XPTO?"*, atravessa as camadas na seguinte ordem:

1. O usuário do PMO envia a mensagem, por texto ou áudio, pelo **Microsoft Teams**. Sendo áudio, o **componente de conversão de áudio em texto** devolve a transcrição em português ao agente.
2. O **agente no Copilot Studio** encaminha o texto ao **conector personalizado**, que chama a **API de PLN** por HTTP.
3. Dentro do Pilar 1, o texto passa pelo **pré-processamento**, é submetido ao **classificador de intenções** e, em seguida, ao **validador de escopo**. Solicitações fora do catálogo aceitável de interações são interrompidas aqui: o usuário é orientado e a solicitação é descartada, sem alcançar os dados do portfólio.
4. Sendo a intenção válida, a **extração de entidades** identifica os elementos da consulta, como código do projeto, período e subportfólio, e aciona a **busca semântica** sobre o índice vetorial ou a **análise comparativa** sobre os dados estruturados.
5. A API devolve uma **resposta estruturada** ao agente. É esse recorte já filtrado, e não o texto original do usuário, que alimenta o Pilar 2.
6. A **orquestração generativa** converte a resposta estruturada em linguagem natural e a devolve ao usuário pelo Teams. Quando a intenção é transacional, o **Power Automate** executa a escrita nas listas do SharePoint. Quando é de geração documental, o **Microsoft 365 Copilot** produz a prévia da apresentação ou do relatório.
7. Em paralelo, o **Entra ID** garante que a consulta respeite as permissões do perfil e a **trilha de auditoria** registra a interação, a intenção identificada e os documentos consultados.

### 3.3.4 Decisões refletidas no esboço

- **O núcleo de PLN é um serviço independente, não um recurso interno do Copilot Studio.** Isso preserva a exigência de autoria e avaliação do Pilar 1 e permite que o pipeline seja testado, medido e evoluído sem depender do provisionamento do ambiente do parceiro.
- **A fronteira de confidencialidade fica no validador de escopo.** Nenhum texto livre do usuário segue para a camada generativa. O que trafega a partir dali é um conjunto estruturado de campos já validados.
- **A camada de dados é substituível.** O acesso ao portfólio ocorre por meio do Power Automate e das listas do SharePoint. Caso a plataforma seja trocada no futuro, o impacto se concentra nesses conectores e o núcleo de PLN é preservado, o que atende à premissa de portabilidade registrada no Termo de Abertura.
- **Rastreabilidade e permissão são componentes, não observações.** Ambas aparecem no diagrama como blocos transversais, por serem requisitos explicitamente nomeados pelo parceiro.

O detalhamento dos componentes internos, das interfaces e dos contratos de dados será desenvolvido nas seções *Solução Técnica (Design)* e *Mapeamento Técnico de Infraestrutura e Implantação* deste documento, ao longo das próximas sprints.

## 3.4 Visão Inicial sobre Tecnologias e Ferramentas

Esta seção apresenta a seleção inicial de tecnologias e ferramentas consideradas para a implementação da solução. As escolhas foram realizadas a partir das restrições, premissas e objetivos definidos no Termo de Abertura do Projeto (TAPI), considerando principalmente a preferência do Metrô pelo ecossistema Microsoft, os requisitos de confidencialidade e rastreabilidade e a necessidade de desenvolvimento autoral do núcleo de Processamento de Linguagem Natural (PLN).

As tecnologias apresentadas nesta seção são classificadas entre aquelas previstas para utilização no **MVP**, desenvolvido e validado sobre dados sintéticos, e aquelas consideradas como alternativas ou possibilidades de evolução. Essa distinção é necessária porque o TAPI estabelece que a integração com o portfólio real do Metrô constitui uma evolução do MVP, não sendo requisito para a validação inicial da solução.

> **Leitura desta seção.** A Seção 3.4 registra a visão de tecnologias formulada na Sprint 1. As decisões de canal permanecem válidas: o agente é entregue no Microsoft Teams, com o Copilot Studio como orquestrador. A Sprint 2 acrescentou o detalhamento que aqui aparece apenas como direção — os requisitos comuns das APIs de voz estão na Seção 8.6, os benchmarks de STT e TTS estão nas Seções 8.7 e 8.8, o benchmark do algoritmo de PLN está na Seção 8.10 e a arquitetura consolidada, com o papel de cada componente, na Seção 5.2.

### 3.4.1 Critérios de seleção

Toda decisão tecnológica desta seção foi avaliada contra os critérios abaixo, extraídos das restrições e premissas do projeto:

| # | Critério | Descrição |
|---|---|---|
| C1 | **Aderência ao ecossistema Microsoft** | Priorizar tecnologias compatíveis com o ambiente já utilizado pelo Metrô, especialmente Microsoft 365, Power Platform e serviços Azure. |
| C2 | **Confidencialidade e segurança** | Evitar o processamento de informações sensíveis por serviços externos não homologados. Durante o MVP, devem ser utilizados dados sintéticos ou anonimizados. |
| C3 | **Autoria do núcleo de PLN** | O pipeline responsável pela identificação de intenções, extração de informações e consulta de fontes deve ser desenvolvido e avaliado pela equipe. |
| C4 | **Confiabilidade e escalabilidade** | Priorizar tecnologias que permitam testes, monitoramento, evolução e ampliação da solução sem necessidade de reestruturação completa. |
| C5 | **Custo e licenciamento** | Considerar as restrições de licenciamento do ambiente Microsoft e evitar dependências que possam gerar custos adicionais desnecessários para o MVP. |
| C6 | **Portabilidade** | Manter o núcleo de IA desacoplado da plataforma de portfólio, permitindo sua adaptação caso o Metrô altere futuramente os sistemas utilizados. |
| C7 | **Integração** | Priorizar tecnologias capazes de se integrar aos serviços existentes, especialmente SharePoint, Power Automate, Power BI e Copilot Studio. |

### 3.4.2 Listagem organizada das tecnologias e ferramentas

A pilha tecnológica é organizada por camadas, considerando a separação entre interface de interação, processamento de linguagem natural, recursos de IA generativa, acesso aos dados, segurança e ferramentas de desenvolvimento.

#### 3.4.2.1 Camada de interface humano-computador

| Tecnologia / Ferramenta | Função na solução | Critérios atendidos |
|---|---|---|
| **Microsoft Copilot Studio** | Canal principal de conversa em linguagem natural. Hospeda o agente, os tópicos e a orquestração generativa. O TAPI define o Copilot Studio como *"camada de orquestração e integração do agente"*. | C1, C5 |
| **Microsoft Teams** | Canal de distribuição do agente para os usuários do PMO, sem exigir novo aplicativo ou novo login. | C1, C4 |
| **Captura de voz nativa do canal (Teams / Copilot Studio)** | Primeira opção para a conversão de áudio em texto prevista no escopo macro, por não exigir provisionamento adicional nem sair do canal já homologado. | C1, C4 |
| **Azure AI Speech (Speech-to-Text, pt-BR)** | Alternativa para a conversão de áudio em texto, caso a captura nativa do canal não atenda ao português ou à qualidade necessária. **A disponibilidade precisa ser confirmada com a GTI.** O documento *Plataforma Tecnológica do Metrô* descreve o Azure AI de forma geral, mas destaca apenas o Azure Machine Learning Studio e o Azure OpenAI, sem citar o serviço de fala. | C1, C2 |

No MVP, a solução utilizará os canais disponibilizados pelo ecossistema Microsoft. Não está previsto o desenvolvimento de uma aplicação web ou mobile independente como interface do produto; o acesso por navegador e por dispositivos móveis ocorrerá pelos canais do Copilot Studio e do Microsoft Teams.

> **Bancada de teste.** Existem no repositório uma interface web em React (`src/frontend`) e um backend FastAPI (`src/backend`) que **não compõem o produto**. Foram construídos como bancada para exercitar isoladamente o caminho de consulta do RAG sobre dados mockados, permitindo medir latência, taxa de sucesso e consumo de tokens sem depender do provisionamento do canal corporativo pela GTI. A bancada utiliza um provedor de LLM específico apenas para viabilizar esse teste; essa escolha não constitui decisão de produto. O provedor a ser adotado será definido por benchmark próprio e submetido à homologação, do mesmo modo que foi feito para a API de transcrição na Seção 8.8. A entrega ao usuário permanece pelo Teams.

> **Base já existente.** O TAPI registra, entre as restrições, que a plataforma atual de portfólio já utiliza *"Copilot Studio para Bot de apoio na obtenção e atualização de status dos projetos e sub portfólios"*, e o documento *Arquitetura Portfólio Metrô* identifica a consulta de situação do portfólio e o suporte de FAQ como recursos "ainda em desenvolvimento". A solução deste projeto, portanto, **não parte de um cenário vazio**. Ela amplia esse agente com o núcleo de PLN autoral e com as transações do Pilar 2. A decisão entre estender o agente existente ou publicar um novo agente no mesmo ambiente será tomada com a GTI na Sprint 2.

#### 3.4.2.2 Camada de lógica de negócio: núcleo de PLN (Pilar 1)

Este é o componente autoral da equipe: recebe o texto transcrito, identifica a intenção, valida se ela pertence ao catálogo aceitável de interações e extrai as entidades necessárias para a consulta.

| Tecnologia / Ferramenta | Função na solução | Critérios atendidos |
|---|---|---|
| **Python 3.11+** | Linguagem do pipeline de PLN. | C3 |
| **Jupyter Notebook** | Ambiente de experimentação, avaliação e documentação executável dos modelos. | C3 |
| **spaCy** (modelo `pt_core_news_lg`) | Pré-processamento em português: tokenização, lematização, *part-of-speech* e reconhecimento de entidades nomeadas (códigos de projeto, datas, valores). | C2, C3 |
| **scikit-learn** | *Baseline* de classificação de intenções (TF-IDF + Regressão Logística / SVM) e cálculo das métricas de avaliação. | C3 |
| **Hugging Face Transformers** + **Sentence-Transformers** | Modelos de linguagem em português (ex.: BERTimbau, `multilingual-e5`) executados localmente para representar sentenças e apoiar a classificação de intenções, a comparação de similaridade e a avaliação do núcleo de PLN. | C2, C3 |
| **Catálogo local de fontes e casos sintéticos** | Organização dos documentos, planilhas, listas simuladas e casos de teste usados pelo núcleo de PLN durante o MVP, sem depender de infraestrutura generativa externa. | C2, C3 |
| **pandas** / **NumPy** | Manipulação dos dados sintéticos e consolidação das análises comparativas. | C3 |
| **FastAPI** | Opção de exposição do núcleo de PLN como API REST documentada em OpenAPI, a ser consolidada conforme o backend do MVP evoluir. | C1, C5 |
| **Docker** | Evolução prevista para empacotamento do serviço de PLN quando houver backend consolidado. Não é requisito da etapa atual do MVP. | C5 |
| **Azure Container Apps** (ou **Azure App Service**) | Destino futuro para execução do serviço de PLN dentro do *tenant* do parceiro, condicionado ao provisionamento da GTI. | C1, C2 |

> **Dependência de provisionamento.** A hospedagem do serviço de PLN em ambiente Azure do Metrô depende da GTI e não estava confirmada na abertura do projeto. Por isso, a implantação em Azure, o empacotamento Docker e a automação de deploy são tratados como evolução. A ausência desse ambiente não bloqueia o desenvolvimento e a avaliação conceitual do núcleo de PLN no MVP.

> **Decisão registrada.** O grupo optou por construir o classificador de intenções com modelos executados localmente, e não delegar a identificação de intenção a um LLM externo. A justificativa é dupla: atende à exigência do Pilar 1 (núcleo autoral e avaliado pela equipe, critério C3) e mantém o texto do usuário fora de serviços não homologados (C2). O uso de LLM fica reservado ao Pilar 2, sobre conteúdo já filtrado.

#### 3.4.2.3 Camada de lógica de negócio: recursos de IA generativa (Pilar 2)

| Tecnologia / Ferramenta | Função na solução | Critérios atendidos |
|---|---|---|
| **Orquestração generativa do Copilot Studio** | Geração das respostas em linguagem natural a partir dos dados estruturados devolvidos pelo pipeline de PLN, e condução de diálogos de múltiplos turnos (ex.: criação de projeto por etapas). | C1, C2 |
| **AI Builder (prompts personalizados)** | Prompts específicos para as transações do Pilar 2, como alertas de risco, verificação de marcos e aderência a normativos. | C1 |
| **Microsoft 365 Copilot** | Geração das prévias de apresentação mensal para a diretoria (PowerPoint) e do relatório de fechamento (Word), a partir do conteúdo consolidado pelo agente. | C1 |

> **Ponto em aberto.** O documento *Plataforma Tecnológica do Metrô* (22/10/2025) registra que o ambiente do parceiro está no Brasil (pt-BR) e que recursos em *preview* habilitados apenas no ambiente americano podiam ainda não estar disponíveis para uso, citando explicitamente o *computer use* (CUA) e o interpretador de Python (*code interpreter*). Como o documento tem quase um ano na data de abertura deste projeto e o Copilot Studio evolui de forma contínua, **o grupo não assume nem descarta a disponibilidade desses recursos. O levantamento do que está efetivamente habilitado no *tenant* do Metrô é uma tarefa da Sprint 2, a ser conduzida junto à GTI.** Nenhuma funcionalidade do MVP depende desses recursos.

#### 3.4.2.4 Camada de acesso a dados e serviços

| Tecnologia / Ferramenta | Função na solução | Critérios atendidos |
|---|---|---|
| **SharePoint Online + Listas** | Fonte de dados do portfólio no ambiente do parceiro. No MVP, é o formato-alvo replicado com dados sintéticos. | C1, C5 |
| **Power Automate (cloud flows)** | Automação dos fluxos de escrita e atualização (registro de status, lembretes de pendências, notificações). O modelo *cloud-flow* é o indicado pelo parceiro, por não haver sistema *on-premises* envolvido. | C1, C4 |
| **Conector personalizado (OpenAPI)** | Ponte entre o Copilot Studio e a API de PLN da equipe, a partir da especificação OpenAPI gerada pelo FastAPI. É a opção principal, por ser o mecanismo consolidado de extensão da Power Platform. | C1, C5 |
| **Model Context Protocol (MCP)**, a avaliar | Alternativa ao conector personalizado, potencialmente com menor acoplamento. Depende de confirmação da GTI quanto ao suporte e ao licenciamento no *tenant* do Metrô, e não é assumida como caminho no MVP. | C1, C5 |
| **Power BI (Microsoft Fabric)** | Painéis de indicadores do portfólio e visualizações citadas nas intenções do usuário (ex.: *dashboard* de compliance financeiro). | C1 |
| **Fabric Activator** | Alertas sobre métricas do portfólio (marcos próximos do vencimento, pendências), com envio via Outlook e Teams pela integração com Power Automate. | C1 |
| **python-docx**, **openpyxl**, **pdfplumber** | Extração de conteúdo dos documentos de projeto (Word, Excel, PDF), incluindo planilhas vinculadas por listas do SharePoint, para consulta estruturada e rastreabilidade das fontes. | C2, C3 |
| **openpyxl** / **python-pptx** (escrita) | Geração dos artefatos de saída solicitados pelo parceiro: exportação do cronograma para Excel e prévia da apresentação mensal para a diretoria. As histórias de usuário do Metrô preveem a pergunta *"Quer exportar para o Excel ou MS Project?"* ao final da construção do cronograma. | C1 |
| **Faker** | Geração da massa de dados sintéticos que substitui as informações reais do portfólio durante todo o MVP. | C2 |

> **Restrição herdada: ingestão no ecossistema Microsoft.** O parceiro informou que a estratégia corporativa de ingestão, organização e permissionamento de arquivos é executada pela GTI e pelo ambiente Microsoft do Metrô. Por isso, no MVP a equipe representa essa estrutura com dados sintéticos e documenta a interface esperada com SharePoint, Copilot Studio e Power Automate, sem assumir uma arquitetura generativa paralela ao ambiente homologado.

> **Restrição herdada: engenharia de dados.** A mesma lógica vale para o Power BI. O documento *Plataforma Tecnológica do Metrô* registra que o grupo responsável pela análise e criação dos painéis *"é um cliente, ou seja, não executa a etapa de engenharia de dados (ingestão/persistir no storage)"*. O MVP, portanto, consome e produz dados no formato das listas do SharePoint, sem assumir responsabilidade por pipelines de ingestão no Fabric.

**Corpus documental do MVP.** A base sobre a qual o agente responde é composta por dois conjuntos. O primeiro são os documentos de projeto gerados sinteticamente no formato dos anexos do parceiro, ou seja, Partida do portfólio, Balanço, Relatório Anual de fechamento do portfólio e Relatório Anual de fechamento de projeto ou programa. O segundo é o normativo **NOR-00-223, Gestão do Portfólio Organizacional**, indicado pelo parceiro nas histórias de usuário como a referência a ser usada para esclarecer dúvidas sobre conceitos e normativos de gestão de portfólio.

#### 3.4.2.5 Camada transversal: identidade, permissões e rastreabilidade

Dois requisitos do TAPI atravessam todas as camadas anteriores e por isso são tratados separadamente. O primeiro é a **rastreabilidade**, listada entre os benefícios esperados como *"registro de todas as consultas e ações realizadas no sistema, com suporte ao não repúdio"* e repetida em todas as intenções do quadro de exemplos do Apêndice. O segundo é a **atuação dentro dos limites de permissão**, item explícito do escopo macro: *"Atuar dentro dos limites de permissão e acesso à informação de cada perfil"*.

| Tecnologia / Ferramenta | Função na solução | Critérios atendidos |
|---|---|---|
| **Microsoft Entra ID** | Identidade corporativa já usada pelos usuários do Metrô. O agente herda a autenticação do canal (Teams), sem login adicional, e a identidade autenticada é propagada até a camada de dados. | C1, C2 |
| **Grupos e permissões do SharePoint** | Autorização efetiva por perfil. A visibilidade de projetos e subportfólios segue as permissões já configuradas nas listas do portfólio, evitando um segundo modelo de permissões paralelo ao do parceiro. | C1, C2 |
| **Lista de auditoria (SharePoint) ou tabela do Dataverse** | Trilha de auditoria da aplicação: registro de cada solicitação recebida, da intenção classificada, dos documentos consultados e da resposta devolvida, com identificação do usuário e carimbo de tempo. | C1, C2 |
| **Logs estruturados do serviço de PLN** (`logging` do Python, formato JSON) | Registro técnico das decisões do pipeline, como intenção identificada, confiança da classificação e trechos recuperados, permitindo auditar *por que* o agente respondeu o que respondeu. | C2, C3 |
| **Application Insights (Azure Monitor)** | Telemetria de disponibilidade, latência e erros do serviço de PLN, quando publicado no ambiente do parceiro. | C1 |

> **Escopo no MVP.** Como o MVP opera sobre dados sintéticos, a trilha de auditoria é implementada de forma funcional, mas sobre a base sintética. O objetivo é demonstrar o mecanismo e deixar a interface pronta, não produzir registros de auditoria com valor legal. A definição da política de retenção e do formato definitivo do registro cabe às áreas de TI e compliance do Metrô.

#### 3.4.2.6 Ferramentas de engenharia, gestão e qualidade

| Ferramenta | Função no projeto |
|---|---|
| **GitLab (`git.inteli.edu.br`)** | Versionamento do código e da documentação, quadro Kanban, *issues*, *merge requests* e registro de contribuições. |
| **GitFlow + Conventional Commits** | Política de branches e padronização das mensagens de commit, detalhadas em `GestaoConfiguracao.md`. |
| **Visual Studio Code** | Ambiente de desenvolvimento, com extensões de Python, Jupyter e Markdown. |
| **Draw.io / Mermaid / PlantUML** | Diagramas UML (componentes e pacotes), BPMN e diagramas de sequência da documentação. |
| **Figma** | Prototipação das interfaces conversacionais e dos fluxos de interação. |
| **pytest** | Biblioteca principal para testes automatizados do pipeline de PLN, das regras de recuperação de contexto e da API FastAPI. |
| **FastAPI TestClient / httpx** | Execução de testes funcionais e de integração contra os endpoints HTTP da API sem necessidade de subir um servidor externo, preservando o contrato OpenAPI gerado pelo próprio FastAPI. |
| **Locust** | Testes de desempenho e carga sobre endpoints HTTP da prova de conceito, com cenários escritos em Python e coleta de latência, vazão e taxa de erro. |
| **Microsoft Forms** | Coleta estruturada do questionário SUS e dos comentários qualitativos dos participantes dos testes de usabilidade, mantendo aderência ao ecossistema Microsoft priorizado pelo parceiro. |
| **scikit-learn (metrics)** | Avaliação do desempenho do núcleo de PLN: acurácia, precisão, revocação e F1 macro para a classificação de intenções, matriz de confusão e métricas de acerto para a consulta de fontes. |
| **Markdown** | Formato de toda a documentação do repositório. |

### 3.4.3 Alternativas avaliadas e não adotadas

O registro das opções descartadas é parte da decisão: ele documenta o que foi considerado e por que não seguiu adiante.

| Alternativa | Por que foi considerada | Por que não foi adotada |
|---|---|---|
| **API de LLM externo** (OpenAI, Anthropic, Google) para **classificação de intenções** | Menor esforço de implementação e boa acurácia sem treinamento. | Viola C2 (trânsito de dados por serviço não homologado) e C3 (o Pilar 1 exige núcleo autoral e avaliado pela equipe). A classificação permanece no pipeline próprio descrito na Seção 8.10. A geração da resposta a partir do contexto recuperado pelo RAG usa um LLM, cujo provedor ainda será definido e homologado. |
| **Azure OpenAI Service** provisionado à parte | Permaneceria dentro do *tenant* Azure do parceiro. | O próprio parceiro registra que o Copilot Studio já conta com os modelos mais recentes, *"não sendo necessário provisionar modelo adicional"*. Custo adicional sem ganho claro no MVP. |
| ***Fine-tuning*** de um modelo de linguagem | Potencial ganho de acurácia no domínio de gestão de portfólio. | O parceiro prioriza recursos homologados do ecossistema Microsoft, especialmente Copilot e Power Platform. Além disso, o volume de dados sintéticos do MVP não sustentaria o treinamento. |
| **Power Apps** como interface principal | Interface visual rica para preenchimento de formulários de projeto. | O escopo do módulo pede interface primariamente em linguagem natural (texto e áudio). Somam-se as restrições de licenciamento (C4), sem conectores premium e com limite de 500 linhas por leitura de lista. |
| **Aplicação web própria** (React/Next.js) fora do ecossistema Microsoft | Liberdade total de implementação e melhor experiência de voz. | Viola C1 e comprometeria a sustentação pela equipe interna do Metrô, que é um benefício esperado explícito do projeto. A interface React existente no repositório é bancada de teste do caminho de RAG, não interface do produto. |
| **Elasticsearch / OpenSearch** para busca | Recurso maduro de busca textual e análise de documentos. | Exigiria infraestrutura adicional a ser provisionada e mantida. Para o MVP, o catálogo local de fontes e a consulta às listas e planilhas simuladas do SharePoint atendem à escala prevista com menor custo operacional. |
| **Azure Machine Learning** como ambiente de treino e *endpoint* | Citado pelo parceiro como recurso disponível. Ofereceria *endpoints* gerenciados de inferência. | Mantido como **evolução prevista**, não como dependência do MVP. O provisionamento depende da GTI e não pode bloquear a Sprint 2. |

### 3.4.4 Riscos e dependências tecnológicas

Os itens abaixo alimentam a seção *Matriz de risco do projeto* deste documento, na categoria técnica.

| Risco / dependência | Impacto no projeto | Encaminhamento |
|---|---|---|
| Disponibilidade de licença e ambiente de Copilot Studio para a equipe Inteli | Sem o ambiente, o Pilar 2 e a integração ficam apenas em especificação. | Confirmar com a GTI logo na Sprint 2 e manter o núcleo de PLN independente do Copilot Studio, testável via API. |
| Recursos do Copilot Studio indisponíveis no ambiente pt-BR | Funcionalidades em *preview* citadas pelo parceiro (CUA, interpretador de Python) podem não existir no *tenant*. | Levantar com a GTI na Sprint 2 o que está habilitado e manter o MVP sem dependência desses recursos. |
| Ausência de ambiente Azure provisionado para hospedar o serviço de PLN | A integração em ambiente corporativo fica apenas especificada. | Manter o desenvolvimento e a validação em ambiente acessível, com Supabase para persistência. Solicitar o provisionamento à GTI como evolução, tratando publicação, Docker e CI/CD como etapas posteriores. |
| Conectores personalizados classificados como *premium* na Power Platform | Custo de licenciamento adicional inviabilizaria a adoção. | Verificar a cobertura pelo licenciamento do Copilot Studio e avaliar MCP como alternativa. |
| Qualidade e representatividade dos dados sintéticos | Modelo com boa métrica em laboratório e desempenho ruim no cenário real. | Derivar a **estrutura** dos dados sintéticos dos anexos do parceiro, com os cinco subportfólios (Turnaround, Expansão da Rede, Desempenho/Eficiência/Segurança Operacional, Receitas Não Tarifárias, Pessoas e Patrimônio), identificadores no padrão `TUR-01` e os campos dos relatórios de partida, balanço e fechamento. As amostras devem ser validadas com o PMO. |
| Modelo de permissões do portfólio mais granular do que o previsto | O agente pode expor a um perfil informação restrita a outro, violando item explícito do escopo macro. | Espelhar as permissões já existentes nas listas do SharePoint em vez de criar um modelo próprio. Validar com o PMO os perfis e o que cada um enxerga antes de implementar as consultas. |
| Desempenho de modelos de linguagem em português executados localmente | Latência ou acurácia insuficientes na classificação de intenções. | Estabelecer o *baseline* leve (TF-IDF + SVM) antes dos modelos maiores, e comparar as métricas antes de decidir. |

### 3.4.5 Fora do escopo do MVP e evolução da solução

O TAPI estabelece que o MVP deve funcionar como uma prova de conceito validada sobre dados sintéticos, enquanto a integração com o portfólio real do Metrô representa uma evolução posterior.

Assim, ficam inicialmente fora do escopo do MVP:

- Integração em produção com o portfólio real do Metrô (SharePoint e Listas do ambiente produtivo)
- Processamento de dados reais e sensíveis fora de ambientes homologados
- Implantação da solução em produção para utilização efetiva pelas equipes do Metrô
- Ingestão homologada de documentos no ambiente Microsoft, executada pela GTI
- Criação de aplicativo mobile próprio
- Criação de uma aplicação web independente do ecossistema Microsoft
- Provisionamento obrigatório de infraestrutura Azure antes da validação do núcleo de PLN
- Utilização obrigatória de modelos generativos externos
- *Fine-tuning* de modelos de linguagem
- Implementação de mecanismos avançados de monitoramento e auditoria de produção

Como possibilidades de evolução, poderão ser consideradas:

- Integração com SharePoint e listas reais do portfólio
- Integração com Power BI e demais serviços analíticos
- Hospedagem do serviço de PLN em infraestrutura Azure homologada
- Empacotamento Docker e pipeline CI/CD após consolidação do backend
- *Endpoints* de inferência gerenciados no Azure Machine Learning
- Microsoft Planner Premium e Dynamics 365 Project Operations, caso a plataforma de portfólio seja substituída
- Expansão da interação por voz, incluindo síntese de fala (*text-to-speech*)
- Integração com MS Project e Businessmap, citados nas histórias de usuário como destinos possíveis de exportação do cronograma. No MVP a exportação é feita para Excel
- Geração automatizada de relatórios e apresentações
- Integração com sistemas externos utilizados pelo portfólio
- Adoção de serviços de IA generativa homologados sobre dados reais e sensíveis

### 3.4.6 Plataforma de execução, confiabilidade e escalabilidade

> Esta subseção consolida a pilha na Sprint 2, incorporando o que foi decidido nas Seções 5.2, 6.2, 8.7 a 8.10. As subseções anteriores permanecem como registro da visão inicial.

**Plataforma de execução**

| Plataforma | Situação | Decisão |
|---|---|---|
| **Web, navegador desktop** | Suportada | O agente é entregue pelo Microsoft Teams em navegador, sem instalação. A bancada de teste em React descrita na Seção 3.4.2.1 roda no mesmo ambiente |
| **Mobile** | Suportada por herança, sem aplicativo próprio | O acesso ocorre pelo aplicativo do Microsoft Teams em iOS e Android, que já está homologado no parceiro. O agente publicado no Teams fica disponível nos três canais sem código específico |
| **Aplicativo mobile próprio** | Fora do escopo | Registrado na Seção 3.4.5. Construir um aplicativo exigiria distribuição, atualização e sustentação próprias, o que contraria o benefício de manutenção pela equipe interna do Metrô |

A decisão de não construir cliente próprio é o que torna o suporte a mobile barato: a entrada por voz descrita na Seção 8.7 usa a captura nativa do canal, e o mesmo endpoint atende navegador e celular sem ramificação de código.

**Linguagens, frameworks e bibliotecas por camada**

| Camada | Tecnologias | Papel |
|---|---|---|
| Canal | Microsoft Teams, Copilot Studio | Interface conversacional e orquestração de tópicos |
| API da aplicação | Python 3.11, FastAPI, Uvicorn | Endpoint HTTP/JSON, validação de entrada e roteamento |
| Núcleo de PLN | scikit-learn, PyTorch, Transformers (BERTimbau), nltk, joblib | Classificação de intenção em dois níveis, conforme as Seções 8.10 e 8.11 |
| Recuperação | Índice vetorial e catálogo local de fontes | Seleção dos trechos que compõem o contexto |
| Voz | Azure AI Speech | Transcrição de entrada e síntese prevista, Seções 8.8 e 8.9 |
| Dados | PostgreSQL gerenciado, Supabase Storage | Persistência do modelo físico da Seção 4.4 |
| Identidade | Microsoft Entra ID | Autenticação e associação de perfil |
| Automação | Power Automate | Execução dos fluxos funcionais |

**Confiabilidade**

| Mecanismo | Onde está documentado |
|---|---|
| Fallback estruturado quando a camada generativa está indisponível | Seção 6.2.5 |
| Validação local de formato, duração e tamanho antes da chamada externa | Seção 8.7.3 |
| Limiares de confiança que impedem acionamento de handler com previsão incerta | Seção 8.10.3 |
| Repetição com espera progressiva nas chamadas ao provedor de transcrição | Seção 6.2.7 |
| Trilha de auditoria persistida, separando falha do usuário de falha do provedor | Seções 6.3.3 e 8.7.6 |

**Escalabilidade**

A escala prevista para o MVP é modesta — dezenas de usuários do PMO, com perguntas curtas — e a arquitetura foi desenhada para crescer sem reestruturação, e não para suportar carga alta desde o início. Três decisões sustentam isso.

A **API é sem estado**. O contexto da conversa vive no banco, em `ai_conversations` e `ai_interactions`, e não em memória do processo. Aumentar a capacidade é acrescentar instâncias atrás de um balanceador, sem sessão fixa.

O **núcleo de PLN é um serviço separado do canal**. O classificador é carregado uma vez e serve as requisições; se a inferência se tornar o gargalo, ela pode ser movida para um endpoint gerenciado sem alterar a API da aplicação, como registrado na Seção 6.3.4.

A **camada de dados é substituível**. O modelo físico é PostgreSQL padrão, sem recurso proprietário, o que mantém a migração para o ambiente Azure do parceiro de baixo atrito quando a GTI provisionar.

O limite conhecido é a franquia gratuita do provedor de transcrição, de cinco horas de áudio por mês, discutida na Seção 8.8.2. Ela é suficiente para a validação do MVP e insuficiente para uso corrente, e por isso a Seção 6.3.4 registra a contratação do nível pago como pendência de evolução, e não como problema em aberto.

### 3.4.7 Referências

**Documentos do parceiro**

- Companhia do Metropolitano de São Paulo. *TAPI: MOD7 ES Agente de IA Portfólio de Projetos Metrô*, rev. 2.
- Companhia do Metropolitano de São Paulo. *Plataforma Tecnológica do Metrô*, 22/10/2025.
- Companhia do Metropolitano de São Paulo. *Arquitetura Portfólio Metrô*, 22/10/2025.
- Companhia do Metropolitano de São Paulo. *História do Usuário: Agente de IA*.
- Companhia do Metropolitano de São Paulo. *NOR-00-223: Gestão do Portfólio Organizacional*.
- Companhia do Metropolitano de São Paulo. Anexos 1 a 4: *Partida do portfólio*, *Balanço do portfólio*, *Relatório Anual de fechamento do portfólio* e *Relatório Anual de fechamento de projeto ou programa*.

> Os documentos acima são de uso restrito e foram disponibilizados pelo Metrô apenas para contextualização do projeto junto ao Inteli. Nenhum conteúdo desses arquivos é reproduzido neste repositório. Os anexos são utilizados como referência de **estrutura** para a geração dos dados sintéticos, e os dois relatórios anuais estão classificados pelo parceiro como *Corporativo* e *Confidencial*.

**Materiais de estudo indicados pelo parceiro**

- Microsoft. *Documentação oficial do Microsoft Copilot Studio*. Disponível em: https://learn.microsoft.com/pt-br/microsoft-copilot-studio/
- Microsoft. *Criar relatórios com o Copilot no Power BI*. Disponível em: https://learn.microsoft.com/pt-br/power-bi/create-reports/copilot-create-desktop-report
- DataCamp. *Power BI Copilot*. Disponível em: https://www.datacamp.com/pt/tutorial/power-bi-copilot

## 3.5 Correlação RFs e RNFs

A matriz cruza os dez requisitos funcionais (Seção 3.1) com os doze requisitos não funcionais (Seção 3.2). O objetivo é tornar explícito onde um atributo de qualidade precisa ser verificado: um RNF sem RF associado não tem onde ser testado, e um RF sem RNF crítico associado tende a ser implementado sem critério de aceitação além do comportamento nominal.

Legenda: **●** correlação forte — o RNF é condição de aceitação do RF; **○** correlação parcial — o RNF incide sobre o RF, mas não o determina.

| | RNF01<br>Confid. | RNF02<br>Acesso | RNF03<br>Rastr. | RNF04<br>Confiab. | RNF05<br>Desemp. | RNF06<br>PLN | RNF07<br>Usab. | RNF08<br>Aderên. | RNF09<br>Portab. | RNF10<br>Manut. | RNF11<br>Falhas | RNF12<br>Dados |
| --- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **RF01** Entrada em linguagem natural | ○ | ○ | ● | | ○ | | ● | ● | | | ○ | |
| **RF02** Identificação da intenção | | | ● | | ○ | ● | ● | | ● | | ○ | ○ |
| **RF03** Classificação no catálogo | | | ● | | | ● | ○ | | ● | ○ | ○ | ○ |
| **RF04** Recuperação de informações | ● | ● | ● | ● | ○ | ● | | ○ | ○ | | ● | ● |
| **RF05** Consulta de projetos | ● | ● | ● | ● | ● | | ○ | ○ | | | ● | ● |
| **RF06** Análise e comparação | ● | ● | ● | ● | ● | | ○ | | | | ● | ● |
| **RF07** Roteamento híbrido | | ○ | ● | ○ | ○ | ● | | ● | ● | ○ | ● | |
| **RF08** Respostas fundamentadas | ○ | ● | ● | ● | ○ | | ● | | | | ● | ○ |
| **RF09** Sugestão proativa | ● | ● | ● | ● | | ○ | ● | | | | ○ | ○ |
| **RF10** Controle da proatividade | ● | ● | ● | | | | ● | | | | | |

Três leituras orientam o trabalho das próximas sprints.

**RNF03 é transversal.** A rastreabilidade incide sobre os dez requisitos funcionais, sem exceção. Isso significa que o registro de auditoria não é uma funcionalidade a ser implementada ao final, e sim uma obrigação de cada rota: qualquer caminho que produza resposta precisa gravar solicitação, intenção, fontes e retorno. É a razão de `ai_interactions`, `consulted_sources` e `audit_events` aparecerem no modelo de dados desde a Seção 4.2.

**RF04, RF05 e RF06 concentram as correlações fortes.** São os requisitos que tocam a informação do portfólio, e por isso acumulam confidencialidade, controle de acesso, confiabilidade e qualidade dos dados simultaneamente. São também os que exigem o maior número de cenários negativos no plano de testes da Sprint 3 — não basta verificar que a resposta certa aparece; é preciso verificar que a resposta indevida não aparece para o perfil errado.

**RF09 e RF10 herdam a carga de confidencialidade.** Os dois requisitos de proatividade correlacionam-se fortemente com RNF01 e RNF02, e é exatamente o achado da prototipação exploratória (Seção 3.8.4): um agente que age a partir do que observa precisa observar, e a observação é a superfície que os dois RNFs restringem. A decisão sobre o regime de iniciativa, registrada como aberta no inventário da Seção 3.8.6.1, é portanto também uma decisão sobre o alcance desses dois RNFs.

## 3.6 Casos de Uso

Os casos de uso serão modelados na Sprint 3, junto com a derivação dos testes funcionais, conforme a Seção 8.3.1. A decisão de tratá-los nesse momento é deliberada: o barema da Sprint 3 exige que cada requisito funcional gere ao menos um cenário positivo e um negativo, e o caso de uso é a forma natural de organizar esses cenários antes de convertê-los em teste.

O material de partida já está produzido e versionado:

- as **user stories** de RF01 a RF10, com critérios de aceitação, na Seção 3.1.1;
- a **modelagem estática** das entidades envolvidas, na Seção 3.1.2;
- os **três cenários dinâmicos** iniciais, na Seção 3.1.3, e os **quatro cenários críticos** detalhados em diagramas de sequência na Seção 5.3;
- o **repertório de oito situações** registradas na prototipação exploratória, na Seção 3.8.6.2, incluindo as cinco que o protótipo não conseguiu atender — que são candidatas diretas a casos de uso de exceção.

## 3.7 Casos de Uso x Requisitos Funcionais

Será desenvolvido na Sprint 3, junto com a Seção 3.6. A rastreabilidade entre requisitos funcionais e modelagem UML já existente está registrada na Seção 3.1.4 e será estendida para incluir os casos de uso e, na sequência, os casos de teste.

## 3.8 Prototipação Exploratória

### 3.8.1 Questão de Projeto

**Questão:** De quem parte a iniciativa da interação — o agente age somente quando é explicitamente solicitado, ou age a partir do que observa da atividade que a pessoa está realizando?

**Justificativa.** A documentação produzida até aqui sustenta os dois regimes sem decidir entre eles. Todos os requisitos funcionais partem de um comando formulado pelo usuário (RF01), mas o catálogo de intenções previsto no RF03 e no RF07 inclui a categoria *alerta*, que pressupõe um agente capaz de se manifestar sem ter sido consultado. A jornada de Carlos (2.5.2.3) atribui valor explícito a "alertas relevantes" e à "identificação proativa de desvios", enquanto a visão do produto (2.4.1) descreve o agente como uma interface conversacional acionada por linguagem natural. A resposta altera o comportamento do sistema diante das pessoas em dois pontos: define se o silêncio é o estado padrão do agente ou uma decisão que ele precisa justificar a cada momento, e determina se o sistema precisa observar continuamente a atividade do usuário — o que incide diretamente sobre as restrições de confidencialidade e de controle de acesso estabelecidas no RNF01 e no RNF02.

### 3.8.2 Alternativas e Formatos de Prototipação

As duas alternativas exploradas respondem à mesma questão a partir de regimes opostos de iniciativa. No Protótipo 1, a interação só existe quando a pessoa a inicia; no Protótipo 2, o agente pode iniciá-la a partir do contexto observado. Ambas são defensáveis no contexto do PMO do Metrô e nenhuma foi construída para perder: o regime reativo oferece controle, previsibilidade e rastreabilidade direta entre pergunta e resposta, enquanto o regime proativo oferece cobertura para situações que a pessoa não sabe que precisa consultar.

#### 3.8.2.1 Protótipo 1 — Agente Reativo sob Demanda

O primeiro protótipo explora uma alternativa em que o agente permanece inteiramente silencioso até ser explicitamente acionado. Nesse regime, o sistema não observa a atividade da pessoa, não interpreta o que está na tela e não avalia oportunidades de assistência: ele existe como um canal de consulta que é aberto pelo usuário, responde ao que foi perguntado, indica quando não possui informação suficiente e volta ao silêncio.

A alternativa parte da hipótese de que, no contexto do PMO, o valor do agente está menos em antecipar necessidades e mais em eliminar o esforço de localizar e consolidar informações que já estão distribuídas entre SharePoint, listas corporativas, relatórios e documentos. Sob essa hipótese, a pessoa continua sendo a única responsável por decidir o que precisa saber, e o agente reduz apenas o custo de obter a resposta.

Três argumentos sustentam a alternativa no contexto específico do parceiro. Primeiro, a confidencialidade: um agente que só age quando chamado não precisa observar continuamente a atividade do usuário, o que elimina uma superfície permanente de leitura de contexto e simplifica a aderência ao RNF01 e ao RNF02. Segundo, a rastreabilidade: como toda resposta responde a uma solicitação explícita, o registro exigido pelo RNF03 tem sempre um par pergunta–resposta bem delimitado, sem necessidade de justificar por que o sistema decidiu falar. Terceiro, a confiança: conforme registrado na Seção 2.2, experiências anteriores do parceiro com IA generativa foram prejudicadas por respostas não fundamentadas na documentação oficial; um regime em que o agente nunca se manifesta espontaneamente reduz o número de oportunidades em que ele pode errar sem ter sido solicitado.

O comportamento explorado pode ser representado conceitualmente como:

```text
Pessoa identifica uma necessidade
            ↓
Pessoa formula uma solicitação explícita
            ↓
Agente interpreta a solicitação
            ↓
   Há informação suficiente na base?
         /                         \
       Não                         Sim
        ↓                           ↓
Agente declara a            Agente responde com
limitação encontrada        fonte referenciada
        ↓                           ↓
Pessoa reformula ou       Pessoa aprofunda ou
abandona a consulta       encerra a interação
            ↓                       ↓
        Agente retorna ao silêncio
```

Entre os comportamentos explorados por esta alternativa estão:

- responder exclusivamente ao que foi solicitado, sem ampliar o escopo da resposta;
- declarar explicitamente a ausência de informação em vez de inferir ou completar lacunas;
- manter ou descartar o contexto entre perguntas sucessivas de uma mesma sessão;
- referenciar a fonte consultada em cada resposta;
- permanecer em silêncio diante de informações relevantes que não foram perguntadas;
- tratar solicitações formuladas com vocabulário diferente do utilizado nos documentos da base;
- decidir se, ao não encontrar informação, o agente deve apenas informar a limitação ou orientar uma reformulação.

**Formato de prototipação:** tirinhas ilustradas, mesmo formato utilizado no Protótipo 2.

A escolha do formato é deliberada e responde a duas exigências distintas. A primeira é a exigência do artefato de experimentar um formato não baseado em interface digital: a tirinha não é uma tela navegável nem um protótipo clicável, e por isso não permite que a exploração se transforme em refinamento de interface. Ela obriga o grupo a representar o comportamento do agente por meio do que acontece entre as pessoas e o sistema ao longo do tempo — quem fala primeiro, o que é dito, o que fica sem ser dito e qual é a consequência disso — que é exatamente a dimensão da questão formulada em 3.8.1.

A segunda é a exigência de comparabilidade. Como a questão trata de uma única variável — a origem da iniciativa —, manter o mesmo meio, as mesmas personas e a mesma estrutura de quatro cenários nos dois protótipos permite atribuir as diferenças observadas ao regime de iniciativa, e não ao formato de representação. O custo dessa decisão está registrado na Seção 3.8.5: por utilizar o mesmo meio nas duas alternativas, a exploração não produz comparação entre formatos de prototipação, apenas entre regimes de comportamento.

#### 3.8.2.2 Protótipo 2 — Agente Proativo e Orientado à Jornada

O segundo protótipo explora uma alternativa em que o agente não depende exclusivamente de solicitações explícitas do usuário para iniciar uma interação. Nesse regime, o sistema considera o contexto da atividade realizada pela pessoa, identifica possíveis necessidades relacionadas ao momento da interação e pode apresentar sugestões de conteúdos, informações ou ações pertinentes.

A alternativa parte da hipótese de que um agente capaz de interpretar o contexto de uso e atuar de forma proativa pode reduzir a dependência do usuário de conhecer previamente quais informações ou funcionalidades estão disponíveis. Em vez de limitar sua atuação à resposta de perguntas, o agente passa a participar da jornada realizada pelo usuário, identificando situações nas quais uma intervenção contextual possa agregar valor.

O comportamento explorado pode ser representado conceitualmente como:

```text
Usuário realiza uma atividade
            ↓
Agente identifica o contexto disponível
            ↓
Agente interpreta a situação
            ↓
Existe uma oportunidade relevante de assistência?
         /                         \
       Não                         Sim
        ↓                           ↓
Sem intervenção             Agente apresenta sugestão
                                    ↓
                           Usuário aceita ou recusa
                              /            \
                            Aceita          Recusa
                              ↓               ↓
                    Agente conduz fluxo   Retorna ao
                       relacionado         contexto
```

Nesse modelo, a interação pode ocorrer diretamente no ambiente em que o usuário já está trabalhando, sem depender necessariamente de uma interface conversacional centralizada. Essa possibilidade é exploratória e não constitui compromisso do MVP, que permanece restrito a dados sintéticos e não pressupõe integração produtiva nem observação contínua da atividade. Em uma evolução futura, o agente poderia apresentar informações, sugestões, perguntas de confirmação ou conteúdos relacionados à atividade observada, buscando reduzir a distância entre a necessidade do usuário e a informação ou ação que pode auxiliá-lo.

No contexto do projeto, a abordagem foi explorada a partir de situações em que a pessoa navega por informações do portfólio, consulta documentos ou realiza atividades relacionadas a um projeto. A partir do contexto identificado, o agente sugere recursos relacionados ao que está sendo feito — documentos, conceitos, indicadores, cronogramas, riscos ou próximos passos.

**Formato de prototipação:** tirinhas ilustradas, o mesmo formato utilizado no Protótipo 1.

A justificativa é a mesma registrada na Seção 3.8.2.1 e vale nos dois sentidos. A tirinha não é uma tela navegável nem um protótipo clicável, o que atende à exigência de um formato não baseado em interface digital e impede que a exploração escorregue para refinamento de interface — risco maior justamente aqui, já que a intervenção proativa é visual por natureza e seria tentador desenhá-la em vez de investigá-la. E, por ser o mesmo meio das mesmas personas nas duas alternativas, permite atribuir as diferenças observadas ao regime de iniciativa, e não ao formato de representação.

A pergunta que o formato permite investigar nesta alternativa é específica: *em que momento a intervenção é bem-vinda e em que momento ela é interrupção*. Isso só aparece quando existe um antes e um depois — a atividade que a pessoa estava fazendo, o agente falando, e o que acontece com a atividade em seguida. É a sequência de painéis que torna esse intervalo visível.

Entre os comportamentos explorados por esta alternativa estão:

- identificar situações relevantes durante a atividade do usuário;
- reconhecer quando o contexto disponível é suficiente para justificar uma intervenção;
- apresentar informações relacionadas ao conteúdo ou atividade em andamento;
- sugerir possíveis próximos passos;
- recomendar documentos, conceitos ou conteúdos potencialmente pertinentes;
- utilizar perguntas de confirmação antes de iniciar uma nova ação;
- adaptar a interação de acordo com a resposta do usuário;
- tratar a recusa de uma sugestão sem comprometer a continuidade da atividade;
- preservar ou modificar o contexto quando o usuário alterar sua intenção;
- limitar a frequência e a intensidade das intervenções para evitar que a proatividade se torne excessivamente intrusiva.

### 3.8.3 Construção e Execução dos Protótipos

#### 3.8.3.1 Protótipo 1 — Agente Reativo sob Demanda

O protótipo foi construído e executado a partir de situações em que o agente permanece silencioso até ser explicitamente acionado pela pessoa. Foram utilizadas as mesmas personas e tipos de situação do Protótipo 2 — Carlos em uma atividade de acompanhamento do portfólio e Mariana em uma atividade de análise e consolidação de informações —, preservando a comparação do regime de iniciativa sem afirmar equivalência estrita entre os roteiros. Para cada situação foram produzidas duas tirinhas: uma representando uma execução de sucesso e outra representando uma execução de falha.

As situações foram representadas no mesmo ambiente corporativo considerado na solução. A diferença em relação ao Protótipo 2 está na origem da interação: não existem elementos sobrepostos à tela de trabalho, e o agente só aparece na tirinha depois que Carlos ou Mariana o aciona deliberadamente. Entre uma solicitação e outra, o agente retorna ao silêncio.

O roteiro painel das quatro tirinhas e as regras de representação estão em [`prototipo-1-roteiro.md`](prototipo-1-roteiro.md).

| Tirinha | Persona | Situação | O que a execução investiga |
| :---: | --- | --- | --- |
| 1A | Carlos | Preparação de reunião de acompanhamento do subportfólio | O regime reativo quando a pessoa sabe exatamente o que precisa perguntar |
| 1B | Carlos | Mesma preparação, com uma dependência entre projetos não consultada | O que acontece com a informação relevante que ninguém perguntou |
| 2A | Mariana | Consolidação do balanço mensal | O ganho real quando a solicitação usa o vocabulário dos documentos |
| 2B | Mariana | Mesma consolidação, com vocabulário divergente da base | O custo transferido à pessoa quando a formulação não encontra correspondência |

#### Execução dos cenários de sucesso

##### Cenário 1 — Carlos consulta o agente para preparar a reunião de acompanhamento

![Tirinha 1A — Execução de sucesso](img/tirinha-1A-1.png)

A primeira execução explora a atuação do agente reativo em uma situação na qual Carlos sabe exatamente qual informação precisa obter. Ele está montando a pauta de uma reunião de acompanhamento do subportfólio e identifica, por conta própria, que precisa confirmar o marco vigente de um dos projetos antes de conduzir a conversa com os líderes.

Carlos abre o canal do agente e formula a solicitação. O agente responde com o marco, a data e a referência ao documento consultado, indicando a versão vigente do cronograma. Em seguida, Carlos aprofunda a consulta perguntando pelos riscos em aberto do mesmo projeto, e recebe uma nova resposta igualmente referenciada.

Concluída a consulta, Carlos encerra o canal e retorna à elaboração da pauta. O agente não se manifesta novamente. Nenhum elemento é apresentado sem ter sido pedido e nenhuma interrupção ocorre durante o restante da atividade.

O cenário foi considerado bem-sucedido porque o agente resolveu, em duas solicitações, uma consolidação que exigiria navegação entre o SharePoint, o Power BI e documentos distintos, mantendo a rastreabilidade de cada informação apresentada. O controle sobre o que é consultado permanece integralmente com Carlos, e a relação entre pergunta e resposta é direta o suficiente para que o registro de auditoria previsto no RNF03 seja produzido sem ambiguidade.

##### Cenário 2 — Mariana consolida o balanço mensal a partir de uma solicitação precisa

![Tirinha 2A — Execução de sucesso](img/tirinha-2A-1.png)

A segunda execução explora uma situação em que Mariana, analista sênior com domínio do vocabulário utilizado nos documentos do portfólio, formula uma solicitação comparativa durante a consolidação do balanço mensal.

Mariana solicita ao agente a comparação do avanço físico dos projetos de um subportfólio entre dois meses. A solicitação é formulada com os mesmos termos empregados nos documentos oficiais, o que permite ao agente localizar as informações correspondentes e retornar uma resposta estruturada, com a fonte de cada item apresentado.

O resultado é utilizado diretamente na elaboração do relatório, sem que Mariana precise consultar manualmente as diferentes plataformas em que essas informações estão distribuídas.

O cenário foi considerado bem-sucedido porque evidencia que o ganho do regime reativo é maior justamente para o perfil que já sabe o que precisa perguntar e como perguntar. Para Mariana, a antecipação de necessidades não representaria um ganho significativo: sua dificuldade não está em identificar a informação necessária, mas no esforço manual de reuni-la.

#### Execução dos cenários de falha

##### Cenário 1 — Informação relevante retida por não ter sido solicitada

![Tirinha 1B — Execução de falha](img/tirinha-1B-1.png)

A primeira execução de falha repete a situação do Cenário 1A, novamente com Carlos preparando a reunião de acompanhamento, mas explora o que acontece com a informação que ele não pensou em consultar.

Carlos formula as mesmas solicitações e recebe as mesmas respostas corretas e referenciadas. Nada de anômalo ocorre durante a interação. Entretanto, existe na base um registro indicando que uma das entregas do subportfólio depende de um contrato pertencente a outro projeto, cuja tramitação está atrasada. O agente dispõe dessa informação e não a apresenta, porque ela não foi solicitada e o regime reativo não prevê que ele fale sem ser chamado.

A consequência aparece fora da interação com o sistema: durante a reunião, o líder do outro projeto informa a dependência, e Carlos é surpreendido por um impacto que poderia ter sido antecipado. A informação estava disponível durante toda a preparação.

A execução revela que a falha do regime reativo não é de recuperação nem de fundamentação — o agente não errou, não inventou e não deixou de responder. Trata-se de uma falha de cobertura, cuja característica mais relevante para o projeto é ser invisível no momento em que ocorre. Nenhum indicador do próprio agente a detecta: do ponto de vista do sistema, a interação foi integralmente bem-sucedida.

O cenário torna visível, portanto, uma decisão de projeto que a alternativa reativa não resolve sozinha: se o sistema dispõe de informação relacionada ao que foi perguntado e capaz de alterar a decisão da pessoa, permanece em aberto se o silêncio continua sendo o comportamento adequado.

##### Cenário 2 — Reformulações sucessivas diante de vocabulário divergente

![Tirinha 2B — Execução de falha](img/tirinha-2B-1.png)

A segunda execução de falha explora uma situação em que Mariana formula sua solicitação com um vocabulário que não corresponde ao utilizado nos documentos da base.

Mariana pergunta quais projetos estão atrasados. O agente responde que não localizou informações correspondentes ao termo empregado. A resposta é adequada ao RNF04 por não inferir nem completar lacunas sem fundamento, mas é insuficiente sob a perspectiva do RNF07, pois não oferece orientação para reformulação. Mariana reformula a solicitação com outro termo e recebe a mesma resposta. Apenas na terceira formulação, ao utilizar a expressão registrada nos documentos, obtém a informação que procurava.

A execução demonstra que a informação estava disponível desde a primeira solicitação, e que o obstáculo não estava na base nem na capacidade de recuperação, mas na correspondência entre a formulação da pessoa e o vocabulário do acervo. O custo de acesso não foi eliminado pelo agente: foi transferido para Mariana, que precisou descobrir por tentativa qual termo o sistema reconhece. Essa dinâmica reproduz uma dor já registrada em sua jornada (Seção 2.5.2.2), na qual a usuária reformula perguntas sucessivamente até obter respostas úteis.

O cenário torna visível a decisão mais consequente identificada nesta alternativa. Ao não localizar a informação, o agente poderia indicar o termo equivalente utilizado na base e resolver a situação na primeira tentativa. Ao fazê-lo, entretanto, passaria a oferecer algo que não foi solicitado. A alternativa reativa, levada ao limite, não se sustenta como categoria pura: existe um grau mínimo de iniciativa sem o qual o regime não funciona para quem não domina o vocabulário do domínio. O RNF07 já previa "orientação adequada para reformulação" sem qualificar esse comportamento como proatividade, o que indica que a fronteira entre os dois regimes é menos nítida do que a formulação da questão sugere.

#### Diário de construção e execução

A construção das tirinhas evidenciou que a dificuldade do Protótipo 1 não está em representar o agente respondendo, mas em determinar o que ele faz — ou deixa de fazer — nos intervalos entre as solicitações.

**Decisão forçada: o que "reativo" significa entre uma pergunta e a seguinte.** Ao construir o Cenário 1A, foi necessário decidir se o agente mantém o contexto da solicitação anterior dentro de uma mesma sessão. A alternativa foi enunciada como "só age quando é chamado", mas isso não determina se, ao receber "e os riscos?", o agente deve entender que a pergunta se refere ao projeto citado antes ou exigir que Carlos repita o nome do projeto. Manter o contexto é uma forma de o agente supor algo que não foi dito, o que já constitui uma decisão de iniciativa, ainda que mínima. A equipe optou por manter o contexto dentro da sessão e registrou a decisão como aberta.

**Ambiguidade: até onde vai o escopo de uma resposta.** No Cenário 1A, Carlos pergunta pelo marco vigente de um projeto. Ao construir a tirinha, a equipe percebeu que a informação poderia estar registrada em dois documentos com datas diferentes — situação explicitamente mencionada na Seção 2.2 como um dos riscos à confiabilidade. Não ficou claro se o agente deve responder com o documento mais recente, apresentar os dois e apontar a divergência, ou recusar-se a responder até que a inconsistência seja resolvida. Nenhuma das três opções contraria a alternativa enunciada, e a escolha altera substancialmente o que a pessoa vê.

**Ambiguidade: o silêncio é um comportamento, não a ausência de comportamento.** O Cenário 1B só pôde ser construído depois que a equipe reconheceu que o agente reativo dispõe da informação sobre a dependência entre projetos e a retém. Isso alterou a leitura da alternativa: não se trata de um agente que sabe menos, mas de um agente que sabe e não fala. A distinção não estava clara quando a alternativa foi enunciada.

**Impossibilidade do formato: a tirinha não mostra a pergunta que não foi feita.** A principal dificuldade de construção do Cenário 1B foi representar visualmente uma omissão. A tirinha mostra o que acontece, e a falha, neste caso, é algo que não acontece. Foi necessário deslocar a consequência para um painel posterior, situado na reunião, no qual a informação ausente aparece pela fala de outra pessoa. O formato obrigou a equipe a materializar a falha em um evento externo à interação com o agente — o que, por sua vez, revelou que essa falha só é observável fora do sistema.

**Decisão forçada: o que o agente faz quando não encontra.** Ao construir o Cenário 2B, ao chegar à terceira reformulação, tornou-se necessário decidir se o agente pode indicar o termo equivalente registrado na base. A equipe optou por representar essa sugestão no último painel como comportamento não definido — hachurada e marcada como tal —, mantendo a lacuna visível em vez de resolvê-la, e registrou a decisão como aberta no inventário da Seção 3.8.6.1.

**Ambiguidade: onde termina uma sessão de consulta.** Ao definir as situações que seriam usadas para forçar o protótipo, a equipe não soube responder o que aconteceria se Carlos retomasse a conversa no dia seguinte com uma referência vaga ao projeto consultado. O Cenário 1A trata o contexto como preservado, mas não estabelece por quanto tempo. A duração e o limite de uma sessão permaneceram indefinidos.

**Impossibilidade do formato: a tirinha não mede o acúmulo.** O Cenário 2B representa três reformulações em três painéis. Na prática, o custo do regime reativo é cumulativo e depende de quantas vezes por dia a pessoa erra o vocabulário. A tirinha representa o episódio, não a frequência, e a diferença entre um episódio isolado e uma ocorrência diária é justamente o que determinaria se a alternativa é sustentável.

#### 3.8.3.2 Protótipo 2 — Agente Proativo e Orientado à Jornada

O protótipo foi construído e executado a partir de situações em que o agente atua de maneira contextual durante uma atividade realizada pela pessoa. Para explorar tanto os comportamentos esperados quanto seus limites, foram produzidas duas tirinhas para cada situação: uma representando uma execução de sucesso e outra representando uma execução de falha.

As situações foram representadas considerando o ambiente tecnológico já utilizado no contexto da solução, especialmente o ecossistema corporativo baseado em SharePoint. A proatividade do agente foi representada por intervenções dinâmicas na própria interface utilizada pela pessoa, por meio de elementos sobrepostos à tela, sem exigir que o usuário abandone a atividade em andamento para iniciar uma conversa independente.

Todas as quatro tirinhas usam o mesmo projeto — **Modernização do Sistema de Sinalização** — para que a variação entre os cenários fique restrita ao comportamento do agente, e não ao conteúdo consultado.

| Tirinha | Persona | Situação | O que a execução investiga |
| :---: | --- | --- | --- |
| 1A | Carlos | Elaboração do Mapa de Benefícios, com o campo "Benefícios" ainda vazio | A intervenção proativa quando o contexto na tela é inequívoco |
| 1B | Carlos | Mesma elaboração, ainda na etapa de levantamento das entregas | O que acontece quando o agente confunde etapa intermediária com pendência |
| 2A | Mariana | Consulta à aba de Riscos do projeto, com um risco de alta criticidade aberto | O ganho da proatividade quando a informação é crítica e pertinente ao que está na tela |
| 2B | Mariana | Consulta a documentos de entrega, com o agente supondo análise de riscos | O custo de uma interpretação incorreta da intenção |

Um traço comum às quatro tirinhas merece registro, porque não foi planejado: em todas elas o agente **anuncia que está observando** — "Estou acompanhando sua atividade", seguido de um bloco "Contexto identificado". A equipe representou assim porque, sem esse anúncio, o leitor da tirinha não teria como saber de onde veio a intervenção. A consequência apareceu depois: tornar a observação visível é o que expõe, para a pessoa, que o sistema lê continuamente sua tela — exatamente a superfície que o RNF01 e o RNF02 restringem. A decisão de representação acabou revelando uma decisão de produto.

#### Execução dos cenários de sucesso

##### Cenário 1 — Pendência identificada durante a elaboração do Mapa de Benefícios

![Tirinha 1A — Execução de sucesso](img/tirinha-1A-2.png)

Carlos está preenchendo o Mapa de Benefícios do projeto Modernização do Sistema de Sinalização no Portal Estratégico. Já registrou o projeto, as entregas e os resultados esperados; o campo "Benefícios" permanece vazio na tela.

O agente observa a atividade e identifica dois elementos concretos: o documento aberto e a seção não preenchida. Com base neles, anuncia o contexto identificado e informa que há informação disponível que pode ajudar na definição dos benefícios daquele projeto. Antes de apresentar qualquer conteúdo, faz uma pergunta de confirmação — "Posso sugerir opções com base nos documentos disponíveis?" — com as alternativas *Sim, mostrar sugestões* e *Não, talvez depois*.

Carlos aceita. O agente devolve três benefícios candidatos, cada um com a fonte documental correspondente: redução de falhas operacionais até 30% (DOC-1287, Estudo Técnico de Viabilidade), melhoria da segurança para os usuários (DOC-0932, Relatório de Impacto Operacional) e aumento da confiabilidade do sistema (DOC-1765, Benchmark Sistemas de Sinalização). Carlos ajusta o conteúdo conforme sua necessidade e segue preenchendo o mapa. O agente encerra a intervenção e permanece disponível.

O cenário foi considerado bem-sucedido por três razões observáveis na tirinha. A intervenção se ancora em um elemento visível e inequívoco — um campo obrigatório vazio no documento aberto —, e não em inferência sobre a jornada. A confirmação antecede o conteúdo, de modo que a decisão de receber a sugestão permanece com Carlos. E cada item apresentado carrega a fonte, o que mantém a rastreabilidade exigida pelo RNF03 mesmo quando o agente fala primeiro.

O que o cenário **não** resolve, e ficou registrado como decisão em aberto: um campo vazio é evidência suficiente para intervir, mas nem todo campo vazio é uma pendência — é exatamente essa a hipótese que o Cenário 1B coloca à prova.

##### Cenário 2 — Informação relevante identificada durante uma atividade de acompanhamento

![Tirinha 2A — Execução de sucesso](img/tirinha-2A-2.png)

Mariana parte da Visão Geral do Portfólio no SharePoint — 48 projetos ativos, 7 em risco, 5 atrasados — para preparar análises de desempenho e qualidade. Abre o projeto Modernização do Sistema de Sinalização e navega até a aba de Riscos.

O agente identifica o projeto em análise e a aba consultada, e localiza ali um risco de alta criticidade em aberto: "Atraso no fornecimento de equipamentos", com impacto Alto e probabilidade Alta, ligado diretamente ao prazo do projeto. Apresenta a observação e pergunta se Mariana deseja ver os detalhes, o impacto e as ações recomendadas.

Mariana aceita. O agente devolve o detalhamento — atraso estimado de até 45 dias, afetando a conclusão da via e os testes operacionais — com três ações recomendadas: acompanhar a entrega com o fornecedor, avaliar o plano de contingência e revisar os marcos críticos. A fonte é declarada: DOC-1287, Relatório de Riscos do Projeto (v3.2). Mariana usa o conteúdo para atualizar sua análise e seguir para a preparação da reunião com os gestores.

O cenário foi considerado bem-sucedido porque a informação apresentada não é apenas pertinente ao domínio: ela é o item de maior criticidade dentro exatamente da aba que Mariana abriu. A proatividade, aqui, não adivinha a necessidade — ela hierarquiza o que já está na tela. É a condição mais favorável possível para o regime proativo, e serve de contraste para o Cenário 2B, em que o agente erra a atividade que Mariana está realizando.

O cenário também mostra o limite do que a tirinha consegue afirmar: ela representa uma intervenção. Se o mesmo agente repetisse essa oferta a cada aba aberta ao longo de uma manhã de trabalho, o julgamento seria outro, e o formato não distingue os dois casos.

#### Execução dos cenários de falha

##### Cenário 1 — Intervenção prematura diante de contexto insuficiente

![Tirinha 1B — Execução de falha](img/tirinha-1B-2.png)

A situação é deliberadamente quase idêntica à do Cenário 1A: Carlos, o mesmo Mapa de Benefícios, o mesmo campo "Benefícios" vazio. A diferença é o momento. Aqui ele acabou de iniciar a elaboração e informou apenas o projeto e algumas entregas — está na etapa de levantamento, não na de preenchimento dos benefícios.

O agente observa a mesma tela e chega a registrar, no painel 2, que os sinais são insuficientes: "Informações ainda parciais", "Não há confirmação da intenção de receber sugestões", e declara que aguardará novos sinais. No painel seguinte, porém, interpreta a ausência de benefícios como pendência que exige intervenção imediata, e apresenta a sugestão mesmo assim — antes que Carlos conclua a etapa anterior, interrompendo o fluxo da atividade.

Carlos recusa: "Ainda não. Estou pesquisando as informações das entregas." O agente responde que vai aguardar novos sinais e oferece duas alternativas — *Acompanhar atividade* e *Resumir o que foi preenchido*.

É no painel 6 que a execução falha de fato. O agente precisa decidir como se comportar depois da recusa, e o protótipo não define esse comportamento. O painel foi desenhado explicitamente como **"Situação não definida no protótipo"**, listando as quatro opções que a equipe não soube escolher — encerrar a intervenção, aguardar e observar, perguntar novamente mais tarde ou sugerir outra forma de apoio — e marcando a lacuna identificada: *estratégia de resposta após recusa inicial*.

A execução revela que a mesma evidência observada no Cenário 1A — um campo obrigatório vazio — sustenta tanto uma intervenção bem-sucedida quanto uma inadequada. O que separa os dois casos não está na tela: está na etapa do trabalho em que a pessoa se encontra, e essa etapa o agente não observa. É a decisão de **quando** intervir, e não a de **o que** oferecer, que a alternativa proativa deixa sem resposta.

Vale registrar o improviso: nos painéis 2 e 3 o agente primeiro reconhece que não tem sinais suficientes e em seguida intervém assim mesmo. A equipe manteve a contradição no desenho em vez de corrigi-la, porque ela é o próprio achado — não havia critério disponível para decidir entre "aguardar" e "intervir", e o protótipo teve de escolher um dos dois para que o painel seguinte existisse.

##### Cenário 2 — Intervenção baseada em interpretação incorreta do contexto

![Tirinha 2B — Execução de falha](img/tirinha-2B-2.png)

Mariana está no mesmo projeto do Cenário 2A, com a aba de Riscos aberta na tela. O agente identifica o contexto e conclui que ela está analisando os riscos do projeto — a leitura mais óbvia possível do que está visível.

A conclusão está errada. Mariana abriu aquela aba de passagem: sua atividade naquele momento são os documentos de entrega. O agente, sem evidência clara da intenção, decide intervir mesmo assim e oferece uma análise comparativa dos riscos com projetos similares. Mariana recusa e corrige a interpretação.

O agente ajusta o contexto — "Entendido! Você está consultando documentos de entrega" — e completa o ciclo de atualização. Mas o painel 5 registra que ele não possui regra sobre o que fazer em seguida: oferece uma nova busca sem saber se deveria estar oferecendo algo. O painel 6 formaliza a lacuna, marcado como **"Comportamento não definido"**, com as quatro opções em aberto — aguardar passivamente, perguntar o objetivo atual, sugerir apoio de forma proativa ou encerrar e aguardar nova interação — e a lacuna nomeada: *estratégia de recuperação após avaliação incorreta do contexto*.

A execução demonstra que uma informação pode ser correta, crítica e pertencente ao projeto certo e ainda assim ser inadequada, porque o critério que falhou não é o de relevância, e sim o de intenção. É a mesma informação do Cenário 2A, na mesma tela, para a mesma pessoa — e o resultado se inverte apenas porque a atividade real era outra.

Isso expõe o limite estrutural da alternativa proativa: a tela mostra **onde** a pessoa está, não **o que** ela está tentando fazer. O agente só tem acesso ao primeiro, e as duas coisas coincidem com frequência suficiente para que a proatividade pareça funcionar — e divergem com frequência suficiente para que ela erre sem aviso.

A comparação entre 2A e 2B foi o achado mais direto da execução, e ele não estava previsto: a equipe esperava que os cenários de falha revelassem problemas de recuperação de informação, e o que apareceu foi um problema de leitura de intenção, que nenhuma melhoria no RAG resolveria.

#### Diário de construção e execução

A construção das tirinhas evidenciou que a principal dificuldade do Protótipo 2 não está em representar a intervenção proativa em si, mas em definir as condições que autorizam o agente a decidir **quando**, **como** e **com que intensidade** iniciar uma interação. Nenhuma dessas três condições estava determinada quando a alternativa foi enunciada, e todas precisaram ser resolvidas painel a painel para que a tirinha pudesse ser desenhada.

**Decisão forçada: qual evidência de contexto autoriza o agente a falar.** Ao construir os cenários de sucesso, não bastou dizer que o agente "identifica o contexto": foi preciso decidir o que exatamente ele estaria vendo no painel anterior para que a intervenção seguinte parecesse justificada. A equipe optou por ancorar cada intervenção em um elemento visível na tela da pessoa — o documento aberto, o campo em preenchimento — e não em histórico ou inferência sobre a jornada. A decisão não foi planejada: ela apareceu porque, sem um elemento visível no painel, o leitor da tirinha não tem como saber por que o agente falou. Ficou registrada como aberta, porque restringe o agente a um contexto raso.

**Decisão forçada: onde a intervenção aparece na tela.** A alternativa foi enunciada sem definir a forma da intervenção. Ao desenhar, foi necessário escolher entre um elemento sobreposto ao ambiente de trabalho e uma interface conversacional separada. A equipe escolheu a sobreposição, porque é o que representa um agente que acompanha a jornada sem exigir que a pessoa abandone a atividade. A escolha, porém, é a que torna a intervenção interruptiva — as duas propriedades vêm juntas, e isso não estava claro antes de desenhar.

**Ambiguidade: informação correta não é o mesmo que momento adequado.** Ao construir os cenários de falha, a equipe percebeu que não sabia dizer o que diferencia uma oportunidade legítima de assistência de uma etapa intermediária de uma atividade em andamento. Nos dois casos o agente dispõe de informação pertinente ao domínio; a diferença está apenas no instante. Não houve critério que a equipe pudesse enunciar para separar os dois, e a tirinha 1B existe justamente porque essa distinção não foi encontrada.

**Ambiguidade: o que o agente faz depois de uma recusa.** A recusa foi representada, mas o painel seguinte não pôde ser desenhado com convicção. Recusar não significa rejeitar a assistência em definitivo: pode significar apenas que aquela sugestão não servia naquele momento. Permaneceu indefinido se o agente deve encerrar a intervenção, pedir esclarecimento, atualizar o contexto ou aguardar novos sinais — e, sem isso, não há como saber quando ele pode voltar a falar.

**Impossibilidade do formato: a tirinha não representa frequência nem intensidade.** É o limite mais consequente desta alternativa. Cada tirinha mostra uma intervenção isolada, e uma intervenção isolada quase sempre parece razoável. O que determina se a proatividade é aceitável ou insuportável é quantas vezes ela ocorre ao longo de um dia de trabalho, e isso o meio não representa. A mesma sugestão do Cenário 1A, repetida seis vezes em uma hora, seria outro sistema — e a tirinha desenha os dois de forma idêntica.

**Impossibilidade do formato: a tirinha não mostra a intenção da pessoa.** O Cenário 2B depende de Mariana estar fazendo uma coisa enquanto o agente supõe outra. Só que a intenção dela não é observável: foi preciso escrevê-la em uma fala explícita para que a falha ficasse legível. Na situação real, essa fala não existiria — o agente erraria sem que ninguém dissesse por quê. O formato obrigou a tornar visível exatamente aquilo que, no sistema real, é invisível, e é por isso que o critério de intervenção não pôde ser derivado da tirinha.

Como resultado, a execução dos cenários não validou uma implementação: tornou visíveis decisões comportamentais em aberto — o nível mínimo de contexto para intervir, a forma e o lugar da intervenção, o tratamento da recusa e os limites de frequência —, todas registradas no inventário da Seção 3.8.6.1.


### 3.8.4 Comparação das Alternativas

A comparação apresentada nesta seção decorre dos cenários e dos diários de construção e execução dos dois protótipos (Seções 3.8.3.1 e 3.8.3.2). Como as alternativas foram representadas com as mesmas personas, tipos de situação e formato de tirinha, as diferenças observadas dizem respeito principalmente à origem da iniciativa da interação. Os roteiros não são estritamente idênticos; por isso, a comparação é analítica, e não uma validação experimental isolada. A exploração não determina a adoção de uma alternativa; ela explicita as condições, os riscos e as decisões que cada uma transfere para a solução.

#### O que cada protótipo tornou visível

O Protótipo 1 tornou visível que o silêncio é um comportamento com consequências, e não a ausência de comportamento. Nos Cenários 1A e 2A, o regime reativo funciona bem quando a pessoa sabe o que precisa consultar e consegue formular a solicitação com os termos reconhecidos pela base: o agente reduz a busca manual, mantém a fonte associada à resposta e não interrompe a atividade. Já os Cenários 1B e 2B mostraram seus limites: uma informação relevante pode permanecer retida por não ter sido solicitada, e uma informação disponível pode não ser encontrada quando o vocabulário da pessoa diverge do vocabulário do acervo.

O Protótipo 2 tornou visível que o valor da proatividade depende menos de recuperar uma informação potencialmente útil do que de justificar a intervenção naquele instante. Nos Cenários 1A e 2A, a sugestão contextual reduz o esforço de localizar informações sem retirar da pessoa a decisão de aceitá-la ou utilizá-la. Nos Cenários 1B e 2B, uma informação correta e pertinente ao domínio se mostrou insuficiente para justificar a intervenção: o contexto pode ainda estar incompleto, ou a atividade observada pode não corresponder à intenção atual da pessoa.

#### Comparação dos efeitos observados

| Aspecto | Protótipo 1 — reativo sob demanda | Protótipo 2 — proativo e orientado à jornada |
| --- | --- | --- |
| Onde demonstrou valor | Consulta objetiva, com fonte, quando a pessoa conhece sua necessidade e sabe formulá-la. | Oferta de apoio no próprio fluxo de trabalho quando há contexto suficiente e a sugestão pode ser recusada sem interromper a atividade. |
| Falha característica | Omissão silenciosa: o agente pode ter a informação relevante e não apresentá-la; a consequência só aparece depois, fora da interação. | Intervenção inadequada: a sugestão é visível e pode interromper, distrair ou não corresponder à intenção da pessoa. |
| Principal incerteza de comportamento | Quanto contexto manter entre perguntas; como tratar documentos divergentes; e se, ao não localizar uma formulação, deve orientar a reformulação. | Qual evidência de contexto é suficiente para intervir; como tratar recusa ou correção; e qual frequência de intervenções é aceitável. |
| Rastreabilidade e governança | O par pergunta–resposta é delimitado e simplifica o registro previsto no RNF03. Não requer observação contínua da atividade. | Exige registrar também o contexto e a justificativa da intervenção. A observação da atividade amplia as implicações de confidencialidade e controle de acesso previstas no RNF01 e no RNF02. |
| Custo deslocado para a pessoa | Identificar a necessidade, iniciar a consulta e, em caso de vocabulário divergente, reformular até obter correspondência. | Avaliar, aceitar ou recusar sugestões e lidar com eventuais interrupções no fluxo de trabalho. |

#### O que surpreendeu o grupo

**A alternativa reativa não se sustenta como categoria pura.** A expectativa inicial era de que “reativo” e “proativo” fossem regimes mutuamente excludentes. O Cenário 2B mostrou o contrário: para que o regime reativo funcione com quem não domina o vocabulário do acervo, ele precisa ao menos orientar uma reformulação, por exemplo indicando o termo equivalente registrado na base. Essa orientação foi deixada explicitamente como comportamento não definido na tirinha. Como o RNF07 já prevê orientação para reformulação, a decisão não é binária: a iniciativa deve ser tratada como uma escala.

**As duas alternativas dependem de interpretar a intenção e o contexto.** No regime proativo, essa interpretação é necessária antes de o sistema falar. No reativo, ela aparece ao resolver referências em perguntas sucessivas, delimitar o escopo de uma resposta e reconhecer formulações diferentes para a mesma necessidade. A diferença está em quem arca primeiro com o erro: no proativo, o sistema pode interromper a pessoa; no reativo, a pessoa pode precisar reformular ou descobrir o vocabulário reconhecido pela base.

**Um regime falha em silêncio e o outro falha em voz alta.** A intervenção inadequada do Protótipo 2 é imediatamente perceptível, pode ser recusada e gera um sinal para avaliação. A falha do Protótipo 1, por sua vez, pode passar inteiramente despercebida: no Cenário 1B, nada indica que uma informação deixou de ser apresentada até que a consequência apareça fora do sistema. Portanto, métricas usuais do MVP, como fundamentação, alucinação e qualidade da recuperação, não medem automaticamente a cobertura de informações que a pessoa não chegou a pedir; essa cobertura exigirá casos de referência ou acompanhamento de uso específico.

**A confiabilidade não se resolve apenas pela iniciativa.** A ambiguidade observada no Cenário 1A — documentos potencialmente divergentes sobre o mesmo marco — afeta ambos os regimes. Seja por resposta sob demanda ou por sugestão proativa, a solução ainda precisa definir se prioriza a fonte mais recente, explicita a divergência ou limita a resposta. A origem da iniciativa não substitui a política de tratamento de evidências.

#### O que o formato tornou possível observar

A representação em tirinha obrigou a equipe a explicitar o intervalo entre uma interação e outra. Foi nesse intervalo que apareceram as falhas mais relevantes: o painel em que o agente reativo dispõe da informação e não a apresenta, e o painel em que o agente proativo decide intervir antes que a necessidade esteja caracterizada. O formato também permitiu manter visível uma lacuna de comportamento — a orientação de reformulação no Cenário 2B — sem transformá-la indevidamente em uma funcionalidade já definida.

O formato também impôs um limite que se tornou um achado: a tirinha não é capaz de representar a pergunta que não foi feita. Para construir o Cenário 1B foi necessário deslocar a consequência para fora da interação com o agente, e essa impossibilidade do meio revelou uma propriedade do próprio regime — a falha por omissão só é observável fora do sistema.

### 3.8.5 Limites da Exploração

Esta seção declara o que os protótipos produzidos, nos formatos utilizados, não são capazes de informar.

**Nenhum usuário real participou.** As quatro tirinhas de cada protótipo foram construídas e lidas pelos próprios integrantes do grupo. As falas atribuídas a Carlos e Mariana foram escritas pela equipe a partir das personas documentadas na Seção 2.5, que são hipóteses de projeto e não observação de campo. A exploração não informa se profissionais do PMO reconheceriam essas situações como representativas de sua rotina, nem se reagiriam às intervenções do Protótipo 2 da forma representada.

**O perfil executivo não foi explorado.** Roberto não aparece em nenhum dos oito cenários produzidos. Como sua jornada (Seção 2.5.2.1) é caracterizada por escassez de tempo e demanda por síntese, é plausível que o equilíbrio entre os dois regimes seja diferente para ele, mas os protótipos não oferecem nenhuma evidência a respeito.

**O vocabulário do Cenário 2B é uma suposição.** A divergência entre o termo empregado por Mariana e o registrado nos documentos foi inventada pela equipe. Não sabemos se os documentos do portfólio do Metrô efetivamente empregam vocabulário distinto daquele utilizado pelas pessoas ao formular perguntas, nem qual a extensão dessa divergência. Essa é uma hipótese verificável na massa documental real e ainda não verificada.

**A frequência das falhas é desconhecida, e é ela que decidiria a questão.** Cada tirinha representa um episódio. O que determinaria a adequação de cada regime é a taxa: quantas vezes por semana uma informação relevante deixa de ser consultada, e quantas vezes por dia uma intervenção proativa é inadequada. Um regime cuja falha ocorre uma vez por mês e outro cuja falha ocorre cinco vezes por dia produzem decisões de projeto opostas, e os protótipos são silenciosos quanto a isso. Apenas o uso continuado, ao longo de semanas, responderia.

**O custo cumulativo não é representável.** Pelo mesmo motivo, a exploração não informa o efeito acumulado das reformulações sucessivas sobre a disposição da pessoa em continuar utilizando o agente, nem o efeito acumulado das interrupções sobre sua tolerância a novas intervenções. Ambos são fenômenos de uso prolongado.

**Não há comparação entre formatos de prototipação.** Os dois protótipos utilizaram tirinhas, decisão tomada deliberadamente para isolar o regime de iniciativa como única variável entre as alternativas (Seção 3.8.2.1). O custo dessa decisão é que a exploração informa o que a tirinha revela, mas não informa o que outro formato revelaria. Comportamentos que dependem de ritmo, de simultaneidade ou da sensação de ser interrompido no meio de uma tarefa provavelmente apareceriam em uma encenação e não apareceram aqui.

**Nada foi verificado quanto à viabilidade técnica.** Os protótipos representam o comportamento desejado, não a capacidade do sistema de produzi-lo. Se o pipeline consegue identificar o contexto da atividade com a precisão que o Protótipo 2 pressupõe, ou reconhecer formulações divergentes com a cobertura que o Protótipo 1 exigiria, são perguntas que dependem de experimentação com o núcleo de PLN e das métricas previstas no RNF06.

**A aceitação institucional da observação contínua não foi avaliada.** A exploração tornou visível que o regime proativo exige que o sistema acompanhe a atividade da pessoa, e que isso incide sobre as restrições de confidencialidade e controle de acesso do parceiro. Se essa observação seria admissível pelas áreas técnicas e de compliance do Metrô é uma questão a ser tratada com o parceiro, e não algo que os protótipos possam responder.

### 3.8.6 Insumos para a Equipe

#### 3.8.6.1 Inventário de Decisões em Aberto

| Decisão em aberto | Alternativas identificadas | O que está em jogo |
| --- | --- | --- |
| Contexto entre perguntas e duração da sessão | Manter o contexto somente na sessão; exigir nova explicitação; ou definir expiração por tempo. | Equilibrar continuidade da conversa, precisão da referência e controle da pessoa sobre o escopo. |
| Resposta diante de fontes divergentes | Priorizar a fonte mais recente; explicitar a divergência; ou interromper a resposta até validação. | Preservar a confiabilidade e a transparência sem ocultar inconsistências documentais. |
| Orientação quando não houver correspondência de vocabulário | Informar apenas a ausência; sugerir termos equivalentes; ou solicitar esclarecimento. | Atender simultaneamente ao RNF04, sem alucinar, e ao RNF07, orientando a reformulação. |
| Informação relevante não solicitada | Permanecer em silêncio; apresentar relação contextual sob demanda; ou sugerir a informação proativamente. | Definir o grau de iniciativa aceitável e reduzir falhas de cobertura sem gerar intrusão. |
| Gatilho e frequência da intervenção proativa | Intervir com evidência mínima; exigir sinais adicionais; e limitar novas intervenções após recusa. | Evitar interrupções e, ao mesmo tempo, não deixar de oferecer apoio em situações relevantes. |
| Tratamento de recusa ou correção | Encerrar a sugestão; pedir esclarecimento; ou atualizar o contexto e aguardar novos sinais. | Manter a pessoa no controle e evitar repetição de intervenções inadequadas. |

#### 3.8.6.2 Repertório de Situações

O repertório reúne as oito situações efetivamente rodadas nas Seções 3.8.3.1 e 3.8.3.2. A última coluna registra o que o protótipo **não** conseguiu atender — que é o material de trabalho para a equipe. A coluna "Improviso" indica as situações em que alguém precisou decidir na hora algo que o protótipo não definia.

| # | Situação e pedido registrado | Protótipo / Persona | Improviso | O que o protótipo não conseguiu atender |
| :---: | --- | --- | :---: | --- |
| S1 | Preparação de reunião: consulta ao marco vigente de um projeto, seguida de “e os riscos?” | P1 · Carlos | Sim | Não define se “os riscos” se referem ao projeto citado antes ou exigem nova explicitação. Contexto mantido por improviso, sem regra de duração de sessão. |
| S2 | Mesma preparação, com uma dependência de contrato atrasado existente na base e não consultada | P1 · Carlos | Não | Não apresenta a informação, porque ninguém perguntou. A falha não é detectável pelo sistema: do ponto de vista dele, a interação foi bem-sucedida. |
| S3 | Consolidação do balanço mensal: comparação do avanço físico entre dois meses, com o vocabulário dos documentos | P1 · Mariana | Não | Nada a registrar — é o caso em que o regime reativo funciona plenamente. Serve de contraste para S4. |
| S4 | Mesma consolidação, formulada como “quais projetos estão atrasados” | P1 · Mariana | Sim | Responde apenas que não localizou, sem indicar o termo equivalente da base. Foram necessárias três reformulações. O painel de sugestão de termo ficou hachurado como comportamento não definido. |
| S5 | Elaboração do Mapa de Benefícios, com pendência identificada pelo agente a partir da tela | P2 · Carlos | Sim | Não define qual evidência de contexto é suficiente para autorizar a intervenção. Funcionou porque a equipe escolheu, por improviso, ancorar em um elemento visível na tela. |
| S6 | Atividade de acompanhamento do portfólio, com informação relacionada oferecida durante a navegação | P2 · Mariana | Não | Não define limite de frequência. Uma intervenção isolada parece adequada; o protótipo não representa a repetição. |
| S7 | Acompanhamento ainda em curso, com o agente intervindo antes de a necessidade estar caracterizada | P2 · Carlos | Sim | Não há critério que separe uma oportunidade legítima de assistência de uma etapa intermediária da atividade. A distinção foi decidida caso a caso ao desenhar. |
| S8 | Navegação alternando entre informações, com o agente interpretando incorretamente a atividade | P2 · Mariana | Não | Não define o comportamento após a recusa ou correção: encerrar, pedir esclarecimento, atualizar o contexto ou aguardar novos sinais. O painel seguinte ficou sem definição. |

Sete das oito situações terminam em algo que o protótipo não resolve. A única exceção é S3, em que o vocabulário da solicitação coincide com o dos documentos e o regime reativo funciona sem lacuna — e é por isso que ela serve de contraste para S4, sua situação gêmea com vocabulário divergente.

Quatro situações exigiram improviso, ou seja, alguém precisou decidir na hora algo que o protótipo não definia: S1, S4, S5 e S7. Nas demais, a lacuna apareceu sem que fosse necessário contorná-la para seguir — em S8, inclusive, a equipe optou por registrar o comportamento como não definido no próprio painel, em vez de escolher um. A concentração das lacunas fora das condições favoráveis é o principal insumo que a exploração entrega para a Sprint 3.

---

# 4. Modelagem de Dados

Esta seção apresenta a modelagem de dados da solução em três níveis complementares: conceitual, lógico e físico. A modelagem foi definida para o MVP do agente inteligente de Gestão de Portfólio de Projetos do Metrô, considerando os requisitos funcionais e não funcionais descritos na Seção 3, a arquitetura de componentes apresentada na Seção 5.2 e a estrutura observada no SharePoint do parceiro.

O objetivo da modelagem é representar, de forma simples e implementável, os dados necessários para que o agente consiga receber solicitações em linguagem natural, classificar intenções, consultar informações de projetos, acessar documentos e planilhas vinculadas no SharePoint, preparar contexto controlado para o Copilot, respeitar permissões por perfil e registrar auditoria das interações.

## 4.1 Especificação da Base de Dados

A base de dados do MVP foi desenhada para funcionar como uma camada intermediária entre o agente conversacional, o núcleo de PLN, o Copilot Studio, os fluxos do Power Automate e as fontes simuladas do SharePoint. Como o projeto utiliza dados sintéticos, a modelagem não replica dados reais do Metrô; ela replica a estrutura necessária para representar projetos, subportfólios, artefatos documentais, cronogramas, avanços físico-econômicos, entregas, marcos, termos de abertura, termos de encerramento, riscos, mudanças, intenções e registros de auditoria.

A decisão de modelagem adotada foi reduzir a complexidade para um MVP, evitando uma tabela para cada página, lista ou biblioteca do SharePoint. Em vez disso, documentos, links, anexos, prompts, normativos e planilhas são representados pela tabela `project_artifacts`. Quando uma lista do parceiro possui ciclo de vida e campos estruturados relevantes para consulta, ela é representada por uma tabela própria, como `project_progress_updates`, `project_deliverables_milestones`, `project_charters` ou `project_closure_terms`. Quando a origem é apenas documental ou um anexo de suporte, ela permanece como artefato consultável.

Essa abordagem contempla o funcionamento observado no ambiente do parceiro: algumas listas do SharePoint apresentam linhas com links ou anexos para arquivos Excel, especialmente cronogramas. No MVP, o link ou anexo da planilha é armazenado em `project_artifacts.sharepoint_url`, `attachment_name` e `attachment_url`; a aba e o intervalo de leitura são indicados por `excel_sheet_name` e `excel_table_or_range`; e cada linha relevante do cronograma é normalizada em `schedule_items`, preservando a origem por meio de campos como `source_sheet_name`, `source_row_number` e `source_cell_range`.

Riscos/problemas e mudanças aparecem em duas granularidades no inventário do parceiro: projeto e subportfólio. Para evitar duplicação desnecessária, o modelo adota `scope_type` em `risk_issue_items` e `change_records`, com restrições que obrigam o preenchimento de exatamente um alvo: `project_id` quando o escopo é projeto, ou `subportfolio_id` quando o escopo é subportfólio. O histórico dos riscos e problemas foi separado em `risk_issue_history`, preservando a evolução de status e criticidade ao longo do tempo.

O modelo também suporta a avaliação do núcleo de PLN implementado no notebook `src/notebooks/classificador_intencoes_metro.ipynb`. Esse notebook trabalha com um catálogo hierárquico de intenções em dois níveis: `macrointencao` (`CONSULTA`, `TRANSACAO`, `ALERTA` e `FORA_DE_ESCOPO`) e intenção específica, totalizando 31 classes na execução de referência. Por isso, a tabela `intent_catalog` registra tanto a macrointenção quanto a intenção específica, o fluxo associado, o handler previsto e os limiares de confiança usados para decidir entre roteamento, acionamento de handler específico ou resposta de limitação.

A tabela `intent_test_cases` armazena exemplos rotulados derivados dos templates do notebook, preservando `template_id`, variação superficial, texto normalizado e split (`treino`, `validacao`, `teste`). Isso mantém a rastreabilidade do protocolo sem vazamento usado no classificador, em que a divisão é feita por template e não por frase. As interações reais ou simuladas são registradas em `ai_interactions`, incluindo macrointenção prevista, confiança da macro, intenção específica prevista, confiança da intenção, handler selecionado, alternativas top-k e eventual resposta de limitação. As fontes consultadas são rastreadas por `consulted_sources`, permitindo verificar quais documentos, extratos, planilhas ou linhas foram usados para compor o retorno ao usuário.

O modelo físico inicial está implementado em [`src/database/sql/01_create_database.sql`](../src/database/sql/01_create_database.sql). A documentação operacional dos artefatos de banco, incluindo carga inicial sintética e rollback controlado, está registrada em [`src/database/docs/README.md`](../src/database/docs/README.md).

## 4.2 Modelo Conceitual de Dados

O modelo conceitual é uma representação abstrata de alto nível, focada nas regras do negócio e no entendimento das entidades que precisam existir para a solução. Neste nível, não são definidos tipos de dados, chaves primárias, chaves estrangeiras ou detalhes de implementação.

As principais entidades conceituais do MVP são:

| Entidade | Descrição de negócio |
|---|---|
| Subportfólio | Categoria estratégica que agrupa projetos do portfólio, como Turnaround, Expansão da Rede Metrô e Gestão e Finanças. |
| Situação de Subportfólio | Registro periódico da situação de um subportfólio, com data de referência, item, situação e ano. |
| Projeto | Iniciativa acompanhada pelo PMO, associada a um subportfólio e composta por documentos, cronograma, status, riscos e mudanças. |
| Artefato do Projeto | Fonte de informação vinculada ao projeto, podendo ser TAP, cronograma, relatório, planilha, lista SharePoint, prompt ou normativo. |
| Extrato de Fonte | Parte extraída de um documento, lista ou planilha para consulta, referência e montagem de contexto controlado no Copilot. |
| Item de Cronograma | Linha estruturada extraída de um cronograma, inclusive quando a origem for uma planilha Excel vinculada no SharePoint. |
| Avanço do Projeto | Medição periódica de avanço físico e econômico previsto e realizado. |
| Entrega ou Marco | Entrega, marco ou etapa relevante do projeto, com datas prevista e realizada e status de acompanhamento. |
| Atualização de Status | Registro de avanço, situação, impedimentos, próximos passos e resumo executivo de um projeto. |
| Termo de Abertura | Registro estruturado do TAP, incluindo liderança, equipe, objetivo, justificativa, escopo, benefícios, premissas, restrições, custos, revisão e situação de liberação. |
| Termo de Encerramento | Registro estruturado do encerramento do projeto, com situação, justificativa, pendências, custo realizado e data de encerramento. |
| Benefício | Benefício esperado ou detalhado para o projeto, ligado ao TAP ou ao Mapa de Benefícios. |
| Risco ou Problema | Evento de risco ou problema materializado que afeta um projeto ou subportfólio. |
| Histórico de Risco ou Problema | Evolução temporal de status, criticidade e comentários de um risco ou problema. |
| Mudança | Registro de alteração de prazo, escopo, custo, prioridade ou outro aspecto relevante de projeto ou subportfólio. |
| Usuário | Pessoa que interage com o agente, vinculada a um perfil como Diretoria, PMO, Líder de Subportfólio ou Equipe de Projeto. |
| Regra de Acesso | Definição conceitual de quais informações um usuário ou perfil pode consultar, alterar ou exportar. |
| Intenção | Necessidade identificada pelo núcleo de PLN, organizada em macrointenção e intenção específica conforme o notebook do classificador. |
| Template de Prompt | Prompt padronizado utilizado para orientar fluxos de resposta, geração documental ou consultas recorrentes. |
| Conversa | Agrupamento das interações realizadas por um usuário em um canal conversacional. |
| Interação | Pergunta/resposta auditável, contendo solicitação, intenção classificada, rota de processamento e resposta. |
| Fonte Consultada | Documento, extrato, planilha, linha ou lista usada para explicar a origem das informações devolvidas ao usuário. |
| Evento de Auditoria | Registro técnico ou funcional gerado durante o processamento da interação. |
| Solicitação Fora de Escopo | Pergunta que não pertence ao catálogo suportado pelo agente, mas deve ser registrada para análise futura. |
| Caso de Teste de Intenção | Exemplo rotulado usado para avaliar o desempenho do classificador, preservando template, split e texto normalizado. |

<div align="center">
  <img src="img/modelo-conceitual.png" alt="Modelo conceitual de dados" width="100%">
</div>

<p align="center"><strong>Figura 18</strong> - Modelo conceitual de dados.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>

O código-fonte do diagrama está versionado em [`docs/diagrams/modelo-conceitual.puml`](diagrams/modelo-conceitual.puml) e pode ser regerado com PlantUML e Graphviz instalados:

```bash
java -jar plantuml.jar -charset UTF-8 -tpng -o ../img docs/diagrams/modelo-conceitual.puml
```

## 4.3 Modelo Lógico de Dados

O modelo lógico detalha o modelo conceitual em formato de tabelas, atributos principais, chaves primárias e chaves estrangeiras. Ele ainda não representa o código final do banco, mas define a estrutura lógica que deve ser implementada.

Para manter o escopo adequado ao MVP e incorporar o inventário do parceiro, a modelagem lógica foi consolidada em 25 tabelas:

| Tabela | PK | FKs principais | Finalidade |
|---|---|---|---|
| subportfolios | id | - | Armazena os subportfólios estratégicos, responsáveis, aprovadores, apoio e identificador de origem do parceiro. |
| subportfolio_status_updates | id | subportfolio_id → subportfolios.id | Armazena a situação periódica do subportfólio por data de referência, item, situação e ano. |
| projects | id | subportfolio_id → subportfolios.id | Armazena os projetos do portfólio, incluindo status programa/projeto e identificador de origem. |
| project_artifacts | id | project_id → projects.id | Representa documentos, listas, links, anexos, planilhas, prompts e normativos vindos do SharePoint ou da massa sintética. |
| source_extracts | id | artifact_id → project_artifacts.id, project_id → projects.id | Armazena extratos consultáveis de documentos, listas e planilhas para composição de contexto no Copilot e rastreabilidade de fontes. |
| schedule_items | id | project_id → projects.id, artifact_id → project_artifacts.id, parent_item_id → schedule_items.id | Armazena linhas estruturadas de cronograma, inclusive extraídas de Excel. |
| project_progress_updates | id | project_id → projects.id | Armazena avanço físico e econômico previsto e realizado por data de referência. |
| project_status_updates | id | project_id → projects.id, artifact_id → project_artifacts.id | Armazena avanço, situação e resumo de status dos projetos. |
| project_deliverables_milestones | id | project_id → projects.id | Armazena entregas e marcos com descrição, datas prevista e realizada e status. |
| project_charters | id | project_id → projects.id, subportfolio_id → subportfolios.id, artifact_id → project_artifacts.id | Armazena o Termo de Abertura do Projeto de forma estruturada. |
| project_closure_terms | id | project_id → projects.id, artifact_id → project_artifacts.id | Armazena o Termo de Encerramento do Projeto. |
| project_benefits | id | project_id → projects.id, charter_id → project_charters.id, source_artifact_id → project_artifacts.id | Armazena benefícios esperados ou detalhados para o projeto. |
| risk_issue_items | id | project_id → projects.id ou subportfolio_id → subportfolios.id, source_artifact_id → project_artifacts.id | Armazena riscos e problemas em estrutura unificada por escopo. |
| risk_issue_history | id | risk_issue_id → risk_issue_items.id | Armazena histórico de status, criticidade e comentários de riscos e problemas. |
| change_records | id | project_id → projects.id ou subportfolio_id → subportfolios.id, source_artifact_id → project_artifacts.id | Armazena registros de mudanças de projeto ou subportfólio. |
| users | id | - | Armazena usuários simulados ou autenticados via Entra ID em evolução futura. |
| access_rules | id | user_id → users.id, subportfolio_id → subportfolios.id, project_id → projects.id | Armazena regras de acesso por usuário, perfil e escopo. |
| intent_catalog | id | - | Armazena macrointenção, intenção específica, fluxo, handler e limiares do classificador. |
| prompt_templates | id | intent_id → intent_catalog.id | Armazena templates de prompts padronizados para Copilot, Power Automate, M365 Copilot e PLN local. |
| ai_conversations | id | user_id → users.id | Armazena sessões conversacionais. |
| ai_interactions | id | conversation_id → ai_conversations.id, user_id → users.id, intent_id → intent_catalog.id, prompt_template_id → prompt_templates.id | Armazena pergunta, macrointenção, intenção específica, confianças, handler, alternativas, rota, resposta e status da interação. |
| consulted_sources | id | interaction_id → ai_interactions.id, artifact_id → project_artifacts.id, extract_id → source_extracts.id, project_id → projects.id | Armazena as fontes consultadas para compor uma resposta. |
| audit_events | id | interaction_id → ai_interactions.id, user_id → users.id | Armazena eventos de auditoria técnica e funcional. |
| out_of_scope_requests | id | interaction_id → ai_interactions.id, reviewed_by → users.id | Armazena perguntas fora do escopo suportado. |
| intent_test_cases | id | intent_id → intent_catalog.id | Armazena exemplos rotulados com template_id, variação, texto normalizado e split agrupado. |

<div align="center">
  <img src="img/modelo-logico.png" alt="Modelo lógico de dados" width="100%">
</div>

<p align="center"><strong>Figura 19</strong> - Modelo lógico de dados.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>

O código-fonte do diagrama está versionado em [`docs/diagrams/modelo-logico.puml`](diagrams/modelo-logico.puml) e pode ser regerado com PlantUML e Graphviz instalados:

```bash
java -jar plantuml.jar -charset UTF-8 -tpng -o ../img docs/diagrams/modelo-logico.puml
```

As principais regras de integridade do modelo lógico são:

- todo projeto deve pertencer a um subportfólio;
- toda situação de subportfólio deve apontar para um subportfólio e uma data de referência;
- todo avanço físico/econômico deve apontar para um projeto e uma data de referência;
- toda entrega ou marco deve apontar para um projeto;
- todo cronograma extraído deve apontar para um projeto e, quando houver origem documental, para um artefato de origem;
- todo TAP estruturado deve apontar para um projeto e pode apontar para o artefato documental que originou seus campos;
- todo termo de encerramento deve apontar para um projeto e pode apontar para o artefato documental correspondente;
- todo benefício deve apontar para um projeto e pode apontar para o TAP ou artefato que o fundamenta;
- todo risco/problema deve ter escopo exclusivo: projeto ou subportfólio, nunca ambos ao mesmo tempo;
- todo registro de mudança deve ter escopo exclusivo: projeto ou subportfólio, nunca ambos ao mesmo tempo;
- todo histórico de risco/problema deve apontar para o risco/problema original;
- todo extrato consultável deve apontar para um artefato e pode apontar para um projeto quando o conteúdo for específico de uma iniciativa;
- toda resposta que utilizar informação documental, lista ou planilha deve possuir ao menos uma fonte em consulted_sources;
- toda interação deve registrar a intenção classificada ou o motivo de falha/fora de escopo;
- classificações abaixo dos limiares definidos pelo classificador devem preservar a macrointenção, a confiança, as alternativas e a resposta de limitação;
- casos de teste de intenção devem preservar template_id e dataset_split para evitar vazamento entre treino, validação e teste;
- o agente deve consultar access_rules antes de retornar informações restritas;
- perguntas fora do catálogo devem gerar registros em out_of_scope_requests;
- leituras, classificações, consultas a fontes, respostas do Copilot e acionamentos de fluxos devem gerar eventos em audit_events.

## 4.4 Modelo Físico de Dados

O modelo físico corresponde à implementação real do banco de dados. Para o MVP, ele foi materializado em um script SQL executável para PostgreSQL 14+, contendo tipos de dados exatos, tamanhos de campos, chaves primárias, chaves estrangeiras, restrições, índices e comentários.

O script físico está em:

- [`src/database/sql/01_create_database.sql`](../src/database/sql/01_create_database.sql)

A documentação técnica dos scripts de banco está em:

- [`src/database/docs/README.md`](../src/database/docs/README.md)

Essa documentação serve como ponto de entrada para os scripts de banco da solução. Além do script de criação, os arquivos de carga inicial sintética e rollback controlado também estão versionados em `src/database/sql`.

O modelo físico adota as seguintes decisões:

- uso de `UUID` como chave primária nas tabelas;
- preservação dos identificadores textuais vindos das listas do parceiro em `partner_source_id`, sem substituir a chave técnica interna;
- unicidade parcial de `partner_source_id` nas tabelas alimentadas por listas e anexos do parceiro, permitindo cargas idempotentes quando houver ID externo e mantendo flexibilidade para registros sem origem sincronizada;
- uso de `JSONB` para metadados flexíveis, como atributos vindos do SharePoint, entidades extraídas pelo PLN e payloads de auditoria;
- tabelas específicas para listas estruturadas do parceiro que possuem uso efetivo no MVP, como situação de subportfólio, avanço, entregas e marcos, TAP, termo de encerramento e benefícios;
- uso de `scope_type` em `risk_issue_items` e `change_records` para representar registros de projeto e de subportfólio em uma estrutura única, com restrições que impedem alvo ambíguo;
- separação do histórico de riscos/problemas em `risk_issue_history`, preservando a evolução temporal sem sobrescrever o registro principal;
- armazenamento dos campos produzidos pelo classificador do notebook, incluindo `macro_intent`, `specific_intent`, confiança de macrointenção, confiança de intenção específica, handler, alternativas e resposta de limitação;
- preservação de `template_id`, texto normalizado e split agrupado em `intent_test_cases`, em alinhamento com o protocolo de avaliação sem vazamento do notebook;
- uso de `CHECK CONSTRAINTS` para domínios controlados, como status de projeto, tipo de artefato, tipo de fonte e perfil de usuário;
- uso de `FOREIGN KEYS` para preservar integridade entre projetos, artefatos, cronogramas, interações, fontes consultadas e auditoria;
- uso de índices para os principais caminhos de consulta do MVP, como projeto, subportfólio, status, artefato, cronograma, intenção, interação e eventos de auditoria;
- compatibilidade com o ecossistema Microsoft, registrando o componente alvo da intenção, os prompts usados por Copilot/Power Automate/M365 Copilot e as fontes consultadas a partir do SharePoint.

O tratamento das planilhas Excel vinculadas em listas do SharePoint também foi contemplado fisicamente. A tabela `project_artifacts` armazena o link da planilha, a aba e o intervalo de leitura; a tabela `schedule_items` armazena as linhas normalizadas do cronograma, incluindo a referência à aba, linha e intervalo de células de origem; a tabela `source_extracts` preserva extratos textuais ou estruturados quando a planilha também precisar ser usada como fonte consultável; e a tabela `consulted_sources` registra qual documento, extrato, planilha, linha ou intervalo foi utilizado para compor a resposta.

# 5. Solução Técnica (Design)

## 5.1 Diagrama de Classes

Esta seção **evolui** a modelagem estática apresentada na Seção 3.1.2, e não a substitui. Aquela modelagem, produzida na Sprint 1, representa o pipeline de processamento: como uma `Solicitacao` percorre classificação, roteamento e geração de resposta. Ela permanece válida e continua sendo a referência da rastreabilidade da Seção 3.1.4.

O que a Sprint 2 acrescentou foi a camada que faltava: o **domínio persistido**. Com o inventário de listas do parceiro, essa camada foi refinada para representar também situação de subportfólio, avanço físico-econômico, entregas, marcos, termos de abertura, termos de encerramento, benefícios e histórico de riscos/problemas. O diagrama abaixo une o pipeline de processamento, o conhecimento consultável, a auditoria e o domínio persistido.

### 5.1.1 Modelo consolidado

<div align="center">
  <img src="img/classes-consolidado.png" alt="Diagrama de classes consolidado, com o pipeline de processamento, a interação e governança, o conhecimento consultável e o domínio do portfólio" width="100%">
</div>

<p align="center"><strong>Figura 20</strong> - Diagrama de classes consolidado, unindo o pipeline de processamento e o domínio persistido.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>

O código-fonte do diagrama está versionado em [`docs/diagrams/classes-consolidado.puml`](diagrams/classes-consolidado.puml). Para regerar a imagem, com PlantUML e Graphviz instalados:

```bash
plantuml -charset UTF-8 -tpng -o ../img docs/diagrams/classes-consolidado.puml
```


### 5.1.2 O que mudou em relação à Seção 3.1.2

| Classe da Sprint 1 | Situação na Sprint 2 | Motivo |
|---|---|---|
| `Solicitacao`, `PipelinePLN`, `Intencao`, `RoteadorIntencao`, `Resposta` | Mantidas | Continuam descrevendo o caminho de processamento e sustentam a rastreabilidade da Seção 3.1.4 |
| `ClassificadorIntencao`, `RecuperadorInformacao`, `AnalisadorComparativo`, `ExecutorFluxoAutomatizado`, `GeradorLLM` | Movidas para a Seção 5.2 | São componentes de arquitetura, não entidades de domínio. O diagrama de componentes é o lugar correto para elas |
| `CategoriaIntencao`, `RotaProcessamento` | Absorvidas como atributos | `macrointencao` e `rota` passaram a ser valores de `Intencao` e `Interacao`, persistidos em `intent_catalog` e `ai_interactions` |
| `DocumentoProjeto` | Renomeada para `Artefato` | O modelo lógico da Seção 4.3 usa `project_artifacts`, e a entidade cobre documentos, listas, planilhas e normativos, não apenas documentos |
| `TrechoRecuperado` | Mantida | Corresponde a `source_extracts` e é o que a `FonteConsultada` referencia |
| `EntidadeExtraida` | Mantida na Seção 3.1.2 | Existe no pipeline, mas não é persistida no MVP; não aparece no modelo de dados |
| `SugestaoProativa`, `ConfiguracaoProatividade` | Mantidas na Seção 3.1.2 | Sustentam RF09 e RF10, cujo escopo está declarado na Seção 3.1.5 |
| — | `Interacao`, `Conversa`, `Usuario`, `RegraAcesso`, `FonteConsultada`, `EventoAuditoria`, `SolicitacaoForaDeEscopo` | Novas. Vieram do modelo de dados: sem persistência, a Sprint 1 não precisava representá-las |
| — | `Subportfolio`, `SituacaoSubportfolio`, `Projeto`, `AvancoProjeto`, `EntregaMarco`, `ItemCronograma`, `TermoAbertura`, `TermoEncerramento`, `Beneficio`, `RiscoProblema`, `HistoricoRiscoProblema`, `Mudanca` | Novas ou refinadas. Representam o domínio do portfólio após o alinhamento com as listas do parceiro |

### 5.1.3 Decisões refletidas no diagrama

- **`Resposta` é composição de `Interacao`, e não entidade independente.** Uma resposta não existe fora da interação que a originou, e `declararLimitacao()` materializa o comportamento exigido pelo RF08: sem fonte suficiente, a resposta declara a limitação em vez de completar a lacuna.
- **`FonteConsultada` liga a resposta ao `TrechoRecuperado`, e não ao `Artefato`.** A rastreabilidade exigida pelo RNF03 precisa apontar o trecho utilizado, não apenas o documento de origem.
- **`Intencao` carrega os limiares e as confianças.** Os valores de 0,550 e 0,700 definidos na Seção 8.10.3 pertencem ao catálogo, não ao código, de modo que possam ser ajustados sem nova implantação, à medida que novas execuções do benchmark recalibrem os limiares. `acimaDoLimiar()` é o que decide se um handler é acionado.
- **`RegraAcesso` é classe, e não atributo de `Usuario`.** O mesmo usuário pode ter níveis diferentes por subportfólio ou por projeto, o que o RNF02 exige e um atributo simples não representaria.
- **`RiscoProblema` e `Mudanca` têm escopo explícito.** Como o parceiro mantém registros em nível de projeto e de subportfólio, o modelo persistido usa `scope_type` e constraints para impedir que um mesmo registro aponte simultaneamente para os dois níveis.
- **`TermoAbertura`, `TermoEncerramento` e `Beneficio` são entidades estruturadas.** Esses dados poderiam existir apenas como artefatos, mas possuem campos consultáveis no MVP e alimentam diretamente respostas sobre escopo, justificativa, custos, benefícios e encerramento.
- **`ItemCronograma.somaDosPesosFecha()` está no domínio.** A validação de que os pesos fecham em 100%, prevista na Seção 2.4.3, é regra de negócio e não de interface.
- **`SolicitacaoForaDeEscopo` é entidade própria.** Registrar o que o agente não soube responder é insumo para evoluir o catálogo, e não um estado descartável da interação.

### 5.1.4 Correspondência com o modelo de dados

A relação com as tabelas da Seção 4.3 não é de um para um. `Resposta`, por exemplo, é persistida em colunas de `ai_interactions`, porque não tem ciclo de vida próprio no banco.

| Classe | Tabelas correspondentes |
|---|---|
| `Subportfolio`, `Projeto` | `subportfolios`, `projects` |
| `SituacaoSubportfolio` | `subportfolio_status_updates` |
| `AvancoProjeto` | `project_progress_updates` |
| `EntregaMarco` | `project_deliverables_milestones` |
| `Artefato`, `TrechoRecuperado` | `project_artifacts`, `source_extracts` |
| `ItemCronograma` | `schedule_items` |
| `TermoAbertura` | `project_charters` |
| `TermoEncerramento` | `project_closure_terms` |
| `Beneficio` | `project_benefits` |
| `RiscoProblema`, `HistoricoRiscoProblema` | `risk_issue_items`, `risk_issue_history` |
| `Mudanca` | `change_records` |
| `Usuario`, `RegraAcesso` | `users`, `access_rules` |
| `Intencao` | `intent_catalog`, `prompt_templates` |
| `Conversa`, `Interacao`, `Resposta` | `ai_conversations`, `ai_interactions` |
| `FonteConsultada` | `consulted_sources` |
| `EventoAuditoria` | `audit_events` |
| `SolicitacaoForaDeEscopo` | `out_of_scope_requests` |

As tabelas `project_status_updates` e `intent_test_cases` não aparecem como classes próprias: a primeira é um registro narrativo de acompanhamento consultado por relatório, enquanto a segunda pertence ao ciclo de avaliação do classificador descrito na Seção 8.10.1, não ao runtime conversacional.

## 5.2 Diagrama de Componentes da UML

O Diagrama de Componentes representa a **estrutura lógica e técnica dos principais módulos da solução e suas interações**. A representação evidencia as fronteiras entre o chat web como canal de interação, o backend da aplicação, o núcleo autoral de Processamento de Linguagem Natural (PLN), a camada de recuperação aumentada por geração (RAG), os workflows guiados do backend e os serviços de Inteligência Artificial utilizados pela solução. Microsoft Teams, Microsoft Copilot Studio, Microsoft Entra ID e o SharePoint corporativo integram a arquitetura-alvo e são descritos como evolução na Seção 5.2.4 e no capítulo de evolução; eles não participam do runtime atualmente implementado.

A arquitetura parte do **chat web** — a bancada React por onde o usuário interage com o agente — e de uma **API da aplicação** (FastAPI), que centraliza o recebimento das mensagens, o gerenciamento da conversa e a integração com os demais componentes. A entrada pode ocorrer por texto ou por voz, cuja transcrição é realizada pelo serviço de Speech-to-Text (Azure AI Speech) antes do processamento do núcleo da aplicação.

O processamento da solicitação é realizado pelo **Pilar 1 — Núcleo de PLN e Roteamento**, responsável pelo pré-processamento, identificação e classificação da intenção, validação de escopo e extração das entidades necessárias. A intenção identificada é associada ao **catálogo de intenções da solução**, que relaciona as solicitações às capacidades e funcionalidades previstas para o produto.

A partir dessa classificação, a conversa é encaminhada para a capacidade correspondente. Solicitações de **consulta ou dúvida documental** seguem pela rota de **RAG**, na qual o recuperador consulta o índice e as fontes documentais — no runtime atual, extratos sintéticos em JSON e no PostgreSQL — reúne os trechos relevantes e monta o contexto utilizado na geração da resposta. O contexto recuperado é então encaminhado ao **LLM**, que produz a resposta em linguagem natural.

Solicitações associadas a **funcionalidades ou fluxos específicos** são encaminhadas a um **workflow guiado do backend**: o frontend conduz as perguntas estruturadas consumindo a API de sessões e, após a confirmação, o backend executa a operação localmente ou aciona o **Power Automate** por HTTP como fronteira assíncrona opcional, recebendo o resultado por webhook. O modo local/simulador mantém o fluxo executável sem depender do ambiente corporativo.

A Figura 21 apresenta a arquitetura-alvo, na qual a orquestração dos fluxos funcionais é assumida por Microsoft Copilot Studio e Power Automate sobre os serviços corporativos. No runtime atualmente implementado, os componentes mantêm responsabilidades distintas: o **PLN interpreta e roteia**, o **RAG recupera conhecimento**, o **LLM gera respostas fundamentadas a partir do contexto recuperado** e os **workflows guiados do backend executam e orquestram os fluxos funcionais associados às intenções**, com Power Automate opcional e Supabase Storage para os artefatos gerados. Identidade, configuração e rastreabilidade atravessam os demais componentes.

<div align="center">
  <img src="img/componentes-metro-5.2.png" alt="Diagrama de componentes da arquitetura-alvo da solução" width="100%">
  <p><strong>Figura 21</strong> - Diagrama de componentes da arquitetura-alvo da solução (visão de evolução corporativa; o runtime atual está descrito no texto desta seção e detalhado na Seção 8.5).</p>
  <sup>Fonte: Material produzido pelos autores, 2026.</sup>
</div>

O código-fonte do diagrama está versionado em [`docs/diagrams/componentes-metro-5.2.puml`](diagrams/componentes-metro-5.2.puml). Para regerar a imagem, utilizando PlantUML e Graphviz instalados no ambiente:

```bash
java -jar plantuml.jar -charset UTF-8 -tpng -o ../img docs/diagrams/componentes-metro-5.2.puml
```

### 5.2.1 Componentes e responsabilidades

| Componente | Responsabilidade |
|---|---|
| **Microsoft Teams** | Canal de interação com o usuário: recebe as solicitações e apresenta respostas, referências e resultados dos fluxos executados, dentro do ambiente de trabalho já utilizado pelas equipes. |
| **API da Aplicação** | Expor o ponto de entrada HTTP/JSON, centralizar a comunicação entre interface, processamento e retorno das respostas. |
| **Gerenciador de Conversação** | Manter o contexto necessário da interação e consolidar os resultados produzidos pelas diferentes rotas de processamento. |
| **Pré-processamento** | Normalizar e preparar o texto para as etapas posteriores do pipeline de PLN. |
| **Classificador de Intenções** | Identificar a intenção expressa pelo usuário e atribuir a categoria correspondente com sua confiança. |
| **Catálogo de Intenções** | Associar as intenções reconhecidas às capacidades e funcionalidades disponíveis, determinando o próximo fluxo de processamento. |
| **Validador de Escopo** | Verificar se a solicitação pertence ao conjunto de interações suportadas pela solução antes do acesso às fontes e aos fluxos. |
| **Extração de Entidades** | Identificar entidades relevantes para a execução da intenção, como projeto, subportfólio, período e critérios de análise. |
| **Recuperador RAG** | Buscar conteúdo relevante para consultas documentais a partir do índice vetorial e das fontes integradas. |
| **Ingestão / Indexação Documental** | Preparar os documentos utilizados pela solução para posterior recuperação semântica. |
| **Extração e Normalização** | Extrair e organizar o conteúdo proveniente dos documentos utilizados na base de conhecimento. |
| **Geração de Embeddings** | Transformar os trechos normalizados em representações vetoriais utilizadas na busca semântica. |
| **Índice Vetorial** | Armazenar embeddings e metadados para permitir a recuperação dos conteúdos mais relevantes. |
| **Integração com SharePoint** | Intermediar o acesso aos documentos, listas e metadados disponibilizados pelo SharePoint. |
| **Microsoft Copilot Studio** | Orquestrar os tópicos e fluxos associados às intenções funcionais identificadas pelo PLN. |
| **Tópicos / Fluxos por Intenção** | Implementar os comportamentos específicos associados às funcionalidades previstas no catálogo de intenções. |
| **Power Automate** | Executar automações e operações de integração necessárias aos fluxos funcionais. |
| **API de LLM** | Gerar respostas em linguagem natural a partir do contexto recuperado pelo RAG. O provedor não está definido: a integração é feita por interface HTTP substituível, e a escolha será registrada quando o benchmark for realizado. |
| **Azure AI Speech** | Consumir a API de Speech-to-Text documentada para converter entradas de voz em texto em português brasileiro antes do processamento pelo backend. |
| **Microsoft Entra ID** | Fornecer a identidade do usuário e apoiar o controle de acesso às funcionalidades e informações. |
| **Trilha de Auditoria** | Registrar eventos relevantes da interação, incluindo intenção, fontes consultadas e fluxos acionados. |
| **Configuração / Secrets** | Armazenar configurações e credenciais necessárias aos serviços integrados sem expô-las à interface. |

### 5.2.2 Fluxo de interação entre os componentes

O fluxo de uma solicitação conversacional típica ocorre da seguinte forma:

1. O **usuário** envia uma mensagem pelo **Microsoft Teams**. Quando a entrada é realizada por voz, o áudio pode ser encaminhado ao **Azure AI Speech**, que devolve a transcrição em texto.
2. A **API da aplicação** recebe a solicitação por HTTP/JSON e a encaminha ao **gerenciador de conversação**.
3. O **Pilar 1 — Núcleo de PLN e Roteamento** realiza o pré-processamento, identifica e classifica a intenção, valida se a solicitação está no escopo suportado, associa a intenção ao catálogo de capacidades e extrai as entidades relevantes para o fluxo selecionado.
4. Após a validação de escopo, o **catálogo de intenções** associa a intenção reconhecida à capacidade responsável pelo processamento da solicitação.
5. Quando a intenção corresponde a uma **consulta ou dúvida documental**, o **Recuperador RAG** busca os conteúdos relevantes no índice vetorial e, quando necessário, na integração com o **SharePoint**. Os resultados são organizados pelo componente de **Montagem de Contexto**.
6. O contexto recuperado é enviado ao **LLM**, que produz a resposta em linguagem natural. O resultado retorna ao gerenciador de conversação.
7. Quando a intenção corresponde a uma **funcionalidade estruturada**, o backend inicia um workflow guiado próprio e o frontend apresenta suas perguntas. O Power Automate é uma fronteira assíncrona opcional; o modo local/simulador mantém o fluxo executável sem acesso ao ambiente do Metrô.
8. O resultado produzido pela rota escolhida é consolidado pelo **backend** e devolvido ao chat web; a integração futura com Microsoft Teams não é requisito do fluxo atual.
9. Durante o processamento, os componentes de **identidade e auditoria** registram os elementos necessários para controle de acesso e rastreabilidade da interação.

### 5.2.3 Relação entre o catálogo de intenções e os fluxos da solução

O catálogo de intenções atua como elemento de ligação entre o **núcleo de PLN** e as capacidades funcionais do agente. Em vez de vincular a conversa diretamente a uma única tecnologia, a classificação identifica a necessidade do usuário e determina qual componente deve assumir o processamento.

A arquitetura suporta dois grandes grupos de roteamento:

| Tipo de intenção | Destino principal | Objetivo |
|---|---|---|
| **Consulta / dúvida documental** | RAG → LLM | Recuperar informações das fontes documentais e produzir uma resposta fundamentada em linguagem natural. |
| **Fluxo funcional / transação / automação** | Backend → workflow guiado → Power Automate opcional | Executar uma capacidade estruturada associada à intenção identificada. |

O catálogo pode, portanto, evoluir juntamente com as funcionalidades priorizadas do produto, mantendo a mesma estrutura de interpretação e roteamento. A inclusão de uma nova capacidade exige principalmente o registro da nova intenção e a implementação do fluxo correspondente, sem necessidade de alterar a interface de chat ou o mecanismo central de classificação.

### 5.2.4 Decisões arquiteturais refletidas no diagrama

- **O canal de interação é desacoplado da lógica de negócio.** O Teams entrega a mensagem à API da aplicação, que controla o roteamento e a consolidação da resposta. Trocar ou acrescentar um canal não exige reestruturar o núcleo de PLN nem as rotas de atendimento.
- **O núcleo de PLN permanece independente dos modelos generativos.** A identificação da intenção, o controle de escopo e o roteamento são responsabilidades do Pilar 1.
- **O catálogo de intenções funciona como mecanismo de roteamento.** A mesma entrada conversacional pode ser direcionada a diferentes capacidades conforme a intenção identificada.
- **O Copilot Studio foi retirado da arquitetura executável.** Os artefatos exportados permanecem apenas como referência histórica; a orquestração ativa está no backend e no frontend, com Power Automate opcional.
- **RAG e geração são componentes distintos.** O mecanismo de recuperação seleciona o contexto relevante e o LLM produz a resposta a partir desse contexto. No runtime atual a fonte documental são extratos sintéticos em JSON e no PostgreSQL; o SharePoint corporativo é a fonte prevista na arquitetura-alvo.
- **A credencial do LLM é protegida no backend.** A interface não acessa diretamente a API generativa nem recebe suas credenciais.
- **A camada de conhecimento é desacoplada dos canais e da geração.** A fonte documental e o índice podem evoluir sem exigir mudanças estruturais na interface ou no mecanismo de roteamento.
- **Identidade e rastreabilidade são transversais.** O controle de acesso e os registros de auditoria devem acompanhar as interações independentemente da rota escolhida.
- **A arquitetura permanece modular.** Novos tópicos, integrações ou capacidades de RAG podem ser adicionados ao catálogo de intenções sem reestruturar integralmente a solução.

### 5.2.5 Limite de representação

O diagrama de componentes concentra-se nas dependências, responsabilidades e interações entre os módulos da solução. A representação detalhada da infraestrutura física, dos containers, nós de execução e ambientes de implantação deve permanecer no **Diagrama de Implantação da UML**, apresentado na Seção 6.1.

---

## 5.3 Diagramas de Sequência da UML

Os diagramas desta seção, como os demais do documento, são gerados a partir de arquivos-fonte em PlantUML versionados em `docs/diagrams/`. Para regerar qualquer um deles, com PlantUML e Graphviz instalados:

```bash
plantuml -charset UTF-8 -tpng -o ../img docs/diagrams/<arquivo>.puml
```


Os diagramas de sequência desta seção detalham a ordem das interações entre os principais componentes da solução na arquitetura-alvo, na qual o canal é o Microsoft Teams, a identidade vem do Microsoft Entra ID e a orquestração de fluxos funcionais usa o Copilot Studio. No runtime atualmente implementado, o canal é o chat web, a identidade é simulada pelo token da bancada e os fluxos funcionais são conduzidos pelos workflows guiados do backend, com Power Automate como fronteira assíncrona opcional; o núcleo autoral de PLN, o catálogo de intenções, a arquitetura RAG, a geração pelo LLM e o Speech-to-Text permanecem idênticos nos dois cenários.

A seleção dos cenários considera os caminhos centrais da solução: consultas documentais fundamentadas, análises comparativas, direcionamento para fluxos funcionais e entrada por voz. Em todos os casos, o PLN permanece responsável pela interpretação e classificação da solicitação, enquanto o catálogo de intenções determina a capacidade que deverá processá-la. A partir desse roteamento, a solicitação segue para a recuperação e geração de resposta ou para o workflow guiado correspondente no backend.

As interações de identidade, autorização e auditoria são tratadas como capacidades transversais. A identidade do usuário deve ser validada antes do acesso às fontes ou da execução de ações, e os eventos relevantes da interação devem ser registrados para fins de rastreabilidade.

### 5.3.1 Consulta documental via RAG

Este cenário representa uma consulta textual sobre informações disponíveis na base utilizada pelo MVP, como **"Qual o prazo do projeto XPTO?"**. O fluxo demonstra o caminho completo desde o canal de interação até a recuperação de informações relevantes e a geração da resposta por meio do LLM.

No contexto do MVP, a fonte utilizada para validação é a **base sintética associada ao índice vetorial**. A integração com SharePoint representa a evolução arquitetural prevista e não deve ser interpretada como dependência do conjunto de dados reais do Metrô.

<div align="center">
  <img src="img/sequencia-rag-consulta.png" alt="Sequência: consulta documental via RAG" width="100%">
</div>

<p align="center"><strong>Figura 22</strong> - Sequência: consulta documental via RAG.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>

O código-fonte do diagrama está versionado em [`docs/diagrams/sequencia-rag-consulta.puml`](diagrams/sequencia-rag-consulta.puml) e pode ser regerado com PlantUML e Graphviz instalados:

```bash
java -jar plantuml.jar -charset UTF-8 -tpng -o ../img docs/diagrams/sequencia-rag-consulta.puml
```

O fluxo evidencia que o LLM não acessa diretamente a fonte documental. A aplicação recupera previamente os conteúdos relevantes e utiliza esses trechos como contexto para a geração da resposta. No MVP, essa recuperação ocorre sobre a base sintética e o índice vetorial; a integração com SharePoint permanece como caminho de evolução para a utilização das fontes corporativas homologadas.

O cenário também explicita o tratamento de informação insuficiente, evitando que a ausência de evidências seja convertida automaticamente em uma resposta generativa. A identidade é validada antes da consulta e os elementos necessários à rastreabilidade são registrados na trilha de auditoria.

### 5.3.2 Análise e comparação entre projetos via RAG

Este cenário representa uma solicitação analítica, como **"Compare os riscos e os prazos dos projetos XPTO e ABC"**. Diferentemente da consulta simples, o pipeline precisa identificar múltiplos projetos e consolidar as informações recuperadas antes da geração da resposta.

Assim como no cenário anterior, o MVP utiliza a **base sintética associada ao índice vetorial**. A eventual integração com SharePoint ocorre em uma etapa posterior, mediante os mecanismos homologados pelo parceiro.

<div align="center">
  <img src="img/sequencia-rag-comparacao.png" alt="Sequência: análise e comparação entre projetos via RAG" width="100%">
</div>

<p align="center"><strong>Figura 23</strong> - Sequência: análise e comparação entre projetos via RAG.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>

O código-fonte do diagrama está versionado em [`docs/diagrams/sequencia-rag-comparacao.puml`](diagrams/sequencia-rag-comparacao.puml) e pode ser regerado com PlantUML e Graphviz instalados:

```bash
java -jar plantuml.jar -charset UTF-8 -tpng -o ../img docs/diagrams/sequencia-rag-comparacao.puml
```

A sequência preserva a diferenciação entre **fato recuperado** e **resultado interpretativo da comparação**. A análise é executada sobre as informações recuperadas e o LLM é responsável pela apresentação em linguagem natural, mantendo as referências associadas às evidências utilizadas.

A validação de identidade antecede a recuperação e os eventos da interação são registrados na auditoria, mantendo o cenário alinhado aos requisitos transversais de controle de acesso e rastreabilidade.

### 5.3.3 Direcionamento para workflow funcional web

Este cenário representa uma solicitação cuja intenção corresponde a uma
capacidade funcional específica do produto. O PLN identifica a intenção e o
catálogo a associa ao workflow correspondente. A partir desse ponto, o
frontend conduz as perguntas estruturadas consumindo a API de sessões; após a
confirmação, o backend executa a operação localmente ou aciona o Power Automate
por HTTP como fronteira assíncrona opcional e recebe o resultado por webhook.
A figura abaixo apresenta a orquestração equivalente na arquitetura-alvo, com
Copilot Studio como plataforma de execução do tópico; no runtime atual esse
papel é desempenhado pelo próprio backend.

<div align="center">
  <img src="img/sequencia-copilot-fluxo.png" alt="Sequência: direcionamento para fluxo funcional via Copilot Studio" width="100%">
</div>

<p align="center"><strong>Figura 24</strong> - Sequência: direcionamento para fluxo funcional via Copilot Studio.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>

O código-fonte do diagrama está versionado em [`docs/diagrams/sequencia-copilot-fluxo.puml`](diagrams/sequencia-copilot-fluxo.puml) e pode ser regerado com PlantUML e Graphviz instalados:

```bash
java -jar plantuml.jar -charset UTF-8 -tpng -o ../img docs/diagrams/sequencia-copilot-fluxo.puml
```

Nesta orquestração, o **Copilot Studio não é responsável por descobrir a intenção do usuário**. A decisão já foi tomada pelo núcleo de PLN e pelo catálogo de intenções, e o Copilot Studio atuaria como plataforma de execução do tópico ou fluxo selecionado. No runtime atual esse papel é desempenhado pelo workflow guiado do backend, que conduz as perguntas pelo frontend e consolida o resultado.

O retorno do **Power Automate** ocorre somente quando o fluxo efetivamente o aciona; no ramo puramente conversacional, o resultado é consolidado sem automação, evitando associar um retorno de automação a uma operação que não foi executada.

A identidade do usuário é validada antes da execução do fluxo e a auditoria registra a intenção identificada, o fluxo acionado e seu resultado.

### 5.3.4 Entrada por voz com Speech-to-Text

Este cenário demonstra a entrada por áudio utilizando a API de **Azure AI Speech** documentada no projeto. A responsabilidade do serviço de Speech-to-Text termina na produção de uma transcrição utilizável; depois disso, o conteúdo segue pelo mesmo pipeline utilizado para entradas textuais.

<div align="center">
  <img src="img/sequencia-voz-stt.png" alt="Sequência: entrada por voz com Speech-to-Text" width="100%">
</div>

<p align="center"><strong>Figura 25</strong> - Sequência: entrada por voz com Speech-to-Text.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>

O código-fonte do diagrama está versionado em [`docs/diagrams/sequencia-voz-stt.puml`](diagrams/sequencia-voz-stt.puml) e pode ser regerado com PlantUML e Graphviz instalados:

```bash
java -jar plantuml.jar -charset UTF-8 -tpng -o ../img docs/diagrams/sequencia-voz-stt.puml
```

O diagrama evidencia que o áudio não cria um fluxo de negócio independente: após uma transcrição válida, a solicitação torna-se equivalente a uma entrada textual para o restante da arquitetura. O Azure AI Speech atua exclusivamente na etapa de Speech-to-Text, enquanto a interpretação, validação e definição da capacidade permanecem sob responsabilidade da aplicação.

O ramo de falha contempla situações documentadas para o serviço de STT, como ausência de correspondência ou transcrição com confiança insuficiente. Nesses casos, a solicitação não deve avançar automaticamente para o PLN como se houvesse texto confiável.

### 5.3.5 Considerações sobre os cenários

Os quatro cenários apresentados cobrem os principais caminhos de interação da solução. A **consulta documental** representa o fluxo central de recuperação e geração fundamentada; a **análise comparativa** acrescenta a consolidação e interpretação de informações de múltiplos projetos; o **direcionamento para fluxos funcionais** demonstra a integração entre o núcleo de PLN, o catálogo de intenções e os workflows guiados do backend — com Copilot Studio previsto apenas na arquitetura-alvo; e a **entrada por voz** demonstra a utilização da API de Speech-to-Text como modalidade alternativa de entrada.

Em todos os cenários, o núcleo de PLN permanece como ponto comum de interpretação e decisão. A diferença entre os caminhos ocorre somente após a identificação e validação da intenção: consultas e análises documentais seguem para recuperação de contexto e geração de resposta, enquanto intenções funcionais são encaminhadas para o workflow guiado associado no backend.

Os cenários também incorporam os requisitos transversais de **identidade, autorização e rastreabilidade**. Na arquitetura-alvo, a autenticação por Microsoft Entra ID antecede as operações protegidas; no runtime atual a identidade é simulada e o token da bancada habilita voz e relatórios. Em ambos os casos, o acesso às fontes ou serviços deve respeitar as permissões aplicáveis e os eventos relevantes da interação são registrados na trilha de auditoria. No caso de fontes corporativas, a autorização efetiva deve permanecer alinhada ao modelo de permissões do ambiente do Metrô.

Por fim, a utilização da **base sintética / índice vetorial** nos cenários de recuperação explicita a delimitação do MVP. A arquitetura permanece preparada para receber as fontes corporativas, inclusive SharePoint, em uma evolução posterior, sem fazer da integração com o portfólio real uma dependência da validação inicial.

---

# 6. Mapeamento técnico de infraestrutura e implantação

Esta seção documenta a estratégia de implantação prevista para a solução, considerando que o projeto ainda está em estágio de PoC acadêmica e que a equipe não possui garantia de acesso a uma assinatura Azure corporativa. Portanto, a implantação descrita aqui não representa um deploy produtivo nem uma pipeline de CI/CD já implementada. O objetivo é registrar uma estratégia reprodutível e simples, capaz de orientar a publicação futura do MVP sem bloquear o desenvolvimento atual.

A decisão principal é separar o que faz parte do MVP do que deve permanecer como evolução. Para o MVP, a nuvem comercial efetivamente assumida é o **Supabase Cloud**, utilizado como banco PostgreSQL gerenciado e ponto de persistência da trilha de auditoria. A aplicação, por sua vez, pode ser executada localmente durante o desenvolvimento e, quando houver código consolidado suficiente, publicada em uma hospedagem simples com domínio público temporário. O empacotamento em Docker, a criação de uma pipeline de deploy e a migração para Azure ficam documentados como evolução futura.

O escopo atual de implantação contempla:

| Componente | Situação no MVP | Papel na estratégia |
|---|---|---|
| Interface web | Em desenvolvimento pela equipe em `src/frontend` | Interface própria para interação com o agente durante a demonstração. |
| API da aplicação | Planejada para expor os endpoints do MVP | Ponte entre frontend, classificação de intenção, recuperação de dados e integrações. |
| Núcleo de PLN | Definido conceitualmente e avaliado no notebook do classificador | Responsável por classificar intenções e orientar o roteamento da solicitação. |
| Banco de dados | Supabase Cloud | Persistência dos dados sintéticos, catálogo, interações e auditoria. |
| Armazenamento | Supabase Storage | Área prevista para documentos sintéticos e, futuramente, artefatos do modelo. |
| Autenticação | Microsoft Entra ID | Mecanismo previsto para autenticação do usuário no MVP. |
| Orquestração | Copilot Studio | Integração prevista para tópicos e fluxos conversacionais. |
| Automação | Power Automate | Evolução para execução de fluxos funcionais sobre dados sintéticos ou homologados. |
| Docker e pipeline de deploy | Fora do escopo atual | Evolução futura, quando houver serviço suficientemente estável para empacotamento e publicação automatizada. |

Como o provedor de LLM externo ainda não está definido nem homologado, conforme registrado na Seção 5.2, a implantação do MVP não deve depender de API generativa externa. Quando a camada do Copilot Studio não estiver disponível, o MVP deve retornar uma resposta estruturada com base nos dados sintéticos recuperados.

## 6.1 Diagrama de implantação da UML

A Figura 26 apresenta a visão de implantação da PoC. O diagrama separa o ambiente atualmente viável para o MVP dos componentes que dependem de desenvolvimento posterior ou provisionamento pela GTI.

<div align="center">
  <img src="img/implantacao-poc.png" alt="Diagrama de implantação planejada da PoC" width="100%">
</div>

<p align="center"><strong>Figura 26</strong> - Diagrama de implantação planejada da PoC.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>

O código-fonte do diagrama está versionado em [`docs/diagrams/implantacao-poc.puml`](diagrams/implantacao-poc.puml).

## 6.2 Justificativa das escolhas de implantação

As escolhas de implantação priorizam simplicidade, baixo custo e aderência ao estágio real do projeto. Como ainda não há um serviço final estabilizado para produção, esta seção evita tratar Docker, pipeline de CI/CD ou Azure como entregas já concluídas.

### 6.2.1 Estratégia de hospedagem

No estágio atual, a execução da aplicação deve permanecer simples: desenvolvimento local, banco em nuvem via Supabase e possibilidade de publicação manual em domínio temporário quando a equipe consolidar o código do MVP. Essa abordagem é adequada porque:

- não exige acesso a uma conta Azure corporativa;
- evita criar uma pipeline de build antes de haver serviço estável;
- permite demonstrar a solução com dados sintéticos;
- mantém o caminho aberto para empacotamento futuro;
- reduz o risco de falhas de CI/CD não relacionadas ao objetivo acadêmico da entrega.

O Docker permanece como evolução recomendada, mas não como requisito atual. Quando o backend estiver consolidado, a equipe poderá criar um `Dockerfile`, validar o build localmente e só então habilitar uma pipeline de build e publicação.

### 6.2.2 Banco de dados e armazenamento

O banco definido para o MVP é o **Supabase Cloud**, usando PostgreSQL gerenciado. Essa escolha permite manter o banco em nuvem sem configurar infraestrutura própria e aproveita o modelo físico já documentado na seção de modelagem de dados.

O Supabase será utilizado em dois papéis:

- **PostgreSQL:** armazenamento dos dados sintéticos, catálogo de intenções, conversas, interações, fontes consultadas, eventos de auditoria e demais tabelas previstas no modelo físico.
- **Supabase Storage:** armazenamento de documentos sintéticos e, futuramente, artefatos auxiliares do modelo de PLN ou índice vetorial, caso esses arquivos sejam necessários para a demonstração.

Os dados iniciais entram por script de inicialização, aproveitando a estrutura existente em `src/database`. A ingestão documental completa permanece como processo separado e não é tratada como etapa obrigatória deste deploy.

**Aderência aos critérios de seleção.** O Supabase é uma dependência externa ao ecossistema Microsoft, priorizado pelo critério C1 da Seção 3.4.1, e por isso a escolha é declarada aqui de forma explícita. Ela atende ao critério C2, que exige o uso de dados sintéticos ou anonimizados durante o MVP e é o que esta seção estabelece: nenhum dado real do portfólio trafega pelo serviço. O destino de homologação continua sendo o ambiente Azure do Metrô, cujo provisionamento depende da GTI e está registrado como pendência na Seção 6.3.4. O modelo físico documentado na Seção 4.4 é PostgreSQL padrão, o que mantém a migração de baixo atrito quando o ambiente corporativo for disponibilizado.

### 6.2.3 Modelo de PLN e artefatos

Para o MVP, a documentação assume o caminho mais simples: o classificador e a lógica de PLN são tratados como componentes em desenvolvimento, com avaliação registrada no notebook do projeto. A publicação de um serviço de inferência separado, o armazenamento versionado de artefatos e o carregamento automatizado de modelos em ambiente remoto ficam como evolução.

Quando essa evolução for implementada, a estratégia recomendada é:

| Item futuro | Estratégia sugerida | Justificativa |
|---|---|---|
| Classificador serializado | Armazenar em Supabase Storage ou incluir no pacote do backend | Facilita reprodução e versionamento. |
| Word2Vec e encoder BERT | Registrar versão usada pelo MVP | Mantém rastreabilidade entre avaliação e execução. |
| Índice vetorial | Começar em arquivo controlado e migrar se o volume crescer | Evita adicionar infraestrutura antes da necessidade. |
| Versionamento do modelo | Usar identificador simples, como `mvp-YYYYMMDD` | Suficiente para rastrear demonstrações acadêmicas. |
| Endpoint gerenciado | Avaliar Azure Machine Learning após provisionamento da GTI | Caminho mais adequado para homologação futura. |

### 6.2.4 Interface, autenticação e integração

A interface principal do MVP é a aplicação própria desenvolvida pela equipe em `src/frontend`, construída com React, Vite, TypeScript e Tailwind CSS. Ela representa o canal de demonstração da solução enquanto a integração corporativa completa não estiver disponível.

A autenticação prevista é o **Microsoft Entra ID**, pois essa decisão mantém alinhamento com o ambiente do Metrô e permite evoluir para controle de acesso por perfil. Como o MVP usa dados sintéticos, a autenticação tem papel principalmente demonstrativo e de rastreabilidade.

O **Copilot Studio** deve ser integrado ao backend por API/OpenAPI quando o serviço estiver consolidado. O papel do Copilot Studio é executar tópicos e fluxos conversacionais associados às intenções identificadas, sem substituir o núcleo autoral de PLN.

O **Power Automate** permanece como caminho para fluxos funcionais. No MVP, esses fluxos podem ser simulados ou executados apenas sobre dados sintéticos, evitando dependência de SharePoint real ou permissões corporativas.

### 6.2.5 Estratégia de fallback

Como não há provedor de LLM definido para o produto e a camada generativa do Copilot Studio pode depender do ambiente disponível, o MVP deve prever um fallback simples. Nesse cenário, a aplicação retorna uma resposta estruturada contendo:

- intenção identificada;
- nível de confiança;
- entidades extraídas, quando houver;
- fontes sintéticas consultadas;
- resposta objetiva baseada nos dados disponíveis;
- indicação de limitação quando não houver evidência suficiente.

Esse fallback permite demonstrar o fluxo principal sem introduzir dependência de serviços generativos externos.

### 6.2.6 Processo reprodutível proposto

O processo recomendado para a PoC é:

1. **Criar o projeto no Supabase Cloud.** Criar organização/projeto e obter URL, chave pública e chave de serviço para scripts administrativos.
2. **Executar os scripts de banco.** Aplicar os scripts de criação e carga inicial presentes em `src/database`.
3. **Cadastrar dados sintéticos.** Inserir somente dados aprovados pela liderança para uso na demonstração.
4. **Configurar variáveis de ambiente.** Definir credenciais do Supabase, ambiente de execução e parâmetros de integração disponíveis.
5. **Executar a aplicação localmente.** Rodar frontend e backend em ambiente de desenvolvimento, enquanto o serviço final não estiver estabilizado.
6. **Validar a persistência.** Confirmar que interações, fontes consultadas e eventos de auditoria são gravados no Supabase.
7. **Configurar autenticação Microsoft.** Registrar a aplicação no Entra ID quando houver URL de callback definida.
8. **Preparar integração com Copilot Studio.** Documentar ou expor a especificação OpenAPI quando a API estiver estável.
9. **Publicar em domínio temporário.** Realizar publicação manual em serviço simples somente quando houver versão demonstrável.
10. **Registrar pendências de evolução.** Docker, pipeline CI/CD, Azure, Azure Machine Learning e Application Insights devem permanecer como próximos passos.

### 6.2.7 Variáveis de ambiente previstas

As variáveis mínimas planejadas para reprodução do MVP são:

| Variável | Camada | Descrição |
|---|---|---|
| `SUPABASE_URL` | Backend/frontend | URL do projeto Supabase. |
| `SUPABASE_ANON_KEY` | Frontend/backend | Chave pública para operações permitidas pelas políticas do Supabase. |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend/scripts | Chave administrativa para carga inicial e rotinas internas. Não deve ser exposta no frontend. |
| `MICROSOFT_CLIENT_ID` | Frontend/backend | Identificador da aplicação registrada no Entra ID. |
| `MICROSOFT_TENANT_ID` | Frontend/backend | Tenant usado para autenticação. |
| `MICROSOFT_REDIRECT_URI` | Frontend | URL de retorno após login. |
| `COPILOT_STUDIO_ENABLED` | Backend | Indica se a integração com Copilot Studio está ativa. |
| `COPILOT_STUDIO_ENDPOINT` | Backend | Endpoint usado quando a integração estiver disponível. |
| `APP_ENV` | Backend/frontend | Ambiente de execução, como `local`, `dev`, `hmg` ou `main`. |

Exemplo de arquivo `.env` planejado para o backend:

```bash
APP_ENV=local
SUPABASE_URL=https://exemplo.supabase.co
SUPABASE_ANON_KEY=ey...
SUPABASE_SERVICE_ROLE_KEY=ey...
MICROSOFT_CLIENT_ID=00000000-0000-0000-0000-000000000000
MICROSOFT_TENANT_ID=00000000-0000-0000-0000-000000000000
COPILOT_STUDIO_ENABLED=false
COPILOT_STUDIO_ENDPOINT=
```

### 6.2.8 Comandos de execução local

Enquanto não houver empacotamento Docker nem pipeline de deploy, a reprodução deve se limitar à execução local da aplicação e à conexão com o Supabase.

Execução local do backend, quando disponível:

```bash
cd src/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

No Windows PowerShell:

```powershell
cd src/backend
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Execução local do frontend:

```bash
cd src/frontend
npm install
npm run dev
```

Build local do frontend:

```bash
cd src/frontend
npm install
npm run build
```

## 6.3 Considerações sobre desempenho e segurança

Como a implantação é uma PoC acadêmica com dados sintéticos, as decisões de segurança e desempenho são proporcionais ao risco do MVP. Ainda assim, a arquitetura preserva pontos importantes para futura homologação: autenticação via Microsoft Entra ID, separação entre frontend e backend, proteção de chaves no servidor e persistência de auditoria no Supabase.

### 6.3.1 Desempenho

As métricas obrigatórias para o MVP são:

| Métrica | Objetivo | Onde medir |
|---|---|---|
| Latência média do endpoint `/api/chat` | Verificar se a interação permanece compatível com uso conversacional. | Backend FastAPI e painel do frontend. |
| Taxa de sucesso das requisições | Identificar falhas de API, falhas de conexão com Supabase e erros de integração. | Backend e registros de auditoria. |
| Tempo de resposta da recuperação de dados | Avaliar o impacto das consultas à base sintética. | Backend e registros de auditoria. |
| Confiança da macrointenção e da intenção específica | Monitorar a qualidade do roteamento do PLN. | Tabela `ai_interactions`. |
| Quantidade de respostas por fallback | Verificar indisponibilidade da camada generativa/Copilot ou ausência de evidência suficiente. | Tabela `ai_interactions` e logs. |
| Quantidade de fontes recuperadas por consulta | Avaliar se o RAG está encontrando evidências suficientes. | Tabela `consulted_sources`. |

Para a PoC, as métricas devem ser simples e associadas aos fluxos já implementados. Métricas mais avançadas de carregamento de modelo, consumo de memória, imagem Docker e telemetria de contêiner devem ser adicionadas somente quando o serviço de PLN estiver empacotado para publicação.

### 6.3.2 Segurança

O MVP utiliza dados sintéticos ou anonimizados, portanto não há tratamento de informações reais do portfólio produtivo. Mesmo assim, a implantação deve seguir as seguintes regras mínimas:

- credenciais do Supabase e do Entra ID não devem ser versionadas no repositório;
- a chave `SUPABASE_SERVICE_ROLE_KEY` deve existir apenas no backend e em scripts administrativos;
- o frontend deve usar somente chaves públicas apropriadas;
- o backend deve validar a identidade recebida antes de registrar a interação;
- toda interação deve gerar registro de auditoria no Supabase;
- documentos sintéticos devem ser aprovados pela liderança antes de entrarem na base da demonstração;
- endpoints administrativos de carga, se existirem, não devem ficar expostos publicamente sem autenticação.

Como a aplicação terá domínio público temporário e todos os dados são sintéticos, o acesso pode ser liberado para avaliadores, equipe e demais participantes do MVP. Para uma evolução com dados reais, essa regra deixa de valer: o acesso deverá ser restrito por Entra ID, grupos, permissões do SharePoint e políticas definidas pela GTI.

### 6.3.3 Auditoria

A trilha de auditoria deve ser persistida no Supabase. O registro mínimo de cada interação deve incluir:

- usuário autenticado ou identificador de sessão;
- data e hora da solicitação;
- texto enviado pelo usuário;
- macrointenção prevista;
- intenção específica prevista;
- confiança das classificações;
- handler ou rota selecionada;
- fontes sintéticas consultadas;
- resposta devolvida;
- indicação de fallback, erro ou informação insuficiente.

Esses campos já se alinham ao modelo de dados documentado, especialmente às entidades `ai_conversations`, `ai_interactions`, `consulted_sources` e `audit_events`.

### 6.3.4 Limitações e pendências de provisionamento

A seção de implantação deve deixar explícito que alguns itens dependem de decisão ou provisionamento externo e não bloqueiam a PoC:

| Item | Situação no MVP | Encaminhamento |
|---|---|---|
| Azure corporativo do Metrô | Pendente de provisionamento pela GTI. | Manter como evolução para homologação. |
| Docker e pipeline CI/CD | Fora do MVP atual. | Criar apenas quando houver backend consolidado para empacotamento e publicação automatizada. |
| Azure Machine Learning | Fora do MVP. | Usar futuramente para endpoint gerenciado ou governança de modelos. |
| Application Insights/Azure Monitor | Não obrigatório na PoC sem Azure. | Substituir por logs e métricas persistidas no Supabase; ativar em Azure no futuro. |
| SharePoint real | Fora do MVP. | Usar apenas base sintética/anonimizada. |
| Fluxos reais de Power Automate | Podem ser simulados no MVP. | Ativar fluxos reais apenas com dados e permissões homologadas. |
| Camada generativa do Copilot Studio | Integração prevista no MVP, sujeita ao ambiente disponível. | Usar fallback estruturado se indisponível. |

### 6.3.5 Checklist de conclusão da implantação

Para considerar a estratégia de deploy reprodutível, a equipe deve validar:

- [ ] banco Supabase criado em nuvem;
- [ ] scripts de criação e carga inicial executados;
- [ ] backend FastAPI executando localmente;
- [ ] endpoint `/health` respondendo;
- [ ] frontend Vite consumindo o backend;
- [ ] autenticação Microsoft Entra ID configurada ou documentada para o ambiente disponível;
- [ ] interação gravada nas tabelas de auditoria;
- [ ] fallback estruturado funcionando sem API generativa externa;
- [ ] endpoint OpenAPI preparado para conexão com Copilot Studio;
- [ ] Docker e pipeline registrados como evolução futura, sem arquivos de build ativando CI/CD nesta etapa;

# 7. Projeto Visual da Solução

O projeto visual será desenvolvido na Sprint 5, junto com o frontend completo, conforme a estratégia de entrega da Seção 8.3.3. A Sprint 3 entrega apenas a interface básica de teste descrita na Seção 8.3.1, cuja finalidade é validar o fluxo de integração e não definir a identidade visual do produto.

## 7.1 Desenvolvimento de Wireframes

Será desenvolvido na Sprint 5.

## 7.2 Desenvolvimento de Mockups

Será desenvolvido na Sprint 5.

## 7.3 Guia Visual

Será desenvolvido na Sprint 5.

# 8. Desenvolvimento do Projeto

## 8.1 Arquitetura de Codificação e Estrutura de Diretórios

O código-fonte fica em `src/`, separado por responsabilidade. A divisão segue as camadas do diagrama de componentes da Seção 5.2: o canal e a interface ficam no `frontend`, a orquestração, as integrações e o núcleo de PLN no `backend`, o esquema de dados em `database` e os experimentos que produziram os artefatos treinados em `notebooks`.

```text
src/
├── backend/                    API FastAPI — orquestração e integrações
│   ├── app/
│   │   ├── main.py             rotas /health, /api/chat e /api/audio
│   │   ├── audio/              recebimento, validação e transcrição (Seção 8.7)
│   │   ├── nlp/                núcleo de PLN (Seção 8.11)
│   │   │   ├── preprocessing.py  normalização, tokenização e stemming
│   │   │   ├── entities.py       extração das entidades do domínio
│   │   │   ├── classifier.py     classificador hierárquico e carga do artefato
│   │   │   ├── inference.py      vetorização, limiares e roteamento
│   │   │   └── data/             léxico do portfólio, substituível
│   │   ├── gemini/             cliente do provedor de LLM
│   │   │   ├── client.py       chamada, retry com backoff e mapeamento de erro
│   │   │   └── schemas.py      contratos de entrada e saída (Pydantic)
│   │   ├── rag/                recuperação de contexto
│   │   │   ├── sharepoint.py   carga, busca e montagem do prompt com fontes
│   │   │   └── data/sharepoint/ exports JSON simulados de listas do SharePoint
│   │   └── tests/              testes automatizados (Seção 8.4)
│   ├── requirements.txt
│   ├── requirements-pln.txt    dependências só da inferência (Seção 8.11.2)
│   └── .env.example            variáveis esperadas, sem segredos
├── frontend/                   interface React + TypeScript (Vite)
│   ├── src/
│   │   ├── components/         componentes de tela e biblioteca de UI
│   │   ├── hooks/              hooks reutilizáveis
│   │   ├── lib/                cliente HTTP do backend e utilitários
│   │   └── App.tsx
│   └── vite.config.ts          proxy de /api para o backend em desenvolvimento
├── database/
│   ├── sql/                    criação, carga inicial e rollback
│   └── docs/                   documentação dos scripts
└── notebooks/                  experimentos e artefatos treinados
    ├── classificador_intencoes_metro.ipynb   benchmark do algoritmo (Seção 8.10)
    ├── preprocessamento_entidades.ipynb      medição do pré-processamento e das entidades
    ├── migrar_artefato_classificador.py      reaponta o artefato para o pacote (Seção 8.11.4)
    └── artefatos/              dataset, catálogo, modelo e métricas da execução
```

Três convenções sustentam essa organização.

**Segredo não entra no repositório.** O backend lê credenciais de `.env`, versionado apenas como `.env.example`. A chave do provedor de LLM existe somente no servidor: o frontend chama `/api/chat` e nunca o provedor diretamente.

**O contrato é declarado uma vez e replicado.** Os tipos de `app/gemini/schemas.py` têm correspondência direta em `frontend/src/lib/gemini-api.ts`. Quando um campo muda no backend, o `tsc --noEmit` do frontend acusa a divergência no build.

**Dado sintético fica junto do código que o consome.** Os exports simulados de listas do SharePoint ficam em `app/rag/data/sharepoint/`, e não em uma base externa, para que a bancada de teste rode sem provisionamento. O diretório é substituível por variável de ambiente (`SHAREPOINT_MOCK_DATA_DIR`) quando houver fonte real. O léxico do domínio em `app/nlp/data/` segue a mesma regra e será gerado a partir da base real do portfólio quando ela existir, sem alteração de código.

**Modelo treinado não é código.** Os artefatos do classificador permanecem em `src/notebooks/artefatos/` e são referenciados pelo pacote `app/nlp/`, em vez de copiados para dentro dele. Uma segunda cópia abriria a possibilidade de o serviço rodar com um artefato diferente do que o benchmark da Seção 8.10 mediu.

## 8.2 Modelo de Recomendação

A solução não emprega um modelo de recomendação no sentido clássico — não há ranqueamento de itens por afinidade de usuário nem filtragem colaborativa, porque o produto não recomenda conteúdo: ele responde a solicitações sobre um portfólio de projetos.

O componente de aprendizado de máquina do projeto é o **classificador de intenções**, documentado em detalhe na Seção 8.10. Ele cumpre a função que, na arquitetura, antecede qualquer recomendação: identifica o que a pessoa pediu, em dois níveis — macrointenção e intenção específica —, e decide para qual rota a solicitação segue (RF07).

Existe um segundo mecanismo com característica de ranqueamento, descrito na Seção 5.3.1: a recuperação de contexto do RAG, implementada em `src/backend/app/rag/sharepoint.py`. Ela pontua os documentos disponíveis por sobreposição de termos com a pergunta, com peso adicional para correspondência no título, e devolve os mais bem pontuados como fontes da resposta. É recuperação de informação, não recomendação: o objetivo é fundamentar a resposta com origem declarada, e não sugerir conteúdo que a pessoa não pediu.

A sugestão proativa de conteúdo — que seria, essa sim, uma recomendação — é o objeto do RF09 e do RF10, e permanece como decisão em aberto após a prototipação exploratória, conforme o inventário da Seção 3.8.6.1.

## 8.3 Planejamento estratégico de desenvolvimento

O desenvolvimento das features será conduzido de forma incremental nas Sprints 3, 4 e 5, usando como insumo os artefatos já concluídos nas Sprints 1 e 2. Esses artefatos anteriores não compõem novas entregas neste planejamento; eles funcionam apenas como referência para orientar implementação, integração, testes e fechamento do projeto. A entrega será organizada para reduzir riscos de integração: primeiro serão implementados os fluxos essenciais de entrada, processamento e consulta; em seguida, serão estabilizadas as integrações, o banco de dados, os webhooks, o deploy e a execução dos testes sistêmicos; por fim, a solução será consolidada, documentada e preparada para apresentação final.

Essa estratégia considera que a solução deve evoluir como uma prova de conceito funcional, usando dados sintéticos ou anonimizados, preservando a rastreabilidade entre requisitos, testes e componentes implementados. Ao final de cada sprint, a documentação técnica deverá ser atualizada junto com o código, evitando que arquitetura, APIs, decisões de implementação e evidências de teste fiquem desconectadas da versão real do sistema.

| Sprint | Foco principal | Principais frentes de trabalho | Qualidade e validação | Resultado esperado |
| --- | --- | --- | --- | --- |
| Sprint 3 | Implementação inicial e planejamento de testes | API de recebimento de áudio, início da integração Speech-to-Text e NLP, frontend básico e preparação do fluxo mínimo integrado | Definição dos testes funcionais, RNFs, integração, desempenho e usabilidade, com critérios de aceitação e estratégia de evidências | Primeira versão funcional da PoC e plano de testes sistêmicos pronto para execução |
| Sprint 4 | Integração, estabilização e execução dos testes | Webhooks, banco de dados, persistência, integração entre componentes e início do deploy em ambiente controlado | Execução dos testes planejados, registro de logs, evidências, falhas, correções e análise de cobertura | Solução demonstrável, principais integrações operando e diagnóstico claro de qualidade |
| Sprint 5 | Finalização, consolidação e entrega final | Frontend completo, mensageria assíncrona, integração frontend-backend, ajustes finais e revisão técnica/documental | Complementação ou reexecução dos testes, validação final da documentação, conformidade do repositório e preparação da apresentação | PoC integrada, documentada, testada e pronta para apresentação aos stakeholders |

### 8.3.1 Sprint 3

Na Sprint 3, o foco será aplicar as definições técnicas e visuais já existentes em uma primeira versão funcional da solução, suficiente para validar os fluxos principais e sustentar o planejamento dos testes sistêmicos. A equipe deverá priorizar a implementação da API de recebimento de áudios, o início da integração entre Speech-to-Text e o algoritmo de NLP, e uma interface básica para envio de texto ou áudio e visualização dos resultados retornados pelo backend.

Como esta sprint será a base para a validação do sistema, o planejamento de testes será tratado como uma entrega central. A equipe deverá derivar os cenários de teste a partir dos requisitos funcionais e não funcionais, contemplando casos positivos, casos de falha, testes de integração entre componentes, testes de desempenho e roteiro de usabilidade com usuários externos. Também deverão ser definidos os critérios de aceitação, as ferramentas de automação, a forma de registro de evidências e a estratégia de uso de cache para chamadas externas, quando aplicável.

Ao final da sprint, espera-se que exista um fluxo mínimo integrado entre frontend, backend e processamento de linguagem natural, mesmo que ainda incompleto. Esse fluxo servirá como base concreta para executar testes na Sprint 4, identificar riscos técnicos antecipadamente e ajustar o escopo da Sprint 5 com maior previsibilidade.

### 8.3.2 Sprint 4

Na Sprint 4, a prioridade será ampliar e estabilizar a solução iniciada na Sprint 3, com foco na integração entre componentes e na execução dos testes planejados. O desenvolvimento deverá avançar na implementação dos webhooks definidos pelo grupo, na criação e população do banco de dados com dados sintéticos ou anonimizados, na integração das operações de leitura e escrita e no início do processo de deploy da prova de conceito em ambiente controlado.

Essa sprint será marcada pela execução dos testes sistêmicos planejados anteriormente. A equipe deverá rodar os testes funcionais, de requisitos não funcionais, de integração e de usabilidade, registrando evidências, logs, falhas encontradas, ajustes realizados e limitações de cobertura. O objetivo não será apenas demonstrar que a solução funciona em cenários esperados, mas também identificar problemas antes da consolidação final, especialmente em pontos críticos como comunicação entre frontend e backend, processamento de áudio/texto, persistência de dados e respostas do agente.

Ao final da sprint, a solução deverá estar mais próxima de uma versão demonstrável, com integrações principais em funcionamento, documentação técnica atualizada e um diagnóstico claro da qualidade atingida. Os resultados dos testes deverão orientar a priorização da Sprint 5, separando correções obrigatórias, melhorias desejáveis e itens que ficarão como evolução futura.

### 8.3.3 Sprint 5

Na Sprint 5, o foco será a finalização do projeto e a consolidação da prova de conceito. A equipe deverá completar o desenvolvimento do frontend, finalizar a integração frontend-backend, implementar o sistema de mensagens assíncronas integrado aos webhooks e complementar os testes sistêmicos que não tenham sido concluídos ou que precisem ser reexecutados após correções da Sprint 4.

Também será a sprint de fechamento técnico e documental. A documentação do projeto deverá ser revisada para refletir a solução efetivamente implementada, incluindo componentes e tecnologias utilizadas, funcionalidades entregues, benefícios alcançados, custos estimados, análise financeira, feedbacks incorporados, arquitetura revisada, aperfeiçoamentos futuros e relação com os ODS aplicáveis. A equipe também deverá verificar a conformidade do repositório, a organização dos arquivos, a reprodutibilidade da execução e a consistência entre código, testes e documentação.

Ao final da Sprint 5, a entrega esperada é uma solução integrada, demonstrável e documentada, acompanhada das evidências de teste, instruções de implantação e apresentação final para stakeholders. O objetivo principal será encerrar o projeto com qualidade, deixando claro o que foi implementado, quais limitações permanecem, quais aprendizados foram obtidos e quais caminhos de evolução podem ser seguidos após a prova de conceito.

## 8.4 Testes Unitários e de Integração

A Sprint 2 entregou a primeira bateria de testes automatizados do projeto, cobrindo a bancada de teste do caminho de consulta: recuperação de contexto e chamada ao provedor de LLM. A Sprint 3 ampliou a suíte com os testes da API de áudio da Seção 8.7, do núcleo de PLN da Seção 8.11, do pipeline HTTP e da interface integrada. O plano completo de testes sistêmicos — funcionais, de RNFs, de integração e de usabilidade — está na Seção 9.

A tabela abaixo registra a bateria original da Sprint 2, mantida como referência do que cobria o caminho de consulta.

**Estratégia adotada.** Os testes isolam a fronteira de rede. A chamada HTTP ao provedor é substituída por um duplo de teste que injeta a resposta ou o erro desejado, de modo que a suíte roda sem chave de API, sem acesso à internet e de forma determinística. O que está sob teste é o código do projeto — mapeamento de contrato, política de retry, tratamento de erro e regra de recuperação —, e não a disponibilidade do serviço externo.

**Ferramentas.** `pytest` como executor, `monkeypatch` para substituir `urlopen` e variáveis de ambiente, e os próprios modelos Pydantic para validar os contratos de entrada e saída.

| Módulo | Teste | O que verifica |
| --- | --- | --- |
| `rag/sharepoint.py` | `test_loads_mock_sharepoint_list_exports` | Carrega os 9 itens das três listas simuladas, com identificador e URL preenchidos. |
| | `test_retrieves_relevant_sharepoint_items` | Uma pergunta sobre objeto perdido recupera o procedimento correspondente como primeiro resultado. |
| | `test_does_not_inject_context_for_unrelated_question` | Pergunta fora do domínio não recupera nada e o prompt segue sem contexto injetado — é a proteção contra fundamentar resposta em fonte irrelevante. |
| | `test_builds_prompt_with_source_labels_and_disclaimer` | O prompt carrega o rótulo `[Fonte N]`, o aviso de dado fictício e a pergunta original, atendendo ao RNF04. |
| `gemini/client.py` | `test_generate_chat_response_maps_text_context_and_usage` | Texto, identificador da interação e contagem de tokens são mapeados corretamente da resposta da API. |
| | `test_generate_chat_response_requires_api_key` | Ausência de credencial falha de forma explícita, sem chamada de rede. |
| | `test_generate_chat_response_injects_retrieved_sharepoint_context` | O contexto recuperado chega ao provedor dentro do prompt enviado. |
| | `test_generate_chat_response_retries_with_exponential_backoff` | Falha transitória é repetida com espera crescente. |
| | `test_generate_chat_response_stops_after_configured_retries` | O número de tentativas respeita o limite configurado, sem laço infinito. |
| | `test_generate_chat_response_does_not_retry_permanent_http_error` | Erro permanente falha na primeira tentativa, sem consumir franquia do provedor. |

**Execução.**

```bash
cd src/backend
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest app/tests -v
```

**Resultado da execução dessa bateria:** 10 testes, 10 aprovados, em 0,21 s.

```text
app/tests/test_gemini_client.py::test_generate_chat_response_maps_text_context_and_usage PASSED
app/tests/test_gemini_client.py::test_generate_chat_response_requires_api_key PASSED
app/tests/test_gemini_client.py::test_generate_chat_response_injects_retrieved_sharepoint_context PASSED
app/tests/test_gemini_client.py::test_generate_chat_response_retries_with_exponential_backoff PASSED
app/tests/test_gemini_client.py::test_generate_chat_response_stops_after_configured_retries PASSED
app/tests/test_gemini_client.py::test_generate_chat_response_does_not_retry_permanent_http_error PASSED
app/tests/test_sharepoint_rag.py::test_loads_mock_sharepoint_list_exports PASSED
app/tests/test_sharepoint_rag.py::test_retrieves_relevant_sharepoint_items PASSED
app/tests/test_sharepoint_rag.py::test_does_not_inject_context_for_unrelated_question PASSED
app/tests/test_sharepoint_rag.py::test_builds_prompt_with_source_labels_and_disclaimer PASSED

============================== 10 passed in 0.21s ==============================
```

**Registro histórico da primeira suíte completa da Sprint 3:** 158 testes, 158 aprovados, em 15,69 s. Os 148 acrescentados desde a bateria original cobriam a API de áudio, o pré-processamento, a extração de entidades, o carregamento do artefato e a inferência.

```text
158 passed, 11 warnings in 15.69s
```

**Verificação atual após a integração da interface.** A execução local em 10 de setembro de 2026 aprovou 171 testes do back-end, 46 testes unitários do front-end e 8 testes de navegador — quatro cenários em desktop e os mesmos quatro em celular. Também passaram lint sem avisos, verificação de formatação e build de produção. O merge da integração ponta a ponta acrescentou quatro testes de rota depois dessa execução, levando o back-end a 175 testes, conforme a Seção 8.11.7. A cobertura unitária do front-end foi de 87,10% das linhas, 84,33% das instruções, 73,12% das ramificações e 83,83% das funções. Os comandos, a matriz por comportamento e os limites da evidência estão em `src/frontend/TESTES.md`.

**Cobertura ainda não atingida.** O teste de navegador atravessa front-end, FastAPI, validação WAV e pipeline, mas substitui Azure, Gemini e classificação nas fronteiras externas. Continuam sem evidência local as chamadas reais aos provedores, autenticação Entra ID, SharePoint corporativo, persistência PostgreSQL, latência de produção e validação manual completa com tecnologia assistiva. Os resultados determinísticos não devem ser usados como aprovação desses itens.

## 8.5 Documentação de front-end e back-end

### 8.5.1 Escopo e estado da implementação

Esta seção descreve a aplicação **que pode ser executada a partir deste repositório**: a bancada web em React, a API FastAPI, o pipeline de classificação e resposta, as integrações externas e o modelo PostgreSQL. O objetivo é permitir que outra pessoa localize cada responsabilidade, reproduza o fluxo e diferencie código operacional de artefatos preparados para etapas futuras.

Para evitar duplicação, os detalhes especializados continuam nas seções já existentes: o modelo de dados está na Seção 4; a arquitetura de implantação, na Seção 6; os contratos e decisões de voz, nas Seções 8.6 a 8.9; o classificador de intenções, nas Seções 8.10 e 8.11; e os testes sistêmicos, na Seção 9. Aqui são registradas as conexões entre esses elementos, o estado real de implementação e os caminhos de reprodução.

O fluxo implementado até esta versão é:

```text
Navegador React
  ├─ texto ───────────────► POST /api/chat ─┐
  └─ WAV + Bearer token ──► POST /api/audio ├─► pipeline.py
                                  │          │    ├─ classificador local opcional
                                  └─ Azure STT    ├─ recuperação em JSONs SharePoint simulados
                                                 └─ Gemini para geração da resposta
                                                        │
                                                        ▼
                                resposta + intenção + fontes + métricas
```

O `GET /health` verifica se o processo FastAPI terminou de iniciar. O caminho de texto e o caminho posterior à transcrição de áudio convergem em `app/pipeline.py`, portanto classificação, recuperação de contexto e geração não possuem implementações paralelas. O front-end transforma o contrato HTTP em mensagens, fontes, indicadores de intenção e estados de carregamento, mas não acessa Azure ou Gemini diretamente e não recebe suas credenciais.

O PostgreSQL/Supabase está conectado de forma opcional: quando `DATABASE_URL` ou `SUPABASE_DATABASE_URL` está configurada, o backend consulta os extratos persistidos e registra conversa, interação, intenção, rota, fontes, workflows, execuções, inscrições, avaliações, notificações, artefatos e auditoria. Sem configuração, consultas, relatórios e alertas podem usar dados sintéticos e repositórios em memória. O fluxo `transacao_gerar_relatorio` executa integralmente em modo local; seu adaptador de Power Automate é opcional e depende das credenciais e do endpoint do ambiente. A geração de alertas é disparada pelo scheduler e processada pelo backend com RabbitMQ, sem depender de Power Automate ou Copilot Studio. Separadamente, um provedor ou simulador pode confirmar a entrega de uma notificação pelo webhook da Seção 8.5.12; o navegador não chama esse webhook. Microsoft Entra ID, SharePoint corporativo e Teams não integram a execução atual. Conversas e preferências permanecem na sessão do navegador; somente o tema pode ser persistido localmente.

### 8.5.2 Arquitetura executável

A visão completa de diretórios está na Seção 8.1. Para acompanhar uma requisição, os pontos de entrada e fronteiras efetivamente usados são:

| Camada | Ponto de entrada | Responsabilidade no fluxo atual |
| --- | --- | --- |
| Interface | `src/frontend/src/App.tsx` | Instala os provedores de tema e conversa e monta a aplicação. |
| Estado do front-end | `src/frontend/src/state/chat-store.tsx` | Mantém conversas em memória, encadeia `previous_interaction_id`, cancela requisições e impede que respostas tardias contaminem outra conversa. |
| Cliente HTTP | `src/frontend/src/lib/api/` | Serializa JSON ou multipart, aplica prazo máximo, interpreta schemas e converte erros em mensagens seguras. |
| API | `src/backend/app/main.py` | Expõe saúde, chat e áudio; valida o contrato externo e normaliza erros. |
| Orquestração | `src/backend/app/pipeline.py` | Executa classificação opcional, resposta controlada fora de escopo e geração fundamentada. |
| Voz | `src/backend/app/audio/` | Autentica a identidade simulada, limita concorrência, valida WAV e chama o Azure Speech-to-Text. |
| Recuperação | `src/backend/app/rag/sharepoint.py` | Carrega exports JSON, ranqueia trechos e monta contexto com fontes declaradas. |
| Geração | `src/backend/app/gemini/` | Chama o Gemini com timeout e retentativas e mapeia texto, uso, latência e fontes. |
| PLN | `src/backend/app/nlp/` | Carrega artefatos treinados, extrai entidades e classifica macrointenção e intenção específica. |
| Dados, artefatos e eventos | `src/database/sql/`, `app/reports/` e `app/alerts/` | Migra, persiste e audita workflows, execuções e inscrições no PostgreSQL; mantém DOCX privado; e processa eventos de alerta por outbox e RabbitMQ. |

Os componentes visuais não chamam `fetch` diretamente; eles acionam operações do estado, que delega ao cliente de `lib/api/`. No back-end, `main.py` não reproduz regras do classificador ou do RAG: encaminha a entrada ao pipeline e converte apenas as falhas previstas em respostas HTTP. Essa separação permite testar a interface, os contratos e cada integração com duplos determinísticos.

### 8.5.3 Documentação automática da API

O FastAPI gera a especificação OpenAPI a partir das rotas de `app/main.py` e dos modelos Pydantic de `app/gemini/schemas.py`, `app/audio/schemas.py` e `app/nlp/schemas.py`. Assim, os contratos validados em execução também alimentam a referência automática.

Com o servidor local na porta padrão, ficam disponíveis:

| Recurso | Endereço local | Conteúdo |
| --- | --- | --- |
| Swagger UI | `http://127.0.0.1:8000/docs` | Referência navegável e formulários para executar as rotas. |
| ReDoc | `http://127.0.0.1:8000/redoc` | Contratos em formato de leitura. |
| OpenAPI JSON | `http://127.0.0.1:8000/openapi.json` | Especificação utilizável por clientes e testes de contrato. |

O título, a descrição e a versão exibidos são definidos na instância `FastAPI` em `app/main.py`. A referência automática demonstra o contrato exposto, mas não substitui as condições de operação registradas a seguir: o teste interativo de áudio exige um token simulado e credenciais válidas do Azure, enquanto o chat que chega ao Gemini requer a respectiva chave.

### 8.5.4 APIs consumidas pelo front-end

O front-end consome somente rotas de mesma origem. Em desenvolvimento, o Vite encaminha `/api` e `/health` para o FastAPI; no build publicado, o servidor responsável pelos arquivos estáticos deve oferecer o mesmo encaminhamento. A variável `API_PROXY_TARGET` muda o destino apenas no servidor de desenvolvimento e nos testes. A tabela abaixo resume as entradas comuns; os contratos completos dos workflows de relatório e alerta estão em [`src/agent/support/IMPLEMENTATION.md`](../src/agent/support/IMPLEMENTATION.md) e no OpenAPI.

| Método e rota | Entrada | Saída utilizada pela interface | Observações de reprodução |
| --- | --- | --- | --- |
| `GET /health` | Sem corpo ou autenticação. | `{"status":"ok"}`. | Confirma a inicialização do processo; não testa Azure, Gemini ou a disponibilidade dos dados. |
| `POST /api/chat` | JSON com `message` (1 a 20.000 caracteres), `previous_interaction_id` opcional e `use_intent_classifier` booleano. | Texto, ID da interação, modelo, latências, consumo, intenção opcional e lista de fontes. | Não exige Bearer token na versão atual. O ID anterior mantém o encadeamento lógico da conversa. |
| `POST /api/audio` | Multipart com arquivo `audio`; `conversation_id`, `language`, `previous_interaction_id` e `use_intent_classifier` opcionais; cabeçalho `Authorization: Bearer <token>`. | Transcrição, conversa, interação, intenção, resposta resumida, resposta completa em `chat` e `pipeline_status`. | O navegador envia WAV PCM mono, 16 bits e 16 kHz. O back-end revalida o conteúdo e aceita uma requisição simultânea por identidade. |
| `/api/workflow-sessions` e `/api/report-requests` | Respostas guiadas, revisão, ação idempotente e confirmação assinada. | Estado da sessão, execução e download autenticado do DOCX. | O modo local é completo; a automação externa é opcional. |
| `/api/alert-workflow-sessions` e `/api/alert-subscriptions` | Configuração, confirmação e comandos de ciclo de vida da inscrição. | Estado da sessão e da inscrição recorrente. | O processamento posterior ocorre nos workers do projeto. |
| `GET /api/notifications` e `POST /api/notifications/{id}/read` | Token de identidade simulado no ambiente local. | Lista de notificações e confirmação de leitura. | A central consulta periodicamente a API; não recebe webhook. |

Uma chamada textual pode ser reproduzida sem o front-end, depois de iniciar o FastAPI e configurar o Gemini:

```powershell
$body = @{
  message = "Qual é o status do projeto de sinalização?"
  previous_interaction_id = $null
  use_intent_classifier = $false
} | ConvertTo-Json

$response = Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/chat `
  -ContentType "application/json" `
  -Body $body

$response | Select-Object text, interaction_id, model, latency_ms, retrieval_ms
$response.sources | Select-Object id, title, list_name, web_url, score
```

O resultado esperado é um objeto com `text`, métricas e `sources`; a lista pode estar vazia quando nenhum trecho ultrapassa o critério de relevância. Para testar o encadeamento, envie o `interaction_id` recebido como `previous_interaction_id` na chamada seguinte. O multipart de áudio já possui exemplo completo na Seção 8.7.4 e pode ser exercitado sem montar o corpo manualmente pelo Swagger UI.

No chat, `use_intent_classifier=false` encaminha a mensagem diretamente à recuperação e à geração. Quando o campo é `true`, o pipeline classifica primeiro: solicitações fora de escopo ou abaixo dos limiares recebem uma resposta controlada sem chamada ao Gemini; solicitações roteadas seguem para o mesmo caminho RAG. A resposta pode, portanto, não possuir `interaction_id`, e o front-end mantém nesse caso o último ID válido da conversa.

No áudio, a ordem é validação, transcrição no Azure e chamada ao mesmo `process_message` usado pelo chat. `conversation_id` identifica a conversa da interface, enquanto `interaction_id` vem do processamento textual. O objeto legado `answer` oferece texto e referências resumidas; `chat` preserva o contrato completo do endpoint textual, inclusive métricas, trecho recuperado e metadados das fontes.

As fontes completas contêm identificador, título, lista de origem, URL, data de alteração, pontuação e trecho opcional. A interface não cria referências quando a API devolve uma lista vazia. Os detalhes do multipart, limites de áudio e códigos específicos estão nas Seções 8.7 e 8.8, evitando repetir aqui a especificação de voz.

O cliente aplica limite de 120 segundos e permite cancelamento por `AbortController`. Cancelar interrompe a espera no navegador e impede que uma resposta tardia altere o estado atual; isso não garante o cancelamento de uma chamada que o back-end ou um provedor já tenha recebido. Erros conhecidos de validação, autenticação, limite, concorrência, provedor e rede são convertidos em mensagens próprias. HTML de proxy, traceback e mensagens privadas dos provedores não são exibidos à pessoa usuária.

### 8.5.5 Integrações e limites operacionais

| Integração | Implementação atual | Configuração ou fonte | Limite conhecido |
| --- | --- | --- | --- |
| Azure AI Speech | `audio/transcription.py` envia o WAV validado para transcrição `pt-BR`, com timeout e retentativas. | `AZURE_SPEECH_RESOURCE` ou `AZURE_SPEECH_ENDPOINT`, `AZURE_SPEECH_KEY`, timeout e número de tentativas no `.env` do back-end. | Exige credencial e rede; a suíte padrão substitui a fronteira HTTP por duplo. |
| Gemini | `gemini/client.py` gera a resposta a partir da pergunta e do contexto recuperado, com timeout e backoff. | `GEMINI_API_KEY`, modelo, limite de saída, nível de raciocínio, timeout e retentativas. | Sem chave, o chat que precisa de geração devolve indisponibilidade controlada. |
| RAG de SharePoint simulado | `rag/sharepoint.py` pesquisa exports JSON versionados e inclui rótulos de fonte no prompt. | `rag/data/sharepoint/` ou `SHAREPOINT_MOCK_DATA_DIR`. | Não acessa o tenant corporativo nem sincroniza alterações do SharePoint. |
| Classificador local | `nlp/` carrega o `joblib` e o encoder BERTimbau via PyTorch/Transformers; `PLN_WARMUP=1` antecipa a carga. | Artefatos em `src/notebooks/artefatos/`; encoder obtido do repositório de modelo indicado na Seção 8.11 (`requirements-pln.txt`). | A primeira instalação/carga pode exigir internet e cache local; não executa transações. |
| Identidade do áudio | `audio/security.py` resolve o Bearer token por um mapa simulado e limita uma transcrição ativa por identidade. | `AUDIO_SIMULATED_IDENTITIES`, por exemplo `token-local=usuario-local`. | Não valida JWT do Entra ID e não aplica as regras da tabela `access_rules`. |
| RabbitMQ | `alerts/messaging.py` publica e consome eventos persistentes de avaliação, criação de notificação e confirmação de entrega, com confirmação manual e DLQ. | `RABBITMQ_URL` e `compose.rabbitmq.yml`. | Necessário para o alerta assíncrono persistente; AMQP, scheduler e outbox não são webhooks. A rodada documental usa double controlado, não broker externo. |

O SharePoint corporativo, Entra ID, Teams e Copilot Studio aparecem nos desenhos e no modelo-alvo, mas não possuem adaptador ativo nesta versão. Power Automate possui um adaptador opcional apenas para relatórios; o modo local não depende dele e o alerta não o utiliza. As demais intenções transacionais continuam sem escrita externa. Essa distinção evita interpretar a bancada como um canal de produção ou como evidência de autorização corporativa.

### 8.5.6 Banco de dados: modelo e integrações operacionais

O modelo físico descrito na Seção 4.3 está implementado em `src/database/sql/01_create_database.sql` para PostgreSQL 14 ou superior, inclusive Supabase PostgreSQL. São 25 tabelas com UUIDs gerados por `pgcrypto`, chaves estrangeiras, restrições de domínio, índices para os caminhos previstos e `JSONB` para metadados cuja estrutura ainda pode evoluir. A relação completa de tabelas e as decisões de modelagem permanecem em `src/database/docs/README.md` para não repetir o dicionário da Seção 4.

Os três scripts têm responsabilidades separadas e ordem explícita:

1. `01_create_database.sql` cria extensões, tabelas, restrições, índices, gatilhos de `updated_at` e comentários;
2. `02_initial_data.sql` insere um subportfólio e um projeto sintéticos, artefato, TAP, benefício, avanço, marco, risco e catálogo mínimo de intenções;
3. `03_rollback_data.sql` remove o baseline em ordem reversa de dependência e deve ser usado somente em ambiente descartável ou depois de backup.

Com um PostgreSQL acessível e `psql` no `PATH`, a criação e a carga podem ser reproduzidas da raiz do repositório:

```powershell
$env:DATABASE_URL = "postgresql://usuario:senha@localhost:5432/metro_poc"
psql "$env:DATABASE_URL" -v ON_ERROR_STOP=1 -f src/database/sql/01_create_database.sql
psql "$env:DATABASE_URL" -v ON_ERROR_STOP=1 -f src/database/sql/02_initial_data.sql
```

Em um banco vazio dedicado à PoC, confirme o baseline e a carga sem depender de uma ferramenta gráfica:

```powershell
psql "$env:DATABASE_URL" -c "SELECT COUNT(*) AS tabelas_public FROM pg_tables WHERE schemaname = 'public';"
psql "$env:DATABASE_URL" -c "SELECT code, title, status FROM public.projects WHERE code = 'PRJ-0442';"
psql "$env:DATABASE_URL" -c "SELECT macro_intent, COUNT(*) FROM public.intent_catalog GROUP BY macro_intent ORDER BY macro_intent;"
```

O primeiro comando deve informar 25 tabelas em um schema `public` inicialmente vazio. O segundo deve devolver o projeto sintético `PRJ-0442`, e o terceiro deve listar as macrointenções da carga mínima. Falha em qualquer uma dessas consultas indica que criação e carga não terminaram conforme o esperado; não avance para uma integração antes de corrigir o primeiro erro reportado por `ON_ERROR_STOP`.

A opção `ON_ERROR_STOP` faz o processo terminar na primeira falha em vez de continuar com uma instalação parcial. A carga usa conflitos controlados e verificações de existência para que uma nova execução atualize ou preserve os registros sintéticos esperados, em vez de duplicá-los.

O banco possui integração opcional no backend. Com `DATABASE_URL` ou `SUPABASE_DATABASE_URL`, a recuperação consulta os extratos PostgreSQL e a rastreabilidade persiste conversas, interações, classificação, rota, fontes, workflows e auditoria; sem URL configurada, a aplicação continua reproduzível com dados sintéticos e repositórios em memória. A interface ainda mantém o histórico geral de conversa apenas em memória, sem reidratação.

Sobre o baseline, migrations incrementais especializam os dois workflows. Para relatórios, `05`, `07`, `09` e `11` cobrem execuções, artefatos, callbacks, sessões, respostas, bucket privado e RLS; os scripts `manage_report_infrastructure.py` e `manage_report_security.py` aplicam e verificam essa infraestrutura. Para alertas, `15_alert_deadline_flow.sql` cria inscrições, avaliações, ocorrências, notificações, tentativas de entrega e outbox; `17_notification_delivery_callbacks.sql` persiste os callbacks de entrega; e `18_notification_delivery_attempt_callback.sql` liga cada tentativa processada ao `callback_id` com unicidade. Todas as tabelas internas relevantes usam RLS e não concedem acesso direto a `anon` ou `authenticated`. `16_rollback_alert_deadline_flow.sql` é o rollback do núcleo original e `scripts/manage_alert_infrastructure.py` oferece `apply`, `status` e `rollback`. Assim, memória e dados sintéticos são modos de desenvolvimento, não substitutos da integração persistente já implementada.

### 8.5.7 Front-end: componentes e comportamento

A bancada usa React 19, TypeScript e Vite. `App.tsx` instala `ThemeProvider` e `ChatProvider`; `AppShell` organiza a barra de conversas, o chat e o painel de documentos. A implementação detalhada de cada componente está em `src/frontend/README.md`; o mapa abaixo registra como as pastas colaboram sem repetir a lista de arquivos da Seção 8.1.

| Área | Responsabilidade observável |
| --- | --- |
| `components/sidebar/` | Criação, busca, seleção e exclusão de conversas da sessão, além do token simulado usado por áudio, relatórios e alertas. |
| `components/chat/` | Estado vazio, histórico, Markdown seguro, classificação, fontes, workflows guiados, confirmação, progresso e download de relatório. |
| `components/notifications/` | Central de notificações, contagem de não lidas e gestão de inscrições de alerta. |
| `components/composer/` | Entrada de texto, alternância da validação de intenção, captura, prévia, descarte e envio de áudio. |
| `components/documents/` | Lista de fontes, trecho recuperado, link original e métricas da resposta selecionada. |
| `components/layout/` e `components/ui/` | Layout responsivo, tema, diálogos, abas e controles acessíveis reutilizáveis. |
| `hooks/`, `lib/` e `state/` | Microfone, conversão WAV, domínio, cliente HTTP, reducer, concorrência e cancelamento. |

A rastreabilidade entre ação, estado e contrato ajuda a localizar uma alteração sem percorrer toda a árvore:

| Ação na interface | Operação de estado | Fronteira chamada | Resultado renderizado |
| --- | --- | --- | --- |
| Enviar texto | `sendMessage` delega ao fluxo comum `send` | `sendChatMessage` em `lib/api/chat.ts` | Mensagem da pessoa, resposta, intenção, fontes e métricas. |
| Enviar gravação | `sendAudio` delega ao mesmo `send` | `uploadAudio` em `lib/api/audio.ts` | Transcrição como entrada e `chat` como resposta do agente. |
| Interromper | `stop` aborta o controlador pendente | `AbortSignal` recebido pelo cliente comum | O indicador termina e nenhuma resposta tardia é aplicada. |
| Trocar ou excluir conversa | `selectConversation` ou `deleteConversation` despacha no reducer | Nenhuma chamada HTTP | Histórico, fontes e documento selecionado mudam apenas na sessão. |
| Abrir uma fonte | seleção derivada de `activeSources` | Nenhuma nova chamada HTTP | `DocumentViewer` mostra metadados e o trecho já devolvido pela API. |

Essa cadeia também define onde testar: componentes verificam a apresentação, a store verifica concorrência e associação à conversa, o cliente verifica serialização e erros, e o Playwright atravessa as quatro camadas pelo comportamento observável.

O envio por texto aceita uma sugestão ou mensagem digitada, usa `Enter` para enviar e `Shift+Enter` para nova linha. O envio por voz requer o token da bancada, permissão do microfone, conclusão da gravação e confirmação da prévia. A captura para em 60 segundos; o navegador converte o sinal para o formato aceito antes do upload. Durante qualquer chamada, a interface bloqueia duplicidade e oferece interrupção.

Cada conversa mantém seu último `interaction_id`, mensagens, fontes e preferências enquanto a página permanece aberta. Criar ou selecionar outra conversa cancela a espera corrente, e o identificador interno da requisição impede que um retorno atrasado seja inserido no destino errado. A busca e a exclusão alteram apenas o estado local. Recarregar a página remove histórico e token; o tema é a única preferência com persistência prevista.

No desktop, as três áreas ficam lado a lado. Abaixo de 1024 px, conversas e documentos abrem em diálogos que podem ser fechados com `Escape`. Estados de carregamento e mudanças relevantes possuem anúncios para tecnologias assistivas, os controles têm nomes acessíveis e o foco retorna ao contexto apropriado ao fechar um diálogo. Essas propriedades fazem parte dos testes descritos em `src/frontend/TESTES.md`, não apenas do desenho visual.

### 8.5.8 Back-end: ciclo de processamento

O back-end usa FastAPI e Pydantic. Na inicialização, `lifespan` lê `PLN_WARMUP`: quando igual a `1`, o classificador é carregado em uma thread antes de o serviço aceitar consultas; quando igual a `0`, a carga ocorre na primeira classificação. O carregamento é protegido por lock para evitar inicializações concorrentes.

Em `POST /api/chat`, Pydantic remove espaços externos e rejeita mensagem vazia ou acima de 20.000 caracteres. `process_message` classifica somente quando solicitado. Uma classificação não roteável encerra o fluxo com uma resposta local e segura; as demais entradas seguem para recuperação de contexto e Gemini. Erros de configuração ou do provedor são convertidos em indisponibilidade ou falha controlada, sem expor detalhes internos.

Em `POST /api/audio`, a identidade simulada é resolvida antes da leitura. O arquivo é lido em blocos de 64 KiB e interrompido assim que ultrapassa o teto, evitando manter em memória um upload que será recusado. Depois da validação e do Azure STT, a transcrição é entregue ao mesmo pipeline do chat por meio de uma thread, para não bloquear o laço assíncrono. A resposta combina o resultado de voz com o contrato completo do chat.

O RAG consulta o PostgreSQL quando configurado e usa como fallback explícito dados sintéticos substituíveis por diretório; em ambos os casos, pontua a correspondência e injeta somente resultados relevantes com identificação da fonte. O cliente Gemini controla timeout e retentativas de falhas transitórias. A rastreabilidade registra no banco o contrato de classificação, a rota, as fontes e os eventos de auditoria; autorização por perfil continua como fronteira de implementação futura.

Para isolar uma falha sem confundir disponibilidade do processo com disponibilidade dos provedores, use os checkpoints na ordem:

| Checkpoint | O que comprova | O que ainda não comprova |
| --- | --- | --- |
| `GET /health` | FastAPI terminou a inicialização; com `PLN_WARMUP=1`, a carga inicial do classificador também terminou. | Credenciais, cota ou rede de Azure e Gemini. |
| `POST /api/chat` com classificador desligado | Validação JSON, RAG local, montagem do prompt e fronteira Gemini. | Encoder e limiares do classificador. |
| `POST /api/chat` com classificador ligado | Carga do modelo, inferência, limiares e roteamento antes da geração. | Captura, WAV e Azure STT. |
| `POST /api/audio` | Identidade simulada, concorrência, leitura limitada, validação WAV, Azure STT, reutilização do pipeline e persistência opcional da rastreabilidade. | Autenticação Entra ID e reidratação do histórico no frontend. |
| Resposta com `sources` | Recuperação dos JSONs, metadados e propagação até o contrato. | Consulta ao SharePoint corporativo. |

Se um checkpoint falhar, teste primeiro o anterior e consulte o corpo controlado da resposta. Os testes determinísticos reproduzem cada fronteira com duplos; uma validação do provedor real deve ser executada separadamente, pois depende de credenciais, rede, cota e região.

### 8.5.9 Execução e verificação reproduzíveis

O passo a passo completo, incluindo pré-requisitos, configuração sem credenciais versionadas, inicialização dos dois serviços, banco opcional, teste manual e solução de problemas, está em `docs/Manual-instalacao.md`. A sequência mínima parte da raiz:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r src/backend/requirements.txt -r src/backend/requirements-pln.txt
Copy-Item src/backend/.env.example src/backend/.env
Set-Location src/frontend
npm ci
```

Depois de preencher o `.env` local, o back-end deve ser iniciado na porta 8000 e o Vite na 5173, em terminais separados. `GET /health` deve devolver `status=ok` antes do uso. A referência automática fica em `/docs`; a interface, em `http://localhost:5173`.

As verificações locais são `pytest` para o back-end e, no front-end, lint, formatação, cobertura, build e Playwright. Os comandos e resultados de referência estão em `src/frontend/TESTES.md`. Os testes automatizados substituem Azure e Gemini por duplos na fronteira de rede; por isso são reproduzíveis sem credenciais, mas não comprovam integrações corporativas nem os RNFs dependentes do ambiente de produção.

### 8.5.10 Geração rastreável de relatório executivo

A intenção `transacao_gerar_relatorio` possui rota determinística no back-end:
depois da classificação, o pipeline devolve a diretiva
`guided_workflow/start/transacao_gerar_relatorio` e não chama o provedor
generativo. O frontend inicia uma sessão persistível e apresenta no próprio
chat as perguntas de escopo, período, público, finalidade, ênfase e contexto,
seguindo até a revisão e a confirmação explícita. O runtime não depende de
Copilot Studio.

O contrato HTTP implementa sessões com revisão otimista e `client_action_id`,
preparação, confirmação protegida por HMAC, idempotência, consulta de estado,
download autenticado e callback do Power Automate. Em modo local, uma massa
sintética autorizada é congelada em snapshot e renderizada em DOCX. No modo
`power_automate_simulator`, o mesmo contrato de callback é exercitado sem
tenant externo. No modo real, o Power Automate recebe o snapshot autorizado,
usa AI Builder apenas para transformações com JSON fixo e devolve o resultado
estruturado; não gera nem hospeda o arquivo.

O backend valida o retorno, aplica redação determinística como fallback, gera
o DOCX com `python-docx`, calcula SHA-256 e o armazena no bucket privado
`generated-reports` do Supabase. O navegador nunca recebe a service role nem
uma URL pública permanente: o cartão do relatório no chat baixa o arquivo pelo
endpoint autenticado. SharePoint, OneDrive e Word Online não participam deste
fluxo.

O código executável está em `src/backend/app/reports/`; a migration está em
`src/database/sql/05_report_generation.sql` e
`src/database/sql/07_guided_report_workflow.sql`; o bucket privado é criado
por `src/database/sql/09_create_report_storage_bucket.sql`, com rollback seguro
em `src/backend/scripts/rollback_report_storage_bucket.py`. A migration
`src/database/sql/11_secure_report_workflow_tables.sql` mantém as cinco tabelas
internas sob RLS e sem privilégios para `anon` ou `authenticated`; o frontend está
em `src/frontend/src/components/chat/report-workflow-card.tsx`. Os artefatos
portáteis de OpenAPI, Power Automate e AI Builder permanecem em
`src/agent/support/`; `src/agent/ONESHOT` é somente histórico e não integra o
runtime. A especificação operacional completa fica em
[`src/agent/support/IMPLEMENTATION.md`](../src/agent/support/IMPLEMENTATION.md), junto ao fluxo de alerta para manter uma
única referência operacional dos workflows especializados.

### 8.5.11 Alerta autônomo de prazo

A intenção `alerta_prazo_atraso` também possui rota determinística. O frontend
coleta projeto, limiar, frequência e política de reenvio e, após a confirmação
assinada, cria uma inscrição persistente. O scheduler registra solicitações de
avaliação na outbox; o publisher as envia ao RabbitMQ; o evaluator revalida o
acesso e compara o cronograma; e o notifier disponibiliza, de forma idempotente,
a notificação na central interna da aplicação.

O disparo e a geração do alerta não usam Copilot Studio, Power Automate, Teams,
e-mail ou webhook: partem do scheduler. A confirmação posterior de entrega pode
ser recebida do provedor/simulador pelo segundo webhook descrito na Seção
8.5.12. A comunicação entre processos usa AMQP e as ações da interface usam
REST; a central consulta notificações pela API e nunca chama o webhook. Filas
duráveis, confirmação manual, dead-letter queues, backoff da outbox,
`episode_key` única e IDs de correlação protegem contra perda e duplicação. O
usuário pode pausar, retomar ou cancelar a inscrição e marcar notificações como
lidas.

No banco, `15_alert_deadline_flow.sql` cria `alert_subscriptions`,
`alert_evaluations`, `alert_occurrences`, `alert_notifications`,
`notification_delivery_attempts`, `notification_delivery_callbacks` e
`message_outbox`, protegidas por RLS e
sem acesso direto dos papéis públicos. A API e os workers usam a conexão segura
do backend. O frontend está em `components/chat/alert-workflow-card.tsx` e
`components/notifications/notification-center.tsx`; a implementação operacional
completa está consolidada em [`src/agent/support/IMPLEMENTATION.md`](../src/agent/support/IMPLEMENTATION.md).

As execuções de ponta a ponta, com casos elegíveis e não elegíveis, repetição,
armazenamento e auditoria correlacionada, estão em
[`src/backend/evidencias/alerta-prazo-atraso/`](../src/backend/evidencias/alerta-prazo-atraso/README.md),
junto da reexecução da regra com o código final e da saída dos testes.

### 8.5.12 Webhooks e mensageria integrados (S5-09 a S5-11)

O estado atual possui **dois webhooks HTTP**. O primeiro recebe o resultado do
processamento opcional de relatório. O segundo recebe a confirmação de entrega
de uma notificação e inicia seu processamento assíncrono pela outbox. O
scheduler que solicita avaliações, os eventos AMQP e as consultas REST do
frontend são mecanismos diferentes e não são chamados de webhook.

#### Webhook 1 — resultado do relatório

**Finalidade.** Receber do Power Automate ou do simulador o estado terminal e o
JSON estruturado de uma execução criada anteriormente. A rota correlaciona o
retorno à execução, valida sua idempotência, atualiza o estado, gera o DOCX no
backend quando há sucesso e persiste o callback.

| Item | Contrato |
| --- | --- |
| Método e rota | `POST /api/integrations/power-automate/report-results` |
| Header obrigatório | `X-Callback-Token: <token>` |
| Variável de ambiente | `REPORT_CALLBACK_TOKEN` |
| Content-Type | `application/json` |
| Persistência | `automation_callbacks` e atualização de `report_executions` |
| Autenticação atual | Token compartilhado comparado em tempo constante. Token inválido retorna `401`. |

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | :---: | --- |
| `contract_version` | literal `"1.0"` | Não | Versão do contrato; assume `1.0`. |
| `callback_id` | string, 8–160 | Sim | Identificador idempotente global do retorno. |
| `execution_id` | string, 1–160 | Sim | Execução de relatório previamente criada. |
| `correlation_id` | string, 1–120 | Sim | Deve ser igual ao da execução. |
| `flow_run_id` | string, 1–160 | Sim | Identificador da execução no fluxo externo/simulador. |
| `status` | enum | Sim | Estado terminal: `completed`, `completed_with_warnings`, `failed`, `blocked` ou `cancelled`. |
| `result` | objeto ou `null` | Condicional | Obrigatório nos estados concluídos; contém `schema_version` e resultados estruturados opcionais. |
| `warnings` | array de strings | Não | Até 50 advertências controladas. |
| `error_code` | string ou `null` | Condicional | Obrigatório em `failed` e `blocked`. |
| `error_message` | string ou `null` | Não | Mensagem controlada, até 500 caracteres. |

Exemplo completo de requisição bem-sucedida:

```http
POST /api/integrations/power-automate/report-results HTTP/1.1
Content-Type: application/json
X-Callback-Token: <REPORT_CALLBACK_TOKEN>

{
  "contract_version": "1.0",
  "callback_id": "callback-report-001",
  "execution_id": "9b13d80d-2b0f-4fd6-a01f-c73f86ef6105",
  "correlation_id": "c95e6931-9cb2-452f-b8e9-d2ab86753cf8",
  "flow_run_id": "flow-run-001",
  "status": "completed",
  "result": {"schema_version": "1.0"},
  "warnings": [],
  "error_code": null,
  "error_message": null
}
```

Exemplo resumido de resposta `200`:

```json
{
  "contract_version": "1.0",
  "execution_id": "9b13d80d-2b0f-4fd6-a01f-c73f86ef6105",
  "correlation_id": "c95e6931-9cb2-452f-b8e9-d2ab86753cf8",
  "status": "completed",
  "status_url": "/api/report-requests/9b13d80d-2b0f-4fd6-a01f-c73f86ef6105",
  "artifact": {"artifact_id": "<id>", "file_name": "relatorio.docx", "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "size_bytes": 1024, "sha256": "<64 caracteres hexadecimais>", "download_url": "/api/report-requests/9b13d80d-2b0f-4fd6-a01f-c73f86ef6105/artifact", "storage_provider": "local", "created_at": "2026-09-25T12:00:01Z"},
  "warnings": [],
  "error": null,
  "created_at": "2026-09-25T11:59:00Z",
  "updated_at": "2026-09-25T12:00:01Z"
}
```

| Código | Quando ocorre |
| :---: | --- |
| `200` | Primeiro callback válido ou repetição idêntica. |
| `401` | `X-Callback-Token` ausente ou inválido. |
| `404` | `execution_id` inexistente. |
| `409` | Correlação divergente, estado terminal incompatível ou mesmo `callback_id` com payload diferente. |
| `422` | Campos, tipos, status ou condicionais inválidos; campos extras também são rejeitados. |
| `503` | Token de callback não configurado ou repositório/dependência indisponível. |
| `500` | Falha inesperada não classificada; não é usada como resposta normal do domínio. |

**Idempotência e processamento.** O backend serializa o payload validado de
forma canônica, calcula SHA-256 e consulta `automation_callbacks`. O mesmo
`callback_id` e o mesmo hash retornam a execução já processada com `200`; hash
diferente retorna `409`. Em sucesso, o resultado estruturado é validado contra
o snapshot autorizado, o DOCX é renderizado e a execução é concluída. Em falha,
o estado e o erro controlado são persistidos. Esse webhook permanece síncrono e
**não publica no RabbitMQ**.

#### Webhook 2 — confirmação de entrega de notificação

**Finalidade.** Receber de um provedor ou simulador a confirmação de uma
notificação existente. O navegador não chama esta rota: ele apenas lista e
marca notificações como lidas pelas APIs da central.

| Item | Contrato |
| --- | --- |
| Método e rota | `POST /api/integrations/notifications/delivery-results` |
| Header obrigatório | `X-Callback-Token: <token>` |
| Variável de ambiente | `NOTIFICATION_CALLBACK_TOKEN` |
| Content-Type | `application/json` |
| Persistência de entrada | `notification_delivery_callbacks` |
| Autenticação atual | Token compartilhado comparado em tempo constante; ausente ou inválido retorna `401`. |
| Processamento | Callback e evento são gravados atomicamente; a tentativa é criada pelo consumer. |

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | :---: | --- |
| `callback_id` | string, 8–160 | Sim | Chave idempotente do retorno. |
| `notification_id` | UUID | Sim | Notificação existente em `alert_notifications`. |
| `provider` | string, 1–80 | Sim | Provedor ou double, por exemplo `simulated`. |
| `status` | enum | Sim | `delivered` ou `failed`. |
| `attempted_at` | data/hora ISO 8601 | Sim | Momento informado pelo provedor. |
| `error_code` | string ou `null` | Não | Código da falha, quando houver. |

Exemplo completo:

```http
POST /api/integrations/notifications/delivery-results HTTP/1.1
Content-Type: application/json
X-Callback-Token: <NOTIFICATION_CALLBACK_TOKEN>

{
  "callback_id": "delivery-callback-001",
  "notification_id": "1674b3e9-ecba-4a78-a50f-848f5eaf0d79",
  "provider": "simulated",
  "status": "delivered",
  "attempted_at": "2026-09-25T12:00:00Z",
  "error_code": null
}
```

Exemplo de resposta `200`:

```json
{
  "callback_id": "delivery-callback-001",
  "notification_id": "1674b3e9-ecba-4a78-a50f-848f5eaf0d79",
  "provider": "simulated",
  "status": "delivered",
  "attempted_at": "2026-09-25T12:00:00Z",
  "error_code": null,
  "received_at": "2026-09-25T12:00:01Z"
}
```

| Código | Quando ocorre |
| :---: | --- |
| `200` | Callback novo persistido e enfileirado, ou repetição idêntica. |
| `401` | `X-Callback-Token` ausente ou inválido. |
| `404` | `notification_id` não existe. |
| `409` | Mesmo `callback_id` com payload diferente. |
| `422` | UUID, status, data, tipo ou campo extra inválido. |
| `503` | `NOTIFICATION_CALLBACK_TOKEN` ausente ou persistência indisponível. |
| `500` | Falha inesperada não classificada; não é usada como resposta normal do domínio. |

**Idempotência e processamento.** A rota calcula SHA-256 do payload canônico.
Na primeira chamada, `notification_delivery_callbacks` e o evento de outbox são
gravados na mesma operação lógica — sob o mesmo lock em memória e na mesma
transação PostgreSQL. Uma repetição idêntica devolve o `received_at` original e
não cria outro evento. Conteúdo diferente com a mesma chave retorna `409`. O
consumer compara novamente o payload ao hash persistido e usa `callback_id`
único em `notification_delivery_attempts`: `delivered` é armazenado no estado
interno `available`; `failed` e `error_code` são preservados.

#### Topologia RabbitMQ

| Elemento | Valor e responsabilidade |
| --- | --- |
| Exchange principal | `metro.alerts`, tipo `topic`, durável. |
| Dead-letter exchange | `metro.alerts.dlx`, tipo `direct`, durável. |
| Routing keys/filas | `alert.evaluation.requested`, `alert.notification.requested` e `notification.delivery.received`; uma fila durável por chave. |
| DLQs | `<routing-key>.dead`, ligadas à DLX com a mesma routing key. |
| Produtor de avaliação | Scheduler → repository/outbox. |
| Produtor de notificação | Evaluator → repository/outbox. |
| Produtor de entrega | Webhook 2 → callback + outbox na mesma operação. |
| Publisher | `python -m app.alerts.worker publisher`; reivindica a outbox com `FOR UPDATE SKIP LOCKED` e publica mensagens persistentes. |
| Consumers | `evaluator`, `notifier` e `delivery`, executados por `app.alerts.worker`. |
| Confirmação | `incoming.process(...)` confirma somente quando o handler termina sem exceção. |
| Retry do publisher | Falha volta a `pending` com atraso de `30 s × tentativas`; após cinco tentativas fica `failed`, com `last_error`. |
| Retry do consumer | Primeira falha é reenfileirada; uma falha após redelivery é rejeitada e roteada à DLQ. |

O envelope publicado contém `event_id` (UUID e `message_id` AMQP),
`event_type="notification.delivery.received"`, `correlation_id` herdado da
notificação e `payload`. O payload repete somente os campos validados do
callback: `callback_id`, `notification_id`, `provider`, `status`,
`attempted_at` e `error_code`. O consumer valida novamente esse envelope antes
de acessar o callback persistido.

Fluxo completo da confirmação de entrega:

```text
provedor/simulador
  -> POST /api/integrations/notifications/delivery-results
  -> autenticação + schema + hash idempotente
  -> notification_delivery_callbacks + message_outbox (mesma operação)
  -> publisher
  -> exchange metro.alerts / notification.delivery.received
  -> fila notification.delivery.received
  -> consumer delivery revalida envelope e payload
  -> notification_delivery_attempts (callback_id único)
  -> ACK; em falha, retry e depois notification.delivery.received.dead
```

O fluxo regular do alerta continua diferente: scheduler → outbox →
`alert.evaluation.requested` → evaluator → outbox →
`alert.notification.requested` → notifier → central. A interface usa
`GET /api/notifications` e `POST /api/notifications/{id}/read`; AMQP e
scheduler não são webhooks.

#### Testes e limites comprovados

Em 25/09/2026, os comandos focados aprovaram **22 testes de alertas** e **24
testes de relatórios** (46 no total). Eles cobrem sucesso, autenticação inválida,
payload inválido, repetição, conflito, ausência do recurso, persistência em
memória, outbox, routing keys, publisher com double, consumers de sucesso/falha
e evento inválido. O registro reproduzível está em
[`docs/evidencias/sprint-05/webhooks-rabbitmq.md`](evidencias/sprint-05/webhooks-rabbitmq.md).

Não houve execução real de Power Automate, Teams, SharePoint corporativo ou
Copilot Studio. O modo `power_automate_simulator` e doubles controlados validam
os contratos. Nesta rodada, o publisher RabbitMQ também foi testado com double,
sem conexão a broker externo; portanto a documentação não usa esses testes como
evidência de homologação Microsoft ou de tráfego RabbitMQ em produção.

## 8.6 Requisitos das APIs de voz (STT/TTS)

### 8.6.1 Objetivo e delimitação

Esta seção consolida os requisitos usados para avaliar interfaces de *Speech-to-Text* (STT) e *Text-to-Speech* (TTS), com base na especificação da Sprint 1. O levantamento define o que cada API deve receber e devolver, quais formatos e restrições precisam ser conhecidos e quais critérios orientam a comparação entre provedores. As decisões e os contratos específicos de STT e TTS são detalhados, respectivamente, nas Seções 8.7 e 8.8.

Os dois serviços ocupam posições diferentes no fluxo de voz:

1. o **STT** recebe o áudio enviado pelo usuário e produz a solicitação textual encaminhada ao pipeline de PLN;
2. o **TTS** recebe a resposta textual final produzida pelo agente e sintetiza um áudio que poderá ser devolvido pelo canal de interação.

Essa distinção preserva a delimitação da Sprint 1. A arquitetura inicial prevê solicitações por texto ou áudio e um componente de conversão de áudio em texto, enquanto os critérios de aceitação do RF01 exigem, no MVP, que o pipeline aceite solicitações textuais. A Seção 8.8 detalha o STT previsto na solução atual. A Seção 8.9 registra a avaliação e o contrato técnico de TTS, mas sua implementação continua classificada na Seção 3.4.5 como evolução; documentar a API não altera o escopo do MVP.

### 8.6.2 Entradas, saídas e formatos

| Serviço | Entrada esperada | Saída esperada | Formatos e metadados adotados ou exigidos | Destino no fluxo | Situação no escopo |
|---|---|---|---|---|---|
| **STT** | Fala em português do Brasil (`pt-BR`), capturada pelo canal como arquivo ou fluxo de áudio. O caso de uso atual é uma pergunta curta do usuário. | Transcrição textual estruturada. Quando disponível, a resposta deve expor o estado do reconhecimento, o texto normalizado e a confiança ou as alternativas retornadas pelo provedor. | A avaliação deve registrar contêiner, codec, taxa de amostragem, número de canais, duração e tamanho máximos, envio binário ou multipart e suporte a processamento síncrono ou streaming. No contrato adotado na Seção 8.8, usa-se preferencialmente WAV com PCM, 16 kHz e mono; OGG com OPUS, 16 kHz e mono também é aceito pelo endpoint documentado. | O texto final é encaminhado ao pipeline de PLN como uma solicitação textual; o STT não classifica a intenção nem gera a resposta do agente. | Componente previsto na arquitetura e detalhado na Seção 8.8. A disponibilidade no ambiente do parceiro ainda depende de confirmação com a GTI. |
| **TTS** | Resposta textual final do agente em português do Brasil, codificada em um documento SSML válido após a aplicação das regras de acesso e fundamentação. | Bytes do áudio sintetizado, acompanhados do tipo de mídia correspondente ao formato solicitado. | O contrato da Seção 8.9 adota `application/ssml+xml` na entrada e `audio-24khz-48kbitrate-mono-mp3` na saída, adequado à reprodução direta. `riff-24khz-16bit-mono-pcm` (WAV) é a alternativa documentada para processamento sem perdas. Devem ser respeitados os limites de tamanho do SSML, duração e taxa de requisições do provedor. | O áudio é devolvido pela camada de interface sem alterar o conteúdo textual fundamentado, que permanece como resposta canônica do agente. | Contrato técnico documentado na Seção 8.9; a implementação permanece como evolução e não é requisito de entrega do MVP. |

Para ambas as APIs, o contrato técnico deve documentar autenticação, parâmetros obrigatórios, exemplo de requisição e resposta, códigos de erro, limites de uso e comportamento quando não for possível processar a entrada. No caso de STT, uma transcrição utilizável é o dado de entrada do restante do pipeline. No caso de TTS, a síntese acrescenta uma modalidade de apresentação e não modifica o conteúdo produzido pelo pipeline.

### 8.6.3 O que é buscado nas APIs

Os critérios abaixo orientam a pesquisa e a comparação de serviços de voz. Eles consolidam as necessidades registradas na arquitetura, nos RNFs e nas documentações específicas de STT e TTS.

| Critério | O que deve ser verificado |
|---|---|
| **Português do Brasil** | Reconhecimento de fala em `pt-BR` para STT e disponibilidade de vozes em `pt-BR` para TTS. |
| **Adequação ao fluxo conversacional** | Modos de processamento compatíveis com perguntas e respostas curtas e com o envio ou a reprodução pelo Teams. A Sprint 1 não define uma meta isolada de latência para STT ou TTS; qualquer medição deve separar o tempo do serviço de voz do tempo do pipeline textual previsto no RNF05. |
| **Entrada, saída e limites explícitos** | Formatos, codecs, taxas de amostragem, quantidade de canais, duração ou caracteres máximos, tamanho de requisição, simultaneidade, cotas e formas de entrega devem estar documentados pelo provedor. |
| **Qualidade observável** | Para STT, retorno do texto normalizado e, quando suportado, confiança e alternativas de reconhecimento. Para TTS, possibilidade de validar inteligibilidade, naturalidade e adequação da voz em português. A Sprint 1 não estabelece limiar numérico de acurácia, confiança ou qualidade de síntese. |
| **Integração e portabilidade** | Interface documentada, preferencialmente HTTP, que possa ser encapsulada por um contrato interno e substituída sem alterar o pipeline de PLN. Devem ser conhecidos os métodos de autenticação e os tipos de conteúdo enviados e recebidos. |
| **Aderência tecnológica** | Compatibilidade com o ecossistema Microsoft já utilizado pelo Metrô e possibilidade de homologação no ambiente do parceiro, conforme o RNF08. |
| **Segurança e confidencialidade** | Nenhum dado real ou sensível pode ser enviado a serviço externo não homologado. Credenciais devem ser mantidas fora do código-fonte e a integração não pode contornar permissões definidas para o usuário. |
| **Tratamento de falhas** | Respostas controladas para entrada inválida, formato não suportado, ausência de fala, texto ou SSML inválido, falha de autenticação, limite excedido e indisponibilidade, em concordância com o RNF11. |
| **Custo e sustentabilidade** | Existência de faixa gratuita ou crédito para o desenvolvimento, limites dessa gratuidade e modelo de cobrança previsível após a franquia, sem tratar valores públicos como cotação contratual. |
| **Documentação e validação** | Documentação oficial suficiente para reproduzir chamadas e possibilidade de teste com amostras representativas antes de confirmar qualidade, latência e custo efetivos. |

### 8.6.4 Restrições e condições de validação

- A captura de voz nativa do Teams/Copilot Studio é a primeira opção indicada na Seção 3.4.2.1. A escolha do Azure AI Speech na Seção 8.8 é a recomendação técnica para a integração STT quando o recurso nativo não atender à qualidade ou ao português necessário; o uso no ambiente do parceiro depende de disponibilidade e homologação pela GTI.
- Os benchmarks de STT e TTS das Seções 8.7 e 8.8 são documentais. Não devem ser apresentadas conclusões empíricas de acurácia, naturalidade ou latência antes da existência de amostras padronizadas e representativas do projeto.
- Os limites de 60 segundos e os formatos WAV/PCM e OGG/OPUS descritos na Seção 8.8 pertencem ao endpoint de áudio curto selecionado para STT e não devem ser generalizados como limites de todos os provedores.
- O SSML, o MP3 adotado e o WAV alternativo descritos na Seção 8.9 pertencem ao contrato do endpoint Azure selecionado para TTS e não constituem exigências universais para outros provedores.
- As APIs de voz não devem receber dados reais ou sensíveis em serviço não homologado. Durante a prova de conceito, aplicam-se as exigências de dados sintéticos ou anonimizados do RNF01.
- A trilha prevista no RNF03 continua baseada na solicitação textual, na intenção, nas fontes e na resposta produzida. Este levantamento não cria uma nova obrigação de armazenar gravações ou áudios sintetizados.
- A escolha técnica do Azure AI Speech para TTS na Seção 8.9 permite reutilizar o recurso e a autenticação do STT, mas não antecipa sua implementação: a síntese de fala permanece fora do escopo do MVP, conforme a Seção 3.4.5.

## 8.7 API de recebimento de áudio

Esta seção documenta a API **da própria solução**, que recebe o áudio enviado pelo usuário. Ela não se confunde com a API de transcrição da Seção 8.8: aquela é um serviço de terceiro consumido pelo backend, enquanto esta é o ponto de entrada da aplicação, responsável por validar o arquivo, encaminhá-lo à transcrição e devolver o texto ao pipeline de PLN.

### 8.7.1 Posição no fluxo

O caminho de uma solicitação por voz é o seguinte:

1. o canal envia o áudio à API da aplicação;
2. a API valida formato, duração e tamanho antes de qualquer chamada externa;
3. quando a integração estiver habilitada, o áudio aprovado é encaminhado ao serviço de Speech-to-Text descrito na Seção 8.8;
4. a transcrição retorna à API, que a submete ao pipeline de PLN da Seção 8.10;
5. a resposta segue o mesmo formato das solicitações textuais, conforme o RF08.

A validação anteceder a chamada externa é decisão de projeto, e não detalhe de implementação: cada requisição rejeitada localmente é uma requisição que não consome a franquia gratuita do provedor nem expõe conteúdo a serviço externo.

### 8.7.2 Endpoint

| Operação | Método | Rota | Autenticação |
|---|---|---|---|
| Enviar áudio para transcrição e processamento | `POST` | `/api/audio` | Token do usuário autenticado, conforme o RNF02 |
| Consultar o estado do serviço | `GET` | `/health` | Não requer |

### 8.7.3 Formatos aceitos e limites

Os limites derivam do endpoint de áudio curto do provedor selecionado na Seção 8.8. A API da aplicação rejeita localmente o que o provedor rejeitaria, evitando uma ida à rede para receber erro.

| Restrição | Valor | Origem |
|---|---|---|
| Contêiner e codec | `WAV` com `PCM` ou `OGG` com `OPUS` | Formatos aceitos pelo endpoint de áudio curto |
| Taxa de amostragem | 16 kHz | Configuração adotada na Seção 8.8 |
| Canais | 1, mono | Configuração adotada na Seção 8.8 |
| Duração máxima | 60 segundos | Limite do endpoint de áudio curto |
| Tamanho máximo do arquivo | 2 MB | Decorrente de 60 s a 16 kHz, 16 bits, mono, com margem para cabeçalho |
| Idioma | `pt-BR` | RNF exige atendimento em português do Brasil |
| Requisições simultâneas por usuário | 1 | Evita consumo concorrente da franquia gratuita |

### 8.7.4 Requisição

O envio é `multipart/form-data`, com o arquivo no campo `audio`. O cabeçalho
`Authorization` deve usar o esquema `Bearer`; a ausência do token, um esquema
distinto ou token não reconhecido no mapa de identidades simulado resulta em
`401 Unauthorized`.

```http
POST /api/audio HTTP/1.1
Host: <HOST-DA-APLICACAO>
Authorization: Bearer <TOKEN>
Content-Type: multipart/form-data; boundary=----limite
Content-Length: <TAMANHO>
```

| Campo | Obrigatório | Descrição |
|---|:---:|---|
| `audio` | Sim | Arquivo binário de áudio. A extensão e o `Content-Type` informado no formulário não substituem a validação do conteúdo do arquivo. |
| `conversation_id` | Não | Texto que identifica uma conversa existente. É devolvido sem alteração; se ausente, a API gera um UUID. |
| `language` | Não | Idioma enviado ao Azure Speech-to-Text. O padrão é `pt-BR`. |
| `previous_interaction_id` | Não | Identificador da interação anterior para preservar o contexto lógico do chat. |
| `use_intent_classifier` | Não | Booleano que habilita a classificação local antes da geração; o padrão é `false`. |

Exemplo com cURL:

```bash
curl --request POST \
  --url https://<HOST-DA-APLICACAO>/api/audio \
  --header 'Authorization: Bearer <TOKEN>' \
  --form 'audio=@pergunta.wav;type=audio/wav' \
  --form 'conversation_id=1f5c9a24-1c2e-4a8f-9a3e-2b6d8c0f1a77' \
  --form 'use_intent_classifier=true'
```

### 8.7.5 Resposta de sucesso

`200 OK`. O endpoint valida o arquivo, executa a transcrição e encaminha o
texto reconhecido ao mesmo pipeline de PLN usado por `POST /api/chat`. A
resposta aprovada traz `pipeline_status: "completed"`, intenção estruturada,
entidades extraídas e métricas do percurso de áudio e PLN, mantendo RNF05
rastreável no contrato HTTP e RNF11 com mensagens controladas para entradas sem
rota segura. No exemplo, `chat` omite `intent`, `entities` e `pipeline_metrics`,
que repetem os objetos do nível superior; `answer.sources` também omite os
campos nulos. O contrato completo das referências é descrito a seguir.

```json
{
  "contract_version": "1.1.0",
  "conversation_id": "1f5c9a24-1c2e-4a8f-9a3e-2b6d8c0f1a77",
  "interaction_id": "8b3e0d51-77aa-4c19-9f2b-5e1c7a4d3e90",
  "trace_id": "0d6f2c1e-4b7a-4f0e-9c3d-5a8b7e6f1d20",
  "transcription": {
    "text": "qual e o prazo do projeto XPTO?",
    "confidence": 0.92,
    "duration_seconds": 4.8
  },
  "intent": {
    "macro": "CONSULTA",
    "specific": "consulta_prazo",
    "confidence_macro": 0.98,
    "confidence_specific": 0.86,
    "flow": "consulta_documental",
    "handler": "consultar_prazo",
    "alternatives": [
      { "specific": "consulta_status", "confidence": 0.09 }
    ]
  },
  "entities": [
    {
      "type": "projeto",
      "value": "XPTO",
      "text": "projeto XPTO",
      "start": 17,
      "end": 29,
      "types": ["projeto"],
      "ambiguous": false
    }
  ],
  "pipeline_metrics": {
    "validation_ms": 3,
    "stt_ms": 410,
    "nlp_ms": 8,
    "route_ms": 35,
    "total_ms": 456
  },
  "chat": {
    "contract_version": "1.1.0",
    "text": "O prazo do projeto XPTO e 30/09/2026. [Fonte 1]",
    "model": "gemini-3.7-flash",
    "interaction_id": "8b3e0d51-77aa-4c19-9f2b-5e1c7a4d3e90",
    "trace_id": "0d6f2c1e-4b7a-4f0e-9c3d-5a8b7e6f1d20",
    "latency_ms": 840,
    "retrieval_ms": 12,
    "usage": { "input_tokens": 120, "output_tokens": 34, "thought_tokens": 0, "total_tokens": 154 },
    "evidence_status": "referenced",
    "claims": [
      {
        "text": "O prazo do projeto XPTO e 30/09/2026.",
        "citation_ids": ["Fonte 1"],
        "evidence": [
          { "citation_id": "Fonte 1", "field": "excerpt", "attribute": null, "quote": "O prazo do projeto XPTO e 30/09/2026." }
        ]
      }
    ],
    "recommendation": null,
    "sources": [
      {
        "id": "cronograma-xpto-01",
        "citation_id": "Fonte 1",
        "title": "Cronograma do projeto XPTO",
        "list_name": "base_atendimento",
        "web_url": "https://mock.sharepoint.local/cronograma-xpto-01",
        "artifact_id": null,
        "extract_id": null,
        "project_id": null,
        "source_locator": null,
        "last_modified": "2026-08-26T12:00:00Z",
        "registration_period": null,
        "validity": null,
        "attributes": {},
        "score": 4.2,
        "excerpt": "O prazo do projeto XPTO e 30/09/2026."
      }
    ]
  },
  "answer": {
    "text": "O prazo do projeto XPTO e 30/09/2026. [Fonte 1]",
    "evidence_status": "referenced",
    "claims": [
      {
        "text": "O prazo do projeto XPTO e 30/09/2026.",
        "citation_ids": ["Fonte 1"],
        "evidence": [
          { "citation_id": "Fonte 1", "field": "excerpt", "attribute": null, "quote": "O prazo do projeto XPTO e 30/09/2026." }
        ]
      }
    ],
    "sources": [
      {
        "id": "cronograma-xpto-01",
        "citation_id": "Fonte 1",
        "title": "Cronograma do projeto XPTO",
        "list_name": "base_atendimento",
        "web_url": "https://mock.sharepoint.local/cronograma-xpto-01",
        "last_modified": "2026-08-26T12:00:00Z",
        "score": 4.2,
        "excerpt": "O prazo do projeto XPTO e 30/09/2026.",
        "artifact": "Cronograma do projeto XPTO",
        "section": "base_atendimento"
      }
    ]
  },
  "pipeline_status": "completed"
}
```

| Campo | Tipo | Descrição |
|---|---|---|
| `contract_version` | `string` | Versão do contrato de resposta, comum a texto e áudio (`1.1.0`). |
| `conversation_id` | `string` | Valor recebido no formulário ou UUID gerado pela API se o campo não foi enviado. |
| `interaction_id` | `string` | UUID gerado para a interação. |
| `trace_id` | `string \| null` | Identificador do registro de auditoria (`ai_interactions`), comum a `consulted_sources` e `audit_events`; `null` sem persistência disponível. |
| `transcription.text` | `string` | Texto reconhecido pelo STT e enviado ao pipeline de PLN. |
| `transcription.confidence` | `float` | Confiança retornada pelo provedor de transcrição. |
| `transcription.duration_seconds` | `float` | Duração extraída do arquivo e arredondada para duas casas decimais. |
| `intent` | `object` | Intenção rica derivada da transcrição: `macro`, `specific`, confianças, `flow`, `handler` e `alternatives`. |
| `entities` | `array` | Entidades extraídas da transcrição, com tipo, valor, texto original, posição e ambiguidade. |
| `pipeline_metrics` | `object` | Tempos em milissegundos de validação, STT, PLN, roteamento e fluxo total, usados para acompanhar o RNF05. |
| `chat` | `object` | Resposta textual completa no mesmo contrato de `POST /api/chat`, incluindo `intent`, `entities`, fontes, afirmações verificadas e métricas do pipeline. |
| `answer.text` | `string` | Espelho compatível do texto de resposta usado pelo frontend atual. |
| `answer.evidence_status` | `string` | `referenced` quando cada afirmação reproduz integralmente a fonte citada; `insufficient` na abstenção. |
| `answer.claims` | `array` | Afirmações com as citações e a evidência integral que as sustenta, iguais às de `chat.claims`. |
| `answer.sources` | `array` | Mesmos campos de `chat.sources`, com os aliases legados `artifact` (título) e `section` (localizador ou lista). |
| `pipeline_status` | `string` | `completed` quando validação, STT e pipeline de chat terminam com resposta controlada. |

### 8.7.6 Códigos de resposta e tratamento de erro

O corpo de erro segue estrutura única, para que o canal possa exibir a mensagem sem interpretar cada caso.

```json
{
  "error": {
    "code": "AUDIO_FORMAT_UNSUPPORTED",
    "message": "Formato de áudio não suportado. Envie WAV/PCM ou OGG/OPUS a 16 kHz, mono.",
    "detail": { "received": "audio/mpeg" }
  }
}
```

| Código HTTP | `code` | Situação |
|---|---|---|
| `200 OK` | — | Áudio transcrito e solicitação processada. |
| `400 Bad Request` | `AUDIO_MISSING` | Campo `audio` ausente na requisição. |
| `400 Bad Request` | `AUDIO_FORMAT_UNSUPPORTED` | Contêiner, codec, taxa de amostragem ou número de canais fora do previsto. |
| `400 Bad Request` | `AUDIO_TOO_LONG` | Gravação acima de 60 segundos. |
| `401 Unauthorized` | `UNAUTHENTICATED` | Token ausente, inválido ou expirado. |
| `413 Payload Too Large` | `AUDIO_TOO_LARGE` | Arquivo acima de 2 MB. |
| `422 Unprocessable Entity` | `NO_SPEECH_DETECTED` | Áudio válido, mas sem fala reconhecível. |
| `429 Too Many Requests` | `RATE_LIMITED` | Já existe uma requisição de áudio em processamento para o mesmo usuário. |
| `502 Bad Gateway` | `STT_PROVIDER_ERROR` | Falha na chamada ao serviço de transcrição. |
| `503 Service Unavailable` | `STT_PROVIDER_UNAVAILABLE` | Serviço de transcrição indisponível; aplica-se o fallback da Seção 6.2.5. |
| `502 Bad Gateway` | `PROCESSING_PROVIDER_ERROR` | A transcrição foi concluída, mas o provedor de resposta falhou de forma controlada. |
| `503 Service Unavailable` | `PROCESSING_UNAVAILABLE` | A transcrição foi concluída, mas o pipeline de PLN ou geração está indisponível. |

O código `403 OUT_OF_SCOPE_FOR_PROFILE`, previsto para a autorização por
`access_rules`, ainda não é retornado por esta rota: essa verificação depende
da persistência e será acrescentada em tarefa própria. Os erros do endpoint
usam sempre o envelope acima; o campo opcional `detail` contém somente dados
seguros da própria requisição, como tipo de mídia recebido, duração ou limite
de tamanho, e nunca detalhes internos do servidor.

### 8.7.7 Situação de implementação

O endpoint está implementado em `src/backend/app/main.py` e pode ser consultado
também pela documentação interativa do FastAPI (`/docs`). Ele valida o
`Authorization: Bearer <TOKEN>`, aceita uma solicitação em processamento por
usuário e realiza todas as validações locais antes de qualquer integração
externa. Na prova de conceito, quando a variável `AUDIO_SIMULATED_IDENTITIES`
não é configurada, qualquer token Bearer não vazio identifica o usuário de
forma estável; quando ela é configurada, apenas os tokens mapeados são aceitos.

O upload, a validação, a transcrição, o encaminhamento ao pipeline de PLN e os
retornos de erro desta seção estão concluídos para a prova de conceito. A
autorização de escopo corporativa e a persistência continuam fora desta entrega;
respostas aprovadas retornam `pipeline_status` igual a `completed`.

## 8.8 Speech-to-Text

### 8.8.1 Introdução

Speech-to-Text (STT), ou reconhecimento automático de fala, é a tecnologia responsável por converter a fala presente em um áudio para texto. O serviço recebe um arquivo ou fluxo de áudio, identifica os trechos falados e devolve a transcrição reconhecida. Dependendo da configuração, a resposta também pode incluir pontuação, normalização de números, alternativas de reconhecimento e um índice de confiança.

No projeto, o STT é utilizado como modalidade de entrada do agente. O usuário grava uma pergunta, o áudio é convertido em texto e a transcrição resultante é encaminhada ao pipeline de Processamento de Linguagem Natural. Portanto, a responsabilidade desta etapa é somente reconhecer a fala e produzir o texto da solicitação.

Os requisitos considerados para a escolha da API foram:

- suporte a português do Brasil (`pt-BR`);
- resposta rápida para perguntas curtas;
- disponibilidade de uma faixa gratuita para o desenvolvimento inicial;
- custo previsível após o término da faixa gratuita;
- integração por uma interface HTTP que possa ser substituída por outro provedor;
- retorno estruturado com texto e confiança do reconhecimento.

### 8.8.2 Benchmark das APIs

O benchmark a seguir é documental, baseado nas funcionalidades e nos preços publicados pelos fornecedores em 19 de agosto de 2026. Não foram atribuídas métricas de acurácia ou latência porque ainda não existe um corpus padronizado de áudios do projeto para um teste empírico.

#### Comparação funcional e de custo

| API | `pt-BR` | Modos disponíveis | Custo para desenvolvimento inicial | Custo após a gratuidade | Portabilidade e integração |
|---|---|---|---|---|---|
| **Azure AI Speech** | Sim | Tempo real, áudio curto, transcrição rápida e lote | **5 horas de áudio por mês no nível Free (F0)**. A franquia gratuita é recorrente, mas limitada à transcrição em tempo real e a uma requisição simultânea. | O nível Standard (S0) é cobrado pelo tempo de áudio, em incrementos de segundo. O valor varia por região, moeda e contrato e deve ser consultado na calculadora Azure. | Disponibiliza API REST e SDKs. O endpoint de áudio curto permite uma integração HTTP direta, mas utiliza formatos e autenticação específicos do provedor. |
| **Google Cloud Speech-to-Text V2** | Sim | Síncrono, assíncrono e streaming | A API V2 não apresenta franquia mensal recorrente na tabela vigente; novos clientes podem utilizar créditos promocionais da plataforma. | Reconhecimento padrão: **US$ 0,016 por minuto** até 500 mil minutos/mês. O lote dinâmico custa **US$ 0,003 por minuto**. Armazenamento e outros recursos podem gerar cobranças adicionais. | Oferece REST, gRPC e bibliotecas para diferentes linguagens, com operações síncronas e assíncronas que favorecem diferentes formas de implantação. |
| **Amazon Transcribe** | Sim | Lote e streaming | **60 minutos por mês durante os primeiros 12 meses**, contados a partir da primeira solicitação. A franquia não é permanente. | Cobrança por segundo de áudio, com mínimo de 15 segundos por solicitação e preço dependente da região e da faixa de uso. | Oferece APIs e SDKs, porém usa assinatura AWS nas requisições e, no processamento em lote, depende de arquivos no Amazon S3. |
| **OpenAI Audio API** | Sim | Arquivo e transcrição em tempo real | Não possui franquia recorrente gratuita para uso da API. | Entre os modelos comparados, `gpt-4o-mini-transcribe` tem custo estimado de **US$ 0,003 por minuto**; outros modelos têm preços diferentes. | Possui endpoint REST simples para envio direto de arquivos, o que reduz o acoplamento da integração à infraestrutura de um provedor específico. |

Os valores acima são referências públicas, não cotações. Impostos, câmbio, região, armazenamento, tráfego e condições contratuais podem alterar o custo efetivo.

#### Matriz de decisão com prioridade ao custo inicial

Cada opção recebeu uma nota de 1 (baixa aderência) a 5 (alta aderência). Como o objetivo inicial é desenvolver sem custo, esse critério recebeu o maior peso.

| Critério | Peso |
|---|---:|
| Gratuidade e custo inicial | 35% |
| Suporte funcional a `pt-BR` | 25% |
| Modos de transcrição e adequação a perguntas curtas | 15% |
| Recursos para vocabulário do domínio | 10% |
| Portabilidade e facilidade de integração | 10% |
| Qualidade da documentação | 5% |

| API | Custo 35% | `pt-BR` 25% | Modos 15% | Vocabulário 10% | Portabilidade 10% | Docs 5% | Nota ponderada |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Azure AI Speech** | 5 | 5 | 5 | 4 | 4 | 5 | **4,80** |
| **Amazon Transcribe** | 4 | 5 | 5 | 4 | 3 | 5 | **4,35** |
| **Google Cloud Speech-to-Text V2** | 2 | 5 | 5 | 5 | 5 | 5 | **3,95** |
| **OpenAI Audio API** | 3 | 4 | 4 | 4 | 5 | 4 | **3,75** |

A nota ponderada é calculada por `Σ(nota × peso)`. O Azure AI Speech é a opção recomendada para o desenvolvimento inicial porque oferece a maior franquia gratuita recorrente entre as alternativas avaliadas, suporta `pt-BR` e fornece um endpoint REST adequado às perguntas curtas do projeto.

#### Vencedor sem considerar a gratuidade

Para deixar explícita a decisão técnica além da fase gratuita, a matriz também foi recalculada removendo o critério de custo e normalizando os 65% restantes.

| API | Nota sem o critério de custo |
|---|---:|
| **Google Cloud Speech-to-Text V2** | **5,00** |
| **Azure AI Speech** | **4,69** |
| **Amazon Transcribe** | **4,54** |
| **OpenAI Audio API** | **4,15** |

Sem o critério de custo, o **Google Cloud Speech-to-Text V2 é o vencedor do benchmark documental**, devido à combinação de modalidades de transcrição, adaptação de vocabulário, suporte a `pt-BR` e interfaces REST e gRPC. Esse resultado não substitui uma comparação empírica de acurácia e latência com áudios representativos do projeto.

Para a fase inicial, permanece selecionado o **Azure AI Speech**, pois a orientação do projeto prioriza uma alternativa gratuita e sua franquia recorrente de cinco horas mensais é suficiente para o desenvolvimento. A aplicação deve acessar o serviço por uma interface interna genérica, de modo que o provedor possa ser substituído sem alterar o restante do pipeline.

### 8.8.3 API escolhida: Azure AI Speech

Para o desenvolvimento inicial será utilizada a **API REST do Azure AI Speech para áudio curto**, compatível com o nível Free (F0). Esse endpoint recebe uma gravação de até 60 segundos e retorna o resultado final de forma síncrona, o que atende às perguntas curtas enviadas ao agente.

#### Endpoints relevantes

| Finalidade | Método HTTP | Endpoint | Uso no projeto |
|---|---|---|---|
| Converter áudio curto em texto | `POST` | `https://<NOME-DO-RECURSO>.cognitiveservices.azure.com/stt/speech/recognition/conversation/cognitiveservices/v1` | Endpoint principal do desenvolvimento inicial. |
| Converter áudio curto por host regional | `POST` | `https://<REGIAO>.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1` | Alternativa equivalente quando o ambiente informa a região do recurso. |
| Obter token temporário | `POST` | `https://<NOME-DO-RECURSO>.cognitiveservices.azure.com/sts/v1.0/issueToken` | Opcional; troca a chave do recurso por um token válido por 10 minutos. |
| Transcrever arquivo com a API rápida | `POST` | `https://<NOME-DO-RECURSO>.cognitiveservices.azure.com/speechtotext/transcriptions:transcribe?api-version=2025-10-15` | Disponível no nível Standard (S0) para uma futura ampliação dos limites. |

O endpoint de áudio curto é o único necessário para a funcionalidade atual. O endpoint de token é utilizado somente quando a aplicação opta por não enviar a chave diretamente em cada requisição. A transcrição rápida não está disponível no nível Free (F0), por isso não é adotada no desenvolvimento inicial.

No ambiente de desenvolvimento, a configuração fica em `src/backend/.env`. `AZURE_SPEECH_RESOURCE` guarda o nome do recurso Speech e `AZURE_SPEECH_KEY` guarda a chave usada no cabeçalho `Ocp-Apim-Subscription-Key`. `AZURE_SPEECH_ENDPOINT` é opcional e registra o endpoint exibido no portal Azure; quando ele vier no formato regional `https://<REGIAO>.api.cognitive.microsoft.com/`, a aplicação converte internamente para o host `https://<REGIAO>.stt.speech.microsoft.com`, que é o formato usado pela API de reconhecimento de fala. `AZURE_SPEECH_TIMEOUT_SECONDS` define o limite de espera da chamada ao provedor, com padrão de 6 segundos, e `AZURE_SPEECH_MAX_ATTEMPTS` define quantas tentativas são feitas diante de falha transitória, com padrão de duas. Os dois valores acompanham o orçamento do RNF05, que concede 10 segundos para uma consulta simples ponta a ponta e do qual a transcrição é apenas a primeira etapa.

#### Requisição de transcrição

```http
POST /stt/speech/recognition/conversation/cognitiveservices/v1?language=pt-BR&format=detailed&profanity=masked HTTP/1.1
Host: <NOME-DO-RECURSO>.cognitiveservices.azure.com
Ocp-Apim-Subscription-Key: <CHAVE-DO-RECURSO>
Content-Type: audio/wav; codecs=audio/pcm; samplerate=16000
Accept: application/json

<CONTEÚDO-BINÁRIO-DO-ÁUDIO>
```

##### Parâmetros de consulta

| Parâmetro | Tipo | Obrigatório | Valores | Descrição |
|---|---|---:|---|---|
| `language` | `string` | Sim | `pt-BR` | Idioma falado no áudio. A ausência desse parâmetro resulta em erro HTTP `4xx`. |
| `format` | `string` | Não | `simple` ou `detailed` | Formato da resposta. O padrão é `simple`. O projeto utiliza `detailed` para obter alternativas e confiança. |
| `profanity` | `string` | Não | `masked`, `removed` ou `raw` | Define o tratamento de linguagem ofensiva. O padrão e a configuração adotada são `masked`. |

##### Cabeçalhos

| Cabeçalho | Obrigatório | Descrição |
|---|---:|---|
| `Ocp-Apim-Subscription-Key` | Condicional | Chave do recurso. Deve ser enviado este cabeçalho **ou** `Authorization`, nunca é necessário enviar ambos. |
| `Authorization` | Condicional | Token no formato `Bearer <TOKEN>`, usado como alternativa à chave. |
| `Content-Type` | Sim | Para WAV adotado no projeto: `audio/wav; codecs=audio/pcm; samplerate=16000`. Também é aceito `audio/ogg; codecs=opus`. |
| `Accept` | Recomendado | Deve ser `application/json`. |
| `Transfer-Encoding` | Não | Usar `chunked` quando o áudio for enviado em partes. |
| `Expect` | Condicional | Usar `100-continue` quando houver transferência em partes. |

##### Corpo e limites de entrada

O corpo da requisição contém somente os bytes do áudio; não é enviado JSON. A API aceita:

| Formato | Codec | Taxa de bits | Taxa de amostragem |
|---|---|---:|---|
| WAV | PCM | 256 kbps | 16 kHz, mono |
| OGG | OPUS | 256 kbps | 16 kHz, mono |

O áudio enviado diretamente pode ter no máximo **60 segundos**. Para o projeto, recomenda-se WAV PCM, 16 kHz e mono, pois esse formato é simples de validar e evita incompatibilidades de codec.

##### Exemplo de requisição com cURL

```bash
curl --location --request POST \
  "https://${AZURE_SPEECH_RESOURCE}.cognitiveservices.azure.com/stt/speech/recognition/conversation/cognitiveservices/v1?language=pt-BR&format=detailed&profanity=masked" \
  --header "Ocp-Apim-Subscription-Key: ${AZURE_SPEECH_KEY}" \
  --header "Content-Type: audio/wav; codecs=audio/pcm; samplerate=16000" \
  --header "Accept: application/json" \
  --data-binary "@pergunta.wav"
```

As variáveis `AZURE_SPEECH_RESOURCE` e `AZURE_SPEECH_KEY` devem ser configuradas no ambiente de execução. A chave não deve ser escrita no código-fonte nem versionada no repositório. Quando `AZURE_SPEECH_ENDPOINT` estiver preenchida com o endpoint regional do portal, o exemplo acima continua equivalente: a aplicação deriva a URL final antes de chamar o provedor.

#### Resposta de sucesso

Status HTTP esperado: `200 OK`.

```json
{
  "RecognitionStatus": "Success",
  "Offset": 500000,
  "Duration": 38200000,
  "NBest": [
    {
      "Confidence": 0.93,
      "Lexical": "qual é o avanço do projeto tur zero um",
      "ITN": "qual é o avanço do projeto tur 01",
      "MaskedITN": "qual é o avanço do projeto tur 01",
      "Display": "Qual é o avanço do projeto TUR-01?"
    }
  ]
}
```

O conteúdo é ilustrativo: o texto e a confiança variam conforme o áudio recebido.

##### Campos da resposta detalhada

| Campo | Tipo | Descrição |
|---|---|---|
| `RecognitionStatus` | `string` | Resultado do reconhecimento. `Success` indica que uma transcrição foi produzida. |
| `Offset` | `integer` | Instante de início da fala, em unidades de 100 nanossegundos. |
| `Duration` | `integer` | Duração da fala reconhecida, em unidades de 100 nanossegundos. |
| `NBest` | `array` | Alternativas de reconhecimento ordenadas pelo serviço. |
| `NBest[].Confidence` | `number` | Confiança da alternativa, entre 0 e 1. |
| `NBest[].Lexical` | `string` | Forma lexical, próxima das palavras efetivamente reconhecidas. |
| `NBest[].ITN` | `string` | Texto após normalização inversa, como conversão de números falados para algarismos. |
| `NBest[].MaskedITN` | `string` | Forma normalizada com o filtro de linguagem ofensiva aplicado. |
| `NBest[].Display` | `string` | Texto final com capitalização, pontuação e normalização. Este é o campo encaminhado ao pipeline de PLN. |

Quando `format=simple`, a resposta é reduzida:

```json
{
  "RecognitionStatus": "Success",
  "DisplayText": "Qual é o avanço do projeto TUR-01?",
  "Offset": 500000,
  "Duration": 38200000
}
```

#### Estados e respostas HTTP esperadas

Mesmo com HTTP `200`, `RecognitionStatus` pode indicar que não houve uma transcrição utilizável:

| `RecognitionStatus` | Significado |
|---|---|
| `Success` | Reconhecimento concluído; o texto está presente. |
| `NoMatch` | Houve detecção de fala, mas nenhuma correspondência foi encontrada. |
| `InitialSilenceTimeout` | O áudio começou apenas com silêncio e excedeu o tempo de espera. |
| `BabbleTimeout` | O início continha ruído e o serviço não identificou fala válida. |
| `Error` | O serviço encontrou um erro interno. |

| HTTP | Resposta esperada |
|---:|---|
| `200 OK` | Requisição processada; o corpo contém o objeto JSON de reconhecimento. |
| `400 Bad Request` | `language` ausente ou inválido, idioma sem suporte ou áudio incompatível. |
| `401 Unauthorized` | Chave, token, região ou endpoint inválido. |
| `403 Forbidden` | Cabeçalho de autenticação ausente ou acesso proibido. |

#### Requisição de transcrição rápida no nível Standard

Caso o projeto ultrapasse os limites do desenvolvimento inicial, o Azure AI Speech continua sendo a API escolhida, mas pode utilizar o endpoint de transcrição rápida do nível Standard (S0). Ele aceita um arquivo por requisição e devolve o resultado de forma síncrona.

| Entrada | Local | Tipo | Obrigatório | Descrição |
|---|---|---|---:|---|
| `api-version` | Query string | `string` | Sim | Versão da API. Usar `2025-10-15`. |
| `Ocp-Apim-Subscription-Key` | Cabeçalho | `string` | Sim, quando usada chave | Chave do recurso Azure AI Speech. |
| `audio` | `multipart/form-data` | Arquivo binário | Sim | Arquivo a ser transcrito. |
| `definition` | `multipart/form-data` | JSON serializado | Sim no projeto | Configuração da transcrição; deve informar `{"locales":["pt-BR"]}`. |

```bash
curl --request POST \
  --url "https://${AZURE_SPEECH_RESOURCE}.cognitiveservices.azure.com/speechtotext/transcriptions:transcribe?api-version=2025-10-15" \
  --header "Ocp-Apim-Subscription-Key: ${AZURE_SPEECH_KEY}" \
  --form "audio=@pergunta.wav;type=audio/wav" \
  --form 'definition={"locales":["pt-BR"]}'
```

Resposta esperada: `200 OK`.

```json
{
  "durationMilliseconds": 4320,
  "combinedPhrases": [
    {
      "text": "Qual é o avanço do projeto TUR-01?"
    }
  ],
  "phrases": [
    {
      "offsetMilliseconds": 160,
      "durationMilliseconds": 3820,
      "text": "Qual é o avanço do projeto TUR-01?",
      "locale": "pt-BR",
      "confidence": 0.93
    }
  ]
}
```

#### Requisição opcional de token

Para trocar a chave por um token temporário:

```http
POST /sts/v1.0/issueToken HTTP/1.1
Host: <NOME-DO-RECURSO>.cognitiveservices.azure.com
Ocp-Apim-Subscription-Key: <CHAVE-DO-RECURSO>
Content-Type: application/x-www-form-urlencoded
Content-Length: 0
```

Resposta esperada: `200 OK`, com o token no corpo como texto. O token é válido por 10 minutos e deve ser enviado na transcrição como:

```http
Authorization: Bearer <TOKEN>
```

## 8.9 Text-to-Speech

### 8.9.1 Introdução

Text-to-Speech (TTS), ou síntese de fala, é a tecnologia responsável por converter um texto em um áudio falado. O serviço recebe um texto (eventualmente marcado com SSML — *Speech Synthesis Markup Language*) e devolve um arquivo ou fluxo de áudio com a fala sintetizada, podendo variar a voz, o idioma, a velocidade e a entonação.

No projeto, o TTS é previsto como modalidade de saída do agente: depois que a resposta textual é gerada pelo pipeline de PLN, esse texto é convertido em áudio e devolvido ao usuário. A responsabilidade desta etapa é somente sintetizar a fala a partir de um texto já pronto, de forma simétrica ao papel do STT na entrada.

**Delimitação de escopo.** Esta seção especifica a API a ser utilizada, com benchmark, decisão e contrato técnico, mas a implementação da síntese de fala permanece como evolução, conforme registrado na Seção 3.4.5. O texto continua sendo a resposta canônica do agente; o áudio acrescenta uma modalidade de apresentação, sem alterar o conteúdo fundamentado produzido pelo pipeline.

Os requisitos considerados para a escolha da API foram:

- suporte a português do Brasil (`pt-BR`) com vozes naturais;
- resposta rápida para respostas curtas geradas pelo agente;
- disponibilidade de uma faixa gratuita para o desenvolvimento inicial;
- custo previsível após o término da faixa gratuita;
- integração por uma interface HTTP que possa ser substituída por outro provedor;
- controle básico de prosódia (velocidade, ênfase, pausas) quando necessário;
- formato de áudio compatível com reprodução direta no frontend (ex.: MP3 ou WAV).

### 8.9.2 Benchmark das APIs

O benchmark a seguir é documental, baseado nas funcionalidades e nos preços publicados pelos fornecedores em 27 de agosto de 2026, mantendo os mesmos quatro provedores comparados no benchmark de STT (Seção 8.8.2) para preservar a consistência entre as duas decisões. Não foram atribuídas métricas de naturalidade percebida ou latência porque ainda não existe um corpus padronizado de respostas do agente para um teste empírico.

#### Comparação funcional e de custo

| API | `pt-BR` | Modos disponíveis | Custo para desenvolvimento inicial | Custo após a gratuidade | Portabilidade e integração |
|---|---|---|---|---|---|
| **Azure AI Speech** | Sim, com múltiplas vozes neurais dedicadas (ex.: `pt-BR-FranciscaNeural`, `pt-BR-AntonioNeural`) | Síntese em tempo real via REST/WebSocket, além de lote (*batch*) | **0,5 milhão de caracteres por mês no nível Free (F0)**, no mesmo recurso já provisionado para o STT. | Nível Standard (S0): cobrado por caractere sintetizado; a documentação oficial estima a faixa de **US$ 15 por milhão de caracteres** para vozes neurais, mas o valor exato varia por região e deve ser consultado na calculadora Azure. | Disponibiliza API REST simples (corpo em SSML) e SDKs; usa cabeçalhos e autenticação específicos do provedor, iguais aos já usados no STT. |
| **Google Cloud Text-to-Speech** | Sim, nas vozes Standard, WaveNet, Neural2, Studio e Chirp 3: HD | Síncrono via REST/gRPC | Franquia gratuita recorrente por tipo de voz: **4 milhões de caracteres/mês** (Standard e WaveNet) ou **1 milhão de caracteres/mês** (Neural2, Studio, Chirp 3: HD). | Standard/WaveNet: **US$ 4 por milhão de caracteres**; Neural2: **US$ 16 por milhão**; Chirp 3: HD: **US$ 30 por milhão**; Studio: **US$ 160 por milhão**. | Oferece REST e gRPC, com autenticação via conta de serviço (OAuth2), exigindo mais configuração inicial que uma chave simples. |
| **Amazon Polly** | Sim, com vozes Standard e Neural (ex.: `Camila`, `Vitória`, `Ricardo`) | Síncrono (tempo real) e assíncrono (lote, para Long-Form e Generative) | Standard: **5 milhões de caracteres/mês** (faixa contínua do *Always Free*); Neural: **1 milhão de caracteres/mês nos primeiros 12 meses**. A franquia das vozes neurais não é permanente. | Standard: **US$ 4 por milhão de caracteres**; Neural: **US$ 16 por milhão**; Long-Form: **US$ 100 por milhão**; Generative: **US$ 30 por milhão**. | Oferece APIs e SDKs, mas as requisições usam assinatura AWS (SigV4), o que aumenta o acoplamento à infraestrutura AWS em comparação com uma chamada HTTP direta. |
| **OpenAI Audio API** | Sim, o texto em `pt-BR` é sintetizado pelas vozes multilíngues do provedor (não há vozes dedicadas ao português) | Arquivo (síncrono), com streaming do áudio de saída | Não possui franquia recorrente gratuita para uso da API. | O modelo `gpt-4o-mini-tts` é cobrado por texto de entrada (**~US$ 0,60 por milhão de caracteres**) e áudio de saída (**~US$ 12 por milhão de tokens de áudio**), resultando em uma estimativa da comunidade de desenvolvedores de **~US$ 0,015 por minuto** de áudio gerado — valor não é uma cotação oficial de tabela. | Endpoint REST único (`POST /v1/audio/speech`) e autenticação simples por chave de API, o que reduz o acoplamento da integração a um provedor específico. |

Os valores acima são referências públicas, não cotações. Impostos, câmbio, região, armazenamento, tráfego e condições contratuais podem alterar o custo efetivo.

#### Matriz de decisão com prioridade ao custo inicial

Cada opção recebeu uma nota de 1 (baixa aderência) a 5 (alta aderência), com os mesmos pesos usados no benchmark de STT, trocando o critério "recursos para vocabulário do domínio" por "controle de prosódia e customização", mais relevante para síntese de fala.

| Critério | Peso |
|---|---:|
| Gratuidade e custo inicial | 35% |
| Suporte funcional a `pt-BR` | 25% |
| Modos de síntese e adequação a respostas curtas | 15% |
| Controle de prosódia e customização (SSML, léxico) | 10% |
| Portabilidade e facilidade de integração | 10% |
| Qualidade da documentação | 5% |

| API | Custo 35% | `pt-BR` 25% | Modos 15% | Controle 10% | Portabilidade 10% | Docs 5% | Nota ponderada |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Google Cloud Text-to-Speech** | 5 | 5 | 5 | 5 | 4 | 5 | **4,90** |
| **Azure AI Speech** | 4 | 5 | 5 | 5 | 5 | 5 | **4,65** |
| **Amazon Polly** | 4 | 5 | 4 | 4 | 3 | 5 | **4,20** |
| **OpenAI Audio API** | 1 | 3 | 4 | 3 | 5 | 4 | **2,70** |

A nota ponderada é calculada por `Σ(nota × peso)`. Diferente do benchmark de STT, o Google Cloud Text-to-Speech obtém a maior nota ponderada, por oferecer a maior franquia gratuita recorrente entre as alternativas e suporte completo a `pt-BR` em várias camadas de qualidade de voz.

#### Vencedor sem considerar a gratuidade

Recalculando a matriz sem o critério de custo e normalizando os 65% restantes, como feito no benchmark de STT:

| API | Nota sem o critério de custo |
|---|---:|
| **Azure AI Speech** | **5,00** |
| **Google Cloud Text-to-Speech** | **4,85** |
| **Amazon Polly** | **3,92** |
| **OpenAI Audio API** | **3,54** |

Sem o critério de custo, o **Azure AI Speech** se destaca por combinar controle fino de prosódia via SSML, portabilidade equivalente à das demais opções e a maior variedade de vozes neurais dedicadas ao `pt-BR` entre os provedores avaliados.

#### Decisão

Apesar de o Google Cloud Text-to-Speech obter a maior nota ponderada, a fase inicial do projeto adota o **Azure AI Speech** pelos mesmos motivos estratégicos que levaram à escolha do STT (Seção 8.8.2): a franquia de 0,5 milhão de caracteres por mês é suficiente para o desenvolvimento e os testes do agente, e — mais importante — **o TTS pode reutilizar o mesmo recurso Azure (mesma chave `AZURE_SPEECH_KEY`, mesma região e o mesmo padrão de autenticação)** já provisionado para o STT, evitando manter credenciais, contas e integrações de dois provedores diferentes para voz de entrada e de saída. Assim como no STT, a aplicação deve acessar o serviço por uma interface interna genérica, de modo que o provedor possa ser substituído (por exemplo, pelo Google Cloud TTS) sem alterar o restante do pipeline, caso a franquia gratuita se torne insuficiente.

### 8.9.3 API escolhida: Azure AI Speech

Para o desenvolvimento inicial será utilizada a **API REST do Azure AI Speech para síntese de voz**, compatível com o nível Free (F0) e com o mesmo recurso Azure já usado no STT.

#### Endpoints relevantes

| Finalidade | Método HTTP | Endpoint | Uso no projeto |
|---|---|---|---|
| Sintetizar fala a partir de texto/SSML | `POST` | `https://<REGIAO>.tts.speech.microsoft.com/cognitiveservices/v1` | Endpoint principal do desenvolvimento inicial. |
| Obter token temporário | `POST` | `https://<NOME-DO-RECURSO>.cognitiveservices.azure.com/sts/v1.0/issueToken` | Opcional; o mesmo endpoint de token já documentado para o STT (Seção 8.8.3) também vale para o TTS. |

O endpoint de síntese aceita até **10 minutos de áudio por requisição**, muito acima do necessário para respostas curtas do agente.

#### Requisição de síntese

```http
POST /cognitiveservices/v1 HTTP/1.1
Host: <REGIAO>.tts.speech.microsoft.com
Ocp-Apim-Subscription-Key: <CHAVE-DO-RECURSO>
Content-Type: application/ssml+xml
X-Microsoft-OutputFormat: audio-24khz-48kbitrate-mono-mp3
User-Agent: agente-metro-portfolio

<speak version='1.0' xml:lang='pt-BR'>
  <voice xml:lang='pt-BR' xml:gender='Female' name='pt-BR-FranciscaNeural'>
    O projeto TUR-01 está com setenta e cinco por cento de avanço.
  </voice>
</speak>
```

##### Cabeçalhos

| Cabeçalho | Obrigatório | Descrição |
|---|---:|---|
| `Ocp-Apim-Subscription-Key` | Condicional | Chave do recurso. Deve ser enviado este cabeçalho **ou** `Authorization`, nunca é necessário enviar ambos — igual ao STT. |
| `Authorization` | Condicional | Token no formato `Bearer <TOKEN>`, obtido no endpoint `/sts/v1.0/issueToken`. |
| `Content-Type` | Sim | Deve ser `application/ssml+xml`; o corpo é sempre SSML para vozes pré-construídas. |
| `X-Microsoft-OutputFormat` | Sim | Formato do áudio de saída. O projeto adota `audio-24khz-48kbitrate-mono-mp3` por gerar um arquivo compacto, adequado para tocar diretamente no frontend; `riff-24khz-16bit-mono-pcm` (WAV) é a alternativa caso seja necessário processamento adicional do áudio sem perdas. |
| `User-Agent` | Sim | Identificador da aplicação, com até 255 caracteres. |

##### Corpo da requisição (SSML)

O corpo contém um documento SSML válido: a tag `<voice>` define a voz utilizada (nome, idioma e gênero) e envolve o texto a ser sintetizado. Caracteres especiais de XML presentes na resposta do agente (`&`, `<`, `>`, `"`, `'`) precisam ser escapados antes de montar o SSML.

##### Exemplo de requisição com cURL

```bash
curl --location --request POST \
  "https://${AZURE_SPEECH_REGION}.tts.speech.microsoft.com/cognitiveservices/v1" \
  --header "Ocp-Apim-Subscription-Key: ${AZURE_SPEECH_KEY}" \
  --header "Content-Type: application/ssml+xml" \
  --header "X-Microsoft-OutputFormat: audio-24khz-48kbitrate-mono-mp3" \
  --header "User-Agent: agente-metro-portfolio" \
  --data "<speak version='1.0' xml:lang='pt-BR'><voice xml:lang='pt-BR' name='pt-BR-FranciscaNeural'>O projeto TUR-01 está com setenta e cinco por cento de avanço.</voice></speak>" \
  --output resposta.mp3
```

As variáveis `AZURE_SPEECH_REGION` e `AZURE_SPEECH_KEY` devem ser configuradas no ambiente de execução, reaproveitando o mesmo recurso do STT. A chave não deve ser escrita no código-fonte nem versionada no repositório.

#### Resposta de sucesso

Status HTTP esperado: `200 OK`. O corpo da resposta não é JSON: são os **bytes brutos do áudio**, no formato indicado por `X-Microsoft-OutputFormat`, com o `Content-Type` correspondente (ex.: `audio/mpeg` para MP3 ou `audio/wav` para PCM/WAV). O áudio deve ser encaminhado como está para o frontend, que o reproduz diretamente (ex.: elemento `<audio>` ou Web Audio API).

#### Estados e respostas HTTP esperadas

| HTTP | Resposta esperada |
|---:|---|
| `200 OK` | Requisição processada; o corpo contém os bytes do áudio sintetizado. |
| `400 Bad Request` | SSML malformado, parâmetro ausente/inválido ou cabeçalho malformado. |
| `401 Unauthorized` | Chave, token ou região inválidos. |
| `415 Unsupported Media Type` | `Content-Type` diferente de `application/ssml+xml`. |
| `429 Too Many Requests` | Limite de taxa excedido — no nível Free (F0), o limite é de 20 requisições a cada 60 segundos. |
| `502 Bad Gateway` / `503 Service Unavailable` | Erro de rede ou indisponibilidade momentânea do serviço. |

#### Limites relevantes

| Limite | Free (F0) | Standard (S0) |
|---|---|---|
| Requisições de síntese em tempo real | 20 a cada 60 segundos | 30 TPS por padrão (ajustável até 1.000 TPS) |
| Duração máxima de áudio por requisição | 10 minutos | 10 minutos |
| Tamanho máximo da mensagem SSML por conexão | 64 KB | 64 KB |
| Tags `<voice>`/`<audio>` distintas por SSML | 50 | 50 |

#### Requisição opcional de token

Idêntica à já documentada para o STT (Seção 8.8.3): trocar a chave por um token Bearer válido por 10 minutos, usando o mesmo endpoint `/sts/v1.0/issueToken` do mesmo recurso Azure.

### 8.9.4 Referências

- Microsoft. [Preços do Azure AI Speech](https://azure.microsoft.com/en-us/pricing/details/speech/). Acesso em: 27 ago. 2026.
- Microsoft. [Quotas e limites do Azure AI Speech](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-quotas-and-limits). Acesso em: 27 ago. 2026.
- Microsoft. [API REST de conversão de texto em fala](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech). Acesso em: 27 ago. 2026.
- Microsoft. [Lista de vozes e idiomas suportados (Speech)](https://learn.microsoft.com/pt-br/azure/ai-services/speech-service/language-support?tabs=tts). Acesso em: 27 ago. 2026.
- Google. [Preços do Text-to-Speech](https://cloud.google.com/text-to-speech/pricing). Acesso em: 27 ago. 2026.
- Amazon Web Services. [Preços do Amazon Polly](https://aws.amazon.com/polly/pricing/). Acesso em: 27 ago. 2026.
- OpenAI. [Guia da API de Text-to-Speech](https://platform.openai.com/docs/guides/text-to-speech). Acesso em: 27 ago. 2026.
- OpenAI. [Preços da API](https://platform.openai.com/docs/pricing). Acesso em: 27 ago. 2026.


## 8.10 Escolha de algoritmo PLN

Esta seção registra a escolha atual do pipeline de Processamento de Linguagem Natural responsável por classificar a solicitação do usuário. A implementação e o benchmark reproduzível estão no notebook [`classificador_intencoes_metro.ipynb`](../src/notebooks/classificador_intencoes_metro.ipynb).

Embora seja referido de forma abreviada como “modelo híbrido”, o componente é tecnicamente um pipeline: a representação híbrida — TF-IDF de palavras e de caracteres reduzidos por SVD, Word2Vec treinado no corpus do projeto e embeddings BERT congelados — gera os atributos de entrada, e classificadores lineares realizam a previsão em dois níveis, macrointenção e intenção específica.

Esta seção trata da **escolha**: como as alternativas foram comparadas, qual venceu e o que a medição sustenta. A **implementação** dessa escolha no serviço — módulos, dependências de execução, exemplos de entrada e saída e testes automatizados — está na Seção 8.11. A Seção 8.10.6 registra o que a implementação confirmou e o que ela mudou na decisão original.

### 8.10.1 Objetivo e protocolo de avaliação

O classificador organiza os pedidos em quatro macrointenções (`CONSULTA`, `TRANSACAO`, `ALERTA` e `FORA_DE_ESCOPO`) e 31 intenções específicas. A macrointenção determina o fluxo geral do agente, enquanto a intenção específica identifica o handler mais adequado.

O conjunto possui 5.353 exemplos, separados em 3.062 para treino, 1.156 para validação e 1.135 para teste. A separação é agrupada por `template_id`: variações geradas a partir do mesmo template permanecem no mesmo conjunto. Esse cuidado reduz o vazamento que ocorreria se frases quase equivalentes fossem distribuídas aleatoriamente entre treino e teste. Os vetorizadores, escaladores, Word2Vec e demais transformadores são ajustados somente com os dados de treino.

A seleção segue três etapas:

1. escolha do pré-processamento por validação cruzada agrupada somente sobre o treino;
2. comparação das representações e classificadores no conjunto de validação, usando como critério principal o F1-macro da intenção específica;
3. avaliação do pipeline escolhido no teste, que não participa da seleção.

### 8.10.2 Benchmark e decisão

O notebook compara TF-IDF de palavras, TF-IDF de caracteres, Word2Vec, embeddings BERT congelados e três combinações híbridas, cada uma com regressão logística e LinearSVC — quatorze combinações no total. A tabela é produzida pelo próprio script e ordenada pelo F1-macro de intenção na validação, de modo que a escolha não é definida previamente por preferência tecnológica.

Esta é a tabela da execução de referência, na íntegra:

| # | Representação | Classificador | Acc. intenção | **F1-macro intenção** | Acc. macro | F1-macro macro |
| :-: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | **Híbrido completo** | **LogReg** | 0,5415 | **0,5425** | 0,8036 | 0,8280 |
| 2 | Híbrido W2V+BERT | LogReg | 0,5355 | 0,5332 | 0,8529 | 0,8486 |
| 3 | BERT congelado | LogReg | 0,4905 | 0,4966 | 0,8391 | 0,8543 |
| 4 | TF-IDF caracteres | LinearSVC | 0,4801 | 0,4878 | 0,7370 | 0,7543 |
| 5 | TF-IDF caracteres | LogReg | 0,4784 | 0,4792 | 0,7517 | 0,7703 |
| 6 | Híbrido completo | LinearSVC | 0,4645 | 0,4745 | 0,6964 | 0,6887 |
| 7 | Híbrido W2V+BERT | LinearSVC | 0,4749 | 0,4670 | 0,7353 | 0,7396 |
| 8 | TF-IDF palavras | LinearSVC | 0,4628 | 0,4652 | 0,7673 | 0,7721 |
| 9 | BERT congelado | LinearSVC | 0,4567 | 0,4576 | 0,7656 | 0,7122 |
| 10 | TF-IDF palavras | LogReg | 0,4394 | 0,4535 | 0,7292 | 0,7373 |
| 11 | Híbrido lexical (palavras+chars) | LinearSVC | 0,4325 | 0,4421 | 0,6678 | 0,6786 |
| 12 | Híbrido lexical (palavras+chars) | LogReg | 0,4291 | 0,4348 | 0,6877 | 0,6883 |
| 13 | Word2Vec | LogReg | 0,4040 | 0,4052 | 0,7154 | 0,7087 |
| 14 | Word2Vec | LinearSVC | 0,3469 | 0,3613 | 0,6462 | 0,6534 |

A alternativa vencedora foi o **Híbrido completo** com regressão logística, que concatena quatro blocos de atributos: TF-IDF de palavras e de caracteres reduzidos por SVD, o Word2Vec treinado no corpus do projeto e os embeddings BERT congelados.

A tabela sustenta três leituras que não eram evidentes antes de medir.

**Nenhum bloco isolado vence.** O Word2Vec sozinho é a pior alternativa da tabela (0,4052), e ainda assim sua presença separa o primeiro colocado do segundo. O BERT congelado sozinho fica em terceiro (0,4966), acima de qualquer representação puramente lexical. A combinação supera cada parte porque os sinais são complementares: o lexical captura a forma escrita, incluindo abreviação e erro de digitação; o BERT aproxima formulações diferentes com significado semelhante.

**A margem sobre o segundo colocado é estreita.** O Híbrido completo supera o Híbrido W2V+BERT por 0,0093 de F1-macro — diferença pequena o bastante para não sustentar afirmação de superioridade robusta. O que a tabela autoriza dizer é que o vencedor é uma combinação híbrida, e não qual delas em definitivo. Vale notar que o segundo colocado tem F1-macro de macrointenção superior ao do primeiro (0,8486 contra 0,8280), o que reforça a leitura de empate técnico no nível macro.

**A regressão logística supera o LinearSVC em quase toda a tabela.** A exceção é o TF-IDF de caracteres, onde o LinearSVC fica marginalmente à frente. Como o roteamento depende de confiança calibrada para aplicar limiares — e não apenas do rótulo previsto —, a saída probabilística da regressão logística é também a que serve ao RF07.

Em seguida, o script compara as duas arquiteturas usando a representação vencedora:

| Arquitetura | Acc. intenção | F1-macro intenção | Acc. macro | F1-macro macro |
| --- | ---: | ---: | ---: | ---: |
| Plana (31 classes) | 0,5415 | 0,5425 | 0,8036 | 0,8280 |
| **Hierárquica (macro → específica)** | **0,6306** | **0,6282** | **0,9196** | **0,9037** |

O ganho da arquitetura hierárquica é substancial e maior que qualquer diferença entre representações: 0,0857 de F1-macro na intenção específica. A explicação é estrutural — prever primeiro a macrointenção e depois acionar um especialista treinado apenas com as intenções daquele grupo reduz o número de classes concorrentes na segunda etapa, e alinha o modelo ao roteamento que o agente de fato executa.

### 8.10.3 Configuração e resultados atuais

A configuração selecionada na execução de referência foi:

| Elemento | Valor selecionado |
|---|---|
| Pré-processamento | `config_22` |
| Caixa | conversão para minúsculas |
| Tokenizador | expressão regular `[^\W_]+` |
| Stopwords | preservadas |
| Pontuação | removida |
| Morfologia | stemming Snowball em português |
| Representação | Híbrido completo (TF-IDF palavras + TF-IDF caracteres + Word2Vec + BERT congelado) |
| Arquitetura | hierárquica |
| Classificador | regressão logística |
| Hiperparâmetros | `C=0.5`; `class_weight=balanced` |
| Limiar de macrointenção | 0,550 |
| Limiar de intenção específica | 0,700 |

A `config_22` foi escolhida por validação cruzada agrupada sobre o treino, entre 72 combinações avaliadas, com F1-macro de 0,3532. A preservação de stopwords é relevante porque palavras como "qual", "quando", "quanto" e "quem" carregam informação útil para distinguir solicitações — e a grade confirma o efeito: as quatro melhores médias por família de configuração mantêm stopwords, e as quatro piores as removem.

Os limiares não foram arbitrados: são calibrados na validação por um procedimento que busca a maior cobertura compatível com uma acurácia-alvo entre os pedidos aceitos. O de macrointenção mirava 97% de acerto e chegou a 93,2% com 97,4% de cobertura — a meta **não** foi atingida, e isso está registrado na saída do notebook. O de intenção específica mirava 80% e atingiu 80,7%, com cobertura de 57,7%.

| Conjunto | Acurácia da intenção | F1-macro da intenção | Acurácia da macro | F1-macro da macro |
|---|---:|---:|---:|---:|
| Validação | 0,6332 | 0,6270 | 0,9135 | 0,9115 |
| Teste | **0,7383** | **0,7401** | **0,9551** | **0,9477** |

Os resultados indicam que o primeiro nível está mais maduro: no teste, a macrointenção atingiu F1-macro de 0,9477, enquanto a intenção específica atingiu 0,7401. O pipeline já apresenta sinal forte para o roteamento geral, mas desempenho moderado na escolha do handler específico.

O desempenho por macrointenção no teste é homogêneo, com precisão entre 0,932 e 1,000:

| Macrointenção | Precisão | Recall | F1 | Suporte |
|---|---:|---:|---:|---:|
| ALERTA | 1,000 | 0,946 | 0,972 | 202 |
| CONSULTA | 0,940 | 0,963 | 0,952 | 492 |
| FORA_DE_ESCOPO | 0,932 | 0,891 | 0,911 | 46 |
| TRANSACAO | 0,955 | 0,957 | 0,956 | 395 |

**Aderência ao RNF06.** O requisito exige F1-macro igual ou superior a 0,80 na classificação de intenções. No nível de macrointenção o critério é atendido com folga (0,9477). No nível de intenção específica, **não é**: 0,7401 está abaixo do limiar exigido. É por isso que o limiar de confiança existe — ele converte a incerteza em fluxo genérico em vez de handler errado. Fechar essa lacuna é trabalho da Sprint 3.

**Efeito prático dos limiares no teste.** Aplicando 0,550 e 0,700 aos 1.135 pedidos do conjunto de teste:

- 14 pedidos (1,2%) ficam abaixo do limiar de macrointenção e recebem a resposta de limitação;
- 305 pedidos (26,9%) são roteados pela macrointenção mas tratados pelo fluxo genérico, sem acionar um handler específico de baixa confiança;
- entre os aceitos, a acurácia sobe de 0,7383 para 0,8775 na intenção específica e para 0,9634 na macrointenção.

Esse é o comportamento conservador exigido pelo RNF04 e pelo RNF11: o custo de 26,9% de cobertura reduzida no handler específico compra um ganho de quase 14 pontos de acurácia entre as decisões efetivamente tomadas.

A execução de referência gerou o classificador serializado (13.472 KB), o modelo Word2Vec (922 KB), o catálogo de intenções, o conjunto de dados e o arquivo de métricas. Dois componentes **não** estão embutidos no arquivo `joblib` e devem ser carregados separadamente pelo ambiente de inferência: o encoder BERT pré-treinado e o modelo Word2Vec. O `joblib` guarda os vetorizadores TF-IDF, as reduções SVD, os escaladores ajustados, o classificador hierárquico, os limiares e o mapa de intenção para macrointenção.

### 8.10.4 Bibliotecas, configuração e exemplos de código

O pipeline é implementado em Python no notebook [`src/notebooks/classificador_intencoes_metro.ipynb`](../src/notebooks/classificador_intencoes_metro.ipynb), e os artefatos da execução de referência estão em `src/notebooks/artefatos/`.

**Bibliotecas utilizadas no treinamento e no benchmark**

| Biblioteca | Papel no pipeline |
|---|---|
| `scikit-learn` | Vetorização TF-IDF, redução por SVD, normalização, regressão logística, LinearSVC, busca de hiperparâmetros com `PredefinedSplit` e métricas |
| `gensim` | Treinamento do Word2Vec sobre o corpus do projeto |
| `sentence-transformers` | Extração dos embeddings BERT congelados |
| `transformers` e `torch` | Alternativa de extração de embeddings quando o `sentence-transformers` não está disponível |
| `nltk` | Stemming Snowball em português e listas de stopwords |
| `pandas` e `numpy` | Manipulação do conjunto de dados e das matrizes de atributos |
| `scipy` | Empilhamento de matrizes esparsas na composição das representações híbridas |
| `joblib` | Serialização do classificador e dos transformadores ajustados |

O ambiente de **inferência** reaproveita parte dessa lista. O encoder do bloco
BERTimbau é carregado por `torch` e `transformers` (`AutoModel`/`AutoTokenizer`
de `neuralmind/bert-base-portuguese-cased`), com os embeddings congelados
concatenados aos vetores TF-IDF antes da decisão do classificador hierárquico.
Essas dependências ficam separadas em `requirements-pln.txt`; sem elas, a
classificação de intenção fica indisponível. As dependências efetivamente
instaladas no backend estão na Seção 8.11.2.

**Passos de configuração**

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install scikit-learn gensim sentence-transformers torch nltk pandas numpy scipy joblib
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
jupyter notebook src/notebooks/classificador_intencoes_metro.ipynb
```

A semente é fixada em todas as etapas que envolvem aleatoriedade, de modo que a execução seja reproduzível.

**Treinamento do Word2Vec sobre o corpus do projeto**

O modelo é treinado **somente com o conjunto de treino**, para que nenhuma informação de validação ou teste vaze para a representação.

```python
W2V_DIM = 200

w2v = Word2Vec(
    sentences=tokens_treino,   # apenas o split de treino
    vector_size=W2V_DIM,
    window=5,
    min_count=1,
    sg=1,                      # skip-gram
    negative=10,
    epochs=60,
    workers=2,
    seed=SEED,
)
```

**Embeddings BERT congelados**

O encoder é utilizado como extrator, sem ajuste supervisionado, e recebe o texto cru — o stemming aplicado às demais representações não é usado aqui, porque o BERT tem tokenizador próprio.

```python
MODELO_BERT = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def embeddings_sentence_transformers(textos, modelo):
    return modelo.encode(
        list(textos),
        batch_size=64,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
```

**Arquitetura hierárquica**

A primeira etapa prevê a macrointenção; a segunda usa um especialista treinado apenas com as intenções daquele grupo, reduzindo o número de classes concorrentes.

```python
class ClassificadorHierarquico:
    """Etapa 1: macrointenção. Etapa 2: especialista da macro predita."""

    def __init__(self, fabrica=novo_clf):
        self.fabrica = fabrica
        self.macro_clf = None
        self.especialistas = {}

    def fit(self, X, y_macro, y_int):
        self.macro_clf = self.fabrica()
        self.macro_clf.fit(X, y_macro)
        for macro in np.unique(y_macro):
            mask = y_macro == macro
            self.especialistas[macro] = self.fabrica().fit(X[mask], y_int[mask])
        return self
```

**Seleção de hiperparâmetros sem vazamento**

A busca usa `PredefinedSplit`, que força o ajuste no treino e a avaliação na validação, em vez de embaralhar os dois.

```python
test_fold = np.concatenate([
    -np.ones(len(y_treino_int), dtype=int),   # treino: nunca avaliado
    np.zeros(len(y_val_int), dtype=int),      # validação: sempre avaliada
])

busca = GridSearchCV(
    LogisticRegression(max_iter=4000, random_state=SEED),
    {"C": [0.5, 1.0, 2.0, 5.0, 10.0, 20.0], "class_weight": [None, "balanced"]},
    scoring="f1_macro", cv=PredefinedSplit(test_fold), n_jobs=-1, refit=False,
)
```

**Exemplo de entrada e saída da inferência**

A vetorização de inferência reaplica exatamente as transformações ajustadas no treino, o que evita divergência entre o que o modelo viu e o que recebe em produção.

```python
def vetorizar(textos):
    """Aplica exatamente as mesmas transformações ajustadas no treino."""
    toks = [preprocess_text(t, **MELHOR_CONFIG) for t in textos]
    partes = [SCALERS[n].transform(bloco(n, textos, toks)) for n in REP_BLOCOS[MELHOR_REP]]
    return np.hstack(partes)

modelo = joblib.load("artefatos/classificador_intencoes.joblib")
X = vetorizar(["qual o prazo do projeto de modernização da linha 1"])
print(modelo.predict_proba(X).max(), modelo.predict(X))
```

Saída real da execução de referência, reproduzida do notebook:

```text
[CONSULTA       1.00] quanto já foi gasto na obra da Linha 6?
    -> handler:consulta_orcamento_custo (conf. intenção = 1.00)
       alternativas: [('consulta_orcamento_custo', 0.9978), ('consulta_visao_portfolio', 0.0006), ...]

[ALERTA         1.00] me avisa se o projeto de sinalização atrasar mais de uma semana
    -> handler:alerta_prazo_atraso (conf. intenção = 1.00)
       alternativas: [('alerta_prazo_atraso', 0.9999), ('alerta_gerenciar_inscricao', 0.0001), ...]

[CONSULTA       0.74] prorroga o prazo do PRJ-0442 até março
    -> handler:consulta_cronograma_prazo (conf. intenção = 0.73)
       alternativas: [('consulta_cronograma_prazo', 0.7321), ('transacao_atualizar_cronograma', 0.1417), ...]

[TRANSACAO      1.00] gera um relatório executivo do subportfólio de modernização
    -> handler:transacao_gerar_relatorio (conf. intenção = 1.00)

[FORA_DE_ESCOPO 1.00] bom dia, tudo certo?
    -> fluxo genérico
```

| Entrada | Macrointenção | Intenção específica | Confiança | Encaminhamento |
|---|---|---|---:|---|
| "quanto já foi gasto na obra da Linha 6?" | `CONSULTA` | `consulta_orcamento_custo` | 1,00 | Rota de consulta com RAG |
| "me avisa se o projeto de sinalização atrasar mais de uma semana" | `ALERTA` | `alerta_prazo_atraso` | 1,00 | Fluxo de alerta |
| "gera um relatório executivo do subportfólio de modernização" | `TRANSACAO` | `transacao_gerar_relatorio` | 1,00 | Workflow guiado no frontend com execução pelo backend/Power Automate |
| "compare a execução orçamentária da Linha 2 com a da Linha 15" | `CONSULTA` | `comparacao_entre_projetos` | 0,98 | Rota de comparação com RAG |
| "bom dia, tudo certo?" | `FORA_DE_ESCOPO` | — | 1,00 | Resposta de limitação, registrada em `out_of_scope_requests` |
| "prorroga o prazo do PRJ-0442 até março" | `CONSULTA` | `consulta_cronograma_prazo` | 0,73 | Acima do limiar de 0,700, mas é um **erro de classificação** |

O último caso merece registro porque é um erro real, e não um exemplo escolhido para ilustrar sucesso. "Prorroga o prazo" é um pedido de alteração — deveria ser `TRANSACAO` / `transacao_atualizar_cronograma`, que aparece como segunda alternativa com 0,1417. O modelo classificou como consulta de cronograma com 0,73 de confiança, acima do limiar de 0,700, de modo que o handler **seria acionado**. É exatamente o tipo de confusão que o F1-macro de 0,7401 na intenção específica resume, e a razão pela qual a Seção 8.10.5 trata a validação com solicitações reais como pré-requisito, e não como refinamento.

### 8.10.5 Limitações e próximos passos

Os números atuais devem ser interpretados com as seguintes ressalvas:

- os prompts são majoritariamente sintéticos e derivados de templates; o agrupamento por `template_id` reduz o vazamento entre variações, mas não substitui uma avaliação externa com solicitações reais;
- o vocabulário do corpus é pequeno — 577 termos no TF-IDF ajustado só com o treino —, e o Word2Vec treinado sobre 3.062 exemplos herda esse limite, com 6,2% de tokens fora do vocabulário no teste;
- o BERT é usado como extrator de embeddings congelado, sem ajuste supervisionado para as intenções do projeto; o notebook prevê o fine-tuning do BERTimbau, mas a célula permanece desativada por exigir GPU;
- a vantagem do Híbrido completo sobre o Híbrido W2V+BERT é de 0,0093 de F1-macro, insuficiente para afirmar superioridade robusta entre as duas combinações;
- o F1-macro de 0,7401 na intenção específica **não atende** ao mínimo de 0,80 exigido pelo RNF06; apenas o nível de macrointenção atende;
- o limiar de macrointenção não alcançou o alvo de 97% de acurácia entre os aceitos, ficando em 93,2%;
- os limiares priorizam segurança e custam cobertura: 26,9% dos pedidos do teste são tratados pelo fluxo genérico em vez de um handler específico;
- o desempenho agregado oculta intenções individuais fracas — `analise_tendencia_desempenho`, por exemplo, tem F1 de 0,299 no teste, e `alerta_estouro_orcamento` tem recall de 0,548 apesar de precisão 1,000;
- a inferência depende do carregamento coordenado de três artefatos — o `joblib`, o Word2Vec e o encoder BERT —, aspecto formalizado na Sprint 3 em `src/backend/app/nlp/inference.py` e descrito na Seção 8.11.4.

Como próximos passos, o grupo deve coletar solicitações reais com usuários do domínio, manter um conjunto externo de teste, revisar as classes com maior confusão — em especial a fronteira entre consulta e transação evidenciada no exemplo de erro da Seção 8.10.4 —, avaliar o fine-tuning do BERTimbau e medir cobertura e acurácia após a aplicação dos limiares. Até essa validação, o híbrido completo deve ser entendido como o **vencedor do benchmark atual** e a escolha do grupo para o MVP, não como um modelo validado para produção.

**Reprodutibilidade.** Os resultados desta seção vêm de uma execução completa do notebook, cujas saídas estão versionadas nas células do próprio arquivo. A semente é fixada em todas as etapas com aleatoriedade. O ambiente da execução de referência usou Python 3.9, scikit-learn 1.6.1, gensim 4.4.0, torch 2.8.0 e sentence-transformers 5.1.2. Quando `gensim` ou `torch` não estão disponíveis, o notebook degrada silenciosamente: as representações que dependem deles são removidas da comparação e o benchmark elege um vencedor entre as restantes. Uma execução nessas condições produz números diferentes dos registrados aqui, e a tabela da Seção 8.10.2 deixa de conter as linhas de Word2Vec, BERT e híbridos.

A célula do Word2Vec emite em `stderr` a linha `Exception ignored in: 'gensim.models.word2vec_inner.our_dot_float'`. É um aviso conhecido da rotina compilada do `gensim` em combinação com a versão do NumPy do ambiente, e não interrompe o treinamento: o vocabulário é construído com os 577 termos do treino e os vetores são gerados nas dimensões esperadas, conforme a saída da própria célula. O aviso está preservado na execução versionada em vez de suprimido, para que o registro corresponda ao que a execução produziu.

### 8.10.6 Revisão da decisão após a implementação

A Sprint 2 escolheu o algoritmo dentro do notebook. A Sprint 3 levou essa escolha para um serviço importável, com testes automatizados, e essa foi a primeira ocasião em que a decisão foi exercida fora do ambiente que a produziu. A revisão abaixo registra o que se manteve, o que mudou e o que o artefato treinado exigiu para funcionar fora do notebook.

**O que se manteve.** Nada da decisão registrada nas Seções 8.10.2 e 8.10.3 foi revertido. O serviço usa a mesma `config_22` de pré-processamento, a mesma representação híbrida de quatro blocos, a mesma arquitetura hierárquica, o mesmo classificador de regressão logística e os mesmos limiares de 0,550 e 0,700. Não houve retreinamento: os pesos em produção são os que produziram as métricas da Seção 8.10.3.

A conservação é verificável, e não declarada. A suíte de testes recalcula as métricas sobre o conjunto de teste a cada execução e reprova se a acurácia da intenção específica sair de 0,7383 ou o F1-macro sair de 0,7401, com tolerância de 0,0002. O mesmo vale para o efeito dos limiares: 14 solicitações abaixo do limiar de macrointenção, 305 no fluxo genérico e 0,8775 de acurácia entre as aceitas. A verificação está descrita na Seção 8.11.7.

**O que mudou: o motor de execução do encoder BERT.** O benchmark extraiu os embeddings com `sentence-transformers`, que carrega o modelo em PyTorch. Esta subseção descreve a arquitetura de inferência anterior, baseada em **ONNX Runtime**, e é mantida como registro histórico. O runtime vigente do classificador v2 executa o encoder BERTimbau diretamente por PyTorch e Transformers, conforme a Seção 8.11.10; as dependências efetivas são `torch` e `transformers` em `requirements-pln.txt`. Na versão histórica, o serviço executava o mesmo modelo em ONNX Runtime, a partir do grafo publicado no próprio repositório do modelo no Hugging Face. A troca não alterava o algoritmo, a representação nem os pesos: os embeddings coincidiam com os do `sentence-transformers` até uma diferença máxima de 2,4 × 10⁻⁷, e as métricas do conjunto de teste ficavam inalteradas.

O que muda é o custo de operar a escolha, medido durante a implementação:

| | PyTorch (`sentence-transformers`) | ONNX Runtime |
| --- | ---: | ---: |
| Tamanho do ambiente instalado | 1,1 GB | **427 MB** |
| Carga do encoder | 6,10 s | **0,33 s** |
| Latência por requisição | 6 ms | **2 ms** |
| Pico de memória | **1.118 MB** | 1.355 MB |

O ganho em disco e em tempo de carga vem de dispensar `torch` e `transformers`, que somavam 780 MB do ambiente. O custo é memória: o grafo em ponto flutuante de 32 bits ocupa cerca de 240 MB a mais em tempo de execução. No deploy em Linux a troca evita ainda uma armadilha conhecida, já que o `pip install torch` padrão baixa a variante com CUDA, de cerca de 2,5 GB, irrelevante para uma inferência em CPU.

A variante quantizada em int8 reduziria o grafo de 449 MB para 113 MB, mas custa 0,35 ponto de acurácia e desloca o efeito dos limiares calibrados na validação. Como isso quebraria a reprodução exata dos números da Seção 8.10.3, a versão em ponto flutuante foi mantida — a compressão é uma otimização legítima, mas exigiria recalibrar os limiares e reescrever esta seção.

**O que o artefato exigiu.** O `joblib` produzido pelo notebook não carregava fora dele. A função *analyzer* do TF-IDF e a classe do classificador hierárquico eram definidas no topo do notebook, e a serialização gravou referências a `__main__.identidade` e `__main__.ClassificadorHierarquico`; de qualquer módulo importável, `joblib.load` falhava com `AttributeError`. As duas definições passaram a viver em `src/backend/app/nlp/classifier.py`, e um script reaponta o artefato para lá sem retreinar. O procedimento está na Seção 8.11.4.

A implementação também tornou explícitas duas dependências que o notebook não precisava declarar. O artefato foi serializado com **scikit-learn 1.6.1**, e carregá-lo com outra versão faz a própria biblioteca advertir que o resultado pode ser inválido. A versão está fixada no `requirements.txt` do backend e o script de migração recusa executar fora dela. O encoder BERTimbau e o tokenizador são obtidos do mesmo snapshot imutável `94d69c95f98f7d5b2a8700c420230ae10def0baa`; `PLN_BERT_REVISION` permite substituir conscientemente essa revisão, mas o runtime exige um SHA hexadecimal completo de 40 caracteres e recusa branches ou tags mutáveis.

Há ainda uma divergência de ambiente entre treino e serviço que convém registrar: a execução de referência do notebook usou Python 3.9, enquanto o serviço exige **Python 3.13 ou anterior**, porque o `gensim` ainda não publica wheel para o 3.14 e a compilação a partir do fonte falha. As duas faixas são compatíveis com os artefatos versionados, mas a restrição superior é real e vale para qualquer ambiente que execute a inferência.

**O que a revisão não muda.** A conclusão do benchmark continua a mesma, com as mesmas ressalvas: a margem sobre o Híbrido W2V+BERT permanece estreita, o conjunto continua sintético e o F1-macro de 0,7401 na intenção específica continua **abaixo** do mínimo de 0,80 exigido pelo RNF06. A implementação não fecha essa lacuna — ela apenas a torna operacional, ao converter a incerteza em fluxo genérico em vez de handler errado. Fechar a lacuna depende dos próximos passos já listados na Seção 8.10.5, e permanece em aberto.

### 8.10.7 Refinamento da acurácia da intenção específica — issue #251

Esta subseção registra a versão 2 do classificador e **substitui, para o artefato atual**, as configurações e métricas históricas das Seções 8.10.3 e 8.10.6. O objetivo foi superar 0,80 de acurácia na intenção específica sem usar o conjunto de teste durante a seleção. Os 1.135 exemplos de teste permaneceram fechados até a escolha final; parâmetros, representações e limiares foram comparados nos 1.156 exemplos de validação.

O pré-processamento escolhido é deliberadamente conservador para português: aplica Unicode NFC, minúsculas e normalização de espaços, mas **não remove acentos, a negação `não` nem stopwords**. Foram geradas 1.450 consultas sintéticas adicionais, distribuídas pelas 31 classes e usadas exclusivamente no treino. A massa base de treino tem 3.062 exemplos; validação e teste não foram ampliados nem reamostrados.

| Configuração avaliada | Acurácia específica na validação | F1-macro específico na validação |
| --- | ---: | ---: |
| TF-IDF de palavras/caracteres + SVM hierárquica | 0,778547 | 0,771790 |
| BERTimbau congelado + SVM hierárquica | 0,730104 | 0,728812 |
| TF-IDF + BERTimbau + SVM calibrada hierárquica | **0,883218** | **0,881366** |

A configuração final concatena TF-IDF de palavras de 1 a 2 gramas, TF-IDF de caracteres de 3 a 5 gramas e embeddings congelados do `neuralmind/bert-base-portuguese-cased`, estes com peso 2,0. O primeiro estágio e cada especialista usam `LinearSVC` com `C=1,0`, calibrada em três dobras. Os limiares definidos na validação são 0,525 para macrointenção e 0,350 para intenção específica.

Somente depois da seleção o conjunto de teste foi aberto. A intenção específica atingiu **0,839648 de acurácia e 0,832724 de F1-macro**; a macrointenção atingiu **0,981498 de acurácia e 0,971470 de F1-macro**. O requisito de 0,80 foi, portanto, atendido nas duas métricas globais da intenção específica. Os números incluem todos os exemplos, antes de qualquer abstenção. Pelo roteamento, 10 exemplos ficaram abaixo do limiar macro e 63 abaixo do limiar específico.

Os experimentos são reproduzíveis por `benchmark_intencoes.py`, `benchmark_bertimbau.py` e `treinar_classificador_intencoes_v2.py`. Os resultados completos, hashes, matriz de confusão e métricas por classe estão em `src/notebooks/artefatos/`. A principal limitação permanece: a base é majoritariamente sintética e requer validação externa com consultas reais. Além disso, `analise_tendencia_desempenho` continua sendo a classe mais fraca e deve orientar a próxima coleta, apesar do ganho global.

## 8.11 Implementação do núcleo de PLN

A Seção 8.10 registra **qual** algoritmo foi escolhido e por quê. Esta registra o **código que o executa**: onde ele vive, de que bibliotecas depende, o que entra, o que sai e quais testes impedem que o comportamento se afaste do benchmark.

A diferença entre as duas seções é a diferença entre o notebook e o serviço. O benchmark da Sprint 2 rodava dentro de `classificador_intencoes_metro.ipynb`, e o modelo treinado só era utilizável de dentro dele. Na Sprint 3 o núcleo virou um pacote Python importável pela API, em `src/backend/app/nlp/`, com uma suíte automatizada que reprova quando as métricas divergem das registradas na Seção 8.10.3. Essa separação entre interface, lógica e dados é o que o RNF10 exige, e é o que permite que a mesma decisão seja exercida em uma requisição HTTP e em uma célula de notebook sem duplicar código.

### 8.11.1 Estrutura do módulo e responsabilidades

O núcleo é composto por quatro módulos de análise, mais dois módulos de fronteira acrescentados quando o pipeline passou a ser alcançado por HTTP:

```text
POST /api/chat  ──┐
                  ├─▶ pipeline.process_message ── orquestra e decide a rota
POST /api/audio ──┘             │
   (texto vindo do STT)         ├─▶ inference.classify ...... macrointenção + intenção
                                │      └─ preprocessing ..... tokeniza e reduz a radical
                                ├─▶ entities.extract_entities  projeto, período, indicador…
                                │
                                ├─▶ handler específico         (intenção acima do limiar)
                                ├─▶ fluxo genérico da macro    (intenção abaixo do limiar)
                                └─▶ resposta controlada        (fora de escopo, ou macro
                                                                abaixo do limiar)
```

| Arquivo | Linhas | Responsabilidade |
| --- | ---: | --- |
| `app/nlp/preprocessing.py` | 179 | Caixa, tokenização, remoção de pontuação e stemming, na `config_22` da Seção 8.10.3 |
| `app/nlp/entities.py` | 207 | Identificação dos elementos do domínio no texto cru, por léxico e por padrão |
| `app/nlp/classifier.py` | 171 | Definição do classificador hierárquico e carregamento validado do artefato treinado |
| `app/nlp/inference.py` | 339 | Vetorização de inferência, aplicação dos limiares e decisão de roteamento |
| `app/nlp/schemas.py` | 38 | Contratos Pydantic da saída pública: intenção, entidade e métricas de etapa |
| `app/pipeline.py` | 102 | Orquestração: classifica, extrai entidades e decide entre resposta controlada e geração |
| `app/nlp/data/lexico_dominio.json` | — | Vocabulário do portfólio: 108 termos em 12 tipos, substituível quando houver base real |

**A divisão de responsabilidade entre os dois analisadores é deliberada.** O classificador decide **o que** foi pedido; a extração de entidades decide **sobre o que**. "Qual o status da Linha 2-Verde?" e "Qual o status da Linha 15-Prata?" têm a mesma intenção e entidades diferentes; "Qual o status da Linha 2-Verde?" e "Qual o orçamento da Linha 2-Verde?" têm a mesma entidade e intenções diferentes. Separar as duas evita que o catálogo de intenções cresça por combinação.

**Os artefatos treinados não são duplicados no backend.** Eles continuam em `src/notebooks/artefatos/`, e `app/nlp/classifier.py` os referencia por caminho relativo. O modelo tem 13,2 MB e o Word2Vec 922 KB; manter uma segunda cópia dentro do pacote criaria a possibilidade de o serviço rodar com um artefato diferente do que o notebook mediu.

**A orquestração fica fora do núcleo, e isso é proposital.** `app/pipeline.py` é o único módulo que conhece ao mesmo tempo o classificador e o provedor gerador; `app/main.py` não reproduz regra nenhuma de PLN, apenas converte as falhas previstas em respostas HTTP. Os módulos de `app/nlp/` continuam sem saber que existe uma API, o que preserva a separação entre interface, lógica e dados exigida pelo RNF10 e mantém o núcleo exercitável fora do serviço, como na Seção 8.11.6.

**O carregamento e a classificação são serializados por um lock de processo.** `app/pipeline.py` mantém um `Lock` global que protege tanto o aquecimento quanto cada chamada a `classify`. Ele evita que duas requisições simultâneas disparem carregamentos concorrentes dos três artefatos na primeira chamada. O efeito colateral é que as classificações passam a ser sequenciais mesmo com o servidor atendendo em paralelo; a consequência para a vazão está medida na Seção 8.11.8.

### 8.11.2 Bibliotecas, frameworks e dependências de execução

As dependências do backend estão separadas em dois arquivos, e a separação tem uma razão operacional: quem trabalha apenas na API de áudio da Seção 8.7 não precisa baixar o encoder BERT nem o Word2Vec.

| Arquivo | Conteúdo | Quando é necessário |
| --- | --- | --- |
| `requirements.txt` | FastAPI, Uvicorn, Pydantic, `httpx`, `scikit-learn`, `nltk`, `numpy`, `joblib`, `pytest` | Sempre — inclui o pré-processamento e a extração de entidades |
| `requirements-pln.txt` | `torch`, `transformers` (encoder BERTimbau) | Somente para a inferência do classificador |

| Biblioteca | Versão fixada | Papel na inferência |
| --- | --- | --- |
| `scikit-learn` | 1.6.1 | Vetorizadores TF-IDF, reduções SVD, escaladores e o classificador serializados no artefato |
| `nltk` | 3.10.3 | Stemming Snowball em português, algorítmico e sem corpus baixado |
| `numpy` | 2.5.2 | Composição da matriz de atributos e agregação dos vetores |
| `joblib` | 1.6.0 | Desserialização do artefato treinado |
| `gensim` | 4.4.0 | Carregamento do Word2Vec treinado no corpus do projeto |
| `onnxruntime` | 1.29.0 | Execução do grafo do encoder BERT em CPU |
| `tokenizers` | 0.23.2 | Tokenização do encoder, independente de `transformers` |
| `huggingface_hub` | 1.30.0 | Download do grafo ONNX e do tokenizador na primeira execução, com cache local |

**Observação sobre a versão vigente.** A tabela acima descreve a lista de dependências da arquitetura histórica (ONNX Runtime). No classificador v2 em produção (Seção 8.11.10), o encoder BERTimbau roda por **PyTorch e Transformers**; portanto `torch` e `transformers` (fixados em `requirements-pln.txt`) são justamente as dependências necessárias, e o `onnxruntime` não faz parte do runtime atual.

**O ambiente exige Python 3.13 ou anterior.** O `gensim` ainda não publica *wheel* para o 3.14 e a compilação a partir do fonte falha. A restrição vale para qualquer ambiente que execute a inferência, inclusive o de implantação previsto na Seção 6.2.

```bash
cd src/backend
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install -r requirements-pln.txt
```

Sem o segundo arquivo, o módulo continua importável e os testes de inferência são **pulados com a razão declarada**, em vez de falharem — a suíte distingue "não instalado" de "quebrado".

### 8.11.3 Pré-processamento e extração de entidades

**A `config_22` é um contrato, não uma preferência.** Os vetorizadores TF-IDF serializados no artefato foram ajustados sobre os tokens que `preprocess_text` produz. Alterar tokenização, caixa ou stemming não degrada o modelo aos poucos: invalida-o, porque os atributos deixam de ser os que ele viu no treino. A função é a mesma do benchmark, portada para módulo importável, e o notebook `preprocessamento_entidades.ipynb` compara as duas implementações sobre as 5.353 frases do conjunto sintético e falha se houver divergência.

```python
from app.nlp.preprocessing import tokenize

tokenize("qual é o status da extensão da Linha 5-Lilás?")
# ['qual', 'é', 'o', 'status', 'da', 'extensã', 'da', 'linh', '5', 'lilás']
```

As stopwords são preservadas de propósito: "qual", "quando", "quanto" e "quem" distinguem tipos de solicitação, e a grade de configurações confirmou o efeito — as quatro melhores médias por família mantêm stopwords e as quatro piores as removem.

**A extração de entidades roda sobre o texto cru, não sobre os tokens.** O tokenizador da `config_22` quebra em `[^\W_]+`, o que separaria `PRJ-2031` em `PRJ` e `2031` e destruiria justamente a forma que identifica o projeto. Duas fontes se combinam: um léxico com o vocabulário conhecido do portfólio e expressões regulares para valores que não cabem em lista fechada — código de projeto, percentual, prazo em dias e data. Quando dois termos se sobrepõem, vence o mais longo, de modo que em "extensão da Linha 5-Lilás" a entidade é o projeto inteiro e não a linha isolada.

```python
from app.nlp.entities import extract_entities

[(e.tipo, e.valor) for e in
 extract_entities("compare o Linha 2-Verde e o Linha 15-Prata por aderência ao cronograma")]
# [('projeto', 'Linha 2-Verde'), ('projeto', 'Linha 15-Prata'),
#  ('indicador', 'aderência ao cronograma')]
```

O casamento ignora caixa e acento, porque o canal recebe texto digitado, e devolve sempre o valor canônico do catálogo: `QUAL O ORCAMENTO DA LINHA 4-AMARELA` produz a entidade `Linha 4-Amarela`, com a grafia do léxico.

**Termos ambíguos não são arbitrados pelo extrator.** "Aderência ao cronograma" é ao mesmo tempo critério de comparação e indicador de desempenho, e qual dos dois vale depende da intenção — que o extrator não conhece. A entidade expõe `tipos` com todos os candidatos e a propriedade `ambigua`, e quem já conhece a intenção escolhe. O campo `tipo` guarda o mais provável por precedência, para o consumidor que não quer tratar a ambiguidade.

Medida contra o gabarito reconstruído da geração do conjunto sintético, a extração obteve **precisão 0,996, revocação 0,999 e F1 0,998** sobre 7.000 entidades em 5.353 frases, com 25 falsos positivos e 5 falsos negativos remanescentes. O número é alto porque o conjunto é sintético e o léxico foi derivado do mesmo dicionário que gerou as frases; a Seção 8.11.6 mostra o que acontece quando o termo está fora dele.

### 8.11.4 Carregamento do artefato treinado

A inferência depende de três artefatos, e apenas o primeiro está no `joblib`:

| Artefato | Origem | Tamanho | O que contém |
| --- | --- | ---: | --- |
| `classificador_intencoes.joblib` | Notebook do benchmark | 13,2 MB | Vetorizadores TF-IDF, reduções SVD, escaladores, classificador hierárquico, limiares e mapa de intenção para macrointenção |
| `word2vec_portfolio.model` | Notebook do benchmark | 922 KB | Word2Vec treinado apenas com o conjunto de treino, 577 termos em 200 dimensões |
| Grafo ONNX do encoder | Hugging Face, baixado na primeira execução | 449 MB | `paraphrase-multilingual-MiniLM-L12-v2` exportado para ONNX, com o tokenizador |

**O artefato precisou ser migrado para carregar fora do notebook.** Pelo motivo descrito na Seção 8.10.6, o `joblib` gravado pelo notebook referenciava `__main__.identidade` e `__main__.ClassificadorHierarquico`. As duas definições passaram a viver em `app/nlp/classifier.py`, e um script reaponta o artefato para lá:

```bash
cd src/backend
.venv/bin/python ../notebooks/migrar_artefato_classificador.py            # reescreve
.venv/bin/python ../notebooks/migrar_artefato_classificador.py --verificar # só confere
```

O script **não retreina**: os pesos, os vetorizadores e os limiares continuam sendo os que produziram as métricas da Seção 8.10.3. O artefato versionado no repositório já está migrado; o script serve para qualquer artefato novo que saia do notebook.

**O carregamento valida o artefato antes de usá-lo.** `load_artifact` confere que as doze chaves esperadas estão presentes e levanta `ValueError` nomeando as ausentes, em vez de deixar a falta aparecer como `KeyError` no meio de uma inferência. Um artefato inexistente levanta `FileNotFoundError` com a instrução de executar o script de migração.

```python
from app.nlp.classifier import load_artifact

artefato = load_artifact()
artefato.limiar_macro, artefato.limiar_intencao
# (0.5500000000000003, 0.7000000000000003)
len(artefato.intencoes)        # 31
len(artefato.macrointencoes)   # 4
```

O resíduo nas casas decimais dos limiares é o rastro da varredura que os calibrou na validação: eles são o resultado de uma soma incremental, e não valores digitados. As comparações do roteamento usam o número armazenado, de modo que o resíduo não altera decisão alguma; a Seção 8.10.3 os arredonda para 0,550 e 0,700 por legibilidade.

### 8.11.5 Inferência e roteamento por limiares

`app.nlp.inference` recebe a solicitação em texto e devolve uma `Classificacao`. O contrato de saída é o seguinte:

| Campo | Tipo | Conteúdo |
| --- | --- | --- |
| `macrointencao` | `str` | `CONSULTA`, `TRANSACAO`, `ALERTA`, `FORA_DE_ESCOPO` ou `INDEFINIDA` |
| `confianca_macro` | `float` | Probabilidade da macrointenção prevista |
| `intencao` | `str \| None` | Intenção específica, ou `None` quando abaixo do limiar |
| `confianca_intencao` | `float` | Probabilidade conjunta P(macro) × P(intenção \| macro) |
| `fluxo` | `str` | Rota do catálogo correspondente à macrointenção |
| `handler` | `str` | `handler:<intenção>`, `fluxo genérico de <macro>` ou `limitacao` |
| `alternativas` | `list[tuple]` | As `top_k` intenções mais prováveis com suas confianças |
| `resposta_sugerida` | `str \| None` | Texto de limitação, preenchido apenas quando a macrointenção fica abaixo do limiar |

Duas propriedades derivadas resumem a decisão para quem consome: `roteada` indica que a solicitação segue no pipeline, e `handler_especifico` indica que um handler dedicado pode ser acionado.

**A vetorização de inferência reaplica exatamente as transformações ajustadas no treino, na ordem em que foram compostas.** Qualquer divergência — outra tokenização, outra ordem de blocos, normalização ausente — produziria atributos que o modelo nunca viu, e o erro seria silencioso: o modelo devolveria um rótulo, apenas o rótulo errado. O TF-IDF de caracteres e o encoder BERT recebem o texto cru; os demais blocos recebem os tokens da `config_22`.

**Os dois limiares definem três rotas**, conforme os valores calibrados na validação e registrados na Seção 8.10.3:

| Condição | Rota | `handler` |
| --- | --- | --- |
| Confiança da macro < 0,550 | Resposta controlada de limitação (RF08/RNF11) | `limitacao` |
| Macro ≥ 0,550 e confiança da intenção < 0,700 | Fluxo genérico da macrointenção | `fluxo genérico de <macro>` |
| Macro ≥ 0,550 e intenção ≥ 0,700 | Handler específico do catálogo | `handler:<intenção>` |

A macrointenção `FORA_DE_ESCOPO` nunca aciona handler específico, ainda que a confiança seja alta: o catálogo a associa à rota "Resposta padrão de limitação (RF08)", e o campo `fluxo` da saída carrega essa rota. O campo `resposta_sugerida`, porém, só é preenchido quando a **macrointenção** fica abaixo do limiar — isto é, quando o pipeline não sabe sequer a categoria do pedido. Quem consome a classificação precisa tratar os dois casos: o texto pronto de limitação e a rota de limitação anunciada em `fluxo`. É o que `app/pipeline.py` faz: quando a solicitação não é roteada **ou** a macrointenção é `FORA_DE_ESCOPO`, ele devolve `resposta_sugerida` se houver e, quando não houver, um texto de limitação próprio — sem chamar o provedor gerador em nenhum dos dois ramos.

**A saída nunca anuncia uma macrointenção e um handler de outra.** O limiar de 0,700 já garante isso por construção, porque a probabilidade da intenção é conjunta e acima de 0,5 as duas coincidem; mesmo assim a verificação é explícita no código, para que recalibrar o limiar para baixo não quebre o contrato em silêncio. Um teste percorre todo o conjunto de teste confirmando a coerência.

**O carregamento é preguiçoso, e a API força a carga na subida quando configurada para isso.** Adiar a carga serve aos testes, mas em produção faria a primeira pessoa a usar o agente pagar o carregamento inteiro dentro da própria requisição. O `lifespan` do FastAPI lê a variável `PLN_WARMUP`: com `1`, o classificador é carregado antes de o serviço aceitar requisições; com `0`, que é o padrão, a carga acontece na primeira classificação. A Seção 8.5 descreve a configuração pelo lado da aplicação.

```python
from app.nlp.inference import get_classifier, classify

get_classifier().warmup()          # o que o lifespan faz com PLN_WARMUP=1

resultado = classify("qual é o status da extensão da Linha 5-Lilás?")
resultado.macrointencao            # 'CONSULTA'
resultado.intencao                 # 'consulta_status_projeto'
resultado.handler                  # 'handler:consulta_status_projeto'
```

`get_classifier` devolve uma instância compartilhada, para que os três artefatos sejam carregados uma única vez no processo.

### 8.11.6 Exemplos de execução: casos de sucesso e de falha

Os resultados abaixo vêm de uma execução real do módulo sobre o artefato versionado, em 8 de setembro de 2026. As confianças são as devolvidas pelo próprio pipeline e não foram arredondadas para favorecer a leitura.

**Casos em que o pipeline aciona um handler específico.**

| Entrada | Entidades extraídas | Macrointenção | Intenção | Conf. | Encaminhamento |
| --- | --- | --- | --- | ---: | --- |
| "qual é o status da extensão da Linha 5-Lilás?" | `projeto: extensão da Linha 5-Lilás` | `CONSULTA` (0,9998) | `consulta_status_projeto` | 0,9944 | `handler:consulta_status_projeto` |
| "compare o Linha 2-Verde e o Linha 15-Prata por aderência ao cronograma" | `projeto: Linha 2-Verde`, `projeto: Linha 15-Prata`, `indicador: aderência ao cronograma` | `CONSULTA` (0,9992) | `comparacao_entre_projetos` | 0,9981 | `handler:comparacao_entre_projetos` |
| "me avisa se o projeto de sinalização atrasar mais de 7 dias" | `prazo_dias: 7 dias` | `ALERTA` (1,0000) | `alerta_prazo_atraso` | 1,0000 | `handler:alerta_prazo_atraso` |
| "gera um relatório executivo do subportfólio de modernização" | `subportfolio: subportfólio de Modernização` | `TRANSACAO` (1,0000) | `transacao_gerar_relatorio` | 0,9999 | `handler:transacao_gerar_relatorio` |
| "qual o statuss do projeto de bilhetgem eletronica?" | — | `CONSULTA` (0,9999) | `consulta_status_projeto` | 0,9960 | `handler:consulta_status_projeto` |

O último caso é o argumento empírico a favor da representação híbrida da Seção 8.10.2. "Statuss" e "bilhetgem" não existem no vocabulário do Word2Vec nem no TF-IDF de palavras, e ainda assim a classificação é correta com 0,996 de confiança: o TF-IDF de caracteres modela a grafia e sobrevive ao erro de digitação. Nenhum bloco isolado daria esse resultado.

**Casos em que os limiares contêm a decisão.** Aqui o pipeline reconhece que não sabe o suficiente e recusa acionar um handler:

| Entrada | Macrointenção | Conf. macro | Melhor intenção | Conf. | Encaminhamento |
| --- | --- | ---: | --- | ---: | --- |
| "atualiza o mapa de benefícios do PRJ-2031 com o novo indicador" | `TRANSACAO` | 0,9744 | `transacao_atualizar_status` | 0,6700 | fluxo genérico de `TRANSACAO` |
| "há bloqueios registrados no Linha 15-Prata?" | `CONSULTA` | 0,5888 | `transacao_registrar_pendencia` | 0,3817 | fluxo genérico de `CONSULTA` |
| "qual a previsão do tempo para amanhã?" | `FORA_DE_ESCOPO` | 1,0000 | `fora_escopo_externo` | 0,9993 | Resposta padrão de limitação (RF08) |
| "bom dia, tudo certo?" | `FORA_DE_ESCOPO` | 1,0000 | `fora_escopo_social` | 0,9999 | Resposta padrão de limitação (RF08) |

A primeira linha mostra o limiar operando com margem estreita e a favor da segurança: 0,67 contra o limiar de 0,70. A intenção mais provável era plausível, mas o pipeline preferiu o fluxo genérico da macrointenção a acionar uma transação de atualização com um terço de dúvida — comportamento exigido pelo RNF04 e pelo RNF11, já que uma transação errada altera dados.

A saída completa do pipeline para dois desses casos, com as entidades reduzidas ao par `(tipo, valor)` e a lista de alternativas quebrada em duas linhas por largura:

```text
ENTRADA   : atualiza o mapa de benefícios do PRJ-2031 com o novo indicador
TOKENS    : ['atualiz', 'o', 'map', 'de', 'benefíci', 'do', 'prj', '2031', 'com', 'o', 'nov', 'indic']
ENTIDADES : [('documento', 'mapa de benefícios'), ('projeto', 'PRJ-2031')]
MACRO     : TRANSACAO (0.9744)
INTENCAO  : None (0.67)
HANDLER   : fluxo genérico de TRANSACAO
FLUXO     : Executor de Transação -> Confirmação -> Registro
ALTERNAT. : [('transacao_atualizar_status', 0.67), ('transacao_cadastrar_projeto', 0.1448),
             ('transacao_solicitar_atualizacao', 0.0568)]

ENTRADA   : há bloqueios registrados no Linha 15-Prata?
TOKENS    : ['há', 'bloquei', 'registr', 'no', 'linh', '15', 'prat']
ENTIDADES : [('projeto', 'Linha 15-Prata')]
MACRO     : CONSULTA (0.5888)
INTENCAO  : None (0.3817)
HANDLER   : fluxo genérico de CONSULTA
FLUXO     : RecuperadorInformacao -> Estruturador de Resposta
ALTERNAT. : [('transacao_registrar_pendencia', 0.3817), ('consulta_status_projeto', 0.2968),
             ('consulta_escopo_tap', 0.2441)]
```

**Casos de falha.** Os três abaixo são erros reais do pipeline, registrados porque delimitam o que a implementação atual não resolve.

| Entrada | O que o pipeline devolveu | Por que é falha |
| --- | --- | --- |
| "quanto já foi gasto na obra da Linha 6-Laranja?" | Intenção `consulta_orcamento_custo` correta, com 0,9981 — mas **nenhuma entidade extraída** | "Linha 6-Laranja" não está no léxico. O pipeline sabe *o que* foi pedido e não sabe *sobre o que*; a recuperação de informação não teria como filtrar o projeto |
| "prorroga o prazo do PRJ-0442 até março" | `CONSULTA` / `consulta_cronograma_prazo` com 0,7321, **acima** do limiar de 0,700 | É um pedido de alteração, e deveria ser `TRANSACAO` / `transacao_atualizar_cronograma`, que aparece como segunda alternativa com 0,1417. O handler **seria acionado**: o limiar não protege este caso |
| "e ai?" | `CONSULTA` com 0,9815 de confiança de macrointenção | Deveria ser `FORA_DE_ESCOPO`. O erro é contido pelo limiar de intenção (0,425 leva ao fluxo genérico), mas o **limiar de macrointenção não o detecta** — a categoria errada foi prevista com alta confiança |

O primeiro caso é a limitação do léxico fechado, já registrada na Seção 8.11.3: um projeto fora de `lexico_dominio.json` só é reconhecido se tiver forma de código, como `PRJ-2031`. Quando a base real do portfólio estiver disponível, o arquivo passa a ser gerado a partir dela e o código não muda.

O segundo é a fronteira entre consulta e transação, que o F1-macro de 0,7401 na intenção específica resume e que a Seção 8.10.5 aponta como classe a revisar. É também a demonstração de que os limiares reduzem o dano, mas não o eliminam.

O terceiro delimita o alcance do mecanismo de contenção: **os dois limiares não são equivalentes em proteção**. O de intenção específica cobre a escolha do handler; o de macrointenção só age quando o modelo está incerto sobre a categoria, e não quando ele está confiante e errado. Uma saudação curta classificada como consulta com 0,98 atravessa o primeiro filtro. O impacto prático é limitado — a solicitação cai no fluxo genérico de `CONSULTA` em vez de receber a resposta de limitação —, mas a resposta ao usuário fica menos adequada do que deveria, e o caso é candidato natural ao conjunto de solicitações reais previsto na Seção 8.10.5.

### 8.11.7 Testes automatizados

A coleta atual registra **252 testes no backend**. A suíte cobre o classificador BERTimbau vigente, os contratos HTTP de texto e áudio e a persistência mínima. Os cenários de áudio incluem a cadeia STT → PLN com classificação real, falhas controladas e correlação por `conversation_id`. Tempos variam conforme o cache do snapshot do modelo e o ambiente de execução.

| Arquivo | Testes | O que verifica |
| --- | ---: | --- |
| `test_nlp_preprocessing.py` | 22 | Cada opção da grade de pré-processamento, a `config_22` selecionada, a preservação de stopwords e a estabilidade dos tokens que o artefato espera |
| `test_nlp_entities.py` | 30 | Casamento por léxico e por padrão, insensibilidade a caixa e acento, resolução de sobreposição pelo termo mais longo, tipos ambíguos e posições no texto original |
| `test_nlp_classifier.py` | 19 | Carregamento e validação do artefato, recusa de artefato incompleto, comportamento do classificador hierárquico e a exigência de que ele carregue **fora** do notebook |
| `test_nlp_inference.py` | 25 | Classificação ponta a ponta, roteamento, preservação de acentos e negação, revisão imutável do modelo BERTimbau e do tokenizador |
| `test_pipeline_api.py` | 22 | Contrato de `POST /api/chat` e `POST /api/audio`, opt-out por `use_intent_classifier`, cadeia áudio → STT simulado → PLN real, proatividade e falhas controladas |
| `test_traceability.py` | 14 | Contrato entre HTTP, classificador real e persistência mínima nas entradas por texto e áudio, incluindo identidade, correlação por `conversation_id` e auditoria da falha do classificador |

Os testes de inferência verificam as métricas e os limiares do artefato vigente descrito na Seção 8.11.10. Os números da Seção 8.10.3 pertencem ao benchmark histórico e não são critérios para o classificador v2.

Os testes de inferência também verificam a coerência entre macrointenção e handler, a preservação de acentos e negação e a recusa de revisões mutáveis ou inválidas do BERTimbau.

**Execução.**

```bash
cd src/backend
.venv/bin/python -m pytest app/tests -q
```

```text
252 passed, 11 warnings
```

Quando `requirements-pln.txt` não está instalado, os testes de inferência são pulados com a razão declarada (`instale requirements-pln.txt`). O job `backend-api` da CI instala os dois arquivos de dependências, importa explicitamente `torch` e `transformers` como verificação obrigatória, executa `test_nlp_inference.py` e `test_traceability.py` e mantém cache do snapshot imutável, portanto o cenário contratual não pode passar por *skip* silencioso.

**A suíte separa velocidade de evidência entre camadas.** A maior parte de `test_pipeline_api.py` substitui classificador e provedor gerador por duplos para verificar rapidamente campos, códigos HTTP e decisões de chamada. `test_audio_transcription_is_classified_by_real_classifier` mantém somente STT e Gemini nas fronteiras controladas e executa o classificador real. Em `test_traceability.py`, `test_chat_real_classifier_contract_and_minimal_persistence` e `test_audio_real_classifier_contract_and_minimal_persistence` não substituem `classify`: usam o artefato real, validam o contrato público e confirmam a gravação mínima. Azure STT, Gemini e o driver PostgreSQL são substituídos nas respectivas fronteiras para que a suíte permaneça determinística.

O smoke test opcional `python -m scripts.verify_audio_stt_pln_real_db`, executado a partir de `src/backend`, comprova a integração com o PostgreSQL/Supabase configurado. Ele envia dois áudios sintéticos pela rota HTTP, mantém o classificador real no cenário positivo, induz uma falha controlada no cenário negativo e verifica `ai_conversations`, `ai_interactions` e `audit_events`. Cada execução usa identificadores únicos e remove explicitamente as conversas, interações e auditorias criadas. A execução de referência da S4-13 confirmou sucesso, falha, correlação, auditoria e limpeza, com zero resíduos.

**Evidência com STT real da S4-13 (17/09/2026).** A cadeia `POST /api/audio` → Azure Speech `pt-BR` → classificador PLN real → Supabase foi executada com a pergunta “Qual é o perfil epidemiológico clássico de uma paciente com artrite reumatoide (AR)?”, da amostra pública [`juliasdata/medical-audio-sample-brazilian-portuguese`](https://huggingface.co/datasets/juliasdata/medical-audio-sample-brazilian-portuguese), revisão `5d31e7d`, licenciada para avaliação por `juliasdata-sample-evaluation-license-1.0`. O WAV original, com SHA-256 `cd04854ed8364e38f1e3a335f9ce5f3e614952421890df6ad9dee9da5a4aaba4`, foi mantido apenas em diretório temporário e convertido de PCM mono, 48 kHz e 16 bits para o contrato PCM mono, 16 kHz e 16 bits; a derivação usada teve SHA-256 `8bda1df850d99ce754e4f95152dc80aabb03a2a31ae5da63bf0a6a790bd4ec59`.

O Azure STT retornou a frase esperada, preservando os termos verificáveis “perfil” e “artrite”. O classificador real retornou a macrointenção `CONSULTA` e, por não haver intenção específica segura para o domínio médico, manteve a intenção específica vazia, respeitando os limiares do artefato. A interação foi localizada no Supabase pelo mesmo `conversation_id`; `ai_interactions.user_prompt` coincidiu com a transcrição, e os eventos `pln_intent_classified` e `database_traceability_recorded` foram encontrados. O provedor gerador, posterior ao escopo áudio → STT → PLN da S4-13, permaneceu como fronteira controlada. O verificador `python -m scripts.verify_audio_stt_pln_live <audio.wav> --expected-term perfil --expected-term artrite` confirmou `LIVE_DB_CORRELATION_OK=True`, `LIVE_DB_AUDIT_OK=True` e `LIVE_DB_CLEANUP_OK=True`; uma consulta posterior não encontrou resíduos da execução.

### 8.11.8 Desempenho medido

Medição na execução de referência, em macOS 26.6 sobre Apple Silicon, com Python 3.13.15, mediana de 200 repetições:

| Etapa | Mediana | Pior caso |
| --- | ---: | ---: |
| Pré-processamento (`tokenize`) | 0,04 ms | 0,12 ms |
| Extração de entidades | 0,01 ms | 1,10 ms |
| Classificação completa (`classify`) | 4,34 ms | 7,22 ms |
| Vetorização em lote de 64 textos | 0,76 ms por texto | — |
| Carga dos três artefatos (`warmup`) | 0,8 s | — |

As duas últimas linhas são execução única, e não mediana de 200. O pior caso da extração de entidades é a primeira chamada, que carrega o léxico do disco; a partir da segunda o custo é o da mediana.

O tempo é dominado pelo encoder BERT: o pré-processamento e a extração de entidades juntos custam cerca de 1% da classificação. O ganho da vetorização em lote — de 4,34 ms para 0,76 ms por texto — indica que a avaliação do conjunto de teste inteiro deve usar `vectorize` com a lista completa, e não um laço de `classify`, como a suíte já faz.

**A folga em relação ao RNF05 é ampla, mas o requisito não é sobre esta etapa.** O RNF05 dá 10 segundos para uma consulta simples ponta a ponta, medidos entre o recebimento pela API e o retorno da resposta estruturada. A classificação consome cerca de 4 ms desse orçamento, contra 6 segundos reservados à transcrição na Seção 8.7 e o tempo da recuperação e da geração da resposta. A conclusão que a medição autoriza é estreita: o classificador **não** é o gargalo do pipeline.

Com a integração da Seção 8.11.9, a medição ponta a ponta deixou de depender de instrumentação nova: as duas rotas devolvem `nlp_ms` e `route_ms`, e a rota de áudio acrescenta `validation_ms`, `stt_ms` e `total_ms`. A verificação formal do RNF05 continua sendo entrega da Seção 9.2, agora apoiada nesses campos.

A carga de 0,8 segundo acontece uma vez por processo. Com `PLN_WARMUP=1` ela é paga na subida da aplicação, e não dentro da primeira requisição.

**O lock de processo elimina o ganho de concorrência.** `app/pipeline.py` protege cada chamada a `classify` com um `Lock` global, o que impede carregamentos concorrentes dos artefatos mas também serializa as classificações. Medindo 16 solicitações no mesmo ambiente da tabela acima, com os artefatos já carregados:

| Cenário | Total | Por solicitação |
| --- | ---: | ---: |
| Sequencial, uma thread | 70,7 ms | 4,42 ms |
| 4 threads, sem o lock | 34,8 ms | 2,17 ms |
| 4 threads, com o lock atual | 74,8 ms | 4,68 ms |
| 8 threads, sem o lock | 30,7 ms | 1,92 ms |
| 8 threads, com o lock atual | 83,4 ms | 5,21 ms |

Sem o lock, quatro threads dobram a vazão e oito chegam a 2,3 vezes — sinal de que a parte pesada da inferência roda fora do GIL, no ONNX Runtime e nas rotinas de álgebra linear. Com o lock, a vazão não sobe em nenhuma das duas configurações e fica marginalmente pior que a execução sequencial, pelo custo de contenção.

O lock protege um cenário real: a carga preguiçosa dos três artefatos não é reentrante, e duas requisições simultâneas na primeira chamada disparariam dois carregamentos. Mas ele é mais largo do que o necessário — bastaria proteger o carregamento, e não cada inferência. Com `PLN_WARMUP=1` os artefatos já estão carregados quando a primeira requisição chega, de modo que a serialização passa a custar vazão sem proteger nada. Estreitar o lock é otimização candidata para a Sprint 4, e não altera nenhum resultado documentado nas Seções 8.10 e 8.11.

### 8.11.9 Situação da integração

| Etapa | Situação | Onde está |
| --- | --- | --- |
| Pré-processamento textual | Implementado e testado | `app/nlp/preprocessing.py` |
| Extração de entidades do domínio | Implementado e testado | `app/nlp/entities.py` |
| Carregamento do artefato treinado | Implementado e testado | `app/nlp/classifier.py` |
| Classificação e roteamento por limiares | Implementado e testado | `app/nlp/inference.py` |
| Exposição do pipeline em rota HTTP | Implementada | `POST /api/chat` e `POST /api/audio` em `app/main.py` e `app/pipeline.py` |
| Persistência da classificação e da rota | Implementada e testada quando o banco está configurado | `app/database/tracing.py` grava macro, intenção, confianças, handler, rota, fontes e auditoria; entidades permanecem no payload do evento de PLN |

O núcleo é importável, exercitável e agora alcançado pelas rotas HTTP. Em
`POST /api/chat`, a classificação é o padrão quando `use_intent_classifier` está
ausente ou `true`; `false` permanece como opt-out explícito da bancada web. Em
`POST /api/audio`, a transcrição segue para o mesmo pipeline textual. As duas
rotas devolvem intenção rica, entidades e métricas (`nlp_ms`, `route_ms`; no
áudio também `validation_ms`, `stt_ms` e `total_ms`), o que viabiliza a medição
incremental do RNF05. Solicitações fora de escopo, indefinidas ou sem rota segura
recebem mensagem controlada sem chamada ao provedor gerador, preservando RNF11.
A persistência é ativada por `DATABASE_URL` ou `SUPABASE_DATABASE_URL`; sem uma
dessas variáveis, a API mantém o modo local sem falhar. Autorização por perfil
continua pendente da entrega específica.

Exemplo resumido do contrato textual exposto por `POST /api/chat`. Cada linha
do texto reproduz integralmente um trecho ou atributo da fonte citada, e a
evidência que a sustenta acompanha a resposta em `claims`; sem evidência
verificável, a resposta volta com `evidence_status: "insufficient"`. Os campos,
as regras de validação e a sugestão proativa estão consolidados nesta seção.

```json
{
  "contract_version": "1.1.0",
  "text": "Status: Em acompanhamento [Fonte 1]",
  "interaction_id": "8b3e0d51-77aa-4c19-9f2b-5e1c7a4d3e90",
  "trace_id": "0d6f2c1e-4b7a-4f0e-9c3d-5a8b7e6f1d20",
  "evidence_status": "referenced",
  "claims": [
    {
      "text": "Status: Em acompanhamento",
      "citation_ids": ["Fonte 1"],
      "evidence": [
        { "citation_id": "Fonte 1", "field": "attribute", "attribute": "Status", "quote": "Status: Em acompanhamento" }
      ]
    }
  ],
  "intent": {
    "macro": "CONSULTA",
    "specific": "consulta_status_projeto",
    "confidence_macro": 0.9998,
    "confidence_specific": 0.9944,
    "flow": "RecuperadorInformacao -> Estruturador de Resposta",
    "handler": "handler:consulta_status_projeto",
    "alternatives": [
      { "intent": "consulta_status_projeto", "confidence": 0.9944 }
    ]
  },
  "entities": [
    {
      "type": "projeto",
      "value": "extensão da Linha 5-Lilás",
      "text": "extensão da Linha 5-Lilás",
      "start": 19,
      "end": 44,
      "types": ["projeto"],
      "ambiguous": false
    }
  ],
  "pipeline_metrics": {
    "nlp_ms": 8,
    "route_ms": 35
  },
  "sources": [
    {
      "id": "projetos:512",
      "citation_id": "Fonte 1",
      "title": "Extensão da Linha 5-Lilás",
      "list_name": "Projetos",
      "web_url": "https://mock.sharepoint.local/projetos/512",
      "last_modified": "2026-08-26T12:00:00Z",
      "score": 4.2,
      "excerpt": "Obra em fase de sistemas.",
      "attributes": { "Status": "Em acompanhamento" }
    }
  ]
}
```

A Seção 8.4 registra a cobertura de teste correspondente e o que continua descoberto.

### 8.11.10 Atualização operacional do classificador v2 — issue #251

O serviço agora consome o mesmo artefato híbrido descrito na Seção 8.10.7. `app/nlp/inference.py` aplica os dois vetorizadores TF-IDF serializados, extrai os embeddings BERTimbau com PyTorch e Transformers, concatena os três blocos e delega a decisão ao classificador hierárquico calibrado. Assim, as referências anteriores a Word2Vec, ONNX Runtime, `config_22`, regressão logística e aos limiares 0,550/0,700 descrevem somente a versão histórica.

A normalização do classificador vive em `normalizar_portugues`, em `app/nlp/preprocessing.py`, separada das rotinas legadas usadas pela extração de entidades. Testes unitários asseguram que `não`, `nao` e caracteres acentuados sejam preservados; testes de integração carregam o artefato real, reproduzem as métricas da Seção 8.10.7 e conferem os limiares 0,525/0,350. As dependências adicionais estão fixadas em `requirements-pln.txt` (`torch` e `transformers`). O custo operacional aumentou em relação à versão lexical/ONNX anterior, portanto o aquecimento na inicialização continua recomendado.

O artefato versionado referencia classes importáveis de `app.nlp.classifier`, sem depender de símbolos definidos em `__main__`. O comando `treinar_classificador_intencoes_v2.py --reparar-artefato` corrige essa referência quando um novo treino for produzido, sem retreinar ou alterar os pesos.

## 8.12 Histórico da integração da interface web

A issue #131 conectou a bancada React aos endpoints de texto e áudio, unificou ambos no pipeline de resposta e acrescentou os testes de componentes, contratos e navegador. A documentação operacional consolidada está na Seção 8.5 e no `src/frontend/README.md`; as evidências permanecem em `src/frontend/TESTES.md`. Esta nota histórica é mantida para rastreabilidade da entrega, sem repetir contratos, componentes ou instruções de execução.


# 9. Planejamento e Execução de Testes

O planejamento dos testes sistêmicos é entrega da Sprint 3, e a execução ocorre na Sprint 4, conforme as Seções 8.3.1 e 8.3.2. As tasks correspondentes já estão detalhadas, estimadas e sequenciadas no backlog da Seção 6.2 do `GestaoProjeto.md`.

Os testes automatizados já existentes nesta sprint — da bancada de teste do caminho de consulta — estão documentados na Seção 8.4.

Antes da escrita dos planos específicos, o projeto fixa o ferramental de teste a ser utilizado. Essa definição evita que os planos descrevam formas de execução incompatíveis com a stack registrada na Seção 3.4 e com a estrutura atual do repositório, composta por backend em Python/FastAPI, bancada web em React para validação do fluxo de consulta, scripts SQL PostgreSQL e notebook de avaliação do classificador de intenções.

| Tipo de teste | Ferramenta ou biblioteca adotada | Aplicação no projeto | Justificativa |
|---|---|---|---|
| Testes funcionais | `pytest` com `fastapi.testclient.TestClient` | Validar endpoints da API, respostas HTTP, contratos de entrada e saída, tratamento de erros e comportamento esperado dos fluxos principais do MVP. | O backend já utiliza Python e FastAPI, e a suíte existente usa `pytest`. O `TestClient` permite exercitar a aplicação FastAPI diretamente, com chamadas equivalentes a requisições HTTP, mantendo os testes automatizados, rápidos e reprodutíveis. |
| Testes de integração | `pytest`, `TestClient` e duplos de teste para fronteiras externas | Verificar a integração entre API, camada Gemini, recuperação de contexto em dados simulados do SharePoint e regras de composição da resposta, sem depender de chave externa ou internet durante a execução padrão. | A estratégia já adotada na Seção 8.4 isola chamadas de rede e testa o código do projeto. Isso protege a reprodutibilidade, respeita o uso de dados sintéticos e evita que falhas de serviços externos sejam confundidas com falhas da aplicação. |
| Testes de desempenho | `Locust` | Simular usuários concorrentes acessando os endpoints HTTP da prova de conceito, especialmente o fluxo de chat/consulta, registrando tempo de resposta, taxa de erro e comportamento sob carga controlada. | O Locust é compatível com a stack Python, descreve cenários em código e é adequado para APIs HTTP. A escolha permite reaproveitar conhecimento da equipe, versionar cenários no repositório e comparar execuções entre sprints. |
| Testes de usabilidade | Microsoft Forms | Coletar respostas do questionário SUS, percepção dos participantes e comentários qualitativos após a execução dos roteiros de teste. | A solução prioriza o ecossistema Microsoft do parceiro. O Forms permite distribuição por link ou Teams, controle de respondentes quando necessário e consolidação simples das respostas para análise posterior. |

As ferramentas escolhidas também respeitam os requisitos não funcionais já definidos: os testes automatizados devem usar dados sintéticos ou anonimizados, a validação funcional deve preservar rastreabilidade entre cenário e requisito, e os testes de desempenho devem registrar evidências objetivas de latência e falha. Chamadas a provedores externos, quando indispensáveis para uma validação específica, devem ser tratadas como execução controlada, separada da suíte determinística padrão.

## 9.1 Testes Funcionais

O plano de testes funcionais valida o comportamento observável definido pelos critérios de aceitação da Seção 3.1. A cobertura contempla RF01 a RF10, incluindo a proatividade controlada de RF09 e RF10 disponível na versão entregue. Cada requisito possui ao menos um cenário positivo, que confirma o fluxo esperado, e um cenário negativo, que exercita entrada inválida, ausência de dados, estado desabilitado ou rota não suportada.

### 9.1.1 Estratégia e preparação

Os testes são de sistema, orientados a cenários e executados pela interface disponível ou, quando aplicável, pela API do backend. Cada caso declara propósito, entrada e execução específica e resultado esperado; essas informações complementam o procedimento comum abaixo e devem ser seguidas na ordem apresentada. A evidência de cada execução deve registrar o identificador do caso, data, responsável, versão ou *commit* testado, ambiente, entrada utilizada, saída obtida, resultado (aprovado, reprovado ou bloqueado) e captura de tela ou registro da requisição. Os dados de teste devem permanecer sintéticos ou anonimizados, em conformidade com o RNF01.

**Ferramentas e massa de teste:** o backend é iniciado com FastAPI/Uvicorn e seus testes de regressão são executados com `pytest`; a interface é iniciada com Vite (`npm run dev`) e verificada antes da execução com `npm run lint` e `npm run build`. Os testes funcionais usam uma massa controlada, com os projetos sintéticos `XPTO` e `ABC`, seus prazos, riscos e status, e sem os atributos de patrocinador e custo final. A massa também deve conter uma intenção com fluxo automatizado e uma intenção do escopo sem automação. Essa massa é pré-requisito do plano: os JSONs atualmente versionados no backend representam atendimento ao passageiro e não substituem os dados de portfólio exigidos por estes casos.

**Pré-condições comuns:** ambiente do MVP em execução; massa de projetos acima carregada; catálogo de intenções e rotas configurado; e acesso à interface ou à documentação da API. Para casos que usam uma rota automatizada, deve haver uma intenção de teste cadastrada com essa rota. Para os demais, deve haver uma intenção do escopo sem automação, capaz de receber contexto estruturado.

**Procedimento comum de execução:** (1) registrar o *commit* e o ambiente sob teste; (2) em `src/backend`, instalar as dependências de `requirements.txt` e executar `python -m pytest app/tests`; (3) iniciar a API FastAPI e a interface conforme a Seção 6.2.8 e, em `src/frontend`, executar `npm run lint` e `npm run build`; (4) selecionar ou autenticar o perfil de teste, se a versão em validação o exigir; (5) restaurar a massa sintética conhecida; (6) executar exatamente a entrada e as verificações do caso; (7) comparar resposta, código HTTP e registros internos com o resultado esperado; e (8) salvar a evidência identificada pelo ID do caso. Uma execução é aprovada somente quando todos os resultados esperados forem observados; qualquer divergência reprova o caso e deve ser registrada sem alterar a expectativa retrospectivamente.

### 9.1.2 Matriz de rastreabilidade

| Requisito | Critérios de aceitação verificados | Casos de teste |
|---|---|---|
| RF01 | CA01.1 texto em linguagem natural; CA01.2 áudio convertido em texto; CA01.3 sem sintaxe técnica; CA01.4 encaminhamento ao PLN | CT-RF01-01, CT-RF01-02 |
| RF02 | CA02.1 processamento semântico; CA02.2 identificação da intenção primária; CA02.3 encaminhamento para classificação | CT-RF02-01, CT-RF02-02 |
| RF03 | CA03.1 associação ao catálogo; CA03.2 categorias consulta/transação/alerta; CA03.3 indicação de fluxo; CA03.4 tratamento fora de escopo | CT-RF03-01, CT-RF03-02 |
| RF04 | CA04.1 consulta a dados sintéticos; CA04.2 recuperação relevante; CA04.3 uso como contexto | CT-RF04-01, CT-RF04-02 |
| RF05 | CA05.1 resposta a consulta; CA05.2 considera projeto/contexto; CA05.3 usa informação recuperada; CA05.4 declara indisponibilidade | CT-RF05-01, CT-RF05-02 |
| RF06 | CA06.1 identifica análise/comparação; CA06.2 compara dois ou mais projetos; CA06.3 considera critérios solicitados; CA06.4 fundamenta nos dados | CT-RF06-01, CT-RF06-02 |
| RF07 | CA07.1 envia intenção/parâmetros ao fluxo; CA07.2 não usa LLM no fluxo; CA07.3 envia somente intenção/contexto validado ao LLM; CA07.4 demonstra ambas as rotas | CT-RF07-01, CT-RF07-02 |
| RF08 | CA08.1 retorno do fluxo/estado; CA08.2 LLM limitado ao contexto validado; CA08.3 não inventa fatos; CA08.4 declara insuficiência; CA08.5 estrutura/referências; CA08.6 separa fatos de interpretação | CT-RF08-01, CT-RF08-02 |
| RF09 | CA09.1 somente intenção sem automação e proatividade ativa; CA09.2 intenção secundária compatível; CA09.3 sugestão separada e opcional; CA09.4 confirmação antes da execução; CA09.5 recusa preserva resposta; CA09.6 ausência de sugestão compatível | CT-RF09-01, CT-RF09-02 |
| RF10 | CA10.1 controle ativado/desativado; CA10.2 estado vale nas interações seguintes; CA10.3 desativado não sugere; CA10.4 intenção primária permanece funcional | CT-RF10-01, CT-RF10-02 |

### 9.1.3 Casos de teste

#### RF01 — Entrada de comandos em linguagem natural

| ID | Cenário | Propósito | Entrada e execução específica | Resultado esperado |
|---|---|---|---|---|
| CT-RF01-01 | Positivo | Confirmar que entradas textual e em áudio, em linguagem natural e sem sintaxe técnica, entram no pipeline. | Enviar `Qual é o prazo do projeto XPTO?`; em seguida, enviar áudio com a mesma frase e verificar a transcrição antes do processamento. | Ambas as entradas são aceitas, preservam o texto (original ou transcrito) e são encaminhadas ao PLN; não é exigida sintaxe de consulta. |
| CT-RF01-02 | Negativo | Confirmar tratamento de entrada vazia ou composta apenas por espaços. | Após o procedimento comum, enviar campo vazio ou `   `. | A solicitação não é encaminhada ao PLN; o sistema informa que é necessário fornecer uma pergunta ou comando válido. |

#### RF02 — Identificação semântica da intenção

| ID | Cenário | Propósito | Entrada e execução específica | Resultado esperado |
|---|---|---|---|---|
| CT-RF02-01 | Positivo | Verificar a identificação da intenção primária de uma consulta de projeto. | Enviar: `Mostre o status do projeto XPTO`. Inspecionar a resposta e o registro do pipeline. | A intenção primária de consulta de status é identificada e encaminhada para a classificação no catálogo. |
| CT-RF02-02 | Negativo | Verificar que texto ambíguo ou sem objetivo de negócio não recebe uma intenção de domínio indevida. | Enviar: `bom dia, tudo certo?`. | O sistema não atribui uma intenção de projeto como fato; encaminha para tratamento de fora de escopo ou orienta a reformulação. |

#### RF03 — Classificação e associação ao catálogo

| ID | Cenário | Propósito | Entrada e execução específica | Resultado esperado |
|---|---|---|---|---|
| CT-RF03-01 | Positivo | Confirmar associação ao catálogo, suas categorias mínimas e a informação de rota. | No catálogo, verificar uma entrada de consulta, uma de transação e uma de alerta; enviar para cada uma sua frase de teste cadastrada e consultar o registro de classificação. | Cada registro contém intenção, categoria correta e indicação de existência de fluxo automatizado; o catálogo possui as três categorias. |
| CT-RF03-02 | Negativo | Confirmar o limite explícito para intenção não suportada. | Enviar: `Reserve uma sala de reunião para amanhã`. | Não é criada associação fictícia ao catálogo; o sistema informa que a solicitação está fora do escopo ou pede reformulação. |

#### RF04 — Recuperação de informações

| ID | Cenário | Propósito | Entrada e execução específica | Resultado esperado |
|---|---|---|---|---|
| CT-RF04-01 | Positivo | Verificar a recuperação de conteúdo relevante da base sintética. | Enviar: `Qual é o prazo do projeto XPTO?` e consultar as fontes ou trechos associados à resposta. | O pipeline consulta a base sintética, recupera trecho relacionado ao projeto XPTO e o disponibiliza como contexto da resposta. |
| CT-RF04-02 | Negativo | Verificar que uma chave de projeto inexistente não produz recuperação inventada. | Enviar: `Qual é o prazo do projeto INEXISTENTE-999?`. | Nenhuma informação não relacionada é apresentada como se fosse do projeto solicitado; a ausência de dados é registrada e comunicada. |

#### RF05 — Consulta de informações dos projetos

| ID | Cenário | Propósito | Entrada e execução específica | Resultado esperado |
|---|---|---|---|---|
| CT-RF05-01 | Positivo | Confirmar resposta a uma consulta simples usando o contexto do projeto pedido. | Enviar: `Qual é o status do projeto XPTO?`. | A resposta apresenta o status disponível para XPTO e faz referência ao contexto ou fonte recuperada. |
| CT-RF05-02 | Negativo | Confirmar declaração explícita quando o dado solicitado não existe na base. | Enviar uma consulta válida sobre atributo não cadastrado, por exemplo `Quem é o patrocinador do projeto XPTO?`, quando esse atributo não estiver na massa. | O sistema informa a indisponibilidade da informação; não completa a resposta com suposição. |

#### RF06 — Análise e comparação de projetos

| ID | Cenário | Propósito | Entrada e execução específica | Resultado esperado |
|---|---|---|---|---|
| CT-RF06-01 | Positivo | Verificar comparação fundamentada de dois projetos segundo critérios pedidos. | Enviar: `Compare os prazos e riscos dos projetos XPTO e ABC`. | A resposta distingue os dois projetos, aborda prazo e risco e aponta os dados ou fontes que sustentam a comparação. |
| CT-RF06-02 | Negativo | Verificar tratamento quando um participante da comparação não existe ou não contém o critério solicitado. | Enviar: `Compare os riscos dos projetos XPTO e INEXISTENTE-999`. | O sistema não cria comparação parcial enganosa; identifica qual dado está ausente e limita a conclusão. |

#### RF07 — Roteamento híbrido das intenções

| ID | Cenário | Propósito | Entrada e execução específica | Resultado esperado |
|---|---|---|---|---|
| CT-RF07-01 | Positivo | Confirmar que intenção com fluxo automatizado usa a rota direta, sem LLM. | Selecionar no catálogo a entrada automatizada da massa e enviar sua frase de teste cadastrada; inspecionar o registro de roteamento e o resultado da ação simulada. | A rota automatizada recebe a intenção e os parâmetros estruturados, devolve seu estado de conclusão e o registro não contém chamada ao LLM. |
| CT-RF07-02 | Negativo | Confirmar que intenção válida sem automação não é enviada ao fluxo automatizado nem recebe contexto não validado. | Enviar uma consulta do escopo cadastrada sem automação, como `Qual é o prazo do projeto XPTO?`, e inspecionar o registro. | O sistema envia ao LLM somente a intenção e o contexto estruturado recuperado; não executa fluxo automatizado. |

#### RF08 — Respostas estruturadas e fundamentadas

| ID | Cenário | Propósito | Entrada e execução específica | Resultado esperado |
|---|---|---|---|---|
| CT-RF08-01 | Positivo | Verificar estrutura e fundamentação dos retornos do LLM e do fluxo automatizado. | Executar CT-RF06-01 e CT-RF07-01; avaliar o retorno completo, suas fontes e o estado da ação simulada. | O retorno do fluxo informa a ação e seu estado; o retorno do LLM usa somente o contexto recuperado, separa dados de interpretação e preserva as referências disponíveis. |
| CT-RF08-02 | Negativo | Verificar que informação sem suporte não é apresentada como fato. | Enviar: `Qual será o custo final do projeto XPTO?` quando a base não possuir previsão de custo final. | A resposta informa insuficiência de dados ou impossibilidade de concluir; não cria valor, fonte ou certeza inexistentes. |

#### RF09 — Sugestão proativa de intenção secundária

| ID | Cenário | Propósito | Entrada e execução específica | Resultado esperado |
|---|---|---|---|---|
| CT-RF09-01 | Positivo | Confirmar que uma consulta sem fluxo automatizado pode gerar uma sugestão opcional compatível, sem retirar do usuário o controle da execução. | Ativar a proatividade; enviar `Qual é o status do projeto XPTO?` usando uma intenção primária do catálogo sem automação e com intenção secundária compatível; registrar a resposta antes de confirmar a sugestão; então selecionar a confirmação. | A resposta principal é concluída normalmente; a sugestão aparece em bloco separado, identificada como opcional e vinculada a uma intenção cadastrada; nenhuma ação secundária ocorre antes da confirmação; depois dela, somente a intenção sugerida é encaminhada à rota prevista. |
| CT-RF09-02 | Negativo | Verificar que o sistema não inventa nem executa sugestão quando falta condição para oferecê-la. | Com a proatividade ativa, executar duas variações: (a) usar uma intenção sem secundária compatível; (b) usar uma intenção com sugestão e selecionar a recusa. Comparar resposta e registros de roteamento. | Na variação (a), somente a resposta principal é devolvida e nenhuma sugestão fictícia é criada; na (b), a recusa encerra a sugestão sem executar a intenção secundária e sem alterar a resposta principal. |

#### RF10 — Controle da proatividade

| ID | Cenário | Propósito | Entrada e execução específica | Resultado esperado |
|---|---|---|---|---|
| CT-RF10-01 | Positivo | Confirmar que o controle de proatividade altera o comportamento das interações posteriores. | Abrir a configuração; registrar o estado inicial; ativar a proatividade; iniciar nova consulta elegível à sugestão do CT-RF09-01; desativar a opção e repetir a mesma consulta em uma nova interação. | O controle exibe os dois estados e persiste a escolha; com a opção ativa, a sugestão compatível é exibida; após desativá-la, a nova interação mantém a resposta primária, mas não apresenta sugestão. |
| CT-RF10-02 | Negativo | Confirmar que desativar sugestões não desativa nem degrada o processamento principal. | Manter a proatividade desativada e executar uma consulta simples, uma comparação e uma solicitação fora do escopo. Inspecionar intenção, rota e resposta de cada execução. | As intenções primárias continuam sendo identificadas, roteadas e respondidas conforme RF02 a RF08; nenhuma sugestão do RF09 aparece e o estado desativado não provoca erro nem altera o tratamento de fora do escopo. |

### 9.1.4 Abrangência e limitações

O plano cobre os dez requisitos funcionais e os três regimes principais do produto: entrada e entendimento (RF01 a RF03), recuperação e resposta fundamentada (RF04 a RF08) e proatividade controlada (RF09 e RF10). A combinação de um caso positivo e um negativo por requisito produz vinte casos rastreáveis. Os positivos percorrem texto, áudio, consulta, comparação, fluxo automatizado, rota com LLM e sugestão opcional. Os negativos concentram-se nas fronteiras de maior risco: entrada vazia ou ambígua, intenção fora do catálogo, projeto ou atributo inexistente, contexto não validado, resposta sem fundamento, sugestão incompatível, recusa e proatividade desativada.

A abrangência é adequada ao planejamento sistêmico porque cada critério de aceitação da Seção 3.1 aparece na matriz e é observado em pelo menos um resultado esperado. Ela não pretende substituir testes unitários de todas as funções nem combinações exaustivas de frases, perfis e documentos. Variações linguísticas e métricas quantitativas do classificador pertencem aos RNF06 e RNF07; desempenho, segurança, acessibilidade, usabilidade e confiabilidade quantitativa pertencem às Seções 9.2 e 9.3.

RF09 e RF10 possuem implementação observável pela interface e pela rota de confirmação, portanto seus casos devem ser executados e não podem mais ser marcados como bloqueados por ausência da funcionalidade. A validação de voz do RF01 depende do endpoint de áudio especificado na Seção 8.7, disponível na versão executada na Sprint 4.

### 9.1.5 Execução e consolidação dos testes funcionais

A execução da Sprint 4 consolidou os resultados dos casos definidos na Seção 9.1.3 para os requisitos RF01 a RF10. Foram preservados o propósito, o cenário positivo ou negativo, a entrada, o resultado esperado e a rastreabilidade de cada caso. A classificação foi realizada somente após a comparação entre o comportamento esperado e o comportamento observado; uma resposta HTTP `200`, isoladamente, não foi considerada suficiente para aprovar um caso.

Foram executados **20 de 20 casos planejados**, sem casos `BLOQUEADO` ou `NÃO EXECUTADO`. Na rodada de 23/09/2026, 15 casos foram aprovados e 5 falharam. A falha do CT-RF09-01 veio de um defeito já registrado na Seção 9.2.7, o `DEF-RNF04-02`, que foi corrigido; no reteste, o caso foi aprovado. O resultado consolidado é de **16 casos APROVADOS (80%)** e **4 casos que FALHARAM (20%)**.

As evidências desta execução são mantidas em `src/backend/evidencias/rf01-rf10/`. Para chamadas de API, os registros textuais são a evidência principal, pois preservam os campos observados durante a execução. Capturas de tela são usadas como evidência complementar nos cenários de áudio e controle de proatividade.

#### 9.1.5.1 Ambiente e protocolo de execução

| Item                                | Configuração observada                                                            |
|:------------------------------------|:----------------------------------------------------------------------------------|
| Data da rodada                      | 23/09/2026; os registros com horário vão das 20:59 às 21:42                       |
| Responsável                         | Wendel Feitosa                                                                    |
| Versão testada                      | commit `be814f6` da `develop`, base da branch `test/executa-rfs`                  |
| Backend                             | FastAPI/Uvicorn em `http://127.0.0.1:8000`                                        |
| Verificação de saúde                | `/health` retornando HTTP `200` e `{"status":"ok"}`                               |
| Python                              | 3.12.x                                                                            |
| Provedor da rodada funcional válida | OpenRouter                                                                        |
| Modelo generativo                   | `google/gemini-3.7-flash`, com limite de 512 tokens de saída, padrão dessa versão |
| Recuperação                         | RAG sobre os extratos documentais sintéticos (`source_extracts`, no Supabase)     |
| Projetos utilizados                 | `PRJ-0442` e `PRJ-0510`                                                           |
| Projeto inexistente de controle     | `INEXISTENTE-999`                                                                 |
| Autenticação da proatividade        | Bearer de identidade simulada configurado no ambiente; valor não versionado       |
| Reteste do CT-RF09-01               | 24/09/2026, commit `c793983`, limite de 1024 tokens                               |

A execução utilizou os estados `APROVADO`, `FALHOU`, `BLOQUEADO` e `NÃO EXECUTADO`. Os testes não foram alterados para forçar aprovação. Quando o caminho estava disponível e a resposta divergiu do critério funcional, o caso foi registrado como `FALHOU`. Os comandos para reproduzir os casos de API estão no README da pasta de evidências.

Três pontos da execução diferem do plano da Seção 9.1.3, sem mudar o resultado esperado de nenhum caso. Os projetos `XPTO` e `ABC` do plano não existem no banco, que tem apenas `PRJ-0442`, `PRJ-0510` e `PRJ-0587`; foram substituídos por `PRJ-0442` e `PRJ-0510`, e `INEXISTENTE-999` segue como controle. No CT-RF09-01, a consulta de status do plano deu lugar a uma consulta de prazo; as duas intenções têm intenção secundária compatível no catálogo. No CT-RF03-01, o catálogo não tem campo de frase de teste cadastrada, e foram usadas frases representativas das descrições das intenções.

A massa sintética fica em dois lugares. As tabelas estruturadas do banco guardam progresso, riscos e marcos de `PRJ-0442`, `PRJ-0510` e `PRJ-0587`, mas só o módulo de relatórios as lê. A recuperação do chat consulta os extratos documentais, e nessa base só o `PRJ-0442` tem documento: há 1 extrato dele, 8 sem projeto e nenhum do `PRJ-0510`. Essa condição foi mantida durante os testes e explica a falha do RF06.

#### 9.1.5.2 Resultado consolidado

| Requisito | Caso positivo                | Caso negativo                | Resultado                     |
|:----------|:-----------------------------|:-----------------------------|:------------------------------|
| RF01      | CT-RF01-01 — **APROVADO**    | CT-RF01-02 — **APROVADO**    | 2/2 aprovados                 |
| RF02      | CT-RF02-01 — **FALHOU**      | CT-RF02-02 — **APROVADO**    | 1 aprovado / 1 falhou         |
| RF03      | CT-RF03-01 — **APROVADO**    | CT-RF03-02 — **FALHOU**      | 1 aprovado / 1 falhou         |
| RF04      | CT-RF04-01 — **APROVADO**    | CT-RF04-02 — **APROVADO**    | 2/2 aprovados                 |
| RF05      | CT-RF05-01 — **APROVADO**    | CT-RF05-02 — **APROVADO**    | 2/2 aprovados                 |
| RF06      | CT-RF06-01 — **FALHOU**      | CT-RF06-02 — **APROVADO**    | 1 aprovado / 1 falhou         |
| RF07      | CT-RF07-01 — **APROVADO**    | CT-RF07-02 — **APROVADO**    | 2/2 aprovados                 |
| RF08      | CT-RF08-01 — **FALHOU**      | CT-RF08-02 — **APROVADO**    | 1 aprovado / 1 falhou         |
| RF09      | CT-RF09-01 — **APROVADO**¹   | CT-RF09-02 — **APROVADO**    | 2/2 aprovados                 |
| RF10      | CT-RF10-01 — **APROVADO**    | CT-RF10-02 — **APROVADO**    | 2/2 aprovados                 |
| **Total** | **8 aprovados / 2 falharam** | **8 aprovados / 2 falharam** | **16 aprovados / 4 falharam** |

¹ Falhou na rodada de 23/09, pelo `DEF-RNF04-02`, e foi aprovado no reteste depois da correção. Na rodada, o total foi de 15 aprovados e 5 falharam.

#### 9.1.5.3 Resultados detalhados

##### RF01 — Entrada de comandos em linguagem natural

| ID         | Cenário  | Entrada executada                                                            | Resultado esperado                                                              | Resultado observado                                                                                                                                                                                                                              | Status       | Evidência                                                                          |
|:-----------|:---------|:-----------------------------------------------------------------------------|:--------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------|:-----------------------------------------------------------------------------------|
| CT-RF01-01 | Positivo | Texto `Qual é o prazo do projeto PRJ-0442?` e áudio com a mesma solicitação. | Texto e áudio são aceitos e encaminhados ao PLN sem sintaxe técnica.            | Texto retornou HTTP `200`, `CONSULTA / consulta_cronograma_prazo`, entidade `PRJ-0442` e prazo de 24/08/2026 a 28/08/2026. O áudio foi transcrito e processado; apesar da aproximação fonética do identificador, o pipeline resolveu `PRJ-0442`. | **APROVADO** | `src/backend/evidencias/rf01-rf10/rf01/CT-RF01-01-texto.txt` e `CT-RF01-01-audio.png` |
| CT-RF01-02 | Negativo | Mensagem vazia ou composta apenas por espaços.                               | A solicitação não é encaminhada ao PLN e o sistema solicita uma entrada válida. | HTTP `422`, código `INVALID_INPUT`, com mensagem para informar uma mensagem válida.                                                                                                                                                              | **APROVADO** | `src/backend/evidencias/rf01-rf10/rf01/CT-RF01-02-vazio.txt`                          |

A diferença fonética observada no STT de CT-RF01-01 foi registrada como observação de qualidade, pois o projeto correto foi resolvido pelo pipeline e o processamento funcional foi concluído.

##### RF02 — Identificação semântica da intenção

| ID         | Cenário  | Entrada executada                     | Resultado esperado                                                                  | Resultado observado                                                                                                                                                                                          | Status       | Evidência                                                       |
|:-----------|:---------|:--------------------------------------|:------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------|:----------------------------------------------------------------|
| CT-RF02-01 | Positivo | `Mostre o status do projeto PRJ-0442` | Identificar a intenção primária de consulta de status e encaminhá-la ao catálogo.   | HTTP `200`, porém `specific=""`. A confiança da macro foi `0.5372`; `transacao_atualizar_status` apareceu com `0.4108` e `consulta_status_projeto` com `0.403`, sem seleção da intenção específica esperada. | **FALHOU**   | `src/backend/evidencias/rf01-rf10/rf02/CT-RF02-01-status.txt`      |
| CT-RF02-02 | Negativo | `bom dia, tudo certo?`                | Não atribuir intenção de projeto; tratar como fora de escopo ou pedir reformulação. | `FORA_DE_ESCOPO`, `model=classificador-local`, zero tokens, nenhuma fonte e orientação de reformulação.                                                                                                      | **APROVADO** | `src/backend/evidencias/rf01-rf10/rf02/CT-RF02-02-fora-escopo.txt` |

CT-RF02-01 demonstra que uma resposta semanticamente relacionada não é suficiente para aprovação quando a intenção primária exigida pelo critério não é identificada.

##### RF03 — Classificação e associação ao catálogo

| ID         | Cenário  | Entrada executada                                          | Resultado esperado                                                                          | Resultado observado                                                                                                                                                                                           | Status       | Evidência                                                        |
|:-----------|:---------|:-----------------------------------------------------------|:--------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------|:-----------------------------------------------------------------|
| CT-RF03-01 | Positivo | Consulta de prazo; geração de relatório; alerta de atraso. | Demonstrar as categorias consulta, transação e alerta, com associação às respectivas rotas. | Prazo → `CONSULTA / consulta_cronograma_prazo` (`0.9443`); relatório → `TRANSACAO / transacao_gerar_relatorio` (`0.8773`, `workflow-router`, tokens `0`); atraso → `ALERTA / alerta_prazo_atraso` (`0.7645`). | **APROVADO** | `src/backend/evidencias/rf01-rf10/rf03/CT-RF03-01-categorias.txt`   |
| CT-RF03-02 | Negativo | `Reserve uma sala de reunião para amanhã`                  | Não associar ficticiamente ao catálogo; informar fora de escopo ou pedir reformulação.      | HTTP `200`, classificado como `TRANSACAO / transacao_agendar_compromisso`, confiança específica `0.7335`, com continuidade da interação.                                                                      | **FALHOU**   | `src/backend/evidencias/rf01-rf10/rf03/CT-RF03-02-reserva-sala.txt` |

O artefato de catálogo inspecionado contém intenções, categorias e fluxos, mas não apresenta um campo explícito de “frase de teste cadastrada”. Por isso, CT-RF03-01 foi executado com frases representativas alinhadas às descrições das intenções, sem afirmar que essas frases estavam cadastradas literalmente.

##### RF04 — Recuperação de informações

| ID         | Cenário  | Entrada executada                            | Resultado esperado                                                            | Resultado observado                                                                                                                                                         | Status       | Evidência                                                       |
|:-----------|:---------|:---------------------------------------------|:------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------|:----------------------------------------------------------------|
| CT-RF04-01 | Positivo | `Qual é o prazo do projeto PRJ-0442?`        | Recuperar trecho relacionado ao projeto e utilizá-lo como contexto.           | A fonte principal foi `Operacao assistida na Linha Azul`, vinculada a `Comunicados de Servico / PRJ-0442`, score `8.0`. Uma fonte não relacionada apareceu com score `2.0`. | **APROVADO** | `src/backend/evidencias/rf01-rf10/rf04/CT-RF04-01-recuperacao.txt` |
| CT-RF04-02 | Negativo | `Qual é o prazo do projeto INEXISTENTE-999?` | Não atribuir informação de outro projeto ao inexistente e comunicar ausência. | O sistema declarou que não havia informação para `INEXISTENTE-999`. Fontes de baixo score foram recuperadas, mas não foram atribuídas ao projeto inexistente.               | **APROVADO** | `src/backend/evidencias/rf01-rf10/rf04/CT-RF04-02-inexistente.txt` |

Foi observado ruído de recuperação em fontes secundárias de baixo score. Como a resposta final preservou a separação entre o projeto solicitado e o conteúdo não relacionado, o comportamento não alterou a classificação dos casos.

##### RF05 — Consulta de informações dos projetos

| ID         | Cenário  | Entrada executada                            | Resultado esperado                                                 | Resultado observado                                                                                                                    | Status       | Evidência                                                        |
|:-----------|:---------|:---------------------------------------------|:-------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------|:-------------|:-----------------------------------------------------------------|
| CT-RF05-01 | Positivo | `Qual é o status do projeto PRJ-0442?`       | Apresentar o status disponível e referência ao contexto ou fonte.  | HTTP `200`, status `Programado`, fonte relacionada a `PRJ-0442` e `CONSULTA / consulta_status_projeto`, confiança específica `0.8492`. | **APROVADO** | `src/backend/evidencias/rf01-rf10/rf05/CT-RF05-01-status.txt`       |
| CT-RF05-02 | Negativo | `Quem é o patrocinador do projeto PRJ-0442?` | Informar indisponibilidade sem completar a resposta com suposição. | O sistema declarou contexto insuficiente e não inventou patrocinador.                                                                  | **APROVADO** | `src/backend/evidencias/rf01-rf10/rf05/CT-RF05-02-patrocinador.txt` |

A diferença entre `Mostre o status...`, que falhou em CT-RF02-01, e `Qual é o status...`, corretamente classificado neste caso, reforça a sensibilidade lexical registrada no defeito DEF-RF02-01.

##### RF06 — Análise e comparação de projetos

| ID         | Cenário  | Entrada executada                                             | Resultado esperado                                                      | Resultado observado                                                                                                                           | Status       | Evidência                                                                  |
|:-----------|:---------|:--------------------------------------------------------------|:------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------|:-------------|:---------------------------------------------------------------------------|
| CT-RF06-01 | Positivo | `Compare os prazos e riscos dos projetos PRJ-0442 e PRJ-0510` | Distinguir os dois projetos, abordar prazo e risco e fundamentar ambos. | A intenção `comparacao_entre_projetos` (`0.7847`) e os dois IDs foram reconhecidos, porém a resposta e as fontes cobriram somente `PRJ-0442`. | **FALHOU**   | `src/backend/evidencias/rf01-rf10/rf06/CT-RF06-01-comparacao.txt`             |
| CT-RF06-02 | Negativo | `Compare os riscos dos projetos PRJ-0442 e INEXISTENTE-999`   | Identificar a ausência e limitar a conclusão.                           | O sistema informou contexto insuficiente, identificou o projeto inexistente e não inventou uma comparação completa.                           | **APROVADO** | `src/backend/evidencias/rf01-rf10/rf06/CT-RF06-02-comparacao-inexistente.txt` |

A falha do CT-RF06-01 vem da base consultada pelo chat, e não da recuperação com vários projetos. O `PRJ-0510` tem progresso, riscos e marcos nas tabelas estruturadas, que o chat não lê, e nenhum documento entre os extratos que ele consulta (Seção 9.1.5.1). Com contexto só do `PRJ-0442`, a resposta não tinha como comparar os dois.

##### RF07 — Roteamento híbrido das intenções

| ID         | Cenário  | Entrada executada                                         | Resultado esperado                                                                      | Resultado observado                                                                                                                                         | Status       | Evidência                                                    |
|:-----------|:---------|:----------------------------------------------------------|:----------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------|:-------------------------------------------------------------|
| CT-RF07-01 | Positivo | `Gere um relatório de acompanhamento do projeto PRJ-0442` | Utilizar rota automatizada, com intenção e parâmetros estruturados, sem chamada ao LLM. | `TRANSACAO / transacao_gerar_relatorio`, `model=workflow-router`, tokens `0`, `workflow.kind=guided_workflow`, `workflow.action=start` e escopo `PRJ-0442`. | **APROVADO** | `src/backend/evidencias/rf01-rf10/rf07/CT-RF07-01-workflow.txt` |
| CT-RF07-02 | Negativo | `Qual é o prazo do projeto PRJ-0442?`                     | Utilizar contexto recuperado + LLM, sem executar fluxo automatizado.                    | Modelo Gemini, uso de tokens, fontes RAG, `consulta_cronograma_prazo` e `workflow=null`.                                                                    | **APROVADO** | `src/backend/evidencias/rf01-rf10/rf07/CT-RF07-02-llm.txt`      |

Em CT-RF07-01, o estado observado foi `start`. A evidência demonstra o roteamento e o início do workflow; não se afirma que o relatório final foi concluído nessa etapa.

##### RF08 — Respostas estruturadas e fundamentadas

| ID         | Cenário  | Entrada executada                              | Resultado esperado                                                                          | Resultado observado                                                                                             | Status       | Evidência                                                       |
|:-----------|:---------|:-----------------------------------------------|:--------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------|:-------------|:----------------------------------------------------------------|
| CT-RF08-01 | Positivo | Reutilização de CT-RF06-01 e CT-RF07-01.       | Demonstrar retorno estruturado do fluxo e resposta LLM fundamentada no contexto recuperado. | CT-RF07-01 demonstrou o workflow corretamente, porém CT-RF06-01 não fundamentou a comparação dos dois projetos. | **FALHOU**   | `src/backend/evidencias/rf01-rf10/rf08/CT-RF08-01-consolidado.txt` |
| CT-RF08-02 | Negativo | `Qual será o custo final do projeto PRJ-0442?` | Declarar insuficiência sem inventar valor, fonte ou certeza.                                | O sistema declarou ausência de previsão de custo final e não criou valor numérico.                              | **APROVADO** | `src/backend/evidencias/rf01-rf10/rf08/CT-RF08-02-custo-final.txt` |

A falha de CT-RF08-01 decorre da mesma causa raiz identificada em CT-RF06-01 e, por isso, não foi tratada como um defeito independente.

##### RF09 — Sugestão proativa de intenção secundária

| ID         | Cenário  | Entrada executada                                                                                                   | Resultado esperado                                                                                                         | Resultado observado                                                                                                                                                                                    | Status       | Evidência                                                                                     |
|:-----------|:---------|:--------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------|:----------------------------------------------------------------------------------------------|
| CT-RF09-01 | Positivo | Proatividade ativa; consulta `Qual é o prazo do projeto PRJ-0442?`; registro da sugestão; confirmação com `accept`. | Resposta principal normal; sugestão separada e opcional; nenhuma execução antes da confirmação; processamento após aceite. | A resposta principal foi preservada e retornou `sugerir_recuperacao_prazo`, `requires_confirmation=true`. A confirmação em `/api/chat/proactive-confirmation` retornou HTTP `200` e `status=accepted`, mas a resposta ao aceite foi cortada e a ação sugerida não chegou ao usuário. No reteste, as cinco respostas ao aceite chegaram inteiras. | **FALHOU** na rodada; **APROVADO** no reteste | `src/backend/evidencias/rf01-rf10/rf09/CT-RF09-01-sugestao.txt`, `CT-RF09-01-accept.txt` e `CT-RF09-01-reteste.txt` |
| CT-RF09-02 | Negativo | \(a\) alerta sem secundária compatível; (b) nova sugestão elegível seguida de `decline`.                            | \(a\) nenhuma sugestão fictícia; (b) recusa encerra a sugestão sem executar a ação secundária.                             | \(a\) `proactive_suggestion=null`; (b) HTTP `200`, `status=declined` e `result=null`.                                                                                                                  | **APROVADO** | `src/backend/evidencias/rf01-rf10/rf09/CT-RF09-02-sem-secundaria.txt` e `CT-RF09-02-decline.txt` |

A proatividade exige identidade. Tentativas de preparação sem Bearer válido retornaram `401` e foram tratadas como falha de pré-condição da execução, não como falha funcional. A rodada válida utilizou a identidade simulada configurada no ambiente sem registrar o valor do token.

Na rodada, a resposta ao aceite do CT-RF09-01 parou depois da primeira linha, sem a ação de recuperação: dos 508 tokens de saída, 463 foram de raciocínio, com o limite de 512. A rodada não registrou o motivo de parada, mas 508 tokens é o valor de todas as respostas encerradas pelo limite de 512 no reteste do truncamento da Seção 9.2.7, e nenhuma resposta completa chegou a esse valor. É o `DEF-RNF04-02`, registrado nessa seção. O `result.intent=null` não indica falha, porque a resposta ao aceite não traz esse campo; a intenção confirmada vai no prompt.

Depois da correção, que eleva o limite para 1024 tokens e avisa o usuário quando a resposta é interrompida, o caso foi reexecutado cinco vezes, com a mesma pergunta, no commit `c793983`. Fora os testes, o único código da aplicação alterado desde a versão da rodada é essa correção. Nas cinco repetições, a sugestão exigiu confirmação e a resposta ao aceite chegou inteira, com 436 a 694 tokens de saída; três delas teriam sido cortadas com o limite anterior. Em todas, o agente procurou a atividade crítica e declarou que as fontes não registram atraso que sustente uma ação de recuperação, sem inventar dados.

##### RF10 — Controle da proatividade

| ID         | Cenário  | Entrada executada                                                                                            | Resultado esperado                                                            | Resultado observado                                                                                                                   | Status       | Evidência                                                                               |
|:-----------|:---------|:-------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------|:-------------|:----------------------------------------------------------------------------------------|
| CT-RF10-01 | Positivo | Pela interface: registrar OFF, ativar ON, consultar prazo, desativar e repetir a consulta em nova interação. | Com ON, exibir sugestão; com OFF, preservar a resposta primária sem sugestão. | ON exibiu a resposta principal e o bloco `Sugestão opcional`; após OFF, a mesma consulta continuou funcional e não exibiu sugestão.   | **APROVADO** | `src/backend/evidencias/rf01-rf10/rf10/CT-RF10-01-interface.txt` e quatro capturas de tela |
| CT-RF10-02 | Negativo | Com `proactivity_enabled=false`, executar consulta simples, comparação e saudação.                           | Preservar processamento primário e não produzir sugestão.                     | Os três fluxos retornaram HTTP `200`, foram classificados/roteados conforme seus cenários e apresentaram `proactive_suggestion=null`. | **APROVADO** | `src/backend/evidencias/rf01-rf10/rf10/CT-RF10-02-proatividade-off.txt`                    |

As quatro capturas de CT-RF10-01 registram, respectivamente, estado inicial OFF, estado ON, consulta ON com sugestão e nova interação OFF sem sugestão. O plano espera que o controle persista a escolha; o verificado foi a persistência nas interações seguintes da mesma sessão (CA10.2): o estado escolhido continuou valendo na nova conversa. A implementação inspecionada mantém o estado na sessão do frontend; não foi observada persistência em `localStorage`, portanto a evidência não é usada para afirmar persistência após recarregamento completo da aplicação.

#### 9.1.5.4 Defeitos identificados

| ID            | Caso(s)                 | Descrição                                                                                                                                                                          | Impacto observado                                                                                                      |
|:--------------|:------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------|
| DEF-RF02-01 | CT-RF02-01              | Sensibilidade lexical na consulta de status. `Mostre o status...` não selecionou a intenção específica, enquanto `Qual é o status...` foi corretamente classificado em CT-RF05-01. | Paráfrases semanticamente equivalentes podem produzir classificação específica diferente.                              |
| DEF-RF03-01 | CT-RF03-02              | Solicitação genérica de reserva de sala foi associada a `transacao_agendar_compromisso`.                                                                                           | O limite de domínio fica permissivo para solicitações sem vínculo com projeto ou portfólio.                            |
| DEF-RF06-01 | CT-RF06-01 e CT-RF08-01 | A comparação reconheceu os dois projetos, mas a base consultada pelo chat não tem documento do `PRJ-0510`, e o chat não lê as tabelas estruturadas em que o projeto tem dados. | Comparações com projetos sem documento na base saem parciais, com apenas um dos projetos.                              |
| DEF-RNF04-02, da Seção 9.2.7 | CT-RF09-01 | Resposta ao aceite da sugestão cortada pelo limite de 512 tokens, consumido pelo raciocínio do modelo.                                                                    | A ação sugerida não chegou ao usuário. Corrigido com o limite de 1024 e o aviso de resposta interrompida; reteste aprovado nas cinco repetições. |

Como ações de correção, recomenda-se ampliar os exemplos/paráfrases de consulta de status, fortalecer a fronteira de domínio de `transacao_agendar_compromisso` e incluir na base consultada pelo chat os extratos documentais dos demais projetos da massa, ou fazer a recuperação do chat ler também as tabelas estruturadas.

#### 9.1.5.5 Observações de qualidade e incidentes

Além das falhas funcionais, a execução revelou cinco pontos que não alteraram diretamente o status dos demais casos:

1.  **Ruído de recuperação:** fontes não relacionadas apareceram em algumas consultas com score baixo. Nos casos aprovados, a resposta final não atribuiu esse conteúdo ao projeto solicitado.
2.  **Sensibilidade lexical:** formulações semanticamente equivalentes de consulta de status produziram classificações diferentes, formalizadas em DEF-RF02-01.
3.  **Proatividade autenticada:** o caminho proativo exige identidade válida. Respostas `401` durante a preparação foram resolvidas com a identidade simulada prevista pela PoC.
4.  **Incidente de provedor:** uma tentativa anterior com a configuração inicial encontrou HTTP `429`. A rodada funcional válida foi repetida com OpenRouter e `google/gemini-3.7-flash`; o incidente permanece apenas como histórico de execução.
5.  **Resposta cortada no CT-RF10-02:** a resposta da comparação terminou no meio da frase, com 508 tokens de saída, pelo mesmo `DEF-RNF04-02`. O status não muda: o corte não depende do controle de proatividade, e a resposta já tinha declarado a insuficiência do contexto antes de parar.

#### 9.1.5.6 Organização das evidências

As evidências ficam versionadas com a seguinte organização:

``` text
src/backend/evidencias/rf01-rf10/
├── README.md
├── rf01/
│   ├── CT-RF01-01-texto.txt
│   ├── CT-RF01-01-audio.png
│   └── CT-RF01-02-vazio.txt
├── rf02/
│   ├── CT-RF02-01-status.txt
│   └── CT-RF02-02-fora-escopo.txt
├── rf03/
│   ├── CT-RF03-01-categorias.txt
│   └── CT-RF03-02-reserva-sala.txt
├── rf04/
│   ├── CT-RF04-01-recuperacao.txt
│   └── CT-RF04-02-inexistente.txt
├── rf05/
│   ├── CT-RF05-01-status.txt
│   └── CT-RF05-02-patrocinador.txt
├── rf06/
│   ├── CT-RF06-01-comparacao.txt
│   └── CT-RF06-02-comparacao-inexistente.txt
├── rf07/
│   ├── CT-RF07-01-workflow.txt
│   └── CT-RF07-02-llm.txt
├── rf08/
│   ├── CT-RF08-01-consolidado.txt
│   └── CT-RF08-02-custo-final.txt
├── rf09/
│   ├── CT-RF09-01-sugestao.txt
│   ├── CT-RF09-01-accept.txt
│   ├── CT-RF09-01-reteste.txt
│   ├── reteste_ct_rf09_01.py
│   ├── CT-RF09-02-sem-secundaria.txt
│   └── CT-RF09-02-decline.txt
└── rf10/
    ├── CT-RF10-01-interface.txt
    ├── CT-RF10-01-A-estado-inicial-off.png
    ├── CT-RF10-01-B-estado-on.png
    ├── CT-RF10-01-C-consulta-on-com-sugestao.png
    ├── CT-RF10-01-D-consulta-off-sem-sugestao.png
    └── CT-RF10-02-proatividade-off.txt
```

Os arquivos `.txt` distinguem registros consolidados de saídas brutas preservadas. Nenhuma credencial, chave, senha ou token deve ser incluído nas evidências.

#### 9.1.5.7 Matriz final de rastreabilidade

| Caso       | Resultado observado resumido                                           | Status       | Evidência principal                                  |
|:-----------|:-----------------------------------------------------------------------|:-------------|:-----------------------------------------------------|
| CT-RF01-01 | Texto e áudio chegaram ao pipeline; `PRJ-0442` foi resolvido.          | **APROVADO** | `rf01/CT-RF01-01-texto.txt` + print                  |
| CT-RF01-02 | Entrada vazia retornou `422 INVALID_INPUT`.                            | **APROVADO** | `rf01/CT-RF01-02-vazio.txt`                          |
| CT-RF02-01 | Intenção específica ficou vazia.                                       | **FALHOU**   | `rf02/CT-RF02-01-status.txt`                         |
| CT-RF02-02 | `FORA_DE_ESCOPO`, sem chamada ao LLM.                                  | **APROVADO** | `rf02/CT-RF02-02-fora-escopo.txt`                    |
| CT-RF03-01 | Consulta, transação e alerta foram reconhecidos.                       | **APROVADO** | `rf03/CT-RF03-01-categorias.txt`                     |
| CT-RF03-02 | Reserva genérica foi classificada como transação de agenda.            | **FALHOU**   | `rf03/CT-RF03-02-reserva-sala.txt`                   |
| CT-RF04-01 | Fonte vinculada a `PRJ-0442` foi recuperada.                           | **APROVADO** | `rf04/CT-RF04-01-recuperacao.txt`                    |
| CT-RF04-02 | Ausência de `INEXISTENTE-999` foi comunicada.                          | **APROVADO** | `rf04/CT-RF04-02-inexistente.txt`                    |
| CT-RF05-01 | Status, fonte e intenção específica foram retornados.                  | **APROVADO** | `rf05/CT-RF05-01-status.txt`                         |
| CT-RF05-02 | Patrocinador ausente não foi inventado.                                | **APROVADO** | `rf05/CT-RF05-02-patrocinador.txt`                   |
| CT-RF06-01 | Só o `PRJ-0442` tem documento na base do chat; a comparação saiu parcial. | **FALHOU**   | `rf06/CT-RF06-01-comparacao.txt`                     |
| CT-RF06-02 | Projeto inexistente foi identificado e a conclusão foi limitada.       | **APROVADO** | `rf06/CT-RF06-02-comparacao-inexistente.txt`         |
| CT-RF07-01 | `workflow-router`, tokens `0` e `action=start`.                        | **APROVADO** | `rf07/CT-RF07-01-workflow.txt`                       |
| CT-RF07-02 | RAG + LLM, com `workflow=null`.                                        | **APROVADO** | `rf07/CT-RF07-02-llm.txt`                            |
| CT-RF08-01 | Workflow correto, porém comparação incompleta.                         | **FALHOU**   | `rf08/CT-RF08-01-consolidado.txt`                    |
| CT-RF08-02 | Ausência de custo final foi declarada sem invenção.                    | **APROVADO** | `rf08/CT-RF08-02-custo-final.txt`                    |
| CT-RF09-01 | Sugestão exigiu confirmação; na rodada, a resposta ao aceite foi cortada; no reteste, chegou inteira nas cinco repetições. | **FALHOU** na rodada; **APROVADO** no reteste | `rf09/CT-RF09-01-accept.txt` + `CT-RF09-01-reteste.txt` |
| CT-RF09-02 | Sem sugestão incompatível; recusa retornou `declined` e `result=null`. | **APROVADO** | `rf09/CT-RF09-02-sem-secundaria.txt` + `decline.txt` |
| CT-RF10-01 | ON exibiu sugestão; OFF preservou resposta sem sugestão.               | **APROVADO** | `rf10/CT-RF10-01-interface.txt` + quatro prints      |
| CT-RF10-02 | Três fluxos primários preservados e `proactive_suggestion=null`.       | **APROVADO** | `rf10/CT-RF10-02-proatividade-off.txt`               |

#### 9.1.5.8 Conclusão

A execução cobriu integralmente os **20 casos funcionais planejados para RF01 a RF10**, sem bloqueios e sem casos não executados. Na rodada, 15 casos foram aprovados e 5 falharam. A falha do CT-RF09-01 veio do `DEF-RNF04-02`, que foi corrigido; no reteste, o caso foi aprovado. O resultado consolidado é de **16 casos aprovados e 4 casos que falharam**.

As quatro falhas em aberto foram mantidas como diagnóstico do produto e agrupadas em três causas raiz: sensibilidade lexical na classificação de status, associação indevida de uma solicitação genérica ao catálogo transacional e falta de documentos do `PRJ-0510` na base consultada pelo chat, que deixa a comparação parcial. CT-RF08-01 é consequência da mesma limitação observada em CT-RF06-01.

Os cenários negativos de ausência de informação apresentaram comportamento seguro: projeto inexistente, patrocinador não documentado e custo final ausente foram tratados sem fabricação de fatos. O roteamento híbrido também foi observado nas duas direções: workflow transacional sem geração LLM e consulta com recuperação + LLM. Por fim, RF09 e RF10 demonstraram que a sugestão secundária permanece opcional, condicionada à confirmação e ausente quando a proatividade está desabilitada.

Com isso, todos os casos possuem classificação, resultado observado, evidência associada e, quando aplicável, defeito ou observação de qualidade rastreável.

## 9.2 Testes de RNFs

### 9.2.1 Planejamento

Este plano transforma os critérios mensuráveis da Seção 3.2 em 24 casos rastreáveis: um cenário positivo e um negativo para cada RNF01 a RNF12. O cenário positivo demonstra o atributo de qualidade nas condições previstas; o negativo introduz uma violação ou falha controlada e verifica se o sistema a impede, detecta ou comunica. A execução padrão usa `pytest` e `TestClient`/`httpx`, com duplos nas fronteiras externas; o desempenho, obrigatório neste plano, é medido com `Locust`. Para o RNF06, `scikit-learn` mede F1 macro e *recall* do núcleo de PLN.

Os dados, prompts, perfis e fontes devem ser sintéticos ou anonimizados. Cada execução registra ID, data, responsável, *commit*, ambiente, massa, entrada, saída, resultado (aprovado, reprovado ou bloqueado) e caminho da evidência, sem incluir chaves, tokens ou conteúdo sensível. Antes de executar, a equipe deve congelar a massa e os critérios: resultados observados não podem ser usados para flexibilizar a meta depois da medição.

**Pré-condições comuns:** API iniciada; massa sintética versionada; duplos das integrações externas configurados; dois perfis simulados com permissões distintas; catálogo de intenções disponível; diretório de evidências identificado pela sprint e pelo *commit*; relógio do ambiente sincronizado. Dependências exclusivas de Teams, SharePoint, Entra ID ou Azure são simuladas na bancada e registradas como pendentes de homologação no ambiente do parceiro.

### 9.2.2 Matriz de rastreabilidade e critérios

| RNF | Propósito e critério objetivo de aprovação | Casos | Ferramenta e evidência mínima |
|---|---|---|---|
| RNF01 | Impedir exposição: 100% da massa é sintética/anonimizada e nenhum dado marcado como sensível chega a serviço não homologado. | CT-RNF01-P, CT-RNF01-N | `pytest`, inventário da massa e payload capturado pelo duplo de rede. |
| RNF02 | Respeitar permissões: 100% das respostas de cada perfil contêm somente recursos autorizados. | CT-RNF02-P, CT-RNF02-N | `pytest`/`TestClient` e matriz perfil × recurso. |
| RNF03 | Auditar interações: 100% dos casos registram perfil, horário, intenção, fontes e resposta ou falha. | CT-RNF03-P, CT-RNF03-N | `pytest` e registro estruturado persistido. |
| RNF04 | Obter pelo menos 90% de respostas fundamentadas e no máximo 5% de alucinação na amostra congelada. | CT-RNF04-P, CT-RNF04-N | Planilha cega, respostas e fontes da amostra. |
| RNF05 | Manter P95 de consulta simples em até 10 s e de comparação em até 20 s, sem erro HTTP ou de contrato na carga definida. | CT-RNF05-P, CT-RNF05-N | `Locust`, CSV/HTML, log da API e configuração do ambiente. |
| RNF06 | Atingir F1 macro ≥ 0,80 na classificação de intenções e *recall* ≥ 0,80 na recuperação. | CT-RNF06-P, CT-RNF06-N | `scikit-learn`, notebook executado e `metricas.json`. |
| RNF07 | Compreender ou orientar a reformulação em pelo menos 80% das formulações em português da amostra. | CT-RNF07-P, CT-RNF07-N | `pytest`, roteiro de usuários e planilha consolidada. |
| RNF08 | Manter Teams como canal previsto, contrato OpenAPI válido e componentes compatíveis com o ecossistema Microsoft. | CT-RNF08-P, CT-RNF08-N | `/openapi.json`, checklist arquitetural e relatório de validação. |
| RNF09 | Executar o núcleo com dados estruturados sem depender da plataforma final ou de uma fonte concreta. | CT-RNF09-P, CT-RNF09-N | `pytest` do RAG, configuração da fonte e log de execução local. |
| RNF10 | Preservar separação entre interface, negócio e dados, API documentada, testes e instruções reproduzíveis. | CT-RNF10-P, CT-RNF10-N | Testes de importação, checklist de estrutura e documentação. |
| RNF11 | Tratar 100% das falhas previstas com resposta controlada, sem *stack trace*, segredo ou corpo bruto do provedor. | CT-RNF11-P, CT-RNF11-N | `pytest`/`TestClient`, respostas HTTP e logs sanitizados. |
| RNF12 | Representar projetos, subportfólios, marcos, riscos, indicadores e documentos na massa sintética. | CT-RNF12-P, CT-RNF12-N | Validador de esquema e relatório de cobertura da massa. |

### 9.2.3 Casos positivos e negativos

| Casos | Propósito | Instruções de execução | Resultado esperado e evidência |
|---|---|---|---|
| CT-RNF01-P / CT-RNF01-N | Verificar confidencialidade tanto no uso normal quanto diante de dado proibido. | **P:** percorrer os arquivos da massa, registrar origem e classificação e executar uma consulta com o duplo de rede capturando o payload. **N:** inserir em uma cópia temporária um marcador inequivocamente classificado como sensível e repetir o envio. | **P:** inventário 100% sintético/anonimizado e payload apenas com dados permitidos. **N:** validação bloqueia o processamento antes da fronteira externa; a evidência contém o relatório e a contagem zero de chamadas externas. |
| CT-RNF02-P / CT-RNF02-N | Confirmar isolamento por perfil e negação segura. | **P:** autenticar o perfil A, consultar um recurso permitido e comparar os campos retornados com a matriz de acesso. **N:** com o perfil B sem permissão, repetir a mesma consulta e inspecionar corpo, metadados e logs. | **P:** somente o escopo autorizado aparece. **N:** resposta de negação controlada, sem conteúdo nem metadados protegidos; anexar requisições e matriz preenchida. |
| CT-RNF03-P / CT-RNF03-N | Demonstrar rastreabilidade em sucesso e falha. | **P:** executar uma consulta válida e buscar o registro pelo identificador da interação. **N:** configurar o duplo de recuperação para falhar, repetir a consulta e buscar o registro correspondente. | Os dois registros contêm perfil, carimbo de tempo, intenção, fontes disponíveis e resposta ou estado de falha; anexar os registros sanitizados e seus IDs. |
| CT-RNF04-P | Medir a fundamentação quando a resposta existe na base, sem seleção oportunista de exemplos. | 1. Congelar a amostra antes da primeira resposta (`app/tests/rnf04/amostra_congelada.json`, v1.2). 2. Enviar a `/api/chat` as 12 perguntas positivas, cujo fato está em um dos extratos de `public.source_extracts` — por exemplo, "Qual é o período da operação assistida na Linha 1-Azul?" —, com `executar_rnf04.py`, que grava resposta integral e fontes. 3. Rotular a planilha cega, que sai sem cenário nem gabarito, conferindo cada afirmação contra as fontes que a própria resposta retornou. 4. Apurar com `avaliar_rnf04.py`. | Toda afirmação sustentada por um trecho das fontes retornadas. Planilha com rótulo e justificativa por caso; apuração com numerador e denominador. |
| CT-RNF04-N | Medir se o agente declara a ausência em vez de inventar. | 1. Na mesma amostra congelada, enviar as 12 perguntas negativas: atributos do PRJ-0442 que existem no banco mas não são recuperáveis (avanço, custo, gerente, riscos, próximo marco), comparação com projeto inexistente (PRJ-0518), fatos fora da massa (tarifa, Linha 2-Verde, Wi-Fi, demanda de julho, Linha 6-Laranja) e um caso-armadilha, em que a fonte recuperada é parecida mas não responde (animais de estimação × bicicleta). 2. Rotular na mesma planilha cega, sem saber o cenário de cada pergunta. 3. Apurar junto com o positivo. | Declarar corretamente a ausência conta como fundamentada; qualquer afirmação sem fonte conta como alucinação. O RNF04 é aprovado só se o conjunto das 24 perguntas tiver ≥ 90% de respostas fundamentadas e ≤ 5% de alucinação. |
| CT-RNF05-P | Medir o tempo de resposta nas condições de uso previstas. | 1. Subir a API e aquecer cada prompt fora da janela de medição (`aquecer.py`). 2. Gravar a ficha de ambiente (`registrar_ambiente.py`). 3. Rodar o `locustfile.py` com 1 usuário por 25 minutos e com 5 usuários por 8 minutos: 75% de consultas simples e 25% de comparações da massa congelada em `prompts.py`, com espera de 1 a 3 s. 4. Repetir as duas janelas com cache frio: reiniciar a API e medir sem o passo 1. 5. Apurar com `apurar_rnf05.py`. Comandos na Seção 9.2.4. | Zero erro HTTP ou de contrato e, com pelo menos 40 amostras por rota, P95 simples ≤ 10 s e P95 comparativo ≤ 20 s nas duas rodadas. Cache frio e quente são apurados em separado. CSVs, log do Locust, ficha de ambiente e apuração no diretório da rodada. |
| CT-RNF05-N | Provar que a medição detecta uma violação. | 1. Subir `api_com_atraso.py`, uma segunda instância da API em que um duplo acrescenta 25 s a toda comparação da massa congelada, sem alterar o restante do pipeline. 2. Rodar o `locustfile.py` contra ela com `RNF05_SO_COMPARACAO=1`, 5 usuários por 6 minutos. | P95 comparativo acima de 20 s: a rodada precisa reprovar. Se aprovar, a medição não enxerga violação e as rodadas positivas não valem. |
| CT-RNF06-P / CT-RNF06-N | Avaliar qualidade do PLN contra limiares reproduzíveis. | **P:** executar integralmente `src/notebooks/classificador_intencoes_metro.ipynb` com o conjunto de teste fechado e calcular F1 macro e *recall*. **N:** avaliar separadamente classes e termos ausentes ou fracos, sem treiná-los novamente, e aplicar os mesmos limiares. | `metricas.json` e notebook registram valores e versão da massa; qualquer métrica abaixo de 0,80 reprova o requisito e identifica as classes afetadas. |
| CT-RNF07-P / CT-RNF07-N | Verificar interação em português natural e orientação de reformulação. | Congelar ao menos 20 formulações. **P:** participantes enviam frases naturais válidas sem conhecer nomes internos. **N:** enviar frases ambíguas, com sinônimos não cadastrados e erros leves; registrar se houve compreensão ou orientação útil. | Pelo menos 80% do conjunto total é compreendido ou recebe reformulação acionável; anexar roteiro, respostas anonimizadas e cálculo. |
| CT-RNF08-P / CT-RNF08-N | Conferir aderência aos contratos e ao ecossistema definido. | **P:** iniciar a API, abrir `/openapi.json` e confrontar canal, conector e componentes com a arquitetura. **N:** validar uma cópia do contrato com operação obrigatória removida ou tipo incompatível. | Contrato real é válido e a arquitetura mantém Teams/Copilot/SharePoint/Azure previstos; a cópia alterada reprova no checklist, sem substituir o contrato versionado. |
| CT-RNF09-P / CT-RNF09-N | Provar portabilidade da origem de dados. | **P:** apontar a configuração para um diretório sintético alternativo e executar a mesma consulta localmente. **N:** apontar para arquivo ausente e depois para formato inválido, observando inicialização e resposta. | A troca válida não exige alteração no núcleo; origens inválidas geram falha explícita e localizada, sem acoplamento à interface ou à fonte concreta. |
| CT-RNF10-P / CT-RNF10-N | Verificar manutenibilidade por evidências estruturais e reprodução. | **P:** seguir o README em ambiente limpo, executar testes e conferir limites entre interface, negócio e dados. **N:** aplicar o checklist a uma cópia com instrução obrigatória removida ou dependência direta de acesso externo introduzida na rota. | A estrutura real passa nos itens objetivos; a violação controlada é detectada pelo teste de importação ou checklist. Anexar comandos, árvore relevante e resultado. |
| CT-RNF11-P / CT-RNF11-N | Garantir respostas controladas para falhas previstas e inesperadas. | **P:** parametrizar falha de classificação, ausência de resultado, indisponibilidade da fonte e *timeout*. **N:** fazer o duplo retornar exceção inesperada e payload inválido; inspecionar resposta e logs. | Todos os casos retornam código e mensagem definidos, preservam auditoria e não expõem *stack trace*, segredo ou corpo bruto do provedor. |
| CT-RNF12-P / CT-RNF12-N | Medir completude da massa sintética. | **P:** executar o validador sobre a massa congelada e contar projetos, subportfólios, marcos, riscos, indicadores e documentos. **N:** remover cada categoria, uma por vez, em cópias temporárias e repetir a validação. | A massa oficial contém todas as categorias; cada cópia incompleta é reprovada com a categoria ausente identificada. Anexar relatório e versão da massa. |

### 9.2.4 Teste obrigatório de desempenho do RNF05

O relógio começa no recebimento do `POST /api/chat` pela API e termina na devolução do JSON estruturado. A medição inclui classificação, recuperação, cache e chamada ao provedor em *cache miss*, mas exclui renderização do frontend, digitação, STT e TTS. O arquivo de cenário a ser versionado antes da execução é `src/backend/app/tests/performance/locustfile.py`; ele deve produzir 75% de consultas simples e 25% de comparações entre pelo menos dois projetos, com espera aleatória de 1 a 3 segundos.

Antes de medir, registrar CPU, memória, sistema operacional, versão do Python, *commit*, configuração da API e modalidade de cache. Reiniciar a API e aquecer uma vez cada prompt. Cache frio e quente são rodadas diferentes e nunca devem ser misturados no mesmo resultado. Chamadas reais ao provedor só podem ocorrer em ambiente autorizado; na CI, usam-se duplos determinísticos.

A partir de `src/backend`, com API e Locust instalados no ambiente de teste, executar:

```powershell
locust -f app/tests/performance/locustfile.py --host http://127.0.0.1:8000 --headless -u 1 -r 1 -t 5m --csv evidencias/rnf05-baseline
locust -f app/tests/performance/locustfile.py --host http://127.0.0.1:8000 --headless -u 5 -r 1 -t 5m --csv evidencias/rnf05-carga
```

A primeira rodada estabelece a linha de base com um usuário; a segunda mede cinco usuários simultâneos. Separar no relatório consultas simples e comparativas. O RNF05 é aprovado somente se, nas duas rodadas, houver zero erro HTTP/contrato, P95 simples ≤10 s e P95 comparativo ≤20 s. Registrar também média, mediana, P90, P99, RPS e quantidade de amostras para diagnóstico, mas nenhum desses valores substitui o P95 como critério. No CT-RNF05-N, o atraso injetado deve fazer o Locust registrar a violação; se o relatório permanecer aprovado, o próprio teste de desempenho está incorreto.

#### Revisão do protocolo a partir da 2ª rodada

Registrada em 22/09/2026, depois da 1ª rodada, e aplicável somente às rodadas seguintes. O protocolo acima permanece como o que foi efetivamente executado na 1ª rodada.

**1. Mínimo de 40 amostras por tipo de consulta.** O P95 só é apurado quando cada rota — simples e comparativa — tem ao menos 40 amostras na rodada. Abaixo disso, a rodada é **inconclusiva por amostra insuficiente** e deve ser estendida, nunca aprovada nem reprovada.

O motivo é aritmético. O Locust calcula o percentil em `calculate_response_time_percentile`, e com menos de 21 amostras o resultado coincide com a pior requisição da rodada. Na Sprint 4, a linha de base com um usuário produziu 10 amostras comparativas em 5 minutos: o critério aplicado foi, na prática, o máximo, mais rígido do que o P95 que o RNF05 define, e uma única requisição de 37,7 s decidiu a rodada. O mínimo de 40 dobra o limite de 21, para que o resultado não fique na fronteira em que uma requisição isolada volta a decidir.

Como a rota comparativa recebe 25% da carga, a linha de base com um usuário precisa de cerca de 25 minutos para atingir 40 amostras comparativas, e a carga com cinco usuários, de cerca de 8 minutos. A duração de 5 minutos passa a ser o mínimo, não o valor fixo.

**2. Aquecimento fora da janela de medição.** O aquecimento de cada prompt roda em passo separado (`app/tests/performance/aquecer.py`), antes do Locust. Dentro do `locustfile`, ele consumia parte da janela cronometrada e as rodadas "de 5 minutos" mediam cerca de 3 minutos e 40 segundos.

**3. Cenário negativo determinístico.** A rodada negativa usa `RNF05_SO_COMPARACAO=1`, que envia apenas pedidos de comparação, e o duplo de atraso reconhece esses pedidos pela lista exata da massa congelada. Roda com cinco usuários por 6 minutos, porque cada requisição leva cerca de 30 segundos com o atraso injetado e a rodada também precisa reunir 40 amostras. Com a mistura normal de 75/25, uma rodada curta podia não exercer o atraso nenhuma vez.

**4. Apuração automática.** `app/tests/performance/apurar_rnf05.py` lê os CSVs das rodadas e aplica, nesta ordem, a verificação de erros, a de amostra mínima e a dos tetos de P95, devolvendo aprovado, reprovado ou inconclusivo por rota. Erro reprova qualquer que seja o tamanho da amostra, porque a exigência de zero erro não depende de estatística; só o P95 precisa de amostra mínima para ter significado. A regra deixa de depender de quem lê o CSV.

**5. Forma da extensão.** Registrada durante a 3ª rodada, depois de a linha de base de 25 minutos terminar com 37 amostras comparativas e antes de o resultado da carga ser conhecido. A extensão é uma nova janela, mais longa, com o mesmo código e novo aquecimento fora dela, porque o Locust exporta percentis por rota, e não o tempo de cada requisição, e duas janelas não podem ser reunidas num P95 único. Um erro em qualquer das janelas reprova a rodada, já que a exigência de zero erro não depende de amostra; o P95 é julgado na janela que tem amostra suficiente; se ela também ficar abaixo de 40 amostras em alguma rota, a rodada é inconclusiva e não há terceira janela. As duas janelas são publicadas.

**6. Comandos.** A partir de `src/backend`, com a API em um terminal e a instância com atraso em outro:

```bash
LLM_PROVIDER=openrouter .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
LLM_PROVIDER=openrouter .venv/bin/python -m uvicorn app.tests.performance.api_com_atraso:app --host 127.0.0.1 --port 8001
```

```bash
export PYTHONPATH=. D=evidencias/rnf05-rodadaN
.venv/bin/python -m app.tests.performance.aquecer --host http://127.0.0.1:8000
.venv/bin/python -m app.tests.performance.registrar_ambiente --rodada baseline --cache quente --saida $D/baseline
.venv/bin/locust -f app/tests/performance/locustfile.py --host http://127.0.0.1:8000 --headless -u 1 -r 1 -t 25m --csv $D/baseline/rnf05-baseline
.venv/bin/python -m app.tests.performance.registrar_ambiente --rodada carga --cache quente --saida $D/carga
.venv/bin/locust -f app/tests/performance/locustfile.py --host http://127.0.0.1:8000 --headless -u 5 -r 1 -t 8m --csv $D/carga/rnf05-carga
.venv/bin/python -m app.tests.performance.registrar_ambiente --rodada violacao --cache quente --host http://127.0.0.1:8001 --saida $D/violacao
RNF05_SO_COMPARACAO=1 .venv/bin/locust -f app/tests/performance/locustfile.py --host http://127.0.0.1:8001 --headless -u 5 -r 1 -t 6m --csv $D/violacao/rnf05-violacao
.venv/bin/python -m app.tests.performance.apurar_rnf05 $D/baseline/rnf05-baseline_stats.csv $D/carga/rnf05-carga_stats.csv
```

Para cache frio, reiniciar a API antes de cada janela, omitir o `aquecer` e usar `--cache frio` na ficha de ambiente. `app/tests/executar_rodada_rnf.sh` encadeia a coleta do RNF04 e os passos de cache quente numa única campanha. `LLM_PROVIDER=openrouter` só tem efeito porque o `.env` da entrega não define essa variável: a API carrega o `.env` com prioridade sobre o ambiente, e o `.env` da entrega usa o Gemini.

O que esta revisão **não** altera: os tetos de 10 e 20 segundos, a exigência de zero erro HTTP ou de contrato, a execução das duas rodadas e o critério de que ambas precisam ser aprovadas. A rodada revisada continua podendo reprovar.

### 9.2.5 Instruções gerais de execução e evidências

1. Criar o diretório de evidências da execução, nomeado com sprint e *commit*, sem adicionar credenciais ou dados pessoais.
2. Em `src/backend`, criar ou ativar o ambiente virtual, instalar `requirements.txt` e executar `.venv\\Scripts\\python.exe -m pytest app/tests -q` no Windows ou `python -m pytest app/tests -q` nos demais ambientes.
3. Iniciar a API com `python -m uvicorn app.main:app`, confirmar `GET /health` e salvar o contrato de `http://127.0.0.1:8000/openapi.json`.
4. Executar CT-RNF01 a CT-RNF04 e CT-RNF09 a CT-RNF12 com duplos de rede e massa restaurada antes de cada cenário negativo.
5. Executar o RNF05 conforme a Seção 9.2.4 e anexar todos os CSVs, o relatório e a configuração. Não executar carga contra ambiente compartilhado sem autorização.
6. Para RNF06, executar o notebook `src/notebooks/classificador_intencoes_metro.ipynb` do início ao fim e salvar as métricas versionadas. Para RNF07, aplicar o roteiro e consolidar as respostas anonimizadas.
7. Preencher a matriz de resultados com aprovado, reprovado ou bloqueado e vincular cada evidência ao ID do caso. Não declarar RNF aprovado por planejamento: aprovação exige execução e evidência.

### 9.2.6 Abrangência e limitações

A abrangência cobre os doze RNFs e as duas direções de comportamento exigidas pelo barema. Os positivos demonstram confidencialidade, autorização, auditoria, fundamentação, desempenho, qualidade do PLN, linguagem natural, aderência tecnológica, portabilidade, manutenção, tratamento de falhas e completude dos dados. Os negativos foram escolhidos a partir das fronteiras de maior risco: vazamento, acesso indevido, perda de auditoria, alucinação, latência, classe fraca, ambiguidade, contrato incompatível, fonte inválida, acoplamento, exceção inesperada e massa incompleta. Essa seleção oferece cobertura sistêmica e rastreável, mas não é uma enumeração de todas as combinações de perfil, documento, intenção e infraestrutura.

Permissões corporativas, Teams, SharePoint real, Entra ID, Azure e transcrição não estão disponíveis na bancada local e, portanto, são simulados; a homologação final depende do ambiente do parceiro. O teste de carga planejado mede o ambiente descrito e não permite extrapolar capacidade de produção. Os resultados são registrados na Seção 9.2.7 com evidências observadas, nunca com estimativas, e a abrangência efetivamente alcançada por cada execução é discutida junto do seu resultado.

### 9.2.7 Resultados

A execução acontece na Sprint 4. Cada CT-RNF registra data, *commit*, ambiente, responsável, resultado, métricas aplicáveis, falha encontrada e link da evidência. Casos bloqueados identificam a dependência e o plano de desbloqueio.

#### RNF04 e RNF05 — Sprint 4

Executados em 22 e 23/09/2026 por Henrique Diniz. O índice completo das rodadas, inclusive as invalidadas e a descartada, com o motivo de cada uma, está em [`evidencias/README.md`](../src/backend/evidencias/README.md).

**Ambiente comum.** Modelo `gemini-3.7-flash`, o mesmo configurado na bancada de teste, chamado pelo OpenRouter em plano pago: o *Free Tier*, que a bancada usa para não gerar custo, limita a 20 requisições por dia, e a amostra do RNF04 sozinha tem 24 perguntas. O adaptador envia ao modelo exatamente o mesmo texto que o Gemini direto receberia, o que é fixado por teste automatizado. Recuperação no Supabase, retentativas e *timeout* do provedor com os valores de produção. Código medido: base `81c787d` com as alterações das branches das tasks, identificado por impressão digital em [`campanha-37flash/arvore-medida.md`](../src/backend/evidencias/campanha-37flash/arvore-medida.md); a 2ª e a 3ª rodadas do RNF05 registram o próprio hash no protocolo congelado antes da execução.

**Ferramentas e scripts.** Os scripts de medição ficam em `src/backend/app/tests`, versionados com o código medido e cobertos por testes automatizados; o notebook das figuras fica junto das evidências.

| Ferramenta ou script | Uso | Por que foi escolhido |
| --- | --- | --- |
| `pytest` | 322 testes do *backend*; desta execução, 55 fixam as correções (RAG, provedor, pool) e 44 testam os próprios scripts de medição | É o framework já usado no *backend* (Seção 8.4); um script de medição sem teste pode aprovar qualquer coisa |
| `Locust` 2.46 | Carga das rodadas do RNF05 (`performance/locustfile.py`) | Definido no planejamento (Seção 9.2.2): mede do lado do cliente, separa as rotas pelo nome da requisição e grava CSV por rota; é Python, e a massa de prompts é importada do mesmo pacote que os testes |
| `performance/aquecer.py` | Aquece cada prompt antes da janela de medição | Aquecer dentro do `locustfile` consumia a janela cronometrada (revisão 2 da Seção 9.2.4) |
| `performance/registrar_ambiente.py` | Ficha de ambiente de cada rodada: máquina, provedor, modelo, retentativas, pool | O planejamento exige registrar o ambiente antes de medir; a ficha registra só a **presença** de cada segredo, nunca o valor |
| `performance/api_com_atraso.py` | Duplo do `CT-RNF05-N`: instância da API que atrasa em 25 s toda comparação da massa congelada | Testa o instrumento antes de confiar nele: se a rodada com atraso aprovar, a medição está errada |
| `performance/apurar_rnf05.py` | Aplica a regra de decisão: erros, depois amostra mínima, depois tetos de P95 | Tira a decisão de quem lê o CSV (revisão 4 da Seção 9.2.4) |
| `rnf04/executar_rnf04.py` | Envia as 24 perguntas congeladas, grava resposta integral e fontes e gera a planilha cega | A planilha sai sem cenário nem gabarito, para que a rotulagem não seja influenciada pelo resultado esperado |
| `rnf04/avaliar_rnf04.py` | Apura fundamentação e alucinação com numerador e denominador explícitos | Aplica o critério sobre o conjunto completo, nunca sobre um subconjunto escolhido depois |
| `executar_rodada_rnf.sh` | Encadeia a coleta do RNF04 e as três rodadas do RNF05 numa campanha | Reproduz a execução completa com um comando |
| SQL em `public.ai_interactions` | Compara o tempo do pipeline, gravado pela auditoria do RNF03, com o tempo do cliente | Separa o custo do sistema do custo do que vem depois do pipeline, sem instrumentação nova |
| [`evidencias/graficos_rnf05.ipynb`](../src/backend/evidencias/graficos_rnf05.ipynb) | Gera as Figuras 27 e 28 a partir dos CSVs versionados | Nenhum número das figuras é digitado à mão |
| OpenRouter | Chama o `gemini-3.7-flash` em plano pago | Mesmo modelo da bancada, sem o limite de 20 requisições por dia do *Free Tier*; o adaptador envia exatamente o mesmo texto que o Gemini direto receberia |

**Comandos do RNF04**, a partir de `src/backend`, com a API no ar como na Seção 9.2.4. Os do RNF05 estão no item 6 da revisão do protocolo, na mesma seção.

```bash
.venv/bin/python -m app.tests.rnf04.executar_rnf04 --host http://127.0.0.1:8000 \
    --saida evidencias/rnf04-v12-37flash --tentativas-transitorias 3 --pausa 1
# rotular evidencias/rnf04-v12-37flash/planilha_cega.csv: fundamentada | alucinacao | nao_fundamentada
.venv/bin/python -m app.tests.rnf04.avaliar_rnf04 --evidencias evidencias/rnf04-v12-37flash
```

| Caso | Resultado | Métricas | Falha encontrada | Evidência |
| --- | :---: | --- | --- | --- |
| CT-RNF04-P e CT-RNF04-N, coleta de 21/09 | ⛔ bloqueado | 11 de 24 perguntas respondidas; as outras 13 receberam HTTP 429, quota diária do *Free Tier* esgotada | Amostra abaixo do mínimo de 20: nenhuma taxa pode ser apurada. A coleta expôs o DEF-RNF04-01 | [relatório](../src/backend/evidencias/rnf04-81c787d/RELATORIO.md) |
| CT-RNF05-P e CT-RNF05-N, 21/09 | ⚪ não executado | As rodadas do Locust não rodaram: a quota diária esgotou durante a coleta do RNF04 | As latências incidentais incluíam a espera entre novas tentativas do provedor e não foram apuradas | [relatório](../src/backend/evidencias/rnf05-81c787d/RELATORIO.md) |
| CT-RNF04-P | ✅ aprovado | 12 de 12 respostas fundamentadas | Nenhuma | [relatório](../src/backend/evidencias/rnf04-v12-37flash/RELATORIO.md) |
| CT-RNF04-N | ✅ aprovado | 10 de 12 fundamentadas, 1 não fundamentada, 1 alucinação | N-06 atribuiu ao projeto o status e o período de um comunicado vinculado a ele; N-04 e N-05 chegaram truncadas | [relatório](../src/backend/evidencias/rnf04-v12-37flash/RELATORIO.md) |
| **RNF04 (conjunto)** | ✅ **atendido** | **91,67%** fundamentadas (mín. 90%) e **4,17%** de alucinação (máx. 5%) | Margem estreita: um caso a mais em qualquer direção reprova | [planilha rotulada](../src/backend/evidencias/rnf04-v12-37flash/planilha_cega.csv) |
| CT-RNF05-P, 1ª rodada, 1 usuário | ❌ reprovado | P95 simples 6,6 s (24 amostras); P95 comparativo **38,0 s** (10 amostras); zero erro | Uma requisição comparativa de 37,7 s definiu o P95 da rota | [relatório](../src/backend/evidencias/rnf05-37flash/RELATORIO.md) |
| CT-RNF05-P, 1ª rodada, 5 usuários | ✅ aprovado | P95 simples 7,1 s (165 amostras); P95 comparativo 8,0 s (43 amostras); zero erro | Nenhuma | [relatório](../src/backend/evidencias/rnf05-37flash/RELATORIO.md) |
| CT-RNF05-N, 1ª rodada | ✅ validado | P95 comparativo de 32,0 s com atraso injetado de 25 s; a rodada reprovou, como exigido | O duplo deixava de atrasar um dos quatro prompts de comparação; corrigido antes da 2ª rodada | [CSVs](../src/backend/evidencias/rnf05-37flash/violacao/) |
| CT-RNF05-P, 2ª rodada, 1 usuário | ❌ reprovado | P95 simples 9,3 s (123 amostras); P95 comparativo 12,0 s (41 amostras); **1 erro** | Uma consulta simples não respondeu em 60 s: a gravação da auditoria do RNF03 ficou presa no banco | [relatório](../src/backend/evidencias/rnf05-rodada2/RELATORIO.md) |
| CT-RNF05-P, 2ª rodada, 5 usuários | ❌ reprovado | P95 simples **11,0 s** (202 amostras); P95 comparativo 11,0 s (72 amostras); zero erro | P95 das consultas simples acima do teto de 10 s | [relatório](../src/backend/evidencias/rnf05-rodada2/RELATORIO.md) |
| CT-RNF05-N, 2ª rodada | ✅ validado | 50 requisições, todas entre 30,1 s e 34,2 s | Nenhuma: o duplo atrasou todos os prompts de comparação | [CSVs](../src/backend/evidencias/rnf05-rodada2/violacao/) |
| CT-RNF05-P, 3ª rodada, 1 usuário, 25 min | ⚪ inconclusivo | P95 simples 7,6 s (159 amostras); P95 comparativo 8,2 s (**37 amostras**); zero erro | Amostra comparativa abaixo do mínimo de 40; linha de base estendida pela regra do item 5 da Seção 9.2.4 | [relatório](../src/backend/evidencias/rnf05-rodada3/RELATORIO.md) |
| CT-RNF05-P, 3ª rodada, 1 usuário, 35 min | ✅ aprovado | P95 simples 7,6 s (181 amostras); P95 comparativo 8,4 s (82 amostras); zero erro | Nenhuma | [relatório](../src/backend/evidencias/rnf05-rodada3/RELATORIO.md) |
| CT-RNF05-P, 3ª rodada, 5 usuários | ✅ aprovado | P95 simples 7,3 s (245 amostras); P95 comparativo 7,6 s (78 amostras); zero erro | Nenhuma | [relatório](../src/backend/evidencias/rnf05-rodada3/RELATORIO.md) |
| CT-RNF05-N, 3ª rodada | ✅ validado | 50 requisições, todas entre 29,4 s e 34,3 s; P95 de 34,0 s | Nenhuma | [CSVs](../src/backend/evidencias/rnf05-rodada3/violacao/) |
| CT-RNF05-P, 3ª rodada, cache frio, 1 usuário, 35 min | ✅ aprovado | P95 simples 7,6 s (208 amostras); P95 comparativo 8,3 s (64 amostras); zero erro | Nenhuma; a primeira requisição depois do reinício levou 7,2 s | [relatório](../src/backend/evidencias/rnf05-rodada3/cache-frio/RELATORIO.md) |
| CT-RNF05-P, 3ª rodada, cache frio, 5 usuários | ✅ aprovado | P95 simples 7,0 s (239 amostras); P95 comparativo 7,4 s (86 amostras); zero erro | Nenhuma | [relatório](../src/backend/evidencias/rnf05-rodada3/cache-frio/RELATORIO.md) |
| **RNF05 (conjunto)** | ✅ **atendido na 3ª rodada**, com cache quente e frio | Zero erro em 1.379 requisições das janelas positivas; P95 simples de 7,0 a 7,6 s com 1 e 5 usuários, contra o teto de 10 s; P95 comparativo de 7,4 a 8,4 s, contra 20 s | A 1ª rodada (uma requisição de 37,7 s numa rota com 10 amostras) e a 2ª (um erro e P95 simples de 11,0 s sob carga) continuam registradas como não atendidas. A gravação síncrona da auditoria ainda acrescenta cerca de 1,8 s | [índice das rodadas](../src/backend/evidencias/README.md) |

**Estados usados na tabela.** *Aprovado* e *reprovado* comparam o observado com o critério; *validado* indica o cenário negativo que reprovou, como exigido; *inconclusivo* é a janela com menos de 40 amostras em alguma rota, que não aprova nem reprova; *bloqueado* é a execução impedida por dependência externa; *não executado*, o caso que não chegou a rodar.

A Figura 27 compara o P95 de cada rodada positiva com o teto do requisito. As barras vermelhas são as rodadas reprovadas: na 1ª, a comparação com um usuário teve 10 amostras e o P95 coincidiu com a pior requisição; na 2ª, houve um erro com um usuário e P95 simples de 11,0 s com cinco. Na 3ª, com cache quente e com cache frio, todas as rotas ficaram abaixo do teto, com pelo menos 64 amostras cada.

<div align="center">
  <img src="img/rnf05-p95-rodadas.png" alt="P95 da consulta simples e da comparação em cada rodada positiva do RNF05, contra os tetos de 10 e 20 segundos" width="100%">
</div>

<p align="center"><strong>Figura 27</strong> - RNF05: P95 medido pelo cliente em cada rodada positiva.<br><sup>Fonte: Material produzido pelos autores, 2026, a partir dos CSVs do Locust.</sup></p>

A Figura 28 abre os percentis da 3ª rodada. As quatro curvas positivas ficam abaixo dos tetos até o P95; a comparação com um usuário tem uma requisição de 13,5 s, que aparece no P99 e no máximo, ainda abaixo do teto de 20 s. A curva do cenário negativo fica acima de 30 s em todos os percentis: a medição enxerga a violação.

<div align="center">
  <img src="img/rnf05-rodada3-percentis.png" alt="Mediana, P90, P95, P99 e máximo de cada janela e rota da 3ª rodada do RNF05, com o cenário negativo acima dos tetos" width="100%">
</div>

<p align="center"><strong>Figura 28</strong> - RNF05: percentis da 3ª rodada por janela e rota, com o cenário negativo.<br><sup>Fonte: Material produzido pelos autores, 2026, a partir dos CSVs do Locust.</sup></p>

**Registros das execuções aprovadas.** Saídas dos apuradores, reproduzíveis a partir dos arquivos de evidência.

Apuração do RNF04 (`avaliar_rnf04.py`), reproduzível a partir da planilha rotulada:

```text
RNF04 — amostra v1.2
  denominador ............ 24
  fundamentadas .......... 22 (91.67%)  [minimo 90.0%]
  alucinacoes ............ 1 (4.17%)  [maximo 5.0%]
  nao fundamentadas ...... 1
  positivo (CT-RNF04-P) .. 12/12 fundamentadas, 0 alucinacao
  negativo (CT-RNF04-N) .. 10/12 fundamentadas, 1 alucinacao

  RESULTADO: APROVADO
```

Apuração da 3ª rodada do RNF05 (`apurar_rnf05.py`, [`apuracao-final.txt`](../src/backend/evidencias/rnf05-rodada3/apuracao-final.txt)):

```text
rodada       rota        amostras falhas       P95  veredito
baseline-estendida comparacao        82      0    8400ms  aprovado — P95 8400 ms dentro do teto de 20000 ms
baseline-estendida simples          181      0    7600ms  aprovado — P95 7600 ms dentro do teto de 10000 ms
carga        comparacao        78      0    7600ms  aprovado — P95 7600 ms dentro do teto de 20000 ms
carga        simples          245      0    7300ms  aprovado — P95 7300 ms dentro do teto de 10000 ms

RNF05: ATENDIDO
codigo de saida: 0
```

Log da API na 3ª rodada, resumido sem identificadores ([`api-log-resumo.txt`](../src/backend/evidencias/rnf05-rodada3/api-log-resumo.txt)): 860 respostas HTTP 200 e nenhuma com outro status, nenhuma nova tentativa contra o provedor, nenhuma falha ao gravar a rastreabilidade do RNF03 e nenhuma consulta cancelada pelo limite de 5 s. Suíte do *backend* depois das correções, com e sem `.env` configurado: `322 passed`.

**Defeitos encontrados e tratamento.**

| ID | Defeito | Tratamento |
| --- | --- | --- |
| DEF-RNF04-01 | Vigência, status e linha do extrato eram recuperados do banco e descartados antes do prompt; perguntas de cronograma recebiam "contexto insuficiente" | Corrigido em `build_rag_input`, com 10 testes de regressão; as perguntas afetadas passaram a responder as datas corretas |
| DEF-RNF04-02 | Respostas truncadas pelo limite de tokens entregues como completas | Mecanismo confirmado nas rodadas do RNF05: 36 de 451 respostas (8,0%) na 2ª e 50 de 860 (5,8%) na 3ª terminaram por limite de tokens no caminho do OpenRouter, porque o raciocínio do modelo consome o mesmo orçamento de 512 tokens do texto. O adaptador passou a registrar cada ocorrência em log. Nenhuma das 35 respostas coletadas pelo Gemini direto terminou cortada. Depois do teste de usabilidade, em que duas respostas chegaram vazias (Seção 9.3.2), o limite passou a 1024 tokens e a resposta interrompida passou a vir com um aviso ao usuário; no reteste, 0 de 38 respostas foram cortadas, contra 4 de 38 com o limite antigo, com cerca de 0,2 s a mais na mediana do tempo do modelo ([relatório](../src/backend/evidencias/reteste-truncamento/RELATORIO.md)). As rodadas do RNF05 foram medidas com o limite de 512 |
| DEF-RNF05-01 | O Gemini no *Free Tier*, provedor da bancada, tem piso de 14,7 s a 37,7 s por chamada trivial, acima do teto do RNF05 | Característica da bancada, não do produto: o *Free Tier* é usado para não gerar custo, e o ambiente do Metrô usará o Copilot Studio com modelos GPT. As rodadas do RNF05 foram medidas com provedor pago. Ver Seção 3.2.2 |
| DEF-RNF05-02 | A gravação da auditoria do RNF03 é síncrona e fica no caminho da resposta. Na 2ª rodada, sob carga, a distância entre o P95 do cliente e o do pipeline foi de 4,1 s, e, sem limite de tempo nas consultas ao banco, uma gravação presa segurou uma resposta por mais de 60 s | Aplicados antes da 3ª rodada: limite de 5 s por consulta ao banco (`statement_timeout`) e *keepalive* de TCP nas conexões, com 9 testes. Na 3ª rodada a distância caiu para 1,8 s, sem erro. A gravação fora do caminho da resposta, por fila ou tarefa em segundo plano, fica para a mensageria prevista na Sprint 5: muda a semântica da auditoria verificada nos testes do RNF03 e é decisão do grupo |
| — | Cada requisição abria duas conexões novas com o Supabase, cerca de 1 s cada | Pool de conexões: de 1.209 ms para 599 ms por acesso, ou cerca de 1,2 s a menos por requisição, com qualquer provedor de LLM |
| — | 21 testes do *backend* falhavam quando havia `.env` configurado | Isolamento do ambiente de teste; 322 testes passam com e sem `.env` |

**Abrangência da execução.** O que as duas execuções cobrem:

- **RNF04:** 24 perguntas congeladas antes da coleta, metade com resposta na base e metade sem, cobrindo as quatro fronteiras de risco de alucinação da massa — atributo do projeto que existe no banco mas não é recuperável, projeto inexistente, fato fora da base e fonte parecida que não responde. A planilha cega impede que o rotulador veja o cenário, e cada rótulo tem justificativa citando a fonte.
- **RNF05:** 1.379 requisições nas janelas positivas da 3ª rodada, com as duas rotas medidas em separado, um e cinco usuários simultâneos, cache quente e cache frio, e um cenário negativo que prova que a medição detecta a violação. O relógio cobre o caminho de texto inteiro, da chegada à API à resposta estruturada, incluindo classificação, recuperação no banco, chamada ao LLM e gravação da auditoria.

O que elas **não** cobrem, e por quê:

| Fora da cobertura | Motivo | Efeito sobre a leitura do resultado |
| --- | --- | --- |
| Modelo de produção | O Metrô usará o Copilot Studio com modelos GPT; as rodadas usam o `gemini-3.7-flash`, o modelo da bancada | Fundamentação e latência valem para o modelo medido e são medidas de novo na homologação, com a mesma amostra e o mesmo protocolo |
| Base real | A massa tem nove extratos recuperáveis e um projeto | O custo da recuperação e o risco de confundir entidades podem crescer com a base real |
| Comparação efetivamente produzida | A massa tem um único projeto, o `PRJ-0442`, e a comparação entre projetos foi adiada para a Sprint 5 (Seção 6.4.1 do `GestaoProjeto.md`). Os prompts comparativos pedem a comparação com o `PRJ-0518`, que não existe | O P95 comparativo mede o sistema tratando o pedido de comparação e declarando a limitação, com chamada ao LLM; **não** demonstra o teto de 20 s para uma comparação real, que é medida quando a funcionalidade existir |
| Rotulagem independente | A planilha é cega, mas foi rotulada por quem construiu a amostra | Cada rótulo pode ser auditado um a um; uma segunda rotulagem por outro integrante daria garantia processual mais forte, e a margem do RNF04 é de um caso em cada critério |
| Rota de áudio | O RNF05 mede o caminho de texto por definição (Seção 9.2.4); a transcrição tem orçamento próprio de 6 s (Seção 8.7) e seu tempo sai no campo `stt_ms` | O tempo de ponta a ponta com voz soma a transcrição ao que foi medido aqui |
| Capacidade de produção | Uma máquina local, uma instância da API e até cinco usuários | O resultado não se extrapola para a carga real do Metrô |

A 2ª rodada separou o custo do sistema do custo da auditoria: o pipeline tinha P95 de 6,5 a 6,9 s, e a gravação síncrona do RNF03 levava a consulta simples a 11,0 s sob carga. Na 3ª rodada, com o limite de tempo e o *keepalive* nas conexões, a distância entre cliente e pipeline caiu de 4,1 s para 1,8 s no P95 sob carga, e o pipeline também ficou mais rápido, com P95 de 5,5 a 6,1 s. A rodada não isola quanto de cada ganho veio da correção e quanto da variação do provedor. A margem da consulta simples sob carga é de 2,7 s até o teto.

**Oportunidades de melhoria identificadas.** Tirar a gravação da auditoria do caminho da resposta, o que reduz a latência percebida em até cerca de 1,8 s e encaixa na mensageria prevista para a Sprint 5 (`DEF-RNF05-02`); reservar ao texto visível um orçamento de tokens separado do raciocínio do modelo, para eliminar as respostas truncadas (`DEF-RNF04-02`); inspecionar o motivo de parada também no caminho do Gemini direto; e repetir a rotulagem do RNF04 com um segundo integrante.

**Próxima medição.** Na homologação, com o provedor adotado pelo Metrô, pela mesma massa e pelo protocolo revisado da Seção 9.2.4, com os tetos inalterados. Se a gravação da auditoria sair do caminho da resposta na Sprint 5, uma nova rodada, congelada antes da execução como as anteriores, mede o efeito.

#### RNF06 — Sprint 4

A avaliação prospectiva ampliada do RNF06 foi executada uma única vez em 23 de setembro de 2026 por Pedro Damacena Machado Uchoa, no commit `c627dd26525472d9ca3e2a9592abbca15059d5aa`. O ambiente utilizou Windows, Python 3.13.15, scikit-learn 1.6.1, NumPy 2.5.2, joblib 1.6.0, Torch 2.13.0 e Transformers 5.16.1. Antes da execução foram congelados os critérios, os 1.135 exemplos do teste de classificação, 72 consultas inéditas de recuperação, a implementação e os hashes de todos os artefatos. O recuperador e a massa não foram alterados depois que o resultado foi observado. A evidência completa está em [`evidencias/sprint-04/rnf06/`](evidencias/sprint-04/rnf06/README.md).

| Caso/componente | Massa e procedimento | Resultado observado | Situação |
| --- | --- | --- | --- |
| CT-RNF06-P — classificação | 1.135 solicitações do `split == teste`; classificador versão 2 e BERTimbau no snapshot imutável, sem retreino | Acurácia 0,839648 e F1-macro 0,832724 | Aprovado |
| CT-RNF06-P/N — recuperação prospectiva | 72 consultas novas; oito por fonte e nove por variação linguística; *top-k* 3 | 40 de 72 fontes; *recall*@3 0,555556; IC de Wilson 95% [0,440874; 0,664609] | Reprovado |
| RNF06 consolidado | Aprovação exige F1-macro, *recall*@3 e limite inferior do IC simultaneamente ≥ 0,80 | F1-macro 0,832724; *recall*@3 0,555556 | **Reprovado** |

A linha de base de 22 de setembro recuperou 11 de 18 fontes e registrou *recall*@3 de 0,611111. As equivalências lexicais adicionadas em seguida foram escolhidas a partir dos erros desses mesmos casos; por isso, a reexecução com 18 de 18 fontes e *recall*@3 de 1,000000 é apenas evidência de regressão conhecida, não de generalização. A avaliação prospectiva v2 corrige essa contaminação metodológica: suas 72 consultas não repetem a massa v1, foram congeladas contra a implementação anterior e não foram reutilizadas para ajuste. Ela revelou fragilidade especialmente em consultas curtas e sinônimos novos (0,333333), formulações implícitas e paráfrases (0,444444). A autoria interna não cega e o uso de fontes sintéticas ainda limitam a validade externa; a conclusão não substitui homologação com solicitações reais e SharePoint do parceiro.

Os demais CT-RNF permanecem sem resultado nesta subseção até que sejam executados com as evidências previstas. Casos bloqueados devem identificar a dependência e o plano de desbloqueio.

## 9.3 Testes de Usabilidade

Os testes de usabilidade têm como objetivo avaliar se o Agente de Gestão de Portfólio pode ser utilizado por pessoas externas à equipe de desenvolvimento para consultar, interpretar e validar informações de projetos por meio de uma interação conversacional. A avaliação concentra-se na experiência do usuário durante os fluxos centrais do MVP: entrada em linguagem natural, consulta de informações, análise comparativa entre projetos, tratamento de informação ausente ou fora de escopo, sugestão proativa e entrada por voz.

A estratégia combina observação moderada de tarefas com aplicação do questionário SUS (*System Usability Scale*) adaptado ao contexto do projeto. A observação será registrada na planilha "Oneshot - Testes de Usabilidade - Agente de Gestão de Portifólio", criada no modelo de testes de usabilidade utilizado pelo grupo, com campos para resultado geral da tarefa, resultado por etapa e ocorrências. O SUS será aplicado por meio de formulário online ao final da sessão, usando escala Likert de 1 a 5, em que 1 significa "Discordo Completamente" e 5 significa "Concordo Completamente".

### 9.3.1 Planejamento dos testes de usabilidade

O planejamento prevê a realização dos testes com pelo menos cinco usuários externos à turma. A planilha de registro foi estruturada para até seis participantes, permitindo incluir um usuário adicional caso haja disponibilidade. A seleção dos participantes deve buscar diversidade de perfil, familiaridade tecnológica e relação com gestão de projetos, para evitar que a avaliação reflita apenas a experiência de usuários com alta proximidade com o tema ou com ferramentas digitais.

A planilha de execução funciona como instrumento de campo para o moderador e os observadores. A aba "Registro dos testes" organiza os cenários em blocos sequenciais, mantendo o mesmo padrão visual do modelo do grupo: título da tarefa, descrição da atividade, resultado geral, cinco etapas observáveis e campo de observações por usuário. A aba "Ocorrências" concentra problemas identificados durante as sessões, incluindo tarefa relacionada, severidade, resumo do ocorrido, potenciais melhorias e participante afetado. Dessa forma, o artefato permite registrar tanto o desempenho objetivo em cada etapa quanto evidências qualitativas de dificuldade, dúvida, hesitação, necessidade de ajuda ou quebra de confiança.

As Figuras 29 a 33 apresentam os principais recortes da planilha criada para conduzir e registrar os testes. Esses prints documentam como o roteiro foi operacionalizado em tarefas observáveis, permitindo que diferentes avaliadores registrem os resultados de forma padronizada.

<div align="center">
  <img src="img/testes-usabilidade-p1e2.png" alt="Planilha de testes de usabilidade com os cenários 1 e 2" width="900">
  <p><strong>Figura 29</strong> - Registro dos cenários 1 e 2 dos testes de usabilidade.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>
</div>

A Figura 29 apresenta os dois primeiros cenários do roteiro: entrada em linguagem natural e consulta de status ou prazo. Esses cenários validam se o usuário consegue iniciar a interação com o agente sem comandos técnicos e se consegue interpretar uma resposta objetiva, incluindo a verificação da fonte indicada.

<div align="center">
  <img src="img/testes-usabilidade-p3e4.png" alt="Planilha de testes de usabilidade com os cenários 3 e 4" width="900">
  <p><strong>Figura 30</strong> - Registro dos cenários 3 e 4 dos testes de usabilidade.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>
</div>

A Figura 30 mostra os cenários voltados à consulta de riscos e à análise comparativa entre projetos. Nessa parte do teste, o observador registra se o participante consegue escolher o tema da consulta, compreender as informações retornadas, pedir detalhes quando necessário e avaliar se a comparação apresentada apoia a tomada de decisão.

<div align="center">
  <img src="img/testes-usabilidade-p5e6.png" alt="Planilha de testes de usabilidade com os cenários 5 e 6" width="900">
  <p><strong>Figura 31</strong> - Registro dos cenários 5 e 6 dos testes de usabilidade.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>
</div>

A Figura 31 registra os cenários de informação ausente ou fora de escopo e de sugestão proativa. Esses testes são importantes para avaliar confiança e controle: o agente deve declarar limites quando não houver informação suficiente e, quando sugerir um próximo passo, deve deixar claro que a ação depende da confirmação do usuário.

<div align="center">
  <img src="img/testes-usabilidade-p7.png" alt="Planilha de testes de usabilidade com o cenário 7" width="900">
  <p><strong>Figura 32</strong> - Registro do cenário 7 dos testes de usabilidade.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>
</div>

A Figura 32 apresenta o cenário de entrada por voz. O objetivo desse bloco é observar se o participante consegue acionar a entrada por áudio, formular uma pergunta curta, conferir a transcrição e obter uma resposta coerente, mantendo o mesmo fluxo previsto para solicitações textuais.

<div align="center">
  <img src="img/testes-usabilidade-ocorrencias.png" alt="Planilha de ocorrências dos testes de usabilidade" width="900">
  <p><strong>Figura 33</strong> - Aba de ocorrências dos testes de usabilidade.<br><sup>Fonte: Material produzido pelos autores, 2026.</sup></p>
</div>

A Figura 33 apresenta a aba de ocorrências, usada para consolidar problemas identificados durante as sessões. O registro separado por tarefa, severidade, descrição do ocorrido, melhoria potencial e participante afetado permite priorizar correções após os testes, distinguindo falhas críticas de ajustes menores de clareza ou interface.

Os perfis desejados são:

| Perfil de participante | Justificativa de inclusão |
|---|---|
| Usuário com experiência em gestão de projetos | Avaliar se as respostas do agente apoiam consultas reais sobre status, prazos, riscos e marcos. |
| Usuário com experiência em análise ou acompanhamento de indicadores | Avaliar se as respostas e comparações são compreensíveis para tomada de decisão. |
| Usuário com familiaridade com ferramentas Microsoft, como Teams ou SharePoint | Avaliar se o canal de interação está aderente ao ambiente corporativo previsto. |
| Usuário com baixa familiaridade com agentes conversacionais | Avaliar se a linguagem natural reduz a necessidade de treinamento ou comandos técnicos. |
| Usuário sem vínculo com a equipe desenvolvedora | Reduzir viés de confirmação e observar dúvidas espontâneas durante o uso. |

Antes do início da sessão, o moderador deve apresentar brevemente o contexto do teste, reforçando que o objetivo é avaliar o sistema, não o participante. O usuário deve ser orientado a verbalizar dúvidas, expectativas e dificuldades durante a execução das tarefas. Cada sessão seguirá o mesmo roteiro, permitindo comparação entre participantes.

O roteiro operacional está dividido nos seguintes cenários:

| Cenário | Objetivo de usabilidade | Etapas observadas | Requisitos relacionados |
|---|---|---|---|
| Entrada em linguagem natural | Verificar se o participante consegue iniciar a interação sem comandos técnicos. | Abrir a interface do agente; formular pergunta sem comando técnico; enviar a pergunta; ler a resposta; dizer se a resposta atende. | RF01, RF02, RF03, RNF07 |
| Consulta de status e prazo | Avaliar clareza e suficiência de uma resposta objetiva sobre projeto. | Identificar o projeto; perguntar status ou prazo; localizar dado principal; verificar fonte indicada; avaliar suficiência da resposta. | RF04, RF05, RF08, RNF04 |
| Consulta de riscos e informações do projeto | Avaliar a qualidade das respostas sobre riscos, avanço, marcos ou indicadores. | Escolher tema da consulta; enviar pergunta ao agente; identificar informações retornadas; pedir detalhe se necessário; avaliar clareza da resposta. | RF04, RF05, RF08, RNF04 |
| Análise e comparação entre projetos | Avaliar se o agente apoia comparações entre iniciativas do portfólio. | Escolher dois projetos; definir critério de comparação; enviar pedido ao agente; interpretar comparação; avaliar apoio à decisão. | RF04, RF06, RF08 |
| Informação ausente ou fora de escopo | Verificar se o agente declara limites em vez de inventar respostas. | Formular pergunta limite; enviar ao agente; identificar mensagem de limite; entender orientação recebida; avaliar confiança na resposta. | RF03, RF08, RNF04, RNF11 |
| Sugestão proativa e controle do usuário | Avaliar se a sugestão opcional é compreensível e mantém o controle com o usuário. | Realizar consulta válida; ler sugestão opcional; aceitar ou recusar sugestão; confirmar controle da ação; avaliar utilidade da sugestão. | RF07, RF09, RF10 |
| Entrada por voz | Avaliar se a modalidade de áudio preserva a intenção do usuário quando disponível no protótipo. | Acionar entrada por voz; falar pergunta curta; conferir transcrição; enviar solicitação; avaliar resposta recebida. | RF01, RNF07, Seções 5.3.4 e 8.7 |

Durante cada tarefa, o observador registrará na planilha:

- resultado geral da tarefa: sucesso, conseguiu com dificuldade, não conseguiu ou não testado;
- resultado de cada etapa do fluxo;
- comentários espontâneos do participante;
- dúvidas, hesitações, reformulações de pergunta e necessidade de ajuda;
- ocorrências com severidade alta, média, baixa ou cosmética;
- potenciais melhorias relacionadas à interface, clareza das respostas, precisão percebida, indicação de fonte, tratamento de limites e controle da proatividade.

Após a execução das tarefas, o participante responderá ao SUS adaptado no formulário online disponível em: https://docs.google.com/forms/d/e/1FAIpQLSev4yrWdqAepCaFaPPoLvj9v6dCIkwuLT7wBWMbkcO4w5_Ehw/viewform. O questionário contém 10 perguntas alternadas entre formulações positivas e negativas, seguindo a estrutura do SUS de John Brooke (1986), adaptadas ao contexto do Agente de Gestão de Portfólio. As perguntas avaliam facilidade de uso, complexidade percebida, integração das funcionalidades, necessidade de suporte, clareza das respostas, confiança, rapidez de aprendizagem e aderência do agente às necessidades do projeto.

O cálculo do SUS seguirá o método tradicional: para itens positivos, subtrai-se 1 da nota atribuída; para itens negativos, subtrai-se a nota de 5. A soma dos valores ajustados é multiplicada por 2,5, resultando em uma pontuação de 0 a 100. Além da pontuação final, os comentários qualitativos e as ocorrências observadas serão usados para priorizar melhorias no agente.

#### Revisão dos instrumentos após o feedback da Sprint 3

Registrada na Sprint 4, antes das sessões com os participantes.

**Instrução do cenário 6.** A instrução anterior, "Observe se o agente sugere um próximo passo e se a sugestão depende da sua confirmação", antecipava ao participante exatamente o que o cenário quer observar: quem é avisado de que haverá uma sugestão procura por ela, e a etapa deixa de medir se a interface a comunica sozinha. A instrução passa a descrever só a tarefa: "Você vai participar de uma reunião sobre o projeto PRJ-0442. Use o agente para se preparar." Consultas sobre situação, prazos, riscos ou marcos do projeto fazem o agente oferecer um próximo passo que depende da confirmação do usuário, e o observador registra se o participante o percebe sem aviso. Uma segunda instrução, lida só depois, pede que o participante ajuste o agente para responder apenas o que foi perguntado, o que observa se ele encontra o controle da proatividade (RF10). O modo proatividade começa ligado em todas as sessões. As demais instruções da planilha descrevem a tarefa sem antecipar o comportamento observado e foram mantidas. Nas sessões da Sprint 4, a planilha ainda trazia a instrução original do cenário 6, e foi ela a lida aos participantes; o resultado desse cenário é lido com essa ressalva na Seção 9.3.2.

**SUS como dado descritivo.** O SUS mede a percepção global de usabilidade e não aponta problemas específicos; com cinco ou seis participantes, a média ainda é instável, porque só se estabiliza por volta de 12 a 14 respondentes. Por isso o plano não fixa meta de SUS para aprovar o sistema. O resultado é publicado com a nota de cada participante, a mediana e a amplitude, ao lado do perfil e da familiaridade declarada, e é lido junto da observação das tarefas, que é o que mostra onde cada pessoa hesitou, errou ou pediu ajuda.

**Perfil de cada participante.** Cada participante recrutado é registrado com a vaga de perfil que preenche, a familiaridade com tecnologia e com agentes conversacionais e a faixa etária, sem dados que o identifiquem. A amostra precisa reunir ao menos uma pessoa de familiaridade baixa e uma de familiaridade alta com agentes conversacionais.

**Ambiente das sessões.** As sessões usam a interface web da bancada (Seção 8.5), que reproduz a conversa, as fontes citadas, a sugestão proativa e a entrada por voz. O canal previsto para o agente é o Teams do Metrô, que não está acessível ao grupo; por isso o item do SUS sobre o uso dentro do Teams mede a expectativa do participante, e não uma experiência que ele teve.

**Instrumentos versionados.** O roteiro do moderador, com abertura, regras de intervenção e o que a base sustenta em cada cenário, o termo de consentimento, o checklist de ambiente executado antes de cada sessão, os critérios de recrutamento e o questionário SUS estão em [`docs/usabilidade/`](usabilidade/README.md). A planilha e o formulário do grupo continuam sendo os instrumentos de campo; os dados anonimizados de cada sessão são transcritos para [`docs/usabilidade/dados/`](usabilidade/dados/) e consolidados pelo notebook [`src/notebooks/consolidacao_usabilidade.ipynb`](../src/notebooks/consolidacao_usabilidade.ipynb). O notebook valida os valores antes de calcular, separa sessões realizadas, bloqueadas e não executadas, apura cada cenário como concluído, concluído com dificuldade, falhou ou não executado, e lista os defeitos críticos ainda sem tratamento ou reteste.

**Piloto técnico.** Antes das sessões, as tarefas foram executadas diretamente contra a API, sem participante, para confirmar que cada uma produz o comportamento que o roteiro descreve: resposta com fonte nos cenários de consulta, declaração de limite nos cenários 4 e 5 e sugestão proativa, com aceite e recusa, no cenário 6. O piloto não gera dado de usabilidade.

### 9.3.2 Resultados

**Execução.** Seis sessões moderadas individuais, em 23/09/2026, conduzidas em sequência na interface web da bancada (commit `c9ad16a`, modelo `gemini-3.7-flash`), uma por participante, todas com o mesmo roteiro, o mesmo moderador e a mesma versão do sistema. O formulário SUS foi aplicado ao final da rodada, e os seis responderam entre 16:56 e 17:05.

A sessão conduzida na bancada compartilhada ficou registrada na auditoria do RNF03: onze perguntas numa mesma conversa, de 16:39:51 a 16:50:12, e a consulta do cenário 3, às 17:26:26, numa conversa separada. As demais sessões rodaram em instâncias locais da bancada, sem `SUPABASE_DATABASE_URL` configurada, o que leva a recuperação ao índice local e não produz evento de auditoria; o registro delas é a planilha de campo do grupo. Os dados anonimizados de todas as sessões estão em [`docs/usabilidade/dados/`](usabilidade/dados/) e a consolidação, em [`src/notebooks/consolidacao_usabilidade.ipynb`](../src/notebooks/consolidacao_usabilidade.ipynb).

**Participantes.** Seis estudantes de uma faculdade de tecnologia, de 18 a 21 anos, externos à turma. A familiaridade declarada com agentes conversacionais cobre os três níveis previstos na Seção 9.3.1: dois participantes de familiaridade alta, que usam ferramentas como ChatGPT, Gemini e Claude na rotina de estudo; dois de familiaridade média, com uso esporádico; e dois de familiaridade baixa, sem uso regular desse tipo de ferramenta. Na familiaridade com tecnologia em geral, quatro declararam alta e dois, média. Nos dados, aparecem como `P1` a `P6`, sem nomes.

| Participante | Sessão | Familiaridade com tecnologia | Familiaridade com agentes |
| :---: | :---: | :---: | :---: |
| P1 | S1 | alta | alta |
| P2 | S2 | alta | média |
| P3 | S3 | média | baixa |
| P4 | S4 | alta | média |
| P5 | S5 | alta | alta |
| P6 | S6 | média | baixa |

**Resultado por cenário.** Cada participante executou os sete cenários na própria sessão, e cada cenário tem seis observações independentes.

| Cenário | ✅ Concluído | ⚠️ Com dificuldade | ❌ Falhou | Leitura |
| --- | :---: | :---: | :---: | --- |
| 1. Entrada em linguagem natural | 4 | 2 | 0 | A pergunta em linguagem comum funcionou sem comando técnico; entre os dois participantes de familiaridade baixa, um procurou um menu de comandos antes de digitar e o outro começou com uma pergunta de uma palavra e a reformulou |
| 2. Consulta de status e prazo | 4 | 2 | 0 | "me fale o prazo do projeto da linha azul" trouxe a vigência de 24/08 a 28/08/2026, com a fonte citada; dois participantes não perceberam a fonte na primeira leitura, e um deles procurou o prazo no meio do texto |
| 3. Consulta de riscos e informações do projeto | 2 | 2 | 2 | Duas respostas chegaram vazias, só com o aviso de dados fictícios (O7), e duas chegaram cortadas no meio da frase (O5) |
| 4. Análise e comparação entre projetos | 3 | 3 | 0 | O agente declarou que a base tem um único projeto e os participantes seguiram; em uma sessão o comunicado de serviço foi tratado como projeto (O4), em outra o agente sugeriu uma comparação logo depois de recusá-la (O3), e um participante demorou a escolher os projetos por não saber o que havia na base |
| 5. Informação ausente ou fora de escopo | 0 | 4 | 2 | O limite foi declarado para a Linha 5, mas perguntas curtas sobre temas que estão na base foram recusadas (O1); dois participantes só concluíram depois da dica do moderador |
| 6. Sugestão proativa e controle do usuário | 0 | 4 | 2 | As sugestões aceitas responderam que as fontes eram insuficientes (O2) e dois participantes só concluíram a etapa de controle depois da dica do moderador (O8) |
| 7. Entrada por voz | 4 | 2 | 0 | A transcrição preservou a intenção em todas as sessões (O6); dois participantes hesitaram em acionar o botão de áudio |

Quatro dicas do moderador foram necessárias, todas nos cenários 5 e 6 e todas com participantes de familiaridade média ou baixa com agentes conversacionais. As etapas com mais problemas foram "entender a orientação recebida" no cenário 5 e "avaliar a utilidade da sugestão" no cenário 6, com seis registros de dificuldade ou falha cada.

<div align="center">
  <img src="img/usabilidade-resultado-por-cenario.png" alt="Resultado de cada cenário do teste de usabilidade, com a distribuição dos seis participantes entre concluído, concluído com dificuldade e falhou" width="100%">
</div>

<p align="center"><strong>Figura 34</strong> - Resultado por cenário do teste de usabilidade.<br><sup>Fonte: Material produzido pelos autores, 2026, a partir dos dados anonimizados das seis sessões.</sup></p>

**Ocorrências.**

| ID | Cenário | Severidade | Ocorrido | Tratamento |
| --- | :---: | :---: | --- | --- |
| O1 | 5 | alta | "fale sobre os Objetos perdidos", "fale sobre o Bilhete digital" e "Bilhete digital", temas que estão na base, foram recusados pelo classificador, com confiança de 42% a 50%, e a orientação pediu para indicar um projeto; a recusa se repetiu nas seis sessões | Aceitar perguntas curtas sobre temas operacionais e orientar a reformulação com exemplos, sem exigir um projeto |
| O2 | 6 | média | As sugestões foram oferecidas sem sustentação nas fontes: depois de uma pergunta sobre a Linha 5, o agente sugeriu identificar o gargalo do projeto e, aceita a sugestão, respondeu que as fontes eram insuficientes | Oferecer a sugestão só quando as fontes recuperadas sustentarem a ação |
| O3 | 4 | baixa | Depois de declarar que só existe um projeto, o agente sugeriu adaptar a prática do projeto com melhor desempenho | Não oferecer sugestão comparativa quando a comparação foi recusada |
| O4 | 4 | baixa | A resposta tratou o comunicado de serviço como projeto, e o participante passou a comparar comunicado com projeto | Indicar no prompt a entidade de cada fonte |
| O5 | 7 | média | Respostas terminaram cortadas no meio da frase, pelo limite de tokens | Corrigido e retestado, com O7 |
| O6 | 7 | cosmética | A transcrição registrou "Eu sou eu perdi um objeto"; a intenção foi preservada | — |
| O7 | 3 | alta | Duas respostas chegaram vazias, só com o aviso de dados fictícios: o raciocínio do modelo consumiu o limite de 512 tokens antes do texto | Corrigido: limite de 1024 tokens e aviso ao usuário quando a resposta for interrompida. No reteste, 0 de 38 respostas cortadas, contra 4 de 38 com o limite antigo ([relatório](../src/backend/evidencias/reteste-truncamento/RELATORIO.md)) |
| O8 | 6 | alta | O controle da proatividade e a confirmação da sugestão não foram percebidos sem ajuda: um participante não encontrou onde pedir que o agente respondesse apenas o que foi perguntado, e outro leu a sugestão como parte da resposta, sem perceber que era uma ação a confirmar | Tornar o controle da proatividade visível na própria conversa, junto da sugestão oferecida |

O único defeito crítico, O7, foi corrigido e retestado. O1 e O8 são de severidade alta porque impediram a tarefa de dois participantes cada, que só concluíram a etapa depois da dica do moderador, mas não são defeitos críticos: nas duas, o agente não apresentou dado incorreto nem executou ação sem confirmação, e os outros quatro participantes concluíram o cenário. O1 a O4 e O8 entram como melhorias para a Sprint 5, com O1 e O8 à frente.

**SUS.** As seis respostas, em ordem de envio, sem vínculo com os códigos dos participantes, porque o formulário não identifica quem respondeu:

| Resposta | R1 | R2 | R3 | R4 | R5 | R6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SUS | 97,5 | 100,0 | 87,5 | 80,0 | 77,5 | 75,0 |

Mediana de 83,75 e amplitude de 75 a 100, com média de 86,25 para seis respondentes. Como definido na Seção 9.3.1, o SUS é dado descritivo e não critério de aprovação. A percepção declarada é mais favorável do que a observação das tarefas sugere: nenhum participante concluiu os cenários 5 e 6 sem dificuldade, houve perguntas recusadas (O1), sugestões que não entregaram o que ofereciam (O2) e duas respostas vazias (O7). A amplitude de 25 pontos acompanha a distância entre as notas mais altas e as mais baixas, mas o formulário não identifica quem respondeu, e por isso não é possível associá-la à familiaridade declarada.

**Abrangência e limitações.**

| Limitação | Efeito sobre a leitura |
| --- | --- |
| Seis sessões, um participante em cada | Cada cenário tem seis observações independentes, o que permite distinguir dificuldade individual de comportamento do sistema, mas não sustenta estatística |
| Amostra concentrada em um perfil | Seis estudantes de tecnologia da mesma faixa etária; a familiaridade com agentes conversacionais varia entre baixa, média e alta, e a vaga de baixa familiaridade foi coberta por P3 e P6. As vagas de gestão de projetos, análise de indicadores e ferramentas Microsoft ficaram vazias: as respostas não foram avaliadas por quem acompanha status, riscos e indicadores na rotina, nem por usuários do ambiente Microsoft previsto para o agente |
| Instrução original do cenário 6 | A instrução lida antecipava a sugestão proativa; a etapa "ler a sugestão" não mede se a interface a comunica sozinha |
| SUS sem vínculo com o participante | O formulário é anônimo, e a nota não pode ser cruzada com a familiaridade declarada nem com o desempenho observado |
| SUS respondido ao final da rodada | As seis respostas chegaram em nove minutos, depois da última sessão, e não logo após a sessão de cada participante; quem foi atendido primeiro respondeu com mais tempo decorrido |
| Auditoria cobre uma das seis sessões | As sessões em instância local não persistem em `ai_interactions` nem em `audit_events`; para elas, a evidência é a planilha de campo, e não a trilha do RNF03 |
| Massa sintética com um projeto | Os cenários 3 e 4 medem sobretudo como o agente declara o que não tem |

**Melhorias priorizadas.** (1) Aceitar perguntas curtas sobre temas operacionais da base, que responde por O1 e pela dificuldade do cenário 5; (2) condicionar a sugestão proativa às fontes recuperadas, que responde por O2 e O3; (3) tornar o controle da proatividade visível junto da sugestão, que responde por O8; (4) separar no prompt a entidade de cada fonte, que responde por O4. Para a próxima rodada, recomendam-se novas sessões com os perfis ainda não cobertos.

---

## 9.4 Testes de Integração

### 9.4.1 Planejamento

O módulo VHS/cache está implementado na fronteira de transcrição Azure Speech.
O [plano final de integração S4-31](testes/sprint4/plano-vhs.md) documenta
arquitetura, limites, invalidação, cenários, critérios congelados, ferramentas,
comandos, métricas e dependências S4-22/S4-28.

### 9.4.2 Resultados

A suíte controlada exercita gravação/hit, miss, TTL, invalidação, falhas e
recuperação, isolamento de chave, capacidade e concorrência. As
[evidências S4-31](evidencias/sprint-04/vhs/README.md) distinguem os resultados
locais dos cenários externos não executados. O coletor registra a comparação
com os critérios em pytest/JUnit antes de classificar cada caso.
O runtime limita a API a um worker enquanto o cache permanecer em memória. A
telemetria autenticada identifica o worker e quantifica hits, misses, chamadas
ao provedor, erros, taxa de acerto e chamadas evitadas. O roteiro de homologação
com Azure real repete um áudio autorizado, mede miss e hits separadamente,
publica mediana/P95 sem expor áudio ou transcrição e remove a conversa sintética
do banco ao final. A homologação externa só é considerada aprovada após a saída
sanitizada dessa execução ser anexada às evidências.

# 10. Procedimentos de Implantação

O deploy da Sprint 4 foi realizado no AWS Academy Learner Lab e teve como objetivo disponibilizar a PoC para testes da equipe e do cliente sem depender de infraestrutura corporativa do Metrô. O processo combinou Supabase PostgreSQL, imagens Docker privadas no Amazon ECR, uma instância EC2 gerenciada por CloudFormation e um Cloudflare Quick Tunnel para fornecer acesso HTTPS temporário.

As etapas abaixo descrevem o que foi configurado, os comandos e artefatos usados e as verificações executadas. Os valores sensíveis foram mantidos fora do Git e são representados apenas pelos nomes das variáveis.

## 10.1 Implantação e Configuração do Banco de Dados

O runtime utiliza o PostgreSQL gerenciado do projeto Supabase **Oneshot**. A conexão administrativa foi configurada localmente em `SUPABASE_DATABASE_URL`, sem versionar seu valor. Antes de iniciar os workers de alerta, o esquema foi inspecionado e a migração pendente foi aplicada separadamente do deploy da aplicação.

### 10.1.1 Preflight do esquema

O primeiro passo foi executar o modo de leitura do gerenciador de infraestrutura de alertas:

```powershell
cd src/backend
.venv\Scripts\python.exe scripts/manage_alert_infrastructure.py status
```

O preflight encontrou as seis tabelas de alertas da migração [`15_alert_deadline_flow.sql`](../src/database/sql/15_alert_deadline_flow.sql) já criadas e estruturalmente compatíveis. Por isso, a migração 15 não foi reaplicada. Também foram encontrados sete registros em `pending_proactive_suggestions`, ainda sem as colunas de resposta preparada exigidas pela migração 08.

Antes da execução, [`08_add_prepared_proactive_response.sql`](../src/database/sql/08_add_prepared_proactive_response.sql) foi alterada para excluir somente registros que fossem, ao mesmo tempo, incompletos, expirados e não reivindicados. A migração lança uma exceção e desfaz a transação se encontrar qualquer registro incompleto que ainda esteja ativo ou reivindicado.

### 10.1.2 Aplicação da migração

Após comparar o arquivo local e confirmar que nenhum registro protegido seria removido, a migração foi enviada ao Supabase e executada uma única vez como transação. O Supabase registrou `08_add_prepared_proactive_response`, versão `20260925034214`.

| Verificação | Antes | Depois |
|---|---:|---:|
| Registros em `pending_proactive_suggestions` | 7 | 0 |
| Registros incompletos protegidos | 0 | 0 |
| Registros expirados, incompletos e não reivindicados | 7 | 0 |

A limpeza removeu os sete registros expirados e não reivindicados. Depois da aplicação, `prepared_response` ficou como `TEXT NOT NULL`, `prepared_model` como `VARCHAR(160) NOT NULL` e `prepared_interaction_id` permaneceu anulável. O RLS foi habilitado e os privilégios diretos de `anon` e `authenticated` foram revogados. As seis tabelas de alertas e seus dados permaneceram inalterados.

O rollback [`16_rollback_alert_deadline_flow.sql`](../src/database/sql/16_rollback_alert_deadline_flow.sql) não foi usado porque remove as seis tabelas e seus dados. A conexão PostgreSQL foi posteriormente testada de dentro do contêiner backend na EC2 pela saída TCP/5432 do Security Group.

## 10.2 Implantação do Protótipo para uso por equipe de desenvolvimento

### 10.2.1 Restrições do Learner Lab e arquitetura adotada

O primeiro deploy usava AWS Systems Manager para toda a operação remota. A EC2 chegou a registrar o SSM Agent como online, mas a política `voc-cancel-cred` do Learner Lab negou explicitamente `ssm:StartSession` e `ssm:SendCommand`. Como uma negação explícita não pode ser contornada pela role da instância, o desenho foi substituído por:

- EC2 pública com Ubuntu 24.04;
- SSH por chave, restrito ao IPv4 `/32` do operador;
- frontend publicado apenas em `127.0.0.1:80` na EC2;
- backend, RabbitMQ e workers somente na rede privada do Compose;
- Cloudflare Quick Tunnel iniciado na própria EC2 para acesso HTTPS externo;
- Supabase como PostgreSQL gerenciado;
- ECR privado para as imagens de backend e frontend;
- CloudWatch Agent e logs locais com rotação.

Não foi aberta entrada HTTP pública no Security Group. O Cloudflare estabelece conexões de saída e encaminha as requisições para o frontend ligado ao *loopback*. A transição entre as duas arquiteturas está consolidada nesta seção.

### 10.2.2 Preparação dos contêineres

O backend e o frontend foram empacotados em Dockerfiles *multi-stage*. O estágio final do backend contém a API FastAPI, o núcleo de PLN e os comandos dos workers. O frontend é compilado com Node e servido por Nginx, que encaminha `/api` para o backend e expõe `/health`.

O arquivo [`compose.prod.yml`](../compose.prod.yml) foi usado tanto nos testes locais quanto na EC2. O perfil padrão contém:

| Serviço | Comando ou função | Rede e exposição |
|---|---|---|
| `backend` | API FastAPI | Apenas `app-private`, porta 8000 não publicada |
| `frontend` | React + Nginx | `127.0.0.1:80` no host |
| `rabbitmq` | `rabbitmq:4.1.8-alpine` | Apenas `app-private`, com volume persistente |
| `scheduler` | `python -m app.alerts.worker scheduler` | Apenas `app-private` |
| `publisher` | `python -m app.alerts.worker publisher` | Apenas `app-private` |
| `evaluator` | `python -m app.alerts.worker evaluator` | Apenas `app-private` |
| `notifier` | `python -m app.alerts.worker notifier` | Apenas `app-private` |

O notebook foi mantido no profile opcional `notebook` e não é iniciado nem baixado na configuração padrão da EC2. Os contêineres usam limites de CPU e memória, `read_only`, `tmpfs`, `no-new-privileges`, descarte de capabilities e rotação do driver de logs. Backend, frontend e RabbitMQ possuem *health checks*; os workers não usam health check HTTP porque não servem requisições.

O build local foi executado com uma tag igual ao SHA completo do commit:

```powershell
$tag = (git rev-parse HEAD).Trim()
.\scripts\docker-build.ps1 -Tag $tag
docker compose -f compose.prod.yml config --quiet
```

Antes da publicação, o backend passou pela suíte completa e pelo `/health` em contêiner. O frontend passou por lint, 59 testes, build TypeScript e health local. Também foi verificado que nenhum `.env`, chave privada ou credencial fazia parte do contexto das imagens.

### 10.2.3 Build e publicação no ECR

Foram usados dois repositórios privados existentes na conta do Learner Lab: `m7-g05-backend` e `m7-g05-frontend`. Ambos foram configurados com tags imutáveis. Não foi utilizada a tag `latest`; cada imagem recebe o SHA completo do commit que originou o build.

Depois do build local, as imagens foram renomeadas com o endereço do registry, autenticadas e enviadas ao ECR:

```powershell
$registry = '307432329071.dkr.ecr.us-east-1.amazonaws.com'
$tag = (git rev-parse HEAD).Trim()

aws ecr get-login-password --region us-east-1 |
  docker login --username AWS --password-stdin $registry

docker tag "m7-g05-backend:$tag" "$registry/m7-g05-backend:$tag"
docker tag "m7-g05-frontend:$tag" "$registry/m7-g05-frontend:$tag"
docker push "$registry/m7-g05-backend:$tag"
docker push "$registry/m7-g05-frontend:$tag"
```

A publicação foi feita para `linux/amd64`. Depois do push, `ecr:DescribeImages` foi usado para recuperar e registrar os digests, que são exigidos pelo preflight de atualização. A versão implantada corresponde ao commit `f776feb352c3556d02e83dc14eea49b0d795f6b9`:

| Imagem | Tag imutável | Digest confirmado no ECR |
|---|---|---|
| `m7-g05-backend` | `f776feb352c3556d02e83dc14eea49b0d795f6b9` | `sha256:1bb49e4cfb7a83881f2b1ea5741792bc916710ec565c5659d827097bf114b497` |
| `m7-g05-frontend` | `f776feb352c3556d02e83dc14eea49b0d795f6b9` | `sha256:ee4cd9024f63519c0f64c061f7c47fbefbeba21b660c01e3bad0bac4e8e3e317` |

Antes do deploy, o preflight confirmou que cada tag existia uma única vez, que os repositórios continuavam imutáveis e que os digests informados coincidiam com o ECR. A correspondência entre tag e commit é usada como rastreabilidade, enquanto o digest identifica o conteúdo efetivamente publicado.

### 10.2.4 Preparação da conta AWS

As credenciais temporárias da sessão do Learner Lab foram mantidas em `.env` local e carregadas por [`common.ps1`](../scripts/aws/common.ps1). O helper lê somente `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` e `AWS_DEFAULT_REGION`, exige `us-east-1` e não imprime os valores. Como essas credenciais expiram, o primeiro teste de cada janela foi `sts:GetCallerIdentity`.

O preflight consultou a VPC, subnet, rota para Internet Gateway, AMI, disponibilidade do tipo de instância, instance profile, ECR e stack existente. Os valores utilizados foram:

| Parâmetro | Configuração usada |
|---|---|
| Região | `us-east-1` |
| VPC | `vpc-071dbf8c393325483` |
| Subnet pública | `subnet-0a4ab0f965bbfa086` em `us-east-1a` |
| AMI | Ubuntu Server 24.04 LTS amd64, `ami-0045d7fc2ad003464` |
| Tipo | `t3.large`, 2 vCPU e 8 GiB de memória |
| Volume raiz | EBS gp3 criptografado de 50 GiB |
| Instance profile | `LabInstanceProfile` |
| Stack | `m7-g05-mvp` |
| Key pair | `m7-g05-learner-lab-2026` |

O template [`infra/aws/template.yaml`](../infra/aws/template.yaml) cria apenas a EC2, o Security Group e um Log Group com retenção de sete dias. VPC, subnet, instance profile e repositórios ECR permanecem externos à stack.

O Security Group não expõe HTTP. A única entrada prevista é TCP/22 a partir do IPv4 público atual do operador em `/32`. As saídas permitem TCP/80 para pacotes do bootstrap, TCP/443 para ECR, CloudWatch, Gemini e Azure Speech, TCP/5432 para o *session pooler* do Supabase e TCP/UDP 7844 para o Cloudflare Tunnel.

### 10.2.5 Criação da chave e substituição da EC2

A primeira EC2 havia sido criada sem key pair. Como a política do Learner Lab impedia SSM e não havia outro canal para instalar uma chave no sistema operacional, a instância precisou ser substituída. Foi usada uma chave ED25519 denominada `m7-g05-learner-lab-2026`. A chave pública foi importada na EC2 e a chave privada permaneceu em `C:\Users\Inteli\.ssh`, fora do repositório e com ACL restrita ao usuário e ao sistema.

O script [`deploy.ps1`](../scripts/aws/deploy.ps1) separa o processo em quatro invocações. A substituição ocorreu antes do rebuild final da Sprint 4 e, portanto, usou a versão anterior já validada no ECR. O mapeamento usado foi:

```powershell
$deploy = @{
  VpcId = 'vpc-071dbf8c393325483'
  SubnetId = 'subnet-0a4ab0f965bbfa086'
  AmiId = 'ami-0045d7fc2ad003464'
  InstanceType = 't3.large'
  RootVolumeSize = 50
  InstanceProfileName = 'LabInstanceProfile'
  EcrRegistryUri = '307432329071.dkr.ecr.us-east-1.amazonaws.com'
  BackendImageTag = '0ef613347a33131036e975bb74b5a3b4baa56fca'
  FrontendImageTag = '0ef613347a33131036e975bb74b5a3b4baa56fca'
  BackendImageDigest = 'sha256:a36625c35ce19f2fbbba96769d474597ba9227f6ff332cca86735c86ca89ee06'
  FrontendImageDigest = 'sha256:feac52befdf953df04df75abdf1ac79b07fa6abd59f4e3b2a31169fa1d538723'
  KeyPairName = 'm7-g05-learner-lab-2026'
  OperatorSshCidr = '<IP_PUBLICO_ATUAL_DO_OPERADOR>/32'
}

.\scripts\aws\deploy.ps1 @deploy
.\scripts\aws\deploy.ps1 @deploy -Action CreateChangeSet
.\scripts\aws\deploy.ps1 -Action InspectChangeSet `
  -ChangeSetName 'm7-g05-ssh-d2fa39877cc7478292ca37fac513d12a'
.\scripts\aws\deploy.ps1 -Action ExecuteChangeSet `
  -ChangeSetName 'm7-g05-ssh-d2fa39877cc7478292ca37fac513d12a' `
  -ConfirmExecution
```

O primeiro comando executa somente o preflight. O segundo cria um change set `UPDATE` sem executá-lo. O terceiro confirma o nome da stack, o estado `CREATE_COMPLETE/AVAILABLE`, o CIDR SSH atual e cada recurso afetado. A execução ocorre apenas na quarta invocação.

O primeiro change set revisado propunha substituir também o Security Group porque o texto de `GroupDescription` havia mudado; ele foi descartado. O template foi corrigido para preservar literalmente a descrição e a tag do grupo existente. O change set seguinte apresentou apenas:

- `ApplicationInstance`: `Modify`, `Replacement=True`, causado pela inclusão de `KeyName`;
- `ApplicationSecurityGroup`: `Modify`, `Replacement=False`, restrito às regras de rede.

Depois da execução, a instância antiga `i-0ee46033b616aeedc` foi terminada pelo CloudFormation e a nova instância `i-0f31228a6d73a765b` entrou em execução com as verificações de sistema e instância aprovadas. A stack terminou em `UPDATE_COMPLETE`.

O IPv4 público da EC2 muda quando a instância é parada e iniciada. Por isso, ele nunca foi fixado em scripts ou documentação operacional. A chave de host SSH foi validada antes da primeira conexão e gravada em `known_hosts`; conexões seguintes usam `StrictHostKeyChecking=yes`.

### 10.2.6 Bootstrap da instância

O User Data da EC2 é mantido em [`infra/aws/user-data.sh`](../infra/aws/user-data.sh). O [`deploy.ps1`](../scripts/aws/deploy.ps1) renderiza esse arquivo dentro do template antes de enviar o CloudFormation; o template-fonte recusa execução sem essa renderização.

Durante o primeiro boot, o script:

1. instala `openssh-server`, `rsyslog`, `logrotate`, `curl`, `gnupg` e certificados;
2. adiciona o repositório oficial do Docker para Ubuntu 24.04;
3. instala Docker CE, CLI, `containerd`, Buildx, Compose Plugin e `amazon-ecr-credential-helper`;
4. instala e inicia o Amazon CloudWatch Agent;
5. cria `/opt/m7`, `/etc/m7`, `/var/log/m7` e os diretórios persistentes;
6. grava o Compose renderizado em `/opt/m7/compose.prod.yml`;
7. cria `/etc/m7/deploy.env` com registry, tags, porta 80 e bind `127.0.0.1`;
8. configura o ECR credential helper para usar a instance profile, sem salvar senha de login;
9. cria os wrappers `/usr/local/bin/m7-compose`, `m7-compose-up` e `m7-rollback`;
10. cria serviços `systemd` para encaminhar os logs de cada contêiner a arquivos limitados por `logrotate`;
11. configura o CloudWatch Agent para coletar os logs dos sete serviços;
12. cria os volumes Docker de relatórios, notebook e RabbitMQ;
13. baixa backend, frontend e RabbitMQ, sem iniciar a aplicação antes da instalação dos secrets.

Os primeiros ensaios do bootstrap falharam porque o pacote `awscli` não existia no APT padrão do Ubuntu 24.04, o helper do ECR havia sido instalado em ordem incompatível com Docker CE e a URL do pacote do CloudWatch Agent estava incorreta. O script final removeu a dependência do AWS CLI na EC2, instalou Docker e o helper na mesma transação e corrigiu o bucket para `amazoncloudwatch-agent-$AWS_REGION`.

### 10.2.7 Instalação do runtime e inicialização da aplicação

O bootstrap não recebe secrets. Foi criado um `runtime.env` fora do repositório contendo as variáveis exigidas pelo backend e pelos workers: `GEMINI_API_KEY`, configuração do Azure Speech, `SUPABASE_DATABASE_URL`, identidades simuladas, `ALERT_CONFIRMATION_SECRET`, credenciais do RabbitMQ, `RABBITMQ_URL` e parâmetros do pool PostgreSQL. O arquivo não pode conter variáveis `AWS_*`.

Depois de confirmar o término do cloud-init, o arquivo foi enviado por um diretório temporário privado e instalado com permissões restritas:

```powershell
ssh -i <CHAVE_PRIVADA> ubuntu@<IP_EC2> `
  "umask 077; mkdir -p ~/.runtime-stage; chmod 700 ~/.runtime-stage"

scp -i <CHAVE_PRIVADA> -o StrictHostKeyChecking=yes `
  <RUNTIME_ENV_PROTEGIDO> `
  ubuntu@<IP_EC2>:.runtime-stage/runtime.env.incoming

ssh -i <CHAVE_PRIVADA> ubuntu@<IP_EC2>
```

Na EC2, a instalação e a subida foram concluídas com:

```bash
chmod 600 ~/.runtime-stage/runtime.env.incoming
sudo install -o root -g root -m 0600 \
  ~/.runtime-stage/runtime.env.incoming /etc/m7/runtime.env
rm -f ~/.runtime-stage/runtime.env.incoming
sudo /usr/local/bin/m7-compose-up
```

`m7-compose-up` valida a presença das variáveis, confirma que a URL AMQP corresponde às credenciais do RabbitMQ e inicia `rabbitmq`, `backend`, `frontend`, `scheduler`, `publisher`, `evaluator` e `notifier`. O arquivo instalado foi conferido como `root:root` modo `0600`.

> **Nota temporal — Sprint 5:** esse registro descreve o deploy anterior ao
> webhook de confirmação. O `compose.prod.yml` atual também declara o consumer
> `delivery`, mas não houve nova execução na AWS que comprove esse contêiner no
> ambiente publicado.

O frontend permaneceu em `127.0.0.1:80`; o backend e o broker não publicam portas no host. O health check interno foi executado antes de criar qualquer acesso externo:

```bash
sudo /usr/local/bin/m7-compose ps
curl --fail --silent --output /dev/null http://127.0.0.1:80/health
```

### 10.2.8 Atualização e rollback

O Compose e as tags não são atualizados automaticamente quando o repositório muda. Para instalar uma nova versão na mesma EC2 foi criado [`update-app.ps1`](../scripts/aws/update-app.ps1), acompanhado pelo executor [`update-app-remote.sh`](../scripts/aws/update-app-remote.sh).

Os parâmetros incluem o ID da instância, chave SSH, runtime protegido, registry, tags e digests esperados. Para instalar a versão final da Sprint 4, foi usado o seguinte mapeamento; apenas os dois caminhos protegidos dependem da estação do operador:

```powershell
$update = @{
  InstanceId = 'i-0f31228a6d73a765b'
  PrivateKeyPath = '<CHAVE_PRIVADA_FORA_DO_REPOSITORIO>'
  RuntimeEnvPath = '<RUNTIME_ENV_FORA_DO_REPOSITORIO>'
  EcrRegistryUri = '307432329071.dkr.ecr.us-east-1.amazonaws.com'
  BackendImageTag = 'f776feb352c3556d02e83dc14eea49b0d795f6b9'
  FrontendImageTag = 'f776feb352c3556d02e83dc14eea49b0d795f6b9'
  BackendImageDigest = 'sha256:1bb49e4cfb7a83881f2b1ea5741792bc916710ec565c5659d827097bf114b497'
  FrontendImageDigest = 'sha256:ee4cd9024f63519c0f64c061f7c47fbefbeba21b660c01e3bad0bac4e8e3e317'
}

.\scripts\aws\update-app.ps1 @update
```

O preflight valida STS, stack, EC2, key pair, host SSH, arquivos locais, Compose e correspondência das tags/digests no ECR. Depois da revisão, a atualização é iniciada explicitamente:

```powershell
.\scripts\aws\update-app.ps1 @update -Action Execute -ConfirmUpdate
```

O script cria um staging remoto com modo `0700`, transfere Compose, runtime, configuração do CloudWatch e executor, cria um backup root-only, atualiza as tags em `/etc/m7/deploy.env`, executa `pull`, recria os sete serviços e verifica `/health`. Se uma etapa falhar, o executor restaura os arquivos anteriores e tenta recuperar os contêineres.

Na primeira execução real foram corrigidos três problemas: o caminho do staging não era enviado ao executor, a configuração consumida do CloudWatch podia estar em um caminho diferente do canônico e as opções `tmpfs` dos workers precisavam estar entre aspas no YAML. Depois das correções, o fluxo terminou com health check aprovado.

O rollback de versão usa [`rollback.ps1`](../scripts/aws/rollback.ps1). Ele confirma previamente que as tags antigas ainda existem no ECR e que seus digests correspondem aos valores registrados. A execução remota exige `-ExecuteRollback -ConfirmRollback` e termina com nova verificação dos contêineres e de `/health`.

Na rotação posterior da chave Gemini, apenas o runtime protegido foi substituído. Backend e workers foram recriados primeiro e o frontend depois, pois o Nginx precisa resolver novamente o endereço interno do backend quando o contêiner é recriado. A chave foi comparada internamente sem imprimir seu valor e a chamada de chat confirmou o novo runtime.

### 10.2.9 Publicação com Cloudflare Quick Tunnel

O acesso externo foi configurado somente depois do health check interno. Foi instalado na EC2 o pacote oficial `cloudflared` para Linux amd64, versão `2026.9.3`, com verificação do checksum publicado. Em seguida foi criado o serviço `m7-cloudflared-quick.service` com usuário sem privilégios, `NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome=true`, reinício automático e o comando:

```bash
/usr/bin/cloudflared tunnel --no-autoupdate --protocol http2 \
  --url http://127.0.0.1:80
```

O túnel não exige entrada TCP/80 ou TCP/443 na EC2. Ele inicia conexões de saída para a Cloudflare pelas portas permitidas no Security Group. DNS, API Cloudflare, TCP/HTTP2 e UDP/QUIC foram verificados pelo próprio `cloudflared`.

O serviço foi habilitado para iniciar junto com a EC2:

```bash
sudo systemctl enable --now m7-cloudflared-quick
sudo systemctl is-active m7-cloudflared-quick
```

O endereço atual é obtido pelo journal:

```bash
sudo journalctl -u m7-cloudflared-quick --no-pager \
  | grep -Eo 'https://[^ ]+\.trycloudflare\.com' \
  | tail -1
```

O subdomínio `trycloudflare.com` é temporário e muda quando o túnel é recriado. Qualquer pessoa com o link consegue abrir a aplicação; por isso, o endereço é compartilhado somente com o grupo e o cliente durante a janela de teste. O endpoint `/api/chat` consome a cota Gemini e não deve ser divulgado publicamente.

### 10.2.10 Validação e resultado da Sprint 4

Depois da subida dos serviços e da criação do túnel, os testes foram repetidos pela rede externa. O estado final registrado foi:

| Verificação | Resultado |
|---|---|
| Stack `m7-g05-mvp` | `UPDATE_COMPLETE` |
| EC2 | `running`, verificações de sistema e instância aprovadas |
| Backend | `healthy` |
| Frontend | `healthy` |
| RabbitMQ | `healthy` |
| Scheduler, publisher, evaluator e notifier | Em execução |
| Runtime | `/etc/m7/runtime.env`, `root:root`, modo `0600` |
| Conexão ao Supabase a partir do backend | Aprovada |
| `GET /health` interno | HTTP 200 |
| `GET /health` pelo Quick Tunnel | HTTP 200 |
| `GET /` pelo Quick Tunnel | HTTP 200 |
| `POST /api/chat` pelo Quick Tunnel | HTTP 200, texto e modelo presentes |
| Serviço do Cloudflare | `active`, sem reinícios na verificação |

Com essas evidências, a aplicação foi considerada **funcional na nuvem na Sprint 4**. O ambiente é adequado à demonstração acadêmica e aos testes controlados da equipe. Ele não representa produção nem homologação corporativa. O fluxo de áudio real não foi reexecutado pelo endereço público nessa validação final e não compõe a evidência de encerramento.

### 10.2.11 Operação após o deploy

Para verificar o ambiente em uma nova sessão:

```bash
sudo /usr/local/bin/m7-compose ps
curl --fail --silent --output /dev/null http://127.0.0.1:80/health
sudo systemctl is-active m7-cloudflared-quick
```

A EC2 pode ser interrompida entre as demonstrações para reduzir consumo. Ao iniciá-la novamente, seu IPv4 público provavelmente mudará. O operador deve consultar o novo endereço, atualizar a regra SSH para o IPv4 atual em `/32`, validar a chave de host e obter o novo endereço do Quick Tunnel. Durante a operação, o provedor do operador alternou entre dois IPv4; os dois foram autorizados temporariamente como `/32`, sem abrir SSH para `0.0.0.0/0`.

Os contêineres do Docker Desktop local não sustentam a aplicação na AWS e podem ser desligados. Na EC2, os serviços usam `restart: unless-stopped` e voltam com o Docker, mas o health check deve ser repetido antes de compartilhar o link.

Para encerrar apenas o acesso externo:

```bash
sudo systemctl disable --now m7-cloudflared-quick
```

Para parar a aplicação antes de interromper a instância:

```bash
sudo /usr/local/bin/m7-compose stop
```

Não se deve usar `docker compose down -v` enquanto os volumes de RabbitMQ ou artefatos ainda forem necessários. Mesmo com a EC2 parada, EBS, ECR e CloudWatch continuam armazenados e podem gerar custo. As principais limitações permanecem sendo as credenciais temporárias do Learner Lab, o SSH dependente do IP do operador, a URL temporária do Cloudflare e a ausência de autenticação adequada para divulgação pública.

Os procedimentos detalhados de diagnóstico, atualização, rollback e encerramento, assim como o histórico das decisões de implantação, estão consolidados nesta seção e nas stories de [infraestrutura AWS](stories/phase-4-aws-mvp.md), [substituição da EC2](stories/phase-4-ec2-ssh-replacement-preparation.md) e [workers/atualização](stories/phase-4-alert-workers-local-update.md).

# 11. Análise de Viabilidade Financeira

Esta seção simula a equipe como uma startup contratada pelo Metrô de São Paulo. Todos os valores estão em reais e representam estimativas para uma venda hipotética do MVP. A análise separa **custos diretos**, necessários para construir a solução, de **despesas operacionais**, necessárias para manter a empresa e viabilizar a entrega, e da **despesa financeira** do empréstimo. O orçamento também incorpora tributos calculados por dentro, lucro e o fluxo de caixa necessário para pagar as obrigações durante o desenvolvimento.

## 11.1 Escopo considerado no orçamento

O objeto da proposta é a entrega, em **7 de outubro de 2026**, de um MVP demonstrável do agente de IA para apoio à gestão do portfólio de projetos do Metrô. O produto utiliza dados sintéticos e contempla as funcionalidades, a arquitetura, os testes, a documentação e o deploy descritos neste documento.

O projeto ocorre entre **3 de agosto e 7 de outubro de 2026**, totalizando dez semanas de calendário e **47 dias úteis de trabalho**, após a exclusão do feriado nacional de 7 de setembro. Foram consideradas seis pessoas desenvolvedoras juniores, contratadas como prestadoras de serviço PJ, com dedicação de oito horas por dia útil. O contrato simulado termina com a entrega: manutenção evolutiva, operação assistida e suporte posterior a 7 de outubro não integram o preço.

## 11.2 Custos diretos do projeto

Custos diretos são os recursos consumidos na produção do MVP e que podem ser atribuídos à entrega. Eles abrangem o trabalho técnico da equipe e as ferramentas usadas diretamente no desenvolvimento.

### 11.2.1 Equipe de desenvolvimento

Cada integrante trabalha 376 horas no período, calculadas por `47 dias úteis × 8 horas`. Como os seis integrantes têm a mesma senioridade, dedicação e responsabilidade de execução, foi aplicada a mesma taxa de **R$ 50,00 por hora**.

| Integrante | Função orçada | Horas | Valor por hora | Custo |
|---|---|---:|---:|---:|
| Felipe Neves | Pessoa desenvolvedora júnior PJ — interface e experiência de uso | 376 | R$ 50,00 | R$ 18.800,00 |
| Henrique Diniz | Pessoa desenvolvedora júnior PJ — PLN e classificação de intenções | 376 | R$ 50,00 | R$ 18.800,00 |
| Jaime Almeida | Pessoa desenvolvedora júnior PJ — dados, voz e testes | 376 | R$ 50,00 | R$ 18.800,00 |
| Leonardo Ramos | Pessoa desenvolvedora júnior PJ — integração e deploy | 376 | R$ 50,00 | R$ 18.800,00 |
| Pedro Uchoa | Pessoa desenvolvedora júnior PJ — integração e qualidade | 376 | R$ 50,00 | R$ 18.800,00 |
| Wendel Feitosa | Pessoa desenvolvedora júnior PJ — backend e áudio | 376 | R$ 50,00 | R$ 18.800,00 |
| **Total da equipe** | **6 pessoas** | **2.256** |  | **R$ 112.800,00** |

A taxa de R$ 50,00 por hora equivale a R$ 8.000,00 para um mês de 160 horas. Ela foi adotada como taxa comercial PJ, que precisa remunerar o trabalho e também compensar a ausência de férias, décimo terceiro, FGTS e demais benefícios típicos de um vínculo CLT. Como referência externa para a ordem de grandeza da remuneração, foi consultado o [Guia Salarial 2026 da Robert Half](https://www.roberthalf.com/br/pt/insights/salary-guide) e sua página para [desenvolvimento full-stack júnior](https://www.roberthalf.com/br/pt/vagas-detalhes/desenvolvedora-full-stack-junior). O valor também mantém o custo da equipe próximo da referência de R$ 111.625,00 observada no feedback fornecido para outro projeto, com a diferença explicada pelas horas efetivas e pela taxa única adotada neste caso.

### 11.2.2 Ferramentas e serviços diretamente ligados à entrega

| Item | Premissa | Custo |
|---|---|---:|
| Codex | Verba simulada de R$ 100,00 por mês para cada uma das 6 pessoas, durante 3 meses | R$ 1.800,00 |
| Gemini | Franquia estimada para desenvolvimento, integração e testes do agente | R$ 500,00 |
| Azure AI Speech | Franquia estimada para integração e testes de transcrição de voz | R$ 300,00 |
| **Total de ferramentas diretas** |  | **R$ 2.600,00** |

O valor de Codex é uma **premissa interna do orçamento**, definida pelo grupo, e não uma conversão de um preço oficial em reais. Os valores de Gemini e Azure AI Speech são franquias controladas para o MVP e devem ser revistos se o volume real de chamadas superar o cenário de demonstração.

Assim, os custos diretos totalizam:

| Categoria de custo | Valor |
|---|---:|
| Equipe de desenvolvimento | R$ 112.800,00 |
| Ferramentas e serviços diretos | R$ 2.600,00 |
| **Total de custos diretos** | **R$ 115.400,00** |

## 11.3 Despesas operacionais

Despesas operacionais são gastos necessários para administrar a startup, divulgar a solução e disponibilizar o ambiente do MVP, mas que não correspondem diretamente às horas de construção das funcionalidades.

| Despesa | Premissa de cálculo | Valor estimado |
|---|---|---:|
| Recursos humanos terceirizado | 40 horas × R$ 75,00 para contratos, cadastro e apoio às pessoas prestadoras | R$ 3.000,00 |
| Financeiro terceirizado | 90 horas × R$ 75,00 para contas a pagar, cobrança, conciliação e fluxo de caixa | R$ 6.750,00 |
| Contabilidade | 3 meses × R$ 1.000,00 para escrituração e apuração tributária simuladas | R$ 3.000,00 |
| Divulgação e marketing | 40 horas × R$ 50,00 para apresentação comercial e comunicação da solução | R$ 2.000,00 |
| Materiais de divulgação | Peças digitais e materiais para a demonstração | R$ 300,00 |
| Infraestrutura do MVP | AWS, monitoramento e Supabase durante a janela necessária | R$ 721,36 |
| **Total de despesas operacionais** |  | **R$ 15.771,36** |

Não foi incluída uma rubrica separada de gestão do projeto: planejamento, cerimônias, coordenação técnica e documentação estão absorvidos nas horas da equipe. Também não foi incluído atendimento ao cliente após a entrega, porque o contrato hipotético termina em 7 de outubro. Essa delimitação evita cobrar atividades que não pertencem ao escopo contratado.

### 11.3.1 Infraestrutura minimizada para o MVP

A infraestrutura considera a EC2 ativa por aproximadamente seis semanas, entre **31 de agosto e 7 de outubro de 2026**, a partir do início da Sprint 3, além dos recursos mínimos de persistência, armazenamento de imagens, observabilidade e banco gerenciado. Para converter os preços de referência em dólar, foi utilizada a PTAX de venda de **R$ 5,1795 por US$ 1,00**, consultada para 24 de setembro de 2026.

| Recurso | Premissa | Valor estimado |
|---|---|---:|
| EC2 `t3.large` | Execução sob demanda por aproximadamente 6 semanas | R$ 393,01 |
| EBS `gp3`, 50 GB | Volume persistente durante o período do projeto | R$ 26,24 |
| IPv4 público | Endereço público durante a janela de execução | R$ 23,62 |
| Amazon ECR | Armazenamento das imagens de backend e frontend | R$ 6,56 |
| Amazon CloudWatch | Logs e métricas essenciais do ambiente | R$ 12,95 |
| Supabase Pro | Banco gerenciado por aproximadamente 2 meses | R$ 258,98 |
| **Total de infraestrutura** |  | **R$ 721,36** |

Os valores foram estimados a partir das páginas oficiais de preços da [AWS EC2 T3](https://aws.amazon.com/ec2/instance-types/t3/), [EBS](https://aws.amazon.com/ebs/volume-types/), [ECR](https://aws.amazon.com/ecr/pricing/), [CloudWatch](https://aws.amazon.com/cloudwatch/pricing/), [IPv4 público](https://aws.amazon.com/vpc/pricing/) e [Supabase](https://supabase.com/pricing). A arquitetura foi dimensionada para demonstração e testes controlados, sem alta disponibilidade, domínio pago ou redundância de produção. Essa escolha mantém a infraestrutura proporcional ao MVP descrito na Seção 10.

## 11.4 Carga tributária estimada

Para a simulação, a startup foi enquadrada no **Simples Nacional, Anexo V**, com receita bruta acumulada nos 12 meses (RBT12) hipotética de **R$ 200.000,00**. Esse valor posiciona a empresa na segunda faixa do Anexo V, com alíquota nominal de 18% e parcela a deduzir de R$ 4.500,00. A alíquota efetiva única é:

`Alíquota efetiva = (RBT12 × alíquota nominal − parcela a deduzir) ÷ RBT12`

`Alíquota efetiva = (R$ 200.000,00 × 18% − R$ 4.500,00) ÷ R$ 200.000,00 = 15,75%`

O percentual de **15,75%** incide sobre o preço cobrado do cliente. Por isso, o imposto não foi apenas somado ao custo: ele foi calculado **por dentro**, de modo que o próprio preço contenha a receita necessária para pagar o tributo. A hipótese usa uma única porcentagem, conforme solicitado no barema, e segue a tabela do [Anexo V da Lei Complementar nº 123/2006](https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp123.htm). Em uma contratação real, o enquadramento, a RBT12 e o fator R precisariam ser confirmados pela contabilidade.

## 11.5 Margem de lucro desejada

A margem desejada é de **15% sobre a soma de custos, despesas operacionais, despesa financeira e impostos**. Ela foi escolhida como estratégia de entrada para uma startup que entrega um primeiro MVP a um cliente institucional: remunera o risco técnico e comercial sem elevar a proposta ao patamar de uma solução produtiva com sustentação e alta disponibilidade.

Como o recebimento integral ocorre somente na entrega, os juros do empréstimo fazem parte da despesa necessária para executar o contrato. O custo financeiro estimado é de **R$ 5.684,09**, calculado sobre o principal de R$ 131.171,36, à taxa de 2% ao mês, pelo prazo de 65 dias. Esse valor foi incorporado à formação do preço para que o lucro permaneça em 15% após a quitação do financiamento.

Como o imposto depende do preço e a margem também inclui o imposto em sua base, o preço foi obtido pela seguinte equação:

`P = B × (1 + m) ÷ [1 − t × (1 + m)]`

Onde `P` é o preço final, `B` é a base de custos, despesas operacionais e despesa financeira, `m` é a margem e `t` é a alíquota tributária. Substituindo `B = R$ 136.855,45`, `m = 15%` e `t = 15,75%`, obtém-se **P = R$ 192.195,11**. O imposto contido nesse preço é de **R$ 30.270,73**. O lucro de **R$ 25.068,93** corresponde a 15% de `R$ 136.855,45 + R$ 30.270,73`.

## 11.6 Preço final do projeto

| Componente do preço | Valor |
|---|---:|
| Custos diretos | R$ 115.400,00 |
| Despesas operacionais | R$ 15.771,36 |
| Despesa financeira do empréstimo | R$ 5.684,09 |
| **Base antes de tributos e lucro** | **R$ 136.855,45** |
| Imposto, calculado por dentro a 15,75% do preço | R$ 30.270,73 |
| Lucro desejado, 15% sobre custos + despesas + juros + impostos | R$ 25.068,93 |
| **Preço final para o Metrô de São Paulo** | **R$ 192.195,11** |

Os valores, as fórmulas e as premissas detalhadas podem ser consultados na [planilha de precificação do projeto](https://docs.google.com/spreadsheets/d/1okRWK8HoPHITbrlPIta1h3NH3-2euzaHEm_N-hrCl30/edit?usp=sharing).

O preço corresponde a uma entrega fechada do MVP e não deve ser interpretado como mensalidade. Qualquer extensão de prazo, uso de dados reais, adequação ao ambiente corporativo do Metrô, suporte continuado ou transformação do MVP em produto de produção exigiria novo orçamento.

## 11.7 Defesa das premissas e dos valores

| Premissa | Defesa |
|---|---|
| 2.256 horas de desenvolvimento | A carga deriva do calendário real: 6 pessoas × 47 dias úteis × 8 horas. Ela evita tratar um projeto de dedicação integral como atividade parcial. |
| R$ 50,00 por hora PJ | Corresponde a R$ 8.000,00 por 160 horas e inclui o risco contratual da prestação PJ. A taxa é uniforme porque senioridade e dedicação são iguais entre os seis integrantes. |
| R$ 112.800,00 de equipe | Representa 86,0% da base de custos e despesas, proporção coerente com um projeto de software intensivo em trabalho especializado. Também se aproxima da referência de R$ 111.625,00 citada no feedback da professora. |
| Ferramentas limitadas a R$ 2.600,00 | São franquias específicas para desenvolvimento e testes do MVP. Não foram incluídas licenças corporativas ou volumes de produção que o escopo não exige. |
| Infraestrutura de R$ 721,36 | A EC2 fica ligada apenas na janela de seis semanas e os serviços foram dimensionados para demonstração. A ausência de alta disponibilidade e domínio pago reduz o custo sem ocultar os componentes utilizados. |
| Apoio terceirizado | RH, financeiro e contabilidade representam funções reais de uma startup com seis prestadores. As horas foram limitadas ao período do contrato. |
| Marketing de R$ 2.300,00 | O projeto prevê divulgação leve e preparação da apresentação comercial, compatíveis com uma venda institucional dirigida, sem campanha de mídia ampla. |
| Juros de R$ 5.684,09 | A despesa financeira decorre do pagamento integral apenas na entrega. Ela foi calculada a 2% ao mês por 65 dias e incorporada ao preço para não reduzir o lucro desejado. |
| Imposto de 15,75% | A alíquota efetiva deriva de uma RBT12 explicitamente simulada e é aplicada sobre a receita. O cálculo por dentro impede que o tributo reduza a margem planejada. |
| Lucro de 15% | É uma margem de entrada para o MVP. Incide sobre custos, despesas operacionais, juros e imposto, preservando a rentabilidade mesmo após a quitação do empréstimo. |

## 11.8 Fluxo de caixa sintético

O cronograma completo de entradas, saídas e saldos está disponível na [planilha de fluxo de caixa do projeto](https://docs.google.com/spreadsheets/d/1yrltco3si6FzcyDPYJFIB3E7hWGV1H-1uU3Cttr9AMk/edit?usp=sharing).

O orçamento mede o resultado econômico do contrato, enquanto o fluxo de caixa verifica se há dinheiro disponível nas datas de pagamento. Como a simulação prevê o pagamento integral pelo Metrô apenas na entrega, em 7 de outubro, a startup precisa financiar os desembolsos de agosto, setembro e do início de outubro.

Foi simulado um empréstimo recebido em **3 de agosto de 2026**, no valor de **R$ 131.171,36**, exatamente igual ao total de custos diretos e despesas operacionais. A taxa assumida é de **2% ao mês**, com juros simples proporcionais por 65 dias:

`Juros = R$ 131.171,36 × 2% × (65 ÷ 30) = R$ 5.684,09`

O empréstimo continua limitado a R$ 131.171,36 porque precisa financiar somente os custos diretos e as despesas operacionais anteriores ao recebimento. Os juros não aumentam o principal: eles são pagos após a entrada do cliente e foram incorporados ao preço de venda.

O Metrô paga R$ 192.195,11 em 7 de outubro. Na mesma data, após o recebimento, a startup quita o principal e os juros do empréstimo. O imposto de R$ 30.270,73 é pago em 20 de novembro, data sintética adotada para evidenciar a obrigação tributária após o faturamento.

| Mês | Saldo inicial | Entradas | Saídas do projeto | Principal do empréstimo | Juros | Impostos | Saldo final |
|---|---:|---:|---:|---:|---:|---:|---:|
| Agosto/2026 | R$ 0,00 | R$ 131.171,36 | R$ 55.261,83 | R$ 0,00 | R$ 0,00 | R$ 0,00 | R$ 75.909,53 |
| Setembro/2026 | R$ 75.909,53 | R$ 0,00 | R$ 57.534,30 | R$ 0,00 | R$ 0,00 | R$ 0,00 | R$ 18.375,23 |
| Outubro/2026 | R$ 18.375,23 | R$ 192.195,11 | R$ 18.375,23 | R$ 131.171,36 | R$ 5.684,09 | R$ 0,00 | R$ 55.339,66 |
| Novembro/2026 | R$ 55.339,66 | R$ 0,00 | R$ 0,00 | R$ 0,00 | R$ 0,00 | R$ 30.270,73 | **R$ 25.068,93** |
| **Total** |  | **R$ 323.366,47** | **R$ 131.171,36** | **R$ 131.171,36** | **R$ 5.684,09** | **R$ 30.270,73** | **R$ 25.068,93** |

Antes do recebimento do cliente, o empréstimo é totalmente consumido pelos R$ 131.171,36 de custos e despesas, de modo que o menor saldo projetado é zero. A conciliação final é:

`Lucro após financiamento = resultado antes do financiamento − juros`

`Lucro após financiamento = R$ 30.753,02 − R$ 5.684,09 = R$ 25.068,93`

O fluxo confirma que todos os pagamentos mapeados podem ser liquidados e que o saldo final coincide com o lucro desejado. Os R$ 25.068,93 representam exatamente 15% da soma de custos diretos, despesas operacionais, juros e imposto. Em relação ao preço de venda, esse resultado corresponde a aproximadamente 13,04%, pois o percentual de 15% foi aplicado sobre a base definida no barema e não diretamente sobre a receita. A simulação não inclui IOF, tarifa de abertura, custo bancário, atraso do cliente nem reserva de contingência; em uma proposta real, esses itens também deveriam compor o preço ou uma linha de crédito adicional. Um adiantamento do Metrô reduziria a necessidade de capital de giro.

## 11.9 Conclusão da viabilidade

Nas premissas adotadas, a entrega é financeiramente viável pelo preço de **R$ 192.195,11**. Esse valor paga os R$ 115.400,00 de custos diretos, os R$ 15.771,36 de despesas operacionais, os R$ 5.684,09 de juros, o imposto único estimado em R$ 30.270,73 e o lucro de R$ 25.068,93. O empréstimo de R$ 131.171,36 resolve o descasamento entre os pagamentos do desenvolvimento e o recebimento final, enquanto a inclusão dos juros na formação do preço preserva o lucro desejado de 15% após a quitação. Portanto, a viabilidade depende de cumprir o prazo, controlar o uso das ferramentas e receber do cliente na data contratada.

# 12. Benefícios Entregues e Aperfeiçoamentos Futuros

Esta seção registra o valor que a prova de conceito entrega ao PMO do Metrô e prioriza as melhorias que ficam para depois do módulo. Cada benefício está ligado à funcionalidade que o produz e à evidência que o sustenta, de modo que nenhum deles depende de declaração: todos remetem a uma medição ou a um registro de execução do próprio documento.

## 12.1 Benefícios entregues

Os Business Drivers da Seção 2.10 definiram quatro resultados esperados: agilizar o acesso às informações (BD01), ampliar a capacidade de análise (BD02), aumentar a confiabilidade das respostas (BD03) e tornar a interação mais acessível (BD04). A tabela mostra o que foi efetivamente entregue para cada um.

| Benefício entregue | Funcionalidade que o produz | Evidência | Driver |
| --- | --- | --- | :---: |
| Consulta ao portfólio em linguagem comum, sem conhecer a estrutura dos documentos | Pipeline de PLN com entrada por texto e por voz (Seções 8.7, 8.8 e 8.11) | No teste de usabilidade, a pergunta em linguagem comum funcionou sem comando técnico nas seis sessões, e a transcrição por voz preservou a intenção em todas elas (Seção 9.3.2) | BD04 |
| Identificação confiável do que foi pedido | Classificador hierárquico de intenções, versão 2 (Seção 8.10.7) | F1-macro de 0,8327 na intenção específica, sobre 1.135 solicitações de teste mantidas fechadas durante a seleção, acima do mínimo de 0,80 (Seção 9.2) | BD01, BD04 |
| Respostas que indicam a origem e declaram o que não sabem | Recuperação com citação de fonte e resposta controlada quando falta informação (Seção 8.5) | 91,67% de respostas fundamentadas e 4,17% de alucinação na amostra avaliada às cegas, dentro dos limites de 90% e 5% do RNF04 (Seção 9.2) | BD03 |
| Resposta em tempo de conversa | Pipeline completo de classificação, recuperação e geração | P95 de consulta simples entre 7,0 e 7,6 s, contra teto de 10 s do RNF05, sem erro em 1.379 requisições (Seção 9.2) | BD01 |
| Relatório executivo sem redação manual | Despacho determinístico de `transacao_gerar_relatorio`, sem LLM na decisão da rota (Seção 8.5.10) | Geração rastreável com webhook de resultado e entrega pela fila (Seções 8.5.10 e 8.5.12) | BD02 |
| Fim da cobrança manual de prazos | Alerta autônomo de atraso, configurado por fluxo guiado no chat (Seção 8.5.11) | Execução registrada em `src/backend/evidencias/alerta-prazo-atraso/` | BD01 |
| Próximo passo sugerido sem perda de controle | Sugestão proativa com confirmação explícita e controle de ativação | Nenhuma sugestão é executada sem confirmação, e desativar as sugestões não altera a resposta principal (RF09 e RF10, Seção 3.1) | BD02 |
| Menos espera e menos custo no provedor de voz | Cache VHS de transcrições (Seção 9.4) | Contra o Azure real, quatro de cinco envios repetidos foram servidos do cache em cerca de 0,1 ms, contra 1.540 ms da chamada ao provedor (Seção 9.4.2) | BD01 |
| Solução demonstrável fora da máquina da equipe | Publicação em AWS EC2, com banco no Supabase (Seção 10.2) | Aplicação validada pela rede externa ao fim da Sprint 4 (Seção 10.2.10) | — |

**O que os benefícios ainda não comprovam.** Três limites acompanham a leitura da tabela. O primeiro é que o RNF06 consolidado segue reprovado pela recuperação: a classificação passou, mas o *recall*@3 das fontes ficou em 0,556, contra o mínimo de 0,80 (Seção 9.2). O benefício de identificar o que foi pedido está entregue; o de encontrar sempre a fonte certa, ainda não. O segundo é que a percepção declarada no SUS, com média de 86,25, é mais favorável do que a observação das tarefas: nenhum participante concluiu sem dificuldade os cenários de informação ausente e de sugestão proativa (Seção 9.3.2). O terceiro é que todas as medições usam massa sintética, com um único projeto, em ambiente de demonstração, e não o portfólio real nem o ambiente corporativo do Metrô.

## 12.2 Aperfeiçoamentos futuros

A ordem segue dois critérios, nesta precedência. Primeiro vem o que hoje reprova um requisito ou impede o uso pelo PMO, porque nenhum ganho novo compensa uma resposta que não encontra a fonte certa. Depois vêm os pedidos do parceiro com menor custo de construção, porque reaproveitam infraestrutura que já existe.

**Prioridade 1 — reprovam requisito ou impedem o uso real**

| # | Aperfeiçoamento | Motivo | Ponto de partida |
| :---: | --- | --- | --- |
| 1 | Base documental de portfólio para a recuperação | Reprova a recuperação do RNF06 (*recall*@3 de 0,556). A massa tem um único projeto, e as listas simuladas do SharePoint ainda tratam de atendimento ao passageiro, não de portfólio | Pedido do parceiro de reproduzir a estrutura do SharePoint do Metrô; o contrato de leitura das listas já existe (Seção 8.5) |
| 2 | Medição com solicitações reais do PMO | Classificação e recuperação foram medidas em frases sintéticas derivadas de templates; o desempenho com perguntas reais não é conhecido | Protocolo de avaliação reutilizável das Seções 8.10.1 e 9.2 |
| 3 | Usabilidade com os perfis ainda não cobertos | As vagas de gestão de projetos, análise de indicadores e ferramentas Microsoft ficaram sem participante; as respostas não foram avaliadas por quem acompanha o portfólio na rotina | Roteiro, planilha e SUS da Seção 9.3.1 |
| 4 | Homologação no ambiente corporativo | Entra ID, Azure e Teams dependem do provisionamento da GTI; a coleta do VHS na imagem publicada acompanha a publicação final | Roteiros das Seções 9.4.2 e 10.2 |

**Prioridade 2 — pedidos do parceiro que reaproveitam infraestrutura existente**

| # | Aperfeiçoamento | O que já existe | O que falta |
| :---: | --- | --- | --- |
| 5 | Lembretes do projeto | Agendador, filas e central de notificações do alerta de prazo (Seção 8.5.11) | Intenção de lembrete, fluxo guiado e disparo por horário, e não por condição de atraso |
| 6 | Tarefas e calendário do projeto no chat | Dados em `schedule_items` e `project_deliverables_milestones` (Seção 4.4) | Rota de leitura por projeto e as visões de lista e de calendário |
| 7 | Agente exposto como servidor MCP | Rotas de consulta, relatório e alerta com contrato estável | Ferramentas MCP com autenticação, para o próprio Metrô conectar o agente ao Copilot sem depender do Copilot Studio, hoje indisponível para a equipe |
| 8 | Integração com o Microsoft Teams | Contrato OpenAPI e arquitetura com o Teams como canal previsto (Seção 5.2) | Canal publicado no tenant do Metrô, após homologação |

Os itens 5 e 6 estavam na linha de corte do planejamento da Sprint 5, que previa registrá-los aqui caso não coubessem na capacidade (Seção 6.5.1 do `GestaoProjeto.md`).

**Prioridade 3 — evolução técnica**

| # | Aperfeiçoamento | Motivo |
| :---: | --- | --- |
| 9 | Cache VHS compartilhado entre réplicas | O cache é hoje em memória e por processo, com validade de 300 s; não sobrevive a reinício e impede escalar a API horizontalmente sem perder os acertos |
| 10 | Lock do classificador restrito ao carregamento | O lock global serializa todas as classificações, embora só o carregamento dos artefatos precise dele; a medição da Seção 8.11.8 mostrou vazão até 2,3 vezes maior sem ele |
| 11 | Ajuste supervisionado do encoder | O encoder é usado congelado, como extrator de atributos; o ajuste para as intenções do projeto depende de GPU |
| 12 | Integração com o Power BI | Evolução prevista desde o Canvas da Seção 2.9, para levar os indicadores do agente aos painéis que o PMO já usa |


# 13. Plano de Adoção e Mobilização do Ecossistema

O agente só gera valor se o PMO, os líderes e a diretoria do Metrô passarem a usá-lo na rotina, e o principal obstáculo para isso não é técnico. A Seção 2.2 registra que experiências anteriores do parceiro com IA generativa falharam porque as respostas nem sempre estavam fundamentadas na documentação oficial, e que isso reduziu a confiança das equipes. A adoção, portanto, parte de uma confiança já quebrada naquele PMO, e não de um terreno neutro. Esta seção descreve quem vai usar o agente, o que deve travar cada público e o que a solução faz, na prática, para destravar.

## 13.1 Mapa de adoção e aculturamento organizacional

### 13.1.1 Público-alvo principal

O público é definido pelos perfis de acesso do modelo de dados, e não por cargos genéricos. Cada usuário tem um `role_name` na tabela `users`, e as regras de `access_rules` delimitam, por subportfólio ou por projeto, o que ele pode ler, alterar e exportar (Seção 4.4). As personas da Seção 2.5 correspondem a esses perfis.

| Perfil no sistema | Quem é no Metrô | Persona | O que faz com o agente | Alcance da permissão |
| --- | --- | --- | --- | --- |
| `pmo` | Analistas do PMO Corporativo, responsáveis pela consolidação e pela qualidade dos dados do portfólio | Mariana | Consolida o balanço mensal, confere consistência, gera o relatório executivo e configura alertas de prazo | Portfólio inteiro, com leitura e exportação |
| `lider_subportfolio` | Gerentes de portfólio de cada subportfólio | Carlos | Prepara reuniões de acompanhamento, compara projetos, investiga desvios e recebe alertas | Projetos do próprio subportfólio |
| `equipe_projeto` | Líderes e equipes que alimentam os documentos de cada projeto | — | Consulta o próprio projeto e responde às pendências de atualização | Projetos em que atua |
| `diretoria` | Diretoria de Planejamento e Gestão Estratégica | Roberto | Lê resumos executivos com fonte, sem navegar nos documentos | Visão consolidada, sem edição |
| `gti` | Gerência de Tecnologia da Informação | — | Homologa o ambiente, provisiona Entra ID, Azure e Teams e opera a solução | Infraestrutura, não o conteúdo do portfólio |
| `admin` | Equipe de sustentação do agente | — | Mantém catálogo de intenções, léxico do domínio e regras de acesso | Configuração do agente |

O público de **entrada** é o PMO. É ali que a dor central do projeto se concentra — a consolidação manual do balanço mensal, descrita na jornada de Mariana — e é o perfil com maior afinidade tecnológica e com acesso ao portfólio inteiro, o que permite medir o ganho antes de expandir. Os líderes de subportfólio entram em seguida, porque dependem de dados que o PMO já validou. A diretoria entra por último, quando já houver histórico de respostas confiáveis: é o público que menos tolera erro e o que tem menos tempo para aprender uma ferramenta nova.

### 13.1.2 Barreiras culturais e técnicas esperadas

As barreiras abaixo foram extraídas de fatos do próprio projeto — do diagnóstico do problema, das restrições do parceiro e do que foi observado no teste de usabilidade da Seção 9.3 —, e não de uma lista genérica de resistência à mudança.

| Barreira | Tipo | Público mais afetado | De onde vem |
| --- | --- | --- | --- |
| Desconfiança em resposta gerada por IA | Cultural | PMO e diretoria | Experiência anterior do Metrô com IA generativa sem lastro documental (Seção 2.2) |
| Receio de expor dado confidencial | Cultural e técnica | Todos, sobretudo a GTI | Restrição de que dado sensível de projeto não trafegue por serviço não homologado (Seção 2.1, RNF01) |
| Medo de perder o controle do próprio trabalho | Cultural | PMO e equipes de projeto | A consolidação é a atividade do PMO; uma ferramenta que a executa pode ser lida como substituição, e não como apoio |
| Receio de alteração indevida de dados | Cultural e técnica | `pmo`, `lider_subportfolio` | Um agente que escreve no portfólio, por linguagem natural, sem que a pessoa veja o que vai mudar |
| Não saber o que perguntar nem como | Técnica | `equipe_projeto` e quem tem pouca familiaridade com agentes | No teste, um participante procurou um menu de comandos antes de digitar, e perguntas curtas sobre temas da base foram recusadas (ocorrência O1, Seção 9.3.2) |
| Não perceber a fonte nem o controle da sugestão | Técnica | Todos | Dois participantes não viram a fonte citada na primeira leitura; o controle da proatividade não foi percebido sem ajuda (O8) |
| Mais uma ferramenta na rotina | Cultural | Diretoria e líderes | O PMO já opera SharePoint, Excel, Power BI e Teams; uma interface nova compete por atenção |
| Ciclo longo de homologação | Técnica e organizacional | GTI e patrocinadores | A adoção de tecnologia nova depende de provisionamento da GTI e de aprovação de compliance (Seção 2.1) |

### 13.1.3 Ações de onboarding e educação

Cada ação responde a uma barreira da tabela anterior. Parte delas já está no comportamento do agente, e o onboarding consiste em torná-las visíveis; a outra parte é organizacional e depende do patrocínio do PMO.

**O que o próprio agente já faz para educar**

| Ação | Barreira atendida | Como funciona |
| --- | --- | --- |
| Toda resposta cita a fonte e declara quando não sabe | Desconfiança em IA | A resposta remete ao documento consultado e, sem informação suficiente, declara o limite em vez de completar (RF08). É a resposta direta à experiência anterior do PMO, e por isso o onboarding começa por ela |
| Classificação antes da geração | Receio de expor dado | A solicitação é classificada localmente, e só o contexto estruturado e validado segue para a camada generativa; fora de escopo recebe resposta controlada, sem chamar o provedor (Seção 8.11.5) |
| Prévia com confirmação assinada antes de criar alerta ou relatório | Receio de alteração indevida | O agente mostra o resumo do que será criado e só executa após confirmação explícita. A confirmação carrega uma assinatura da prévia exibida, e o backend recusa confirmar uma versão diferente da que a pessoa viu (Seções 8.5.10 e 8.5.11) |
| Sugestão sempre opcional e desativável | Medo de perder o controle | Nenhuma sugestão é executada sem confirmação, e o controle de proatividade desliga as sugestões sem alterar a resposta principal (RF09 e RF10) |
| Fluxo guiado em vez de formulário | Não saber o que perguntar | Relatório e alerta são configurados por perguntas sucessivas no chat, com opções a escolher, como no alerta de prazo (Seção 8.5.11) |

**O que a implantação precisa fazer**

| Fase | Público | Ação | Critério para avançar |
| :---: | --- | --- | --- |
| 0 | `gti` | Homologar o ambiente: Entra ID, recurso Azure e canal no Teams. Apresentar à GTI e ao compliance a fronteira de confidencialidade e a trilha de auditoria do RNF03 | Ambiente homologado e perfis carregados a partir do Entra ID |
| 1 | `pmo` e um subportfólio piloto | Sessão de apresentação de 30 minutos centrada em três demonstrações: a fonte citada, a declaração de limite e a prévia antes da escrita. Distribuir um cartão de perguntas de exemplo por perfil | Uso recorrente pelo PMO e indicadores de qualidade da Seção 13.2.4 dentro da meta por quatro semanas |
| 2 | `lider_subportfolio` e `equipe_projeto` | Expandir por subportfólio, um de cada vez, com o multiplicador do subportfólio conduzindo a primeira sessão da própria equipe | Subportfólio com multiplicador ativo e pendências de atualização respondidas pelo agente |
| 3 | `diretoria` | Entregar o resumo executivo mensal gerado pelo agente junto do material habitual, sem pedir que a diretoria opere o chat | Diretoria consultando o agente diretamente, sem intermediação do PMO |

O piloto começa pelo **Mapa de Benefícios**, o mesmo documento escolhido como piloto das transações do agente na Seção 2.9: é o artefato de entrada do ciclo de vida do projeto, o PMO já conhece o fluxo, e os fluxos AS-IS e TO-BE da Seção 2.6 mostram onde o trabalho muda. Começar por um documento conhecido reduz o que o usuário precisa aprender ao mesmo tempo.


## 13.2 Mecanismos de incentivo e engajamento

A adoção contínua depende do que cada pessoa ganha ao mudar sua forma de trabalhar. As três dimensões abaixo foram desenhadas para o modelo de trabalho do PMO do Metrô, e, sempre que possível, cada mecanismo aponta para um dado que a solução já registra, para que o engajamento possa ser acompanhado em vez de presumido. Os mecanismos que dependem de algo ainda não construído estão identificados como tal.

### 13.2.1 Utilidade e ganho de produtividade

O ganho é diferente para cada perfil, porque o trabalho que o agente substitui é diferente.

| Perfil | O que deixa de fazer | O que passa a ter |
| --- | --- | --- |
| `pmo` | Compilar o balanço mensal a partir de SharePoint, listas, Power BI e planilhas, e cobrar atualização pessoa por pessoa | Uma consulta única sobre projetos e subportfólios, o relatório executivo gerado a partir dos dados consolidados e o alerta de prazo cobrando no seu lugar |
| `lider_subportfolio` | Cruzar Power BI, documentos e relatos de líderes para investigar um desvio antes da reunião | Comparação entre projetos e alerta quando um marco atrasa além do limite que ele mesmo configurou |
| `equipe_projeto` | Responder a cobranças avulsas e preencher formulários estáticos | Pendências que chegam pelo alerta, com o item exato a atualizar, e configuração por fluxo guiado no chat |
| `diretoria` | Ler documentos extensos ou esperar a consolidação manual do PMO | Resumo executivo que indica a origem de cada número |

Dois resultados medidos sustentam esse ganho desde já: a resposta chega em tempo de conversa, com P95 de consulta simples entre 7,0 e 7,6 s, e 91,67% das respostas são fundamentadas nas fontes (Seção 9.2). A redução do tempo para encontrar uma informação, prevista na matriz de objetivos da Seção 2.4 com meta de 50%, depende da comparação entre a busca manual e a consulta ao agente sobre os mesmos casos; essa comparação é feita no piloto e entra como indicador na Seção 13.2.4.

### 13.2.2 Governança e voz ativa

O usuário precisa ver que o que ele reporta muda o agente. Os mecanismos abaixo transformam uso em melhoria.

| Mecanismo | Como funciona | Dado que o alimenta |
| --- | --- | --- |
| Perguntas não atendidas viram backlog | Toda solicitação classificada como fora de escopo já é gravada pelo backend. Uma vez por mês, o PMO revisa essas perguntas e decide quais são lacunas do agente e quais estão de fato fora do escopo | `out_of_scope_requests` |
| Avaliação de cada resposta no próprio chat | A construir. O usuário marca a resposta como útil ou não útil e, no segundo caso, escolhe o motivo: fonte errada, informação incompleta ou pergunta mal entendida | Campo de avaliação a acrescentar à interação em `ai_interactions` |
| Curadoria da base de conhecimento com o PMO | O léxico do domínio e o catálogo de intenções foram construídos para serem substituídos pela base real sem alterar código. A curadoria decide o que entra; uma intenção nova exige retreino e reavaliação pelo protocolo da Seção 8.10, e por isso é decisão de governança, e não ajuste de configuração | `lexico_dominio.json`, `intent_catalog` |
| Grupo de usuários-chave | Um multiplicador por subportfólio, mais o PMO, prioriza a cada trimestre as melhorias seguintes, partindo da lista priorizada da Seção 12.2 | Ata da priorização |
| Indicadores publicados | Os indicadores da Seção 13.2.4 são divulgados mensalmente ao grupo de usuários-chave, inclusive os que pioraram | Painel mensal |

A combinação dos dois primeiros mecanismos responde à barreira mais grave da Seção 13.1.2: a desconfiança nasce de respostas sem lastro, e o PMO passa a ver, com dados, onde o agente erra e o que foi feito a respeito.

### 13.2.3 Comunidade e reconhecimento

| Mecanismo | Como funciona |
| --- | --- |
| Rede de multiplicadores | Um usuário de referência por subportfólio, escolhido entre os primeiros a adotar, conduz a primeira sessão da própria equipe na fase 2 do onboarding e é o primeiro contato para dúvidas |
| Reconhecimento dos primeiros adotantes | Os participantes do piloto têm o nome registrado na comunicação do PMO e voto na primeira priorização trimestral |
| Destaque à qualidade dos dados | O agente já sabe quando um dado está velho: um item de cronograma sem atualização há mais de 45 dias é marcado como desatualizado, e o alerta de prazo deixa de concluir sobre ele. O percentual de projetos atualizados por subportfólio é publicado no painel mensal, e o subportfólio com maior completude é destacado na reunião do PMO |
| Biblioteca de perguntas por perfil | Um canal no Teams reúne as perguntas que funcionaram, organizadas por perfil, e alimenta o cartão de exemplos entregue no onboarding |

O destaque à qualidade dos dados tem um efeito que vai além da adoção: o agente responde melhor quanto mais atualizada estiver a base, e o reconhecimento dá ao líder de projeto um motivo próprio para manter o dado em dia, e não apenas a cobrança do PMO.

### 13.2.4 Indicadores de uso e qualidade

Os indicadores de uso e de qualidade dos dados vêm de tabelas que o backend já preenche, sem coleta manual. Os de qualidade das respostas exigem avaliação amostral, como a feita no RNF04; a avaliação no chat ainda precisa ser construída; e a comparação com a busca manual é feita sobre os mesmos casos no piloto. As metas de qualidade repetem as dos requisitos não funcionais, e os indicadores de uso partem de uma linha de base medida nas quatro primeiras semanas do piloto.

| Indicador | Dimensão | Meta | Fonte |
| --- | --- | --- | --- |
| Usuários ativos por perfil, por semana | Uso | Crescimento a cada fase do onboarding | `ai_interactions` cruzada com `users` |
| Usuários que voltam a usar em quatro semanas | Uso | Linha de base no piloto | `ai_interactions` |
| Subportfólios com multiplicador ativo | Comunidade | Todos os subportfólios da fase 2 | Registro do grupo de usuários-chave |
| Respostas fundamentadas nas fontes | Qualidade | ≥ 90% (RNF04) | `consulted_sources` e avaliação amostral |
| Taxa de alucinação | Qualidade | ≤ 5% (RNF04) | Avaliação amostral |
| Solicitações compreendidas ou orientadas para reformulação | Qualidade | ≥ 80% (Seção 2.4) | `ai_interactions` e `out_of_scope_requests` |
| P95 de consulta simples | Qualidade | ≤ 10 s (RNF05) | Métricas de etapa devolvidas pela API |
| Respostas avaliadas como não úteis | Qualidade | Tendência de queda | Avaliação no chat, a construir |
| Sugestões proativas aceitas sobre oferecidas | Utilidade | Linha de base no piloto | `pending_proactive_suggestions` |
| Tempo para encontrar uma informação, comparado à busca manual | Produtividade | Redução de 50% (Seção 2.4) | Comparação sobre os mesmos casos no piloto |
| Projetos com dados atualizados nos últimos 45 dias | Qualidade dos dados | Crescimento por subportfólio | Regra de frescor do alerta |

Os quatro indicadores de qualidade com meta definida já têm linha de base medida na Seção 9.2. Quando um deles cair abaixo da meta por duas medições seguidas, a expansão para a fase seguinte do onboarding é suspensa até a causa ser tratada — regra que impede que a adoção avance sobre uma confiança que o próprio agente esteja corroendo.


# Referências

- Microsoft. [Preços do Azure AI Speech](https://azure.microsoft.com/en-us/pricing/details/speech/). Acesso em: 19 ago. 2026.
- Microsoft. [Quotas e limites do Azure AI Speech](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-quotas-and-limits). Acesso em: 19 ago. 2026.
- Microsoft. [API REST de conversão de fala em texto para áudio curto](https://learn.microsoft.com/pt-br/azure/ai-services/speech-service/rest-speech-to-text-short). Acesso em: 19 ago. 2026.
- Microsoft. [Transcriptions — Transcribe, API 2025-10-15](https://learn.microsoft.com/en-us/rest/api/speechtotext/transcriptions/transcribe?view=rest-speechtotext-2025-10-15). Acesso em: 19 ago. 2026.
- Microsoft. [Suporte a idiomas do Azure AI Speech](https://learn.microsoft.com/pt-br/azure/ai-services/speech-service/language-support). Acesso em: 19 ago. 2026.
- Microsoft. [Regiões do Azure AI Speech](https://learn.microsoft.com/pt-br/azure/ai-services/speech-service/regions). Acesso em: 19 ago. 2026.
- Google. [Preços do Speech-to-Text](https://cloud.google.com/speech-to-text/pricing). Acesso em: 19 ago. 2026.
- Google. [Idiomas do Cloud Speech-to-Text V2](https://docs.cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages). Acesso em: 19 ago. 2026.
- Amazon Web Services. [Preços do Amazon Transcribe](https://aws.amazon.com/transcribe/pricing/). Acesso em: 19 ago. 2026.
- Amazon Web Services. [Idiomas do Amazon Transcribe](https://docs.aws.amazon.com/pt_br/transcribe/latest/dg/supported-languages.html). Acesso em: 19 ago. 2026.
- OpenAI. [Preços da API](https://platform.openai.com/pricing). Acesso em: 19 ago. 2026.
- OpenAI. [Audio API — Create transcription](https://platform.openai.com/docs/api-reference/audio/createTranscription). Acesso em: 19 ago. 2026.
- Amazon Web Services. [Instâncias Amazon EC2 T3](https://aws.amazon.com/ec2/instance-types/t3/). Acesso em: 25 set. 2026.
- Amazon Web Services. [Tipos de volume do Amazon EBS](https://aws.amazon.com/ebs/volume-types/). Acesso em: 25 set. 2026.
- Amazon Web Services. [Preços do Amazon ECR](https://aws.amazon.com/ecr/pricing/). Acesso em: 25 set. 2026.
- Amazon Web Services. [Preços do Amazon CloudWatch](https://aws.amazon.com/cloudwatch/pricing/). Acesso em: 25 set. 2026.
- Amazon Web Services. [Preços da Amazon VPC](https://aws.amazon.com/vpc/pricing/). Acesso em: 25 set. 2026.
- Banco Central do Brasil. [Cotações e boletins PTAX](https://ptax.bcb.gov.br/ptax_internet/consultarTodasAsMoedas.do?method=consultaTodasMoedas). Acesso em: 25 set. 2026.
- Brasil. [Lei Complementar nº 123, de 14 de dezembro de 2006](https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp123.htm). Acesso em: 25 set. 2026.
- OpenAI. [Codex pricing](https://learn.chatgpt.com/docs/pricing). Acesso em: 25 set. 2026.
- Robert Half. [Guia Salarial 2026](https://www.roberthalf.com/br/pt/insights/salary-guide). Acesso em: 25 set. 2026.
- Robert Half. [Desenvolvedor(a) full-stack júnior](https://www.roberthalf.com/br/pt/vagas-detalhes/desenvolvedora-full-stack-junior). Acesso em: 25 set. 2026.
- Supabase. [Preços](https://supabase.com/pricing). Acesso em: 25 set. 2026.

<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://git.inteli.edu.br/graduacao/2026-2a/t17/g05">Agente de IA para o Portfólio de Projetos do Metrô</a> by <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://git.inteli.edu.br/graduacao/2026-2a/t17/g05">Oneshot</a>, <a href="https://www.inteli.edu.br/">Inteli</a>, <a href="https://www.linkedin.com/in/ntsfelipe/">Felipe Neves</a>, <a href="https://www.linkedin.com/in/henrique-rodrigues-diniz-b7b011319/">Henrique Diniz</a>, <a href="https://www.linkedin.com/in/jaimeandradedealmeida/">Jaime Almeida</a>, <a href="https://www.linkedin.com/in/leonardoramosvieira">Leonardo Ramos</a>, <a href="https://www.linkedin.com/in/pedro-uchoaa/">Pedro Uchoa</a> e <a href="https://www.linkedin.com/in/wendel-feitosa-975bb1346/">Wendel Feitosa</a> is licensed under <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="license noopener noreferrer">Attribution 4.0 International</a>.</p>
