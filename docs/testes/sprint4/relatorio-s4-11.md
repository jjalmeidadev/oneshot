# Relatório S4-11 (#200) — Validação de persistência, auditoria e acesso por perfil sintético

**Sprint 4 · Grupo 05 · Frente de testes sistêmicos**
Responsável pela execução: Felipe

---

## 1. Escopo e critério

A task valida três coisas distintas, e é importante não misturá-las no veredito:

1. **Persistência** — o que o backend grava no Supabase sobrevive, na forma certa, sem sobrescrita.
2. **Auditoria e correlação** — dá para reconstruir o caminho de uma pergunta do início ao fim, cruzando `ai_conversations → ai_interactions → consulted_sources → audit_events`.
3. **Acesso por perfil sintético** — usuários de perfis diferentes enxergam recortes diferentes, e o sistema nega o que está fora do perfil.

Os eixos 1 e 2 são executáveis hoje. O eixo 3 está bloqueado pelo defeito **D-01** (seção 5).

**Status possíveis em qualquer caso:** Aprovado / Falhou / Bloqueado / Não executado.
Bloqueado é resultado válido pelo DoD, desde que com motivo e número da issue.

**Instrumento:** `src/database/sql/consultas_validacao_s4-11.sql` — script de leitura, um bloco por caso, autocontido. Não é migração e não recebe numeração `01`–`14` de propósito.

---

## 2. Cabeçalho de congelamento — Rodada 1

| Campo | Valor |
|---|---|
| Rodada | 1 |
| Data de execução | 22/09/2026 |
| Branch | `feature/S4-11-validacao-persistencia` (a partir de `origin/develop`) |
| Commit congelado | `15765c9` |
| Ambiente | Backend local (`src/backend`, venv Python 3.13.9) apontando para o Supabase do projeto |
| Banco | Supabase — schema `public` |
| Janela da massa | a partir de `2026-09-22 00:00:00-03` (literal a trocar no `.sql`) |
| Massa | Leitura do `P-00`: 2.028 interações na janela (totais 2.096 / 2.082 conversas / 8.635 eventos / 5.100 fontes). Leitura do `R-01`, mais tarde na mesma rodada: **2.658 interações**. O banco recebeu tráfego entre os dois blocos — ver nota abaixo. `out_of_scope_requests` = 0, `users` = 0, `access_rules` = 0 em ambas. |
| Executor | Felipe |

> A rodada 2 **acrescenta** uma seção 13 com seu próprio cabeçalho de congelamento. Não reescreve esta.

> **Nota de congelamento.** A massa cresceu de 2.028 para 2.658 interações entre o `P-00` e o `R-01`, na mesma rodada. O ambiente é compartilhado e continuou recebendo tráfego durante a execução. Os números desta rodada são, portanto, um retrato de um alvo em movimento. Isso não invalida nenhum veredito — todos os casos são invariantes (contagens que devem ser zero), e um invariante violado por 6 ou por 8 linhas segue violado. Mas significa que **as contagens absolutas não são reproduzíveis** e que a rodada 2 vai medir outros valores. Para a rodada 2, congelar o ambiente ou registrar `NOW()` no início e no fim.

### 2.1 Leitura da massa (P-00)

O inventário devolveu um cenário diferente do previsto no briefing, e ele reorganiza a rodada.

**Não é preciso gerar tráfego.** A hipótese de trabalho era um banco vazio, a ser preenchido com ~5 consultas manuais. O real é 2.028 interações na janela. Isso é melhor: valida-se persistência sobre volume, não sobre anedota.

**A massa foi escrita pelo backend, não por seed.** Verificado por varredura das 16 migrações em `src/database/sql/`: nenhuma delas tem `INSERT` em `ai_conversations`, `ai_interactions`, `consulted_sources`, `audit_events` ou `out_of_scope_requests`. A distinção é decisiva para esta task — linha inserida por script SQL não prova nada sobre o caminho de escrita do backend, e validaria o seed, não o sistema. Como nenhuma migração as popula, toda a massa veio pela aplicação.

**A janela perdeu a função de isolamento.** Ela existia para separar "o que eu gerei nesta rodada" do histórico. Com 2.022 conversas criadas hoje, ela não separa nada. Consequência prática: os casos que dependem de pré-condição disparada por mim (CV-04, CV-07, CV-08) não podem usar a janela do dia. Duas saídas:

- **Preferida — validar sobre a massa existente.** CV-04 e CV-08 não precisam de pergunta minha: com 2.028 interações, repetições e casos fora de escopo ou já existem na massa, ou a ausência deles é o achado. Só o CV-07 (erro provocado) exige disparo manual.
- **Alternativa — janela estreita.** Registrar `NOW()` antes de disparar e usar esse instante como corte, mantendo a massa histórica como contexto.

