# S5-27 (#281) — Bloqueio de dado sensível antes do provedor

Corrige o defeito **D-06** do relatório S4-33: um marcador sensível injetado na massa atravessava a montagem do prompt e seria enviado ao provedor de LLM. O RNF01 era atendido por convenção (a massa é sintética), e não por controle.

## Padrões acordados

Lista acordada pelo grupo para o DoR. A implementação está em `src/backend/app/security/sensitive_data.py`.

| Categoria | Detecção | Substituto |
|---|---|---|
| Marcador de classificação | `DADO SENSÍVEL` (inclusive `DADO-SENSIVEL-…`); `CONFIDENCIAL`, `SIGILOSO` e `RESTRITO` em maiúsculas; `Classificação: confidencial/restrito/sigiloso` | `[DADO CLASSIFICADO]` |
| Classificação no metadado | `project_artifacts.confidentiality_level` igual a `restrito` ou `confidencial` | documento retido |
| CPF | com ou sem pontuação, **com dígito verificador válido** | `[CPF]` |
| CNPJ | com ou sem pontuação, com dígito verificador válido | `[CNPJ]` |
| E-mail | endereço completo | `[E-MAIL]` |
| Telefone | com DDD e hífen, com ou sem `+55` | `[TELEFONE]` |
| Cartão | 13 a 19 dígitos que passam no algoritmo de Luhn | `[CARTÃO]` |
| Credencial | chave `AIza…`, `sk-…`, JWT, `Bearer …`, `senha:`/`token:`/`api_key:` com valor | `[CREDENCIAL]` |

Os padrões priorizam a precisão. A palavra "restrito" em minúsculas ("acesso restrito à via"), CPF com dígito errado, códigos como `PRJ-0442`, datas e valores monetários **não** são tratados como sensíveis. A massa sintética (9 documentos), os seeds SQL e o prompt montado com todos os documentos não têm nenhuma ocorrência.

## Barreiras

| Etapa | Onde | O que acontece |
|---|---|---|
| Pergunta (texto ou transcrição) | `pipeline.process_message`, antes da classificação | A pergunta é **bloqueada** com resposta controlada (`model = bloqueio-dado-sensivel`), e nenhuma chamada externa sai. |
| Documentos do RAG | `generate_chat_response`, logo após `retrieve_context` | O dado é **mascarado** no título, no conteúdo, nos atributos e no nome do projeto. Documentos `restrito` ou `confidencial` ficam fora do contexto. Se nada sobrar, a resposta é de evidência insuficiente, sem chamada. |
| Prompt final | `_call_llm`, único ponto de chamada ao Gemini e ao OpenRouter | Varredura de defesa em profundidade. Se algo escapar das barreiras anteriores, a chamada é recusada com `SensitiveDataBlockedError` (HTTP 422). |

A versão mascarada dos documentos é a mesma usada no prompt, nas fontes exibidas e na verificação de evidência, para que a resposta continue conferível.

## Auditoria sem expor o dado

- Novo evento `sensitive_content_blocked` em `audit_events`, com `component = api` e `event_status = bloqueado`. O payload traz a etapa, a ação, as categorias, as contagens e os IDs das fontes mascaradas ou retidas. Nunca traz o valor.
- A pergunta bloqueada é gravada **já mascarada** em `ai_interactions.user_prompt` e `normalized_prompt`, por exemplo `meu CPF e [CPF]`.
- `processing_status = erro`, com o motivo registrado como falha controlada. A restrição `ai_interactions_status_ck` não aceita `bloqueado`, e a decisão da S5-27 foi não alterar o schema nesta task.

## Execução

```bash
cd src/backend
python -m pytest app/tests/test_rnf01_rnf03_s4_33.py app/tests/test_sensitive_data_rnf01.py -v
```

| Caso | Antes (develop `28337f4`) | Depois |
|---|---|---|
| CT-RNF01-P (massa sintética e origem declarada) | Aprovado | Aprovado |
| CT-RNF01-N (marcador injetado na cópia da massa, envio pelo caminho real com duplo de rede) | **Falhou**: o payload capturado continha o marcador | **Aprovado**: zero chamadas com dado sensível; o payload leva `[DADO CLASSIFICADO]` |
| `test_sensitive_data_rnf01.py` (28 casos) | não existia | 28 aprovados |

Os 28 casos novos cobrem:

- os 12 padrões acordados e 7 falsos positivos;
- a ausência de achados na massa e no prompt;
- o mascaramento e a retenção de documentos;
- a chamada real com duplo de rede;
- a resposta sem chamada quando só há documentos classificados;
- a guarda final;
- o bloqueio da pergunta pela API, de texto e de áudio, sem classificação e sem chamada;
- a auditoria sem o dado.

Para a suíte do job `backend-api`, os arquivos novos foram incluídos no `.gitlab-ci.yml`. Resultado local, já com a develop da autenticação: 373 aprovados (a develop sozinha tem 342). Os 3 testes com classificador real dependem do `requirements-pln.txt` (torch) e falham no ambiente sem essas dependências, antes e depois desta mudança.

## Limitações

- **O áudio é enviado bruto ao Azure Speech** antes de virar texto, então não pode ser inspecionado antes dessa fronteira. A transcrição passa pela barreira da pergunta normalmente.
- **A detecção é por padrão**, não por classificação semântica. Nome de pessoa, endereço e valores de contrato não são reconhecidos sem um rótulo explícito. Ampliar a lista é uma decisão do grupo, e o lugar de mudar é `PATTERNS` em `sensitive_data.py`.
- **A reexecução formal do RNF01 a RNF03** com as correções é a S5-30 (#284).
