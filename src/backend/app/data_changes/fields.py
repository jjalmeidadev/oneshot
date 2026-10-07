"""Campos editaveis pelo chat e suas regras de validacao (S5-05, Secao 8.5.13).

Este modulo e a tabela de campos do contrato em forma de codigo. Cada campo
diz em que tabela e coluna mora, como o valor e lido a partir do texto, como e
validado contra o registro atual e como aparece na previa. Nenhuma outra
coluna pode ser alterada pelo chat.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, Literal

from app.security.sensitive_data import scan

EntityKey = Literal["projeto", "cronograma", "marco", "risco"]
FieldKind = Literal["status", "date", "percent", "text"]

#: Limites de "data valida" do contrato.
MIN_DATE = date(2020, 1, 1)
MAX_DATE = date(2036, 12, 31)

#: Status de projeto que o chat nao aceita: encerrar ou descontinuar segue o
#: processo formal do PMO.
PROJECT_CLOSING_STATUSES = frozenset({"concluido", "descontinuado"})


class InvalidValueError(ValueError):
    """Valor que viola a regra do campo. A mensagem vai para o usuario."""


@dataclass(frozen=True)
class EntitySpec:
    key: EntityKey
    table: str
    #: Nome usado nas mensagens ("o risco", "a atividade").
    noun: str
    article: str
    #: Expressao SQL do rotulo exibido para o registro.
    label_sql: str
    #: Colunas lidas para validar e montar a previa.
    columns: tuple[str, ...]
    #: Coluna que liga o registro ao projeto.
    project_column: str = "project_id"
    #: Filtro adicional para que so registros de projeto sejam editaveis.
    extra_where: str = ""


ENTITIES: dict[str, EntitySpec] = {
    "projeto": EntitySpec(
        key="projeto",
        table="projects",
        noun="projeto",
        article="o",
        label_sql="code",
        columns=("status", "planned_end_date", "start_date"),
        project_column="id",
    ),
    "cronograma": EntitySpec(
        key="cronograma",
        table="schedule_items",
        noun="atividade",
        article="a",
        label_sql="activity_name",
        columns=("planned_end_date", "status", "progress_percent", "planned_start_date"),
    ),
    "marco": EntitySpec(
        key="marco",
        table="project_deliverables_milestones",
        noun="marco",
        article="o",
        label_sql="description",
        columns=("planned_date", "status", "completed_date"),
    ),
    "risco": EntitySpec(
        key="risco",
        table="risk_issue_items",
        noun="risco",
        article="o",
        label_sql="COALESCE(title, item, left(risk_or_issue_text, 120))",
        columns=("status", "owner_name", "due_date", "item_type"),
        extra_where="scope_type = 'projeto'",
    ),
}


@dataclass(frozen=True)
class FieldSpec:
    key: str
    entity: EntityKey
    column: str
    label: str
    kind: FieldKind
    change_type: str
    allowed: tuple[str, ...] = field(default_factory=tuple)
    #: Data prevista: aceita no passado, mas com aviso.
    planned_date: bool = False

    @property
    def entity_spec(self) -> EntitySpec:
        return ENTITIES[self.entity]


FIELDS: dict[str, FieldSpec] = {
    spec.key: spec
    for spec in (
        FieldSpec(
            "projeto.status", "projeto", "status", "Status do projeto", "status", "outro",
            allowed=("planejado", "em_andamento", "atencao", "critico", "suspenso"),
        ),
        FieldSpec(
            "projeto.prazo_final", "projeto", "planned_end_date", "Prazo final previsto",
            "date", "prazo", planned_date=True,
        ),
        FieldSpec(
            "cronograma.prazo", "cronograma", "planned_end_date", "Prazo da atividade",
            "date", "prazo", planned_date=True,
        ),
        FieldSpec(
            "cronograma.status", "cronograma", "status", "Status da atividade", "status", "outro",
            allowed=("planejado", "em_andamento", "atrasado", "concluido", "cancelado", "bloqueado"),
        ),
        FieldSpec(
            "cronograma.progresso", "cronograma", "progress_percent", "Progresso da atividade",
            "percent", "outro",
        ),
        FieldSpec(
            "marco.data_prevista", "marco", "planned_date", "Data prevista do marco",
            "date", "prazo", planned_date=True,
        ),
        FieldSpec(
            "marco.status", "marco", "status", "Status do marco", "status", "outro",
            allowed=("planejado", "em_andamento", "atrasado", "concluido", "cancelado"),
        ),
        FieldSpec(
            "marco.data_conclusao", "marco", "completed_date", "Data de conclusão do marco",
            "date", "prazo",
        ),
        FieldSpec(
            "risco.status", "risco", "status", "Status do risco", "status", "outro",
            allowed=("aberto", "em_tratamento", "mitigado", "resolvido", "aceito", "cancelado"),
        ),
        FieldSpec(
            "risco.responsavel", "risco", "owner_name", "Responsável pelo risco", "text",
            "responsavel",
        ),
        FieldSpec(
            "risco.prazo", "risco", "due_date", "Prazo do risco", "date", "prazo",
            planned_date=True,
        ),
    )
}

STATUS_LABELS = {
    "planejado": "planejado",
    "em_andamento": "em andamento",
    "atencao": "atenção",
    "critico": "crítico",
    "suspenso": "suspenso",
    "concluido": "concluído",
    "descontinuado": "descontinuado",
    "atrasado": "atrasado",
    "cancelado": "cancelado",
    "bloqueado": "bloqueado",
    "aberto": "aberto",
    "em_tratamento": "em tratamento",
    "mitigado": "mitigado",
    "resolvido": "resolvido",
    "aceito": "aceito",
}

#: Sinonimos aceitos no texto, ja sem acento e em minusculas.
STATUS_SYNONYMS = {
    "planejado": "planejado",
    "planejada": "planejado",
    "em andamento": "em_andamento",
    "andamento": "em_andamento",
    "em execucao": "em_andamento",
    "em curso": "em_andamento",
    "iniciado": "em_andamento",
    "iniciada": "em_andamento",
    "em atencao": "atencao",
    "atencao": "atencao",
    "critico": "critico",
    "critica": "critico",
    "suspenso": "suspenso",
    "suspensa": "suspenso",
    "pausado": "suspenso",
    "pausada": "suspenso",
    "paralisado": "suspenso",
    "paralisada": "suspenso",
    "concluido": "concluido",
    "concluida": "concluido",
    "finalizado": "concluido",
    "finalizada": "concluido",
    "encerrado": "concluido",
    "encerrada": "concluido",
    "entregue": "concluido",
    "descontinuado": "descontinuado",
    "descontinuada": "descontinuado",
    "atrasado": "atrasado",
    "atrasada": "atrasado",
    "cancelado": "cancelado",
    "cancelada": "cancelado",
    "bloqueado": "bloqueado",
    "bloqueada": "bloqueado",
    "aberto": "aberto",
    "aberta": "aberto",
    "reaberto": "aberto",
    "reaberta": "aberto",
    "em tratamento": "em_tratamento",
    "tratamento": "em_tratamento",
    "mitigado": "mitigado",
    "mitigada": "mitigado",
    "resolvido": "resolvido",
    "resolvida": "resolvido",
    "aceito": "aceito",
    "aceita": "aceito",
}
_STATUS_PATTERN = re.compile(
    r"\b(" + "|".join(
        re.escape(term) for term in sorted(
            {*STATUS_SYNONYMS, *(code.replace("_", " ") for code in STATUS_LABELS), *STATUS_LABELS},
            key=len,
            reverse=True,
        )
    ) + r")\b"
)

MONTHS = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}
_MONTH_NAMES = "|".join(MONTHS)
#: Padroes de data, aplicados ao texto sem acento e em minusculas.
#: Os limites `(?<![\d/])` e `(?![\d/])` impedem casar so parte de um numero:
#: "31/03/20277" nao pode virar "31/03" sem ano (#260, revisao do MR).
DATE_PATTERNS = (
    re.compile(r"(?<![\d/-])(\d{4})-(\d{2})-(\d{2})(?![\d/-])"),
    re.compile(r"(?<![\d/])(\d{1,2})/(\d{1,2})(?:/(\d{4}|\d{2}))?(?![\d/])"),
    re.compile(
        rf"(?<!\d)(\d{{1,2}})(?:o|º)?\s+de\s+({_MONTH_NAMES})(?:\s+de\s+(\d{{4}}))?"
        r"(?!\d)(?!\s+de\s+\d)"
    ),
)
#: Mes sem dia ("ate marco de 2027"): o chat pergunta pelo dia.
MONTH_ONLY_PATTERN = re.compile(
    rf"\b(?:em|ate|para|pra)\s+({_MONTH_NAMES})(?:\s+de\s+(\d{{4}}))?(?!\d)(?!\s+de\s+\d)"
)
#: Dia e mes por extenso, mesmo com ano invalido ("31 de marco de 20277").
#: Mascarado antes de procurar o tipo de registro, para que o mes "marco" nunca
#: seja lido como marco do projeto.
MONTH_MENTION_PATTERN = re.compile(
    rf"(?<!\d)\d{{1,2}}(?:o|º)?\s+de\s+(?:{_MONTH_NAMES})\b(?:\s+de\s+\d+)?"
)
#: Numero inteiro com sinal e separadores. A validacao recebe o numero como foi
#: escrito, e nao um pedaco dele.
NUMBER_PATTERN = re.compile(r"[-−]?\d+(?:[.,]\d+)*")


@dataclass(frozen=True)
class ParsedValue:
    """Valor validado: o tipado para gravar, o canonico e o exibido."""

    value: Any
    canonical: str
    display: str
    warnings: tuple[str, ...] = ()


def fold(text: str) -> str:
    """Minusculas sem acento, preservando o comprimento do texto.

    Preservar o comprimento permite usar as posicoes encontradas no texto
    dobrado para recortar o texto original, com a grafia que a pessoa usou.
    """

    folded = []
    for character in text:
        base = unicodedata.normalize("NFD", character)[0]
        folded.append(base.lower() if len(base.lower()) == 1 else character)
    return "".join(folded)


def find_status(text: str) -> str | None:
    """Primeiro status reconhecido no texto (o termo mais longo vence)."""

    match = _STATUS_PATTERN.search(fold(text).replace("_", " "))
    if not match:
        return None
    term = match.group(1)
    return STATUS_SYNONYMS.get(term) or term.replace(" ", "_")


def find_dates(text: str, today: date) -> list[tuple[int, int, date | None]]:
    """Datas do texto com a posicao. `None` indica data invalida no calendario."""

    folded = fold(text)
    found: list[tuple[int, int, date | None]] = []
    taken: list[tuple[int, int]] = []
    for pattern in DATE_PATTERNS:
        for match in pattern.finditer(folded):
            if any(start < match.end() and match.start() < end for start, end in taken):
                continue
            taken.append((match.start(), match.end()))
            found.append((match.start(), match.end(), _date_from_match(pattern, match, today)))
    return sorted(found, key=lambda item: item[0])


def find_month_only(text: str) -> re.Match[str] | None:
    return MONTH_ONLY_PATTERN.search(fold(text))


def _date_from_match(pattern: re.Pattern[str], match: re.Match[str], today: date) -> date | None:
    try:
        if pattern is DATE_PATTERNS[0]:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        if pattern is DATE_PATTERNS[1]:
            day, month, year = int(match.group(1)), int(match.group(2)), match.group(3)
        else:
            day, month, year = int(match.group(1)), MONTHS[match.group(2)], match.group(3)
        if year is None:
            candidate = date(today.year, month, day)
            # Sem ano: a proxima ocorrencia da data.
            return candidate if candidate >= today else date(today.year + 1, month, day)
        year_number = int(year)
        if year_number < 100:
            year_number += 2000
        return date(year_number, month, day)
    except ValueError:
        return None


def parse_value(spec: FieldSpec, raw: Any, today: date) -> Any:
    """Converte o valor informado no tipo do campo, sem olhar o registro."""

    if raw is None or (isinstance(raw, str) and not raw.strip()):
        raise InvalidValueError(f"Informe o novo valor de {spec.label.lower()}.")

    if spec.kind == "status":
        code = find_status(str(raw))
        if code is None:
            raise InvalidValueError(_allowed_message(spec))
        if code not in spec.allowed:
            if spec.key == "projeto.status" and code in PROJECT_CLOSING_STATUSES:
                raise InvalidValueError(
                    "Encerrar ou descontinuar um projeto segue o processo formal do PMO "
                    "e não pode ser feito pelo chat. " + _allowed_message(spec)
                )
            raise InvalidValueError(_allowed_message(spec))
        return code

    if spec.kind == "date":
        if isinstance(raw, date):
            return raw
        dates = find_dates(str(raw), today)
        if not dates:
            raise InvalidValueError(
                "Informe a data no formato dd/mm/aaaa, por exemplo 31/03/2027."
            )
        value = dates[-1][2]
        if value is None:
            raise InvalidValueError("A data informada não existe no calendário.")
        return value

    if spec.kind == "percent":
        return _parse_percent(raw)

    text = re.sub(r"\s+", " ", str(raw)).strip().strip("\"'“”.,;")
    if any(unicodedata.category(character) == "Cc" for character in text):
        raise InvalidValueError("O responsável não pode conter caracteres de controle.")
    if not 2 <= len(text) <= 160:
        raise InvalidValueError("O responsável deve ter de 2 a 160 caracteres.")
    if scan(text).found:
        raise InvalidValueError(
            "O responsável não pode conter dado pessoal ou sensível, como e-mail, "
            "CPF ou telefone. Informe o nome ou a área."
        )
    return text


def _parse_percent(raw: Any) -> Decimal:
    """Le o progresso exatamente como foi escrito, com sinal e casas decimais.

    A conferencia de casas decimais e feita no texto, e nao no `Decimal`:
    `Decimal("35.555")` e `Decimal("1.000")` nao revelam, depois de
    convertidos, que a pessoa escreveu tres casas.
    """

    invalid = "Informe o progresso como um número de 0 a 100, por exemplo 60 ou 62,5."
    if isinstance(raw, bool):
        raise InvalidValueError(invalid)
    if isinstance(raw, (int, Decimal)):
        text = str(raw)
    else:
        numbers = NUMBER_PATTERN.findall(str(raw))
        if not numbers:
            raise InvalidValueError(invalid)
        text = numbers[-1].replace("−", "-")
    separators = [character for character in text if character in ".,"]
    if len(separators) > 1:
        raise InvalidValueError(invalid)
    fraction = re.split(r"[.,]", text, maxsplit=1)[1] if separators else ""
    try:
        value = Decimal(text.replace(",", "."))
    except InvalidOperation as error:
        raise InvalidValueError(invalid) from error
    if value < 0 or value > 100:
        raise InvalidValueError("O progresso deve estar entre 0 e 100%.")
    if len(fraction) > 2:
        raise InvalidValueError("O progresso aceita no máximo duas casas decimais.")
    return value


def validate(
    spec: FieldSpec,
    value: Any,
    current: dict[str, Any],
    today: date,
) -> ParsedValue:
    """Aplica as regras que dependem do registro atual e monta a previa."""

    warnings: list[str] = []
    if spec.kind == "date":
        if not MIN_DATE <= value <= MAX_DATE:
            raise InvalidValueError("A data deve estar entre 01/01/2020 e 31/12/2036.")
        if spec.key == "projeto.prazo_final":
            if current.get("status") in PROJECT_CLOSING_STATUSES:
                raise InvalidValueError(
                    "O prazo de um projeto concluído ou descontinuado não pode ser alterado pelo chat."
                )
            start = current.get("start_date")
            if start and value < start:
                raise InvalidValueError(
                    f"O prazo final não pode ser anterior ao início do projeto ({format_date(start)})."
                )
        if spec.key == "cronograma.prazo":
            start = current.get("planned_start_date")
            if start and value < start:
                raise InvalidValueError(
                    f"O prazo não pode ser anterior ao início previsto da atividade ({format_date(start)})."
                )
        if spec.key == "marco.data_conclusao" and value > today:
            raise InvalidValueError("A data de conclusão não pode ser posterior a hoje.")
        if spec.planned_date and value < today:
            warnings.append("A data informada já passou.")

    if spec.key == "marco.status" and value == "concluido" and not current.get("completed_date"):
        warnings.append(
            "O marco ficará concluído sem data de conclusão. Registre a data em seguida, se for o caso."
        )
    if spec.key == "cronograma.status" and value == "concluido":
        progress = current.get("progress_percent")
        if progress is not None and Decimal(str(progress)) < 100:
            warnings.append("A atividade ficará concluída com progresso abaixo de 100%.")
    if spec.key == "cronograma.progresso" and value == 100 and current.get("status") != "concluido":
        warnings.append("O progresso chega a 100%, mas o status da atividade não muda sozinho.")
    if spec.key == "risco.status" and value in {"resolvido", "cancelado"}:
        warnings.append("A data de fechamento do risco não é preenchida automaticamente.")

    return ParsedValue(
        value=value,
        canonical=canonical(spec, value),
        display=display(spec, value),
        warnings=tuple(warnings),
    )


def canonical(spec: FieldSpec, value: Any) -> str | None:
    """Forma estavel usada para comparar e registrar antes e depois."""

    if value is None:
        return None
    if spec.kind == "date":
        return value.isoformat() if isinstance(value, date) else str(value)
    if spec.kind == "percent":
        number = Decimal(str(value)).normalize()
        return format(number, "f")
    return str(value)


def display(spec: FieldSpec, value: Any) -> str:
    if value is None or value == "":
        return "não informado"
    if spec.kind == "date":
        parsed = value if isinstance(value, date) else date.fromisoformat(str(value))
        return format_date(parsed)
    if spec.kind == "percent":
        return format(Decimal(str(value)).normalize(), "f").replace(".", ",") + "%"
    if spec.kind == "status":
        return STATUS_LABELS.get(str(value), str(value))
    return str(value)


def typed_from_canonical(spec: FieldSpec, value: str | None) -> Any:
    """Converte o valor canonico de volta ao tipo da coluna (desfazer)."""

    if value is None:
        return None
    if spec.kind == "date":
        return date.fromisoformat(value)
    if spec.kind == "percent":
        return Decimal(value)
    return value


def format_date(value: date) -> str:
    return value.strftime("%d/%m/%Y")


def _allowed_message(spec: FieldSpec) -> str:
    labels = ", ".join(STATUS_LABELS[code] for code in spec.allowed)
    return f"{spec.label} aceita: {labels}."
