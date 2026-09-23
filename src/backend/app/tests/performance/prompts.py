"""Massa de prompts congelada para a medicao de desempenho do RNF05.

Os prompts saem exclusivamente da massa sintetica versionada em
`src/database/sql/02_initial_data.sql` e `src/database/sql/04_rag_synthetic_data.sql`.
Nenhum texto aqui pode ser alterado depois do inicio de uma rodada: a Secao 9.2.1
do `Projeto.md` proibe ajustar massa ou criterio apos a medicao.

A divisao segue a Secao 9.2.4: 75% de consultas simples e 25% de comparacoes
entre pelo menos dois projetos. Os pesos das tarefas do `locustfile` reproduzem
essa proporcao (3 para 1).
"""

# Consultas simples. Cada pergunta tem resposta sustentada por pelo menos um
# extrato de `public.source_extracts`, carregado por 04_rag_synthetic_data.sql.
CONSULTAS_SIMPLES: tuple[str, ...] = (
    "Em quais dias e horarios o transporte de bicicleta e permitido?",
    "Como funciona o bilhete digital no celular?",
    "Qual e o procedimento para registrar um objeto perdido?",
    "O que a equipe faz quando uma escada rolante fica indisponivel?",
    "Como e feito o apoio a passageiro com mobilidade reduzida?",
    "Qual e o periodo da operacao assistida na Linha 1-Azul?",
    "Existe acesso alternativo previsto na Estacao Republica?",
    "Como registrar uma reclamacao ou sugestao?",
    "O que e a campanha educativa de embarque?",
    "Qual e o status do comunicado de operacao assistida?",
)

# Comparacoes entre projetos.
#
# LIMITACAO DECLARADA: a massa sintetica atual contem um unico projeto
# (`PRJ-0442`, em 02_initial_data.sql). Nao existe um segundo projeto para
# comparar, e `comparacao_entre_projetos` foi explicitamente adiada para a
# Sprint 5 pela Secao 6.4.1 do `GestaoProjeto.md`.
#
# Estes prompts continuam na medicao porque a Secao 9.2.4 exige 25% de
# comparacoes, mas o que eles medem e a latencia do caminho que trata o pedido
# de comparacao — hoje, uma limitacao declarada — e nao a latencia de uma
# comparacao efetivamente produzida. O relatorio da rodada precisa repetir essa
# ressalva; um P95 comparativo confortavel aqui NAO demonstra que o requisito
# foi atendido para comparacoes reais.
COMPARACOES: tuple[str, ...] = (
    "Compare o avanco fisico do PRJ-0442 com o do PRJ-0518.",
    "Entre o PRJ-0442 e o PRJ-0518, qual esta mais proximo do prazo planejado?",
    "Quero comparar os riscos do PRJ-0442 com os riscos do PRJ-0518.",
    "Compare o custo previsto dos projetos PRJ-0442 e PRJ-0518.",
)

#: Todos os prompts da rodada, usados no aquecimento exigido pela Secao 9.2.4
#: ("aquecer uma vez cada prompt" antes de medir).
TODOS_OS_PROMPTS: tuple[str, ...] = CONSULTAS_SIMPLES + COMPARACOES
