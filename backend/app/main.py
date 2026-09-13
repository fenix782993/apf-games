from typing import Optional
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import engine, get_db, SessionLocal
from app.models.models import Base, User, GameResult, Achievement, DailyTask, AuditLog
from app.schemas.auth import RegisterIn, LoginIn
from app.schemas.games import ResultIn, AchievementIn
from app.services.security import hash_password, verify_password, make_token, decode_token
from app.services.game_service import record_result
from app.core.config import OWNER_EMAIL, OWNER_PASSWORD

Base.metadata.create_all(bind=engine)

app = FastAPI(title="APF Games FULL V1", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        owner = db.query(User).filter_by(email=OWNER_EMAIL.lower()).first()
        if not owner:
            owner = User(
                email=OWNER_EMAIL.lower(),
                password_hash=hash_password(OWNER_PASSWORD),
                name="APF Owner",
                role="OWNER",
            )
            db.add(owner)
            db.commit()
    finally:
        db.close()

def auth_user(authorization: Optional[str], db: Session) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Требуется авторизация")
    try:
        uid = decode_token(authorization[7:])
    except ValueError:
        raise HTTPException(401, "Сессия истекла")
    user = db.get(User, uid)
    if not user:
        raise HTTPException(401, "Пользователь не найден")
    return user

def public_user(u):
    return {
        "id": u.id,
        "email": u.email,
        "name": u.name,
        "role": u.role,
        "xp": u.xp,
        "points": u.points,
        "games_played": u.games_played,
        "best_score": u.best_score,
        "level": u.xp // 500 + 1,
    }

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "APF Games FULL V1", "time": datetime.now(timezone.utc).isoformat()}

@app.post("/api/auth/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(User).filter_by(email=email).first():
        raise HTTPException(400, "Email уже зарегистрирован")
    user = User(email=email, password_hash=hash_password(data.password), name=data.name.strip())
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": make_token(user.id), "user": public_user(user)}

@app.post("/api/auth/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Неверный email или пароль")
    return {"token": make_token(user.id), "user": public_user(user)}

@app.get("/api/me")
def me(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    return public_user(auth_user(authorization, db))

@app.get("/api/games")
def games():
    return [
        {"id":"race","name":"APF Race","description":"Разгоняйся, держи скорость и набирай очки."},
        {"id":"parking","name":"Perfect Parking","description":"Поставь автомобиль в зону парковки за минимальное число ходов."},
        {"id":"quiz","name":"Auto Quiz","description":"Автомобильная викторина."},
        {"id":"memory","name":"Auto Memory","description":"Собери все пары карточек."},
    ]

@app.post("/api/games/result")
def save_result(data: ResultIn, authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    user = auth_user(authorization, db)
    xp, points = record_result(db, user, data.game, data.score, data.duration)
    return {
        "score": data.score,
        "xp": xp,
        "points": points,
        "total_xp": user.xp,
        "total_points": user.points,
        "level": user.xp // 500 + 1,
    }

@app.get("/api/games/history")
def history(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    user = auth_user(authorization, db)
    rows = db.query(GameResult).filter_by(user_id=user.id).order_by(desc(GameResult.created_at)).limit(100).all()
    return [{"game":r.game,"score":r.score,"xp":r.xp,"points":r.points,"duration":r.duration,"created_at":r.created_at.isoformat()} for r in rows]

@app.get("/api/games/leaderboard/{game}")
def leaderboard(game: str, db: Session = Depends(get_db)):
    rows = (
        db.query(GameResult, User)
        .join(User, User.id == GameResult.user_id)
        .filter(GameResult.game == game)
        .order_by(GameResult.score.desc())
        .limit(50)
        .all()
    )
    return [{"rank":i+1,"name":u.name,"score":r.score,"created_at":r.created_at.isoformat()} for i,(r,u) in enumerate(rows)]

@app.post("/api/achievements")
def add_achievement(data: AchievementIn, authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    user = auth_user(authorization, db)
    exists = db.query(Achievement).filter_by(user_id=user.id, code=data.code).first()
    if not exists:
        db.add(Achievement(user_id=user.id, code=data.code, title=data.title))
        db.commit()
    return {"ok": True}

@app.get("/api/achievements")
def achievements(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    user = auth_user(authorization, db)
    rows = db.query(Achievement).filter_by(user_id=user.id).order_by(desc(Achievement.created_at)).all()
    return [{"code":a.code,"title":a.title,"created_at":a.created_at.isoformat()} for a in rows]

@app.get("/api/tasks/daily")
def daily_tasks(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    user = auth_user(authorization, db)
    today = datetime.now(timezone.utc).date().isoformat()
    task = db.query(DailyTask).filter_by(user_id=user.id, task_date=today, code="play").first()
    if not task:
        task = DailyTask(user_id=user.id, task_date=today, code="play", progress=0, target=3)
        db.add(task)
        db.commit()
    return [{"code":task.code,"progress":task.progress,"target":task.target,"claimed":task.claimed,"reward_points":100}]

@app.post("/api/tasks/daily/claim")
def claim_daily(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    user = auth_user(authorization, db)
    today = datetime.now(timezone.utc).date().isoformat()
    task = db.query(DailyTask).filter_by(user_id=user.id, task_date=today, code="play").first()
    if not task or task.progress < task.target:
        raise HTTPException(400, "Задание ещё не выполнено")
    if task.claimed:
        raise HTTPException(400, "Награда уже получена")
    task.claimed = True
    user.points += 100
    db.commit()
    return {"ok":True,"reward_points":100,"total_points":user.points}

@app.get("/api/admin/users")
def admin_users(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    user = auth_user(authorization, db)
    if user.role != "OWNER":
        raise HTTPException(403, "Только владелец")
    rows = db.query(User).order_by(User.id.desc()).limit(500).all()
    return [public_user(u) for u in rows]

@app.post("/api/admin/users/{user_id}/role/{role}")
def set_role(user_id: int, role: str, authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    owner = auth_user(authorization, db)
    if owner.role != "OWNER":
        raise HTTPException(403, "Только владелец")
    if role not in {"PLAYER","MODERATOR","OWNER"}:
        raise HTTPException(400, "Недопустимая роль")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    user.role = role
    db.add(AuditLog(user_id=owner.id, action="role_change", detail=f"{user_id} -> {role}"))
    db.commit()
    return public_user(user)
