# Relatório S4-20 (#209) — E2E textual com RAG e verificação de persistência

Sprint 4 · Grupo 05 · Frente de testes sistêmicos
Execução: Felipe

---

## 1. Planejamento

O objetivo é comprovar que uma pergunta textual atravessa cliente, API, PLN, recuperação e geração, e que o resultado fica localizável no Supabase: conversa, interação, fontes consultadas e eventos de auditoria.

**Escopo de modelos.** A issue previa exercitar caminhos GPT e Claude. O grupo decidiu não implementá-los por enquanto, e o backend tem um único provedor de geração (`app/gemini/`, configurado por `GEMINI_API_KEY` e `GEMINI_MODEL`). O item do DoD sobre seleção de modelo continua verificável: basta comparar duas execuções com modelos Gemini diferentes e confirmar que PLN e recuperação não mudam. O item de fallback não é verificável, pois não existe mecanismo de fallback no código.

**Por que não usar o `e2e_server.py` existente.** Aquele servidor substitui PLN, geração e transcrição por versões determinísticas. Serve para validar o contrato entre rotas, mas não atravessa as camadas reais, que é o que este DoD exige. Os cenários abaixo rodam contra o backend real.

**Ferramentas.** `pytest` para os cenários automatizados (`src/backend/app/tests/test_e2e_textual_rag_s4_20.py`), `curl` para os cenários que exigem reiniciar o backend com variáveis diferentes, e consultas SQL no Supabase para conferir a persistência.

**Correlação.** Como a API não devolve o identificador da linha gravada no banco (achado A-01), a correlação entre resposta e registro é feita por um marcador único injetado no texto da pergunta.

---

## 2. Ambiente e congelamento

| Campo | Valor |
|---|---|
| Rodada | 1 |
| Data | 24/09/2026 |
| Branch | `feature/S4-20-e2e-textual-rag`, a partir de `origin/develop` |
| Commit | `<preencher>` |
| Ambiente | Backend local (`uvicorn app.main:app --port 8000`), Gemini real, Supabase do projeto |
| Modelo base | `gemini-3.7-flash` |
| Modelo alternativo | `gemini-3.8-flash` |

---

## 3. Cenários de teste

| ID | Tipo | Propósito | Execução | Resultado esperado |
|---|:---:|---|---|---|
| CT-E2E-01 | Positivo | Confirmar que a pergunta atravessa API, PLN, recuperação e geração | `POST /api/chat` com pergunta de consulta ao portfólio, contendo marcador único | HTTP 200; intenção classificada; `nlp_ms > 0`; fontes devolvidas |
| CT-E2E-02 | Positivo | Confirmar que a interação é localizável no Supabase com a cadeia completa | Localizar a interação pelo marcador e percorrer conversa, fontes e auditoria | 1 interação; conversa correspondente; linhas em `consulted_sources`; eventos em `audit_events` |
| CT-E2E-03 | Negativo | Confirmar tratamento de falha do provedor de geração | Subir o backend com modelo indisponível para a chave e enviar a mesma pergunta | Cliente recebe mensagem controlada, sem detalhe técnico; interação persistida com `processing_status = 'erro'` e evento com `event_status = 'falha'` |
| CT-E2E-04 | Positivo | Confirmar que a seleção de modelo altera somente a geração | Mesma pergunta com `GEMINI_MODEL = gemini-3.7-flash` e depois `gemini-3.8-flash` | Intenção e fontes idênticas; `model` e texto diferentes |
| CT-E2E-05 | Positivo | Confirmar que a resposta permite ao cliente localizar seu registro no banco | Comparar o `interaction_id` da resposta com `ai_interactions.id` | O identificador devolvido corresponde a uma linha em `ai_interactions` |
| CT-E2E-06 | Positivo | Correlacionar o Copilot Studio no E2E | Depende da integração entregue por #212–#220 | Evidência de ponta a ponta incluindo o canal do Copilot Studio |
| CT-E2E-07 | Positivo | Verificar fallback entre modelos | Forçar indisponibilidade do modelo principal | Sistema recorre a modelo alternativo automaticamente |

---

## 4. Resultados

