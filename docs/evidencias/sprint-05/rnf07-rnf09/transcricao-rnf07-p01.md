# RNF07 — transcrição das imagens do participante P01

Recebimento: 06/10/2026, America/Fortaleza. Origem: dezessete imagens enviadas
pelo participante nesta conversa. Transcrição visual feita pelo assistente
Codex, sem reexecutar as solicitações. Os binários das imagens não foram
disponibilizados como arquivos locais: os originais permanecem anexados à
conversa e **ainda precisam ser incorporados ao repositório** para preservar
a evidência visual junto ao MR. Não foram inventados nomes de arquivo nem
hashes de imagens. As quebras visuais de linha foram unidas; a grafia foi
preservada.

Os horários transcritos abaixo são os exibidos na interface. A data de execução
não aparece nos recortes; 06/10/2026 é a data de recebimento, não uma data
inferida a partir dos horários. Nas imagens 1–7, o modelo visível é
`google/gemini-3.7-flash`; nas imagens 8–12, a identificação exibida é
`rag-retriever`. Essa identificação não foi transcrita como chamada a um LLM.

## Imagem 1 — duas ocorrências da frase P01

Pergunta, em ambas as ocorrências:

> Como uso o bilhete digital na catraca?

Resposta, em ambas as ocorrências:

> No cenario ficticio do MVP, o bilhete digital pode ser apresentado na catraca pelo celular. Se a leitura falhar, aumentar o brilho da tela, confirmar que o codigo esta inteiramente visivel e procurar um agente de atendimento. [Fonte 1]

Fonte visível: **Uso do bilhete digital no MVP**. Horário: 00:05.
Classificação visível: **INDEFINIDA 46.9%**.

Avaliação técnica preliminar: **compreendida**. A resposta explica a
apresentação pelo celular e o procedimento de falha, atendendo à rubrica
congelada. O rótulo do classificador não é usado isoladamente para reprovar
a compreensão conversacional: avalia-se a resposta final entregue.

As duas ocorrências são preservadas nesta transcrição, mas P01 entra apenas
uma vez na amostra. Não se sabe se houve reenvio ou duplicação na exibição.
Não correspondem a P02 nem P03, cujas perguntas são diferentes.

## Imagem 2 — frase P04

Pergunta:

> Posso levar minha bicicleta no domingo?

Resposta:

> Na politica ficticia do MVP, bicicletas sao aceitas aos sabados, domingos e feriados durante toda a operacao, e nos dias uteis apos as 20h30. O passageiro deve usar o ultimo carro e respeitar a capacidade indicada pela equipe. [Fonte 1]

Fonte visível: **Transporte de bicicleta**. Horário: 00:06.
Classificação visível: **FORA_DE_ESCOPO 56.4%**.

Avaliação técnica preliminar: **compreendida**. Informa permissão aos domingos
e condições de uso, conforme a fonte sintética e a rubrica. A classificação
divergente fica registrada como observação; a resposta final atende à pergunta.

## Imagem 2 — frase P05

Pergunta:

> Em que horário posso levar bicicleta durante a semana?

Resposta:

> Não há evidência recuperada suficiente para responder com rastreabilidade.

A interface exibe **FONTES CONSULTADAS, SEM EVIDÊNCIA PARA ESTA RESPOSTA**,
com os títulos **Transporte de bicicleta** e **Operacao assistida na Linha Azul**.
Horário: 00:06. Classificação: **INDEFINIDA 51.4%**.

Avaliação técnica preliminar: **falhou**. A rubrica exige informar o horário
após 20h30 e condições da fonte. A resposta não traz o horário nem diz como
reformular. A fonte sintética `base_atendimento.json`, item 303, contém essa
informação. A imagem comprova o sintoma, mas não identifica se a perda ocorreu
na geração ou na validação da resposta; nenhuma causa foi inferida como certa.
Ocorrência **OBS-S5-31-RNF07-01**, a investigar depois da coleta congelada.

