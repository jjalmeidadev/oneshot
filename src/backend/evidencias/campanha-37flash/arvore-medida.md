# Impressao digital do codigo medido

Base commitada: 81c787d (test/executar-rnf04-rnf05)
Registrado em: 2026-09-22T18:54:18Z, antes das rodadas desta campanha

Os testes desta campanha rodaram sobre a base acima MAIS alteracoes ainda nao
commitadas no momento da medicao:

```
 M src/backend/app/gemini/client.py
 M src/backend/app/rag/database.py
 M src/backend/app/rag/sharepoint.py
 M src/backend/app/tests/test_database_rag.py
?? src/backend/app/tests/conftest.py
?? src/backend/app/tests/executar_rodada_rnf.sh
?? src/backend/app/tests/performance/
?? src/backend/app/tests/rnf04/
?? src/backend/app/tests/test_llm_provider.py
?? src/backend/app/tests/test_rag_atributos_no_prompt.py
?? src/backend/app/tests/test_rnf04_coletor.py
```

## Hash do codigo medido

```
1ef17e89981f4846ac3f7bd53ce955f44f4d4b0a9397ddbf663135702840e1a7
```

Cobre todos os arquivos de src/backend/app (aplicacao e testes), rastreados
ou nao, excluindo o que o .gitignore ignora. Evidencias e .env ficam fora.

## Como conferir depois do commit

Em um checkout limpo do commit, a partir da raiz do repositorio:

```bash
git ls-files --cached --others --exclude-standard -- src/backend/app \
  | LC_ALL=C sort | while read f; do shasum -a 256 "$f"; done \
  | shasum -a 256
```

O resultado so e igual ao hash acima se o commit contiver exatamente o codigo
que foi medido.

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
8dda97c959f45078b83f4fb9b9d955e0a575b0259f041ce324b2d73340f1ebb1  src/backend/app/database/connection.py
8696d862d5174b88a4f62fbb5c2d318a93caaf3a84128f7b6540705ba6d9dbb0  src/backend/app/database/tracing.py
d6e012c4c1c8d12530e1dabde58b1ca0376479bbabc20ff533f779ca4f54b2ab  src/backend/app/gemini/__init__.py
315ca54d390f402ba44ca6f2ee4e6921935d3f6143c078ea51a96e4db913a0d6  src/backend/app/gemini/client.py
142d9e29cbfa30cba40b7216ae8949f3adae0dbe6632e1ff85fec203a1858ef2  src/backend/app/gemini/schemas.py
53560f4c5de9613bb4881aa42aa65d030a9a6786a6487bd040ef3843bf6058fe  src/backend/app/main.py
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
6e323da143a0dc2340f7ce65f0f0d09ee0a45bdc907fab14d1892baa012d1692  src/backend/app/tests/conftest.py
57d3c34869fa3f202160ff6f9fbe3d475f7bbd59e1e5cbbd6d62abbbae31f13a  src/backend/app/tests/e2e_server.py
0b1fd011260e7c66ee88a499883254b4ff88a32b8fc033d5e1b5a88d87028383  src/backend/app/tests/executar_rodada_rnf.sh
fc5d5c46714299cb8d323b502e50203b5a887c674d0d966fa75e78301041809f  src/backend/app/tests/performance/README.md
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  src/backend/app/tests/performance/__init__.py
bb9bcff66be2fc2420aa3dfc271e99a62e6c9d2180cf51b7ca9bdcdc6e9ee921  src/backend/app/tests/performance/api_com_atraso.py
64234844c8f8da8f6b12c3431b49dfad246f1fb555d7fb8b8af8c8cacdaf8778  src/backend/app/tests/performance/locustfile.py
62898b3cefc93e0f4f6e56bea77111f121fdfa6d2a963f8d500de83f8b34345e  src/backend/app/tests/performance/prompts.py
1a72859885f2a29eb78c277643b650a1a879a9d66ac07939bbad8c5f3e75f8aa  src/backend/app/tests/performance/registrar_ambiente.py
8c72edceb6361ebaad0604ccc0d96ff98bdb06dfe34c21983530cdb1b0d4912c  src/backend/app/tests/rnf04/README.md
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  src/backend/app/tests/rnf04/__init__.py
9da017ef37ab6974d7b1c2d74f3f6e50d9b040a092a91a3f570a403b7d82fba6  src/backend/app/tests/rnf04/amostra_congelada.json
0fd81719336216dda6677eca2daf78bcde0750ae5b23b479c060c3e1cef6e956  src/backend/app/tests/rnf04/avaliar_rnf04.py
4a6fcbe0ea1205783ac38512da7809baf3a6cf9b95398fb91cdb6de4a54ce819  src/backend/app/tests/rnf04/executar_rnf04.py
dbe199ef6f9643280689cbe25be6f4286c17d0f32f6a577440888c5b4530fe4f  src/backend/app/tests/test_audio_upload.py
2e898afaaf7c76e73a9109e60dcc37ca6ef99cb490557f7db0f91f04de12a566  src/backend/app/tests/test_database_connection.py
9d2044546c249adc7a3d155322a4b65d8bef48f301aba875e54ab383f050610d  src/backend/app/tests/test_database_rag.py
75ce3e33ced85b0bbf2eb3ecb23275c9e2e52b3c6bbfced41e4cebda2c21d8e4  src/backend/app/tests/test_gemini_client.py
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

