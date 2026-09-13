from typing import Optional
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.db.session import engine, get_db, SessionLocal
from app.models.models import (
    Base,
    User,
    GameResult,
    Achievement,
    DailyTask,
    AuditLog,
)
from app.schemas.auth import RegisterIn, LoginIn
from app.schemas.games import ResultIn, AchievementIn
from app.services.security import (
    hash_password,
    verify_password,
    make_token,
    decode_token,
)
from app.services.game_service import record_result
from app.core.config import OWNER_EMAIL, OWNER_PASSWORD


# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="APF Games FULL",
    version="1.0.0",
    description="APF Games API",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup():
    db = SessionLocal()

    try:
        owner = (
            db.query(User)
            .filter(User.email == OWNER_EMAIL.lower())
            .first()
        )

        if owner is None:
            owner = User(
                email=OWNER_EMAIL.lower(),
                password_hash=hash_password(OWNER_PASSWORD),
                name="APF Owner",
                role="OWNER",
                xp=0,
                points=0,
                games_played=0,
                best_score=0,
            )

            db.add(owner)
            db.commit()

    finally:
        db.close()


# ============================================================
# HELPERS
# ============================================================

def get_current_user(
    authorization: Optional[str],
    db: Session,
) -> User:

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Требуется авторизация",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Неверный формат токена",
        )

    token = authorization[7:].strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Пустой токен",
        )

    try:
        user_id = decode_token(token)

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Сессия истекла или токен недействителен",
        )

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Пользователь не найден",
        )

    return user


def public_user(user: User):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "xp": user.xp,
        "points": user.points,
        "games_played": user.games_played,
        "best_score": user.best_score,
        "level": (user.xp // 500) + 1,
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "service": "APF Games",
        "version": "1.0.0",
        "status": "online",
        "message": "APF Games API is running",
        "docs": "/docs",
        "health": "/api/health",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "APF Games",
        "version": "1.0.0",
        "time": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================
# AUTH — REGISTER
# ============================================================

@app.post("/api/auth/register")
def register(
    data: RegisterIn,
    db: Session = Depends(get_db),
):
    email = data.email.lower().strip()

    existing = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email уже зарегистрирован",
        )

    name = data.name.strip()

    if len(name) < 2:
        raise HTTPException(
            status_code=400,
            detail="Имя должно содержать минимум 2 символа",
        )

    user = User(
        email=email,
        password_hash=hash_password(data.password),
        name=name,
        role="PLAYER",
        xp=0,
        points=0,
        games_played=0,
        best_score=0,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "token": make_token(user.id),
        "user": public_user(user),
    }


# ============================================================
# AUTH — LOGIN
# ============================================================

@app.post("/api/auth/login")
def login(
    data: LoginIn,
    db: Session = Depends(get_db),
):
    email = data.email.lower().strip()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль",
        )

    if not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль",
        )

    return {
        "token": make_token(user.id),
        "user": public_user(user),
    }


# ============================================================
# CURRENT USER
# ============================================================

