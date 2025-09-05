from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.models.ticket import Ticket, TicketCreate, TicketResponse, TicketValidationRequest
from app.services.qr import generate_qr
from app.db.session import get_session
from datetime import datetime, timezone
import uuid

router = APIRouter()

@router.post("/tickets", response_model=TicketResponse)
def create_ticket(t: TicketCreate, session: Session = Depends(get_session)):
    try:
        ticket_id = str(uuid.uuid4())
        ticket = Ticket(ticket_id=ticket_id, **t.dict())
        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        qr_payload = ticket.ticket_id
        qr = generate_qr(qr_payload)

        return TicketResponse(**t.dict(), ticket_id=ticket_id, qr=qr)
    except Exception as e:
        print(f"Error in /tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate_ticket", response_model=TicketResponse)
def validate_ticket(body: TicketValidationRequest, session: Session = Depends(get_session)):
    ticket_id = body.payload.strip()

    result = session.exec(select(Ticket).where(Ticket.ticket_id == ticket_id)).first()

    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if result.used:
        return TicketResponse(
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


@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/tickets/all", response_model=list[TicketResponse])
def get_all_tickets(session: Session = Depends(get_session)):
    tickets = session.exec(select(Ticket)).all()
    return [
        TicketResponse(
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
