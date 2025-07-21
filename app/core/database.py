""" from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import aioredis
from .config import settings

# SQLAlchemy 설정
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)
Base = declarative_base()

# Redis 설정
redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

# DB 세션 의존성 주입
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Redis 연결 의존성 주입
async def get_redis():
    return redis
 """