| ID | Resultado obtido | Evidência | Status |
|---|---|---|:---:|
| CT-E2E-01 | HTTP 200 em 16,27 s. `model = gemini-3.7-flash`; intenção `CONSULTA / consulta_visao_portfolio`; `nlp_ms = 63`; `retrieval_ms = 1933`; duas fontes devolvidas | `evidencias/r1-e2e-01.json` | **Aprovado** |
| CT-E2E-02 | Os quatro elos conferidos automaticamente: 1 interação localizada pelo marcador, conversa correspondente, fontes gravadas em `consulted_sources` e eventos de auditoria presentes, incluindo o componente `api` | Saída do `pytest` | **Aprovado** |
| CT-E2E-03 | Cliente recebeu `{"detail":"Não foi possível obter uma resposta. Tente novamente em instantes."}`, sem detalhe técnico. Interação `94c3d48d-9ce7-4832-ae6f-920723558537` persistida com `processing_status = 'erro'` e 2 eventos com `event_status = 'falha'`. `route_taken = 'sharepoint_query'`, ou seja, a recuperação executou e a falha ficou restrita à geração | Consulta ao Supabase na janela da execução | **Aprovado** |
| CT-E2E-04 | Intenção, confianças, alternativas e fontes idênticas nos dois modelos; apenas `model`, texto e tempo diferentes. Detalhe na seção 4.1 | `evidencias/r1-e2e-04-modelo-b.json` | **Aprovado** |
| CT-E2E-05 | O `interaction_id` devolvido foi `v1_ChdqR2kxYXVlVEthSG96N0lQM3R5c21Bcx…`, identificador do Gemini, não um UUID de `ai_interactions` | Saída do `pytest`, registrado como `xfail` | **Falhou** |
| CT-E2E-06 | Não executado. A integração com o Copilot Studio é entregue por #212–#220 | — | **Bloqueado** |
| CT-E2E-07 | Não executado. Não há mecanismo de fallback em `app/gemini/client.py`; só troca de modelo por variável de ambiente, que é configuração | — | **Bloqueado** |

### 4.1 Comparação entre modelos (CT-E2E-04)

| Medida | `gemini-3.7-flash` | `gemini-3.8-flash` |
|---|---|---|
| `intent.macro` | CONSULTA | CONSULTA |
| `intent.specific` | `consulta_visao_portfolio` | `consulta_visao_portfolio` |
| `confidence_macro` | 0,9995 | 0,9995 |
| `confidence_specific` | 0,5999 | 0,5999 |
| Alternativas | 0,5999 / 0,3851 / 0,0053 | 0,5999 / 0,3851 / 0,0053 |
| Fontes | `procedimentos-operacionais:103` (2,0) e `:101` (1,0) | as mesmas, mesmos escores |
| `retrieval_ms` | 1933 | 1906 |
| `model` | `gemini-3.7-flash` | `gemini-3.8-flash` |
| `latency_ms` | 10.567 | 4.011 |

A classificação coincidiu até a quarta casa decimal, inclusive a lista de alternativas, e as fontes vieram com os mesmos identificadores e escores. A troca de modelo não afetou PLN nem recuperação.

---

## 5. Achados

### A-01 — a resposta da API não devolve o identificador da interação no banco

`GeminiChatResponse` tem o campo `interaction_id`, mas ele carrega o identificador do provedor de geração, não o da linha gravada no Supabase. Em `app/pipeline.py`, a função `_trace_safely()` chama `trace_interaction()` e descarta o retorno, que é justamente esse identificador.

O cliente não consegue apontar para o próprio registro. A correlação só é possível por aproximação — texto da pergunta mais janela de tempo —, que é o que este relatório fez com o marcador único.

É o mesmo problema do defeito D-03 da #200 (`correlation_id` nunca gravado), visto pelo lado do cliente.

Correção: `_trace_safely()` retorna o identificador e `process_message()` o atribui à resposta. Duas linhas.

### A-02 — falha de persistência não é sinalizada ao cliente

`_trace_safely()` captura `TraceabilityError` e registra apenas um aviso no log local. A requisição segue e devolve 200.

Se a gravação falhar, o usuário recebe a resposta normalmente e nada é registrado, sem sinal externo. Combinado com o defeito D-05 da #200 — o evento do fluxo guiado usa um componente que a restrição do schema rejeita, derrubando a transação inteira —, existe um caminho em que pedir um relatório devolve resposta normal e não deixa rastro no banco.

