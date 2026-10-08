# Revisão dos Feedbacks Recebidos

Este documento registra cada feedback recebido pelo grupo ao longo do módulo, a sprint em que foi apontado e o que foi feito a respeito. Ele cumpre duas funções: dá rastreabilidade às correções, para que cada uma possa ser conferida no repositório, e deixa explícito o que ainda não foi corrigido e por quê.

## Método

Cada item foi conferido contra o estado atual do repositório em 3 de outubro de 2026, e não contra a memória da equipe. A coluna "Onde conferir" aponta a seção ou o arquivo em que a correção pode ser verificada. Quando um feedback posterior confirmou a correção de um item anterior, essa confirmação é citada.

O documento cobre os feedbacks de grupo recebidos nas Sprints 1, 2 e 3. As avaliações individuais de aprendizagem não foram incluídas, porque avaliam respostas de cada integrante e não apontam correções na documentação do grupo. A única exceção é a nota coletiva incluída no feedback individual de planejamento e execução da Sprint 2, que trata de uma prática do time e aparece como item próprio.

| Status | Significado |
| --- | --- |
| ✅ Corrigido | A correção existe e foi conferida no repositório |
| 🔄 Em andamento | A correção está em execução na Sprint 5 e ainda não chegou à `develop` |
| ⚖️ Mantido com justificativa | O item não foi alterado, por decisão registrada |
| ⏳ Pendente | O item não foi corrigido; o destino da correção está indicado |

## Resumo

| Sprint | Artefato avaliado | Itens | ✅ | 🔄 | ⚖️ | ⏳ |
| :---: | --- | :---: | :---: | :---: | :---: | :---: |
| 1 | Entendimento do Projeto e do Negócio | 14 | 14 | — | — | — |
| 1 | Especificação de Requisitos | — | — | — | — | — |
| 1 | Gestão de Projeto e Configuração | 5 | 4 | 1 | — | — |
| 2 | Gestão de Projetos Evolutiva | 10 | 9 | 1 | — | — |
| 2 | Estratégia Técnica da Solução | 6 | 6 | — | — | — |
| 2 | Prototipação Exploratória | 6 | 3 | — | 3 | — |
| 3 | Planejamento de Testes Sistêmicos | 7 | 7 | — | — | — |
| 3 | Desenvolvimento e Documentação Técnica | 5 | 3 | 1 | — | 1 |
| 3 | Gestão de Projetos Evolutiva | 7 | 2 | — | — | 5 |
| | **Total** | **60** | **48** | **3** | **3** | **6** |

A Especificação de Requisitos da Sprint 1 recebeu apenas pontos positivos e não gerou item de correção.

Dos seis itens pendentes, quatro são de gestão de configuração do repositório — tags, nomes de branch e o registro de uma operação sobre o histórico —, um é uma afirmação que ficou desatualizada no `GestaoProjeto.md`, e um depende de solicitações reais do PMO. Nenhum deles altera o funcionamento da solução.

## Sprint 1

### Entendimento do Projeto e do Negócio

