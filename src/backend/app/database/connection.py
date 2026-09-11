"""Conexao PostgreSQL/Supabase para probes controlados do backend."""

from collections.abc import Callable
import os
from typing import Any

DATABASE_URL_ENV_NAMES = ("DATABASE_URL", "SUPABASE_DATABASE_URL")
DEFAULT_CONNECT_TIMEOUT_SECONDS = 5
PUBLIC_DATABASE_ERROR_MESSAGE = (
    "Nao foi possivel conectar ao banco de dados. Tente novamente em instantes."
)


class DatabaseConfigurationError(RuntimeError):
    """Erro de configuracao esperado antes de abrir conexao externa."""


class DatabaseConnectionError(RuntimeError):
    """Erro controlado de conexao sem detalhes tecnicos para o usuario final."""


def get_database_url() -> str:
    """Retorna a URL de conexao configurada para Postgres/Supabase."""

    for name in DATABASE_URL_ENV_NAMES:
        value = os.getenv(name, "").strip()
        if value:
            return value

    raise DatabaseConfigurationError(
        "Configure DATABASE_URL ou SUPABASE_DATABASE_URL no ambiente do backend."
    )


def probe_database_connection(
    connect: Callable[..., Any] | None = None,
) -> bool:
    """Executa `SELECT 1` para validar somente conectividade com o banco."""

    try:
        connection = open_database_connection(connect=connect)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
                return bool(row and row[0] == 1)
        finally:
            connection.close()
    except DatabaseConfigurationError:
        raise
    except Exception as error:
        raise DatabaseConnectionError(PUBLIC_DATABASE_ERROR_MESSAGE) from error


def open_database_connection(connect: Callable[..., Any] | None = None) -> Any:
    """Abre uma conexao PostgreSQL/Supabase com timeout controlado."""

    database_url = get_database_url()
    connector = connect or _connect_with_psycopg
    return connector(
        database_url,
        connect_timeout=DEFAULT_CONNECT_TIMEOUT_SECONDS,
    )


def _connect_with_psycopg(database_url: str, **kwargs: object) -> Any:
    try:
        import psycopg
    except ImportError as error:
        raise DatabaseConfigurationError(
            "Instale as dependencias do backend antes de conectar ao banco."
        ) from error

    return psycopg.connect(database_url, **kwargs)
