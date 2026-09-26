# redigir-resumo-executivo-v1

Estado: desativado por padrão. O fallback determinístico do backend é a
implementação ativa.

Redija no máximo 140 palavras usando exclusivamente o JSON validado. Não
calcule valores, não selecione riscos ou benefícios e não transforme previsão
em realização. Cada afirmação factual deve apontar para um `source_id`
recebido. Se faltarem evidências, declare a limitação.

Saída JSON fixa:

```json
{
  "schema_version": "1.0",
  "summary": "string",
  "citation_source_ids": [],
  "limitations": []
}
```
