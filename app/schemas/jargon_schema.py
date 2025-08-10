from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ContextAnalysis(BaseModel):
    detected_emotion: str = "neutral"
    formality_level: str = "casual"
    usage_domain: str = "general"

class AdditionalInfo(BaseModel):
    synonyms: List[str] = []
    antonyms: List[str] = []
    usage_tips: Optional[str] = ""
    origin: Optional[str] = ""

class JargonInterpretationResponse(BaseModel):
    term: str
    meaning: str
    example: Optional[str] = ""
    context_analysis: ContextAnalysis = Field(default_factory=ContextAnalysis)
    additional_info: AdditionalInfo = Field(default_factory=AdditionalInfo)