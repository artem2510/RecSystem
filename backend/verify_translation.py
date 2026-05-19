"""
Перевірка результатів перекладу жанрів
"""
import sys
sys.path.append('c:/D/5 kurs/CascadeProjects/RecSystem/backend')
from app.core.database import SessionLocal
from app.models.movie import Movie

def verify_translation():
    """Перевірка перекладу жанрів"""
    db = SessionLocal()
    try:
        movies = db.query(Movie).all()
        
        # Збираємо всі унікальні жанри
        all_genres = set()
        for movie in movies:
            if movie.genres:
                all_genres.update(movie.genres)
        
        print(f"Всього фільмів: {len(movies)}")
        print(f"Унікальних жанрів: {len(all_genres)}\n")
        
        print("Список всіх жанрів:")
        for genre in sorted(all_genres):
            # Підрахунок кількості фільмів з цим жанром
            count = sum(1 for m in movies if m.genres and genre in m.genres)
            print(f"  - {genre} ({count} фільмів)")
        
        print("\n" + "="*60)
        print("Приклади фільмів з жанрами:")
        print("="*60)
        
        for i, movie in enumerate(movies[:10]):
            print(f"\n{i+1}. {movie.title} ({movie.year})")
            print(f"   Жанри: {', '.join(movie.genres) if movie.genres else 'Немає'}")
        
    except Exception as e:
        print(f"Помилка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_translation()

