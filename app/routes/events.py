# app/routes/events.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import uuid4
from datetime import datetime

from app.db.session import get_session
from app.models.event import Event, EventCreate, EventRead
from app.models.user import User
from app.dependencies.auth import require_permission

log = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/events")

@router.post("/", response_model=EventRead)
def create_event(
    event: EventCreate,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_permission("create_event")),
):
    """
    Create a new event. Requires 'create_event' permission.
    """
    try:
        existing = session.exec(
            select(Event).where(Event.name == event.name, Event.date == event.date)
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Event already exists")

        new_event = Event(
            id=str(uuid4()),
            name=event.name,
            date=event.date,
            location=event.location,
            created_at=datetime.utcnow()
        )
        session.add(new_event)
        session.commit()
        session.refresh(new_event)
        log.info(f"Event created: {new_event.id} ({new_event.name})")
        return new_event
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail="Error creating event")

@router.get("/", response_model=list[EventRead])
def list_events(
    session: Session = Depends(get_session),
    _viewer: User = Depends(require_permission("view_events")),
):
    """
    List all events. Requires 'view_events' permission.
    """
    try:
        events = session.exec(select(Event)).all()
        return events
    except Exception as e:
        log.error(f"Error listing events: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving events")

@router.delete("/{event_id}")
def delete_event(
    event_id: str,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_permission("delete_event")),
):
    """
    Delete an event by ID. Requires 'delete_event' permission.
    """
    try:
        event = session.get(Event, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        session.delete(event)
        session.commit()
        log.info(f"Event deleted: {event_id}")
        return {"message": f"Event {event_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting event {event_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting event")
