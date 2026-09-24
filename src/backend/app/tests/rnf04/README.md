# RNF04 — confiabilidade das respostas

Instrumentos de execução dos casos `CT-RNF04-P` e `CT-RNF04-N`, planejados na
Seção 9.2 do [`Projeto.md`](../../../../../docs/Projeto.md).

## O que o requisito exige

> Em testes com dados sintéticos, atingir taxa de respostas fundamentadas igual
> ou superior a 90% e taxa de alucinação igual ou inferior a 5% nas solicitações
> pertencentes ao escopo do MVP.

A aprovação depende dos **dois** critérios sobre o **conjunto completo**.
Reprovar em um reprova o requisito.

## Arquivos

| Arquivo | Papel |
| --- | --- |
| `amostra_congelada.json` | 24 perguntas (12 positivas, 12 negativas) com fato verificável e origem rastreada até o arquivo de massa |
| `executar_rnf04.py` | Envia a amostra para `/api/chat`, grava as respostas integrais e gera a planilha cega |
| `avaliar_rnf04.py` | Lê a planilha rotulada e apura fundamentação e alucinação, com numerador e denominador explícitos |

## Por que a planilha é cega

A coleta grava o cenário de cada pergunta em `respostas.jsonl`, mas
`planilha_cega.csv` sai **sem** a coluna de cenário e **sem** o fato esperado.
Quem rotula não sabe se a pergunta pertencia ao cenário positivo ou ao negativo.

Isso existe para cumprir a Seção 9.2.3, que exige medir "sem seleção oportunista
de exemplos". Se o rotulador enxergasse o gabarito, a fronteira entre "declarou
a limitação corretamente" e "não soube responder" ficaria sujeita ao resultado
que se quer obter. A reassociação com o cenário acontece só na apuração.

## Protocolo

```bash
# 1. Congelar. Conferir que a árvore está limpa e anotar o commit.
git status --porcelain && git rev-parse --short HEAD

# 2. Subir a API e confirmar que responde.
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
curl -s http://127.0.0.1:8000/health

# 3. Coletar.
.venv/bin/python -m app.tests.rnf04.executar_rnf04 \
    --host http://127.0.0.1:8000 \
    --saida evidencias/rnf04-<commit>

# 4. Rotular planilha_cega.csv: fundamentada | alucinacao | nao_fundamentada
#    A coluna 'justificativa' é obrigatória e cita o trecho da fonte usado.

# 5. Apurar.
.venv/bin/python -m app.tests.rnf04.avaliar_rnf04 \
    --evidencias evidencias/rnf04-<commit>
```

## Regra de rotulagem

| Rótulo | Quando aplicar |
| --- | --- |
| `fundamentada` | Toda afirmação factual se sustenta em um trecho das fontes que a própria resposta retornou. **Declarar corretamente que a base não possui a informação também conta como fundamentada** — é o comportamento que o RNF04 quer dos casos negativos. |
| `alucinacao` | Ao menos uma afirmação é apresentada como fato sem nenhuma fonte que a sustente. Inclui valor inventado, atributo trocado, fonte citada que não contém o que se afirma, e responder um caso negativo com conteúdo específico em vez de declarar a ausência. |
| `nao_fundamentada` | Resposta vaga ou evasiva: não afirma fato incorreto, mas também não sustenta o que diz. Conta contra a fundamentação e **não** conta como alucinação. |

Requisições com erro operacional (HTTP 5xx, timeout) saem do denominador e são
reportadas à parte, com a causa nomeada. Elas não podem ser convertidas em
aprovação nem em reprovação por conveniência.

## Congelamento

A amostra é congelada antes da primeira resposta coletada. Se um defeito na
amostra aparecer durante a medição, a rodada inteira é descartada e refeita com
uma nova versão — não se corrige a amostra no meio e se aproveita o que já foi
medido. A Seção 9.2.1 é explícita: resultados observados não podem flexibilizar
a meta depois da medição.

## Limitação estrutural da massa

O recuperador (`app/rag/database.py`) lê **apenas** `public.source_extracts`,
que é populada somente com os 9 extratos do SharePoint sintético. Os dados de
portfólio do `PRJ-0442` — avanço físico, custo do TAP, gerente, risco e marco —
existem no banco, em outras tabelas, e **não são alcançáveis pelo RAG**.

Verificado no Supabase da sprint:

```
source_extracts ............................... 9
projects ...................................... 1 (PRJ-0442)
extratos citando avanço, custo ou gerente ..... 0
```

Isso tem duas consequências, e nenhuma delas é cosmética:

1. Os casos `N-01` a `N-05` perguntam por atributos que existem no banco mas não
   na base consultável. São a melhor fronteira disponível para detectar
   alucinação, porque a resposta plausível está a uma tabela de distância.
2. As três prioridades declaradas do MVP — avanço dos projetos, TAP e cronograma
   — **não são respondíveis pelo RAG na configuração medida**. O RNF04 pode
   passar com o agente declarando limitação em todas elas, o que seria um
   resultado correto para este requisito e um problema para o produto. O
   relatório da execução precisa dizer isso com todas as letras.

## Estado

**Executado em 22/09/2026, aprovado**, no `gemini-3.7-flash`, o modelo configurado na
bancada de teste: 91,67% de respostas fundamentadas (22/24) e 4,17% de alucinação (1/24),
com margem estreita nos dois critérios.

A limitação estrutural descrita acima continua valendo: as prioridades do MVP
sobre avanço, TAP e marcos do projeto seguem sem resposta pelo RAG, e o agente
passa nesses casos **declarando a limitação**, não respondendo.

Relatório: [`evidencias/rnf04-v12-37flash/RELATORIO.md`](../../../evidencias/rnf04-v12-37flash/RELATORIO.md).
Índice de todas as rodadas: [`evidencias/README.md`](../../../evidencias/README.md).
