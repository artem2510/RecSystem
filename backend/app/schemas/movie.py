from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class MovieCreate(BaseModel):
    """Схема для створення фільму"""
    title: str
    original_title: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None
    duration: Optional[int] = None
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None
    genres: List[str] = []
    keywords: List[str] = []


class MovieResponse(BaseModel):
    """Базова схема відповіді з даними фільму"""
    id: int
    title: str
    original_title: Optional[str]
    year: Optional[int]
    duration: Optional[int]
    poster_url: Optional[str]
    genres: List[str]
    average_rating: float
    ratings_count: int
    views_count: int
    
    class Config:
        from_attributes = True


class MovieDetail(MovieResponse):
    """Детальна схема фільму"""
    description: Optional[str]
    trailer_url: Optional[str]
    keywords: List[str]
    emotions: Dict[str, float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
