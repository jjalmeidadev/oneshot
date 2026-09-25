# Evidências dos testes funcionais — RF01 a RF10

Esta pasta consolida as evidências dos testes funcionais RF01–RF10 executados na Sprint 4. Plano na Seção 9.1.3 e resultados na Seção 9.1.5 do [`Projeto.md`](../../../../docs/Projeto.md).

## Execução

| Item | Registro |
| --- | --- |
| Data | 23/09/2026; os registros com horário vão das 20:59 às 21:42 (horário de Brasília) |
| Responsável | Wendel Feitosa |
| Versão testada | commit `be814f6` da `develop`, base da branch da execução |
| Backend | FastAPI/Uvicorn local em `http://127.0.0.1:8000`, base de conhecimento no Supabase |
| Interface | Vite (`npm run dev`), usada no áudio do CT-RF01-01 e no CT-RF10-01 |
| Provedor e modelo | OpenRouter, `google/gemini-3.7-flash`, limite de 512 tokens de saída (padrão dessa versão) |
| Reteste do CT-RF09-01 | 24/09/2026, commit `c793983`, limite de 1024 tokens; ver [`rf09/CT-RF09-01-reteste.txt`](rf09/CT-RF09-01-reteste.txt). Fora os testes, o único código de `src/backend/app` que muda entre `be814f6` e `c793983` é a correção do truncamento, em `app/gemini/client.py` |

## Resultado consolidado

| Momento | Executados | APROVADO | FALHOU | BLOQUEADO | NÃO EXECUTADO |
| --- | ---: | ---: | ---: | ---: | ---: |
| Rodada de 23/09 | 20 | 15 | 5 | 0 | 0 |
| Depois do reteste do CT-RF09-01 | 20 | 16 | 4 | 0 | 0 |

## Como reproduzir

Os casos de API usam duas rotas do backend. A partir de `src/backend`, com o `.env` configurado:

```bash
LLM_PROVIDER=openrouter .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Consulta, sem proatividade (casos de RF01 a RF08 e CT-RF10-02):

```bash
curl -s http://127.0.0.1:8000/api/chat -H "Content-Type: application/json" \
  -d '{"message": "Qual é o prazo do projeto PRJ-0442?", "conversation_id": "ct-rf04-01", "proactivity_enabled": false}'
```

Com proatividade (CT-RF09-01 e CT-RF09-02), a rota exige o Bearer de uma identidade simulada de `AUDIO_SIMULATED_IDENTITIES`, que não é registrado nas evidências:

```bash
curl -s http://127.0.0.1:8000/api/chat -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "Qual é o prazo do projeto PRJ-0442?", "conversation_id": "ct-rf09-01", "proactivity_enabled": true}'

curl -s http://127.0.0.1:8000/api/chat/proactive-confirmation -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{"suggestion_id": "<suggestion_id da resposta anterior>", "conversation_id": "ct-rf09-01", "decision": "accept"}'
```

`decision` recebe `accept` ou `decline`. O comando exato do CT-RF10-02 está no próprio registro, e o reteste do CT-RF09-01 tem script próprio, [`rf09/reteste_ct_rf09_01.py`](rf09/reteste_ct_rf09_01.py). O áudio do CT-RF01-01 e o CT-RF10-01 foram executados pela interface.

## Regra de proveniência

Os arquivos usam dois tipos de registro:

- `TIPO DE REGISTRO: SAÍDA BRUTA PRESERVADA`: o conteúdo integral relevante foi preservado no histórico da execução.
- `TIPO DE REGISTRO: REGISTRO CONSOLIDADO`: os valores observados foram preservados durante a execução, mas o dump integral original do terminal não está disponível neste pacote. Nenhum campo ausente foi inventado.

As classificações registradas nos casos CT-RF02-01, CT-RF03-02, CT-RF05-01 e CT-RF06-01 foram conferidas de novo no classificador local, que é determinístico, e os valores coincidem.

Credenciais, tokens, senhas e chaves foram deliberadamente omitidos.

## Defeitos

- DEF-RF02-01 — sensibilidade lexical na classificação de consulta de status.
- DEF-RF03-01 — reserva genérica associada a `transacao_agendar_compromisso`.
- DEF-RF06-01 — a base consultada pelo chat não tem documento do PRJ-0510, e o chat não lê as tabelas estruturadas em que o projeto tem dados; a comparação sai só com o PRJ-0442. CT-RF08-01 falha pela mesma causa.
- DEF-RNF04-02, registrado na Seção 9.2.7 — a resposta ao aceite do CT-RF09-01 foi cortada pelo limite de tokens. Corrigido; no reteste, 5 de 5 respostas chegaram inteiras.
