# Backend

Contrato de fontes, citações por afirmação, períodos e correlação da auditoria:
[Referências nas respostas](../../docs/contrato-referencias.md).

API FastAPI do projeto, com chat via Gemini e recuperacao de contexto em listas simuladas do SharePoint.

## Configuracao

Crie `src/backend/.env` a partir de `.env.example` e informe uma chave do
Google AI Studio em `GEMINI_API_KEY`. A chave e utilizada somente pelo backend.

Por padrao, as respostas usam nivel de raciocinio `low` e ate 512 tokens para
reduzir a latencia. Falhas transitorias sao repetidas ate tres vezes, com esperas
de 2, 4 e 8 segundos. Esses valores podem ser ajustados em `.env` por meio de
`GEMINI_THINKING_LEVEL`, `GEMINI_MAX_OUTPUT_TOKENS`, `GEMINI_MAX_RETRIES`,
`GEMINI_RETRY_BASE_DELAY_SECONDS` e `GEMINI_REQUEST_TIMEOUT_SECONDS`.

O benchmark isolado da hipótese de economia de tokens usa OpenRouter sem trocar
o provedor do backend. Configure `OPENROUTER_API_KEY` somente no mesmo `.env` e
consulte o [protocolo e as evidências](../../docs/evidencias/sprint-04/hipotese-tokens/README.md).

Para validar a conectividade com o banco Supabase/PostgreSQL do projeto Oneshot,
configure `DATABASE_URL` ou `SUPABASE_DATABASE_URL` em `src/backend/.env`. A URL
deve vir do painel **Connect** do Supabase e manter credenciais apenas no ambiente
local. Em producao, prefira conexao direta ou pooler de sessao para backend
persistente e inclua `sslmode=require`.

Com a URL do banco configurada, o RAG consulta `source_extracts` e
`project_artifacts`, usando `projects` quando houver vinculo. A busca considera
texto da pergunta, macro/intencao especifica e entidades extraidas pelo PLN,
especialmente projeto ou linha. Sem URL de banco, o backend preserva o fallback
local nos JSONs simulados de `app/rag/data/sharepoint`.

Quando uma consulta classificada como `CONSULTA` nao recupera fontes suficientes,
a API responde explicitamente que nao encontrou contexto seguro, sem inventar
informacao.

Para transcrever audio, configure tambem o recurso Azure AI Speech homologado
para o ambiente. O portal Azure exibe o nome do recurso e, em alguns casos, um
endpoint regional no formato `https://<regiao>.api.cognitive.microsoft.com/`; a
aplicacao aceita esse valor em `AZURE_SPEECH_ENDPOINT` e o normaliza para o host
de STT usado pela API de audio curto.

| Variavel | Uso |
| --- | --- |
| `AZURE_SPEECH_RESOURCE` | Nome do recurso Speech, usado para montar `https://<recurso>.cognitiveservices.azure.com` quando nao ha endpoint explicito. |
| `AZURE_SPEECH_ENDPOINT` | Endpoint opcional exibido no portal; aceita `*.api.cognitive.microsoft.com`, `*.stt.speech.microsoft.com` ou `*.cognitiveservices.azure.com`. |
| `AZURE_SPEECH_KEY` | Chave do recurso Azure AI Speech, mantida somente no `.env` local. |
| `AZURE_SPEECH_TIMEOUT_SECONDS` | Tempo maximo da chamada ao provedor, padrao 6 s; o backend limita o valor entre 1 e 120 segundos. |
| `AZURE_SPEECH_MAX_ATTEMPTS` | Tentativas totais em falha transitoria, padrao 2; o backend limita entre 1 e 5. |
| `DATABASE_URL` | String PostgreSQL principal para o Supabase/PostgreSQL, com SSL exigido quando aplicavel. |
| `SUPABASE_DATABASE_URL` | Alias aceito quando o ambiente separa explicitamente a URL do Supabase. |

```powershell
cd src/backend
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

A API fica disponivel em `http://127.0.0.1:8000`. O frontend encaminha as
requisicoes de `/api` para esse endereco durante o desenvolvimento.

## API de audio

