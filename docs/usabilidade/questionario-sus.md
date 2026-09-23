# Questionário SUS — *System Usability Scale*

Aplicado ao final de cada sessão pelo formulário online da Seção 9.3.1 do
[`Projeto.md`](../Projeto.md), "Avaliação do Agente de Gestão de Portfólio". As
afirmações abaixo são as do formulário, na mesma ordem; se alguma mudar no
formulário, este arquivo muda junto.

## Aplicação

- escala de 1 a 5, em que **1 = Discordo completamente** e **5 = Concordo
  completamente**;
- o participante responde sozinho, sem o moderador comentar as alternativas;
- as dez afirmações aparecem sempre nesta ordem, para que as respostas sejam
  comparáveis;
- nenhuma afirmação fica em branco; se o participante não quiser responder uma, o
  SUS dele é registrado como inválido, e nunca completado por estimativa.

A alternância entre afirmações positivas (ímpares) e negativas (pares) é do
instrumento original (Brooke, 1996) e é mantida: ela ajuda a identificar quem marca
tudo igual sem ler.

## Afirmações

> Avalie sua experiência utilizando o Agente de Gestão de Portfólio através desta
> pesquisa de satisfação.

| # | Afirmação | Sentido |
| :---: | --- | :---: |
| 1 | Você gostaria de utilizar o Agente de Gestão de Portfólio com frequência para consultar status, prazos, riscos, marcos e informações dos projetos? | + |
| 2 | Você achou o agente desnecessariamente complexo para realizar consultas ou análises sobre o portfólio de projetos? | − |
| 3 | Foi fácil interagir com o agente usando linguagem natural, sem precisar conhecer comandos técnicos, nomes internos de campos ou a estrutura dos dados? | + |
| 4 | Você precisaria de apoio técnico ou treinamento adicional para conseguir usar o agente de forma adequada nas suas atividades de gestão de portfólio? | − |
| 5 | As funcionalidades do agente pareceram bem integradas, incluindo interpretação da solicitação, recuperação de informações, comparação entre projetos e apresentação das fontes utilizadas? | + |
| 6 | Você percebeu inconsistências nas respostas do agente, como falta de clareza, informações pouco fundamentadas ou dificuldade em diferenciar dados recuperados de interpretações geradas? | − |
| 7 | Você acredita que usuários do PMO, gestores e demais perfis envolvidos conseguiriam aprender rapidamente a usar o agente dentro do fluxo de trabalho no Teams? | + |
| 8 | Você achou a interação com o agente lenta, trabalhosa ou difícil ao tentar obter respostas, comparar projetos ou entender limitações da base de informações? | − |
| 9 | Você sentiu confiança nas respostas do agente porque elas foram claras, úteis, compatíveis com a solicitação feita e indicaram fontes ou limitações quando necessário? | + |
| 10 | Você precisou aprender muitas coisas antes de conseguir usar o agente com segurança para consultar informações, interpretar respostas ou validar se os requisitos do projeto estavam sendo atendidos? | − |

## Cálculo

1. itens ímpares: contribuição = resposta − 1;
2. itens pares: contribuição = 5 − resposta;
3. soma das dez contribuições, de 0 a 40;
4. multiplicação por 2,5: SUS de 0 a 100.

O SUS não é porcentagem: um SUS de 70 não significa "70% de aprovação".

## Como o resultado é lido

O SUS entra na consolidação como **dado descritivo**, lido junto da observação das
tarefas, e não como critério de aprovação do sistema. Não há meta de SUS.

- **Mede percepção global, não aponta problemas.** O que mostra onde o sistema
  falha é a observação: em que etapa cada pessoa hesitou, errou ou pediu ajuda. O
  SUS diz como a experiência foi percebida no conjunto.
- **Foi criado para interfaces gráficas.** As afirmações foram adaptadas ao agente
  e ao portfólio, mas alguns itens seguem se ajustando mal a uma interação
  conversacional. Borsci et al. (2022) propõem uma escala própria para agentes
  conversacionais, a *Chatbot Usability Scale*.
- **O item 7 é uma projeção.** Ele pergunta sobre o uso dentro do Teams, e as
  sessões acontecem na interface web da bancada, porque o ambiente Teams do Metrô
  não está acessível ao grupo. A resposta mede a expectativa do participante, e
  não uma experiência que ele teve.
- **Com cinco participantes, a média é instável.** Cinco pessoas bastam para revelar
  boa parte dos problemas recorrentes (Nielsen e Landauer, 1993), mas a média do SUS
  só se estabiliza por volta de 12 a 14 respondentes (Tullis e Stetson, 2004).

Por isso a consolidação publica **a nota de cada participante, a mediana e a
amplitude**, ao lado do perfil e da familiaridade declarada. A média aparece só
acompanhada do número de respondentes. Uma média de 72 com notas entre 45 e 95
conta uma história diferente de uma média de 72 com notas entre 68 e 76.

## Perguntas abertas

Aplicadas depois do SUS, sem escala:

1. O que foi mais difícil ou mais confuso na sessão?
2. Você confiaria em uma resposta desse agente para levar a uma reunião? Por quê?
3. Se você pudesse mudar uma coisa, o que seria?

As respostas vão para a coluna `comentario_aberto` de
[`dados/sus.csv`](dados/sus.csv), sem nada que identifique o participante.

## Referências

BORSCI, Simone et al. The Chatbot Usability Scale: the design and pilot of a
usability scale for interaction with AI-based conversational agents. *Personal and
Ubiquitous Computing*, v. 26, p. 95-119, 2022.

BROOKE, John. SUS: a "quick and dirty" usability scale. In: JORDAN, Patrick W. et
al. (ed.). *Usability Evaluation in Industry*. London: Taylor & Francis, 1996.
p. 189-194.

NIELSEN, Jakob; LANDAUER, Thomas K. A mathematical model of the finding of
usability problems. In: *Proceedings of the INTERACT'93 and CHI'93 Conference on
Human Factors in Computing Systems*. New York: ACM, 1993. p. 206-213.

TULLIS, Thomas S.; STETSON, Jacqueline N. A comparison of questionnaires for
assessing website usability. In: *Usability Professionals Association Annual
Conference*. Minneapolis: UPA, 2004.
