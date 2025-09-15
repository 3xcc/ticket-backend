import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from app.db.session import get_session
from app.models.template import TicketTemplate
from app.utils.render import render_ticket
from app.dependencies.auth import require_admin

router = APIRouter(prefix="/render", tags=["Render"])

@router.get("/{template_id}")
def render_template(
    template_id: str,
    qr_data: str = Query("DEMO-TICKET-123", description="Data to encode in the QR code"),
    session: Session = Depends(get_session),
    _ = Depends(require_admin)
):
    """
    Render a ticket from a template ID and QR data.
    Returns a PNG image stream.
    """
    try:
        tpl = session.get(TicketTemplate, template_id)
        if not tpl:
            logging.warning(f"Render failed — template {template_id} not found")
            raise HTTPException(status_code=404, detail="Template not found")

        img_buf = render_ticket(tpl, qr_data)
        return StreamingResponse(img_buf, media_type="image/png")

    except ValueError as ve:
        # Raised by render_ticket if background is missing or invalid
        logging.error(f"Render error for template {template_id}: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))

    except HTTPException:
        # Let FastAPI handle already-raised HTTP errors
        raise

    except Exception as e:
        logging.exception(f"Unexpected error rendering template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during rendering")
