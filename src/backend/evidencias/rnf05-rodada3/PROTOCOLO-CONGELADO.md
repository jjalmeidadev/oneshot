# RNF05 — 3ª rodada: protocolo congelado antes da execução

**Congelado em:** 2026-09-22T22:22:50Z, antes de iniciar qualquer instância da API.
**Código medido:** base `81c787d` com as alterações da branch
`test/executar-rnf04-rnf05`, hash de `src/backend/app`:

```
71ee4895d5c3d65f2d3199a3edaa28a0149d2f9a7eb96cce69e095440b99ff41
```

Calculado com o mesmo comando registrado em
[`campanha-37flash/arvore-medida.md`](../campanha-37flash/arvore-medida.md).

## Por que existe uma 3ª rodada

A 2ª rodada ([`rnf05-rodada2/`](../rnf05-rodada2/RELATORIO.md)) reprovou por dois
critérios: um erro na linha de base, causado por uma gravação de auditoria presa
no banco por mais de 60 s, e o P95 da consulta simples sob carga, 11.000 ms contra
o teto de 10.000 ms.

Esta rodada mede **uma única correção**, feita depois da 2ª rodada e antes deste
congelamento:

| Correção | Arquivo |
| --- | --- |
| Limite de tempo de 5 s por consulta ao banco (`statement_timeout`), aplicado a cada conexão nova, e *keepalive* de TCP nas conexões | `app/database/connection.py` |

Verificada contra o Supabase antes do congelamento, com o pool ligado e desligado:
`SHOW statement_timeout` devolve `5s`, os parâmetros de *keepalive* chegam à
conexão e `pg_sleep(6)` é cancelada pelo servidor em 5,3 s.

A gravação da auditoria continua síncrona, no caminho da resposta. Movê-la para
fora desse caminho muda a semântica do RNF03 e não faz parte desta rodada.

**As rodadas anteriores continuam registradas como não atendidas.** Esta rodada não
as substitui nem as apaga; o resultado desta será publicado ao lado delas,
qualquer que seja.

## Critérios — iguais aos das rodadas anteriores

| Critério | Valor |
| --- | --- |
| P95 da consulta simples | ≤ 10.000 ms |
| P95 da comparação | ≤ 20.000 ms |
| Erros HTTP ou de contrato | zero |
| Amostra mínima por tipo de consulta | 40 |
| Rodadas positivas | as duas precisam ser aprovadas |

Nenhum teto foi alterado.

## Método — igual ao da 2ª rodada

| Item | Valor |
| --- | --- |
| Aquecimento | `aquecer.py`, fora da janela de medição |
| Linha de base | 1 usuário, 25 min |
| Carga | 5 usuários, 8 min |
| Negativa | 5 usuários, 6 min, só comparação, atraso de 25 s em todos os prompts de comparação |
| Massa e proporção | `prompts.py`, 75% simples e 25% comparação, espera de 1 a 3 s |
| Provedor | `google/gemini-3.7-flash` pelo OpenRouter, plano pago |
| API | configuração de produção: 3 retentativas, *timeout* de 30 s por chamada ao provedor, pool de conexões ligado |
| Apuração | `apurar_rnf05.py` |

## Regra de decisão — a mesma da 2ª rodada

1. Qualquer erro em rodada positiva: **não atendido**.
2. Alguma rota com menos de 40 amostras: **inconclusivo**. A rodada é estendida,
   e o resultado inconclusivo é publicado junto.
3. P95 acima do teto em qualquer rota: **não atendido**.
4. Todas as rotas das duas rodadas positivas aprovadas: **atendido**.
5. Cenário negativo: precisa **reprovar** (P95 comparativo acima de 20 s). Se
   aprovar, a medição é considerada incorreta e as rodadas positivas não valem.

## Diferença para o manifesto da 2ª rodada

```
< fa7133bd6fbd03dec33de9033af218e71748f6ae32cea335d63f3fe95ab19300  src/backend/app/database/connection.py
> 1b0f2e8e32368f038f5cb985052e916cee330757b3aefe98da79c1e98e04ecf0  src/backend/app/database/connection.py
< 8fbb1e29ad3a759546a626ebceeed6adf735ac5073285090a9223148b1c4c3aa  src/backend/app/tests/conftest.py
> a44feeff09b4aa2a99849df9b727899bdb5e4e4c2950144580a3618f4b2936c0  src/backend/app/tests/conftest.py
< cf03870acbb69a2544c0004b9fa8751ddf0e567dc05f042912b3d31ab0b871b9  src/backend/app/tests/test_database_pool.py
> 55a23e79ee2439ae31a1b1367457b3cff98c4e9714d3356fa543571c6e086445  src/backend/app/tests/test_database_pool.py
```

`conftest.py` e `test_database_pool.py` são testes e não rodam na API.

## Manifesto por arquivo

