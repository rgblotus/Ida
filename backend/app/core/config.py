from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn, Field
from typing import Literal, Optional
from pathlib import Path

class Settings(BaseSettings):
    # Security
    SECRET_KEY: str = Field(..., alias="SECRET_KEY")
    ALGORITHM: Literal["HS256", "HS384", "HS512"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    API_V1_STR: str = "/api/v1"

    # Infrastructure
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/nikidb"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Server
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    LOG_LEVEL: str = "INFO"  # kept as snake_case for compatibility with main.py

    # Milvus
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    
    # Ollama Configuration
    OLLAMA_LOCAL_URL: str = "http://localhost:11434"
    OLLAMA_CLOUD_URL: str = "https://api.ollama.ai"
    OLLAMA_MODEL: str = "phi3"
    OLLAMA_CLOUD_API_KEY: Optional[str] = None
    
    # OpenAI Configuration (Optional)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # RAG Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    
    # File Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    # Weather API
    OPENWEATHER_API_KEY: str = "b32c32cd24f76e497b482c3355b37152"
    DEFAULT_CITY: str = "Surat"

    model_config = {
        "env_file": Path(__file__).parent.parent.parent / ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "case_sensitive": False  # Allow case insensitivity to match env vars to fields
    }

settings = Settings()