@app.get("/api/me")
def me(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    user = get_current_user(
        authorization,
        db,
    )

    return public_user(user)


# ============================================================
# GAMES LIST
# ============================================================

@app.get("/api/games")
def games():

    return [
        {
            "id": "race",
            "name": "APF Race",
            "description": (
                "Разгоняй автомобиль, "
                "контролируй скорость и набирай очки."
            ),
            "category": "arcade",
        },
        {
            "id": "parking",
            "name": "Perfect Parking",
            "description": (
                "Припаркуй автомобиль "
                "максимально точно."
            ),
            "category": "skill",
        },
        {
            "id": "quiz",
            "name": "Auto Quiz",
            "description": (
                "Проверь знания автомобилей "
                "и получи XP."
            ),
            "category": "quiz",
        },
        {
            "id": "memory",
            "name": "Auto Memory",
            "description": (
                "Найди все пары автомобилей "
                "за минимальное количество ходов."
            ),
            "category": "puzzle",
        },
    ]


# ============================================================
# SAVE GAME RESULT
# ============================================================

@app.post("/api/games/result")
def save_game_result(
    data: ResultIn,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):

    user = get_current_user(
        authorization,
        db,
    )

    allowed_games = {
        "race",
        "parking",
        "quiz",
        "memory",
    }

    if data.game not in allowed_games:
        raise HTTPException(
            status_code=400,
            detail="Неизвестная игра",
        )

    xp, points = record_result(
        db=db,
        user=user,
        game=data.game,
        score=data.score,
        duration=data.duration,
    )

    return {
        "ok": True,
        "game": data.game,
        "score": data.score,
        "xp": xp,
        "points": points,
        "total_xp": user.xp,
        "total_points": user.points,
        "level": (user.xp // 500) + 1,
    }


# ============================================================
# GAME HISTORY
# ============================================================

@app.get("/api/games/history")
def game_history(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):

    user = get_current_user(
        authorization,
        db,
    )

    rows = (
        db.query(GameResult)
        .filter(GameResult.user_id == user.id)
        .order_by(desc(GameResult.created_at))
        .limit(100)
        .all()
    )

    return [
        {
            "id": row.id,
            "game": row.game,
            "score": row.score,
            "xp": row.xp,
            "points": row.points,
            "duration": row.duration,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]


# ============================================================
# GAME LEADERBOARD
# ============================================================

@app.get("/api/games/leaderboard/{game}")
def game_leaderboard(
    game: str,
    db: Session = Depends(get_db),
):

    allowed_games = {
        "race",
        "parking",
        "quiz",
        "memory",
    }

    if game not in allowed_games:
        raise HTTPException(
            status_code=400,
            detail="Неизвестная игра",
        )

    rows = (
        db.query(GameResult, User)
        .join(
            User,
            User.id == GameResult.user_id,
        )
        .filter(GameResult.game == game)
        .order_by(GameResult.score.desc())
        .limit(50)
        .all()
    )

    result = []

    for index, (game_result, user) in enumerate(
        rows,
        start=1,
    ):
        result.append(
            {
                "rank": index,
                "user_id": user.id,
                "name": user.name,
                "score": game_result.score,
                "created_at": (
                    game_result.created_at.isoformat()
                ),
            }
        )

    return result


# ============================================================
# GLOBAL LEADERBOARD
# ============================================================

@app.get("/api/leaderboard")
def global_leaderboard(
    db: Session = Depends(get_db),
):

    users = (
        db.query(User)
        .order_by(
            User.xp.desc(),
            User.points.desc(),
        )
        .limit(100)
        .all()
    )

    return [
        {
            "rank": index,
            "id": user.id,
            "name": user.name,
            "xp": user.xp,
            "points": user.points,
            "level": (user.xp // 500) + 1,
            "games_played": user.games_played,
            "best_score": user.best_score,
        }
        for index, user in enumerate(
            users,
            start=1,
        )
    ]


# ============================================================
# ACHIEVEMENTS — CREATE
# ============================================================

@app.post("/api/achievements")
def add_achievement(
    data: AchievementIn,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):

    user = get_current_user(
        authorization,
        db,
    )

    existing = (
        db.query(Achievement)
        .filter(
            Achievement.user_id == user.id,
            Achievement.code == data.code,
        )
        .first()
    )

    if existing:
        return {
            "ok": True,
            "already_exists": True,
        }

    achievement = Achievement(
        user_id=user.id,
        code=data.code,
        title=data.title,
    )

    db.add(achievement)
    db.commit()

    return {
        "ok": True,
        "already_exists": False,
    }


# ============================================================
# ACHIEVEMENTS — LIST
# ============================================================

@app.get("/api/achievements")
def achievements(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):

    user = get_current_user(
        authorization,
        db,
    )

    rows = (
        db.query(Achievement)
        .filter(
            Achievement.user_id == user.id
        )
        .order_by(
            desc(Achievement.created_at)
        )
        .all()
    )

    return [
        {
            "id": achievement.id,
            "code": achievement.code,
            "title": achievement.title,
            "created_at": (
                achievement.created_at.isoformat()
            ),
        }
        for achievement in rows
    ]


# ============================================================
# DAILY TASK
# ============================================================

@app.get("/api/tasks/daily")
def daily_tasks(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):

    user = get_current_user(
        authorization,
        db,
    )

    today = (
        datetime.now(timezone.utc)
        .date()
        .isoformat()
    )

    task = (
        db.query(DailyTask)
        .filter(
            DailyTask.user_id == user.id,
            DailyTask.task_date == today,
            DailyTask.code == "play",
        )
        .first()
    )

    if task is None:

        task = DailyTask(
            user_id=user.id,
            task_date=today,
            code="play",
            progress=0,
            target=3,
            claimed=False,
        )

        db.add(task)
        db.commit()
        db.refresh(task)

    return [
        {
            "id": task.id,
            "code": task.code,
            "progress": task.progress,
            "target": task.target,
            "claimed": task.claimed,
            "reward_points": 100,
        }
    ]


# ============================================================
# CLAIM DAILY TASK
# ============================================================

@app.post("/api/tasks/daily/claim")
def claim_daily_task(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):

    user = get_current_user(
        authorization,
        db,
    )

    today = (
        datetime.now(timezone.utc)
        .date()
        .isoformat()
    )

    task = (
        db.query(DailyTask)
        .filter(
            DailyTask.user_id == user.id,
            DailyTask.task_date == today,
            DailyTask.code == "play",
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=400,
            detail="Ежедневное задание не найдено",
        )

    if task.progress < task.target:
        raise HTTPException(
            status_code=400,
            detail="Задание ещё не выполнено",
        )

    if task.claimed:
        raise HTTPException(
            status_code=400,
            detail="Награда уже получена",
        )

    task.claimed = True

    user.points += 100

    db.add(
        AuditLog(
            user_id=user.id,
            action="daily_reward",
            detail="Получено +100 APF Points",
        )
    )

    db.commit()

    return {
        "ok": True,
        "reward_points": 100,
        "total_points": user.points,
    }


# ============================================================
# ADMIN — USERS
# ============================================================

@app.get("/api/admin/users")
def admin_users(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):

    owner = get_current_user(
        authorization,
        db,
    )

    if owner.role != "OWNER":
        raise HTTPException(
            status_code=403,
            detail="Только владелец может использовать этот раздел",
        )

    users = (
        db.query(User)
        .order_by(User.id.desc())
        .limit(500)
        .all()
    )

    return [
        public_user(user)
        for user in users
    ]


# ============================================================
# ADMIN — CHANGE ROLE
# ============================================================

@app.post("/api/admin/users/{user_id}/role/{role}")
def change_user_role(
    user_id: int,
    role: str,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):

    owner = get_current_user(
        authorization,
        db,
    )

    if owner.role != "OWNER":
        raise HTTPException(
            status_code=403,
            detail="Только владелец",
        )

    role = role.upper()

    allowed_roles = {
        "PLAYER",
        "MODERATOR",
        "OWNER",
    }

    if role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Недопустимая роль",
        )

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден",
        )

    old_role = user.role

    user.role = role

    db.add(
        AuditLog(
            user_id=owner.id,
            action="role_change",
            detail=(
                f"user={user.id}; "
                f"{old_role}->{role}"
            ),
        )
    )

    db.commit()
    db.refresh(user)

    return public_user(user)


# ============================================================
# ADMIN — USER STATS
# ============================================================

@app.get("/api/admin/stats")
def admin_stats(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):

    owner = get_current_user(
        authorization,
        db,
    )

    if owner.role != "OWNER":
        raise HTTPException(
            status_code=403,
            detail="Только владелец",
        )

    users_count = db.query(User).count()
    games_count = db.query(GameResult).count()
    achievements_count = db.query(Achievement).count()

    total_points = sum(
        value or 0
        for (value,) in db.query(User.points).all()
    )

    total_xp = sum(
        value or 0
        for (value,) in db.query(User.xp).all()
    )

    return {
        "users": users_count,
        "games": games_count,
        "achievements": achievements_count,
        "total_points": total_points,
        "total_xp": total_xp,
    }


# ============================================================
# ADMIN — AUDIT LOG
# ============================================================

@app.get("/api/admin/audit")
def admin_audit(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):

    owner = get_current_user(
        authorization,
        db,
    )

    if owner.role != "OWNER":
        raise HTTPException(
            status_code=403,
            detail="Только владелец",
        )

    rows = (
        db.query(AuditLog)
        .order_by(desc(AuditLog.created_at))
        .limit(200)
        .all()
    )

    return [
        {
            "id": row.id,
            "user_id": row.user_id,
            "action": row.action,
            "detail": row.detail,
            "created_at": (
                row.created_at.isoformat()
            ),
        }
        for row in rows
    ]
