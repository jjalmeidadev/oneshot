# RNF05 — rodada definitiva · 22/09/2026

Issue [#231](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/231) (S4-35).
Casos `CT-RNF05-P` e `CT-RNF05-N`, Seção 9.2.4 do `Projeto.md`.
**No modelo da bancada de teste (`gemini-3.7-flash`)**, em plano pago.

> A 2ª rodada, com o protocolo revisado e congelado antes da execução, está em
> [`rnf05-rodada2/`](../rnf05-rodada2/RELATORIO.md).

## Resultado

> ## ❌ REPROVADO — por uma única requisição
>
> | Rodada | Rota | Reqs | Falhas | P95 | Teto | |
> | --- | --- | ---: | ---: | ---: | ---: | :---: |
> | 1 usuário, 5 min | simples | 24 | 0 | 6.600 ms | 10.000 | ✅ |
> | 1 usuário, 5 min | **comparação** | **10** | 0 | **38.000 ms** | **20.000** | **❌** |
> | 5 usuários, 5 min | simples | 165 | 0 | 7.100 ms | 10.000 | ✅ |
> | 5 usuários, 5 min | comparação | 43 | 0 | 8.000 ms | 20.000 | ✅ |
>
> O critério exige as duas rodadas aprovadas. A linha de base reprova na rota
> de comparação, e **uma única requisição** decide o resultado. Das 242
> requisições das duas rodadas, 241 ficaram abaixo de 8,2 s e uma levou 37,7 s.
> Com só 10 amostras de comparação na linha de base, o P95 dessa rota é
> praticamente a pior amostra.
>
> `CT-RNF05-N` foi **validado**: a medição detecta a violação injetada.

## Ambiente

| Campo | Valor |
| --- | --- |
| Data | 22/09/2026, 19:19 a 19:32 UTC |
| Modelo | `google/gemini-3.7-flash`, o mesmo configurado na bancada |
| Caminho | OpenRouter, tier pago |
| Retries do provedor | 3, padrão de produção |
| Timeout por chamada ao provedor | 30 s, padrão de produção |
| Pool de conexões com o banco | ligado |
| Aquecimento | 14 prompts, **antes** da janela de medição, todos HTTP 200 |
| Máquina | Apple M5 Pro, 18 núcleos, 48 GB, macOS (Darwin 25.6) |
| Código medido | hash `c2cb357a…`, manifesto em [`campanha-37flash/arvore-medida.md`](../campanha-37flash/arvore-medida.md) |

## A requisição de 37,7 s

A 6ª requisição da linha de base, a 1 min 19 s do início, levou 37.702 ms. O
máximo acumulado da rodada não mudou depois disso. Nenhuma outra requisição das
duas rodadas passou de 8,2 s.

**Explicação mais provável:** travamento do provedor. O valor bate quase
exatamente com a configuração de produção:

```
30.000 ms   timeout da primeira chamada (GEMINI_REQUEST_TIMEOUT_SECONDS=30)
 2.000 ms   espera antes da nova tentativa (GEMINI_RETRY_BASE_DELAY_SECONDS=2)
~5.700 ms   segunda chamada, bem-sucedida (compatível com as demais)
─────────
~37.700 ms
```

**Isso não está provado.** O cliente não registrava novas tentativas em log no
momento da rodada, então não há rastro do timeout. A conclusão é aritmética, não
observacional. O registro foi adicionado depois da rodada (ver "Correções
aplicadas"), e o mesmo evento, se repetir, fica visível.

## Alternativas descartadas para aprovar a rodada

**Baixar o timeout do provedor de 30 s para ~10 s** faria um travamento custar
cerca de 17 s em vez de 37 s, e provavelmente aprovaria a rodada. **Não foi
feito**, porque a bancada de teste roda no Gemini Free Tier, em que uma chamada
trivial mediu **de 14,7 s a 37,7 s**. Com timeout de 10 s, **praticamente toda
requisição da bancada falharia**. Seria fazer o teste passar quebrando a
bancada que a equipe usa para desenvolver e demonstrar o sistema.

**Repetir a linha de base até sair sem outlier** também não foi feito. A
Seção 9.2.1 proíbe ajustar a medição ao resultado, e trocar uma rodada reprovada
por outra aprovada, sem mudança no produto, é exatamente isso.

## Onde o tempo é gasto, e o que foi corrigido

A decomposição das requisições do RNF04, feitas em sequência, expôs um gargalo
que não era o LLM:

| Etapa | Antes | Leitura |
| --- | ---: | --- |
| Chamada ao LLM | 2.959 ms | mediana |
| Recuperação RAG | 1.184 ms | mediana |
| **Resto, sem explicação** | **2.717 ms** | mediana |

O "resto" era **conexão com o banco**. Cada requisição abria duas conexões novas
com o Supabase, uma para o RAG e outra para a rastreabilidade do RNF03, e o
handshake com o servidor nos EUA custa ~1 s cada.

**Corrigido com pool de conexões** (`app/database/connection.py`):

| Acesso ao banco | Mediana |
| --- | ---: |
| Sem pool (conexão nova) | 1.209 ms |
| **Com pool** | **599 ms** |

**~1,2 s a menos por requisição.** O ganho não depende do provedor de LLM,
porque o acesso ao banco é o mesmo com qualquer um.

Os ~600 ms que sobram por acesso são quatro idas e voltas (verificação da
conexão, BEGIN, consulta, ROLLBACK). Dá para reduzir tirando a transação, mas a
rastreabilidade do RNF03 grava várias linhas que precisam ser atômicas. Não
vale arriscar auditoria pela metade para ganhar ~300 ms.

## `CT-RNF05-P` — rodadas positivas

Protocolo da Seção 9.2.4: reiniciar a API, aquecer cada prompt uma vez **fora**
da janela e medir.

```bash
LLM_PROVIDER=openrouter .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
.venv/bin/python -m app.tests.performance.aquecer --host http://127.0.0.1:8000

locust -f app/tests/performance/locustfile.py --host http://127.0.0.1:8000 \
    --headless -u 1 -r 1 -t 5m --csv evidencias/rnf05-37flash/baseline/rnf05-baseline
locust -f app/tests/performance/locustfile.py --host http://127.0.0.1:8000 \
    --headless -u 5 -r 1 -t 5m --csv evidencias/rnf05-37flash/carga/rnf05-carga
```

| Rodada | Rota | Média | Mediana | P90 | P95 | P99 | Máx. | RPS |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 usuário | simples | 5.245 | 5.200 | 6.300 | 6.600 | 6.900 | 6.928 | 0,08 |
| 1 usuário | comparação | 9.679 | 7.100 | 38.000 | 38.000 | 38.000 | 37.702 | 0,03 |
| 5 usuários | simples | 4.765 | 4.900 | 6.600 | 7.100 | 7.700 | 7.764 | 0,55 |
| 5 usuários | comparação | 6.342 | 6.500 | 7.500 | 8.000 | 8.200 | 8.157 | 0,14 |

Valores em ms. Média, mediana, P90, P99 e RPS são diagnóstico; o critério é o P95.

## `CT-RNF05-N` — cenário negativo: ✅ validado

Instância com 25 s de atraso injetado na rota de comparação, em código de teste
(`api_com_atraso.py`), sem tocar em `app/`.

```bash
LLM_PROVIDER=openrouter .venv/bin/python -m uvicorn \
    app.tests.performance.api_com_atraso:app --host 127.0.0.1 --port 8001
RNF05_SO_COMPARACAO=1 locust -f app/tests/performance/locustfile.py \
    --host http://127.0.0.1:8001 --headless -u 1 -r 1 -t 3m \
    --csv evidencias/rnf05-37flash/violacao/rnf05-violacao
```

P95 comparativo de **32.000 ms**, contra o teto de 20 s. A rodada **reprova**,
que é exatamente o que dela se exige: a medição enxerga a violação.

> **Defeito do duplo, encontrado nesta rodada.** O duplo reconhecia comparação
> por palavra-chave ("compare", "comparar") e deixava passar um dos quatro
> prompts: *"Entre o PRJ-0442 e o PRJ-0518, qual está mais próximo do prazo?"*.
> Verificado prompt a prompt: três levaram ~30 s e esse levou 6 s. Nesta rodada
> o sorteio caiu nele na maioria das vezes, por isso a mediana ficou em 7,1 s.
>
> A conclusão se mantém, porque a rodada reprovou e a violação foi detectada.
> O duplo foi corrigido depois para comparar com a lista exata da massa
> congelada. **A rodada não foi refeita**: refazer não mudaria a conclusão.

## Rodadas descartadas

Uma primeira execução da campanha foi descartada antes de qualquer apuração: o
aquecimento rodava dentro da janela cronometrada do Locust. As rodadas "de 5
minutos" mediram ~3 min 40 s, e a negativa não chegou a medir nenhuma
requisição. Os números estão publicados em
[`descartada-aquecimento-na-janela/`](descartada-aquecimento-na-janela/LEIA.md).

Por transparência: as duas rodadas positivas descartadas **tinham sido
aprovadas** (P95 comparativo de 7,9 s e 7,4 s). Foram descartadas por não
cumprirem a duração declarada, não pelo resultado. A rodada válida, que cumpriu o
protocolo, reprovou.

## Provedor da bancada e provedor de produção

A bancada de teste usa o Gemini no Free Tier para não gerar custo. Esse
provedor tem piso de 14,7 s a 37,7 s por chamada trivial, medido em controle
separado ([`rnf05-baseline-flashlite/`](../rnf05-baseline-flashlite/RELATORIO.md)),
e por isso as rodadas deste relatório foram medidas com o mesmo modelo em plano
pago. No ambiente do Metrô, o agente usará o Copilot Studio com modelos GPT.

O que os dados sustentam:

- **com provedor pago**, a carga de 5 usuários foi aprovada e 241 de 242
  requisições ficaram abaixo de 8,2 s; a linha de base reprovou por um único
  evento, provavelmente do provedor, numa rota com 10 amostras;
- **o piso do Free Tier é da bancada, não do produto**: ele reflete uma escolha
  de custo para desenvolvimento e testes;
- **no ambiente de produção**, com outro modelo e outro provedor, a latência
  depende do que o Metrô adotar e é medida na homologação.

## Correções aplicadas depois das rodadas

Nenhuma delas altera o resultado registrado acima. Todas estão cobertas por
`app/tests/test_instrumentacao_rnf05.py`.

| Correção | Motivo |
| --- | --- |
| Registro em log de cada nova tentativa contra o provedor | Permite confirmar se um outlier foi timeout seguido de nova tentativa |
| Aviso em log quando o OpenRouter corta a resposta por limite de tokens | Ver `DEF-RNF04-02` no relatório do RNF04 |
| Duplo do cenário negativo compara com a lista exata de prompts | Deixava passar um dos quatro prompts de comparação |

## Recomendações para a Sprint 5

1. **Medir a latência no provedor de produção.** O Free Tier da bancada não é
   referência de desempenho do produto; a medição que vale para o Metrô é a do
   Copilot Studio com modelos GPT, no ambiente homologado.
2. ~~Aumentar a amostra de comparações da linha de base.~~ **Decidido em
   22/09/2026**: o protocolo passa a exigir ao menos 40 amostras por tipo de
   consulta, e a linha de base passa a durar 25 minutos. Os tetos de 10 s e 20 s
   foram **mantidos**. Registro em `Projeto.md`, Seções 3.2.2 e 9.2.4, e regra
   aplicada por `app/tests/performance/apurar_rnf05.py`.

   A revisão vale só a partir da 2ª rodada. Aplicada aos CSVs desta rodada,
   apenas para conferir a leitura, ela não aprovaria a Sprint 4: a linha de base
   ficaria **inconclusiva**, porque também as consultas simples (24 amostras)
   ficam abaixo do mínimo. O resultado registrado continua **não atendido**.
3. **Timeout adaptado ao provedor.** 30 s faz sentido no Free Tier; em tier pago,
   em que a chamada leva ~3 s, é um teto que só serve para amplificar
   travamentos.

## Ressalva do cenário comparativo

A massa tem **um único projeto** (`PRJ-0442`), e `comparacao_entre_projetos` foi
adiada para a Sprint 5. As requisições de comparação medem a latência da
**recusa**, não a de uma comparação produzida.

## Arquivos

| Caminho | Conteúdo |
| --- | --- |
| `aquecimento.log` | Os 14 prompts de aquecimento, todos HTTP 200 |
| `baseline/`, `carga/`, `violacao/` | Ficha de ambiente, CSVs do Locust e log de cada rodada |
| `descartada-aquecimento-na-janela/` | Primeira execução, descartada, com o motivo |
