"""
Скрипт для імпорту фільмів з TMDb API (The Movie Database)
"""
import requests
import time
from app.core.database import SessionLocal, engine, Base
from app.models.movie import Movie
from app.services.nlp_analyzer import NLPAnalyzer

# TMDb API key (безкоштовний)
# Зареєструйтесь на https://www.themoviedb.org/settings/api щоб отримати ключ
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"  # Це демо ключ, краще використати свій
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

def get_popular_movies(page=1):
    """Отримання популярних фільмів"""
    url = f"{TMDB_BASE_URL}/movie/popular"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "uk-UA",
        "page": page
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["results"]
    return []

def get_movie_details(movie_id):
    """Отримання деталей фільму"""
    url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "uk-UA"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def import_movies(num_pages=5):
    """Імпорт фільмів в базу даних"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    nlp = NLPAnalyzer()
    
    try:
        print(f"🎬 Початок імпорту фільмів з TMDb...")
        
        movies_imported = 0
        
        for page in range(1, num_pages + 1):
            print(f"\n📄 Завантаження сторінки {page}/{num_pages}...")
            popular_movies = get_popular_movies(page)
            
            for tmdb_movie in popular_movies:
                # Перевірка чи фільм вже існує
                existing_movie = db.query(Movie).filter(
                    Movie.title == tmdb_movie["title"]
                ).first()
                
                if existing_movie:
                    print(f"⏭️  Пропущено (вже існує): {tmdb_movie['title']}")
                    continue
                
                # Отримання деталей фільму
                details = get_movie_details(tmdb_movie["id"])
                if not details:
                    continue
                
                # Підготовка даних
                title = tmdb_movie.get("title", "")
                original_title = tmdb_movie.get("original_title", "")
                description = tmdb_movie.get("overview", "")
                year = int(tmdb_movie.get("release_date", "2000-01-01")[:4]) if tmdb_movie.get("release_date") else None
                poster_path = tmdb_movie.get("poster_path")
                poster_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else None
                
                # Жанри
                genres = [genre["name"] for genre in details.get("genres", [])]
                
                # Тривалість
                duration = details.get("runtime")
                
                # Аналіз емоцій
                emotions = nlp.analyze_emotions(description) if description else {}
                
                # Ключові слова
                keywords = nlp.extract_keywords(description) if description else []
                
                # Рейтинг
                average_rating = round(tmdb_movie.get("vote_average", 0), 1)
                ratings_count = tmdb_movie.get("vote_count", 0)
                
                # Створення фільму
                movie = Movie(
                    title=title,
                    original_title=original_title,
                    description=description,
                    year=year,
                    duration=duration,
                    poster_url=poster_url,
                    genres=genres,
                    keywords=keywords,
                    emotions=emotions,
                    average_rating=average_rating,
                    ratings_count=ratings_count,
                    views_count=0
                )
                
                db.add(movie)
                movies_imported += 1
                print(f"✅ Додано: {title} ({year}) - Рейтинг: {average_rating}/10")
                
                # Затримка щоб не перевантажити API
                time.sleep(0.3)
            
            db.commit()
            print(f"💾 Збережено фільми зі сторінки {page}")
        
        print(f"\n🎉 Імпорт завершено! Всього додано: {movies_imported} фільмів")
        
    except Exception as e:
        print(f"❌ Помилка при імпорті: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 ІМПОРТ ФІЛЬМІВ З TMDb")
    print("=" * 60)
    
    # Імпортуємо 5 сторінок по 20 фільмів = 100 фільмів
    import_movies(num_pages=5)
    
    print("\n" + "=" * 60)
    print("✨ Готово! Тепер у вас є реальні фільми з постерами!")
    print("=" * 60)
