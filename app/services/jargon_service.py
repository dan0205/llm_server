import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import aioredis

from app import models, schemas
from .ai_service import interpret_with_llm, analyze_conversation_context

async def get_interpretation(term: str, db: AsyncSession, redis: aioredis.Redis, context_sentence: str = None):
    # 1. Redis 캐시 확인 (문맥 정보 포함)
    cache_key = f"jargon:{term}:{hash(context_sentence) if context_sentence else 'no_context'}"
    cached_interpretation = await redis.get(cache_key)
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
        await redis.set(cache_key, response.model_dump_json(), ex=3600) # 1시간
        return response

    # 3. GPT API 호출 (문맥 정보 포함)
    new_interpretation_data = await interpret_with_llm(term, context_sentence)
    if not new_interpretation_data:
        return None

    # 4. 새 데이터를 DB에 저장
    if not jargon:
        jargon = models.Jargon(term=term)
        db.add(jargon)
        await db.flush() # jargon.id를 얻기 위해 flush
    
    new_interpretation = models.Interpretation(
        jargon_id=jargon.id,
        meaning=new_interpretation_data.get("meaning", ""),
        example=new_interpretation_data.get("example", "")
    )
    db.add(new_interpretation)
    await db.commit()

    # 향상된 응답 구성
    response = schemas.JargonInterpretationResponse(
        term=term,
        meaning=new_interpretation_data.get("meaning", ""),
        example=new_interpretation_data.get("example", ""),
        context_analysis=schemas.ContextAnalysis(
            detected_emotion=new_interpretation_data.get("context_analysis", {}).get("detected_emotion", "neutral"),
            formality_level=new_interpretation_data.get("context_analysis", {}).get("formality_level", "casual"),
            usage_domain=new_interpretation_data.get("context_analysis", {}).get("usage_domain", "general")
        ) if new_interpretation_data.get("context_analysis") else None,
        additional_info=schemas.AdditionalInfo(
            similar_terms=new_interpretation_data.get("additional_info", {}).get("similar_terms", []),
            usage_tips=new_interpretation_data.get("additional_info", {}).get("usage_tips"),
            origin=new_interpretation_data.get("additional_info", {}).get("origin")
        ) if new_interpretation_data.get("additional_info") else None
    )
    
    # 새 결과를 캐시에 저장
    await redis.set(cache_key, response.model_dump_json(), ex=3600)
    
    return response

async def get_all_jargon_terms(db: AsyncSession):
    result = await db.execute(select(models.Jargon.term))
    return result.scalars().all()

async def analyze_user_input(user_input: str) -> dict:
    """사용자 입력을 분석하여 신조어와 문맥을 추출합니다."""
    return await analyze_conversation_context(user_input)

async def get_contextual_interpretation(term: str, context_sentence: str, db: AsyncSession, redis: aioredis.Redis):
    """문맥을 고려한 신조어 해석을 제공합니다."""
    return await get_interpretation(term, db, redis, context_sentence)

async def batch_interpret_terms(terms: list, context_sentence: str = None, db: AsyncSession = None, redis: aioredis.Redis = None):
    """여러 신조어를 일괄 해석합니다."""
    results = []
    
    for term in terms:
        try:
            if db and redis:
                result = await get_interpretation(term, db, redis, context_sentence)
            else:
                result = await interpret_with_llm(term, context_sentence)
            
            results.append({
                "term": term,
                "success": True,
                "result": result
            })
        except Exception as e:
            results.append({
                "term": term,
                "success": False,
                "error": str(e)
            })
    
    return results