| # | Item apontado | Correção realizada ou justificativa | Onde conferir | Status |
| :---: | --- | --- | --- | :---: |
| 1.01 | A seção que define o que o produto faz não tinha lista; o conteúdo concreto estava no canvas | A seção passou a trazer uma tabela de capacidades, com o que o agente faz em cada uma | `Projeto.md`, 2.4.3 | ✅ |
| 1.02 | 22 objetivos com verbos não mensuráveis, enquanto a matriz por métrica ficava como apêndice | A lista foi removida, e os objetivos passaram a ser a matriz de consolidação por métrica | `Projeto.md`, 2.4.4 | ✅ |
| 1.03 | A priorização não seguia a fórmula declarada, e faltava a linha de corte do MVP | Regra de priorização explícita, com faixas definidas pelo produto entre importância e viabilidade, e linha de corte do MVP declarada | `Projeto.md`, 2.8 | ✅ |
| 1.04 | As tabelas das Seções 2.8 e 2.8.1 repetiam as mesmas features e se contradiziam | A Seção 2.8 concentra a matriz; a 2.8.1 passou a descrever as features por faixa, sem repetir a tabela | `Projeto.md`, 2.8 e 2.8.1 | ✅ |
| 1.05 | A persona Mariana, que encarna a dor central, não tinha jornada | Jornada de Mariana incluída, com as etapas do balanço mensal | `Projeto.md`, 2.5.2.2 | ✅ |
| 1.06 | Gateway sem função no fluxo de negócio | Fluxo revisado; o gateway restante decide entre duas saídas | `Projeto.md`, 2.6 | ✅ |
| 1.07 | A raia "Repositório corporativo" executava tarefas | Convenção declarada: só aparecem como raia participantes que executam e decidem | `Projeto.md`, 2.6 | ✅ |
| 1.08 | Faltava justificar por que modelar o processo do Mapa de Benefícios | O processo foi situado entre os do portfólio, com a justificativa do recorte | `Projeto.md`, 2.6 e 2.9 | ✅ |
| 1.09 | A matriz de responsabilidades tinha só dois itens do lado do Metrô | Responsabilidades do Metrô incluídas: acesso ao ambiente, homologação junto à GTI, validação e participação nos rituais | `Projeto.md`, 2.4.5 | ✅ |
| 1.10 | Seções 2.6.6 e 2.6.7 dentro da Seção 2.7 | Numeração corrigida | `Projeto.md`, 2.6 e 2.7 | ✅ |
| 1.11 | Legendas com o marcador "Figura X" | Nenhuma ocorrência; as figuras estão numeradas em sequência | `Projeto.md` | ✅ |
| 1.12 | As imagens das personas Mariana e Carlos tinham texto alternativo "Persona Roberto" | Cada imagem traz o nome da própria persona | `Projeto.md`, 2.5.1 | ✅ |
| 1.13 | O arquivo `logo-btg.png` era o logo do Inteli, com nome herdado de outro projeto | O logo correto está em `logo-Inteli.png`. O arquivo antigo, que não era mais referenciado em nenhum documento, foi removido nesta revisão | `docs/img/` | ✅ |
| 1.14 | Cabeçalho, sumário e identificação do grupo seriam cobrados a partir da Sprint 3 | Nome do projeto, nome do grupo, integrantes e sumário preenchidos | `Projeto.md`, início do documento | ✅ |

### Gestão de Projeto e Configuração

| # | Item apontado | Correção realizada ou justificativa | Onde conferir | Status |
| :---: | --- | --- | --- | :---: |
| 1.15 | A retrospectiva não trazia nenhuma medida, e sem linha de base não haveria como comparar | Retrospectivas passaram a trazer indicadores com meta; o feedback da Sprint 2 apontou a retrospectiva como o instrumento mais rigoroso do documento | `GestaoProjeto.md`, Seção 2 | ✅ |
| 1.16 | A matriz de papéis identificava cada pessoa só pelo primeiro nome, sem ligação com as issues | As matrizes passaram a apontar as issues sob responsabilidade de cada integrante, o que o feedback da Sprint 3 confirmou | `GestaoProjeto.md`, Seção 4 | ✅ |
| 1.17 | Squash com exclusão de branch fazia o commit herdar o título do MR, e 15 de 21 commits saíam fora da convenção | O mecanismo está documentado; a validação automática do título do merge request está em revisão na Sprint 5 | `GestaoConfiguracao.md`, 5.3.1 | 🔄 |
| 1.18 | O cabeçalho do `GestaoProjeto.md` estava com o texto do modelo | Preenchido, o que o feedback da Sprint 2 confirmou | `GestaoProjeto.md`, início do documento | ✅ |
| 1.19 | O modelo de registro da daily perdeu a formatação de bloco de código | Os campos da daily estão listados sem formatação quebrada | `GestaoProjeto.md`, política de dailies | ✅ |

## Sprint 2

### Gestão de Projetos Evolutiva

