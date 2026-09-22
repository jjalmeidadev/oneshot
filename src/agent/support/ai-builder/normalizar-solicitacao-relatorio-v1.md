# normalizar-solicitacao-relatorio-v1

Estado: desativado por padrão. Uso permitido somente após autorização e
validação determinística.

Entrada: texto livre já limitado ao pedido de relatório e catálogo fechado de
valores permitidos.

Instrução: extraia somente valores explicitamente presentes. Nunca invente
escopo, datas ou intenção. Quando houver ambiguidade, retorne o campo em
`missing_fields`.

Saída JSON fixa:

```json
{
  "schema_version": "1.0",
  "report_type": "executive_status",
  "scope_type": "project|subportfolio|null",
  "scope_reference": "string|null",
  "period_start": "YYYY-MM-DD|null",
  "period_end": "YYYY-MM-DD|null",
  "audience": "executive_board|pmo|project_team|null",
  "purpose": "monthly_governance|decision_support|status_communication|null",
  "emphasis": [],
  "missing_fields": [],
  "ambiguities": []
}
```

