from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.core.database import get_db, get_redis
from app.models.jargon import Jargon
from app.schemas.jargon_schema import (
    JargonCreate, 
    JargonResponse, 
    JargonUpdate, 
    JargonSearchRequest,
    JargonAnalysisRequest
)
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/jargon/{word}")
async def get_jargon(word: str):
    """
    신조어 정보를 조회합니다. 
    Redis 캐시 → PostgreSQL DB → GPT API 순서로 조회합니다.
    """
    try:
        # 간단한 테스트 데이터 반환
        test_data = {
            "word": word,
            "explanation": f"'{word}'에 대한 설명입니다. 이는 테스트용 데이터입니다.",
            "source": "테스트 데이터",
            "search_count": 1,
            "is_user_modified": False,
            "modified_by": None,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": None
        }
        
        logger.info(f"테스트 데이터로 '{word}' 반환")
        return test_data
        
    except Exception as e:
        logger.error(f"신조어 조회 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 내부 오류가 발생했습니다."
        )

@router.post("/jargon/analyze")
async def analyze_jargons(
    request: JargonAnalysisRequest,
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """
    여러 신조어를 한 번에 분석합니다.
    """
    try:
        ai_service = AIService()
        analysis_results = await ai_service.analyze_jargon(
            request.words, 
            request.context
        )
        
        # 분석 결과를 DB에 저장
        saved_jargons = []
        for result in analysis_results:
            jargon = Jargon(
                word=result["word"],
                explanation=result["explanation"],
                source=result.get("source", "알 수 없음")
            )
            db.add(jargon)
            saved_jargons.append(jargon)
        
        db.commit()
        
        # Redis에 캐시 저장
        for jargon in saved_jargons:
            cache_key = f"jargon:{jargon.word}"
            redis_client.setex(cache_key, 3600, "cached")
        
        logger.info(f"{len(request.words)}개 신조어 분석 완료")
        return {"message": "분석 완료", "results": analysis_results}
        
    except Exception as e:
        logger.error(f"신조어 분석 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="분석 중 오류가 발생했습니다."
        )

@router.put("/jargon/{word}")
async def update_jargon(
    word: str,
    update_data: JargonUpdate,
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """
    신조어 정보를 사용자가 수정합니다.
    """
    try:
        jargon = db.query(Jargon).filter(Jargon.word == word).first()
        
        if not jargon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"'{word}'를 찾을 수 없습니다."
            )
        
        # 업데이트
        if update_data.explanation:
            jargon.explanation = update_data.explanation
        if update_data.source:
            jargon.source = update_data.source
        if update_data.modified_by:
            jargon.modified_by = update_data.modified_by
            jargon.is_user_modified = True
        
        db.commit()
        db.refresh(jargon)
        
        # Redis 캐시 삭제
        cache_key = f"jargon:{word}"
        redis_client.delete(cache_key)
        
        logger.info(f"'{word}' 정보 수정 완료")
        return {"message": "수정 완료", "jargon": jargon}
        
    except Exception as e:
        logger.error(f"신조어 수정 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="수정 중 오류가 발생했습니다."
        )

@router.get("/jargon", response_model=List[JargonResponse])
async def list_jargons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    저장된 신조어 목록을 조회합니다.
    """
    try:
        jargons = db.query(Jargon).offset(skip).limit(limit).all()
        return jargons
    except Exception as e:
        logger.error(f"신조어 목록 조회 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="목록 조회 중 오류가 발생했습니다."
        ) 