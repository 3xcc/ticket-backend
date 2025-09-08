from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select
from app.models.admin_user import AdminUser
from app.db.session import get_session
from app.utils.roles import has_permission
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")

def get_current_admin_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> AdminUser:
    credentials_exception = HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
        user_id = int(payload.get("sub"))
        token_ver = int(payload.get("ver"))
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user = session.exec(select(AdminUser).where(AdminUser.id == user_id)).first()
    if not user or user.token_version != token_ver:
        raise credentials_exception

    return user

def require_permission(action: str):
    """
    Factory function that returns a dependency checking if the current user has a given permission.
    """
    def checker(user: AdminUser = Depends(get_current_admin_user)):
        if not has_permission(user.role, action):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return checker
