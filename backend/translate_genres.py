"""
Скрипт для перекладу жанрів фільмів з англійської на українську
"""
import sys
sys.path.append('c:/D/5 kurs/CascadeProjects/RecSystem/backend')
from app.core.database import SessionLocal
from app.models.movie import Movie

# Словник перекладів жанрів
GENRE_TRANSLATIONS = {
    "Action": "Бойовик",
    "Adventure": "Пригоди",
    "Animation": "Анімація",
    "Comedy": "Комедія",
    "Crime": "Кримінал",
    "Documentary": "Документальний",
    "Drama": "Драма",
    "Family": "Сімейний",
    "Fantasy": "Фентезі",
    "History": "Історичний",
    "Horror": "Жахи",
    "Music": "Музичний",
    "Mystery": "Містика",
    "Romance": "Романтика",
    "Science Fiction": "Фантастика",
    "TV Movie": "Телефільм",
    "Thriller": "Трилер",
    "War": "Військовий",
    "Western": "Вестерн"
}

def translate_genres():
    """Переклад жанрів у всіх фільмах"""
    db = SessionLocal()
    try:
        movies = db.query(Movie).all()
        
        print(f"Знайдено {len(movies)} фільмів для обробки")
        print("\nПочинаємо переклад жанрів...\n")
        
        updated_count = 0
        
        for movie in movies:
            if movie.genres:
                original_genres = movie.genres.copy()
                translated_genres = []
                
                for genre in movie.genres:
                    # Перекладаємо жанр якщо він є в словнику
                    if genre in GENRE_TRANSLATIONS:
                        translated_genres.append(GENRE_TRANSLATIONS[genre])
                    else:
                        # Якщо переклад не знайдено, залишаємо оригінал
                        translated_genres.append(genre)
                        print(f"⚠️  Переклад не знайдено для жанру: {genre}")
                
                # Оновлюємо жанри фільму
                if original_genres != translated_genres:
                    movie.genres = translated_genres
                    updated_count += 1
                    
                    if updated_count <= 5:  # Показуємо перші 5 прикладів
                        print(f"✅ {movie.title}")
                        print(f"   Було: {original_genres}")
                        print(f"   Стало: {translated_genres}\n")
        
        # Зберігаємо зміни
        db.commit()
        
        print(f"\n{'='*60}")
        print(f"✨ Переклад завершено!")
        print(f"📊 Оновлено фільмів: {updated_count} з {len(movies)}")
        print(f"{'='*60}\n")
        
        # Показуємо всі унікальні жанри після перекладу
        all_genres = set()
        for movie in movies:
            if movie.genres:
                all_genres.update(movie.genres)
        
        print("Жанри після перекладу:")
        for genre in sorted(all_genres):
            print(f"  - {genre}")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("🎬 ПЕРЕКЛАД ЖАНРІВ ФІЛЬМІВ")
    print("="*60)
    print()
    
    translate_genres()

