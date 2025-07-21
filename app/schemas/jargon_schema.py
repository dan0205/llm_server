""" from pydantic import BaseModel
from typing import Optional

class JargonBase(BaseModel):
    term: str

class JargonCreate(JargonBase):
    pass

class InterpretationBase(BaseModel):
    meaning: str
    example: Optional[str] = None

class JargonInterpretationResponse(InterpretationBase):
    term: str
 """