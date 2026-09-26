"""Gera consultas adicionais de treino para o classificador de intenções.

Os padrões foram escritos a partir das confusões observadas exclusivamente na
validação. O script não altera os splits fixos: todas as novas consultas são de
treino e textos já existentes em qualquer split são descartados. A geração é
determinística e preserva acentos, negações e demais palavras funcionais.
"""

from __future__ import annotations

import csv
import random
import re
import unicodedata
from pathlib import Path


SEED = 251
RAIZ = Path(__file__).resolve().parent
DATASET = RAIZ / "artefatos" / "dataset_intencoes.csv"
SAIDA = RAIZ / "artefatos" / "consultas_sinteticas_issue_251.csv"


SLOTS = {
    "projeto": [
        "Linha 2-Verde",
        "Linha 15-Prata",
        "extensão da Linha 5-Lilás",
        "modernização da Linha 3-Vermelha",
        "programa de acessibilidade",
        "projeto de sinalização CBTC",
        "reforma da Estação Santana",
        "PRJ-2031",
    ],
    "projeto2": [
        "Linha 4-Amarela",
        "Linha 17-Ouro",
        "Estação Vila Sônia",
        "programa de eficiência energética",
        "projeto de renovação de frota",
        "modernização do CCO",
        "Pátio Oratório",
        "PRJ-0442",
    ],
    "subportfolio": [
        "Expansão",
        "Modernização",
        "Manutenção",
        "Tecnologia da Informação",
        "Sustentabilidade",
        "Segurança Operacional",
        "Acessibilidade",
        "obras civis",
    ],
    "periodo": [
        "neste mês",
        "no último trimestre",
        "desde janeiro",
        "nos últimos seis meses",
        "em 2026",
        "no acumulado do ano",
        "nesta semana",
        "no primeiro semestre",
    ],
    "data": [
        "30/06/2026",
        "15/09/2026",
        "dezembro de 2026",
        "fim do trimestre",
        "31/03/2027",
        "próxima quinzena",
        "segunda-feira",
        "fim do mês",
    ],
    "responsavel": [
        "Roberto",
        "Mariana",
        "Carlos",
        "gerente do projeto",
        "PMO",
        "equipe de engenharia",
        "patrocinador",
        "diretoria de operações",
    ],
    "indicador": [
        "SPI",
        "CPI",
        "percentual de conclusão",
        "aderência ao cronograma",
        "desvio de custo",
        "curva S",
        "execução orçamentária",
        "avanço físico",
    ],
    "risco": [
        "atraso na desapropriação",
        "indisponibilidade de fornecedor",
        "estouro de orçamento",
        "impacto ambiental",
        "integração de sistemas",
        "falta de mão de obra",
        "risco regulatório",
        "falha de suprimentos",
    ],
    "documento": [
        "TAP",
        "relatório anual",
        "balanço do portfólio",
        "cronograma físico-financeiro",
        "ata da última reunião",
        "planilha de marcos",
        "relatório de acompanhamento",
        "matriz de riscos",
    ],
}


