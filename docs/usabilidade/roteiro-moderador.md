# Roteiro do moderador

Operacionaliza os sete cenários da Seção 9.3.1 do [`Projeto.md`](../Projeto.md).

**Duração:** 40 a 50 minutos. **Todas as sessões seguem este roteiro, na mesma
ordem e com as mesmas palavras**: é o que torna os participantes comparáveis.

A instrução de cada cenário é a mesma da planilha do grupo e é lida em voz alta,
sem acréscimos. Ela diz **o que** o participante precisa fazer, nunca **o que o
teste quer observar**: se a instrução antecipa o comportamento observado, o
participante procura por ele e a etapa deixa de medir se a interface o comunica
sozinha.

## Antes da sessão

Rodar o [checklist de ambiente](checklist-ambiente.md) inteiro. Se um item
obrigatório falhar, a sessão não começa.

## Abertura (5 min)

Ler em voz alta:

> Obrigado por participar. Vou te pedir para usar um protótipo de agente que
> responde perguntas sobre projetos, fazendo algumas tarefas que eu vou propor.
>
> Três coisas antes de começar. Primeira: **estamos avaliando o sistema, não
> você.** Se algo ficar confuso, isso é informação valiosa para a gente, e não
> existe resposta errada da sua parte. Segunda: **todos os dados são fictícios**,
> criados para a demonstração; nada disso é a operação real do Metrô. Terceira:
> **vá falando em voz alta** o que você está pensando, esperando ou estranhando.
> Eu não vou te ajudar de imediato, porque preciso ver onde o sistema não se
> explica sozinho, mas se você ficar preso eu intervenho.
>
> Para as tarefas, imagine que você trabalha no escritório de projetos e
> acompanha, entre outros, o projeto **PRJ-0442, Modernização do Sistema de
> Sinalização**. Podemos começar?

Recolher o consentimento. Iniciar a gravação somente se autorizada.

## Regras de intervenção

Existem para que "conseguiu com dificuldade" não vire "sucesso" por causa de uma
ajuda dada cedo demais. Valem para todos os cenários.

| Situação | O que o moderador faz |
| --- | --- |
| Silêncio por mais de 20 s | "O que você está pensando agora?" — pergunta neutra, nunca uma dica |
| "É aqui que eu clico?" | "O que você acha?", e observa a decisão |
| Travado há mais de 2 min | Registra `nao_conseguiu` na etapa e só então dá a dica mínima para seguir |
| Pede a resposta certa | "Te conto no fim da sessão" |
| Erro do sistema: tela branca, erro 5xx, demora acima de 60 s | Registra ocorrência `alta`, recarrega e retoma na mesma etapa |

Toda dica é anotada, com a etapa em que foi dada.

---

## Cenário 1 — Entrada em linguagem natural (5 min)

**Instrução:**
> Use o agente para fazer uma primeira pergunta sobre um projeto do portfólio.

**Etapas:** abrir a interface do agente · formular pergunta sem comando técnico ·
enviar a pergunta · ler a resposta · dizer se a resposta atende.

**Requisitos:** RF01, RF02, RF03, RNF07.

**Observar:** se a pessoa procura menu, comando ou sintaxe antes de simplesmente
escrever. Hesitação aqui indica que a interface não comunica que aceita
linguagem natural.

## Cenário 2 — Consulta de status e prazo (7 min)

**Instrução:**
> Consulte status, prazo ou marco de um projeto e avalie se a resposta foi clara.

**Etapas:** identificar o projeto · perguntar status ou prazo · localizar o dado
principal · verificar a fonte indicada · avaliar a suficiência da resposta.

**Requisitos:** RF04, RF05, RF08, RNF04.

**O que a base sustenta:** para o PRJ-0442, a base recuperável tem o comunicado da
operação assistida na Linha 1-Azul, de 24/08/2026 a 28/08/2026; status e datas do
projeto em si não estão entre os extratos. A resposta esperada informa o que a
fonte traz e declara o que falta.

**Observar:** se a pessoa percebe sozinha a fonte citada. Se ela não comentar a
fonte, ao final do cenário perguntar: "Se alguém da equipe perguntasse de onde veio
essa informação, o que você responderia?" — e registrar a etapa 4 como
`dificuldade` quando a fonte só for encontrada depois da pergunta.

## Cenário 3 — Consulta de riscos e informações do projeto (7 min)

**Instrução:**
> Peça ao agente informações de risco, avanço, marco ou indicador de um projeto.

**Etapas:** escolher o tema da consulta · enviar a pergunta ao agente · identificar
as informações · pedir detalhe se necessário · avaliar a clareza da resposta.

**Requisitos:** RF04, RF05, RF08, RNF04.

**O que a base sustenta:** riscos, avanço físico, marcos e indicadores do PRJ-0442
não estão entre os extratos recuperáveis. A resposta correta separa o que a fonte
traz do que não está disponível, sem inventar valores.

**Observar:** se o participante entende o que o agente tem e o que não tem. A falta
do dado é limitação da massa sintética, registrada como tal; um valor inventado é
alucinação e vira ocorrência `alta`.

## Cenário 4 — Análise e comparação entre projetos (7 min)

**Instrução:**
> Compare dois projetos por riscos, prazos, avanço ou marcos.

