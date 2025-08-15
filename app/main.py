import os
import time
from typing import Optional
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from starlette.requests import Request
from app.api.v1 import jargon_router
from app.core.database import Base, engine, _redis
from app.core.config import settings
from openai import AsyncOpenAI
import traceback
from fastapi.responses import JSONResponse

# .env 파일 우선순위 강제 (쉘값에 덮이지 않게)
from dotenv import load_dotenv
load_dotenv(override=True)  # override=True로 .env 우선

print(f"[STARTUP] Environment check:")
print(f"[STARTUP] OPENAI_API_KEY exists: {bool(os.getenv('OPENAI_API_KEY'))}")
print(f"[STARTUP] REDIS_URL: {os.getenv('REDIS_URL', 'not set')}")

app = FastAPI(title="LLM Server")

# CORS 설정 - 확장 프로그램 ID만 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://iidglihcogajpjpmdjadngifkokpjmmg"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 예외 핸들러 (개발용)
@app.exception_handler(Exception)
async def _dbg_ex_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse({"error": str(exc)}, status_code=500)

# 구조화 로깅 미들웨어
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        return response
    finally:
        dur = int((time.time() - start)*1000)
        print(f"[REQ] {request.method} {request.url.path} {dur}ms")

app.include_router(jargon_router.router, prefix="/api/v1", tags=["Jargons"])

@app.on_event("startup")
async def startup_event():
    # DB 테이블 생성은 유지
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 환경변수 검증 로그
    if not settings.OPENAI_API_KEY:
        print("[WARN] OPENAI_API_KEY is empty")
    if not settings.REDIS_URL:
        print("[WARN] REDIS_URL is empty")

@app.get("/__health")
async def __health():
    return {"ok": True}

@app.get("/__debug/redis")
async def __debug_redis():
    try:
        pong = await _redis.ping()
        return {"ok": bool(pong)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/__debug/openai")
async def __debug_openai():
    try:
        cli = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) # 키만 확인 (네트워크 미호출)
        return {"ok": bool(settings.OPENAI_API_KEY)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/__debug/llm")
async def __debug_llm():
    try:
        from app.services.ai_service import interpret_with_llm
        
        # 테스트용 간단한 호출
        result = await interpret_with_llm("테스트", "테스트 문맥")
        
        return {
            "ok": True,
            "test_result": result,
            "openai_key_exists": bool(settings.OPENAI_API_KEY),
            "openai_key_length": len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0
        }
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return {"ok": False, "error_details": error_details}

@app.get("/__debug/cache")
async def __debug_cache():
    """캐시 내용을 확인하고 관리할 수 있는 디버그 엔드포인트"""
    try:
        from app.services.jargon_service import cache_key_for
        
        # 테스트용 캐시 키 생성
        test_key = cache_key_for("테스트", "테스트 문맥")
        
        return {
            "ok": True,
            "cache_namespace": "jargon:v2",
            "test_key": test_key,
            "redis_connected": await _redis.ping() if _redis else False
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/__debug/cache/{term}")
async def __debug_cache_term(term: str, context: Optional[str] = None):
    """특정 term의 캐시 내용 확인"""
    try:
        from app.services.jargon_service import cache_key_for
        
        key = cache_key_for(term, context)
        cached_value = await _redis.get(key) if _redis else None
        
        if cached_value:
            import json
            try:
                parsed = json.loads(cached_value)
                return {
                    "ok": True,
                    "key": key,
                    "cached": True,
                    "value": parsed,
                    "ttl": await _redis.ttl(key) if _redis else None
                }
            except json.JSONDecodeError:
                return {
                    "ok": True,
                    "key": key,
                    "cached": True,
                    "value": cached_value.decode('utf-8'),
                    "raw": True
                }
        else:
            return {
                "ok": True,
                "key": key,
                "cached": False
            }
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.delete("/__debug/cache/{term}")
async def __debug_cache_delete(term: str, context: Optional[str] = None):
    """특정 term의 캐시 삭제"""
    try:
        from app.services.jargon_service import cache_key_for
        
        key = cache_key_for(term, context)
        deleted = await _redis.delete(key) if _redis else 0
        
        return {
            "ok": True,
            "key": key,
            "deleted": bool(deleted),
            "deleted_count": deleted
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "OK"}