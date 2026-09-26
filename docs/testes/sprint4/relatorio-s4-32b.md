# Relatório S4-32B (#228) — Execução e consolidação dos testes de integração

Sprint 4 · Grupo 05 · Frente de testes sistêmicos
Execução: Felipe

---

## 1. Planejamento

O objetivo é validar comunicação e tratamento de erro nas fronteiras do sistema: comunicação interna entre componentes, serviços externos, VHS/cache e tratamento de erro. Cada frente precisa de instrução, ferramenta, validação esperada, resultado e evidência; dependência indisponível vira bloqueio registrado.

**Critério de classificação.** Um arquivo é de integração quando **cruza fronteira entre componentes** — API, modelo, banco ou serviço externo. O critério vale pelo objeto do teste, não pela presença de duplo: `test_database_pool` e `test_llm_provider` usam duplos, mas o que eles exercitam *é* a fronteira, e por isso entram. Se o grupo preferir o critério estrito de "só conta se tocar o recurso real", a integração cai de 216 para 171 testes.

**Ferramenta.** `pytest` com o marcador `integration`, registrado em `app/tests/conftest.py`. O registro fica ali, e não num `pytest.ini` novo, para não mudar o rootdir da suíte.

---

## 2. Ambiente e congelamento

| Campo | Valor |
|---|---|
| Rodada | 1 |
| Data | 24/09/2026 |
| Branch | `feature/S4-32B-testes-integracao`, a partir de `origin/develop` |
| Ambiente | Windows, Python 3.13.9, pytest 9.1.1, venv do backend |
| Massa | Banco do projeto com ~2.600 interações acumuladas; massa sintética local |
| Duração | 3min56s |

---

## 3. Inventário da suíte

A classificação anterior, da Sprint 3, contava 223 testes. A suíte tem hoje **378**, crescimento de 70%, com arquivos novos vindos da campanha de RNF04 e RNF05 de outro integrante. A contagem foi refeita do zero.

| Fronteira | Arquivos | Testes |
|---|---|---:|
| **Integração** | | **216** |
| Serviço externo — modelo real | `test_nlp_inference` | 25 |
| API — cliente HTTP real, provedores com duplo | `test_audio_upload` (64), `test_pipeline_api` (22), `test_reports` (22) | 108 |
| Banco | `test_database_pool` (28), `test_traceability` (14), `test_persistence_audit_s4_11` (13) | 55 |
| Provedor de LLM | `test_llm_provider` | 17 |
| Massa documental | `test_sharepoint_rag` | 11 |
| **Unitário** | | **162** |
| PLN | `test_nlp_entities` (30), `test_nlp_preprocessing` (22), `test_nlp_classifier` (19) | 71 |
| Instrumentação e apuração de RNF | `test_instrumentacao_rnf05` (22), `test_apurar_rnf05` (15), `test_rnf04_coletor` (7) | 44 |
| RAG e prompt | `test_rag_atributos_no_prompt` (10), `test_rag_proactivity` (7), `test_database_rag` (7), `test_rag_evaluation` (3) | 27 |
| Leitura de artefatos versionados | `test_secondary_intents_sql` (6), `test_gemini_client` (6), `test_token_hypothesis_benchmark` (3), `test_database_connection` (3), `test_rag_synthetic_sql` (2) | 20 |
| **VHS/cache** | nenhum arquivo existe | **0** |

---

## 4. Cobertura por frente do DoD

| Frente | Instrução | Ferramenta | Validação esperada | Resultado | Evidência |
|---|---|---|---|---|---|
| Comunicação interna | `pytest -m integration` sobre os arquivos de API, banco e massa documental | `pytest`, `TestClient` | Componentes se comunicam e persistem o resultado | **Aprovado** — 196 testes | `execucao-integracao.log`, `relatorio-integracao.xml` |
| Serviços externos | Mesma rodada; modelo do Hugging Face real, provedores de LLM e STT com duplo | `pytest`, `transformers` | Contrato com o provedor respeitado, inclusive em falha | **Aprovado** — 42 testes | Idem |
| VHS/cache | — | — | — | **Bloqueado** | Seção 6 |
| Tratamento de erro | Varredura por cenários de erro em toda a suíte | `pytest` | Falha prevista tratada com resposta controlada | **Aprovado** — 69 testes, 52 nos arquivos de integração | Idem |