Se o participante perguntar quais projetos existem, responder: "Além do PRJ-0442,
você ouviu falar de um projeto PRJ-0518." Não acrescentar mais nada.

**Etapas:** escolher dois projetos · definir o critério de comparação · enviar o
pedido ao agente · interpretar a comparação · avaliar o apoio à decisão.

**Requisitos:** RF04, RF06, RF08.

> **Leitura obrigatória do moderador.** A massa sintética tem um único projeto, e a
> comparação entre projetos foi adiada para a Sprint 5 (Seção 6.4.1 do
> `GestaoProjeto.md`). Não há comparação a produzir. O comportamento correto do
> agente é declarar que não localizou o segundo projeto; se ele fizer isso, a
> etapa de interpretação mede se o participante **entende a recusa** e sabe o que
> fazer em seguida. A frustração, se aparecer, é registrada como limitação de
> escopo conhecida, e não como defeito do agente. Se o agente **produzir** uma
> comparação entre dois projetos, é alucinação: ocorrência `alta`, com
> `defeito_critico = sim`.

## Cenário 5 — Informação ausente ou fora de escopo (6 min)

**Instrução:**
> Faça uma pergunta que talvez não esteja na base ou esteja fora do escopo do MVP.

**Etapas:** formular a pergunta limite · enviar ao agente · identificar a mensagem
de limite · entender a orientação recebida · avaliar a confiança na resposta.

**Requisitos:** RF03, RF08, RNF04, RNF11.

**Observar:** a Seção 9.3 antecipa a tensão deste cenário — declarar o limite
atende ao RNF04, mas pode falhar no RNF07 se o agente não orientar a reformulação.
Anotar textualmente o que o participante diz ao receber a resposta; é a evidência
mais direta sobre confiança.

## Cenário 6 — Sugestão proativa e controle do usuário (6 min)

O modo proatividade já está ligado desde o início da sessão, igual para todos
(checklist de ambiente).

**Instrução, parte A:**
> Você vai participar de uma reunião sobre o projeto PRJ-0442. Use o agente para se
> preparar.

A instrução não menciona sugestões. Consultas sobre situação, prazos, riscos ou
marcos do projeto fazem o agente oferecer um próximo passo, na forma de uma
pergunta que depende da confirmação do usuário — por exemplo, "Quer que eu
priorize o risco mais relevante e sugira uma medida de mitigação?".

Quando o participante disser que terminou, perguntar apenas: "Me conte o que você
viu nas respostas."

**Instrução, parte B** — lida só depois da parte A:
> Imagine que, a partir de agora, você prefere que o agente responda só o que foi
> perguntado. Faça esse ajuste.

**Etapas:** realizar consulta válida · ler a sugestão opcional · aceitar ou
recusar a sugestão · confirmar o controle da ação · avaliar a utilidade da
sugestão.

| Etapa | Como classificar |
| --- | --- |
| Ler a sugestão opcional | `sucesso` se a percebe sozinha na parte A; `dificuldade` se só a menciona ao responder "o que você viu"; `nao_conseguiu` se não a percebe |
| Aceitar ou recusar | `sucesso` se decide e a decisão tem o efeito esperado; `nao_testado` se nenhuma sugestão apareceu em duas consultas |
| Confirmar o controle da ação | `sucesso` se entende que nada foi executado sem a confirmação dele **e**, na parte B, encontra e desliga o modo proatividade |

**Requisitos:** RF07, RF09, RF10.

Se o participante acreditar que o agente executou uma ação sem confirmação, é
ocorrência `alta`: perda de controle percebida.

## Cenário 7 — Entrada por voz (6 min)

**Instrução:**
> Envie uma pergunta curta por voz e verifique se a transcrição preserva sua
> intenção.

**Etapas:** acionar a entrada por voz · falar a pergunta curta · conferir a
transcrição · enviar a solicitação · avaliar a resposta recebida.

**Requisitos:** RF01, RNF07, Seções 5.3.4 e 8.7.

Se a entrada por voz estiver indisponível na sessão, as cinco etapas ficam
`nao_testado`, com a dependência nomeada nas observações. Não substituir por uma
pergunta digitada, porque isso faria o cenário parecer executado.

---

## Encerramento (5 min)

> Terminamos as tarefas. Agora vou te pedir para responder dez perguntas rápidas
> sobre a sua experiência. Não tem certo nem errado: é a sua impressão.

Enviar o formulário SUS ([`questionario-sus.md`](questionario-sus.md)). O
participante responde sozinho, sem comentários do moderador sobre as alternativas.

Depois do SUS, três perguntas abertas:

1. O que foi mais difícil ou mais confuso na sessão?
2. Você confiaria em uma resposta desse agente para levar a uma reunião? Por quê?
3. Se você pudesse mudar uma coisa, o que seria?

Agradecer e interromper a gravação. Conferir que a planilha está completa antes de
o participante sair: lacuna preenchida de memória vale menos.

## Logo após a sessão, no mesmo dia

- passar as observações e as ocorrências da planilha para
  [`dados/registro.csv`](dados/registro.csv) e
  [`dados/ocorrencias.csv`](dados/ocorrencias.csv), sem nomes;
- lançar as respostas do formulário em [`dados/sus.csv`](dados/sus.csv);
- atualizar a linha do participante em
  [`dados/participantes.csv`](dados/participantes.csv), com o commit testado;
- guardar o termo assinado fora do repositório.