O endpoint `POST /api/audio` recebe o audio da solicitacao em `multipart/form-data`,
no campo `audio`. A validacao segue o contrato da Secao 8.7 do `docs/Projeto.md` e
acontece antes de qualquer chamada externa, para que um arquivo fora do contrato nao
consuma a franquia do provedor de transcricao.

| Restricao | Valor |
| --- | --- |
| Conteiner e codec | `WAV` com `PCM` ou `OGG` com `OPUS` |
| Taxa de amostragem | 16 kHz (no ramo Opus tambem 48 kHz, ver abaixo) |
| Canais | 1, mono |
| Profundidade | 16 bits |
| Duracao maxima | 60 segundos |
| Tamanho maximo | 2 MB |
| Requisicoes simultaneas por usuario | 1 |

Todo erro previsto usa o mesmo envelope, sem detalhe tecnico interno, conforme o RNF11.

## Smoke test de audio com banco real

Com `DATABASE_URL` ou `SUPABASE_DATABASE_URL` configurada, execute a partir de
`src/backend`:

```powershell
.venv\Scripts\python.exe -m scripts.verify_audio_stt_pln_real_db
```

O script atravessa `POST /api/audio`, STT controlado, PLN real e persistencia no
PostgreSQL/Supabase. Ele valida um caso positivo e uma falha controlada, confere
correlacao e auditoria e remove ao final todos os registros sinteticos criados.

Para validar a mesma cadeia com Azure STT real, forneca um WAV PCM de 16 kHz,
mono e 16 bits. O provedor gerador posterior fica controlado para isolar o
escopo audio -> STT -> PLN:

```powershell
.venv\Scripts\python.exe -m scripts.verify_audio_stt_pln_live `
  C:\caminho\amostra.wav --expected-term perfil --expected-term artrite
