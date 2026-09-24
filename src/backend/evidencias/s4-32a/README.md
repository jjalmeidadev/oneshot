# Evidências funcionais — S4-32A

Esta pasta consolida as evidências dos testes funcionais RF01–RF10 executados na Sprint 4.

## Resultado consolidado

- Casos planejados: 20
- Casos executados: 20
- APROVADO: 16
- FALHOU: 4
- BLOQUEADO: 0
- NÃO EXECUTADO: 0

## Regra de proveniência

Os arquivos usam dois tipos de registro:

- `TIPO DE REGISTRO: SAÍDA BRUTA PRESERVADA`: o conteúdo integral relevante foi preservado no histórico da execução.
- `TIPO DE REGISTRO: REGISTRO CONSOLIDADO`: os valores observados foram preservados durante a execução, mas o dump integral original do terminal não está disponível neste pacote. Nenhum campo ausente foi inventado.

Credenciais, tokens, senhas e chaves foram deliberadamente omitidos.

## Defeitos

- DEF-S4-32A-01 — sensibilidade lexical na classificação de consulta de status.
- DEF-S4-32A-02 — reserva genérica associada a `transacao_agendar_compromisso`.
- DEF-S4-32A-03 — recuperação/contextualização incompleta em comparação multi-projeto.

CT-RF08-01 é afetado pela mesma causa raiz de DEF-S4-32A-03.
