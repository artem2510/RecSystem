import sys
sys.path.append('c:/D/5 kurs/CascadeProjects/RecSystem/backend')
from app.core.database import SessionLocal
from app.models.movie import Movie

# Ukrainian characters and words that indicate Ukrainian genres
ukrainian_indicators = [
    'а', 'б', 'в', 'г', 'ґ', 'д', 'е', 'є', 'ж', 'з', 'и', 'і', 'ї', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ь', 'ю', 'я',
    'А', 'Б', 'В', 'Г', 'Ґ', 'Д', 'Е', 'Є', 'Ж', 'З', 'И', 'І', 'Ї', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ь', 'Ю', 'Я'
]

def is_ukrainian_genre(genre):
    """Check if a genre name contains Ukrainian characters"""
    return any(char in genre for char in ukrainian_indicators)

def categorize_genres():
    """Categorize genres into Ukrainian and English"""
    db = SessionLocal()
    try:
        movies = db.query(Movie).all()
        all_genres = set()

        for movie in movies:
            if movie.genres:
                all_genres.update(movie.genres)

        ukrainian_genres = []
        english_genres = []

        for genre in sorted(all_genres):
            if is_ukrainian_genre(genre):
                ukrainian_genres.append(genre)
            else:
                english_genres.append(genre)

        return ukrainian_genres, english_genres, len(movies)
    finally:
        db.close()

def delete_ukrainian_genres():
    """Delete movies that have only Ukrainian genres"""
    db = SessionLocal()
    try:
        # Get all movies
        movies = db.query(Movie).all()

        movies_to_delete = []
        for movie in movies:
            if movie.genres:
                # Check if all genres are Ukrainian
                all_ukrainian = all(is_ukrainian_genre(genre) for genre in movie.genres)
                if all_ukrainian:
                    movies_to_delete.append(movie)

        if movies_to_delete:
            print(f"Found {len(movies_to_delete)} movies with only Ukrainian genres:")

            for movie in movies_to_delete[:10]:  # Show first 10
                print(f"  - {movie.title} ({movie.year}): {movie.genres}")

            if len(movies_to_delete) > 10:
                print(f"  ... and {len(movies_to_delete) - 10} more")

            # Ask for confirmation
            confirm = input(f"\nDelete these {len(movies_to_delete)} movies? (y/N): ")
            if confirm.lower() == 'y':
                for movie in movies_to_delete:
                    db.delete(movie)
                db.commit()
                print(f"Successfully deleted {len(movies_to_delete)} movies with Ukrainian genres")
            else:
                print("Deletion cancelled")
        else:
            print("No movies found with only Ukrainian genres")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Analyzing genres...")
    ukrainian_genres, english_genres, total_movies = categorize_genres()

    print(f"\nTotal movies: {total_movies}")
    print(f"Ukrainian genres found: {len(ukrainian_genres)}")
    print(f"English genres found: {len(english_genres)}")

    if ukrainian_genres:
        print("\nUkrainian genres:")
        for genre in ukrainian_genres:
            print(f"  - {genre}")

    if english_genres:
        print("\nEnglish genres:")
        for genre in english_genres:
            print(f"  - {genre}")

    print("\n" + "="*50)
    delete_ukrainian_genres()

