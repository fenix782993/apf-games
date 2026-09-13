# APF Games FULL V1

Полноценный стартовый production-style проект APF Games:
- FastAPI backend
- PostgreSQL/SQLite
- JWT authentication
- Argon2 password hashing (без passlib/bcrypt)
- профиль, XP, уровни, APF Points
- игры с реальной механикой
- сохранение результатов
- достижения
- ежедневные задания
- история
- глобальный и игровой рейтинг
- owner/admin API
- responsive React/Vite UI
- Render configuration

## Render API
Build:
pip install -r backend/requirements.txt

Start:
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT

## Render frontend
Build:
cd frontend && npm ci && npm run build

Publish:
frontend/dist

Set VITE_API_URL to the API URL.

## Local backend
cd /d APF_GAMES_FULL_V1\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

## Local frontend
cd /d APF_GAMES_FULL_V1\frontend
npm install
npm run dev

Frontend: http://localhost:5173
API: http://localhost:8000
Docs: http://localhost:8000/docs

## Owner
owner@apg.local
owner123

Change the password immediately in a real deployment.
