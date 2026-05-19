from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.recommendation import RecommendationResponse, ExplanationResponse
from app.schemas.movie import MovieResponse
from app.models.user import User
from app.models.movie import Movie
from app.api.deps import get_current_user
from app.services.recommender import RecommenderSystem
from app.services.explainer import ExplainableAI

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("", response_model=List[RecommendationResponse])
def get_recommendations(
    limit: int = 10,
    mood: Optional[str] = Query(None, description="Настрій користувача (happy, sad, stressed, bored, romantic, adventurous, thoughtful)"),
    weather: Optional[str] = Query(None, description="Погодні умови (rain, clear, clouds, snow)"),
    use_context: bool = Query(True, description="Використовувати контекстуальні фактори"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отримання персоналізованих рекомендацій з контекстом"""
    recommender = RecommenderSystem(db)
    explainer = ExplainableAI(db)
    
    # Отримання рекомендацій з контекстуальними факторами
    recommendations = recommender.get_recommendations(
        current_user.id, 
        limit,
        user_mood=mood,
        weather_condition=weather,
        use_context=use_context
    )
    
    # Формування відповіді з поясненнями
    result = []
    for movie, score, explanation_data in recommendations:
        # Генерація пояснень
        explanations = explainer.explain_recommendation(
            current_user.id, 
            movie, 
            explanation_data
        )
        
        result.append(RecommendationResponse(
            movie=MovieResponse.model_validate(movie),
            score=score,
            explanations=[
                ExplanationResponse(**exp) for exp in explanations
            ]
        ))
    
    return result


@router.get("/explain/{movie_id}", response_model=List[ExplanationResponse])
def explain_movie_recommendation(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отримання пояснення чому рекомендовано конкретний фільм"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фільм не знайдено")
    
    recommender = RecommenderSystem(db)
    explainer = ExplainableAI(db)
    
    # Обчислення скорів для фільму
    score, explanation_data = recommender._calculate_hybrid_score(current_user.id, movie)
    
    # Генерація пояснень
    explanations = explainer.explain_recommendation(
        current_user.id, 
        movie, 
        explanation_data
    )
    
    return [ExplanationResponse(**exp) for exp in explanations]


@router.get("/explain-why-not/{movie_id}")
def explain_why_not_recommended(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Детальний аналіз збігу фільму з вподобаннями користувача"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фільм не знайдено")
    
    recommender = RecommenderSystem(db)
    explainer = ExplainableAI(db)
    
    # Обчислення скорів
    score, explanation_data = recommender._calculate_hybrid_score(current_user.id, movie)
    
    # Детальний аналіз
    analysis = explainer.explain_why_not(current_user.id, movie, explanation_data)
    
    return analysis


@router.get("/counterfactual/{movie_id}")
def get_counterfactual_explanation(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Контр-фактичні пояснення: 'Що якби?'"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фільм не знайдено")
    
    recommender = RecommenderSystem(db)
    explainer = ExplainableAI(db)
    
    # Обчислення скорів
    score, explanation_data = recommender._calculate_hybrid_score(current_user.id, movie)
    
    counterfactual = explainer.explain_counterfactual(current_user.id, movie, explanation_data)
    
    return {
        "counterfactual": counterfactual,
        "movie_id": movie_id,
        "movie_title": movie.title
    }


@router.get("/alternatives/{movie_id}")
def get_alternative_recommendations(
    movie_id: int,
    reason: str = Query("different_logic", description="Причина пошуку альтернатив"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Альтернативні рекомендації з поясненнями"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фільм не знайдено")
    
    explainer = ExplainableAI(db)
    alternatives_with_reasons = explainer.get_alternative_recommendations(current_user.id, movie, reason)
    
    # Повертаємо фільми з поясненнями
    return [
        {
            "movie": MovieResponse.model_validate(alt["movie"]),
            "reason": alt["reason"],
            "alternative_type": alt["alternative_type"]
        }
        for alt in alternatives_with_reasons
    ]


@router.get("/similar/{movie_id}", response_model=List[MovieResponse])
def get_similar_movies(
    movie_id: int,
    db: Session = Depends(get_db)
):
    """Отримання схожих фільмів"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Фільм не знайдено")
    
    # Пошук фільмів зі схожими жанрами
    similar_movies = db.query(Movie).filter(
        Movie.id != movie_id
    ).all()
    
    # Обчислення схожості за жанрами
    scored_movies = []
    for similar_movie in similar_movies:
        common_genres = set(movie.genres) & set(similar_movie.genres)
        if common_genres:
            score = len(common_genres) / max(len(movie.genres), len(similar_movie.genres))
            scored_movies.append((similar_movie, score))
    
    # Сортування за схожістю
    scored_movies.sort(key=lambda x: x[1], reverse=True)
    
    result = [MovieResponse.model_validate(m) for m, _ in scored_movies[:limit]]
    return result


@router.get("/quick-pick", response_model=RecommendationResponse)
def get_quick_pick(
    mood: Optional[str] = Query(None, description="Ваш настрій"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Швидкий вибір 'Фільм на вечір' - одна найкраща рекомендація"""
    recommender = RecommenderSystem(db)
    explainer = ExplainableAI(db)
    
    # Отримуємо топ-1 рекомендацію з контекстом
    recommendations = recommender.get_recommendations(
        current_user.id, 
        limit=1,
        user_mood=mood,
        use_context=True
    )
    
    if not recommendations:
        raise HTTPException(status_code=404, detail="Не вдалося знайти рекомендацію")
    
    movie, score, explanation_data = recommendations[0]
    
    # Генерація пояснень
    explanations = explainer.explain_recommendation(
        current_user.id, 
        movie, 
        explanation_data
    )
    
    return RecommendationResponse(
        movie=MovieResponse.model_validate(movie),
        score=score,
        explanations=[ExplanationResponse(**exp) for exp in explanations]
    )


@router.get("/moods")
def get_available_moods():
    """Отримання списку доступних настроїв"""
    return {
        "moods": [
            {"value": "happy", "label": "Щасливий 😊", "emoji": "😊"},
            {"value": "sad", "label": "Сумний 😢", "emoji": "😢"},
            {"value": "stressed", "label": "Стресовий 😰", "emoji": "😰"},
            {"value": "bored", "label": "Нудно 😑", "emoji": "😑"},
            {"value": "romantic", "label": "Романтичний 💕", "emoji": "💕"},
            {"value": "adventurous", "label": "Пригодницький 🗺️", "emoji": "🗺️"},
            {"value": "thoughtful", "label": "Задумливий 🤔", "emoji": "🤔"},
            {"value": "scared", "label": "Моторошно 👻", "emoji": "👻"}
        ]
    }
