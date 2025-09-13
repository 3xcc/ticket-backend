from fastapi import APIRouter, Depends, HTTPException, Form
from sqlmodel import Session, select
from datetime import datetime
import os

from app.models.user import User
from app.utils.auth import verify_password, create_token
from app.db.session import get_session

router = APIRouter()

@router.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    token = create_token(user)

    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()

    return {"access_token": token, "token_type": "bearer"}
