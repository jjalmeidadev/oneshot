# Sessão RNF07 — participante P01

Data: 05/10/2026, America/Fortaleza.
Estado atual (06/10/2026): coleta recebida por imagens — vinte
formulações distintas documentadas, avaliação do participante e confirmação
das condições de aplicação pendentes.

Participante confirmou nesta conversa que pode realizar a aplicação e pediu
inicialização local. Consentimento recebido nesta conversa para registro de
perguntas, respostas do protótipo e avaliações sob código P01, sem nome nem
gravação, com finalidade de documentação acadêmica. Foi informado de que os
dados são fictícios e de que pode interromper quando quiser. Resposta literal:
“Autorizo esse registro”.

Amostra: `docs/testes/sprint5/amostra-rnf07.csv`, SHA-256
`ab61a63a088ca3c47d235588e0a05cb225a59a6eb89e80973b2100921f6587ff`.
Identificadores das frases P01–P10 e N01–N10 não são identificadores de pessoas.

Ambiente preparado: frontend Vite em `http://127.0.0.1:5173`, backend local
em `http://127.0.0.1:8000`. Fonte: nove documentos sintéticos versionados;
conexões PostgreSQL/Supabase desabilitadas nesta instância para preservar a
origem congelada. Provedor configurado: OpenRouter, modelo
`google/gemini-3.7-flash`; credenciais mantidas no ambiente local e ausentes
das evidências. Classificador ligado, proatividade desligada, conversa nova
por frase. A disponibilidade ponta a ponta ainda depende do smoke test.

Uma sessão com um único participante é uma avaliação formativa;
não demonstra representatividade de usuários finais do parceiro. A revisão
de outra frente permanece pendente.

## Verificação prévia do ambiente

Frontend e `/health`: HTTP 200. Pergunta de aquecimento fora da amostra:
“Quais orientações existem para o embarque no trem?”. A rota retornou HTTP 502;
requisição e resposta estão em `smoke-rnf07.json`. A chamada diagnóstica mínima
ao OpenRouter, fora do sandbox, retornou HTTP 401 e `API key expired.`.
O teste da alternativa Gemini direto retornou HTTP 503 por alta demanda no
modelo `gemini-3.7-flash`. Credenciais não foram copiadas para evidências.
Esses diagnósticos não são tentativas de participantes e não entram no
numerador nem no denominador da amostra RNF07.

Após retentativa, a chamada mínima ao Gemini direto respondeu com sucesso.
Uma instância local passou a usar `LLM_PROVIDER=gemini` apenas no processo,
sem modificar `.env`. O aquecimento completo voltou a apresentar HTTP 503
do provedor durante as retentativas. Assim, a chamada mínima bem-sucedida
não foi tomada como prova de estabilidade. O participante informou que vai
atualizar `OPENROUTER_API_KEY` no `.env` e avisar; a atualização ainda não foi
confirmada. Nenhuma das vinte frases foi aplicada ao participante até aqui.

## Ambiente liberado para aplicação

O participante confirmou “atualizei”. O backend foi reiniciado para reler a
configuração. O aquecimento com classificador ligado e proatividade desligada
retornou HTTP 200, modelo `google/gemini-3.7-flash`, pelo OpenRouter.
Evidência integral: `smoke-rnf07-chave-atualizada.json`. A resposta foi
“Não há evidência recuperada suficiente para responder com rastreabilidade.”
Isso demonstra conexão e execução, não aprovação da qualidade conversacional.
A pergunta não pertence à amostra e não foi computada em RNF07.

Configuração da aplicação humana: OpenRouter com o mesmo modelo, base
sintética local, validação de intenção ligada, proatividade desligada e
conversa nova por frase. O participante receberá blocos de cinco frases e
deverá devolver a resposta literal e sua avaliação para cada uma. O primeiro
bloco corresponde a P01–P05. Ainda não há resultado humano a contabilizar.

## Coleta recebida em 06/10/2026

Duas imagens enviadas pelo participante mostram P01 duas vezes, P04 e P05.
A duplicata não aumenta a amostra. A [transcrição integral](transcricao-rnf07-p01.md)
e a [planilha parcial](coleta-rnf07-p01.csv) registram as respostas e a avaliação
técnica preliminar: duas compreendidas e uma falha. P02 e P03 não aparecem.
Ainda faltam avaliações do participante, revisão independente, confirmação
de conversa nova por frase e incorporação dos binários das imagens ao repositório.
As afirmações anteriores de ausência de coleta descrevem a preparação histórica.

No segundo envio, outras duas imagens documentam P02 e P03. Ambas retornam
ausência de evidência suficiente, sem responder ou orientar reformulação.
A avaliação técnica preliminar do primeiro bloco passa a **2 compreendidas
e 3 falhas**, em cinco formulações distintas. Faltam quinze respostas da
amostra e permanecem pendentes as confirmações e avaliações acima.

No terceiro envio, três imagens documentam P06–P10. P06 e P10 atendem à
rubrica; P07, P08 e P09 não respondem nem orientam reformulação. Total técnico
preliminar: **4 compreendidas e 6 falhas** em dez frases positivas. Faltam
N01–N10. Mantidas essas avaliações, o teto da rodada é 14/20 (70%), abaixo
da meta de 80%; a coleta deve ser concluída e preservada antes de corrigir
o comportamento e realizar eventual reteste. Ainda não houve confirmação
do participante sobre conversas novas ou suas avaliações de utilidade.

No quarto envio, cinco imagens documentam N01–N05. Todas apresentam a mesma
resposta de fora de escopo, identificada como `rag-retriever`, sem pedir
esclarecimento ou orientar reformulação. Foram avaliadas preliminarmente
como falhas conforme as rubricas individuais. Total atual: **4 compreendidas
e 11 falhas** em quinze formulações distintas. Faltam N06–N10; o teto de
sucesso da rodada passa a 9/20 (45%). A confirmação das condições de aplicação,
as avaliações do participante e a revisão independente continuam pendentes.

No quinto envio, cinco imagens documentam N06–N10. N06 e N08 foram
compreendidas; N07, N09 e N10 falharam. Coleta concluída das vinte frases,
com **6 compreendidas, nenhuma orientação útil e 14 falhas (30%)** pela
avaliação técnica preliminar. RNF07 não atinge 80%. A revisão independente,
as avaliações do participante, a confirmação de conversas novas e a
incorporação dos arquivos originais das imagens permanecem pendentes.
