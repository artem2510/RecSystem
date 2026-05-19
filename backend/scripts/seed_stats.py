import random
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.models.rating import Rating
from app.models.viewing_history import ViewingHistory


def seed_stats(num_ratings_per_user=30, num_views_per_user=50):
    db = SessionLocal()
    try:
        from app.models.user import User
        from app.models.movie import Movie

        user_rows = db.query(User.id).all()
        user_ids = [u[0] for u in user_rows]
        movie_rows = db.query(Movie.id).all()
        movie_ids = [m[0] for m in movie_rows]

        if not user_ids or not movie_ids:
            print('No users or movies found — skipping seeding')
            return

        for uid in user_ids:
            sampled_movies = random.sample(movie_ids, min(len(movie_ids), num_ratings_per_user))
            for mid in sampled_movies:
                rating_value = round(random.uniform(4.0, 9.5), 1)
                try:
                    db.add(Rating(user_id=uid, movie_id=mid, rating=rating_value))
                except Exception:
                    db.rollback()
            db.commit()

            sampled_views = random.sample(movie_ids, min(len(movie_ids), num_views_per_user))
            for mid in sampled_views:
                watched_at = datetime.utcnow() - timedelta(days=random.randint(0, 365))
                completed = random.random() < 0.7
                try:
                    db.add(ViewingHistory(user_id=uid, movie_id=mid, watched_at=watched_at, completed=completed))
                except Exception:
                    db.rollback()
            db.commit()

        from app.models.rating import Rating
        from app.models.movie import Movie as MovieModel

        for mid in movie_ids:
            ratings = db.query(Rating.rating).filter(Rating.movie_id == mid).all()
            ratings_values = [r[0] for r in ratings]
            count = len(ratings_values)
            avg = round(sum(ratings_values) / count, 1) if count else None
            if count:
                db.query(MovieModel).filter(MovieModel.id == mid).update({
                    MovieModel.ratings_count: count,
                    MovieModel.average_rating: avg
                })
        db.commit()
        print('Seeding completed')
    finally:
        db.close()


if __name__ == '__main__':
    seed_stats()
