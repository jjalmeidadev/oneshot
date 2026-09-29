# Relatório S4-33 (#229) — RNF01, RNF02 e RNF03

Sprint 4 · Grupo 05 · Frente de testes sistêmicos
Execução: Felipe

---

## 1. Planejamento

O objetivo é verificar segurança e rastreabilidade: confidencialidade (RNF01), acesso por perfil (RNF02) e auditoria (RNF03), com caso positivo e negativo para cada um.

Os casos, critérios e instruções seguem a Seção 9.2 do `docs/Projeto.md`, que é a fonte de verdade do projeto. Os identificadores são os de lá: `CT-RNF01-P`, `CT-RNF01-N`, e assim por diante — dois casos por requisito, não quatro.

**Ferramenta.** `pytest`, em `src/backend/app/tests/test_rnf01_rnf03_s4_33.py`. Os casos de RNF01 operam sobre a massa sintética e sobre o prompt montado antes da chamada ao provedor, sem rede nem banco. Os de RNF02 e RNF03 conferem a persistência no Supabase.

**Reaproveitamento.** O RNF03 é o que as tasks anteriores já exercitaram: o caso positivo corresponde ao CT-E2E-02 da #209 e o negativo ao CT-E2E-03. Aqui a verificação é feita sobre toda a massa acumulada, não sobre uma interação isolada.

---

## 2. Ambiente e congelamento

| Campo | Valor |
|---|---|
| Rodada | 1 |
| Data | 24/09/2026 |
| Branch | `feature/S4-33-rnf01-rnf03`, a partir de `origin/develop` |
| Ambiente | Massa sintética local e Supabase do projeto |
| Massa | 9 documentos sintéticos em `app/rag/data/sharepoint`; interações acumuladas em `ai_interactions` |
| Execução | `python -m pytest app/tests/test_rnf01_rnf03_s4_33.py -v` |

---

## 3. Cenários de teste

| ID | Tipo | Propósito | Execução | Resultado esperado |
|---|:---:|---|---|---|
| CT-RNF01-P | Positivo | Confirmar que a massa é integralmente sintética e que o prompt declara a origem | Percorrer os documentos da massa e montar o prompt de uma consulta | Todos os documentos vêm de listas simuladas, no domínio `mock.sharepoint.local`; o prompt declara que o contexto é fictício |
| CT-RNF01-N | Negativo | Confirmar que dado marcado como sensível é bloqueado antes da fronteira externa | Copiar a massa para diretório temporário, injetar um marcador sensível e montar o prompt | O marcador não chega ao prompt enviado ao provedor |
| CT-RNF02-P | Positivo | Confirmar que perfis e regras de acesso existem e delimitam escopo | Consultar `users` e `access_rules` | Ao menos os três perfis sintéticos ativos e regras de acesso cadastradas |
| CT-RNF02-N | Negativo | Confirmar que acesso não autorizado recebe negação controlada e auditável | Procurar registro de negação por perfil na auditoria | Existe evento de negação por perfil registrado |
| CT-RNF03-P | Positivo | Confirmar que a interação registra perfil, horário, intenção, fontes e resposta | Percorrer as interações concluídas e conferir cada campo do critério | Os cinco elementos presentes em 100% dos casos |
| CT-RNF03-N | Negativo | Confirmar que a falha também é registrada | Percorrer as interações com estado de erro e conferir a auditoria | Toda interação com erro tem evento de auditoria de falha |

---

## 4. Resultados

**2 aprovados, 2 reprovados, 2 bloqueados.**

| ID | Resultado obtido | Evidência | Status |
|---|---|---|:---:|
| CT-RNF01-P | 9 documentos, todos de listas simuladas (`base-atendimento`, `comunicados-servico`, `procedimentos-operacionais`) e no domínio `mock.sharepoint.local`. O prompt carrega a declaração "dados ficticios para o MVP" | Saída do `pytest` | **Aprovado** |
| CT-RNF01-N | O marcador sensível injetado atravessou a montagem do prompt e seria enviado ao provedor. Não há validação de conteúdo sensível em nenhum ponto do caminho textual | Saída do `pytest`, registrado como `xfail` | **Falhou** — D-06 |
| CT-RNF02-P | `users` e `access_rules` vazias | Saída do `pytest`, registrado como `xfail` | **Bloqueado** — D-01 |
| CT-RNF02-N | Nenhum registro de negação por perfil na auditoria | Saída do `pytest`, registrado como `xfail` | **Bloqueado** — D-01 |
| CT-RNF03-P | Horário, intenção e resposta presentes em 100% das interações concluídas. Dois dos cinco elementos do critério falham: **perfil** nulo em todas (D-01) e **fontes** ausentes em 16 respostas de rota documental (D-04) | Saída do `pytest` | **Falhou** parcialmente |
| CT-RNF03-N | Toda interação com estado de erro tem evento de auditoria de falha correspondente | Saída do `pytest` | **Aprovado** |

