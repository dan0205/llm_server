""" import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import aioredis

from app import models, schemas
from .ai_service import interpret_with_llm

async def get_interpretation(term: str, db: AsyncSession, redis: aioredis.Redis):
    # 1. Redis 캐시 확인
    cached_interpretation = await redis.get(f"jargon:{term}")
    if cached_interpretation:
        return json.loads(cached_interpretation)

    # 2. DB 확인
    result = await db.execute(
        select(models.Jargon)
        .options(selectinload(models.Jargon.interpretations))
        .filter(models.Jargon.term == term)
    )
    jargon = result.scalar_one_or_none()

    if jargon and jargon.interpretations:
        interpretation = jargon.interpretations[0] # 가장 최신 해석을 가져온다고 가정
        response = schemas.JargonInterpretationResponse(
            term=jargon.term,
            meaning=interpretation.meaning,
            example=interpretation.example
        )
        # DB 결과를 캐시에 저장
        await redis.set(f"jargon:{term}", response.model_dump_json(), ex=3600) # 1시간
        return response

    # 3. GPT API 호출
    new_interpretation_data = await interpret_with_llm(term)
    if not new_interpretation_data:
        return None

    # 4. 새 데이터를 DB에 저장
    if not jargon:
        jargon = models.Jargon(term=term)
        db.add(jargon)
        await db.flush() # jargon.id를 얻기 위해 flush
    
    new_interpretation = models.Interpretation(
        jargon_id=jargon.id,
        **new_interpretation_data
    )
    db.add(new_interpretation)
    await db.commit()

    response = schemas.JargonInterpretationResponse(
        term=term, **new_interpretation_data
    )
    # 새 결과를 캐시에 저장
    await redis.set(f"jargon:{term}", response.model_dump_json(), ex=3600)
    
    return response

async def get_all_jargon_terms(db: AsyncSession):
    result = await db.execute(select(models.Jargon.term))
    return result.scalars().all()

 """