**Proporções da massa** (leitura preliminar, a confirmar nos casos):

| Razão | Valor | Leitura |
|---|---|---|
| `audit_events` / `ai_interactions` | ≈ 4,1 | Auditoria emitindo vários eventos por interação — compatível com o esperado |
| `consulted_sources` / `ai_interactions` | ≈ 2,4 | Interações citando fonte em média — compatível |
| `ai_interactions` / `ai_conversations` | ≈ 1,007 | **Praticamente uma interação por conversa.** Tráfego de teste ou API, não diálogo multi-turno |
| `out_of_scope_requests` | **0** | **Candidato a defeito** — ver abaixo |

**Achado provável D-02 (a confirmar no CV-08).** Zero linhas em `out_of_scope_requests` sobre 2.096 interações. Duas explicações, e é preciso separá-las antes de dar veredito: ou nenhuma das 2.096 perguntas foi classificada como fora de escopo — improvável, já que `intent_catalog` tem `FORA_DE_ESCOPO` e `intent_test_cases` carrega casos com esse rótulo esperado — ou o caminho de fora de escopo classifica corretamente mas **não persiste** em `out_of_scope_requests`. A segunda hipótese é um defeito de persistência, que é exatamente o objeto desta task.

O bloco `P-02` abaixo decide entre as duas.

### 2.2 Pré-condições da rodada

- [x] Inventário `P-00` executado e registrado na linha **Massa**.
- [ ] Rodar `P-01` (caracterização da massa por canal, rota e status) e anexar como `evidencias/r1-p-01.csv`.
- [ ] Rodar `P-02` (fora de escopo: classificadas × registradas) — decide o veredito do CV-08 e a existência do D-02.
- [ ] Provocar **uma falha controlada** — chave do provedor de geração inválida — e disparar uma consulta, anotando o horário (pré-condição do CV-07, único caso que ainda exige disparo manual).
- [ ] Salvar cada saída em `docs/testes/sprint4/evidencias/` como `r1-cv-XX.<ext>`.

### 2.3 Confirmado pelo P-00 — D-01

`users` = 0 e `access_rules` = 0, como previsto na seção 5. CV-09 a CV-12 seguem **Bloqueados**, agora com evidência numérica da própria rodada, não só por leitura de código.


---

## 3. Matriz de casos

| Caso | Tipo | Eixo | O que prova | Status R1 |
|---|---|---|---|---|
| CV-01 | positivo | Persistência | Cada consulta disparada virou uma linha em `ai_interactions`, com `user_prompt` íntegro | **Aprovado** |
| CV-02 | positivo | Persistência | Nenhuma interação órfã e nenhuma conversa sem interação | **Aprovado** |
| CV-03 | positivo | Persistência | Campos classificatórios dentro do domínio; nada marcado `processado` sem intenção ou sem resposta | **Aprovado** |
| CV-04 | positivo | Persistência | Reexecutar a mesma pergunta cria registro novo, não sobrescreve o anterior | **Aprovado** |
| CV-05 | positivo | Correlação | A cadeia conversa → interação → fontes → auditoria fecha para toda interação | **Falhou — D-04** |
| CV-06 | positivo | Auditoria | Todo evento tem `correlation_id`, e uma interação não mistura dois | **Falhou — D-03** |
| CV-07 | **negativo** | Auditoria | Erro de processamento é persistido e auditado como `falha`, não engolido | **Aprovado** |
| CV-08 | **negativo** | Auditoria | Pergunta fora de escopo vira `out_of_scope_requests` + `limitation_response`, sem citar fonte | **Falhou — D-02** |
| CV-09 | positivo | Acesso | Perfis sintéticos cadastrados em `users`, com `entra_object_id` | **Bloqueado — D-01 · Sprint 5** |
| CV-10 | positivo | Acesso | `access_rules` cobrindo regra por `user_id` e por `role_name` | **Bloqueado — D-01 · Sprint 5** |
| CV-11 | **negativo** | Acesso | Líder do subportfólio A não obtém dado do subportfólio B | **Bloqueado — D-01 · Sprint 5** |
| CV-12 | positivo | Acesso | `ai_interactions.user_id` e `audit_events.user_id` preenchidos | **Bloqueado — D-01 · Sprint 5** |

---

## 4. Execução — Rodada 1

Instrumento: bloco `R-01` do `consultas_validacao_s4-11.sql` (painel dos oito casos em uma consulta), mais `P-02` e `P-03` para o detalhamento do fora de escopo.

