"""Reexecuta a regra do alerta de prazo com o código atual sobre o cronograma do banco.

As execuções de ponta a ponta de `execucoes-e2e.md` rodaram durante o
desenvolvimento. Este script liga as evidências à versão do código em que ele é
executado: usa `AlertService` e `PostgresScheduleSource` reais, lendo os marcos
do banco, e um repositório em memória, então nada é gravado no banco. O papel do
notifier (consumir `alert.notification.requested`) é feito aqui, chamando o mesmo
`create_notification` que o worker chama, porque o RabbitMQ não participa da
regra nem da deduplicação.

Cada cenário declara o resultado esperado antes da execução. A data de referência
é 22/09/2026, a mesma das execuções de ponta a ponta. O segredo da confirmação é
gerado para esta execução e descartado; a identidade é a simulada do `.env`, da
qual só o sujeito aparece na saída.

Uso, a partir de `src/backend`, com `SUPABASE_DATABASE_URL` no `.env`:

    PYTHONPATH=. .venv/bin/python evidencias/alerta-prazo-atraso/reexecutar_regra.py
"""

import json
import os
import subprocess
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from app.alerts.errors import AlertAccessDeniedError, AlertConflictError  # noqa: E402
from app.alerts.repository import InMemoryAlertRepository  # noqa: E402
from app.alerts.schemas import (  # noqa: E402
    AlertNotification,
    AlertRule,
    AlertSubscription,
    CreateAlertRequest,
    PrepareAlertRequest,
)
from app.alerts.service import AlertService  # noqa: E402
from app.alerts.source import PostgresScheduleSource  # noqa: E402
from app.reports.security import resolve_report_identity_by_subject  # noqa: E402

REFERENCIA = date(2026, 9, 22)
SAIDA = Path(__file__).resolve().parent / "reexecucao-regra.txt"


class Execucao:
    def __init__(self) -> None:
        self.repositorio = InMemoryAlertRepository()
        self.fonte = PostgresScheduleSource()
        self.servico = AlertService(self.repositorio, self.fonte, secret=os.urandom(32))
        configuracao = json.loads(os.getenv("REPORT_SIMULATED_IDENTITIES", "{}"))
        sujeito = next(iter(configuracao.values()))["subject"]
        self.identidade = resolve_report_identity_by_subject(sujeito)
        self.projetos = {item["code"]: item for item in self.fonte.list_projects()}
        self.entregues = 0
        self.linhas: list[str] = []
        self.conformes = 0
        self.total = 0

    def inscrever(self, codigo: str, limiar: int, reenvio: int | None = None, chave: str | None = None):
        projeto = self.projetos[codigo]
        regra = AlertRule(
            project_id=projeto["id"],
            project_label=projeto["label"],
            threshold_days=limiar,
            resend_interval_days=reenvio,
        )
        preparado = self.servico.prepare(
            PrepareAlertRequest(conversation_id="reexecucao-regra", rule=regra), self.identidade
        )
        return self.servico.create(
            CreateAlertRequest(
                prepared_alert=preparado.prepared_alert,
                confirmation_hash=preparado.confirmation_hash,
                idempotency_key=chave or f"reexecucao:{uuid4()}",
            ),
            self.identidade,
        ), preparado

    def entregar(self) -> list[bool]:
        """Consome os pedidos de notificação pendentes, como o notifier faz."""

        resultados = []
        for evento in self.repositorio.outbox[self.entregues:]:
            if evento["event_type"] == "alert.notification.requested":
                notificacao = AlertNotification.model_validate(evento["payload"]["notification"])
                resultados.append(
                    self.repositorio.create_notification(notificacao, evento["payload"]["episode_key"])
                )
        self.entregues = len(self.repositorio.outbox)
        return resultados

    def avaliar(self, inscricao_id: str, referencia: date = REFERENCIA) -> tuple[str, list[bool]]:
        avaliacao = self.servico.evaluate(inscricao_id, referencia)
        projeto = self.repositorio.get_subscription(inscricao_id).rule.project_id
        nomes = {item.item_id: item.description for item in self.fonte.list_items(projeto)}
        self.linhas.append(
            f"  observado: {avaliacao.outcome.value} ({avaliacao.eligible_count} de "
            f"{avaliacao.evaluated_count} itens elegíveis), data de referência {referencia}"
        )
        for detalhe in avaliacao.details:
            self.linhas.append(
                f"    - {nomes.get(detalhe['item_id'], detalhe['item_id'])}: "
                f"{detalhe.get('overdue_days', '—')} dias de atraso → {detalhe['result']}"
            )
        entregas = self.entregar()
        self.linhas.append(
            "  pedidos de notificação consumidos: "
            + (", ".join("notificação criada" if criada else "episódio já notificado, ignorado" for criada in entregas) or "nenhum")
        )
        return avaliacao.outcome.value, entregas

    def cenario(self, titulo: str, esperado: str) -> None:
        self.total += 1
        self.linhas += ["", f"Cenário {self.total} — {titulo}", f"  esperado: {esperado}"]

    def concluir(self, conforme: bool) -> None:
        self.conformes += conforme
        self.linhas.append(f"  resultado: {'conforme' if conforme else 'DIVERGENTE'}")


