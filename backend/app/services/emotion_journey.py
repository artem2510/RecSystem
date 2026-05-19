"""
Сервіс для створення емоційних подорожей (Mood Playlists)
Планування послідовності фільмів для ідеального вечора
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import random

from app.models.movie import Movie
from app.models.viewing_history import ViewingHistory
from app.services.emotion_analyzer import EmotionAnalyzer


class EmotionJourney:
    """Створення емоційних подорожей - плейлистів фільмів"""
    
    def __init__(self, db: Session):
        self.db = db
        self.emotion_analyzer = EmotionAnalyzer(db)
        
        # Шаблони емоційних подорожей
        self.journey_templates = {
            "relaxing_evening": {
                "name": "Розслаблюючий вечір",
                "description": "Від легкої комедії до затишної драми",
                "emoji": "🌙",
                "sequence": ["оптимістичний", "романтичний", "драматичний"],
                "duration_target": 300  # 5 годин
            },
            "adrenaline_rush": {
                "name": "Адреналіновий вечір",
                "description": "Динамічні фільми для любителів гострих відчуттів",
                "emoji": "⚡",
                "sequence": ["пригодницький", "напружений", "напружений"],
                "duration_target": 360
            },
            "emotional_rollercoaster": {
                "name": "Емоційні гойдалки",
                "description": "Від сміху до сліз і назад",
                "emoji": "🎢",
                "sequence": ["оптимістичний", "драматичний", "оптимістичний"],
                "duration_target": 330
            },
            "date_night": {
                "name": "Романтичний вечір",
                "description": "Ідеально для побачення",
                "emoji": "💕",
                "sequence": ["романтичний", "романтичний"],
                "duration_target": 240
            },
            "scary_marathon": {
                "name": "Марафон жахів",
                "description": "Для любителів моторошного",
                "emoji": "👻",
                "sequence": ["жахливий", "жахливий", "жахливий"],
                "duration_target": 300
            },
            "adventure_day": {
                "name": "День пригод",
                "description": "Епічні подорожі та героїчні історії",
                "emoji": "🗺️",
                "sequence": ["пригодницький", "пригодницький", "оптимістичний"],
                "duration_target": 400
            },
            "mood_recovery": {
                "name": "Відновлення настрою",
                "description": "Після важкого дня - тільки позитив",
                "emoji": "☀️",
                "sequence": ["оптимістичний", "оптимістичний"],
                "duration_target": 200
            },
            "deep_thoughts": {
                "name": "Глибокі роздуми",
                "description": "Філософські та драматичні фільми",
                "emoji": "🤔",
                "sequence": ["драматичний", "драматичний"],
                "duration_target": 280
            }
        }
    
    def create_journey(
        self, 
        user_id: int, 
        template_key: str,
        custom_sequence: Optional[List[str]] = None
    ) -> Dict:
        """Створення емоційної подорожі за шаблоном"""
        
        if template_key not in self.journey_templates and not custom_sequence:
            raise ValueError(f"Невідомий шаблон: {template_key}")
        
        # Отримуємо шаблон або створюємо кастомний
        if custom_sequence:
            template = {
                "name": "Кастомна подорож",
                "description": "Ваша унікальна послідовність",
                "emoji": "🎬",
                "sequence": custom_sequence,
                "duration_target": len(custom_sequence) * 120
            }
        else:
            template = self.journey_templates[template_key]
        
        # Отримуємо переглянуті фільми
        watched_ids = self._get_watched_movies(user_id)
        
        # Підбираємо фільми для кожної емоції
        playlist = []
        total_duration = 0
        
        for emotion in template["sequence"]:
            movie = self._find_best_movie_for_emotion(
                user_id, 
                emotion, 
                watched_ids,
                target_duration=template["duration_target"] // len(template["sequence"])
            )
            
            if movie:
                playlist.append({
                    "movie": movie,
                    "emotion": emotion,
                    "position": len(playlist) + 1
                })
                total_duration += movie.duration if movie.duration else 120
                watched_ids.append(movie.id)  # Не повторювати в плейлисті
        
        # Аналіз емоційної кривої
        emotion_curve = self._analyze_emotion_curve(playlist)
        
        return {
            "template": template_key if not custom_sequence else "custom",
            "name": template["name"],
            "description": template["description"],
            "emoji": template["emoji"],
            "playlist": playlist,
            "total_duration": total_duration,
            "total_movies": len(playlist),
            "emotion_curve": emotion_curve,
            "recommendations": self._generate_recommendations(playlist)
        }
    
    def get_contrast_journey(self, user_id: int, last_movie_id: int) -> Dict:
        """Створення контрастної подорожі після конкретного фільму"""
        last_movie = self.db.query(Movie).filter(Movie.id == last_movie_id).first()
        
        if not last_movie or not last_movie.emotions:
            return self.create_journey(user_id, "relaxing_evening")
        
        # Визначаємо домінуючу емоцію
        dominant_emotion = max(last_movie.emotions.items(), key=lambda x: x[1])[0]
        
        # Карта контрастних емоцій
        contrast_map = {
            "драматичний": ["оптимістичний", "оптимістичний"],
            "жахливий": ["оптимістичний", "романтичний"],
            "напружений": ["романтичний", "оптимістичний"],
            "оптимістичний": ["драматичний"],
            "романтичний": ["пригодницький"],
            "пригодницький": ["романтичний", "драматичний"]
        }
        
        sequence = contrast_map.get(dominant_emotion, ["оптимістичний"])
        
        return self.create_journey(user_id, None, custom_sequence=sequence)
    
    def get_all_templates(self) -> List[Dict]:
        """Отримання всіх доступних шаблонів"""
        return [
            {
                "key": key,
                "name": template["name"],
                "description": template["description"],
                "emoji": template["emoji"],
                "emotions": template["sequence"],
                "estimated_duration": template["duration_target"]
            }
            for key, template in self.journey_templates.items()
        ]
    
    def _get_watched_movies(self, user_id: int) -> List[int]:
        """Отримання ID переглянутих фільмів"""
        watched = self.db.query(ViewingHistory.movie_id).filter(
            ViewingHistory.user_id == user_id
        ).all()
        return [m[0] for m in watched]
    
    def _find_best_movie_for_emotion(
        self, 
        user_id: int, 
        emotion: str, 
        exclude_ids: List[int],
        target_duration: int = 120
    ) -> Optional[Movie]:
        """Пошук найкращого фільму для конкретної емоції з різноманітністю"""
        
        # Отримуємо ВСІ фільми (знижуємо поріг рейтингу для більшого вибору)
        query = self.db.query(Movie).filter(
            Movie.average_rating >= 4.0  # Знижено з 5.0 до 4.0
        )
        
        if exclude_ids:
            query = query.filter(Movie.id.notin_(exclude_ids))
        
        all_movies = query.all()
        
        if not all_movies:
            return None
        
        print(f"🎬 Доступно фільмів для '{emotion}': {len(all_movies)}")
        
        # Фільтруємо за емоцією (знижений поріг до 0.2 для більшого вибору)
        emotion_movies = []
        for movie in all_movies:
            if movie.emotions and emotion in movie.emotions:
                emotion_score = movie.emotions[emotion]
                if emotion_score >= 0.2:  # Знижено з 0.3 до 0.2
                    # Враховуємо тривалість
                    duration_diff = abs(movie.duration - target_duration) if movie.duration else 0
                    duration_penalty = duration_diff / 100.0
                    
                    # Фінальний скор
                    final_score = emotion_score - duration_penalty + (movie.average_rating / 20.0)
                    emotion_movies.append((movie, final_score))
        
        print(f"✅ Знайдено фільмів з емоцією '{emotion}': {len(emotion_movies)}")
        
        # Fallback: якщо немає фільмів з потрібною емоцією, використовуємо жанри
        if not emotion_movies:
            print(f"⚠️ Не знайдено фільмів для емоції '{emotion}', використовуємо fallback за жанрами")
            
            # Мапа емоцій на жанри
            emotion_to_genres = {
                "оптимістичний": ["Comedy", "Family", "Animation", "Music"],
                "драматичний": ["Drama", "History", "War"],
                "напружений": ["Thriller", "Action", "Crime", "Mystery"],
                "романтичний": ["Romance", "Drama"],
                "жахливий": ["Horror", "Thriller"],
                "пригодницький": ["Adventure", "Action", "Fantasy", "Science Fiction"]
            }
            
            target_genres = emotion_to_genres.get(emotion, [])
            
            # Шукаємо фільми за жанрами
            genre_movies = []
            for movie in all_movies:
                if movie.genres and any(genre in movie.genres for genre in target_genres):
                    score = movie.average_rating / 10.0 if movie.average_rating else 0.5
                    genre_movies.append((movie, score))
            
            if genre_movies:
                genre_movies.sort(key=lambda x: x[1], reverse=True)
                # Беремо з топ-30 випадково для різноманітності
                top_candidates = genre_movies[:30]
                return random.choice(top_candidates)[0]
            
            # Якщо і жанрів немає, беремо просто якісні фільми
            fallback_movies = sorted(
                all_movies, 
                key=lambda m: m.average_rating if m.average_rating else 0, 
                reverse=True
            )[:50]  # Збільшено з 10 до 50
            
            if fallback_movies:
                return random.choice(fallback_movies)
            return None
        
        # Сортуємо за скором
        emotion_movies.sort(key=lambda x: x[1], reverse=True)
        
        # РІЗНОМАНІТНІСТЬ: Беремо з топ-5 випадково, а не завжди найкращий
        top_candidates = emotion_movies[:5] if len(emotion_movies) >= 5 else emotion_movies
        selected = random.choice(top_candidates)
        
        print(f"🎯 Обрано: {selected[0].title} (скор: {selected[1]:.2f})")
        
        return selected[0]
    
    def _analyze_emotion_curve(self, playlist: List[Dict]) -> List[Dict]:
        """Аналіз емоційної кривої плейлиста"""
        curve = []
        
        for item in playlist:
            movie = item["movie"]
            if movie.emotions:
                # Середня інтенсивність емоцій
                intensity = sum(movie.emotions.values()) / len(movie.emotions)
                
                curve.append({
                    "position": item["position"],
                    "movie_title": movie.title,
                    "emotion": item["emotion"],
                    "intensity": round(intensity, 2)
                })
        
        return curve
    
    def _generate_recommendations(self, playlist: List[Dict]) -> List[str]:
        """Генерація рекомендацій для плейлиста"""
        recommendations = []
        
        if len(playlist) == 0:
            return ["⚠️ Не вдалося створити плейлист. Спробуйте інший шаблон або додайте більше фільмів з емоційними характеристиками."]
        
        # Аналіз тривалості
        total_duration = sum(
            item["movie"].duration if item["movie"].duration else 120 
            for item in playlist
        )
        
        if total_duration > 360:
            recommendations.append("⏰ Це довгий марафон! Підготуйте попкорн та напої")
        elif total_duration < 180:
            recommendations.append("⚡ Швидкий перегляд - ідеально для вечора")
        
        # Аналіз емоційної різноманітності
        emotions = set(item["emotion"] for item in playlist)
        if len(emotions) >= 3:
            recommendations.append("🎢 Різноманітна емоційна подорож - приготуйтесь до контрастів")
        elif len(emotions) == 1:
            recommendations.append("🎯 Фокусована подорож - глибоке занурення в одну емоцію")
        
        # Рекомендації за часом
        recommendations.append(f"🕐 Рекомендований час початку: {self._suggest_start_time(total_duration)}")
        
        return recommendations
    
    def _suggest_start_time(self, total_duration: int) -> str:
        """Пропозиція часу початку"""
        if total_duration > 300:
            return "14:00-15:00 (на весь вечір)"
        elif total_duration > 200:
            return "18:00-19:00 (вечірній перегляд)"
        else:
            return "20:00-21:00 (швидкий вечір)"
