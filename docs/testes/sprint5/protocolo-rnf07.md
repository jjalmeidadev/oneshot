# S5-31 — amostra congelada de RNF07

Data: 05/10/2026 (America/Fortaleza). Origem: Seção 9.2.3 de `docs/Projeto.md`.

A amostra em `amostra-rnf07.csv` contém 20 formulações: 10 positivas e 10
negativas (ambiguidade, sinônimos e erros leves). Foi preparada antes da rodada;
não representa falas coletadas de participantes. A base é a massa sintética
versionada em `src/backend/app/rag/data/sharepoint`. O manifesto da rodada
registra SHA-256 da amostra e das fontes. Não alterar frases ou critérios após
observar respostas; revisões exigem nova rodada identificada.

## Aplicação

1. Obter consentimento com o material de `docs/usabilidade`; identificar cada
   participante apenas por código. Não registrar nome, e-mail ou token.
2. Registrar commit, canal, provedor/modelo e configuração da aplicação. Confirmar
   estabilidade com uma solicitação fora da amostra. Não usar respostas simuladas
   para declarar compreensão conversacional.
3. Pedir aos participantes que enviem as frases na interface sem apresentar
   comandos ou nomes internos. Usar uma conversa nova por frase, inclusive nos
   casos ambíguos. Não treinar o participante com o resultado esperado.
4. Registrar literalmente a resposta anonimizada, o código do participante e
   eventuais erros. Não substituir resposta ruim nem descartar uma tentativa.
5. O avaliador atribui `compreendida`, `orientacao_util` ou `falhou`, usando o
   critério individual congelado. Orientação útil precisa dizer o que esclarecer
   ou como reformular; somente “não encontrei” não basta. Não contar duas vezes
   uma mesma frase. Campos vazios significam não executado.
6. Revisor de outra frente confere respostas e avaliações. Guardar a planilha
   preenchida separada da amostra congelada, com identificação da rodada.

## Apuração

Taxa = 100 × (compreendidas + orientações úteis) / 20. Aceitação: pelo menos
16/20 (80%). Informar também os subtotais P e N, sem aplicar um limiar novo por
subgrupo. Com qualquer frase não executada, publicar contagem parcial e manter
RNF07 pendente; não reduzir o denominador nem declarar aprovação da amostra.
Ausência de participantes/respostas nesta rodada impede calcular a taxa.

## Limites

Cobertura: consultas sobre nove documentos fictícios do MVP, sem aferição de
áudio, ações transacionais ou representatividade estatística do público do Metrô.
O teste automatizado registra os dois casos humanos como `skipped`; isso não é
aprovação. Resultados anteriores de recuperação ou classificação não substituem
respostas conversacionais e avaliação com participantes.
