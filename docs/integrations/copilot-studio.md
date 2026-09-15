# Integracao Copilot Studio, Entra ID e Direct Line

Este documento descreve a configuracao externa necessaria para a S4-22. O
codigo do repositorio nao prova, sozinho, que o tenant foi configurado. Somente
uma chamada executada no ambiente real pode ser usada como evidencia de
integracao concluida.

## Fronteiras implementadas

- `POST /api/integrations/copilot/dispatch`: operacao do custom connector.
- `POST /api/copilot/token`: broker de token temporario Direct Line para a
  bancada web. O segredo mestre nunca e devolvido ao navegador.
- `X-Correlation-ID`: aceito quando valido e devolvido em toda resposta dessas
  duas fronteiras.
- aliases de modelo: `auto`, `gpt` e `claude`. O backend rejeita qualquer outro
  valor e diferencia rota permitida de rota atualmente indisponivel.

O endpoint de despacho executa apenas classificacao e extracao de entidades.
Ele nao chama Gemini, GPT ou Claude. A geracao e a selecao concreta do modelo
continuam sob responsabilidade do Copilot Studio ou, se aprovado em ADR, de um
deployment do Foundry model router.

## 1. Registrar a API no Entra ID

1. Criar ou selecionar um app registration single-tenant para o backend.
2. Em **Expose an API**, definir o Application ID URI usado em
   `COPILOT_ENTRA_AUDIENCE`.
3. Criar os scopes delegados `copilot.invoke` e `copilot.channel`.
4. Autorizar o app registration usado pela conexao do custom connector para
   `copilot.invoke`.
5. Autorizar a aplicacao web somente para `copilot.channel`.
6. Conceder consentimento administrativo conforme a politica do tenant.

O backend valida assinatura RS256, issuer, tenant, audience, expiracao e scope.
Token valido com scope incorreto recebe `403`; token ausente, invalido ou
expirado recebe `401`. Indisponibilidade da descoberta/JWKS recebe
`503 AUTH_PROVIDER_UNAVAILABLE`. Nenhuma resposta contem detalhe da credencial.

## 2. Importar o custom connector

1. Copiar `src/backend/openapi/copilot-connector.v1.yaml`.
2. Substituir somente os placeholders `api.example.invalid`, `{tenant-id}` e
   `{backend-app-id}` pelos identificadores homologados.
3. Importar o arquivo no Power Platform e criar a connection reference.
4. Configurar OAuth 2.0/Entra ID com autorizacao delegada OBO.
5. Manter `model_route` como parametro interno do topico, nunca como texto ou
   escolha livre fornecida pela pessoa usuaria.
6. Executar os cenarios da matriz de evidencia abaixo.

Client secrets, certificados e tokens nao devem ser inseridos no YAML. Quando
um segredo for inevitavel, ele deve ser fornecido por connection reference ou
cofre do ambiente publicado.

## 3. Habilitar o canal web seguro

1. Publicar o agente e habilitar **Require secured access** no canal web.
2. Guardar um dos segredos Direct Line como `COPILOT_DIRECT_LINE_SECRET` no
   cofre/secret store do backend.
3. Definir `COPILOT_DIRECT_LINE_TRUSTED_ORIGINS` com origens exatas HTTPS.
4. A aplicacao autenticada chama `POST /api/copilot/token` com um access token
   contendo `copilot.channel`.
5. A aplicacao usa apenas o token temporario retornado para abrir a conversa.
6. Rotacionar pelos dois slots de segredo do canal sem indisponibilidade.

A bancada web nao altera a decisao de produto: Teams/Copilot Studio permanece
o canal principal ate que uma ADR e a GTI aprovem outro canal.

## 4. Politica de modelos

`COPILOT_ALLOWED_MODEL_ROUTES` e a allowlist arquitetural.
`COPILOT_AVAILABLE_MODEL_ROUTES` contem somente aliases habilitados e testados
no tenant. Exemplo durante homologacao:

```dotenv
COPILOT_ALLOWED_MODEL_ROUTES=auto,gpt,claude
COPILOT_AVAILABLE_MODEL_ROUTES=auto,gpt
```

Uma rota permitida, mas nao disponivel, recebe
`503 MODEL_ROUTE_UNAVAILABLE`; valor desconhecido ou proibido recebe
`422 MODEL_ROUTE_NOT_ALLOWED`. Nao existe fallback silencioso.

Antes de disponibilizar `gpt` ou `claude`, registrar em ADR se o alias aponta
para modelo primario/prompt do Copilot ou para Foundry model router. A politica
deve definir teto de tokens, chamadas e tempo e impedir loops autonomos.

## 5. Auditoria e correlacao

No ambiente integrado, configurar `COPILOT_AUDIT_REQUIRED=1` e uma URL de banco.
O despacho somente retorna sucesso se `ai_conversations`, `ai_interactions` e
`audit_events` puderem receber a evidencia. Sao correlacionados:

- `request_id`: identificador estavel do pedido, usado como base para a futura
  deduplicacao dos fluxos com efeito externo;
- `correlation_id`: propagacao entre sistemas;
- `execution_id`: tentativa atual do backend;
- `conversation_id`: conversa Direct Line/Copilot;
- `interaction_id`: registro persistido pelo backend.

Os futuros webhooks S4-25B/C devem propagar `correlation_id`, `execution_id` e
o identificador de run do Power Automate. A idempotencia dos callbacks pertence
a essas tasks dependentes e nao e simulada pela S4-22.

## 6. Matriz de evidencia no tenant

| Cenario | Resultado esperado |
|---|---|
| Token valido com `copilot.invoke` | `200`, IDs correlacionaveis e auditoria persistida |
| Token ausente ou assinatura invalida | `401 UNAUTHENTICATED`, sem detalhe interno |
| Token expirado | `401 UNAUTHENTICATED` |
| Token valido sem scope | `403 FORBIDDEN` |
| Descoberta/JWKS do Entra indisponivel | `503 AUTH_PROVIDER_UNAVAILABLE` |
| `model_route` desconhecido | `422 MODEL_ROUTE_NOT_ALLOWED` |
| Alias permitido indisponivel | `503 MODEL_ROUTE_UNAVAILABLE`, sem fallback silencioso |
| Falha temporaria Direct Line | repeticao limitada e `503` controlado ao esgotar |
| Repeticao de callback | coberta pelas S4-25B/C, sem duplicar efeito |

Nunca anexar access tokens, segredo Direct Line, authorization headers ou
valores de connection references como evidencia.
