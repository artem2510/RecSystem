"""
Розширена аналітика для персонального дашборду
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Dict, List
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import numpy as np

from app.models.user import User
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.viewing_history import ViewingHistory


class DashboardAnalytics:
    """Розширена аналітика для дашборду користувача"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_comprehensive_stats(self, user_id: int) -> Dict:
        """Отримання всієї статистики користувача"""
        return {
            "basic_stats": self._get_basic_stats(user_id),
            "timeline_stats": self._get_timeline_stats(user_id),
            "genre_distribution": self._get_genre_distribution(user_id),
            "rating_trends": self._get_rating_trends(user_id),
            "achievements": self._get_achievements(user_id),
            "social_metrics": self._get_social_metrics(user_id),
            "predictions": self._get_predictions(user_id),
            "goals_progress": self._get_goals_progress(user_id)
        }
    
    def _get_basic_stats(self, user_id: int) -> Dict:
        """Базова статистика"""
        ratings_count = self.db.query(Rating).filter(Rating.user_id == user_id).count()
        views_count = self.db.query(ViewingHistory).filter(ViewingHistory.user_id == user_id).count()
        
        avg_rating = self.db.query(func.avg(Rating.rating)).filter(
            Rating.user_id == user_id
        ).scalar() or 0.0
        
        # Улюблений жанр
        user_ratings = self.db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.rating >= 7.0
        ).all()
        
        genres = []
        for rating in user_ratings:
            movie = self.db.query(Movie).filter(Movie.id == rating.movie_id).first()
            if movie and movie.genres:
                genres.extend(movie.genres)
        
        favorite_genre = Counter(genres).most_common(1)[0][0] if genres else "Немає"
        
        return {
            "ratings_count": ratings_count,
            "views_count": views_count,
            "average_rating": round(avg_rating, 1),
            "favorite_genre": favorite_genre,
            "total_watch_time": self._calculate_total_watch_time(user_id)
        }
    
    def _get_timeline_stats(self, user_id: int) -> Dict:
        """Статистика в часі (останні 12 місяців)"""
        now = datetime.now()
        twelve_months_ago = now - timedelta(days=365)
        
        # Рейтинги по місяцях
        ratings = self.db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.created_at >= twelve_months_ago
        ).all()
        
        monthly_data = defaultdict(lambda: {"count": 0, "avg_rating": []})
        
        for rating in ratings:
            if rating.created_at:
                month_key = rating.created_at.strftime("%Y-%m")
                monthly_data[month_key]["count"] += 1
                monthly_data[month_key]["avg_rating"].append(rating.rating)
        
        timeline = []
        for i in range(12):
            date = now - timedelta(days=30 * i)
            month_key = date.strftime("%Y-%m")
            data = monthly_data.get(month_key, {"count": 0, "avg_rating": []})
            
            timeline.append({
                "month": date.strftime("%b %Y"),
                "ratings_count": data["count"],
                "average_rating": round(np.mean(data["avg_rating"]), 1) if data["avg_rating"] else 0
            })
        
        timeline.reverse()
        return {"timeline": timeline}
    
    def _get_genre_distribution(self, user_id: int) -> Dict:
        """Розподіл жанрів"""
        user_ratings = self.db.query(Rating).filter(Rating.user_id == user_id).all()
        
        genre_stats = defaultdict(lambda: {"count": 0, "total_rating": 0})
        
        for rating in user_ratings:
            movie = self.db.query(Movie).filter(Movie.id == rating.movie_id).first()
            if movie and movie.genres:
                for genre in movie.genres:
                    genre_stats[genre]["count"] += 1
                    genre_stats[genre]["total_rating"] += rating.rating
        
        distribution = []
        for genre, stats in genre_stats.items():
            distribution.append({
                "genre": genre,
                "count": stats["count"],
                "average_rating": round(stats["total_rating"] / stats["count"], 1)
            })
        
        distribution.sort(key=lambda x: x["count"], reverse=True)
        return {"genres": distribution[:10]}
    
    def _get_rating_trends(self, user_id: int) -> Dict:
        """Тренди оцінок"""
        ratings = self.db.query(Rating).filter(
            Rating.user_id == user_id
        ).order_by(Rating.created_at).all()
        
        if len(ratings) < 10:
            return {"trend": "insufficient_data", "direction": "neutral"}
        
        # Беремо останні 20 оцінок
        recent_ratings = [r.rating for r in ratings[-20:]]
        older_ratings = [r.rating for r in ratings[-40:-20]] if len(ratings) >= 40 else recent_ratings
        
        recent_avg = np.mean(recent_ratings)
        older_avg = np.mean(older_ratings)
        
        if recent_avg > older_avg + 0.5:
            trend = "increasing"
            description = "Ви стали оцінювати фільми вище"
        elif recent_avg < older_avg - 0.5:
            trend = "decreasing"
            description = "Ви стали більш критичними"
        else:
            trend = "stable"
            description = "Ваші оцінки стабільні"
        
        return {
            "trend": trend,
            "description": description,
            "recent_average": round(recent_avg, 1),
            "older_average": round(older_avg, 1)
        }
    
    def _get_achievements(self, user_id: int) -> List[Dict]:
        """Система досягнень"""
        achievements = []
        
        ratings_count = self.db.query(Rating).filter(Rating.user_id == user_id).count()
        views_count = self.db.query(ViewingHistory).filter(ViewingHistory.user_id == user_id).count()
        
        # Досягнення за кількість оцінок
        if ratings_count >= 100:
            achievements.append({
                "id": "critic_master",
                "title": "Майстер-критик",
                "description": "Оцінено 100+ фільмів",
                "icon": "🏆",
                "unlocked": True,
                "progress": 100
            })
        elif ratings_count >= 50:
            achievements.append({
                "id": "critic_pro",
                "title": "Професійний критик",
                "description": "Оцінено 50+ фільмів",
                "icon": "🥇",
                "unlocked": True,
                "progress": 100
            })
        elif ratings_count >= 10:
            achievements.append({
                "id": "critic_beginner",
                "title": "Початківець критик",
                "description": "Оцінено 10+ фільмів",
                "icon": "🥉",
                "unlocked": True,
                "progress": 100
            })
        else:
            achievements.append({
                "id": "critic_beginner",
                "title": "Початківець критик",
                "description": "Оцініть 10 фільмів",
                "icon": "🥉",
                "unlocked": False,
                "progress": (ratings_count / 10) * 100
            })
        
        # Досягнення за різноманітність жанрів
        user_ratings = self.db.query(Rating).filter(Rating.user_id == user_id).all()
        unique_genres = set()
        for rating in user_ratings:
            movie = self.db.query(Movie).filter(Movie.id == rating.movie_id).first()
            if movie and movie.genres:
                unique_genres.update(movie.genres)
        
        if len(unique_genres) >= 10:
            achievements.append({
                "id": "genre_explorer",
                "title": "Дослідник жанрів",
                "description": f"Переглянуто {len(unique_genres)} різних жанрів",
                "icon": "🎭",
                "unlocked": True,
                "progress": 100
            })
        
        # Досягнення за марафон
        if views_count >= 50:
            achievements.append({
                "id": "marathon_runner",
                "title": "Марафонець",
                "description": "Переглянуто 50+ фільмів",
                "icon": "🏃",
                "unlocked": True,
                "progress": 100
            })
        
        # Досягнення за високі оцінки
        high_ratings = self.db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.rating >= 9.0
        ).count()
        
        if high_ratings >= 20:
            achievements.append({
                "id": "optimist",
                "title": "Оптиміст",
                "description": "Поставлено 20+ оцінок 9+",
                "icon": "😊",
                "unlocked": True,
                "progress": 100
            })
        
        return achievements
    
    def _get_social_metrics(self, user_id: int) -> Dict:
        """Соціальні метрики"""
        # Середня оцінка користувача
        user_avg = self.db.query(func.avg(Rating.rating)).filter(
            Rating.user_id == user_id
        ).scalar() or 0.0
        
        # Середня оцінка всіх користувачів
        global_avg = self.db.query(func.avg(Rating.rating)).scalar() or 0.0
        
        # Порівняння
        difference = user_avg - global_avg
        if difference > 0.5:
            comparison = "Ви оцінюєте фільми вище за середнього користувача"
        elif difference < -0.5:
            comparison = "Ви більш критичні за середнього користувача"
        else:
            comparison = "Ваші оцінки близькі до середніх"
        
        # Унікальність смаків
        user_ratings = self.db.query(Rating).filter(Rating.user_id == user_id).all()
        unique_movies = 0
        
        for rating in user_ratings:
            # Фільми, які мало хто оцінив
            ratings_count = self.db.query(Rating).filter(Rating.movie_id == rating.movie_id).count()
            if ratings_count <= 5:
                unique_movies += 1
        
        uniqueness_score = (unique_movies / len(user_ratings) * 100) if user_ratings else 0
        
        return {
            "user_average": round(user_avg, 1),
            "global_average": round(global_avg, 1),
            "comparison": comparison,
            "uniqueness_score": round(uniqueness_score, 1),
            "uniqueness_description": self._get_uniqueness_description(uniqueness_score)
        }
    
    def _get_predictions(self, user_id: int) -> Dict:
        """Предиктивна аналітика"""
        # Аналіз останніх 30 днів
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        recent_views = self.db.query(ViewingHistory).filter(
            ViewingHistory.user_id == user_id,
            ViewingHistory.watched_at >= thirty_days_ago
        ).count()
        
        # Прогноз на наступний місяць
        predicted_views = recent_views  # Проста екстраполяція
        
        # Аналіз трендів жанрів
        recent_ratings = self.db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.created_at >= thirty_days_ago
        ).all()
        
        recent_genres = []
        for rating in recent_ratings:
            movie = self.db.query(Movie).filter(Movie.id == rating.movie_id).first()
            if movie and movie.genres:
                recent_genres.extend(movie.genres)
        
        trending_genre = Counter(recent_genres).most_common(1)[0][0] if recent_genres else None
        
        return {
            "predicted_monthly_views": predicted_views,
            "trending_genre": trending_genre,
            "trend_description": f"Ваш інтерес до жанру '{trending_genre}' зростає" if trending_genre else "Недостатньо даних"
        }
    
    def _get_goals_progress(self, user_id: int) -> List[Dict]:
        """Прогрес по цілях"""
        ratings_count = self.db.query(Rating).filter(Rating.user_id == user_id).count()
        views_count = self.db.query(ViewingHistory).filter(ViewingHistory.user_id == user_id).count()
        
        # Ціль на рік
        year_start = datetime(datetime.now().year, 1, 1)
        year_views = self.db.query(ViewingHistory).filter(
            ViewingHistory.user_id == user_id,
            ViewingHistory.watched_at >= year_start
        ).count()
        
        goals = [
            {
                "id": "year_50_movies",
                "title": "50 фільмів за рік",
                "current": year_views,
                "target": 50,
                "progress": min((year_views / 50) * 100, 100),
                "icon": "🎯"
            },
            {
                "id": "rate_100_movies",
                "title": "Оцінити 100 фільмів",
                "current": ratings_count,
                "target": 100,
                "progress": min((ratings_count / 100) * 100, 100),
                "icon": "⭐"
            }
        ]
        
        return goals
    
    def _calculate_total_watch_time(self, user_id: int) -> int:
        """Розрахунок загального часу перегляду (в хвилинах)"""
        views = self.db.query(ViewingHistory).filter(
            ViewingHistory.user_id == user_id
        ).all()
        
        total_minutes = 0
        for view in views:
            movie = self.db.query(Movie).filter(Movie.id == view.movie_id).first()
            if movie and movie.duration:
                total_minutes += movie.duration
        
        return total_minutes
    
    def _get_uniqueness_description(self, score: float) -> str:
        """Опис унікальності смаків"""
        if score > 30:
            return "Ви маєте дуже унікальні смаки! 🌟"
        elif score > 15:
            return "Ваші вподобання досить оригінальні"
        else:
            return "Ви любите популярні фільми"