TEMPLATES = {
    "consulta_status_projeto": [
        "consulte a situação atual do {projeto}",
        "em que estado se encontra o {projeto}?",
        "quero apenas o andamento geral do {projeto}",
        "o {projeto} avançou desde a última atualização?",
        "resuma o progresso atual do {projeto}",
        "há novidade sobre a execução do {projeto}?",
    ],
    "consulta_cronograma_prazo": [
        "consulte a data de término prevista do {projeto}",
        "quantos dias faltam para concluir o {projeto}?",
        "qual é o atraso acumulado no cronograma do {projeto}?",
        "mostre o prazo vigente do {projeto}",
        "quando começa e quando termina o {projeto}?",
        "o cronograma do {projeto} ainda prevê entrega em {data}?",
        "qual é a previsão atual de conclusão do {projeto}?",
        "as datas do {projeto} precisaram ser replanejadas?",
    ],
    "consulta_marcos_entregas": [
        "qual é o próximo marco contratual do {projeto}?",
        "liste as etapas já entregues do {projeto}",
        "quais entregáveis vencem {periodo} no {projeto}?",
        "consulte os milestones pendentes do {projeto}",
        "houve aceite da última entrega do {projeto}?",
        "quantos marcos ainda não foram concluídos no {projeto}?",
    ],
    "consulta_orcamento_custo": [
        "consulte o custo total previsto do {projeto}",
        "qual é o saldo disponível no orçamento do {projeto}?",
        "quanto foi realizado financeiramente no {projeto} {periodo}?",
        "mostre a diferença entre custo planejado e realizado do {projeto}",
        "qual verba ainda não foi utilizada no {projeto}?",
        "o orçamento aprovado do {projeto} foi ultrapassado?",
    ],
    "consulta_escopo_tap": [
        "o que não está incluído no escopo do {projeto}?",
        "consulte as premissas e restrições do TAP do {projeto}",
        "qual entrega final está definida para o {projeto}?",
        "liste os objetivos formais do {projeto}",
        "a atividade de testes faz parte do escopo do {projeto}?",
        "resuma a justificativa e os limites do {projeto}",
    ],
    "consulta_responsavel_equipe": [
        "quem responde oficialmente pelo {projeto}?",
        "consulte o gerente e o patrocinador do {projeto}",
        "qual equipe está alocada no {projeto}?",
        "quem é o ponto focal do {projeto}?",
        "qual área é responsável pela execução do {projeto}?",
        "o {responsavel} cuida de qual projeto?",
    ],
    "consulta_indicadores_kpi": [
        "consulte o valor atual do indicador {indicador} do {projeto}",
        "mostre somente os KPIs medidos no {projeto}",
        "o {indicador} do {projeto} atingiu a meta?",
        "qual é o desempenho numérico do {projeto} {periodo}?",
        "exiba o painel de métricas do {projeto}",
        "quais indicadores do {projeto} estão abaixo da meta?",
    ],
    "consulta_riscos_projeto": [
        "consulte a lista de riscos já registrados no {projeto}",
        "qual é a probabilidade e o impacto dos riscos do {projeto}?",
        "mostre a matriz de riscos vigente do {projeto}",
        "o risco de {risco} consta no {projeto}?",
        "quais riscos do {projeto} ainda estão abertos?",
        "qual tratamento está definido para o maior risco do {projeto}?",
    ],
    "consulta_pendencias_projeto": [
        "consulte as ações em aberto do {projeto}",
        "quais pendências aguardam resposta no {projeto}?",
        "liste os itens não resolvidos do {projeto}",
        "há alguma ação atrasada atribuída no {projeto}?",
        "quem deve responder às pendências do {projeto}?",
        "mostre o backlog de providências do {projeto}",
    ],
    "consulta_documentos_fonte": [
        "onde encontro o {documento} do {projeto}?",
        "forneça o link de origem do {documento} do {projeto}",
        "em qual pasta do SharePoint está o {documento}?",
        "qual documento comprova a informação do {projeto}?",
        "localize a versão mais recente do {documento}",
        "mostre a fonte documental usada para o {projeto}",
    ],
    "consulta_visao_portfolio": [
        "mostre uma visão consolidada do portfólio de {subportfolio}",
        "quantos projetos existem na carteira de {subportfolio}?",
        "resuma a saúde geral do portfólio de {subportfolio}",
        "consulte o panorama executivo de todos os projetos",
        "qual é a distribuição dos projetos por situação?",
        "liste os projetos prioritários do subportfólio de {subportfolio}",
    ],
    "comparacao_entre_projetos": [
        "compare {projeto} com {projeto2} pelo prazo",
        "qual dos projetos {projeto} e {projeto2} tem maior custo?",
        "mostre lado a lado os indicadores de {projeto} e {projeto2}",
        "aponte as diferenças de risco entre {projeto} e {projeto2}",
        "faça um comparativo do avanço de {projeto} versus {projeto2}",
        "entre {projeto} e {projeto2}, qual está mais atrasado?",
    ],
    "analise_tendencia_desempenho": [
        "analise a evolução histórica do desempenho do {projeto}",
        "qual é a tendência do {indicador} do {projeto} ao longo do tempo?",
        "projete o comportamento futuro do {projeto} com base no histórico",
        "o desempenho do {projeto} vem melhorando ou piorando {periodo}?",
        "explique a causa da variação temporal do {indicador}",
        "mostre a série histórica do avanço do {projeto}",
        "quais causas explicam a variação de desempenho do {projeto}?",
        "avalie como o {indicador} do {projeto} evoluiu {periodo}",
    ],
    "transacao_atualizar_status": [
        "atualize a situação do {projeto} para em andamento",
        "registre que o {projeto} alcançou 80% de avanço",
        "mude o estado do {projeto} para concluído",
        "salve um novo percentual de progresso para o {projeto}",
        "altere o status executivo do {projeto}",
        "registre a atualização de andamento do {projeto} em {data}",
    ],
    "transacao_atualizar_cronograma": [
        "replaneje a data final do {projeto} para {data}",
        "prorrogue o prazo do {projeto} até {data}",
        "altere o cronograma base do {projeto}",
        "mova o próximo marco do {projeto} para {data}",
        "registre uma nova previsão de término para o {projeto}",
        "repactue as datas atrasadas do {projeto}",
    ],
    "transacao_registrar_risco": [
        "cadastre o risco de {risco} no {projeto}",
        "inclua um novo risco crítico no registro do {projeto}",
        "atualize a probabilidade do risco de {risco}",
        "registre impacto alto para {risco} no {projeto}",
        "adicione uma resposta ao risco de {risco}",
        "encerre o risco de {risco} no {projeto}",
    ],
    "transacao_registrar_pendencia": [
        "abra uma pendência para o {responsavel} no {projeto}",
        "registre uma nova ação em aberto no {projeto}",
        "atribua a pendência do {projeto} ao {responsavel}",
        "marque a ação do {projeto} como resolvida",
        "adicione prazo {data} à pendência do {projeto}",
        "encerre o item pendente do {projeto}",
    ],
    "transacao_gerar_relatorio": [
        "gere um relatório executivo do {projeto}",
        "crie o relatório mensal do portfólio de {subportfolio}",
        "produza um balanço escrito do {projeto} {periodo}",
        "monte o relatório de acompanhamento do {projeto}",
        "emita um documento com o resumo do {projeto}",
        "prepare o relatório anual da carteira de {subportfolio}",
    ],
    "transacao_gerar_apresentacao": [
        "gere uma apresentação executiva sobre o {projeto}",
        "crie slides para a reunião do portfólio de {subportfolio}",
        "monte um PowerPoint com os resultados do {projeto}",
        "prepare um deck para a diretoria sobre o {projeto}",
        "transforme o resumo do {projeto} em slides",
        "faça uma apresentação visual do portfólio de {subportfolio}",
    ],
    "transacao_exportar_dados": [
        "exporte os dados do {projeto} para Excel",
        "baixe uma planilha com o portfólio de {subportfolio}",
        "gere um arquivo CSV dos indicadores do {projeto}",
        "salve a relação de projetos em formato de planilha",
        "extraia os dados brutos do {projeto}",
        "prepare um arquivo para download com a carteira de {subportfolio}",
    ],
    "transacao_agendar_compromisso": [
        "agende uma reunião sobre o {projeto} para {data}",
        "marque um checkpoint com o {responsavel}",
        "crie um compromisso de revisão do {projeto}",
        "reserve horário para discutir o portfólio de {subportfolio}",
        "inclua no calendário uma reunião do {projeto}",
        "convide o {responsavel} para uma revisão em {data}",
    ],
    "transacao_solicitar_atualizacao": [
        "peça ao {responsavel} uma atualização do {projeto}",
        "cobre o envio das informações pendentes do {projeto}",
        "solicite uma nova posição sobre o {projeto}",
        "envie ao {responsavel} um pedido de atualização",
        "notifique o responsável para atualizar o {projeto}",
        "requisite os dados mais recentes do {projeto}",
        "cobre o envio do {documento} pendente do {projeto}",
        "notifique o {responsavel} de que o {projeto} precisa ser atualizado",
        "peça confirmação do marco de {data} ao responsável do {projeto}",
        "envie uma cobrança pela revisão dos dados do {projeto}",
    ],
    "transacao_cadastrar_projeto": [
        "cadastre um novo projeto no portfólio de {subportfolio}",
        "crie o registro inicial de um projeto em planejamento",
        "inclua o {projeto} na carteira corporativa",
        "abra uma ficha de projeto com responsável {responsavel}",
        "adicione um novo programa ao subportfólio de {subportfolio}",
        "registre o projeto recém-aprovado no catálogo",
    ],
    "alerta_prazo_atraso": [
        "avise se o {projeto} ultrapassar o prazo",
        "notifique quando houver atraso no cronograma do {projeto}",
        "gere alerta caso a entrega do {projeto} não ocorra até {data}",
        "me alerte quando faltar uma semana para o prazo do {projeto}",
        "dispare aviso de marco vencido no {projeto}",
        "monitore estouro de prazo no portfólio de {subportfolio}",
    ],
    "alerta_estouro_orcamento": [
        "avise se o {projeto} ultrapassar o orçamento aprovado",
        "notifique quando o custo do {projeto} exceder o planejado",
        "gere alerta para desvio financeiro acima de 10% no {projeto}",
        "me alerte se o saldo do {projeto} ficar negativo",
        "dispare aviso de estouro orçamentário no {projeto}",
        "monitore excesso de gasto no portfólio de {subportfolio}",
    ],
    "alerta_risco_critico": [
        "avise quando surgir risco crítico no {projeto}",
        "notifique se o risco de {risco} tiver impacto alto",
        "gere alerta para risco sem plano de resposta no {projeto}",
        "me alerte quando a criticidade de um risco aumentar",
        "dispare aviso de risco escalado no {projeto}",
        "monitore riscos vermelhos no portfólio de {subportfolio}",
    ],
    "alerta_desatualizacao_dados": [
        "avise quando os dados do {projeto} ficarem desatualizados",
        "notifique se o {projeto} passar quinze dias sem atualização",
        "gere alerta para indicador antigo no {projeto}",
        "me alerte se não houver nova posição do {projeto}",
        "dispare aviso de informação vencida no portfólio de {subportfolio}",
        "monitore a data da última atualização do {projeto}",
        "notifique quando o status do {projeto} não for revisado {periodo}",
        "avise se o {documento} do {projeto} não for enviado até {data}",
        "gere alerta se o responsável não atualizar os dados {periodo}",
        "alerte sobre documento vencido no portfólio de {subportfolio}",
    ],
    "alerta_configurar_monitoramento": [
        "configure monitoramento semanal para o {projeto}",
        "crie uma regra de alerta para o {indicador} do {projeto}",
        "acompanhe automaticamente o {projeto} {periodo}",
        "defina frequência diária para verificar o {projeto}",
        "ative uma nova condição de monitoramento no {projeto}",
        "configure limite para alertar sobre o {indicador}",
    ],
    "alerta_gerenciar_inscricao": [
        "pause os alertas do {projeto}",
        "cancele minha inscrição nas notificações de {subportfolio}",
        "silencie temporariamente os avisos do {projeto}",
        "reative os alertas que acompanho sobre o {projeto}",
        "remova a notificação existente do {projeto}",
        "liste e desative minhas assinaturas de alerta",
    ],
    "fora_escopo_social": [
        "bom dia, como você está?",
        "obrigado pela ajuda",
        "olá, só estou testando o chat",
        "até mais e boa semana",
        "você está funcionando?",
        "legal, entendi a resposta",
    ],
    "fora_escopo_externo": [
        "qual é a previsão do tempo de amanhã?",
        "me conte o resultado do jogo",
        "ensine uma receita de bolo",
        "qual é a cotação do dólar hoje?",
        "quantos dias de férias eu tenho?",
        "como faço a declaração do imposto de renda?",
    ],
}


