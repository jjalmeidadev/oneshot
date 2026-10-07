# Evidências de testes — integração #131

## S5-23 — E2E integrado e falhas de comunicação (07/10/2026)

A suíte Playwright passa com **60 testes em 4 specs** (20 cenários × desktop,
tablet e celular). `e2e/integracao-falhas.spec.ts` acrescenta o alerta contra o
workflow real do backend e as falhas de comunicação: 503, 502 e 500 do backend,
504 de gateway, _timeout_ do cliente e perda de conexão. Em cada falha, a spec
confere a mensagem controlada, a ausência de detalhe interno e a recuperação no
envio seguinte.

O E2E encurta o _timeout_ do cliente para 10 s com `VITE_API_TIMEOUT_MS`; fora
dele, o padrão continua 120 s. O job `frontend-e2e` publica o relatório HTML
como artefato exposto no MR e o JUnit em `test-results/e2e/junit.xml`. Detalhes
no [relatório S5-23](../../docs/testes/sprint5/relatorio-s5-23.md).

## S5-22 — testes por componente (05/10/2026)

A suíte atual passa com **112 testes em 18 arquivos**, incluindo 48 novos casos
para UI, barra lateral, tema, proatividade, notificações, configuração de alertas
e renderização de mensagens. O inventário cobre os **38 módulos de componentes**,
além dos providers e de `App`.

| Métrica      | Medição atual | Mínimo global |
| ------------ | ------------- | ------------- |
| Linhas       | 86,36%        | 80%           |
| Instruções   | 83,96%        | 80%           |
| Funções      | 85,81%        | 75%           |
| Ramificações | 75,25%        | 70%           |

`vitest.config.ts` aplica os mínimos locais e na pipeline. Um gate adicional
por arquivo em `src/components/**/*.tsx` rejeita componentes com zero execução
de linhas, instruções ou funções. Esse gate foi verificado com uma fixture sem
teste: os 18 testes de UI passaram e a cobertura encerrou com código 1 por causa
da fixture, removida ao concluir a verificação.

O job `frontend-unit` publica JUnit em `test-results/unit/junit.xml` e relatório
Cobertura em `coverage/cobertura-coverage.xml`, além de HTML e JSON summary.
Execute `npm run typecheck` para verificar tipos separadamente do build.

Inventário, critérios, limites e evidências reproduzíveis estão no
[relatório S5-22](../../docs/testes/sprint5/relatorio-s5-22.md). A publicação do MR,
execução remota e aprovação comentada por revisor de outra frente permanecem
pendentes; a revisão local não substitui essas condições.

## Resultados da integração #131 (registro anterior)

A validação cobre a interface S3/S5, os contratos HTTP, a conversão de áudio, o contexto de conversa e falhas de comunicação. As execuções locais concluíram com **171 testes do backend, 46 testes unitários do frontend e 8 testes de ponta a ponta aprovados**. Lint, compilação de produção e verificação de formatação também passaram. A auditoria npm não encontrou vulnerabilidades.

| Camada             | Casos e resultado esperado                                                                                                                                 |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Componentes        | Renderizar mensagens, fontes, detalhes, controles, estados vazios e navegação; permitir busca, seleção e exclusão de conversas e troca de tema.            |
| Estado de conversa | Enviar texto e áudio pelas APIs, reutilizar o contexto correto, impedir envios concorrentes e descartar respostas após cancelamento.                       |
| Cliente HTTP       | Serializar JSON e multipart, transmitir token e contexto, traduzir falhas em mensagens seguras e respeitar cancelamento.                                   |
| Gravação           | Converter áudio para WAV PCM16 mono de 16 kHz, respeitar duração e tamanho, liberar microfone e URLs, inclusive quando a permissão chega após desmontagem. |
| Backend            | Validar entradas e parâmetros, classificar intenções, preservar contratos e contexto, devolver erros controlados e integrar transcrição à resposta.        |
| Navegador          | Executar envio e exibição de texto, fontes e métricas; recuperar de falhas; cancelar envio; gravar áudio sintético e receber resposta.                     |
| Acessibilidade     | Verificar interface com axe nos temas claro e escuro, em desktop, tablet e celular, incluindo navegação responsiva e o fluxo principal só pelo teclado.    |