```

O verificador usa PLN e Supabase reais, confere transcricao, classificacao,
correlacao e auditoria e remove a conversa sintetica no bloco de limpeza. O
audio permanece local e nao e copiado para o repositorio.
O campo `detail` so aparece quando ha algo a informar:

```json
{
  "error": {
    "code": "AUDIO_FORMAT_UNSUPPORTED",
    "message": "Formato de audio nao suportado. Envie WAV/PCM ou OGG/OPUS a 16 kHz, mono.",
    "detail": { "received": "audio/mpeg" }
  }
}
```

| HTTP | `code` | Situacao |
| --- | --- | --- |
| `400` | `AUDIO_MISSING` | Campo `audio` ausente. |
| `400` | `AUDIO_FORMAT_UNSUPPORTED` | Conteiner, codec, taxa, canais ou profundidade fora do previsto. |
| `400` | `AUDIO_TOO_LONG` | Gravacao acima de 60 segundos. |
| `401` | `UNAUTHENTICATED` | Cabecalho `Authorization` ausente ou token invalido. |
| `413` | `AUDIO_TOO_LARGE` | Arquivo acima de 2 MB. |
| `422` | `NO_SPEECH_DETECTED` | Audio valido, porem sem sinal audivel. |
| `429` | `RATE_LIMITED` | Ja existe uma transcricao em andamento para o usuario. |
| `502` | `STT_PROVIDER_ERROR` | Falha na chamada ao servico de transcricao. |
| `503` | `STT_PROVIDER_UNAVAILABLE` | Servico de transcricao indisponivel. |

O `403 OUT_OF_SCOPE_FOR_PROFILE` da Secao 8.7.6 depende das regras de perfil em
`access_rules` e entra junto com a persistencia, em task separada.

### Identidade do usuario

A autenticacao **nao e feita por este backend**. Conforme a Secao 6.2.4 do
`docs/Projeto.md`, a identidade vem do **Microsoft Entra ID**: o agente vive
dentro do Teams e o canal entrega quem e a pessoa junto com a mensagem. A API
apenas valida o token recebido em `Authorization: Bearer <TOKEN>` e extrai o
identificador do usuario, no formato da coluna `users.entra_object_id`.

Enquanto o ambiente corporativo nao esta provisionado, o token do Entra e
substituido pelo mapa simulado `AUDIO_SIMULATED_IDENTITIES`, no formato
`<token>=<entra_object_id>` separado por virgula. Com a variavel vazia, o
cabecalho continua obrigatorio e o identificador e derivado do proprio token.

A autorizacao de dominio — qual subportfolio ou projeto cada perfil alcanca —
continua sendo da solucao, via `access_rules`: o Entra informa quem e a pessoa,
nao o que ela pode ver do portfolio. E o risco R04 da Secao 3.6.

**Taxa de amostragem no ramo Opus.** O Opus sempre decodifica a 48 kHz e o campo
`input_sample_rate` do `OpusHead` e informativo (RFC 7845). O `MediaRecorder` dos
navegadores grava declarando 48 kHz, entao exigir 16 kHz ali recusaria toda gravacao
vinda do frontend. O ramo Opus aceita `0`, `16000` e `48000`; o ramo WAV mantem a
exigencia estrita de 16 kHz da Secao 8.7.3.

O Speech-to-Text usa o Azure AI Speech para audio curto, em `pt-BR`, via
`app/audio/transcription.py`. Um audio aprovado na validacao recebe `200` com a
transcricao retornada pelo provedor. A transcrição segue para o pipeline compartilhado de classificação e resposta.
O campo `pipeline_status` é `"completed"` somente após a resposta; `chat` traz
o mesmo contrato de `POST /api/chat`, incluindo fontes completas e métricas.

**A chamada ao provedor e assincrona.** A rota de audio e `async def`, e um
cliente HTTP sincrono dentro dela bloquearia o laco de eventos: enquanto o
Azure nao respondesse, nenhuma outra requisicao seria atendida — nem `/health`,
nem `/api/chat`, nem outro upload.

Os limites acompanham o orcamento do RNF05, que da 10 segundos para uma
consulta simples ponta a ponta e do qual a transcricao e apenas a primeira
etapa: 6 segundos de espera e ate duas tentativas, com meio segundo entre elas.

O cliente HTTP e criado uma vez por requisicao, de modo que a retentativa
reaproveite a conexao ja estabelecida. Compartilha-lo entre requisicoes
diferentes daria mais um ganho, mas exige fecha-lo no encerramento da
aplicacao, e por isso cabe ao ciclo de vida do FastAPI, junto da integracao do
pipeline com a API.

As falhas do provedor sao traduzidas para os codigos da Secao 8.7.6:

| Situacao no Azure | Resposta |
| --- | --- |
| `429`, franquia ou concorrencia excedida | `429 RATE_LIMITED`, sem repetir a chamada |
| `408`, `500`, `502`, `503`, `504` | `503 STT_PROVIDER_UNAVAILABLE`, apos as tentativas |
| Demais respostas `4xx` | `502 STT_PROVIDER_ERROR`, sem repetir |
| `RecognitionStatus` `NoMatch` ou tempos de silencio | `422 NO_SPEECH_DETECTED` |
| `RecognitionStatus` `Error` | `502 STT_PROVIDER_ERROR` |

```bash
curl --request POST \
  --url http://127.0.0.1:8000/api/audio \
  --header 'Authorization: Bearer <TOKEN>' \
  --form 'audio=@pergunta.wav;type=audio/wav'
```

## Nucleo de PLN

O modulo `app/nlp/` cobre o pre-processamento, a extracao de entidades e o
classificador de intencoes. O classificador decide **o que** foi pedido; a
extracao de entidades decide **sobre o que**.

| Modulo | Papel |
| --- | --- |
| `preprocessing.py` | Normaliza o texto do classificador sem remover acentos, negacoes ou stopwords; tambem mantem as rotinas legadas da extracao de entidades |
| `entities.py` | Identifica projeto, subportfolio, periodo, indicador e demais elementos do dominio |
| `classifier.py` | Carrega o artefato treinado e define o classificador hierarquico |
| `inference.py` | Classifica a solicitacao e aplica os limiares de roteamento |
| `data/lexico_dominio.json` | Vocabulario do portfolio, substituivel quando a base real existir |

O classificador v2 usa uma normalizacao conservadora: Unicode NFC, letras
minusculas e espacos normalizados. A funcao `normalizar_portugues` preserva
acentos, a negacao `nao`/`não` e todas as stopwords, porque esses elementos
podem inverter ou alterar o sentido em portugues. Os vetorizadores serializados
foram ajustados com esse contrato; qualquer mudanca nele exige novo treino e
nova avaliacao. As configuracoes antigas continuam disponiveis apenas para
reproduzir os benchmarks e a extracao de entidades.

```python
from app.nlp.preprocessing import tokenize
from app.nlp.entities import extract_entities

