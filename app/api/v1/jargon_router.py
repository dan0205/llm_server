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

@router.get("/jargon/{word}", response_model=JargonResponse)
async def get_jargon(word: str, db: Session = Depends(get_db), redis_client = Depends(get_redis)):
    """
    신조어 정보를 조회합니다. 
    Redis 캐시 → PostgreSQL DB → GPT API 순서로 조회합니다.
    """
    try:
        # 1. Redis 캐시에서 조회
        cache_key = f"jargon:{word}"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            logger.info(f"Redis 캐시에서 '{word}' 조회됨")
            # 캐시된 데이터를 파싱하여 반환 (실제로는 JSON 직렬화 필요)
            # 여기서는 간단히 DB에서 다시 조회
            pass
        
        # 2. PostgreSQL DB에서 조회
        jargon = db.query(Jargon).filter(Jargon.word == word).first()
        
        if jargon:
            # 검색 횟수 증가
            jargon.search_count += 1
            db.commit()
            
            # Redis에 캐시 저장 (TTL: 1시간)
            redis_client.setex(cache_key, 3600, "cached")
            
            logger.info(f"DB에서 '{word}' 조회됨")
            return jargon
        
        # 3. GPT API를 통해 분석
        ai_service = AIService()
        analysis_result = await ai_service.get_single_word_analysis(word)
        
        if analysis_result:
            # 새로운 신조어를 DB에 저장
            new_jargon = Jargon(
                word=analysis_result["word"],
                explanation=analysis_result["explanation"],
                source=analysis_result.get("source", "알 수 없음")
            )
            
            db.add(new_jargon)
            db.commit()
            db.refresh(new_jargon)
            
            # Redis에 캐시 저장
            redis_client.setex(cache_key, 3600, "cached")
            
            logger.info(f"GPT API로 '{word}' 분석 완료")
            return new_jargon
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"'{word}'에 대한 정보를 찾을 수 없습니다."
        )
        
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