## Imagem 3 — frase P02 (segundo envio)

Pergunta:

> O código do meu bilhete não está sendo lido. O que faço?

Resposta:

> Não há evidência recuperada suficiente para responder com rastreabilidade.

A interface exibe **FONTES CONSULTADAS, SEM EVIDÊNCIA PARA ESTA RESPOSTA**,
com o título **Uso do bilhete digital no MVP**. Horário: 00:16.
Classificação visível: **INDEFINIDA 49.2%**.

Avaliação técnica preliminar: **falhou**. Não orienta aumentar o brilho,
conferir a visibilidade do código e procurar atendimento, conforme previsto
na fonte sintética e na rubrica. Também não oferece reformulação acionável.
O título pertinente foi recuperado, mas o recorte não determina a causa da
ausência de resposta. Registrada como mais uma ocorrência do sintoma
**OBS-S5-31-RNF07-01**, sem atribuir causa à geração ou à validação.

## Imagem 4 — frase P03 (segundo envio)

Pergunta:

> Como registro uma reclamação sobre o atendimento?

Resposta:

> Não há evidência recuperada suficiente para responder com rastreabilidade.

A interface exibe **FONTES CONSULTADAS, SEM EVIDÊNCIA PARA ESTA RESPOSTA**,
com os títulos **Canal de registro de sugestoes e reclamacoes** e
**Atendimento a objeto perdido**. Horário: 00:18.
Classificação visível: **INDEFINIDA 45.5%**.

Avaliação técnica preliminar: **falhou**. Não informa o canal fictício nem
os dados mínimos para registrar a reclamação, conforme a rubrica; não orienta
reformulação. O título pertinente foi recuperado. Também compõe a ocorrência
**OBS-S5-31-RNF07-01**, com causa ainda não determinada.

## Imagem 5 — frase P06 (terceiro envio)

Pergunta:

> Por que o intervalo dos trens da Linha Azul aumenta à noite?

Resposta:

> Durante o periodo ficticio, o intervalo entre trens podera ser ampliado entre 22h e o encerramento da operacao para testes de sinalizacao. Recomenda-se comunicar o tempo adicional de viagem nos canais de atendimento. [Fonte 1]

Fonte visível: **Operacao assistida na Linha Azul**. Pergunta às 00:19 e
resposta às 00:20. Classificação: **CONSULTA 97.5%**.
Avaliação técnica preliminar: **compreendida**, pois explica os testes de
sinalização e o período a partir das 22h, conforme a rubrica.

## Imagem 5 — frase P07

Pergunta:

> Qual acesso devo usar na Estação República durante a manutenção?

Resposta:

> Não há evidência recuperada suficiente para responder com rastreabilidade.

Fontes visíveis sob **FONTES CONSULTADAS, SEM EVIDÊNCIA PARA ESTA RESPOSTA**:
**Acesso alternativo na Estacao Republica** e **Transporte de bicicleta**.
Horário: 00:20. Classificação: **CONSULTA 98.6%**.
Avaliação técnica preliminar: **falhou**. Não indica a Rua do Arouche nem
orienta reformulação. A classificação como consulta e a fonte pertinente
visível não bastaram para produzir resposta adequada.

## Imagem 6 — frase P08

Pergunta:

> Perdi um objeto no metrô. Como registro isso?

Resposta:

> Não há evidência recuperada suficiente para responder com rastreabilidade.

Fontes visíveis sob **FONTES CONSULTADAS, SEM EVIDÊNCIA PARA ESTA RESPOSTA**:
**Atendimento a objeto perdido** e **Canal de registro de sugestoes e reclamacoes**.
Horário: 00:20. Classificação: **INDEFINIDA 49.8%**.
Avaliação técnica preliminar: **falhou**. Não orienta registrar descrição,
local e horário ou consultar achados e perdidos, nem oferece reformulação útil.

## Imagem 7 — frase P09

Pergunta:

