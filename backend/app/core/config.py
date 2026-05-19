from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Налаштування додатку"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./movie_recommender.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]
    
    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Movie Recommender System"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
