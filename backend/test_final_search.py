import sys
sys.path.append('c:/D/5 kurs/CascadeProjects/RecSystem/backend')
from app.core.database import SessionLocal
from app.models.movie import Movie

def normalize_search_query(text: str) -> str:
    """Нормалізація пошукового запиту для кращого пошуку"""
    return text.strip().lower()

def calculate_relevance(movie: Movie, query: str) -> int:
    """Розрахунок релевантності фільму до запиту"""
    query_lower = query.lower()
    title_lower = (movie.title or "").lower()
    original_lower = (movie.original_title or "").lower()
    
    score = 0
    
    # Точний збіг на початку назви - найвищий пріоритет
    if title_lower.startswith(query_lower) or original_lower.startswith(query_lower):
        score += 1000
    
    # Точний збіг у назві
    elif query_lower in title_lower or query_lower in original_lower:
        score += 500
    
    # Додаємо рейтинг фільму
    score += int(movie.average_rating * 10)
    
    return score

db = SessionLocal()

# Тест пошуку "тит"
query = "тит"
query_normalized = normalize_search_query(query)

print(f"Пошук: '{query}'")
print()

all_movies = db.query(Movie).all()

# Фільтруємо в Python для підтримки кирилиці
matching_movies = []
for movie in all_movies:
    title_lower = (movie.title or "").lower()
    original_lower = (movie.original_title or "").lower()
    
    if query_normalized in title_lower or query_normalized in original_lower:
        matching_movies.append(movie)

print(f"Знайдено фільмів: {len(matching_movies)}")
print()

# Сортуємо за релевантністю
sorted_movies = sorted(
    matching_movies,
    key=lambda m: calculate_relevance(m, query_normalized),
    reverse=True
)

print("Топ 10 результатів:")
for i, movie in enumerate(sorted_movies[:10], 1):
    relevance = calculate_relevance(movie, query_normalized)
    print(f"{i}. {movie.title} ({movie.original_title}) - Релевантність: {relevance}, Рейтинг: {movie.average_rating}")

db.close()

