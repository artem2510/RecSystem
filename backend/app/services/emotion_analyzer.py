"""
Сервіс для аналізу емоційного профілю користувача
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Optional
from collections import defaultdict
import numpy as np

from app.models.user import User
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.viewing_history import ViewingHistory


class EmotionAnalyzer:
    """Аналіз емоційного профілю та вподобань користувача"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Базові емоції для аналізу
        self.base_emotions = [
            "оптимістичний",
            "драматичний",
            "напружений",
            "романтичний",
            "жахливий",
            "пригодницький"
        ]
    
    def get_user_emotion_profile(self, user_id: int) -> Dict:
        """Отримання емоційного профілю користувача"""
        # Отримання високо оцінених фільмів
        high_rated_movies = self.db.query(Movie).join(Rating).filter(
            Rating.user_id == user_id,
            Rating.rating >= 7.0
        ).all()
        
        if not high_rated_movies:
            return self._get_empty_profile()
        
        # Збір емоцій з усіх фільмів
        emotion_scores = defaultdict(list)
        for movie in high_rated_movies:
            if movie.emotions:
                for emotion, score in movie.emotions.items():
                    if emotion in self.base_emotions:
                        emotion_scores[emotion].append(score)
        
        # Обчислення середніх значень
        avg_emotions = {}
        for emotion in self.base_emotions:
            if emotion in emotion_scores:
                avg_emotions[emotion] = round(np.mean(emotion_scores[emotion]), 2)
            else:
                avg_emotions[emotion] = 0.0
        
        # Визначення домінуючих емоцій
        sorted_emotions = sorted(avg_emotions.items(), key=lambda x: x[1], reverse=True)
        dominant_emotions = [e[0] for e in sorted_emotions[:3] if e[1] > 0.3]
        
        # Визначення емоційного типу
        emotion_type = self._determine_emotion_type(avg_emotions, dominant_emotions)
        
        # Аналіз емоційної різноманітності
        emotion_diversity = self._calculate_emotion_diversity(avg_emotions)
        
        return {
            "emotions": avg_emotions,
            "dominant_emotions": dominant_emotions,
            "emotion_type": emotion_type,
            "diversity_score": emotion_diversity,
            "total_movies_analyzed": len(high_rated_movies),
            "description": self._generate_profile_description(emotion_type, dominant_emotions)
        }
    
    def get_emotion_trajectory(self, user_id: int) -> List[Dict]:
        """Емоційна траєкторія - зміна емоційних вподобань у часі"""
        # Отримання оцінок з часовими мітками
        ratings = self.db.query(Rating).filter(
            Rating.user_id == user_id
        ).order_by(Rating.created_at).all()
        
        if len(ratings) < 5:
            return []
        
        # Розбиваємо на періоди (по 10 фільмів)
        trajectory = []
        chunk_size = 10
        
        for i in range(0, len(ratings), chunk_size):
            chunk = ratings[i:i + chunk_size]
            
            # Збір емоцій для цього періоду
            period_emotions = defaultdict(list)
            for rating in chunk:
                movie = self.db.query(Movie).filter(Movie.id == rating.movie_id).first()
                if movie and movie.emotions:
                    for emotion, score in movie.emotions.items():
                        if emotion in self.base_emotions:
                            period_emotions[emotion].append(score)
            
            # Середні значення для періоду
            avg_period_emotions = {}
            for emotion in self.base_emotions:
                if emotion in period_emotions:
                    avg_period_emotions[emotion] = round(np.mean(period_emotions[emotion]), 2)
                else:
                    avg_period_emotions[emotion] = 0.0
            
            trajectory.append({
                "period": i // chunk_size + 1,
                "movies_count": len(chunk),
                "emotions": avg_period_emotions,
                "timestamp": chunk[-1].created_at.isoformat() if chunk[-1].created_at else None
            })
        
        return trajectory
    
    def get_emotion_recommendations(self, user_id: int, target_emotion: str) -> List[Movie]:
        """Рекомендації фільмів за конкретною емоцією"""
        if target_emotion not in self.base_emotions:
            return []
        
        # Отримання фільмів, які користувач ще не бачив
        watched_movie_ids = self.db.query(ViewingHistory.movie_id).filter(
            ViewingHistory.user_id == user_id
        ).all()
        watched_ids = [m[0] for m in watched_movie_ids]
        
        # Пошук фільмів з високим скором цієї емоції
        all_movies = self.db.query(Movie).filter(
            Movie.id.notin_(watched_ids) if watched_ids else True
        ).all()
        
        # Фільтрація та сортування за емоційним скором
        emotion_movies = []
        for movie in all_movies:
            if movie.emotions and target_emotion in movie.emotions:
                emotion_score = movie.emotions[target_emotion]
                if emotion_score >= 0.5:  # Мінімальний поріг
                    emotion_movies.append((movie, emotion_score))
        
        # Сортування за емоційним скором та рейтингом
        emotion_movies.sort(key=lambda x: (x[1], x[0].average_rating), reverse=True)
        
        return [movie for movie, _ in emotion_movies[:10]]
    
    def get_emotion_contrast_recommendation(self, user_id: int, last_movie_id: int) -> Optional[Movie]:
        """Контраст-рекомендація: фільм з протилежними емоціями"""
        last_movie = self.db.query(Movie).filter(Movie.id == last_movie_id).first()
        
        if not last_movie or not last_movie.emotions:
            return None
        
        # Визначаємо домінуючу емоцію останнього фільму
        dominant_emotion = max(last_movie.emotions.items(), key=lambda x: x[1])
        
        # Карта протилежних емоцій
        opposite_emotions = {
            "оптимістичний": "драматичний",
            "драматичний": "оптимістичний",
            "напружений": "романтичний",
            "романтичний": "напружений",
            "жахливий": "оптимістичний",
            "пригодницький": "драматичний"
        }
        
        target_emotion = opposite_emotions.get(dominant_emotion[0])
        
        if not target_emotion:
            return None
        
        # Знаходимо фільм з протилежною емоцією
        recommendations = self.get_emotion_recommendations(user_id, target_emotion)
        
        return recommendations[0] if recommendations else None
    
    def _get_empty_profile(self) -> Dict:
        """Порожній профіль для нових користувачів"""
        return {
            "emotions": {emotion: 0.0 for emotion in self.base_emotions},
            "dominant_emotions": [],
            "emotion_type": "Новачок",
            "diversity_score": 0.0,
            "total_movies_analyzed": 0,
            "description": "Оцініть більше фільмів, щоб ми могли визначити ваш емоційний профіль"
        }
    
    def _determine_emotion_type(self, emotions: Dict, dominant: List[str]) -> str:
        """Визначення емоційного типу користувача"""
        if not dominant:
            return "Збалансований"
        
        # Типи на основі домінуючих емоцій
        emotion_types = {
            ("оптимістичний",): "Оптиміст",
            ("драматичний",): "Меланхолік",
            ("напружений",): "Адреналіновий наркоман",
            ("романтичний",): "Романтик",
            ("жахливий",): "Любитель гострих відчуттів",
            ("пригодницький",): "Шукач пригод",
            ("оптимістичний", "романтичний"): "Романтичний оптиміст",
            ("драматичний", "романтичний"): "Чутлива душа",
            ("напружений", "пригодницький"): "Шукач адреналіну",
            ("оптимістичний", "пригодницький"): "Веселий авантюрист",
        }
        
        # Перевірка комбінацій
        for combo, type_name in emotion_types.items():
            if all(e in dominant for e in combo):
                return type_name
        
        # За замовчуванням
        return f"Любитель {dominant[0]}"
    
    def _calculate_emotion_diversity(self, emotions: Dict) -> float:
        """Розрахунок різноманітності емоційних вподобань"""
        values = list(emotions.values())
        
        if not values or max(values) == 0:
            return 0.0
        
        # Ентропія як міра різноманітності
        total = sum(values)
        if total == 0:
            return 0.0
        
        probabilities = [v / total for v in values if v > 0]
        entropy = -sum(p * np.log2(p) for p in probabilities)
        
        # Нормалізація (максимальна ентропія для 6 емоцій = log2(6) ≈ 2.58)
        max_entropy = np.log2(len(self.base_emotions))
        diversity = entropy / max_entropy if max_entropy > 0 else 0.0
        
        return round(diversity, 2)
    
    def _generate_profile_description(self, emotion_type: str, dominant: List[str]) -> str:
        """Генерація опису емоційного профілю"""
        if not dominant:
            return "Ваші вподобання ще формуються. Продовжуйте дивитись фільми!"
        
        descriptions = {
            "Оптиміст": "Ви любите фільми, які піднімають настрій та надихають на позитив",
            "Меланхолік": "Ви цінуєте глибокі емоційні переживання та драматичні історії",
            "Адреналіновий наркоман": "Вас приваблюють напружені та захоплюючі фільми",
            "Романтик": "Ви шукаєте любовні історії та емоційні зв'язки",
            "Любитель гострих відчуттів": "Ви обожнюєте фільми, що лякають та хвилюють",
            "Шукач пригод": "Ви мрієте про епічні подорожі та героїчні пригоди",
            "Романтичний оптиміст": "Ви любите світлі любовні історії з щасливим кінцем",
            "Чутлива душа": "Ви цінуєте глибокі емоційні зв'язки та романтичні драми",
            "Шукач адреналіну": "Ви обожнюєте динамічні пригоди, повні небезпек",
            "Веселий авантюрист": "Ви любите легкі пригодницькі фільми з гумором"
        }
        
        return descriptions.get(emotion_type, f"Ви - {emotion_type}, з унікальним поєднанням вподобань")
