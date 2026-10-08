# Evidências S5-31 — RNF07, RNF08 e RNF09 (#285)

Entrada principal: [consolidação dos seis casos](../../../../docs/testes/sprint5/consolidacao-s5-31.md).

| Artefato | Conteúdo |
|---|---|
| [Amostra congelada](../../../../docs/testes/sprint5/amostra-rnf07.csv) | Vinte frases e critérios definidos antes da aplicação |
| [Protocolo](../../../../docs/testes/sprint5/protocolo-rnf07.md) | Aplicação, rubrica e cálculo da taxa |
| [Sessão P01](sessao-rnf07-p01.md) | Consentimento e sequência de preparação e coleta |
| [Transcrições](transcricao-rnf07-p01.md) | Respostas e metadados visíveis nas dezessete imagens recebidas |
| [Galeria das 17 imagens originais](imagens/README.md) | Capturas conferidas, mapeadas por frase e preservadas sem edição, com SHA-256 |
| [Planilha](coleta-rnf07-p01.csv) | Vinte respostas, avaliação técnica e pendências de revisão |
| [Rodada 01](rodada-01/pytest.txt) | Diagnóstico inicial de contrato e portabilidade |
| [Rodada 02](rodada-02/manifesto.json) | Diagnóstico reproduzível anterior à correção |
| [Rodada 03](rodada-03/manifesto.json) | Reteste após correção de RNF09 |
| [Rodada 04](rodada-04/manifesto.json) | Seis casos, incluindo apuração das transcrições de RNF07 |
| [Rodada 05](rodada-05/manifesto.json) | Verificação final após inclusão dos arquivos das imagens |

RNF07: 6/20 respostas adequadas (30%), em avaliação técnica preliminar;
14 falhas. RNF09: positivos e negativos aprovados após correção. A saída
não zero da suíte é esperada pelos critérios que continuam reprovados,
não deve ser apresentada como aprovação dos seis casos.

Os dezessete binários foram localizados, conferidos e incorporados à pasta
`imagens/`. As menções à ausência de binários nos registros históricos
descrevem o estado anterior à localização; essa pendência está resolvida.
Não foram reconstruídas imagens nem produzidas capturas substitutas.

## Datas e integridade

As evidências preservam datas de execução e recebimento de 05–06/10/2026.
A pedido do responsável pela entrega, os quinze commits desta organização
usarão metadados de autor e committer de 02/10/2026 nos quatro primeiros e
05/10/2026 nos onze restantes, no fuso -03:00. Essas datas de organização
do histórico **não são as datas de execução dos testes**; consultar os
manifestos, logs e registros de coleta para a cronologia experimental.

Os hashes dos manifestos descrevem os bytes locais no momento de cada
rodada, inclusive o estado não commitado da árvore. Alterações posteriores
não invalidam registros anteriores: exigem nova rodada para uma nova
verificação. O cálculo automatizado de RNF07 verifica IDs, perguntas e
quantidade contra a amostra; não substitui a avaliação de utilidade do
participante ou a revisão independente.

## Localizacao das evidencias

A pasta foi transferida de `docs/evidencias/sprint-05/rnf07-rnf09` para
`src/backend/evidencias/rnf07-rnf09`. Logs e manifestos historicos preservam
os caminhos e hashes observados na execucao original; para localizar seus
artefatos, substituir o prefixo antigo pelo novo. Nao foram reescritos
resultados de rodadas anteriores.
