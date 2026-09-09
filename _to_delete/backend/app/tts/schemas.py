from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    sample_rate: int = Field(default=22050, ge=8000, le=48000)
    amplitude: float = Field(default=0.28, ge=0.05, le=0.9)


class TTSAnalysis(BaseModel):
    original_text: str
    normalized_text: str
    syllables: list[str]
    sample_rate: int
    duration_seconds: float
    sample_count: int
    peak_amplitude: float
    rms_amplitude: float