def executar() -> Execucao:
    e = Execucao()

    e.cenario("elegível: PRJ-0442, limiar de 0 dias", "matched e uma notificação criada")
    (elegivel, _), _ = e.inscrever("PRJ-0442", 0)
    resultado, entregas = e.avaliar(elegivel.subscription_id)
    e.concluir(resultado == "matched" and entregas == [True])

    e.cenario("limite estrito: PRJ-0442, limiar de 2 dias", "not_matched, porque 2 dias de atraso não é mais que 2")
    (estrito, _), _ = e.inscrever("PRJ-0442", 2)
    resultado, entregas = e.avaliar(estrito.subscription_id)
    e.concluir(resultado == "not_matched" and entregas == [])

    e.cenario("não elegível: PRJ-0442, limiar de 3 dias", "not_matched e nenhuma notificação")
    (acima, _), _ = e.inscrever("PRJ-0442", 3)
    resultado, entregas = e.avaliar(acima.subscription_id)
    e.concluir(resultado == "not_matched" and entregas == [])

    e.cenario("não elegível: PRJ-0587, limiar de 3650 dias", "not_matched e nenhuma notificação")
    (distante, _), _ = e.inscrever("PRJ-0587", 3650)
    resultado, entregas = e.avaliar(distante.subscription_id)
    e.concluir(resultado == "not_matched" and entregas == [])

    e.cenario(
        "repetição: nova avaliação da inscrição do cenário 1, mesma data",
        "matched, e o novo pedido de notificação é ignorado pelo episódio já notificado",
    )
    resultado, entregas = e.avaliar(elegivel.subscription_id)
    total = len(e.repositorio.list_notifications(e.identidade.subject))
    e.linhas.append(f"  notificações do dono depois da repetição: {total}")
    e.concluir(resultado == "matched" and entregas == [False] and total == 1)

    e.cenario(
        "reenvio a cada 7 dias: PRJ-0442, limiar de 0 dias, avaliado em 22/09, 29/09 e 30/09",
        "notificação em 22/09 (2 dias de atraso), nova em 29/09 (9 dias, novo bloco de 7) "
        "e nenhuma em 30/09 (10 dias, mesmo bloco)",
    )
    (reenvio, _), _ = e.inscrever("PRJ-0442", 0, reenvio=7)
    entregas_por_data = [e.avaliar(reenvio.subscription_id, REFERENCIA + timedelta(days=dias))[1] for dias in (0, 7, 8)]
    e.concluir(entregas_por_data == [[True], [True], [False]])

    e.cenario("criação idempotente: mesma chave de idempotência duas vezes", "a segunda chamada devolve a mesma inscrição, sem criar outra")
    (primeira, criada1), _ = e.inscrever("PRJ-0510", 5, chave="reexecucao:idempotencia")
    (segunda, criada2), _ = e.inscrever("PRJ-0510", 5, chave="reexecucao:idempotencia")
    e.linhas.append(f"  observado: primeira criada={criada1}, segunda criada={criada2}, mesma inscrição={primeira.subscription_id == segunda.subscription_id}")
    e.concluir(criada1 and not criada2 and primeira.subscription_id == segunda.subscription_id)

    e.cenario("confirmação adulterada: limiar alterado depois da revisão", "recusa com AlertConflictError")
    _, preparado = e.inscrever("PRJ-0442", 1)
    adulterado = preparado.prepared_alert.model_copy(deep=True)
    adulterado.request.rule.threshold_days = 30
    try:
        e.servico.create(CreateAlertRequest(prepared_alert=adulterado, confirmation_hash=preparado.confirmation_hash, idempotency_key=f"reexecucao:{uuid4()}"), e.identidade)
        e.linhas.append("  observado: inscrição criada")
        e.concluir(False)
    except AlertConflictError as erro:
        e.linhas.append(f"  observado: {type(erro).__name__} — {erro.message}")
        e.concluir(True)

    e.cenario("bloqueio: inscrição cujo dono não tem mais identidade válida", "AlertAccessDeniedError e inscrição no estado blocked")
    agora = datetime.now(timezone.utc)
    sem_acesso = AlertSubscription(
        subscription_id=str(uuid4()), correlation_id=str(uuid4()), idempotency_key="reexecucao:bloqueio",
        owner_subject="sujeito-sem-acesso", rule=elegivel.rule, next_evaluation_at=agora,
        created_at=agora, updated_at=agora,
    )
    e.repositorio.create_subscription(sem_acesso)
    try:
        e.servico.evaluate(sem_acesso.subscription_id, REFERENCIA)
        e.linhas.append("  observado: avaliação executada")
        e.concluir(False)
    except AlertAccessDeniedError as erro:
        estado = e.repositorio.get_subscription(sem_acesso.subscription_id).status.value
        e.linhas.append(f"  observado: {type(erro).__name__}; estado da inscrição: {estado}")
        e.concluir(estado == "blocked")
    return e


def commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "desconhecido"


if __name__ == "__main__":
    execucao = executar()
    cabecalho = [
        "TIPO DE REGISTRO: SAÍDA BRUTA PRESERVADA",
        "",
        "Reexecução da regra do alerta de prazo com o código atual",
        f"Execução: {datetime.now().astimezone():%d/%m/%Y %H:%M} (UTC{datetime.now().astimezone():%z})",
        f"Commit: {commit()}",
        "Cronograma: marcos do banco, somente leitura (PostgresScheduleSource)",
        "Repositório: em memória, sem escrita no banco (InMemoryAlertRepository)",
        f"Identidade: sujeito {execucao.identidade.subject}, da identidade simulada do .env",
        "",
        "Comando, a partir de src/backend:",
        "  PYTHONPATH=. .venv/bin/python evidencias/alerta-prazo-atraso/reexecutar_regra.py",
        "",
        f"Resultado: {execucao.conformes} de {execucao.total} cenários conforme o esperado.",
    ]
    SAIDA.write_text("\n".join(cabecalho + execucao.linhas) + "\n", encoding="utf-8")
    print(f"{execucao.conformes}/{execucao.total} cenários conformes; saída em {SAIDA.name}")
