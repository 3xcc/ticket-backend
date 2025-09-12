from jose import jwt
from datetime import datetime, timedelta

from app.config import settings  # or use os.getenv if you prefer

JWT_SECRET = settings.JWT_SECRET  # already set in Render
JWT_EXPIRY_MINUTES = 60

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
