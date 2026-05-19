@echo off
chcp 65001 >nul
echo ============================================
echo 🎬 ЗАПУСК РЕКОМЕНДАЦІЙНОЇ СИСТЕМИ ФІЛЬМІВ
echo ============================================
echo.

echo 📦 Крок 1: Встановлення залежностей Backend...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Помилка встановлення залежностей
    pause
    exit /b 1
)

echo.
echo 🗄️  Крок 2: Ініціалізація бази даних...
python init_db_simple.py
if %errorlevel% neq 0 (
    echo ❌ Помилка ініціалізації БД
    pause
    exit /b 1
)

echo.
echo 🎬 Крок 3: Завантаження фільмів з TMDb...
python import_movies_tmdb.py
if %errorlevel% neq 0 (
    echo ❌ Помилка завантаження фільмів
    pause
    exit /b 1
)

echo.
echo ✅ Backend готовий!
echo.
echo 📝 Тепер запустіть Backend та Frontend:
echo.
echo Backend:  uvicorn app.main:app --reload
echo Frontend: cd frontend ^&^& npm install ^&^& npm run dev
echo.
pause
