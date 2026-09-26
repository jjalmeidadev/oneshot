"""Conexao PostgreSQL/Supabase para probes controlados do backend."""

from collections.abc import Callable
import os
from threading import Lock
from typing import Any

DATABASE_URL_ENV_NAMES = ("DATABASE_URL", "SUPABASE_DATABASE_URL")
DEFAULT_CONNECT_TIMEOUT_SECONDS = 5

#: Tamanho maximo do pool. Cada requisicao usa uma conexao por vez (RAG, depois
#: rastreabilidade), entao o numero de conexoes simultaneas acompanha o numero de
#: requisicoes simultaneas. Cinco cobre a carga do RNF05 sem pressionar o limite
#: de clientes do pooler do Supabase, compartilhado com o resto do time.
DEFAULT_POOL_MAX_SIZE = 5
#: Espera maxima por uma conexao livre antes de desistir com erro controlado.
DEFAULT_POOL_TIMEOUT_SECONDS = 10

#: Tempo maximo de uma consulta no servidor. As consultas do sistema levam cerca
#: de 140 ms, e nenhuma usa trava no banco; 5 s e folga de mais de 30 vezes.
DEFAULT_STATEMENT_TIMEOUT_MS = 5_000

#: *Keepalive* de TCP. Detecta em cerca de 11 s uma conexao cujo outro lado
#: sumiu sem avisar, em vez de esperar o sistema operacional desistir.
KEEPALIVE_KWARGS = {
    "keepalives": 1,
    "keepalives_idle": 5,
    "keepalives_interval": 2,
    "keepalives_count": 3,
}
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
    """Entrega uma conexao PostgreSQL/Supabase pronta para uso.

    Por padrao a conexao vem de um pool compartilhado e volta para ele no
    `close()`. Antes do pool, cada chamada abria uma conexao nova e a fechava no
    fim: o handshake com o pooler do Supabase custa cerca de 1 s, e cada
    requisicao ao `/api/chat` abre duas (recuperacao e rastreabilidade). Eram
    ~2 s por requisicao gastos so para conectar, medidos na execucao do RNF05.

    Quem chama continua usando o mesmo contrato — `cursor()`, `commit()`,
    `rollback()`, `close()` — e nao precisa saber se ha pool.

    `connect` explicito (os testes) e `DATABASE_POOL_ENABLED=0` mantem o
    comportamento antigo: conexao nova a cada chamada.
    """

    database_url = get_database_url()
    if connect is not None:
        return connect(database_url, connect_timeout=DEFAULT_CONNECT_TIMEOUT_SECONDS)
    if not _pool_enabled():
        connection = _connect_with_psycopg(database_url, **_connection_kwargs())
        _configurar_conexao(connection)
        return connection
    return _PooledConnection(_get_pool(database_url))


def _connection_kwargs() -> dict[str, object]:
    return {"connect_timeout": DEFAULT_CONNECT_TIMEOUT_SECONDS, **KEEPALIVE_KWARGS}


def _statement_timeout_ms() -> int:
    try:
        valor = int(os.getenv("DATABASE_STATEMENT_TIMEOUT_MS", DEFAULT_STATEMENT_TIMEOUT_MS))
    except ValueError:
        return DEFAULT_STATEMENT_TIMEOUT_MS
    return min(max(valor, 500), 60_000)


def _configurar_conexao(connection: Any) -> None:
    """Limita o tempo de cada consulta nesta sessao do banco.

    Sem limite, uma consulta presa segura a resposta ao usuario sem prazo. Na
    2a rodada do RNF05, uma gravacao da auditoria do RNF03 ficou presa e uma
    resposta levou mais de 60 s, embora o pipeline tivesse terminado. Com o
    limite, a consulta e cancelada pelo servidor e o erro segue o tratamento
    que ja existe em cada chamador.

    `SET` vale para a sessao inteira no *pooler* do Supabase em modo sessao,
    que e o da porta 5432 usada pelo projeto. O `commit` devolve a conexao sem
    transacao aberta, como o pool exige.
    """

    with connection.cursor() as cursor:
        cursor.execute(f"SET statement_timeout = {_statement_timeout_ms()}")
    connection.commit()