tokenize("Qual é o status da extensão da Linha 5-Lilás?")
# ['qual', 'é', 'o', 'status', 'da', 'extensã', 'da', 'linh', '5', 'lilás']

[(e.tipo, e.valor) for e in extract_entities("compare o Linha 2-Verde por custo em 2026")]
# [('projeto', 'Linha 2-Verde'), ('criterio', 'custo'), ('periodo', 'em 2026')]
```

A extracao roda sobre o **texto cru**, nao sobre os tokens: o tokenizador quebra
em `[^\W_]+` e separaria `PRJ-2031` em `PRJ` e `2031`. O casamento ignora caixa
e acento e devolve sempre o valor canonico do catalogo, porque o canal recebe
texto digitado.

Termos que pertencem a mais de um tipo — `aderencia ao cronograma` e criterio e
indicador — nao sao arbitrados aqui: a entidade expoe `tipos` com os candidatos
e `ambigua`, e quem ja conhece a intencao escolhe.

Medido contra o gabarito reconstruido da geracao do conjunto sintetico:
**precisao 0,996, revocacao 0,999, F1 0,998** sobre 7.000 entidades em 5.353
frases. O notebook reproduz a medicao e registra as limitacoes.

### Classificador de intencoes

O artefato treinado fica em `src/notebooks/artefatos/classificador_intencoes.joblib`
e e carregado por `app.nlp.classifier`:

```python
from app.nlp.classifier import load_artifact

artefato = load_artifact()
artefato.limiar_macro, artefato.limiar_intencao   # 0.525, 0.350
len(artefato.intencoes)                            # 31
```

O modelo e hierarquico: preve a macrointencao (`CONSULTA`, `TRANSACAO`,
`ALERTA`, `FORA_DE_ESCOPO`) e depois aciona um especialista treinado apenas com
as intencoes daquele grupo.

**O artefato precisava ser migrado para carregar fora do notebook.** O `joblib`
gravado pelo notebook do benchmark referenciava `__main__.identidade` e
`__main__.ClassificadorHierarquico`, definicoes que viviam no topo dele — de
qualquer codigo importavel, `joblib.load` falhava com `AttributeError`. As duas
passaram a viver em `app/nlp/classifier.py`, e o script abaixo reaponta o
artefato para la:

```bash
cd src/backend && .venv/bin/python ../notebooks/migrar_artefato_classificador.py
```

O artefato v2 ja referencia diretamente `app.nlp.classifier`. Para reparar uma
serializacao nova produzida pelo script de treino, execute
`treinar_classificador_intencoes_v2.py --reparar-artefato`; a operacao nao
retreina nem altera pesos, vetorizadores ou limiares.

**A versao do scikit-learn importa.** O artefato foi serializado com a 1.6.1,
fixada em `requirements.txt`. Carregar com outra versao faz o proprio
scikit-learn advertir que o resultado pode ser invalido, e o script de migracao
recusa executar fora dela.

O conjunto de treino, validacao e teste esta versionado na coluna `split` de
`dataset_intencoes.csv`, agrupado por `template_id`: nenhum template aparece em
mais de um conjunto, o que evita o vazamento que variacoes quase equivalentes
causariam.

### Inferencia

`app.nlp.inference` recebe a solicitacao em texto e devolve a macrointencao, a
intencao especifica e as confiancas:

```python
from app.nlp.inference import classify

classify("qual é o status da extensão da Linha 5-Lilás?")
# macrointencao='CONSULTA'  intencao='consulta_status_projeto'
# handler='handler:consulta_status_projeto'

