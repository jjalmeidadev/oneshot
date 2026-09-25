# Testes de usabilidade — instrumentos e dados

Instrumentos de campo e dados anonimizados dos testes de usabilidade da Sprint 4,
planejados na Seção 9.3 do [`Projeto.md`](../Projeto.md).

As sessões usam a interface web da bancada (`src/frontend`), que reproduz a conversa,
as fontes citadas, a sugestão proativa e a entrada por voz. O agente foi projetado
para rodar no Teams do Metrô, mas esse ambiente não está acessível ao grupo.

## Instrumentos

| Arquivo | Quando usar |
| --- | --- |
| [`perfis-participantes.md`](perfis-participantes.md) | No recrutamento: vagas, elegibilidade e anonimização |
| [`termo-consentimento.md`](termo-consentimento.md) | Antes de cada sessão; a via assinada fica fora do repositório |
| [`checklist-ambiente.md`](checklist-ambiente.md) | Antes de cada sessão, inteiro |
| [`roteiro-moderador.md`](roteiro-moderador.md) | Durante a sessão: abertura, regras de intervenção e os sete cenários |
| [`questionario-sus.md`](questionario-sus.md) | Ao final da sessão, junto do formulário online |
| [`consolidacao_usabilidade.ipynb`](../../src/notebooks/consolidacao_usabilidade.ipynb) | Depois das sessões: consolida os dados abaixo |

A planilha "Oneshot - Testes de Usabilidade - Agente de Gestão de Portifólio" e o
formulário SUS online, descritos na Seção 9.3.1, continuam sendo os instrumentos de
campo. Os arquivos de [`dados/`](dados/) são a versão anonimizada que vai para o
repositório e alimenta a consolidação.

## Sequência

```
recrutar (perfis-participantes.md) → dados/participantes.csv
  → por sessão:  checklist-ambiente.md
                 termo-consentimento.md
                 roteiro-moderador.md  →  planilha do grupo  →  dados/registro.csv
                                                             →  dados/ocorrencias.csv
                 formulário SUS        →  dados/sus.csv
  → consolidacao_usabilidade.ipynb     →  Seção 9.3.2 do Projeto.md
```

## Dados anonimizados

Nenhum arquivo de `dados/` registra nome, e-mail, telefone, empregador ou cargo.
Cada participante aparece só como `P1` a `P6`, com a vaga de perfil e a faixa
etária de dez anos. O vínculo entre pessoa e código existe apenas no termo de
consentimento assinado, guardado pelo moderador fora do repositório.

### `participantes.csv`

| Coluna | Valores |
| --- | --- |
| `vaga_perfil` | a vaga de [`perfis-participantes.md`](perfis-participantes.md) que o participante preenche |
| `externo_a_turma` | `sim` — exigência para todos |
| `familiaridade_tecnologica`, `familiaridade_agentes` | `baixa`, `media` ou `alta`, declarada pelo participante; `nao_informada` quando não foi coletada |
| `faixa_etaria` | `18-29`, `30-39`, `40-49`, `50-59` ou `60+` |
| `sessao` | identificador da sessão de que o participante fez parte, como `S1`. Em sessão individual, `registro.csv` traz o resultado observado daquele participante; quando vários participantes fazem as tarefas na mesma sessão, a linha de cada um traz o resultado da sessão |
| `status_sessao` | `realizada`, `bloqueada` (impedida por falha de ambiente, com o motivo) ou `nao_executada` |
| `commit_testado` | commit da versão usada na sessão; o mesmo para todas |

### `registro.csv` — `resultado_geral` e `etapa_1` a `etapa_5`

| Valor | Significado |
| --- | --- |
| `sucesso` | completou sem ajuda |
| `dificuldade` | completou, mas hesitou, reformulou ou errou o caminho antes |
| `nao_conseguiu` | não completou, ou só completou depois de uma dica do moderador |
| `nao_testado` | o cenário não pôde ser exercido na versão testada, com a dependência nomeada nas observações |

`dica_dada` recebe `sim` ou `nao`. Toda dica vira `nao_conseguiu` na etapa em que
foi dada.

### `ocorrencias.csv` — `severidade`

| Valor | Critério |
| --- | --- |
| `alta` | impede a tarefa, faz o usuário perder o controle de uma ação ou quebra a confiança na resposta |
| `media` | atrapalha e exige retrabalho, mas a tarefa termina |
| `baixa` | incômodo de clareza ou de interface, sem efeito no resultado |
| `cosmetica` | detalhe visual ou de redação, sem efeito no uso |

`defeito_critico` recebe `sim` ou `nao`; toda ocorrência `alta` é avaliada para
`sim`. Todo defeito crítico precisa de `tratamento` (correção feita, com o commit,
ou impedimento declarado) e de `reteste` (`aprovado`, `reprovado` ou `pendente`).

### `ocorrencias.csv` — `participante`

O código do participante em cuja sessão a ocorrência foi registrada, o da sessão (`S1`), quando
ela vale para todos os participantes de uma sessão coletiva, ou `verificacao_posterior`, quando
foi encontrada pelo moderador depois da sessão, sem participantes. Uma ocorrência que se repete
em várias sessões entra uma vez, com a recorrência declarada no `resumo`.

### `sus.csv`

O formulário não identifica quem respondeu. Cada resposta entra como `R1`, `R2`…, na
ordem de envio, com o horário em `enviada_em`, sem vínculo com os códigos `P1`–`P6`.
`q1` a `q10` recebem inteiros de 1 a 5, na ordem do formulário. Resposta em branco
invalida aquele SUS, que é reportado como inválido e nunca completado por estimativa.
`comentario_aberto` guarda as perguntas abertas do encerramento, quando houver, sem
nada que identifique a pessoa.

## Limitação conhecida do cenário 4

A massa sintética tem um único projeto, o `PRJ-0442`, e a comparação entre
projetos foi adiada para a Sprint 5. O cenário de comparação mede se o
participante entende a recusa do agente, e não a qualidade de uma comparação. Se o
agente produzir uma comparação entre dois projetos, isso é alucinação e vira
ocorrência `alta`, com `defeito_critico = sim`.
