# S5-31 (#285) — RNF07 a RNF09

> Situação atual após a coleta das vinte frases: [consolidação dos seis casos](consolidacao-s5-31.md).

> Histórico das rodadas 01/02. Após correção, RNF09-P/N foram aprovados na
> rodada 03: [reteste de RNF09](reteste-s5-31-rnf09.md). Os resultados abaixo
> permanecem como evidência da versão anterior à correção.

Data da execução: 05/10/2026, America/Fortaleza. Critérios: Seções 9.2.2 e
9.2.3 de `docs/Projeto.md`. Complementação prevista na Seção 6.4.1 de
`docs/GestaoProjeto.md`. Execução automatizada: assistente Codex; revisão humana
de outra frente: pendente.

**Resultado: 2 aprovados, 2 reprovados e 2 não executados.** Não há aprovação
integral dos três requisitos nem encerramento da issue.

## Ambiente e rastreabilidade

Base: commit `28337f402537ba3c52fee6d703d75e70af64dc65` de `develop`.
O [manifesto da rodada 02](../../../src/backend/evidencias/rnf07-rnf09/rodada-02/manifesto.json)
registra versões reais, plataforma, estado da árvore de trabalho, comando e
hashes dos arquivos usados. A árvore estava limpa antes da preparação desta
entrega. Foram acrescentados testes e documentos, sem alterar o produto.

A API foi iniciada em processo por `FastAPI TestClient`, incluindo seu ciclo
de vida. `/health` e `/openapi.json` responderam HTTP 200. Não foi iniciado
servidor TCP nem acessado tenant, banco ou provedor externo. `.env` foi
desabilitado e a fixture existente neutralizou as configurações de serviços.
As mutações de contrato e de massa ocorreram em cópias; as fontes reais foram
preservadas. Esse ambiente foi suficiente para os casos técnicos locais,
mas não comprova estabilidade do ambiente integrado com usuários.

## Seis casos

| Caso | Resultado observado | Ferramenta | Evidência |
|---|---|---|---|
| CT-RNF07-P | **Não executado.** Dez frases positivas congeladas; não foram fornecidos participantes nem respostas conversacionais desta rodada. Não há taxa calculável. | Roteiro + CSV preparados; `pytest` registra `skipped` | [Amostra](amostra-rnf07.csv), [protocolo](protocolo-rnf07.md), [JUnit](../../../src/backend/evidencias/rnf07-rnf09/rodada-02/pytest.xml) |
| CT-RNF07-N | **Não executado.** Dez frases com ambiguidade, sinônimos e erros leves congeladas; falta aplicação e julgamento humano da orientação recebida. | Roteiro + CSV preparados; `pytest` registra `skipped` | [Amostra](amostra-rnf07.csv), [protocolo](protocolo-rnf07.md), [JUnit](../../../src/backend/evidencias/rnf07-rnf09/rodada-02/pytest.xml) |
| CT-RNF08-P | **Reprovado no critério vigente.** Contrato real passa no checklist estrutural e de integração. A arquitetura vigente remove Copilot Studio, exigido pelo texto de aceitação. | `pytest`, TestClient, modelo OpenAPI do FastAPI/Pydantic e inspeção arquitetural | [Observação](../../../src/backend/evidencias/rnf07-rnf09/rodada-02/CT-RNF08-P.json), [contrato real](../../../src/backend/evidencias/rnf07-rnf09/rodada-02/openapi-real.json), [arquitetura vigente](../../../src/agent/README.md) |
| CT-RNF08-N | **Aprovado.** Cópia sem `POST /api/chat` rejeitada; cópia com `message: integer` rejeitada. Nova leitura confirma contrato real intacto. | `pytest`, cópias profundas e mesmo checklist do positivo | [Erros detectados](../../../src/backend/evidencias/rnf07-rnf09/rodada-02/CT-RNF08-N.json), [operação removida](../../../src/backend/evidencias/rnf07-rnf09/rodada-02/openapi-sem-chat.json), [tipo incompatível](../../../src/backend/evidencias/rnf07-rnf09/rodada-02/openapi-tipo-incompativel.json) |
| CT-RNF09-P | **Aprovado no núcleo RAG local.** A mesma consulta retorna o mesmo conteúdo após configurar diretório alternativo; identificador exclusivo `s5-31-alternativa:101` comprova uso da nova fonte. Conteúdo chega ao prompt sem edição no núcleo. | `pytest`, diretório temporário, `SHAREPOINT_MOCK_DATA_DIR`, `retrieve_context` e `build_rag_input` reais | [Consulta, IDs, conteúdo e prompt](../../../src/backend/evidencias/rnf07-rnf09/rodada-02/CT-RNF09-P.json) |
| CT-RNF09-N | **Reprovado.** Diretório e arquivo ausentes retornam zero documentos sem erro. JSON malformado gera `JSONDecodeError`; JSON com estrutura de lista gera `AttributeError` sem validação de domínio. Observado no carregamento e na consulta. | `pytest`, fontes inválidas em diretórios temporários e núcleo real | [Quatro subcenários e duas etapas](../../../src/backend/evidencias/rnf07-rnf09/rodada-02/CT-RNF09-N.json) |

