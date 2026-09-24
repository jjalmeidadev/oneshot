# RNF05 — desempenho

Cenário de carga do teste obrigatório de desempenho, planejado na Seção 9.2.4 do
[`Projeto.md`](../../../../../docs/Projeto.md).

| Arquivo | Papel |
| --- | --- |
| `locustfile.py` | Cenário exigido nominalmente pela Seção 9.2.4. 75% consultas simples, 25% comparações, espera de 1 a 3 s |
| `aquecer.py` | Aquecimento de cada prompt, executado **antes** da medição e fora da janela do Locust |
| `prompts.py` | Massa de prompts congelada, extraída da massa sintética versionada |
| `api_com_atraso.py` | Duplo do `CT-RNF05-N`: injeta atraso acima do teto só na rota de comparação |
| `registrar_ambiente.py` | Ficha de CPU, memória, SO, Python, commit e configuração, exigida antes de medir |
| `apurar_rnf05.py` | Aplica o protocolo revisado aos CSVs: erros, amostra mínima de 40 por tipo de consulta e tetos do P95 |

## Critério

| Rota | Teto do P95 |
| --- | ---: |
| Consulta simples | 10 s |
| Comparação | 20 s |

Aprovação exige, **nas duas rodadas**: zero erro HTTP ou de contrato, P95 simples
≤ 10 s e P95 comparativo ≤ 20 s. A partir da 2ª rodada, cada tipo de consulta precisa de **ao menos 40 amostras** por
rodada; abaixo disso a rodada é inconclusiva e deve ser estendida. Com menos de 21
amostras, o P95 calculado pelo Locust coincide com a pior requisição. Média, mediana, P90, P99 e RPS são registrados
para diagnóstico e **não substituem o P95**.

## Execução

```bash
# 1. Ficha do ambiente ANTES de medir
.venv/bin/python -m app.tests.performance.registrar_ambiente \
    --rodada baseline --cache quente --saida evidencias/rnf05-baseline

# 2. Reiniciar a API e aquecer, FORA da janela de medição
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
.venv/bin/python -m app.tests.performance.aquecer --host http://127.0.0.1:8000

# 3. Positiva 1 — linha de base, 1 usuário
locust -f app/tests/performance/locustfile.py --host http://127.0.0.1:8000 \
    --headless -u 1 -r 1 -t 5m --csv evidencias/rnf05-baseline

# 4. Positiva 2 — carga, 5 usuários
locust -f app/tests/performance/locustfile.py --host http://127.0.0.1:8000 \
    --headless -u 5 -r 1 -t 5m --csv evidencias/rnf05-carga

# 5. Negativa — instância com atraso, em porta separada
.venv/bin/python -m uvicorn app.tests.performance.api_com_atraso:app \
    --host 127.0.0.1 --port 8001
RNF05_SO_COMPARACAO=1 locust -f app/tests/performance/locustfile.py \
    --host http://127.0.0.1:8001 --headless -u 1 -r 1 -t 3m \
    --csv evidencias/rnf05-violacao
```

A partir de `src/backend`, com `PYTHONPATH=.` se o Locust não encontrar o pacote
`app`. A campanha inteira, RNF04 incluído, roda em um comando com
`bash app/tests/executar_rodada_rnf.sh`.

A rodada negativa usa `RNF05_SO_COMPARACAO=1`. O atraso só existe na rota de
comparação, que a mistura normal sorteia em 1 de cada 4 tarefas; sem a variável,
uma rodada curta pode não sortear nenhuma comparação e o cenário não prova nada.

## Cache frio e cache quente

São rodadas **diferentes** e nunca se misturam no mesmo resultado.

- **quente**: reiniciar a API, rodar `aquecer.py` e só então o Locust;
- **frio**: reiniciar a API e rodar o Locust direto, sem `aquecer.py`.

O aquecimento **não** fica dentro do `locustfile`. O relógio do `-t` do Locust
corre durante o `test_start`: com o aquecimento lá dentro, as rodadas "de 5
minutos" mediam cerca de 3 min 40 s, e a rodada negativa, que aquecia a instância
com atraso de 25 s, não chegou a medir nenhuma requisição.

O backend não tem cache de respostas nesta versão; o módulo VHS/cache ainda
está em desenvolvimento. "Quente" aqui significa pool de conexões aberto e
classificador carregado, não resposta reaproveitada.

A modalidade usada vai para a ficha do ambiente, em `--cache`.

## O cenário negativo precisa reprovar

`api_com_atraso.py` injeta 25 s (configurável em `RNF05_ATRASO_SEGUNDOS`) apenas
nos pedidos de comparação, acima do teto de 20 s. As consultas simples seguem
intactas, como a Seção 9.2.3 exige.

**Se o relatório da rodada negativa permanecer aprovado, o próprio teste de
desempenho está incorreto** — e, nesse caso, a rodada positiva também não vale
nada, porque a medição não enxerga violação.

O atraso vive em código de teste. Nenhuma linha de `app/` de produção é alterada
para produzir a violação.

## Ressalva do cenário comparativo

A massa tem **um único projeto** (`PRJ-0442`) e `comparacao_entre_projetos` foi
adiada para a Sprint 5. Os 25% de prompts comparativos medem a latência da
recusa, não a de uma comparação produzida. A ressalva completa está no cabeçalho
de `prompts.py` e precisa acompanhar qualquer P95 comparativo publicado.

## Estado

**Atendido na 3ª rodada, em 22 e 23/09/2026.** No `gemini-3.7-flash` em plano
pago, as quatro janelas positivas — 1 e 5 usuários, com cache quente e com cache
frio — terminaram sem erro, com P95 simples de 7,0 a 7,6 s e comparativo de 7,4 a
8,4 s. O cenário negativo foi validado. A 1ª rodada (uma requisição de 37,7 s numa
rota com 10 amostras) e a 2ª (um erro e P95 simples de 11,0 s sob carga)
continuam registradas como não atendidas. O P95 comparativo carrega a ressalva
da seção anterior.

As rodadas usam provedor pago. O Free Tier, usado na bancada para não gerar
custo, tem piso de 14,7 s a 37,7 s por chamada trivial, medido em controle
separado, e não serve como referência de desempenho do sistema.

Relatório: [`evidencias/rnf05-rodada3/RELATORIO.md`](../../../evidencias/rnf05-rodada3/RELATORIO.md).
Índice de todas as rodadas: [`evidencias/README.md`](../../../evidencias/README.md).