Como verificar: enviar uma mensagem que o classificador roteie para `transacao_gerar_relatorio` e conferir se a interação aparece no Supabase.

### A-03 — intenção roteada abaixo do limiar configurado (a verificar)

A intenção `consulta_visao_portfolio` foi roteada com confiança 0,5999, enquanto `intent_catalog.intent_confidence_threshold` tem padrão 0,7000.

Não é possível concluir com esta evidência se o classificador consulta esse campo ou usa limiar próprio. Registrado para verificação na #229.

---

## 6. Instruções de execução

Pré-requisitos no `.env` do backend: `GEMINI_API_KEY`, `GEMINI_MODEL` e `SUPABASE_DATABASE_URL`.

```bash
cd src/backend
source .venv/Scripts/activate

# terminal 1 — backend real
uvicorn app.main:app --port 8000

# terminal 2 — cenários automatizados
export E2E_BASE_URL=http://127.0.0.1:8000
python -m pytest app/tests/test_e2e_textual_rag_s4_20.py -v
```

Três observações de execução:

Use `127.0.0.1`, não `localhost`. No Windows, `localhost` resolve primeiro para IPv6 e o uvicorn escuta em IPv4; a requisição fica pendurada até estourar o tempo, e o sintoma aparece como "backend não respondeu".

Se o `.env` tiver `PLN_WARMUP=1`, o servidor carrega o classificador antes de aceitar requisições e leva cerca de um minuto. Espere a linha `Application startup complete`.

O `main.py` carrega o `.env` com `override=True`, então trocar `GEMINI_MODEL` exige editar o arquivo — exportar a variável no terminal não tem efeito.

Resultado da rodada 1 nos cenários automatizados: 6 aprovados, 1 `xfail` (o CT-E2E-05, esperado e documentado).

---

## 7. Conformidade com DoR e DoD

### 7.1 DoR

| Item | Situação |
|---|---|
| S4-12 a S4-17A e S4-19 | `<confirmar com o grupo>` |
| Contratos de API, PLN e persistência identificados | Atendido — `GeminiChatRequest`/`GeminiChatResponse`, `app/pipeline.py`, `app/database/tracing.py` |
| Massa sintética e cenários positivo e negativo preparados | Atendido |

### 7.2 DoD

| Item | Situação |
|---|---|
| Cenário atravessa frontend, API, PLN, recuperação e resposta | Atendido — CT-E2E-01 |
| Referências do backend, conversa, fontes e auditoria localizadas no Supabase | Atendido — CT-E2E-02 |
| Teste automatizado comprova o contrato entre camadas | Atendido — `test_e2e_textual_rag_s4_20.py` |
| Exemplos de API, fontes e rastreabilidade atualizados quando afetados | Nenhum contrato foi alterado; nada a atualizar |
| E2E correlaciona frontend, API, PLN, RAG, Copilot Studio, resposta e Supabase | Parcial — Copilot Studio bloqueado (CT-E2E-06) |
| Modelo solicitado, modelo usado, fallback, fontes e períodos com evidência reproduzível | Parcial — modelo e fontes comprovados (CT-E2E-04); fallback não existe (CT-E2E-07) |

Os dois itens parciais ficaram assim por ausência de implementação, não por lacuna de teste. Ambos registrados como bloqueio, conforme o DoD admite.

---

## 8. Conclusão

**4 aprovados, 1 falha, 2 bloqueados.**

O fluxo textual com RAG funciona de ponta a ponta: a pergunta atravessa todas as camadas e o resultado fica gravado no Supabase de forma correlacionada e verificável automaticamente.

O tratamento de erro também está correto. A falha do provedor ocorreu naturalmente durante a preparação do CT-E2E-04, quando o backend subiu com um modelo indisponível para a chave. O cliente recebeu mensagem controlada e a interação foi persistida como erro, com os eventos de auditoria correspondentes.

A troca de modelo não afetou as camadas anteriores, que era o ponto central do item de seleção de modelo no DoD.

A falha registrada é a ausência de identificador de correlação na resposta da API (A-01), com correção de duas linhas. Os dois bloqueios — Copilot Studio e fallback — dependem de implementação que não existe nesta sprint.
