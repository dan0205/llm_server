from pydantic_settings import BaseSettings

# env 파일에 이런식으로 값을 넣어야 하는 걸 알려주는 설계도
# 해당 변수에 값을 넣지말고 env 파일에 넣기기

class Settings(BaseSettings):

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/llm_db"
    REDIS_URL: str = "redis://cache:6379"

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

