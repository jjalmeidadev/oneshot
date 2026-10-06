"""Barreira de dado sensivel antes do provedor de LLM (S5-27, D-06, RNF01).

O RNF01 exige que nenhum dado marcado como sensivel chegue a servico externo
nao homologado. Ate a S5-27 isso era cumprido por convencao (a massa e
sintetica), nao por controle: o CT-RNF01-N mostrou um marcador sensivel
atravessando a montagem do prompt.

Este modulo concentra os padroes acordados pelo grupo e as tres operacoes que
o caminho textual usa:

- ``scan``: encontra e mascara os padroes num texto;
- ``protect_documents``: mascara os documentos recuperados pelo RAG e retira
  os classificados como restritos ou confidenciais;
- ``SensitiveDataReport``: resumo para a auditoria, com etapa, categorias e
  contagens. Nunca carrega o valor encontrado.

Os padroes priorizam precisao: CPF, CNPJ e cartao so contam com digito
verificador valido, telefone exige DDD e hifen, e os rotulos de classificacao
so contam em maiusculas ou na forma "Classificacao: X", para nao barrar texto
operacional como "acesso restrito a via".
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - apenas para tipagem
    from app.rag.sharepoint import RetrievedDocument


# --------------------------------------------------------------------------
# Padroes acordados
# --------------------------------------------------------------------------

#: Niveis de `project_artifacts.confidentiality_level` que nunca saem para o
#: provedor. `publico` e `interno` seguem, com o conteudo mascarado.
CLASSIFIED_LEVELS = frozenset({"restrito", "confidencial"})

#: Rotulos legiveis de cada categoria, usados na mensagem ao usuario.
CATEGORY_LABELS = {
    "marcador_classificacao": "marcador de classificação",
    "cpf": "CPF",
    "cnpj": "CNPJ",
    "email": "e-mail",
    "telefone": "telefone",
    "cartao": "número de cartão",
    "credencial": "credencial de acesso",
}

#: Texto que substitui o dado no prompt, na fonte exibida e na auditoria.
PLACEHOLDERS = {
    "marcador_classificacao": "[DADO CLASSIFICADO]",
    "cpf": "[CPF]",
    "cnpj": "[CNPJ]",
    "email": "[E-MAIL]",
    "telefone": "[TELEFONE]",
    "cartao": "[CARTÃO]",
    "credencial": "[CREDENCIAL]",
}


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value)


def _valid_cpf(value: str) -> bool:
    digits = _digits(value)
    if len(digits) != 11 or digits == digits[0] * 11:
        return False
    for size in (9, 10):
        total = sum(int(digit) * weight for digit, weight in zip(digits, range(size + 1, 1, -1)))
        check = (total * 10) % 11 % 10
        if check != int(digits[size]):
            return False
    return True


def _valid_cnpj(value: str) -> bool:
    digits = _digits(value)
    if len(digits) != 14 or digits == digits[0] * 14:
        return False
    for size, weights in (
        (12, (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)),
        (13, (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)),
    ):
        total = sum(int(digit) * weight for digit, weight in zip(digits, weights))
        remainder = total % 11
        check = 0 if remainder < 2 else 11 - remainder
        if check != int(digits[size]):
            return False
    return True


def _valid_card(value: str) -> bool:
    digits = _digits(value)
    if not 13 <= len(digits) <= 19 or digits == digits[0] * len(digits):
        return False
    total = 0
    for index, digit in enumerate(reversed(digits)):
        number = int(digit)
        if index % 2 == 1:
            number *= 2
            if number > 9:
                number -= 9
        total += number
    return total % 10 == 0


@dataclass(frozen=True)
class SensitivePattern:
    category: str
    regex: re.Pattern[str]
    validator: Callable[[str], bool] | None = None

    def matches(self, text: str) -> Iterable[re.Match[str]]:
        for match in self.regex.finditer(text):
            if self.validator is None or self.validator(match.group(0)):
                yield match


#: Ordem importa so para desempate: em sobreposicao vence o trecho mais longo
#: e, no empate, o padrao que aparece primeiro.
PATTERNS: tuple[SensitivePattern, ...] = (
    # Rotulo explicito de dado sensivel, inclusive o marcador do CT-RNF01-N.
    SensitivePattern(
        "marcador_classificacao",
        re.compile(r"\bDADOS?[-_ ]SENS[IÍ]VE(?:L|IS)\b[\w-]*", re.IGNORECASE),
    ),
    # Rotulos de classificacao em maiusculas, como aparecem em cabecalhos.
    SensitivePattern(
        "marcador_classificacao",
        re.compile(r"\b(?:CONFIDENCIAL|SIGILOSO|SIGILOSA|RESTRITO|RESTRITA)\b"),
    ),
    # "Classificacao: confidencial", em qualquer caixa.
    SensitivePattern(
        "marcador_classificacao",
        re.compile(
            r"\bclassifica[cç][aã]o\s*:\s*(?:confidencial|sigilos[oa]|restrit[oa])\b",
            re.IGNORECASE,
        ),
    ),
    SensitivePattern(
        "credencial",
        re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    ),
    SensitivePattern(
        "credencial",
        re.compile(r"\bsk-(?:or-v1-|proj-|ant-)?[A-Za-z0-9_-]{20,}"),
    ),
    SensitivePattern(
        "credencial",
        re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
    ),
    SensitivePattern(
        "credencial",
        re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{16,}=*", re.IGNORECASE),
    ),
    SensitivePattern(
        "credencial",
        re.compile(
            r"\b(?:senha|password|passwd|api[_-]?key|token|secret)\s*[:=]\s*\S{4,}",
            re.IGNORECASE,
        ),
    ),
    SensitivePattern(
        "email",
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    ),
    SensitivePattern(
        "cnpj",
        re.compile(r"(?<![\w.])\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}(?![\w])"),
        _valid_cnpj,
    ),
    SensitivePattern(
        "cpf",
        re.compile(r"(?<![\w.])\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?![\w])"),
        _valid_cpf,
    ),
    SensitivePattern(
        "cartao",
        re.compile(r"(?<![\w])\d{4}(?:[ -]?\d{4}){2}[ -]?\d{1,7}(?![\w])"),
        _valid_card,
    ),
    SensitivePattern(
        "telefone",
        re.compile(r"(?<![\w])(?:\+55\s?)?(?:\(\d{2}\)|\d{2})\s?9?\d{4}-\d{4}(?![\w])"),
    ),
)


# --------------------------------------------------------------------------
# Varredura de texto
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ScanResult:
    """Texto mascarado e contagem por categoria. Nao guarda o dado original."""

    masked: str
    counts: dict[str, int] = field(default_factory=dict)

    @property
    def found(self) -> bool:
        return bool(self.counts)

    @property
    def categories(self) -> list[str]:
        return sorted(self.counts)


def scan(text: str | None) -> ScanResult:
    """Encontra os padroes e devolve o texto com cada ocorrencia substituida."""

    if not text:
        return ScanResult(masked=text or "")

    spans: list[tuple[int, int, str, int]] = []
    for priority, pattern in enumerate(PATTERNS):
        for match in pattern.matches(text):
            spans.append((match.start(), match.end(), pattern.category, priority))

    if not spans:
        return ScanResult(masked=text)

    # Resolve sobreposicoes: trecho mais longo primeiro, depois prioridade.
    spans.sort(key=lambda span: (span[0] - span[1], span[3], span[0]))
    chosen: list[tuple[int, int, str]] = []
    for start, end, category, _priority in spans:
        if all(end <= other_start or start >= other_end for other_start, other_end, _ in chosen):
            chosen.append((start, end, category))
    chosen.sort()

    pieces: list[str] = []
    cursor = 0
    counts: Counter[str] = Counter()
    for start, end, category in chosen:
        pieces.append(text[cursor:start])
        pieces.append(PLACEHOLDERS[category])
        counts[category] += 1
        cursor = end
    pieces.append(text[cursor:])
    return ScanResult(masked="".join(pieces), counts=dict(counts))


def describe_categories(categories: Iterable[str]) -> str:
    """Lista legivel das categorias, como "CPF e e-mail", para o usuario."""

    labels = [CATEGORY_LABELS.get(category, category) for category in sorted(set(categories))]
    if len(labels) <= 1:
        return "".join(labels)
    return f"{', '.join(labels[:-1])} e {labels[-1]}"


# --------------------------------------------------------------------------
# Relatorio para auditoria
# --------------------------------------------------------------------------


@dataclass
class SensitiveDataReport:
    """O que a barreira fez numa requisicao, sem nenhum valor encontrado.

    ``stage`` indica onde o dado apareceu: ``mensagem`` (pergunta bloqueada),
    ``documentos`` (contexto mascarado ou retido) ou ``prompt`` (guarda final).
    """

    stage: str
    action: str
    counts: dict[str, int] = field(default_factory=dict)
    masked_sources: list[str] = field(default_factory=list)
    withheld_sources: list[str] = field(default_factory=list)

    @property
    def triggered(self) -> bool:
        return bool(self.counts or self.masked_sources or self.withheld_sources)

    def audit_payload(self) -> dict:
        return {
            "rnf": "RNF01",
            "stage": self.stage,
            "action": self.action,
            "categories": sorted(self.counts),
            "occurrences": dict(sorted(self.counts.items())),
            "masked_source_ids": list(self.masked_sources),
            "withheld_source_ids": list(self.withheld_sources),
        }


# --------------------------------------------------------------------------
# Documentos do RAG
# --------------------------------------------------------------------------


def protect_documents(
    results: list["RetrievedDocument"],
) -> tuple[list["RetrievedDocument"], SensitiveDataReport]:
    """Mascara os documentos e retira os classificados como restritos.

    O mascaramento vale para tudo que vai ao prompt e a fonte exibida: titulo,
    conteudo, atributos e nome do projeto. Um documento classificado como
    restrito ou confidencial nao tem o que mascarar e fica fora do contexto.
    """

    protected: list["RetrievedDocument"] = []
    counts: Counter[str] = Counter()
    masked_sources: list[str] = []
    withheld_sources: list[str] = []

    for result in results:
        document = result.document
        level = (getattr(document, "confidentiality_level", None) or "").strip().lower()
        if level in CLASSIFIED_LEVELS:
            withheld_sources.append(document.source_id)
            counts["marcador_classificacao"] += 1
            continue

        title = scan(document.title)
        content = scan(document.content)
        project_title = scan(document.project_title)
        attributes = [(label, scan(value)) for label, value in document.attributes]

        document_counts: Counter[str] = Counter()
        for item in (title, content, project_title, *(value for _label, value in attributes)):
            document_counts.update(item.counts)

        if document_counts:
            counts.update(document_counts)
            masked_sources.append(document.source_id)
            document = replace(
                document,
                title=title.masked,
                content=content.masked,
                search_text=content.masked,
                project_title=project_title.masked if document.project_title else None,
                attributes=tuple((label, value.masked) for label, value in attributes),
            )
            result = replace(result, document=document)
        protected.append(result)

    report = SensitiveDataReport(
        stage="documentos",
        action="mascarado" if protected or not withheld_sources else "bloqueado",
        counts=dict(counts),
        masked_sources=masked_sources,
        withheld_sources=withheld_sources,
    )
    return protected, report
