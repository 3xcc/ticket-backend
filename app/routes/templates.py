from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.template import TicketTemplate
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateOut
from app.dependencies.auth import require_admin

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.get("/", response_model=list[TemplateOut])
def list_templates(
    session: Session = Depends(get_session),
    _ = Depends(require_admin)
):
    """List all ticket templates (admin only)."""
    return session.exec(select(TicketTemplate)).all()


@router.post("/", response_model=TemplateOut, status_code=status.HTTP_201_CREATED)
def create_template(
    payload: TemplateCreate,
    session: Session = Depends(get_session),
    _ = Depends(require_admin)
):
    """Create a new ticket template (admin only)."""
    tpl = TicketTemplate(
        name=payload.name,
        background_url=payload.background_url,
        fields=payload.fields
    )
    session.add(tpl)
    session.commit()
    session.refresh(tpl)
    return tpl


@router.get("/{template_id}", response_model=TemplateOut)
def get_template(
    template_id: str,
    session: Session = Depends(get_session),
    _ = Depends(require_admin)
):
    """Get a single ticket template by ID (admin only)."""
    tpl = session.get(TicketTemplate, template_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    return tpl


@router.put("/{template_id}", response_model=TemplateOut)
def update_template(
    template_id: str,
    payload: TemplateUpdate,
    session: Session = Depends(get_session),
    _ = Depends(require_admin)
):
    """Update an existing ticket template (admin only)."""
    tpl = session.get(TicketTemplate, template_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(tpl, key, value)
    tpl.updated_at = datetime.utcnow()

    session.add(tpl)
    session.commit()
    session.refresh(tpl)
    return tpl


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: str,
    session: Session = Depends(get_session),
    _ = Depends(require_admin)
):
    """Delete a ticket template (admin only)."""
    tpl = session.get(TicketTemplate, template_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    session.delete(tpl)
    session.commit()
    return None
