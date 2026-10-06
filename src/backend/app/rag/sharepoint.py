import json
import os
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import AbstractSet, TYPE_CHECKING

from app.nlp.schemas import AudioIntent
from app.rag.errors import RagSourceError

if TYPE_CHECKING:
    from app.rag.proactivity import SecondaryIntent


DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "data" / "sharepoint"
DEFAULT_RESULT_LIMIT = 3

_STOP_WORDS = {
    "a",
    "ao",
    "aos",
    "as",
    "com",
    "como",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "esta",
    "este",
    "eu",
    "o",
    "os",
    "para",
    "por",
    "qual",
    "que",
    "se",
    "um",
    "uma",
}

# Equivalencias pequenas e auditaveis do dominio metroviario. A normalizacao
# para um termo canonico melhora a recuperacao de parafrases sem depender da
# massa de avaliacao ou carregar um modelo adicional em tempo de execucao.
_DOMAIN_TOKEN_EQUIVALENTS = {
    "achei": "achado",
    "achados": "achado",
    "barreira": "catraca",
    "bike": "bicicleta",
    "comboio": "trem",
    "comboios": "trem",
    "entro": "acesso",
    "mochila": "objeto",
    "passe": "bilhete",
    "queixa": "reclamacao",
    "reclamacoes": "reclamacao",
    "saindo": "desembarque",
    "trens": "trem",
    "vagao": "trem",
}


#: Campos do extrato que ja aparecem em outra parte do bloco `[Fonte N]` e nao
#: devem ser repetidos como atributo.
_CAMPOS_JA_RENDERIZADOS = {"Title", "Conteudo", "Descricao", "Resumo", "PalavrasChave"}

#: Rotulos legiveis para os atributos vindos do banco. A chave e o nome tecnico
#: gravado em `source_extracts.metadata` por 04_rag_synthetic_data.sql.
_ROTULOS_DE_ATRIBUTO = {
    "status": "Status",
    "line": "Linha",
    "category": "Categoria",
    "validity": "Vigencia",
}


@dataclass(frozen=True)
class SharePointDocument:
    source_id: str
    title: str
    list_name: str
    content: str
    web_url: str
    last_modified: str
    search_text: str
    artifact_id: str | None = None
    extract_id: str | None = None
    project_id: str | None = None
    source_locator: str | None = None
    fallback: bool = True
    #: Atributos estruturados do extrato, como pares (rotulo, valor) ja prontos
    #: para o prompt. Vigencia, status, linha e categoria vivem fora do
    #: `content_text` e, ate a correcao do DEF-RNF04-01, eram recuperados do
    #: banco e descartados antes de chegar ao LLM: o agente devolvia a fonte
    #: certa e respondia "contexto insuficiente" sobre uma data que estava no
    #: registro recuperado. Tupla para preservar o dataclass congelado.
    attributes: tuple[tuple[str, str], ...] = ()
    registration_period: dict[str, str | None] | None = None
    validity: dict[str, str | None] | None = None
    project_code: str | None = None
    project_title: str | None = None


@dataclass(frozen=True)
class RetrievedDocument:
    document: SharePointDocument
    score: float


def attributes_from_fields(fields: dict) -> tuple[tuple[str, str], ...]:
    """Extrai atributos do item do SharePoint no formato bruto do JSON local.

    `ValidadeInicio` e `ValidadeFim` sao unidos em um unico rotulo `Vigencia`,
    porque duas datas soltas no prompt levam o modelo a trata-las como fatos
    independentes em vez de como um intervalo.
    """

    atributos: list[tuple[str, str]] = []
    inicio = str(fields.get("ValidadeInicio") or "").strip()
    fim = str(fields.get("ValidadeFim") or "").strip()
    if inicio or fim:
        atributos.append(("Vigencia", _intervalo(inicio, fim)))

    for nome, valor in fields.items():
        if nome in _CAMPOS_JA_RENDERIZADOS or nome in {"ValidadeInicio", "ValidadeFim"}:
            continue
        if not isinstance(valor, (str, int, float)):
            continue
        texto = str(valor).strip()
        if texto:
            atributos.append((nome, texto))
    return tuple(atributos)


def attributes_from_metadata(metadata: dict | None) -> tuple[tuple[str, str], ...]:
    """Extrai atributos do `source_extracts.metadata` gravado pelo banco."""

    if not isinstance(metadata, dict):
        return ()

    atributos: list[tuple[str, str]] = []
    vigencia = metadata.get("validity")
    if isinstance(vigencia, dict):
        intervalo = _intervalo(
            str(vigencia.get("start") or "").strip(),
            str(vigencia.get("end") or "").strip(),
        )
        if intervalo:
            atributos.append(("Vigencia", intervalo))

    for chave, rotulo in _ROTULOS_DE_ATRIBUTO.items():
        if chave == "validity":
            continue
        valor = metadata.get(chave)
        if isinstance(valor, (str, int, float)) and str(valor).strip():
            atributos.append((rotulo, str(valor).strip()))
    return tuple(atributos)


