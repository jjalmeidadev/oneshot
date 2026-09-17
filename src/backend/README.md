# Backend

API FastAPI do projeto, com chat via Gemini e recuperacao de contexto em listas simuladas do SharePoint.

## Configuracao

Crie `src/backend/.env` a partir de `.env.example` e informe uma chave do
Google AI Studio em `GEMINI_API_KEY`. A chave e utilizada somente pelo backend.

Por padrao, as respostas usam nivel de raciocinio `low` e ate 512 tokens para
reduzir a latencia. Falhas transitorias sao repetidas ate tres vezes, com esperas
de 2, 4 e 8 segundos. Esses valores podem ser ajustados em `.env` por meio de
`GEMINI_THINKING_LEVEL`, `GEMINI_MAX_OUTPUT_TOKENS`, `GEMINI_MAX_RETRIES`,
`GEMINI_RETRY_BASE_DELAY_SECONDS` e `GEMINI_REQUEST_TIMEOUT_SECONDS`.

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
| `preprocessing.py` | Normaliza, tokeniza e reduz a radical, na `config_22` da Secao 8.10.3 |
| `entities.py` | Identifica projeto, subportfolio, periodo, indicador e demais elementos do dominio |
| `classifier.py` | Carrega o artefato treinado e define o classificador hierarquico |
| `inference.py` | Classifica a solicitacao e aplica os limiares de roteamento |
| `data/lexico_dominio.json` | Vocabulario do portfolio, substituivel quando a base real existir |

**A `config_22` e um contrato, nao uma preferencia.** Os vetorizadores TF-IDF
serializados em `src/notebooks/artefatos/classificador_intencoes.joblib` foram
ajustados sobre os tokens que `preprocess_text` produz. Alterar tokenizacao,
caixa ou stemming invalida o modelo treinado, e o benchmark precisa ser
reexecutado. O notebook `src/notebooks/preprocessamento_entidades.ipynb`
compara as duas implementacoes sobre as 5.353 frases do conjunto sintetico e
falha se houver uma divergencia.

A configuracao selecionada nao exige corpus baixado do NLTK: o tokenizador e
uma expressao regular e o Snowball e algoritmico. As demais opcoes da grade,
mantidas para o benchmark continuar reproduzivel, podem pedir
`nltk.download('punkt')` e `nltk.download('stopwords')`.

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
artefato.limiar_macro, artefato.limiar_intencao   # 0.55, 0.70
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

O script nao retreina: os pesos, os vetorizadores e os limiares continuam sendo
os que produziram as metricas da Secao 8.10.3. Com `--verificar` ele apenas
confere, sem gravar. O artefato versionado ja esta migrado; o script serve para
qualquer artefato novo que saia do notebook.

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

Os dois limiares governam o roteamento. Abaixo de 0,550 na macrointencao, a
solicitacao recebe a resposta controlada de limitacao. Acima dela, mas abaixo
de 0,700 na intencao, segue para o fluxo generico da macro em vez de acionar um
handler incerto. No conjunto de teste isso significa 14 solicitacoes (1,2%) com
resposta de limitacao e 305 (26,9%) no fluxo generico, e a acuracia entre as
aceitas sobe de 0,7383 para 0,8775.

A saida nunca anuncia uma macrointencao e um handler de outra. O limiar de
0,700 ja garante isso — a probabilidade da intencao e conjunta, e acima de 0,5
as duas coincidem por construcao — mas a verificacao e explicita, para
recalibrar o limiar para baixo nao quebrar o contrato em silencio.

**O encoder roda em ONNX Runtime, nao em PyTorch.** A representacao vencedora
combina quatro blocos, e dois deles nao estao no `joblib`: o Word2Vec, em
`word2vec_portfolio.model`, e o encoder BERT, baixado do Hugging Face na
primeira execucao e mantido em cache local. O grafo usado e o ONNX publicado no
proprio repositorio do modelo.

Os embeddings sao identicos aos do `sentence-transformers` — diferenca maxima de
2,4e-07 — e as metricas do conjunto de teste ficam inalteradas. O que muda e o
custo:

| | PyTorch | ONNX Runtime |
| --- | ---: | ---: |
| Ambiente | 1,1 GB | **427 MB** |
| Carga do encoder | 6,10 s | **0,33 s** |
| Latencia por requisicao | 6 ms | **2 ms** |
| Pico de memoria | **1.118 MB** | 1.355 MB |

O ganho em disco e em carga vem de dispensar `torch` e `transformers`, que
somavam 780 MB. O custo e memoria: o grafo fp32 ocupa cerca de 240 MB a mais em
tempo de execucao, e desligar o *memory arena* do onnxruntime nao reduziu isso.
No deploy em Linux a troca tambem evita uma armadilha: o `pip install torch`
padrao baixa a variante com CUDA, de cerca de 2,5 GB.

