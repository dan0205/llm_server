from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # 데이터베이스 설정
    DATABASE_URL: str = "postgresql://user:password@localhost/llm_db"
    
    # Redis 설정
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # GPT API 설정
    OPENAI_API_KEY: Optional[str] = None
    
    # 애플리케이션 설정
    APP_NAME: str = "LLM 신조어 분석 API"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings() 