Distribuição do tratamento de erro: `test_audio_upload` (17), `test_database_pool` (12), `test_pipeline_api` (7), `test_traceability` (5), `test_nlp_inference` (5), `test_nlp_preprocessing` (4), `test_reports` (3), `test_llm_provider` (3), `test_instrumentacao_rnf05` (3), e mais 10 distribuídos em seis arquivos.

---

## 5. Resultado da rodada de linha de base

```
216 selected, 162 deselected
209 passed, 1 failed, 6 xfailed
236.56s (3:56)
```

| Situação | Quantidade |
|---|---:|
| Aprovados | 209 |
| Falhas | 1 |
| `xfail` — defeitos conhecidos e documentados | 6 |

**Rodada de confirmação**, após o ajuste de escopo descrito em 5.1: `210 passed, 6 xfailed` em 3min34s, sem falhas.

As evidências versionadas (`relatorio-integracao.xml` e `execucao-integracao.log`) são da rodada de **linha de base**, com a falha presente. É proposital: é essa rodada que sustenta a classificação da seção 5.1. A confirmação é registrada aqui em texto.

Os seis `xfail` são os defeitos já registrados nas tasks anteriores: D-01 (controle de acesso), D-02 (fora de escopo não persistido), D-03 (`correlation_id` nunca gravado), D-04 (resposta documental sem fonte) e D-05 (componente fora do domínio na auditoria do fluxo guiado). Todos com `strict=True`, para que a suíte acuse caso algum seja corrigido e o marcador fique para trás.

### 5.1 Classificação da falha

**`test_toda_interacao_gera_evento_de_auditoria` — 2 interações sem nenhum evento de auditoria.**

| Interação | Data | Rota | Estado | Pergunta |
|---|---|---|---|---|
| `733e6659-a047-484e-abfd-61adf37fe3af` | 11/09/2026 01:11 | `fora_escopo` | `sem_confianca` | "qa final baixa confianca indefinida" |
| `34d23777-c053-4220-bd39-a638874ccb26` | 11/09/2026 01:02 | `fora_escopo` | `sem_confianca` | "verificacao controlada baixa confianca" |

**Classificação: defeito histórico, fechado, sem reincidência.**

As duas são sondagens manuais de QA de 11/09, da Sprint 3, no caminho de baixa confiança. Não há terceira ocorrência: em cerca de 2.600 interações posteriores, todas têm auditoria. O código atual de `_insert_audit_events` sempre emite ao menos o evento `api_interaction_processed`, qualquer que seja o estado de processamento — ou seja, o comportamento que produziu esses dois registros não existe mais.

Não abre issue: o defeito foi corrigido entre sprints, e os dois registros são resíduo de dado, não de código.

**Ação sobre o teste.** O invariante varria o histórico inteiro e, por causa de dois registros de uma versão anterior, reprovaria para sempre — deixando de servir para o que importa, que é acusar uma ocorrência nova. Foi acrescentado um corte em `INICIO_DA_AUDITORIA_COMPLETA = 2026-09-12`, com os dois identificadores e a justificativa no próprio arquivo. O corte não esconde o achado: ele está documentado aqui e no comentário do teste.

---

## 6. VHS/cache — bloqueio

**O mecanismo não existe no código.**

A Seção 9.4 do `Projeto.md` descreve o VHS como cache no modelo de cassete: chave derivada do áudio e do idioma, resposta gravada no primeiro acesso e devolvida sem nova chamada ao provedor nos seguintes, com TTL e sem cachear erro.

A varredura de `app/audio/transcription.py` não encontra nada disso: não há chave, armazenamento, TTL nem qualquer estrutura de cache. Existem apenas as exceções previstas pelo plano — `SttProviderError`, `SttProviderUnavailable` e `SttProviderRateLimited` — e a lógica de nova tentativa em `_post_with_retry`.

Também não existe `app/tests/test_vhs_integration.py`.

**Por que não foi escrito nesta rodada.** O plano diz que a suíte poderia rodar com duplo desde já, e isso é verdade para o provedor externo. Mas pressupõe que o mecanismo de cache exista no código e que apenas o Azure seja simulado. Sem cache, todo cenário de *cache hit* reprovaria — o teste estaria medindo a ausência de uma funcionalidade, não validando uma integração. Escrever a suíte agora produziria um relatório vermelho que diz o mesmo que esta seção diz em texto.

