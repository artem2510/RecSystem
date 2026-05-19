import sys
sys.path.append('c:/D/5 kurs/CascadeProjects/RecSystem/backend')
from app.core.database import SessionLocal
from app.models.movie import Movie
from datetime import datetime

try:
    db = SessionLocal()

    # Get all movies ordered by creation date
    movies = db.query(Movie).order_by(Movie.created_at).all()

    print(f'Total movies: {len(movies)}')
    print('\nFirst 10 movies (oldest):')
    for i, movie in enumerate(movies[:10]):
        print(f'{i+1}. {movie.title} ({movie.year}) - Genres: {movie.genres}')
        if movie.created_at:
            print(f'   Created: {movie.created_at}')

    print('\nLast 10 movies (newest):')
    for i, movie in enumerate(movies[-10:]):
        print(f'{len(movies)-9+i}. {movie.title} ({movie.year}) - Genres: {movie.genres}')
        if movie.created_at:
            print(f'   Created: {movie.created_at}')

    db.close()
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