O [log completo](../../../src/backend/evidencias/rnf07-rnf09/rodada-02/pytest.txt)
registra `2 failed, 2 passed, 2 skipped`, com código de saída 1. Falhas não
foram convertidas em aprovações ou `xfail`. O aviso de depreciação de
`httpx`/TestClient não impediu a execução.

## Checklist arquitetural e limites de RNF08

| Item do critério | Constatação |
|---|---|
| Teams como canal previsto | Permanece no RNF08 em `Projeto.md`; não houve publicação ou teste de canal nesta rodada. |
| Copilot Studio | `src/agent/README.md` declara sua remoção da execução; `ONESHOT/` é histórico. Contradiz o critério atual. |
| SharePoint | Exportações JSON sintéticas locais alimentam o RAG testado. O runtime do relatório declara não depender de SharePoint. Não houve homologação da integração real. |
| Azure | Há configuração de Azure Speech descrita em `src/backend/README.md`; o serviço não foi chamado nesta rodada. |
| API e conector | Contrato servido pela API verificado quanto à estrutura, presença de `GET /health`, `POST /api/chat`, `POST /api/audio`, respostas 200 e tipo textual da mensagem. Não houve importação em conector Microsoft. |

O checklist é delimitado: `OpenAPI.model_validate` e verificações explícitas
não equivalem a certificação completa da especificação OpenAPI nem de todas
as referências. A incompatibilidade de `message` é detectada pela regra de
integração; `integer` isoladamente é um tipo válido na especificação.

## Defeitos e encaminhamento

- **DEF-S5-31-01 — requisito e arquitetura divergentes.** O requisito ainda
  exige Copilot enquanto o runtime o removeu. Encaminhar para conciliação de
  RNF08 na S5-43 (#297), já prevista no backlog. Após revisão aprovada do
  requisito, atualizar o checklist e executar nova rodada. Não alterar o
  critério retroativamente para aprovar esta execução. A asserção automatizada
  acompanha a declaração documental; sua ausência futura não prova por si só
  aderência tecnológica, que exige nova revisão arquitetural.
- **DEF-S5-31-02 — configuração inválida da origem.** `load_sharepoint_documents`
  aceita caminhos ausentes e não valida a estrutura JSON antes de acessar
  `.get`. Encaminhar à frente backend para erro explícito e localizado e
  tratamento na fronteira da aplicação, seguido de reteste. O erro de JSON
  sintático foi explícito; não foi validado o envelope HTTP desses erros.

RNF09 positivo cobre recuperação e montagem do prompt localmente. Não certifica
classificador, geração por LLM, contêiner, serviço publicado ou substituição de
PostgreSQL por outro fornecedor. RNF07 exige pelo menos 16 sucessos em 20,
somando compreensão e orientação útil sem dupla contagem; não usar métricas
de recuperação como substitutas.

## Reprodução

A partir de `src/backend`, com o ambiente Python do projeto instalado:

```powershell
python -m scripts.run_s5_31 --round rodada-03
```

Usar um identificador novo: o executor recusa sobrescrever evidências. Ele
congela hashes antes do pytest e preserva seu código de saída. A rodada 01
é o diagnóstico inicial, antes de reduzir o log dos contratos e reforçar
o critério de erro da estrutura inválida; a rodada 02 é a referência final.
Ambas resultaram em 2 aprovações, 2 reprovações e 2 não execuções. A amostra
de RNF07 não mudou entre as rodadas.

## DoR e DoD

Casos da Seção 9.2.3 revisados e seis linhas com ferramenta, evidência e
resultado registradas. Não execuções identificadas com motivo. Amostra de
RNF07 congelada antes da rodada técnica, com roteiro e rubrica de avaliação.

Permanecem pendentes: aplicação de RNF07 com participantes; confirmação do
ambiente integrado; conferência de assignee, revisor de outra frente, labels
e milestone no Kanban; publicação e aprovação do MR com comentário de revisão.
Não foi consultado nem alterado o estado remoto da issue. O texto do MR está
preparado em [mr-s5-31.md](mr-s5-31.md), com `Closes #285`; nenhum MR foi
publicado ou aprovado nesta execução.
