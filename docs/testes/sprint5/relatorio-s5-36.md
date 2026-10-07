# S5-36 (#290) — Consolidação final dos testes sistêmicos

Data: 07/10/2026, America/Sao_Paulo. Base: `develop` em `568a1c1`, com a
revisão de arquitetura da S5-43 (#297). Origem: barema, item 10.
Consolidação e reavaliação do RNF08 assistidas por IA; revisão humana de outra
frente: pendente.

Esta consolidação junta, em uma tabela por requisito, o resultado vigente de
cada caso, a evidência que o sustenta e o destino de cada defeito que ficou
aberto. O texto resumido entra na Seção 9.5 de `docs/Projeto.md`.

## Como ler os resultados

- **Aprovado** e **reprovado** comparam o observado com o critério da Seção
  9.2.2 ou com o resultado esperado da Seção 9.1.3.
- **Bloqueado** é o caso que não pôde rodar porque falta algo fora do teste.
- **Não executado** é o caso que não rodou por outro motivo.
- O resultado vigente é o da **última execução** do caso. Uma correção
  integrada sem nova execução não muda o resultado; ela aparece na coluna de
  situação e no destino do defeito.

## Situação das quatro dependências

| Task | O que deveria entregar | Situação em 07/10 | Efeito nesta consolidação |
|---|---|---|---|
| S5-30 (#284) | Reexecutar RNF01 a RNF03 depois das correções | Aberta e sem MR. A branch `test/reexecutar-rnf01-rnf03` tem só uma rodada de diagnóstico de 29/09, anterior às correções, com o mesmo resultado da S4-33 | RNF02 e RNF03 ficam com o resultado da S4-33 (24/09). O RNF01 usa a verificação da S5-27 |
| S5-31 (#285) | Executar RNF07 a RNF09 | Integrada (`e50742e`) | RNF07 e RNF09 entram como registrados. O RNF08 foi reavaliado aqui, pelo critério revisado |
| S5-32 (#286) | Executar RNF10 a RNF12 | Integrada (`3997701`) | Entram como registrados |
| S5-33 (#287) | Reexecutar os casos funcionais reprovados e o RNF06 | Integrada (`3997701`) | Entram como registrados; três itens seguem bloqueados pela S5-12 (#266) |

## Resultado por requisito

### Funcionais

| Requisito | Casos | Última execução | Resultado vigente | Evidência |
|---|---|---|---|---|
| RF01 | CT-RF01-01, CT-RF01-02 | 23/09 | **Aprovado** (2/2) | Seção 9.1.5.7 |
| RF02 | CT-RF02-01, CT-RF02-02 | 07/10 (S5-33) e 23/09 | **Aprovado** (2/2) | [Relatório S5-33](relatorio-s5-33.md) |
| RF03 | CT-RF03-01, CT-RF03-02 | 23/09 e 07/10 (S5-33) | **Aprovado** (2/2) | [Relatório S5-33](relatorio-s5-33.md) |
| RF04 | CT-RF04-01, CT-RF04-02 | 23/09 | **Aprovado** (2/2) | Seção 9.1.5.7 |
| RF05 | CT-RF05-01, CT-RF05-02 | 23/09 | **Aprovado** (2/2) | Seção 9.1.5.7 |
| RF06 | CT-RF06-01, CT-RF06-02 | 07/10 (S5-33) e 23/09 | **Bloqueado** (1 aprovado, 1 bloqueado) | [Relatório S5-33](relatorio-s5-33.md#casos-bloqueados) |
| RF07 | CT-RF07-01, CT-RF07-02 | 23/09 | **Aprovado** (2/2) | Seção 9.1.5.7 |
| RF08 | CT-RF08-01, CT-RF08-02 | 07/10 (S5-33) e 23/09 | **Bloqueado** (1 aprovado, 1 bloqueado) | [Relatório S5-33](relatorio-s5-33.md#casos-bloqueados) |
| RF09 | CT-RF09-01, CT-RF09-02 | Reteste após o DEF-RNF04-02 e 23/09 | **Aprovado** (2/2) | Seção 9.1.5.7 |
| RF10 | CT-RF10-01, CT-RF10-02 | 23/09 | **Aprovado** (2/2) | Seção 9.1.5.7 |

**Total funcional:** 18 casos aprovados e 2 bloqueados, sem falha em aberto.
Oito requisitos aprovados e dois bloqueados, ambos pela mesma causa: a base do
chat não tem documento do `PRJ-0510` (DEF-RF06-01), o que depende da S5-12
(#266).

### Não funcionais

| Requisito | Última execução | Resultado vigente | Situação | Evidência |
|---|---|---|---|---|
| RNF01 | P: 24/09 (S4-33). N: verificação da S5-27, após a correção | **Aprovado** | O marcador sensível deixou de chegar ao provedor; o payload leva `[DADO CLASSIFICADO]` | [S4-33](../sprint4/relatorio-s4-33.md#4-resultados), [S5-27](../../evidencias/sprint-05/s5-27-dado-sensivel.md#execução) |
| RNF02 | 24/09 (S4-33) | **Bloqueado** | Perfis e regras de acesso chegaram com a S5-03 e a S5-04 (#257, #258), integradas. Falta reexecutar na S5-30 | [S4-33](../sprint4/relatorio-s4-33.md#4-resultados) |
| RNF03 | 24/09 (S4-33) | **Reprovado** (P reprovado, N aprovado) | Perfil (D-01), fontes (D-04) e auditoria (D-02, D-03, D-05) corrigidos pela S5-04, S5-26 e S5-25, integradas. Falta reexecutar na S5-30 | [S4-33](../sprint4/relatorio-s4-33.md#4-resultados) |
| RNF04 | Sprint 4 | **Aprovado** | 91,67% de respostas fundamentadas e 4,17% de alucinação | [Relatório](../../../src/backend/evidencias/rnf04-v12-37flash/RELATORIO.md) |
| RNF05 | Sprint 4, 3ª rodada | **Aprovado** | P95 simples de 7,0 a 7,6 s e comparativo de 7,4 a 8,4 s, sem erro; o cenário negativo reprovou, como exigido | [Relatório](../../../src/backend/evidencias/rnf05-rodada3/RELATORIO.md) |
| RNF06 | Sprint 4 (v2) | **Reprovado** | F1-macro 0,8327 aprovado; *recall*@3 0,5556 reprovado. A S5-33 não remediu: depende da S5-12 (#266) | [Evidências](../../evidencias/sprint-04/rnf06/README.md), [S5-33](relatorio-s5-33.md#casos-bloqueados) |
| RNF07 | 06/10 (S5-31) | **Reprovado** | 6 de 20 formulações compreendidas; a meta é 16. A coleta antecedeu a integração da S5-28 (#282), que trata perguntas curtas | [Consolidação S5-31](consolidacao-s5-31.md) |
| RNF08 | 07/10 (S5-36) | **Aprovado** | Reavaliado pelo critério revisado na S5-43; detalhes abaixo | [P](../../../src/backend/evidencias/rnf08-s5-36/rodada-01/CT-RNF08-P.json), [N](../../../src/backend/evidencias/rnf08-s5-36/rodada-01/CT-RNF08-N.json) |
| RNF09 | 05/10 (S5-31, rodada 03) | **Aprovado** | Aprovado depois da correção do DEF-S5-31-02 | [Reteste](reteste-s5-31-rnf09.md) |
| RNF10 | 07/10 (S5-32) | **Aprovado** | | [Relatório S5-32](relatorio-s5-32.md) |
| RNF11 | 07/10 (S5-32) | **Reprovado** (P aprovado, N reprovado) | Exceção inesperada em `/api/chat` volta como 500 genérico, sem envelope e sem auditoria (DEF-S5-32-01) | [Relatório S5-32](relatorio-s5-32.md) |
| RNF12 | 07/10 (S5-32) | **Aprovado** | | [Relatório S5-32](relatorio-s5-32.md) |

**Total não funcional:** 7 requisitos aprovados (RNF01, RNF04, RNF05, RNF08,
RNF09, RNF10 e RNF12), 4 reprovados (RNF03, RNF06, RNF07 e RNF11) e 1
bloqueado (RNF02).

**Sobre o RNF01.** A S4-33 reprovou o CT-RNF01-N em 24/09, e a rodada de
diagnóstico da S5-30, em 29/09, repetiu o resultado, ainda antes da correção. A S5-27 executou o mesmo teste
(`test_rnf01_rnf03_s4_33.py`) depois da correção e o caso passou, junto com 28
casos novos de `test_sensitive_data_rnf01.py`. O resultado vigente é essa
execução. A rodada formal da S5-30 deve confirmá-lo.

## Reavaliação do RNF08

A S5-31 reprovou o CT-RNF08-P porque o critério da época exigia o Copilot
Studio na arquitetura, e o runtime já não o tinha (DEF-S5-31-01). A S5-43
revisou o requisito: contrato OpenAPI válido, cada componente do runtime com
equivalente Microsoft mapeado na Seção 6.4 e canal publicável no Teams e
acessível pelo Copilot via MCP, sem dependência do Copilot Studio.

O teste novo, [`test_rnf08_s5_36.py`](../../../src/backend/app/tests/test_rnf08_s5_36.py),
transforma cada parte do critério em uma verificação:

| Parte do critério | Como é verificada |
|---|---|
| OpenAPI válido | `/health` e `/openapi.json` com HTTP 200 e o mesmo checklist de contrato da S5-31 |
| Equivalente Microsoft mapeado | Os pacotes de `src/backend/app` são descobertos no disco, sem lista fixa, e somados ao frontend, a `main.py`, a `pipeline.py` e ao `compose.prod.yml`. Cada um precisa aparecer na primeira coluna de uma linha das Seções 6.4.3 a 6.4.6 com a coluna de equivalente preenchida |
| Sem dependência do Copilot Studio | Código do backend e do frontend, `.env.example`, Compose e Dockerfiles não podem ter variável `COPILOT_STUDIO_*` nem endpoint do serviço fora de comentário. A Figura 22 só pode citar o Copilot Studio na legenda |
| Teams e Copilot via MCP previstos | A tabela da Seção 5.2.1 precisa ter as duas linhas marcadas como previstas |

O caso negativo aplica cada violação a uma cópia em memória e confere que ela
é detectada: contrato sem `POST /api/chat`, tipo incompatível, de-para sem as
linhas dos alertas, equivalente vazio para o PLN, `COPILOT_STUDIO_ENDPOINT` no
`.env.example` e o Copilot Studio como componente da Figura 22. O teste confere
no fim que o contrato e o `Projeto.md` reais não mudaram.

**Achados durante a preparação.** A primeira execução local reprovou o caso
positivo por dois motivos reais, corrigidos nesta mesma entrega:

1. `data_changes` (alteração de dados pelo chat, S5-06) e `sharepoint_webhooks`
   (webhook do SharePoint simulado, S5-09) estavam no runtime sem linha na
   Seção 6.4. As duas linhas foram acrescentadas. Na mesma revisão, as linhas
   dos MRs !127, !123 e !128, que ainda diziam "Planejado no `develop`",
   passaram a refletir a integração.
2. O comentário de `src/backend/.env.example` dizia que, no Metrô, o agente
   usaria o Copilot Studio com modelos GPT. O texto passou a citar o modelo
   aprovado pela GTI no Azure.

Duas menções ao Copilot Studio continuam no código e não são dependência: a
docstring de `reports/workflow.py` ("independente de Copilot Studio") e o
comentário de `lib/api/constants.ts` que lista os valores aceitos pelo CHECK de
`ai_conversations.channel`. Elas ficam registradas na evidência, em
`copilot_studio_mentions`.

**Resultado.** CT-RNF08-P e CT-RNF08-N aprovados; RNF08 aprovado. O
DEF-S5-31-01 fica encerrado. O teste antigo da S5-31 para o CT-RNF08-P foi
marcado como `skip`, com o motivo, e a rodada-04 continua guardando o resultado
pelo critério anterior. O teste novo tem o marcador `integration` e roda no
job `backend-api`: um pacote novo sem linha na Seção 6.4 reprova a pipeline.
O escopo é local: o teste não prova a publicação no
tenant do Metrô, que depende da S5-19 (#273) e da S5-18 (#272).

Para reproduzir, a partir de `src/backend`:

```bash
python -m scripts.run_s5_36 --round rodada-02
```

## Demais frentes de teste

| Frente | Execução | Resultado vigente | Evidência |
|---|---|---|---|
| Unitários do frontend (S5-22) | 05/10 | **Aprovado**: 112 testes em 18 arquivos; cobertura de 86,36% das linhas, 83,96% das instruções, 85,81% das funções e 75,25% das ramificações, acima dos mínimos aplicados pelo job `frontend-unit` | [Relatório S5-22](relatorio-s5-22.md) |
| Integração do backend (S4-32B e #255) | Sprint 4; gate em 01/10 | **Aprovado**: suíte marcada com `integration` no job `backend-api`; o gate de marcadores de conflito roda antes dos testes | [S4-32B](../sprint4/relatorio-s4-32b.md), [#255](issue-255-gate-integracao.md) |
| Persistência e auditoria (S4-11) | 22/09 | Achados D-01 a D-06 corrigidos pela S5-03/S5-04, S5-25, S5-26 e S5-27; a revalidação sobre o banco é a da S5-30 | [S4-11](../sprint4/relatorio-s4-11.md) |
| E2E textual com RAG (S4-20) | 24/09 e reteste | **Aprovado** em CT-E2E-01 a 05. CT-E2E-06 **cancelado**: correlacionava o Copilot Studio, que saiu da arquitetura. CT-E2E-07 **não aplicável**: o projeto não tem fallback automático entre modelos; a falha do provedor é tratada com resposta controlada (CT-E2E-03 e CT-RNF11-P) | [S4-20](../sprint4/relatorio-s4-20.md) |
| E2E da interface e falhas de comunicação (S5-23) | 07/10 | **Aprovado**: 60 testes, 20 cenários em desktop, tablet e celular | [Relatório S5-23](relatorio-s5-23.md) |
| Cache VHS com Azure Speech real (S4-31 e S5-35) | 03/10 | **Aprovado**: 1 chamada ao provedor e 4 acertos em 5 envios, sem erro | [Evidências](../../evidencias/sprint-05/vhs-azure-real/README.md) |
| Usabilidade (Seção 9.3) | 23/09 | Seis sessões; SUS médio de 86,25. Ocorrências O1 a O8 com o destino abaixo; não houve nova sessão depois das correções | Seção 9.3.2 |

## Defeitos e destino

| ID | Origem | Situação | Destino |
|---|---|---|---|
| DEF-RF02-01 | CT-RF02-01 | Corrigido pela S5-28 (#282) e aprovado na S5-33 | Encerrado |
| DEF-RF03-01 | CT-RF03-02 | Corrigido pela S5-28 (#282) e aprovado na S5-33 | Encerrado |
| DEF-RF06-01 | CT-RF06-01, CT-RF08-01 | Aberto | S5-12 (#266). Sem a #266 nesta sprint, segue para a Seção 12.2, item 1 |
| RNF06, recuperação | CT-RNF06-P/N | Reprovado | Mesmo destino do DEF-RF06-01; a massa prospectiva é congelada sobre o corpus novo antes da medição |
| D-01 | S4-11, S4-33 | Corrigido pela S5-03 e S5-04 (#257, #258) | Reexecução do RNF02 e do RNF03 na S5-30 (#284) |
| D-02, D-03, D-05 | S4-11 | Corrigidos pela S5-25 (#279); o backfill `19_backfill_s5_25_audit.sql` ainda precisa ser aplicado no banco de destino | Reexecução do RNF03 na S5-30 (#284) |
| D-04 | S4-11, S4-33 | Corrigido pela S5-26 (#280) | Reexecução do RNF03 na S5-30 (#284) |
| D-06 | S4-33 | Corrigido pela S5-27 (#281); CT-RNF01-N aprovado | Confirmação na S5-30 (#284) |
| DEF-RNF04-01 | CT-RNF04 | Corrigido | Encerrado |
| DEF-RNF04-02 | CT-RNF04, CT-RF09-01, O5, O7 | Corrigido: limite de 1024 tokens e aviso de resposta interrompida | Encerrado |
| DEF-RNF05-01 | CT-RNF05 | Característica do *Free Tier* da bancada | Medição com o modelo de produção na homologação (Seção 12.2, item 4) |
| DEF-RNF05-02 | CT-RNF05 | Mitigado: limite de 5 s por consulta e *keepalive*. A gravação da auditoria continua no caminho da resposta | Seção 12.2, item 16 |
| DEF-S5-31-01 | CT-RNF08-P | Encerrado pela revisão do RNF08 (S5-43) e pela reavaliação desta task | Encerrado |
| DEF-S5-31-02 | CT-RNF09-N | Corrigido e retestado | Encerrado |
| RNF07 | CT-RNF07-P/N | Reprovado, 6 de 20 | Seção 12.2, item 6: nova aplicação sobre a versão com a S5-28 |
| DEF-S5-32-01 | CT-RNF11-N | Aberto: não há tratador global de exceções em `/api/chat` | Seção 12.2, item 5 |
| O1 | Usabilidade | Corrigido pela S5-28 (#282), sem nova sessão | Nova sessão junto da S5-34 (#288) |
| O2, O3, O4 | Usabilidade | Abertos | S5-29 (#283), aberta |
| O6 | Usabilidade | Cosmético; a intenção foi preservada | Sem ação |
| O8 | Usabilidade | Tratado pela S5-20 (#274), sem nova sessão | Nova sessão junto da S5-34 (#288) |
| Perfis não cobertos | Usabilidade | Gestão de projetos, indicadores e Microsoft sem participante | S5-34 (#288); sem ela, Seção 12.2, item 3 |

## Limites desta consolidação

- RNF02 e RNF03 continuam com o resultado de 24/09, anterior às correções. Se
  a S5-30 for integrada antes do fechamento, as duas linhas e o total precisam
  ser atualizados.
- RNF04 e RNF05 foram medidos na Sprint 4 e não foram repetidos depois das
  mudanças da Sprint 5. Não há indício de regressão, mas também não há nova
  medição.
- As ocorrências de usabilidade corrigidas não passaram por nova sessão; a
  correção está no código, não na experiência medida.
- A reavaliação do RNF08 é local e documental. Ela não substitui a homologação
  no ambiente Microsoft do Metrô.
