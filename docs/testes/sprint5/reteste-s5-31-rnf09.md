# S5-31 — reteste de RNF09

Data: 05/10/2026 (America/Fortaleza). Continuidade da rodada 02 descrita no
[relatório inicial](relatorio-s5-31.md). Evidências anteriores preservadas.

**RNF09-P e RNF09-N aprovados na rodada 03.** A suíte de seis casos registra
3 aprovados, 1 reprovado (RNF08-P) e 2 não executados (RNF07 aguardando coleta).
Código de saída 1 é causado por RNF08-P, não por RNF09.

## Correção e resultado

O carregador agora exige um diretório existente com arquivos JSON, verifica
o formato da coleção `value` e dos itens `fields` e emite `RagSourceError`
para falhas de leitura, codificação, sintaxe e estrutura. Uma exportação
válida com `value: []` continua representando uma coleção vazia legítima.
O tipo do erro pertence ao núcleo RAG e não depende da interface.

O cliente do provedor traduz esse erro para falha de serviço 503; a rota de
chat preserva seu envelope público e não expõe caminhos internos. Não chama
o LLM quando a origem falha.

| Caso | Resultado | Ferramenta e evidência |
|---|---|---|
| CT-RNF09-P | Aprovado: mesma consulta e conteúdo na origem alternativa, ID exclusivo comprova configuração consumida | `pytest`, [observação](../../../src/backend/evidencias/rnf07-rnf09/rodada-03/CT-RNF09-P.json) |
| CT-RNF09-N | Aprovado: diretório ausente, arquivo ausente, JSON malformado e estrutura inválida geram `RagSourceError` no carregamento e na consulta | `pytest`, [oito observações](../../../src/backend/evidencias/rnf07-rnf09/rodada-03/CT-RNF09-N.json) |

[Manifesto e hashes](../../../src/backend/evidencias/rnf07-rnf09/rodada-03/manifesto.json),
[log integral](../../../src/backend/evidencias/rnf07-rnf09/rodada-03/pytest.txt) e
[JUnit](../../../src/backend/evidencias/rnf07-rnf09/rodada-03/pytest.xml).

## Regressão

Execução no ambiente Python local, com `PYTHON_DOTENV_DISABLED=1`:

```powershell
python -m pytest app/tests/test_sharepoint_rag.py app/tests/test_database_rag.py app/tests/test_pipeline_api.py -q --tb=short
```

Resultado observado no terminal: **58 passed, 1 warning in 72.86s**.
Este parágrafo é o resumo da saída, não uma transcrição do log integral.
Inclui estruturas inválidas, codificação ilegível, distinção entre diretório
vazio e coleção válida vazia, erro 503 pela API sem chamada ao LLM e regressão
dos caminhos de consulta e pipeline. Aviso: depreciação de httpx/TestClient.

DEF-S5-31-02 corrigido e retestado no escopo local. Permanecem os limites
anteriores: não se testaram implantação em contêiner nem serviço publicado.
RNF07 está em preparação de sessão consentida com participante P01. RNF08-P
e aprovação do MR continuam pendentes; a task não está 100% concluída.