```
01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b  src/backend/app/__init__.py
6d95f8381763a9e03f0152e8d5420f04dcbc3a2971515fbb6200d2142c16353c  src/backend/app/audio/errors.py
3ba889f32a1d32778e1dfc1008bd45a40e0d8d55d6fe4b2dcb65ad581adf863f  src/backend/app/audio/schemas.py
9824ed3ddd20b1f5a1939a2fda0fcbbdf65dff175426e8d9923401e192a9c517  src/backend/app/audio/security.py
844dde000296dc85bad84f3cd4d6e3d1a85543fc114babd12422909c638cafa6  src/backend/app/audio/service.py
7fe2b30e9fb1feb53f5beaed6e2cc1e2b2058cd6019ef09fac97ec44bdb95fcc  src/backend/app/audio/transcription.py
2f4a165959a045e5f7df611df7f49026c735a80789f46557b87d6bd7282ee0e8  src/backend/app/audio/validation.py
73c267a3c05926fc9514f2db050ab6fa198334a1b68e274bf2c3b5db9dc2e954  src/backend/app/database/__init__.py
1b0f2e8e32368f038f5cb985052e916cee330757b3aefe98da79c1e98e04ecf0  src/backend/app/database/connection.py
8696d862d5174b88a4f62fbb5c2d318a93caaf3a84128f7b6540705ba6d9dbb0  src/backend/app/database/tracing.py
d6e012c4c1c8d12530e1dabde58b1ca0376479bbabc20ff533f779ca4f54b2ab  src/backend/app/gemini/__init__.py
89dec67851822be1b7700d951aa18274d468092b70f1c90d799ea133b56528b9  src/backend/app/gemini/client.py
142d9e29cbfa30cba40b7216ae8949f3adae0dbe6632e1ff85fec203a1858ef2  src/backend/app/gemini/schemas.py
7a21bcbb1dfb6bcef97f81ef12c23ce38c70c9f812ddeeec1517d609615bca52  src/backend/app/main.py
c894efcf3a449560240340203982da1eb66947078ef689d44ff007787951d331  src/backend/app/nlp/__init__.py
fe6cc5b10f26c7487185bb8e59b5129645aa1454d988a3c39185c7226a07d7e6  src/backend/app/nlp/classifier.py
d2e54505652ef33b596a779520415d3dba133fc0394a70a38e5c7cd7eeeaf67a  src/backend/app/nlp/data/lexico_dominio.json
80f2d695daccf5b951cb7a4cade0e146f6308d3f96b5cd17b406d5b6be7cda87  src/backend/app/nlp/entities.py
6465333b8187021442907c96394f735f1a1c52a39ecf92054b8ca5e77cb8b1aa  src/backend/app/nlp/inference.py
cc6aaad379d069000f118a194879bb46b8eff2390ec95b55fa9ccc3c087b77b4  src/backend/app/nlp/preprocessing.py
d8a1611b5988ae734c9ccaf003c32ac7182d570beecd81edb1c4455edf09f85e  src/backend/app/nlp/schemas.py
9a72db1ec5844ff7d6b710a7391c304126bb04ba361bbd10b06c307fd9830cc1  src/backend/app/pipeline.py
6eab0635ef8c40cb618767478a8f6e1044112791fa435df4f6e14dff26b151f7  src/backend/app/rag/__init__.py
9bc8fbdc35f5fc6ce9f92743b6459503bc4dae7dfacc10c8429cabad27a8c18a  src/backend/app/rag/data/secondary_intents.json
850a4f06fef9a1032164ed8cbd3d0f805f8dcdfb8b67cd28accf1fd0b7e70e8d  src/backend/app/rag/data/sharepoint/README.md
cc1f57689bd3c7b6f6b94cce434e789c2d31af464d69b6025dc9a886d225bb64  src/backend/app/rag/data/sharepoint/base_atendimento.json
32c52074cac7d9a5d7f1ad6ea13cb1011d4f875e08e53217da685e0555a64060  src/backend/app/rag/data/sharepoint/comunicados_servico.json
c6f51b402bff41985f5d936907ec586e61e15be878525356c91e07564091492f  src/backend/app/rag/data/sharepoint/procedimentos_operacionais.json
276f98f0009c4a563694ec7ed0756046f359cf86b0f9ad41358e4550498709a8  src/backend/app/rag/database.py
5b97285633d96426b4ea958eb155ec84dd55d13af19bbed12288ea5aa53b887e  src/backend/app/rag/proactive_confirmation.py
8b0a07e915a51361f50281d680e169cc01417e290d8de26e050c26e7e17ff570  src/backend/app/rag/proactivity.py
51aed036a47e5762050449c94b56d38813079fd947c8faed5842e46805331f99  src/backend/app/rag/sharepoint.py
a44feeff09b4aa2a99849df9b727899bdb5e4e4c2950144580a3618f4b2936c0  src/backend/app/tests/conftest.py
57d3c34869fa3f202160ff6f9fbe3d475f7bbd59e1e5cbbd6d62abbbae31f13a  src/backend/app/tests/e2e_server.py
c4f1a4c83c6e14deaf02ad95b612173c142aad301294eab0fff8bb17561bf457  src/backend/app/tests/executar_rodada_rnf.sh
2662c1e27520b38c4998ba2213759afe481f89c7ae73d628506ea694e0728a8d  src/backend/app/tests/performance/README.md
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  src/backend/app/tests/performance/__init__.py
447bb225f149ed1bfd6c15e9c48aceb85f5322ed46ded152f501e3d4dc258532  src/backend/app/tests/performance/api_com_atraso.py
133a613e9db80ab8a0d72a4d17ac2dee465e3fc97849b1abf214926e53ffa194  src/backend/app/tests/performance/apurar_rnf05.py
4d88db557b506cf3e70cdfea726b3beb12d05bc40fd0909984d8beb85b9e4403  src/backend/app/tests/performance/aquecer.py
aaa69e48f16398e6ad0367f21ebca6534b8863a8e8d7c9b5921171d297a373d6  src/backend/app/tests/performance/locustfile.py
62898b3cefc93e0f4f6e56bea77111f121fdfa6d2a963f8d500de83f8b34345e  src/backend/app/tests/performance/prompts.py
1ff09c666fcad095ae4c1612899924e370ad806254f9bea13c4f67510f1151e8  src/backend/app/tests/performance/registrar_ambiente.py
ab8fe9800a46543c51a753482497637b369fe7844a024915e04a892545ce7440  src/backend/app/tests/rnf04/README.md
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  src/backend/app/tests/rnf04/__init__.py
9da017ef37ab6974d7b1c2d74f3f6e50d9b040a092a91a3f570a403b7d82fba6  src/backend/app/tests/rnf04/amostra_congelada.json
0fd81719336216dda6677eca2daf78bcde0750ae5b23b479c060c3e1cef6e956  src/backend/app/tests/rnf04/avaliar_rnf04.py
2b686382bc08faeb97155f05a06c4d0de881cd68102d993b2403fe00d252db35  src/backend/app/tests/rnf04/executar_rnf04.py
16eb1ece2e44e9af7d3f8be8a360b075fd849f013879c339c28f4e44b391d217  src/backend/app/tests/test_apurar_rnf05.py
dbe199ef6f9643280689cbe25be6f4286c17d0f32f6a577440888c5b4530fe4f  src/backend/app/tests/test_audio_upload.py
2e898afaaf7c76e73a9109e60dcc37ca6ef99cb490557f7db0f91f04de12a566  src/backend/app/tests/test_database_connection.py
55a23e79ee2439ae31a1b1367457b3cff98c4e9714d3356fa543571c6e086445  src/backend/app/tests/test_database_pool.py
9d2044546c249adc7a3d155322a4b65d8bef48f301aba875e54ab383f050610d  src/backend/app/tests/test_database_rag.py
75ce3e33ced85b0bbf2eb3ecb23275c9e2e52b3c6bbfced41e4cebda2c21d8e4  src/backend/app/tests/test_gemini_client.py
e4da131ca94a29847945fce1e2e611120fa8c70e499e6792de449591c9db9c2b  src/backend/app/tests/test_instrumentacao_rnf05.py
e12177b923fb94dd4ed2d747f967d9d573ebf96494a034be1b08ac64fc9ce45a  src/backend/app/tests/test_llm_provider.py
f724ba91fd758864729f7ca675413ae751a2e7c131f11591c32cbed5a867ebd3  src/backend/app/tests/test_nlp_classifier.py
fd9661c702bf7907d81533a4a03d38bfac7c4ebefe59c0e1411a655f6120011e  src/backend/app/tests/test_nlp_entities.py
20668133541440a7f078b15a1619d94af6eac8cfad6b83e30a2ffc6837ed9e36  src/backend/app/tests/test_nlp_inference.py
aa9465eb080ebe08f0cded41b41443a2626e74358da1c3f3c34b94b94d5de1a5  src/backend/app/tests/test_nlp_preprocessing.py
528fb54a62bfd563e1f736d564f58745273290105344551b887bd36070fd8b80  src/backend/app/tests/test_pipeline_api.py
f629183c4d1d0aa363efe7a2f70d4bb6108aa007784ed72a8c8fb6d6483df71a  src/backend/app/tests/test_rag_atributos_no_prompt.py
dbae562adb07e3142682c64b7d85cee9aae8661501c7ffa70fabc94e7f574c69  src/backend/app/tests/test_rag_proactivity.py
ccb121d7150709930ed3b96d99dce39301525261a4aca6b50f1eca016402b329  src/backend/app/tests/test_rag_synthetic_sql.py
9dd835cc6c367212850b7082c11fdd39862fb42a314be0ad030a5bdfe75295e9  src/backend/app/tests/test_rnf04_coletor.py
b710cdd1cfcf1b21648918fba9d5dcdf8293233f748fe4fb78146a547be38656  src/backend/app/tests/test_secondary_intents_sql.py
61193b59c5bc2abc6b606d582d9fcfcc3380447080e34b8e1e336a44e41fa3ab  src/backend/app/tests/test_sharepoint_rag.py
219f3907551590a696fbec938726013f57def6278fc38a857d91efd1e79b129a  src/backend/app/tests/test_traceability.py
```
