# S4-31 — VHS/cache de Speech-to-Text

## Escopo e integração

Fronteira: `POST /api/audio` → autenticação e validação local →
`audio.service` → `audio.transcription.transcribe` → VHS → cliente HTTP Azure.
O pipeline PLN/LLM e a auditoria continuam executando a cada upload válido.
Banco, Gemini, OpenRouter e operações de escrita do Copilot não são cacheados.

Implementação: cassetes de `Transcription` imutáveis em memória, por processo,
TTL de 300 segundos a partir do sucesso e limite LRU de 256 entradas.
Não há persistência em disco ou compartilhamento entre workers. Reiniciar o
worker descarta o cache. A chave SHA-256 incorpora bytes do áudio, URL/idioma,
formato, duração, versão do contrato e credencial; nenhum áudio ou segredo é
armazenado no cassete ou publicado nas métricas. Conforme o plano original,
áudio idêntico compartilha transcrição entre usuários autenticados no mesmo
recurso; autorização e validação sempre precedem a consulta ao cache.

`VHS_ENABLED=0` desativa o cache (rollback operacional). Ausente ou `1`, ativa.
Invalidação administrativa interna: `transcription.response_cache.invalidate()`
no processo que atende as requisições; um comando em outro processo não afeta
esse worker. Para invalidar todos os workers, reiniciar o serviço.
Mudança de recurso, credencial ou versão da chave produz miss automaticamente.
Invalidação durante uma chamada impede que a resposta antiga repovoe o cache.
Repetições simultâneas compartilham uma chamada; erros e ausência de fala nunca
são gravados. Erros continuam usando o contrato HTTP existente.

## DoR e coleta reproduzível

Executar a partir de `src/backend`, com o ambiente virtual do projeto:

```powershell
python scripts/verify_vhs.py
```

Na instalação local com `.venv` na raiz: `../../.venv/Scripts/python.exe scripts/verify_vhs.py`.
O coletor cria uma pasta nova em `docs/evidencias/sprint-04/vhs/`, congela antes
da execução o commit-base, estado da árvore, SHA-256 de código/testes/plano,
versões Python/pytest/FastAPI/httpx, SO, comando e massa em `ambiente.json`.
O hash identifica as alterações ainda não commitadas. A massa é WAV sintético
de 1 s, PCM 16 kHz/mono/16 bits, amplitudes 8000 e 4000; não representa fala real.
O provedor HTTP é controlado e contado, com retries limitados a uma tentativa.
Cache e variáveis são isolados antes de cada teste. Não são lidas credenciais
para chamadas externas nesta suíte.

Ferramentas: pytest, FastAPI TestClient, monkeypatch sobre `httpx.AsyncClient.post`,
relógio injetado para TTL e JUnit XML. Evidências: `pytest.txt`, `pytest.xml`
(assertions, tempos e propriedades) e `resultado.json` por caso.

## Critérios congelados por cenário

Todos usam o comando acima; para executar um caso isolado:
`python -m pytest app/tests/test_vhs_integration.py -v -k NOME`.
O nome abaixo é o sufixo do teste. Métricas por cenário estão no XML/JSON.

| Cenário / NOME | Critério comparado antes da classificação |
|---|---|
| `record_and_hit` | Dois uploads HTTP 200, transcrições iguais; exatamente 1 chamada HTTP, 1 miss, 1 record, 1 hit |
| `miss_different_audio` | Dois áudios distintos: 2 respostas 200, 2 chamadas e 2 misses |
| `language_and_resource_isolation` | Alterar idioma e recurso: 3 chamadas, sem reutilização indevida |
| `expiration` | Hit em 9,99 s; em 10 s, novo miss; 2 chamadas e 1 expiração |
| `invalidation` | Remoção de 1 cassete; próximo upload chama novamente; 2 chamadas, 1 invalidação |
| `provider_error_and_recovery` | HTTP 400/503/429, NoMatch, Error e JSON de tipo inválido: códigos 502/503/429/422/502/502; duas tentativas fazem 2 chamadas e zero records; recuperação seguida de hit totaliza 3 chamadas |
| `transport_failure` | Timeout → 503; JSON malformado → 502; repetição chama novamente e não grava erro |
| `disabled` | Cache desligado: 2 chamadas e zero records |
| `capacity` | Limite 1, sequência A/B/A: 3 chamadas e 2 evictions |
| `concurrent_repetitions` | Dez requisições simultâneas na camada de cache: 1 chamada, 9 coalesced, respostas iguais |
| `invalidation_during_request` | Invalidar em voo: resposta entregue, mas não gravada; próxima consulta chama novamente |

`provider_call` conta invocações lógicas ao provedor; retries internos podem
produzir mais chamadas HTTP em produção. `http_calls` mede a fronteira HTTP na
rodada controlada. `provider_error` inclui falhas técnicas, cancelamento e ausência
de fala; `expired` conta cassetes removidos pela limpeza sob demanda.
`response_cache.metrics()` entrega um snapshot cumulativo por processo; os
contadores não são expostos em endpoint público. O tempo do pytest é tempo de
teste, não latência Azure nem evidência de atendimento ao RNF05.

## Classificação e dependências

- **Aprovado:** assertions compararam observação com todos os critérios do caso.
- **Falhou:** divergência observada; traceback do XML/TXT é a evidência do defeito.
- **Bloqueado:** impedimento concreto de execução, com motivo e responsável a registrar; falha de infraestrutura do coletor não vira aprovação.
- **Não executado:** não houve execução; ausência de teste não demonstra defeito nem indisponibilidade.

S4-22 (conector/autenticação Copilot) e S4-28 (backend publicado) não são pré-requisitos
da suíte local, mas são portas de saída para aceite da integração publicada.
Seu estado não foi confirmado nesta execução; não são declaradas concluídas.
Para a próxima rodada, o responsável pela publicação deve congelar URL, versão,
número de workers, credenciais disponíveis (sem publicar valores), áudio de fala
autorizado e TTL. Executar dois uploads iguais autenticados, coletar respostas
e delta de chamadas Azure por worker; invalidar e repetir; observar códigos de
erro com falha controlada em homologação. Usar uma única réplica/worker para
comparar com o critério de exatamente uma chamada. Registrar comando sem token,
contadores, horário e evidência sanitizada. Não usar endpoint público de falha.

Copilot real, Azure real, carga RNF05 e usabilidade permanecem **não executados**
nesta rodada. Se faltar acesso durante a tentativa real, registrar **bloqueado**
com a dependência e o responsável. Os resultados controlados comprovam a
integração local de áudio/cache/cliente e preservação do contrato; não aprovam
as dependências externas ou o diagnóstico sistêmico inteiro.