**Resultado consolidado: 5 aprovados, 3 falhas, 4 bloqueados.**

### CV-01 — Persistência da interação textual _(positivo)_ · **Aprovado**

- **Medida:** 2.658 interações na janela; 0 sem `user_prompt`; 0 sem `processing_ms`.
- **Leitura:** nenhuma escrita chegou mutilada. O texto do usuário e o tempo de processamento estão íntegros em toda a massa.
- **Evidência:** `evidencias/r1-r-01.csv`

### CV-02 — Integridade do vínculo conversa ↔ interação _(positivo)_ · **Aprovado**

- **Medida:** 0 interações órfãs; 0 conversas sem interação.
- **Leitura:** não há conversa aberta cuja interação tenha se perdido. O par nasce junto, o que é o comportamento esperado de `trace_interaction`, que escreve os dois na mesma transação.
- **Evidência:** `evidencias/r1-r-01.csv`

### CV-03 — Domínio dos campos classificatórios _(positivo)_ · **Aprovado**

- **Medida:** 0 processadas sem intenção macro; 0 processadas sem `response_text`.
- **Leitura:** este era o caso que caçava o que as `CHECK` constraints não cobrem — interação marcada como concluída sem classificação ou sem resposta. Não existe nenhuma. O estado `processado` significa de fato processado.
- **Evidência:** `evidencias/r1-r-01.csv`

### CV-04 — Reexecução preserva histórico _(positivo)_ · **Aprovado**

- **Medida:** 47 prompts repetidos na massa; 0 com `updated_at` posterior à escrita.
- **Leitura:** a persistência é append-only. Reexecutar a mesma pergunta cria registro novo e não toca o anterior. **Este é o caso que fecha o quarto item do DoD** ("reexecução, erro ou acesso negado aplicável foi testado e documentado") — e, com o CV-07, fecha por dois caminhos, não um.
- **Evidência:** `evidencias/r1-r-01.csv`

### CV-05 — Cadeia de correlação completa _(positivo)_ · **Falhou**

- **Medida:** 0 interações sem evento de auditoria; **6 respostas de rota documental sem nenhuma fonte citada**.
- **Leitura:** a primeira metade passa com folga — toda interação é auditada. A segunda falha: 6 respostas de rota `sharepoint_query` ou `analise_local`, marcadas como `processado`, não citaram fonte alguma. Em proporção é pouco (6 em 2.658, ~0,2%), mas a natureza do caso não admite proporção: uma resposta de rota documental sem lastro é uma resposta que o usuário lê como fundamentada e não é.
- **Encaminhamento:** defeito **D-04**, seção 6.6. Exige inspeção das 6 linhas antes de dimensionar.
- **Evidência:** `evidencias/r1-r-01.csv`

### CV-06 — Auditoria com `correlation_id` consistente _(positivo)_ · **Falhou**

- **Medida:** **10.631 eventos sem `correlation_id`**; 0 interações misturando dois identificadores.
- **Leitura:** a segunda metade passa por vacuidade — não há como misturar dois identificadores quando não existe nenhum. O campo `correlation_id` está nulo em toda a massa.
- **Encaminhamento:** defeito **D-03**, seção 6.5. É o achado de maior alcance da rodada, porque atinge diretamente o primeiro item do DoD e a task "registrar identificadores de correlação".
- **Evidência:** `evidencias/r1-r-01.csv`

### CV-07 — Erro de processamento persistido e auditado _(negativo)_ · **Aprovado**

- **Medida:** 52 interações com `processing_status = 'erro'`; **52 auditadas com `event_status = 'falha'`**. Cobertura de 100%.
- **Leitura:** o caso não precisou de falha provocada — a massa já continha 52 erros reais. E o sistema se comporta bem no pior momento: quando falha, ele grava que falhou. Nenhum erro foi engolido. É o resultado mais tranquilizador da rodada, porque erro silencioso é o modo de falha que mais custa caro em auditoria.
- **Nota de planejamento:** este caso estava previsto como "adiado para a Sprint 5 se a massa não tivesse erros". Está aprovado nesta rodada e **sai da lista de reprogramados**.
- **Evidência:** `evidencias/r1-r-01.csv`

### CV-08 — Fora de escopo registrado com resposta de limitação _(negativo)_ · **Falhou**

- **Medida:** **190 classificadas como fora de escopo; 0 registradas** em `out_of_scope_requests`.
- **Leitura:** o número subiu de 136 (leitura do `P-02`) para 190 (leitura do `R-01`) junto com a massa, e a coluna da direita seguiu em zero. A tabela nunca é escrita.
- **Encaminhamento:** defeito **D-02**, seção 6.1 a 6.4, com causa raiz identificada no código.
- **Evidência:** `evidencias/r1-p-02.csv`, `evidencias/r1-r-01.csv`