> Como ajudar um passageiro com mobilidade reduzida?

Resposta:

> Não há evidência recuperada suficiente para responder com rastreabilidade.

Fonte visível sob **FONTES CONSULTADAS, SEM EVIDÊNCIA PARA ESTA RESPOSTA**:
**Apoio a passageiro com mobilidade reduzida**. Horário: 00:21.
Classificação: **CONSULTA 64.1%**.
Avaliação técnica preliminar: **falhou**. Não orienta confirmar destino,
comunicar a equipe de recepção e usar rota acessível, nem oferece reformulação.

P07, P08 e P09 ampliam o sintoma **OBS-S5-31-RNF07-01**: fonte pertinente
visível e resposta de insuficiência sem orientação. A causa permanece não
determinada pelas imagens.

## Imagem 7 — frase P10

Pergunta:

> O que fazer quando uma escada rolante fica indisponível?

Resposta:

> Sinalizar o equipamento como indisponivel, indicar a alternativa acessivel mais proxima e abrir um chamado de manutencao. Atualizar o comunicado ao passageiro quando o status do chamado mudar. [Fonte 1]

O título da fonte aparece truncado na imagem: **Comunicacao de indisponibilidade de escada rol...**.
Horário: 00:21. Classificação: **CONSULTA 95.4%**.
Avaliação técnica preliminar: **compreendida**, pois informa sinalização,
alternativa acessível e abertura de chamado, conforme a rubrica congelada.

## Imagens 8–12 — frases N01–N05 (quarto envio)

As cinco respostas são literalmente iguais:

> Essa solicitação não está no escopo da base de conhecimento disponível.

Nenhuma fonte é exibida nesses recortes. A identificação de resposta exibida
é `rag-retriever` em todos eles. Os dados individuais são:

| Imagem | Frase | Pergunta literal | Horário | Classificação visível |
|---|---|---|---|---|
| 8 | N01 | Isso ainda está funcionando? | 00:25 | INDEFINIDA 52.8% |
| 9 | N02 | E amanhã? | 00:26 | FORA_DE_ESCOPO 96.6% |
| 10 | N03 | Meu tíquete eletrônico não passa no bloqueio. | 00:30 | ALERTA 72.3% |
| 11 | N04 | Quero registrar uma insatisfação com a viagem. | 00:31 | TRANSACAO 57.5% |
| 12 | N05 | Posso embarcar com minha magrela no domingo? | 00:31 | FORA_DE_ESCOPO 58.5% |

Avaliação técnica preliminar: **falhou** para cada uma das cinco frases.
A negativa genérica não atende à orientação acionável exigida pela rubrica:

- N01: não solicita identificação do equipamento ou serviço referido por “isso”.
- N02: não pede assunto nem contexto para “amanhã”.
- N03: não compreende o bilhete digital nem pede esclarecimento específico.
- N04: não orienta o registro de reclamação nem uma reformulação específica.
- N05: não compreende bicicleta nem pergunta o significado de “magrela”.

Ocorrência **OBS-S5-31-RNF07-02 — ausência de orientação útil na resposta de
fora de escopo**. O rótulo do classificador, isoladamente, não é critério de
aprovação ou reprovação: o defeito observado é a resposta entregue sem
compreensão ou ajuda para reformular. Não houve reexecução pelo assistente.

## Imagens 13–17 — frases N06–N10 (quinto envio)

### Imagem 13 — N06

> Como uso o bilhete digtal na catraca?

> No cenario ficticio do MVP, o bilhete digital pode ser apresentado na catraca pelo celular. Se a leitura falhar, aumentar o brilho da tela, confirmar que o codigo esta inteiramente visivel e procurar um agente de atendimento. [Fonte 1]

Fonte: **Uso do bilhete digital no MVP**. Horário: 00:33.
Classificação: **CONSULTA 72.0%**. Modelo: `google/gemini-3.7-flash`.
Avaliação técnica preliminar: **compreendida**, apesar do erro leve “digtal”.

