# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "AuroraOS"
    API_V1_PREFIX: str = "/v1"
    DATABASE_URL: str = "sqlite:///./auroraos.db"
    
    # LLM API Keys
    OPENAI_API_KEY: Optional[str] = None  # GPT models
    XAI_API_KEY: Optional[str] = None     # Grok models (soft-ero content)

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore unknown env variables


settings = Settings()

