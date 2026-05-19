from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List
from collections import Counter
from app.core.database import get_db
from app.models.user import User
from app.models.rating import Rating
from app.models.movie import Movie
from app.models.viewing_history import ViewingHistory
from app.api.deps import get_current_user
from app.services.dashboard_analytics import DashboardAnalytics

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Отримання статистики користувача"""
    
    # Кількість оцінених фільмів
    ratings_count = db.query(Rating).filter(Rating.user_id == current_user.id).count()
    
    # Кількість переглянутих фільмів
    views_count = db.query(ViewingHistory).filter(
        ViewingHistory.user_id == current_user.id
    ).count()
    
    # Середня оцінка користувача
    avg_rating = db.query(func.avg(Rating.rating)).filter(
        Rating.user_id == current_user.id
    ).scalar() or 0.0
    
    # Улюблені жанри
    user_ratings = db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.rating >= 7.0
    ).all()
    
    genres = []
    for rating in user_ratings:
        movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
        if movie and movie.genres:
            genres.extend(movie.genres)
    
    genre_counts = Counter(genres)
    favorite_genres = [
        {"genre": genre, "count": count}
        for genre, count in genre_counts.most_common(5)
    ]
    
    return {
        "ratings_count": ratings_count,
        "views_count": views_count,
        "average_rating": round(avg_rating, 1),
        "favorite_genres": favorite_genres
    }


@router.get("/preferences")
def get_user_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Аналіз вподобань користувача"""
    
    # Отримання всіх оцінок користувача
    ratings = db.query(Rating).filter(Rating.user_id == current_user.id).all()
    
    if not ratings:
        return {
            "genre_preferences": [],
            "emotion_preferences": [],
            "rating_distribution": {}
        }
    
    # Аналіз жанрових вподобань
    genre_ratings = {}
    emotion_ratings = {}
    
    for rating in ratings:
        movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
        if not movie:
            continue
        
        # Жанри
        for genre in movie.genres:
            if genre not in genre_ratings:
                genre_ratings[genre] = []
            genre_ratings[genre].append(rating.rating)
        
        # Емоції
        if movie.emotions:
            for emotion, score in movie.emotions.items():
                if score >= 0.5:  # Тільки значущі емоції
                    if emotion not in emotion_ratings:
                        emotion_ratings[emotion] = []
                    emotion_ratings[emotion].append(rating.rating)
    
    # Обчислення середніх оцінок
    genre_preferences = [
        {
            "genre": genre,
            "average_rating": round(sum(ratings_list) / len(ratings_list), 1),
            "count": len(ratings_list)
        }
        for genre, ratings_list in genre_ratings.items()
    ]
    genre_preferences.sort(key=lambda x: x["average_rating"], reverse=True)
    
    emotion_preferences = [
        {
            "emotion": emotion,
            "average_rating": round(sum(ratings_list) / len(ratings_list), 1),
            "count": len(ratings_list)
        }
        for emotion, ratings_list in emotion_ratings.items()
    ]
    emotion_preferences.sort(key=lambda x: x["average_rating"], reverse=True)
    
    # Розподіл оцінок
    rating_distribution = {
        "1-3": len([r for r in ratings if 1 <= r.rating < 4]),
        "4-6": len([r for r in ratings if 4 <= r.rating < 7]),
        "7-8": len([r for r in ratings if 7 <= r.rating < 9]),
        "9-10": len([r for r in ratings if 9 <= r.rating <= 10])
    }
    
    return {
        "genre_preferences": genre_preferences[:10],
        "emotion_preferences": emotion_preferences[:10],
        "rating_distribution": rating_distribution
    }


@router.get("/history")
def get_viewing_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict]:
    """Історія переглядів користувача"""
    
    history = db.query(ViewingHistory).filter(
        ViewingHistory.user_id == current_user.id
    ).order_by(ViewingHistory.watched_at.desc()).limit(limit).all()
    
    result = []
    for item in history:
        movie = db.query(Movie).filter(Movie.id == item.movie_id).first()
        if movie:
            # Отримання оцінки користувача
            rating = db.query(Rating).filter(
                Rating.user_id == current_user.id,
                Rating.movie_id == movie.id
            ).first()
            
            result.append({
                "movie_id": movie.id,
                "title": movie.title,
                "poster_url": movie.poster_url,
                "genres": movie.genres,
                "watched_at": item.watched_at,
                "completed": item.completed,
                "user_rating": rating.rating if rating else None
            })
    
    return result


@router.get("/analytics")
def get_comprehensive_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отримання повної аналітики для дашборду 2.0"""
    analytics = DashboardAnalytics(db)
    return analytics.get_comprehensive_stats(current_user.id)


@router.get("/achievements")
def get_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отримання досягнень користувача"""
    analytics = DashboardAnalytics(db)
    stats = analytics.get_comprehensive_stats(current_user.id)
    return {"achievements": stats["achievements"]}


@router.get("/goals")
def get_goals_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Прогрес по цілях"""
    analytics = DashboardAnalytics(db)
    stats = analytics.get_comprehensive_stats(current_user.id)
    return {"goals": stats["goals_progress"]}
