# Evidências de testes — integração #131

## Escopo e resultados

A validação cobre a interface S3/S5, os contratos HTTP, a conversão de áudio, o contexto de conversa e falhas de comunicação. As execuções locais concluíram com **171 testes do backend, 46 testes unitários do frontend e 8 testes de ponta a ponta aprovados**. Lint, compilação de produção e verificação de formatação também passaram. A auditoria npm não encontrou vulnerabilidades.

| Camada             | Casos e resultado esperado                                                                                                                                 |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Componentes        | Renderizar mensagens, fontes, detalhes, controles, estados vazios e navegação; permitir busca, seleção e exclusão de conversas e troca de tema.            |
| Estado de conversa | Enviar texto e áudio pelas APIs, reutilizar o contexto correto, impedir envios concorrentes e descartar respostas após cancelamento.                       |
| Cliente HTTP       | Serializar JSON e multipart, transmitir token e contexto, traduzir falhas em mensagens seguras e respeitar cancelamento.                                   |
| Gravação           | Converter áudio para WAV PCM16 mono de 16 kHz, respeitar duração e tamanho, liberar microfone e URLs, inclusive quando a permissão chega após desmontagem. |
| Backend            | Validar entradas e parâmetros, classificar intenções, preservar contratos e contexto, devolver erros controlados e integrar transcrição à resposta.        |
| Navegador          | Executar envio e exibição de texto, fontes e métricas; recuperar de falhas; cancelar envio; gravar áudio sintético e receber resposta.                     |
| Acessibilidade     | Verificar interface com axe nos temas claro e escuro, em desktop e celular, incluindo navegação responsiva.                                                |

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

O Playwright inicia os servidores locais automaticamente e executa os quatro cenários em desktop (1440 × 900) e celular (390 × 844). A configuração usa a instalação Python da raiz; `E2E_PYTHON` permite indicar outro executável. Os relatórios ficam em `coverage/` e `playwright-report/`.

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

## Limites da evidência

Os testes de navegador usam o backend real e validam o arquivo WAV enviado, mas substituem as bordas de Azure, Gemini e classificação por respostas determinísticas. A classificação local também foi executada separadamente com o modelo real. Não havia credenciais para comprovar chamadas reais de Azure e Gemini; essa validação deve ser realizada no ambiente configurado antes da publicação.

Os testes não comprovam autenticação corporativa Entra, acesso real ao SharePoint, persistência de conversas, latência de produção ou conformidade integral de acessibilidade. A auditoria automática deve ser complementada por uso manual com teclado e leitor de tela. Conversas e token permanecem somente na memória da sessão, conforme a interface documentada.
