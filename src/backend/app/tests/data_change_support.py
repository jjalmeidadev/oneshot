"""Massa e perfis compartilhados pelos testes da alteracao pelo chat (S5-06).

A massa espelha `13_seed_portfolio_report_data.sql`: os mesmos nomes, datas e
status do PRJ-0442 e do PRJ-0510, para que os exemplos do contrato (Secao
8.5.13) rodem igual em memoria e no PostgreSQL.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid5, NAMESPACE_URL

from app.data_changes.repository import InMemoryDataChangeRepository, Project
from app.data_changes.service import DataChangeService
from app.security.access import AccessContext, AccessGrant

SUBPORTFOLIO_MOD = "11111111-1111-4111-8111-111111111111"
SUBPORTFOLIO_DEMO = "22222222-2222-4222-8222-222222222222"
PRJ_0442 = "00000000-0000-4000-8000-000000000442"
PRJ_0510 = "00000000-0000-4000-8000-000000000510"
PRJ_DEMO = "00000000-0000-4000-8000-00000000d3e0"

RISK_INTERFERENCIA = "aaaaaaaa-0000-4000-8000-000000000001"
RISK_JANELA = "aaaaaaaa-0000-4000-8000-000000000002"
RISK_LEGADO = "aaaaaaaa-0000-4000-8000-000000000003"
MILESTONE_LOTE1 = "bbbbbbbb-0000-4000-8000-000000000001"
MILESTONE_OPERACAO = "bbbbbbbb-0000-4000-8000-000000000002"
MILESTONE_ACEITE = "bbbbbbbb-0000-4000-8000-000000000003"
ACTIVITY_LOTE2 = "cccccccc-0000-4000-8000-000000000003"
ACTIVITY_LOTE1 = "cccccccc-0000-4000-8000-000000000002"
ACTIVITY_TESTES = "cccccccc-0000-4000-8000-000000000004"

#: 06/10/2026, 14h em Sao Paulo.
START = datetime(2026, 10, 6, 17, 0, tzinfo=timezone.utc)


@dataclass
class Clock:
    now: datetime = START

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kwargs: float) -> None:
        self.now = self.now + timedelta(**kwargs)


def build_repository() -> InMemoryDataChangeRepository:
    repo = InMemoryDataChangeRepository()
    repo.add_project(
        Project(PRJ_0442, "PRJ-0442", "Modernizacao do Sistema de Sinalizacao da Linha Azul", SUBPORTFOLIO_MOD),
        {"status": "em_andamento", "planned_end_date": date(2026, 12, 20), "start_date": date(2026, 1, 15)},
    )
    repo.add_project(
        Project(PRJ_0510, "PRJ-0510", "Modernizacao do Centro de Controle Operacional", SUBPORTFOLIO_MOD),
        {"status": "atencao", "planned_end_date": date(2027, 3, 15), "start_date": date(2026, 2, 1)},
    )
    repo.add_project(
        Project(PRJ_DEMO, "PRJ-DEMO-ACESSO", "Projeto sintetico de negacao cruzada", SUBPORTFOLIO_DEMO),
        {"status": "planejado", "planned_end_date": date(2027, 6, 30), "start_date": date(2026, 6, 1)},
    )
    for target_id, label, status, owner, due in (
        (RISK_JANELA, "Restricao de janela operacional para instalacao", "em_tratamento",
         "Coordenacao de Implantacao", date(2026, 10, 15)),
        (RISK_INTERFERENCIA, "Interferencia com a operacao comercial", "aberto",
         "Gerencia de Operacao", date(2026, 11, 30)),
        (RISK_LEGADO, "Compatibilidade com equipamentos legados", "em_tratamento",
         "Engenharia de Sistemas", date(2026, 10, 31)),
    ):
        repo.add_target("risco", target_id, PRJ_0442, label,
                        {"status": status, "owner_name": owner, "due_date": due, "item_type": "risco"})
    for target_id, label, planned, status in (
        (MILESTONE_LOTE1, "Instalacao do primeiro lote de equipamentos de sinalizacao", date(2026, 9, 20), "em_andamento"),
        (MILESTONE_OPERACAO, "Inicio da operacao assistida na Linha Azul", date(2026, 11, 10), "planejado"),
        (MILESTONE_ACEITE, "Aceite definitivo do sistema de sinalizacao", date(2027, 2, 28), "planejado"),
    ):
        repo.add_target("marco", target_id, PRJ_0442, label,
                        {"planned_date": planned, "status": status, "completed_date": None})
    for target_id, label, start, end, progress, status in (
        (ACTIVITY_LOTE1, "Instalacao do lote 1 de equipamentos de sinalizacao",
         date(2026, 5, 4), date(2026, 9, 20), Decimal("100.00"), "concluido"),
        (ACTIVITY_LOTE2, "Instalacao do lote 2 de equipamentos de sinalizacao",
         date(2026, 9, 21), date(2026, 11, 15), Decimal("35.00"), "em_andamento"),
        (ACTIVITY_TESTES, "Testes integrados de sinalizacao",
         date(2026, 11, 16), date(2026, 12, 10), Decimal("0.00"), "planejado"),
    ):
        repo.add_target("cronograma", target_id, PRJ_0442, label, {
            "planned_end_date": end, "status": status, "progress_percent": progress,
            "planned_start_date": start,
        })
    return repo


def build_service(repo: InMemoryDataChangeRepository | None = None, clock: Clock | None = None) -> DataChangeService:
    return DataChangeService(repo or build_repository(), now=clock or Clock())


def _context(
    key: str,
    role: str,
    grants: tuple[AccessGrant, ...],
    display_name: str,
    project_codes: tuple[str, ...] = (),
) -> AccessContext:
    user_id = uuid5(NAMESPACE_URL, f"s5-06:{key}")
    return AccessContext(
        user_id=user_id,
        auth_subject=uuid5(NAMESPACE_URL, f"auth:{key}"),
        role_name=role,
        allowed_subportfolio_ids=frozenset(UUID(g.subportfolio_id) if isinstance(g.subportfolio_id, str) else g.subportfolio_id
                                           for g in grants if g.subportfolio_id),
        allowed_project_ids=frozenset(UUID(str(g.project_id)) for g in grants if g.project_id),
        can_read=any(g.can_read for g in grants),
        can_write=any(g.can_write for g in grants),
        can_export=any(g.can_export for g in grants),
        grants=grants,
        allowed_project_codes=frozenset(code.casefold() for code in project_codes),
        allowed_subportfolio_codes=frozenset(
            g.subportfolio_code.casefold() for g in grants if g.subportfolio_code
        ),
        display_name=display_name,
        email=f"{key}@oneshot.example.com",
    )


def gerente() -> AccessContext:
    return _context(
        "gerente", "equipe_projeto",
        (AccessGrant("projeto", None, UUID(PRJ_0442), True, True, True, project_code="PRJ-0442"),),
        "[DEMO] Gerente de Projeto",
        ("PRJ-0442",),
    )


def outro_gerente() -> AccessContext:
    """Mesmo perfil e escopo do gerente, mas outra pessoa."""

    return _context(
        "gerente-2", "equipe_projeto",
        (AccessGrant("projeto", None, UUID(PRJ_0442), True, True, True, project_code="PRJ-0442"),),
        "[DEMO] Gerente substituto",
        ("PRJ-0442",),
    )


def pmo() -> AccessContext:
    return _context(
        "pmo", "pmo",
        (AccessGrant("portfolio", None, None, True, False, True),),
        "[DEMO] PMO",
        ("PRJ-0442", "PRJ-0510", "PRJ-DEMO-ACESSO"),
    )


def lider(can_write: bool = False) -> AccessContext:
    return _context(
        "lider" + ("-escrita" if can_write else ""), "lider_subportfolio",
        (AccessGrant("subportfolio", UUID(SUBPORTFOLIO_MOD), None, True, can_write, True, subportfolio_code="MOD"),),
        "[DEMO] Lider de Subportfolio",
        ("PRJ-0442", "PRJ-0510"),
    )


def consulta() -> AccessContext:
    return _context(
        "consulta", "consulta",
        (AccessGrant("projeto", None, UUID(PRJ_0510), True, False, False, project_code="PRJ-0510"),),
        "[DEMO] Consulta",
        ("PRJ-0510",),
    )


def escrita_em_um_leitura_em_outro() -> AccessContext:
    """Duas regras: escrita no PRJ-0442 e so leitura no PRJ-0510.

    O agregado `can_write` e verdadeiro; a checagem por regra precisa negar o
    PRJ-0510.
    """

    return _context(
        "duas-regras", "equipe_projeto",
        (
            AccessGrant("projeto", None, UUID(PRJ_0442), True, True, True, project_code="PRJ-0442"),
            AccessGrant("projeto", None, UUID(PRJ_0510), True, False, False, project_code="PRJ-0510"),
        ),
        "[DEMO] Duas regras",
        ("PRJ-0442", "PRJ-0510"),
    )
