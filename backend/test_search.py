import sys
sys.path.append('c:/D/5 kurs/CascadeProjects/RecSystem/backend')
from app.core.database import SessionLocal
from app.models.movie import Movie

db = SessionLocal()

# Пошук фільмів з "титан" у назві
print("Пошук 'титан':")
movies = db.query(Movie).filter(
    Movie.title.ilike('%титан%')
).all()

for movie in movies:
    print(f'  - {movie.title} ({movie.original_title}) - ID: {movie.id}')

# Пошук фільмів з "titan" у назві
print("\nПошук 'titan':")
movies2 = db.query(Movie).filter(
    Movie.original_title.ilike('%titan%')
).all()

for movie in movies2:
    print(f'  - {movie.title} ({movie.original_title}) - ID: {movie.id}')

# Пошук з "тит"
print("\nПошук 'тит':")
movies3 = db.query(Movie).filter(
    Movie.title.ilike('%тит%')
).all()

print(f'Знайдено {len(movies3)} фільмів')
for movie in movies3[:10]:
    print(f'  - {movie.title} ({movie.original_title})')

db.close()

