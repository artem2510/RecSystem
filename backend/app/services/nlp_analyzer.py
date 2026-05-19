import numpy as np
from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
import re


class NLPAnalyzer:
    """Сервіс для NLP-аналізу та визначення емоцій"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        
        # Словники емоційних ключових слів
        self.emotion_keywords = {
            "оптимістичний": [
                "happy", "joy", "love", "hope", "dream", "success", "victory", 
                "triumph", "celebration", "friendship", "comedy", "fun", "light"
            ],
            "драматичний": [
                "drama", "conflict", "struggle", "pain", "loss", "tragedy",
                "emotional", "intense", "powerful", "moving", "deep"
            ],
            "напружений": [
                "thriller", "suspense", "tension", "mystery", "danger", "fear",
                "chase", "escape", "survival", "action", "intense", "edge"
            ],
            "романтичний": [
                "love", "romance", "relationship", "heart", "passion", "couple",
                "kiss", "wedding", "date", "romantic", "affection"
            ],
            "жахливий": [
                "horror", "scary", "terror", "fear", "monster", "ghost", "dark",
                "nightmare", "haunted", "evil", "creepy", "frightening"
            ],
            "пригодницький": [
                "adventure", "journey", "quest", "explore", "discovery", "travel",
                "expedition", "treasure", "hero", "epic", "exciting"
            ]
        }
    
    def analyze_emotions(self, text: str) -> Dict[str, float]:
        """Аналіз емоційних характеристик тексту"""
        if not text:
            return {emotion: 0.0 for emotion in self.emotion_keywords.keys()}
        
        text_lower = text.lower()
        emotions = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            # Підрахунок збігів ключових слів
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            # Нормалізація (від 0 до 1)
            score = min(matches / len(keywords) * 2, 1.0)
            emotions[emotion] = round(score, 2)
        
        return emotions
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Витягування ключових слів з тексту"""
        if not text:
            return []
        
        # Очищення тексту
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Фільтрація коротких слів
        words = [w for w in words if len(w) > 3]
        
        # Підрахунок частоти
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Сортування за частотою
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_words[:top_n]]
    
    def create_content_vector(self, text: str, genres: List[str]) -> List[float]:
        """Створення векторного представлення контенту"""
        # Комбінуємо текст та жанри
        combined_text = f"{text} {' '.join(genres)}"
        
        try:
            # TF-IDF векторизація
            vector = self.vectorizer.fit_transform([combined_text]).toarray()[0]
            return vector.tolist()
        except:
            # Якщо помилка, повертаємо нульовий вектор
            return [0.0] * 100
    
    def calculate_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """Обчислення косинусної подібності між векторами"""
        if not vector1 or not vector2:
            return 0.0
        
        v1 = np.array(vector1)
        v2 = np.array(vector2)
        
        # Косинусна подібність
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
