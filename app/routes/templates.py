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
    templates = session.exec(select(TicketTemplate)).all()
    return [
        _add_download_url(tpl)
        for tpl in templates
    ]


@router.post("/", response_model=TemplateOut, status_code=status.HTTP_201_CREATED)
def create_template(
    payload: TemplateCreate,
    session: Session = Depends(get_session),
    _ = Depends(require_admin)
):
    """Create a new ticket template (admin only)."""
    tpl = TicketTemplate(
        name=payload.name,
        background_file_id=payload.background_file_id,
        fields=[field.model_dump() for field in payload.fields]  # <-- serialize to dicts
    )

    session.add(tpl)
    session.commit()
    session.refresh(tpl)
    return _add_download_url(tpl)


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
    return _add_download_url(tpl)


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
    return _add_download_url(tpl)


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


# --- Internal helper ---
def _add_download_url(tpl: TicketTemplate) -> TemplateOut:
    """Attach a download_url to the TemplateOut schema."""
    download_url = (
        f"/api/files/{tpl.background_file_id}"
        if tpl.background_file_id else None
    )
    return TemplateOut(
        id=tpl.id,
        name=tpl.name,
        background_file_id=tpl.background_file_id,
        fields=tpl.fields,
        created_at=tpl.created_at,
        updated_at=tpl.updated_at,
        download_url=download_url
    )
