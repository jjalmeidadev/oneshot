# Gate de conflitos e suíte de integração — issue #255

## Entrega

O hook `.githooks/pre-commit` e o job `conflict-markers` usam
`scripts/check-conflict-markers.sh`, com a regex da Seção 5.3.3 de
`GestaoConfiguracao.md`. A busca examina o índice Git (`--cached`), ignora
arquivos binários (`-I`) e informa arquivo e linha de cada ocorrência. Assim,
uma resolução ainda não adicionada ao stage não libera um commit com conflito.
Arquivos não rastreados e alterações fora do stage não fazem parte do commit.
Erro operacional do Git também reprova a verificação.

O estágio `validate` antecede `test`: um conflito interrompe a pipeline antes
dos testes de frontend e backend. Os controles anteriores do hook continuam
ativos. Instale os hooks com `scripts/install-hooks.sh` ou
`scripts/install-hooks.ps1`, conforme o ambiente.

O job `backend-api` executa:

```sh
cd src/backend
python -m pytest app/tests -m integration --strict-markers -q -o junit_family=legacy --junitxml=evidencias/backend-junit.xml
```

Todos os 14 módulos anteriormente enumerados pelo job permanecem selecionados.
Oito deles receberam `pytestmark = pytest.mark.integration`; os demais já
possuíam o marcador. O registro existente em `conftest.py` foi preservado.
Novos testes com esse marcador entram na CI sem editar a lista de arquivos.
O relatório JUnit continua disponível como artefato por sete dias.

## Verificação local em 01/10/2026

```sh
python -m unittest discover -s scripts/tests -v
```

Resultado: **7 testes aprovados**. Os cenários executam o script do job e o
hook real em repositórios Git temporários. Foram conferidos:

- Rejeição de cada marcador de início, separação e fim em LF e CRLF.
- Rejeição do separador com espaços e tabulação.
- Aceitação de `================ 10 passed` e exemplos no meio de uma linha.
- Rejeição de conflito staged mesmo após resolver a cópia local.
- Aceitação de marcadores fora do stage, arquivos não rastreados e binários.
- Aceitação após remover o arquivo conflitante do índice.
- Falha explícita quando não é possível consultar um repositório Git.

A inspeção da lista anterior confirmou **14/14 módulos preservados**.
O YAML foi carregado com sucesso e a ordem dos estágios foi conferida.

A primeira rodada completa encontrou uma dependência ausente no ambiente local
(`psycopg-pool`): 375 testes aprovados, uma falha, 25 ignorados, 112 não
selecionados e dois `xfail`. As dependências `python-docx`, `psycopg-pool` e
`psycopg[binary]`, já declaradas pelo projeto, foram instaladas somente no
ambiente local isolado. O código de produção e os critérios dos testes não
precisaram mudar.

A rodada final completa passou: **376 aprovados, 25 ignorados, 112 não
selecionados e dois `xfail`, sem falhas**, em 203,35 segundos. Python 3.13.15
e pytest 9.1.1. A execução local limitou `OMP_NUM_THREADS` e `MKL_NUM_THREADS`
a dois e usou o diretório isolado de dependências em `PYTHONPATH`; essas
configurações não alteram a pipeline. Foram emitidos dois avisos de depreciação
do FastAPI/Starlette. O [JUnit final](issue-255-backend-junit.xml) registra os
casos e resultados. O subconjunto sem `test_nlp_inference.py` também passou:
351 aprovados, 25 ignorados, 137 não selecionados e dois `xfail`.

## Evidência negativa e positiva na CI

A variável opcional `CONFLICT_MARKERS_PROBE=1` insere um marcador em
`.conflict-marker-probe` e adiciona esse arquivo somente ao índice descartável
do runner antes da verificação. O resultado esperado é o job
`conflict-markers` vermelho, com a ocorrência identificada no log, e os jobs
do estágio `test` impedidos de iniciar. Nenhum marcador é commitado.

Foi enviado o commit `d8cc695` na branch `ci/255-gate-marcadores-integracao`
com essa variável pelo push, para executar a sondagem negativa. A branch de
entrega é `feature/255-gate-marcadores-integracao`.

Para repetir pelo GitLab, abra **Build → Pipelines → New pipeline**, selecione
a branch da entrega e informe `CONFLICT_MARKERS_PROBE=1`. Para a rodada
positiva, execute uma nova pipeline sem essa variável (ou com valor `0`).
A variável não altera configurações persistentes do projeto e não permite
ignorar o gate: serve exclusivamente para comprovar sua rejeição.

Os resultados das pipelines precisam ser conferidos no GitLab e vinculados
ao MR. A aprovação e o comentário de revisão cabem a @leonardo.vieira.
Testes dependentes de backend externo ou banco real seguem seus próprios
`skip` quando o ambiente necessário não está disponível; os `xfail` existentes
continuam indicando defeitos conhecidos, sem esconder falhas novas.


## Resolução dos conflitos do MR !120 — 06/10/2026

Integração da `develop` em `9c7b6aa`. A resolução de `.gitlab-ci.yml` preserva
o estágio `validate`, o gate `conflict-markers` e sua sondagem negativa, junto
do job `validar-titulo-mr` introduzido na develop. O backend continua selecionando
os testes com `-m integration --strict-markers` e mantém a instalação CPU do
PyTorch. Os novos módulos de acesso, carga de identidades e proteção de dados
sensíveis receberam o marcador de integração para que não sejam excluídos do job.

