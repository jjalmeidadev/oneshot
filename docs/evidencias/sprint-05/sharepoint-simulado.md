# S5-12 (#266) — SharePoint simulado ampliado

## Escopo comprovado

A entrega amplia a massa documental sintética de 9 para 11 itens e garante
fonte recuperável para `PRJ-0442`, `PRJ-0510` e `PRJ-0587`. O contrato usado é
local: JSONs em `app/rag/data/sharepoint`, `project_artifacts` e
`source_extracts`. Não houve acesso nem homologação com SharePoint corporativo.

## Implementação

- `documentos_projetos.json` contém documentos sintéticos para `PRJ-0510` e
  `PRJ-0587`;
- `comunicados_servico.json#201` possui vínculo explícito ao `PRJ-0442`;
- `04_rag_synthetic_data.sql` resolve `CodigoProjeto`, atualiza artefatos e
  extratos existentes e insere somente extratos ausentes;
- `app.rag.reindex` aplica a carga e valida cobertura e duplicação;
- `scripts.reindex_sharepoint_mock` expõe `apply` e `status` por CLI;
- o fallback local indexa código e nome e filtra o projeto antes do ranking.

## Reprodução

Na pasta `src/backend`, com `DATABASE_URL` ou `SUPABASE_DATABASE_URL`:

```powershell
.\.venv\Scripts\python.exe -m scripts.reindex_sharepoint_mock apply
.\.venv\Scripts\python.exe -m scripts.reindex_sharepoint_mock status
```

Saída esperada, com as contagens dependentes do estado da base:

```json
{
  "duplicate_extract_groups": 0,
  "projects": [
    {"artifact_count": 1, "extract_count": 1, "project_code": "PRJ-0442"},
    {"artifact_count": 1, "extract_count": 1, "project_code": "PRJ-0510"},
    {"artifact_count": 1, "extract_count": 1, "project_code": "PRJ-0587"}
  ],
  "valid": true
}
```

## Testes automatizados

```powershell
cd src/backend
.\.venv\Scripts\python.exe -m pytest app/tests/test_sharepoint_reindex.py app/tests/test_sharepoint_rag.py app/tests/test_rag_synthetic_sql.py app/tests/test_database_rag.py app/tests/test_sensitive_data_rnf01.py app/tests/test_rnf01_rnf03_s4_33.py -q
```

Resultado observado em 07/10/2026: **87 aprovados, 6 ignorados e 0 falhas**.
Os seis casos ignorados dependem de conexão com banco externo, ausente nesta
execução local. Os dois avisos emitidos são de depreciação do TestClient e não
alteram o resultado dos casos.

Os casos cobrem contrato JSON, cobertura dos três projetos, consultas por
código e nome, comparação, isolamento por escopo, duas reaplicações, detecção
de duplicação, rollback, SQL esperado e saída JSON do CLI.

## Quality gates finais

Execução local em 07/10/2026:

- frontend: `npm run lint` e `npm run typecheck` aprovados;
- frontend: `npm test -- --run` com **22 arquivos e 141 testes aprovados**;
- frontend: `npm run build` aprovado, com 2.601 módulos transformados;
- backend: `python -m pytest -q` com **649 aprovados, 25 ignorados e 4
  falhas** em 407,74 s;
- integridade do diff: `git diff --check` aprovado, com avisos não bloqueantes
  de futura normalização LF/CRLF.

As quatro falhas da regressão completa não foram introduzidas pela S5-12 e
reproduzem pendências globais já conhecidas e aceitas para prosseguimento nesta
frente: dois casos RNF07 abaixo da meta, um caso RNF08 sobre a arquitetura do
Copilot e um caso de síntese de áudio. A suíte relacionada à S5-12 permaneceu
com 87 aprovados, 6 ignorados e nenhuma falha.

O CodeRabbit CLI não foi executado. A máquina disponibilizou apenas a
distribuição WSL `docker-desktop`, sem `bash` nem ambiente compatível com o
CLI. Por isso, esta evidência não substitui a revisão automática nem a revisão
humana do MR.

## Limitações

- Os testes determinísticos usam doubles para a conexão na operação de carga.
- Os casos que exigem banco externo são ignorados quando a conexão não está
  configurada.
- A aplicação real da carga deve ser evidenciada separadamente no ambiente que
  contém as migrations base e os três projetos.
- Esta evidência não demonstra Microsoft Graph, tenant do Metrô ou SharePoint
  corporativo.
- A story permanece `InProgress`: a implementação local está concluída, mas o
  gate global do backend e a revisão CodeRabbit ainda não permitem promoção
  para `InReview`.
