from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime

from app.models.admin_user import AdminUser
from app.utils.security import verify_password
from app.utils.token import create_access_token
from app.dependencies.db import get_session

router = APIRouter()

@router.post("/admin/login")
def login(email: str, password: str, session: Session = Depends(get_session)):
    # Find user by email
    user = session.exec(select(AdminUser).where(AdminUser.email == email)).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT with user ID + token version
    token = create_access_token({
        "sub": str(user.id),
        "ver": user.token_version
    })

    # Update last login timestamp
    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()

    return {"access_token": token, "token_type": "bearer"}