classify("qual a previsão do tempo para amanhã?")
# macrointencao='FORA_DE_ESCOPO'  intencao=None
```

Os dois limiares governam o roteamento. Abaixo de 0,525 na macrointencao, a
solicitacao recebe a resposta controlada de limitacao. Acima dela, mas abaixo
de 0,350 na intencao, segue para o fluxo generico da macro em vez de acionar um
handler incerto. No conjunto de teste isso representa 10 solicitacoes abaixo do
limiar macro e 63 abaixo do limiar especifico. Na validacao, a acuracia entre
as intencoes aceitas foi 0,9010, com cobertura de 94,38%.

A saida nunca anuncia uma macrointencao e um handler de outra. O limiar de
0,350 e deliberadamente menor que o valor antigo, mas a verificacao explicita
de consistencia impede que um handler de outra macrointencao seja acionado.

**A representacao vencedora e hibrida.** Ela concatena TF-IDF de palavras
(1--2 gramas), TF-IDF de caracteres (3--5 gramas) e embeddings congelados do
`neuralmind/bert-base-portuguese-cased`, com peso 2,0 para o bloco BERTimbau.
Cada macrointencao tem um especialista `LinearSVC` (`C=1,0`) calibrado em tres
dobras. O encoder e carregado por PyTorch e Transformers e mantido em cache
durante a vida do processo. Esse ganho de qualidade traz custo maior de carga e
inferencia que a alternativa puramente lexical.

As dependencias ficam em `requirements-pln.txt`, separadas de
`requirements.txt`, porque quem trabalha so na API de audio nao precisa delas.
Sem elas, os testes de inferencia sao pulados com a razao declarada.

```bash
.venv/bin/python -m pip install -r requirements-pln.txt
```

No Windows, use o mesmo interpretador do ambiente local:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-pln.txt
```

**A API deve chamar `warmup()` na subida.** O carregamento e preguicoso, o que
serve aos testes, mas faria a primeira pessoa a usar o agente pagar a carga do
BERTimbau dentro da propria requisicao.

```python
from app.nlp.inference import get_classifier

get_classifier().warmup()
```

A inferencia reproduz sobre o conjunto de teste acuracia 0,839648 e F1-macro
0,832724 na intencao especifica, alem de 0,981498 e 0,971470 na macrointencao.
Os testes falham se esses valores divergirem do registro versionado.

### Avaliacao automatizada do RNF06

A medicao versionada esta em
`src/notebooks/artefatos/avaliacao_classificador_intencoes.json` e e gerada pelo
teste `app/tests/test_nlp_inference.py`, usando o classificador real de
`src/backend/app/nlp/`. O protocolo filtra exclusivamente as linhas
`split == teste` de `src/notebooks/artefatos/dataset_intencoes.csv`, sem
retreinar o modelo, totalizando 1.135 solicitacoes sinteticas.

Resultado atual para a intencao especifica: acuracia 0,839648 e F1 macro
0,832724. Para macrointencao: acuracia 0,981498 e F1 macro 0,971470. O JSON
tambem publica precisao, recall e F1 por classe, matriz de confusao, hashes dos
dados e do artefato e os pontos de operacao escolhidos somente na validacao.

As cinco classes mais fracas nesta medicao sao:

| Classe | Precisao | Recall | F1 | Suporte |
| --- | ---: | ---: | ---: | ---: |
| `analise_tendencia_desempenho` | 0,1429 | 0,0244 | 0,0417 | 41 |
| `consulta_indicadores_kpi` | 0,4474 | 0,8421 | 0,5841 | 38 |
| `consulta_orcamento_custo` | 0,7059 | 0,6486 | 0,6761 | 37 |
| `alerta_gerenciar_inscricao` | 1,0000 | 0,5161 | 0,6809 | 31 |
| `alerta_prazo_atraso` | 0,8077 | 0,6000 | 0,6885 | 35 |

Limitacoes registradas: o conjunto ainda e majoritariamente sintetico, sem
validacao externa com solicitacoes reais do dominio; a medicao principal inclui
todos os exemplos antes de qualquer abstencao; e a classe
`analise_tendencia_desempenho` continua muito abaixo das demais, apesar do ganho
global. Os 1.450 exemplos sinteticos adicionais foram usados exclusivamente no
treino; validacao e teste permaneceram inalterados.

