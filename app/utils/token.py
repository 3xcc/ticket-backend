import os
from datetime import datetime, timedelta, timezone
from jose import jwt

# Configure via environment variables in production (Render dashboard)
SECRET_KEY = os.getenv("JWT_SECRET", "change-this-in-production")
ALGORITHM = os.getenv("JWT_ALG", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MIN", "60"))

def create_access_token(user_id: int, role: str, token_version: int) -> str:
    # role is expected to be a plain string
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": str(role),
        "token_version": int(token_version or 0),
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
