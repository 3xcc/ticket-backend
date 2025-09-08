from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.ticket import Ticket
from app.models.admin_user import AdminUser, AdminRole
from app.models.ticket import TicketResponse
from app.utils.security import verify_password
from app.utils.token import create_access_token
from app.dependencies.auth import require_permission
from datetime import datetime

router = APIRouter(prefix="/admin")

# ---------------------------
# Login Endpoint
# ---------------------------
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    user = session.exec(select(AdminUser).where(AdminUser.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id, user.role, user.token_version)
    return {"access_token": token, "token_type": "bearer"}

# ---------------------------
# Edit Ticket
# ---------------------------
@router.put("/tickets/{ticket_id}", response_model=TicketResponse)
def edit_ticket(
    ticket_id: str,
    updates: dict,
    session: Session = Depends(get_session),
    editor: AdminUser = Depends(require_permission("edit_ticket"))
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

# ---------------------------
# Delete Ticket
# ---------------------------
@router.delete("/tickets/{ticket_id}")
def delete_ticket(
    ticket_id: str,
    session: Session = Depends(get_session),
    admin: AdminUser = Depends(require_permission("delete_ticket"))
):
    ticket = session.exec(select(Ticket).where(Ticket.ticket_id == ticket_id)).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    session.delete(ticket)
    session.commit()
    return {"message": f"Ticket {ticket_id} deleted successfully"}

# ---------------------------
# Bulk Delete (Dangerous)
# ---------------------------
@router.delete("/tickets")
def bulk_delete(
    confirm: bool = False,
    session: Session = Depends(get_session),
    admin: AdminUser = Depends(require_permission("delete_ticket"))
):
    if not confirm:
        raise HTTPException(status_code=400, detail="Confirmation required")

    session.exec(select(Ticket)).delete()
    session.commit()
    return {"message": "All tickets deleted successfully"}

# ---------------------------
# Export Tickets
# ---------------------------
@router.get("/export", response_model=list[TicketResponse])
def export_tickets(
    session: Session = Depends(get_session),
    viewer: AdminUser = Depends(require_permission("export"))
):
    tickets = session.exec(select(Ticket)).all()
    return [TicketResponse.model_validate(t) for t in tickets]