A versao quantizada em int8 reduziria o grafo de 449 MB para 113 MB, mas custa
0,35 ponto de acuracia e desloca o efeito dos limiares, quebrando a reproducao
exata dos numeros documentados. Por isso a fp32 foi mantida.

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

O ambiente exige **Python 3.13 ou anterior**: o `gensim` ainda nao publica wheel
para o 3.14 e a compilacao a partir do fonte falha.

**A API deve chamar `warmup()` na subida.** O carregamento e preguicoso, o que
serve aos testes mas faria a primeira pessoa a usar o agente pagar a carga
inteira dentro da propria requisicao — 0,33 s com ONNX, 6,1 s com PyTorch,
dentro do orcamento de 10 s do RNF05.

```python
from app.nlp.inference import get_classifier

get_classifier().warmup()
```

A inferencia reproduz os numeros da Secao 8.10.3 sobre o conjunto de teste —
acuracia 0,7383 e F1-macro 0,7401 na intencao especifica — e os testes falham se
divergirem.

### Avaliacao automatizada do RNF06

A medicao versionada esta em
`src/notebooks/artefatos/avaliacao_classificador_intencoes.json` e e gerada pelo
teste `app/tests/test_nlp_inference.py`, usando o classificador real de
`src/backend/app/nlp/`. O protocolo filtra exclusivamente as linhas
`split == teste` de `src/notebooks/artefatos/dataset_intencoes.csv`, sem
retreinar o modelo, totalizando 1.135 solicitacoes sinteticas.

Resultado atual para a intencao especifica: acuracia 0,7383 e F1 macro 0,7401. O JSON tambem publica precisao, recall e F1 por
classe, matriz de confusao e classes com pior desempenho.

As cinco classes mais fracas nesta medicao sao:

| Classe | Precisao | Recall | F1 | Suporte |
| --- | ---: | ---: | ---: | ---: |
| `analise_tendencia_desempenho` | 0,3846 | 0,2439 | 0,2985 | 41 |
| `transacao_exportar_dados` | 0,4815 | 0,3514 | 0,4062 | 37 |
| `consulta_documentos_fonte` | 0,9231 | 0,3000 | 0,4528 | 40 |
| `consulta_pendencias_projeto` | 0,8125 | 0,3714 | 0,5098 | 35 |
| `consulta_cronograma_prazo` | 0,4561 | 0,6341 | 0,5306 | 41 |

Limitacoes registradas: o conjunto ainda e sintetico, sem validacao com
solicitacoes reais do dominio; a medicao considera a intencao especifica prevista
pelo modelo antes dos limiares de roteamento; e classes com baixo suporte ou
fronteiras proximas entre consulta e transacao concentram parte dos erros.

## Testes

```powershell
cd src/backend
.venv\Scripts\python.exe -m pytest app/tests
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

`POST /api/chat` aceita `use_intent_classifier` além de `message` e `previous_interaction_id`. Campo ausente ou `true` executa classificação e extração de entidades por padrão; `false` é opt-out explícito para preservar o toggle da interface. A resposta inclui `intent` rico (`macro`, `specific`, confianças, `flow`, `handler` e `alternatives`), `entities`, `pipeline_metrics` (`nlp_ms` e `route_ms`) e `sources[].excerpt` com o trecho recuperado. Perguntas sem confiança suficiente, fora do escopo ou sem rota segura recebem resposta controlada sem chamada ao Gemini.

`POST /api/audio` aceita também os campos multipart `previous_interaction_id` e `use_intent_classifier`. Depois de validar e transcrever, executa o mesmo pipeline de texto fora do laço assíncrono. Preserva `answer`, retorna `pipeline_status="completed"` e acrescenta `chat` com as fontes completas, intenção rica, entidades, métricas (`validation_ms`, `stt_ms`, `nlp_ms`, `route_ms`, `total_ms`) e ID real da interação. Não são mais gerados IDs de interação fictícios nem respostas provisórias de sucesso.

O pipeline classifica e gera respostas informativas. A identificação de uma intenção transacional não executa uma alteração em sistemas corporativos. Autorização por perfil, persistência e integração Entra ID continuam dependendo dos módulos e do ambiente previstos para essas entregas.

Com `PLN_WARMUP=1`, a inicialização carrega o classificador antes de aceitar requisições. As chamadas ao modelo são serializadas para evitar carregamentos concorrentes. Uma falha de inicialização exige corrigir dependências/modelos; em testes determinísticos use `PLN_WARMUP=0`.

Erros de configuração e do Gemini são convertidos em mensagens controladas. Entradas textuais inválidas retornam `422` com `error.code=INVALID_INPUT`; detalhes internos de validação não são apresentados ao usuário.

A [documentação do frontend](../frontend/README.md) descreve estrutura, fluxos, contratos, execução e limitações. A [matriz de testes](../frontend/TESTES.md) reúne as evidências da integração S3/S5.
