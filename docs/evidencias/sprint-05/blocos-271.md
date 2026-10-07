# Evidências da issue #271 — blocos nas respostas

## Entrega e decisão

O frontend apresenta os blocos `table`, `indicator` e `highlight` do contrato 1.2.0 da #270. O texto original continua visível, inclusive em respostas antigas sem `blocks`. Os blocos são preservados pela conversão para a mensagem e pelos canais de texto e áudio. Respostas com evidência insuficiente ou erro não exibem blocos factuais.

A tabela tem legenda, cabeçalhos de coluna e referências por linha. Em telas pequenas, a região recebe foco e permite rolagem horizontal por teclado, sem ampliar a página. O indicador usa lista de definição e formatação `pt-BR`: `42.5` com unidade `%` é exibido como `42,5%`, sem multiplicar o valor. O destaque tem nome acessível, texto “Destaque” e ícone decorativo, sem depender da cor ou anunciar urgência que o contrato não informa. Os blocos ficam dentro do log de mensagens já anunciado pelo chat.

As referências dos blocos abrem o documento correspondente pelo identificador da citação, incluindo fontes com `citation_id` explícito. Uma referência não encontrada fica como texto. HTML é exibido literalmente. Tipos desconhecidos, números não finitos e tabelas não retangulares são ignorados, preservando a mensagem original.

## Validação executada em 05/10/2026

Em `src/frontend`:

| Procedimento | Resultado observado |
| --- | --- |
| `npm test` | 13 arquivos e 83 testes aprovados; inclui 10 cenários de componentes e 2 cenários de preservação dos blocos nos canais |
| `npm run build` | TypeScript e compilação de produção aprovados |
| `npm run lint` | Aprovado, sem avisos |
| Prettier nos nove arquivos TypeScript alterados | Aprovado |
| `git diff --check` | Aprovado |
| `npm exec -- playwright test --config playwright.blocks.config.ts` | 4 cenários aprovados: desktop 1440×1000 e celular 390×844, em tema claro e escuro |

Os testes em navegador verificam os três tipos dentro do chat, ausência de transbordamento horizontal da página, foco na região da tabela e abertura da fonte com Enter. O axe-core analisa os novos blocos com tags `wcag2a`, `wcag2aa` e `wcag21aa`: nenhum cenário apresentou violação ou resultado inconclusivo de contraste. A inspeção das capturas confirmou a apresentação nos dois tamanhos e temas.

As capturas usam dados sintéticos de teste, não dados do parceiro:

- [Desktop claro](blocos-271-desktop-light.png)
- [Desktop escuro](blocos-271-desktop-dark.png)
- [Celular claro](blocos-271-mobile-light.png)
- [Celular escuro](blocos-271-mobile-dark.png)

## Reprodução e critérios de aceite

1. Instalar as dependências com `npm ci` em `src/frontend`, caso necessário, e disponibilizar o Chromium do Playwright (`npm exec -- playwright install chromium`).
2. Executar `npm test`, `npm run build` e `npm run lint`. Os três comandos devem terminar sem falhas.
3. Executar `npm exec -- playwright test --config playwright.blocks.config.ts`. Os quatro cenários devem passar e as capturas acima devem ser produzidas. A configuração inicia o frontend na porta 5176 e simula apenas as respostas HTTP necessárias, sem credenciais reais.
4. Para conferir a semântica, consultar `src/frontend/src/components/chat/response-blocks.tsx` e seus testes: a tabela deve ter caption e scope, o indicador deve associar nome e valor e o destaque deve ter nome e rótulo textual. As referências devem funcionar com Tab e Enter.

## Dependências e limites

A branch foi criada a partir de `origin/develop` em `d54c9ba`. O contrato foi conferido contra `feature/270-blocos-resposta` em `37ea9d3`. A #270 ainda precisa ser integrada para que o backend de develop produza blocos reais; esta entrega não incorpora os commits da dependência e não altera o backend.

A validação automática de acessibilidade e a semântica são evidências de suporte a leitor de tela. Uma sessão manual com NVDA ou outro leitor de tela não foi executada. A análise axe foi restrita aos novos blocos, não certifica toda a aplicação. Os testes de navegador usam fixtures do contrato; não foi executada uma chamada a um provedor real de IA.

A aprovação e o comentário substantivo de @jaime.almeida continuam pendentes. O item da DoD que exige MR aprovado só poderá ser marcado após essa revisão. Não foi realizado merge nem fechamento da issue.
