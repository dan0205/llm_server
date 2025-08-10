from pydantic_settings import BaseSettings

# env 파일에 이런식으로 값을 넣어야 하는 걸 알려주는 설계도
# 해당 변수에 값을 넣지말고 env 파일에 넣기기

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/llm_db"
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str = "change_me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"  # 추가 필드 무시

settings = Settings()

