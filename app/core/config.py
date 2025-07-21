""" from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 데이터베이스 설정
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/dbname"
    
    # Redis 설정
    REDIS_URL: str = "redis://localhost:6379"

    # JWT 보안 설정
    SECRET_KEY: str = "your_super_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7일

    # 외부 API 키
    OPENAI_API_KEY: str = "your_openai_api_key"
    GOOGLE_CLIENT_ID: str = "your_google_client_id.apps.googleusercontent.com"

    class Config:
        env_file = ".env"

settings = Settings()

 """