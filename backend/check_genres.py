import sys
sys.path.append('c:/D/5 kurs/CascadeProjects/RecSystem/backend')
from app.core.database import SessionLocal
from app.models.movie import Movie

try:
    db = SessionLocal()
    movies = db.query(Movie).all()
    genres = set()
    for movie in movies:
        if movie.genres:
            genres.update(movie.genres)

    print('Current genres in database:')
    for genre in sorted(list(genres)):
        print(f'  - {genre}')

    print(f'\nTotal movies: {len(movies)}')
    db.close()
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()

