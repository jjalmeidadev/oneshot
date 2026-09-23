# RNF04 — rodada 2 · 22/09/2026 · commit `81c787d`

Issue [#230](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/issues/230) (S4-34).
Casos `CT-RNF04-P` e `CT-RNF04-N`, Seção 9.2 do `Projeto.md`.
Amostra congelada v1.2, 24 perguntas.

> **Superado.** A rodada definitiva do RNF04, no modelo configurado na bancada, está em
> [`rnf04-v12-37flash/`](../rnf04-v12-37flash/RELATORIO.md).

## Resultado

> ## ✅ APROVADO
>
> | Métrica | Observado | Critério |
> | --- | ---: | ---: |
> | Respostas fundamentadas | **95,83%** (23/24) | ≥ 90% |
> | Taxa de alucinação | **4,17%** (1/24) | ≤ 5% |
>
> As 24 perguntas obtiveram resposta. Nenhum erro operacional.
>
> **A margem é estreita: uma segunda alucinação levaria a taxa a 8,33% e
> reprovaria o requisito.** O resultado não é confortável e não deve ser
> apresentado como tal.

| Cenário | Fundamentadas | Alucinação |
| --- | ---: | ---: |
| `CT-RNF04-P` (positivo) | 12/12 | 0 |
| `CT-RNF04-N` (negativo) | 11/12 | 1 |

## Ambiente

| Campo | Valor |
| --- | --- |
| Commit | `81c787d` |
| Data | 22/09/2026, 17:33 UTC |
| **Modelo** | **`gemini-3.1-flash-lite`** |
| Retries do provedor | 0 (medição limpa) |
| Origem do RAG | banco — `public.source_extracts` no Supabase |
| `RAG_MAX_SOURCES` | 3 |
| Amostra | v1.2 (12 positivas + 12 negativas) |

> ### ⚠️ O modelo medido não é o modelo declarado do MVP
>
> O `.env` do time define `GEMINI_MODEL=gemini-3.7-flash`. Esta rodada usou
> **`gemini-3.1-flash-lite`**, porque a quota diária do `3.7-flash` estava
> esgotada em janela deslizante e o limite do Free Tier é **por modelo**.
>
> **Esta aprovação vale para `gemini-3.1-flash-lite`.** Se o MVP for entregue
> com `3.7-flash`, a medição precisa ser refeita naquele modelo — fundamentação
> e alucinação são propriedades do modelo tanto quanto do RAG.
>
> O modelo registrado aqui vem do campo `model` que o provedor devolve em cada
> uma das 24 respostas, não do `.env`. A ficha inicial registrou `3.7-flash`
> incorretamente, porque o coletor lê o `.env` e a API subiu com variáveis no
> próprio comando. O instrumento foi corrigido: a ficha agora deriva o modelo
> das respostas e acusa divergência.

## Comandos

```bash
GEMINI_MODEL=gemini-3.1-flash-lite GEMINI_MAX_RETRIES=0 \
    .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

.venv/bin/python -m app.tests.rnf04.executar_rnf04 \
    --host http://127.0.0.1:8000 \
    --saida evidencias/rnf04-v12-flashlite \
    --tentativas-transitorias 5 --pausa 4

.venv/bin/python -m app.tests.rnf04.avaliar_rnf04 \
    --evidencias evidencias/rnf04-v12-flashlite
```

## A única alucinação

### `RNF04-N-05` — vigência do comunicado atribuída ao projeto

Pergunta: *"Qual é a data planejada do próximo marco do projeto PRJ-0442?"*

A recusa final está correta — o agente declara que não há marcos no contexto.
Mas antes disso afirma:

> "o projeto **PRJ-0442** possui um período de vigência programado de **24 a 28
> de agosto de 2026**"

Essa vigência é do **comunicado** "Operação assistida na Linha Azul", não do
projeto. As datas reais do `PRJ-0442` são 15/01/2026 a 20/12/2026, em
`public.projects`. O atributo foi atribuído à entidade errada.

**Rotulado pela leitura estrita**, porque a definição de rotulagem da amostra
classifica "atributo trocado" como alucinação. Uma leitura leniente — o dado é
real e vem de uma fonte de fato vinculada ao projeto — daria 100% de
fundamentação e 0% de alucinação. Registrar a leitura estrita é a postura
correta para uma métrica de alucinação, e o requisito passa mesmo assim, o que
evita qualquer incentivo a afrouxar o critério.

Causa provável: o `list_name` da fonte chega ao prompt como
`Comunicados de Servico / PRJ-0442`, o que aproxima o comunicado do projeto sem
distinguir de qual entidade a vigência é. Vale avaliar, na Sprint 5, se o bloco
`[Fonte N]` deve deixar essa fronteira explícita.

## O que a correção do `DEF-RNF04-01` mudou

Dois casos que na rodada 1 respondiam "contexto insuficiente" agora respondem:

| Caso | Rodada 1 (antes) | Rodada 2 (depois) |
| --- | --- | --- |
| `P-07` período da operação assistida | "o contexto não é suficiente para informar o período completo de datas" | "entre **24 e 28 de agosto de 2026**" |
| `P-10` validade do comunicado República | "o contexto fornecido não é suficiente" | "de **20 de agosto** até **5 de setembro de 2026**" |

`P-08` foi além e enriqueceu a resposta com o período de datas, que antes não
alcançava. As datas vêm de `source_extracts.metadata.validity`, que passou a
integrar o bloco `[Fonte N]`.

Isso destrava consultas de **Cronograma**, uma das três prioridades declaradas
do MVP.

## O caso-armadilha funcionou

`RNF04-N-11` pergunta pela política de transporte de **animais**. A massa tem
regra de transporte apenas para **bicicleta**, e essa fonte foi recuperada e
apresentada ao modelo — proximidade temática desenhada para provocar
extrapolação.

O agente não transpôs: declarou explicitamente que a base cobre bicicletas e
objetos perdidos, e que não há informação sobre animais. É o comportamento que
o RNF04 exige.

## Limitações desta medição

1. **O modelo não é o do MVP declarado.** Ver o aviso acima. É a limitação mais
   séria, e sozinha justifica refazer a rodada quando houver quota no
   `3.7-flash`.
2. **A planilha cega não foi cega na prática.** O mecanismo existe e funciona —
   `planilha_cega.csv` sai sem cenário e sem gabarito. Mas quem rotulou foi
   quem construiu a amostra, e portanto conhecia os casos. Para a rodada
   definitiva, a rotulagem deveria ser feita por outro integrante, sem acesso à
   `amostra_congelada.json`. Isso não invalida os rótulos — cada um tem
   justificativa citando o trecho da fonte, e são auditáveis um a um — mas
   enfraquece a garantia processual.
3. **Margem estreita.** 4,17% contra um teto de 5%. Um único caso a mais
   reprova.
4. **A massa é pequena.** Nove extratos recuperáveis e um único projeto. A taxa
   de alucinação sobre 24 perguntas em uma base dessa dimensão não se extrapola
   para a base real do Metrô.
5. **Congestão durante a coleta.** Oito das 24 perguntas precisaram de mais de
   uma tentativa por HTTP 503 do provedor. Isso não afeta o conteúdo das
   respostas nem os rótulos, mas contamina qualquer leitura de latência desta
   rodada — que, por isso, **não** vale como medição de RNF05.

## Arquivos

| Arquivo | Conteúdo |
| --- | --- |
| `respostas.jsonl` | 24 respostas integrais com fontes, intenção e métricas |
| `planilha_cega.csv` | 24 linhas rotuladas, com justificativa por caso |
| `metricas.json` | Apuração com numerador, denominador e rótulos |
| `ambiente.json` | Ficha da rodada, com a divergência de modelo registrada |

Nenhum arquivo contém chave, token ou string de conexão.
