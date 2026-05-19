# 📋 Команди для запуску проєкту

## 🎯 Варіант 1: Автоматичне налаштування (Windows)

```bash
# Подвійний клік на файл або запустіть:
START.bat
```

Це автоматично:
1. Встановить залежності
2. Створить базу даних
3. Завантажить 100 фільмів

---

## 🎯 Варіант 2: Ручне налаштування

### 1️⃣ Встановлення Backend

```bash
cd backend
pip install -r requirements.txt
```

### 2️⃣ Створення користувачів

```bash
python init_db_simple.py
```

**Результат:**
```
✅ Створено 3 користувачів
📝 Тестові користувачі:
  - username: user1, password: password123
  - username: user2, password: password123
  - username: admin, password: admin123
```

### 3️⃣ Завантаження фільмів

```bash
python import_movies_tmdb.py
```

**Результат:**
```
🎬 Початок імпорту фільмів з TMDb...
📄 Завантаження сторінки 1/5...
✅ Додано: Інтерстеллар (2014) - Рейтинг: 8.4/10
✅ Додано: Початок (2010) - Рейтинг: 8.4/10
...
🎉 Імпорт завершено! Всього додано: 100 фільмів
```

### 4️⃣ Запуск Backend

```bash
uvicorn app.main:app --reload
```

**Результат:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 5️⃣ Встановлення Frontend

**В НОВОМУ терміналі:**

```bash
cd frontend
npm install
```

### 6️⃣ Запуск Frontend

```bash
npm run dev
```

**Результат:**
```
VITE v5.0.7  ready in 500 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

---

## 🌐 Доступ до сайту

| Сервіс | URL |
|--------|-----|
| **Frontend (Сайт)** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API Документація** | http://localhost:8000/docs |

---

## 🔧 Додаткові команди

### Перезавантажити фільми

```bash
cd backend
python import_movies_tmdb.py
```

### Змінити кількість фільмів

Відредагуйте `import_movies_tmdb.py`:

```python
# В кінці файлу
import_movies(num_pages=10)  # 200 фільмів замість 100
```

### Очистити базу даних

```bash
cd backend
del movie_recommender.db
python init_db_simple.py
python import_movies_tmdb.py
```

### Перевірити статус

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000
```

---

## ❌ Вирішення проблем

### "ModuleNotFoundError"

```bash
cd backend
pip install -r requirements.txt
```

### "Port 8000 already in use"

```bash
# Знайти процес
netstat -ano | findstr :8000

# Вбити процес (замініть PID)
taskkill /PID <номер_процесу> /F
```

### "npm ERR!"

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Немає фільмів на сайті

```bash
cd backend
python import_movies_tmdb.py
```

---

## 🎬 Готово!

Тепер відкрийте http://localhost:3000 та насолоджуйтесь! 🍿
