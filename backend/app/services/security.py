from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from pwdlib import PasswordHash
from app.core.config import JWT_SECRET, JWT_ALGORITHM, ACCESS_DAYS

passwords = PasswordHash.recommended()

def hash_password(value: str) -> str:
    return passwords.hash(value)

def verify_password(value: str, hashed: str) -> bool:
    return passwords.verify(value, hashed)

def make_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=ACCESS_DAYS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(value: str) -> int:
    try:
        payload = jwt.decode(value, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except (JWTError, ValueError, KeyError):
        raise ValueError("invalid token")
