from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Movie(Base):
    """Модель фільму"""
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    original_title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    year = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)  # в хвилинах
    poster_url = Column(String, nullable=True)
    trailer_url = Column(String, nullable=True)
    
    # Жанри (список)
    genres = Column(JSON, nullable=False, default=list)
    
    # Ключові слова
    keywords = Column(JSON, nullable=True, default=list)
    
    # Емоційні характеристики
    emotions = Column(JSON, nullable=True, default=dict)
    # Приклад: {"оптимістичний": 0.8, "драматичний": 0.3, "напружений": 0.5}
    
    # Статистика
    average_rating = Column(Float, default=0.0)
    ratings_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    
    # Векторне представлення для рекомендацій (зберігається як JSON)
    content_vector = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ratings = relationship("Rating", back_populates="movie", cascade="all, delete-orphan")
    viewing_history = relationship("ViewingHistory", back_populates="movie", cascade="all, delete-orphan")
