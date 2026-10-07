# S5-33 (#287) — Reexecução dos casos funcionais reprovados e do RNF06

Data da execução: 07/10/2026, America/Sao_Paulo. Origem: barema, item 10;
RNF06. Execução automatizada assistida por IA; revisão humana de outra frente:
pendente.

**Resultado: 2 casos aprovados na reexecução e 3 bloqueados.** CT-RF02-01 e
CT-RF03-02, que dependiam da S5-28 (#282), foram aprovados. CT-RF06-01,
CT-RF08-01 e a recuperação do RNF06 dependem da S5-12 (#266), que ainda não foi
iniciada: a issue está aberta, sem responsável e sem MR. Esses três casos não
foram reexecutados, porque a causa da falha original continua presente.

## Situação dos cinco itens

| Caso | Rodada anterior (23/09) | Correção esperada | Reexecução (07/10) | Evidência |
|---|---|---|---|---|
| CT-RF02-01 | FALHOU (DEF-RF02-01) | S5-28 (#282), integrada em `5dd9421` | **APROVADO** | [Observação](../../../src/backend/evidencias/rf-reexecucao-s5-33/rodada-01/CT-RF02-01.json) |
| CT-RF03-02 | FALHOU (DEF-RF03-01) | S5-28 (#282), integrada em `5dd9421` | **APROVADO** | [Observação](../../../src/backend/evidencias/rf-reexecucao-s5-33/rodada-01/CT-RF03-02.json) |
| CT-RF06-01 | FALHOU (DEF-RF06-01) | S5-12 (#266) | **BLOQUEADO** | Seção "Casos bloqueados" |
| CT-RF08-01 | FALHOU (DEF-RF06-01) | S5-12 (#266) | **BLOQUEADO** | Seção "Casos bloqueados" |
| RNF06, recuperação | Reprovado (*recall*@3 0,555556) | S5-12 (#266) | **BLOQUEADO** | Seção "Casos bloqueados" |

## Reexecução de CT-RF02-01 e CT-RF03-02

### Ambiente e protocolo

- Commit `e544388` da branch `test/s5-testes-sistemicos-finais`, que contém a
  `develop` em `84df352` e, portanto, a correção da #282.
- Windows 11, Python 3.13.9, torch 2.13.0, transformers 5.16.1 e
  scikit-learn 1.6.1. Classificador v2 com BERTimbau; o
  [manifesto](../../../src/backend/evidencias/rf-reexecucao-s5-33/rodada-01/manifesto.json)
  guarda o SHA-256 de cada artefato de `src/notebooks/artefatos`.
- Mesmas entradas da rodada de 23/09, enviadas a `POST /api/chat` em processo
  (`TestClient`). Classificador, regras de roteamento e extração de entidades
  são os reais.
- **Diferença em relação a 23/09:** a geração do texto pelo LLM foi
  substituída por um duplo, e o banco não foi usado. Os dois casos são
  julgados pela classificação e pelo encaminhamento, não pelo texto da
  resposta. O duplo registra se foi chamado e com qual intenção. Neste
  notebook, a política de controle de aplicativos do Windows bloqueia a DLL do
  `psycopg`, então não era possível repetir a consulta ao Supabase.

### Resultados

| Caso | Entrada | Observado | Critério | Resultado |
|---|---|---|---|---|
| CT-RF02-01 | `Mostre o status do projeto PRJ-0442` | HTTP 200; `CONSULTA` / `consulta_status_projeto`; handler `handler:consulta_status_projeto`; o provedor recebeu a intenção específica | Intenção primária de consulta de status, encaminhada ao catálogo | **APROVADO** |
| CT-RF03-02 | `Reserve uma sala de reunião para amanhã` | HTTP 200; `FORA_DE_ESCOPO`, sem intenção específica; handler `limitacao:agendamento`; provedor não chamado; 0 tokens; resposta local de limitação | Sem associação fictícia ao catálogo; fora de escopo ou reformulação | **APROVADO** |

**Como a aprovação acontece.** Nos dois casos, a decisão vem da camada de
roteamento criada na #282 (`app/nlp/routing.py`), aplicada depois da previsão
do modelo. O modelo não foi retreinado:

- No CT-RF02-01, a regra `consulta_status_explicita` seleciona
  `consulta_status_projeto`. As probabilidades do modelo são as mesmas de
  23/09: `transacao_atualizar_status` 0,4108 e `consulta_status_projeto`
  0,4030, ambas abaixo do limiar de 0,70. A confiança informada é a real, sem
  valor artificial.
- No CT-RF03-02, a regra `limite_agendamento` trata a reserva genérica como
  fora de escopo. O modelo ainda dá 0,7335 para `transacao_agendar_compromisso`,
  mas essa saída não é mais usada.

Os defeitos DEF-RF02-01 e DEF-RF03-01 ficam corrigidos no comportamento do
sistema. A sensibilidade lexical continua existindo dentro do modelo e está
contida pela regra. Paráfrases fora das regras dependem do modelo, como a
própria #282 registra.

Saída completa: [pytest](../../../src/backend/evidencias/rf-reexecucao-s5-33/rodada-01/pytest.txt)
e [JUnit](../../../src/backend/evidencias/rf-reexecucao-s5-33/rodada-01/pytest.xml).
Os dois casos também entram no job `backend-api` da pipeline, que instala o
classificador real.

Para reproduzir, a partir de `src/backend`, com `requirements-pln.txt`
instalado:

```bash
python -m scripts.run_s5_33 --round rodada-02
```

## Casos bloqueados

| Caso | Por que continua falhando | Dependência | Plano de desbloqueio |
|---|---|---|---|
| CT-RF06-01 | A base consultada pelo chat não tem documento do PRJ-0510, então a comparação sai só com o PRJ-0442 (DEF-RF06-01, Seção 9.1.5.4). Nada nessa base mudou desde 23/09. | S5-12 (#266): ampliar o SharePoint simulado com a estrutura do Metrô | Quando a #266 for integrada, reexecutar com o mesmo protocolo de 23/09 |
| CT-RF08-01 | Mesma causa: a resposta consolidada depende dos dois projetos na base | S5-12 (#266) | Reexecutar junto com o CT-RF06-01 |
| RNF06, recuperação | O recuperador e o corpus são os mesmos da avaliação prospectiva v2, que reprovou com *recall*@3 de 0,555556 (Seção 9.2.7) | S5-12 (#266) | Ver abaixo |

**Por que a massa nova do RNF06 não foi congelada agora.** A DoD pede a massa
congelada *antes da medição*. Como não houve medição, essa condição não foi
violada. Congelar as consultas agora seria precipitado: a S5-12 vai mudar o
corpus, e uma massa prospectiva precisa cobrir as fontes que existirão quando
a medição acontecer. O procedimento previsto é este:

1. integrar a #266;
2. escrever as consultas inéditas sobre o novo corpus, sem olhar o
   comportamento do recuperador;
3. registrar o SHA-256 da massa e dos artefatos;
4. só então executar `scripts/benchmark_rnf06.py`, uma única vez, como na v2.

Assim a medição não é contaminada.

## Defeitos remanescentes

| ID | Situação após a S5-33 | Destino |
|---|---|---|
| DEF-RF02-01 | Corrigido pela #282 (regra de roteamento); reexecução aprovada | Encerrado |
| DEF-RF03-01 | Corrigido pela #282 (regra de roteamento); reexecução aprovada | Encerrado |
| DEF-RF06-01 | Aberto; afeta CT-RF06-01 e CT-RF08-01 | Depende da #266. A consolidação (S5-36, #290) registra como remanescente se a #266 não entrar na sprint |
| RNF06, recuperação | Reprovado; sem nova medição | Mesmo destino do DEF-RF06-01 |