### CV-09 a CV-12 — Acesso por perfil sintético · **Bloqueados**

**Status: Bloqueado — D-01. Reprogramado para a Sprint 5.** Motivo e enquadramento na seção 5. Os quatro casos permanecem escritos, com critério de aprovação definido e consulta pronta no `.sql`: quando a carga de identidade e o controle de acesso entrarem, a execução é rodar os mesmos blocos, sem reescrever caso nenhum. As consultas correspondentes foram executadas e a saída anexada como **evidência do bloqueio**, não como tentativa de aprovação.

| Caso | Saída observada | Evidência |
|---|---|---|
| CV-09 | `users` vazia — 0 registros | `evidencias/r1-p-00.csv` |
| CV-10 | `access_rules` vazia — 0 registros | `evidencias/r1-p-00.csv` |
| CV-11 | Nenhum `audit_event` com `event_status = 'bloqueado'` por perfil | `evidencias/r1-cv-11.csv` |
| CV-12 | `user_id` nulo nas interações da rota textual | `evidencias/r1-cv-12.csv` |

---

## 5. Defeito D-01 — controle de acesso por perfil não existe

**Enunciado:** o controle de acesso por perfil não existe, nem em dados nem em código.

### 5.1 Evidência

1. `users` e `access_rules` estão vazias, e a carga da #199 não as popula:
   `grep -rn -i -E "insert into\s+(public\.)?(users|access_rules)" src/database/sql/` → sem resultado.
   Confirmado por leitura direta de `02_initial_data.sql`: os `INSERT` cobrem `subportfolios`, `projects`, `project_artifacts`, `project_charters`, `project_benefits`, `project_deliverables_milestones`, `project_progress_updates`, `risk_issue_items`, `intent_catalog` e `secondary_intents` — nenhum toca `users` ou `access_rules`.
2. O backend não consulta `access_rules` em lugar nenhum. Única ocorrência no código: comentário em `src/backend/app/audio/security.py:13`.
3. `grep -rn "OUT_OF_SCOPE_FOR_PROFILE" src/backend/app --include=*.py` → só o comentário acima. O erro nunca é emitido.
4. A rota textual ainda não exige identidade. Na rota de áudio a identidade vem de `AUDIO_SIMULATED_IDENTITIES` (`<token>=<entra_object_id>`), compatível com `users.entra_object_id` — ou seja, o schema está pronto, a implementação não.

O schema **suporta** o controle: `users.role_name` tem `CHECK` com os seis perfis, e `access_rules` aceita regra por `user_id` **ou** por `role_name` (`access_rules_subject_ck`), com `permission_scope` ∈ `portfolio | subportfolio | projeto | artefato | auditoria`. O que falta é dado e código, não modelagem.

### 5.2 Enquadramento

Materialização do risco **R04** (`docs/Projeto.md`, seções 3.6 e 6.2.4) — Técnico, probabilidade 3 × impacto 5 = 15, severidade **Crítica**, responsável Wendel Feitosa, "Em Monitoramento".

### 5.3 Impacto nos requisitos não funcionais

| RNF | Situação | Causa |
|---|---|---|
| RNF02 (Muito Alta) | **Reprovado** | Nenhuma negativa de acesso é emitida |
| RNF03 | **Reprovado parcialmente** | Só pelo campo de usuário: `ai_interactions.user_id` e `audit_events.user_id` ficam nulos |
| RNF11 | Afetado | Depende do mesmo mecanismo |

### 5.4 Decisão do grupo

Implementação vai para a **Sprint 5**; um integrante assumiu. Registrar em **#240** (matriz de riscos) e **#244/#245** (backlog Sprint 5).

### 5.5 Mitigação barata proposta (não aplicada)

Popular **somente** `public.users` com 4 registros sintéticos — `diretoria`, 2× `lider_subportfolio` em subportfólios distintos, `equipe_projeto` — **sem nenhuma implementação de autorização**.

Isso recupera o **RNF03** a custo zero de código, e mantém o RNF02 corretamente reprovado, que é o estado real do sistema. O `INSERT` correspondente está no apêndice do `.sql`, **comentado de propósito**: task de validação não altera massa. Se o grupo aprovar, vira migração numerada pela mão do dono da área.

---

## 6. Defeito D-02 — fora de escopo classificado mas não persistido

**Enunciado:** o backend roteia corretamente perguntas fora de escopo, mas não grava nada em `public.out_of_scope_requests`. A tabela está vazia desde sempre.

