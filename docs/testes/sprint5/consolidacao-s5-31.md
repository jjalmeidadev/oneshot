# S5-31 (#285) — consolidação dos seis casos

Atualização: 06/10/2026 (America/Fortaleza). Critérios: Seção 9.2.3 de
`Projeto.md`. Resultado técnico atual: **3 casos aprovados e 3 reprovados**.
Os seis casos têm resultado e evidência textual; a aceitação formal e o
fechamento da issue permanecem pendentes dos itens descritos ao final.

**Imagens incorporadas:** [galeria das dezessete capturas originais](../../../src/backend/evidencias/rnf07-rnf09/imagens/README.md),
com vínculo às frases e manifesto SHA-256. Todas correspondem aos anexos
enviados pelo participante, conferidos visualmente e copiados sem edição.

## Resultados

| Caso | Resultado técnico | Ferramenta | Evidência |
|---|---|---|---|
| CT-RNF07-P | Reprovado pela meta conjunta de RNF07; positivas: 4/10 compreendidas, 6 falhas | Interface local, participante P01, transcrição visual, rubrica congelada e apuração CSV por pytest | [Transcrições](../../../src/backend/evidencias/rnf07-rnf09/transcricao-rnf07-p01.md), [apuração P](../../../src/backend/evidencias/rnf07-rnf09/rodada-04/CT-RNF07-P.json) |
| CT-RNF07-N | Reprovado pela meta conjunta de RNF07; negativas: 2/10 compreendidas, 8 falhas | Mesmas ferramentas; frases ambíguas, sinônimos e erros leves | [Planilha](../../../src/backend/evidencias/rnf07-rnf09/coleta-rnf07-p01.csv), [apuração N](../../../src/backend/evidencias/rnf07-rnf09/rodada-04/CT-RNF07-N.json) |
| CT-RNF08-P | Reprovado: contrato passa no checklist, mas o critério exige Copilot removido da arquitetura vigente | TestClient, modelo OpenAPI/Pydantic, checklist e revisão documental | [Observação](../../../src/backend/evidencias/rnf07-rnf09/rodada-04/CT-RNF08-P.json) |
| CT-RNF08-N | Aprovado: cópias sem operação obrigatória ou com tipo incompatível rejeitadas | pytest, checklist de contrato e cópias isoladas | [Observação](../../../src/backend/evidencias/rnf07-rnf09/rodada-04/CT-RNF08-N.json) |
| CT-RNF09-P | Aprovado: consulta e conteúdo preservados em diretório alternativo sem alterar núcleo | pytest, configuração de origem e núcleo RAG local | [Observação](../../../src/backend/evidencias/rnf07-rnf09/rodada-04/CT-RNF09-P.json) |
| CT-RNF09-N | Aprovado após correção: origens ausentes/inválidas falham explicitamente | pytest, fontes inválidas e erro de domínio | [Observação](../../../src/backend/evidencias/rnf07-rnf09/rodada-04/CT-RNF09-N.json) |

Execução: `python -m scripts.run_s5_31 --round rodada-04` em `src/backend`.
[Log](../../../src/backend/evidencias/rnf07-rnf09/rodada-04/pytest.txt),
[JUnit](../../../src/backend/evidencias/rnf07-rnf09/rodada-04/pytest.xml) e
[manifesto com hashes](../../../src/backend/evidencias/rnf07-rnf09/rodada-04/manifesto.json).
A saída 1 corresponde aos três critérios reprovados, sem mascarar falhas.
O pytest de RNF07 apura registros já coletados; não simula participantes,
reaplica perguntas nem substitui a revisão humana.

## RNF07: vinte frases recebidas

Dezessete imagens fornecidas pelo participante documentam as vinte frases
da amostra congelada. A repetição visível de P01 conta uma única vez.
Resultado técnico pela rubrica: **6 compreendidas + 0 orientações úteis**,
com **14 falhas**. Taxa: `100 × 6 / 20 = 30%`, inferior a `80%` (16/20).
Nenhuma frase ficou sem resposta registrada. O denominador e os critérios
não foram alterados após observar as respostas. A avaliação de utilidade
pelo participante e a revisão independente ainda não foram recebidas.

Observações a encaminhar à frente backend:

- **OBS-S5-31-RNF07-01:** sete respostas de insuficiência apesar de título
  pertinente exibido (P02, P03, P05, P07, P08, P09 e N10). Investigar geração
  e validação de evidência; a imagem não determina a causa interna.
- **OBS-S5-31-RNF07-02:** seis respostas genéricas de fora de escopo sem
  orientação acionável (N01–N05 e N09). Prever esclarecimento útil para
  ambiguidades e termos não compreendidos, sem inventar fatos.
- **OBS-S5-31-RNF07-03:** N07, com erro leve, exibe fonte de reclamações em
  vez de orientação sobre objeto perdido. Investigar recuperação e tratamento
  linguístico com casos adicionais, evitando ajustes exclusivos à amostra.

Eventuais correções exigem nova rodada identificada. Manter esta coleta
reprovada no histórico. O produto não foi alterado pelo assistente entre
os blocos de perguntas desta sessão.

## Limites e pendências para fechar a task

1. Confirmar se o participante usou conversa nova para cada frase. A pergunta
   foi feita durante a coleta e ainda não foi respondida. Até essa confirmação,
   a conformidade com o protocolo está pendente; eventual desvio exige registro
   e reaplicação controlada, sem apagar os resultados atuais.
2. Receber as avaliações de utilidade do participante e a revisão de outra
   frente. As avaliações técnicas registradas foram feitas pelo assistente,
   não atribuídas ao participante nem apresentadas como aprovação de revisor.
3. Incorporar os arquivos originais das dezessete imagens ao repositório.
   **Concluído:** originais localizados em `OneDrive/Imagens/Screenshots`,
   conferidos e preservados em `imagens/`, com manifesto de nomes e hashes.
4. Conciliar RNF08 e arquitetura com a frente responsável, conforme S5-43
   (#297); não alterar o critério apenas para aprovar o resultado.
5. Conferir assignee, revisor, labels e milestone; publicar MR, obter comentário
   e aprovação de revisor, com `Closes #285`. Nada disso foi simulado ou marcado
   como realizado. O [texto do MR](mr-s5-31.md) está preparado localmente.

Histórico: [rodadas 01/02](relatorio-s5-31.md) e
[correção e reteste de RNF09](reteste-s5-31-rnf09.md). A regressão do código
alterado passou em 58 testes. As limitações de escopo local de RNF08/RNF09
continuam válidas; não houve homologação em tenant, contêiner ou serviço publicado.

Verificação final após incorporar as imagens: [rodada 05](../../../src/backend/evidencias/rnf07-rnf09/rodada-05/pytest.txt).
Ela preserva o resultado de 3 aprovados e 3 reprovados; a inclusão de imagens
não modifica as respostas recebidas nem constitui reaplicação com participante.
