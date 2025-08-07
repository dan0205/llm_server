from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import aioredis
import time

from app import schemas
from app.core.database import get_db, get_redis
from app.services import jargon_service
from app.services.ai_service import (
    analyze_conversation_context,
    get_similar_terms,
    clarify_ambiguous_term,
    interpret_with_llm
)

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

@router.post("/jargons/interpret-contextual", response_model=schemas.EnhancedInterpretationResponse)
async def get_contextual_interpretation(
    request: schemas.ContextualInterpretationRequest,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis)
):
    """문맥을 고려한 신조어 해석을 제공합니다."""
    start_time = time.time()
    
    try:
        # 문맥 기반 해석
        result = await interpret_with_llm(request.term, request.context_sentence)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to interpret term"
            )
        
        processing_time = time.time() - start_time
        
        # 응답 구성
        response = schemas.EnhancedInterpretationResponse(
            term=request.term,
            meaning=result.get("meaning", ""),
            example=result.get("example", ""),
            context_analysis=schemas.ContextAnalysis(
                detected_emotion=result.get("context_analysis", {}).get("detected_emotion", "neutral"),
                formality_level=result.get("context_analysis", {}).get("formality_level", "casual"),
                usage_domain=result.get("context_analysis", {}).get("usage_domain", "general")
            ),
            additional_info=schemas.AdditionalInfo(
                similar_terms=result.get("additional_info", {}).get("similar_terms", []),
                usage_tips=result.get("additional_info", {}).get("usage_tips"),
                origin=result.get("additional_info", {}).get("origin")
            ),
            confidence_score=0.9,  # 실제로는 AI 모델의 신뢰도 점수를 사용
            processing_time=processing_time
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )

@router.post("/jargons/analyze-conversation", response_model=schemas.ConversationAnalysis)
async def analyze_conversation(
    user_input: str
):
    """사용자 입력에서 신조어와 문맥을 분석합니다."""
    try:
        analysis = await analyze_conversation_context(user_input)
        return schemas.ConversationAnalysis(**analysis)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing conversation: {str(e)}"
        )

@router.get("/jargons/similar/{term}", response_model=schemas.SimilarTermsResponse)
async def get_similar_terms_endpoint(term: str):
    """특정 신조어와 유사한 신조어들을 찾습니다."""
    try:
        similar_terms = await get_similar_terms(term)
        return schemas.SimilarTermsResponse(
            similar_terms=similar_terms,
            related_concepts=[]  # 향후 확장 가능
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding similar terms: {str(e)}"
        )

@router.post("/jargons/clarify", response_model=schemas.AmbiguousTermClarification)
async def clarify_ambiguous_term_endpoint(
    term: str,
    context: str
):
    """모호한 신조어의 의미를 명확히 합니다."""
    try:
        clarification = await clarify_ambiguous_term(term, context)
        return schemas.AmbiguousTermClarification(**clarification)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clarifying term: {str(e)}"
        )

@router.post("/jargons/batch-analyze")
async def batch_analyze_terms(
    terms: List[str],
    context: Optional[str] = None
):
    """여러 신조어를 일괄 분석합니다."""
    results = []
    
    for term in terms:
        try:
            result = await interpret_with_llm(term, context)
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
    
    return {"results": results}