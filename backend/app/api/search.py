from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from app.core.database import get_db
from app.schemas.movie import MovieResponse
from app.models.movie import Movie

router = APIRouter(prefix="/search", tags=["Search"])


def normalize_search_query(text: str) -> str:
    """Нормалізація пошукового запиту для кращого пошуку"""
    return text.strip().lower()


def calculate_relevance(movie: Movie, query: str) -> int:
    """Розрахунок релевантності фільму до запиту"""
    query_lower = query.lower()
    title_lower = (movie.title or "").lower()
    original_lower = (movie.original_title or "").lower()
    
    score = 0
    
    # Точний збіг на початку назви - найвищий пріоритет
    if title_lower.startswith(query_lower) or original_lower.startswith(query_lower):
        score += 1000
    
    # Точний збіг у назві
    elif query_lower in title_lower or query_lower in original_lower:
        score += 500
    
    # Додаємо рейтинг фільму
    score += int(movie.average_rating * 10)
    
    return score


@router.get("/autocomplete", response_model=List[MovieResponse])
def autocomplete_search(
    q: str = Query(..., min_length=1, description="Пошуковий запит"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Швидкий пошук для автодоповнення (autocomplete)"""
    if not q or len(q.strip()) == 0:
        return []
    
    query_normalized = normalize_search_query(q)
    
    # Отримуємо ВСІ фільми з бази (для невеликої бази це швидко)
    # Для великої бази можна додати кешування
    all_movies = db.query(Movie).all()
    
    # Фільтруємо в Python для підтримки кирилиці
    matching_movies = []
    for movie in all_movies:
        title_lower = (movie.title or "").lower()
        original_lower = (movie.original_title or "").lower()
        
        if query_normalized in title_lower or query_normalized in original_lower:
            matching_movies.append(movie)
    
    # Сортуємо за релевантністю
    sorted_movies = sorted(
        matching_movies,
        key=lambda m: calculate_relevance(m, query_normalized),
        reverse=True
    )
    
    return [MovieResponse.model_validate(m) for m in sorted_movies[:limit]]


@router.get("", response_model=List[MovieResponse])
def search_movies(
    q: Optional[str] = Query(None, description="Пошуковий запит"),
    genre: Optional[str] = Query(None, description="Фільтр за жанром"),
    emotion: Optional[str] = Query(None, description="Фільтр за емоцією"),
    year_from: Optional[int] = Query(None, description="Рік від"),
    year_to: Optional[int] = Query(None, description="Рік до"),
    min_rating: Optional[float] = Query(None, ge=0, le=10, description="Мінімальний рейтинг"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Пошук фільмів за різними критеріями"""
    
    # Якщо є текстовий пошук, використовуємо Python-фільтрацію
    if q:
        query_normalized = normalize_search_query(q)
        all_movies = db.query(Movie).all()
        
        # Фільтруємо в Python для підтримки кирилиці
        matching_movies = []
        for movie in all_movies:
            title_lower = (movie.title or "").lower()
            original_lower = (movie.original_title or "").lower()
            description_lower = (movie.description or "").lower()
            
            if (query_normalized in title_lower or 
                query_normalized in original_lower or 
                query_normalized in description_lower):
                matching_movies.append(movie)
        
        # Застосовуємо інші фільтри
        if genre:
            matching_movies = [m for m in matching_movies if m.genres and genre in m.genres]
        if year_from:
            matching_movies = [m for m in matching_movies if m.year and m.year >= year_from]
        if year_to:
            matching_movies = [m for m in matching_movies if m.year and m.year <= year_to]
        if min_rating:
            matching_movies = [m for m in matching_movies if m.average_rating >= min_rating]
        
        # Обробка емоцій
        if emotion:
            matching_movies = [
                m for m in matching_movies 
                if m.emotions and m.emotions.get(emotion, 0) >= 0.5
            ]
        
        # Сортуємо за релевантністю
        sorted_movies = sorted(
            matching_movies,
            key=lambda m: calculate_relevance(m, query_normalized),
            reverse=True
        )
        
        return [MovieResponse.model_validate(m) for m in sorted_movies[:limit]]
    
    # Якщо немає текстового пошуку, використовуємо SQL-запити
    query = db.query(Movie)
    
    # Фільтр за жанром
    if genre:
        query = query.filter(Movie.genres.contains([genre]))
    
    # Фільтр за емоцією
    if emotion:
        # Пошук фільмів де емоція має високий скор
        all_movies = query.all()
        filtered_movies = [
            m for m in all_movies 
            if m.emotions and m.emotions.get(emotion, 0) >= 0.5
        ]
        movies = filtered_movies[:limit]
    else:
        # Фільтр за роком
        if year_from:
            query = query.filter(Movie.year >= year_from)
        if year_to:
            query = query.filter(Movie.year <= year_to)
        
        # Фільтр за рейтингом
        if min_rating:
            query = query.filter(Movie.average_rating >= min_rating)
        
        # Просто за рейтингом
        movies = query.order_by(Movie.average_rating.desc()).limit(limit).all()
    
    return [MovieResponse.model_validate(m) for m in movies]


@router.get("/emotions", response_model=List[str])
def get_available_emotions():
    """Отримання списку доступних емоцій"""
    return [
        "оптимістичний",
        "драматичний",
        "напружений",
        "романтичний",
        "жахливий",
        "пригодницький"
    ]


@router.get("/genres", response_model=List[str])
def get_available_genres(db: Session = Depends(get_db)):
    """Отримання списку доступних жанрів"""
    movies = db.query(Movie).all()
    genres = set()
    for movie in movies:
        if movie.genres:
            genres.update(movie.genres)
    
    return sorted(list(genres))
