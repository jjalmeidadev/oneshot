"""Validador da massa sintética (RNF12, CT-RNF12-P/N, S5-32).

Confere se a massa versionada representa as seis categorias exigidas pelo
RNF12: projetos, subportfólios, marcos, riscos, indicadores e documentos.

A massa tem duas origens, e o validador lê as duas sem banco nem rede:

* **SQL de carga** (`src/database/sql`): dados estruturados do portfólio.
  Cada ``INSERT INTO`` é contado pelas linhas que produz: tuplas de
  ``VALUES`` ou ramos de ``SELECT ... UNION ALL``. Inserts dentro de CTEs
  (``WITH ... AS (INSERT ...)``) também são contados.
* **Listas simuladas do SharePoint** (`app/rag/data/sharepoint`): os
  documentos. A carga ``04_rag_synthetic_data.sql`` copia esses itens para
  ``project_artifacts`` e ``source_extracts``; por isso os documentos são
  contados nos JSONs, que são a fonte única dos extratos.

Uso, a partir de ``src/backend``::

    python -m scripts.validar_massa_sintetica
    python -m scripts.validar_massa_sintetica --saida relatorio.json

Retorna exit code 0 quando todas as categorias estão presentes e 1 quando
alguma falta. O relatório traz as contagens, as categorias ausentes e o
SHA-256 de cada arquivo lido, que identifica a versão da massa validada.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re
import sys

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parents[1]

#: Cargas que compõem a massa sintética do portfólio. As demais migrações
#: criam esquema, permissões ou infraestrutura e não fazem parte da massa.
SQL_PADRAO = (
    ROOT / "src/database/sql/02_initial_data.sql",
    ROOT / "src/database/sql/04_rag_synthetic_data.sql",
    ROOT / "src/database/sql/13_seed_portfolio_report_data.sql",
)
SHAREPOINT_PADRAO = BACKEND / "app/rag/data/sharepoint"

#: Categoria do RNF12 -> tabelas do modelo físico que a representam.
#: Indicadores: avanço físico/econômico planejado x realizado e indicadores
#: de medição dos benefícios (`measurement_indicator`).
CATEGORIAS_SQL: dict[str, tuple[str, ...]] = {
    "projetos": ("public.projects",),
    "subportfolios": ("public.subportfolios",),
    "marcos": ("public.project_deliverables_milestones",),
    "riscos": ("public.risk_issue_items",),
    "indicadores": ("public.project_progress_updates", "public.project_benefits"),
}
CATEGORIA_DOCUMENTOS = "documentos"
CATEGORIAS = (*CATEGORIAS_SQL, CATEGORIA_DOCUMENTOS)

_INSERT = re.compile(r"\bINSERT\s+INTO\s+([A-Za-z_][\w.]*)", re.IGNORECASE)
_PALAVRA = re.compile(r"[A-Za-z_]+")


@dataclass
class RelatorioMassa:
    contagens: dict[str, int]
    detalhes: dict[str, dict[str, int]]
    ausentes: list[str]
    arquivos: dict[str, str]
    erros: list[str] = field(default_factory=list)

    @property
    def aprovado(self) -> bool:
        return not self.ausentes and not self.erros

    def como_dict(self) -> dict:
        return {
            "aprovado": self.aprovado,
            "categorias_exigidas": list(CATEGORIAS),
            "contagens": self.contagens,
            "detalhes": self.detalhes,
            "ausentes": self.ausentes,
            "erros": self.erros,
            "versao_da_massa_sha256": self.arquivos,
        }


def mascarar_sql(texto: str) -> str:
    """Troca literais e comentários por espaços, preservando posições.

    Assim parênteses, ponto e vírgula e palavras-chave dentro de textos
    (``'Inicio da operacao (fase 1); ...'``) não confundem a contagem.
    """

    saida = list(texto)
    i, n = 0, len(texto)
    while i < n:
        c = texto[i]
        if c == "-" and texto.startswith("--", i):
            fim = texto.find("\n", i)
            fim = n if fim == -1 else fim
            saida[i:fim] = " " * (fim - i)
            i = fim
        elif c == "/" and texto.startswith("/*", i):
            fim = texto.find("*/", i + 2)
            fim = n if fim == -1 else fim + 2
            saida[i:fim] = " " * (fim - i)
            i = fim
        elif c == "'":
            j = i + 1
            while j < n:
                if texto[j] == "'" and j + 1 < n and texto[j + 1] == "'":
                    j += 2
                elif texto[j] == "'":
                    break
                else:
                    j += 1
            saida[i + 1 : j] = " " * (j - i - 1)
            i = j + 1
        elif c == "$":
            marca = re.match(r"\$[A-Za-z_]*\$", texto[i:])
            if marca:
                tag = marca.group(0)
                fim = texto.find(tag, i + len(tag))
                fim = n if fim == -1 else fim + len(tag)
                saida[i:fim] = " " * (fim - i)
                i = fim
            else:
                i += 1
        else:
            i += 1
    return "".join(saida)


def _profundidades(texto: str) -> list[int]:
    profundidade, resultado = 0, []
    for c in texto:
        if c == ")":
            profundidade -= 1
        resultado.append(profundidade)
        if c == "(":
            profundidade += 1
    return resultado


def _linhas_do_insert(mascarado: str, prof: list[int], inicio: int) -> int:
    """Conta as linhas produzidas pelo INSERT que começa em ``inicio``."""

    base = prof[inicio]
    i, n = inicio, len(mascarado)
    # Pula a lista de colunas, se houver.
    while i < n and mascarado[i] != "(" and mascarado[i] != ";":
        if _PALAVRA.match(mascarado, i) and mascarado[i : i + 6].upper() in ("VALUES", "SELECT"):
            break
        i += 1
    if i < n and mascarado[i] == "(":
        while i < n and not (mascarado[i] == ")" and prof[i] == base):
            i += 1
        i += 1

    corpo_inicio = i
    modo, linhas = None, 0
    while i < n:
        if mascarado[i] == ";" and prof[i] == base:
            break
        if prof[i] < base:  # fim do CTE que contém o INSERT
            break
        if prof[i] == base:
            palavra = _PALAVRA.match(mascarado, i)
            if palavra and (i == 0 or not mascarado[i - 1].isalnum()):
                token = palavra.group(0).upper()
                if modo is None and token in ("VALUES", "SELECT"):
                    modo, linhas = token, (0 if token == "VALUES" else 1)
                elif modo is not None and (
                    token == "RETURNING"
                    or (token == "ON" and re.match(r"ON\s+CONFLICT\b", mascarado[i:], re.IGNORECASE))
                ):
                    break
                elif modo == "SELECT" and token == "UNION":
                    linhas += 1
                i += len(palavra.group(0))
                continue
            if modo == "VALUES" and mascarado[i] == "(":
                linhas += 1
        i += 1
    if modo is None:
        raise ValueError(f"INSERT sem VALUES/SELECT na posição {corpo_inicio}")
    return linhas


def contar_inserts(texto_sql: str) -> dict[str, int]:
    """Linhas inseridas por tabela em um arquivo SQL."""

    mascarado = mascarar_sql(texto_sql)
    prof = _profundidades(mascarado)
    contagem: dict[str, int] = {}
    for achado in _INSERT.finditer(mascarado):
        tabela = achado.group(1).lower()
        if "." not in tabela:
            tabela = f"public.{tabela}"
        linhas = _linhas_do_insert(mascarado, prof, achado.end())
        contagem[tabela] = contagem.get(tabela, 0) + linhas
    return contagem


def contar_documentos(diretorio: Path) -> dict[str, int]:
    """Itens por lista simulada do SharePoint."""

    contagem: dict[str, int] = {}
    for arquivo in sorted(diretorio.glob("*.json")):
        conteudo = json.loads(arquivo.read_text(encoding="utf-8"))
        itens = conteudo.get("value")
        if not isinstance(itens, list):
            raise ValueError(f"{arquivo.name}: campo 'value' ausente ou inválido")
        lista = (conteudo.get("list") or {}).get("id") or arquivo.stem
        contagem[lista] = len(itens)
    return contagem


def _sha256(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def _relativo(caminho: Path) -> str:
    try:
        return caminho.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return caminho.name


def validar_massa(
    arquivos_sql: tuple[Path, ...] | list[Path] = SQL_PADRAO,
    diretorio_sharepoint: Path = SHAREPOINT_PADRAO,
) -> RelatorioMassa:
    erros: list[str] = []
    por_tabela: dict[str, int] = {}
    arquivos: dict[str, str] = {}

    for caminho in arquivos_sql:
        try:
            texto = Path(caminho).read_text(encoding="utf-8")
            for tabela, linhas in contar_inserts(texto).items():
                por_tabela[tabela] = por_tabela.get(tabela, 0) + linhas
            arquivos[_relativo(Path(caminho))] = _sha256(Path(caminho))
        except (OSError, ValueError) as erro:
            erros.append(f"{Path(caminho).name}: {erro}")

    try:
        documentos = contar_documentos(Path(diretorio_sharepoint))
        for arquivo in sorted(Path(diretorio_sharepoint).glob("*.json")):
            arquivos[_relativo(arquivo)] = _sha256(arquivo)
    except (OSError, ValueError) as erro:
        documentos = {}
        erros.append(f"SharePoint simulado: {erro}")

    detalhes = {
        categoria: {tabela: por_tabela.get(tabela, 0) for tabela in tabelas}
        for categoria, tabelas in CATEGORIAS_SQL.items()
    }
    detalhes[CATEGORIA_DOCUMENTOS] = documentos
    contagens = {categoria: sum(valores.values()) for categoria, valores in detalhes.items()}
    ausentes = [categoria for categoria in CATEGORIAS if contagens.get(categoria, 0) == 0]
    return RelatorioMassa(contagens, detalhes, ausentes, arquivos, erros)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida a completude da massa sintética (RNF12).")
    parser.add_argument("--sql", nargs="+", type=Path, help="Arquivos SQL da massa; padrão: cargas 02, 04 e 13.")
    parser.add_argument("--sharepoint", type=Path, default=SHAREPOINT_PADRAO, help="Diretório das listas simuladas.")
    parser.add_argument("--saida", type=Path, help="Grava o relatório JSON neste caminho.")
    args = parser.parse_args(argv)

    relatorio = validar_massa(tuple(args.sql) if args.sql else SQL_PADRAO, args.sharepoint)
    texto = json.dumps(relatorio.como_dict(), ensure_ascii=False, indent=2)
    if args.saida:
        args.saida.write_text(texto + "\n", encoding="utf-8")
    print(texto)
    return 0 if relatorio.aprovado else 1


if __name__ == "__main__":
    sys.exit(main())
