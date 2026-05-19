from pydantic import BaseModel, Field
from datetime import datetime


class RatingCreate(BaseModel):
    """Схема для створення оцінки"""
    movie_id: int
    rating: float = Field(..., ge=1, le=10, description="Оцінка від 1 до 10")


class RatingResponse(BaseModel):
    """Схема відповіді з оцінкою"""
    id: int
    user_id: int
    movie_id: int
    rating: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
