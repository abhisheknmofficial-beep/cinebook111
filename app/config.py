import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "CineBook"
    PROJECT_TAGLINE: str = "Discover. Choose. Experience."
    SECRET_KEY: str = os.getenv("SECRET_KEY", "cinebook-secret-key-for-college-demo-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cinebook.db")
    DEBUG: bool = True

settings = Settings()
