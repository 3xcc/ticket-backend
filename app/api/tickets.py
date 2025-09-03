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

    statement = select(Ticket).where(Ticket.ticket_id == ticket_id)
    result = session.exec(statement).first()

    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found")

    scanned_at = datetime.now(timezone.utc).isoformat()

    return TicketResponse(
        name=result.name,
        id_card_number=result.id_card_number,
        event="Generic Event",  # Extend Ticket model later if needed
        status="valid",
        timestamp=scanned_at
    )

@router.get("/health")
def health():
    return {"status": "ok"}
