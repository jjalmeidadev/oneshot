"""Pool de conexoes com o Supabase.

Antes do pool, cada chamada a `open_database_connection` abria uma conexao nova
e a fechava no fim. O handshake com o pooler do Supabase custa cerca de 1 s e
cada requisicao ao `/api/chat` abre duas — recuperacao e rastreabilidade —, o
que somava ~2 s por requisicao so para conectar. Medido na execucao do RNF05.

Estes testes usam um pool falso: o que se verifica e o contrato com quem chama,
nao o psycopg_pool em si.
"""

import pytest

from app.database import connection as modulo
from app.database.connection import _PooledConnection, open_database_connection


class Status:
    """Imita `connection.info.transaction_status` do psycopg."""

    IDLE = 0
    ACTIVE = 1
    INTRANS = 2
    INERROR = 3
    UNKNOWN = 4


class InfoFalsa:
    def __init__(self, status: int) -> None:
        self.transaction_status = status


class ConexaoFalsa:
    def __init__(self, status: int = Status.IDLE, rollback_falha: bool = False) -> None:
        self.info = InfoFalsa(status)
        self.rollback_falha = rollback_falha
        self.rollbacks = 0
        self.fechada = False

    def cursor(self):
        return "cursor-real"

    def commit(self):
        return "commit-real"

    def rollback(self):
        self.rollbacks += 1
        if self.rollback_falha:
            raise RuntimeError("conexao caiu")
        self.info.transaction_status = Status.IDLE

    def close(self):
        self.fechada = True


class PoolFalso:
    def __init__(self, conexao: ConexaoFalsa, putconn_falha: bool = False) -> None:
        self.conexao = conexao
        self.putconn_falha = putconn_falha
        self.emprestadas = 0
        self.devolvidas = []

    def getconn(self):
        self.emprestadas += 1
        return self.conexao

    def putconn(self, conexao):
        if self.putconn_falha:
            raise RuntimeError("pool fechado")
        self.devolvidas.append(conexao)


#: Marcado pela #228 (S4-32B): este arquivo cruza fronteira entre
#: componentes (API, modelo, banco ou servico externo). Rodar so estes com
#: `pytest -m integration`.
pytestmark = pytest.mark.integration


class TestConexaoEmprestada:
    def test_delega_a_conexao_real(self):
        emprestada = _PooledConnection(PoolFalso(ConexaoFalsa()))

        assert emprestada.cursor() == "cursor-real"
        assert emprestada.commit() == "commit-real"

    def test_close_devolve_ao_pool_em_vez_de_encerrar(self):
        conexao = ConexaoFalsa()
        pool = PoolFalso(conexao)

        _PooledConnection(pool).close()

        assert pool.devolvidas == [conexao]
        assert conexao.fechada is False

    def test_close_duas_vezes_devolve_uma_so(self):
        """Uma conexao devolvida duas vezes seria entregue a dois donos."""

        pool = PoolFalso(ConexaoFalsa())
        emprestada = _PooledConnection(pool)

        emprestada.close()
        emprestada.close()

        assert len(pool.devolvidas) == 1

    @pytest.mark.parametrize("status", [Status.INTRANS, Status.INERROR])
    def test_transacao_pendente_e_desfeita_antes_de_devolver(self, status):
        """As leituras do RAG deixam transacao implicita aberta.

        Antes, o `close()` real a descartava. Devolvida suja, ela contaminaria a
        proxima requisicao que recebesse a mesma conexao.
        """

        conexao = ConexaoFalsa(status=status)

        _PooledConnection(PoolFalso(conexao)).close()

        assert conexao.rollbacks == 1

    @pytest.mark.parametrize("status", [Status.IDLE, Status.ACTIVE, Status.UNKNOWN])
    def test_sem_transacao_pendente_nao_ha_rollback(self, status):
        conexao = ConexaoFalsa(status=status)

        _PooledConnection(PoolFalso(conexao)).close()

        assert conexao.rollbacks == 0

    def test_close_nunca_levanta_quando_o_rollback_falha(self):
        """O teste mais importante do arquivo.

        `close()` roda no `finally` de quem usa a conexao. Se levantasse, a
        excecao substituiria o retorno ja calculado: uma leitura que deu certo
        viraria erro para o usuario so porque a conexao caiu depois.
        """

        conexao = ConexaoFalsa(status=Status.INTRANS, rollback_falha=True)
        pool = PoolFalso(conexao)

        _PooledConnection(pool).close()

        assert pool.devolvidas == [conexao]

    def test_close_nunca_levanta_quando_o_pool_recusa_a_devolucao(self):
        conexao = ConexaoFalsa()

        _PooledConnection(PoolFalso(conexao, putconn_falha=True)).close()

        assert conexao.fechada is True

    def test_resultado_calculado_sobrevive_a_falha_no_close(self):
        """Reproduz o padrao real de uso: return dentro de try/finally."""

        conexao = ConexaoFalsa(status=Status.INTRANS, rollback_falha=True)

        def leitura_do_rag():
            emprestada = _PooledConnection(PoolFalso(conexao))
            try:
                return ["extrato recuperado"]
            finally:
                emprestada.close()

        assert leitura_do_rag() == ["extrato recuperado"]


