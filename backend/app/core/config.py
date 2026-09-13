import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./apf_games.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION")
JWT_ALGORITHM = "HS256"
ACCESS_DAYS = 30

OWNER_EMAIL = os.getenv("OWNER_EMAIL", "owner@apg.local")
OWNER_PASSWORD = os.getenv("OWNER_PASSWORD", "owner123")
