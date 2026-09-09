"""Servico interno do pipeline de PLN usado pelas rotas de texto e audio."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from app.nlp.entities import Entidade, extract_entities
from app.nlp.inference import LIMITATION_ANSWER, UNDEFINED_MACRO, Classificacao, classify

OUT_OF_SCOPE_ANSWER = (
    "Esta solicitação está fora do escopo do agente de portfólio do Metro. "
    "Posso ajudar com status, prazos, riscos, custos, documentos e comparações "
    "dos projetos do portfólio."
)
CLASSIFICATION_ERROR_ANSWER = (
    "Não foi possível classificar sua solicitação agora. "
    "Tente novamente em instantes ou reformule o pedido."
)


@dataclass(frozen=True)
class NlpPipelineResult:
    classification: Classificacao
    entities: list[Entidade]
    nlp_ms: int
    controlled_answer: str | None = None

    @property
    def blocked(self) -> bool:
        return self.controlled_answer is not None


def process_text_pipeline(text: str) -> NlpPipelineResult:
    """Classifica, extrai entidades e decide se a resposta deve ser controlada."""

    started_at = perf_counter()
    try:
        classification = classify(text)
        entities = extract_entities(text)
    except Exception:
        return NlpPipelineResult(
            classification=_classification_fallback(text),
            entities=[],
            nlp_ms=_elapsed_ms(started_at),
            controlled_answer=CLASSIFICATION_ERROR_ANSWER,
        )

    controlled_answer = _controlled_answer_for(classification)
    return NlpPipelineResult(
        classification=classification,
        entities=entities,
        nlp_ms=_elapsed_ms(started_at),
        controlled_answer=controlled_answer,
    )


def _controlled_answer_for(classification: Classificacao) -> str | None:
    if classification.macrointencao == "FORA_DE_ESCOPO":
        return OUT_OF_SCOPE_ANSWER
    if (
        classification.macrointencao == UNDEFINED_MACRO
        or classification.resposta_sugerida is not None
    ):
        return classification.resposta_sugerida or LIMITATION_ANSWER
    return None


def _classification_fallback(text: str) -> Classificacao:
    return Classificacao(
        texto=text,
        macrointencao=UNDEFINED_MACRO,
        confianca_macro=0.0,
        intencao=None,
        confianca_intencao=0.0,
        fluxo="Resposta padrao de limitacao (RNF11)",
        handler="limitacao",
        alternativas=[],
        resposta_sugerida=CLASSIFICATION_ERROR_ANSWER,
    )


def _elapsed_ms(started_at: float) -> int:
    return round((perf_counter() - started_at) * 1000)