class TestSelecaoDoCaminho:
    def test_connect_explicito_ignora_o_pool(self, monkeypatch):
        """Os testes existentes injetam `connect` e nao podem passar pelo pool."""

        monkeypatch.setenv("DATABASE_URL", "postgresql://u:s@exemplo/postgres")
        monkeypatch.setenv("DATABASE_POOL_ENABLED", "1")
        monkeypatch.setattr(
            modulo, "_get_pool", lambda _url: pytest.fail("nao deveria usar o pool")
        )
        chamadas = []

        open_database_connection(connect=lambda url, **kw: chamadas.append(url) or "conexao")

        assert chamadas == ["postgresql://u:s@exemplo/postgres"]

    def test_pool_ligado_por_padrao(self, monkeypatch):
        monkeypatch.delenv("DATABASE_POOL_ENABLED", raising=False)

        assert modulo._pool_enabled() is True

    def test_pool_pode_ser_desligado(self, monkeypatch):
        monkeypatch.setenv("DATABASE_POOL_ENABLED", "0")

        assert modulo._pool_enabled() is False

    def test_pool_ligado_empresta_conexao(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql://u:s@exemplo/postgres")
        monkeypatch.setenv("DATABASE_POOL_ENABLED", "1")
        pool = PoolFalso(ConexaoFalsa())
        monkeypatch.setattr(modulo, "_get_pool", lambda _url: pool)

        conexao = open_database_connection()

        assert isinstance(conexao, _PooledConnection)
        assert pool.emprestadas == 1

    @pytest.mark.parametrize(
        ("valor", "esperado"),
        [("8", 8), ("0", 1), ("99", 20), ("abc", 5)],
    )
    def test_tamanho_do_pool_e_limitado(self, monkeypatch, valor, esperado):
        monkeypatch.setenv("DATABASE_POOL_MAX_SIZE", valor)

        assert modulo._pool_max_size() == esperado


class CursorQueRegistra:
    def __init__(self, destino: list) -> None:
        self.destino = destino

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def execute(self, consulta: str) -> None:
        self.destino.append(consulta)


class ConexaoQueRegistra:
    def __init__(self) -> None:
        self.consultas: list[str] = []
        self.commits = 0

    def cursor(self):
        return CursorQueRegistra(self.consultas)

    def commit(self) -> None:
        self.commits += 1


class TestLimiteDeTempoDasConsultas:
    """Correcao 1 do DEF-RNF05-02.

    Na 2a rodada do RNF05, uma gravacao da auditoria ficou presa no banco e uma
    resposta levou mais de 60 s. Nenhuma consulta tinha limite de tempo.
    """

    def test_configuracao_aplica_o_limite_e_fecha_a_transacao(self):
        conexao = ConexaoQueRegistra()

        modulo._configurar_conexao(conexao)

        assert conexao.consultas == ["SET statement_timeout = 5000"]
        assert conexao.commits == 1

    @pytest.mark.parametrize(
        ("valor", "esperado"),
        [("8000", 8000), ("100", 500), ("999999", 60_000), ("abc", 5_000)],
    )
    def test_limite_configuravel_e_contido(self, monkeypatch, valor, esperado):
        monkeypatch.setenv("DATABASE_STATEMENT_TIMEOUT_MS", valor)

        assert modulo._statement_timeout_ms() == esperado

    def test_parametros_de_conexao_incluem_keepalive(self):
        parametros = modulo._connection_kwargs()

        assert parametros["connect_timeout"] == modulo.DEFAULT_CONNECT_TIMEOUT_SECONDS
        assert parametros["keepalives"] == 1
        assert parametros["keepalives_idle"] == 5

    def test_conexao_sem_pool_recebe_keepalive_e_limite(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql://u:s@exemplo/postgres")
        monkeypatch.setenv("DATABASE_POOL_ENABLED", "0")
        conexao = ConexaoQueRegistra()
        recebido = {}

        def conectar(url, **kwargs):
            recebido.update(kwargs)
            return conexao

        monkeypatch.setattr(modulo, "_connect_with_psycopg", conectar)

        modulo.open_database_connection()

        assert recebido["keepalives"] == 1
        assert conexao.consultas == ["SET statement_timeout = 5000"]

    def test_pool_configura_cada_conexao_nova(self, monkeypatch):
        capturado = {}

        class PoolFalso:
            @staticmethod
            def check_connection(_conexao):
                return None

            def __init__(self, url, **kwargs):
                capturado.update(kwargs)

            def close(self):
                return None

        import psycopg_pool

        monkeypatch.setattr(psycopg_pool, "ConnectionPool", PoolFalso)
        monkeypatch.setattr(modulo, "_pool", None)
        monkeypatch.setattr(modulo, "_pool_url", None)

        modulo._get_pool("postgresql://u:s@exemplo/postgres")

        assert capturado["configure"] is modulo._configurar_conexao
        assert capturado["kwargs"]["keepalives"] == 1

    def test_connect_injetado_nao_recebe_configuracao(self, monkeypatch):
        """Os duplos dos testes existentes nao executam SET."""

        monkeypatch.setenv("DATABASE_URL", "postgresql://u:s@exemplo/postgres")
        conexao = ConexaoQueRegistra()

        modulo.open_database_connection(connect=lambda url, **kw: conexao)

        assert conexao.consultas == []
