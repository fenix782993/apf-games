from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.models import User, GameResult, Achievement, DailyTask

GAME_RULES = {
    "race": {"xp": 1.0, "points": 0.20},
    "parking": {"xp": 1.1, "points": 0.22},
    "quiz": {"xp": 1.2, "points": 0.25},
    "memory": {"xp": 1.15, "points": 0.24},
}

def rewards(score: int, game: str):
    rule = GAME_RULES.get(game, {"xp": 1.0, "points": 0.2})
    xp = max(5, min(250, int(score * rule["xp"] / 10) + 5))
    points = max(1, min(500, int(score * rule["points"] / 10) + 2))
    return xp, points

def record_result(db: Session, user: User, game: str, score: int, duration: float):
    xp, points = rewards(score, game)
    row = GameResult(user_id=user.id, game=game, score=score, xp=xp, points=points, duration=duration)
    db.add(row)
    user.xp += xp
    user.points += points
    user.games_played += 1
    if score > user.best_score:
        user.best_score = score
    db.commit()
    db.refresh(user)

    if user.games_played >= 1:
        ensure_achievement(db, user, "first_game", "Первая игра")
    if user.games_played >= 10:
        ensure_achievement(db, user, "ten_games", "10 игр")
    if user.best_score >= 1000:
        ensure_achievement(db, user, "score_1000", "1000 очков")

    today = datetime.now(timezone.utc).date().isoformat()
    task = db.query(DailyTask).filter_by(user_id=user.id, task_date=today, code="play").first()
    if not task:
        task = DailyTask(user_id=user.id, task_date=today, code="play", progress=0, target=3)
        db.add(task)
    task.progress = min(task.target, task.progress + 1)
    db.commit()
    return xp, points

def ensure_achievement(db, user, code, title):
    exists = db.query(Achievement).filter_by(user_id=user.id, code=code).first()
    if not exists:
        db.add(Achievement(user_id=user.id, code=code, title=title))
        db.commit()
