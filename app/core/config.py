import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    VOYAGE_API_KEY: Optional[str] = os.getenv("VOYAGE_API_KEY")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ragbot.db")
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    UPLOAD_DIRECTORY: str = os.getenv("UPLOAD_DIRECTORY", "./uploads")
    OUTPUT_DIRECTORY: str = os.getenv("OUTPUT_DIRECTORY", "./outputs")
    
    class Config:
        env_file = ".env"

settings = Settings()