### 6.1 Evidência (bloco `P-02`, rodada 1)

| Medida | Valor |
|---|---|
| Interações com `route_taken = 'fora_escopo'` | 136 |
| Interações com `processing_status = 'fora_escopo'` | 134 |
| Interações com `macro_intent_predicted = 'FORA_DE_ESCOPO'` | 134 |
| **Classificadas como fora de escopo (união)** | **136** |
| **Registradas em `out_of_scope_requests`** | **0** |

**Causa raiz, no código.** `src/backend/app/database/tracing.py` é o único caminho de escrita da rastreabilidade. Ele grava em exatamente quatro tabelas — `ai_conversations`, `ai_interactions`, `consulted_sources` e `audit_events` — e **não existe nenhum `INSERT INTO public.out_of_scope_requests` em lugar nenhum do backend**. O módulo calcula `_route_taken()` devolvendo `'fora_escopo'` e `_limitation_response()`, escreve os dois na interação, e para aí.

Ou seja: não é bug de runtime nem falha intermitente. A escrita nunca foi implementada. Isso simplifica a correção e a estimativa — é função nova no `tracing.py`, não caça a regressão.

**Efeito colateral favorável na severidade.** Como `_limitation_response()` existe e é gravada em `ai_interactions.limitation_response`, é provável que o usuário tenha recebido a resposta de limitação corretamente, e que o perdido seja só a trilha de curadoria. O `P-03` confirma empiricamente antes de fixar a severidade.

A união igual a 136 — o mesmo valor de `route_taken` — prova que a rota é o superconjunto: toda interação marcada por status ou intenção também foi roteada, e **2 interações foram roteadas sem que status e intenção acompanhassem**. Achado menor, registrado como A-03.

### 6.2 Por que isso não é detalhe de auditoria

`out_of_scope_requests` não é log. O schema lhe dá `review_status` ∈ `pendente | revisado | incorporar_catalogo | descartado`, com `reviewed_by` e `reviewed_at`: a tabela existe para alimentar a **evolução do catálogo de intenções**. Cada linha é um pedido real que o sistema não soube atender, esperando triagem humana para virar intenção nova.

Com a escrita ausente, 136 sinais de demanda não coberta foram descartados. O ciclo de melhoria do `intent_catalog` fica sem entrada — e ele é o mecanismo pelo qual o produto deixa de ser estático.

### 6.3 Severidade — pendente de uma medida

A severidade depende de um dado que a rodada 1 ainda não separou: se as 136 interações responderam ao usuário com `limitation_response`.

- **Se responderam** — o usuário foi corretamente informado da limitação, e o que se perdeu foi a trilha de curadoria. Severidade **Média**: defeito de persistência, sem impacto ao usuário final.
- **Se não responderam** — o usuário recebeu vazio ou, pior, resposta inventada. Severidade **Alta**, e o defeito deixa de ser só de persistência.

O bloco `P-03` do `.sql` mede exatamente isso. Preencher antes de abrir a issue, porque a severidade muda o destinatário e a prioridade.

> Nota metodológica: o `P-02` original contou `limitation_response` sobre a janela inteira (186 de 2.028), não sobre o subconjunto de fora de escopo. O número não responde à pergunta acima e não deve ser usado para isso. O `P-03` corrige o recorte.

### 6.4 Encaminhamento

Issue para o dono do caminho de PLN/roteamento. Não corrigir dentro desta task — a #200 valida, não implementa.

---

## 7. Defeito D-03 — identificador de correlação nunca é gravado

**Enunciado:** `audit_events.correlation_id` está nulo em 100% da massa. 10.631 eventos, nenhum identificador.

### 7.1 Causa raiz

`_insert_audit_events()`, em `src/backend/app/database/tracing.py`, monta o `INSERT` com seis colunas: `interaction_id`, `event_type`, `component`, `event_status`, `user_id`, `event_payload`. **`correlation_id` não está na lista.** A coluna existe no schema, é nullable, e nunca recebe valor.

Não é perda ocasional nem truncamento: é campo que o caminho de escrita ignora.

### 7.2 Por que é o achado de maior alcance da rodada

Três coisas dependem dele, e é preciso separá-las, porque duas sobrevivem e uma não.

**A correlação em si sobrevive.** A cadeia `conversa → interação → fontes → eventos` continua reconstruível pelas chaves estrangeiras — o CV-05 provou que 0 interações ficam sem evento. Então o primeiro item do DoD ("conversa, interação, fontes e eventos ficam correlacionados") está atendido **estruturalmente**.

