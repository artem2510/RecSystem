# ⚡ ЗАПУСТИТИ ЗАРАЗ - 3 кроки

## Термінал 1: Backend

```bash
cd backend
pip install requests sqlalchemy fastapi uvicorn pydantic pydantic-settings python-jose passlib python-multipart scikit-learn numpy
python init_db_simple.py
python import_movies_tmdb.py
uvicorn app.main:app --reload
```

✅ Backend запущено: http://localhost:8000

---

## Термінал 2: Frontend

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend запущено: http://localhost:3000

---

## 🎬 Готово!

Відкрийте: **http://localhost:3000**

### Тестові користувачі:
- `user1` / `password123`
- `user2` / `password123`  
- `admin` / `admin123`

---

## 🎯 Що робити далі:

1. **Зареєструватись** або увійти як user1
2. **Оцінити 5-10 фільмів** (поставити зірки)
3. **Перейти в Рекомендації** - побачите персоналізовані пропозиції
4. **Подивитись пояснення** чому рекомендовані саме ці фільми
5. **Відкрити Дашборд** - статистика ваших вподобань

---

## 📚 Документація API

http://localhost:8000/docs

---

Насолоджуйтесь! 🍿🎬
