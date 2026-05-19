"""
Контекстуальна рекомендаційна система
Враховує час доби, день тижня, погоду, настрій користувача
"""
from datetime import datetime, time
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.movie import Movie


class ContextualRecommender:
    """Контекстуальні рекомендації на основі зовнішніх факторів"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Правила для часу доби
        self.time_of_day_rules = {
            "morning": {  # 6:00 - 12:00
                "preferred_genres": ["Комедія", "Анімація", "Сімейний", "Пригоди"],
                "max_duration": 120,  # Короткі фільми вранці
                "mood": "light",
                "description": "Легкі та позитивні фільми для доброго ранку"
            },
            "afternoon": {  # 12:00 - 18:00
                "preferred_genres": ["Бойовик", "Пригоди", "Фантастика", "Комедія"],
                "max_duration": 150,
                "mood": "energetic",
                "description": "Енергійні фільми для активного дня"
            },
            "evening": {  # 18:00 - 22:00
                "preferred_genres": ["Драма", "Трилер", "Містика", "Романтика"],
                "max_duration": 180,
                "mood": "thoughtful",
                "description": "Глибокі та захоплюючі фільми для вечора"
            },
            "night": {  # 22:00 - 6:00
                "preferred_genres": ["Жахи", "Трилер", "Містика", "Драма"],
                "max_duration": 140,
                "mood": "intense",
                "description": "Атмосферні фільми для пізнього вечора"
            }
        }
        
        # Правила для днів тижня
        self.day_of_week_rules = {
            "weekday": {  # Понеділок - П'ятниця
                "preferred_duration": (90, 130),  # Короткі фільми
                "preferred_genres": ["Комедія", "Бойовик", "Трилер"],
                "avoid_genres": [],
                "description": "Швидкі та динамічні фільми для будніх днів"
            },
            "weekend": {  # Субота - Неділя
                "preferred_duration": (120, 200),  # Довгі епіки
                "preferred_genres": ["Драма", "Фантастика", "Пригоди", "Фентезі", "Історичний"],
                "avoid_genres": [],
                "description": "Епічні та глибокі фільми для вихідних"
            }
        }
        
        # Правила для погоди
        self.weather_rules = {
            "rainy": {
                "preferred_genres": ["Драма", "Романтика", "Містика", "Документальний"],
                "mood": "cozy",
                "description": "Затишні фільми для дощової погоди"
            },
            "sunny": {
                "preferred_genres": ["Пригоди", "Комедія", "Бойовик", "Сімейний"],
                "mood": "uplifting",
                "description": "Яскраві та енергійні фільми для сонячного дня"
            },
            "cloudy": {
                "preferred_genres": ["Драма", "Трилер", "Фантастика"],
                "mood": "contemplative",
                "description": "Задумливі фільми для похмурої погоди"
            },
            "snowy": {
                "preferred_genres": ["Романтика", "Драма", "Сімейний", "Фентезі"],
                "mood": "magical",
                "description": "Чарівні фільми для снігової погоди"
            }
        }
        
        # Правила для настрою користувача
        self.mood_rules = {
            "happy": {
                "preferred_genres": ["Комедія", "Романтика", "Пригоди", "Музичний"],
                "avoid_genres": ["Жахи", "Драма"],
                "emotions": ["оптимістичний", "романтичний"],
                "description": "Веселі та позитивні фільми"
            },
            "sad": {
                "preferred_genres": ["Драма", "Романтика", "Документальний"],
                "avoid_genres": ["Жахи", "Трилер"],
                "emotions": ["драматичний", "романтичний"],
                "description": "Емоційні фільми для переживання почуттів"
            },
            "stressed": {
                "preferred_genres": ["Комедія", "Анімація", "Сімейний"],
                "avoid_genres": ["Жахи", "Трилер", "Військовий"],
                "emotions": ["оптимістичний"],
                "description": "Легкі та розслаблюючі фільми"
            },
            "bored": {
                "preferred_genres": ["Бойовик", "Трилер", "Пригоди", "Фантастика"],
                "avoid_genres": ["Документальний"],
                "emotions": ["напружений", "пригодницький"],
                "description": "Динамічні та захоплюючі фільми"
            },
            "romantic": {
                "preferred_genres": ["Романтика", "Драма", "Комедія"],
                "avoid_genres": ["Жахи", "Військовий"],
                "emotions": ["романтичний", "оптимістичний"],
                "description": "Романтичні та ніжні фільми"
            },
            "adventurous": {
                "preferred_genres": ["Пригоди", "Бойовик", "Фантастика", "Фентезі"],
                "avoid_genres": ["Документальний", "Драма"],
                "emotions": ["пригодницький"],
                "description": "Пригодницькі та епічні фільми"
            },
            "thoughtful": {
                "preferred_genres": ["Драма", "Документальний", "Містика", "Фантастика"],
                "avoid_genres": ["Комедія", "Бойовик"],
                "emotions": ["драматичний"],
                "description": "Глибокі та філософські фільми"
            },
            "scared": {
                "preferred_genres": ["Жахи", "Трилер", "Містика"],
                "avoid_genres": ["Комедія", "Романтика", "Сімейний"],
                "emotions": ["жахливий", "напружений"],
                "description": "Моторошні та напружені фільми"
            }
        }
    
    def get_time_of_day_context(self, current_time: Optional[datetime] = None) -> Dict:
        """Визначення контексту часу доби"""
        if current_time is None:
            current_time = datetime.now()
        
        hour = current_time.hour
        
        if 6 <= hour < 12:
            return {"period": "morning", **self.time_of_day_rules["morning"]}
        elif 12 <= hour < 18:
            return {"period": "afternoon", **self.time_of_day_rules["afternoon"]}
        elif 18 <= hour < 22:
            return {"period": "evening", **self.time_of_day_rules["evening"]}
        else:
            return {"period": "night", **self.time_of_day_rules["night"]}
    
    def get_day_of_week_context(self, current_date: Optional[datetime] = None) -> Dict:
        """Визначення контексту дня тижня"""
        if current_date is None:
            current_date = datetime.now()
        
        # 0 = Понеділок, 6 = Неділя
        day = current_date.weekday()
        
        if day < 5:  # Понеділок - П'ятниця
            return {"type": "weekday", **self.day_of_week_rules["weekday"]}
        else:  # Субота - Неділя
            return {"type": "weekend", **self.day_of_week_rules["weekend"]}
    
    def get_mood_context(self, mood: str) -> Optional[Dict]:
        """Отримання контексту настрою"""
        if mood in self.mood_rules:
            return {"mood": mood, **self.mood_rules[mood]}
        return None
    
    def get_weather_context(self, weather_condition: str) -> Optional[Dict]:
        """Отримання контексту погоди"""
        weather_map = {
            "rain": "rainy",
            "clear": "sunny",
            "clouds": "cloudy",
            "snow": "snowy"
        }
        
        weather_type = weather_map.get(weather_condition.lower(), "cloudy")
        
        if weather_type in self.weather_rules:
            return {"weather": weather_type, **self.weather_rules[weather_type]}
        return None
    
    def calculate_contextual_score(
        self, 
        movie: Movie, 
        time_context: Optional[Dict] = None,
        day_context: Optional[Dict] = None,
        mood_context: Optional[Dict] = None,
        weather_context: Optional[Dict] = None
    ) -> float:
        """Обчислення контекстуального скору для фільму"""
        score = 0.0
        max_score = 0.0
        
        # Час доби (вага 30%)
        if time_context:
            max_score += 30
            time_score = self._calculate_time_score(movie, time_context)
            score += time_score * 30
        
        # День тижня (вага 20%)
        if day_context:
            max_score += 20
            day_score = self._calculate_day_score(movie, day_context)
            score += day_score * 20
        
        # Настрій (вага 35%)
        if mood_context:
            max_score += 35
            mood_score = self._calculate_mood_score(movie, mood_context)
            score += mood_score * 35
        
        # Погода (вага 15%)
        if weather_context:
            max_score += 15
            weather_score = self._calculate_weather_score(movie, weather_context)
            score += weather_score * 15
        
        return score / max_score if max_score > 0 else 0.5
    
    def _calculate_time_score(self, movie: Movie, time_context: Dict) -> float:
        """Розрахунок скору на основі часу доби"""
        score = 0.0
        
        # Перевірка жанрів
        if movie.genres:
            genre_matches = len(set(movie.genres) & set(time_context["preferred_genres"]))
            score += genre_matches / len(time_context["preferred_genres"]) * 0.7
        
        # Перевірка тривалості
        if movie.duration and movie.duration <= time_context["max_duration"]:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_day_score(self, movie: Movie, day_context: Dict) -> float:
        """Розрахунок скору на основі дня тижня"""
        score = 0.0
        
        # Перевірка тривалості
        if movie.duration:
            min_dur, max_dur = day_context["preferred_duration"]
            if min_dur <= movie.duration <= max_dur:
                score += 0.5
            elif movie.duration < min_dur:
                score += 0.3
        
        # Перевірка жанрів
        if movie.genres:
            genre_matches = len(set(movie.genres) & set(day_context["preferred_genres"]))
            if genre_matches > 0:
                score += 0.5
        
        return min(score, 1.0)
    
    def _calculate_mood_score(self, movie: Movie, mood_context: Dict) -> float:
        """Розрахунок скору на основі настрою"""
        score = 0.0
        
        # Перевірка жанрів
        if movie.genres:
            preferred_matches = len(set(movie.genres) & set(mood_context["preferred_genres"]))
            avoid_matches = len(set(movie.genres) & set(mood_context.get("avoid_genres", [])))
            
            score += preferred_matches / len(mood_context["preferred_genres"]) * 0.6
            score -= avoid_matches * 0.2
        
        # Перевірка емоцій
        if movie.emotions and "emotions" in mood_context:
            emotion_matches = sum(
                movie.emotions.get(emotion, 0) 
                for emotion in mood_context["emotions"]
            )
            score += emotion_matches / len(mood_context["emotions"]) * 0.4
        
        return max(min(score, 1.0), 0.0)
    
    def _calculate_weather_score(self, movie: Movie, weather_context: Dict) -> float:
        """Розрахунок скору на основі погоди"""
        score = 0.0
        
        # Перевірка жанрів
        if movie.genres:
            genre_matches = len(set(movie.genres) & set(weather_context["preferred_genres"]))
            score += genre_matches / len(weather_context["preferred_genres"])
        
        return min(score, 1.0)
    
    def get_contextual_explanation(
        self,
        time_context: Optional[Dict] = None,
        day_context: Optional[Dict] = None,
        mood_context: Optional[Dict] = None,
        weather_context: Optional[Dict] = None
    ) -> List[str]:
        """Генерація пояснень контекстуальних рекомендацій"""
        explanations = []
        
        if time_context:
            explanations.append(f"⏰ {time_context['description']}")
        
        if day_context:
            explanations.append(f"📅 {day_context['description']}")
        
        if mood_context:
            explanations.append(f"🎭 {mood_context['description']}")
        
        if weather_context:
            explanations.append(f"🌦️ {weather_context['description']}")
        
        return explanations
