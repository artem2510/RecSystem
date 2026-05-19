from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.movie import MovieCreate, MovieResponse, MovieDetail
from app.schemas.rating import RatingCreate, RatingResponse
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.viewing_history import ViewingHistory
from app.api.deps import get_current_user
from app.models.user import User
from app.services.nlp_analyzer import NLPAnalyzer

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("", response_model=List[MovieResponse])
def get_movies(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    genre: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Отримання списку фільмів"""
    query = db.query(Movie)
    
    if genre:
        query = query.filter(Movie.genres.contains([genre]))
    
    movies = query.offset(skip).limit(limit).all()
    return [MovieResponse.model_validate(m) for m in movies]


@router.get("/{movie_id}", response_model=MovieDetail)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """Отримання деталей фільму"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фільм не знайдено")
    
    return MovieDetail.model_validate(movie)


@router.post("", response_model=MovieResponse)
def create_movie(
    movie_data: MovieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Створення нового фільму (тільки для адміністраторів)"""
    nlp = NLPAnalyzer()
    
    # Аналіз емоцій
    emotions = nlp.analyze_emotions(movie_data.description or "")
    
    # Витягування ключових слів
    keywords = nlp.extract_keywords(movie_data.description or "")
    
    # Створення фільму
    movie = Movie(
        title=movie_data.title,
        original_title=movie_data.original_title,
        description=movie_data.description,
        year=movie_data.year,
        duration=movie_data.duration,
        poster_url=movie_data.poster_url,
        trailer_url=movie_data.trailer_url,
        genres=movie_data.genres,
        keywords=keywords,
        emotions=emotions
    )
    
    db.add(movie)
    db.commit()
    db.refresh(movie)
    
    return MovieResponse.model_validate(movie)


@router.post("/{movie_id}/rate", response_model=RatingResponse)
def rate_movie(
    movie_id: int,
    rating_data: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Оцінити фільм"""
    # Перевірка чи існує фільм
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фільм не знайдено")
    
    # Перевірка чи користувач вже оцінював цей фільм
    existing_rating = db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.movie_id == movie_id
    ).first()
    
    if existing_rating:
        # Оновлення існуючої оцінки
        existing_rating.rating = rating_data.rating
        db.commit()
        db.refresh(existing_rating)
        
        # Оновлення середнього рейтингу фільму
        _update_movie_rating(db, movie_id)
        
        return RatingResponse.model_validate(existing_rating)
    
    # Створення нової оцінки
    rating = Rating(
        user_id=current_user.id,
        movie_id=movie_id,
        rating=rating_data.rating
    )
    
    db.add(rating)
    db.commit()
    db.refresh(rating)
    
    # Оновлення середнього рейтингу фільму
    _update_movie_rating(db, movie_id)
    
    return RatingResponse.model_validate(rating)


@router.post("/{movie_id}/watch")
def mark_as_watched(
    movie_id: int,
    completed: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Позначити фільм як переглянутий"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фільм не знайдено")
    
    # Додавання до історії переглядів
    viewing = ViewingHistory(
        user_id=current_user.id,
        movie_id=movie_id,
        completed=completed
    )
    
    db.add(viewing)
    
    # Оновлення лічильника переглядів
    movie.views_count += 1
    
    db.commit()
    
    return {"message": "Фільм позначено як переглянутий"}


def _update_movie_rating(db: Session, movie_id: int):
    """Оновлення середнього рейтингу фільму"""
    from sqlalchemy import func
    
    result = db.query(
        func.avg(Rating.rating).label('avg_rating'),
        func.count(Rating.id).label('count')
    ).filter(Rating.movie_id == movie_id).first()
    
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie:
        movie.average_rating = float(result.avg_rating) if result.avg_rating else 0.0
        movie.ratings_count = result.count
        db.commit()
