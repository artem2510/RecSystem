# Інструкція по запуску проєкту

## Передумови

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+

## Крок 1: Налаштування бази даних

1. Встановіть PostgreSQL
2. Створіть базу даних:
```sql
CREATE DATABASE movie_recommender;
```

## Крок 2: Налаштування Backend

1. Перейдіть до папки backend:
```bash
cd backend
```

2. Створіть віртуальне середовище:
```bash
python -m venv venv
```

3. Активуйте віртуальне середовище:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Встановіть залежності:
```bash
pip install -r requirements.txt
```

5. Створіть файл `.env` (скопіюйте з `.env.example`):
```bash
copy .env.example .env
```

6. Відредагуйте `.env` файл з вашими налаштуваннями:
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/movie_recommender
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

7. Ініціалізуйте базу даних тестовими даними:
```bash
python init_db.py
```

8. Запустіть backend сервер:
```bash
uvicorn app.main:app --reload
```

Backend буде доступний на: http://localhost:8000
API документація: http://localhost:8000/docs

## Крок 3: Налаштування Frontend

1. Відкрийте новий термінал та перейдіть до папки frontend:
```bash
cd frontend
```

2. Встановіть залежності:
```bash
npm install
```

3. Запустіть frontend:
```bash
npm run dev
```

Frontend буде доступний на: http://localhost:3000

## Тестові користувачі

Після ініціалізації бази даних будуть доступні наступні користувачі:

- **Username**: `user1`, **Password**: `password123`
- **Username**: `user2`, **Password**: `password123`
- **Username**: `admin`, **Password**: `admin123`

## Структура проєкту

```
RecSystem/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Конфігурація
│   │   ├── models/       # Моделі БД
│   │   ├── schemas/      # Pydantic схеми
│   │   ├── services/     # Бізнес-логіка
│   │   └── main.py       # Головний файл
│   ├── requirements.txt
│   └── init_db.py        # Ініціалізація БД
├── frontend/
│   ├── src/
│   │   ├── components/   # React компоненти
│   │   ├── pages/        # Сторінки
│   │   ├── contexts/     # Context API
│   │   ├── services/     # API сервіси
│   │   └── App.jsx
│   └── package.json
└── README.md
```

## Основні функції

### Backend API

- **Автентифікація**: `/api/auth/register`, `/api/auth/login`
- **Фільми**: `/api/movies`, `/api/movies/{id}`
- **Рекомендації**: `/api/recommendations`
- **Пошук**: `/api/search`
- **Дашборд**: `/api/dashboard/stats`

### Frontend

- **Головна сторінка**: Огляд популярних фільмів
- **Фільми**: Перегляд всіх фільмів з фільтрацією
- **Пошук**: Розширений пошук за різними критеріями
- **Рекомендації**: Персоналізовані рекомендації з поясненнями
- **Дашборд**: Статистика та аналіз вподобань

## Troubleshooting

### Backend не запускається

1. Перевірте чи активовано віртуальне середовище
2. Перевірте підключення до бази даних
3. Перевірте чи всі залежності встановлені

### Frontend не запускається

1. Видаліть `node_modules` та `package-lock.json`
2. Запустіть `npm install` знову
3. Перевірте чи backend запущений

### Помилки з базою даних

1. Перевірте чи PostgreSQL запущений
2. Перевірте правильність DATABASE_URL в `.env`
3. Спробуйте пересоздать базу даних

## Розробка

### Додавання нових фільмів

Використовуйте POST `/api/movies` endpoint з JWT токеном

### Тестування API

Відкрийте http://localhost:8000/docs для інтерактивної документації Swagger

## Deployment

Для production deployment:

1. Змініть `SECRET_KEY` на безпечний випадковий ключ
2. Налаштуйте production базу даних
3. Встановіть `DEBUG=False`
4. Використовуйте gunicorn для backend
5. Зберіть frontend: `npm run build`
6. Налаштуйте nginx як reverse proxy

## Підтримка

Якщо виникли питання або проблеми, створіть issue в репозиторії проєкту.