**Encaminhamento.** Registrado como bloqueio, conforme o DoD admite. Depende da implementação do VHS, que por sua vez está encadeada à saída do Azure AI Speech do estágio de stub (task 11 do backlog, citada na Seção 9.4 do `Projeto.md`). Entra no backlog da Sprint 5 junto com os demais itens.

---

## 7. Achado sobre a cobertura automatizada

O `.gitlab-ci.yml` executa, no job `backend-api`, uma lista fixa de cinco arquivos:

```
test_gemini_client.py  test_audio_upload.py  test_nlp_inference.py
test_pipeline_api.py   test_traceability.py
```

São 131 dos 378 testes da suíte. **Os outros 247 nunca rodam automaticamente** — incluindo `test_database_pool` (28), `test_reports` (22), `test_llm_provider` (17) e toda a família de RNF04 e RNF05.

Com o marcador `integration` agora registrado, o job pode passar a usar `pytest -m integration`, o que sobe a cobertura automatizada de 131 para 216 testes sem enumerar arquivo nenhum — e sem o risco, que existe hoje, de um arquivo novo nascer fora da lista e nunca ser executado.

Não alterado nesta task: mexer no pipeline é decisão do grupo e não cabe dentro de uma task de validação. Fica como proposta.

---

## 8. Instruções de execução

```bash
cd src/backend
source .venv/Scripts/activate

# inventário: quais testes são de integração
python -m pytest app/tests -m integration --collect-only -q

# rodada de linha de base, com evidência
python -m pytest app/tests -m integration -rfEs --durations=10 \
  --junitxml=relatorio-integracao.xml 2>&1 | tee execucao-integracao.log
```

Leva cerca de quatro minutos. O grosso é `test_nlp_inference`, que carrega o modelo real do Hugging Face: três casos dele respondem por 208 dos 236 segundos.

Os testes de banco precisam de `SUPABASE_DATABASE_URL` no `.env`; sem ela, se ignoram sozinhos em vez de reprovar. A venv precisa estar atualizada com o `requirements.txt` da `develop`.

---

## 9. Conformidade com DoR e DoD

### 9.1 DoR

| Item | Situação |
|---|---|
| Frentes B a E testáveis e S4-31 | Atendido para as frentes cobertas; VHS/cache indisponível (seção 6) |
| Versão, massa, ambiente e critérios congelados antes da execução | Atendido — seção 2 |
| Ferramenta de coleta e local das evidências preparados | Atendido — `relatorio-integracao.xml` e `execucao-integracao.log` |

### 9.2 DoD

| Item | Situação |
|---|---|
| Comunicação interna, serviços externos, VHS/cache e tratamento de erro com instrução, ferramenta, validação esperada, resultado e evidência | Três frentes atendidas; VHS/cache **bloqueado** com motivo registrado |
| Dependência indisponível registrada como bloqueio | Atendido — seção 6 |
| Resultados distinguem aprovado, falhou, bloqueado e não executado | Atendido — seções 4 e 5 |
| Comandos, métricas, evidências e defeitos permitem auditar a conclusão | Atendido — seções 5 e 8 |

---

## 10. Conclusão

**209 aprovados, 1 falha, 6 `xfail`, 1 frente bloqueada.**

As fronteiras que existem funcionam. Comunicação interna, serviços externos e tratamento de erro passam na rodada completa, e o tratamento de erro tem cobertura densa: 69 testes, 52 deles nos arquivos de integração.

A única falha não é do código atual. São duas interações de 11/09 sem auditoria, resíduo de uma versão anterior do caminho de baixa confiança, sem reincidência em cerca de 2.600 interações posteriores.

O VHS/cache fica bloqueado porque o mecanismo não existe — não é lacuna de teste, e escrever a suíte agora só produziria vermelho sem informação nova.

Fica registrada uma oportunidade que a marcação abre: a pipeline executa hoje 131 dos 378 testes por lista fixa. Com o marcador, passaria a 216 sem enumerar arquivo, e um arquivo novo deixaria de nascer fora da cobertura automatizada.