| # | Item apontado | Correção realizada ou justificativa | Onde conferir | Status |
| :---: | --- | --- | --- | :---: |
| 2.01 | A matriz de risco não trazia a data da última revisão de cada item | Coluna incluída, o que o feedback da Sprint 3 confirmou | `GestaoProjeto.md`, matriz de riscos | ✅ |
| 2.02 | A matriz de papéis da Sprint 2 descrevia as entregas em texto, sem link para a issue | As matrizes passaram a listar as issues de cada integrante, o que o feedback da Sprint 3 confirmou | `GestaoProjeto.md`, Seção 4 | ✅ |
| 2.03 | 62% das tasks em tamanho G e 23 de 26 em prioridade Alta, o que não ordena o trabalho | O planejamento da Sprint 4 fixou premissas, capacidade e limites antes do backlog, o que o feedback da Sprint 3 confirmou | `GestaoProjeto.md`, 6.4.1 | ✅ |
| 2.04 | As 26 tasks ocupavam cerca de metade da capacidade declarada | Capacidade e backlog passaram a ser dimensionados em horas, com reserva e linha de corte explícitas | `GestaoProjeto.md`, 6.5.1 | ✅ |
| 2.05 | O número de commits de squash dentro da convenção divergia entre os dois documentos de gestão | A recontagem virou linha de base única dos dois documentos, o que o feedback da Sprint 3 confirmou | `GestaoProjeto.md` e `GestaoConfiguracao.md` | ✅ |
| 2.06 | A tabela de hooks estava quebrada por um parágrafo inserido no meio dela | Tabela íntegra, com o parágrafo fora dela | `GestaoConfiguracao.md`, 7.2 | ✅ |
| 2.07 | As fontes `.puml` dos diagramas não estavam registradas como política | A Seção 8 documenta as fontes editáveis e a regra de versionar fonte e imagem no mesmo MR, o que o feedback da Sprint 3 confirmou | `GestaoConfiguracao.md`, 8.3 | ✅ |
| 2.08 | A padronização do título do merge request, definida na Sprint 1, não foi cumprida | Mesma correção do item 1.17, em revisão na Sprint 5 | `GestaoConfiguracao.md`, 5.3.1 | 🔄 |
| 2.09 | A Seção 1.2 descrevia o escopo do documento como planejamento da Sprint 2 | Escopo atualizado para o conjunto das sprints | `GestaoProjeto.md`, 1.2 | ✅ |
| 2.10 | Cartões que ficam no backlog do começo ao fim tornam impossível distinguir corte de esquecimento | Política do planejamento da Sprint 5: task cortada ou fundida é fechada com o motivo e o destino, e nunca excluída | `GestaoProjeto.md`, 6.5.1 | ✅ |

### Estratégia Técnica da Solução

| # | Item apontado | Correção realizada ou justificativa | Onde conferir | Status |
| :---: | --- | --- | --- | :---: |
| 2.11 | F1-macro de 0,74 na intenção específica, abaixo do mínimo de 0,80; o limiar não substitui a evolução do classificador | A versão 2 do classificador atingiu F1-macro de 0,8327 no conjunto de teste, mantido fechado durante a seleção | `Projeto.md`, 8.10.7 e 9.2 | ✅ |
| 2.12 | Teams e a interface React apareciam ambos como canal principal, sem separar PoC de arquitetura-alvo | A interface React foi declarada como bancada de teste, fora do produto; o canal da arquitetura-alvo é o Teams | `Projeto.md`, 3.4.2.1 | ✅ |
| 2.13 | Não estava claro se o Gemini era decisão arquitetural ou implementação de referência | O provedor da bancada foi separado do de produção, e a integração com o modelo generativo é feita por interface HTTP substituível | `Projeto.md`, 3.2.2 e 5.2 | ✅ |
| 2.14 | O RAG mantinha FAISS e ChromaDB como alternativas, sem escolha consolidada | As alternativas saíram da arquitetura, e a estratégia de indexação foi definida com critério: arquivo controlado, com migração condicionada ao volume | `Projeto.md`, 6.2.3 | ✅ |
| 2.15 | A plataforma de nuvem para executar o algoritmo não estava definida | Implantação em AWS EC2, com contêineres publicados no ECR | `Projeto.md`, 10.2 | ✅ |
| 2.16 | Os diagramas misturavam alternativas, componentes de PoC e arquitetura-alvo | Diagramas separados: um para a bancada e outro para a arquitetura-alvo | `Projeto.md`, 3.3 e 5.2 | ✅ |