Resultado da suíte: `4 passed, 5 xfailed`. Os `xfail` correspondem aos defeitos conhecidos, marcados com `strict=True` para que a suíte acuse caso algum deles seja corrigido e o marcador fique para trás.

---

## 5. Achados

### D-06 — não existe validação de confidencialidade no caminho textual

`build_rag_input`, em `app/rag/sharepoint.py`, copia `document.content` para o prompt sem inspecionar o conteúdo. Nenhum módulo do backend classifica, marca ou bloqueia dado sensível: a varredura por termos de confidencialidade, anonimização ou redação não encontra nada no caminho textual.

O caso negativo comprova: um marcador inequivocamente sensível, injetado numa cópia da massa, chega inteiro ao prompt que seria enviado ao provedor externo.

**O que isso significa para o RNF01.** O requisito é atendido hoje **por convenção, não por controle** — a massa é sintética porque ninguém colocou dado real nela. Não existe barreira técnica. No momento em que o sistema apontar para dados reais de portfólio do parceiro, nada impede que conteúdo sensível saia para o provedor.

O caso positivo passa e o negativo reprova, e essa combinação é exatamente o diagnóstico: o estado atual é seguro por acidente do ambiente de demonstração, não por desenho.

**Correção sugerida:** validação antes da montagem do prompt, com lista de marcadores de confidencialidade e contagem de chamadas externas bloqueadas, conforme a evidência mínima que a Seção 9.2.2 já prevê para o RNF01.

### D-01 e D-04 — já registrados

| Defeito | Onde foi registrado | Efeito aqui |
|---|---|---|
| D-01 — controle de acesso por perfil não existe | Seção 5 do relatório S4-11 | Bloqueia CT-RNF02-P e CT-RNF02-N, e derruba o elemento "perfil" do critério do RNF03 |
| D-04 — resposta documental sem fonte registrada | Seção 8.1 do relatório S4-11 | Derruba o elemento "fontes" do critério do RNF03. Eram 6 ocorrências na rodada da #200; são 16 agora, com a massa maior |

### Correção de método na rodada

A primeira versão do CT-RNF02-N contava eventos de auditoria com `event_status = 'bloqueado'` como sinal de negação por perfil. O critério estava errado: `_insert_audit_events` marca o evento de PLN como `bloqueado` sempre que o estado é `sem_confianca` ou `fora_escopo`, que são recusas de classificação, não de autorização. O teste passou inesperadamente e o `strict=True` acusou.

O caso foi corrigido para procurar o sinal correto — o erro `OUT_OF_SCOPE_FOR_PROFILE`, que o backend nunca emite. Registrado aqui porque o critério mal escolhido teria produzido um falso aprovado no RNF02, que é justamente o requisito mais sensível dos três.

---

## 6. Instruções de execução

```bash
cd src/backend
source .venv/Scripts/activate
python -m pytest app/tests/test_rnf01_rnf03_s4_33.py -v
```

Os casos de RNF01 não exigem configuração. Os de RNF02 e RNF03 precisam de `SUPABASE_DATABASE_URL` (ou `DATABASE_URL`) no `.env` do backend; sem ela, se ignoram sozinhos em vez de reprovar.

Duas observações de ambiente:

A venv precisa estar atualizada com o `requirements.txt` da `develop`. O `psycopg-pool` entrou junto com o pool de conexões em `app/database/connection.py`, e uma venv montada antes disso faz os casos de banco pularem com mensagem de dependência ausente.

O `conftest.py` da suíte zera as variáveis de ambiente do produto antes de cada teste, de propósito, para que o resultado não dependa da máquina. Os casos de banco deste arquivo leem o `.env` na importação do módulo, antes dessa fixture — funciona, mas é uma exceção à convenção da suíte. Vale trocar por uma variável explícita de opt-in numa próxima rodada, para que ninguém rode contra o Supabase sem querer.

---

## 7. Conformidade com DoR e DoD

### 7.1 DoR

| Item | Situação |
|---|---|
| Massa, perfis e persistência disponíveis | **Parcialmente atendido** — massa e persistência sim; **perfis não existem** (D-01). É a mesma lacuna que a #200 registrou: a carga sintética da S4-09 nunca cobriu identidade |
| Versão, massa, ambiente e critérios congelados antes da execução | Atendido — seção 2, e os critérios vêm da Seção 9.2 do `Projeto.md` |
| Ferramenta de coleta e local das evidências preparados | Atendido |

