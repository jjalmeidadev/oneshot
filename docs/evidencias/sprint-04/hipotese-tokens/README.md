# Hipótese de economia de tokens por intenção

## Objetivo

Esta evidência da issue #253 mede se o classificador local reduz o consumo
agregado de tokens da LLM e separa esse efeito do custo de preparar uma intenção
secundária. O experimento não usa tempo de resposta como métrica.

## Hipóteses e mecanismos

- **H1 — classificador:** reduz tokens quando bloqueia solicitações fora de
  escopo ou encaminha uma transação para um workflow sem LLM. Em consultas que
  chegam ao modelo, a intenção primária é enviada em uma linha compacta com
  macrointenção, intenção específica e handler.
- **H2 — intenção secundária:** a resposta secundária é preparada junto da
  resposta principal. A confirmação posterior somente libera o texto
  persistido; portanto, não há uma segunda chamada à LLM.

A economia só é considerada útil quando o resultado funcional permanece
aceitável. Uma redução causada apenas por não responder a uma consulta válida
deve ser registrada como falha, e não como sucesso da hipótese.

## Desenho A/B

A massa congelada em `casos.json` contém três solicitações: uma consulta com
fonte controlada, uma geração de relatório com workflow local e uma solicitação
fora de escopo. Cada caso passa pelas variantes abaixo, sempre com o mesmo
modelo, limite de saída, temperatura e conteúdo-fonte:

| Variante | Classificador | Secundária na chamada principal |
| --- | --- | --- |
| `classificador_desligado` | Não | Não |
| `classificador_ligado` | Sim | Não |
| `classificador_e_secundaria_inline` | Sim | Sim, quando houver associação |

O script registra por caso e variante:

- JSON enviado ao OpenRouter e JSON integral devolvido pelo provedor;
- tokens de entrada, saída, raciocínio e total;
- número de chamadas à LLM;
- classificação, intenção secundária, quantidade de fontes e resultado
  funcional básico;
- hash SHA-256 do prompt, sem persistir a chave de API.

## Configuração e execução

O segredo fica somente em `src/backend/.env`, ignorado pelo Git:

```dotenv
OPENROUTER_API_KEY=<chave-local>
OPENROUTER_MODEL=google/gemini-3.1-flash-lite
OPENROUTER_MAX_OUTPUT_TOKENS=256
```

O modelo padrão foi escolhido por ser uma opção de alta eficiência disponível
no OpenRouter. Para reproduzir a rodada:

```powershell
Set-Location src/backend
python scripts/benchmark_token_hypothesis.py
```

Cada execução cria um diretório UTC em `execucao/`, com `resultado.json` e uma
pasta `json-bruto/`. A redução consolidada usa:

```text
1 - (tokens da variante / tokens com classificador desligado)
```

Não some `total_tokens` aos seus componentes: o total já representa a contagem
consolidada informada pelo provedor.

## Critérios de interpretação

1. H1 recebe apoio quando `classificador_ligado` usa menos tokens e menos
   chamadas que `classificador_desligado`, sem falha funcional nos casos.
2. H2 recebe apoio operacional quando a confirmação da sugestão não chama o
   provedor novamente. O custo de preparar a resposta secundária continua
   pertencendo à chamada principal e deve ser comparado separadamente.
3. Três prompts demonstram o mecanismo, mas não estimam economia de produção.
   Uma conclusão generalizável exige uma massa maior e representativa da
   distribuição real de intenções.
4. Os tokens são comparáveis apenas dentro da mesma rodada e do mesmo modelo.
   Mudanças de provedor, modelo, fontes ou limite de saída invalidam a
   comparação direta.

## Resultado observado

A rodada de 23 de setembro de 2026 está registrada em
[`execucao/20260923T190626Z/resultado.json`](execucao/20260923T190626Z/resultado.json).
A massa enviada ao provedor é inteiramente sintética e os arquivos foram
verificados para confirmar que não contêm a chave de API.

| Variante | Chamadas | Entrada | Saída | Total | Redução contra desligado |
| --- | ---: | ---: | ---: | ---: | ---: |
| Classificador desligado | 3 | 211 | 396 | 607 | 0% |
| Classificador ligado | 1 | 204 | 141 | 345 | 43,16% |
| Classificador + secundária inline | 1 | 343 | 180 | 523 | 13,84% |

Nos três casos, o classificador identificou corretamente a consulta, a
transação e a solicitação fora de escopo. A transação foi encaminhada ao
workflow local e o caso fora de escopo recebeu a limitação local, eliminando
duas chamadas ao modelo. A consulta conservou a citação esperada nas três
variantes.

Assim, **H1 recebeu apoio nesta amostra**: a economia agregada veio do
roteamento, não de uma redução do prompt da consulta. Isoladamente, incluir a
intenção compacta aumentou a entrada da consulta de 189 para 204 tokens, mas
permitiu que o sistema tomasse as decisões que reduziram o número total de
chamadas.

**H2 recebeu apoio operacional, mas não demonstra economia isolada na chamada
inicial.** A variante inline produziu a resposta primária e a resposta
secundária preparada em uma única chamada. Ela consumiu 178 tokens a mais que
a variante com apenas o classificador, aumento de 51,59%, embora ainda tenha
consumido 13,84% menos que o cenário totalmente desligado. O ganho líquido da
secundária depende da frequência com que a sugestão é aceita e do custo da
segunda chamada que existia antes; esta rodada não reconstruiu essa chamada
legada.

O verificador funcional desta prova é deliberadamente básico: confere o
roteamento e, quando há fonte, a presença da citação. A amostra de três prompts
demonstra o mecanismo, mas não estima o tráfego de produção. Tempo de resposta
não foi coletado, conforme a delimitação da issue.

## Referências do provedor

- [OpenRouter — Quickstart](https://openrouter.ai/docs/quickstart)
- [OpenRouter — Chat completions](https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request)
- [OpenRouter — Gemini 3.1 Flash Lite](https://openrouter.ai/google/gemini-3.1-flash-lite)
