"""Resultado público da classificação, compartilhado por texto e áudio."""
from pydantic import BaseModel


class AudioIntent(BaseModel):
    macro: str
    specific: str
    confidence_macro: float
    confidence_specific: float
