"""Тест альтернативних рекомендацій"""
import sys
sys.path.append('.')

from app.core.database import SessionLocal
from app.models.movie import Movie
from app.services.explainer import ExplainableAI

def test_alternatives():
    db = SessionLocal()
    try:
        # Беремо перший фільм
        movie = db.query(Movie).first()
        if not movie:
            print("❌ Немає фільмів в БД")
            return
        
        print(f"✅ Тестуємо альтернативи для фільму: {movie.title}")
        print(f"   Жанри: {movie.genres}")
        print(f"   Рейтинг: {movie.average_rating}")
        
        explainer = ExplainableAI(db)
        
        # Тест 1: different_genre
        print("\n📊 Тест 1: different_genre")
        try:
            alternatives = explainer.get_alternative_recommendations(
                user_id=1,
                rejected_movie=movie,
                reason="different_genre"
            )
            print(f"   Знайдено альтернатив: {len(alternatives)}")
            if alternatives:
                print(f"   Перша альтернатива: {alternatives[0]['movie'].title}")
                print(f"   Пояснення: {alternatives[0]['reason']}")
        except Exception as e:
            print(f"   ❌ Помилка: {e}")
        
        # Тест 2: different_emotion
        print("\n📊 Тест 2: different_emotion")
        try:
            alternatives = explainer.get_alternative_recommendations(
                user_id=1,
                rejected_movie=movie,
                reason="different_emotion"
            )
            print(f"   Знайдено альтернатив: {len(alternatives)}")
            if alternatives:
                print(f"   Перша альтернатива: {alternatives[0]['movie'].title}")
        except Exception as e:
            print(f"   ❌ Помилка: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_alternatives()
