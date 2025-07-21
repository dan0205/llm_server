""" from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import aioredis

from app import schemas
from app.core.database import get_db, get_redis
from app.services import jargon_service

router = APIRouter()

@router.get("/jargons", response_model=List[str])
async def get_all_jargons_list(db: AsyncSession = Depends(get_db)):
    """웹페이지 하이라이팅을 위해 DB에 저장된 모든 신조어 목록을 반환합니다."""
    return await jargon_service.get_all_jargon_terms(db)

@router.get("/jargons/interpret/{term}", response_model=schemas.JargonInterpretationResponse)
async def get_jargon_interpretation(
    term: str,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis)
):
    """특정 신조어의 의미를 조회합니다. (캐시 -> DB -> LLM 순)"""
    interpretation = await jargon_service.get_interpretation(term, db, redis)
    if not interpretation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interpretation not found"
        )
    return interpretation
 """