### Imagem 14 — N07

> Perdi um objto no metro. Como registro?

> Não há evidência recuperada suficiente para responder com rastreabilidade.

Fonte sob o aviso de ausência de evidência: **Canal de registro de sugestoes e reclamacoes**.
Horário: 00:33. Classificação: **FORA_DE_ESCOPO 59.3%**.
Modelo: `google/gemini-3.7-flash`.
Avaliação técnica preliminar: **falhou**. Não compreende objeto perdido nem
oferece reformulação útil. Diferentemente dos casos com título pertinente
visível, o recorte mostra somente uma fonte de reclamações. Registrar como
**OBS-S5-31-RNF07-03 — recuperação inadequada diante de erro leve**, sem
atribuir às imagens uma prova completa do processamento interno.

### Imagem 15 — N08

> A escda rolante parou. O que faço?

> Sinalizar o equipamento como indisponivel, indicar a alternativa acessivel mais proxima e abrir um chamado de manutencao. Atualizar o comunicado ao passageiro quando o status do chamado mudar. [Fonte 1]

Fonte com título truncado: **Comunicacao de indisponibilidade de escada rol...**.
Pergunta às 00:33 e resposta às 00:34. Classificação: **CONSULTA 75.2%**.
Modelo: `google/gemini-3.7-flash`.
Avaliação técnica preliminar: **compreendida**, apesar do erro leve “escda”.

### Imagem 16 — N09

> Está atrasado?

> Essa solicitação não está no escopo da base de conhecimento disponível.

Sem fonte exibida. Horário: 00:34. Classificação: **FORA_DE_ESCOPO 61.1%**.
Identificação da resposta: `rag-retriever`.
Avaliação técnica preliminar: **falhou**. Não solicita identificação do
projeto ou serviço e período. Amplia **OBS-S5-31-RNF07-02**.

### Imagem 17 — N10

> Por onde entro se a entrada da República estiver interditada?

> Não há evidência recuperada suficiente para responder com rastreabilidade.

Fonte sob o aviso de ausência de evidência: **Acesso alternativo na Estacao Republica**.
Horário: 00:34. Classificação: **CONSULTA 68.3%**.
Modelo: `google/gemini-3.7-flash`.
Avaliação técnica preliminar: **falhou**. Não indica Rua do Arouche nem
oferece esclarecimento útil. Amplia **OBS-S5-31-RNF07-01**.

## Consolidação das vinte respostas e limites

Vinte formulações distintas documentadas: **6 compreendidas, 0 orientações
úteis e 14 falhas**, em avaliação técnica preliminar. As positivas P01–P10
somam 4 compreendidas e 6 falhas; as negativas N01–N10 somam 2 compreendidas
e 8 falhas. Não há frase sem resposta registrada. A duplicata de P01 não conta.

Taxa observada: **100 × (6 + 0) / 20 = 30%**, abaixo dos 80% (16/20).
RNF07 reprovado pela rubrica técnica aplicada às respostas recebidas.
Os subtotais de 40% para positivas e 20% para negativas são descritivos;
não representam novos limiares de aceitação por subgrupo. Avaliação do
participante e revisão de outra frente permanecem pendentes.

Não houve alteração do produto pelo assistente durante a coleta humana.
Eventuais correções devem ser avaliadas em rodada posterior, preservando
estas evidências. A apuração automatizada do CSV não reaplica o teste com
participantes nem constitui revisão independente.

Os recortes mostram múltiplas interações, mas não comprovam se cada frase
foi enviada em conversa nova. Essa condição do protocolo está pendente de
confirmação. Se houve desvio, preservar os registros como exploratórios e
identificar uma nova rodada conforme o protocolo, sem apagar falhas.

Dados tabulados em [coleta-rnf07-p01.csv](coleta-rnf07-p01.csv). A amostra
original não foi alterada e estas transcrições não são saídas de `pytest`.
