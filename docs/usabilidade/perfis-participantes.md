# Perfis e recrutamento dos participantes

Transforma a tabela de perfis da Seção 9.3.1 do
[`Projeto.md`](../Projeto.md) em critérios de recrutamento verificáveis.

## Por que a diversidade é critério

O planejamento exige ao menos cinco participantes externos à turma, com diversidade
de perfil e de familiaridade tecnológica. Cinco pessoas acostumadas a agentes
conversacionais mostrariam pouco sobre a adoção por quem não usa esse tipo de
ferramenta, e o viés de confirmação entra pelo recrutamento, não pela condução.
Por isso os perfis abaixo são **vagas distintas**. Se uma vaga não for preenchida,
o relatório registra a vaga vazia e o efeito dela sobre a leitura dos resultados;
um participante extra de perfil já coberto não substitui a vaga sem que a troca
seja declarada.

## Vagas

| Vaga | Perfil | O que este participante permite observar |
| :---: | --- | --- |
| P1 | Experiência em gestão de projetos | Se as respostas sustentam consultas reais sobre status, prazos, riscos e marcos |
| P2 | Experiência em análise ou acompanhamento de indicadores | Se respostas e comparações são compreensíveis para apoiar decisão |
| P3 | Familiaridade com ferramentas Microsoft, como Teams e SharePoint | Se o canal de interação é aderente ao ambiente corporativo previsto |
| P4 | Baixa familiaridade com agentes conversacionais | Se a linguagem natural dispensa treinamento ou comando técnico |
| P5 | Sem vínculo com a equipe desenvolvedora | Dúvidas espontâneas, sem viés de confirmação |
| P6 | Reserva, de qualquer perfil, declarando qual | Folga prevista na planilha do grupo para até seis participantes |

Todos os participantes são externos à turma. A vaga P5 reforça a ausência de
vínculo, mas a exigência vale para as seis.

A familiaridade tecnológica é registrada para todos, e não só para P4: a amostra
precisa reunir ao menos um participante de familiaridade `baixa` e um de `alta`
com agentes conversacionais, para que a leitura do SUS e das dificuldades não
reflita um único nível de experiência.

## Elegibilidade

Elegível:

- maior de 18 anos;
- externo à turma T17 e sem participação no desenvolvimento do produto;
- disponível para uma sessão única de 40 a 50 minutos;
- de acordo com o registro por anotação e, se quiser, com a gravação de tela e áudio.

Não elegível:

- integrantes do grupo Oneshot ou de outros grupos da turma;
- quem já participou de uma sessão deste produto, porque o aprendizado da primeira
  sessão contaminaria a medição de facilidade de uso;
- quem acompanhou o desenvolvimento de perto a ponto de conhecer a massa sintética:
  saber de antemão que só existe o `PRJ-0442` invalida os cenários de informação
  ausente e de comparação.

## Registro

Cada confirmação vai para [`dados/participantes.csv`](dados/participantes.csv), com
a vaga, as duas familiaridades declaradas, a faixa etária e as datas de confirmação
e da sessão. A data de confirmação mostra se o recrutamento foi feito antes das
sessões, o que muda a leitura de um resultado.

## Anonimização

Nenhum documento versionado registra nome, e-mail, telefone, empregador ou cargo.
Nos artefatos, cada participante aparece assim:

```
P3 | vaga: ferramentas_microsoft | familiaridade com agentes: media | faixa etária: 30-39
```

O vínculo entre pessoa e código existe apenas no termo de consentimento assinado,
guardado pelo moderador fora do repositório.