A avaliacao prospectiva ampliada da issue #232 mede a recuperacao local com 72
consultas novas, balanceadas entre nove fontes e oito variacoes linguisticas.
A implementacao e a massa foram congeladas antes da unica execucao. O resultado
foi recall@3 de 0,555556 (40/72), com intervalo de Wilson de 95% entre 0,440874
e 0,664609. Embora a classificacao tenha obtido acuracia 0,839648 e F1-macro
0,832724, o RNF06 esta reprovado porque a recuperacao ficou abaixo de 0,80.

Uma rodada anterior marcou recall@3 de 1,000000 nos 18 casos usados para
ajustar equivalencias lexicais. Esse valor e mantido somente como teste de
regressao: como os erros da propria massa orientaram a mudanca, ele nao mede
generalizacao. Evidencias, hashes, casos e limitacoes estao em
`../../docs/evidencias/sprint-04/rnf06/`.

Para reproduzir os dois componentes de uma vez, a partir de `src/backend`:

```powershell
..\..\.venv\Scripts\python.exe scripts\benchmark_rnf06.py
```

O retorno 0 confirma que os dois limiares foram atingidos. Se algum deles
regredir, o comando retorna 1 e ainda grava o JSON com todos os casos e a
conclusao observada.

## Testes

```powershell
cd src/backend
.venv\Scripts\python.exe -m pytest app/tests
```

O fluxo transacional de relatórios possui testes em
`app/tests/test_reports.py`. Ele cobre o workflow guiado, identidade, escopo,
confirmação, callback idempotente, geração do DOCX e download autenticado. O
modo `power_automate_simulator` exercita o contrato externo sem tenant. Os
contratos, estados, variáveis e limites da integração estão documentados em
[`../agent/support/IMPLEMENTATION.md`](../agent/support/IMPLEMENTATION.md).

### Callback de resultado de relatórios (S5-09)

O webhook `POST /api/integrations/power-automate/report-results` recebe o
resultado terminal do processamento de um relatório. A chamada exige
`Content-Type: application/json` e o header `X-Callback-Token`, comparado em
tempo constante ao segredo `REPORT_CALLBACK_TOKEN`. O corpo correlaciona
`callback_id`, `execution_id`, `correlation_id` e `flow_run_id`, informa o
estado terminal e inclui o resultado ou o erro correspondente.

O callback é armazenado em `automation_callbacks`. A primeira chamada e uma
repetição equivalente retornam `200`, sem novo processamento; o mesmo
`callback_id` com payload diferente retorna `409`. Token ausente ou inválido
retorna `401`; execução desconhecida retorna `404` e corpo
inválido retorna `422`. Esse fluxo é síncrono e não publica evento no RabbitMQ.

### Callback de entrega de notificacoes (S5-10)

O webhook usa `POST /api/integrations/notifications/delivery-results` e exige o
header `X-Callback-Token`, comparado ao segredo `NOTIFICATION_CALLBACK_TOKEN`.
O corpo aceita `callback_id` (string), `notification_id` (UUID), `provider`
(string), `status` (`delivered` ou `failed`), `attempted_at` (data/hora ISO
8601) e `error_code` (string opcional):

```json
{
  "callback_id": "delivery-callback-001",
  "notification_id": "1674b3e9-ecba-4a78-a50f-848f5eaf0d79",
  "provider": "simulated",
  "status": "delivered",
  "attempted_at": "2026-09-25T12:00:00Z",
  "error_code": null
}
```

A primeira confirmacao valida e sua repeticao identica retornam `200`; o mesmo
`callback_id` com outro conteudo retorna `409`. Token invalido retorna `401`,
corpo invalido retorna `422` e notificacao inexistente retorna `404`. Cada
callback novo e persistido junto a um evento `notification.delivery.received`
na outbox. O publisher encaminha o evento ao RabbitMQ e o consumer `delivery`
acrescenta a tentativa de entrega; repeticoes identicas nao duplicam o evento
nem o processamento.

