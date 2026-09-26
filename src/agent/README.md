# Artefatos legados e portaveis do fluxo de relatorio

O Copilot Studio foi removido da arquitetura de execucao porque o ambiente do
parceiro nao sera disponibilizado. `ONESHOT/` permanece somente como historico
da exportacao anterior e nao deve ser publicado, sincronizado ou tratado como
runtime da solucao.

Os artefatos ainda reutilizaveis estao em `support/`:

- `ai-builder/`: prompts com saida JSON fixa;
- `power-automate/`: blueprint HTTP assincrono;
- `openapi/`: contrato da API e do callback;
- `word/`: referencia de conteudo e layout do DOCX;
- `fixtures/`: exemplos de payload.

## Runtime vigente

1. O PLN retorna `handler:transacao_gerar_relatorio`.
2. `POST /api/chat` devolve uma diretiva `guided_workflow`.
3. O frontend inicia `POST /api/workflow-sessions` e apresenta no chat cada
   pergunta, opcao, revisao e confirmacao.
4. O backend valida identidade, escopo e concorrencia e cria a execucao.
5. Em `local`, o backend processa diretamente. Em
   `power_automate_simulator`, exercita o mesmo callback sem tenant externo. Em
   `power_automate`, envia por HTTP o snapshot autorizado ao fluxo real.
6. O Power Automate usa AI Builder apenas para transformacoes delimitadas e
   devolve JSON a `POST /api/integrations/power-automate/report-results`.
7. O backend valida o JSON, aplica fallback deterministico quando necessario,
   gera o DOCX e o grava em Storage privado do Supabase.
8. O frontend acompanha o status e baixa o arquivo autenticado no proprio chat.

Nao existem dependencias de Copilot Studio, SharePoint, OneDrive ou Word Online
na execucao vigente. O DOCX e produzido com `python-docx`; o Supabase guarda o
arquivo privado e o PostgreSQL guarda estado, correlacao e auditoria.

## Modos suportados

| Modo | Automacao | Armazenamento |
| --- | --- | --- |
| `local` | backend | `local` para desenvolvimento |
| `power_automate_simulator` | callback local com o contrato real | `local` ou `supabase` |
| `power_automate` | fluxo Microsoft via HTTP + callback | `supabase` recomendado |

O modo real somente pode ser declarado integrado depois de configurar as
connection references do AI Builder, os dois tokens, a URL HTTPS do backend e
executar a homologacao no tenant de destino.
