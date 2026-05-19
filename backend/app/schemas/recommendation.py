from pydantic import BaseModel
from typing import List, Dict, Any
from .movie import MovieResponse


class ExplanationResponse(BaseModel):
    """Схема пояснення рекомендації"""
    reason_type: str  # "genre_similarity", "collaborative", "emotion_match"
    reason_text: str
    confidence: float  # від 0 до 1
    details: Dict[str, Any]


class RecommendationResponse(BaseModel):
    """Схема рекомендації з поясненням"""
    movie: MovieResponse
    score: float
    explanations: List[ExplanationResponse]