### 7.2 DoD

| Item | Situação |
|---|---|
| Confidencialidade, acesso e auditoria têm casos positivos e negativos executados, com instruções, resultados e evidências | Atendido para RNF01 e RNF03; RNF02 executado com resultado bloqueado e motivo registrado |
| Resultados distinguem aprovado, falhou, bloqueado e não executado | Atendido — seção 4 |
| Comandos, métricas, evidências e defeitos permitem auditar a conclusão | Atendido — comando na seção 6, defeitos na seção 5 |

---

## 8. Conclusão

**2 aprovados, 2 reprovados, 2 bloqueados.**

**RNF01 reprova.** A massa é integralmente sintética e o prompt declara sua origem, mas não existe nenhum mecanismo que impeça dado sensível de sair. O requisito está sendo cumprido pelo conteúdo do ambiente de demonstração, não por controle do sistema — e é isso que o caso negativo revelou.

**RNF02 fica bloqueado**, pelo mesmo motivo já documentado na #200: não há perfis no banco nem verificação de autorização no código. Está reprogramado para a Sprint 5, e depende de duas entregas nesta ordem: carga sintética de identidade e implementação do controle de acesso.

**RNF03 reprova por dois dos cinco elementos do critério.** Horário, intenção e resposta são registrados em 100% das interações, e a falha também é auditada corretamente. Faltam o perfil, que depende do D-01, e as fontes, que dependem do D-04.

Nenhuma das três reprovações é lacuna de teste: as três apontam para funcionalidade que não existe. As correções estão identificadas, com dono de área definido, e duas delas já estavam no backlog da Sprint 5 antes desta rodada.

---

## 9. Rodada 2 — S5-30 (#284), diagnóstico antes da integração das dependências

**Congelamento da rodada.** Em 29/09/2026, às 14:56:04 UTC, a branch `test/reexecutar-rnf01-rnf03` estava no commit `10333c4` (mesmo commit de `develop`). A massa local tinha 9 documentos sintéticos; o banco compartilhado continha 2.801 interações. As contagens abaixo são um retrato desse instante e podem mudar com o tráfego do ambiente.

**Condição de entrada.** S5-04, S5-26 e S5-27 não estavam integradas ao código desta branch; S5-25 estava em branch separada. O banco não tinha perfis nem regras de acesso ativos. Esta rodada mede o estado efetivo, mas ainda não constitui a reexecução *após as correções* exigida pela S5-30.

**Execução.** De `src/backend`, com o `.env` local e acesso somente de leitura ao banco:

```powershell
.venv/Scripts/python.exe -m pytest --noconftest app/tests/test_rnf01_rnf03_s4_33.py -q -rx
```

O `--noconftest` evita que a fixture geral apague as variáveis de banco. Nenhuma credencial, pergunta ou resposta do banco foi impressa. Resultado bruto: **3 passed, 5 xfailed, 1 failed**; os nove testes implementam os seis casos, pois RNF01-P e RNF03-P têm mais de uma verificação cada.

| Caso | Resultado da rodada 2 | Evidência | Estado |
|---|---|---|---|
| CT-RNF01-P | Os dois testes da massa e do prompt aprovaram | `pytest`: 2 passed; 9 documentos sintéticos | **Aprovado** |
| CT-RNF01-N | O marcador sensível ainda chega ao prompt; D-06 permanece | `pytest`: xfailed estrito | **Reprovado** |
| CT-RNF02-P | 0 perfis exigidos e 0 regras de acesso ativos | `pytest`: xfailed estrito; consultas agregadas ao banco | **Bloqueado** |
| CT-RNF02-N | 0 eventos de negativa por perfil | `pytest`: xfailed estrito; consulta agregada ao banco | **Bloqueado** |
| CT-RNF03-P | 2 interações processadas sem intenção macro no teste original; 21 respostas documentais sem fonte; 2.801 interações sem `user_id` | `pytest`: 1 failed e 2 xfailed; consultas agregadas ao banco | **Reprovado** |
| CT-RNF03-N | As 89 interações com erro têm evento de auditoria de falha | `pytest`: 1 passed; 89/89 em consulta agregada | **Aprovado** |

**Marcadores.** Nenhum dos cinco xfails foi removido: todos continuam representando falhas ou dependências ausentes nesta branch. O teste de horário/intenção/resposta também reprova sobre dois registros sem intenção macro. A correção do contrato de classificador opcional feita na S5-25 está em outra branch e ainda não integra este checkout.

**Próxima execução necessária.** Integrar as quatro dependências, carregar os perfis, conferir o bloqueio antes do provedor e executar novamente os seis casos sobre novas interações controladas. A rodada 1 nas seções 1–8 foi preservada integralmente.
