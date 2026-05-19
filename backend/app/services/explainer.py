from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.user import User
from app.models.viewing_history import ViewingHistory


class ExplainableAI:
    """Модуль для пояснення рекомендацій (Explainable AI 2.0)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def explain_recommendation(
        self, 
        user_id: int, 
        movie: Movie, 
        scores: Dict[str, float]
    ) -> List[Dict]:
        """Генерація пояснень для рекомендації"""
        explanations = []
        
        # Пояснення на основі контентної фільтрації
        if scores.get("content_score", 0) > 0.5:
            content_explanation = self._explain_content_similarity(user_id, movie)
            if content_explanation:
                explanations.append(content_explanation)
        
        # Пояснення на основі колаборативної фільтрації
        if scores.get("collaborative_score", 0) > 0.5:
            collab_explanation = self._explain_collaborative(user_id, movie)
            if collab_explanation:
                explanations.append(collab_explanation)
        
        # Пояснення на основі емоцій
        if scores.get("emotion_score", 0) > 0.5:
            emotion_explanation = self._explain_emotions(user_id, movie)
            if emotion_explanation:
                explanations.append(emotion_explanation)
        
        # Загальна популярність
        if movie.average_rating >= 7.0:
            explanations.append({
                "reason_type": "popularity",
                "reason_text": f"Високий рейтинг: {movie.average_rating:.1f}/10 ({movie.ratings_count} оцінок)",
                "confidence": min(movie.average_rating / 10.0, 1.0),
                "details": {
                    "average_rating": movie.average_rating,
                    "ratings_count": movie.ratings_count
                }
            })
        
        return explanations
    
    def _explain_content_similarity(self, user_id: int, movie: Movie) -> Dict:
        """Пояснення схожості за жанрами"""
        # Отримання улюблених жанрів користувача
        user_ratings = self.db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.rating >= 7.0
        ).all()
        
        if not user_ratings:
            return None
        
        favorite_genres = []
        for rating in user_ratings:
            rated_movie = self.db.query(Movie).filter(Movie.id == rating.movie_id).first()
            if rated_movie and rated_movie.genres:
                favorite_genres.extend(rated_movie.genres)
        
        # Знаходження спільних жанрів
        common_genres = list(set(movie.genres) & set(favorite_genres))
        
        if not common_genres:
            return None
        
        genre_text = ", ".join(common_genres)
        confidence = len(common_genres) / len(movie.genres) if movie.genres else 0
        
        return {
            "reason_type": "genre_similarity",
            "reason_text": f"Схожий за жанрами: {genre_text}",
            "confidence": min(confidence, 1.0),
            "details": {
                "common_genres": common_genres,
                "movie_genres": movie.genres,
                "match_percentage": round(confidence * 100, 1)
            }
        }
    
    def _explain_collaborative(self, user_id: int, movie: Movie) -> Dict:
        """Пояснення на основі схожих користувачів"""
        # Знаходження користувачів, які оцінили цей фільм високо
        high_ratings = self.db.query(Rating).filter(
            Rating.movie_id == movie.id,
            Rating.rating >= 7.0,
            Rating.user_id != user_id
        ).all()
        
        if not high_ratings:
            return None
        
        # Перевірка, чи є серед них схожі користувачі
        similar_user_count = len(high_ratings)
        avg_rating = sum(r.rating for r in high_ratings) / len(high_ratings)
        
        return {
            "reason_type": "collaborative",
            "reason_text": f"Подобається {similar_user_count} користувачам зі схожими вподобаннями (середня оцінка: {avg_rating:.1f}/10)",
            "confidence": min(avg_rating / 10.0, 1.0),
            "details": {
                "similar_users_count": similar_user_count,
                "average_rating": round(avg_rating, 1),
                "ratings_distribution": self._get_ratings_distribution(high_ratings)
            }
        }
    
    def _explain_emotions(self, user_id: int, movie: Movie) -> Dict:
        """Пояснення на основі емоційних характеристик"""
        if not movie.emotions:
            return None
        
        # Отримання домінуючих емоцій фільму
        dominant_emotions = sorted(
            movie.emotions.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:2]
        
        if not dominant_emotions:
            return None
        
        emotion_names = [e[0] for e in dominant_emotions]
        emotion_text = ", ".join(emotion_names)
        confidence = sum(e[1] for e in dominant_emotions) / len(dominant_emotions)
        
        return {
            "reason_type": "emotion_match",
            "reason_text": f"Емоційно відповідає вашим вподобанням: {emotion_text}",
            "confidence": min(confidence, 1.0),
            "details": {
                "dominant_emotions": dict(dominant_emotions),
                "all_emotions": movie.emotions
            }
        }
    
    def _get_ratings_distribution(self, ratings: List[Rating]) -> Dict[str, int]:
        """Розподіл оцінок"""
        distribution = {
            "excellent": 0,  # 9-10
            "good": 0,       # 7-8
            "average": 0     # 5-6
        }
        
        for rating in ratings:
            if rating.rating >= 9:
                distribution["excellent"] += 1
            elif rating.rating >= 7:
                distribution["good"] += 1
            else:
                distribution["average"] += 1
        
        return distribution
    
    def explain_why_not(self, user_id: int, movie: Movie, scores: Dict[str, float]) -> Dict:
        """Детальний аналіз збігу з вподобаннями користувача"""
        
        try:
            # Отримуємо детальну інформацію про вподобання користувача
            user_preferences = self._get_user_preferences(user_id)
            
            # Розраховуємо збіг по кожному фактору
            genre_match = self._calculate_genre_match(user_id, movie)
            emotion_match = self._calculate_emotion_match(user_id, movie)
            collaborative_match = self._calculate_collaborative_match(user_id, movie)
            
            # Загальний скор
            total_score = (
                scores.get("content_score", 0) * 0.4 +
                scores.get("emotion_score", 0) * 0.3 +
                scores.get("collaborative_score", 0) * 0.3
            )
            
            return {
                "total_match": round(total_score * 100, 1),
                "factors": {
                    "genres": {
                        "match_percentage": round(genre_match["match_percentage"], 1),
                        "your_favorites": genre_match["user_favorites"][:5],
                        "movie_genres": movie.genres if movie.genres else [],
                        "common_genres": genre_match["common_genres"],
                        "score": round(scores.get("content_score", 0) * 100, 1)
                    },
                    "emotions": {
                        "match_percentage": round(emotion_match["match_percentage"], 1),
                        "your_favorites": emotion_match["user_favorites"],
                        "movie_emotions": emotion_match["movie_emotions"],
                        "common_emotions": emotion_match["common_emotions"],
                        "score": round(scores.get("emotion_score", 0) * 100, 1)
                    },
                    "similar_users": {
                        "match_percentage": round(collaborative_match["match_percentage"], 1),
                        "positive_ratings": collaborative_match["positive_count"],
                        "negative_ratings": collaborative_match["negative_count"],
                        "total_similar_users": collaborative_match["total_users"],
                        "score": round(scores.get("collaborative_score", 0) * 100, 1)
                    },
                    "rating": {
                        "average": movie.average_rating if movie.average_rating else 0,
                        "count": movie.ratings_count if movie.ratings_count else 0,
                        "quality": "відмінний" if movie.average_rating and movie.average_rating >= 8 else "добрий" if movie.average_rating and movie.average_rating >= 7 else "середній" if movie.average_rating and movie.average_rating >= 5 else "низький"
                    }
                },
                "insights": self._generate_insights(total_score, genre_match, emotion_match, collaborative_match, movie),
                "already_watched": self._is_watched(user_id, movie.id)
            }
        except Exception as e:
            print(f"Error in explain_why_not: {e}")
            # Повертаємо базову структуру у випадку помилки
            return {
                "total_match": 0,
                "factors": {
                    "genres": {
                        "match_percentage": 0,
                        "your_favorites": [],
                        "movie_genres": movie.genres if movie.genres else [],
                        "common_genres": [],
                        "score": 0
                    },
                    "emotions": {
                        "match_percentage": 0,
                        "your_favorites": [],
                        "movie_emotions": [],
                        "common_emotions": [],
                        "score": 0
                    },
                    "similar_users": {
                        "match_percentage": 0,
                        "positive_ratings": 0,
                        "negative_ratings": 0,
                        "total_similar_users": 0,
                        "score": 0
                    },
                    "rating": {
                        "average": movie.average_rating if movie.average_rating else 0,
                        "count": movie.ratings_count if movie.ratings_count else 0,
                        "quality": "невідомо"
                    }
                },
                "insights": ["Недостатньо даних для аналізу. Оцініть більше фільмів!"],
                "already_watched": False
            }
    
    def explain_counterfactual(self, user_id: int, movie: Movie, scores: Dict[str, float]) -> Dict:
        """Інтерактивні симуляції 'Що якби?' з можливістю зміни параметрів"""
        
        # Поточні скори
        current_content = scores.get("content_score", 0)
        current_emotion = scores.get("emotion_score", 0)
        current_collab = scores.get("collaborative_score", 0)
        
        current_total = (current_content * 0.4 + current_emotion * 0.3 + current_collab * 0.3)
        
        # Розраховуємо потенційні покращення для кожного фактору
        factors = []
        
        # 1. Жанри (Content Score)
        genre_potential = self._calculate_genre_potential(user_id, movie, current_content)
        factors.append({
            "name": "genres",
            "label": "Вподобання жанрів",
            "current_value": round(current_content * 100, 1),
            "potential_value": round(genre_potential * 100, 1),
            "impact": round((genre_potential - current_content) * 40, 1),  # 40% від загального
            "description": f"Якби ви більше любили {', '.join(movie.genres[:2]) if movie.genres else 'ці жанри'}",
            "icon": "🎬"
        })
        
        # 2. Емоції (Emotion Score)
        emotion_potential = self._calculate_emotion_potential(user_id, movie, current_emotion)
        dominant_emotion = max(movie.emotions.items(), key=lambda x: x[1])[0] if movie.emotions else "драматичні"
        factors.append({
            "name": "emotions",
            "label": "Емоційні вподобання",
            "current_value": round(current_emotion * 100, 1),
            "potential_value": round(emotion_potential * 100, 1),
            "impact": round((emotion_potential - current_emotion) * 30, 1),  # 30% від загального
            "description": f"Якби ви частіше дивились {dominant_emotion} фільми",
            "icon": "😊"
        })
        
        # 3. Схожі користувачі (Collaborative Score)
        collab_potential = self._calculate_collaborative_potential(user_id, movie, current_collab)
        factors.append({
            "name": "similar_users",
            "label": "Оцінки схожих користувачів",
            "current_value": round(current_collab * 100, 1),
            "potential_value": round(collab_potential * 100, 1),
            "impact": round((collab_potential - current_collab) * 30, 1),  # 30% від загального
            "description": "Якби більше схожих користувачів оцінили високо",
            "icon": "👥"
        })
        
        # Розраховуємо максимальний потенційний скор
        potential_total = (genre_potential * 0.4 + emotion_potential * 0.3 + collab_potential * 0.3)
        
        # Топ-3 найбільш впливових змін
        top_changes = sorted(factors, key=lambda x: abs(x["impact"]), reverse=True)[:3]
        
        return {
            "current_score": round(current_total, 3),
            "potential_score": round(potential_total, 3),
            "max_improvement": round((potential_total - current_total) * 100, 1),
            "factors": factors,
            "top_changes": top_changes,
            "suggestions": self._generate_counterfactual_suggestions(factors, movie)
        }
    
    def get_alternative_recommendations(
        self, 
        user_id: int, 
        rejected_movie: Movie,
        reason: str = "different_logic"
    ) -> List[Dict]:
        """Розумні альтернативні рекомендації з персоналізацією"""
        import random
        from sqlalchemy import func
        
        try:
            # Отримуємо вподобання користувача
            user_prefs = self._get_user_preferences(user_id)
            watched_ids = self._get_watched_ids(user_id)
            exclude_ids = watched_ids + [rejected_movie.id] if watched_ids else [rejected_movie.id]
            
            # Базовий запит - ВСЯ база фільмів (без обмежень)
            base_query = self.db.query(Movie).filter(
                Movie.id.notin_(exclude_ids),
                Movie.average_rating >= 5.5  # Розширили діапазон
            )
            
            alternatives = []
            explanation = ""
            
            if reason == "different_genre":
                # СТРАТЕГІЯ: Фільми з ІНШИХ жанрів, які користувач теж любить
                
                # 1. Знаходимо жанри відхиленого фільму
                rejected_genres = set(rejected_movie.genres) if rejected_movie.genres else set()
                
                # 2. Знаходимо улюблені жанри користувача (крім тих що у відхиленому фільмі)
                user_favorite_genres = []
                if user_prefs["genres"]:
                    sorted_genres = sorted(user_prefs["genres"].items(), key=lambda x: x[1], reverse=True)
                    user_favorite_genres = [g for g, _ in sorted_genres if g not in rejected_genres][:3]
                
                if user_favorite_genres:
                    # Шукаємо фільми з улюблених жанрів користувача
                    all_movies = base_query.all()
                    
                    # Фільтруємо: має бути хоч один улюблений жанр, але НЕ жанри відхиленого
                    candidates = [
                        m for m in all_movies
                        if m.genres and 
                        any(g in user_favorite_genres for g in m.genres) and
                        not any(g in rejected_genres for g in m.genres)
                    ]
                    
                    # Сортуємо за рейтингом + додаємо випадковість
                    candidates.sort(key=lambda x: (x.average_rating or 0) + random.uniform(0, 1), reverse=True)
                    alternatives = candidates[:8]
                    
                    explanation = f"Фільми з ваших улюблених жанрів ({', '.join(user_favorite_genres[:2])}), але без {', '.join(list(rejected_genres)[:2])}"
                else:
                    # Якщо немає вподобань - беремо популярні з інших жанрів
                    all_movies = base_query.order_by(Movie.average_rating.desc()).limit(200).all()
                    candidates = [
                        m for m in all_movies
                        if m.genres and not any(g in rejected_genres for g in m.genres)
                    ]
                    random.shuffle(candidates)
                    alternatives = candidates[:8]
                    explanation = f"Популярні фільми без жанрів {', '.join(list(rejected_genres)[:2])}"
                
            elif reason == "different_emotion":
                # СТРАТЕГІЯ: Фільми з ІНШИМИ емоціями, які користувач любить
                
                # 1. Знаходимо домінуючу емоцію відхиленого фільму
                rejected_emotions = set()
                if rejected_movie.emotions:
                    # Беремо емоції що > 30%
                    rejected_emotions = {e for e, score in rejected_movie.emotions.items() if score > 0.3}
                
                # 2. Знаходимо улюблені емоції користувача (крім тих що у відхиленому)
                user_favorite_emotions = []
                if user_prefs["emotions"]:
                    total_score = sum(user_prefs["emotions"].values())
                    sorted_emotions = sorted(user_prefs["emotions"].items(), key=lambda x: x[1], reverse=True)
                    user_favorite_emotions = [e for e, _ in sorted_emotions if e not in rejected_emotions][:3]
                
                if user_favorite_emotions:
                    # Шукаємо фільми з улюблених емоцій користувача
                    all_movies = base_query.all()
                    
                    candidates = []
                    for m in all_movies:
                        if not m.emotions:
                            continue
                        
                        # Перевіряємо чи є улюблені емоції користувача
                        has_favorite = any(
                            m.emotions.get(e, 0) > 0.3 
                            for e in user_favorite_emotions
                        )
                        
                        # Перевіряємо чи немає відхилених емоцій
                        has_rejected = any(
                            m.emotions.get(e, 0) > 0.3 
                            for e in rejected_emotions
                        )
                        
                        if has_favorite and not has_rejected:
                            candidates.append(m)
                    
                    # Сортуємо за рейтингом + випадковість
                    candidates.sort(key=lambda x: (x.average_rating or 0) + random.uniform(0, 1), reverse=True)
                    alternatives = candidates[:8]
                    
                    explanation = f"Фільми з вашими улюбленими емоціями ({', '.join(user_favorite_emotions[:2])}), але без {', '.join(list(rejected_emotions)[:2])}"
                else:
                    # Якщо немає вподобань - беремо з різними емоціями
                    all_movies = base_query.order_by(Movie.average_rating.desc()).limit(200).all()
                    candidates = [
                        m for m in all_movies
                        if m.emotions and not any(m.emotions.get(e, 0) > 0.3 for e in rejected_emotions)
                    ]
                    random.shuffle(candidates)
                    alternatives = candidates[:8]
                    explanation = f"Фільми з іншими емоціями (не {', '.join(list(rejected_emotions)[:2])})"
            
            else:
                # За замовчуванням - персоналізовані рекомендації
                all_movies = base_query.limit(500).all()
                random.shuffle(all_movies)
                alternatives = all_movies[:8]
                explanation = "Різноманітні фільми спеціально для вас"
            
            # Якщо не знайшли - fallback
            if not alternatives:
                print(f"No alternatives found, using fallback")
                all_movies = base_query.order_by(func.random()).limit(8).all()
                alternatives = all_movies
                explanation = "Випадкові якісні фільми з бази"
            
            # Формуємо відповідь
            result = [
                {
                    "movie": alt,
                    "reason": explanation,
                    "alternative_type": reason
                }
                for alt in alternatives
            ]
            
            print(f"Returning {len(result)} alternatives for reason: {reason}, movie: {rejected_movie.title}")
            return result
            
        except Exception as e:
            print(f"Error in get_alternative_recommendations: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _explain_content_mismatch(self, user_id: int, movie: Movie) -> Dict:
        """Деталі невідповідності контенту"""
        user_ratings = self.db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.rating >= 7.0
        ).all()
        
        if not user_ratings:
            return {"reason": "Недостатньо даних про ваші вподобання"}
        
        favorite_genres = []
        for rating in user_ratings:
            rated_movie = self.db.query(Movie).filter(Movie.id == rating.movie_id).first()
            if rated_movie and rated_movie.genres:
                favorite_genres.extend(rated_movie.genres)
        
        from collections import Counter
        top_genres = [g for g, _ in Counter(favorite_genres).most_common(3)]
        
        return {
            "your_favorite_genres": top_genres,
            "movie_genres": movie.genres,
            "overlap": list(set(movie.genres) & set(top_genres))
        }
    
    def _explain_collaborative_mismatch(self, user_id: int, movie: Movie) -> Dict:
        """Деталі колаборативної невідповідності"""
        ratings = self.db.query(Rating).filter(Rating.movie_id == movie.id).all()
        
        if not ratings:
            return {"reason": "Цей фільм ще ніхто не оцінив"}
        
        avg_rating = sum(r.rating for r in ratings) / len(ratings)
        
        return {
            "average_rating": round(avg_rating, 1),
            "ratings_count": len(ratings),
            "recommendation": "Спробуйте фільми з вищим рейтингом"
        }
    
    def _explain_emotion_mismatch(self, user_id: int, movie: Movie) -> Dict:
        """Деталі емоційної невідповідності"""
        if not movie.emotions:
            return {"reason": "Емоційний профіль фільму не визначено"}
        
        dominant_emotion = max(movie.emotions.items(), key=lambda x: x[1])
        
        return {
            "movie_dominant_emotion": dominant_emotion[0],
            "intensity": dominant_emotion[1],
            "suggestion": f"Цей фільм має сильний {dominant_emotion[0]} характер"
        }
    
    def _is_watched(self, user_id: int, movie_id: int) -> bool:
        """Перевірка чи фільм переглянуто"""
        watched = self.db.query(ViewingHistory).filter(
            ViewingHistory.user_id == user_id,
            ViewingHistory.movie_id == movie_id
        ).first()
        return watched is not None
    
    def _get_similar_genre_movies(self, user_id: int, movie: Movie) -> List[Movie]:
        """Фільми схожих жанрів"""
        if not movie.genres:
            return []
        
        watched_ids = self._get_watched_ids(user_id)
        
        similar = self.db.query(Movie).filter(
            Movie.id.notin_(watched_ids + [movie.id]) if watched_ids else Movie.id != movie.id
        ).all()
        
        # Фільтруємо за жанрами
        similar_genre = [
            m for m in similar
            if any(g in movie.genres for g in m.genres)
        ]
        
        return similar_genre[:5]
    
    def _get_watched_ids(self, user_id: int) -> List[int]:
        """ID переглянутих фільмів"""
        watched = self.db.query(ViewingHistory.movie_id).filter(
            ViewingHistory.user_id == user_id
        ).all()
        return [m[0] for m in watched]
    
    def _calculate_potential_score(self, current_scores: Dict, suggestions: List[Dict]) -> float:
        """Розрахунок потенційного скору"""
        base_score = current_scores.get("final_score", 0)
        
        # Додаємо потенційне покращення
        for suggestion in suggestions:
            if suggestion["impact"] == "high":
                base_score += 0.2
            elif suggestion["impact"] == "medium":
                base_score += 0.1
            else:
                base_score += 0.05
        
        return min(base_score, 1.0)
    
    def _get_user_preferences(self, user_id: int) -> Dict:
        """Отримання вподобань користувача"""
        user_ratings = self.db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.rating >= 7.0
        ).all()
        
        genres = {}
        emotions = {}
        
        for rating in user_ratings:
            rated_movie = self.db.query(Movie).filter(Movie.id == rating.movie_id).first()
            if rated_movie:
                # Жанри
                if rated_movie.genres:
                    for genre in rated_movie.genres:
                        genres[genre] = genres.get(genre, 0) + 1
                
                # Емоції
                if rated_movie.emotions:
                    for emotion, score in rated_movie.emotions.items():
                        emotions[emotion] = emotions.get(emotion, 0) + score
        
        return {
            "genres": genres,
            "emotions": emotions,
            "total_ratings": len(user_ratings) if user_ratings else 1  # Уникаємо ділення на 0
        }
    
    def _calculate_genre_match(self, user_id: int, movie: Movie) -> Dict:
        """Розрахунок збігу жанрів"""
        prefs = self._get_user_preferences(user_id)
        user_genres = prefs["genres"]
        
        if not user_genres or not movie.genres:
            return {
                "match_percentage": 0,
                "user_favorites": [],
                "common_genres": []
            }
        
        # Топ жанрів користувача
        sorted_genres = sorted(user_genres.items(), key=lambda x: x[1], reverse=True)
        user_favorites = [{"genre": g, "count": c, "percentage": round(c / prefs["total_ratings"] * 100, 1)} 
                         for g, c in sorted_genres]
        
        # Спільні жанри
        common = list(set(movie.genres) & set(user_genres.keys()))
        
        # Відсоток збігу
        if common:
            match_score = sum(user_genres[g] for g in common) / sum(user_genres.values())
        else:
            match_score = 0
        
        return {
            "match_percentage": match_score * 100,
            "user_favorites": user_favorites,
            "common_genres": common
        }
    
    def _calculate_emotion_match(self, user_id: int, movie: Movie) -> Dict:
        """Розрахунок збігу емоцій"""
        prefs = self._get_user_preferences(user_id)
        user_emotions = prefs["emotions"]
        
        if not user_emotions or not movie.emotions:
            return {
                "match_percentage": 0,
                "user_favorites": [],
                "movie_emotions": [],
                "common_emotions": []
            }
        
        # Нормалізуємо емоції користувача
        total_emotion_score = sum(user_emotions.values())
        user_favorites = [
            {"emotion": e, "score": round(s / total_emotion_score * 100, 1)} 
            for e, s in sorted(user_emotions.items(), key=lambda x: x[1], reverse=True)
        ][:5]
        
        # Емоції фільму
        movie_emotions = [
            {"emotion": e, "score": round(s * 100, 1)}
            for e, s in sorted(movie.emotions.items(), key=lambda x: x[1], reverse=True)
        ][:5]
        
        # Спільні емоції
        common = list(set(movie.emotions.keys()) & set(user_emotions.keys()))
        
        # Відсоток збігу
        if common:
            match_score = sum(movie.emotions[e] * user_emotions[e] for e in common) / sum(user_emotions.values())
        else:
            match_score = 0
        
        return {
            "match_percentage": match_score * 100,
            "user_favorites": user_favorites,
            "movie_emotions": movie_emotions,
            "common_emotions": common
        }
    
    def _calculate_collaborative_match(self, user_id: int, movie: Movie) -> Dict:
        """Розрахунок збігу з схожими користувачами"""
        # Знаходимо рейтинги цього фільму
        movie_ratings = self.db.query(Rating).filter(
            Rating.movie_id == movie.id,
            Rating.user_id != user_id
        ).all()
        
        if not movie_ratings:
            return {
                "match_percentage": 0,
                "positive_count": 0,
                "negative_count": 0,
                "total_users": 0
            }
        
        positive = sum(1 for r in movie_ratings if r.rating >= 7)
        negative = sum(1 for r in movie_ratings if r.rating < 7)
        
        match_percentage = (positive / len(movie_ratings)) * 100 if movie_ratings else 0
        
        return {
            "match_percentage": match_percentage,
            "positive_count": positive,
            "negative_count": negative,
            "total_users": len(movie_ratings)
        }
    
    def _generate_insights(self, total_score: float, genre_match: Dict, emotion_match: Dict, 
                          collaborative_match: Dict, movie: Movie) -> List[str]:
        """Генерація персональних інсайтів"""
        insights = []
        
        # Інсайт про загальний збіг
        if total_score >= 0.7:
            insights.append(f"✅ Відмінний збіг ({round(total_score * 100)}%)! Цей фільм ідеально підходить під ваш смак")
        elif total_score >= 0.5:
            insights.append(f"👍 Добрий збіг ({round(total_score * 100)}%). Ймовірно вам сподобається")
        elif total_score >= 0.3:
            insights.append(f"🤔 Середній збіг ({round(total_score * 100)}%). Може бути цікаво спробувати щось нове")
        else:
            insights.append(f"❌ Низький збіг ({round(total_score * 100)}%). Не ваш стиль фільмів")
        
        # Інсайт про жанри
        if genre_match["common_genres"]:
            insights.append(f"🎬 Спільні жанри: {', '.join(genre_match['common_genres'])}")
        else:
            insights.append("🎬 Немає спільних жанрів з вашими улюбленими")
        
        # Інсайт про емоції
        if emotion_match["common_emotions"]:
            insights.append(f"😊 Спільні емоції: {', '.join(emotion_match['common_emotions'])}")
        else:
            insights.append("😊 Інший емоційний профіль ніж ви зазвичай дивитесь")
        
        # Інсайт про схожих користувачів
        if collaborative_match["positive_count"] > collaborative_match["negative_count"]:
            insights.append(f"👥 {collaborative_match['positive_count']} схожих користувачів оцінили високо")
        elif collaborative_match["negative_count"] > 0:
            insights.append(f"👥 {collaborative_match['negative_count']} схожих користувачів оцінили низько")
        
        # Інсайт про рейтинг
        if movie.average_rating >= 8:
            insights.append(f"⭐ Високий рейтинг {movie.average_rating:.1f}/10 - якісний фільм")
        elif movie.average_rating < 6:
            insights.append(f"⭐ Рейтинг {movie.average_rating:.1f}/10 - не найкраща оцінка")
        
        return insights
    
    def _calculate_genre_potential(self, user_id: int, movie: Movie, current_score: float) -> float:
        """Розрахунок потенційного скору якби користувач любив ці жанри"""
        # Якщо жанри фільму повністю збігаються з улюбленими - максимальний скор
        return min(current_score + 0.5, 1.0)
    
    def _calculate_emotion_potential(self, user_id: int, movie: Movie, current_score: float) -> float:
        """Розрахунок потенційного скору якби користувач любив ці емоції"""
        # Якщо емоції фільму повністю збігаються з улюбленими - максимальний скор
        return min(current_score + 0.4, 1.0)
    
    def _calculate_collaborative_potential(self, user_id: int, movie: Movie, current_score: float) -> float:
        """Розрахунок потенційного скору якби більше користувачів оцінили високо"""
        # Якщо всі схожі користувачі оцінили високо - максимальний скор
        return min(current_score + 0.3, 1.0)
    
    def _generate_counterfactual_suggestions(self, factors: List[Dict], movie: Movie) -> List[str]:
        """Генерація текстових порад на основі факторів"""
        suggestions = []
        
        # Сортуємо за впливом
        sorted_factors = sorted(factors, key=lambda x: abs(x["impact"]), reverse=True)
        
        for factor in sorted_factors[:3]:
            if abs(factor["impact"]) > 5:  # Тільки значущі зміни
                impact_text = f"+{factor['impact']:.0f}%" if factor["impact"] > 0 else f"{factor['impact']:.0f}%"
                suggestions.append(f"{factor['icon']} {factor['description']} → {impact_text} до загального скору")
        
        if not suggestions:
            suggestions.append("✅ Цей фільм вже добре підходить під ваші вподобання!")
        
        return suggestions
