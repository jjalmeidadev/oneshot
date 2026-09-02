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

Enquanto a integracao de Speech-to-Text nao existir, um audio aprovado na validacao
recebe `200` com `pipeline_status` igual a `"stubbed"` e transcricao vazia. A troca
acontece em `app/audio/transcription.py`, sem alterar o endpoint.

```bash
curl --request POST \
  --url http://127.0.0.1:8000/api/audio \
  --header 'Authorization: Bearer <TOKEN>' \
  --form 'audio=@pergunta.wav;type=audio/wav'
```

## Testes

```powershell
cd src/backend
.venv\Scripts\python.exe -m pytest app/tests
```
