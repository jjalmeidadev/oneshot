# Evidências — Homologação do VHS com Azure AI Speech real

Plano e critérios: [plano-vhs.md](../../../testes/sprint4/plano-vhs.md), seção
"Homologação real e benefício quantitativo".
Saída sanitizada: [saida-sanitizada.txt](saida-sanitizada.txt).

A rodada local da Sprint 4 comprovou o cache contra respostas controladas do
Azure. Esta rodada repete o mesmo áudio contra o **provedor real**, com a
configuração de Azure AI Speech e de PostgreSQL do projeto, e mede o miss e os
hits separadamente.

## Resultado

**Critério congelado para cinco repetições atendido integralmente.**

| Contador | Critério do plano | Medido |
| --- | :---: | :---: |
| `provider_call` | 1 | **1** |
| `miss` | 1 | **1** |
| `record` | 1 | **1** |
| `hit` | 4 | **4** |
| `provider_error` | 0 | **0** |
| Chamadas evitadas | 4 | **4** |
| Taxa de hit | 80% | **80,00%** |

| Envio | Tipo | Latência da transcrição |
| :---: | --- | ---: |
| 1 | Miss — chamada real ao Azure | 1.540,27 ms |
| 2 | Hit — reproduzido do cache | 0,19 ms |
| 3 | Hit | 0,13 ms |
| 4 | Hit | 0,12 ms |
| 5 | Hit | 0,11 ms |

O primeiro envio paga a ida ao provedor; os quatro seguintes são servidos em
menos de 0,2 ms, sem nova chamada. As cinco transcrições são idênticas.

A cadeia completa também foi verificada: a transcrição real foi classificada
como `CONSULTA` / `consulta_status_projeto`, a interação sintética foi gravada
com `correlation_id` e auditoria, e removida do banco ao final, sem resíduo.

## Reprodutibilidade

Duas execuções independentes — o roteiro completo do plano e uma coleta isolada
do VHS, em processos distintos — produziram os mesmos hashes:

| Insumo | SHA-256 |
| --- | --- |
| Áudio | `ce6cd19e03cc1e54565d6b913ee347929be060c777f044331d18ec4a4725eb1f` |
| Transcrição | `2b07eaa35c46f892366cc0daa271163719d12c41da9e6ff55f430302d5969cbb` |

## Execução

| Item | Valor |
| --- | --- |
| Data | 3 de outubro de 2026 |
| Commit-base | `10333c4` |
| Ambiente | Python 3.13.15, macOS 26.6.2 arm64, `httpx` 0.28.1, `fastapi` 0.141.1 |
| Provedor | Azure AI Speech real, recurso do projeto, região `eastus` |
| Banco | PostgreSQL do projeto no Supabase |
| Áudio | Fala sintetizada em português do Brasil, WAV PCM 16 bits, 16 kHz, mono, 4,6 s. Não versionado |

Comando do roteiro, a partir de `src/backend`:

```bash
python scripts/verify_audio_stt_pln_live.py <audio.wav> \
  --expected-term <termo-esperado> --repetitions 5
```

A coleta isolada chama `app.audio.transcription.transcribe` cinco vezes sobre o
mesmo áudio, com o cache invalidado antes do primeiro envio, e registra o delta
dos contadores de `ResponseCache.snapshot()`. Ela existe porque o roteiro
completo publica as razões agregadas, e o critério do plano é expresso contador
a contador.

## Escopo desta evidência

A rodada foi executada a partir do ambiente local de desenvolvimento, contra o
Azure e o PostgreSQL reais. O plano reserva a classificação de homologação
aprovada para a execução do mesmo comando na imagem publicada; essa execução
acontece com a publicação da versão final, usando este mesmo roteiro e este
mesmo critério.

Nenhuma chave, token, áudio ou transcrição em texto é publicado. A saída
sanitizada contém apenas hashes, contadores e latências.
