from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select
from app.models.user import User, UserRole
from app.db.session import get_session
from app.utils.roles import has_permission
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token"
    )

    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = str(sub)

        ver_claim = payload.get("ver", payload.get("token_version"))
        if ver_claim is None:
            raise credentials_exception
        token_ver = int(ver_claim)
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user = session.get(User, user_id)
    if not user:
        user = session.exec(select(User).where(User.id == user_id)).first()

    if not user or user.token_version != token_ver:
        raise credentials_exception

    return user

def require_permission(action: str):
    """
    Dependency factory that checks if the current user
    """