from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.schemas.jargon_schema import JargonInterpretationResponse
from app.core.database import get_db, get_redis
from app.services.jargon_service import get_interpretation

router = APIRouter()

@router.options("/jargons/interpret/{term}")
async def options_interpret(term: str):
    # 아무 검증/의존성 없이 프리플라이트에 204 No Content
    return Response(status_code=204)

@router.get("/jargons/interpret/{term}")
async def interpret_jargon(
    term: str,
    context: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    rds: redis.Redis = Depends(get_redis),
):
    term = (term or "").strip()
    if not term:
        raise HTTPException(status_code=400, detail="term is required")

    data = await get_interpretation(term, db, rds, context)
    # 항상 {"meaning_line": "..."} 형태로 보장
    line = data.get("meaning_line", "") if isinstance(data, dict) else str(data)
    return JSONResponse(content={"meaning_line": line}, status_code=200)