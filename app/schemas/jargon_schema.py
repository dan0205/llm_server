from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JargonBase(BaseModel):
    word: str
    explanation: str
    source: Optional[str] = None

class JargonCreate(JargonBase):
    pass

class JargonUpdate(BaseModel):
    explanation: Optional[str] = None
    source: Optional[str] = None
    modified_by: Optional[str] = None

class JargonResponse(JargonBase):
    id: int
    search_count: int
    is_user_modified: bool
    modified_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class JargonSearchRequest(BaseModel):
    word: str

class JargonAnalysisRequest(BaseModel):
    words: list[str]
    context: Optional[str] = None 