### Prototipação Exploratória

| # | Item apontado | Correção realizada ou justificativa | Onde conferir | Status |
| :---: | --- | --- | --- | :---: |
| 2.17 | Os diários de construção não traziam datas nem sessões | Os diários registram sessões realizadas na Sprint 2, que não foram datadas na ocasião. Acrescentar datas agora seria reconstruir o registro, e não corrigi-lo | `Projeto.md`, 3.8.3 | ⚖️ |
| 2.18 | As tirinhas foram lidas apenas pelo próprio grupo, e a falha foi desenhada, não encontrada | Atendido pela implementação, e não por nova rodada de prototipação: a questão do regime de iniciativa foi testada com seis usuários externos no cenário 6 do teste de usabilidade | `Projeto.md`, 9.3.2 | ✅ |
| 2.19 | Os dois protótipos usaram tirinha, e faltou o contraste entre formatos | Limitação declarada na própria seção: o formato único foi escolhido para isolar o regime de iniciativa como única variável entre as alternativas | `Projeto.md`, 3.8.5 | ⚖️ |
| 2.20 | Definir a evidência que encerraria a questão de projeto junto ao parceiro | Atendido pela implementação: o regime foi decidido — sugestão opcional, com confirmação e controle de ativação — e avaliado no cenário 6, que revelou a dificuldade de perceber o controle | `Projeto.md`, 3.1 e 9.3.2 | ✅ |
| 2.21 | Prototipar o regime intermediário apontado na comparação | Atendido pela implementação: o regime construído é o intermediário, em que a sugestão nasce da consulta do próprio usuário e depende de confirmação, sem observação contínua | `Projeto.md`, 3.1 | ✅ |
| 2.22 | Indicar qual decisão do inventário bloqueava a sprint seguinte | A decisão de maior peso, o regime de iniciativa, foi resolvida com a implementação da sugestão proativa e do seu controle na Sprint 4; a prototipação não teve nova iteração em que o inventário fosse reeditado | `Projeto.md`, 3.1 e 3.8.6 | ⚖️ |

## Sprint 3

### Planejamento de Testes Sistêmicos

| # | Item apontado | Correção realizada ou justificativa | Onde conferir | Status |
| :---: | --- | --- | --- | :---: |
| 3.01 | As linhas do CT-RNF04 reuniam o caso positivo e o negativo numa mesma célula, e o procedimento perdia passos | Casos positivo e negativo separados em linhas próprias, com passos numerados | `Projeto.md`, 9.2.3 | ✅ |
| 3.02 | Faltava dizer se as metas de 10 e 20 segundos do RNF05 eram hipótese da equipe ou acordo com o parceiro | O registro de revisão declara as metas como hipótese inicial da equipe, mantida com base na medição | `Projeto.md`, 3.2.2 | ✅ |
| 3.03 | A Seção 9.4.1 dizia que o plano "será desenvolvido na Sprint 3", na própria Sprint 3 | Frase removida | `Projeto.md`, 9.4.1 | ✅ |
| 3.04 | As fronteiras entre API e PLN, PLN e recuperação, backend e frontend e API e banco não tinham cenário | Testes de integração executados na Sprint 4 sobre a comunicação interna entre componentes, os serviços externos, o VHS e o tratamento de erro | `docs/testes/sprint4/relatorio-s4-32b.md` | ✅ |
| 3.05 | Registrar na planilha o perfil de cada usuário recrutado | Tabela de participantes com familiaridade com tecnologia e com agentes conversacionais | `Projeto.md`, 9.3.2 | ✅ |
| 3.06 | A instrução do cenário 6 antecipava ao participante o que o teste queria observar | Instrução reescrita antes das sessões | `Projeto.md`, 9.3, revisão dos instrumentos | ✅ |
| 3.07 | Tratar o SUS como dado descritivo, e não como meta de aprovação | O SUS é declarado como dado descritivo e lido junto da observação das tarefas | `Projeto.md`, 9.3.2 | ✅ |

