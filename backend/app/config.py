from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI helper (RAG)
    HF_TOKEN: str = ""
    HF_CHAT_MODEL: str = "openai/gpt-oss-120b"
    HF_PROVIDER: str = "auto"
    HF_EMBEDDING_MODEL: str = "Qwen/Qwen3-Embedding-0.6B"
    HF_EMBEDDING_PROVIDER: str = "deepinfra"
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    class Config:
        env_file = ".env"

settings = Settings()