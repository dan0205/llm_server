from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Jargon(Base):
    __tablename__ = "jargons"
    id = Column(Integer, primary_key=True, index=True)
    term = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    interpretations = relationship("Interpretation", back_populates="jargon")

class Interpretation(Base):
    __tablename__ = "interpretations"
    id = Column(Integer, primary_key=True, index=True)
    meaning = Column(Text, nullable=False)
    example = Column(Text)
    jargon_id = Column(Integer, ForeignKey("jargons.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    jargon = relationship("Jargon", back_populates="interpretations")