class _PooledConnection:
    """Conexao emprestada do pool que volta para ele no `close()`.

    Delega tudo a conexao real. O `close()` e o unico ponto diferente: em vez de
    encerrar a conexao, desfaz qualquer transacao pendente e a devolve.

    Desfazer antes de devolver preserva a semantica anterior. As leituras do RAG
    executam SELECT sem `commit()` e contavam com o `close()` para descartar a
    transacao implicita; uma conexao devolvida ainda dentro dela entraria suja
    na proxima requisicao.
    """

    def __init__(self, pool: Any) -> None:
        self._pool = pool
        self._connection = pool.getconn()
        self._devolvida = False

    def __getattr__(self, nome: str) -> Any:
        return getattr(self._connection, nome)

    def close(self) -> None:
        """Devolve a conexao ao pool sem nunca levantar excecao.

        `close()` e chamado de dentro do `finally` de quem usa a conexao. Se ele
        levantasse, a excecao substituiria o retorno ja calculado: uma leitura
        concluida com sucesso viraria erro so porque a conexao caiu depois. Por
        isso qualquer falha aqui e absorvida — uma conexao quebrada e descartada
        pelo proprio pool na devolucao, e o pool repoe outra.
        """

        if self._devolvida:
            return
        self._devolvida = True
        try:
            if _transacao_pendente(self._connection):
                self._connection.rollback()
        except Exception:
            pass
        try:
            self._pool.putconn(self._connection)
        except Exception:
            try:
                self._connection.close()
            except Exception:
                pass


_pool_lock = Lock()
_pool: Any = None
_pool_url: str | None = None


def _get_pool(database_url: str) -> Any:
    """Cria o pool na primeira chamada e o reaproveita nas seguintes."""

    global _pool, _pool_url
    with _pool_lock:
        if _pool is not None and _pool_url == database_url:
            return _pool
        if _pool is not None:
            _pool.close()
        try:
            from psycopg_pool import ConnectionPool
        except ImportError as error:
            raise DatabaseConfigurationError(
                "Instale as dependencias do backend antes de conectar ao banco."
            ) from error

        _pool = ConnectionPool(
            database_url,
            min_size=1,
            max_size=_pool_max_size(),
            timeout=DEFAULT_POOL_TIMEOUT_SECONDS,
            kwargs=_connection_kwargs(),
            configure=_configurar_conexao,
            # Confere a conexao antes de entrega-la. Custa uma ida e volta
            # (~140 ms) e evita entregar uma conexao que o pooler do Supabase ja
            # derrubou por ociosidade — o que viraria erro na requisicao do
            # usuario em vez de uma reconexao transparente.
            check=ConnectionPool.check_connection,
            open=True,
        )
        _pool_url = database_url
        return _pool


def close_database_pool() -> None:
    """Encerra o pool, se houver. Chamado no desligamento da aplicacao."""

    global _pool, _pool_url
    with _pool_lock:
        if _pool is not None:
            _pool.close()
        _pool = None
        _pool_url = None


def _pool_enabled() -> bool:
    return os.getenv("DATABASE_POOL_ENABLED", "1").strip() != "0"


def _pool_max_size() -> int:
    try:
        return min(max(int(os.getenv("DATABASE_POOL_MAX_SIZE", DEFAULT_POOL_MAX_SIZE)), 1), 20)
    except ValueError:
        return DEFAULT_POOL_MAX_SIZE


def _transacao_pendente(connection: Any) -> bool:
    info = getattr(connection, "info", None)
    status = getattr(info, "transaction_status", None)
    if status is None:
        return False
    # psycopg.pq.TransactionStatus: 0 IDLE, 1 ACTIVE, 2 INTRANS, 3 INERROR,
    # 4 UNKNOWN. So INTRANS e INERROR pedem rollback. ACTIVE e UNKNOWN indicam
    # conexao em estado anomalo, que o pool descarta sozinho na devolucao.
    return int(status) in (2, 3)


def _connect_with_psycopg(database_url: str, **kwargs: object) -> Any:
    try:
        import psycopg
    except ImportError as error:
        raise DatabaseConfigurationError(
            "Instale as dependencias do backend antes de conectar ao banco."
        ) from error

    return psycopg.connect(database_url, **kwargs)
