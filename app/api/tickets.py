from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, func
from app.models.ticket import Ticket, TicketCreate, TicketResponse, TicketValidationRequest
from app.models.admin_user import AdminUser
from app.services.qr import generate_qr
from app.db.session import get_session
from app.dependencies.auth import require_permission
from datetime import datetime, timezone
import uuid
import logging
import traceback

router = APIRouter()
log = logging.getLogger("uvicorn.error")

# ---------------------------
# Create Ticket (Public)
# ---------------------------
@router.post("/tickets", response_model=TicketResponse)
def create_ticket(t: TicketCreate, session: Session = Depends(get_session)):
    try:
        # Optional: prevent duplicates per event (adjust if global uniqueness is desired)
        existing = session.exec(
            select(Ticket).where(
                (Ticket.id_card_number == t.id_card_number) &
                (Ticket.event == t.event)
            )
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ticket already exists for this ID and event")

        ticket_id = str(uuid.uuid4())

        row = session.exec(select(func.max(Ticket.ticket_number))).one_or_none()
        max_num_str = None
        if row is not None:
            # row may be a tuple like (value,)
            max_num_str = row[0] if isinstance(row, (tuple, list)) else row

        try:
            next_num = (int(max_num_str) + 1) if max_num_str else 1
        except (ValueError, TypeError):
            # If somehow the max in DB is non-numeric, reset to 1
            next_num = 1

        ticket = Ticket(
            ticket_id=ticket_id,
            ticket_number=str(next_num).zfill(4),
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

        # Generate QR last; if QR generation fails, don't lose the created record
        try:
            qr = generate_qr(ticket.ticket_id)
        except Exception as e:
            log.exception("QR generation failed for ticket_id=%s: %s", ticket.ticket_id, e)
            # Still return the ticket; client can regenerate QR if needed
            qr = ""

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
    except HTTPException:
        raise
    except Exception as e:
        # Roll back any partial transaction state
        try:
            session.rollback()
        except Exception:
            pass
        log.error("Error in /tickets: %s", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------------------
# Validate Ticket (Scanner)
# ---------------------------
@router.post("/validate_ticket", response_model=TicketResponse)
def validate_ticket(
    body: TicketValidationRequest,
    session: Session = Depends(get_session),
    scanner: AdminUser = Depends(require_permission("scan_ticket"))
):
    try:
        ticket_id = (body.payload or "").strip()
        if not ticket_id:
            raise HTTPException(status_code=400, detail="Invalid payload")

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
                qr=generate_qr(result.ticket_id),
                status="already_checked_in",
                event=result.event,
                timestamp=result.scanned_at
            )

        result.used = True
        result.scanned_at = datetime.now(timezone.utc).isoformat()

        if hasattr(result, "scanned_by"):
            result.scanned_by = scanner.id

        session.add(result)
        session.commit()
        session.refresh(result)

        return TicketResponse(
            ticket_number=result.ticket_number,
            name=result.name,
            id_card_number=result.id_card_number,
            date_of_birth=result.date_of_birth,
            phone_number=result.phone_number,
            ticket_id=result.ticket_id,
            qr=generate_qr(result.ticket_id),  # ✅ FIXED HERE
            status="valid",
            event=result.event,
            timestamp=result.scanned_at
        )
    except HTTPException:
        raise
    except Exception as e:
        try:
            session.rollback()
        except Exception:
            pass
        log.error("Error in /validate_ticket: %s", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------------------
# Health Check
# ---------------------------
@router.get("/health")
def health():
    return {"status": "ok"}

# ---------------------------
# Get All Tickets (Optional)
# ---------------------------
@router.get("/tickets/all", response_model=list[TicketResponse])
def get_all_tickets(
    session: Session = Depends(get_session),
    viewer: AdminUser = Depends(require_permission("scan_ticket"))  # Optional protection
):
    tickets = session.exec(select(Ticket)).all()
    return [
        TicketResponse(
            ticket_number=t.ticket_number,
            name=t.name,
            id_card_number=t.id_card_number,
            date_of_birth=t.date_of_birth,
            phone_number=t.phone_number,
            ticket_id=t.ticket_id,
            qr=generate_qr(t.ticket_id),
            status="already_checked_in" if t.used else "valid",
            event=t.event,
            timestamp=t.scanned_at
        )
        for t in tickets
    ]