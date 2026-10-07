# S5-32 (#286) — RNF10 a RNF12

Data da execução: 07/10/2026, America/Sao_Paulo. Critérios: Seções 9.2.2 e
9.2.3 de `docs/Projeto.md`. Execução automatizada assistida por IA; revisão
humana de outra frente: pendente.

**Resultado: 5 aprovados e 1 reprovado.** RNF10 e RNF12 aprovados nos dois
sentidos. RNF11 aprovado no positivo e reprovado no negativo, pelo defeito
`DEF-S5-32-01`. Nenhum caso ficou sem execução.

## Ambiente e rastreabilidade

Base: commit `84df352b8d03fd206fe811e2462c4b05c05775b1` da `develop`, a mesma
da [pipeline #89702](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/pipelines/89702),
verde nos quatro jobs. O [manifesto da rodada 01](../../../src/backend/evidencias/rnf10-rnf12/rodada-01/manifesto.json)
registra versões, plataforma, estado da árvore, comando e SHA-256 dos arquivos
usados. Esta entrega acrescenta testes, o validador da massa, o executor da
rodada e documentação, sem alterar o produto.

A API foi iniciada em processo por `FastAPI TestClient`, com ciclo de vida.
Não houve banco, rede, provedor de LLM nem `.env`: `PYTHON_DOTENV_DISABLED=1` e
a fixture `ambiente_isolado` neutralizaram configurações locais. Provedor e
fonte foram substituídos por duplos **na fronteira** (`urlopen`, diretório da
fonte, `classify`), para que o tratamento de erro real do backend fosse
exercitado. As mutações dos negativos ocorreram em cópias temporárias, e os
originais foram relidos no fim para provar que ficaram intactos.

Para reproduzir, a partir de `src/backend`:

```bash
python -m scripts.run_s5_32 --round rodada-02          # rodada completa com evidências
python -m pytest app/tests/test_rnf10_rnf12_s5_32.py   # só os casos
python -m scripts.validar_massa_sintetica              # só o validador (exit 1 se faltar categoria)
```

Os casos são marcados como `integration`. Como o job `backend-api` enumera
os arquivos de teste, `test_rnf10_rnf12_s5_32.py` foi incluído nessa lista
junto com a S5-23.

## Seis casos

| Caso | Resultado observado | Ferramenta | Evidência |
|---|---|---|---|
| CT-RNF10-P | **Aprovado.** Os sete itens do checklist passaram: a interface (`main.py`, `*/router.py`, `security/http.py`) não acessa banco nem rede diretamente; negócio e dados não dependem do framework web; o driver PostgreSQL só aparece na camada de dados; o frontend só chama a API por `src/lib/api`; o README tem instalar, executar e testar; `/openapi.json` é válido, com 35 operações e todas com resposta documentada, e `/docs` responde 200; há 41 arquivos de teste no backend, 24 no frontend e 3 specs E2E. O README foi seguido em ambiente limpo: 717 testes aprovados, e as 6 falhas não vêm do README (3 exigem `torch`, aprovados na pipeline; 3 são as falhas já conhecidas da S5-31). | `pytest`, análise estática de imports (`ast`), TestClient, modelo OpenAPI do FastAPI | [Checklist](../../../src/backend/evidencias/rnf10-rnf12/rodada-01/CT-RNF10-P.json), [reprodução do README](../../../src/backend/evidencias/rnf10-rnf12/rodada-01/reproducao-readme/README.md) |
| CT-RNF10-N | **Aprovado.** Cópia do README sem a instrução de teste: o checklist acusou `executar os testes`. Cópia de `reports/router.py` com `import httpx`, `import psycopg` e chamada externa na rota: o checklist acusou acesso direto e driver fora da camada de dados. A estrutura real continuou sem violações e com hashes inalterados. | `pytest`, mesmo checklist do positivo, cópias temporárias | [Violações detectadas](../../../src/backend/evidencias/rnf10-rnf12/rodada-01/CT-RNF10-N.json) |
| CT-RNF11-P | **Aprovado.** As cinco falhas previstas responderam com código e mensagem definidos, registro de auditoria e nada sensível na resposta ou no log: falha de classificação → 503; ausência de resultado → 200 com a resposta de fora de escopo, sem chamar o provedor; fonte indisponível → 503; *timeout* do provedor → 502; provedor 5xx → 502, sem o corpo bruto do provedor. | `pytest`/TestClient, duplos na fronteira, `caplog` | [Classificação](../../../src/backend/evidencias/rnf10-rnf12/rodada-01/CT-RNF11-P-falha_de_classificacao.json), [sem resultado](../../../src/backend/evidencias/rnf10-rnf12/rodada-01/CT-RNF11-P-ausencia_de_resultado.json), [fonte](../../../src/backend/evidencias/rnf10-rnf12/rodada-01/CT-RNF11-P-fonte_indisponivel.json), [timeout](../../../src/backend/evidencias/rnf10-rnf12/rodada-01/CT-RNF11-P-timeout_do_provedor.json), [5xx](../../../src/backend/evidencias/rnf10-rnf12/rodada-01/CT-RNF11-P-provedor_5xx.json) |
| CT-RNF11-N | **Reprovado (DEF-S5-32-01).** Com payload inválido do provedor, a resposta foi controlada: 502, mensagem definida, falha auditada e nenhum vazamento. Com exceção inesperada, nada sensível vazou, mas a API devolveu o `Internal Server Error` genérico do Starlette em texto puro, sem mensagem definida pelo projeto, e a interação não foi auditada. O critério exige os dois. | `pytest`/TestClient com `raise_server_exceptions=False`, `caplog`; caso registrado como `xfail(strict=True)` | [Payload inválido](../../../src/backend/evidencias/rnf10-rnf12/rodada-01/CT-RNF11-N-payload_invalido.json), [exceção inesperada](../../../src/backend/evidencias/rnf10-rnf12/rodada-01/CT-RNF11-N-excecao_inesperada.json) |
| CT-RNF12-P | **Aprovado.** As seis categorias estão na massa versionada: 3 projetos, 1 subportfólio, 10 marcos, 10 riscos, 17 indicadores (9 de avanço físico/econômico e 8 de benefícios) e 9 documentos (3 listas simuladas do SharePoint com 3 itens cada). | `scripts/validar_massa_sintetica.py` | [Relatório do validador](../../../src/backend/evidencias/rnf10-rnf12/rodada-01/validador-massa.json), [observação do caso](../../../src/backend/evidencias/rnf10-rnf12/rodada-01/CT-RNF12-P.json) |
| CT-RNF12-N | **Aprovado.** Seis cópias temporárias, cada uma sem uma categoria. Todas foram reprovadas, e o relatório apontou exatamente a categoria removida. A massa oficial continuou aprovada e com os mesmos hashes. | `pytest` + validador sobre cópias | [Seis cópias](../../../src/backend/evidencias/rnf10-rnf12/rodada-01/CT-RNF12-N.json) |

## Versão da massa validada

O validador identifica a massa pelo SHA-256 dos arquivos lidos. Os hashes desta
rodada estão no [relatório do validador](../../../src/backend/evidencias/rnf10-rnf12/rodada-01/validador-massa.json):
cargas `02_initial_data.sql`, `04_rag_synthetic_data.sql` e
`13_seed_portfolio_report_data.sql`, e as três listas de
`app/rag/data/sharepoint`.

As contagens são as linhas **declaradas** nas cargas (tuplas de `VALUES` ou
ramos de `SELECT ... UNION ALL`), sem consulta ao banco. Os documentos são
contados nos JSONs, porque `04_rag_synthetic_data.sql` deriva deles os
`project_artifacts` e `source_extracts`. Quando a S5-12 ampliar o SharePoint
simulado, basta executar o validador de novo.

## Defeito encontrado

| ID | Caso | Descrição | Impacto | Destino proposto |
|---|---|---|---|---|
| DEF-S5-32-01 | CT-RNF11-N | `POST /api/chat` só trata `GeminiConfigurationError`, `GeminiAPIError` e falha de armazenamento de confirmações. Uma exceção sem tratador registrado na aplicação escapa do pipeline antes do `_trace_safely`: a resposta é o 500 genérico do Starlette (`text/plain`, sem envelope do projeto) e a interação não chega à auditoria. Em execução real, o Uvicorn também grava o *traceback* completo no log do servidor. | O usuário recebe um erro sem orientação, e a falha some do registro exigido pelo RNF03. Nesta rodada, nenhum segredo apareceu na resposta. | Tratador global de exceções na API, com envelope padrão (`503`/`500` + mensagem definida) e registro da falha na auditoria. Fica para a consolidação (S5-36, #290) decidir entre corrigir na sprint ou registrar como defeito remanescente. |

## Abrangência e limites

- O RNF10 foi verificado por evidência estrutural objetiva (imports, README,
  contrato e testes). Não mede complexidade nem duplicação de código.
- O README foi reproduzido em Linux. O passo de `requirements-pln.txt` não
  rodou neste ambiente, porque a rede bloqueou o índice do PyTorch. Os três
  testes que dependem do classificador real foram aprovados na pipeline
  #89702, que instala esse arquivo.
- O RNF11 cobre a rota `/api/chat`. A rota de áudio tem envelope próprio de
  erro, já verificado pelos testes de `test_audio_upload.py`, e não foi
  reexecutada aqui.
- Banco, Teams, SharePoint real e provedores reais não foram acessados. A
  homologação no ambiente do Metrô continua pendente, como na Seção 9.2.6.
