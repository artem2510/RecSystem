# Рекомендаційна система для фільмів

## Опис проєкту

Веб-орієнтована рекомендаційна система для фільмів з гібридними методами фільтрації (контентна + колаборативна), аналізом емоційного фону контенту та пояснювальними механізмами (Explainable AI).

## Основні можливості

- 🔐 **Автентифікація та реєстрація користувачів**
- 🎬 **Гібридна система рекомендацій** (контентна + колаборативна фільтрація)
- 😊 **NLP-аналіз емоційних характеристик фільмів**
- 💡 **Explainable AI** - пояснення кожної рекомендації
- 📊 **Інтерактивний дашборд** з візуалізацією вподобань
- 🔍 **Розширений пошук** за жанрами, ключовими словами та емоціями
- 📈 **Статистика переглядів** та динаміка інтересів

## Архітектура

### Backend
- **Framework**: FastAPI (Python)
- **База даних**: PostgreSQL
- **ORM**: SQLAlchemy
- **Аутентифікація**: JWT tokens
- **NLP**: spaCy, Transformers (HuggingFace)
- **Explainable AI**: власні правила + SHAP

### Frontend
- **Framework**: React 18
- **Styling**: TailwindCSS
- **UI Components**: shadcn/ui
- **Icons**: Lucide React
- **Charts**: Recharts
- **State Management**: React Context + Hooks
- **HTTP Client**: Axios

## Структура проєкту

```
RecSystem/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Конфігурація, безпека
│   │   ├── models/           # SQLAlchemy моделі
│   │   ├── schemas/          # Pydantic схеми
│   │   ├── services/         # Бізнес-логіка
│   │   │   ├── auth.py
│   │   │   ├── recommender.py
│   │   │   ├── nlp_analyzer.py
│   │   │   └── explainer.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── App.jsx
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## Встановлення та запуск

### 🚀 Швидкий старт (SQLite, без PostgreSQL)

**Backend:**
```bash
cd backend
pip install -r requirements.txt

# Створити користувачів
python init_db_simple.py

# Завантажити 100 реальних фільмів з TMDb
python import_movies_tmdb.py

# Запустити сервер
uvicorn app.main:app --reload
```

**Frontend (в новому терміналі):**
```bash
cd frontend
npm install
npm run dev
```

📖 **Детальна інструкція**: Дивіться [QUICK_START.md](QUICK_START.md)

### 🐘 Запуск з PostgreSQL

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Створити .env з PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/movie_recommender

python init_db.py
uvicorn app.main:app --reload
```

## Змінні середовища

**За замовчуванням використовується SQLite** - не потрібно створювати `.env`

Для PostgreSQL створіть `.env` у папці `backend/`:

```env
DATABASE_URL=postgresql://user:password@localhost/movie_recommender
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🎬 Джерело даних фільмів

Фільми завантажуються з **TMDb API (The Movie Database)**:
- ✅ 100+ реальних фільмів
- ✅ Постери високої якості
- ✅ Описи українською
- ✅ Рейтинги та жанри
- ✅ Безкоштовно

## API Endpoints

### Автентифікація
- `POST /api/auth/register` - Реєстрація
- `POST /api/auth/login` - Вхід
- `GET /api/auth/me` - Поточний користувач

### Фільми
- `GET /api/movies` - Список фільмів
- `GET /api/movies/{id}` - Деталі фільму
- `POST /api/movies/{id}/rate` - Оцінити фільм

### Рекомендації
- `GET /api/recommendations` - Персоналізовані рекомендації
- `GET /api/recommendations/explain/{movie_id}` - Пояснення рекомендації

### Пошук
- `GET /api/search?q={query}&emotion={emotion}` - Пошук фільмів

### Дашборд
- `GET /api/dashboard/stats` - Статистика користувача
- `GET /api/dashboard/preferences` - Аналіз вподобань

## Технічні деталі

### Гібридна рекомендаційна система

1. **Контентна фільтрація**:
   - TF-IDF векторизація описів фільмів
   - Косинусна подібність між фільмами
   - Аналіз жанрів та ключових слів

2. **Колаборативна фільтрація**:
   - User-based collaborative filtering
   - Матриця схожості користувачів
   - Прогнозування оцінок

3. **Гібридний підхід**:
   - Зважене комбінування результатів
   - Адаптивні ваги на основі доступних даних

### NLP та емоційний аналіз

- Використання трансформерів для визначення емоційного тону
- Класифікація емоцій: оптимістичний, драматичний, напружений, романтичний, жахливий
- Векторне представлення текстових описів

### Explainable AI

Кожна рекомендація супроводжується поясненням:
- **Схожість за жанрами**: % співпадіння жанрів
- **Популярність серед схожих користувачів**: кількість переглядів
- **Емоційна відповідність**: схожість емоційних характеристик
- **Оцінки**: середній рейтинг від схожих користувачів

## Ліцензія

MIT License

