# S5-23 (#277) — E2E dos fluxos integrados e das falhas de comunicação

Data da execução: 07/10/2026, America/Sao_Paulo. Origem: barema de
integração frontend-backend, itens 6 e 7. Execução automatizada assistida por
IA; revisão humana de outra frente: pendente.

**Resultado: fluxos principais aprovados no E2E.** A suíte Playwright rodou
com **60 testes aprovados e 0 falhas**: 20 cenários em cada uma das três
larguras (desktop 1440 px, tablet 768 px e celular 390 px). Desses 20, 8 são
novos nesta entrega e cobrem o alerta e as falhas de comunicação.

## Como a suíte funciona

O Playwright sobe dois servidores (`playwright.config.ts`):

- **Backend**: `app/tests/e2e_server.py`, com as rotas reais da API,
  repositórios em memória e provedores determinísticos (LLM, STT e
  classificador). Nada sai da máquina.
- **Interface**: o Vite, com o proxy `/api` apontando para esse backend.

Assim, cada clique percorre a interface, o cliente HTTP, a API e a regra de
negócio. Só os provedores externos são substituídos.

## Fluxos principais

| Fluxo | Spec | Contra o backend? | Resultado |
|---|---|---|---|
| Texto, fontes e modo técnico | `chat.spec.ts` | Sim | Aprovado nas 3 larguras |
| Áudio: gravação sintética, WAV e resposta | `chat.spec.ts` | Sim | Aprovado nas 3 larguras |
| Relatório: fluxo guiado até o DOCX | `chat.spec.ts` | Sim | Aprovado nas 3 larguras |
| **Alerta: configurar e ativar** | `integracao-falhas.spec.ts` | Sim. O workflow real de `app/alerts` vai até a assinatura ativa, conferida depois em `GET /api/alert-subscriptions` | Aprovado nas 3 larguras |
| Alteração de dados: prévia, confirmação, histórico, desfazer e cancelamento | `alteracao-dados.spec.ts` (S5-07) | Não. A API da S5-06 é simulada com `page.route` | Aprovado nas 3 larguras |

A alteração de dados é o único fluxo com a API simulada no E2E. A spec veio
da S5-07, porque o `e2e_server.py` não expõe as rotas da S5-06. O contrato do
backend dessa funcionalidade é coberto por `test_data_change_api.py` e
`test_data_change_service.py`, que rodam no job `backend-api`.

## Falhas de comunicação

Em todos os casos, a spec confere três coisas: a mensagem controlada aparece
(`role="alert"`), nenhum detalhe interno chega à tela (`privado`, `Traceback`,
`Internal Server Error`, corpo bruto) e a interface volta a funcionar no envio
seguinte.

| Falha | Origem | Mensagem exibida | Resultado |
|---|---|---|---|
| 503: provedor indisponível | Backend (`GeminiAPIError` 503) | "O serviço está indisponível. Tente novamente em instantes." | Aprovado |
| 502: falha do provedor | Backend (`GeminiAPIError` 502) | "Não foi possível obter uma resposta do serviço. Tente novamente." | Aprovado |
| 500: exceção inesperada | Backend (`RuntimeError`) | "Não foi possível concluir a solicitação. Tente novamente em instantes." | Aprovado na interface (ver observação) |
| 504: *gateway timeout* | Rede (proxy devolve HTML 504) | "O processamento demorou mais que o esperado. Tente novamente." | Aprovado |
| *Timeout* do cliente | Rede (a API nunca responde) | Mesma mensagem de demora; o botão de envio volta | Aprovado |
| Perda de conexão | Rede (`context.setOffline(true)`) | Mensagem genérica, sem travar; volta a funcionar quando a rede retorna | Aprovado |
| 503 no meio do workflow de alerta | Rede (`/alert-workflow-sessions/*/answers`) | "Nao foi possivel atualizar o alerta."; a etapa é mantida e a repetição avança | Aprovado |

**Observação sobre o 500.** A interface trata o erro corretamente. Já o
backend devolve o 500 genérico do Starlette e, como mostra o
[log da execução](evidencias-s5-23/execucao-e2e.txt), o Uvicorn grava o
*traceback* com a mensagem interna. Esse é o defeito `DEF-S5-32-01`,
registrado na [S5-32](relatorio-s5-32.md), e não uma falha da interface.

## Mudança no produto

`src/frontend/src/lib/api/client.ts` tinha o *timeout* de 120 s fixo no
código. Agora ele vem de `REQUEST_TIMEOUT_MS`, que continua sendo 120 s por
padrão. Só os testes E2E encurtam esse valor para 10 s, pela variável
`VITE_API_TIMEOUT_MS` definida em `playwright.config.ts`. Sem isso, o cenário
de *timeout* esperaria dois minutos em cada largura.

Para gerar as falhas, o `e2e_server.py` ganhou os gatilhos `falha-gateway`
(502) e `falha-inesperada` (500), além do roteamento da intenção
`alerta_prazo_atraso`.

## Relatório na pipeline

O job `frontend-e2e` passa a publicar:

- o **relatório HTML** do Playwright como artefato exposto no MR
  (`expose_as: "Relatorio E2E"`);
- o **JUnit** em `src/frontend/test-results/e2e/junit.xml`, declarado em
  `artifacts:reports:junit`, que alimenta a aba de testes do MR;
- *traces* e *screenshots* das falhas, em `test-results/`.

A configuração do artefato foi validada pela API de *lint* de CI do GitLab do
projeto. Junto, o arquivo de teste da S5-32 (`test_rnf10_rnf12_s5_32.py`) foi
incluído na lista do job `backend-api`, que passou a enumerar arquivos em vez
de usar o marcador `integration`.

## Ambiente e evidências

- Base: `develop` em `84df352`, mais o commit da S5-32 (`f046cde`).
- Playwright 1.63.0, Chromium 141, Node.js 22, Python 3.13. A pipeline usa a
  imagem `mcr.microsoft.com/playwright:v1.63.0-noble`.
- Evidências: [JUnit da execução](evidencias-s5-23/junit-e2e.xml) e
  [saída completa](evidencias-s5-23/execucao-e2e.txt), com os caminhos locais
  trocados por `<repo>`.

Para reproduzir, em `src/frontend`, com as dependências do README instaladas:

```bash
npm run test:e2e
npx playwright test e2e/integracao-falhas.spec.ts   # só os cenários novos
```

## Limites

- Os provedores reais (LLM, Azure Speech e TTS) não participam do E2E. Eles
  já têm homologação própria (Seção 9.4.2 e S4-31).
- A perda de conexão é simulada pelo navegador (`setOffline`), não por falha
  física de rede.
- A execução registrada aqui foi local. A execução remota acontece na pipeline
  do MR, com o relatório publicado como artefato.
