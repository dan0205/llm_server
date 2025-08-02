""" from fastapi import FastAPI
from app.api.v1 import auth_router, jargon_router
from app.core.database import Base, engine

app = FastAPI(title="신조어 해석기 API")

# API 라우터 포함
app.include_router(auth_router.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(jargon_router.router, prefix="/api/v1", tags=["Jargons"])

@app.on_event("startup")
async def startup_event():
    # 애플리케이션 시작 시 DB 테이블 생성 (개발 환경용)
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # 개발시 필요하면 주석 해제
        await conn.run_sync(Base.metadata.create_all)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Jargon Interpreter API!"} """
