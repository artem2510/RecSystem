"""
Скрипт для завантаження фільмів з TMDb API по жанрам для балансування колекції
"""
import requests
import time
from app.core.database import SessionLocal, engine, Base
from app.models.movie import Movie
from app.services.nlp_analyzer import NLPAnalyzer

# TMDb API key
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# Список популярних жанрів (TMDb жанри ID)
GENRES = {
    "Action": 28,
    "Adventure": 12,
    "Animation": 16,
    "Comedy": 35,
    "Crime": 80,
    "Documentary": 99,
    "Drama": 18,
    "Family": 10751,
    "Fantasy": 14,
    "History": 36,
    "Horror": 27,
    "Music": 10402,
    "Mystery": 9648,
    "Romance": 10749,
    "Science Fiction": 878,
    "TV Movie": 10770,
    "Thriller": 53,
    "War": 10752,
    "Western": 37
}

def get_movies_by_genre(genre_id, page=1):
    """Отримання фільмів за жанром"""
    url = f"{TMDB_BASE_URL}/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "uk-UA",
        "with_genres": genre_id,
        "page": page,
        "sort_by": "popularity.desc",
        "vote_count.gte": 100  # Фільми з мінімум 100 голосами
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

def import_movies_by_genres(target_per_genre=25):
    """Завантаження фільмів по жанрам для балансування колекції"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    nlp = NLPAnalyzer()

    try:
        print(f"🎬 Початок балансування фільмів по жанрам...")
        print(f"🎯 Ціль: {target_per_genre} фільмів на жанр")

        total_added = 0

        for genre_name, genre_id in GENRES.items():
            print(f"\n📂 Жанр: {genre_name}")

            # Перевіряємо скільки фільмів цього жанру вже є
            existing_movies = db.query(Movie).filter(
                Movie.genres.contains(genre_name)
            ).count()

            print(f"   Поточна кількість: {existing_movies}")

            if existing_movies >= target_per_genre:
                print(f"   ✅ Досить фільмів ({existing_movies}/{target_per_genre})")
                continue

            needed = target_per_genre - existing_movies
            print(f"   Потрібно додати: {needed}")

            added_for_genre = 0
            page = 1

            while added_for_genre < needed and page <= 5:  # Максимум 5 сторінок
                print(f"   📄 Завантаження сторінки {page}...")

                movies = get_movies_by_genre(genre_id, page)

                for tmdb_movie in movies:
                    # Перевірка чи фільм вже існує
                    existing_movie = db.query(Movie).filter(
                        Movie.title == tmdb_movie["title"]
                    ).first()

                    if existing_movie:
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
                    genres = [genre_name]  # Використовуємо поточний жанр

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
                    added_for_genre += 1
                    total_added += 1

                    print(f"   ✅ Додано: {title} ({year}) - {genre_name}")

                    # Затримка щоб не перевантажити API
                    time.sleep(0.3)

                    if added_for_genre >= needed:
                        break

                page += 1

            db.commit()
            print(f"   💾 Збережено {added_for_genre} фільмів для жанру {genre_name}")

        print(f"\n🎉 Балансування завершено! Додано: {total_added} фільмів")

    except Exception as e:
        print(f"❌ Помилка при балансуванні: {e}")
        db.rollback()
    finally:
        db.close()

def show_genre_stats():
    """Показати статистику по жанрах"""
    db = SessionLocal()

    try:
        print("📊 Статистика по жанрах після балансування:")
        print("=" * 50)

        # Отримуємо всі жанри та кількість фільмів
        cursor = db.execute("""
            SELECT genres, COUNT(*) as count
            FROM movies
            GROUP BY genres
            ORDER BY count DESC
        """)

        for genres, count in cursor:
            print(f"{genres}: {count} фільмів")

    except Exception as e:
        print(f"Помилка при отриманні статистики: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 БАЛАНСУВАННЯ ФІЛЬМІВ ПО ЖАНРАМ")
    print("=" * 60)

    # Завантажуємо фільми для балансування (25 фільмів на жанр)
    import_movies_by_genres(target_per_genre=25)

    # Показуємо статистику
    print("\n" + "=" * 60)
    show_genre_stats()
    print("=" * 60)

    print("\n✨ Балансування завершено!")