**A task de registrar identificadores não sobrevive.** A issue #200 pede, nominalmente, "registrar consultas, contagens e **identificadores de correlação**". Não há identificador para registrar. O bloco `R-02` foi escrito para extraí-los e vai voltar vazio.

**A convenção de evidência do grupo não sobrevive.** A S4-08 e a S4-09 documentam que `scripts/verify-supabase.ps1` "registra a correlação em `audit_events`" e salva o identificador junto da evidência. Essa convenção não funciona para o caminho da aplicação — só para o script de verificação, que grava seu próprio evento. Ou seja: o grupo acredita ter um mecanismo de correlação que, na prática, existe só na ferramenta de verificação, não no produto.

### 7.3 Correção e severidade

Correção barata: acrescentar a coluna ao `INSERT` e propagar um identificador gerado no início de `trace_interaction()` — o mesmo valor para todos os eventos da interação. Uma linha de geração, uma coluna no `INSERT`, um parâmetro.

Severidade **Média**: não há perda de dado nem de rastreabilidade estrutural, mas a auditoria fica sem o identificador que a própria documentação do grupo diz usar. Para RNF03 é um atenuante relevante, não um bloqueio.

### 7.4 Encaminhamento

Issue para o dono do caminho de rastreabilidade, junto com o D-02 — os dois são no mesmo arquivo e podem sair no mesmo MR.

---

## 8. Defeitos D-04 e D-05

### 8.1 D-04 — resposta documental sem fonte citada

**Medida:** 6 interações com `route_taken` em (`sharepoint_query`, `analise_local`), `processing_status = 'processado'`, e nenhuma linha em `consulted_sources`.

São 0,2% da massa, e a proporção não atenua: a rota documental promete resposta lastreada em documento. Sem fonte, o usuário recebe algo que parece fundamentado e não é — o mesmo risco que o CV-08 cobre pelo lado do fora de escopo.

**Pendente de inspeção.** Seis linhas é pouco para diagnosticar por contagem. Duas hipóteses plausíveis, com encaminhamentos opostos: a recuperação não achou nada e o sistema respondeu assim mesmo (defeito de comportamento — deveria degradar para limitação), ou achou e a escrita das fontes falhou (defeito de persistência). A consulta de inspeção está no bloco CV-05 do `.sql`, que lista as linhas uma a uma.

**Severidade:** a definir após a inspeção. Registrar como aberto.

### 8.2 D-05 — componente fora do domínio derruba a auditoria do fluxo guiado

**Achado de código, ainda não observado em execução.** Registrado aqui porque a análise é conclusiva e o impacto, se confirmado, é alto.

Em `_insert_audit_events()`, o evento do fluxo guiado é emitido com `component = "guided_workflow"`:

```python
events.append((
    "guided_workflow_dispatched",
    "guided_workflow",   # <-- fora do dominio
    "pendente",
    {...},
))
```

O schema não aceita esse valor. `audit_events_component_ck` permite exatamente `api | pln | copilot_studio | power_automate | m365_copilot | sharepoint | database`. O `INSERT` viola a constraint e levanta exceção.

**O agravante está na transação.** `trace_interaction()` executa conversa, interação, fontes e eventos dentro de um único `cursor`, e o `except` chama `_rollback(connection)`. Uma violação na escrita dos eventos **descarta a interação inteira** — conversa, interação, fontes e todos os eventos — e propaga `TraceabilityError`. Não é um evento perdido: é o rastro inteiro da interação que desaparece.

**Por que ainda não é conclusivo.** O ramo só executa quando `response.workflow` está preenchida. Não sei dizer, pelos dados, se esse caminho foi exercitado na massa — e se foi, as interações afetadas não estão no banco justamente porque o rollback as apagou, o que torna o defeito invisível por contagem. É o tipo de falha que não aparece no que você mede, só no que falta.

**Como confirmar:** disparar uma requisição que produza `response.workflow` e observar se `trace_interaction` levanta `TraceabilityError`. Alternativamente, comparar o número de respostas de fluxo guiado servidas pela API com o número de interações persistidas no mesmo período.

**Correção:** trocar o componente por um valor do domínio (`api` ou `database`) ou acrescentar `guided_workflow` à constraint — decisão do dono do schema. Independente disso, vale isolar a escrita dos eventos em savepoint, para que um evento inválido não custe a interação inteira.

**Severidade proposta:** Alta, condicionada à confirmação.

---

## 9. Achados colaterais

