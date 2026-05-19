"""
Простий скрипт для ініціалізації бази даних з SQLite (без PostgreSQL)
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.user import User
from app.core.security import get_password_hash

# Використовуємо SQLite для простоти
SQLALCHEMY_DATABASE_URL = "sqlite:///./movie_recommender.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Ініціалізація бази даних з тестовими користувачами"""
    # Створення таблиць
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Перевірка чи вже є користувачі
        if db.query(User).first():
            print("⚠️  База даних вже ініціалізована")
            return
        
        print("🔧 Створення тестових користувачів...")
        
        # Створення користувачів
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
        
        print(f"✅ Створено {len(users)} користувачів")
        print("\n📝 Тестові користувачі:")
        print("  - username: user1, password: password123")
        print("  - username: user2, password: password123")
        print("  - username: admin, password: admin123")
        print("\n✨ База даних готова!")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🗄️  ІНІЦІАЛІЗАЦІЯ БАЗИ ДАНИХ (SQLite)")
    print("=" * 60)
    init_db()
