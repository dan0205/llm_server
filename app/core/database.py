from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import redis.asyncio as redis
from .config import settings

# SQLAlchemy
engine = create_async_engine(settings.DATABASE_URL, future=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, autoflush=False, autocommit=False)
Base = declarative_base()

# Redis
_redis = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_redis():
    return _redis
