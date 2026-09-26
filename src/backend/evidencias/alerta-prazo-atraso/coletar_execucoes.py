"""Extrai do banco as execuções de ponta a ponta do alerta de prazo.

Somente leitura: consulta inscrições, sessões guiadas, avaliações, outbox,
ocorrências, notificações, tentativas de entrega e auditoria, e monta
`execucoes-e2e.md`, com uma seção por inscrição ligada pelo `correlation_id`.

O relatório traz apenas identificadores, regras, resultados e horários. O
sujeito do dono da inscrição é o da identidade simulada do ambiente local.

Uso, a partir de `src/backend`, com `SUPABASE_DATABASE_URL` no `.env`:

    PYTHONPATH=. .venv/bin/python evidencias/alerta-prazo-atraso/coletar_execucoes.py
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from app.database.connection import open_database_connection  # noqa: E402

SAIDA = Path(__file__).resolve().parent / "execucoes-e2e.md"
FUSO = ZoneInfo("America/Sao_Paulo")


def hora(valor: datetime | None) -> str:
    return valor.astimezone(FUSO).strftime("%d/%m %H:%M:%S") if valor else "—"


def consultar(cursor, sql: str, parametros: tuple = ()) -> list[dict]:
    cursor.execute(sql, parametros)
    colunas = [coluna.name for coluna in cursor.description]
    return [dict(zip(colunas, linha)) for linha in cursor.fetchall()]


def coletar() -> dict:
    conexao = open_database_connection()
    try:
        with conexao.cursor() as cursor:
            dados = {
                "inscricoes": consultar(cursor, """
                    SELECT s.subscription_id::text AS id, s.correlation_id, s.owner_subject,
                           s.status, s.created_at, s.updated_at, p.code AS projeto,
                           s.subscription_payload -> 'rule' AS regra
                      FROM public.alert_subscriptions s
                      LEFT JOIN public.projects p ON p.id::text = s.project_id
                     ORDER BY s.created_at"""),
                "sessoes": consultar(cursor, """
                    SELECT session_payload ->> 'subscription_id' AS inscricao,
                           workflow_status, session_payload -> 'answers' AS respostas
                      FROM public.workflow_sessions
                     WHERE workflow_name = 'alerta_prazo_atraso'"""),
                "avaliacoes": consultar(cursor, """
                    SELECT evaluation_id::text AS id, subscription_id::text AS inscricao,
                           as_of_date, outcome, created_at,
                           evaluation_payload -> 'eligible_count' AS elegiveis,
                           evaluation_payload -> 'evaluated_count' AS avaliados,
                           evaluation_payload -> 'details' AS detalhes
                      FROM public.alert_evaluations ORDER BY created_at"""),
                "outbox": consultar(cursor, """
                    SELECT event_id::text AS id, event_type, correlation_id, status,
                           attempts, created_at, published_at
                      FROM public.message_outbox ORDER BY created_at"""),
                "notificacoes": consultar(cursor, """
                    SELECT n.notification_id::text AS id, n.subscription_id::text AS inscricao,
                           n.status, n.created_at, n.read_at, o.episode_key,
                           n.notification_payload ->> 'title' AS titulo,
                           n.notification_payload ->> 'overdue_days' AS atraso,
                           (SELECT COUNT(*) FROM public.notification_delivery_attempts t
                             WHERE t.notification_id = n.notification_id) AS tentativas
                      FROM public.alert_notifications n
                      JOIN public.alert_occurrences o USING (occurrence_id)
                     ORDER BY n.created_at"""),
                "auditoria": consultar(cursor, """
                    SELECT event_type, component, event_status, correlation_id,
                           event_payload, created_at
                      FROM public.audit_events
                     WHERE component IN ('alert_workflow', 'alert_scheduler',
                                         'alert_evaluator', 'message_bus',
                                         'notification_dispatcher')
                     ORDER BY created_at"""),
                "itens": consultar(cursor, """
                    SELECT m.id::text AS id, p.code AS projeto, m.description,
                           m.planned_date, m.completed_date, m.status
                      FROM public.project_deliverables_milestones m
                      JOIN public.projects p ON p.id = m.project_id
                     ORDER BY p.code, m.planned_date"""),
                "carga": consultar(cursor, """
                    SELECT MIN(created_at) AS gravada_em
                      FROM public.project_deliverables_milestones"""),
            }
    finally:
        conexao.close()
    return dados


def montar(dados: dict) -> str:
    por_inscricao = defaultdict(lambda: defaultdict(list))
    for chave in ("avaliacoes", "notificacoes"):
        for linha in dados[chave]:
            por_inscricao[linha["inscricao"]][chave].append(linha)
    por_correlacao = defaultdict(lambda: defaultdict(list))
    for chave in ("outbox", "auditoria"):
        for linha in dados[chave]:
            por_correlacao[linha["correlation_id"]][chave].append(linha)
    sessoes = {linha["inscricao"]: linha for linha in dados["sessoes"] if linha["inscricao"]}
    itens = {linha["id"]: linha for linha in dados["itens"]}

    linhas = [
        "# Execuções de ponta a ponta do alerta de prazo",
        "",
        f"Extraído do banco em {datetime.now(FUSO):%d/%m/%Y %H:%M} por `coletar_execucoes.py`,",
        "somente com consultas de leitura. Horários de Brasília.",
        "",
        "## Itens de cronograma avaliados",
        "",
        f"Marcos da carga atual da massa, gravada em {hora(dados['carga'][0]['gravada_em'])}. "
        "A carga apaga e recria os marcos, então os IDs de item das avaliações anteriores a ela "
        "são da carga anterior; nesses casos, o item aparece pelo nome no título da notificação "
        "e pela data planejada na chave do episódio (`inscrição:item:data planejada:bloco de reenvio`).",
        "",
        "| Projeto | Item | Data planejada | Conclusão | Situação |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in dados["itens"]:
        linhas.append(
            f"| {item['projeto']} | {item['description']} | {item['planned_date']} "
            f"| {item['completed_date'] or '—'} | {item['status'] or '—'} |"
        )

    linhas += [
        "",
        "## Resumo por inscrição",
        "",
        "| Inscrição | Projeto | Limiar (dias) | Frequência | Reenvio (dias) | Avaliações | "
        "Pedidos de notificação publicados | Notificações criadas | Estado final |",
        "| --- | --- | ---: | --- | ---: | --- | ---: | ---: | --- |",
    ]
    for inscricao in dados["inscricoes"]:
        regra = inscricao["regra"]
        avaliacoes = por_inscricao[inscricao["id"]]["avaliacoes"]
        eventos = por_correlacao[inscricao["correlation_id"]]["outbox"]
        pedidos = sum(e["event_type"] == "alert.notification.requested" for e in eventos)
        linhas.append(
            f"| `{inscricao['id'][:8]}` | {inscricao['projeto']} | {regra['threshold_days']} "
            f"| {regra['trigger_type']} | {regra.get('resend_interval_days') or '—'} "
            f"| {', '.join(a['outcome'] for a in avaliacoes) or '—'} | {pedidos} "
            f"| {len(por_inscricao[inscricao['id']]['notificacoes'])} | {inscricao['status']} |"
        )

    for inscricao in dados["inscricoes"]:
        regra = inscricao["regra"]
        correlacao = inscricao["correlation_id"]
        sessao = sessoes.get(inscricao["id"])
        linhas += [
            "",
            f"## Inscrição `{inscricao['id']}`",
            "",
            f"- Correlação: `{correlacao}`",
            f"- Dono: `{inscricao['owner_subject']}`",
            f"- Regra: projeto {inscricao['projeto']} ({regra['project_label']}), "
            f"avisar com mais de {regra['threshold_days']} dias corridos de atraso "
            f"(`{regra['comparison_operator']}`), {regra['trigger_type']}, "
            f"reenvio {regra.get('resend_interval_days') or 'desligado'}",
            f"- Criada em {hora(inscricao['created_at'])}; estado `{inscricao['status']}` "
            f"desde {hora(inscricao['updated_at'])}",
        ]
        if sessao:
            linhas.append(
                f"- Sessão guiada: `{sessao['workflow_status']}`, respostas "
                f"`{json.dumps(sessao['respostas'], ensure_ascii=False, sort_keys=True)}`"
            )
        linhas += ["", "**Avaliações**", ""]
        for avaliacao in por_inscricao[inscricao["id"]]["avaliacoes"]:
            linhas.append(
                f"- `{avaliacao['id'][:8]}` em {hora(avaliacao['created_at'])}, data de "
                f"referência {avaliacao['as_of_date']}: **{avaliacao['outcome']}**, "
                f"{avaliacao['elegiveis']} de {avaliacao['avaliados']} itens elegíveis"
            )
            for detalhe in avaliacao["detalhes"]:
                item = itens.get(detalhe["item_id"])
                nome = item["description"] if item else f"item `{detalhe['item_id'][:8]}` da carga anterior"
                atraso = detalhe.get("overdue_days", "—")
                linhas.append(f"  - {nome}: {atraso} dias de atraso → `{detalhe['result']}`")
        linhas += ["", "**Outbox (RabbitMQ)**", ""]
        for evento in por_correlacao[correlacao]["outbox"]:
            linhas.append(
                f"- `{evento['event_type']}`: `{evento['status']}`, {evento['attempts']} "
                f"tentativa(s), gravado {hora(evento['created_at'])}, publicado "
                f"{hora(evento['published_at'])}"
            )
        notificacoes = por_inscricao[inscricao["id"]]["notificacoes"]
        linhas += ["", "**Notificações**", ""]
        if not notificacoes:
            linhas.append("- nenhuma")
        for notificacao in notificacoes:
            linhas.append(
                f"- `{notificacao['id'][:8]}` \"{notificacao['titulo']}\", {notificacao['atraso']} "
                f"dias de atraso; `{notificacao['status']}`, criada {hora(notificacao['created_at'])}, "
                f"lida {hora(notificacao['read_at'])}; {notificacao['tentativas']} tentativa de "
                f"entrega; episódio `{notificacao['episode_key']}`"
            )
        linhas += ["", "**Auditoria**", ""]
        for evento in por_correlacao[correlacao]["auditoria"]:
            linhas.append(
                f"- {hora(evento['created_at'])} `{evento['event_type']}` "
                f"({evento['component']}, {evento['event_status']}): "
                f"`{json.dumps(evento['event_payload'], ensure_ascii=False, sort_keys=True)}`"
            )
    return "\n".join(linhas) + "\n"


if __name__ == "__main__":
    SAIDA.write_text(montar(coletar()), encoding="utf-8")
    print(f"Relatório gravado em {SAIDA.name}")