## Cobertura unitária do frontend

O relatório V8 inclui componentes, hooks, bibliotecas e estado da aplicação. A cobertura de ponta a ponta não é somada a estes números.

| Métrica      | Cobertura | Elementos cobertos |
| ------------ | --------- | ------------------ |
| Linhas       | 87,10%    | 554/636            |
| Instruções   | 84,33%    | 587/696            |
| Ramificações | 73,12%    | 389/532            |
| Funções      | 83,83%    | 166/198            |

## Reprodução

Siga a preparação do [README](README.md), incluindo as dependências Python do backend e Node.js 24. Na pasta `src/frontend`, execute:

```sh
npm ci
npm run lint
npm run format:check
npm run build
npm run test:coverage
npx playwright install chromium
npm run test:e2e
```

O Playwright inicia os servidores locais automaticamente e executa os cenários de `e2e/chat.spec.ts` e de `e2e/responsividade-acessibilidade.spec.ts` em desktop (1440 × 900), tablet (768 × 1024) e celular (390 × 844). O segundo arquivo confere, nas três larguras e nos dois temas, a ausência de rolagem horizontal e de violações do axe (WCAG 2.0, 2.1 e 2.2 A/AA) nos estados vazio, resposta, ajustes e fontes, e percorre o fluxo principal só pelo teclado. A configuração usa a instalação Python da raiz; `E2E_PYTHON` permite indicar outro executável. Os relatórios ficam em `coverage/` e `playwright-report/`.

Para a suíte completa do backend, na raiz do repositório, execute:

```sh
python -m pytest src/backend/app/tests
```

Use o ambiente virtual preparado conforme o README do backend. Os testes do classificador dependem do modelo documentado e podem precisar baixá-lo na primeira execução. A execução completa apresentou dez avisos de dependências (Starlette/httpx e otimização do SciPy), sem falhas.

O pipeline `.gitlab-ci.yml` automatiza testes unitários, verificações do frontend, testes determinísticos da API e testes de navegador. A aprovação local não comprova a execução do pipeline remoto; consulte seu resultado na merge request.

## Evidência do alerta de prazo

Os testes `alert-workflow-card.test.tsx` e `notification-center.test.tsx`
validam a conclusão acessível do workflow e o resumo de notificações. A suíte
TypeScript também verifica os contratos discriminados de relatório e alerta.
O fluxo de mensageria AMQP deve ser validado separadamente com Docker Engine e
RabbitMQ ativos, porque os testes de componente não inicializam infraestrutura.

## Evidência da alteração de dados pelo chat (S5-07)

`data-change-card.test.tsx` cobre os quatro estados exigidos pela issue #261 (prévia, confirmação, cancelamento e erro) e também o erro transitório com nova tentativa, o desfazer dentro e fora da janela, a prévia expirada, os avisos, o histórico do campo, a recusa sem ações e as perguntas com candidatos e com valor inválido. `data-change-flow.test.tsx` atravessa a aplicação real (store, lista e cartão) e confirma que, depois de gravar, trocar de conversa e voltar não oferece confirmar de novo. `e2e/alteracao-dados.spec.ts` repete o fluxo no Chromium em desktop, tablet e celular, com auditoria axe do cartão nos temas claro e escuro e verificação de rolagem horizontal. O servidor E2E não tem as rotas da S5-06, então a resposta do chat e as rotas do cartão são simuladas com `page.route`; a permissão de escrita é coberta pelos testes do backend da S5-06. Evidência e capturas em `docs/evidencias/sprint-05/s5-07-interface-alteracao.md`.

## Limites da evidência

Os testes de navegador usam o backend real e validam o arquivo WAV enviado, mas substituem as bordas de Azure, Gemini e classificação por respostas determinísticas. A classificação local também foi executada separadamente com o modelo real. Não havia credenciais para comprovar chamadas reais de Azure e Gemini; essa validação deve ser realizada no ambiente configurado antes da publicação.

Os testes não comprovam autenticação corporativa Entra, acesso real ao SharePoint, persistência de conversas, latência de produção ou conformidade integral de acessibilidade. A auditoria automática deve ser complementada por uso manual com teclado e leitor de tela. Conversas e token permanecem somente na memória da sessão, conforme a interface documentada.
