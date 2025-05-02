import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv(".env", override=False)   # does nothing if .env absent

class _Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY") or ""
    OPENAI_MODEL: str  = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    MONGO_URI: str     = os.getenv("MONGO_URI") or ""
    JWT_SECRET: str    = os.getenv("JWT_SECRET") or "dev-secret"
    ALPHA_KEY: str     = os.getenv("ALPHA_VANTAGE_KEY", "")

@lru_cache
def settings() -> _Settings:        
    return _Settings()