## Duas versoes medidas nesta campanha

| Medicao | Hash do codigo | O que mudou |
| --- | --- | --- |
| RNF04 (24 perguntas) | `1ef17e89981f4846ac3f7bd53ce955f44f4d4b0a9397ddbf663135702840e1a7` | versao registrada acima |
| RNF05, 1a rodada (linha de base, carga e negativa) | `c2cb357a8f5957450189fe526cb2730b3197bb3b87ae4de6c236c3ea47f44324` | pool de conexoes com o Supabase e aquecimento fora da janela do Locust |

O pool so altera o tempo de acesso ao banco: nao muda o que e recuperado nem o
que o modelo responde. Por isso o resultado do RNF04, medido antes dele, continua
valendo para o codigo final quanto a fundamentacao e alucinacao.

O manifesto por arquivo acima corresponde a versao do RNF04. Para conferir a
versao do RNF05, rodar o mesmo comando sobre o commit que contem o pool.

## Manifesto por arquivo da versao do RNF05 (`c2cb357a...`)

Gravado antes de qualquer edicao posterior a medicao. Arquivos que aparecerem
com hash diferente no commit foram alterados depois das rodadas; a lista e a
natureza dessas alteracoes estao no relatorio do RNF05.

```
01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b  src/backend/app/__init__.py
6d95f8381763a9e03f0152e8d5420f04dcbc3a2971515fbb6200d2142c16353c  src/backend/app/audio/errors.py
3ba889f32a1d32778e1dfc1008bd45a40e0d8d55d6fe4b2dcb65ad581adf863f  src/backend/app/audio/schemas.py
9824ed3ddd20b1f5a1939a2fda0fcbbdf65dff175426e8d9923401e192a9c517  src/backend/app/audio/security.py
844dde000296dc85bad84f3cd4d6e3d1a85543fc114babd12422909c638cafa6  src/backend/app/audio/service.py
7fe2b30e9fb1feb53f5beaed6e2cc1e2b2058cd6019ef09fac97ec44bdb95fcc  src/backend/app/audio/transcription.py
2f4a165959a045e5f7df611df7f49026c735a80789f46557b87d6bd7282ee0e8  src/backend/app/audio/validation.py
73c267a3c05926fc9514f2db050ab6fa198334a1b68e274bf2c3b5db9dc2e954  src/backend/app/database/__init__.py
fa7133bd6fbd03dec33de9033af218e71748f6ae32cea335d63f3fe95ab19300  src/backend/app/database/connection.py
8696d862d5174b88a4f62fbb5c2d318a93caaf3a84128f7b6540705ba6d9dbb0  src/backend/app/database/tracing.py
d6e012c4c1c8d12530e1dabde58b1ca0376479bbabc20ff533f779ca4f54b2ab  src/backend/app/gemini/__init__.py
315ca54d390f402ba44ca6f2ee4e6921935d3f6143c078ea51a96e4db913a0d6  src/backend/app/gemini/client.py
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
8fbb1e29ad3a759546a626ebceeed6adf735ac5073285090a9223148b1c4c3aa  src/backend/app/tests/conftest.py
57d3c34869fa3f202160ff6f9fbe3d475f7bbd59e1e5cbbd6d62abbbae31f13a  src/backend/app/tests/e2e_server.py
0b1fd011260e7c66ee88a499883254b4ff88a32b8fc033d5e1b5a88d87028383  src/backend/app/tests/executar_rodada_rnf.sh
fc5d5c46714299cb8d323b502e50203b5a887c674d0d966fa75e78301041809f  src/backend/app/tests/performance/README.md
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  src/backend/app/tests/performance/__init__.py
bb9bcff66be2fc2420aa3dfc271e99a62e6c9d2180cf51b7ca9bdcdc6e9ee921  src/backend/app/tests/performance/api_com_atraso.py
4d88db557b506cf3e70cdfea726b3beb12d05bc40fd0909984d8beb85b9e4403  src/backend/app/tests/performance/aquecer.py
aaa69e48f16398e6ad0367f21ebca6534b8863a8e8d7c9b5921171d297a373d6  src/backend/app/tests/performance/locustfile.py
62898b3cefc93e0f4f6e56bea77111f121fdfa6d2a963f8d500de83f8b34345e  src/backend/app/tests/performance/prompts.py
1ff09c666fcad095ae4c1612899924e370ad806254f9bea13c4f67510f1151e8  src/backend/app/tests/performance/registrar_ambiente.py
8c72edceb6361ebaad0604ccc0d96ff98bdb06dfe34c21983530cdb1b0d4912c  src/backend/app/tests/rnf04/README.md
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  src/backend/app/tests/rnf04/__init__.py
9da017ef37ab6974d7b1c2d74f3f6e50d9b040a092a91a3f570a403b7d82fba6  src/backend/app/tests/rnf04/amostra_congelada.json
0fd81719336216dda6677eca2daf78bcde0750ae5b23b479c060c3e1cef6e956  src/backend/app/tests/rnf04/avaliar_rnf04.py
2b686382bc08faeb97155f05a06c4d0de881cd68102d993b2403fe00d252db35  src/backend/app/tests/rnf04/executar_rnf04.py
dbe199ef6f9643280689cbe25be6f4286c17d0f32f6a577440888c5b4530fe4f  src/backend/app/tests/test_audio_upload.py
2e898afaaf7c76e73a9109e60dcc37ca6ef99cb490557f7db0f91f04de12a566  src/backend/app/tests/test_database_connection.py
cf03870acbb69a2544c0004b9fa8751ddf0e567dc05f042912b3d31ab0b871b9  src/backend/app/tests/test_database_pool.py
9d2044546c249adc7a3d155322a4b65d8bef48f301aba875e54ab383f050610d  src/backend/app/tests/test_database_rag.py
75ce3e33ced85b0bbf2eb3ecb23275c9e2e52b3c6bbfced41e4cebda2c21d8e4  src/backend/app/tests/test_gemini_client.py
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

## O que mudou depois das rodadas do RNF05

Diferenca entre o manifesto acima e o codigo commitado. Nenhuma alteracao
muda o que as rodadas mediram: sao registro em log, instrumento de teste,
apuracao para a proxima sprint e documentacao.

| Arquivo | Situacao | Natureza |
| --- | --- | --- |
| `src/backend/app/gemini/client.py` | alterado | log de novas tentativas e de truncamento; nenhuma mudanca de comportamento |
| `src/backend/app/tests/executar_rodada_rnf.sh` | alterado | roteiro, nao executado nas rodadas; linha de base de 25 min e apuracao pelo protocolo revisado |
| `src/backend/app/tests/performance/README.md` | alterado | documentacao |
| `src/backend/app/tests/performance/api_com_atraso.py` | alterado | duplo compara com a lista exata de prompts |
| `src/backend/app/tests/rnf04/README.md` | alterado | documentacao |
| `src/backend/app/tests/performance/apurar_rnf05.py` | novo | apurador do protocolo revisado; escrito depois da 1a rodada, que foi apurada pela leitura dos CSVs, e usado na 2a e na 3a |
| `src/backend/app/tests/test_apurar_rnf05.py` | novo | testes do apurador |
| `src/backend/app/tests/test_instrumentacao_rnf05.py` | novo | testes das correcoes de instrumentacao |

## Rodadas seguintes do RNF05

A 2a e a 3a rodadas tem impressao digital e manifesto por arquivo proprios,
gravados antes da execucao no `PROTOCOLO-CONGELADO.md` de cada uma:
[`rnf05-rodada2/`](../rnf05-rodada2/PROTOCOLO-CONGELADO.md) (`10f53523...`) e
[`rnf05-rodada3/`](../rnf05-rodada3/PROTOCOLO-CONGELADO.md) (`71ee4895...`). O
codigo da 3a rodada e o que foi commitado; o commit exato esta no
[`README.md`](../README.md) deste diretorio.