def _intervalo(inicio: str, fim: str) -> str:
    if inicio and fim:
        return f"de {inicio} a {fim}"
    if inicio:
        return f"a partir de {inicio}"
    if fim:
        return f"ate {fim}"
    return ""


def _blocos_de_atributo(document: SharePointDocument) -> list[str]:
    """Linhas de atributo do bloco `[Fonte N]`, ou lista vazia se nao houver."""

    return [f"{rotulo}: {valor}" for rotulo, valor in document.attributes]


def load_sharepoint_documents(
    data_dir: Path | None = None,
) -> list[SharePointDocument]:
    directory = data_dir or _configured_data_dir()
    documents: list[SharePointDocument] = []

    if not directory.is_dir():
        raise RagSourceError("A origem de dados deve ser um diretório existente.")

    files = sorted(directory.glob("*.json"))
    if not files:
        raise RagSourceError("A origem de dados não contém arquivos JSON.")

    for file_path in files:
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise RagSourceError("Não foi possível ler um JSON válido na origem de dados.") from error
        if (
            not isinstance(payload, dict)
            or not isinstance(payload.get("list", {}), dict)
            or not isinstance(payload.get("value"), list)
            or any(
                not isinstance(item, dict) or not isinstance(item.get("fields"), dict)
                for item in payload.get("value", [])
            )
        ):
            raise RagSourceError("Estrutura inválida: a origem deve conter uma lista value de itens com fields.")
        list_data = payload.get("list", {})
        list_id = str(list_data.get("id") or file_path.stem)
        list_name = str(list_data.get("displayName") or file_path.stem)

        for item in payload.get("value", []):
            fields = item.get("fields", {})
            item_id = str(item.get("id") or fields.get("id") or "sem-id")
            title = str(fields.get("Title") or f"Item {item_id}")
            content = str(
                fields.get("Conteudo")
                or fields.get("Descricao")
                or fields.get("Resumo")
                or ""
            )
            searchable_values = [
                str(value)
                for value in fields.values()
                if isinstance(value, (str, int, float))
            ]
            documents.append(
                SharePointDocument(
                    source_id=f"{list_id}:{item_id}",
                    title=title,
                    list_name=list_name,
                    content=content,
                    web_url=str(item.get("webUrl") or ""),
                    last_modified=str(item.get("lastModifiedDateTime") or ""),
                    search_text=" ".join(searchable_values),
                    attributes=attributes_from_fields(fields),
                    registration_period=item.get("registration_period"),
                    project_id=item.get("project_id"),
                    project_code=item.get("project_code"),
                    project_title=item.get("project_title"),
                    validity=(
                        {"start": fields.get("ValidadeInicio"), "end": fields.get("ValidadeFim")}
                        if fields.get("ValidadeInicio") or fields.get("ValidadeFim") else None
                    ),
                )
            )

    return documents


def retrieve_sharepoint_context(
    query: str,
    documents: list[SharePointDocument] | None = None,
    limit: int | None = None,
    allowed_project_ids: AbstractSet[str] | None = None,
) -> list[RetrievedDocument]:
    query_tokens = _semantic_tokens(query)
    if not query_tokens:
        return []

    candidates = documents if documents is not None else load_sharepoint_documents()
    if allowed_project_ids is not None:
        allowed = {str(value).casefold() for value in allowed_project_ids}
        candidates = [
            document
            for document in candidates
            # Documento sem projeto e institucional e vale para todos os perfis.
            if not document.project_id
            or document.project_id.casefold() in allowed
            or (document.project_code or "").casefold() in allowed
        ]
    scored: list[RetrievedDocument] = []

    for document in candidates:
        document_tokens = _semantic_tokens(document.search_text)
        matched_tokens = query_tokens & document_tokens
        if not matched_tokens:
            continue

        title_tokens = _semantic_tokens(document.title)
        title_matches = query_tokens & title_tokens
        if len(query_tokens) > 1 and len(matched_tokens) < 2 and not title_matches:
            continue

        coverage = len(matched_tokens) / len(query_tokens)
        score = len(matched_tokens) + (2 * len(title_matches)) + coverage
        scored.append(RetrievedDocument(document=document, score=round(score, 3)))

    result_limit = limit if limit is not None else _configured_result_limit()
    return sorted(
        scored,
        key=lambda result: (-result.score, result.document.source_id),
    )[:result_limit]


