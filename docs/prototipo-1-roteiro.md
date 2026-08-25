# Protótipo 1 — Agente Reativo sob Demanda

Roteiro de produção das tirinhas e protocolo de execução.

Documento de apoio à Seção 3.8 do [`Projeto.md`](Projeto.md). A alternativa investigada, os quatro cenários e o diário de construção estão no documento principal; aqui fica o roteiro painel a painel das quatro tirinhas, com os diálogos e as regras de representação que definem o comportamento do agente em cada painel.

**Questão investigada:** de quem parte a iniciativa da interação — o agente age somente quando é explicitamente solicitado, ou age a partir do que observa da atividade que a pessoa está realizando?

**Regime representado neste protótipo:** o agente permanece silencioso até ser acionado. Não observa a tela, não avalia oportunidades de assistência e não se manifesta entre uma solicitação e outra.

---

## 1. Regras de representação

Regras que valem para as quatro tirinhas e que existem para impedir que o Protótipo 1 seja desenhado com comportamentos do Protótipo 2:

1. O agente nunca ocupa um painel antes de ser acionado pela pessoa.
2. Não existem elementos sobrepostos à tela de trabalho. O agente aparece apenas dentro do canal em que foi aberto.
3. Toda resposta do agente referencia a fonte consultada.
4. O agente não amplia o escopo da resposta além do que foi perguntado.
5. Quando não há informação suficiente, o agente declara a limitação. O que ele pode ou não acrescentar depois disso é objeto do Cenário 2B e deve permanecer indefinido até a execução.
6. O acabamento não é avaliado. Traço torto, balão refeito e rascunho fotografado servem melhor ao artefato do que arte finalizada.

---

## 2. Roteiro das tirinhas

### 2.1 Tirinha 1A — Carlos, preparação de reunião (execução de sucesso)

**Arquivo:** `img/tirinha-1A-1.png`

| Painel | Conteúdo |
| :---: | --- |
| 1 | Carlos na sua mesa, com uma pauta de reunião pela metade em uma folha. Nenhum agente em cena. Pensamento: *"Preciso do marco vigente do projeto de modernização antes das 14h."* |
| 2 | Carlos abre o canal do agente e digita: *"Qual é o marco vigente do projeto de Modernização de Sinalização?"* |
| 3 | Resposta do agente: marco, data e a fonte citada — *"conforme cronograma revisado em 12/08, versão vigente no SharePoint"*. |
| 4 | Carlos digita: *"E os riscos em aberto desse projeto?"* Resposta com três riscos e a fonte. |
| 5 | Carlos fecha o canal. A pauta está completa. O agente não aparece neste painel. |

**O que este cenário deve tornar visível:** quando a pessoa sabe o que precisa perguntar, o regime reativo entrega a informação com fonte, sem interromper e sem exigir que ela navegue entre plataformas. É o caso em que a alternativa é forte, e ele precisa ser desenhado com convicção.

---

### 2.2 Tirinha 1B — Carlos, a pergunta que não foi feita (execução de falha)

**Arquivo:** `img/tirinha-1B-1.png`

| Painel | Conteúdo |
| :---: | --- |
| 1 | Repete a situação de 1A: Carlos consulta o agente, recebe a resposta correta com fonte, fecha o canal. Nada de errado acontece. |
| 2 | Enquadramento mostrando o que o agente tinha na base e não apresentou: um documento indicando que a entrega depende de um contrato de outro projeto do subportfólio, atrasado. Carlos não perguntou. |
| 3 | Reunião. O líder do outro projeto informa a dependência. Carlos é pego sem contexto. |
| 4 | Carlos, depois da reunião: *"A informação estava lá o tempo todo."* |

**O que este cenário deve tornar visível:** a falha do regime reativo não é de recuperação nem de fundamentação — o agente não errou. É uma falha de cobertura, e ela é invisível no momento em que ocorre. Nenhuma métrica do próprio agente a detecta.

**Ponto de atenção na produção:** a tentação é desenhar o agente avisando no painel 2. Se isso acontecer, o protótipo virou o Protótipo 2. O painel 2 mostra a informação retida, não o agente falando.

---

### 2.3 Tirinha 2A — Mariana, consolidação do balanço (execução de sucesso)

**Arquivo:** `img/tirinha-2A-1.png`

| Painel | Conteúdo |
| :---: | --- |
| 1 | Mariana com o balanço mensal aberto. Pensamento: *"Preciso comparar o avanço físico dos projetos de modernização entre julho e agosto."* |
| 2 | Ela digita a solicitação usando o vocabulário dos documentos: *"Compare o avanço físico dos projetos do subportfólio de Modernização entre julho e agosto."* |
| 3 | Resposta estruturada em tabela, com as fontes de cada linha. |
| 4 | Mariana utiliza o resultado diretamente no relatório. Legenda: o que levava uma manhã de navegação entre Power BI, SharePoint e planilhas foi resolvido em uma solicitação. |

**O que este cenário deve tornar visível:** o ganho do regime reativo é maior justamente para o perfil que domina o domínio e sabe formular. Para Mariana, a proatividade seria em boa medida desnecessária.

---

### 2.4 Tirinha 2B — Mariana, o vocabulário que não bate (execução de falha)

**Arquivo:** `img/tirinha-2B-1.png`

| Painel | Conteúdo |
| :---: | --- |
| 1 | Mariana digita: *"Quais projetos estão atrasados?"* |
| 2 | Agente: *"Não encontrei informações sobre 'atrasado' nos documentos disponíveis."* Resposta correta — o agente não inventou. |
| 3 | Mariana reformula: *"Projetos fora do prazo."* Mesma resposta. |
| 4 | Terceira reformulação: *"Projetos com desvio de marco."* O agente responde, com fonte. |
| 5 | Mariana: *"Ele sabia desde a primeira pergunta. Só não sabia que eu estava perguntando isso."* |

**O que este cenário deve tornar visível:** o custo de acesso não desapareceu, foi transferido para a pessoa, que precisa adivinhar o vocabulário da base. E abre a decisão central do inventário: se o agente pudesse ter respondido *"não encontrei 'atrasado'; a base registra 'desvio de marco'"*, ele teria oferecido algo que não foi pedido. O regime reativo puro não se sustenta como categoria; existe um grau de iniciativa indispensável para que ele funcione.

**Ponto de atenção na produção:** a sugestão aparece no painel 6 hachurada e rotulada como comportamento não definido. Ela é a lacuna que a exploração expõe, e não um comportamento que o protótipo estabelece.

---

---

## 3. Produção e rodagem

A produção das imagens e a rodagem dos protótipos até falhar são tratadas em tasks próprias e não fazem parte deste documento. Este roteiro é o insumo para ambas: define o que cada painel precisa mostrar e, principalmente, o que ele não pode mostrar sem descaracterizar a alternativa reativa.

Os arquivos referenciados pela Seção 3.8.3.1 do `Projeto.md` são `img/tirinha-1A-1.png`, `img/tirinha-1B-1.png`, `img/tirinha-2A-1.png` e `img/tirinha-2B-1.png`.
