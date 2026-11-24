"""
Application Configuration
Loads environment variables and provides settings object
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

# backend/app/core/config.py -> repo root is three levels above app/
_REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    SECRET_KEY: str = "change_this_secret_key"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://scraper:scraper_password@localhost:5432/scraper_db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_WORKER_CONCURRENCY: int = 4
    CELERY_TASK_TIME_LIMIT: int = 600
    
    # LLM Configuration
    LLM_PRIMARY_PROVIDER: str = "groq"
    LLM_FALLBACK_PROVIDER: str = "gemini"
    LLM_FALLBACK_ENABLED: bool = True
    
    # Groq
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    
    # Gemini
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    
    # Timeouts & Limits
    LLM_TIMEOUT_SECONDS: int = 45
    LLM_MAX_RETRIES: int = 2
    SCRAPING_TIMEOUT_SECONDS: int = 30
    BROWSER_TIMEOUT_SECONDS: int = 30
    EXTRACTION_TIMEOUT_MINUTES: int = 5
    MAX_PAGE_SIZE_MB: int = 10
    MAX_CONCURRENT_JOBS: int = 10
    MAX_RECORDS_PER_JOB: int = 1000
    
    # Security
    ENABLE_SSRF_PROTECTION: bool = True
    ALLOWED_URL_SCHEMES: str = "http,https"
    BLOCK_PRIVATE_IPS: bool = True
    BLOCK_CLOUD_METADATA: bool = True
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Features
    ENABLE_HISTORY: bool = True
    HISTORY_RETENTION_DAYS: int = 90
    ENABLE_METRICS: bool = True
    MOCK_LLM: bool = False
    
    class Config:
        # Look for .env in the current dir first, then the repo root, so the
        # backend works whether started from the repo root or from backend/.
        env_file = (str(_REPO_ROOT / ".env"), ".env")
        case_sensitive = True
        extra = "ignore"


# Create global settings instance
settings = Settings()