O contrato completo dos dois webhooks, os códigos HTTP e a topologia AMQP estão
na [Seção 8.5.12 de Projeto.md](../../docs/Projeto.md#8512-webhooks-e-mensageria-integrados-s5-09-a-s5-11).
Os comandos e resultados reproduzíveis estão na
[evidência da Sprint 5](../../docs/evidencias/sprint-05/webhooks-rabbitmq.md).

A fonte de dados do relatório é selecionada por `REPORT_PORTFOLIO_SOURCE`:
`synthetic` (padrão) lê a massa em `app/reports/data/synthetic_portfolio.json`;
`database` lê projetos, riscos, marcos, benefícios e mudanças das tabelas reais
(`projects`, `risk_issue_items`, `project_deliverables_milestones`,
`project_benefits`, `change_records`, `project_status_updates`,
`project_progress_updates`). Para o modo `database`, aplique o seed
`../database/sql/13_seed_portfolio_report_data.sql` (massa em português) e defina
também `REPORT_REPOSITORY_MODE=database`.

Execução CLI do mesmo serviço, sem depender da interface:

```powershell
$env:REPORT_CLI_TOKEN = "token-configurado-em-REPORT_SIMULATED_IDENTITIES"
python -m app.reports.cli --scope-type subportfolio --scope-id sp-modernizacao `
  --start-date 2026-08-01 --end-date 2026-08-31 `
  --audience executive_board --purpose monthly_governance `
  --emphasis schedule --emphasis risks
```

Recorte mínimo para a integração PLN/API da task #126:

```powershell
cd src/backend
.venv\Scripts\python.exe -m pytest app/tests/test_pipeline_api.py -q
.venv\Scripts\python.exe -m pytest app/tests/test_audio_upload.py -q
.venv\Scripts\python.exe -m pytest app/tests/test_nlp_entities.py -q
```

A suite automatizada cobre validacao de formato, duracao, tamanho, silencio,
autenticacao simulada, limite de uma requisicao por usuario, contrato de resposta
do upload, mensagens de erro controladas e a fronteira HTTP com o Azure AI
Speech. As chamadas ao provedor externo usam duplos de teste por padrao, mesmo
com `.env` preenchido, para manter a execucao reproduzivel e sem consumo de
franquia.

As opcoes de pre-processamento mantidas para reproduzir o benchmark de PLN podem
exigir dados do NLTK. Quando o ambiente ainda nao tiver esses corpora:

```powershell
.venv\Scripts\python.exe -c "import nltk; nltk.download('stopwords', download_dir='.venv/nltk_data'); nltk.download('punkt_tab', download_dir='.venv/nltk_data')"
```

Validacoes E2E contra o Azure devem ser executadas separadamente da suite
deterministica. Um arquivo publico usado como amostra foi
`tiririca_campanha.wav`, referenciado em
`https://bookdown.org/davi_moreira/txt4cs/scrape.html` e disponivel no GitHub do
material. Como a amostra original esta em WAV estereo a 44,1 kHz, a copia de
teste deve ser convertida para WAV PCM mono a 16 kHz antes do envio ao
`POST /api/audio`.


## Integração da bancada web (#131)

`POST /api/chat` aceita `conversation_id`, `use_intent_classifier`, `message` e `previous_interaction_id`. `conversation_id` identifica a conversa; `previous_interaction_id` encadeia o provedor e não é mais reutilizado como ID externo. Campo ausente ou `true` executa classificação e extração de entidades por padrão; `false` é opt-out explícito para preservar o toggle da interface. A resposta inclui `intent` rico (`macro`, `specific`, confianças, `flow`, `handler` e `alternatives`), `entities`, `pipeline_metrics` (`nlp_ms` e `route_ms`) e `sources[].excerpt` com o trecho recuperado. Para `transacao_gerar_relatorio`, inclui `workflow` e não chama Gemini.

`POST /api/chat/proactive-confirmation` aceita exclusivamente `suggestion_id`, `conversation_id` e `decision` (`accept` ou `decline`), sem campo de mensagem livre, e exige o mesmo esquema de autenticação. A chamada principal prepara a resposta secundária junto da resposta principal e armazena esse conteúdo sem exibi-lo. A confirmação só é encontrada quando UUID, identidade e conversa coincidem: `decline` descarta o registro e `accept` libera a resposta preparada, ambos sem nova chamada ao Gemini. A decisão e a resposta liberada continuam registradas na trilha RNF03. Uma sugestão expirada, já decidida ou fora do escopo do solicitante retorna `404`.

Com `DATABASE_URL` ou `SUPABASE_DATABASE_URL`, as sugestões pendentes e suas respostas já preparadas são armazenadas em `pending_proactive_suggestions`, permitindo confirmação por qualquer worker durante o TTL. Bancos existentes precisam da migração `08_add_prepared_proactive_response.sql`. Sem banco configurado, desenvolvimento e testes usam um fallback em memória de processo; esse modo não oferece continuidade após reinício nem balanceamento entre workers e não deve ser usado em produção.

`POST /api/audio` aceita também os campos multipart `previous_interaction_id`, `use_intent_classifier` e `proactivity_enabled`. Depois de validar e transcrever, executa o mesmo pipeline de texto fora do laço assíncrono. Preserva `answer`, retorna `pipeline_status="completed"` e acrescenta `chat` com as fontes completas, intenção rica, eventual sugestão proativa, entidades, métricas (`validation_ms`, `stt_ms`, `nlp_ms`, `route_ms`, `total_ms`) e ID real da interação. Não são mais gerados IDs de interação fictícios nem respostas provisórias de sucesso.

O pipeline classifica e gera respostas informativas. A intenção de relatório inicia um workflow funcional no frontend/backend; outras intenções transacionais ainda não executam alteração em sistemas corporativos. A identidade corporativa Entra ID permanece dependente do ambiente previsto para a implantação.

Com `PLN_WARMUP=1`, a inicialização carrega o classificador antes de aceitar requisições. As chamadas ao modelo são serializadas para evitar carregamentos concorrentes. Uma falha de inicialização exige corrigir dependências/modelos; em testes determinísticos use `PLN_WARMUP=0`.

Erros de configuração e do Gemini são convertidos em mensagens controladas. Entradas textuais inválidas retornam `422` com `error.code=INVALID_INPUT`; detalhes internos de validação não são apresentados ao usuário.

A [documentação do frontend](../frontend/README.md) descreve estrutura, fluxos, contratos, execução e limitações. A [matriz de testes](../frontend/TESTES.md) reúne as evidências da integração S3/S5.

## Alerta autônomo de prazo

`handler:alerta_prazo_atraso` inicia um workflow guiado próprio. Depois da
confirmação, scheduler, outbox e RabbitMQ avaliam o cronograma em segundo plano
e gravam notificações internas. O fluxo não depende de Power Automate; apenas a
confirmação de entrega usa o webhook S5-10 descrito acima. Com PostgreSQL e
RabbitMQ configurados, execute o publisher com `python -m app.alerts.worker
publisher` e o consumer com `python -m app.alerts.worker delivery`. Veja [a
documentação operacional](../agent/support/IMPLEMENTATION.md#3-workflow-alerta_prazo_atraso).

## VHS/cache de transcricao (S4-31)

Cache STT ativo por padrao, TTL 300s e 256 entradas por processo.
`VHS_ENABLED=0` desativa; reiniciar os workers invalida todos os cassetes.
O runtime do container fixa um worker de API enquanto o cache não for
compartilhado. Não escale o serviço `backend` horizontalmente sem substituir o
VHS por armazenamento distribuído.

Uma identidade válida do áudio pode consultar `GET /api/audio/vhs/metrics`.
O endpoint não devolve áudio, transcrição, chave ou credencial: informa somente
o identificador efêmero do worker, topologia, ocupação, contadores, taxa de hit
e estimativa de chamadas evitadas.

Plano, limites e comandos: [plano VHS](../../docs/testes/sprint4/plano-vhs.md).
Coleta local: `python scripts/verify_vhs.py` a partir de `src/backend`.
Validação com Azure real: `python scripts/verify_audio_stt_pln_live.py
<audio.wav> --expected-term <termo> --repetitions 5`, no ambiente publicado.
