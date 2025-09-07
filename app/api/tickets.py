from fastapi import APIRouter, HTTPException, Depends, Body
from sqlmodel import Session, select, delete, func
from app.models.ticket import Ticket, TicketCreate, TicketResponse, TicketValidationRequest
from app.services.qr import generate_qr
from app.db.session import get_session
from datetime import datetime, timezone
import uuid

router = APIRouter()

# ---------------------------
# Create Ticket
# ---------------------------
@router.post("/tickets", response_model=TicketResponse)
def create_ticket(t: TicketCreate, session: Session = Depends(get_session)):
    try:
        ticket_id = str(uuid.uuid4())

        # Get current max ticket_number and increment
        max_num = session.exec(select(func.max(Ticket.ticket_number))).one_or_none()
        try:
            next_num = int(max_num or 0) + 1
        except ValueError:
            next_num = 1

        ticket = Ticket(
            ticket_id=ticket_id,
            ticket_number=str(next_num).zfill(4),  # e.g., 0001, 0002
            name=t.name,
            id_card_number=t.id_card_number,
            date_of_birth=t.date_of_birth,
            phone_number=t.phone_number,
            event=t.event,
            used=False,
            scanned_at=None
        )

        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        qr_payload = ticket.ticket_id  # QR encodes ticket_id for scanning
        qr = generate_qr(qr_payload)

        return TicketResponse(
            ticket_number=ticket.ticket_number,
            name=ticket.name,
            id_card_number=ticket.id_card_number,
            date_of_birth=ticket.date_of_birth,
            phone_number=ticket.phone_number,
            ticket_id=ticket.ticket_id,
            qr=qr,
            status="valid",
            event=ticket.event,
            timestamp=""
        )
    except Exception as e:
        print(f"Error in /tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Validate Ticket
# ---------------------------
@router.post("/validate_ticket", response_model=TicketResponse)
def validate_ticket(body: TicketValidationRequest, session: Session = Depends(get_session)):
    ticket_id = body.payload.strip()

    result = session.exec(select(Ticket).where(Ticket.ticket_id == ticket_id)).first()

    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if result.used:
        return TicketResponse(
            ticket_number=result.ticket_number,
            name=result.name,
            id_card_number=result.id_card_number,
            date_of_birth=result.date_of_birth,
            phone_number=result.phone_number,
            ticket_id=result.ticket_id,
            qr="",
            status="already_checked_in",
            event=result.event,
            timestamp=result.scanned_at
        )

    result.used = True
    result.scanned_at = datetime.now(timezone.utc).isoformat()
    session.add(result)
    session.commit()

    return TicketResponse(
        ticket_number=result.ticket_number,
        name=result.name,
        id_card_number=result.id_card_number,
        date_of_birth=result.date_of_birth,
        phone_number=result.phone_number,
        ticket_id=result.ticket_id,
        qr="",
        status="valid",
        event=result.event,
        timestamp=result.scanned_at
    )


# ---------------------------
# Health Check
# ---------------------------
@router.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------
# Get All Tickets
# ---------------------------
@router.get("/tickets/all", response_model=list[TicketResponse])
def get_all_tickets(session: Session = Depends(get_session)):
    tickets = session.exec(select(Ticket)).all()
    return [
        TicketResponse(
            ticket_number=t.ticket_number,
            name=t.name,
            id_card_number=t.id_card_number,
            date_of_birth=t.date_of_birth,
            phone_number=t.phone_number,
            ticket_id=t.ticket_id,
            qr="",
            status="already_checked_in" if t.used else "valid",
            event=t.event,
            timestamp=t.scanned_at
        )
        for t in tickets
    ]


# ---------------------------
# Admin Management Endpoints
# ---------------------------
@router.put("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: str, updates: dict = Body(...), session: Session = Depends(get_session)):
    """
    Edit details of an existing ticket.
    Pass only the fields you want to update in the request body.
    """
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    for key, value in updates.items():
        if hasattr(ticket, key):
            setattr(ticket, key, value)

    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    return TicketResponse(
        ticket_number=ticket.ticket_number,
        name=ticket.name,
        id_card_number=ticket.id_card_number,
        date_of_birth=ticket.date_of_birth,
        phone_number=ticket.phone_number,
        ticket_id=ticket.ticket_id,
        qr="",
        status="already_checked_in" if ticket.used else "valid",
        event=ticket.event,
        timestamp=ticket.scanned_at
    )


@router.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: str, session: Session = Depends(get_session)):
    """
    Delete a single ticket by ID.
    """
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    session.delete(ticket)
    session.commit()
    return {"detail": f"Ticket {ticket_id} deleted successfully"}


@router.delete("/tickets")
def delete_all_tickets(confirm: bool = False, session: Session = Depends(get_session)):
    if not confirm:
        raise HTTPException(status_code=400, detail="Confirmation required to delete all tickets")

    session.exec(delete(Ticket))
    session.commit()
    return {"detail": "All tickets deleted successfully"}

@router.get("/export")
def export_tickets(session: Session = Depends(get_session)):
    tickets = session.exec(select(Ticket)).all()
    return [ticket.dict() for ticket in tickets]
