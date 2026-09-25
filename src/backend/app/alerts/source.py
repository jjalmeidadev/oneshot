"""Fontes de cronograma monitoradas pelo avaliador."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from app.alerts.errors import AlertConfigurationError
from app.alerts.schemas import ScheduleItem
from app.database.connection import open_database_connection


class ScheduleSource(ABC):
    @abstractmethod
    def list_projects(self) -> list[dict[str, str]]: ...

    @abstractmethod
    def list_items(self, project_id: str) -> list[ScheduleItem]: ...


class SyntheticScheduleSource(ScheduleSource):
    """Dados deterministicos para CLI, testes e demonstracao isolada."""

    def list_projects(self) -> list[dict[str, str]]:
        return [
            {"id": "PRJ-SINALIZACAO", "label": "Projeto de Sinalizacao"},
            {"id": "PRJ-ESTACOES", "label": "Modernizacao de Estacoes"},
        ]

    def list_items(self, project_id: str) -> list[ScheduleItem]:
        now = datetime.now(timezone.utc)
        values = {
            "PRJ-SINALIZACAO": [
                ScheduleItem(
                    item_id="A.3",
                    project_id=project_id,
                    description="Entrega A.3",
                    planned_end_date="2026-08-24",
                    progress_percent=80,
                    status="em_andamento",
                    updated_at=now,
                    source="synthetic://cronograma/A.3",
                ),
                ScheduleItem(
                    item_id="A.4",
                    project_id=project_id,
                    description="Entrega A.4",
                    planned_end_date="2026-09-28",
                    progress_percent=40,
                    status="em_andamento",
                    updated_at=now,
                    source="synthetic://cronograma/A.4",
                ),
            ]
        }
        return values.get(project_id, [])


class PostgresScheduleSource(ScheduleSource):
    def list_projects(self) -> list[dict[str, str]]:
        connection = open_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id::text, code, title FROM public.projects ORDER BY title"
                )
                return [
                    {"id": str(row[0]), "code": str(row[1]), "label": str(row[2])}
                    for row in cursor.fetchall()
                ]
        finally:
            connection.close()

    def list_items(self, project_id: str) -> list[ScheduleItem]:
        connection = open_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id::text, project_id::text, activity_name,
                           planned_end_date, actual_end_date, progress_percent,
                           status, updated_at
                    FROM public.schedule_items
                    WHERE project_id::text = %s
                    UNION ALL
                    SELECT id::text, project_id::text, description,
                           planned_date, completed_date, NULL, status, updated_at
                    FROM public.project_deliverables_milestones
                    WHERE project_id::text = %s
                    ORDER BY planned_end_date NULLS LAST;
                    """,
                    (project_id, project_id),
                )
                return [
                    ScheduleItem(
                        item_id=str(row[0]),
                        project_id=str(row[1]),
                        description=str(row[2]),
                        planned_end_date=row[3],
                        completed_date=row[4],
                        progress_percent=float(row[5]) if row[5] is not None else None,
                        status=str(row[6]) if row[6] else None,
                        updated_at=row[7],
                        source=f"db://schedule/{row[0]}",
                    )
                    for row in cursor.fetchall()
                ]
        except Exception as error:
            raise AlertConfigurationError("Nao foi possivel consultar o cronograma.") from error
        finally:
            connection.close()


@lru_cache(maxsize=1)
def get_schedule_source() -> ScheduleSource:
    mode = os.getenv("ALERT_SCHEDULE_SOURCE", "synthetic").strip().lower()
    if mode == "synthetic":
        return SyntheticScheduleSource()
    if mode == "database":
        return PostgresScheduleSource()
    raise AlertConfigurationError("ALERT_SCHEDULE_SOURCE invalido.")