MACRO_POR_PREFIXO = {
    "consulta_": "CONSULTA",
    "comparacao_": "CONSULTA",
    "analise_": "CONSULTA",
    "transacao_": "TRANSACAO",
    "alerta_": "ALERTA",
    "fora_": "FORA_DE_ESCOPO",
}


def normalizar(texto: str) -> str:
    return " ".join(unicodedata.normalize("NFC", texto).lower().split())


def macro_da_intencao(intencao: str) -> str:
    for prefixo, macro in MACRO_POR_PREFIXO.items():
        if intencao.startswith(prefixo):
            return macro
    raise ValueError(f"Intenção sem macro conhecida: {intencao}")


def placeholders(template: str) -> list[str]:
    return re.findall(r"\{([a-z0-9_]+)\}", template)


def expandir(template: str, deslocamento: int) -> list[str]:
    nomes = placeholders(template)
    if not nomes:
        return [template]
    quantidade = max(len(SLOTS[nome]) for nome in nomes)
    return [
        template.format(
            **{
                nome: SLOTS[nome][(indice + deslocamento) % len(SLOTS[nome])]
                for nome in nomes
            }
        )
        for indice in range(quantidade)
    ]


def gerar() -> list[dict[str, str]]:
    with DATASET.open(encoding="utf-8", newline="") as arquivo:
        existentes = {normalizar(linha["texto"]) for linha in csv.DictReader(arquivo)}

    random.seed(SEED)
    linhas: list[dict[str, str]] = []
    for intencao, templates in TEMPLATES.items():
        for indice_template, template in enumerate(templates):
            for indice_texto, texto in enumerate(expandir(template, indice_template)):
                if normalizar(texto) in existentes:
                    continue
                existentes.add(normalizar(texto))
                linhas.append(
                    {
                        "texto": texto,
                        "intencao": intencao,
                        "macrointencao": macro_da_intencao(intencao),
                        "template_id": f"issue251_{intencao}#{indice_template:02d}",
                        "variacao": "sintetico_issue_251",
                        "split": "treino",
                        "split_ingenuo": "treino",
                    }
                )
    random.shuffle(linhas)
    return linhas


def main() -> int:
    linhas = gerar()
    with SAIDA.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]))
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"{len(linhas)} consultas sintéticas gravadas em {SAIDA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
