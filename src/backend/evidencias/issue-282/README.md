# Aceitar perguntas curtas e ajustar fronteiras de intenção — #282

## Acordo e casos congelados

Esta entrega trata O1 e os defeitos DEF-RF02-01 e DEF-RF03-01 da Sprint 05.
Os casos foram extraídos da seção 9.3.2 de `docs/Projeto.md` e dos registros
`evidencias/rf01-rf10/rf02/CT-RF02-01-status.txt` e
`evidencias/rf01-rf10/rf03/CT-RF03-02-reserva-sala.txt` antes da alteração.

| Origem | Entrada congelada | Resultado esperado |
| --- | --- | --- |
| O1 | `fale sobre os Objetos perdidos` | CONSULTA documental, sem exigir projeto |
| O1 | `fale sobre o Bilhete digital` | CONSULTA documental, sem exigir projeto |
| O1 | `Bilhete digital` | CONSULTA documental, sem exigir projeto |
| CT-RF02-01 | `Mostre o status do projeto PRJ-0442` | CONSULTA / consulta_status_projeto |
| CT-RF03-02 | `Reserve uma sala de reunião para amanhã` | FORA_DE_ESCOPO, sem acionar agendamento ou provedor |

As paráfrases adicionais incluem perguntas com caixa e acentos diferentes,
`Como funciona o bilhete digital?`, `achados e perdidos`, `Exiba o andamento
da Linha 5-Lilás` e `Qual é o status do projeto PRJ-0442?`. Os controles
negativos incluem alteração de status, negação, pedido misto, clima e saudação.
Agendamentos vinculados a projeto, linha ou portfólio preservam a decisão do
modelo; agendamentos genéricos não são promovidos a transações do catálogo.

## Decisão e limites

O modelo, seus vetorizadores, dataset e limiares foram preservados. O ajuste é
uma camada explícita de roteamento depois da previsão, em `app/nlp/routing.py`.
Consultas curtas sobre Bilhete digital, Objetos perdidos e Achados e perdidos
seguem para a recuperação documental. Esses temas existem nas bases
`app/rag/data/sharepoint/base_atendimento.json` e
`app/rag/data/sharepoint/procedimentos_operacionais.json`.

O reconhecimento usa a pergunta inteira, evitando que citar um tema em uma
transação a converta em consulta. A regra de status aceita solicitações
explícitas de consulta com escopo de domínio e não converte pedidos de
alteração, negativos ou mistos. A reserva de sala não é uma capacidade do
catálogo, mesmo quando a frase menciona um projeto. Sua resposta é produzida
localmente, com zero tokens do provedor, e segue para a auditoria.

`intent.routing_rule` identifica a regra aplicada. As confianças informadas
continuam sendo probabilidades reais do modelo para a classe selecionada,
podendo estar abaixo do limiar; não se atribui confiança artificial de 100%.
A resposta de reformulação oferece exemplos de tema e de projeto, sem tornar
um projeto obrigatório. A constante equivalente do frontend foi sincronizada.

Esta entrega amplia os exemplos de regressão e as paráfrases aceitas no
roteamento, sem retreinar com os casos de teste. A lista de temas operacionais
é deliberadamente limitada aos temas congelados e ao sinônimo registrado na
base. Novos temas precisam de exemplos e validação próprios. O acerto do
roteamento não comprova que o provedor externo produziu uma resposta factual.

## Verificação reproduzível

Na raiz do repositório, com as dependências do backend e de
`src/backend/requirements-pln.txt` instaladas e o BERTimbau disponível:

```powershell
$env:PYTHONPATH = 'src/backend'
$env:HF_HUB_OFFLINE = '1' # usar apenas quando o snapshot já estiver em cache
python -m pytest src/backend/app/tests/test_nlp_inference.py -q -p no:cacheprovider
python -m pytest src/backend/app/tests/test_nlp_domain_routes.py src/backend/app/tests/test_pipeline_api.py src/backend/app/tests/test_nlp_entities.py src/backend/app/tests/test_nlp_preprocessing.py -q -p no:cacheprovider
python -m pytest src/backend/app/tests/test_audio_upload.py src/backend/app/tests/test_traceability.py -q -p no:cacheprovider
git diff --check
```

Os XMLs nesta pasta registram as execuções locais. `resultado.json` contém a
medição independente sobre as 1.135 entradas do split `teste`, hashes do dataset
e do modelo e as saídas dos nove casos congelados e paráfrases com o modelo
real. O F1-macro mede a intenção específica prevista pelo modelo antes dos
limiares e regras, conforme o protocolo existente do classificador. A aceitação
dos casos operacionais é verificada separadamente pelos testes de roteamento.

Resultado final: **224 testes aprovados** — 34 de inferência e benchmark,
108 de roteamento/API/entidades/pré-processamento e 82 de áudio/auditoria.
`congelados.xml` registra também a execução isolada dos nove casos reais.
As suítes de API/áudio emitiram somente o aviso de depreciação existente do
cliente de testes Starlette; não houve falha. `git diff --check` passou.

O benchmark reproduziu F1-macro **0,832724**, acima da meta **0,80**, sem
retreino. O teste da reserva confirma ausência de chamada ao provedor, fontes
vazias, resposta de limitação e uma chamada de auditoria. O arquivo de
constantes do frontend passou na verificação de formatação com Prettier.

Não foram executados testes com Gemini, banco de produção, transcrição Azure
real ou participantes de usabilidade; os testes de integração substituem os
serviços externos. Não foi executado o build completo do frontend: a alteração
nesse componente é somente o texto da constante. A aprovação escrita do
revisor e o merge continuam pendentes da revisão humana.
