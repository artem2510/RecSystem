"""
API endpoints для аналізу емоцій та емоційного профілю
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.schemas.movie import MovieResponse
from app.api.deps import get_current_user
from app.services.emotion_analyzer import EmotionAnalyzer
from app.services.emotion_journey import EmotionJourney

router = APIRouter(prefix="/emotions", tags=["Emotions"])


@router.get("/profile")
def get_emotion_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отримання емоційного профілю користувача"""
    analyzer = EmotionAnalyzer(db)
    profile = analyzer.get_user_emotion_profile(current_user.id)
    
    return profile


@router.get("/trajectory")
def get_emotion_trajectory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Емоційна траєкторія - зміна вподобань у часі"""
    analyzer = EmotionAnalyzer(db)
    trajectory = analyzer.get_emotion_trajectory(current_user.id)
    
    return {
        "trajectory": trajectory,
        "periods_count": len(trajectory)
    }


@router.get("/recommendations/{emotion}", response_model=List[MovieResponse])
def get_emotion_based_recommendations(
    emotion: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Рекомендації фільмів за конкретною емоцією"""
    analyzer = EmotionAnalyzer(db)
    
    # Перевірка валідності емоції
    valid_emotions = [
        "оптимістичний", "драматичний", "напружений",
        "романтичний", "жахливий", "пригодницький"
    ]
    
    if emotion not in valid_emotions:
        raise HTTPException(
            status_code=400,
            detail=f"Невалідна емоція. Доступні: {', '.join(valid_emotions)}"
        )
    
    movies = analyzer.get_emotion_recommendations(current_user.id, emotion)
    
    return [MovieResponse.model_validate(m) for m in movies[:limit]]


@router.get("/contrast/{movie_id}", response_model=Optional[MovieResponse])
def get_contrast_recommendation(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Контраст-рекомендація: фільм з протилежними емоціями"""
    analyzer = EmotionAnalyzer(db)
    movie = analyzer.get_emotion_contrast_recommendation(current_user.id, movie_id)
    
    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Не вдалося знайти контрастну рекомендацію"
        )
    
    return MovieResponse.model_validate(movie)


@router.get("/available")
def get_available_emotions():
    """Список доступних емоцій для аналізу"""
    return {
        "emotions": [
            {
                "value": "оптимістичний",
                "label": "Оптимістичний",
                "emoji": "😊",
                "color": "#FFD700",
                "description": "Веселі та позитивні фільми"
            },
            {
                "value": "драматичний",
                "label": "Драматичний",
                "emoji": "😢",
                "color": "#4169E1",
                "description": "Глибокі емоційні переживання"
            },
            {
                "value": "напружений",
                "label": "Напружений",
                "emoji": "😰",
                "color": "#FF4500",
                "description": "Захоплюючі та напружені моменти"
            },
            {
                "value": "романтичний",
                "label": "Романтичний",
                "emoji": "💕",
                "color": "#FF69B4",
                "description": "Любовні історії та емоційні зв'язки"
            },
            {
                "value": "жахливий",
                "label": "Жахливий",
                "emoji": "👻",
                "color": "#8B0000",
                "description": "Моторошні та лякаючі фільми"
            },
            {
                "value": "пригодницький",
                "label": "Пригодницький",
                "emoji": "🗺️",
                "color": "#32CD32",
                "description": "Епічні подорожі та пригоди"
            }
        ]
    }


@router.get("/journey/templates")
def get_journey_templates(
    db: Session = Depends(get_db)
):
    """Отримання всіх шаблонів емоційних подорожей"""
    journey = EmotionJourney(db)
    templates = journey.get_all_templates()
    
    return {"templates": templates}


@router.post("/journey/create")
def create_emotion_journey(
    template_key: str = Query(..., description="Ключ шаблону подорожі"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Створення емоційної подорожі (Mood Playlist)"""
    journey_service = EmotionJourney(db)
    
    try:
        journey = journey_service.create_journey(current_user.id, template_key)
        
        # Серіалізуємо movie об'єкти в плейлисті
        if journey.get("playlist"):
            journey["playlist"] = [
                {
                    "movie": MovieResponse.model_validate(item["movie"]),
                    "emotion": item["emotion"],
                    "position": item["position"]
                }
                for item in journey["playlist"]
            ]
        
        return journey
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/journey/custom")
def create_custom_journey(
    emotions: List[str] = Query(..., description="Послідовність емоцій"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Створення кастомної емоційної подорожі"""
    journey_service = EmotionJourney(db)
    
    journey = journey_service.create_journey(
        current_user.id, 
        None, 
        custom_sequence=emotions
    )
    
    # Серіалізуємо movie об'єкти в плейлисті
    if journey.get("playlist"):
        journey["playlist"] = [
            {
                "movie": MovieResponse.model_validate(item["movie"]),
                "emotion": item["emotion"],
                "position": item["position"]
            }
            for item in journey["playlist"]
        ]
    
    return journey


@router.get("/journey/contrast/{movie_id}")
def get_contrast_journey(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Контрастна подорож після конкретного фільму"""
    journey_service = EmotionJourney(db)
    journey = journey_service.get_contrast_journey(current_user.id, movie_id)
    
    # Серіалізуємо movie об'єкти в плейлисті
    if journey.get("playlist"):
        journey["playlist"] = [
            {
                "movie": MovieResponse.model_validate(item["movie"]),
                "emotion": item["emotion"],
                "position": item["position"]
            }
            for item in journey["playlist"]
        ]
    
    return journey