def build_rag_input(
    message: str,
    results: list[RetrievedDocument],
    *,
    intent: AudioIntent | None = None,
    secondary_intent: "SecondaryIntent | None" = None,
) -> str:
    if not results and intent is None:
        return message

    source_blocks = []
    for index, result in enumerate(results, start=1):
        document = result.document
        source_blocks.append(
            "\n".join(
                (
                    f"[Fonte {index}] {document.title}",
                    f"Lista: {document.list_name}",
                    f"Atualizado em: {document.last_modified}",
                    f"Periodo de registro: {json.dumps(document.registration_period, ensure_ascii=False)}",
                    *_blocos_de_atributo(document),
                    f"Conteudo: {document.content}",
                )
            )
        )

    context = "\n\n".join(source_blocks) or "Nenhuma fonte recuperada."
    routing = _compact_intent_context(intent)
    primary_prompt = (
        "Voce e um assistente do Metro em um ambiente de demonstracao. "
        "Os trechos abaixo vieram de listas simuladas do SharePoint e sao "
        "dados ficticios para o MVP. Use-os quando forem pertinentes, cite "
        "as fontes no formato [Fonte N] e informe quando o contexto nao for "
        "suficiente. Modo extrativo estrito: selecione somente os trechos que "
        "respondem a pergunta. Copie INTEGRALMENTE o Conteudo de uma fonte "
        "ou um atributo completo no formato Rotulo: valor, sem parafrasear, "
        "resumir, cortar frases ou mudar numeros. Preserve condicoes e negacoes. "
        "Escreva cada unidade copiada em uma unica linha, sempre terminando "
        "com suas citacoes [Fonte N]. Se nao houver unidade que responda, "
        "informe evidencia insuficiente. Nao inclua afirmacoes sem fonte nem "
        "cabecalhos sem citacao. Nao apresente esses dados como informacao operacional real.\n\n"
        f"{routing}\n\n"
        f"Contexto recuperado:\n{context}\n\n"
        f"Pergunta do usuario: {message}"
    )
    if secondary_intent is not None:
        primary_prompt += (
            "\n\nProatividade preparada na mesma inferencia: gere a resposta principal "
            "e tambem uma resposta secundaria que ficara oculta ate a confirmacao "
            "do usuario. A resposta secundaria deve apenas analisar ou recomendar; "
            "nao execute alteracoes externas. Na resposta secundaria, copie "
            "primeiro, no mesmo modo extrativo, as unidades das fontes que sustentam "
            "a analise, uma por linha e terminando com [Fonte N]; depois escreva uma "
            "unica linha iniciada por 'Sugestão:' com a acao recomendada, sem numeros, "
            "datas ou fatos ausentes das linhas copiadas. Responda somente com um objeto JSON "
            "valido, sem bloco Markdown, com as chaves primary_response e "
            "prepared_secondary_response.\n"
            f"Intencao secundaria: {secondary_intent.name}\n"
            f"Instrucao secundaria: {secondary_intent.rag_instruction}"
        )
    return primary_prompt


def _compact_intent_context(intent: AudioIntent | None) -> str:
    if intent is None:
        return "Roteamento: classificador desativado; interprete a pergunta diretamente."
    return (
        "Intencao primaria validada: "
        f"macro={intent.macro}; especifica={intent.specific or 'generica'}; "
        f"handler={intent.handler or 'rag'}"
    )


def _configured_data_dir() -> Path:
    configured = os.getenv("SHAREPOINT_MOCK_DATA_DIR", "").strip()
    return Path(configured) if configured else DEFAULT_DATA_DIR


def _configured_result_limit() -> int:
    raw_value = os.getenv("RAG_MAX_SOURCES", str(DEFAULT_RESULT_LIMIT))
    try:
        return min(max(int(raw_value), 1), 8)
    except ValueError:
        return DEFAULT_RESULT_LIMIT


def _meaningful_tokens(value: str) -> set[str]:
    return {
        token
        for token in _normalize(value).split()
        if len(token) >= 3 and token not in _STOP_WORDS
    }


def _semantic_tokens(value: str) -> set[str]:
    """Retorna tokens significativos reduzidos ao vocabulario do dominio."""

    return {
        _DOMAIN_TOKEN_EQUIVALENTS.get(token, token)
        for token in _meaningful_tokens(value)
    }


def _normalize(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore")
    return re.sub(r"[^a-z0-9]+", " ", ascii_value.decode().lower()).strip()
