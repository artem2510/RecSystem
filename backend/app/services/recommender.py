from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Dict, Tuple, Optional
import numpy as np
from collections import defaultdict
from datetime import datetime

from app.models.user import User
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.viewing_history import ViewingHistory
from app.services.nlp_analyzer import NLPAnalyzer
from app.services.contextual_recommender import ContextualRecommender


class RecommenderSystem:
    """Гібридна рекомендаційна система з контекстуальними факторами"""
    
    def __init__(self, db: Session):
        self.db = db
        self.nlp_analyzer = NLPAnalyzer()
        self.contextual_recommender = ContextualRecommender(db)
        
        # Ваги для гібридного підходу (базові)
        self.content_weight = 0.3
        self.collaborative_weight = 0.3
        self.emotion_weight = 0.15
        self.contextual_weight = 0.25  # Нова вага для контексту
    
    def get_recommendations(
        self, 
        user_id: int, 
        limit: int = 10,
        user_mood: Optional[str] = None,
        weather_condition: Optional[str] = None,
        use_context: bool = True
    ) -> List[Tuple[Movie, float, Dict]]:
        """Отримання персоналізованих рекомендацій з контекстом"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # Отримання фільмів, які користувач вже бачив
        watched_movie_ids = self._get_watched_movies(user_id)
        
        # Отримання всіх фільмів
        all_movies = self.db.query(Movie).filter(
            Movie.id.notin_(watched_movie_ids) if watched_movie_ids else True
        ).all()
        
        if not all_movies:
            return []
        
        # Отримання контекстуальних факторів
        time_context = None
        day_context = None
        mood_context = None
        weather_context = None
        
        if use_context:
            current_time = datetime.now()
            time_context = self.contextual_recommender.get_time_of_day_context(current_time)
            day_context = self.contextual_recommender.get_day_of_week_context(current_time)
            
            if user_mood:
                mood_context = self.contextual_recommender.get_mood_context(user_mood)
            
            if weather_condition:
                weather_context = self.contextual_recommender.get_weather_context(weather_condition)
        
        # Обчислення скорів для кожного фільму
        movie_scores = []
        for movie in all_movies:
            score, explanation = self._calculate_hybrid_score(
                user_id, 
                movie,
                time_context=time_context,
                day_context=day_context,
                mood_context=mood_context,
                weather_context=weather_context
            )
            movie_scores.append((movie, score, explanation))
        
        # Сортування за скором
        movie_scores.sort(key=lambda x: x[1], reverse=True)
        
        return movie_scores[:limit]
    
    def _get_watched_movies(self, user_id: int) -> List[int]:
        """Отримання ID переглянутих фільмів"""
        watched = self.db.query(ViewingHistory.movie_id).filter(
            ViewingHistory.user_id == user_id
        ).all()
        return [m[0] for m in watched]
    
    def _calculate_hybrid_score(
        self, 
        user_id: int, 
        movie: Movie,
        time_context: Optional[Dict] = None,
        day_context: Optional[Dict] = None,
        mood_context: Optional[Dict] = None,
        weather_context: Optional[Dict] = None
    ) -> Tuple[float, Dict]:
        """Обчислення гібридного скору з контекстом"""
        content_score = self._content_based_score(user_id, movie)
        collaborative_score = self._collaborative_score(user_id, movie)
        emotion_score = self._emotion_based_score(user_id, movie)
        
        # Контекстуальний скор
        contextual_score = 0.5  # За замовчуванням нейтральний
        if any([time_context, day_context, mood_context, weather_context]):
            contextual_score = self.contextual_recommender.calculate_contextual_score(
                movie,
                time_context=time_context,
                day_context=day_context,
                mood_context=mood_context,
                weather_context=weather_context
            )
        
        # Зважене комбінування
        final_score = (
            content_score * self.content_weight +
            collaborative_score * self.collaborative_weight +
            emotion_score * self.emotion_weight +
            contextual_score * self.contextual_weight
        )
        
        # Пояснення
        explanation = {
            "content_score": round(content_score, 2),
            "collaborative_score": round(collaborative_score, 2),
            "emotion_score": round(emotion_score, 2),
            "contextual_score": round(contextual_score, 2),
            "final_score": round(final_score, 2),
            "contextual_factors": self.contextual_recommender.get_contextual_explanation(
                time_context, day_context, mood_context, weather_context
            )
        }
        
        return final_score, explanation
    
    def _content_based_score(self, user_id: int, movie: Movie) -> float:
        """Контентна фільтрація на основі жанрів та описів"""
        # Отримання улюблених жанрів користувача
        user_ratings = self.db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.rating >= 7.0
        ).all()
        
        if not user_ratings:
            return 0.5  # Нейтральний скор
        
        # Збір жанрів з високо оцінених фільмів
        favorite_genres = []
        for rating in user_ratings:
            rated_movie = self.db.query(Movie).filter(Movie.id == rating.movie_id).first()
            if rated_movie and rated_movie.genres:
                favorite_genres.extend(rated_movie.genres)
        
        if not favorite_genres:
            return 0.5
        
        # Обчислення схожості жанрів
        genre_overlap = len(set(movie.genres) & set(favorite_genres))
        max_overlap = min(len(movie.genres), len(favorite_genres))
        
        if max_overlap == 0:
            return 0.3
        
        genre_score = genre_overlap / max_overlap
        return min(genre_score, 1.0)
    
    def _collaborative_score(self, user_id: int, movie: Movie) -> float:
        """Колаборативна фільтрація"""
        # Знаходження схожих користувачів
        similar_users = self._find_similar_users(user_id, limit=10)
        
        if not similar_users:
            # Якщо немає схожих користувачів, використовуємо середній рейтинг
            return movie.average_rating / 10.0 if movie.average_rating else 0.5
        
        # Отримання оцінок схожих користувачів для цього фільму
        ratings = self.db.query(Rating).filter(
            and_(
                Rating.movie_id == movie.id,
                Rating.user_id.in_([u[0] for u in similar_users])
            )
        ).all()
        
        if not ratings:
            return 0.5
        
        # Зважений середній рейтинг
        weighted_sum = sum(r.rating * similar_users[[u[0] for u in similar_users].index(r.user_id)][1] 
                          for r in ratings)
        weight_sum = sum(similar_users[[u[0] for u in similar_users].index(r.user_id)][1] 
                        for r in ratings)
        
        if weight_sum == 0:
            return 0.5
        
        avg_rating = weighted_sum / weight_sum
        return min(avg_rating / 10.0, 1.0)
    
    def _emotion_based_score(self, user_id: int, movie: Movie) -> float:
        """Оцінка на основі емоційних характеристик"""
        # Отримання емоційних вподобань користувача
        user_ratings = self.db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.rating >= 7.0
        ).all()
        
        if not user_ratings or not movie.emotions:
            return 0.5
        
        # Збір емоцій з високо оцінених фільмів
        user_emotions = defaultdict(list)
        for rating in user_ratings:
            rated_movie = self.db.query(Movie).filter(Movie.id == rating.movie_id).first()
            if rated_movie and rated_movie.emotions:
                for emotion, score in rated_movie.emotions.items():
                    user_emotions[emotion].append(score)
        
        if not user_emotions:
            return 0.5
        
        # Обчислення середніх емоційних вподобань
        avg_user_emotions = {
            emotion: np.mean(scores) 
            for emotion, scores in user_emotions.items()
        }
        
        # Обчислення схожості емоцій
        similarity_scores = []
        for emotion, movie_score in movie.emotions.items():
            if emotion in avg_user_emotions:
                diff = abs(movie_score - avg_user_emotions[emotion])
                similarity = 1 - diff
                similarity_scores.append(similarity)
        
        if not similarity_scores:
            return 0.5
        
        return np.mean(similarity_scores)
    
    def _find_similar_users(self, user_id: int, limit: int = 10) -> List[Tuple[int, float]]:
        """Знаходження схожих користувачів"""
        # Отримання оцінок поточного користувача
        user_ratings = self.db.query(Rating).filter(Rating.user_id == user_id).all()
        
        if not user_ratings:
            return []
        
        user_movie_ratings = {r.movie_id: r.rating for r in user_ratings}
        
        # Отримання всіх інших користувачів
        other_users = self.db.query(User).filter(User.id != user_id).all()
        
        similarities = []
        for other_user in other_users:
            other_ratings = self.db.query(Rating).filter(
                Rating.user_id == other_user.id
            ).all()
            
            if not other_ratings:
                continue
            
            other_movie_ratings = {r.movie_id: r.rating for r in other_ratings}
            
            # Знаходження спільних фільмів
            common_movies = set(user_movie_ratings.keys()) & set(other_movie_ratings.keys())
            
            if len(common_movies) < 2:
                continue
            
            # Обчислення кореляції Пірсона
            user_ratings_list = [user_movie_ratings[m] for m in common_movies]
            other_ratings_list = [other_movie_ratings[m] for m in common_movies]
            
            correlation = np.corrcoef(user_ratings_list, other_ratings_list)[0, 1]
            
            if not np.isnan(correlation):
                similarities.append((other_user.id, correlation))
        
        # Сортування за схожістю
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:limit]