Validações executadas:

```shell
python -m unittest discover -s scripts/tests -v
sh scripts/test-validate-mr-title.sh
# Em src/backend:
python -m pytest app/tests -m integration --strict-markers -q -p no:cacheprovider
```

Resultado: **7 testes do gate aprovados**; testes da validação do título aprovados;
**453 testes de integração aprovados, 25 ignorados, 112 não selecionados e um
xfail**, sem falhas, em 387,02 segundos. A execução local usou dependências
isoladas e limitou `OMP_NUM_THREADS` e `MKL_NUM_THREADS` a dois.
Foram emitidos avisos de depreciação e de incompatibilidade de `record_property`
com o formato JUnit local; a CI mantém `junit_family=legacy`.
A estrutura YAML foi conferida e `git diff --check` passou. O gate foi executado
sobre o índice final antes do commit. Serviços externos não configurados
continuam cobertos pelos skips existentes. A pipeline remota deve ser conferida
separadamente; os resultados acima são locais.

## Correção das regras da pipeline do MR !120 — 06/10/2026

A [pipeline de branch #88573](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/pipelines/88573),
do commit `713173f8`, não iniciou jobs: o GitLab informou
`Project exceeded the allowed number of jobs in active pipelines. Retry later.`
É um limite de jobs ativos do projeto, não uma falha de teste.
A [pipeline de MR #88574](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/pipelines/88574)
passou, mas incluía apenas a validação do título. Os quatro jobs sem `rules`
não eram selecionados para eventos de merge request, deixando de verificar
o gate e a suíte de integração no resultado usado pelo MR.

O `workflow:rules` agora impede a pipeline duplicada de push quando a branch
tem MR aberto. Eventos de MR continuam permitidos. Execuções manuais,
agendadas, acionadas e de tags continuam permitidas, incluindo a sondagem
negativa manual documentada acima. Cada um dos quatro jobs recebeu
`rules: [{when: on_success}]`, para participar também da pipeline do MR,
respeitando o estágio `validate`: se o gate falhar, os testes não iniciam.
A validação do título continua exclusiva de eventos de MR.
Essa configuração segue a [orientação oficial do GitLab para evitar pipelines duplicadas](https://docs.gitlab.com/ci/yaml/workflow/#switch-between-branch-pipelines-and-merge-request-pipelines).

Validação desta correção:

- Os sete testes existentes do gate passaram, assim como os casos do título.
  A primeira tentativa local foi impedida por restrições de acesso ao shell
  e a diretórios temporários; a repetição autorizada fora dessa restrição passou.
- O YAML foi carregado com PyYAML. Uma avaliação local das regras conferiu
  nove cenários: MR, push com e sem MR, develop, main, execução manual,
  agendada, acionada e tag. O MR selecionou os cinco jobs, o push com MR
  não gerou pipeline e os demais cenários selecionaram os quatro jobs de
  qualidade. A ordem dos estágios e `-m integration --strict-markers`
  foram preservadas. Essa avaliação local não substitui a execução no runner.
- `git diff --check` passou.
- O editor de pipelines do GitLab confirmou a sintaxe da configuração
  corrigida. A simulação de push na branch do MR foi bloqueada pelo workflow,
  conforme esperado. Na simulação com `main`, o GitLab voltou a informar
  o limite de jobs ativos do projeto; portanto, não foi possível obter uma
  simulação completa aprovada no servidor.

As suítes de aplicação não foram repetidas nesta correção: seus comandos e
arquivos não mudaram. A confirmação da pipeline completa no novo commit
depende de publicar a correção e de haver capacidade disponível no GitLab.
Não foram canceladas pipelines de outras entregas nem alterado o limite do projeto.

## Adaptação ao limite sem acesso administrativo — 06/10/2026

A pipeline de MR do commit `1a521a2` foi criada como
[#88794](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/pipelines/88794),
sem pipeline duplicada de branch, mas o GitLab recusou seus cinco jobs pelo
mesmo limite de atividade. Na consulta posterior, os filtros `created`,
`pending` e `running` não mostraram pipelines do projeto. O valor administrativo
do limite não está acessível; não foi presumido nem alterado.

A validação do título foi incorporada ao job `conflict-markers`, após o gate.
Os testes do validador são executados nesse job e o título real é conferido
somente em eventos de MR. Assim, a pipeline completa usa **quatro jobs**, como
as execuções anteriores, mantendo as três suítes de aplicação, suas imagens,
artefatos e comandos. Um conflito ou título inválido interrompe a pipeline
no estágio `validate`, antes de iniciar as suítes de aplicação.

Verificações locais: sete testes do gate aprovados; testes do título aprovados;
bloco condicional executado com push e execução manual sem título, MR com
título válido e MR com título inválido. Os três primeiros foram aceitos e
o último foi rejeitado. A estrutura YAML confirmou quatro jobs executáveis,
ordem dos estágios preservada e seleção `integration` mantida.
O resultado remoto desta adaptação deve ser verificado na pipeline do novo commit.
