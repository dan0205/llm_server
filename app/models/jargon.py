from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class Jargon(Base):
    __tablename__ = "jargons"
    
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(100), unique=True, index=True, nullable=False)
    explanation = Column(Text, nullable=False)
    source = Column(String(500), nullable=True)
    search_count = Column(Integer, default=0)
    is_user_modified = Column(Boolean, default=False)
    modified_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Jargon(word='{self.word}', explanation='{self.explanation[:50]}...')>" 