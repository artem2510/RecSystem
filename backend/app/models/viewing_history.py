from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ViewingHistory(Base):
    """Модель історії переглядів"""
    __tablename__ = "viewing_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    watched_at = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=False)  # чи переглянуто повністю
    
    # Relationships
    user = relationship("User", back_populates="viewing_history")
    movie = relationship("Movie", back_populates="viewing_history")
