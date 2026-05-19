"""
Скрипт для ініціалізації бази даних тестовими даними
"""
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.movie import Movie
from app.models.rating import Rating
from app.core.security import get_password_hash
from app.services.nlp_analyzer import NLPAnalyzer

# Створення таблиць
Base.metadata.create_all(bind=engine)

def init_db():
    db = SessionLocal()
    nlp = NLPAnalyzer()
    
    try:
        # Перевірка чи вже є дані
        if db.query(User).first():
            print("База даних вже ініціалізована")
            return
        
        print("Ініціалізація бази даних...")
        
        # Створення тестових користувачів
        users = [
            User(
                email="user1@example.com",
                username="user1",
                hashed_password=get_password_hash("password123"),
                full_name="Іван Петренко"
            ),
            User(
                email="user2@example.com",
                username="user2",
                hashed_password=get_password_hash("password123"),
                full_name="Марія Коваленко"
            ),
            User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                full_name="Адміністратор"
            )
        ]
        
        for user in users:
            db.add(user)
        
        db.commit()
        print(f"Створено {len(users)} користувачів")
        
        # Створення тестових фільмів
        movies_data = [
            {
                "title": "Інтерстеллар",
                "original_title": "Interstellar",
                "description": "Група дослідників використовує новознайдену червоточину для подолання обмежень космічних подорожей та завоювання величезних відстаней у міжзоряній подорожі.",
                "year": 2014,
                "duration": 169,
                "genres": ["Фантастика", "Драма", "Пригоди"],
                "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"
            },
            {
                "title": "Початок",
                "original_title": "Inception",
                "description": "Злодій, який краде корпоративні секрети за допомогою технології спільного сновидіння, отримує завдання впровадити ідею в розум CEO.",
                "year": 2010,
                "duration": 148,
                "genres": ["Бойовик", "Фантастика", "Трилер"],
                "poster_url": "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg"
            },
            {
                "title": "Темний лицар",
                "original_title": "The Dark Knight",
                "description": "Коли загроза, відома як Джокер, викликає хаос і руйнування серед людей Готема, Бетмен повинен прийняти один з найбільших психологічних і фізичних тестів.",
                "year": 2008,
                "duration": 152,
                "genres": ["Бойовик", "Кримінал", "Драма"],
                "poster_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg"
            },
            {
                "title": "Форрест Гамп",
                "original_title": "Forrest Gump",
                "description": "Історія життя простодушного чоловіка з низьким IQ, який ненавмисно бере участь у кількох визначальних подіях американської історії.",
                "year": 1994,
                "duration": 142,
                "genres": ["Драма", "Романтика"],
                "poster_url": "https://image.tmdb.org/t/p/w500/saHP97rTPS5eLmrLQEcANmKrsFl.jpg"
            },
            {
                "title": "Матриця",
                "original_title": "The Matrix",
                "description": "Комп'ютерний хакер дізнається від таємничих повстанців про справжню природу його реальності та його роль у війні проти її контролерів.",
                "year": 1999,
                "duration": 136,
                "genres": ["Бойовик", "Фантастика"],
                "poster_url": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg"
            },
            {
                "title": "Список Шиндлера",
                "original_title": "Schindler's List",
                "description": "У Польщі під час Другої світової війни Оскар Шиндлер поступово стає стурбованим своїми єврейськими працівниками після того, як став свідком їх переслідування нацистами.",
                "year": 1993,
                "duration": 195,
                "genres": ["Біографія", "Драма", "Історія"],
                "poster_url": "https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg"
            },
            {
                "title": "Втеча з Шоушенка",
                "original_title": "The Shawshank Redemption",
                "description": "Два ув'язнені зав'язують дружбу протягом багатьох років, знаходячи розраду та можливе викуплення через акти звичайної порядності.",
                "year": 1994,
                "duration": 142,
                "genres": ["Драма"],
                "poster_url": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg"
            },
            {
                "title": "Зоряні війни: Епізод V",
                "original_title": "Star Wars: Episode V - The Empire Strikes Back",
                "description": "Після того, як повстанці зазнають поразки від Імперії на крижаній планеті Хот, Люк Скайвокер починає навчання джедая з Йодою.",
                "year": 1980,
                "duration": 124,
                "genres": ["Бойовик", "Пригоди", "Фантастика"],
                "poster_url": "https://image.tmdb.org/t/p/w500/2l05cFWJacyIsTpsqSgH0wQXe4V.jpg"
            },
            {
                "title": "Володар перснів: Повернення короля",
                "original_title": "The Lord of the Rings: The Return of the King",
                "description": "Гендальф і Арагорн ведуть Світ Людей проти армії Саурона, щоб відвернути його увагу від Фродо та Сема.",
                "year": 2003,
                "duration": 201,
                "genres": ["Пригоди", "Драма", "Фентезі"],
                "poster_url": "https://image.tmdb.org/t/p/w500/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg"
            },
            {
                "title": "Бійцівський клуб",
                "original_title": "Fight Club",
                "description": "Страждаючий від безсоння офісний працівник та безтурботний виробник мила формують підпільний бійцівський клуб.",
                "year": 1999,
                "duration": 139,
                "genres": ["Драма"],
                "poster_url": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg"
            }
        ]
        
        movies = []
        for movie_data in movies_data:
            # Аналіз емоцій
            emotions = nlp.analyze_emotions(movie_data["description"])
            keywords = nlp.extract_keywords(movie_data["description"])
            
            movie = Movie(
                title=movie_data["title"],
                original_title=movie_data["original_title"],
                description=movie_data["description"],
                year=movie_data["year"],
                duration=movie_data["duration"],
                genres=movie_data["genres"],
                poster_url=movie_data.get("poster_url"),
                keywords=keywords,
                emotions=emotions,
                average_rating=0.0,
                ratings_count=0,
                views_count=0
            )
            db.add(movie)
            movies.append(movie)
        
        db.commit()
        print(f"Створено {len(movies)} фільмів")
        
        # Створення тестових оцінок
        import random
        ratings_data = []
        
        for user in users[:2]:  # Перші два користувачі
            # Кожен користувач оцінює випадкові фільми
            rated_movies = random.sample(movies, k=random.randint(5, 8))
            for movie in rated_movies:
                rating_value = random.uniform(6.0, 10.0)
                rating = Rating(
                    user_id=user.id,
                    movie_id=movie.id,
                    rating=round(rating_value, 1)
                )
                db.add(rating)
                ratings_data.append(rating)
        
        db.commit()
        print(f"Створено {len(ratings_data)} оцінок")
        
        # Оновлення середніх рейтингів фільмів
        from sqlalchemy import func
        for movie in movies:
            result = db.query(
                func.avg(Rating.rating).label('avg_rating'),
                func.count(Rating.id).label('count')
            ).filter(Rating.movie_id == movie.id).first()
            
            if result.avg_rating:
                movie.average_rating = float(result.avg_rating)
                movie.ratings_count = result.count
        
        db.commit()
        
        print("База даних успішно ініціалізована!")
        print("\nТестові користувачі:")
        print("  username: user1, password: password123")
        print("  username: user2, password: password123")
        print("  username: admin, password: admin123")
        
    except Exception as e:
        print(f"Помилка при ініціалізації: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