| # | Achado | Onde | Encaminhamento |
|---|---|---|---|
| A-01 | Numeração duplicada em `src/database/sql/` — dois `05`, dois `06`, dois `07`. A ordem de aplicação fica ambígua e o resultado de um banco recriado do zero depende da ordem alfabética do sistema de arquivos. | `src/database/sql/` | Issue para o dono do banco |
| A-03 | 2 interações roteadas para `fora_escopo` sem que `processing_status` e `macro_intent_predicted` acompanhassem. Ou a rota é decidida por critério diferente da classificação, ou o status não é atualizado na escrita. | `ai_interactions` | Anexar à issue do D-02 |
| A-02 | Nenhum teste automatizado tocava o banco de verdade. A fronteira backend ↔ Supabase tinha cobertura zero — descoberto na classificação da #228. | `src/backend/app/tests/` | **Endereçado nesta task**: `test_persistence_audit_s4_11.py` cobre as invariantes de persistência, correlação e auditoria contra o Supabase real |

---

## 10. Conformidade com DoR e DoD da #200

Texto de referência: issue "Validar persistência, auditoria e acesso por perfil sintético", aberta por Jaime Almeida.

### 10.1 DoR — e a ressalva que precisa ficar registrada

| Item do DoR | Situação |
|---|---|
| S4-09, regras sintéticas e caminho informado como funcional | **Parcialmente atendido** — ver abaixo |
| Scripts, contratos de dados e ambiente sintético disponíveis e versionados | Atendido — 16 migrações versionadas em `src/database/sql/` |
| Credenciais somente no ambiente local, sem exposição | Atendido — nenhuma credencial neste relatório ou no `.sql` |

**A ressalva.** O DoR exige "regras sintéticas". A documentação da própria S4-09 (`src/database/docs/s4-09-idempotent-seed.md`) declara o que a carga idempotente cobre: *subportfólios, projetos, artefatos, extratos, TAP, benefícios, avanços, entregas, riscos e intenções*. **Identidade e regras de acesso não estão na lista** — nem em `02_initial_data.sql`, nem em `04_rag_synthetic_data.sql`.

Ou seja: o D-01 não é um defeito descoberto durante a execução. É uma **pré-condição que nunca existiu**. A S4-09 entregou o que prometeu; ela simplesmente nunca prometeu `users` nem `access_rules`. A #200 foi puxada com o DoR atendido só em parte, e isso explica — sem culpar ninguém — por que o eixo de acesso não tem como ser validado.

Consequência prática: a Sprint 5 precisa de uma task de **carga sintética de identidade e regras de acesso** antes da task de implementação do controle. Duas coisas, não uma.

### 10.2 DoD — o que fecha e o que não fecha

| Item do DoD | Instrumento | Situação |
|---|---|---|
| Conversa, interação, fontes e eventos ficam correlacionados | CV-05, CV-06 | **Atendido com ressalva** — a cadeia fecha pelas chaves estrangeiras (0 interações sem evento), mas `correlation_id` está nulo em 100% dos eventos (D-03) e 6 respostas documentais não citaram fonte (D-04) |
| Perfil permitido acessa seu escopo e perfil negado recebe erro controlado e auditável | CV-09 a CV-12 | **Não atendível** — D-01 |
| Consultas, contagens ou identificadores comprovam o resultado no Supabase | `consultas_validacao_s4-11.sql` + evidências | **Atendido por consultas e contagens.** Identificadores de correlação não existem na base (D-03) |
| Reexecução, erro **ou** acesso negado aplicável foi testado e documentado | CV-04 e CV-07 | **Atendido por dois caminhos** — reexecução (47 prompts repetidos, 0 sobrescritas) e erro (52 erros, 52 auditados). O item pedia um |

E as Tasks da issue:

| Task | Situação |
|---|---|
| Exercitar acesso permitido e negado | Bloqueado — D-01 |
| Correlacionar eventos | CV-05 e CV-06 — cadeia fecha por FK; `correlation_id` ausente (D-03) |
| Executar o cenário de repetição, falha ou acesso negado aplicável | CV-04 (repetição) e CV-07 (falha) — ambos aprovados |
| Registrar consultas, contagens e identificadores de correlação | Consultas e contagens registradas. **Identificadores não existem** — `R-02` retorna vazio por causa do D-03 |

### 10.3 Veredito sobre o fechamento

Três dos quatro itens do DoD fecham nesta sprint, com evidência sobre 2.028 interações reais.

O segundo item — perfil permitido acessa seu escopo, perfil negado recebe erro controlado e auditável — **não fecha**, e não fecha por ausência de implementação, não por lacuna de teste. Os casos estão escritos, o critério está definido e a consulta está pronta; falta o sistema ter o comportamento.

