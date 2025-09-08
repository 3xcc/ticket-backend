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
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = int(sub)

        # Accept either "ver" or "token_version" to avoid breaking older tokens
        ver_claim = payload.get("ver", payload.get("token_version"))
        if ver_claim is None:
            raise credentials_exception
        token_ver = int(ver_claim)
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    # Prefer primary-key lookup if available
    user = session.get(AdminUser, user_id)
    if not user:
        # Fallback in case session.get behaves differently in your setup
        user = session.exec(select(AdminUser).where(AdminUser.id == user_id)).first()

    if not user or user.token_version != token_ver:
        raise credentials_exception

    return user

def require_permission(action: str):
    """
    Dependency factory that checks if the current user has a given permission.
    Admins bypass all permission checks.
    """
    def checker(user: AdminUser = Depends(get_current_admin_user)):
        if getattr(user, "role", None) == "admin":
            return user
        if not has_permission(user.role, action):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return checker
