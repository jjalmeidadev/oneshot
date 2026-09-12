"""Leitura da documentação e divisão em trechos.

Duas decisões moram aqui e valem ser explicadas.

**O corte é por cabeçalho, não por tamanho fixo.** A documentação do projeto é
markdown com hierarquia — `## 8.7 Contrato da API`, `### 8.7.6 Erros` — e essa
hierarquia já é a divisão semântica que um cortador cego por caracteres tentaria
adivinhar. Cortar por cabeçalho dá trechos que começam e terminam em fronteiras
de assunto, e de quebra dá a **citação de graça**: o caminho de cabeçalhos é
exatamente o que a resposta precisa mostrar como fonte. Seções longas ainda são
subdivididas, com sobreposição, para nenhum trecho estourar o limite do
embedding.

**O caminho de cabeçalhos entra no texto vetorizado.** Um trecho que diz apenas
"o limiar é 0,550" não casa com a pergunta "qual o limiar do classificador?".
Prefixado com `Projeto.md — Classificador de intenções > Limiares`, casa. É a
diferença entre recuperar por acaso e recuperar por assunto.

O carregador despacha por extensão desde já. Hoje só o ramo de markdown existe,
mas se algum documento final vier em PDF ou planilha, é uma função nova neste
arquivo — não uma reescrita do pipeline.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

#: Arquivos que não são documentação e não devem entrar no índice.
IGNORED_NAMES = {".gitkeep", ".DS_Store", "Thumbs.db"}
#: Pastas de apoio: imagens, diagramas e afins não têm texto a vetorizar.
IGNORED_DIRS = {"img", "images", "assets", "diagrams", ".git"}

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")


@dataclass(frozen=True)
class SourceDocument:
    """Um arquivo da documentação, já em texto."""

    name: str
    relative_path: str
    path: Path
    text: str


@dataclass(frozen=True)
class Chunk:
    """Um trecho indexável, com a procedência junto."""

    id: str
    document: str
    relative_path: str
    #: Caminho de cabeçalhos até o trecho, ex.: "Riscos > R08 — Tempo".
    section: str
    #: Âncora do cabeçalho mais fundo, para linkar direto na seção.
    anchor: str
    #: O texto como está no documento — é isto que a resposta cita.
    text: str
    #: O que de fato vai para o embedding: documento + seção + texto.
    embed_text: str
    order: int


# --- Carregamento ---------------------------------------------------------


def _load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


#: Despacho por extensão. Acrescentar PDF ou DOCX é acrescentar uma linha aqui
#: e a função correspondente — o resto do pipeline não muda.
LOADERS: dict[str, Callable[[Path], str]] = {
    ".md": _load_text_file,
    ".markdown": _load_text_file,
    ".txt": _load_text_file,
}


def load_documents(corpus_dir: Path) -> tuple[list[SourceDocument], list[str]]:
    """Lê a documentação. Devolve os documentos e o que foi ignorado."""

    if not corpus_dir.is_dir():
        raise FileNotFoundError(
            f"A pasta da documentação não existe: {corpus_dir}. "
            "Defina RAG_CORPUS_DIR se ela estiver em outro lugar."
        )

    documentos: list[SourceDocument] = []
    ignorados: list[str] = []

    for path in sorted(corpus_dir.rglob("*")):
        if not path.is_file():
            continue
        relativo = path.relative_to(corpus_dir)
        if any(parte in IGNORED_DIRS for parte in relativo.parts[:-1]):
            continue
        if path.name in IGNORED_NAMES or path.name.startswith("."):
            continue

        carregar = LOADERS.get(path.suffix.lower())
        if carregar is None:
            ignorados.append(relativo.as_posix())
            continue

        documentos.append(
            SourceDocument(
                name=path.name,
                relative_path=relativo.as_posix(),
                path=path,
                text=carregar(path),
            )
        )

    return documentos, ignorados


# --- Divisão em trechos ---------------------------------------------------


def slugify(title: str) -> str:
    """Âncora no estilo do GitHub, para o link cair direto na seção."""

    limpo = re.sub(r"[*_`]", "", title)
    limpo = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", limpo)  # [texto](link) -> texto
    limpo = unicodedata.normalize("NFC", limpo).strip().lower()
    limpo = re.sub(r"[^\w\s-]", "", limpo, flags=re.UNICODE)
    # Um hífen por espaço, e não por sequência de espaços: é assim que o
    # GitHub e o GitLab montam a âncora, então "A — B" vira "a--b". Colapsar
    # geraria um link que não existe na página renderizada.
    return re.sub(r"\s", "-", limpo).strip("-")


def clean_heading(title: str) -> str:
    limpo = re.sub(r"[*_`]", "", title)
    limpo = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", limpo)
    return limpo.strip()


def _split_long(text: str, max_chars: int, overlap: int) -> list[str]:
    """Quebra um bloco grande em pedaços, preferindo fronteiras de parágrafo."""

    if len(text) <= max_chars:
        return [text]

    pedacos: list[str] = []
    atual = ""
    for paragrafo in text.split("\n\n"):
        candidato = f"{atual}\n\n{paragrafo}" if atual else paragrafo

        if len(candidato) <= max_chars:
            atual = candidato
            continue

        if atual:
            pedacos.append(atual)
            # A sobreposição carrega o fim do pedaço anterior, para uma frase
            # cortada na fronteira ainda existir inteira em algum lugar.
            atual = (atual[-overlap:] + "\n\n" + paragrafo) if overlap else paragrafo
        else:
            atual = paragrafo

        # Parágrafo único maior que o teto: corta na força, sem escolha.
        while len(atual) > max_chars:
            pedacos.append(atual[:max_chars])
            atual = atual[max_chars - overlap :] if overlap else atual[max_chars:]

    if atual.strip():
        pedacos.append(atual)
    return pedacos


def chunk_document(
    document: SourceDocument,
    max_chunk_chars: int = 1800,
    chunk_overlap_chars: int = 200,
    min_chunk_chars: int = 60,
) -> list[Chunk]:
    """Divide um documento em trechos por cabeçalho.

    Seções praticamente vazias — um cabeçalho e nada abaixo — são descartadas:
    elas não respondem nada e só competiriam por lugar entre os recuperados.
    """

    trechos: list[Chunk] = []
    pilha: list[tuple[int, str]] = []
    buffer: list[str] = []
    em_bloco_de_codigo = False

    def caminho() -> str:
        return " > ".join(titulo for _, titulo in pilha)

    def fechar() -> None:
        corpo = "\n".join(buffer).strip()
        buffer.clear()
        if len(corpo) < min_chunk_chars:
            return

        secao = caminho() or document.name
        ancora = slugify(pilha[-1][1]) if pilha else ""
        for pedaco in _split_long(corpo, max_chunk_chars, chunk_overlap_chars):
            ordem = len(trechos)
            identificador = hashlib.sha1(
                f"{document.relative_path}|{secao}|{ordem}".encode("utf-8")
            ).hexdigest()[:12]
            trechos.append(
                Chunk(
                    id=identificador,
                    document=document.name,
                    relative_path=document.relative_path,
                    section=secao,
                    anchor=ancora,
                    text=pedaco.strip(),
                    # O cabeçalho entra no texto vetorizado: é o que faz o
                    # trecho casar com a pergunta pelo assunto, e não por acaso.
                    embed_text=f"{document.name} — {secao}\n\n{pedaco.strip()}",
                    order=ordem,
                )
            )

    for linha in document.text.splitlines():
        if FENCE.match(linha):
            em_bloco_de_codigo = not em_bloco_de_codigo
            buffer.append(linha)
            continue

        cabecalho = None if em_bloco_de_codigo else HEADING.match(linha)
        if cabecalho is None:
            buffer.append(linha)
            continue

        # Cabeçalho novo: fecha o que veio antes e reposiciona a hierarquia.
        fechar()
        nivel = len(cabecalho.group(1))
        titulo = clean_heading(cabecalho.group(2))
        while pilha and pilha[-1][0] >= nivel:
            pilha.pop()
        if titulo:
            pilha.append((nivel, titulo))

    fechar()
    return trechos


def build_chunks(
    corpus_dir: Path,
    max_chunk_chars: int = 1800,
    chunk_overlap_chars: int = 200,
) -> tuple[list[Chunk], list[SourceDocument], list[str]]:
    """Lê a documentação inteira e devolve os trechos prontos para vetorizar."""

    documentos, ignorados = load_documents(corpus_dir)
    trechos: list[Chunk] = []
    for documento in documentos:
        trechos.extend(
            chunk_document(documento, max_chunk_chars, chunk_overlap_chars)
        )
    return trechos, documentos, ignorados


def fingerprint(documents: list[SourceDocument]) -> str:
    """Impressão digital do corpus.

    É o que permite ao `--check` dizer se a documentação mudou desde a última
    indexação — a salvaguarda contra apresentar amanhã com índice velho.
    """

    resumo = hashlib.sha256()
    for documento in sorted(documents, key=lambda d: d.relative_path):
        resumo.update(documento.relative_path.encode("utf-8"))
        resumo.update(hashlib.sha256(documento.text.encode("utf-8")).digest())
    return resumo.hexdigest()[:16]