**Decisão registrada:** o item fica formalmente em aberto e sua execução é **reprogramada para a Sprint 5**. O relatório não o marca como atendido.

### 10.4 Reprogramado para a Sprint 5

Esta seção é a entrada direta para o backlog (#244/#245) e para a matriz de riscos (#240).

| O que | Por que ficou | Pré-requisito |
|---|---|---|
| CV-09 — perfis sintéticos em `users` | Tabela vazia; a S4-09 nunca cobriu identidade (seção 8.1) | Task de **carga sintética de identidade e regras de acesso** |
| CV-10 — regras em `access_rules` | Idem | Mesma task de carga |
| CV-11 — negativa de acesso entre subportfólios | O backend nunca emite `OUT_OF_SCOPE_FOR_PROFILE` (D-01) | Task de **implementação do controle de acesso** |
| CV-12 — rastreabilidade por usuário | `user_id` nulo em interações e eventos | Qualquer uma das duas acima já recupera parte |
| Issue do D-02 | Aberta nesta sprint; correção é do dono do caminho de rastreabilidade | — |
| Issue do D-03 | Aberta nesta sprint; mesmo arquivo do D-02, pode sair no mesmo MR | — |
| Inspeção do D-04 | 6 linhas a diagnosticar antes de dimensionar | Consulta do CV-05 no `.sql` |
| Confirmação do D-05 | Achado de código; exige exercitar o fluxo guiado | Backend local com requisição que produza `response.workflow` |

**Duas tasks, não uma.** A carga sintética de identidade e a implementação do controle de acesso são entregas distintas, e nesta ordem. Se a Sprint 5 puxar só a implementação, ela trava na mesma ausência de dado que travou esta rodada.

**Nada precisa ser reescrito.** Os quatro casos bloqueados já têm critério de aprovação e consulta no `consultas_validacao_s4-11.sql`. A rodada da Sprint 5 é executar os mesmos blocos e acrescentar uma seção ao relatório — não refazer a análise.

---

## 11. Conclusão da Rodada 1

**5 aprovados, 3 falhas, 4 bloqueados.**

| Veredito | Casos |
|---|---|
| Aprovado | CV-01, CV-02, CV-03, CV-04, CV-07 |
| Falhou | CV-05 (D-04), CV-06 (D-03), CV-08 (D-02) |
| Bloqueado | CV-09, CV-10, CV-11, CV-12 (D-01, Sprint 5) |

**O que o sistema faz bem.** A escrita é íntegra e append-only: nada chega mutilado, nada é sobrescrito, nenhuma conversa perde sua interação, nenhum estado `processado` é falso. E — o resultado mais tranquilizador da rodada — quando o sistema falha, ele grava que falhou: 52 erros, 52 auditados, cobertura de 100%. Erro silencioso é o modo de falha mais caro em auditoria, e ele não acontece aqui.

**Onde ele falha.** As três falhas têm a mesma natureza e o mesmo endereço: são **escritas que nunca foram implementadas** em `app/database/tracing.py`, não regressões. A tabela `out_of_scope_requests` não recebe `INSERT` nenhum (D-02); a coluna `correlation_id` não está na lista de colunas do `INSERT` de eventos (D-03). Isso é boa notícia para a estimativa — é código novo em um arquivo só, não caça a bug.

**O achado que ninguém esperava.** O D-05 não veio dos dados, veio da leitura do código durante a análise: o evento do fluxo guiado usa um `component` que a constraint do schema não aceita, e como toda a rastreabilidade roda em uma transação, a violação descarta a interação inteira. Se confirmado, é o defeito mais grave da lista — e é invisível por contagem, porque as interações afetadas não estão no banco justamente por terem sido apagadas.

**Sobre a massa.** Nenhum destes vereditos veio de tráfego que eu gerei. Todos vieram de 2.658 interações que o sistema já tinha produzido. Cinco consultas manuais, como o plano original previa, não teriam exposto nem o D-02 nem o D-03.

**Veredito da task.** Três dos quatro itens do DoD fecham, dois deles com ressalva nomeada. O segundo item — acesso por perfil — não fecha e está reprogramado para a Sprint 5, com causa documentada na seção 5 e pré-requisito identificado na 10.1.

## 12. Regras seguidas nesta task

- Uma branch por task, MR pequeno: `feature/S4-11-validacao-persistencia`, a partir de `origin/develop`.
- Relatório por rodada, com cabeçalho de congelamento. A rodada 2 acrescenta a seção 13; não reescreve a 4.
- Defeito encontrado vira issue para o dono da área. **Nenhum código de produção foi alterado nesta task** — inclusive por isso a mitigação do D-01 está comentada.
