from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging
import io
import base64
import qrcode
from uuid import uuid4

from app.db.session import get_session
from app.models.user import User
from app.models.ticket import Ticket, TicketResponse
from app.utils.auth import verify_password, create_token, hash_password
from app.dependencies.auth import require_permission

router = APIRouter(prefix="/admin")
log = logging.getLogger("uvicorn.error")

# 🧾 Request Models
class LoginRequest(BaseModel):
    email: str
    password: str

class CreateUserRequest(BaseModel):
    email: str
    password: str
    role: str

# 🎟️ QR Generator
def generate_qr_base64(data: str) -> str:
    qr_img = qrcode.make(data)
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

# 🔐 Admin Login
@router.post("/login")
def login(
    data: LoginRequest,
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == data.email)).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    token = create_token(user)
    return {"access_token": token, "token_type": "bearer"}

# 👤 Create User (scanner/admin)
@router.post("/create_user")
def create_user(
    data: CreateUserRequest,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_permission("create_user")),
):
    existing = session.exec(select(User).where(User.email == data.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")

    new_user = User(
        id=str(uuid4()),
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
        token_version=1,
        created_at=datetime.utcnow(),
        is_active=True
    )
    session.add(new_user)
    session.commit()
    return {"message": f"User {data.email} created"}

# ✏️ Edit Ticket
@router.put("/tickets/{ticket_id}", response_model=TicketResponse)
def edit_ticket(
    ticket_id: str,
    updates: dict,
    session: Session = Depends(get_session),
    _editor: User = Depends(require_permission("edit_ticket")),
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

# 🗑️ Delete Single Ticket
@router.delete("/tickets/{ticket_id}")
def delete_ticket(
    ticket_id: str,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_permission("delete_ticket")),
):
    ticket = session.exec(select(Ticket).where(Ticket.ticket_id == ticket_id)).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    session.delete(ticket)
    session.commit()
    return {"message": f"Ticket {ticket_id} deleted successfully"}

# 🧹 Bulk Delete Tickets
@router.delete("/tickets")
def bulk_delete(
    confirm: bool = False,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_permission("delete_ticket")),
):
    if not confirm:
        raise HTTPException(status_code=400, detail="Confirmation required")
    tickets = session.exec(select(Ticket)).all()
    for t in tickets:
        session.delete(t)
    session.commit()
    return {"message": "All tickets deleted successfully"}

# 📤 Export Tickets
@router.get("/export", response_model=List[TicketResponse])
def export_tickets(
    used: Optional[bool] = Query(None),
    event: Optional[str] = Query(None),
    scanned_by: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    _viewer: User = Depends(require_permission("export")),
):
    query = select(Ticket)

    if used is not None:
        query = query.where(Ticket.used == used)
    if event:
        query = query.where(Ticket.event == event)
    if scanned_by:
        query = query.where(Ticket.scanned_by == scanned_by)
    if start:
        query = query.where(Ticket.scanned_at >= start)
    if end:
        query = query.where(Ticket.scanned_at <= end)

    tickets = session.exec(query).all()
    results: List[TicketResponse] = []
    for t in tickets:
        results.append(
            TicketResponse(
                ticket_number=t.ticket_number,
                name=t.name,
                id_card_number=t.id_card_number,
                date_of_birth=t.date_of_birth,
                phone_number=t.phone_number,
                ticket_id=t.ticket_id,
                qr=generate_qr_base64(t.ticket_id),
                status="already_checked_in" if t.used else "valid",
                event=t.event,
                timestamp=t.scanned_at
            )
        )
    return results