### Desenvolvimento e Documentação Técnica

| # | Item apontado | Correção realizada ou justificativa | Onde conferir | Status |
| :---: | --- | --- | --- | :---: |
| 3.08 | A rota de áudio exigia token, mas a de texto não, e as duas levam ao mesmo pipeline | A rota de texto já valida o token quando ele é enviado, mas ainda aceita chamada sem token. A autenticação obrigatória, com controle de acesso por perfil, está em revisão na Sprint 5 | `src/backend/app/main.py` | 🔄 |
| 3.09 | A intenção específica ficava abaixo do mínimo do RNF06 | Classificador versão 2, com F1-macro de 0,8327 | `Projeto.md`, 8.10.7 | ✅ |
| 3.10 | Como os dados são sintéticos, o desempenho com perguntas reais ainda precisa ser medido | Não corrigido: depende de solicitações reais do PMO, que não estiveram disponíveis no módulo. Registrado como aperfeiçoamento de prioridade 1 | `Projeto.md`, 12.2 | ⏳ |
| 3.11 | A Seção 8.11.9 dizia que a persistência não estava implementada, embora o registro das interações já existisse | A seção registra a persistência implementada e testada em `app/database/tracing.py` | `Projeto.md`, 8.11.9 | ✅ |
| 3.12 | A Seção 8.10.3 ainda atribuía à Sprint 3 o fechamento da lacuna do RNF06 | Corrigido nesta revisão: a frase passa a remeter à versão 2 do classificador, que fechou a lacuna | `Projeto.md`, 8.10.3 | ✅ |

### Gestão de Projetos Evolutiva

| # | Item apontado | Correção realizada ou justificativa | Onde conferir | Status |
| :---: | --- | --- | --- | :---: |
| 3.13 | O documento afirmava que os marcadores de conflito permaneciam em cinco arquivos, quando já tinham sido removidos | A afirmação continua no texto. Destino: fechamento da gestão do projeto, junto da análise da Sprint 5 | `GestaoProjeto.md`, 2.3.5 e 3.9 | ⏳ |
| 3.14 | A regra da daily exigia quatro campos, mas não dizia onde fica o template | A ação de melhoria define o template completo no Slack, inclusive para quem estiver ausente | `GestaoProjeto.md`, ações de melhoria da Sprint 3 | ✅ |
| 3.15 | O planejamento da Sprint 4 abria tarefas para corrigir marcadores de conflito que já tinham sido removidos | As tarefas foram encerradas sem execução, porque o conserto já existia | Board da Sprint 4 | ✅ |
| 3.16 | A sincronização do histórico da `main` com o da `hmg` apagou a autoria dos commits na `main`, e a operação não foi registrada | Sem registro como procedimento ou incidente. Destino: revisão final da gestão de configuração | `GestaoConfiguracao.md` | ⏳ |
| 3.17 | A mensagem do commit dessa operação terminava com o marcador de exemplo `(#NNN)` | Mesmo registro de incidente do item anterior | `GestaoConfiguracao.md` | ⏳ |
| 3.18 | Não havia nenhuma tag no repositório, embora existisse um commit "release 0.3.0" | O repositório continua sem tags. Destino: publicação da versão final | `git tag` | ⏳ |
| 3.19 | Duas branches remotas violavam a convenção por acento | `docs/documentação-stt` e `feat/Implementar-validação-de-formatos-e-tratamento` continuam no remoto. Destino: revisão final da gestão de configuração | `git branch -r` | ⏳ |
