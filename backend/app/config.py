import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "SoilTwin AI"
    API_V1_PREFIX: str = "/api"
    
    # Provider: "gemini", "openai", or "mock" (auto-fallback to mock if keys not provided)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Model routing
    FAST_MODEL: str = os.getenv("FAST_MODEL", "gemini-1.5-flash" if os.getenv("LLM_PROVIDER") == "gemini" else "gpt-4o-mini")
    STRONG_MODEL: str = os.getenv("STRONG_MODEL", "gemini-1.5-pro" if os.getenv("LLM_PROVIDER") == "gemini" else "gpt-4o")
    
    # Storage & Paths
    BASE_DIR: Path = BASE_DIR
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    KNOWLEDGE_BASE_DIR: Path = BASE_DIR / "knowledge_base"
    MODELS_DIR: Path = BASE_DIR / "models"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'soil_twin.db'}")
    
    # Embeddings
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    
    # Agentic constraints
    MAX_RETRIES: int = 2
    TOP_K_RETRIEVAL: int = 3
    RELEVANCE_THRESHOLD: float = 0.55
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
