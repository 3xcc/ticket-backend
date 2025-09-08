from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from typing import Any, Dict, List
import logging

from app.db.session import get_session
from app.models.admin_user import AdminUser
from app.models.ticket import Ticket, TicketResponse
from app.utils.security import verify_password
from app.utils.token import create_access_token
from app.dependencies.auth import require_permission

router = APIRouter(prefix="/admin")
log = logging.getLogger("uvicorn.error")

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.exec(
        select(AdminUser).where(AdminUser.email == form_data.username)
    ).first()

    print("DEBUG: user =", user)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    try:
        password_ok = verify_password(form_data.password, user.hashed_password)
        print("DEBUG: password_ok =", password_ok)
    except Exception as e:
        print("DEBUG: password verification error:", e)
        raise HTTPException(status_code=500, detail="Password verification failed")

    if not password_ok:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    role = getattr(user.role, "value", user.role)
    print("DEBUG: role =", role)

    try:
        token = create_access_token(user.id, role, user.token_version)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        print("DEBUG: token creation error:", e)
        raise HTTPException(status_code=500, detail="Token creation failed")


@router.put("/tickets/{ticket_id}", response_model=TicketResponse)
def edit_ticket(
    ticket_id: str,
    updates: Dict[str, Any],
    session: Session = Depends(get_session),
    _editor: AdminUser = Depends(require_permission("edit_ticket")),
):
    ticket = session.exec(select(Ticket).where(Ticket.ticket_id == ticket_id)).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    for key, value in updates.items():
        if hasattr(ticket, key):
            setattr(ticket, key, value)

    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return TicketResponse.model_validate(ticket)

@router.delete("/tickets/{ticket_id}")
def delete_ticket(
    ticket_id: str,
    session: Session = Depends(get_session),
    _admin: AdminUser = Depends(require_permission("delete_ticket")),
):
    ticket = session.exec(select(Ticket).where(Ticket.ticket_id == ticket_id)).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    session.delete(ticket)
    session.commit()
    return {"message": f"Ticket {ticket_id} deleted successfully"}

@router.delete("/tickets")
def bulk_delete(
    confirm: bool = False,
    session: Session = Depends(get_session),
    _admin: AdminUser = Depends(require_permission("delete_ticket")),
):
    if not confirm:
        raise HTTPException(status_code=400, detail="Confirmation required")
    tickets = session.exec(select(Ticket)).all()
    for t in tickets:
        session.delete(t)
    session.commit()
    return {"message": "All tickets deleted successfully"}

@router.get("/export", response_model=List[TicketResponse])
def export_tickets(
    session: Session = Depends(get_session),
    _viewer: AdminUser = Depends(require_permission("export")),
):
    tickets = session.exec(select(Ticket)).all()
    return [TicketResponse.model_validate(t) for t in tickets]
